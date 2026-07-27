"""
rescue_damage.py   ->  place at  scripts/reporting/rescue_damage.py

Reranker rescue / damage summary.
Spec: docs/specs/2026-07-26-reranker-rescue-damage.md
Inputs:  results/dense_results.csv (stage 1), results/rerank_results.csv (stage 2)
Output:  results/rerank_rescue_damage.csv  (frozen 17-col / 21-row schema, §9)

Everything else here is the "surrounding infrastructure" the policy allows an
agent to generate:
    - load_and_validate_inputs()      §2 input fail-fast contract
    - build_paired_frame()            the mechanical one-to-one join
    - validate_output_schema()        §9.3 exact 21-row / key-set check
    - validate_summary_consistency()  §9.5 internal count/rate identities
    - oracle_check()                  §9.5 independent aggregate regression
    - write_rescue_damage_csv()       §9.1/§9.2/§9.4 serialization

Record this boundary in the AI Usage Declaration: the counting function is
hand-written; the validation/serialization/oracle plumbing is agent-generated.

Usage:
    python scripts/reporting/rescue_damage.py
    python scripts/reporting/rescue_damage.py \
        --dense results/dense_results.csv \
        --rerank results/rerank_results.csv \
        --out results/rerank_rescue_damage.csv
"""

import argparse
import math
import os
import sys

# Make both `from src...` and `import summarize_results` (sibling) importable,
# regardless of whether scripts/ is a package.
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, HERE)

import pandas as pd

from src.results_schema import RESULT_COLUMNS
# The independent oracle re-uses the general summarizer's group-mean path
# (a different code route than the counting below), exactly as §9.5 requires.
from summarize_results import summarize


# ── Frozen output contract (spec §9) — these are schema constants, not logic ──

OUTPUT_COLUMNS = [
    "criterion", "setting", "k", "question_type", "n",
    "dense_hits", "rerank_hits",
    "stable_miss", "rescues", "damages", "stable_hit",
    "rescue_rate", "damage_rate", "net_count", "net_rate",
    "rescue_given_dense_miss", "damage_given_dense_hit",
]

# The 7 valid (criterion, setting, k) combinations (§5, §9.3).
VALID_COMBINATIONS = [
    ("full_evidence_recall", "pooled", 2),
    ("full_evidence_recall", "pooled", 5),
    ("full_evidence_recall", "pooled", 10),
    ("full_evidence_recall", "per_question", 2),
    ("full_evidence_recall", "per_question", 5),
    ("any_evidence_recall", "pooled", 5),
    ("any_evidence_recall", "per_question", 5),
]

QUESTION_TYPE_GROUPS = ["overall", "bridge", "comparison"]  # §7

# Deterministic sort keys (§9.4).
_CRITERION_ORDER = {"full_evidence_recall": 0, "any_evidence_recall": 1}
_SETTING_ORDER = {"pooled": 0, "per_question": 1}
_QTYPE_ORDER = {"overall": 0, "bridge": 1, "comparison": 2}

INTEGER_COLUMNS = [
    "k", "n", "dense_hits", "rerank_hits",
    "stable_miss", "rescues", "damages", "stable_hit", "net_count",
]
RATE_COLUMNS = [
    "rescue_rate", "damage_rate", "net_rate",
    "rescue_given_dense_miss", "damage_given_dense_hit",
]

_META_COLUMNS = ["question_type", "level", "question", "gold_titles"]
_JOIN_KEYS = ["setting", "example_id"] + _META_COLUMNS


# ─────────────────────────── §2  INPUT CONTRACT ──────────────────────────────

