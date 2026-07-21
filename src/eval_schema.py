"""
eval_schema.py

Stage 2 schema constants and contract-only validators for the EVALUATION layer
of the metrics/schema v2 refactor: ``per_example.csv``, tidy-long
``aggregate.csv`` / ``aggregate_by_<dimension>.csv``, and the eval
``manifest.json``.

Authoritative frozen contracts:
- physical eval shape: ``docs/specs/2026-07-20-retrieval-eval-schema-v2.md``
  (``eval_schema_version = retrieval_eval_schema_v2``);
- metric meaning and the canonical v2 identifiers:
  ``docs/specs/2026-07-17-retrieval-metrics-v2.md``
  (``metric_definition_version = retrieval_metrics_v2``).

This module references the canonical metric identifiers verbatim and never
redefines a metric. Per the project AI-usage boundary, metric formulas and core
computation stay team-owned in :mod:`src.evaluator`; the validators here check
schema, types, ranges, nullability, and provenance only. They never recompute
or redefine a metric, and never reuse the ambiguous mixed ``RESULT_COLUMNS``.
"""

import re as _re
from typing import List, Mapping, Sequence

from src.raw_schema import (
    RAW_METHODS,
    RAW_SETTINGS,
    SHA256_HEX_RE,
    SHA256_FINGERPRINT_RE,
    CREATED_AT_RE,
    RETRIEVAL_RUN_ID_RE as _RUN_ID_RE,
    compute_sha256,
    _is_int,
    _is_finite_number,
)

# ---------------------------------------------------------------------------
# Version identifiers (metric spec §6)
# ---------------------------------------------------------------------------

RETRIEVAL_EVAL_SCHEMA_V2 = "retrieval_eval_schema_v2"
METRIC_DEFINITION_V2 = "retrieval_metrics_v2"
EVALUATION_PROTOCOL_V2 = "hotpotqa_retrieval_protocol_v2"

# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------

QUESTION_TYPES = ("bridge", "comparison")
LEVELS = ("easy", "medium", "hard")

# Deterministic subgroup value order (serialization contract).
QUESTION_TYPE_ORDER = ("bridge", "comparison")
LEVEL_ORDER = ("easy", "medium", "hard")

# ---------------------------------------------------------------------------
# per_example.csv column contract (metadata first, then the 11 metric columns)
# ---------------------------------------------------------------------------

PER_EXAMPLE_METADATA_COLUMNS = [
    "eval_id",
    "eval_schema_version",
    "metric_definition_version",
    "evaluation_protocol_version",
    "retrieval_run_id",
    "method",
    "setting",
    "example_id",
    "question_type",
    "level",
    "gold_title_count",
    "retrieved_depth",
]

# Canonical per-example metric identifiers (metric spec §5.1), exact order.
ANY_HIT_INDICATOR_COLUMNS = [
    "any_evidence_hit_indicator_at_2",
    "any_evidence_hit_indicator_at_5",
    "any_evidence_hit_indicator_at_10",
]
FULL_HIT_INDICATOR_COLUMNS = [
    "full_evidence_hit_indicator_at_2",
    "full_evidence_hit_indicator_at_5",
    "full_evidence_hit_indicator_at_10",
]
EVIDENCE_RECALL_COLUMNS = [
    "evidence_recall_at_2",
    "evidence_recall_at_5",
    "evidence_recall_at_10",
]
RECIPROCAL_RANK_COLUMNS = [
    "reciprocal_rank_at_10",
    "reciprocal_rank_at_50",
]

PER_EXAMPLE_METRIC_COLUMNS = (
    ANY_HIT_INDICATOR_COLUMNS
    + FULL_HIT_INDICATOR_COLUMNS
    + EVIDENCE_RECALL_COLUMNS
    + RECIPROCAL_RANK_COLUMNS
)

PER_EXAMPLE_COLUMNS = PER_EXAMPLE_METADATA_COLUMNS + PER_EXAMPLE_METRIC_COLUMNS

# Indicators serialize as int 0/1; recall + reciprocal-rank serialize as floats.
INDICATOR_COLUMNS = ANY_HIT_INDICATOR_COLUMNS + FULL_HIT_INDICATOR_COLUMNS
FLOAT_METRIC_COLUMNS = EVIDENCE_RECALL_COLUMNS + RECIPROCAL_RANK_COLUMNS

