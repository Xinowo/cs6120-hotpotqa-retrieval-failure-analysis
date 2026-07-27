"""
disagreement_cases.py   ->  place at  scripts/reporting/disagreement_cases.py

Extract questions where BM25 and dense DISAGREE on a hit, under a chosen binary
criterion / cutoff / corpus setting. This is the raw material for the
"when does dense beat BM25 / when does BM25 beat dense" analysis (a Week 3
expected output: results/disagreement_cases.csv).

AI-USAGE BOUNDARY:
  This is pure plumbing — join the formal result CSVs, read the ALREADY-computed
  0/1 hit columns, filter to disagreements, and emit them for inspection. It
  defines no metric (metric logic stays hand-written in src/evaluator.py) and
  makes no failure-category judgment. The one judgment that IS yours — WHAT rule
  counts as a "disagreement" — is exposed as CLI flags (--criterion/--k/--setting),
  defaulting to the sensible pooled full_evidence_recall@5 choice. Change the
  flags to slice differently; the classification/interpretation of each case is
  done by you, downstream.

Usage:
    python scripts/reporting/disagreement_cases.py
    python scripts/reporting/disagreement_cases.py --criterion any_evidence_recall --k 5
    python scripts/reporting/disagreement_cases.py --setting per_question --k 2
    python scripts/reporting/disagreement_cases.py --with-rerank
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd

from src.results_schema import RESULT_COLUMNS

OUTPUT_COLUMNS = [
    "example_id", "setting", "question_type", "level", "question", "gold_titles",
    "criterion", "k", "bm25_hit", "dense_hit", "direction",
    "bm25_retrieved_titles", "dense_retrieved_titles",
]
# Extra rerank columns appended only when --with-rerank is set.
RERANK_COLUMNS = ["rerank_hit", "rerank_retrieved_titles"]


def _load(path, expected_method):
    df = pd.read_csv(path)
    if list(df.columns) != RESULT_COLUMNS:
        raise ValueError(f"{path}: columns do not match RESULT_COLUMNS.")
    methods = set(df["method"].unique())
    if methods != {expected_method}:
        raise ValueError(f"{path}: expected method {expected_method!r}, got {methods}.")
    return df


def extract_disagreements(bm25, dense, criterion, k, setting, rerank=None):
    col = f"{criterion}@{k}"
    b = bm25[bm25.setting == setting].set_index("example_id")
    d = dense[dense.setting == setting].set_index("example_id")

    if set(b.index) != set(d.index):
        raise ValueError("BM25 and dense example_id sets differ for this setting.")

    consumed = pd.concat([b[col], d[col]])
    if not consumed.dropna().isin([0, 1]).all() or consumed.isna().any():
        raise ValueError(
            f"{col} is empty or non-0/1 in setting {setting!r} "
            f"(is this a valid criterion/cutoff for this setting?)."
        )

    rows = []
    for eid in b.index:
        bm25_hit = int(b.loc[eid, col])
        dense_hit = int(d.loc[eid, col])
        if bm25_hit == dense_hit:
            continue  # agreement — not a disagreement case
        row = {
            "example_id": eid,
            "setting": setting,
            "question_type": b.loc[eid, "question_type"],
            "level": b.loc[eid, "level"],
            "question": b.loc[eid, "question"],
            "gold_titles": b.loc[eid, "gold_titles"],
            "criterion": criterion,
            "k": k,
            "bm25_hit": bm25_hit,
            "dense_hit": dense_hit,
            "direction": "dense_only" if dense_hit else "bm25_only",
            "bm25_retrieved_titles": b.loc[eid, "retrieved_titles"],
            "dense_retrieved_titles": d.loc[eid, "retrieved_titles"],
        }
        if rerank is not None:
            r = rerank[rerank.setting == setting].set_index("example_id")
            row["rerank_hit"] = int(r.loc[eid, col])
            row["rerank_retrieved_titles"] = r.loc[eid, "retrieved_titles"]
        rows.append(row)

    columns = OUTPUT_COLUMNS + (RERANK_COLUMNS if rerank is not None else [])
    return pd.DataFrame(rows, columns=columns)


def main(bm25_path, dense_path, rerank_path, criterion, k, setting, out_path):
    bm25 = _load(bm25_path, "bm25")
    dense = _load(dense_path, "dense")
    rerank = _load(rerank_path, "rerank") if rerank_path else None

    df = extract_disagreements(bm25, dense, criterion, k, setting, rerank=rerank)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False)

    n_dense_only = int((df.direction == "dense_only").sum())
    n_bm25_only = int((df.direction == "bm25_only").sum())
    print(f"Rule: {criterion}@{k}, setting={setting}")
    print(f"Disagreements: {len(df)}  (dense_only={n_dense_only}, bm25_only={n_bm25_only})")
    print(f"By question_type:\n{df.groupby(['question_type', 'direction']).size()}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Extract BM25-vs-dense hit disagreements.")
    p.add_argument("--bm25", default="results/bm25_results.csv")
    p.add_argument("--dense", default="results/dense_results.csv")
    p.add_argument("--with-rerank", action="store_true",
                   help="Also include the reranker's hit/titles per case.")
    p.add_argument("--rerank", default="results/rerank_results.csv")
    p.add_argument("--criterion", default="full_evidence_recall",
                   choices=["full_evidence_recall", "any_evidence_recall",
                            "partial_evidence_recall"])
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--setting", default="pooled", choices=["pooled", "per_question"])
    p.add_argument("--out", default="results/disagreement_cases.csv")
    args = p.parse_args()

    main(
        bm25_path=args.bm25, dense_path=args.dense,
        rerank_path=args.rerank if args.with_rerank else None,
        criterion=args.criterion, k=args.k, setting=args.setting,
        out_path=args.out,
    )
