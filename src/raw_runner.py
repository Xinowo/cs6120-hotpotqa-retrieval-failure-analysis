"""
raw_runner.py

Stage 3 slice 2 (U5) for the metrics/schema v2 refactor: the runner / CLI /
migration-audit layer that drives the accepted, frozen writer core
(:mod:`src.raw_writer`, U1-U4) end to end for a real (or fake) retrieval run.

What this layer adds on top of the writer core:

- **Single-pass batch production (never a second retrieval).** For one
  ``(method, setting)`` it produces the ``(Paragraph, score)`` batches exactly
  once and feeds those same batches to the writer core (and, optionally, to the
  read-only migration-audit view). Pooled builds one shared index over the
  deduplicated pooled corpus and scores every question against it
  (``retrieve_many`` when the retriever offers it, else a per-query
  ``retrieve`` loop); per-question builds one index per example over that
  example's own paragraphs and saves the complete mini-corpus. This is the
  generalization the raw schema requires: export reuses the retrieval call that
  determined the ranking.
- **Bundle assembly and publication.** It shapes rows, computes the canonical
  checksum and the three fingerprints, assembles the manifest, and publishes an
  atomic, refuse-overwrite bundle -- all through :mod:`src.raw_writer`. It adds
  no serialization, no metric, and no validator of its own; ``write_raw_bundle``
  runs the full acceptance gate on the on-disk bytes.
- **Migration-audit title-order parity.** A pure comparison of the new rankings'
  per-example title order against a legacy ``retrieved_titles`` list (the
  read-only legacy baseline, or a temporary legacy-shaped view built from the
  *same* batches). Any temporary view is written only to a caller-supplied,
  ignored migration-scratch directory and is the caller's to delete; it is never
  a formal ``results/``/``evals/`` artifact.
- **A transitional CLI.** ``--method``/``--setting`` (``both`` publishes two
  independent bundles and reports both run IDs), an explicit ``--run-root``,
  opt-in legacy-audit, and injection hooks so smoke tests drive fake retrievers
  with no model download. It is additive: it changes no existing runner and does
  not become anyone's default.

AI-usage boundary: runner / CLI / migration plumbing over an already-frozen
schema and an already-accepted writer core -- agent-allowed. It defines no
metric, no failure label, and no new serialization; it never reuses the
mixed-purpose ``RESULT_COLUMNS`` contract (it reads only the legacy
``retrieved_titles`` join separator, for read-only migration-audit parsing).
"""

import argparse
import collections.abc
import os
import re
import shlex
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Optional, Sequence, Tuple

from src.data_loader import Paragraph, build_pooled_corpus
# TITLE_SEPARATOR is the legacy join separator; imported ONLY to parse the
# read-only legacy retrieved_titles column during migration-audit. This does not
# reuse the mixed RESULT_COLUMNS contract for the new raw schema.
from src.results_schema import TITLE_SEPARATOR
from src.raw_schema import RawSchemaError, compute_sha256
from src.raw_writer import (
    build_ranking_rows_from_batches,
    build_raw_manifest,
    build_retrieval_run_id,
    dataset_fingerprint,
    example_ids_fingerprint,
    per_example_corpus_size_map,
    per_question_corpus_fingerprint,
    pooled_corpus_fingerprint,
    rankings_csv_bytes,
    write_raw_bundle,
)

# The spec's canonical run-bundle root (results/ and evals/ are siblings).
DEFAULT_RUN_ROOT = os.path.join("results", "retrieval_runs")
# Protocol pooled depth; per-question depth is each example's full mini-corpus.
DEFAULT_POOLED_DEPTH = 50
RAW_METHODS = ("dense", "bm25")
RAW_SETTINGS = ("pooled", "per_question")
DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# A real git commit is a 40-hex SHA-1 (or a 64-hex SHA-256 object-format repo).
# The default git-provenance helper validates HEAD against this before recording
# it, so a manifest never carries a non-commit placeholder.
GIT_COMMIT_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")

# A retriever is anything exposing ``retrieve(query, top_k) -> [(Paragraph,
# score), ...]``; pooled additionally exploits an optional ``retrieve_many``.
# A retriever factory turns a paragraph list into such a retriever (so the pooled
# shared index and each per-question mini-index are built the same way, and tests
# inject a fake).
MakeRetriever = Callable[[List[Paragraph]], object]