# The ONLY per-example columns that may be empty, and only when
# setting == "per_question" (metric spec §3). Reciprocal ranks are never empty.
PER_QUESTION_NULLABLE_COLUMNS = [
    "any_evidence_hit_indicator_at_10",
    "full_evidence_hit_indicator_at_10",
    "evidence_recall_at_10",
]

# ---------------------------------------------------------------------------
# aggregate.csv column contract (tidy-long)
# ---------------------------------------------------------------------------

AGGREGATE_COLUMNS = [
    "eval_id",
    "eval_schema_version",
    "metric_definition_version",
    "evaluation_protocol_version",
    "method",
    "setting",
    "n_questions",
    "metric_name",
    "value",
    "n_valid",
]

# Canonical aggregate metric identifiers (metric spec §5.2).
AGGREGATE_METRIC_NAMES = [
    "any_evidence_hit_rate_at_2",
    "any_evidence_hit_rate_at_5",
    "any_evidence_hit_rate_at_10",
    "full_evidence_hit_rate_at_2",
    "full_evidence_hit_rate_at_5",
    "full_evidence_hit_rate_at_10",
    "macro_evidence_recall_at_2",
    "macro_evidence_recall_at_5",
    "macro_evidence_recall_at_10",
    "mean_reciprocal_rank_at_10",
    "mean_reciprocal_rank_at_50",
]

# Aggregate identifiers whose value is deliberately absent (n_valid == 0) for a
# per_question group, mirroring the three per-example @10 hit/recall NaNs.
PER_QUESTION_EMPTY_AGGREGATE_NAMES = [
    "any_evidence_hit_rate_at_10",
    "full_evidence_hit_rate_at_10",
    "macro_evidence_recall_at_10",
]

# ---------------------------------------------------------------------------
# Subgroup files
# ---------------------------------------------------------------------------

SUBGROUP_DIMENSIONS = ("question_type", "level")
SUBGROUP_FILENAME = {
    "question_type": "aggregate_by_question_type.csv",
    "level": "aggregate_by_level.csv",
}
SUBGROUP_VALUE_ORDER = {
    "question_type": QUESTION_TYPE_ORDER,
    "level": LEVEL_ORDER,
}


def aggregate_by_columns(dimension: str) -> List[str]:
    """Column order for a subgroup file: the grouping column is inserted after
    ``setting`` (metric spec / eval schema §aggregate_by)."""
    _require(dimension in SUBGROUP_DIMENSIONS,
             f"subgroup dimension must be one of {SUBGROUP_DIMENSIONS}")
    columns = list(AGGREGATE_COLUMNS)
    insert_at = columns.index("setting") + 1
    columns.insert(insert_at, dimension)
    return columns


# ---------------------------------------------------------------------------
# Central machine-name -> report-label mapping (metric spec §5.3)
# ---------------------------------------------------------------------------

_HIT_RATE_LABEL = {"any": "Any Evidence Hit Rate", "full": "Full Evidence Hit Rate"}

AGGREGATE_REPORT_LABELS = {}
for _k in (2, 5, 10):
    AGGREGATE_REPORT_LABELS[f"any_evidence_hit_rate_at_{_k}"] = f"Any Evidence Hit Rate@{_k}"
    AGGREGATE_REPORT_LABELS[f"full_evidence_hit_rate_at_{_k}"] = f"Full Evidence Hit Rate@{_k}"
    AGGREGATE_REPORT_LABELS[f"macro_evidence_recall_at_{_k}"] = f"Macro Evidence Recall@{_k}"
for _h in (10, 50):
    AGGREGATE_REPORT_LABELS[f"mean_reciprocal_rank_at_{_h}"] = f"MRR@{_h}"
del _k, _h


def report_label(aggregate_metric_name: str) -> str:
    """Return the single canonical presentation label for an aggregate metric
    identifier. Report labels are presentation-only and are never storage
    identifiers or ``metric_name`` values."""
    try:
        return AGGREGATE_REPORT_LABELS[aggregate_metric_name]
    except KeyError:
        raise EvalSchemaError(
            f"no report label for {aggregate_metric_name!r}; it is not a canonical "
            f"aggregate metric identifier"
        )


