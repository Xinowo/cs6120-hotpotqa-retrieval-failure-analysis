"""
summarize_results.py

Aggregation-only helper: read the formal long-format result CSVs
(results/dense_results.csv, results/bm25_results.csv, and any future
rerank_results.csv sharing src.results_schema.RESULT_COLUMNS) and reduce them
to a per-(method, setting) summary table.

This script computes group means of columns that already exist in the input
CSVs; it defines no metrics of its own. Per the project AI-use boundary, metric
definitions and their per-example computation live in src/evaluator.py and are
not touched here. The only naming convention applied is the schema's own rule
that a per-example reciprocal_rank_at_K averaged over a group is reported as
MRR@K (see src/results_schema.py).

Empty cells in the input (e.g. any_evidence_recall@10 for the per_question
setting, which the schema K policy leaves uncomputed) are NaN and are skipped
by the mean, leaving that group's cell blank in the summary.

Usage:
    python scripts/summarize_results.py
    python scripts/summarize_results.py --inputs results/dense_results.csv results/bm25_results.csv
    python scripts/summarize_results.py --group-by method setting question_type
    python scripts/summarize_results.py --out results/summary_metrics.csv
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.results_schema import RECALL_COLUMNS, RECIPROCAL_RANK_COLUMNS

# Group means of these per-example reciprocal ranks are MRR@K by definition.
RR_TO_MRR = {
    "reciprocal_rank_at_10": "MRR@10",
    "reciprocal_rank_at_50": "MRR@50",
}
METRIC_COLUMNS = RECALL_COLUMNS + RECIPROCAL_RANK_COLUMNS

DEFAULT_INPUTS = ["results/dense_results.csv", "results/bm25_results.csv"]


def load_inputs(paths):
    """Concatenate the given result CSVs, keeping only rows we can group."""
    frames = []
    for path in paths:
        if not os.path.exists(path):
            print(f"  (skipping missing input: {path})")
            continue
        frames.append(pd.read_csv(path))
    if not frames:
        raise SystemExit("No input result CSVs found; nothing to summarize.")
    return pd.concat(frames, ignore_index=True)


def summarize(df: pd.DataFrame, group_by) -> pd.DataFrame:
    """Mean of each metric column within each group; NaN cells stay blank."""
    metric_cols = [c for c in METRIC_COLUMNS if c in df.columns]
    counts = df.groupby(group_by, dropna=False).size().rename("n")
    means = df.groupby(group_by, dropna=False)[metric_cols].mean()
    summary = pd.concat([counts, means], axis=1).reset_index()
    return summary.rename(columns=RR_TO_MRR)


def to_markdown(summary: pd.DataFrame) -> str:
    """Render as a GitHub-flavored table without requiring the 'tabulate' dep."""
    cols = list(summary.columns)
    lines = ["| " + " | ".join(cols) + " |",
             "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in summary.iterrows():
        cells = []
        for col in cols:
            value = row[col]
            if pd.isna(value):
                cells.append("")
            elif isinstance(value, float):
                cells.append(f"{value:.3f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(inputs, group_by, out_path):
    df = load_inputs(inputs)
    summary = summarize(df, group_by)

    print("\nSummary (group means; RR means shown as MRR@K):\n")
    print(to_markdown(summary))

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        summary.to_csv(out_path, index=False)
        print(f"\nSaved summary ({len(summary)} groups) to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Aggregate formal result CSVs into a per-group summary table."
    )
    parser.add_argument("--inputs", nargs="+", default=DEFAULT_INPUTS,
                        help="Result CSV paths to concatenate and summarize.")
    parser.add_argument("--group-by", nargs="+", default=["method", "setting"],
                        help="Columns to group by (e.g. method setting question_type).")
    parser.add_argument("--out", type=str, default=None,
                        help="Optional path to write the summary CSV.")
    args = parser.parse_args()

    main(inputs=args.inputs, group_by=args.group_by, out_path=args.out)