@dataclass
class RawRunResult:
    """The outcome of publishing one ``(method, setting)`` run bundle."""
    method: str
    setting: str
    run_id: str
    bundle_dir: str
    manifest: dict
    rankings_bytes: bytes
    rows: List[dict]
    # The single retrieval's batches, kept so a caller (or migration-audit) can
    # reuse them without re-retrieving.
    batches: List[List[Tuple[Paragraph, float]]]
    # Pooled corpus (deduplicated) for a pooled run, else None.
    pooled_paragraphs: Optional[List[Paragraph]]


# ---------------------------------------------------------------------------
# Method default provenance configs (the manifest's model_or_retriever_config).
# ---------------------------------------------------------------------------


def dense_model_config(model_name: str = DENSE_MODEL_NAME) -> dict:
    """The closed Dense ``model_or_retriever_config``. ``score_type`` is derived
    by the manifest builder (``cosine_similarity``); this records only provenance,
    not the metric."""
    return {
        "implementation": "sentence_transformers",
        "identifier": model_name,
        "parameters": {"normalize": True},
    }


def bm25_model_config(package_version: str = "0.2.2") -> dict:
    """The exact frozen BM25 ``model_or_retriever_config`` the writer's BM25
    provenance gate (``validate_bm25_config``) requires. ``package_version`` is
    the installed ``rank_bm25`` distribution version; the remaining values
    describe the current ``BM25Okapi`` implementation (``text.lower().split()``
    tokenizer, no stopword removal)."""
    return {
        "implementation": "rank_bm25",
        "identifier": "BM25Okapi",
        "parameters": {
            "b": 0.75,
            "epsilon": 0.25,
            "k1": 1.5,
            "lowercase": True,
            "package_version": package_version,
            "stopword_policy": "none",
            "tokenizer": "python_str_split",
        },
    }


# ---------------------------------------------------------------------------
# Single-pass batch production (no second retrieval)
# ---------------------------------------------------------------------------


def _pooled_batches(retriever, examples, depth) -> List[List[Tuple[Paragraph, float]]]:
    """Score every question against the one shared pooled index in a single pass.

    Uses ``retrieve_many`` when the retriever offers it (Dense's batched matrix
    multiply), else a per-query ``retrieve`` loop (BM25 has no batch path); both
    return each query's top-``depth`` ``(Paragraph, score)`` list, so the two
    methods produce the identical row shape. The index is built once by the
    caller and never re-queried for export.
    """
    questions = [ex.question for ex in examples]
    retrieve_many = getattr(retriever, "retrieve_many", None)
    if callable(retrieve_many):
        return list(retrieve_many(questions, top_k=depth))
    return [retriever.retrieve(question, top_k=depth) for question in questions]


def _per_question_batches(make_retriever, examples) -> List[List[Tuple[Paragraph, float]]]:
    """Build one index per example over that example's own paragraphs and save
    its COMPLETE mini-corpus (``top_k == len(example.paragraphs)``), so
    ``saved_depth == per_example_corpus_size`` and no ranking is capped below its
    full corpus."""
    batches = []
    for example in examples:
        size = len(example.paragraphs)
        retriever = make_retriever(example.paragraphs)
        batches.append(retriever.retrieve(example.question, top_k=size))
    return batches


# ---------------------------------------------------------------------------
# Bundle assembly + publication (delegates every byte/validator to the writer)
# ---------------------------------------------------------------------------


def _raw_record_example_id(record) -> Optional[str]:
    """The ``example_id`` :func:`src.data_loader.process_example` derives from a
    raw dataset record: HotpotQA ``id`` (preferred) or legacy ``_id``. Returns
    ``None`` for a non-mapping record so the binding check below rejects it
    distinctly instead of raising an attribute error."""
    if not isinstance(record, dict):
        return None
    return record.get("id", record.get("_id"))


def _require_dataset_binding(raw_records: Sequence, examples: Sequence) -> None:
    """Fail closed unless the complete loaded raw records are bound to the
    evaluated examples: same non-empty cardinality and same selected ``id`` order.

    ``dataset_fingerprint`` hashes ``raw_records`` and ``example_ids_fingerprint``
    hashes ``examples``' IDs; the raw spec requires both in the SAME selected
    dataset order. If the two collections are unbound, a bundle could hash one
    dataset snapshot while publishing another's rankings/IDs, so a structurally
    valid manifest would falsely certify cross-method/migration provenance. We
    therefore reject a wrong count, a wrong ID, or a swapped order here rather
    than reordering or repairing the input.
    """
    if len(raw_records) != len(examples):
        raise ValueError(
            f"raw_records cardinality {len(raw_records)} does not match the "
            f"{len(examples)} loaded examples; dataset provenance must hash the same "
            "records that were evaluated, in the same selected order")
    for index, (record, example) in enumerate(zip(raw_records, examples)):
        record_id = _raw_record_example_id(record)
        if record_id != example.example_id:
            raise ValueError(
                f"raw_records[{index}] id {record_id!r} does not match "
                f"examples[{index}] example_id {example.example_id!r}; dataset "
                "provenance must be bound to the evaluated examples in selected order "
                "(mismatches are rejected, never reordered or repaired)")


