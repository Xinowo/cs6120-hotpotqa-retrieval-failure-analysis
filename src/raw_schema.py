"""
raw_schema.py

Stage 2 schema constants and contract-only validators for the RAW retrieval
layer of the metrics/schema v2 refactor. This is the independent raw contract:
it deliberately does NOT reuse the mixed-purpose ``RESULT_COLUMNS`` from
:mod:`src.results_schema`, which packs retrieval output, dataset metadata, and
per-example metrics into one CSV.

Authoritative frozen contract:
``docs/specs/2026-07-20-raw-retrieval-rankings-schema.md`` (bundle version
``retrieval_raw_schema_v1``). This module only encodes that physical contract
(column set/order, manifest field types, closed nested shapes, ID grammar,
per-question completeness, pooled-depth exhaustion, serialization/checksum
rules). It stores no gold, computes no metric, and defines no metric.

AI-usage boundary: pure schema/plumbing and validation. No metric definition,
formula, or core evaluator computation lives here (those stay team-owned in
:mod:`src.evaluator`). Validators check schema, types, ranges, nullability, and
provenance only; they never recompute or redefine a metric.
"""

import hashlib
import re
from typing import Dict, List, Mapping, Sequence

# ---------------------------------------------------------------------------
# Version identifiers
# ---------------------------------------------------------------------------

# One bundle-level version covers both manifest.json and rankings.csv.
RETRIEVAL_RAW_SCHEMA_V1 = "retrieval_raw_schema_v1"
# Migration-only, score-free ranked titles; never a formal v1 artifact.
LEGACY_RAW_SCHEMA_V0 = "legacy_raw_schema_v0"

# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------

RAW_METHODS = ("bm25", "dense", "rerank")
RAW_SETTINGS = ("pooled", "per_question")

SCORE_TYPE_BY_METHOD = {
    "dense": "cosine_similarity",
    "bm25": "bm25_okapi",
    "rerank": "cross_encoder_logit",
}
SCORE_DIRECTION = "higher_is_better"

# Closed deduplication-policy identifiers, keyed by (method_class, setting)
# where method_class is "dense_bm25" for the two lexical/dense retrievers or
# "rerank" for the reranker (which never changes the parent candidate set).
DEDUPLICATION_POLICIES = {
    ("dense_bm25", "pooled"): "exact_title_keep_first_dataset_order",
    ("dense_bm25", "per_question"): "none_preserve_source_order",
    ("rerank", "pooled"): "none_parent_candidate_set_unchanged",
}

# Closed tie-break identifiers, keyed by method_class.
TIE_BREAK_POLICIES = {
    "dense_bm25": "score_desc_then_corpus_order_asc",
    "rerank": "score_desc_then_parent_rank_asc",
}

VALID_DEDUPLICATION_POLICIES = frozenset(DEDUPLICATION_POLICIES.values())
VALID_TIE_BREAK_POLICIES = frozenset(TIE_BREAK_POLICIES.values())

# ---------------------------------------------------------------------------
# rankings.csv column contract (fixed order)
# ---------------------------------------------------------------------------

RANKING_COLUMNS = [
    "retrieval_run_id",
    "method",
    "setting",
    "example_id",
    "rank",
    "title",
    "score",
]

# ---------------------------------------------------------------------------
# manifest.json field contract
# ---------------------------------------------------------------------------

# Fields present in every raw v1 manifest (order kept for documentation only;
# JSON object key order is not part of the contract).
RAW_MANIFEST_ALWAYS_FIELDS = [
    "raw_schema_version",
    "retrieval_run_id",
    "created_at",
    "method",
    "setting",
    "split",
    "n_requested",
    "n_loaded",
    "retrieval_depth",
    "score_type",
    "score_direction",
    "model_or_retriever_config",
    "dataset_identifier",
    "dataset_fingerprint",
    "example_ids_fingerprint",
    "corpus_fingerprint",
    "deduplication_policy",
    "tie_break_policy",
    "git_commit",
    "command",
    "rankings_sha256",
]

# Present only for setting == "pooled".
RAW_MANIFEST_POOLED_ONLY_FIELDS = ["corpus_size"]
# Present only for setting == "per_question".
RAW_MANIFEST_PER_QUESTION_ONLY_FIELDS = ["per_example_corpus_size"]
# Present only for method == "rerank".
RAW_MANIFEST_RERANK_ONLY_FIELDS = [
    "parent_retrieval_run_id",
    "parent_rankings_sha256",
    "parent_candidate_depth",
]