# ---------------------------------------------------------------------------
# manifest.json contract
# ---------------------------------------------------------------------------

EVAL_MANIFEST_FIELDS = [
    "eval_schema_version",
    "metric_definition_version",
    "evaluation_protocol_version",
    "eval_id",
    "created_at",
    "source_retrieval_run_id",
    "source_rankings_sha256",
    "dataset_identifier",
    "dataset_fingerprint",
    "gold_mapping_version_or_fingerprint",
    "k_policy",
    "aggregation_groups",
    "evaluator_git_commit",
    "command",
    "artifact_sha256",
]

# Frozen k_policy value (eval schema §k_policy). No key/value/array order differs.
K_POLICY = {
    "insufficient_depth_policy": "reject_unless_corpus_exhausted",
    "per_question": {
        "computed_hit_recall_cutoffs": [2, 5],
        "reciprocal_rank_horizons": [10, 50],
        "uncomputed_hit_recall_cutoffs": [10],
    },
    "pooled": {
        "computed_hit_recall_cutoffs": [2, 5, 10],
        "reciprocal_rank_horizons": [10, 50],
        "uncomputed_hit_recall_cutoffs": [],
    },
}

# aggregation_groups always starts with method+setting, then subgroups in the
# fixed order question_type, level.
VALID_AGGREGATION_GROUPS = [
    ["method+setting"],
    ["method+setting", "question_type"],
    ["method+setting", "level"],
    ["method+setting", "question_type", "level"],
]

# eval_id grammar: eval_<retrieval_run_id>_metrics_v2_e<NN>
EVAL_ID_RE = _re.compile(
    r"^eval_(?P<run_id>.+)_metrics_v2_e(?P<seq>\d{2})$"
)

# Legacy-only identifiers that must never appear as active eval columns.
LEGACY_ONLY_IDENTIFIER_RE = _re.compile(
    r"^(any|full|partial)_evidence_recall@\d+$"
)