def run_one_setting(
    *,
    method: str,
    setting: str,
    examples: Sequence,
    raw_records: Sequence,
    make_retriever: MakeRetriever,
    run_root: str,
    model_or_retriever_config: dict,
    dataset_identifier: str,
    split: str,
    date: str,
    seq: int,
    created_at: str,
    git_commit: str,
    command: str,
    pooled_depth: int = DEFAULT_POOLED_DEPTH,
    n_requested: Optional[int] = None,
    dataset_fingerprint_value: Optional[str] = None,
) -> RawRunResult:
    """Produce the single-pass batches for one ``(method, setting)`` and publish
    a complete run bundle through the writer core.

    ``raw_records`` are the complete loaded raw dataset records (pre-conversion),
    hashed for ``dataset_fingerprint``. They are bound to ``examples`` before
    retrieval: the same non-empty cardinality and the same selected ``id`` order,
    so the dataset digest can only describe the snapshot actually evaluated. The
    fingerprint is ALWAYS derived from those records; the optional
    ``dataset_fingerprint_value`` is a cache that must equal the freshly derived
    digest byte-for-byte (a mismatched or forged value is rejected, not trusted).
    Every serialization, checksum, schema, depth/completeness, and BM25-provenance
    check happens inside :func:`src.raw_writer.write_raw_bundle` on the exact
    on-disk bytes; this function only shapes the inputs.
    """
    if method not in RAW_METHODS:
        raise ValueError(f"method must be one of {RAW_METHODS}, got {method!r}")
    if setting not in RAW_SETTINGS:
        raise ValueError(f"setting must be one of {RAW_SETTINGS}, got {setting!r}")
    examples = list(examples)
    n_loaded = len(examples)
    if n_loaded < 1:
        raise ValueError("a formal run needs at least one example")
    if n_requested is None:
        n_requested = n_loaded

    # Bind dataset provenance to the evaluated examples BEFORE retrieval (a
    # generator of raw records is materialized exactly once here). See
    # :func:`_require_dataset_binding`.
    raw_records = list(raw_records)
    _require_dataset_binding(raw_records, examples)

    if setting == "pooled":
        pooled_paragraphs, _collision_titles = build_pooled_corpus(examples)
        retriever = make_retriever(pooled_paragraphs)
        batches = _pooled_batches(retriever, examples, pooled_depth)
        retrieval_depth = pooled_depth
        corpus_fingerprint = pooled_corpus_fingerprint(pooled_paragraphs)
    else:
        pooled_paragraphs = None
        batches = _per_question_batches(make_retriever, examples)
        # retrieval_depth is the maximum per-example saved depth (spec rule); the
        # per-example truth lives in per_example_corpus_size.
        retrieval_depth = max(len(example.paragraphs) for example in examples)
        corpus_fingerprint = per_question_corpus_fingerprint(examples)

    run_id = build_retrieval_run_id(method, setting, n_loaded, retrieval_depth, date, seq)
    rows = build_ranking_rows_from_batches(
        examples, batches, retrieval_run_id=run_id, method=method, setting=setting
    )
    rankings_bytes = rankings_csv_bytes(rows)

    derived_dataset_fingerprint = dataset_fingerprint(raw_records)
    if (dataset_fingerprint_value is not None
            and dataset_fingerprint_value != derived_dataset_fingerprint):
        raise ValueError(
            f"supplied dataset_fingerprint_value {dataset_fingerprint_value!r} does "
            f"not equal the digest derived from the loaded raw records "
            f"{derived_dataset_fingerprint!r}; a cached digest must match the freshly "
            "derived one exactly (no valid-digest bypass)")
    dataset_fingerprint_value = derived_dataset_fingerprint
    ids_fingerprint = example_ids_fingerprint([example.example_id for example in examples])

    manifest_kwargs = dict(
        method=method,
        setting=setting,
        split=split,
        n_requested=n_requested,
        n_loaded=n_loaded,
        retrieval_depth=retrieval_depth,
        date=date,
        seq=seq,
        created_at=created_at,
        model_or_retriever_config=model_or_retriever_config,
        dataset_identifier=dataset_identifier,
        dataset_fingerprint=dataset_fingerprint_value,
        example_ids_fingerprint=ids_fingerprint,
        corpus_fingerprint=corpus_fingerprint,
        git_commit=git_commit,
        command=command,
        rankings_sha256=compute_sha256(rankings_bytes),
    )
    if setting == "pooled":
        manifest_kwargs["corpus_size"] = len(pooled_paragraphs)
    else:
        manifest_kwargs["per_example_corpus_size"] = per_example_corpus_size_map(examples, batches)

    manifest = build_raw_manifest(**manifest_kwargs)
    bundle_dir = write_raw_bundle(run_root, manifest, rankings_bytes)

    return RawRunResult(
        method=method,
        setting=setting,
        run_id=run_id,
        bundle_dir=bundle_dir,
        manifest=manifest,
        rankings_bytes=rankings_bytes,
        rows=rows,
        batches=batches,
        pooled_paragraphs=pooled_paragraphs,
    )


