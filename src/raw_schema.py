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
from datetime import datetime
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
# Frozen BM25 configuration shape (raw spec, model_or_retriever_config for
# method == "bm25"). The generic manifest validator deliberately stays
# method-agnostic (it only checks the closed outer object plus a recursive JSON
# grammar for `parameters`); this closed inner shape is enforced separately by
# `validate_bm25_config` and its method-specific provenance test, exactly as the
# raw spec assigns ("method-specific provenance tests validate the required
# parameter names").
# ---------------------------------------------------------------------------

BM25_IMPLEMENTATION = "rank_bm25"
BM25_IDENTIFIER = "BM25Okapi"
BM25_TOKENIZER = "python_str_split"
BM25_STOPWORD_POLICY = "none"
# Exact parameter key set; no extra key is allowed.
BM25_PARAMETER_KEYS = frozenset(
    {"b", "epsilon", "k1", "lowercase", "package_version", "stopword_policy", "tokenizer"}
)

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

# Whole-string exact-format grammars.
#
# Each pattern below describes CONTENT ONLY and is ALWAYS applied with
# ``re.fullmatch(...)``, which requires the pattern to consume the entire
# candidate string. The patterns deliberately carry no ``^``/``$`` anchors, so
# nothing can be mistaken for whole-string safety that is not. A trailing ``$``
# anchor combined with ``re.match(...)`` is NOT whole-string validation: in
# Python ``$`` also matches the position immediately before a single final
# newline, so ``pattern.match("<canonical value>\n")`` succeeds while leaving the
# ``\n`` unconsumed. That trailing line feed is an extra character that is not
# part of any frozen ID/checksum/fingerprint format (retrieval IDs are directory
# and join keys; checksums/fingerprints are exact provenance strings), so it must
# be rejected -- never repaired by ``strip()``/``rstrip()`` or any normalization.
# ``fullmatch`` has no before-final-newline escape hatch and rejects it.
#
# <method>_<setting>_n<N>_d<depth>_<YYYYMMDD>_r<NN>
# Every numeric field uses ASCII [0-9] rather than the regex shorthand \d, which
# in Python 3 also matches non-ASCII Unicode decimal digits (Arabic-Indic,
# fullwidth, etc.). Retrieval IDs are directory and join keys, so the frozen
# contract's base-10 ASCII serialization has exactly one canonical spelling; a
# visually confusable alternate numeric alphabet is not an accepted ID.
RETRIEVAL_RUN_ID_RE = re.compile(
    r"(?P<method>bm25|dense|rerank)"
    r"_(?P<setting>pooled|per_question)"
    r"_n(?P<n>[0-9]+)"
    r"_d(?P<depth>[0-9]+)"
    r"_(?P<date>[0-9]{8})"
    r"_r(?P<seq>[0-9]{2})"
)

# Bare rankings/parent checksum: exactly 64 lowercase hex chars, no prefix.
SHA256_HEX_RE = re.compile(r"[0-9a-f]{64}")
# Fingerprint fields: "sha256:" prefix followed by exactly 64 lowercase hex chars.
SHA256_FINGERPRINT_RE = re.compile(r"sha256:[0-9a-f]{64}")

# created_at is additionally range-checked by strptime below; this regex is the
# shape gate and, like the others, is applied with fullmatch() so a trailing LF
# cannot slip in ahead of the parse.
CREATED_AT_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


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


def validate_utc_timestamp(value, where: str) -> None:
    """Reject any ``created_at`` that is not a real UTC calendar timestamp.

    The frozen format is ``YYYY-MM-DDTHH:MM:SSZ`` with no fractional seconds.
    A shape-only regex would accept impossible values such as
    ``2026-99-99T99:99:99Z``; parsing with ``strptime`` rejects them because it
    range-checks month/day/hour/minute/second (and day-of-month per month).
    """
    _require(isinstance(value, str) and CREATED_AT_RE.fullmatch(value) is not None,
             f"{where} must be UTC 'YYYY-MM-DDTHH:MM:SSZ' with no fractional seconds, "
             f"got {value!r}")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        raise RawSchemaError(
            f"{where} {value!r} is not a real UTC calendar timestamp")


