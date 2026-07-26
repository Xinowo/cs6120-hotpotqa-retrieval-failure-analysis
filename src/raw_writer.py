"""
raw_writer.py

Stage 3 (writer core) for the metrics/schema v2 refactor: the method-agnostic
producer side of the RAW retrieval layer. It turns already-produced
``(Paragraph, score)`` retrieval batches into a complete
``retrieval_raw_schema_v1`` run bundle on disk (``manifest.json`` +
``rankings.csv``) whose exact serialized bytes satisfy the frozen contract and
the contract-only validators in :mod:`src.raw_schema`.

Authoritative frozen contract:
``docs/specs/2026-07-20-raw-retrieval-rankings-schema.md``. This module encodes
only the *serialization* half of that contract (the byte-exact ``rankings.csv``
and ``manifest.json`` forms, the canonical-JSON fingerprint inputs, the run-ID
spelling, atomic write, and refuse-overwrite collision policy); the *validation*
half already lives in :mod:`src.raw_schema` and is reused verbatim here. The two
sides deliberately share one set of column/version/policy constants so the writer
can never drift from what the validator accepts.

Design boundaries (kept identical to the raw schema module):

- It stores no gold, computes no metric, and defines no metric. ``score`` is the
  retriever's own native number, passed straight through from the retrieval call
  that produced the ranking; it is never fabricated or back-derived from rank.
- It never triggers a second retrieval: :func:`build_ranking_rows_from_batches`
  consumes the batches the caller already retrieved (the same generalization
  that :mod:`src.top50_export` applied to the pooled dense export, now widened to
  the full raw column set and reused by every method/setting).
- It never reuses the mixed-purpose ``RESULT_COLUMNS`` contract.

AI-usage boundary: pure file-I/O / serialization / plumbing, agent-allowed. No
metric definition, formula, or core evaluator computation lives here.
"""

import csv
import io
import json
import numbers
import os
import shutil
import tempfile
from collections.abc import Mapping, Set

from src.raw_schema import (
    DEDUPLICATION_POLICIES,
    RANKING_COLUMNS,
    RAW_METHODS,
    RAW_SETTINGS,
    RETRIEVAL_RAW_SCHEMA_V1,
    RawSchemaError,
    SCORE_DIRECTION,
    SCORE_TYPE_BY_METHOD,
    TIE_BREAK_POLICIES,
    compute_sha256,
    validate_bm25_config,
    validate_rankings_checksum,
    validate_raw_bundle,
    validate_retrieval_run_id,
)

# The two on-disk file names in a v1 run bundle (directory layout is fixed by
# the raw spec: a bundle is exactly these two files, nothing else).
MANIFEST_FILENAME = "manifest.json"
RANKINGS_FILENAME = "rankings.csv"


def _require(condition, message):
    if not condition:
        raise RawSchemaError(message)


def _method_class(method):
    # Mirror of src.raw_schema._method_class: the two lexical/dense retrievers
    # share one policy class; the reranker is its own class. Kept as a tiny local
    # copy so the writer never imports a private name, but the policy *values* are
    # looked up from the shared raw_schema tables (single source of truth).
    return "rerank" if method == "rerank" else "dense_bm25"


# ---------------------------------------------------------------------------
# U1 -- byte-exact serialization of rankings.csv / manifest.json + fingerprints
# ---------------------------------------------------------------------------
#
# Every rule below is quoted from the raw spec's "Serialization and checksum
# rules". The bytes these functions produce are exactly what ``rankings_sha256``
# is computed over, so they must be reproduced precisely -- pandas.to_csv cannot
# (it controls neither float formatting nor the record terminator), which is why
# this uses the csv module with each numeric cell pre-formatted to its frozen
# text form.


def _int_text(value):
    """Frozen integer text: base-10 ASCII, no leading '+' and no leading zero
    except the value 0. ``str`` of a Python int is exactly that. Rejects bool
    (an int subclass that is never a valid schema integer)."""
    _require(isinstance(value, int) and not isinstance(value, bool),
             f"integer cell must be a non-bool int, got {value!r}")
    return str(value)


