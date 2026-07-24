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
    RETRIEVAL_RUN_ID_RE as _RUN_ID_RE,
    compute_sha256,
    validate_utc_timestamp,
    validate_retrieval_run_id,
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
# The e<NN> suffix uses ASCII [0-9] (not \d, which also matches non-ASCII Unicode
# decimal digits). The embedded <retrieval_run_id> is validated separately by the
# single canonical validate_retrieval_run_id, which enforces the same ASCII-only
# numeric grammar; there is no second run-ID parser here.
# Like the raw exact-format patterns, this expresses content only and is applied
# with fullmatch() (never `$`-anchored match()), so a trailing LF after the e<NN>
# segment is rejected rather than absorbed by `$` matching before a final newline.
EVAL_ID_RE = _re.compile(
    r"eval_(?P<run_id>.+)_metrics_v2_e(?P<seq>[0-9]{2})"
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


def validate_eval_id(eval_id: str, source_retrieval_run_id: str = None) -> str:
    """Validate the ``eval_<retrieval_run_id>_metrics_v2_e<NN>`` grammar and,
    when given, that the embedded run ID matches the source run. The embedded
    run ID is fully validated (grammar + real date + r>=01), not just its regex
    shape. Returns the embedded ``retrieval_run_id``."""
    # fullmatch (not match) so a trailing LF after the e<NN> segment is rejected,
    # not silently ignored by a `$`-before-newline match.
    match = EVAL_ID_RE.fullmatch(eval_id) if isinstance(eval_id, str) else None
    _require(match is not None,
             f"eval_id {eval_id!r} must match eval_<retrieval_run_id>_metrics_v2_e<NN>")
    # Owner decision: the eval e<NN> sequence uses the same canonical policy as the
    # raw rerun sequence -- ASCII digits only (already enforced by the regex),
    # starting at e01; e00 is invalid. int() on two ASCII digits is always 0..99.
    e_seq = int(match.group("seq"))
    _require(1 <= e_seq <= 99,
             f"eval_id sequence starts at e01; e{match.group('seq')} is invalid "
             f"(ASCII 01-99 only)")
    embedded = match.group("run_id")
    # Full semantic validation of the embedded run ID (raises EvalSchemaError via
    # the shared validator, which raises RawSchemaError -- both are ValueError,
    # but re-wrap for a consistent eval-layer error type).
    try:
        validate_retrieval_run_id(embedded, where="eval_id embedded retrieval_run_id")
    except ValueError as exc:
        raise EvalSchemaError(str(exc))
    if source_retrieval_run_id is not None:
        _require(embedded == source_retrieval_run_id,
                 f"eval_id run segment {embedded!r} must equal "
                 f"source_retrieval_run_id {source_retrieval_run_id!r}")
    return embedded


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


def _validate_indicator_cell(value, column: str, where: str, must_be_empty: bool) -> None:
    if must_be_empty:
        # per_question @10 hit/recall cells are deliberately uncomputed: they
        # must be empty, not merely allowed to be. A populated (even type-valid)
        # value is a protocol violation (metric spec §3, golden §7.5).
        _require(_is_empty_cell(value),
                 f"{where}: {column} must be empty for per_question (deliberately "
                 f"uncomputed @10), got {value!r}")
        return
    _require(not _is_empty_cell(value),
             f"{where}: {column} is required and must not be empty here")
    # The frozen eval physical contract declares every Indicator column `int 0/1`
    # and says "Indicators serialize as integer 0 or 1". Require a schema integer
    # BEFORE the value membership check: Python treats 1.0 == 1 and -0.0 == 0, so a
    # bare `value in (0, 1)` membership test would silently accept the prohibited
    # floats 1.0/0.0/-0.0 (and, without the bool guard, True/False). Reuse the
    # shared _is_int, which already excludes bool (an int subclass); it also rejects
    # any float or string. No cast/round/normalize -- a float like 1.0 is rejected,
    # not converted. Recall/RR stay float (see _validate_unit_float_cell).
    _require(_is_int(value) and value in (0, 1),
             f"{where}: {column} must serialize as integer 0 or 1 (a float such as "
             f"1.0/0.0/-0.0, a bool, or a string is not an integer Indicator), "
             f"got {value!r}")


def _validate_unit_float_cell(value, column: str, where: str, must_be_empty: bool) -> None:
    if must_be_empty:
        _require(_is_empty_cell(value),
                 f"{where}: {column} must be empty for per_question (deliberately "
                 f"uncomputed @10), got {value!r}")
        return
    _require(not _is_empty_cell(value),
             f"{where}: {column} is required and must not be empty here")
    _require(_is_finite_number(value) and 0.0 <= float(value) <= 1.0,
             f"{where}: {column} must be a finite float in [0, 1], got {value!r}")


def validate_per_example_rows(rows: Sequence[Mapping], manifest: Mapping = None) -> None:
    """Validate per-example row content and bundle composition.

    Per row: exact key set, version stamps, metadata vocabularies,
    method/setting agreement with the embedded ``retrieval_run_id`` segments,
    metric types/ranges, the per_question @10 required-empty policy, and key
    uniqueness. Across the file (a bundle): at least one row (the source raw run
    has ``n_loaded >= 1``, so a complete per_example file is never empty); rows in
    ascending ``example_id`` order (the frozen serialization order, mirroring the
    raw rankings' ascending-``example_id`` order); exactly one ``eval_id``, one
    source ``retrieval_run_id``, and one ``method``/``setting`` -- a per_example
    file never mixes more than one raw run. When ``manifest`` is given, the single
    ``eval_id`` and source run must equal the manifest values.

    It checks the STORED values only; it never recomputes any metric.
    """
    rows = list(rows)
    _require(len(rows) >= 1,
             "a complete per_example file must contain at least one row "
             "(the source raw run has n_loaded >= 1)")

    eval_ids = set()
    run_ids = set()
    method_settings = set()
    seen_keys = set()
    prev_example_id = None
    retrieved_depths = []

    for i, row in enumerate(rows):
        where = f"per_example row {i}"

        _require(set(row.keys()) == set(PER_EXAMPLE_COLUMNS),
                 f"{where}: keys must be exactly the {len(PER_EXAMPLE_COLUMNS)} canonical "
                 f"per_example columns; missing={sorted(set(PER_EXAMPLE_COLUMNS) - set(row))}, "
                 f"unexpected={sorted(set(row) - set(PER_EXAMPLE_COLUMNS))}")

        _require(row.get("eval_schema_version") == RETRIEVAL_EVAL_SCHEMA_V2,
                 f"{where}: eval_schema_version must be {RETRIEVAL_EVAL_SCHEMA_V2!r}")
        _require(row.get("metric_definition_version") == METRIC_DEFINITION_V2,
                 f"{where}: metric_definition_version must be {METRIC_DEFINITION_V2!r}")
        _require(row.get("evaluation_protocol_version") == EVALUATION_PROTOCOL_V2,
                 f"{where}: evaluation_protocol_version must be {EVALUATION_PROTOCOL_V2!r}")

        eval_id = row.get("eval_id")
        run_id = row.get("retrieval_run_id")
        # Ensures eval_id grammar and that its embedded run == this row's run_id.
        validate_eval_id(eval_id, run_id)

        method = row.get("method")
        setting = row.get("setting")
        _require(method in RAW_METHODS, f"{where}: method {method!r} invalid")
        _require(setting in RAW_SETTINGS, f"{where}: setting {setting!r} invalid")
        # method/setting must match the source run encoded in retrieval_run_id.
        # run_id was already whole-string validated above (validate_eval_id checked
        # its embedded run == run_id via fullmatch); fullmatch here keeps the shared
        # whole-string rule and safely extracts the segments.
        run_match = _RUN_ID_RE.fullmatch(run_id)
        _require(run_match.group("method") == method,
                 f"{where}: method {method!r} must match retrieval_run_id method segment "
                 f"{run_match.group('method')!r}")
        _require(run_match.group("setting") == setting,
                 f"{where}: setting {setting!r} must match retrieval_run_id setting segment "
                 f"{run_match.group('setting')!r}")
        _require(row.get("question_type") in QUESTION_TYPES,
                 f"{where}: question_type {row.get('question_type')!r} invalid")
        _require(row.get("level") in LEVELS,
                 f"{where}: level {row.get('level')!r} invalid")

        example_id = row.get("example_id")
        _require(isinstance(example_id, str) and example_id != "",
                 f"{where}: example_id must be a non-empty string")
        # Physical order mirrors the raw rankings: strictly ascending example_id
        # (Unicode code point). One row per example, so equal IDs are duplicates.
        if prev_example_id is not None:
            _require(prev_example_id < example_id,
                     f"{where}: per_example rows must be in ascending example_id order "
                     f"(the source rankings order); {example_id!r} does not come after "
                     f"{prev_example_id!r}")
        prev_example_id = example_id

        gold_count = row.get("gold_title_count")
        _require(_is_int(gold_count) and gold_count >= 1,
                 f"{where}: gold_title_count must be an integer >= 1 (empty gold is "
                 f"rejected upstream), got {gold_count!r}")
        depth = row.get("retrieved_depth")
        _require(_is_int(depth) and depth >= 1,
                 f"{where}: retrieved_depth must be an integer >= 1, got {depth!r}")
        retrieved_depths.append(depth)

        is_per_question = setting == "per_question"
        for column in INDICATOR_COLUMNS:
            must_be_empty = is_per_question and column in PER_QUESTION_NULLABLE_COLUMNS
            _validate_indicator_cell(row[column], column, where, must_be_empty)
        for column in FLOAT_METRIC_COLUMNS:
            must_be_empty = is_per_question and column in PER_QUESTION_NULLABLE_COLUMNS
            _validate_unit_float_cell(row[column], column, where, must_be_empty)

        key = (eval_id, run_id, example_id)
        _require(key not in seen_keys,
                 f"{where}: duplicate (eval_id, retrieval_run_id, example_id) {key!r}")
        seen_keys.add(key)

        eval_ids.add(eval_id)
        run_ids.add(run_id)
        method_settings.add((method, setting))

    _require(len(eval_ids) == 1,
             f"a per_example bundle must contain exactly one eval_id, got {eval_ids}")
    _require(len(run_ids) == 1,
             f"a per_example bundle must reference exactly one source retrieval_run_id, "
             f"got {run_ids}")
    _require(len(method_settings) == 1,
             f"a per_example bundle must have exactly one method/setting, "
             f"got {method_settings}")

    # Finding F: bind file cardinality and per-row depth to the single source
    # run's n<N>/d<depth>, both parsed straight from the one retrieval_run_id (no
    # manifest, no metric recomputation). Under the frozen one-run/one-row-per-
    # example serialization contract a complete file must cover every source
    # example, so its row count equals n and no example's saved depth exceeds d.
    source_run_id = next(iter(run_ids))
    source_match = _RUN_ID_RE.fullmatch(source_run_id)
    source_n = int(source_match.group("n"))
    source_depth = int(source_match.group("depth"))
    _require(len(rows) == source_n,
             f"a complete per_example file must contain exactly n={source_n} rows "
             f"(one per source example, from the run-ID n segment), got {len(rows)}")
    for d in retrieved_depths:
        _require(d <= source_depth,
                 f"retrieved_depth {d} must not exceed the source run d={source_depth}")
    (_, setting) = next(iter(method_settings))
    if setting == "per_question":
        # d<depth> is the maximum per-example saved depth, so it must be attained.
        _require(max(retrieved_depths) == source_depth,
                 f"per_question d={source_depth} must equal the maximum saved "
                 f"retrieved_depth across examples, got {max(retrieved_depths)}")
    else:
        # A pooled run has one fixed retrieval depth, so every example shares the
        # same saved depth. Exact corpus-exhaustion binding (== corpus_size) is a
        # raw-layer concern; the eval contract has no corpus_size field.
        _require(len(set(retrieved_depths)) == 1,
                 f"a pooled per_example file must have one shared retrieved_depth "
                 f"across examples, got {sorted(set(retrieved_depths))}")

    if manifest is not None:
        _require(eval_ids == {manifest.get("eval_id")},
                 "per_example eval_id must equal the manifest eval_id")
        _require(run_ids == {manifest.get("source_retrieval_run_id")},
                 "per_example retrieval_run_id must equal the manifest "
                 "source_retrieval_run_id")


# ---------------------------------------------------------------------------
# aggregate.csv validators
# ---------------------------------------------------------------------------


def validate_aggregate_columns(columns: Sequence[str], dimension: str = None) -> None:
    """Reject missing/extra/reordered aggregate columns for ``aggregate.csv``
    (``dimension`` None) or a subgroup file (``question_type`` / ``level``)."""
    expected = AGGREGATE_COLUMNS if dimension is None else aggregate_by_columns(dimension)
    if list(columns) != expected:
        raise EvalSchemaError(
            f"aggregate columns must be exactly {expected} in order, got {list(columns)}")


def _expected_aggregate_n_valid(setting: str, metric_name: str, n_questions: int) -> int:
    """The frozen null policy fixes ``n_valid`` exactly: only the three
    per_question @10 hit/recall aggregates may drop values (``n_valid = 0``);
    every other metric has no permitted per-example NaN, so ``n_valid`` equals
    the group's ``n_questions``. This is a nullability rule, not a recomputation
    of the metric value."""
    if setting == "per_question" and metric_name in PER_QUESTION_EMPTY_AGGREGATE_NAMES:
        return 0
    return n_questions


def _validate_aggregate_value_cell(value, n_valid, where: str) -> None:
    if n_valid == 0:
        _require(_is_empty_cell(value),
                 f"{where}: value must be empty when n_valid == 0, got {value!r}")
        return
    _require(not _is_empty_cell(value),
             f"{where}: value must be present when n_valid > 0")
    _require(_is_finite_number(value) and 0.0 <= float(value) <= 1.0,
             f"{where}: value must be a finite float in [0, 1], got {value!r}")


def validate_aggregate_row(row: Mapping, dimension: str = None, where: str = "aggregate row") -> None:
    """Validate a single tidy-long aggregate row.

    Checks the exact key set, version stamps, group vocabularies, canonical
    ``metric_name``, the frozen ``n_valid`` value (mandatory metrics equal
    ``n_questions``; per_question @10 equal 0), and value/``n_valid``
    consistency. It never recomputes an aggregate value.
    """
    if dimension is not None:
        _require(dimension in SUBGROUP_DIMENSIONS,
                 f"dimension must be one of {SUBGROUP_DIMENSIONS} or None")
    expected_cols = AGGREGATE_COLUMNS if dimension is None else aggregate_by_columns(dimension)
    _require(set(row.keys()) == set(expected_cols),
             f"{where}: keys must be exactly {expected_cols}; "
             f"missing={sorted(set(expected_cols) - set(row))}, "
             f"unexpected={sorted(set(row) - set(expected_cols))}")

    _require(row.get("eval_schema_version") == RETRIEVAL_EVAL_SCHEMA_V2,
             f"{where}: eval_schema_version must be {RETRIEVAL_EVAL_SCHEMA_V2!r}")
    _require(row.get("metric_definition_version") == METRIC_DEFINITION_V2,
             f"{where}: metric_definition_version must be {METRIC_DEFINITION_V2!r}")
    _require(row.get("evaluation_protocol_version") == EVALUATION_PROTOCOL_V2,
             f"{where}: evaluation_protocol_version must be {EVALUATION_PROTOCOL_V2!r}")

    embedded_run = validate_eval_id(row.get("eval_id"))

    method = row.get("method")
    setting = row.get("setting")
    _require(method in RAW_METHODS, f"{where}: method {method!r} invalid")
    _require(setting in RAW_SETTINGS, f"{where}: setting {setting!r} invalid")
    # method/setting must match the raw run encoded in eval_id (one eval bundle
    # corresponds to exactly one raw retrieval run).
    run_match = _RUN_ID_RE.fullmatch(embedded_run)
    _require(run_match.group("method") == method,
             f"{where}: method {method!r} must match the eval_id source run method "
             f"{run_match.group('method')!r}")
    _require(run_match.group("setting") == setting,
             f"{where}: setting {setting!r} must match the eval_id source run setting "
             f"{run_match.group('setting')!r}")

    if dimension is not None:
        allowed = QUESTION_TYPES if dimension == "question_type" else LEVELS
        _require(row.get(dimension) in allowed,
                 f"{where}: {dimension} {row.get(dimension)!r} invalid")

    n_questions = row.get("n_questions")
    _require(_is_int(n_questions) and n_questions >= 0,
             f"{where}: n_questions must be an integer >= 0")

    metric_name = row.get("metric_name")
    _require(metric_name in AGGREGATE_METRIC_NAMES,
             f"{where}: metric_name {metric_name!r} must be a canonical aggregate identifier")

    n_valid = row.get("n_valid")
    _require(_is_int(n_valid), f"{where}: n_valid must be an integer, got {n_valid!r}")
    expected_n_valid = _expected_aggregate_n_valid(setting, metric_name, n_questions)
    _require(n_valid == expected_n_valid,
             f"{where}: n_valid for {setting} {metric_name} must be {expected_n_valid} "
             f"(mandatory metrics use n_questions; only per_question @10 uses 0), "
             f"got {n_valid}")

    _validate_aggregate_value_cell(row.get("value", ""), n_valid, where)


def validate_aggregate_rows(rows: Sequence[Mapping], dimension: str = None,
                            manifest: Mapping = None) -> None:
    """Validate a complete tidy-long aggregate file: ``aggregate.csv``
    (``dimension`` None) or a subgroup file (``question_type`` / ``level``).

    Per row: :func:`validate_aggregate_row`. Across the file: at least one row;
    each group is a CONTIGUOUS block of exactly the 11 canonical metrics once, in
    canonical order; ``n_questions`` is constant within a group; subgroup blocks
    appear in their frozen value order; the file is a single bundle (one
    ``eval_id``, one ``method``/``setting``). When ``manifest`` is given, the
    ``eval_id`` must match and -- for a subgroup file -- the dimension must be
    declared in ``aggregation_groups`` and its file present in ``artifact_sha256``.
    It never recomputes an aggregate.
    """
    if dimension is not None:
        _require(dimension in SUBGROUP_DIMENSIONS,
                 f"dimension must be one of {SUBGROUP_DIMENSIONS} or None")

    rows = list(rows)
    _require(len(rows) >= 1,
             "a complete aggregate file must contain at least one row "
             "(the default group has all 11 metrics; the source run has n_loaded >= 1)")

    eval_ids = set()
    method_settings = set()

    for i, row in enumerate(rows):
        validate_aggregate_row(row, dimension=dimension, where=f"aggregate row {i}")
        eval_ids.add(row["eval_id"])
        method_settings.add((row["method"], row["setting"]))

    _require(len(eval_ids) == 1,
             f"an aggregate file must contain exactly one eval_id, got {eval_ids}")
    _require(len(method_settings) == 1,
             f"an aggregate file must have exactly one method/setting, got {method_settings}")

    # Split into consecutive blocks by group key; a group must be one contiguous
    # block (never re-entered), with exactly the 11 canonical metrics in order and
    # a single n_questions value.
    def group_key_of(row):
        base = (row["method"], row["setting"])
        return base + (row[dimension],) if dimension is not None else base

    blocks = []  # list of (group_key, [rows])
    for row in rows:
        gk = group_key_of(row)
        if not blocks or blocks[-1][0] != gk:
            blocks.append((gk, []))
        blocks[-1][1].append(row)

    seen_groups = set()
    for gk, block in blocks:
        _require(gk not in seen_groups,
                 f"group {gk} rows must form one contiguous block, not be interleaved")
        seen_groups.add(gk)
        _require([r["metric_name"] for r in block] == AGGREGATE_METRIC_NAMES,
                 f"group {gk} must contain exactly the 11 canonical aggregate metrics "
                 f"once, in canonical order; got {[r['metric_name'] for r in block]}")
        n_questions_values = {r["n_questions"] for r in block}
        _require(len(n_questions_values) == 1,
                 f"group {gk} must use one n_questions across its metric rows, "
                 f"got {n_questions_values}")

    if dimension is not None:
        order = list(SUBGROUP_VALUE_ORDER[dimension])
        block_values = [gk[-1] for gk, _ in blocks]
        positions = [order.index(v) for v in block_values]
        _require(positions == sorted(positions),
                 f"{dimension} blocks must appear in canonical order {order}; "
                 f"got {block_values}")

    # Finding F: bind the aggregate question counts to the single source run's
    # n<N> (parsed from the run embedded in the one eval_id -- no manifest, no
    # recomputation). The default file's one group counts every source question;
    # a subgroup file partitions the same questions, so its blocks' n_questions
    # sum to n. Comparing stored structural counts to encoded provenance, never
    # recalculating an aggregate value.
    source_n = int(_RUN_ID_RE.fullmatch(
        EVAL_ID_RE.fullmatch(next(iter(eval_ids))).group("run_id")).group("n"))
    block_n_questions = [next(iter({r["n_questions"] for r in block}))
                         for _, block in blocks]
    if dimension is None:
        _require(block_n_questions[0] == source_n,
                 f"the default aggregate group n_questions must equal the source "
                 f"run n={source_n}, got {block_n_questions[0]}")
    else:
        total = sum(block_n_questions)
        _require(total == source_n,
                 f"the {dimension} subgroup blocks' n_questions must sum to the "
                 f"source run n={source_n}, got {block_n_questions} (sum {total})")

    if manifest is not None:
        _require(eval_ids == {manifest.get("eval_id")},
                 "aggregate eval_id must equal the manifest eval_id")
        if dimension is not None:
            groups = manifest.get("aggregation_groups") or []
            _require(dimension in groups,
                     f"a {dimension} subgroup file requires {dimension!r} in the manifest "
                     f"aggregation_groups {groups!r}")
            artifact = manifest.get("artifact_sha256") or {}
            _require(SUBGROUP_FILENAME[dimension] in artifact,
                     f"the manifest artifact_sha256 must include "
                     f"{SUBGROUP_FILENAME[dimension]!r}")


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

    validate_utc_timestamp(manifest["created_at"], "created_at")

    # Full semantic validation of the source run ID (grammar + real date + r>=01),
    # not just its regex shape.
    try:
        validate_retrieval_run_id(manifest["source_retrieval_run_id"],
                                  where="source_retrieval_run_id")
    except ValueError as exc:
        raise EvalSchemaError(str(exc))
    _require(isinstance(manifest["source_rankings_sha256"], str)
             and SHA256_HEX_RE.fullmatch(manifest["source_rankings_sha256"]) is not None,
             "source_rankings_sha256 must be 64 lowercase hex chars")

    for field in ("dataset_identifier", "gold_mapping_version_or_fingerprint",
                  "evaluator_git_commit", "command"):
        value = manifest[field]
        _require(isinstance(value, str) and value != "",
                 f"{field} must be a non-empty string")

    _require(isinstance(manifest["dataset_fingerprint"], str)
             and SHA256_FINGERPRINT_RE.fullmatch(manifest["dataset_fingerprint"]) is not None,
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
        _require(isinstance(digest, str) and SHA256_HEX_RE.fullmatch(digest) is not None,
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
