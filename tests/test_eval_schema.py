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


def per_question_per_example_row(example_id="q1"):
    row = dict(_versions())
    row.update({
        "eval_id": PERQ_EVAL_ID,
        "retrieval_run_id": PERQ_RUN_ID,
        "method": "bm25",
        "setting": "per_question",
        "example_id": example_id,
        "question_type": "comparison",
        "level": "easy",
        "gold_title_count": 2,
        "retrieved_depth": 10,
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
                  n_questions=2, eval_id=EVAL_ID):
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
    return row


def full_aggregate_rows():
    rows = []
    for name in AGGREGATE_METRIC_NAMES:
        rows.append(aggregate_row(name, 0.5, 2))
    return rows


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
    # validator does not confuse setting policies.
    validate_per_example_rows([pooled_per_example_row()])


def test_indicator_must_be_zero_or_one():
    row = pooled_per_example_row()
    row["any_evidence_hit_indicator_at_2"] = 2
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])
    row = pooled_per_example_row()
    row["full_evidence_hit_indicator_at_2"] = 0.5
    with pytest.raises(EvalSchemaError):
        validate_per_example_rows([row])


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
# Aggregate rows
# ---------------------------------------------------------------------------


def test_valid_full_aggregate_rows():
    validate_aggregate_rows(full_aggregate_rows())


def test_aggregate_value_empty_iff_n_valid_zero():
    # n_valid == 0 requires an empty value.
    validate_aggregate_rows([aggregate_row("mean_reciprocal_rank_at_10", "", 0)])
    # n_valid > 0 requires a present value.
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([aggregate_row("mean_reciprocal_rank_at_10", "", 2)])
    # value present while n_valid == 0 is inconsistent.
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([aggregate_row("mean_reciprocal_rank_at_10", 0.5, 0)])


def test_per_question_at_10_aggregates_must_be_empty_with_zero_valid():
    for name in PER_QUESTION_EMPTY_AGGREGATE_NAMES:
        # Correct: n_valid 0, empty value.
        validate_aggregate_rows([aggregate_row(name, "", 0, method="bm25",
                                               setting="per_question",
                                               eval_id=PERQ_EVAL_ID)])
        # Wrong: a per_question @10 aggregate with a real value.
        with pytest.raises(EvalSchemaError):
            validate_aggregate_rows([aggregate_row(name, 0.5, 2, method="bm25",
                                                   setting="per_question",
                                                   eval_id=PERQ_EVAL_ID)])


def test_aggregate_metric_name_must_be_canonical():
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([aggregate_row("mrr@10", 0.5, 2)])
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([aggregate_row("any_evidence_hit_indicator_at_2", 1, 2)])


def test_aggregate_n_valid_cannot_exceed_n_questions():
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([aggregate_row("mean_reciprocal_rank_at_10", 0.5, 3,
                                               n_questions=2)])


def test_aggregate_value_out_of_range_rejected():
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([aggregate_row("macro_evidence_recall_at_2", 1.5, 2)])


def test_aggregate_key_uniqueness():
    row = aggregate_row("mean_reciprocal_rank_at_10", 0.5, 2)
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([row, dict(row)])


def test_aggregate_by_dimension_rows():
    row = aggregate_row("mean_reciprocal_rank_at_10", 0.5, 1)
    row["question_type"] = "bridge"
    validate_aggregate_rows([row], dimension="question_type")
    # Bad subgroup value rejected.
    row_bad = aggregate_row("mean_reciprocal_rank_at_10", 0.5, 1)
    row_bad["question_type"] = "yesno"
    with pytest.raises(EvalSchemaError):
        validate_aggregate_rows([row_bad], dimension="question_type")


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


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-q"]))