# ---------------------------------------------------------------------------
# Migration-audit: new rankings vs legacy retrieved_titles (title-order parity)
# ---------------------------------------------------------------------------


@dataclass
class TitleMismatch:
    """One (example, rank) where the new ranking title differs from legacy."""
    example_id: str
    rank: int
    legacy_title: Optional[str]
    new_title: Optional[str]


def titles_by_example_from_rows(rows: Sequence[dict]) -> dict:
    """Group new rankings rows into ``{example_id: [title, ...]}`` in ascending
    rank order (the writer's canonical physical order)."""
    by_example: dict = {}
    for row in sorted(rows, key=lambda r: (r["example_id"], r["rank"])):
        by_example.setdefault(row["example_id"], []).append(row["title"])
    return by_example


LEGACY_AUDIT_REQUIRED_COLUMNS = ("method", "setting", "example_id", "retrieved_titles")


def legacy_titles_by_example(legacy_rows: Sequence[dict], method: str, setting: str) -> dict:
    """Extract ``{example_id: [title, ...]}`` from legacy long-format rows for one
    ``(method, setting)``, rejecting malformed migration input distinctly.

    Each legacy row carries a ``retrieved_titles`` cell joined by the legacy
    ``TITLE_SEPARATOR``; the ranked order is the join order. Read-only migration
    input: nothing here is written back to a formal artifact.

    The legacy contract is one row per ``(method, setting, example)`` and a formal
    stored ranking is non-empty. A silent read that let a later duplicate row
    overwrite an earlier ranking, or that turned an empty/NaN ``retrieved_titles``
    cell into ``[]``, would make :func:`title_parity_report` iterate zero legacy
    ranks and report a FALSE zero-mismatch parity -- the exact message used to
    approve a migration. We therefore validate the required columns, reject a
    duplicate ``(method, setting, example_id)`` (in either row order), reject an
    empty/non-string ``example_id``, and reject an empty/NaN stored title list
    BEFORE any parity comparison, raising :class:`RawSchemaError`. The intentional
    legal case -- a non-empty legacy prefix shorter than a complete per-question v1
    list -- is preserved (that is a rank-by-rank agreement, handled by
    :func:`title_parity_report`, not an empty legacy list).
    """
    by_example: dict = {}
    for position, row in enumerate(legacy_rows):
        for column in LEGACY_AUDIT_REQUIRED_COLUMNS:
            if column not in row:
                raise RawSchemaError(
                    f"legacy audit row {position} is missing required column "
                    f"{column!r}; malformed migration input must be rejected, not "
                    "read as zero mismatches")
        if row["method"] != method or row["setting"] != setting:
            continue
        example_id = row["example_id"]
        if not isinstance(example_id, str) or example_id == "":
            raise RawSchemaError(
                f"legacy audit row {position} has an empty/non-string example_id "
                f"{example_id!r} for {method}/{setting}")
        if example_id in by_example:
            raise RawSchemaError(
                f"legacy audit has a duplicate row for example_id {example_id!r} "
                f"({method}/{setting}); the legacy contract is one row per "
                "(method, setting, example) and a later row must not silently "
                "overwrite an earlier ranking")
        cell = row["retrieved_titles"]
        if not isinstance(cell, str) or cell == "":
            raise RawSchemaError(
                f"legacy audit row for example_id {example_id!r} ({method}/{setting}) "
                "has an empty/NaN retrieved_titles cell; a formal stored ranking is "
                "non-empty, so an empty legacy list cannot certify zero-mismatch "
                "parity")
        by_example[example_id] = cell.split(TITLE_SEPARATOR)
    return by_example