MODEL_CONFIG_KEYS = ("implementation", "identifier", "parameters")

# ---------------------------------------------------------------------------
# ID grammar and fingerprint/checksum text formats
# ---------------------------------------------------------------------------

# <method>_<setting>_n<N>_d<depth>_<YYYYMMDD>_r<NN>
RETRIEVAL_RUN_ID_RE = re.compile(
    r"^(?P<method>bm25|dense|rerank)"
    r"_(?P<setting>pooled|per_question)"
    r"_n(?P<n>\d+)"
    r"_d(?P<depth>\d+)"
    r"_(?P<date>\d{8})"
    r"_r(?P<seq>\d{2})$"
)

# Bare rankings/parent checksum: 64 lowercase hex chars, no prefix.
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
# Fingerprint fields: "sha256:" prefix followed by 64 lowercase hex chars.
SHA256_FINGERPRINT_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

CREATED_AT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class RawSchemaError(ValueError):
    """Raised when a raw retrieval bundle violates ``retrieval_raw_schema_v1``."""


# ---------------------------------------------------------------------------
# Small typed-value helpers (schema checks only; never metric logic)
# ---------------------------------------------------------------------------


def _method_class(method: str) -> str:
    return "rerank" if method == "rerank" else "dense_bm25"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RawSchemaError(message)


def _is_int(value) -> bool:
    # Reject bool: it is an int subclass but never a valid schema integer here.
    return isinstance(value, int) and not isinstance(value, bool)


def _is_finite_number(value) -> bool:
    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    return value == value and value not in (float("inf"), float("-inf"))


