"""
summarize_results.py

Aggregation-only helper: read the formal long-format result CSVs
(results/bm25_results.csv, results/dense_results.csv, and
results/rerank_results.csv, which all share src.results_schema.RESULT_COLUMNS)
and reduce them to a per-(method, setting) summary table.

This script computes group means of columns that already exist in the input
CSVs; it defines no metrics of its own. Per the project AI-use boundary, metric
definitions and their per-example computation live in src/evaluator.py and are
not touched here. The general summary applies the schema's rule that a group
mean of reciprocal_rank_at_K is reported as MRR@K. The optional pooled main
table additionally maps frozen storage identifiers to the approved
report-facing aggregate names; it does not rename the source CSV columns.

Empty cells in the input (e.g. any_evidence_recall@10 for the per_question
setting, which the schema K policy leaves uncomputed) are NaN and are skipped
by the mean, leaving that group's cell blank in the summary.

Every requested input must exist and match src.results_schema.RESULT_COLUMNS
exactly, including column order. This keeps incomplete or stale formal result
files from producing a plausible-looking partial summary.

Usage:
    python scripts/reporting/summarize_results.py
    python scripts/reporting/summarize_results.py --inputs results/dense_results.csv results/bm25_results.csv
    python scripts/reporting/summarize_results.py --group-by method setting question_type
    python scripts/reporting/summarize_results.py --out results/summary_metrics.csv
    python scripts/reporting/summarize_results.py --main-table --out results/main_results_v1.csv
"""

import argparse
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

import pandas as pd

from src.results_schema import (
    RECALL_COLUMNS,
    RECIPROCAL_RANK_COLUMNS,
    RESULT_COLUMNS,
)

# Group means of these per-example reciprocal ranks are MRR@K by definition.
RR_TO_MRR = {
    "reciprocal_rank_at_10": "MRR@10",
    "reciprocal_rank_at_50": "MRR@50",
}
METRIC_COLUMNS = RECALL_COLUMNS + RECIPROCAL_RANK_COLUMNS

DEFAULT_INPUTS = [
    "results/bm25_results.csv",
    "results/dense_results.csv",
    "results/rerank_results.csv",
]

# Report-facing aggregate names for the final pooled main table. These do not
# alter the frozen per-example storage identifiers in RESULT_COLUMNS.
MAIN_TABLE_COLUMN_MAP = {
    "method": "Method",
    "any_evidence_recall@2": "Any Evidence Hit Rate@2",
    "any_evidence_recall@5": "Any Evidence Hit Rate@5",
    "any_evidence_recall@10": "Any Evidence Hit Rate@10",
    "full_evidence_recall@2": "Full Evidence Hit Rate@2",
    "full_evidence_recall@5": "Full Evidence Hit Rate@5",
    "full_evidence_recall@10": "Full Evidence Hit Rate@10",
    "partial_evidence_recall@5": "Evidence Recall@5",
    "MRR@10": "MRR@10",
    "MRR@50": "MRR@50",
}
MAIN_TABLE_METHOD_LABELS = {
    "bm25": "BM25",
    "dense": "Dense",
    "rerank": "Dense + Rerank",
}
MAIN_TABLE_COLUMNS = list(MAIN_TABLE_COLUMN_MAP.values())


def validate_result_schema(columns, source):
    """Require the exact formal result schema and report useful differences."""
    actual = list(columns)
    if actual == RESULT_COLUMNS:
        return

    missing = [column for column in RESULT_COLUMNS if column not in actual]
    unexpected = [column for column in actual if column not in RESULT_COLUMNS]
    differences = []
    if missing:
        differences.append(f"missing columns: {missing}")
    if unexpected:
        differences.append(f"unexpected columns: {unexpected}")
    if not missing and not unexpected:
        differences.append("columns are not in RESULT_COLUMNS order")
    raise ValueError(
        f"{source} does not match RESULT_COLUMNS ({'; '.join(differences)})"
    )