def _materialize_legacy_ranking(value, example_id: str) -> List[str]:
    """Validate one legacy ranking's nested SHAPE and materialize it exactly once,
    BEFORE any parity comparison, so a malformed ranking can never iterate zero
    times (or character-by-character) and become the false ``[]`` zero-mismatch
    approval signal.

    A formal stored ranking is an ORDERED, non-empty collection of string titles.
    A bare truthiness check (``if not ranking``) is insufficient: a Python
    generator/iterator object is truthy even when it yields nothing, and a bare
    ``str``/``bytes`` is truthy and iterable, so both slip past it and are then
    read as zero mismatches or per-character "titles". We therefore:

    - reject a bare ``str``/``bytes``/``bytearray`` (a character/byte sequence, not
      a title collection);
    - reject a :class:`collections.abc.Mapping` (iterating it hashes only keys);
    - reject an unordered :class:`collections.abc.Set` (``set``/``frozenset``/
      keys-view -- no saved rank order to compare against);
    - support an ordered iterable (``list``/``tuple``/generator/iterator) by
      materializing it **exactly once** via ``list(value)``; a non-iterable scalar
      raises here;
    - require the materialized ranking to be non-empty and every element a string.

    Nothing is stringified, split, reordered, dropped, or repaired -- malformed
    input is rejected with :class:`RawSchemaError`, never normalized into success.
    """
    if isinstance(value, (str, bytes, bytearray)):
        raise RawSchemaError(
            f"legacy ranking for example_id {example_id!r} is a bare "
            f"{type(value).__name__} {value!r}; a formal stored ranking is an ordered "
            "collection of string titles, not a character/byte sequence (rejected "
            "before any comparison, never split into per-character titles)")
    if isinstance(value, collections.abc.Mapping):
        raise RawSchemaError(
            f"legacy ranking for example_id {example_id!r} is a mapping ({value!r}); a "
            "formal stored ranking is an ordered title collection, not a mapping "
            "(iterating it would compare only its keys)")
    if isinstance(value, collections.abc.Set):
        raise RawSchemaError(
            f"legacy ranking for example_id {example_id!r} is an unordered "
            f"{type(value).__name__} ({value!r}); a stored ranking must carry a saved "
            "rank order, which a set/frozenset/keys-view cannot provide")
    try:
        materialized = list(value)   # ordered iterable / one-shot iterator: consumed once
    except TypeError as err:
        raise RawSchemaError(
            f"legacy ranking for example_id {example_id!r} is not iterable ({value!r}); "
            "a formal stored ranking is an ordered collection of string titles") from err
    if not materialized:
        raise RawSchemaError(
            f"legacy ranking for example_id {example_id!r} is empty; a formal stored "
            "ranking is non-empty, so an empty legacy ranking cannot certify "
            "zero-mismatch parity (rejected before any comparison, never read as zero "
            "mismatches)")
    for position, title in enumerate(materialized):
        if not isinstance(title, str):
            raise RawSchemaError(
                f"legacy ranking for example_id {example_id!r} has a non-string title "
                f"at rank {position + 1} ({title!r}); ranking titles must be strings")
    return materialized


