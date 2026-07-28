"""
bm25_failure_shortlist.py   ->  scripts/reporting/bm25_failure_shortlist.py

Surface BM25 failure candidates for qualitative review as a NEUTRAL, mechanical
shortlist. This tool exports OBSERVABLE SIGNALS only; it assigns no causal
failure category.

Under the accepted failure-review boundary
(docs/specs/2026-07-12-failure-review-pipeline-design.md §1), judging a cause
such as lexical mismatch requires reading the gold and retrieved paragraph text
side by side, because the result CSV metrics/titles are too high-level. Under
the notes-first manual protocol boundary
(docs/specs/2026-07-27-manual-failure-review-course-protocol.md §2, "Stable
boundaries"), no system or agent pre-fills a causal label. This script therefore
emits only what the result CSVs mechanically show; the human reviewer assigns
causes downstream.

Frozen / narrowed contract:
    docs/specs/2026-07-27-bm25-dense-reporting-contracts.md

Two mechanical signals are surfaced under a chosen criterion / cutoff / setting
(default: pooled full_evidence_recall@5). A case may carry either or both:

  - dense_hit_bm25_miss  : under the selected criterion@k, BM25 misses (hit=0)
                           while dense hits (hit=1). A purely mechanical
                           observation that the two retrievers diverged here.
  - bm25_no_gold_in_top2 : BM25 misses (hit=0) AND no gold title appears in
                           BM25's own stored top-2 titles. A purely mechanical
                           observation about where the gold titles landed.

Neither signal names or implies a cause.

AI-USAGE BOUNDARY:
  Pure plumbing — validate the formal result CSVs, filter/sort ALREADY-computed
  0/1 hit columns, and join stored titles for context. It defines no metric and
  makes NO failure-category judgment; `observed_signal` values are mechanical
  descriptors, not verdicts. The criterion is restricted to the two BINARY hit
  metrics (partial_evidence_recall is intentionally unsupported).

Usage:
    python scripts/reporting/bm25_failure_shortlist.py
    python scripts/reporting/bm25_failure_shortlist.py --k 2 --per-signal 20
    python scripts/reporting/bm25_failure_shortlist.py --setting per_question --k 2
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd

from src.results_schema import TITLE_SEPARATOR
from scripts.reporting.formal_result_inputs import (
    load_result_csv,
    validate_consumed_binary,
    validate_cross_method_identity,
    validate_setting,
    validate_structure,
)

# Only the two binary hit criteria are supported (see module docstring).
SUPPORTED_CRITERIA = ["full_evidence_recall", "any_evidence_recall"]

# Neutral, mechanical signal vocabulary (see module docstring). No causal names.
SIGNAL_DENSE_HIT_BM25_MISS = "dense_hit_bm25_miss"
SIGNAL_BM25_NO_GOLD_IN_TOP2 = "bm25_no_gold_in_top2"

OUTPUT_COLUMNS = [
    "example_id", "observed_signal", "setting", "criterion", "k",
    "question_type", "level", "question", "gold_titles",
    "bm25_top5", "dense_top5",
    "bm25_hit", "dense_hit", "bm25_gold_found", "n_gold",
]


def _titles(cell, n=None):
    """Split a stored title list into its titles.

    An empty cell is the approved serialization of an empty retrieved list and
    yields `[]`, not `['']`. A non-string cell refuses instead of being
    stringified: `str(NaN)` would otherwise fabricate the title `"nan"` and put
    it in a published artifact.
    """
    if not isinstance(cell, str):
        raise ValueError(
            f"stored title list must be a string, got {cell!r} "
            f"({type(cell).__name__}); a missing cell is never stringified into "
            f"a fabricated title."
        )
    if cell == "":
        return []
    parts = cell.split(TITLE_SEPARATOR)
    return parts[:n] if n is not None else parts


def _make_row(eid, signal, b_row, d_row, col, criterion, k, setting):
    gold = set(_titles(b_row["gold_titles"]))
    bm25_all = _titles(b_row["retrieved_titles"])
    # DISTINCT gold titles present anywhere in BM25's stored list — never the
    # number of retrieved occurrences, which a repeated title would inflate
    # past n_gold and which would also perturb the ranking key below.
    bm25_gold_found = len(gold & set(bm25_all))
    n_gold = len(gold)
    if not 0 <= bm25_gold_found <= n_gold:
        raise ValueError(
            f"{eid}: bm25_gold_found={bm25_gold_found} violates "
            f"0 <= bm25_gold_found <= n_gold={n_gold}."
        )
    return {
        "example_id": eid,
        "observed_signal": signal,
        "setting": setting,
        "criterion": criterion,
        "k": k,
        "question_type": b_row["question_type"],
        "level": b_row["level"],
        "question": b_row["question"],
        "gold_titles": b_row["gold_titles"],
        "bm25_top5": TITLE_SEPARATOR.join(_titles(b_row["retrieved_titles"], 5)),
        "dense_top5": TITLE_SEPARATOR.join(_titles(d_row["retrieved_titles"], 5)),
        "bm25_hit": int(b_row[col]),
        "dense_hit": int(d_row[col]),
        # how many gold titles BM25 found ANYWHERE in its stored list (mechanical
        # context for how far the gold landed): 0 = no gold anywhere in storage.
        "bm25_gold_found": bm25_gold_found,
        "n_gold": n_gold,
    }


def build_shortlist(bm25, dense, criterion, k, setting, per_signal):
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

    # Close the join before reading or converting any cell: per-file structure,
    # the whole typed metric contract on every one of the 22 (metric column,
    # setting) slots — required-empty/required-populated placement, genuine
    # integer 0/1 binaries, finite [0,1] floats, never coercing anything —
    # cross-method id parity + metadata identity, and 0/1 consumed cells.
    # `bm25`/`dense` may be frames a caller built in memory, so the unconsumed
    # columns are validated here rather than trusted.
    frames = {"bm25": bm25, "dense": dense}
    for method, frame in frames.items():
        validate_structure(frame, method, method)
    validate_cross_method_identity(frames)
    validate_consumed_binary(bm25, col, setting, "bm25")
    validate_consumed_binary(dense, col, setting, "dense")

    b = bm25[bm25.setting == setting].set_index("example_id")
    d = dense[dense.setting == setting].set_index("example_id")

    dense_hit_bm25_miss, bm25_no_gold_in_top2 = [], []
    for eid in b.index:
        b_row = b.loc[eid]
        if int(b_row[col]) != 0:
            continue  # only BM25 misses are failure candidates
        d_row = d.loc[eid]
        gold = set(_titles(b_row["gold_titles"]))
        # Signal A: the two retrievers diverged (dense hit, BM25 missed).
        if int(d_row[col]) == 1:
            dense_hit_bm25_miss.append(
                _make_row(eid, SIGNAL_DENSE_HIT_BM25_MISS, b_row, d_row,
                          col, criterion, k, setting)
            )
        # Signal B: no gold title in BM25's own stored top-2.
        if not (set(_titles(b_row["retrieved_titles"], 2)) & gold):
            bm25_no_gold_in_top2.append(
                _make_row(eid, SIGNAL_BM25_NO_GOLD_IN_TOP2, b_row, d_row,
                          col, criterion, k, setting)
            )

    # Rank each signal group deterministically: fewest gold titles found first,
    # then by question_type and example_id.
    def rank(rows):
        return sorted(
            rows,
            key=lambda r: (r["bm25_gold_found"], r["question_type"], r["example_id"]),
        )

    dense_hit_bm25_miss = rank(dense_hit_bm25_miss)
    bm25_no_gold_in_top2 = rank(bm25_no_gold_in_top2)
    shortlist = dense_hit_bm25_miss[:per_signal] + bm25_no_gold_in_top2[:per_signal]
    return (
        pd.DataFrame(shortlist, columns=OUTPUT_COLUMNS),
        len(dense_hit_bm25_miss),
        len(bm25_no_gold_in_top2),
    )


def main(bm25_path, dense_path, criterion, k, setting, per_signal, out_path):
    bm25 = load_result_csv(bm25_path, "bm25")
    dense = load_result_csv(dense_path, "dense")
    df, n_a, n_b = build_shortlist(bm25, dense, criterion, k, setting, per_signal)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False)

    print(f"Rule: {criterion}@{k}, setting={setting}")
    print(f"Signal counts: {SIGNAL_DENSE_HIT_BM25_MISS}={n_a}, "
          f"{SIGNAL_BM25_NO_GOLD_IN_TOP2}={n_b}")
    print(f"Shortlisted (top {per_signal} each): {len(df)} rows -> {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Surface neutral BM25 failure-candidate signals (no causal labels)."
    )
    p.add_argument("--bm25", default="results/bm25_results.csv")
    p.add_argument("--dense", default="results/dense_results.csv")
    p.add_argument("--criterion", default="full_evidence_recall",
                   choices=SUPPORTED_CRITERIA)
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--setting", default="pooled", choices=["pooled", "per_question"])
    p.add_argument("--per-signal", type=int, default=15,
                   help="How many candidates to keep per signal group.")
    p.add_argument("--out", default="results/bm25_failure_shortlist.csv")
    args = p.parse_args()

    main(
        bm25_path=args.bm25, dense_path=args.dense,
        criterion=args.criterion, k=args.k, setting=args.setting,
        per_signal=args.per_signal, out_path=args.out,
    )
