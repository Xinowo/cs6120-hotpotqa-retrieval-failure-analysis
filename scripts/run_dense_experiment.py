"""
run_dense_experiment.py  (the formal dense runner)

Turns the Week 1 debug script into the real experiment runner: it produces
`results/dense_results.csv` in the finalized long-format schema
(docs/specs/2026-07-15-results-csv-schema.md), one row per (method, setting,
example), so BM25 / dense / rerank files concat by `example_id`.

Pipeline (unchanged from Week 1, just re-shaped to the schema):

    HotpotQA example -> per-question paragraph corpus -> DenseRetriever
        -> top-10 titles -> Any Evidence Recall@k (evaluator.py)

Both corpus settings are wired: **per_question** builds one small corpus per
question (each re-embedded, exactly like Week 1); **pooled** builds ONE shared
index over every question's paragraphs merged and deduplicated
(data_loader.build_pooled_corpus) and scores all questions against it. Per the
K policy, per_question fills @2/@5 (a ~10-paragraph corpus makes @10 trivially
1.0) and leaves @10 empty; pooled fills all three cutoffs.

This runner only *calls* evaluator.py (evaluate_example / aggregate_results);
it never re-implements a recall metric -- that logic is a hand-written core
component and stays in evaluator.py.

Usage:
    python scripts/run_dense_experiment.py --n 10 --setting per_question
    python scripts/run_dense_experiment.py --n 500 --setting pooled
    python scripts/run_dense_experiment.py --n 100 --out results/dense_results.csv

`--k` sets how many ranked titles are retrieved and stored in
`retrieved_titles`; it must cover the largest metric cutoff this setting
evaluates. The default depends on --setting (10 for per_question, 50 for
pooled -- the pooled top-50 doubles as the reranker's candidate depth).

Note: the first run downloads all-MiniLM-L6-v2 (~90MB) and HotpotQA, so it
needs network access once; both are cached locally afterward.
"""

import argparse
import os
import sys

# Allow running directly from the project root without installing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.data_loader import build_pooled_corpus, load_examples
from src.dense_retriever import DenseRetriever
from src.evaluator import aggregate_results, evaluate_example

METHOD = "dense"

# Per the schema, `retrieved_titles` stores the top ranked titles (enough to
# recompute any metric at k <= the cutoffs). The default depth depends on the
# setting (10 per_question, 50 pooled -- the pooled top-50 doubles as the
# reranker's candidate depth); overridable via --k.
DEFAULT_STORE_TOP_K = 10
POOLED_STORE_TOP_K = 50
STORE_TOP_K_BY_SETTING = {"per_question": DEFAULT_STORE_TOP_K, "pooled": POOLED_STORE_TOP_K}

# The schema fixes three metric columns; which are FILLED depends on setting
# (K policy in the spec): per_question fills @2/@5 and leaves @10 empty (a
# ~10-paragraph corpus makes @10 trivially 1.0); pooled fills all three.
ALL_METRIC_KS = [2, 5, 10]
K_BY_SETTING = {
    "per_question": [2, 5],
    "pooled": [2, 5, 10],
}

TITLE_SEP = " | "

# Fixed column order, matching the schema table exactly.
COLUMNS = [
    "method",
    "setting",
    "example_id",
    "question_type",
    "level",
    "question",
    "gold_titles",
    "retrieved_titles",
] + [f"any_evidence_recall@{k}" for k in ALL_METRIC_KS]


def make_row(example, retrieved_titles, setting, store_top_k=DEFAULT_STORE_TOP_K):
    """Build one schema-shaped CSV row (a dict) for one example, plus the
    per-example metric dict (for aggregation).

    `retrieved_titles` is the ranked title list from the retriever; only its
    first `store_top_k` entries go into the CSV. Metrics are computed only at
    the K policy's cutoffs for this setting; metric columns outside that set
    are left as None, which pandas writes as an empty cell and reads back as
    NaN (so mean() skips them) -- matching the schema's empty-vs-computed rule.
    """
    k_values = K_BY_SETTING[setting]
    metrics = evaluate_example(retrieved_titles, example.gold_titles, k_values=k_values)

    row = {
        "method": METHOD,
        "setting": setting,
        "example_id": example.example_id,
        "question_type": example.question_type,
        "level": example.level,
        "question": example.question,
        "gold_titles": TITLE_SEP.join(sorted(example.gold_titles)),
        "retrieved_titles": TITLE_SEP.join(retrieved_titles[:store_top_k]),
    }
    for k in ALL_METRIC_KS:
        key = f"any_evidence_recall@{k}"
        # int(bool) -> 1/0 per schema; None -> empty cell for k's not computed.
        row[key] = int(metrics[key]) if key in metrics else None

    return row, metrics