def title_parity_report(
    new_titles: dict, legacy_titles: dict, *, require_same_examples: bool = True
) -> List[TitleMismatch]:
    """Compare new vs legacy per-example title order and return every mismatch.

    For each example present in the legacy baseline, every legacy rank must equal
    the new title at that position (the raw/parity rule: agree at every saved
    rank). A new list shorter than legacy, or a differing title at any rank, is a
    mismatch. An empty returned list means zero title-order mismatches (parity).
    With ``require_same_examples`` the example_id sets must match exactly (a
    missing or extra example is itself surfaced as a mismatch).

    This helper is also a public boundary, so it fails closed on a malformed legacy
    ranking rather than trusting the caller to have filtered it. Each legacy ranking
    is validated and materialized ONCE by :func:`_materialize_legacy_ranking` before
    any comparison: a bare str/bytes, a mapping, an unordered set, a non-iterable,
    an empty collection, and a truthy-but-empty generator/iterator are all rejected
    with :class:`RawSchemaError`, so none can iterate zero (or per-character) times
    and return ``[]`` -- the exact zero-mismatch approval signal. A non-empty legacy
    prefix shorter than a complete new list stays the intentional legal case
    (rank-by-rank agreement, not emptiness) and is preserved.
    """
    validated_legacy = {
        example_id: _materialize_legacy_ranking(legacy_titles[example_id], example_id)
        for example_id in sorted(legacy_titles)
    }
    mismatches: List[TitleMismatch] = []
    if require_same_examples:
        for example_id in sorted(set(new_titles) - set(validated_legacy)):
            mismatches.append(TitleMismatch(example_id, 0, None, "<example absent from legacy>"))
    for example_id in sorted(validated_legacy):
        legacy_list = validated_legacy[example_id]
        new_list = new_titles.get(example_id)
        if new_list is None:
            mismatches.append(TitleMismatch(example_id, 0, "<example absent from new run>", None))
            continue
        for index, legacy_title in enumerate(legacy_list):
            new_title = new_list[index] if index < len(new_list) else None
            if new_title != legacy_title:
                mismatches.append(
                    TitleMismatch(example_id, index + 1, legacy_title, new_title))
    return mismatches


def build_legacy_audit_view_rows(result: RawRunResult, *, store_depth: Optional[int] = None) -> List[dict]:
    """Build legacy-shaped ``{method, setting, example_id, retrieved_titles}`` rows
    from the SAME batches (no re-retrieval), for a temporary migration-audit view.

    Only for comparison against the read-only legacy baseline; the caller writes
    this to an ignored migration-scratch directory and deletes it after the audit.
    ``store_depth`` optionally truncates each title list to the legacy stored
    depth (10 per-question / 50 pooled) so the two lists line up rank-for-rank.
    """
    new_titles = titles_by_example_from_rows(result.rows)
    view_rows = []
    for example_id in sorted(new_titles):
        titles = new_titles[example_id]
        if store_depth is not None:
            titles = titles[:store_depth]
        view_rows.append({
            "method": result.method,
            "setting": result.setting,
            "example_id": example_id,
            "retrieved_titles": TITLE_SEPARATOR.join(titles),
        })
    return view_rows


# ---------------------------------------------------------------------------
# Default (real) retriever factories -- thin, lazy, never touched by smoke tests
# ---------------------------------------------------------------------------


def default_retriever_factory(method: str, *, encoder=None, model_name: str = DENSE_MODEL_NAME,
                              cache_dir=None) -> MakeRetriever:
    """Return a ``make_retriever(paragraphs)`` for real runs. Retriever classes are
    imported lazily so an injected fake factory (and thus the offline smoke tests)
    never imports a real model / BM25 backend."""
    if method == "dense":
        from src.dense_retriever import DenseRetriever

        def make_dense(paragraphs):
            return DenseRetriever(paragraphs, encoder=encoder, model_name=model_name,
                                  cache_dir=cache_dir)

        return make_dense
    if method == "bm25":
        from src.retrievers import BM25Retriever

        def make_bm25(paragraphs):
            return BM25Retriever(paragraphs)

        return make_bm25
    raise ValueError(f"method must be one of {RAW_METHODS}, got {method!r}")


def default_model_config(method: str, *, model_name: str = DENSE_MODEL_NAME) -> dict:
    """The provenance config for a real run of ``method``."""
    if method == "dense":
        return dense_model_config(model_name)
    if method == "bm25":
        return bm25_model_config(_installed_bm25_version())
    raise ValueError(f"method must be one of {RAW_METHODS}, got {method!r}")


def _installed_bm25_version() -> str:
    """The installed ``rank_bm25`` distribution version for the BM25 provenance
    config. Fails closed: it raises when the version cannot be established rather
    than substituting a pinned-looking placeholder.

    ``package_version`` is factual dependency provenance for the formal manifest,
    not a default. A hard-coded fallback (the previous ``"0.2.2"``) is non-empty
    and therefore passes the generic manifest shape validator, so it would let an
    invented version be certified clean and defeat reproducibility. We look the
    version up and refuse to invent one when metadata is missing or empty.
    """
    import importlib.metadata as importlib_metadata

    try:
        installed = importlib_metadata.version("rank_bm25")
    except importlib_metadata.PackageNotFoundError as err:
        raise RuntimeError(
            "cannot establish the installed rank_bm25 version for BM25 provenance; "
            "refusing to record a fabricated placeholder version") from err
    if not isinstance(installed, str) or installed.strip() == "":
        raise RuntimeError(
            f"installed rank_bm25 version is empty/invalid ({installed!r}); refusing "
            "to record fabricated BM25 provenance")
    return installed


