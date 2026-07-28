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

import numpy as np
import pandas as pd

from src.results_schema import RESULT_COLUMNS
# Shared physical input domains (structure-level plumbing only): the same
# strict metadata/consumed-cell predicates the BM25-vs-dense reporting tools
# use, so the two paths cannot drift apart in what they accept.
from scripts.reporting.formal_result_inputs import (
    META_COLUMNS,
    read_formal_result_csv,
    validate_consumed_binary,
    validate_metadata_domains,
    validate_typed_metric_frame,
)
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

_JOIN_KEYS = ["setting", "example_id"] + META_COLUMNS


# ─────────────────────────── §2  INPUT CONTRACT ──────────────────────────────

def _validate_one_file(df, source, expected_method):
    """Per-file structural contract (§2). Fail-fast on any violation."""
    if list(df.columns) != RESULT_COLUMNS:
        raise ValueError(f"{source}: columns do not match RESULT_COLUMNS exactly.")

    # Closed upstream value domains: required metadata is non-null text, and
    # question_type / level stay inside the shared schema's vocabularies.
    validate_metadata_domains(df, source)

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

    # Frozen cardinality (§2): exactly 1000 rows = 500 pooled + 500 per_question.
    if len(df) != 1000:
        raise ValueError(
            f"{source}: expected exactly 1000 rows (§2), got {len(df)}."
        )
    for setting in ("pooled", "per_question"):
        sub = df[df.setting == setting]
        if len(sub) != 500:
            raise ValueError(
                f"{source}: setting {setting!r} must have exactly 500 rows (§2), "
                f"got {len(sub)}."
            )
        # Frozen §7 group counts (overall=500, bridge=404, comparison=96),
        # checked before counting so a partial/malformed run cannot be
        # published and the bridge/comparison subgroups always partition the
        # population. The closed question_type vocabulary itself was already
        # enforced above by validate_metadata_domains.
        counts = sub["question_type"].value_counts()
        n_bridge, n_comparison = int(counts.get("bridge", 0)), int(counts.get("comparison", 0))
        if n_bridge != 404 or n_comparison != 96:
            raise ValueError(
                f"{source}: setting {setting!r} question_type counts must be "
                f"bridge=404, comparison=96 (§7), got bridge={n_bridge}, "
                f"comparison={n_comparison}."
            )

    # Consumed-cell contract (§2): every cell we will actually read must be a
    # plain integer 0/1 (bool, float 0.0/1.0, numeric string, and empty cells
    # are refused before any int() conversion); per_question @10 recall cells
    # must stay blank (never consumed).
    for criterion, setting, k in VALID_COMBINATIONS:
        validate_consumed_binary(df, f"{criterion}@{k}", setting, source)
    pq = df[df.setting == "per_question"]
    for col in ("any_evidence_recall@10", "full_evidence_recall@10",
                "partial_evidence_recall@10"):
        if not pq[col].isna().all():
            raise ValueError(
                f"{source}: per_question {col} must be blank (K policy, §2)."
            )

    # The shared typed-frame metric contract, run last so the rescue-specific
    # messages above keep reporting the defects they name. It adds the other
    # half of the same rule for a frame that never passed the shared reader:
    # every other metric slot must be populated, every populated binary cell
    # must be a genuine integer 0/1, and every partial/reciprocal-rank cell must
    # be numeric, finite, and in [0, 1] — for the columns this counting never
    # reads as well as the seven it does.
    validate_typed_metric_frame(df, source)


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
    # Missing values participate in the comparison, so a value present on one
    # side and absent on the other counts as drift instead of being ignored.
    combined = pd.concat([dense, rerank], ignore_index=True)
    nunique = combined.groupby("example_id", dropna=False)[META_COLUMNS].nunique(
        dropna=False
    )
    drift = nunique[(nunique > 1).any(axis=1)]
    if not drift.empty:
        raise ValueError(
            f"Same-example_id metadata drift across (method, setting) rows for "
            f"{len(drift)} id(s), e.g. {list(drift.index[:3])} (§2)."
        )


