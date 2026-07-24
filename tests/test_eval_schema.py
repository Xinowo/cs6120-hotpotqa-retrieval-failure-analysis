"""
test_eval_schema.py

Synthetic, offline tests for the EVALUATION schema constants and contract-only
validators in :mod:`src.eval_schema`. Every fixture is a hand-built dict/list
plus in-memory bytes: no model download, no network, no real corpus, and no
metric recomputation.

These tests exercise the frozen ``retrieval_eval_schema_v2`` physical contract
(``docs/specs/2026-07-20-retrieval-eval-schema-v2.md``) and the canonical v2
identifiers from ``docs/specs/2026-07-17-retrieval-metrics-v2.md``: exact
per-example / aggregate column order, the per_question @10 null policy, the
tidy-long aggregate value/n_valid consistency, the eval-ID grammar, the central
report-label mapping, the frozen ``k_policy`` and ``aggregation_groups``, and the
``artifact_sha256`` key set. Validators check STORED values only; a value like
``evidence_recall_at_2 = 0.5`` is treated as data to range-check, never
recomputed.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from src.eval_schema import (
    RETRIEVAL_EVAL_SCHEMA_V2,
    METRIC_DEFINITION_V2,
    EVALUATION_PROTOCOL_V2,
    PER_EXAMPLE_COLUMNS,
    PER_EXAMPLE_METRIC_COLUMNS,
    AGGREGATE_COLUMNS,
    AGGREGATE_METRIC_NAMES,
    PER_QUESTION_NULLABLE_COLUMNS,
    PER_QUESTION_EMPTY_AGGREGATE_NAMES,
    K_POLICY,
    VALID_AGGREGATION_GROUPS,
    AGGREGATE_REPORT_LABELS,
    EvalSchemaError,
    report_label,
    aggregate_by_columns,
    expected_artifact_keys,
    validate_eval_id,
    validate_per_example_columns,
    validate_per_example_rows,
    validate_aggregate_columns,
    validate_aggregate_row,
    validate_aggregate_rows,
    validate_eval_manifest,
    validate_artifact_checksum,
)
from src.raw_schema import compute_sha256


RUN_ID = "dense_pooled_n2_d50_20260720_r01"
EVAL_ID = "eval_dense_pooled_n2_d50_20260720_r01_metrics_v2_e01"
PERQ_RUN_ID = "bm25_per_question_n2_d10_20260720_r01"
PERQ_EVAL_ID = "eval_bm25_per_question_n2_d10_20260720_r01_metrics_v2_e01"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _versions():
    return {
        "eval_schema_version": RETRIEVAL_EVAL_SCHEMA_V2,
        "metric_definition_version": METRIC_DEFINITION_V2,
        "evaluation_protocol_version": EVALUATION_PROTOCOL_V2,
    }


def pooled_per_example_row(example_id="q1"):
    row = dict(_versions())
    row.update({
        "eval_id": EVAL_ID,
        "retrieval_run_id": RUN_ID,
        "method": "dense",
        "setting": "pooled",
        "example_id": example_id,
        "question_type": "bridge",
        "level": "hard",
        "gold_title_count": 2,
        "retrieved_depth": 50,
        "any_evidence_hit_indicator_at_2": 1,
        "any_evidence_hit_indicator_at_5": 1,
        "any_evidence_hit_indicator_at_10": 1,
        "full_evidence_hit_indicator_at_2": 0,
        "full_evidence_hit_indicator_at_5": 1,
        "full_evidence_hit_indicator_at_10": 1,
        "evidence_recall_at_2": 0.5,
        "evidence_recall_at_5": 1.0,
        "evidence_recall_at_10": 1.0,
        "reciprocal_rank_at_10": 1.0,
        "reciprocal_rank_at_50": 1.0,
    })
    return row


def _perq_ids(n, depth):
    """A per_question source run ID plus its eval ID, internally consistent in
    n<N> (== row count) and d<depth> (== max saved retrieved_depth). Used to
    build per_example fixtures whose encoded provenance matches the rows they
    actually contain (Finding F)."""
    run = f"bm25_per_question_n{n}_d{depth}_20260720_r01"
    return run, f"eval_{run}_metrics_v2_e01"


def per_question_per_example_row(example_id="q1", retrieved_depth=10,
                                 retrieval_run_id=PERQ_RUN_ID, eval_id=PERQ_EVAL_ID):
    row = dict(_versions())
    row.update({
        "eval_id": eval_id,
        "retrieval_run_id": retrieval_run_id,
        "method": "bm25",
        "setting": "per_question",
        "example_id": example_id,
        "question_type": "comparison",
        "level": "easy",
        "gold_title_count": 2,
        "retrieved_depth": retrieved_depth,
        "any_evidence_hit_indicator_at_2": 1,
        "any_evidence_hit_indicator_at_5": 1,
        "any_evidence_hit_indicator_at_10": "",   # deliberately empty
        "full_evidence_hit_indicator_at_2": 0,
        "full_evidence_hit_indicator_at_5": 1,
        "full_evidence_hit_indicator_at_10": "",  # deliberately empty
        "evidence_recall_at_2": 0.5,
        "evidence_recall_at_5": 1.0,
        "evidence_recall_at_10": "",              # deliberately empty
        "reciprocal_rank_at_10": 1.0,
        "reciprocal_rank_at_50": 1.0,
    })
    return row


def aggregate_row(metric_name, value, n_valid, method="dense", setting="pooled",
                  n_questions=2, eval_id=EVAL_ID, dimension=None, subgroup_value=None):
    row = dict(_versions())
    row.update({
        "eval_id": eval_id,
        "method": method,
        "setting": setting,
        "n_questions": n_questions,
        "metric_name": metric_name,
        "value": value,
        "n_valid": n_valid,
    })
    if dimension is not None:
        row[dimension] = subgroup_value
    return row


def full_group_rows(method="dense", setting="pooled", n_questions=2, eval_id=EVAL_ID,
                    dimension=None, subgroup_value=None):
    """Build all 11 canonical aggregate rows for one group, in canonical order,
    with the frozen n_valid/value per the null policy (per_question @10 metrics
    get n_valid=0 and an empty value; every other metric gets n_valid=n_questions
    and a present value)."""
    rows = []
    for name in AGGREGATE_METRIC_NAMES:
        if setting == "per_question" and name in PER_QUESTION_EMPTY_AGGREGATE_NAMES:
            rows.append(aggregate_row(name, "", 0, method=method, setting=setting,
                                      n_questions=n_questions, eval_id=eval_id,
                                      dimension=dimension, subgroup_value=subgroup_value))
        else:
            rows.append(aggregate_row(name, 0.5, n_questions, method=method, setting=setting,
                                      n_questions=n_questions, eval_id=eval_id,
                                      dimension=dimension, subgroup_value=subgroup_value))
    return rows


def full_aggregate_rows():
    return full_group_rows()


def eval_manifest(groups=None, artifact=None):
    groups = ["method+setting"] if groups is None else groups
    if artifact is None:
        artifact = {key: "f" * 64 for key in expected_artifact_keys(groups)}
    return {
        "eval_schema_version": RETRIEVAL_EVAL_SCHEMA_V2,
        "metric_definition_version": METRIC_DEFINITION_V2,
        "evaluation_protocol_version": EVALUATION_PROTOCOL_V2,
        "eval_id": EVAL_ID,
        "created_at": "2026-07-20T12:00:00Z",
        "source_retrieval_run_id": RUN_ID,
        "source_rankings_sha256": "d" * 64,
        "dataset_identifier": "hotpotqa_distractor_v1",
        "dataset_fingerprint": "sha256:" + "a" * 64,
        "gold_mapping_version_or_fingerprint": "gold_map_v1",
        "k_policy": K_POLICY,
        "aggregation_groups": groups,
        "evaluator_git_commit": "0" * 40,
        "command": "python scripts/evaluate.py",
        "artifact_sha256": artifact,
    }


# ---------------------------------------------------------------------------
# Column contracts and layer separation
# ---------------------------------------------------------------------------


def test_per_example_metric_columns_are_the_eleven_canonical_names():
    assert PER_EXAMPLE_METRIC_COLUMNS == [
        "any_evidence_hit_indicator_at_2", "any_evidence_hit_indicator_at_5",
        "any_evidence_hit_indicator_at_10", "full_evidence_hit_indicator_at_2",
        "full_evidence_hit_indicator_at_5", "full_evidence_hit_indicator_at_10",
        "evidence_recall_at_2", "evidence_recall_at_5", "evidence_recall_at_10",
        "reciprocal_rank_at_10", "reciprocal_rank_at_50",
    ]


def test_valid_per_example_columns_accepted():
    validate_per_example_columns(PER_EXAMPLE_COLUMNS)


def test_per_example_columns_reject_missing_extra_reordered():
    with pytest.raises(EvalSchemaError):
        validate_per_example_columns(PER_EXAMPLE_COLUMNS[:-1])
    with pytest.raises(EvalSchemaError):
        validate_per_example_columns(PER_EXAMPLE_COLUMNS + ["surprise"])
    swapped = list(PER_EXAMPLE_COLUMNS)
    swapped[-1], swapped[-2] = swapped[-2], swapped[-1]
    with pytest.raises(EvalSchemaError):
        validate_per_example_columns(swapped)


def test_per_example_columns_reject_legacy_only_identifier():
    cols = list(PER_EXAMPLE_COLUMNS)
    cols[-1] = "partial_evidence_recall@10"
    with pytest.raises(EvalSchemaError):
        validate_per_example_columns(cols)


@pytest.mark.parametrize("wrong_layer", [
    "any_evidence_hit_rate_at_2", "mean_reciprocal_rank_at_10",
    "macro_evidence_recall_at_2", "mrr", "mrr_for_example",
])
def test_per_example_columns_reject_aggregate_layer_identifier(wrong_layer):
    cols = list(PER_EXAMPLE_COLUMNS)
    cols[-1] = wrong_layer
    with pytest.raises(EvalSchemaError):
        validate_per_example_columns(cols)


def test_aggregate_columns_are_tidy_long():
    assert AGGREGATE_COLUMNS == [
        "eval_id", "eval_schema_version", "metric_definition_version",
        "evaluation_protocol_version", "method", "setting", "n_questions",
        "metric_name", "value", "n_valid",
    ]


def test_aggregate_by_dimension_inserts_group_column_after_setting():
    cols = aggregate_by_columns("question_type")
    assert cols[cols.index("setting") + 1] == "question_type"
    with pytest.raises(EvalSchemaError):
        aggregate_by_columns("answer")  # not a v2 subgroup dimension


# ---------------------------------------------------------------------------
# Per-example rows
# ---------------------------------------------------------------------------


def test_valid_pooled_per_example_rows():
    validate_per_example_rows([pooled_per_example_row("q1"),
                               pooled_per_example_row("q2")])


def test_valid_per_question_rows_with_empty_at_10():
    validate_per_example_rows([per_question_per_example_row("q1"),
                               per_question_per_example_row("q2")])


def test_pooled_at_10_must_not_be_empty():
    row = pooled_per_example_row()
    row["evidence_recall_at_10"] = ""
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_per_question_reciprocal_rank_still_required():
    row = per_question_per_example_row()
    row["reciprocal_rank_at_50"] = ""  # RR is never empty, even per_question
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_per_question_at_2_and_at_5_must_not_be_empty():
    # Only the three @10 hit/recall cells may be empty; @2/@5 are always present.
    row = per_question_per_example_row()
    row["evidence_recall_at_5"] = ""
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_pooled_populated_at_10_is_accepted():
    # In pooled the @10 cells are required and populated -- sanity that the
    # validator does not confuse setting policies. Two rows keep the file
    # consistent with the source ID's n2 (Finding F).
    validate_per_example_rows([pooled_per_example_row("q1"),
                               pooled_per_example_row("q2")])


def test_indicator_must_be_zero_or_one():
    row = pooled_per_example_row()
    row["any_evidence_hit_indicator_at_2"] = 2
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])
    row = pooled_per_example_row()
    row["full_evidence_hit_indicator_at_2"] = 0.5
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


# ---------------------------------------------------------------------------
# Finding I regression — Indicator cells must be SCHEMA INTEGER 0/1, not floats
# that merely compare equal (1.0, 0.0, -0.0), booleans, or numeric-looking
# strings. The frozen eval physical contract declares every Indicator column
# `int 0/1` and says "Indicators serialize as integer 0 or 1"
# (docs/specs/2026-07-20-retrieval-eval-schema-v2.md:75,108-113). Python treats
# 1.0 == 1 and -0.0 == 0, so a membership-only check silently accepts them.
# Each negative below lives in a COMPLETE, internally consistent file (matching
# the source ID's n/depth, ordering, versions, provenance) so the rejection
# cannot be attributed to a different earlier check, and each is paired with an
# accepted genuine-integer control in the same cell.
# ---------------------------------------------------------------------------

# All six per-example Indicator columns. In pooled every one is a required,
# non-empty integer cell (the @10 required-empty policy is per_question only).
_ALL_INDICATOR_COLUMNS = [
    "any_evidence_hit_indicator_at_2",
    "any_evidence_hit_indicator_at_5",
    "any_evidence_hit_indicator_at_10",
    "full_evidence_hit_indicator_at_2",
    "full_evidence_hit_indicator_at_5",
    "full_evidence_hit_indicator_at_10",
]
# The four per_question Indicator cells that are actually computed (@2/@5); the
# two @10 hit indicators are required-empty there and never reach the int check.
_PER_QUESTION_COMPUTED_INDICATOR_COLUMNS = [
    "any_evidence_hit_indicator_at_2",
    "any_evidence_hit_indicator_at_5",
    "full_evidence_hit_indicator_at_2",
    "full_evidence_hit_indicator_at_5",
]
# Integral-valued floats that == an allowed integer (the Finding I lookalikes).
_INDICATOR_INTEGRAL_FLOATS = [1.0, 0.0, -0.0]


@pytest.mark.parametrize("column", _ALL_INDICATOR_COLUMNS)
@pytest.mark.parametrize("bad", _INDICATOR_INTEGRAL_FLOATS)
def test_pooled_indicator_rejects_integral_valued_floats(column, bad):
    # Complete 2-row pooled file (RUN_ID is n2). The only defect is one Indicator
    # cell carrying a float equal to 0 or 1; it must be rejected, not coerced.
    rows = [pooled_per_example_row("q1"), pooled_per_example_row("q2")]
    rows[0][column] = bad
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows(rows)


@pytest.mark.parametrize("column", _PER_QUESTION_COMPUTED_INDICATOR_COLUMNS)
@pytest.mark.parametrize("bad", _INDICATOR_INTEGRAL_FLOATS)
def test_per_question_computed_indicator_rejects_integral_valued_floats(column, bad):
    # The four computed @2/@5 per_question Indicators (PERQ_RUN_ID is n2, d10; the
    # @10 hit cells stay required-empty). An integral-valued float is still rejected.
    rows = [per_question_per_example_row("q1"), per_question_per_example_row("q2")]
    rows[0][column] = bad
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows(rows)


@pytest.mark.parametrize("column", _ALL_INDICATOR_COLUMNS)
@pytest.mark.parametrize("bad", [True, False])
def test_pooled_indicator_rejects_booleans(column, bad):
    # bool is an int subclass, but _is_int excludes it: True/False are never
    # integer 0/1 Indicator cells. Locks in the pre-existing intended behavior.
    rows = [pooled_per_example_row("q1"), pooled_per_example_row("q2")]
    rows[0][column] = bad
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows(rows)


@pytest.mark.parametrize("column", _ALL_INDICATOR_COLUMNS)
@pytest.mark.parametrize("bad", ["0", "1"])
def test_pooled_indicator_rejects_numeric_strings(column, bad):
    # A CSV-looking "0"/"1" string is not a schema integer and is rejected, not
    # parsed. (An empty string is the only valid null, tested separately.)
    rows = [pooled_per_example_row("q1"), pooled_per_example_row("q2")]
    rows[0][column] = bad
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows(rows)


@pytest.mark.parametrize("column", _ALL_INDICATOR_COLUMNS)
@pytest.mark.parametrize("good", [0, 1])
def test_pooled_indicator_accepts_true_integer_controls(column, good):
    # Paired positive control: a genuine Python int 0/1 in the same cell of an
    # otherwise identical complete file is accepted.
    rows = [pooled_per_example_row("q1"), pooled_per_example_row("q2")]
    rows[0][column] = good
    validate_per_example_rows(rows)


@pytest.mark.parametrize("column", _PER_QUESTION_COMPUTED_INDICATOR_COLUMNS)
@pytest.mark.parametrize("good", [0, 1])
def test_per_question_computed_indicator_accepts_true_integer_controls(column, good):
    # Paired positive control for the four computed per_question Indicators.
    rows = [per_question_per_example_row("q1"), per_question_per_example_row("q2")]
    rows[0][column] = good
    validate_per_example_rows(rows)


@pytest.mark.parametrize("bad", [-0.1, 1.1, float("inf"), "0.5"])
def test_recall_and_rr_must_be_unit_floats(bad):
    row = pooled_per_example_row()
    row["evidence_recall_at_2"] = bad
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


@pytest.mark.parametrize("literal", ["NaN", "None", "null"])
def test_literal_null_strings_are_rejected(literal):
    row = per_question_per_example_row()
    row["evidence_recall_at_10"] = literal  # only empty cell is a valid null
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_gold_title_count_must_be_positive():
    row = pooled_per_example_row()
    row["gold_title_count"] = 0  # empty gold rejected upstream
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_bad_question_type_or_level_rejected():
    row = pooled_per_example_row()
    row["question_type"] = "yesno"
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])
    row = pooled_per_example_row()
    row["level"] = "trivial"
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_wrong_version_stamp_rejected():
    row = pooled_per_example_row()
    row["metric_definition_version"] = "retrieval_metrics_v1"
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_per_example_key_uniqueness():
    dup = pooled_per_example_row("q1")
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([pooled_per_example_row("q1"), dup])


# ---------------------------------------------------------------------------
# P1 regression — per_question @10 must be required-empty, not optional
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("column,populated", [
    ("any_evidence_hit_indicator_at_10", 1),
    ("full_evidence_hit_indicator_at_10", 0),
    ("evidence_recall_at_10", 1.0),
])
def test_per_question_populated_at_10_rejected_individually(column, populated):
    row = per_question_per_example_row()
    row[column] = populated  # type/range valid but prohibited for per_question
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_per_question_all_three_at_10_populated_rejected():
    # The exact adversarial case the independent review flagged as ACCEPTED.
    row = per_question_per_example_row(retrieved_depth=12)
    row["any_evidence_hit_indicator_at_10"] = 1
    row["full_evidence_hit_indicator_at_10"] = 1
    row["evidence_recall_at_10"] = 1.0
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


@pytest.mark.parametrize("depth", [8, 10, 12])
def test_per_question_at_10_empty_accepted_for_any_complete_depth(depth):
    # The required-empty @10 policy is independent of the complete corpus depth
    # (<10, ==10, >10). Each case uses an internally consistent single-example
    # source ID (n1, d<depth>) so the Finding F depth binding holds
    # (retrieved_depth == d == depth); RR@10/RR@50 remain present.
    run, ev = _perq_ids(1, depth)
    validate_per_example_rows([per_question_per_example_row(
        retrieved_depth=depth, retrieval_run_id=run, eval_id=ev)])


# ---------------------------------------------------------------------------
# P5 regression — per_example bundle composition and exact key set
# ---------------------------------------------------------------------------


def test_per_example_bundle_must_not_mix_two_runs():
    # Two individually type-valid rows from different eval IDs / raw runs /
    # methods / settings must NOT be accepted together as one file.
    pooled = pooled_per_example_row("q1")
    perq = per_question_per_example_row("q1")
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([pooled, perq])


def test_per_example_method_must_match_run_id_segment():
    row = pooled_per_example_row()
    row["method"] = "bm25"  # disagrees with the dense run encoded in the IDs
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_per_example_extra_or_missing_row_key_rejected():
    row = pooled_per_example_row()
    row["surprise"] = 1
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])
    row = pooled_per_example_row()
    del row["reciprocal_rank_at_50"]
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


def test_per_example_manifest_cross_check():
    rows = [pooled_per_example_row("q1"), pooled_per_example_row("q2")]
    validate_per_example_rows(rows, manifest=eval_manifest())

    other = eval_manifest()
    other["eval_id"] = "eval_bm25_pooled_n2_d50_20260720_r01_metrics_v2_e01"
    with pytest.raises(EvalSchemaError):  # rows' eval_id != manifest eval_id
        validate_per_example_rows(rows, manifest=other)


def test_per_example_empty_file_rejected():
    # A complete per_example file cannot be empty (source raw n_loaded >= 1).
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([])
    with pytest.raises(EvalSchemaError):  # empty must not bypass the manifest check
        validate_per_example_rows([], manifest=eval_manifest())


def test_per_example_rows_must_be_ascending_example_id():
    a = pooled_per_example_row("q1")
    b = pooled_per_example_row("q2")
    validate_per_example_rows([a, b])  # ascending ok
    with pytest.raises(EvalSchemaError):  # q2 before q1
        validate_per_example_rows([b, a])


# ---------------------------------------------------------------------------
# Finding F — per_example cardinality / depth bound to the source run n<N>/d<depth>
# ---------------------------------------------------------------------------


def test_per_example_row_count_must_equal_source_n():
    # Source ID n2 but the complete file contains only one row.
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([pooled_per_example_row("q1")])


def test_pooled_retrieved_depth_exceeding_source_d_rejected():
    # Pooled source d50; both rows share retrieved_depth 51 (> d).
    a = pooled_per_example_row("q1")
    b = pooled_per_example_row("q2")
    a["retrieved_depth"] = 51
    b["retrieved_depth"] = 51
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([a, b])


def test_pooled_retrieved_depth_must_be_uniform():
    # Pooled runs use one fixed depth, so examples cannot differ in saved depth.
    a = pooled_per_example_row("q1")
    b = pooled_per_example_row("q2")
    b["retrieved_depth"] = 49  # <= d=50 but not equal to a's 50
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([a, b])


def test_per_question_retrieved_depth_exceeding_source_d_rejected():
    # per_question source d10; a row at retrieved_depth 12 exceeds d.
    a = per_question_per_example_row("q1", retrieved_depth=12)
    b = per_question_per_example_row("q2", retrieved_depth=10)
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([a, b])


def test_per_question_max_depth_must_equal_source_d():
    # per_question d<depth> is the MAX saved depth, so it must be attained; here
    # source d10 but no row reaches 10.
    a = per_question_per_example_row("q1", retrieved_depth=7)
    b = per_question_per_example_row("q2", retrieved_depth=8)
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([a, b])


def test_valid_per_question_n2_d12_file():
    # A truly consistent per_question file: n2 (two rows), d12 attained by the
    # deepest example, the other shallower; @10 cells remain empty.
    run, ev = _perq_ids(2, 12)
    a = per_question_per_example_row("q1", retrieved_depth=12,
                                     retrieval_run_id=run, eval_id=ev)
    b = per_question_per_example_row("q2", retrieved_depth=5,
                                     retrieval_run_id=run, eval_id=ev)
    validate_per_example_rows([a, b])


# ---------------------------------------------------------------------------
# eval_id grammar
# ---------------------------------------------------------------------------


def test_valid_eval_id():
    validate_eval_id(EVAL_ID, RUN_ID)


def test_eval_id_run_segment_must_match_source_run():
    with pytest.raises(EvalSchemaError):
        validate_eval_id(EVAL_ID, "bm25_pooled_n2_d50_20260720_r01")


@pytest.mark.parametrize("bad", [
    "dense_pooled_n2_d50_20260720_r01_metrics_v2_e01",   # missing eval_ prefix
    "eval_dense_pooled_n2_d50_20260720_r01_metrics_v2_e1",  # 1-digit seq
    "eval_not_a_run_id_metrics_v2_e01",   # embedded run id invalid
])
def test_bad_eval_ids_rejected(bad):
    with pytest.raises(EvalSchemaError):
        validate_eval_id(bad)


# ---------------------------------------------------------------------------
# Aggregate columns
# ---------------------------------------------------------------------------


def test_valid_aggregate_columns():
    validate_aggregate_columns(AGGREGATE_COLUMNS)
    validate_aggregate_columns(aggregate_by_columns("level"), dimension="level")


def test_aggregate_columns_reject_missing_extra_reordered():
    with pytest.raises(EvalSchemaError):
        validate_aggregate_columns(AGGREGATE_COLUMNS[:-1])
    with pytest.raises(EvalSchemaError):
        validate_aggregate_columns(AGGREGATE_COLUMNS + ["surprise"])
    swapped = list(AGGREGATE_COLUMNS)
    swapped[-1], swapped[-2] = swapped[-2], swapped[-1]
    with pytest.raises(EvalSchemaError):
        validate_aggregate_columns(swapped)


# ---------------------------------------------------------------------------
# Aggregate single-row (validate_aggregate_row): n_valid / value semantics
# ---------------------------------------------------------------------------


def test_aggregate_row_mandatory_n_valid_equals_n_questions():
    # pooled RR@10 is mandatory -> n_valid must equal n_questions.
    validate_aggregate_row(aggregate_row("mean_reciprocal_rank_at_10", 0.5, 2))
    # n_valid == 0 for a mandatory pooled metric is the review's ACCEPTED case;
    # it must now be rejected.
    with pytest.raises(EvalSchemaError):
        validate_aggregate_row(aggregate_row("mean_reciprocal_rank_at_10", "", 0))
    # n_valid strictly between 0 and n_questions is also invalid for a mandatory
    # metric (no permitted per-example NaN).
    with pytest.raises(EvalSchemaError):
        validate_aggregate_row(aggregate_row("mean_reciprocal_rank_at_10", 0.5, 1))


def test_aggregate_row_mandatory_value_must_be_present():
    with pytest.raises(EvalSchemaError):  # n_valid 2 but empty value
        validate_aggregate_row(aggregate_row("mean_reciprocal_rank_at_10", "", 2))


def test_aggregate_row_per_question_rr_n_valid_must_equal_n_questions():
    # The review's ACCEPTED case: per_question RR with n_valid < n_questions.
    with pytest.raises(EvalSchemaError):
        validate_aggregate_row(aggregate_row("mean_reciprocal_rank_at_50", 0.5, 1,
                                             method="bm25", setting="per_question",
                                             n_questions=2, eval_id=PERQ_EVAL_ID))


def test_aggregate_row_per_question_at_10_must_be_zero_valid_and_empty():
    for name in PER_QUESTION_EMPTY_AGGREGATE_NAMES:
        validate_aggregate_row(aggregate_row(name, "", 0, method="bm25",
                                             setting="per_question", eval_id=PERQ_EVAL_ID))
        with pytest.raises(EvalSchemaError):  # a real value is prohibited
            validate_aggregate_row(aggregate_row(name, 0.5, 2, method="bm25",
                                                 setting="per_question",
                                                 eval_id=PERQ_EVAL_ID))


def test_aggregate_row_metric_name_must_be_canonical():
    with pytest.raises(EvalSchemaError):
        validate_aggregate_row(aggregate_row("mrr@10", 0.5, 2))
    with pytest.raises(EvalSchemaError):  # per-example identifier at aggregate layer
        validate_aggregate_row(aggregate_row("any_evidence_hit_indicator_at_2", 1, 2))


def test_aggregate_row_value_out_of_range_rejected():
    with pytest.raises(EvalSchemaError):
        validate_aggregate_row(aggregate_row("macro_evidence_recall_at_2", 1.5, 2))


def test_aggregate_row_extra_or_missing_key_rejected():
    row = aggregate_row("mean_reciprocal_rank_at_10", 0.5, 2)
    row["surprise"] = 1
    with pytest.raises(EvalSchemaError):
        validate_aggregate_row(row)
    row = aggregate_row("mean_reciprocal_rank_at_10", 0.5, 2)
    del row["n_valid"]
    with pytest.raises(EvalSchemaError):
        validate_aggregate_row(row)


# ---------------------------------------------------------------------------
# Aggregate file-level (validate_aggregate_rows): completeness, order, bundle
# ---------------------------------------------------------------------------


def test_valid_full_aggregate_rows():
    validate_aggregate_rows(full_aggregate_rows())


def test_valid_per_question_full_aggregate_rows():
    validate_aggregate_rows(full_group_rows(method="bm25", setting="per_question",
                                            eval_id=PERQ_EVAL_ID))


def test_aggregate_file_missing_metrics_rejected():
    rows = full_aggregate_rows()[:1]  # only 1 of 11 canonical metrics
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows)


def test_aggregate_file_extra_metric_row_rejected():
    rows = full_aggregate_rows() + [aggregate_row("mean_reciprocal_rank_at_10", 0.5, 2)]
    with pytest.raises(EvalSchemaError):  # duplicate -> group != canonical set
        validate_aggregate_rows(rows)


def test_aggregate_file_reverse_metric_order_rejected():
    rows = list(reversed(full_aggregate_rows()))
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows)


def test_aggregate_file_must_not_mix_two_bundles():
    rows = full_group_rows(eval_id=EVAL_ID) + full_group_rows(
        method="bm25", setting="per_question", eval_id=PERQ_EVAL_ID)
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows)


def test_valid_subgroup_aggregate_file_both_values():
    rows = (full_group_rows(dimension="question_type", subgroup_value="bridge", n_questions=1)
            + full_group_rows(dimension="question_type", subgroup_value="comparison", n_questions=1))
    validate_aggregate_rows(rows, dimension="question_type")


def test_subgroup_values_out_of_canonical_order_rejected():
    rows = (full_group_rows(dimension="question_type", subgroup_value="comparison", n_questions=1)
            + full_group_rows(dimension="question_type", subgroup_value="bridge", n_questions=1))
    with pytest.raises(EvalSchemaError):  # comparison before bridge
        validate_aggregate_rows(rows, dimension="question_type")


def test_subgroup_bad_value_rejected():
    rows = full_group_rows(dimension="level", subgroup_value="trivial")
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows, dimension="level")


def test_aggregate_file_manifest_cross_check():
    validate_aggregate_rows(full_aggregate_rows(), manifest=eval_manifest())
    other = eval_manifest()
    other["eval_id"] = "eval_bm25_pooled_n2_d50_20260720_r01_metrics_v2_e01"
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(full_aggregate_rows(), manifest=other)


def test_aggregate_empty_file_rejected():
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([])
    with pytest.raises(EvalSchemaError):  # empty must not bypass the manifest check
        validate_aggregate_rows([], manifest=eval_manifest())


def test_aggregate_group_n_questions_must_be_constant():
    rows = full_aggregate_rows()
    rows[1]["n_questions"] = 3  # drifts within the single group
    rows[1]["n_valid"] = 3      # keep the per-row n_valid rule locally satisfied
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows)


def test_aggregate_method_setting_must_match_embedded_source_run():
    # eval_id embeds a dense_pooled run but rows claim bm25 -> rejected, even
    # though method/setting are individually valid vocabulary members.
    rows = full_group_rows(method="bm25", setting="pooled", eval_id=EVAL_ID)
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows)


def test_subgroup_blocks_must_be_contiguous():
    bridge = full_group_rows(dimension="question_type", subgroup_value="bridge", n_questions=1)
    comparison = full_group_rows(dimension="question_type", subgroup_value="comparison", n_questions=1)
    # Interleave: bridge[0], all comparison, then bridge[1:].
    interleaved = [bridge[0]] + comparison + bridge[1:]
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(interleaved, dimension="question_type")


def test_subgroup_dimension_must_be_declared_in_manifest():
    rows = (full_group_rows(dimension="question_type", subgroup_value="bridge", n_questions=1)
            + full_group_rows(dimension="question_type", subgroup_value="comparison", n_questions=1))
    # Manifest whose aggregation_groups omits question_type (and its artifact key).
    manifest = eval_manifest(groups=["method+setting"])
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows, dimension="question_type", manifest=manifest)


def test_subgroup_artifact_key_must_be_present_in_manifest():
    rows = (full_group_rows(dimension="question_type", subgroup_value="bridge", n_questions=1)
            + full_group_rows(dimension="question_type", subgroup_value="comparison", n_questions=1))
    # aggregation_groups declares question_type but artifact_sha256 omits its file.
    manifest = eval_manifest(groups=["method+setting", "question_type"])
    del manifest["artifact_sha256"]["aggregate_by_question_type.csv"]
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows, dimension="question_type", manifest=manifest)


def test_subgroup_file_with_declared_manifest_accepted():
    rows = (full_group_rows(dimension="question_type", subgroup_value="bridge", n_questions=1)
            + full_group_rows(dimension="question_type", subgroup_value="comparison", n_questions=1))
    manifest = eval_manifest(groups=["method+setting", "question_type"])
    validate_aggregate_rows(rows, dimension="question_type", manifest=manifest)


# ---------------------------------------------------------------------------
# Finding F — aggregate question counts bound to the source run n<N>
# ---------------------------------------------------------------------------


def test_default_aggregate_n_questions_must_equal_source_n():
    # Source ID n2 but every row claims n_questions=3 (per-row n_valid stays
    # locally consistent, so only the source-cardinality binding catches it).
    rows = full_group_rows(n_questions=3)
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows)


def test_subgroup_n_questions_must_sum_to_source_n():
    # question_type source ID n2 but bridge=2 and comparison=2 partition to 4.
    rows = (full_group_rows(dimension="question_type", subgroup_value="bridge", n_questions=2)
            + full_group_rows(dimension="question_type", subgroup_value="comparison", n_questions=2))
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows(rows, dimension="question_type")


# ---------------------------------------------------------------------------
# Report-label mapping
# ---------------------------------------------------------------------------


def test_report_labels_cover_every_aggregate_metric():
    assert set(AGGREGATE_REPORT_LABELS) == set(AGGREGATE_METRIC_NAMES)


def test_report_label_values():
    assert report_label("any_evidence_hit_rate_at_2") == "Any Evidence Hit Rate@2"
    assert report_label("macro_evidence_recall_at_10") == "Macro Evidence Recall@10"
    assert report_label("mean_reciprocal_rank_at_50") == "MRR@50"


def test_report_label_unknown_rejected():
    with pytest.raises(EvalSchemaError):
        report_label("not_a_metric")


def test_report_labels_are_not_storage_identifiers():
    # No report label is ever a stored metric_name.
    assert set(AGGREGATE_REPORT_LABELS.values()).isdisjoint(AGGREGATE_METRIC_NAMES)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def test_valid_default_manifest():
    validate_eval_manifest(eval_manifest())


def test_valid_manifest_with_both_subgroups():
    groups = ["method+setting", "question_type", "level"]
    validate_eval_manifest(eval_manifest(groups=groups))


def test_manifest_rejects_extra_or_missing_field():
    manifest = eval_manifest()
    manifest["surprise"] = 1
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)
    manifest = eval_manifest()
    del manifest["k_policy"]
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_manifest_k_policy_must_match_frozen_value():
    manifest = eval_manifest()
    manifest["k_policy"] = dict(K_POLICY)
    manifest["k_policy"]["pooled"] = dict(manifest["k_policy"]["pooled"])
    manifest["k_policy"]["pooled"]["computed_hit_recall_cutoffs"] = [2, 5]  # drift
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


@pytest.mark.parametrize("bad_groups", [
    ["question_type"],                       # must start with method+setting
    ["method+setting", "level", "question_type"],  # wrong subgroup order
    ["method+setting", "answer"],            # unknown subgroup
    ["method+setting", "question_type", "question_type"],  # duplicate
])
def test_manifest_rejects_illegal_aggregation_groups(bad_groups):
    artifact = {key: "f" * 64 for key in {"per_example.csv", "aggregate.csv"}}
    manifest = eval_manifest(groups=bad_groups, artifact=artifact)
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_artifact_key_set_must_match_aggregation_groups():
    # question_type listed but its file is missing from artifact_sha256.
    groups = ["method+setting", "question_type"]
    artifact = {"per_example.csv": "f" * 64, "aggregate.csv": "f" * 64}
    manifest = eval_manifest(groups=groups, artifact=artifact)
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_artifact_key_set_rejects_unlisted_subgroup_file():
    # level file present but level not in aggregation_groups.
    groups = ["method+setting"]
    artifact = {
        "per_example.csv": "f" * 64,
        "aggregate.csv": "f" * 64,
        "aggregate_by_level.csv": "f" * 64,
    }
    manifest = eval_manifest(groups=groups, artifact=artifact)
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_manifest_excludes_self_referential_checksum():
    assert "manifest.json" not in expected_artifact_keys(
        ["method+setting", "question_type", "level"])


def test_source_rankings_sha256_must_be_bare_hex():
    manifest = eval_manifest()
    manifest["source_rankings_sha256"] = "sha256:" + "d" * 64
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_dataset_fingerprint_must_have_prefix():
    manifest = eval_manifest()
    manifest["dataset_fingerprint"] = "a" * 64
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_manifest_eval_id_run_segment_must_match_source():
    manifest = eval_manifest()
    manifest["source_retrieval_run_id"] = "bm25_pooled_n2_d50_20260720_r01"
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_manifest_source_run_full_semantic_validation():
    # Source run with an impossible date, embedded consistently in eval_id, must
    # be rejected (full validation, not just regex shape).
    manifest = eval_manifest()
    manifest["source_retrieval_run_id"] = "dense_pooled_n2_d50_20261399_r01"
    manifest["eval_id"] = "eval_dense_pooled_n2_d50_20261399_r01_metrics_v2_e01"
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)

    manifest = eval_manifest()
    manifest["source_retrieval_run_id"] = "dense_pooled_n2_d50_20260720_r00"  # r00
    manifest["eval_id"] = "eval_dense_pooled_n2_d50_20260720_r00_metrics_v2_e01"
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_eval_id_embedding_invalid_run_rejected():
    # The run embedded in an eval_id is fully validated, not just regex-shaped.
    with pytest.raises(EvalSchemaError):
        validate_eval_id("eval_dense_pooled_n2_d50_20261399_r01_metrics_v2_e01")  # bad date
    with pytest.raises(EvalSchemaError):
        validate_eval_id("eval_dense_pooled_n2_d50_20260720_r00_metrics_v2_e01")  # r00


def test_eval_id_embedded_run_rejects_non_positive_segments():
    # Propagation point 4: the eval_id-embedded run reuse rejects n0/d0.
    with pytest.raises(EvalSchemaError):
        validate_eval_id("eval_dense_pooled_n0_d50_20260720_r01_metrics_v2_e01")  # n0
    with pytest.raises(EvalSchemaError):
        validate_eval_id("eval_dense_pooled_n2_d0_20260720_r01_metrics_v2_e01")   # d0


def test_eval_manifest_source_run_rejects_non_positive_segments():
    # Propagation point 3: the eval source run reuse rejects n0/d0 (both the
    # source_retrieval_run_id and the consistently embedded eval_id run).
    manifest = eval_manifest()
    manifest["source_retrieval_run_id"] = "dense_pooled_n0_d50_20260720_r01"
    manifest["eval_id"] = "eval_dense_pooled_n0_d50_20260720_r01_metrics_v2_e01"
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)

    manifest = eval_manifest()
    manifest["source_retrieval_run_id"] = "dense_pooled_n2_d0_20260720_r01"
    manifest["eval_id"] = "eval_dense_pooled_n2_d0_20260720_r01_metrics_v2_e01"
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


# ---------------------------------------------------------------------------
# Finding G — eval e<NN> is ASCII-only and numeric (e01..e99; e00 invalid); the
# embedded/source raw run reuses the one canonical ASCII-only run-ID validator
# ---------------------------------------------------------------------------

# chr() so terminal encoding cannot swap the character for "?" (false test).
_AR_ZERO = chr(0x0660)   # ARABIC-INDIC DIGIT ZERO
_AR_ONE = chr(0x0661)    # ARABIC-INDIC DIGIT ONE


def test_eval_id_rejects_ascii_e00():
    # Owner decision: the eval sequence starts at e01; ASCII e00 is invalid.
    with pytest.raises(EvalSchemaError):
        validate_eval_id("eval_dense_pooled_n2_d50_20260720_r01_metrics_v2_e00")


def test_eval_id_accepts_ascii_e01_and_e99():
    # e01 and e99 are the legal ASCII sequence endpoints.
    validate_eval_id("eval_dense_pooled_n2_d50_20260720_r01_metrics_v2_e01")
    validate_eval_id("eval_dense_pooled_n2_d50_20260720_r01_metrics_v2_e99")


def test_eval_id_rejects_unicode_digit_suffix():
    # Non-ASCII decimal digits in the e<NN> suffix are not the canonical spelling.
    with pytest.raises(EvalSchemaError):
        validate_eval_id(
            "eval_dense_pooled_n2_d50_20260720_r01_metrics_v2_e0" + _AR_ONE)
    with pytest.raises(EvalSchemaError):
        validate_eval_id(
            "eval_dense_pooled_n2_d50_20260720_r01_metrics_v2_e" + _AR_ZERO * 2)


def test_eval_source_and_embedded_run_reject_arabic_indic_zero_sequence():
    # The embedded raw run and the manifest source run both route through the
    # single canonical validate_retrieval_run_id, so an Arabic-Indic zero rerun
    # sequence is rejected via the eval_id grammar and via manifest validation.
    bad_run = "dense_pooled_n2_d50_20260720_r" + _AR_ZERO * 2
    bad_eval = "eval_" + bad_run + "_metrics_v2_e01"
    with pytest.raises(EvalSchemaError):
        validate_eval_id(bad_eval)
    manifest = eval_manifest()
    manifest["source_retrieval_run_id"] = bad_run
    manifest["eval_id"] = bad_eval
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


# ---------------------------------------------------------------------------
# Artifact checksum
# ---------------------------------------------------------------------------


def test_artifact_checksum_roundtrip():
    payload = b"eval_id,eval_schema_version,...\n"
    manifest = eval_manifest()
    manifest["artifact_sha256"]["per_example.csv"] = compute_sha256(payload)
    validate_artifact_checksum("per_example.csv", payload, manifest)


def test_artifact_checksum_mismatch_rejected():
    manifest = eval_manifest()
    manifest["artifact_sha256"]["per_example.csv"] = compute_sha256(b"a")
    with pytest.raises(EvalSchemaError):
        validate_artifact_checksum("per_example.csv", b"b", manifest)


def test_artifact_checksum_unlisted_filename_rejected():
    manifest = eval_manifest()
    with pytest.raises(EvalSchemaError):
        validate_artifact_checksum("aggregate_by_level.csv", b"x", manifest)


# ---------------------------------------------------------------------------
# Finding H — a single trailing LF must be rejected by whole-string exact-format
# validation (eval_id grammar, bare SHA-256 checksums, sha256: fingerprints, and
# every artifact digest). Each negative case differs from an accepted canonical
# control ONLY by one final LF; no strip()/rstrip()/normalization repairs it.
# ---------------------------------------------------------------------------

_LF = "\n"


def test_eval_id_helper_rejects_terminal_lf_but_accepts_canonical():
    # Case 4: the direct eval_id helper, both with and without the source-run arg.
    validate_eval_id(EVAL_ID, RUN_ID)  # control
    with pytest.raises(EvalSchemaError):
        validate_eval_id(EVAL_ID + _LF, RUN_ID)
    validate_eval_id(EVAL_ID)  # control (no source run supplied)
    with pytest.raises(EvalSchemaError):
        validate_eval_id(EVAL_ID + _LF)


def test_eval_manifest_rejects_terminal_lf_eval_id():
    # Case 5: propagation through the eval manifest eval_id.
    validate_eval_manifest(eval_manifest())  # control
    manifest = eval_manifest()
    manifest["eval_id"] = EVAL_ID + _LF
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_source_rankings_sha256_rejects_terminal_lf():
    # Case 8a: bare source_rankings_sha256.
    validate_eval_manifest(eval_manifest())  # control
    manifest = eval_manifest()
    manifest["source_rankings_sha256"] = manifest["source_rankings_sha256"] + _LF
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


def test_every_artifact_sha256_digest_rejects_terminal_lf():
    # Case 8b: every artifact_sha256 digest, using the fullest artifact key set
    # (both subgroup files present) so all four digests are exercised.
    groups = ["method+setting", "question_type", "level"]
    validate_eval_manifest(eval_manifest(groups=groups))  # control
    for key in expected_artifact_keys(groups):
        manifest = eval_manifest(groups=groups)
        manifest["artifact_sha256"][key] = manifest["artifact_sha256"][key] + _LF
        with pytest.raises(EvalSchemaError):
            validate_eval_manifest(manifest)


def test_eval_dataset_fingerprint_rejects_terminal_lf():
    # Case 9: the sha256:-prefixed dataset_fingerprint.
    validate_eval_manifest(eval_manifest())  # control
    manifest = eval_manifest()
    manifest["dataset_fingerprint"] = manifest["dataset_fingerprint"] + _LF
    with pytest.raises(EvalSchemaError):
        validate_eval_manifest(manifest)


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-q"]))
