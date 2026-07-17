"""
run_bm25_experiment.py

Week 2 BM25 experiment runner. Follows docs/specs/2026-07-15-results-csv-schema.md
exactly: single long-format output file results/bm25_results.csv, shared with
dense_results.csv's column set so both can be concatenated by example_id.

Runs BM25 in BOTH corpus settings:

  - pooled:       one shared corpus built from ALL loaded examples' paragraphs
                  (deduplicated by title). PRIMARY setting. k = 2, 5, 10 all
                  computed and filled; top-50 titles are stored.
  - per_question: each question retrieves over its own ~10 paragraphs only
                  (Week 1 setting). CONTRAST setting. k = 2, 5 computed;
                  k = 10 is NOT computed (left empty), since it is trivially
                  1.0 on a ~10-paragraph corpus (schema spec K policy).
                  All available titles up to 10 are stored.

Table-reporting rule (unchanged, per Weekly Todo Plan): pooled tables report
k = 2, 5, 10; per_question tables report k = 2 only. The stored per_question
@5 values are for failure-analysis slicing only, not the main results table.

Usage:
    python scripts/run_bm25_experiment.py --n 100
    python scripts/run_bm25_experiment.py --n 500 --split validation
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.data_loader import load_examples, build_pooled_corpus
from src.retrievers import BM25Retriever
from src.evaluator import evaluate_example, aggregate_results
from src.results_schema import (
    METRIC_KS_BY_SETTING,
    RESULT_COLUMNS,
    STORE_DEPTH_BY_SETTING,
    TITLE_SEPARATOR,
)

POOLED_K_VALUES = list(METRIC_KS_BY_SETTING["pooled"])
PER_QUESTION_K_VALUES = list(METRIC_KS_BY_SETTING["per_question"])
POOLED_TOP_K_MAX = STORE_DEPTH_BY_SETTING["pooled"]
PER_QUESTION_TOP_K_MAX = STORE_DEPTH_BY_SETTING["per_question"]

# Fixed column order shared by BM25, dense, and the future reranker.
COLUMN_ORDER = RESULT_COLUMNS


def _to_csv_value(value):
    """Booleans must be written as 1/0 per schema, not True/False strings."""
    if isinstance(value, bool):
        return int(value)
    return value


def _evaluate_for_results(retrieved_titles, gold_titles, k_values):
    """Call the existing evaluator and expose explicit RR@10/RR@50 fields."""
    metrics = evaluate_example(retrieved_titles, gold_titles, k_values=k_values)
    metrics.pop("mrr")
    metrics["reciprocal_rank_at_10"] = evaluate_example(
        retrieved_titles[:10], gold_titles, k_values=[]
    )["mrr"]
    metrics["reciprocal_rank_at_50"] = evaluate_example(
        retrieved_titles[:50], gold_titles, k_values=[]
    )["mrr"]
    return metrics


def _build_row(method: str, setting: str, ex, retrieved_titles, metrics: dict) -> dict:
    row = {
        "method": method,
        "setting": setting,
        "example_id": ex.example_id,
        "question_type": ex.question_type,
        "level": ex.level,
        "question": ex.question,
        "gold_titles": TITLE_SEPARATOR.join(sorted(ex.gold_titles)),
        "retrieved_titles": TITLE_SEPARATOR.join(retrieved_titles),
    }
    for key in COLUMN_ORDER[len(row):]:
        row[key] = _to_csv_value(metrics.get(key))
    return row


def run_pooled_setting(examples) -> list:
    """BM25 retrieval where every question searches ONE shared pooled corpus."""
    pooled_paragraphs, collision_titles = build_pooled_corpus(examples)
    print(f"Pooled corpus size: {len(pooled_paragraphs)} paragraphs "
          f"({len(collision_titles)} title collisions logged)")
    if collision_titles:
        print(f"  Collision titles (first 5): {collision_titles[:5]}")

    # One shared BM25 index for the whole pooled corpus -- built once, queried
    # by every question (vs. per_question, which builds a fresh small index
    # per question). This is the key structural difference between settings.
    retriever = BM25Retriever(pooled_paragraphs)

    rows = []
    per_example_metrics = []
    for ex in examples:
        retrieved_titles = retriever.retrieve_titles(ex.question, top_k=POOLED_TOP_K_MAX)
        metrics = _evaluate_for_results(retrieved_titles, ex.gold_titles, POOLED_K_VALUES)
        per_example_metrics.append(metrics)
        rows.append(_build_row("bm25", "pooled", ex, retrieved_titles, metrics))

    overall = aggregate_results(per_example_metrics)
    print("Overall BM25 (pooled setting):")
    for metric, value in overall.items():
        print(f"  {metric}: {value:.3f}")

    return rows


def run_per_question_setting(examples) -> list:
    """BM25 retrieval where each question searches only its own ~10 paragraphs."""
    rows = []
    per_example_metrics = []
    for ex in examples:
        retriever = BM25Retriever(ex.paragraphs)
        retrieved_titles = retriever.retrieve_titles(ex.question, top_k=PER_QUESTION_TOP_K_MAX)
        metrics = _evaluate_for_results(
            retrieved_titles, ex.gold_titles, PER_QUESTION_K_VALUES
        )
        per_example_metrics.append(metrics)
        rows.append(_build_row("bm25", "per_question", ex, retrieved_titles, metrics))

    overall = aggregate_results(per_example_metrics)
    print("Overall BM25 (per_question setting, k=2 is the reportable number; k=5 is analysis-only):")
    for metric, value in overall.items():
        print(f"  {metric}: {value:.3f}")

    return rows


def main(n: int, split: str, out_path: str):
    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    print("=== Pooled setting (primary) ===")
    pooled_rows = run_pooled_setting(examples)

    print("\n=== Per-question setting (contrast) ===")
    per_question_rows = run_per_question_setting(examples)

    all_rows = pooled_rows + per_question_rows
    df = pd.DataFrame(all_rows)
    # Reindex to the fixed column order; any metric not computed for a given
    # row (e.g. any_evidence_recall@10 for per_question rows) becomes an
    # empty cell here, exactly per the schema's K policy.
    df = df.reindex(columns=COLUMN_ORDER)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} rows to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 2 BM25 experiment: pooled + per_question settings")
    parser.add_argument("--n", type=int, default=100, help="Number of examples to load")
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split to use")
    parser.add_argument("--out", type=str, default="results/bm25_results.csv", help="Output CSV path")
    args = parser.parse_args()

    main(n=args.n, split=args.split, out_path=args.out)
