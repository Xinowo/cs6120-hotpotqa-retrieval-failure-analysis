"""
run_rerank_experiment.py  (the formal reranker runner)

The third retrieval stage after BM25 (run_bm25_experiment.py) and dense
(run_dense_experiment.py): re-scores the dense pooled top-50 shortlist with a
cross-encoder and writes `results/rerank_results.csv` in the SAME finalized
long-format schema (docs/specs/2026-07-15-results-csv-schema.md) as the other
two methods, one row per (method, setting, example), so all three files concat
by `example_id`.

Pipeline (pooled only -- reranking a top-50 shortlist is meaningful only in the
pooled setting; a ~10-paragraph per_question corpus has nothing to sharpen):

    results/dense_top50_pooled.csv   (example_id, rank, title, score)
        -> group candidate titles per example, ordered by dense rank
        -> join (example_id, title) back to the pooled corpus for paragraph
           TEXT (the top-50 export stores no text, by design)
        -> CrossEncoderReranker.rerank  (reuses the cross-encoder reranker
           class; this runner never re-implements scoring/sorting)
        -> reranked titles -> evidence Recall@k + reciprocal rank (evaluator.py)

Two inputs must describe the SAME evaluation set, enforced before any model is
built: the pooled corpus is rebuilt here from `load_examples(--split, --n)`, and
the top-50 CSV's example-ID set must equal the loaded example-ID set exactly
(both a missing and an unexpected ID raise), each example must carry exactly the
pooled storage depth of candidates, and every candidate title must resolve to a
paragraph in the corpus. Passing an --n/--split that does not match the run
which produced the CSV is therefore caught loudly, never silently dropped.

Like the dense/BM25 runners, this one only *calls* evaluator.py
(evaluate_example / aggregate_results); it re-implements no recall metric --
that logic is a hand-written core component and stays in evaluator.py. The
per-example bare ``mrr`` key is replaced with the explicit reciprocal-rank
column names the schema fixes (RR@10 / RR@50, no bare ``mrr``).

AI-usage boundary: pure plumbing (CSV join -> reuse reranker -> call evaluator
-> write rows), no metric definition and no failure-taxonomy judgement, so this
is agent-allowed per the project's AI boundary.

Usage:
    python scripts/run_rerank_experiment.py --n 500
    python scripts/run_rerank_experiment.py --n 500 \
        --top50-in results/dense_top50_pooled.csv --out results/rerank_results.csv

The first real run downloads cross-encoder/ms-marco-MiniLM-L-6-v2 and HotpotQA,
so it needs network access once; both are cached locally afterward.
"""

import argparse
import os
import sys

# Allow running directly from the project root without installing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.cross_encoder_reranker import CrossEncoderReranker
from src.data_loader import Paragraph, build_pooled_corpus, load_examples
from src.evaluator import aggregate_results, evaluate_example
from src.results_schema import (
    METRIC_KS_BY_SETTING,
    RESULT_COLUMNS,
    STORE_DEPTH_BY_SETTING,
    TITLE_SEPARATOR,
)
from src.top50_export import TOP50_COLUMNS

METHOD = "rerank"

# Reranking is a pooled-only stage: the dense top-50 shortlist exists only for
# the pooled corpus (per_question corpora are ~10 paragraphs, nothing to
# rerank). Storage depth and the filled metric cutoffs come straight from the
# shared schema so this method matches dense/BM25 exactly.
SETTING = "pooled"
POOLED_STORE_TOP_K = STORE_DEPTH_BY_SETTING[SETTING]
POOLED_METRIC_KS = list(METRIC_KS_BY_SETTING[SETTING])

TITLE_SEP = TITLE_SEPARATOR

# Fixed column order shared by BM25, dense, and this reranker.
COLUMNS = RESULT_COLUMNS


def read_top50(top50_path):
    """Read the dense top-50 export, validating its exact
    (example_id, rank, title, score) schema before use.

    example_id is forced to str so it joins against HotpotExample.example_id
    (a str) even if a batch of ids happened to look numeric.
    """
    if not os.path.exists(top50_path):
        raise FileNotFoundError(
            f"Reranker input not found: {top50_path!r}. Produce it first with "
            f"run_dense_experiment.py --setting both --top50-out {top50_path}."
        )
    df = pd.read_csv(top50_path, dtype={"example_id": str})
    if list(df.columns) != TOP50_COLUMNS:
        raise ValueError(
            f"{top50_path!r} has columns {list(df.columns)}, expected the "
            f"top-50 export schema {TOP50_COLUMNS}."
        )
    return df