def run_per_question(examples, encoder=None, store_top_k=DEFAULT_STORE_TOP_K):
    """Per-question path: one DenseRetriever per example over that question's
    own ~10 paragraphs (Week 1 behavior). Returns (rows, per_example_metrics).

    `encoder` is injected so all questions reuse one loaded model (and so
    tests can pass a fake encoder and stay offline); with encoder=None each
    DenseRetriever lazily builds the real model on first use.
    """
    rows = []
    per_example_metrics = []
    for ex in examples:
        retriever = DenseRetriever(ex.paragraphs, encoder=encoder)
        titles = retriever.retrieve_titles(ex.question, top_k=store_top_k)
        row, metrics = make_row(ex, titles, "per_question", store_top_k=store_top_k)
        rows.append(row)
        per_example_metrics.append(metrics)
    return rows, per_example_metrics


def run_pooled(examples, pooled_paragraphs, encoder=None, store_top_k=POOLED_STORE_TOP_K):
    """Pooled path: ONE shared DenseRetriever over the whole deduplicated
    pooled corpus; every question is scored against it in a single batch
    (retrieve_many_titles), instead of a per-question corpus. Returns
    (rows, per_example_metrics).

    `pooled_paragraphs` is the shared corpus from build_pooled_corpus; `encoder`
    is injected so the one model load is reused (and tests stay offline). Row
    and metric shaping is identical to run_per_question -- only the corpus and
    the batched retrieval differ.
    """
    retriever = DenseRetriever(pooled_paragraphs, encoder=encoder)
    title_batches = retriever.retrieve_many_titles(
        [ex.question for ex in examples], top_k=store_top_k
    )

    rows = []
    per_example_metrics = []
    for ex, titles in zip(examples, title_batches):
        row, metrics = make_row(ex, titles, "pooled", store_top_k=store_top_k)
        rows.append(row)
        per_example_metrics.append(metrics)
    return rows, per_example_metrics


def _warm_encoder(examples):
    """Build one DenseRetriever up front just to load the model once, then
    reuse its encoder across all questions (Week 1 trick). Returns None for
    an empty example set (nothing to warm)."""
    if not examples:
        return None
    warm = DenseRetriever(examples[0].paragraphs)
    return warm._encoder


def main(n, split, setting, k, out_path):
    if setting not in K_BY_SETTING:
        raise ValueError(f"Unknown setting: {setting!r}")

    # Default storage depth depends on the setting; an explicit --k overrides.
    if k is None:
        k = STORE_TOP_K_BY_SETTING[setting]

    max_metric_k = max(K_BY_SETTING[setting])
    if k < max_metric_k:
        raise ValueError(
            f"--k={k} is too small: setting {setting!r} evaluates recall up to "
            f"@{max_metric_k}, so at least {max_metric_k} titles must be stored."
        )

    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    print("Building dense encoder (first run downloads all-MiniLM-L6-v2)...")
    encoder = _warm_encoder(examples)

    if setting == "per_question":
        rows, per_example_metrics = run_per_question(examples, encoder=encoder, store_top_k=k)
    else:  # pooled: one shared index over every question's paragraphs
        pooled_paragraphs, collision_titles = build_pooled_corpus(examples)
        print(
            f"Pooled corpus: {len(pooled_paragraphs)} paragraphs "
            f"({len(collision_titles)} title collisions).\n"
        )
        rows, per_example_metrics = run_pooled(
            examples, pooled_paragraphs, encoder=encoder, store_top_k=k
        )

    df = pd.DataFrame(rows, columns=COLUMNS)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}\n")

    print(f"Overall DENSE retrieval metrics ({setting}, n={len(examples)}):")
    for metric, value in aggregate_results(per_example_metrics).items():
        print(f"  {metric}: {value:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dense runner: HotpotQA -> dense retrieval -> "
        "Any Evidence Recall@k, written in the long-format results schema."
    )
    parser.add_argument("--n", type=int, default=100, help="Number of examples to load")
    parser.add_argument(
        "--setting",
        type=str,
        default="per_question",
        choices=["per_question", "pooled"],
        help="Corpus setting: per_question (small per-question corpus) or "
        "pooled (one shared deduplicated corpus over all questions)",
    )
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split")
    parser.add_argument(
        "--k",
        type=int,
        default=None,
        help="How many ranked titles to retrieve and store in retrieved_titles "
        "(must cover the largest metric cutoff). Default depends on --setting: "
        "10 for per_question, 50 for pooled.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="results/dense_results.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    main(n=args.n, split=args.split, setting=args.setting, k=args.k, out_path=args.out)