def _git_head() -> str:
    """The current git commit that produced the run, for manifest provenance.
    Fails closed: it raises when git is unavailable, exits nonzero, or returns a
    non-commit-shaped value rather than substituting a placeholder.

    ``git_commit`` is factual code provenance and audit evidence, not a default.
    The previous ``"unknown_git_commit"`` fallback is non-empty and passes the
    generic manifest shape validator, so it would let a run with no real commit be
    certified clean. We check the exit status and validate a real commit-shaped
    result (40- or 64-hex) before returning it.
    """
    import subprocess

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    except OSError as err:
        raise RuntimeError(
            "cannot run git to establish the commit for run provenance; refusing to "
            "record a fabricated placeholder commit") from err
    if completed.returncode != 0:
        raise RuntimeError(
            f"git rev-parse HEAD failed (exit {completed.returncode}): "
            f"{completed.stderr.strip()!r}; refusing to record a placeholder commit")
    head = completed.stdout.strip()
    if GIT_COMMIT_RE.fullmatch(head) is None:
        raise RuntimeError(
            f"git rev-parse HEAD returned a non-commit-shaped value {head!r}; "
            "refusing to record fabricated code provenance")
    return head


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish v2 raw retrieval run bundles (results/retrieval_runs/<run-id>/). "
                    "Additive/transitional: changes no existing runner and is not a default.")
    parser.add_argument("--method", required=True, choices=list(RAW_METHODS))
    parser.add_argument("--setting", default="both",
                        choices=["both", "pooled", "per_question"])
    parser.add_argument("--n", type=int, default=None,
                        help="number of questions to load (default: all in split)")
    parser.add_argument("--split", default="validation")
    parser.add_argument("--run-root", default=DEFAULT_RUN_ROOT, dest="run_root",
                        help="bundle root; refuse-overwrite on an existing run-id dir")
    parser.add_argument("--depth", type=int, default=DEFAULT_POOLED_DEPTH,
                        help="pooled retrieval depth (per-question uses each full mini-corpus)")
    parser.add_argument("--seq", type=int, default=1, help="same-day rerun sequence (1..99)")
    parser.add_argument("--dataset-identifier", default="hotpotqa_distractor_v1",
                        dest="dataset_identifier")
    parser.add_argument("--model-name", default=DENSE_MODEL_NAME, dest="model_name")
    parser.add_argument("--legacy-audit", default=None, dest="legacy_audit",
                        help="opt-in: legacy long-format CSV to check title-order parity against "
                             "(read-only migration input; never written back)")
    return parser


def _settings_for(setting_arg: str) -> List[str]:
    return list(RAW_SETTINGS) if setting_arg == "both" else [setting_arg]


def _default_load_dataset(split: str, n: Optional[int]):
    """Load raw records and processed examples together (real path). Returns
    ``(raw_records, examples)`` where raw_records are plain JSON-compatible dicts
    for the dataset fingerprint."""
    from src.data_loader import load_raw_hotpotqa, process_example

    raw = load_raw_hotpotqa(split=split, n=n)
    raw_records = [dict(record) for record in raw]
    examples = [process_example(record) for record in raw_records]
    return raw_records, examples


def _reconstruct_command() -> str:
    """Reconstruct the exact, replayable command line that launched this process.

    Uses :func:`shlex.join`, so an argument containing spaces or quotes round-trips
    through :func:`shlex.split` to the identical argv -- a raw ``" ".join`` cannot
    represent argument boundaries and would silently corrupt, for example, a
    ``--run-root`` path that contains spaces. The argv is the real process argv, so
    the recorded command names the entry point actually used (the executable plus
    the script path or ``-m module``) instead of a hard-coded guess.
    ``sys.orig_argv`` (Python 3.10+) preserves ``-m module`` and the true
    interpreter path; on earlier interpreters we fall back to
    ``[sys.executable, *sys.argv]``, which still records the real executable and
    entry-point path.
    """
    orig_argv = getattr(sys, "orig_argv", None)
    argv = list(orig_argv) if orig_argv else [sys.executable, *sys.argv]
    return shlex.join(argv)


