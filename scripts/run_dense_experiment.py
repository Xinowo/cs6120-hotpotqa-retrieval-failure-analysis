"""
run_dense_experiment.py  (the formal dense runner)

Turns the Week 1 debug script into the real experiment runner: it produces
`results/dense_results.csv` in the finalized long-format schema
(docs/specs/2026-07-15-results-csv-schema.md), one row per (method, setting,
example), so BM25 / dense / rerank files concat by `example_id`.

Pipeline (unchanged from Week 1, just re-shaped to the schema):

    HotpotQA example -> paragraph corpus -> DenseRetriever
        -> ranked titles -> evidence Recall@k + reciprocal rank (evaluator.py)

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
    python scripts/run_dense_experiment.py --n 500
    python scripts/run_dense_experiment.py --n 10 --setting per_question
    python scripts/run_dense_experiment.py --n 500 --setting pooled

The default ``--setting both`` writes both settings into the one formal method
file. Storage depth is protocol-locked: all available results up to 10 for
per_question and top-50 for pooled. The pooled top-50 also doubles as the
reranker's candidate depth.

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
from src.results_schema import (
    METRIC_KS,
    METRIC_KS_BY_SETTING,
    RESULT_COLUMNS,
    STORE_DEPTH_BY_SETTING,
    TITLE_SEPARATOR,
    validate_setting,
)
from src.top50_export import build_top50_rows_from_batches, write_top50_csv

METHOD = "dense"

# Per the schema, `retrieved_titles` stores the top ranked titles (enough to
# recompute any metric at k <= the cutoffs). The default depth depends on the
# setting (10 per_question, 50 pooled -- the pooled top-50 doubles as the
# reranker's candidate depth). A setting-specific --k is accepted only when it
# equals the protocol value; ``both`` determines each depth automatically.
DEFAULT_STORE_TOP_K = STORE_DEPTH_BY_SETTING["per_question"]
POOLED_STORE_TOP_K = STORE_DEPTH_BY_SETTING["pooled"]
STORE_TOP_K_BY_SETTING = STORE_DEPTH_BY_SETTING

# The schema fixes three metric columns; which are FILLED depends on setting
# (K policy in the spec): per_question fills @2/@5 and leaves @10 empty (a
# ~10-paragraph corpus makes @10 trivially 1.0); pooled fills all three.
ALL_METRIC_KS = list(METRIC_KS)
K_BY_SETTING = {setting: list(ks) for setting, ks in METRIC_KS_BY_SETTING.items()}

TITLE_SEP = TITLE_SEPARATOR

# Fixed column order shared by BM25, dense, and the future reranker.
COLUMNS = RESULT_COLUMNS


def evaluate_for_results(retrieved_titles, gold_titles, k_values):
    """Shape existing evaluator output for the formal result schema.

    The evaluator owns all metric computation. This runner calls it on the
    two documented horizons and replaces its context-dependent bare ``mrr``
    key with explicit per-example reciprocal-rank column names.
    """
    metrics = evaluate_example(retrieved_titles, gold_titles, k_values=k_values)
    metrics.pop("mrr")
    metrics["reciprocal_rank_at_10"] = evaluate_example(
        retrieved_titles[:10], gold_titles, k_values=[]
    )["mrr"]
    metrics["reciprocal_rank_at_50"] = evaluate_example(
        retrieved_titles[:50], gold_titles, k_values=[]
    )["mrr"]
    return metrics


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
    metrics = evaluate_for_results(retrieved_titles, example.gold_titles, k_values)

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
    for key in COLUMNS[len(row):]:
        value = metrics.get(key)
        # int(bool) -> 1/0 per schema; None -> empty for uncomputed cutoffs.
        row[key] = int(value) if isinstance(value, bool) else value

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
    (retrieve_many), instead of a per-question corpus. Returns
    (rows, per_example_metrics, scored_batches).

    `scored_batches` is that single retrieval pass's `(Paragraph, score)`
    ranking per example. It is returned so the caller can also build the
    score-bearing top-50 export from the SAME ranking, without querying the
    index a second time and with an order guaranteed to match retrieved_titles.

    `pooled_paragraphs` is the shared corpus from build_pooled_corpus; `encoder`
    is injected so the one model load is reused (and tests stay offline). Row
    and metric shaping is identical to run_per_question -- only the corpus and
    the batched retrieval differ.
    """
    retriever = DenseRetriever(pooled_paragraphs, encoder=encoder)
    scored_batches = retriever.retrieve_many(
        [ex.question for ex in examples], top_k=store_top_k
    )

    rows = []
    per_example_metrics = []
    for ex, ranked in zip(examples, scored_batches):
        titles = [paragraph.title for paragraph, _ in ranked]
        row, metrics = make_row(ex, titles, "pooled", store_top_k=store_top_k)
        rows.append(row)
        per_example_metrics.append(metrics)
    return rows, per_example_metrics, scored_batches