class EvalSchemaError(ValueError):
    """Raised when an eval bundle violates ``retrieval_eval_schema_v2``."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvalSchemaError(message)


def _is_empty_cell(value) -> bool:
    """The canonical serialized null is an empty CSV cell, loaded as NaN.

    Accepts a zero-length string, Python ``None``, or a float NaN. Literal
    strings ``"NaN"``, ``"None"``, ``"null"`` are NOT nulls and fall through to
    the type checks, which reject them.
    """
    if value is None:
        return True
    if isinstance(value, float) and value != value:
        return True
    if isinstance(value, str) and value == "":
        return True
    return False


# ---------------------------------------------------------------------------
# eval_id
# ---------------------------------------------------------------------------


def validate_eval_id(eval_id: str, source_retrieval_run_id: str = None) -> None:
    """Validate the ``eval_<retrieval_run_id>_metrics_v2_e<NN>`` grammar and,
    when given, that the embedded run ID matches the source run."""
    match = EVAL_ID_RE.match(eval_id) if isinstance(eval_id, str) else None
    _require(match is not None,
             f"eval_id {eval_id!r} must match eval_<retrieval_run_id>_metrics_v2_e<NN>")
    embedded = match.group("run_id")
    _require(_RUN_ID_RE.match(embedded) is not None,
             f"eval_id embeds an invalid retrieval_run_id {embedded!r}")
    if source_retrieval_run_id is not None:
        _require(embedded == source_retrieval_run_id,
                 f"eval_id run segment {embedded!r} must equal "
                 f"source_retrieval_run_id {source_retrieval_run_id!r}")


# ---------------------------------------------------------------------------
# per_example.csv validators
# ---------------------------------------------------------------------------


def validate_per_example_columns(columns: Sequence[str]) -> None:
    """Reject missing/extra/reordered columns and any legacy-only or
    wrong-layer identifier at the per-example layer."""
    for column in columns:
        _require(LEGACY_ONLY_IDENTIFIER_RE.match(column) is None,
                 f"legacy-only identifier {column!r} is not an accepted eval column")
        # Aggregate-layer identifiers must never leak into per-example columns.
        _require(not column.endswith("_rate_at_2")
                 and not column.endswith("_rate_at_5")
                 and not column.endswith("_rate_at_10")
                 and not column.startswith("mean_reciprocal_rank")
                 and not column.startswith("macro_")
                 and column != "mrr"
                 and not column.startswith("mrr_"),
                 f"aggregate/presentation identifier {column!r} must not appear at the "
                 f"per-example layer (use indicator / reciprocal_rank)")
    if list(columns) != PER_EXAMPLE_COLUMNS:
        raise EvalSchemaError(
            f"per_example columns must be exactly the {len(PER_EXAMPLE_COLUMNS)} "
            f"canonical columns in order; got {list(columns)}"
        )


def _validate_indicator_cell(value, column: str, where: str, allow_empty: bool) -> None:
    if _is_empty_cell(value):
        _require(allow_empty, f"{where}: {column} must not be empty here")
        return
    _require(value in (0, 1) and not isinstance(value, bool),
             f"{where}: {column} must serialize as 0 or 1, got {value!r}")


def _validate_unit_float_cell(value, column: str, where: str, allow_empty: bool) -> None:
    if _is_empty_cell(value):
        _require(allow_empty, f"{where}: {column} must not be empty here")
        return
    _require(_is_finite_number(value) and 0.0 <= float(value) <= 1.0,
             f"{where}: {column} must be a finite float in [0, 1], got {value!r}")


def validate_per_example_rows(rows: Sequence[Mapping]) -> None:
    """Validate per-example row content: version stamps, metadata vocabularies,
    metric types/ranges, the per_question @10 null policy, and key uniqueness.

    It checks the STORED values only; it never recomputes any metric from
    titles and gold.
    """
    seen_keys = set()
    for i, row in enumerate(rows):
        where = f"per_example row {i}"

        _require(row.get("eval_schema_version") == RETRIEVAL_EVAL_SCHEMA_V2,
                 f"{where}: eval_schema_version must be {RETRIEVAL_EVAL_SCHEMA_V2!r}")
        _require(row.get("metric_definition_version") == METRIC_DEFINITION_V2,
                 f"{where}: metric_definition_version must be {METRIC_DEFINITION_V2!r}")
        _require(row.get("evaluation_protocol_version") == EVALUATION_PROTOCOL_V2,
                 f"{where}: evaluation_protocol_version must be {EVALUATION_PROTOCOL_V2!r}")

        eval_id = row.get("eval_id")
        validate_eval_id(eval_id, row.get("retrieval_run_id"))

        method = row.get("method")
        setting = row.get("setting")
        _require(method in RAW_METHODS, f"{where}: method {method!r} invalid")
        _require(setting in RAW_SETTINGS, f"{where}: setting {setting!r} invalid")
        _require(row.get("question_type") in QUESTION_TYPES,
                 f"{where}: question_type {row.get('question_type')!r} invalid")
        _require(row.get("level") in LEVELS,
                 f"{where}: level {row.get('level')!r} invalid")

        example_id = row.get("example_id")
        _require(isinstance(example_id, str) and example_id != "",
                 f"{where}: example_id must be a non-empty string")

        gold_count = row.get("gold_title_count")
        _require(_is_int(gold_count) and gold_count >= 1,
                 f"{where}: gold_title_count must be an integer >= 1 (empty gold is "
                 f"rejected upstream), got {gold_count!r}")
        depth = row.get("retrieved_depth")
        _require(_is_int(depth) and depth >= 1,
                 f"{where}: retrieved_depth must be an integer >= 1, got {depth!r}")

        is_per_question = setting == "per_question"
        for column in INDICATOR_COLUMNS:
            allow_empty = is_per_question and column in PER_QUESTION_NULLABLE_COLUMNS
            _validate_indicator_cell(row.get(column, ""), column, where, allow_empty)
        for column in FLOAT_METRIC_COLUMNS:
            allow_empty = is_per_question and column in PER_QUESTION_NULLABLE_COLUMNS
            _validate_unit_float_cell(row.get(column, ""), column, where, allow_empty)

        key = (eval_id, row.get("retrieval_run_id"), example_id)
        _require(key not in seen_keys,
                 f"{where}: duplicate (eval_id, retrieval_run_id, example_id) {key!r}")
        seen_keys.add(key)


# ---------------------------------------------------------------------------
# aggregate.csv validators
# ---------------------------------------------------------------------------


def _validate_aggregate_value_cell(value, n_valid, where: str) -> None:
    if n_valid == 0:
        _require(_is_empty_cell(value),
                 f"{where}: value must be empty when n_valid == 0, got {value!r}")
        return
    _require(not _is_empty_cell(value),
             f"{where}: value must be present when n_valid > 0")
    _require(_is_finite_number(value) and 0.0 <= float(value) <= 1.0,
             f"{where}: value must be a finite float in [0, 1], got {value!r}")


def validate_aggregate_rows(rows: Sequence[Mapping], dimension: str = None) -> None:
    """Validate tidy-long aggregate rows for ``aggregate.csv`` (dimension None)
    or a subgroup file (``dimension`` in ``question_type`` / ``level``).

    Checks version stamps, group vocabularies, canonical ``metric_name``,
    value/``n_valid`` consistency, the per_question @10 empty-aggregate policy,
    and key uniqueness. It never recomputes an aggregate.
    """
    if dimension is not None:
        _require(dimension in SUBGROUP_DIMENSIONS,
                 f"dimension must be one of {SUBGROUP_DIMENSIONS} or None")

    seen_keys = set()
    for i, row in enumerate(rows):
        where = f"aggregate row {i}"

        _require(row.get("eval_schema_version") == RETRIEVAL_EVAL_SCHEMA_V2,
                 f"{where}: eval_schema_version must be {RETRIEVAL_EVAL_SCHEMA_V2!r}")
        _require(row.get("metric_definition_version") == METRIC_DEFINITION_V2,
                 f"{where}: metric_definition_version must be {METRIC_DEFINITION_V2!r}")
        _require(row.get("evaluation_protocol_version") == EVALUATION_PROTOCOL_V2,
                 f"{where}: evaluation_protocol_version must be {EVALUATION_PROTOCOL_V2!r}")

        validate_eval_id(row.get("eval_id"))

        method = row.get("method")
        setting = row.get("setting")
        _require(method in RAW_METHODS, f"{where}: method {method!r} invalid")
        _require(setting in RAW_SETTINGS, f"{where}: setting {setting!r} invalid")

        subgroup_value = None
        if dimension is not None:
            subgroup_value = row.get(dimension)
            allowed = QUESTION_TYPES if dimension == "question_type" else LEVELS
            _require(subgroup_value in allowed,
                     f"{where}: {dimension} {subgroup_value!r} invalid")

        n_questions = row.get("n_questions")
        _require(_is_int(n_questions) and n_questions >= 0,
                 f"{where}: n_questions must be an integer >= 0")

        metric_name = row.get("metric_name")
        _require(metric_name in AGGREGATE_METRIC_NAMES,
                 f"{where}: metric_name {metric_name!r} must be a canonical aggregate "
                 f"identifier")

        n_valid = row.get("n_valid")
        _require(_is_int(n_valid) and 0 <= n_valid <= n_questions,
                 f"{where}: n_valid must be an integer in [0, n_questions]")

        if setting == "per_question" and metric_name in PER_QUESTION_EMPTY_AGGREGATE_NAMES:
            _require(n_valid == 0,
                     f"{where}: per_question {metric_name} must have n_valid == 0")

        _validate_aggregate_value_cell(row.get("value", ""), n_valid, where)

        key_fields = [row.get("eval_id"), method, setting]
        if dimension is not None:
            key_fields.append(subgroup_value)
        key_fields.append(metric_name)
        key = tuple(key_fields)
        _require(key not in seen_keys,
                 f"{where}: duplicate aggregate key {key!r}")
        seen_keys.add(key)


# ---------------------------------------------------------------------------
# manifest.json validators
# ---------------------------------------------------------------------------


def expected_artifact_keys(aggregation_groups: Sequence[str]) -> set:
    """Return the exact ``artifact_sha256`` key set implied by
    ``aggregation_groups`` (the self-referential manifest is excluded)."""
    keys = {"per_example.csv", "aggregate.csv"}
    if "question_type" in aggregation_groups:
        keys.add("aggregate_by_question_type.csv")
    if "level" in aggregation_groups:
        keys.add("aggregate_by_level.csv")
    return keys


def validate_eval_manifest(manifest: Mapping) -> None:
    """Validate an eval ``retrieval_eval_schema_v2`` manifest object.

    Enforces the closed field set, JSON types, the frozen ``k_policy`` value,
    legal ``aggregation_groups`` arrays, the exact ``artifact_sha256`` key set,
    fingerprint/checksum text formats, and version stamps. It never recomputes
    a metric.
    """
    _require(isinstance(manifest, dict), "manifest must be a JSON object")
    _require(set(manifest.keys()) == set(EVAL_MANIFEST_FIELDS),
             f"manifest fields must be exactly {sorted(EVAL_MANIFEST_FIELDS)}; "
             f"missing={sorted(set(EVAL_MANIFEST_FIELDS) - set(manifest))}, "
             f"unexpected={sorted(set(manifest) - set(EVAL_MANIFEST_FIELDS))}")

    _require(manifest["eval_schema_version"] == RETRIEVAL_EVAL_SCHEMA_V2,
             f"eval_schema_version must be {RETRIEVAL_EVAL_SCHEMA_V2!r}")
    _require(manifest["metric_definition_version"] == METRIC_DEFINITION_V2,
             f"metric_definition_version must be {METRIC_DEFINITION_V2!r}")
    _require(manifest["evaluation_protocol_version"] == EVALUATION_PROTOCOL_V2,
             f"evaluation_protocol_version must be {EVALUATION_PROTOCOL_V2!r}")

    validate_eval_id(manifest["eval_id"], manifest["source_retrieval_run_id"])

    _require(CREATED_AT_RE.match(manifest["created_at"]) is not None,
             "created_at must be UTC 'YYYY-MM-DDTHH:MM:SSZ' with no fractional seconds")

    _require(isinstance(manifest["source_retrieval_run_id"], str)
             and _RUN_ID_RE.match(manifest["source_retrieval_run_id"]) is not None,
             "source_retrieval_run_id must be a valid retrieval_run_id")
    _require(isinstance(manifest["source_rankings_sha256"], str)
             and SHA256_HEX_RE.match(manifest["source_rankings_sha256"]) is not None,
             "source_rankings_sha256 must be 64 lowercase hex chars")

    for field in ("dataset_identifier", "gold_mapping_version_or_fingerprint",
                  "evaluator_git_commit", "command"):
        value = manifest[field]
        _require(isinstance(value, str) and value != "",
                 f"{field} must be a non-empty string")

    _require(isinstance(manifest["dataset_fingerprint"], str)
             and SHA256_FINGERPRINT_RE.match(manifest["dataset_fingerprint"]) is not None,
             "dataset_fingerprint must be 'sha256:' + 64 lowercase hex chars")

    _require(manifest["k_policy"] == K_POLICY,
             "k_policy must exactly match the frozen hotpotqa_retrieval_protocol_v2 value")

    groups = manifest["aggregation_groups"]
    _require(isinstance(groups, list) and groups in VALID_AGGREGATION_GROUPS,
             f"aggregation_groups must be one of {VALID_AGGREGATION_GROUPS}, got {groups!r}")

    artifact = manifest["artifact_sha256"]
    _require(isinstance(artifact, dict),
             "artifact_sha256 must be a JSON object")
    _require(set(artifact.keys()) == expected_artifact_keys(groups),
             f"artifact_sha256 keys must be exactly {sorted(expected_artifact_keys(groups))} "
             f"for aggregation_groups {groups!r}, got {sorted(artifact.keys())}")
    for filename, digest in artifact.items():
        _require(isinstance(digest, str) and SHA256_HEX_RE.match(digest) is not None,
                 f"artifact_sha256[{filename!r}] must be 64 lowercase hex chars")


def validate_artifact_checksum(filename: str, file_bytes: bytes, manifest: Mapping) -> None:
    """Verify ``manifest['artifact_sha256'][filename]`` matches the given bytes.

    Used, for example, to confirm the aggregate manifest references the correct
    ``per_example.csv`` checksum before aggregation consumes it.
    """
    artifact = manifest.get("artifact_sha256", {})
    _require(filename in artifact,
             f"{filename!r} is not listed in artifact_sha256")
    actual = compute_sha256(file_bytes)
    expected = artifact[filename]
    _require(actual == expected,
             f"artifact_sha256[{filename!r}] mismatch: manifest {expected!r} != "
             f"actual {actual!r}")