def _legacy_audit(result: RawRunResult, legacy_csv_path: str) -> List[TitleMismatch]:
    """Read the legacy CSV (read-only), extract this run's ``(method, setting)``
    titles, and return the title-order mismatches against the new run."""
    import pandas as pd

    frame = pd.read_csv(legacy_csv_path, dtype=str).fillna("")
    legacy_rows = frame.to_dict("records")
    legacy_titles = legacy_titles_by_example(legacy_rows, result.method, result.setting)
    new_titles = titles_by_example_from_rows(result.rows)
    return title_parity_report(new_titles, legacy_titles)


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    make_retriever_factory: Optional[Callable[[str], MakeRetriever]] = None,
    load_dataset: Optional[Callable[[str, Optional[int]], Tuple[Sequence, Sequence]]] = None,
    model_config_for: Optional[Callable[[str], dict]] = None,
    now: Optional[Callable[[], datetime]] = None,
    git_commit: Optional[str] = None,
    command: Optional[str] = None,
) -> int:
    """Run the raw retrieval CLI. Every external dependency (retriever
    construction, dataset loading, wall clock, git, and the recorded command) is
    injectable so smoke tests stay fully offline. ``--setting both`` publishes two
    independent bundles, audits every requested setting, and reports both run IDs;
    it returns nonzero only after finishing every setting. Returns a process exit
    code (0 on success)."""
    args = _build_arg_parser().parse_args(argv)

    if make_retriever_factory is None:
        def make_retriever_factory(method):
            return default_retriever_factory(method, model_name=args.model_name)
    if load_dataset is None:
        load_dataset = _default_load_dataset
    if model_config_for is None:
        def model_config_for(method):
            return default_model_config(method, model_name=args.model_name)
    if now is None:
        now = lambda: datetime.now(timezone.utc)
    if git_commit is None:
        git_commit = _git_head()
    if command is None:
        command = _reconstruct_command()

    moment = now()
    date = moment.strftime("%Y%m%d")
    created_at = moment.strftime("%Y-%m-%dT%H:%M:%SZ")

    raw_records, examples = load_dataset(args.split, args.n)
    # Materialize BOTH collections exactly once here -- immediately after loading
    # and before the settings loop or any publication -- so a one-shot loader (an
    # aligned generator of raw records is a documented valid input) composes with
    # --setting both. If raw_records stayed a generator, the first setting would
    # consume it via run_one_setting's own list() and publish, then the second
    # would bind against an empty list and raise cardinality zero -- a misleading
    # half-run that already wrote one bundle. Both settings must hash and publish
    # the same materialized snapshot; run_one_setting keeps its defensive list()
    # so a direct caller stays safe too.
    raw_records = list(raw_records)
    examples = list(examples)
    make_retriever = make_retriever_factory(args.method)
    model_or_retriever_config = model_config_for(args.method)

    published: List[RawRunResult] = []
    audit_mismatch = False
    for setting in _settings_for(args.setting):
        result = run_one_setting(
            method=args.method,
            setting=setting,
            examples=examples,
            raw_records=raw_records,
            make_retriever=make_retriever,
            run_root=args.run_root,
            model_or_retriever_config=model_or_retriever_config,
            dataset_identifier=args.dataset_identifier,
            split=args.split,
            date=date,
            seq=args.seq,
            created_at=created_at,
            git_commit=git_commit,
            command=command,
            pooled_depth=args.depth,
            n_requested=args.n,
        )
        published.append(result)
        print(f"published {result.run_id} -> {result.bundle_dir}")

        if args.legacy_audit:
            # The migration audit is a post-publication comparison, so a parity
            # MISMATCH is an audit *result*, not a reason to skip the other
            # setting. With --setting both we must still publish and audit the
            # remaining setting, report every run ID, and aggregate the mismatch
            # status, returning nonzero only after every requested setting has run.
            # (Malformed legacy input is a distinct, fatal condition that raises
            # inside _legacy_audit before it can be mistaken for parity.)
            mismatches = _legacy_audit(result, args.legacy_audit)
            if mismatches:
                audit_mismatch = True
                print(f"  MIGRATION-AUDIT: {len(mismatches)} title-order mismatch(es) vs "
                      f"{args.legacy_audit} for {result.method}/{result.setting}")
                for mismatch in mismatches[:10]:
                    print(f"    {mismatch.example_id} rank {mismatch.rank}: "
                          f"legacy={mismatch.legacy_title!r} new={mismatch.new_title!r}")
            else:
                print(f"  MIGRATION-AUDIT: zero title-order mismatches vs legacy "
                      f"{result.method}/{result.setting}")

    print("run_ids: " + ", ".join(result.run_id for result in published))
    return 1 if audit_mismatch else 0


if __name__ == "__main__":
    raise SystemExit(main())
