"""
disagreement_cases.py   ->  place at  scripts/reporting/disagreement_cases.py

Extract questions where BM25 and dense DISAGREE on a hit, under a chosen binary
criterion / cutoff / corpus setting. This is the raw material for the
"when does dense beat BM25 / when does BM25 beat dense" analysis (a Week 3
expected output: results/disagreement_cases.csv).

Frozen / narrowed contract:
    docs/specs/2026-07-27-bm25-dense-reporting-contracts.md

AI-USAGE BOUNDARY:
  This is pure plumbing — validate the formal result CSVs, read the
  ALREADY-computed 0/1 hit columns, filter to disagreements, and emit them for
  inspection. It defines no metric (metric logic stays hand-written in
  src/evaluator.py) and makes no failure-category judgment. The one judgment
  that IS yours — WHAT rule counts as a "disagreement" — is exposed as CLI flags
  (--criterion/--k/--setting). The criterion is restricted to the two BINARY hit
  metrics (full/any); partial_evidence_recall is not a binary hit and is
  intentionally unsupported (it would require a separately approved non-binary
  contract). The classification/interpretation of each case is done by you,
  downstream.

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

from scripts.reporting.formal_result_inputs import (
    load_result_csv,
    validate_consumed_binary,
    validate_cross_method_identity,
    validate_setting,
    validate_structure,
)

# Only the two binary hit criteria are supported (see module docstring).
SUPPORTED_CRITERIA = ["full_evidence_recall", "any_evidence_recall"]

OUTPUT_COLUMNS = [
    "example_id", "setting", "question_type", "level", "question", "gold_titles",
    "criterion", "k", "bm25_hit", "dense_hit", "direction",
    "bm25_retrieved_titles", "dense_retrieved_titles",
]
# Extra rerank columns appended only when --with-rerank is set.
RERANK_COLUMNS = ["rerank_hit", "rerank_retrieved_titles"]

# Deterministic output order: direction, then question_type, then example_id.
_DIRECTION_ORDER = {"dense_only": 0, "bm25_only": 1}


def extract_disagreements(bm25, dense, criterion, k, setting, rerank=None):
    if criterion not in SUPPORTED_CRITERIA:
        raise ValueError(
            f"Unsupported criterion {criterion!r}; this binary tool supports "
            f"{SUPPORTED_CRITERIA} only."
        )
    # Refuse an unsupported setting before selecting rows: filtering by an
    # unknown value would otherwise leave an empty frame that satisfies every
    # cell check vacuously and is indistinguishable from a real zero-case run.
    validate_setting(setting)
    col = f"{criterion}@{k}"

    frames = {"bm25": bm25, "dense": dense}
    if rerank is not None:
        frames["rerank"] = rerank
    # Close the join before reading or converting any cell: per-file structure
    # (exact schema, uniform method, setting vocabulary, unique keys), the whole
    # typed metric contract on every one of the 22 (metric column, setting)
    # slots — required-empty/required-populated placement, genuine integer 0/1
    # binaries, finite [0,1] floats, applied to the bm25, dense, and optional
    # rerank frames alike and never coercing anything — identical id sets per
    # setting across methods, identical example metadata across every
    # (method, setting) row, and a present 0/1 value in each consumed cell.
    # `bm25`/`dense`/`rerank` may be frames a caller built in memory, so the
    # unconsumed columns are validated here rather than trusted.
    for method, frame in frames.items():
        validate_structure(frame, method, method)
    validate_cross_method_identity(frames)
    for method, frame in frames.items():
        validate_consumed_binary(frame, col, setting, method)

    b = bm25[bm25.setting == setting].set_index("example_id")
    d = dense[dense.setting == setting].set_index("example_id")
    r = (
        rerank[rerank.setting == setting].set_index("example_id")
        if rerank is not None else None
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
        if r is not None:
            # rerank cell already validated 0/1 above, so int() cannot silently
            # coerce a non-binary value.
            row["rerank_hit"] = int(r.loc[eid, col])
            row["rerank_retrieved_titles"] = r.loc[eid, "retrieved_titles"]
        rows.append(row)

    columns = OUTPUT_COLUMNS + (RERANK_COLUMNS if rerank is not None else [])
    df = pd.DataFrame(rows, columns=columns)
    # Deterministic order so reruns on the same bundle are byte-stable.
    return df.sort_values(
        by=["direction", "question_type", "example_id"],
        key=lambda s: s.map(_DIRECTION_ORDER) if s.name == "direction" else s,
    ).reset_index(drop=True)


def main(bm25_path, dense_path, rerank_path, criterion, k, setting, out_path):
    bm25 = load_result_csv(bm25_path, "bm25")
    dense = load_result_csv(dense_path, "dense")
    rerank = load_result_csv(rerank_path, "rerank") if rerank_path else None

    df = extract_disagreements(bm25, dense, criterion, k, setting, rerank=rerank)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False)

    n_dense_only = int((df.direction == "dense_only").sum())
    n_bm25_only = int((df.direction == "bm25_only").sum())
    print(f"Rule: {criterion}@{k}, setting={setting}")
    print(f"Disagreements: {len(df)}  (dense_only={n_dense_only}, bm25_only={n_bm25_only})")
    if len(df):
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
                   choices=SUPPORTED_CRITERIA)
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