def _validate_one_file(df, source, expected_method):
    """Per-file structural contract (§2). Fail-fast on any violation."""
    if list(df.columns) != RESULT_COLUMNS:
        raise ValueError(f"{source}: columns do not match RESULT_COLUMNS exactly.")

    methods = set(df["method"].unique())
    if methods != {expected_method}:
        raise ValueError(
            f"{source}: expected method uniformly {expected_method!r}, got {methods}."
        )

    settings = set(df["setting"].unique())
    if settings != {"pooled", "per_question"}:
        raise ValueError(
            f"{source}: setting vocabulary must be exactly "
            f"{{'pooled','per_question'}}, got {settings}."
        )

    counts = df.groupby("setting")["example_id"].agg(["size", "nunique"])
    for setting, row in counts.iterrows():
        if row["size"] != row["nunique"]:
            raise ValueError(
                f"{source}: duplicate example_id within setting {setting!r} "
                f"({row['size']} rows, {row['nunique']} unique)."
            )
    if set(df[df.setting == "pooled"].example_id) != set(
        df[df.setting == "per_question"].example_id
    ):
        raise ValueError(f"{source}: pooled and per_question ID sets differ (§2).")

    # Consumed-cell contract (§2): every cell we will actually read must be 0/1;
    # per_question @10 recall cells must stay blank (never consumed).
    for criterion, setting, k in VALID_COMBINATIONS:
        col = f"{criterion}@{k}"
        cells = df[df.setting == setting][col]
        if not cells.isin([0, 1]).all():
            raise ValueError(
                f"{source}: consumed cell {col} in setting {setting!r} "
                f"has empty or non-0/1 values (§2)."
            )
    pq = df[df.setting == "per_question"]
    for col in ("any_evidence_recall@10", "full_evidence_recall@10",
                "partial_evidence_recall@10"):
        if not pq[col].isna().all():
            raise ValueError(
                f"{source}: per_question {col} must be blank (K policy, §2)."
            )


def _validate_cross(dense, rerank):
    """Cross-file / cross-setting identity contract (§2)."""
    for setting in ("pooled", "per_question"):
        di = set(dense[dense.setting == setting].example_id)
        ri = set(rerank[rerank.setting == setting].example_id)
        if di != ri:
            raise ValueError(
                f"Cross-method ID drift in setting {setting!r}: dense vs rerank "
                f"ID sets differ (breaks the one-to-one join, §2)."
            )

    # Each example_id's metadata must be identical across all four
    # (method, setting) rows — binds across both methods AND both settings.
    combined = pd.concat([dense, rerank], ignore_index=True)
    nunique = combined.groupby("example_id")[_META_COLUMNS].nunique()
    drift = nunique[(nunique > 1).any(axis=1)]
    if not drift.empty:
        raise ValueError(
            f"Same-example_id metadata drift across (method, setting) rows for "
            f"{len(drift)} id(s), e.g. {list(drift.index[:3])} (§2)."
        )


def load_and_validate_inputs(dense_path, rerank_path):
    """Load both formal result CSVs and enforce the full §2 contract."""
    dense = pd.read_csv(dense_path)
    rerank = pd.read_csv(rerank_path)
    _validate_one_file(dense, dense_path, expected_method="dense")
    _validate_one_file(rerank, rerank_path, expected_method="rerank")
    _validate_cross(dense, rerank)
    return dense, rerank


def build_paired_frame(dense, rerank):
    """One-to-one join on (setting, example_id) — mechanical, no judgment.

    Returns one row per (setting, example_id) carrying the shared metadata
    (question_type, level, question, gold_titles) plus every metric column
    from BOTH stages, suffixed `_dense` / `_rerank`.  So for any criterion c
    and cutoff k you read the paired hit outcome from:

        f"{c}@{k}_dense"    and    f"{c}@{k}_rerank"

    Both are 0/1 for the valid (criterion, setting, k) combinations, since
    load_and_validate_inputs already enforced that.
    """
    merged = dense.merge(
        rerank, on=_JOIN_KEYS, suffixes=("_dense", "_rerank"), validate="one_to_one"
    )
    if len(merged) != len(dense):
        raise ValueError(
            f"Join was not one-to-one: {len(dense)} left rows -> {len(merged)} "
            f"merged rows (check the §2 contract)."
        )
    return merged


