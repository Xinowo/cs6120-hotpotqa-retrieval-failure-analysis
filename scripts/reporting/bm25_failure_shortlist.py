"""
bm25_failure_shortlist.py   ->  place at  scripts/reporting/bm25_failure_shortlist.py

Surface BM25 failure candidates for the qualitative analysis (Week 3: find
lexical-mismatch and distractor-entity examples). Emits a ranked shortlist so
the strongest teaching cases float to the top.

Two candidate categories are surfaced under a chosen criterion / cutoff /
setting (default: pooled full_evidence_recall@5):

  - lexical_mismatch : BM25 misses the full evidence but DENSE finds it. The
                       natural reading is that evidence wording diverges from
                       the question wording, so lexical overlap fails where
                       semantics succeed.
  - distractor_entity: BM25 misses AND none of the gold titles appear in BM25's
                       own top-2, i.e. it confidently ranked wrong-but-similar
                       passages above the evidence.

AI-USAGE BOUNDARY:
  Pure plumbing — this filters and sorts ALREADY-computed hit columns from the
  formal result CSVs and joins on titles for context. It defines no metric and
  makes NO final failure-category judgment: the columns are named
  `category_candidate` precisely because they are candidate signals, not
  verdicts. The actual classification and the written failure analysis are done
  by a team member downstream. A case can legitimately appear in both lists.

Usage:
    python scripts/reporting/bm25_failure_shortlist.py
    python scripts/reporting/bm25_failure_shortlist.py --k 2 --per-category 20
    python scripts/reporting/bm25_failure_shortlist.py --setting per_question --k 2
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd

from src.results_schema import RESULT_COLUMNS, TITLE_SEPARATOR

OUTPUT_COLUMNS = [
    "example_id", "category_candidate", "question_type", "level", "question",
    "gold_titles", "bm25_top5", "dense_top5",
    "bm25_hit", "dense_hit", "bm25_gold_found", "n_gold",
]


def _load(path, expected_method):
    df = pd.read_csv(path)
    if list(df.columns) != RESULT_COLUMNS:
        raise ValueError(f"{path}: columns do not match RESULT_COLUMNS.")
    methods = set(df["method"].unique())
    if methods != {expected_method}:
        raise ValueError(f"{path}: expected method {expected_method!r}, got {methods}.")
    return df


def _titles(cell, n=None):
    parts = str(cell).split(TITLE_SEPARATOR)
    return parts[:n] if n is not None else parts


def _make_row(eid, category, b_row, d_row):
    gold = set(_titles(b_row["gold_titles"]))
    bm25_all = _titles(b_row["retrieved_titles"])
    return {
        "example_id": eid,
        "category_candidate": category,
        "question_type": b_row["question_type"],
        "level": b_row["level"],
        "question": b_row["question"],
        "gold_titles": b_row["gold_titles"],
        "bm25_top5": TITLE_SEPARATOR.join(_titles(b_row["retrieved_titles"], 5)),
        "dense_top5": TITLE_SEPARATOR.join(_titles(d_row["retrieved_titles"], 5)),
        "bm25_hit": int(b_row[COL]),
        "dense_hit": int(d_row[COL]),
        # how many gold titles BM25 found ANYWHERE in its stored list (context
        # for how badly it missed): 0 = cleanest mismatch/distractor case.
        "bm25_gold_found": sum(1 for t in bm25_all if t in gold),
        "n_gold": len(gold),
    }


def build_shortlist(bm25, dense, criterion, k, setting, per_category):
    global COL
    COL = f"{criterion}@{k}"

    b = bm25[bm25.setting == setting].set_index("example_id")
    d = dense[dense.setting == setting].set_index("example_id")
    if set(b.index) != set(d.index):
        raise ValueError("BM25 and dense example_id sets differ for this setting.")

    consumed = pd.concat([b[COL], d[COL]])
    if consumed.isna().any() or not consumed.isin([0, 1]).all():
        raise ValueError(
            f"{COL} is empty or non-0/1 in setting {setting!r} "
            f"(is this a valid criterion/cutoff for this setting?)."
        )

    lexical, distractor = [], []
    for eid in b.index:
        b_row = b.loc[eid]
        if b_row[COL] != 0:
            continue  # only BM25 misses are failure candidates
        d_row = d.loc[eid]
        # Category A: dense rescues what BM25 missed -> lexical-mismatch signal.
        if d_row[COL] == 1:
            lexical.append(_make_row(eid, "lexical_mismatch", b_row, d_row))
        # Category B: no gold in BM25's own top-2 -> distractor-entity signal.
        gold = set(_titles(b_row["gold_titles"]))
        if not (set(_titles(b_row["retrieved_titles"], 2)) & gold):
            distractor.append(_make_row(eid, "distractor_entity", b_row, d_row))

    # Rank each category so the cleanest cases (BM25 found the fewest gold
    # titles) come first, then group bridge/comparison together deterministically.
    def rank(rows):
        return sorted(rows, key=lambda r: (r["bm25_gold_found"], r["question_type"], r["example_id"]))

    lexical, distractor = rank(lexical), rank(distractor)
    shortlist = lexical[:per_category] + distractor[:per_category]
    return pd.DataFrame(shortlist, columns=OUTPUT_COLUMNS), len(lexical), len(distractor)


def main(bm25_path, dense_path, criterion, k, setting, per_category, out_path):
    bm25 = _load(bm25_path, "bm25")
    dense = _load(dense_path, "dense")
    df, n_lex, n_dis = build_shortlist(bm25, dense, criterion, k, setting, per_category)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False)

    print(f"Rule: {criterion}@{k}, setting={setting}")
    print(f"Total candidates found: lexical_mismatch={n_lex}, distractor_entity={n_dis}")
    print(f"Shortlisted (top {per_category} each): {len(df)} rows -> {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Surface BM25 failure-example candidates.")
    p.add_argument("--bm25", default="results/bm25_results.csv")
    p.add_argument("--dense", default="results/dense_results.csv")
    p.add_argument("--criterion", default="full_evidence_recall",
                   choices=["full_evidence_recall", "any_evidence_recall",
                            "partial_evidence_recall"])
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--setting", default="pooled", choices=["pooled", "per_question"])
    p.add_argument("--per-category", type=int, default=15,
                   help="How many candidates to keep per category.")
    p.add_argument("--out", default="results/bm25_failure_shortlist.csv")
    args = p.parse_args()

    main(
        bm25_path=args.bm25, dense_path=args.dense,
        criterion=args.criterion, k=args.k, setting=args.setting,
        per_category=args.per_category, out_path=args.out,
    )