def candidate_titles_by_example(top50_df):
    """Group the top-50 export into {example_id: [title, ...]} ordered by
    ascending dense rank.

    Ranks within each example must be contiguous 1..N (the export writes one
    row per (example, rank) with no gaps); a gap would mean the candidate list
    was truncated or corrupted, so we fail loudly rather than rerank a partial
    shortlist. The candidate order feeds the reranker only as tie-break input --
    the cross-encoder re-scores everything -- but we still honour the dense
    ranking so ties resolve reproducibly.
    """
    grouped = {}
    for example_id, sub in top50_df.groupby("example_id", sort=False):
        sub = sub.sort_values("rank")
        ranks = sub["rank"].tolist()
        expected = list(range(1, len(sub) + 1))
        if ranks != expected:
            raise ValueError(
                f"example {example_id!r}: top-50 ranks are not contiguous "
                f"1..{len(sub)} (got {ranks}); the candidate shortlist is "
                f"truncated or corrupted."
            )
        grouped[example_id] = sub["title"].tolist()
    return grouped


def build_candidate_paragraphs(titles, text_by_title, example_id):
    """Join each candidate title back to the pooled corpus to recover its
    paragraph TEXT (the top-50 export stores titles + scores only). Returns a
    list of Paragraph, in the given title order.

    A title absent from the pooled corpus means the top-50 CSV and the rebuilt
    corpus describe different evaluation sets (wrong --n/--split), which would
    corrupt every downstream rank and metric -- so we raise instead of dropping
    the candidate.
    """
    paragraphs = []
    for title in titles:
        if title not in text_by_title:
            raise ValueError(
                f"Candidate title {title!r} (example {example_id!r}) is not in "
                f"the pooled corpus. The top-50 CSV must come from the SAME "
                f"--n/--split used to build this pooled corpus."
            )
        paragraphs.append(Paragraph(title=title, text=text_by_title[title]))
    return paragraphs