def summarize_rescue_damage(paired: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize reranker rescue and damage statistics for every valid evaluation
    configuration.

    The input is a one-to-one joined DataFrame containing the dense retrieval
    results and reranker results for the same question. For each valid
    (criterion, setting, k) combination and each question type, every question
    is classified into one of four mutually exclusive categories:

        - stable_miss : dense = 0, rerank = 0
        - rescue      : dense = 0, rerank = 1
        - damage      : dense = 1, rerank = 0
        - stable_hit  : dense = 1, rerank = 1

    The function then aggregates these counts and computes the derived metrics
    defined in §9.5 of the specification, including hit counts, rescue/damage
    rates, net improvement, and conditional rescue/damage rates.

    Parameters
    ----------
    paired : pd.DataFrame
        Output of build_paired_frame(), containing one row per
        (setting, example_id) with both dense and reranker evaluation columns.

    Returns
    -------
    pd.DataFrame
        A 21-row summary DataFrame following the exact OUTPUT_COLUMNS schema.
        Each row corresponds to one
        (criterion, setting, k, question_type) combination.
    """

    rows = []

    # Iterate through every valid evaluation configuration defined in the spec.
    for criterion, setting, k in VALID_COMBINATIONS:

        # Restrict the paired results to the requested retrieval setting.
        setting_df = paired[paired["setting"] == setting]

        # Produce one summary for overall, bridge, and comparison questions.
        for question_type in QUESTION_TYPE_GROUPS:

            if question_type == "overall":
                # Overall includes every question in the current setting.
                group = setting_df
            else:
                # Bridge/comparison summaries are computed independently.
                group = setting_df[
                    setting_df["question_type"] == question_type
                ]

            # Binary hit columns for the selected metric.
            dense_col = f"{criterion}@{k}_dense"
            rerank_col = f"{criterion}@{k}_rerank"

            n = len(group)

            # Four mutually exclusive transition categories.
            stable_miss = 0
            rescues = 0
            damages = 0
            stable_hit = 0

            # Compare dense and reranker outcomes question-by-question.
            for _, row in group.iterrows():

                dense_hit = row[dense_col]
                rerank_hit = row[rerank_col]

                if dense_hit == 0 and rerank_hit == 0:
                    stable_miss += 1

                elif dense_hit == 0 and rerank_hit == 1:
                    rescues += 1

                elif dense_hit == 1 and rerank_hit == 0:
                    damages += 1

                elif dense_hit == 1 and rerank_hit == 1:
                    stable_hit += 1

                else:
                    # Input validation should prevent illegal values.
                    raise ValueError(
                        f"Illegal hit pair ({dense_hit}, {rerank_hit})"
                    )

            # Recover dense/reranker hit totals from the transition counts.
            dense_hits = damages + stable_hit
            rerank_hits = rescues + stable_hit

            # Overall rescue/damage frequencies.
            rescue_rate = rescues / n
            damage_rate = damages / n

            # Net improvement introduced by reranking.
            net_count = rescues - damages
            net_rate = net_count / n

            # Conditional rescue denominator equals the number of dense misses.
            dense_misses = n - dense_hits

            # Follow the spec: use NaN (written as blank CSV cells) when the
            # denominator is zero.
            if dense_misses == 0:
                rescue_given_dense_miss = float("nan")
            else:
                rescue_given_dense_miss = rescues / dense_misses

            if dense_hits == 0:
                damage_given_dense_hit = float("nan")
            else:
                damage_given_dense_hit = damages / dense_hits

            # Store one summary row for this evaluation configuration.
            rows.append(
                {
                    "criterion": criterion,
                    "setting": setting,
                    "k": k,
                    "question_type": question_type,
                    "n": n,
                    "dense_hits": dense_hits,
                    "rerank_hits": rerank_hits,
                    "stable_miss": stable_miss,
                    "rescues": rescues,
                    "damages": damages,
                    "stable_hit": stable_hit,
                    "rescue_rate": rescue_rate,
                    "damage_rate": damage_rate,
                    "net_count": net_count,
                    "net_rate": net_rate,
                    "rescue_given_dense_miss": rescue_given_dense_miss,
                    "damage_given_dense_hit": damage_given_dense_hit,
                }
            )

    # Return the unsorted summary. Ordering and formatting are handled later by
    # write_rescue_damage_csv().
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)

# ───────────────────────── §9.3/§9.5  OUTPUT CHECKS ──────────────────────────

def validate_output_schema(summary):
    """§9.3: exactly the 17 columns and the 21-row key set, no more/less."""
    if list(summary.columns) != OUTPUT_COLUMNS:
        raise ValueError(
            f"Output columns must be exactly OUTPUT_COLUMNS in order; got "
            f"{list(summary.columns)}."
        )
    expected_keys = {
        (c, s, k, q)
        for (c, s, k) in VALID_COMBINATIONS
        for q in QUESTION_TYPE_GROUPS
    }
    actual_keys = set(
        zip(summary.criterion, summary.setting, summary.k, summary.question_type)
    )
    if actual_keys != expected_keys:
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys
        raise ValueError(f"21-row key set wrong. missing={missing} extra={extra}")
    if len(summary) != 21:
        raise ValueError(f"Expected exactly 21 rows, got {len(summary)}.")


def validate_summary_consistency(summary):
    """§9.5: every group must satisfy the count and rate identities."""
    for _, r in summary.iterrows():
        tag = (r.criterion, r.setting, r.k, r.question_type)
        n, dh, rh = r.n, r.dense_hits, r.rerank_hits
        sm, res, dam, sh = r.stable_miss, r.rescues, r.damages, r.stable_hit

        if n != sm + res + dam + sh:
            raise ValueError(f"{tag}: n != stable_miss+rescues+damages+stable_hit")
        if dh != dam + sh:
            raise ValueError(f"{tag}: dense_hits != damages+stable_hit")
        if rh != res + sh:
            raise ValueError(f"{tag}: rerank_hits != rescues+stable_hit")
        if r.net_count != res - dam:
            raise ValueError(f"{tag}: net_count != rescues-damages")

        def close(a, b):
            return math.isclose(a, b, rel_tol=0.0, abs_tol=1e-9)

        if not close(r.rescue_rate, res / n):
            raise ValueError(f"{tag}: rescue_rate identity failed")
        if not close(r.damage_rate, dam / n):
            raise ValueError(f"{tag}: damage_rate identity failed")
        if not close(r.net_rate, r.net_count / n):
            raise ValueError(f"{tag}: net_rate identity failed")

        # Conditional rates: blank on zero denominator (§9.2), else the ratio.
        if n - dh == 0:
            if pd.notna(r.rescue_given_dense_miss):
                raise ValueError(f"{tag}: rescue_given_dense_miss must be blank")
        elif not close(r.rescue_given_dense_miss, res / (n - dh)):
            raise ValueError(f"{tag}: rescue_given_dense_miss identity failed")
        if dh == 0:
            if pd.notna(r.damage_given_dense_hit):
                raise ValueError(f"{tag}: damage_given_dense_hit must be blank")
        elif not close(r.damage_given_dense_hit, dam / dh):
            raise ValueError(f"{tag}: damage_given_dense_hit identity failed")


def oracle_check(summary, dense, rerank):
    """§9.5 independent oracle: net_rate must equal (rerank_mean - dense_mean)
    of the raw {criterion}@{k} column, computed via summarize() — a separate
    code path that re-averages the accepted inputs, never the counts above."""
    combined = pd.concat([dense, rerank], ignore_index=True)
    overall = summarize(combined, ["method", "setting"])
    by_type = summarize(combined, ["method", "setting", "question_type"])

    for _, r in summary.iterrows():
        col = f"{r.criterion}@{r.k}"
        if r.question_type == "overall":
            sel = overall[overall.setting == r.setting]
        else:
            sel = by_type[
                (by_type.setting == r.setting)
                & (by_type.question_type == r.question_type)
            ]
        dmean = float(sel[sel.method == "dense"][col].iloc[0])
        rmean = float(sel[sel.method == "rerank"][col].iloc[0])
        expected = rmean - dmean
        if not math.isclose(r.net_rate, expected, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError(
                f"Oracle mismatch at {(r.criterion, r.setting, r.k, r.question_type)}: "
                f"net_rate={r.net_rate!r} but rerank_mean-dense_mean={expected!r}."
            )


# ─────────────────────────── §9.1/§9.4  WRITER ───────────────────────────────

def write_rescue_damage_csv(summary, out_path):
    """Serialize to the frozen schema: exact column order (§9.1), deterministic
    row order (§9.4), integer counts, full-precision rates (§9.2), blank cells
    for NaN conditional rates."""
    df = summary.copy()
    df = df[OUTPUT_COLUMNS]
    df = df.assign(
        _c=df.criterion.map(_CRITERION_ORDER),
        _s=df.setting.map(_SETTING_ORDER),
        _q=df.question_type.map(_QTYPE_ORDER),
    ).sort_values(["_c", "_s", "k", "_q"]).drop(columns=["_c", "_s", "_q"])

    for col in INTEGER_COLUMNS:
        df[col] = df[col].astype("int64")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    # float_format=None -> full-precision repr; NaN -> empty field by default.
    df.to_csv(out_path, index=False, float_format=None)


def main(dense_path, rerank_path, out_path):
    dense, rerank = load_and_validate_inputs(dense_path, rerank_path)
    print(f"Inputs pass the §2 contract: {len(dense)} dense + {len(rerank)} rerank rows.")

    paired = build_paired_frame(dense, rerank)
    summary = summarize_rescue_damage(paired)   # <- your hand-written core

    validate_output_schema(summary)
    validate_summary_consistency(summary)
    oracle_check(summary, dense, rerank)
    print("Output passes §9.3 schema, §9.5 identities, and the independent oracle.")

    write_rescue_damage_csv(summary, out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Reranker rescue/damage summary (spec 2026-07-26).")
    p.add_argument("--dense", default="results/dense_results.csv")
    p.add_argument("--rerank", default="results/rerank_results.csv")
    p.add_argument("--out", default="results/rerank_rescue_damage.csv")
    args = p.parse_args()
    main(args.dense, args.rerank, args.out)