def _float_text(value):
    """Frozen float text: ``format(value, '.17g')`` (lowercase exponent), with
    negative zero normalized to ``0``. ``.17g`` round-trips every finite IEEE-754
    double exactly. Non-finite scores are refused rather than serialized -- the
    raw layer never stores a fabricated or infinite score."""
    _require(isinstance(value, (int, float)) and not isinstance(value, bool),
             f"score cell must be a non-bool number, got {value!r}")
    _require(value == value and value not in (float("inf"), float("-inf")),
             f"score cell must be finite, got {value!r}")
    # ``value == 0`` is True for both 0.0 and -0.0, so this is the negative-zero
    # normalization; ``format(-0.0, '.17g')`` would otherwise emit '-0'.
    if value == 0:
        return "0"
    return format(value, ".17g")


def rankings_csv_bytes(rows):
    """Serialize ranking rows to the exact frozen ``rankings.csv`` bytes.

    Output is UTF-8 without BOM, comma-delimited, header required, LF record
    terminator, ``QUOTE_MINIMAL`` with ``"`` quotechar and doubled embedded
    quotes (no escapechar). Rows are emitted in the frozen physical order --
    ascending ``example_id`` by Unicode code point, then ascending integer
    ``rank`` -- which is authoritative here (the on-disk order is what the
    checksum covers), so a caller may pass rows in any order.
    """
    ordered = sorted(rows, key=lambda r: (r["example_id"], r["rank"]))
    buffer = io.StringIO(newline="")
    writer = csv.writer(
        buffer,
        delimiter=",",
        quotechar='"',
        doublequote=True,
        escapechar=None,
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    writer.writerow(RANKING_COLUMNS)
    for row in ordered:
        for column in ("retrieval_run_id", "method", "setting", "example_id", "title"):
            _require(isinstance(row.get(column), str),
                     f"rankings cell {column!r} must be a string, got {row.get(column)!r}")
        writer.writerow([
            row["retrieval_run_id"],
            row["method"],
            row["setting"],
            row["example_id"],
            _int_text(row["rank"]),
            row["title"],
            _float_text(row["score"]),
        ])
    return buffer.getvalue().encode("utf-8")


def read_rankings_bytes(data):
    """Parse ``rankings.csv`` bytes back into ``(columns, rows)``.

    The inverse of :func:`rankings_csv_bytes`, used both to re-validate a bundle
    from its own on-disk bytes after writing and by offline round-trip tests.
    ``rank`` is parsed to ``int`` and ``score`` to ``float`` so the returned rows
    feed the raw_schema row validators directly; all other cells stay strings.
    """
    text = data.decode("utf-8")
    reader = csv.reader(
        io.StringIO(text, newline=""),
        delimiter=",",
        quotechar='"',
        doublequote=True,
        escapechar=None,
    )
    records = list(reader)
    if not records:
        return [], []
    header = records[0]
    rows = []
    for i, raw in enumerate(records[1:]):
        # A malformed physical row (wrong cell count, or a rank/score cell that is
        # not the frozen integer/float text) is a schema violation, not an
        # interpreter error: raise RawSchemaError so the writer's acceptance gate
        # reports it uniformly instead of leaking a bare ValueError from int/float.
        _require(len(raw) == len(header),
                 f"rankings row {i}: expected {len(header)} cells to match the header, "
                 f"got {len(raw)}")
        record = dict(zip(header, raw))
        try:
            record["rank"] = int(record["rank"])
        except (KeyError, ValueError):
            raise RawSchemaError(
                f"rankings row {i}: rank must be integer text, got {record.get('rank')!r}")
        try:
            record["score"] = float(record["score"])
        except (KeyError, ValueError):
            raise RawSchemaError(
                f"rankings row {i}: score must be float text, got {record.get('score')!r}")
        rows.append(record)
    return header, rows


def manifest_json_bytes(manifest):
    """Serialize a manifest object to the exact frozen ``manifest.json`` bytes:
    ``json.dumps(..., ensure_ascii=False, allow_nan=False, sort_keys=True,
    separators=(',', ':'))`` encoded as UTF-8 without BOM, followed by one LF."""
    text = json.dumps(
        manifest,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (text + "\n").encode("utf-8")


def canonical_json_bytes(value):
    """Canonical JSON fingerprint input: same dump parameters as the manifest but
    with NO trailing newline (the spec hashes canonical JSON bytes directly)."""
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def fingerprint(value):
    """Return ``sha256:`` + the lowercase hex SHA-256 of ``value``'s canonical
    JSON bytes, the frozen form for every ``*_fingerprint`` manifest field."""
    return "sha256:" + compute_sha256(canonical_json_bytes(value))


# ---------------------------------------------------------------------------
# U2 -- fingerprint builders + canonical run-ID + manifest assembly
# ---------------------------------------------------------------------------
#
# The fingerprint builders below shape their argument into the exact JSON value
# the raw spec hashes, then defer to :func:`fingerprint`. They take duck-typed
# objects (``.title`` / ``.text`` on paragraphs, ``.example_id`` / ``.paragraphs``
# on examples) so offline tests can drive them with plain fakes.


def _require_fingerprint_string(value, where, *, allow_empty=True):
    """Fail closed on a non-string fingerprint preimage field BEFORE hashing.

    The frozen fingerprint preimages are JSON shapes with string fields
    (``example_id``, paragraph ``title`` / ``text``). Canonical JSON would happily
    serialize a non-string such as an integer ID or title into a syntactically
    valid ``sha256:`` value that no downstream validator can reverse, so wrong
    dataset/corpus identity would become indistinguishable from valid provenance.
    We therefore reject the wrong scalar type here rather than coercing it to a
    string. ``example_id`` is a join key and must be non-empty; paragraph
    ``title``/``text`` follow the rankings contract, which permits an empty string.
    """
    _require(isinstance(value, str) and (allow_empty or value != ""),
             f"{where} must be a {'' if allow_empty else 'non-empty '}string, "
             f"got {value!r}")


def _validate_fingerprint_json(value, where):
    """Recursively require a JSON-compatible fingerprint preimage: only JSON value
    types, string object keys, and finite numbers.

    Mirrors the raw_schema JSON grammar; kept as a tiny local copy so the writer
    never imports a private name (the same convention as :func:`_method_class`).
    This fails closed on shapes canonical JSON would otherwise coerce silently
    (for example a non-string dict key) or that are not valid JSON at all.
    """
    if value is None or isinstance(value, str) or isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        _require(value == value and value not in (float("inf"), float("-inf")),
                 f"{where}: numbers must be finite")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _validate_fingerprint_json(item, f"{where}[{i}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _require(isinstance(key, str), f"{where}: object keys must be strings")
            _validate_fingerprint_json(item, f"{where}.{key}")
        return
    raise RawSchemaError(f"{where}: unsupported JSON value type {type(value).__name__}")


def _materialize_formal_collection(value, where):
    """Materialize a fingerprint preimage collection, failing closed on the
    container-shape traps BEFORE hashing.

    A fingerprint preimage is an ORDERED collection: the raw spec's JSON arrays of
    dataset records, ``example_id`` strings, or corpus objects, whose order is
    authoritative (selected dataset order, corpus input order, per-question source
    context order). A bare string, bytes, or mapping passed where such a collection
    is expected is a different shape that Python would still iterate -- a string
    into its characters, a mapping into its keys -- silently producing a
    valid-looking but wrong digest (for example ``example_ids_fingerprint("q1")``
    would hash ``["q", "1"]`` rather than ``["q1"]``). An UNORDERED collection --
    ``set``, ``frozenset``, or a mapping key view (every ``collections.abc.Set``) --
    is just as wrong: it iterates in a process-randomized order, so equal logical
    inputs would receive different fingerprints across runs, defeating the
    deterministic cross-method/migration provenance the digest exists to carry. All
    of these traps are rejected rather than materialized, and a non-iterable scalar
    is rejected too. A formal run has ``n_loaded >= 1`` and a positive
    setting-specific corpus, so an empty formal collection is rejected after
    materialization. Legitimate ordered iterables (``list``/``tuple``/``deque``/
    generators) are preserved (a generator is consumed exactly once, here). The
    caller's input is never stringified, split, reordered, or otherwise repaired.
    """
    _require(not isinstance(value, (str, bytes, bytearray)),
             f"{where} must be an ordered collection, not a bare "
             f"{type(value).__name__} (which would be hashed as its individual "
             f"characters/bytes)")
    _require(not isinstance(value, Mapping),
             f"{where} must be an ordered collection of items, not a single mapping "
             f"(which would be hashed as its keys)")
    _require(not isinstance(value, Set),
             f"{where} must be an ordered collection, not an unordered "
             f"{type(value).__name__} (a set/frozenset/mapping key view iterates in "
             f"a process-randomized order, so it cannot carry the required selected/"
             f"source order and would hash nondeterministically)")
    try:
        items = list(value)
    except TypeError:
        raise RawSchemaError(
            f"{where} must be an ordered iterable collection, got a non-iterable "
            f"{type(value).__name__}")
    _require(len(items) >= 1,
             f"{where} must be a non-empty formal collection (a formal run has "
             f"n_loaded >= 1 and a positive corpus)")
    return items


def dataset_fingerprint(raw_records):
    """Hash the JSON array of the complete loaded raw dataset records, in
    selected dataset order (before conversion to ``HotpotExample``)."""
    records = _materialize_formal_collection(raw_records, "dataset_fingerprint records")
    for i, record in enumerate(records):
        _require(isinstance(record, dict),
                 f"dataset_fingerprint records[{i}] must be a raw-record JSON object, "
                 f"got {type(record).__name__}")
    _validate_fingerprint_json(records, "dataset_fingerprint records")
    return fingerprint(records)


def example_ids_fingerprint(example_ids):
    """Hash the JSON array of ``example_id`` strings in selected dataset order."""
    ids = _materialize_formal_collection(example_ids, "example_ids_fingerprint")
    for i, example_id in enumerate(ids):
        _require_fingerprint_string(example_id, f"example_ids_fingerprint[{i}]",
                                    allow_empty=False)
    return fingerprint(ids)


def pooled_corpus_fingerprint(paragraphs):
    """Hash the post-deduplication JSON array of ``{"title", "text"}`` objects in
    corpus input order (the pooled shared corpus)."""
    items = _materialize_formal_collection(paragraphs, "pooled_corpus_fingerprint")
    entries = []
    for i, paragraph in enumerate(items):
        _require_fingerprint_string(paragraph.title,
                                    f"pooled_corpus_fingerprint[{i}].title")
        _require_fingerprint_string(paragraph.text,
                                    f"pooled_corpus_fingerprint[{i}].text")
        entries.append({"title": paragraph.title, "text": paragraph.text})
    return fingerprint(entries)


def per_question_corpus_fingerprint(examples):
    """Hash the selected-order JSON array of
    ``{"example_id", "paragraphs": [{"title", "text"}, ...]}`` objects, each
    paragraph array in source context order (the per-question corpora)."""
    items = _materialize_formal_collection(examples, "per_question_corpus_fingerprint")
    entries = []
    for i, example in enumerate(items):
        _require_fingerprint_string(example.example_id,
                                    f"per_question_corpus_fingerprint[{i}].example_id",
                                    allow_empty=False)
        # The nested per-question mini-corpus is itself an ORDERED, non-empty
        # collection (spec: paragraphs in source context order; every formal
        # per-example corpus size is positive). Route it through the same guard so
        # a nested set/frozenset/key-view, a string/bytes/mapping, a non-iterable,
        # or an empty mini-corpus fails closed here instead of hashing a
        # process-randomized or empty paragraph array.
        para_items = _materialize_formal_collection(
            example.paragraphs, f"per_question_corpus_fingerprint[{i}].paragraphs")
        paragraphs = []
        for j, paragraph in enumerate(para_items):
            base = f"per_question_corpus_fingerprint[{i}].paragraphs[{j}]"
            _require_fingerprint_string(paragraph.title, f"{base}.title")
            _require_fingerprint_string(paragraph.text, f"{base}.text")
            paragraphs.append({"title": paragraph.title, "text": paragraph.text})
        entries.append({"example_id": example.example_id, "paragraphs": paragraphs})
    return fingerprint(entries)


def per_example_corpus_size_map(examples, batches):
    """Return ``{example_id: per_example_corpus_size}`` from the INDEPENDENT source
    mini-corpora, not from the saved batches.

    ``per_example_corpus_size`` is the size of each example's complete source
    mini-corpus (for the current types, ``len(example.paragraphs)``). That is the
    corpus truth the raw contract compares the saved batch depth against. Deriving
    it from ``len(batch)`` instead would make the validator's
    ``saved_depth == per_example_corpus_size`` check tautological -- the same
    truncated output would supply both sides, so a per-question ranking capped
    below its full mini-corpus could certify itself as corpus-exhausted and be
    published. The size therefore comes from the source collection, and bundle
    validation (:func:`src.raw_schema.validate_per_question_completeness`)
    independently compares the saved batch depth against it. ``batches`` is
    accepted only to preserve the positional examples/batches alignment guard; it
    never contributes to the recorded size. This is a structural count, not a
    metric.
    """
    _require(len(examples) == len(batches),
             f"examples and batches must be the same length, got "
             f"{len(examples)} and {len(batches)}")
    size_map = {}
    for example in examples:
        example_id = example.example_id
        _require(isinstance(example_id, str) and example_id != "",
                 f"example_id must be a non-empty string, got {example_id!r}")
        size = len(example.paragraphs)
        _require(size >= 1,
                 f"per-question source mini-corpus for {example_id!r} must contain "
                 f"at least one paragraph, got {size}")
        size_map[example_id] = size
    return size_map


def build_retrieval_run_id(method, setting, n_loaded, retrieval_depth, date, seq):
    """Assemble the canonical ``<method>_<setting>_n<N>_d<depth>_<YYYYMMDD>_r<NN>``
    run ID. Emits the canonical base-10 spelling (no leading zeros on ``n``/``d``)
    and refuses out-of-range parts so the writer can never mint a malformed ID."""
    _require(method in RAW_METHODS, f"method must be one of {RAW_METHODS}, got {method!r}")
    _require(setting in RAW_SETTINGS, f"setting must be one of {RAW_SETTINGS}, got {setting!r}")
    _require(isinstance(n_loaded, int) and not isinstance(n_loaded, bool) and n_loaded >= 1,
             f"n_loaded must be an integer >= 1, got {n_loaded!r}")
    _require(isinstance(retrieval_depth, int) and not isinstance(retrieval_depth, bool)
             and retrieval_depth >= 1,
             f"retrieval_depth must be an integer >= 1, got {retrieval_depth!r}")
    _require(isinstance(date, str) and len(date) == 8 and date.isascii() and date.isdigit(),
             f"date must be 8 ASCII digits YYYYMMDD, got {date!r}")
    _require(isinstance(seq, int) and not isinstance(seq, bool) and 1 <= seq <= 99,
             f"seq must be an integer in 1..99, got {seq!r}")
    run_id = f"{method}_{setting}_n{n_loaded}_d{retrieval_depth}_{date}_r{seq:02d}"
    # The eight-digit/ASCII date shape above still admits an impossible calendar
    # date such as 20260230. Reuse the single canonical run-ID validator (real
    # `strptime` calendar check + r01..r99 + n/depth/method/setting binding) on
    # the constructed ID so the builder can never mint an ID the validator would
    # reject; this adds no second divergent parser and does not touch the
    # unresolved n02/d03 leading-zero policy (the builder still emits canonical
    # no-leading-zero n/d spellings).
    validate_retrieval_run_id(run_id, expected_method=method, expected_setting=setting,
                              expected_n=n_loaded, expected_depth=retrieval_depth)
    return run_id


def build_raw_manifest(*, method, setting, split, n_requested, n_loaded, retrieval_depth,
                       date, seq, created_at, model_or_retriever_config, dataset_identifier,
                       dataset_fingerprint, example_ids_fingerprint, corpus_fingerprint,
                       git_commit, command, rankings_sha256, corpus_size=None,
                       per_example_corpus_size=None, parent_retrieval_run_id=None,
                       parent_rankings_sha256=None, parent_candidate_depth=None):
    """Assemble a complete ``retrieval_raw_schema_v1`` manifest object.

    Pure construction: it fills the method/setting-conditional field set, derives
    the run ID, and looks up ``score_type`` / ``score_direction`` /
    ``deduplication_policy`` / ``tie_break_policy`` from the shared raw_schema
    tables so they can never disagree with the validator. It does NOT validate
    (callers run :func:`src.raw_schema.validate_manifest`, and
    :func:`write_raw_bundle` runs the full bundle validation after writing). The
    caller supplies already-computed fingerprints and ``rankings_sha256``.
    """
    method_class = _method_class(method)
    dedup_key = (method_class, setting)
    _require(dedup_key in DEDUPLICATION_POLICIES,
             f"no deduplication policy for method={method!r} setting={setting!r} "
             f"(a rerank run requires setting='pooled')")

    run_id = build_retrieval_run_id(method, setting, n_loaded, retrieval_depth, date, seq)

    manifest = {
        "raw_schema_version": RETRIEVAL_RAW_SCHEMA_V1,
        "retrieval_run_id": run_id,
        "created_at": created_at,
        "method": method,
        "setting": setting,
        "split": split,
        "n_requested": n_requested,
        "n_loaded": n_loaded,
        "retrieval_depth": retrieval_depth,
        "score_type": SCORE_TYPE_BY_METHOD[method],
        "score_direction": SCORE_DIRECTION,
        "model_or_retriever_config": model_or_retriever_config,
        "dataset_identifier": dataset_identifier,
        "dataset_fingerprint": dataset_fingerprint,
        "example_ids_fingerprint": example_ids_fingerprint,
        "corpus_fingerprint": corpus_fingerprint,
        "deduplication_policy": DEDUPLICATION_POLICIES[dedup_key],
        "tie_break_policy": TIE_BREAK_POLICIES[method_class],
        "git_commit": git_commit,
        "command": command,
        "rankings_sha256": rankings_sha256,
    }

    if setting == "pooled":
        manifest["corpus_size"] = corpus_size
    else:  # per_question
        manifest["per_example_corpus_size"] = per_example_corpus_size

    if method == "rerank":
        manifest["parent_retrieval_run_id"] = parent_retrieval_run_id
        manifest["parent_rankings_sha256"] = parent_rankings_sha256
        manifest["parent_candidate_depth"] = parent_candidate_depth

    return manifest


# ---------------------------------------------------------------------------
# U4 -- ranking rows from already-retrieved batches (never re-retrieves)
# ---------------------------------------------------------------------------


def _native_score_to_float(value):
    """Return the serialized Python float for a genuine native retriever score.

    The raw contract requires ``score`` to be a finite native number produced by
    the same retrieval call and never fabricated or type-repaired. The supported
    paths emit real numeric scalars: Dense returns a Python ``float`` and BM25
    returns a NumPy floating scalar (``numpy.float64``). We therefore accept only
    real numbers (:class:`numbers.Real`, which covers Python ``int``/``float`` and
    the NumPy real scalar types) and explicitly reject ``bool`` (an ``int``
    subclass that is never a score) and strings BEFORE any conversion. Without
    this gate an unconditional ``float(value)`` silently turns an invalid upstream
    value such as ``True`` into ``1.0`` or ``"0.5"`` into ``0.5``, destroying the
    evidence that the retriever did not supply the contracted numeric type. Only
    after the type gate is an allowed non-Python scalar narrowed to a Python float,
    and a non-finite result is refused without repair.
    """
    _require(isinstance(value, numbers.Real) and not isinstance(value, bool),
             f"score must be a finite native real number from the retrieval call "
             f"(not a bool, string, or other type), got {value!r}")
    result = float(value)
    _require(result == result and result not in (float("inf"), float("-inf")),
             f"score must be finite, got {value!r}")
    return result


def build_ranking_rows_from_batches(examples, batches, *, retrieval_run_id, method, setting):
    """Shape full ``RANKING_COLUMNS`` rows from already-retrieved scored batches.

    ``batches[i]`` is example ``i``'s ranked list of ``(Paragraph, score)`` tuples
    (exactly what ``DenseRetriever.retrieve_many`` / ``BM25Retriever.retrieve``
    return), aligned positionally with ``examples``. This is the method-agnostic
    generalization of :func:`src.top50_export.build_top50_rows_from_batches`, now
    emitting every raw column. ``rank`` is 1-based within each example.

    ``examples`` and ``batches`` must be the same length: they are aligned
    positionally, so a mismatch means batch ``i`` does not belong to example
    ``i``. We raise instead of relying on ``zip``, which would silently truncate
    to the shorter sequence and drop or misalign questions without any error.
    """
    _require(len(examples) == len(batches),
             f"examples and batches must be the same length, got {len(examples)} "
             f"examples and {len(batches)} batches; they are aligned positionally so "
             "a mismatch would drop or misalign rows.")
    rows = []
    for example, ranked in zip(examples, batches):
        for rank, (paragraph, score) in enumerate(ranked, start=1):
            rows.append({
                "retrieval_run_id": retrieval_run_id,
                "method": method,
                "setting": setting,
                "example_id": example.example_id,
                "rank": rank,
                "title": paragraph.title,
                "score": _native_score_to_float(score),
            })
    return rows


# ---------------------------------------------------------------------------
# U3 -- atomic bundle writer (refuse-overwrite + post-write validation)
# ---------------------------------------------------------------------------


def _validate_bundle_bytes(rankings_bytes, manifest):
    """Run the complete raw acceptance gate over the EXACT on-disk bundle bytes.

    This is the single mandatory gate every published bundle must pass; there is
    no bypass. It enforces, on the bytes actually written to disk:

    - **Canonical byte parity (U1/U3):** ``rankings.csv`` must be the byte-exact
      frozen serialization of its own parsed rows. Because
      :func:`rankings_csv_bytes` re-emits LF, ``.17g`` float text, plain integer
      text, ``QUOTE_MINIMAL`` quoting, and the canonical ``(example_id, rank)``
      order, this rejects foreign CRLF, noncanonical numeric text, altered
      quoting, extra cells, or a physical reordering even when the recorded
      checksum matches those noncanonical bytes.
    - **Generic bundle validation:** columns, manifest, row order/continuity,
      depth/completeness, and the ``n_loaded`` cardinality
      (:func:`src.raw_schema.validate_raw_bundle`).
    - **Method-specific BM25 provenance:** the frozen closed BM25 config whenever
      ``method == 'bm25'`` (the generic manifest validator is deliberately
      method-agnostic, so the writer composes this gate itself).
    - **Checksum:** ``rankings_sha256`` over the exact bytes.
    """
    columns, rows = read_rankings_bytes(rankings_bytes)
    validate_raw_bundle(columns, rows, manifest)
    _require(rankings_bytes == rankings_csv_bytes(rows),
             "rankings.csv bytes are not the canonical serialization of their parsed "
             "rows (noncanonical line ending, integer/float text, quoting, extra "
             "cells, or physical order); the raw contract fixes the exact bytes that "
             "the checksum is computed over")
    if manifest.get("method") == "bm25":
        validate_bm25_config(manifest["model_or_retriever_config"])
    validate_rankings_checksum(rankings_bytes, manifest)


def write_raw_bundle(run_root, manifest, rankings_bytes):
    """Write a complete run bundle to ``<run_root>/<retrieval_run_id>/`` atomically.

    Collision policy (raw spec): if the target bundle directory already exists the
    writer refuses and errors -- raw run IDs are write-once, never overwritten.

    Atomicity and acceptance: both files are written into a hidden temp directory
    inside ``run_root``; the writer then rereads the two files it just wrote and
    runs the full raw acceptance gate (:func:`_validate_bundle_bytes`) over those
    exact on-disk bytes -- canonical byte parity, schema/row/depth/completeness,
    the method-specific BM25 config when applicable, and ``rankings_sha256``. Only
    on success is the temp directory renamed onto the final bundle path in a
    single filesystem operation. An interrupted or invalid write therefore leaves
    only the temp directory (cleaned up on any exception) and can never look like a
    formal, complete bundle. There is deliberately no unvalidated completion path:
    every accepted bundle has passed the gate on its own disk bytes.

    Returns the final bundle directory path.
    """
    run_id = manifest["retrieval_run_id"]
    bundle_dir = os.path.join(run_root, run_id)
    _require(not os.path.exists(bundle_dir),
             f"refusing to overwrite existing run bundle {bundle_dir!r}; raw run IDs "
             "are write-once (collision policy)")

    manifest_bytes = manifest_json_bytes(manifest)

    os.makedirs(run_root, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="." + run_id + ".", dir=run_root)
    try:
        rankings_path = os.path.join(tmp_dir, RANKINGS_FILENAME)
        manifest_path = os.path.join(tmp_dir, MANIFEST_FILENAME)
        with open(rankings_path, "wb") as handle:
            handle.write(rankings_bytes)
        with open(manifest_path, "wb") as handle:
            handle.write(manifest_bytes)
        # Reread exactly what landed on disk and validate THOSE bytes (never the
        # in-memory copies), so the accepted bundle is proven byte-for-byte before
        # the rename makes the formal path appear.
        with open(rankings_path, "rb") as handle:
            disk_rankings = handle.read()
        with open(manifest_path, "rb") as handle:
            disk_manifest = json.loads(handle.read().decode("utf-8"))
        _validate_bundle_bytes(disk_rankings, disk_manifest)
        # Rename the whole temp directory onto the final path. os.rename does not
        # overwrite an existing directory, and we already refused above, so the
        # formal path appears only as a complete, validated bundle.
        os.rename(tmp_dir, bundle_dir)
    except BaseException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return bundle_dir