def load_inputs(paths):
    """Load and concatenate complete, schema-valid formal result CSVs."""
    missing_paths = [str(path) for path in paths if not os.path.exists(path)]
    if missing_paths:
        raise FileNotFoundError(
            f"Missing input result CSV(s): {', '.join(missing_paths)}"
        )

    frames = []
    for path in paths:
        frame = pd.read_csv(path)
        validate_result_schema(frame.columns, path)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def summarize(df: pd.DataFrame, group_by) -> pd.DataFrame:
    """Mean of each metric column within each group; NaN cells stay blank."""
    validate_result_schema(df.columns, "input dataframe")
    missing_group_columns = [column for column in group_by if column not in df.columns]
    if missing_group_columns:
        raise ValueError(f"Unknown group-by column(s): {missing_group_columns}")

    counts = df.groupby(group_by, dropna=False).size().rename("n")
    means = df.groupby(group_by, dropna=False)[METRIC_COLUMNS].mean()
    summary = pd.concat([counts, means], axis=1).reset_index()
    return summary.rename(columns=RR_TO_MRR)


def build_main_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build the report-facing pooled three-method main table."""
    validate_result_schema(df.columns, "input dataframe")
    pooled = df[
        (df["setting"] == "pooled")
        & (df["method"].isin(MAIN_TABLE_METHOD_LABELS))
    ].copy()

    missing_methods = [
        method
        for method in MAIN_TABLE_METHOD_LABELS
        if method not in set(pooled["method"])
    ]
    if missing_methods:
        raise ValueError(f"Main table missing pooled method(s): {missing_methods}")

    ids_by_method = {
        method: set(group["example_id"])
        for method, group in pooled.groupby("method")
    }
    duplicate_methods = [
        method
        for method, group in pooled.groupby("method")
        if len(group) != group["example_id"].nunique()
    ]
    if duplicate_methods:
        raise ValueError(
            f"Main table inputs contain duplicate pooled example IDs: {duplicate_methods}"
        )
    # Report the partition of methods by identical ID set rather than diffing
    # against an arbitrary reference method: with three or more methods, a fixed
    # reference makes the outlier look like the agreeing majority is at fault.
    methods_by_id_set = {}
    for method in MAIN_TABLE_METHOD_LABELS:
        methods_by_id_set.setdefault(
            frozenset(ids_by_method[method]), []
        ).append(method)
    if len(methods_by_id_set) > 1:
        partition = sorted(sorted(methods) for methods in methods_by_id_set.values())
        raise ValueError(
            "Pooled example ID sets do not match across main-table methods; "
            f"methods grouped by identical ID set: {partition}"
        )

    summary = summarize(pooled, ["method", "setting"])
    order = {method: index for index, method in enumerate(MAIN_TABLE_METHOD_LABELS)}
    summary = summary.sort_values(
        "method", key=lambda values: values.map(order)
    ).reset_index(drop=True)
    table = summary[list(MAIN_TABLE_COLUMN_MAP)].rename(
        columns=MAIN_TABLE_COLUMN_MAP
    )
    table["Method"] = table["Method"].map(MAIN_TABLE_METHOD_LABELS)
    return table[MAIN_TABLE_COLUMNS]


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


def main(inputs, group_by, out_path, main_table=False):
    df = load_inputs(inputs)
    summary = build_main_table(df) if main_table else summarize(df, group_by)

    heading = (
        "Pooled main results table (report-facing aggregate names)"
        if main_table
        else "Summary (group means; RR means shown as MRR@K)"
    )
    print(f"\n{heading}:\n")
    print(to_markdown(summary))

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        float_format = "%.3f" if main_table else None
        summary.to_csv(out_path, index=False, float_format=float_format)
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
    parser.add_argument(
        "--main-table",
        action="store_true",
        help=(
            "Write the pooled BM25-vs-Dense-vs-Rerank main table with "
            "report-facing aggregate names and three-decimal values."
        ),
    )
    args = parser.parse_args()

    main(
        inputs=args.inputs,
        group_by=args.group_by,
        out_path=args.out,
        main_table=args.main_table,
    )