def _warm_encoder(examples):
    """Build one DenseRetriever up front just to load the model once, then
    reuse its encoder across all questions (Week 1 trick). Returns None for
    an empty example set (nothing to warm)."""
    if not examples:
        return None
    warm = DenseRetriever(examples[0].paragraphs)
    return warm._encoder


def main(n, split, setting, k, out_path, top50_out=None):
    if setting == "both":
        if k is not None:
            raise ValueError("--k cannot be used with --setting=both; depths are 10 and 50.")
        settings = ["pooled", "per_question"]
    else:
        validate_setting(setting)
        expected_k = STORE_TOP_K_BY_SETTING[setting]
        if k is not None and k != expected_k:
            raise ValueError(
                f"--k={k} conflicts with the formal {setting!r} storage depth "
                f"of {expected_k}. Omit --k or pass --k={expected_k}."
            )
        settings = [setting]

    # The score-bearing top-50 export only exists for the pooled setting (the
    # reranker's candidate list). Reject it up front for a per_question-only run
    # so we fail before loading any data or model.
    if top50_out is not None and "pooled" not in settings:
        raise ValueError(
            "--top50-out requires the pooled setting; use --setting both "
            "(default) or --setting pooled."
        )

    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    print("Building dense encoder (first run downloads all-MiniLM-L6-v2)...")
    encoder = _warm_encoder(examples)

    rows = []
    metrics_by_setting = {}
    pooled_batches = None
    if "pooled" in settings:
        pooled_paragraphs, collision_titles = build_pooled_corpus(examples)
        print(
            f"Pooled corpus: {len(pooled_paragraphs)} paragraphs "
            f"({len(collision_titles)} title collisions).\n"
        )
        pooled_rows, pooled_metrics, pooled_batches = run_pooled(
            examples,
            pooled_paragraphs,
            encoder=encoder,
            store_top_k=STORE_TOP_K_BY_SETTING["pooled"],
        )
        rows.extend(pooled_rows)
        metrics_by_setting["pooled"] = pooled_metrics

    if "per_question" in settings:
        per_question_rows, per_question_metrics = run_per_question(
            examples,
            encoder=encoder,
            store_top_k=STORE_TOP_K_BY_SETTING["per_question"],
        )
        rows.extend(per_question_rows)
        metrics_by_setting["per_question"] = per_question_metrics

    df = pd.DataFrame(rows, columns=COLUMNS)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}\n")

    # Build the score-bearing top-50 export from the SAME pooled ranking as the
    # results CSV (no second retrieval), so the two artifacts' per-question
    # order is identical by construction.
    if top50_out is not None:
        top50_rows = build_top50_rows_from_batches(examples, pooled_batches)
        write_top50_csv(top50_rows, top50_out)
        print(f"Saved {len(top50_rows)} pooled top-50 rows to {top50_out}\n")

    for metric_setting, per_example_metrics in metrics_by_setting.items():
        print(f"Overall DENSE retrieval metrics ({metric_setting}, n={len(examples)}):")
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
        default="both",
        choices=["both", "per_question", "pooled"],
        help="Corpus setting: both (formal default), per_question, or pooled",
    )
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split")
    parser.add_argument(
        "--k",
        type=int,
        default=None,
        help="How many ranked titles to retrieve and store in retrieved_titles "
        "(protocol-locked: 10 for per_question, 50 for pooled). Normally omit.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="results/dense_results.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--top50-out",
        type=str,
        default=None,
        dest="top50_out",
        help="Also write the pooled score-bearing top-50 export "
        "(example_id,rank,title,score) here, built from the same pooled "
        "retrieval as the results CSV. Requires the pooled setting.",
    )
    args = parser.parse_args()

    main(
        n=args.n,
        split=args.split,
        setting=args.setting,
        k=args.k,
        out_path=args.out,
        top50_out=args.top50_out,
    )