def validate_retrieval_run_id(run_id, expected_method=None, expected_setting=None,
                              expected_n=None, expected_depth=None,
                              where="retrieval_run_id"):
    """Fully validate a ``retrieval_run_id`` and return its regex match.

    This is the single canonical run-ID validator, reused for the primary raw
    manifest, the reranker parent, the eval source run, and the run embedded in
    an ``eval_id``. It enforces the full grammar semantics, not just the regex
    shape: a real UTC calendar date (``strptime``) and an ASCII rerun sequence in
    ``01``..``99`` (``r00`` and any non-ASCII digit spelling invalid). Optional
    ``expected_*`` bind the method, setting,
    ``n<N>`` (== ``n_loaded``), and ``d<depth>`` (== ``retrieval_depth``) segments
    when the caller has those values (a foreign ID whose manifest is not
    available simply omits ``expected_n`` / ``expected_depth``).
    """
    # fullmatch (not match) so a trailing LF after the r<NN> segment is rejected,
    # not silently ignored by a `$`-before-newline match.
    match = RETRIEVAL_RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
    _require(match is not None,
             f"{where} {run_id!r} must match the frozen grammar "
             f"<method>_<setting>_n<N>_d<depth>_<YYYYMMDD>_r<NN>")
    try:
        datetime.strptime(match.group("date"), "%Y%m%d")
    except ValueError:
        raise RawSchemaError(
            f"{where} date segment {match.group('date')!r} is not a real calendar date")
    # The sequence is now two ASCII digits (regex-guaranteed). Interpret it
    # numerically and require 1 <= seq <= 99 rather than only string-comparing to
    # ASCII "00": that string compare let a Unicode-zero pair (numerically 0) slip
    # past the r01 lower bound. The ASCII-only regex already rejects non-ASCII
    # digits, and int() on two ASCII digits is always in 0..99.
    seq = int(match.group("seq"))
    _require(1 <= seq <= 99,
             f"{where} sequence starts at r01; r{match.group('seq')} is invalid "
             f"(ASCII 01-99 only)")
    # Positivity is UNCONDITIONAL (Finding E): the raw spec fixes n<N> == n_loaded
    # (>= 1) and d<depth> == retrieval_depth (>= 1), so a zero-question or
    # zero-depth ID can never name a conforming raw bundle -- not even as a
    # reranker parent or eval source whose own manifest is unavailable here. This
    # is a range check on the ID itself; it needs no manifest and no expected_*
    # value, stays method-agnostic, and computes no metric.
    _require(int(match.group("n")) >= 1,
             f"{where} n segment {match.group('n')} must be >= 1 (n_loaded >= 1)")
    _require(int(match.group("depth")) >= 1,
             f"{where} d segment {match.group('depth')} must be >= 1 "
             f"(retrieval_depth >= 1)")
    if expected_method is not None:
        _require(match.group("method") == expected_method,
                 f"{where} method segment {match.group('method')!r} must be "
                 f"{expected_method!r}")
    if expected_setting is not None:
        _require(match.group("setting") == expected_setting,
                 f"{where} setting segment {match.group('setting')!r} must be "
                 f"{expected_setting!r}")
    if expected_n is not None:
        _require(int(match.group("n")) == expected_n,
                 f"{where} n segment {match.group('n')} must equal n_loaded {expected_n}")
    if expected_depth is not None:
        _require(int(match.group("depth")) == expected_depth,
                 f"{where} d segment {match.group('depth')} must equal retrieval_depth "
                 f"{expected_depth}")
    return match


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
    manifest, finite numeric scores, and the frozen PHYSICAL row order: rows are
    ordered by ascending ``example_id`` (Unicode code point) then ascending
    integer ``rank``, and within each example ``rank`` appears physically as
    ``1, 2, ..., n`` with no gaps or duplicates. The order is verified from the
    row sequence itself (not a sorted copy), because the frozen serialization
    order is what the ``rankings_sha256`` checksum is computed over. It never
    inspects gold or recomputes a metric.
    """
    run_id = manifest.get("retrieval_run_id")
    method = manifest.get("method")
    setting = manifest.get("setting")

    prev_key = None
    next_rank_by_example: Dict[str, int] = {}

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

        # Physical global order: strictly ascending (example_id, rank). This also
        # rejects duplicate (example_id, rank) rows and out-of-order example
        # blocks (e.g. a q2 block placed before q1).
        key = (example_id, rank)
        if prev_key is not None:
            _require(prev_key < key,
                     f"{where}: rows must be physically ordered by ascending "
                     f"example_id then rank; {key!r} does not come after {prev_key!r}")
        prev_key = key

        # Physical per-example contiguity: ranks appear as 1, 2, ..., n in order.
        expected_rank = next_rank_by_example.get(example_id, 1)
        _require(rank == expected_rank,
                 f"{where}: example {example_id!r} rank must appear physically as "
                 f"1..n; expected {expected_rank}, got {rank}")
        next_rank_by_example[example_id] = rank + 1


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

    validate_utc_timestamp(manifest["created_at"], "created_at")

    _require(isinstance(manifest["split"], str) and manifest["split"] != "",
             "split must be a non-empty string")

    n_requested = manifest["n_requested"]
    n_loaded = manifest["n_loaded"]
    _require(_is_int(n_requested) and n_requested >= 1, "n_requested must be an integer >= 1")
    _require(_is_int(n_loaded) and n_loaded >= 1, "n_loaded must be an integer >= 1")

    retrieval_depth = manifest["retrieval_depth"]
    _require(_is_int(retrieval_depth) and retrieval_depth >= 1,
             "retrieval_depth must be an integer >= 1")

    # Full run-ID validation (grammar + real date + r>=01) with the n<N>/d<depth>
    # and method/setting segments bound to the manifest values.
    validate_retrieval_run_id(manifest["retrieval_run_id"], expected_method=method,
                              expected_setting=setting, expected_n=n_loaded,
                              expected_depth=retrieval_depth, where="retrieval_run_id")

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
        _require(isinstance(value, str) and SHA256_FINGERPRINT_RE.fullmatch(value) is not None,
                 f"{field} must be 'sha256:' + 64 lowercase hex chars, got {value!r}")

    _require(isinstance(manifest["rankings_sha256"], str)
             and SHA256_HEX_RE.fullmatch(manifest["rankings_sha256"]) is not None,
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
        # A v1 rerank run requires a Dense pooled parent. The parent's own
        # manifest is not available here, so n/depth are not bound, but the ID
        # must still be fully valid (grammar + real date + r>=01), not just
        # regex-shaped.
        validate_retrieval_run_id(manifest["parent_retrieval_run_id"],
                                  expected_method="dense", expected_setting="pooled",
                                  where="parent_retrieval_run_id")
        _require(isinstance(manifest["parent_rankings_sha256"], str)
                 and SHA256_HEX_RE.fullmatch(manifest["parent_rankings_sha256"]) is not None,
                 "parent_rankings_sha256 must be 64 lowercase hex chars")
        depth = manifest["parent_candidate_depth"]
        _require(_is_int(depth) and depth >= 1,
                 "parent_candidate_depth must be an integer >= 1")
        _require(depth == retrieval_depth,
                 "a v1 rerank run requires parent_candidate_depth == retrieval_depth")


def validate_bm25_config(config: Mapping) -> None:
    """Method-specific provenance validator for a BM25 ``model_or_retriever_config``.

    The frozen raw spec deliberately keeps the generic manifest validator
    method-agnostic (closed outer shape + recursive JSON grammar) and assigns the
    BM25 inner-key contract to a method-specific provenance check. This function
    is that check; it is NOT called by :func:`validate_manifest`. It enforces the
    exact implementation/identifier, the exact seven parameter keys, and their
    types and frozen string values. It defines no metric.
    """
    _validate_model_config(config)  # closed outer shape + recursive JSON values
    _require(config["implementation"] == BM25_IMPLEMENTATION,
             f"BM25 implementation must be {BM25_IMPLEMENTATION!r}, got "
             f"{config['implementation']!r}")
    _require(config["identifier"] == BM25_IDENTIFIER,
             f"BM25 identifier must be {BM25_IDENTIFIER!r}, got {config['identifier']!r}")

    params = config["parameters"]
    _require(set(params.keys()) == set(BM25_PARAMETER_KEYS),
             f"BM25 parameters must have exactly keys {sorted(BM25_PARAMETER_KEYS)}; "
             f"missing={sorted(set(BM25_PARAMETER_KEYS) - set(params))}, "
             f"unexpected={sorted(set(params) - set(BM25_PARAMETER_KEYS))}")

    for numeric_key in ("b", "epsilon", "k1"):
        _require(_is_finite_number(params[numeric_key]),
                 f"BM25 parameter {numeric_key!r} must be a finite number, got "
                 f"{params[numeric_key]!r}")
    _require(isinstance(params["lowercase"], bool),
             "BM25 parameter 'lowercase' must be a boolean")
    _require(isinstance(params["package_version"], str) and params["package_version"] != "",
             "BM25 parameter 'package_version' must be a non-empty string")
    _require(params["tokenizer"] == BM25_TOKENIZER,
             f"BM25 parameter 'tokenizer' must be {BM25_TOKENIZER!r}, got "
             f"{params['tokenizer']!r}")
    _require(params["stopword_policy"] == BM25_STOPWORD_POLICY,
             f"BM25 parameter 'stopword_policy' must be {BM25_STOPWORD_POLICY!r}, got "
             f"{params['stopword_policy']!r}")


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