def load_and_validate_inputs(dense_path, rerank_path):
    """Load both formal result CSVs and enforce the full §2 contract."""
    dense = read_formal_result_csv(dense_path)
    rerank = read_formal_result_csv(rerank_path)
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

    This is a public function that accepts already-created result frames, so it
    re-applies the shared typed metric contract to both of them rather than
    trusting its caller: a frame built or mutated in memory must satisfy the
    same placement, integer-binary, and `[0,1]` invariants as one that came
    through the reader, before any join or count can consume it.
    """
    validate_typed_metric_frame(dense, "dense")
    validate_typed_metric_frame(rerank, "rerank")
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

    # §7 partition: for each (criterion, setting, k) the overall row's n must
    # equal bridge + comparison, so the subgroups always partition the group.
    for (crit, setting, k), grp in summary.groupby(
        ["criterion", "setting", "k"], sort=False
    ):
        by_q = grp.set_index("question_type")["n"]
        if int(by_q["overall"]) != int(by_q["bridge"]) + int(by_q["comparison"]):
            raise ValueError(
                f"({crit}, {setting}, {k}): overall n={int(by_q['overall'])} "
                f"!= bridge {int(by_q['bridge'])} + comparison "
                f"{int(by_q['comparison'])} (partition broken)."
            )


def _is_plain_int(value):
    """True only for a genuine integer scalar (excludes bool, float, string)."""
    return isinstance(value, (int, np.integer)) and not isinstance(value, bool)


def _is_real_float(value):
    """True only for a real float scalar (excludes bool)."""
    return isinstance(value, (float, np.floating)) and not isinstance(value, bool)


def validate_output_types_and_ranges(summary):
    """§9.2 physical contract, enforced BEFORE any serialization/coercion.

    - integer columns are plain integers (not bool, float, or numeric string);
    - counts are >= 0, except `net_count` which may be negative;
    - rate columns are finite floats in range ([0,1], `net_rate` in [-1,1]);
    - a conditional rate is blank (NaN) exactly on a zero denominator, and a
      finite in-range float otherwise.

    This never truncates: it refuses a non-compliant frame so the writer cannot
    coerce (e.g. `int(0.5)`) a defective value into a contract-invalid CSV.
    """
    non_negative_int = [c for c in INTEGER_COLUMNS if c != "net_count"]

    for col in INTEGER_COLUMNS:
        for value in summary[col].tolist():
            if not _is_plain_int(value):
                raise ValueError(
                    f"integer column {col!r} has a non-integer value "
                    f"{value!r} (type {type(value).__name__}); §9.2 requires "
                    f"plain integers."
                )
    for col in non_negative_int:
        for value in summary[col].tolist():
            if int(value) < 0:
                raise ValueError(
                    f"count column {col!r} is negative ({value!r}); only "
                    f"net_count may be negative (§9.2)."
                )

    _ATOL = 1e-9
    always_rates = {
        "rescue_rate": (0.0, 1.0),
        "damage_rate": (0.0, 1.0),
        "net_rate": (-1.0, 1.0),
    }
    for col, (lo, hi) in always_rates.items():
        for value in summary[col].tolist():
            if not _is_real_float(value) or not math.isfinite(value):
                raise ValueError(
                    f"rate column {col!r} must be a finite float, got "
                    f"{value!r} (§9.2)."
                )
            if not (lo - _ATOL <= value <= hi + _ATOL):
                raise ValueError(
                    f"rate column {col!r}={value!r} is out of range "
                    f"[{lo}, {hi}] (§9.2)."
                )

    # Conditional rates: blank iff zero denominator, else finite float in [0,1].
    for n, dh, rgdm, dgdh, crit, setting, k, q in zip(
        summary["n"], summary["dense_hits"],
        summary["rescue_given_dense_miss"], summary["damage_given_dense_hit"],
        summary["criterion"], summary["setting"],
        summary["k"], summary["question_type"],
    ):
        tag = (crit, setting, k, q)
        for col, value, zero_denominator in (
            ("rescue_given_dense_miss", rgdm, int(n) - int(dh) == 0),
            ("damage_given_dense_hit", dgdh, int(dh) == 0),
        ):
            if zero_denominator:
                if pd.notna(value):
                    raise ValueError(
                        f"{tag}: {col} must be a blank cell on a zero "
                        f"denominator, got {value!r} (§9.2)."
                    )
            else:
                if not _is_real_float(value) or not math.isfinite(value):
                    raise ValueError(
                        f"{tag}: {col} must be a finite float, got {value!r} (§9.2)."
                    )
                if not (0.0 - _ATOL <= value <= 1.0 + _ATOL):
                    raise ValueError(
                        f"{tag}: {col}={value!r} is out of range [0, 1] (§9.2)."
                    )


def _expected_row_key_order():
    """The exact §9.4 (criterion, setting, k, question_type) row order."""
    return [
        (criterion, setting, k, q)
        for (criterion, setting, k) in VALID_COMBINATIONS
        for q in QUESTION_TYPE_GROUPS
    ]


def validate_row_order(frame):
    """§9.4: rows must appear in the exact deterministic key order."""
    actual = list(
        zip(frame.criterion, frame.setting,
            [int(k) for k in frame.k], frame.question_type)
    )
    expected = _expected_row_key_order()
    if actual != expected:
        raise ValueError(
            f"Row order does not match §9.4. Expected the 21-row key order "
            f"starting {expected[:2]}, got {actual[:2]}."
        )


def oracle_check(summary, dense, rerank):
    """§9.5 independent oracle: net_rate must equal (rerank_mean - dense_mean)
    of the raw {criterion}@{k} column, computed via summarize() — a separate
    code path that re-averages the accepted inputs, never the counts above.

    Another public function that accepts already-created result frames, so it
    holds them to the same shared typed metric contract before averaging
    anything out of them.
    """
    validate_typed_metric_frame(dense, "dense")
    validate_typed_metric_frame(rerank, "rerank")
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
    for NaN conditional rates.

    The writer never coerces or truncates. It re-validates the final, ordered,
    sorted frame, writes to a temporary file, re-validates the round-tripped
    bytes, and only then atomically replaces the destination. A refusal at any
    step therefore never creates or overwrites `out_path`.
    """
    df = summary[OUTPUT_COLUMNS].copy()
    df = df.assign(
        _c=df.criterion.map(_CRITERION_ORDER),
        _s=df.setting.map(_SETTING_ORDER),
        _q=df.question_type.map(_QTYPE_ORDER),
    ).sort_values(["_c", "_s", "k", "_q"]).drop(columns=["_c", "_s", "_q"])

    # Validate the exact bytes we are about to write, before touching the
    # destination. Integer columns are already plain integers (validated
    # upstream); no astype coercion is performed here.
    validate_output_schema(df)
    validate_output_types_and_ranges(df)
    validate_row_order(df)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    tmp_path = out_path + ".tmp"
    # float_format=None -> full-precision repr; NaN -> empty field by default.
    df.to_csv(tmp_path, index=False, float_format=None)
    try:
        # Round-trip guard: the persisted artifact itself must satisfy the whole
        # contract before it may replace the destination.
        written = pd.read_csv(tmp_path)
        validate_output_schema(written)
        validate_output_types_and_ranges(written)
        validate_summary_consistency(written)
        validate_row_order(written)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    os.replace(tmp_path, out_path)


def main(dense_path, rerank_path, out_path):
    dense, rerank = load_and_validate_inputs(dense_path, rerank_path)
    print(f"Inputs pass the §2 contract: {len(dense)} dense + {len(rerank)} rerank rows.")

    paired = build_paired_frame(dense, rerank)
    summary = summarize_rescue_damage(paired)   # <- your hand-written core

    # All validation happens before any type conversion or destination mutation.
    validate_output_schema(summary)
    validate_summary_consistency(summary)
    validate_output_types_and_ranges(summary)
    oracle_check(summary, dense, rerank)
    print("Output passes §9.3 schema, §9.2 types/ranges, §9.5 identities, and the oracle.")

    write_rescue_damage_csv(summary, out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Reranker rescue/damage summary (spec 2026-07-26).")
    p.add_argument("--dense", default="results/dense_results.csv")
    p.add_argument("--rerank", default="results/rerank_results.csv")
    p.add_argument("--out", default="results/rerank_rescue_damage.csv")
    args = p.parse_args()
    main(args.dense, args.rerank, args.out)