def evaluate_for_results(retrieved_titles, gold_titles, k_values):
    """Shape existing evaluator output for the formal result schema.

    The evaluator owns all metric computation. This runner calls it on the two
    documented horizons and replaces its context-dependent bare ``mrr`` key
    with explicit per-example reciprocal-rank column names (matching how the
    dense and failure-review runners each shape the same evaluator output).
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


def make_row(example, retrieved_titles, store_top_k=POOLED_STORE_TOP_K):
    """Build one schema-shaped CSV row (a dict) for one example, plus the
    per-example metric dict (for aggregation).

    `retrieved_titles` is the RERANKED title list; only its first `store_top_k`
    entries go into the CSV. Metrics are computed at the pooled K policy's
    cutoffs (@2/@5/@10); booleans are encoded 1/0. Shape is identical to the
    dense runner's pooled rows -- only `method` differs.
    """
    metrics = evaluate_for_results(
        retrieved_titles, example.gold_titles, POOLED_METRIC_KS
    )

    row = {
        "method": METHOD,
        "setting": SETTING,
        "example_id": example.example_id,
        "question_type": example.question_type,
        "level": example.level,
        "question": example.question,
        "gold_titles": TITLE_SEP.join(sorted(example.gold_titles)),
        "retrieved_titles": TITLE_SEP.join(retrieved_titles[:store_top_k]),
    }
    for key in COLUMNS[len(row):]:
        value = metrics.get(key)
        # int(bool) -> 1/0 per schema; None never occurs here (pooled fills all
        # three cutoffs) but the guard mirrors the dense runner.
        row[key] = int(value) if isinstance(value, bool) else value

    return row, metrics


def run_rerank_pooled(
    examples,
    titles_by_example,
    text_by_title,
    reranker,
    store_top_k=POOLED_STORE_TOP_K,
):
    """Rerank each example's dense top-50 shortlist and shape schema rows.

    For every example (in the given order, matching dense_results.csv's pooled
    rows): pull its candidate titles, join them to pooled-corpus text, rerank
    with the injected `CrossEncoderReranker`, and build the result row. Returns
    (rows, per_example_metrics).

    `titles_by_example` must cover every example (validated by the caller);
    `store_top_k` reranked titles are stored (50 for the pooled protocol).
    """
    rows = []
    per_example_metrics = []
    for ex in examples:
        candidates = build_candidate_paragraphs(
            titles_by_example[ex.example_id], text_by_title, ex.example_id
        )
        reranked_titles = reranker.rerank_titles(
            ex.question, candidates, top_k=store_top_k
        )
        # Output invariant: the formal pooled protocol stores exactly
        # store_top_k titles per row. With exactly store_top_k validated input
        # candidates and the reranker's one-score-per-candidate contract, the
        # reranked list is store_top_k long; this postcondition guarantees the
        # runner can never serialize a short row even if an injected reranker
        # misbehaves.
        if len(reranked_titles) != store_top_k:
            raise ValueError(
                f"example {ex.example_id!r}: reranked output has "
                f"{len(reranked_titles)} titles, expected exactly {store_top_k}."
            )
        row, metrics = make_row(ex, reranked_titles, store_top_k=store_top_k)
        rows.append(row)
        per_example_metrics.append(metrics)
    return rows, per_example_metrics


def validate_candidate_coverage(examples, titles_by_example):
    """The top-50 CSV's example-ID set must equal the loaded example-ID set
    EXACTLY -- neither side may carry an ID the other lacks.

    A loaded example missing from the CSV means the CSV came from a different
    (smaller) run; an example in the CSV that is not loaded means the CSV came
    from a larger run than requested. Either way the two artifacts describe
    different evaluation sets, so downstream ID/metric comparisons would be
    invalid. Both directions are reported (with a few offending IDs each) and
    the check runs before any model is built or any example is reranked.
    """
    loaded_ids = {ex.example_id for ex in examples}
    csv_ids = set(titles_by_example)
    missing = sorted(loaded_ids - csv_ids)
    unexpected = sorted(csv_ids - loaded_ids)
    if missing or unexpected:
        raise ValueError(
            f"top-50 CSV and loaded examples must describe the SAME evaluation "
            f"set. {len(missing)} loaded example(s) missing from the CSV "
            f"(first few: {missing[:5]}); {len(unexpected)} CSV example(s) not "
            f"in the loaded set (first few: {unexpected[:5]}). Use the same "
            f"--n/--split that produced the CSV."
        )


def validate_candidate_depths(titles_by_example, expected_depth=POOLED_STORE_TOP_K):
    """Every example must carry EXACTLY `expected_depth` candidates (the pooled
    storage depth, 50).

    This is deliberately separate from the contiguity check in
    `candidate_titles_by_example`: contiguity proves the ranks are 1..N with no
    gaps, but N could be 49 or 51 and still be contiguous. Depth proves N is
    exactly 50 -- a truncated (short) or oversized export is an invalid formal
    input that must fail before it is reranked and serialized, not be silently
    reranked at the wrong depth. Runs before any model is built.
    """
    wrong = {
        example_id: len(titles)
        for example_id, titles in titles_by_example.items()
        if len(titles) != expected_depth
    }
    if wrong:
        sample = list(wrong.items())[:5]
        raise ValueError(
            f"{len(wrong)} example(s) do not have exactly {expected_depth} "
            f"candidates in the top-50 CSV (example_id -> observed depth, first "
            f"few: {sample}); the pooled reranker input must store exactly "
            f"{expected_depth} candidates per example."
        )


def main(n, split, top50_in, out_path, reranker=None):
    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    pooled_paragraphs, collision_titles = build_pooled_corpus(examples)
    print(
        f"Pooled corpus: {len(pooled_paragraphs)} paragraphs "
        f"({len(collision_titles)} title collisions).\n"
    )
    text_by_title = {p.title: p.text for p in pooled_paragraphs}

    print(f"Reading dense candidate shortlist from {top50_in}...")
    titles_by_example = candidate_titles_by_example(read_top50(top50_in))
    validate_candidate_coverage(examples, titles_by_example)
    validate_candidate_depths(titles_by_example)

    if reranker is None:
        print("Building cross-encoder (first run downloads ms-marco-MiniLM-L-6-v2)...")
        reranker = CrossEncoderReranker()

    rows, per_example_metrics = run_rerank_pooled(
        examples, titles_by_example, text_by_title, reranker,
        store_top_k=POOLED_STORE_TOP_K,
    )

    df = pd.DataFrame(rows, columns=COLUMNS)
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}\n")

    print(f"Overall RERANK retrieval metrics ({SETTING}, n={len(examples)}):")
    for metric, value in aggregate_results(per_example_metrics).items():
        print(f"  {metric}: {value:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reranker runner: dense pooled top-50 -> cross-encoder "
        "rerank -> Any/Full/Partial Evidence Recall@k, written in the "
        "long-format results schema."
    )
    parser.add_argument("--n", type=int, default=500, help="Number of examples to load")
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split")
    parser.add_argument(
        "--top50-in",
        type=str,
        default="results/dense_top50_pooled.csv",
        dest="top50_in",
        help="Dense pooled top-50 export (example_id,rank,title,score) used as "
        "the reranker's candidate shortlist.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="results/rerank_results.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    main(
        n=args.n,
        split=args.split,
        top50_in=args.top50_in,
        out_path=args.out,
    )