def compute_sha256(data: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of exact ``data`` bytes."""
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# rankings.csv validators
# ---------------------------------------------------------------------------


def validate_rankings_columns(columns: Sequence[str]) -> None:
    """Reject any missing, extra, or reordered rankings column."""
    if list(columns) != RANKING_COLUMNS:
        raise RawSchemaError(
            f"rankings columns must be exactly {RANKING_COLUMNS} in order, "
            f"got {list(columns)}"
        )


def validate_rankings_rows(rows: Sequence[Mapping], manifest: Mapping) -> None:
    """Validate rankings row content against the manifest.

    Checks value vocabularies, run-ID/method/setting agreement with the
    manifest, per-example 1-based contiguous ranks, key uniqueness, and finite
    numeric scores. It never inspects gold or recomputes a metric.
    """
    run_id = manifest.get("retrieval_run_id")
    method = manifest.get("method")
    setting = manifest.get("setting")

    seen_keys = set()
    ranks_by_example: Dict[str, List[int]] = {}

    for i, row in enumerate(rows):
        where = f"rankings row {i}"
        _require(row.get("retrieval_run_id") == run_id,
                 f"{where}: retrieval_run_id must match manifest {run_id!r}")
        _require(row.get("method") == method,
                 f"{where}: method must match manifest {method!r}")
        _require(row.get("setting") == setting,
                 f"{where}: setting must match manifest {setting!r}")

        example_id = row.get("example_id")
        _require(isinstance(example_id, str) and example_id != "",
                 f"{where}: example_id must be a non-empty string")

        rank = row.get("rank")
        _require(_is_int(rank) and rank >= 1,
                 f"{where}: rank must be an integer >= 1, got {rank!r}")

        title = row.get("title")
        _require(isinstance(title, str),
                 f"{where}: title must be a string")

        score = row.get("score")
        _require(_is_finite_number(score),
                 f"{where}: score must be a finite number, got {score!r}")

        key = (run_id, example_id, rank)
        _require(key not in seen_keys,
                 f"{where}: duplicate (retrieval_run_id, example_id, rank) {key!r}")
        seen_keys.add(key)

        ranks_by_example.setdefault(example_id, []).append(rank)

    for example_id, ranks in ranks_by_example.items():
        expected = list(range(1, len(ranks) + 1))
        if sorted(ranks) != expected:
            raise RawSchemaError(
                f"example {example_id!r}: ranks must be 1-based and contiguous "
                f"with no gaps or duplicates, got {sorted(ranks)}"
            )


def saved_depth_by_example(rows: Sequence[Mapping]) -> Dict[str, int]:
    """Return the saved row count (depth) per ``example_id``.

    This is a structural count of ranking rows, not a metric.
    """
    depths: Dict[str, int] = {}
    for row in rows:
        depths[row["example_id"]] = depths.get(row["example_id"], 0) + 1
    return depths


def validate_pooled_depth(rows: Sequence[Mapping], manifest: Mapping) -> None:
    """Validate pooled saved depth as ``min(retrieval_depth, corpus_size)``.

    A short ranking is legal only because the corpus was exhausted
    (``corpus_size < retrieval_depth``); the same short depth with a larger
    corpus is cap-induced truncation and is rejected.
    """
    _require(manifest.get("setting") == "pooled",
             "validate_pooled_depth requires a pooled manifest")
    retrieval_depth = manifest.get("retrieval_depth")
    corpus_size = manifest.get("corpus_size")
    _require(_is_int(retrieval_depth) and retrieval_depth >= 1,
             "pooled retrieval_depth must be an integer >= 1")
    _require(_is_int(corpus_size) and corpus_size >= 1,
             "pooled corpus_size must be an integer >= 1")

    expected_depth = min(retrieval_depth, corpus_size)
    for example_id, depth in saved_depth_by_example(rows).items():
        if depth != expected_depth:
            raise RawSchemaError(
                f"pooled example {example_id!r}: saved depth {depth} must equal "
                f"min(retrieval_depth={retrieval_depth}, corpus_size={corpus_size})"
                f"={expected_depth}; a shorter depth is legal only when the "
                f"corpus is exhausted, otherwise it is cap-induced truncation"
            )


def validate_per_question_completeness(rows: Sequence[Mapping], manifest: Mapping) -> None:
    """Validate per-question complete-mini-corpus storage.

    Requires ``saved_depth(example) == per_example_corpus_size(example)`` for
    every example, an exact key-set match against the ranked example IDs,
    positive sizes, and ``retrieval_depth == max(per_example_corpus_size)``.
    """
    _require(manifest.get("setting") == "per_question",
             "validate_per_question_completeness requires a per_question manifest")
    size_map = manifest.get("per_example_corpus_size")
    _require(isinstance(size_map, dict),
             "per_example_corpus_size must be a JSON object")

    saved = saved_depth_by_example(rows)

    _require(set(size_map.keys()) == set(saved.keys()),
             "per_example_corpus_size keys must equal the ranked example_id set; "
             f"missing={set(saved) - set(size_map)}, extra={set(size_map) - set(saved)}")

    for example_id, size in size_map.items():
        _require(_is_int(size) and size >= 1,
                 f"per_example_corpus_size[{example_id!r}] must be an integer >= 1, "
                 f"got {size!r}")
        _require(saved[example_id] == size,
                 f"per_question example {example_id!r}: saved depth "
                 f"{saved[example_id]} must equal its complete mini-corpus size "
                 f"{size} (no cap-induced truncation)")

    retrieval_depth = manifest.get("retrieval_depth")
    _require(_is_int(retrieval_depth),
             "retrieval_depth must be an integer")
    _require(retrieval_depth == max(size_map.values()),
             f"retrieval_depth ({retrieval_depth}) must equal "
             f"max(per_example_corpus_size)={max(size_map.values())}")


# ---------------------------------------------------------------------------
# manifest.json validators
# ---------------------------------------------------------------------------


def _validate_model_config(config: Mapping) -> None:
    _require(isinstance(config, dict),
             "model_or_retriever_config must be a JSON object")
    _require(set(config.keys()) == set(MODEL_CONFIG_KEYS),
             f"model_or_retriever_config must have exactly keys {MODEL_CONFIG_KEYS}, "
             f"got {sorted(config.keys())}")
    _require(isinstance(config["implementation"], str) and config["implementation"] != "",
             "model_or_retriever_config.implementation must be a non-empty string")
    _require(isinstance(config["identifier"], str) and config["identifier"] != "",
             "model_or_retriever_config.identifier must be a non-empty string")
    _require(isinstance(config["parameters"], dict),
             "model_or_retriever_config.parameters must be a JSON object")
    _validate_json_value(config["parameters"], "model_or_retriever_config.parameters")


def _validate_json_value(value, where: str) -> None:
    """Recursively validate the JSONValue grammar (finite numbers only)."""
    if value is None or isinstance(value, str):
        return
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        _require(_is_finite_number(value), f"{where}: numbers must be finite")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _validate_json_value(item, f"{where}[{i}]")
        return
    if isinstance(value, dict):
        for k, v in value.items():
            _require(isinstance(k, str), f"{where}: object keys must be strings")
            _validate_json_value(v, f"{where}.{k}")
        return
    raise RawSchemaError(f"{where}: unsupported JSON value type {type(value).__name__}")


def expected_manifest_fields(method: str, setting: str) -> set:
    """Return the exact top-level manifest field set for method/setting."""
    fields = set(RAW_MANIFEST_ALWAYS_FIELDS)
    if setting == "pooled":
        fields.update(RAW_MANIFEST_POOLED_ONLY_FIELDS)
    elif setting == "per_question":
        fields.update(RAW_MANIFEST_PER_QUESTION_ONLY_FIELDS)
    if method == "rerank":
        fields.update(RAW_MANIFEST_RERANK_ONLY_FIELDS)
    return fields


def validate_manifest(manifest: Mapping) -> None:
    """Validate a raw ``retrieval_raw_schema_v1`` manifest object.

    Enforces the closed field set (conditional fields present exactly under
    their setting/method), JSON types, value vocabularies, closed nested
    shapes, ID grammar, fingerprint/checksum text formats, and per-question
    completeness of the size map. It never recomputes a metric.
    """
    _require(isinstance(manifest, dict), "manifest must be a JSON object")

    version = manifest.get("raw_schema_version")
    _require(version == RETRIEVAL_RAW_SCHEMA_V1,
             f"raw_schema_version must be {RETRIEVAL_RAW_SCHEMA_V1!r} for a formal "
             f"v1 manifest, got {version!r} (a score-free migration input uses "
             f"{LEGACY_RAW_SCHEMA_V0!r} and is validated by the migration adapter)")

    method = manifest.get("method")
    setting = manifest.get("setting")
    _require(method in RAW_METHODS, f"method must be one of {RAW_METHODS}, got {method!r}")
    _require(setting in RAW_SETTINGS, f"setting must be one of {RAW_SETTINGS}, got {setting!r}")
    if method == "rerank":
        _require(setting == "pooled",
                 "a v1 rerank run requires setting == 'pooled'")

    expected = expected_manifest_fields(method, setting)
    actual = set(manifest.keys())
    _require(actual == expected,
             f"manifest fields must be exactly {sorted(expected)} for "
             f"method={method!r} setting={setting!r}; missing={sorted(expected - actual)}, "
             f"unexpected={sorted(actual - expected)}")

    run_id = manifest["retrieval_run_id"]
    match = RETRIEVAL_RUN_ID_RE.match(run_id) if isinstance(run_id, str) else None
    _require(match is not None,
             f"retrieval_run_id {run_id!r} must match the frozen grammar "
             f"<method>_<setting>_n<N>_d<depth>_<YYYYMMDD>_r<NN>")
    _require(match.group("method") == method,
             "retrieval_run_id method segment must match manifest method")
    _require(match.group("setting") == setting,
             "retrieval_run_id setting segment must match manifest setting")

    _require(CREATED_AT_RE.match(manifest["created_at"]) is not None,
             "created_at must be UTC 'YYYY-MM-DDTHH:MM:SSZ' with no fractional seconds")

    _require(isinstance(manifest["split"], str) and manifest["split"] != "",
             "split must be a non-empty string")

    n_requested = manifest["n_requested"]
    n_loaded = manifest["n_loaded"]
    _require(_is_int(n_requested) and n_requested >= 1, "n_requested must be an integer >= 1")
    _require(_is_int(n_loaded) and n_loaded >= 1, "n_loaded must be an integer >= 1")

    retrieval_depth = manifest["retrieval_depth"]
    _require(_is_int(retrieval_depth) and retrieval_depth >= 1,
             "retrieval_depth must be an integer >= 1")

    _require(manifest["score_type"] == SCORE_TYPE_BY_METHOD[method],
             f"score_type must be {SCORE_TYPE_BY_METHOD[method]!r} for method {method!r}")
    _require(manifest["score_direction"] == SCORE_DIRECTION,
             f"score_direction must be {SCORE_DIRECTION!r}")

    _validate_model_config(manifest["model_or_retriever_config"])

    for field in ("dataset_identifier", "git_commit", "command"):
        value = manifest[field]
        _require(isinstance(value, str) and value != "",
                 f"{field} must be a non-empty string")

    for field in ("dataset_fingerprint", "example_ids_fingerprint", "corpus_fingerprint"):
        value = manifest[field]
        _require(isinstance(value, str) and SHA256_FINGERPRINT_RE.match(value) is not None,
                 f"{field} must be 'sha256:' + 64 lowercase hex chars, got {value!r}")

    _require(isinstance(manifest["rankings_sha256"], str)
             and SHA256_HEX_RE.match(manifest["rankings_sha256"]) is not None,
             "rankings_sha256 must be 64 lowercase hex chars")

    dedup = manifest["deduplication_policy"]
    expected_dedup = DEDUPLICATION_POLICIES[(_method_class(method), setting)]
    _require(dedup == expected_dedup,
             f"deduplication_policy must be {expected_dedup!r} for method={method!r} "
             f"setting={setting!r}, got {dedup!r}")

    tie = manifest["tie_break_policy"]
    expected_tie = TIE_BREAK_POLICIES[_method_class(method)]
    _require(tie == expected_tie,
             f"tie_break_policy must be {expected_tie!r} for method={method!r}, got {tie!r}")

    if setting == "pooled":
        corpus_size = manifest["corpus_size"]
        _require(_is_int(corpus_size) and corpus_size >= 1,
                 "corpus_size must be an integer >= 1 for a pooled run")
    else:
        size_map = manifest["per_example_corpus_size"]
        _require(isinstance(size_map, dict) and len(size_map) == n_loaded,
                 "per_example_corpus_size must be a JSON object with exactly n_loaded keys")
        for example_id, size in size_map.items():
            _require(isinstance(example_id, str) and example_id != "",
                     "per_example_corpus_size keys must be non-empty strings")
            _require(_is_int(size) and size >= 1,
                     f"per_example_corpus_size[{example_id!r}] must be an integer >= 1")

    if method == "rerank":
        _require(isinstance(manifest["parent_retrieval_run_id"], str)
                 and manifest["parent_retrieval_run_id"] != "",
                 "parent_retrieval_run_id must be a non-empty string")
        _require(isinstance(manifest["parent_rankings_sha256"], str)
                 and SHA256_HEX_RE.match(manifest["parent_rankings_sha256"]) is not None,
                 "parent_rankings_sha256 must be 64 lowercase hex chars")
        depth = manifest["parent_candidate_depth"]
        _require(_is_int(depth) and depth >= 1,
                 "parent_candidate_depth must be an integer >= 1")
        _require(depth == retrieval_depth,
                 "a v1 rerank run requires parent_candidate_depth == retrieval_depth")


def validate_rankings_checksum(rankings_bytes: bytes, manifest: Mapping) -> None:
    """Verify ``manifest['rankings_sha256']`` matches the given rankings bytes."""
    actual = compute_sha256(rankings_bytes)
    expected = manifest.get("rankings_sha256")
    if actual != expected:
        raise RawSchemaError(
            f"rankings_sha256 mismatch: manifest {expected!r} != actual {actual!r}"
        )


def validate_raw_bundle(columns: Sequence[str], rows: Sequence[Mapping],
                        manifest: Mapping) -> None:
    """Run every raw-side structural check for a parsed bundle.

    Convenience entry point that composes column, manifest, row, and
    setting-specific depth/completeness validation. Checksum validation
    (:func:`validate_rankings_checksum`) needs the exact on-disk bytes and is
    kept separate.
    """
    validate_rankings_columns(columns)
    validate_manifest(manifest)
    validate_rankings_rows(rows, manifest)
    if manifest["setting"] == "pooled":
        validate_pooled_depth(rows, manifest)
    else:
        validate_per_question_completeness(rows, manifest)
    _require(manifest["n_loaded"] == len(saved_depth_by_example(rows)),
             "n_loaded must equal the distinct example_id count in rankings")
