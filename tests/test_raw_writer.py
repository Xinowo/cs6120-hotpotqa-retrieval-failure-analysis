"""
test_raw_writer.py

Synthetic, offline tests for the RAW retrieval writer core in
:mod:`src.raw_writer` (Stage 3, writer half of the metrics/schema v2 refactor).
Every fixture is a hand-built fake example / ``(Paragraph, score)`` batch plus
in-memory bytes: no model download, no network, no real corpus, and no formal
run bundle written outside pytest's ``tmp_path``.

These tests exercise the *producer* side of the frozen
``retrieval_raw_schema_v1`` contract
(``docs/specs/2026-07-20-raw-retrieval-rankings-schema.md``): the byte-exact
``rankings.csv`` / ``manifest.json`` serialization, the canonical-JSON
fingerprint inputs, the canonical run-ID spelling, atomic refuse-overwrite bundle
writing, and the row builder that consumes already-retrieved batches. The whole
point is that whatever the writer emits is accepted by the independent
:mod:`src.raw_schema` validators and that its exact bytes hash to the recorded
``rankings_sha256``. They never assert a metric value -- the raw layer has none.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import inspect
import json
from collections import deque

import numpy as np
import pytest

from src.data_loader import Paragraph
from src.raw_schema import (
    RANKING_COLUMNS,
    RETRIEVAL_RAW_SCHEMA_V1,
    SCORE_TYPE_BY_METHOD,
    SHA256_FINGERPRINT_RE,
    SHA256_HEX_RE,
    RawSchemaError,
    compute_sha256,
    validate_bm25_config,
    validate_manifest,
    validate_rankings_rows,
    validate_raw_bundle,
    validate_rankings_checksum,
    validate_retrieval_run_id,
)
from src import raw_writer
from src.raw_writer import (
    MANIFEST_FILENAME,
    RANKINGS_FILENAME,
    build_ranking_rows_from_batches,
    build_raw_manifest,
    build_retrieval_run_id,
    canonical_json_bytes,
    dataset_fingerprint,
    example_ids_fingerprint,
    fingerprint,
    manifest_json_bytes,
    per_example_corpus_size_map,
    per_question_corpus_fingerprint,
    pooled_corpus_fingerprint,
    rankings_csv_bytes,
    read_rankings_bytes,
    write_raw_bundle,
)


# ---------------------------------------------------------------------------
# Fakes (pure Python; the writer only duck-types .example_id / .paragraphs on an
# example and .title / .text on a paragraph, and consumes (Paragraph, score))
# ---------------------------------------------------------------------------


class FakeExample:
    def __init__(self, example_id, paragraphs=None):
        self.example_id = example_id
        self.paragraphs = paragraphs or []


def _para(title, text=None):
    return Paragraph(title=title, text=text if text is not None else f"text of {title}")


def _batch(pairs):
    """Build one example's ranked [(Paragraph, score), ...] from (title, score)."""
    return [(_para(title), score) for title, score in pairs]


def _perq_example_and_batch(example_id, pairs, *, source_paragraphs=None):
    """Return a self-consistent per-question ``(FakeExample, batch)`` pair.

    The example's source ``.paragraphs`` are the retrieved-and-scored paragraphs
    (unless ``source_paragraphs`` overrides them), so the source mini-corpus size
    ``len(example.paragraphs)`` equals the saved batch depth ``len(batch)`` by
    construction -- exactly the independent consistency the per_question contract
    requires. Passing a larger ``source_paragraphs`` models a ranking capped below
    its full mini-corpus (an invalid raw artifact)."""
    paragraphs = [_para(title) for title, _ in pairs]
    batch = [(paragraph, score) for paragraph, (_, score) in zip(paragraphs, pairs)]
    example = FakeExample(example_id, source_paragraphs if source_paragraphs is not None
                          else paragraphs)
    return example, batch


def _dense_model_config():
    return {
        "implementation": "sentence_transformers",
        "identifier": "all-MiniLM-L6-v2",
        "parameters": {"normalize": True, "batch_size": 32},
    }


def _bm25_model_config():
    return {
        "implementation": "rank_bm25",
        "identifier": "BM25Okapi",
        "parameters": {
            "b": 0.75,
            "epsilon": 0.25,
            "k1": 1.5,
            "lowercase": True,
            "package_version": "0.2.2",
            "stopword_policy": "none",
            "tokenizer": "python_str_split",
        },
    }


def _canned_fingerprints():
    """Format-valid fingerprint strings for tests that only need a valid manifest
    shape, not the real fingerprint algorithm (covered separately)."""
    return {
        "dataset_fingerprint": "sha256:" + "a" * 64,
        "example_ids_fingerprint": "sha256:" + "b" * 64,
        "corpus_fingerprint": "sha256:" + "c" * 64,
    }


def _build_bundle(method, setting, batches, examples, *, depth, corpus_size=None,
                  model_config=None, parent=None):
    """End-to-end helper: batches -> rows -> checksum -> manifest -> (manifest, bytes).

    Returns the built manifest and the exact rankings bytes, both consistent, so a
    caller can write and/or validate them. Depth/corpus_size are chosen by the
    caller to be internally consistent with the batches.
    """
    n_loaded = len(examples)
    run_id = build_retrieval_run_id(method, setting, n_loaded, depth, "20260720", 1)
    rows = build_ranking_rows_from_batches(
        examples, batches, retrieval_run_id=run_id, method=method, setting=setting
    )
    rankings_bytes = rankings_csv_bytes(rows)
    sha = compute_sha256(rankings_bytes)

    kwargs = dict(
        method=method,
        setting=setting,
        split="validation",
        n_requested=n_loaded,
        n_loaded=n_loaded,
        retrieval_depth=depth,
        date="20260720",
        seq=1,
        created_at="2026-07-20T12:00:00Z",
        model_or_retriever_config=model_config or _dense_model_config(),
        dataset_identifier="hotpotqa_distractor_v1",
        git_commit="0" * 40,
        command=f"python scripts/run_x.py --setting {setting}",
        rankings_sha256=sha,
        **_canned_fingerprints(),
    )
    if setting == "pooled":
        kwargs["corpus_size"] = corpus_size
    else:
        kwargs["per_example_corpus_size"] = per_example_corpus_size_map(examples, batches)
    if method == "rerank":
        kwargs["parent_retrieval_run_id"] = parent or "dense_pooled_n2_d3_20260720_r01"
        kwargs["parent_rankings_sha256"] = "e" * 64
        kwargs["parent_candidate_depth"] = depth

    manifest = build_raw_manifest(**kwargs)
    return manifest, rankings_bytes


# ---------------------------------------------------------------------------
# U1 -- byte-exact serialization
# ---------------------------------------------------------------------------


def test_int_text_rejects_bool_and_formats_plainly():
    assert raw_writer._int_text(0) == "0"
    assert raw_writer._int_text(50) == "50"
    with pytest.raises(RawSchemaError):
        raw_writer._int_text(True)
    with pytest.raises(RawSchemaError):
        raw_writer._int_text(1.0)


def test_float_text_normalizes_negative_zero():
    assert raw_writer._float_text(0.0) == "0"
    assert raw_writer._float_text(-0.0) == "0"
    # A tiny negative underflowing to -0.0 also normalizes.
    assert raw_writer._float_text(-1e-400) == "0"


def test_float_text_round_trips_full_precision():
    for value in (0.1, 1.0 / 3.0, 123456.789012345, 1e-10, -2.5, 9.999999999999999):
        assert float(raw_writer._float_text(value)) == value
    # Lowercase exponent, per the frozen rule.
    assert "e" in raw_writer._float_text(1e-10)
    assert "E" not in raw_writer._float_text(1e-10)


def test_float_text_rejects_non_finite_and_bool():
    for bad in (float("inf"), float("-inf"), float("nan"), True):
        with pytest.raises(RawSchemaError):
            raw_writer._float_text(bad)


def test_rankings_bytes_are_utf8_lf_no_bom():
    ex = [FakeExample("q1")]
    rows = build_ranking_rows_from_batches(
        ex, [_batch([("t1", 0.9), ("t2", 0.8)])],
        retrieval_run_id="dense_pooled_n1_d2_20260720_r01", method="dense", setting="pooled",
    )
    data = rankings_csv_bytes(rows)
    assert not data.startswith(b"\xef\xbb\xbf")   # no UTF-8 BOM
    assert b"\r" not in data                       # LF only, never CRLF
    assert data.endswith(b"\n")
    text = data.decode("utf-8")
    assert text.splitlines()[0] == ",".join(RANKING_COLUMNS)


def test_rankings_round_trip_parses_back_and_validates():
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 0.9), ("t2", 0.8), ("t3", 0.7)]),
               _batch([("u1", 0.5), ("u2", 0.4), ("u3", 0.3)])]
    manifest, data = _build_bundle("dense", "pooled", batches, ex, depth=3, corpus_size=5)

    columns, rows = read_rankings_bytes(data)
    assert columns == RANKING_COLUMNS
    validate_rankings_rows(rows, manifest)
    # The recorded checksum is over exactly these bytes.
    validate_rankings_checksum(data, manifest)
    assert manifest["rankings_sha256"] == compute_sha256(data)


def test_rankings_serialized_in_canonical_order_regardless_of_input():
    # Feed rows deliberately out of (example_id, rank) order.
    run_id = "dense_pooled_n2_d2_20260720_r01"
    unordered = [
        {"retrieval_run_id": run_id, "method": "dense", "setting": "pooled",
         "example_id": "q2", "rank": 2, "title": "b2", "score": 0.1},
        {"retrieval_run_id": run_id, "method": "dense", "setting": "pooled",
         "example_id": "q1", "rank": 2, "title": "a2", "score": 0.2},
        {"retrieval_run_id": run_id, "method": "dense", "setting": "pooled",
         "example_id": "q2", "rank": 1, "title": "b1", "score": 0.3},
        {"retrieval_run_id": run_id, "method": "dense", "setting": "pooled",
         "example_id": "q1", "rank": 1, "title": "a1", "score": 0.4},
    ]
    _, rows = read_rankings_bytes(rankings_csv_bytes(unordered))
    assert [(r["example_id"], r["rank"]) for r in rows] == [
        ("q1", 1), ("q1", 2), ("q2", 1), ("q2", 2)
    ]


def test_rankings_csv_quotes_special_characters():
    run_id = "dense_pooled_n1_d3_20260720_r01"
    tricky = ["plain", 'has "quotes" inside', "has,comma\nand newline"]
    rows = [
        {"retrieval_run_id": run_id, "method": "dense", "setting": "pooled",
         "example_id": "q1", "rank": i + 1, "title": title, "score": 1.0 - 0.1 * i}
        for i, title in enumerate(tricky)
    ]
    _, parsed = read_rankings_bytes(rankings_csv_bytes(rows))
    assert [r["title"] for r in parsed] == tricky


def test_rankings_rejects_non_string_cell():
    run_id = "dense_pooled_n1_d1_20260720_r01"
    rows = [{"retrieval_run_id": run_id, "method": "dense", "setting": "pooled",
             "example_id": "q1", "rank": 1, "title": None, "score": 0.5}]
    with pytest.raises(RawSchemaError):
        rankings_csv_bytes(rows)


def test_manifest_json_bytes_is_canonical():
    manifest = {"b": 1, "a": {"d": 2, "c": 3}}
    data = manifest_json_bytes(manifest)
    assert data.endswith(b"\n")
    assert not data.startswith(b"\xef\xbb\xbf")
    text = data.decode("utf-8")
    # sorted keys, no whitespace separators, exactly one trailing newline.
    assert text == '{"a":{"c":3,"d":2},"b":1}\n'
    assert json.loads(text) == manifest


def test_manifest_json_bytes_rejects_non_finite():
    with pytest.raises(ValueError):
        manifest_json_bytes({"x": float("nan")})


def test_fingerprint_format_determinism_and_no_trailing_newline():
    value = [{"title": "t", "text": "x"}]
    fp = fingerprint(value)
    assert SHA256_FINGERPRINT_RE.fullmatch(fp) is not None
    assert fingerprint(value) == fp                      # deterministic
    assert fingerprint([{"title": "t", "text": "y"}]) != fp   # content-sensitive
    # Fingerprint input has NO trailing newline (unlike manifest bytes).
    assert not canonical_json_bytes(value).endswith(b"\n")
    assert fp == "sha256:" + compute_sha256(canonical_json_bytes(value))


# ---------------------------------------------------------------------------
# U2 -- fingerprint builders, run-ID, manifest assembly
# ---------------------------------------------------------------------------


def test_build_run_id_canonical_no_leading_zeros():
    run_id = build_retrieval_run_id("dense", "pooled", 500, 50, "20260720", 1)
    assert run_id == "dense_pooled_n500_d50_20260720_r01"
    # Fully valid per the independent validator (grammar + real date + r>=01).
    validate_retrieval_run_id(run_id, expected_method="dense", expected_setting="pooled",
                              expected_n=500, expected_depth=50)


@pytest.mark.parametrize("kwargs", [
    {"seq": 0}, {"seq": 100}, {"n_loaded": 0}, {"retrieval_depth": 0},
    {"date": "2026072"}, {"date": "2026072a"}, {"method": "sparse"}, {"setting": "both"},
])
def test_build_run_id_rejects_bad_parts(kwargs):
    base = dict(method="dense", setting="pooled", n_loaded=500,
                retrieval_depth=50, date="20260720", seq=1)
    base.update(kwargs)
    with pytest.raises(RawSchemaError):
        build_retrieval_run_id(**base)


def test_corpus_fingerprints_differ_by_setting_and_order():
    paras = [_para("A"), _para("B")]
    examples = [FakeExample("q1", [_para("A")]), FakeExample("q2", [_para("B")])]
    pooled_fp = pooled_corpus_fingerprint(paras)
    per_q_fp = per_question_corpus_fingerprint(examples)
    assert SHA256_FINGERPRINT_RE.fullmatch(pooled_fp) is not None
    assert SHA256_FINGERPRINT_RE.fullmatch(per_q_fp) is not None
    assert pooled_fp != per_q_fp
    # example_ids fingerprint is order-sensitive.
    assert example_ids_fingerprint(["q1", "q2"]) != example_ids_fingerprint(["q2", "q1"])


def test_build_dense_pooled_manifest_is_valid():
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 0.9), ("t2", 0.8), ("t3", 0.7)]),
               _batch([("u1", 0.6), ("u2", 0.5), ("u3", 0.4)])]
    manifest, _ = _build_bundle("dense", "pooled", batches, ex, depth=3, corpus_size=5)
    validate_manifest(manifest)
    assert manifest["raw_schema_version"] == RETRIEVAL_RAW_SCHEMA_V1
    assert manifest["score_type"] == SCORE_TYPE_BY_METHOD["dense"]
    assert manifest["deduplication_policy"] == "exact_title_keep_first_dataset_order"
    assert manifest["tie_break_policy"] == "score_desc_then_corpus_order_asc"
    assert SHA256_HEX_RE.fullmatch(manifest["rankings_sha256"]) is not None
    assert "per_example_corpus_size" not in manifest


def test_build_dense_per_question_manifest_is_valid():
    # Variable legal source sizes 3 and 2; retrieval_depth must equal their max.
    e1, b1 = _perq_example_and_batch("q1", [("t1", 0.9), ("t2", 0.8), ("t3", 0.7)])
    e2, b2 = _perq_example_and_batch("q2", [("u1", 0.6), ("u2", 0.5)])
    manifest, _ = _build_bundle("dense", "per_question", [b1, b2], [e1, e2], depth=3)
    validate_manifest(manifest)
    assert manifest["per_example_corpus_size"] == {"q1": 3, "q2": 2}
    assert manifest["retrieval_depth"] == 3
    assert "corpus_size" not in manifest


def test_build_bm25_pooled_manifest_is_valid_including_bm25_config():
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 4.0), ("t2", 3.0)]),
               _batch([("u1", 2.0), ("u2", 1.0)])]
    manifest, _ = _build_bundle("bm25", "pooled", batches, ex, depth=2, corpus_size=5,
                                model_config=_bm25_model_config())
    validate_manifest(manifest)
    assert manifest["score_type"] == "bm25_okapi"
    # The BM25 inner-config contract is a separate method-specific provenance check.
    validate_bm25_config(manifest["model_or_retriever_config"])


def test_build_rerank_manifest_is_valid():
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 0.9), ("t2", 0.1), ("t3", -0.3)]),
               _batch([("u1", 0.7), ("u2", 0.2), ("u3", -0.5)])]
    rerank_config = {"implementation": "sentence_transformers",
                     "identifier": "cross-encoder/ms-marco", "parameters": {}}
    manifest, _ = _build_bundle("rerank", "pooled", batches, ex, depth=3, corpus_size=5,
                                model_config=rerank_config)
    validate_manifest(manifest)
    assert manifest["score_type"] == "cross_encoder_logit"
    assert manifest["parent_candidate_depth"] == manifest["retrieval_depth"]
    assert manifest["deduplication_policy"] == "none_parent_candidate_set_unchanged"


def test_build_manifest_refuses_rerank_per_question():
    with pytest.raises(RawSchemaError):
        build_raw_manifest(
            method="rerank", setting="per_question", split="validation",
            n_requested=1, n_loaded=1, retrieval_depth=3, date="20260720", seq=1,
            created_at="2026-07-20T12:00:00Z",
            model_or_retriever_config=_dense_model_config(),
            dataset_identifier="hotpotqa_distractor_v1",
            git_commit="0" * 40, command="x", rankings_sha256="d" * 64,
            per_example_corpus_size={"q1": 3},
            **_canned_fingerprints(),
        )


# ---------------------------------------------------------------------------
# U3 -- atomic bundle writer
# ---------------------------------------------------------------------------


def test_write_bundle_round_trips_from_disk(tmp_path):
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 0.9), ("t2", 0.8), ("t3", 0.7)]),
               _batch([("u1", 0.6), ("u2", 0.5), ("u3", 0.4)])]
    manifest, data = _build_bundle("dense", "pooled", batches, ex, depth=3, corpus_size=5)

    run_root = str(tmp_path / "retrieval_runs")
    bundle_dir = write_raw_bundle(run_root, manifest, data)

    assert os.path.isdir(bundle_dir)
    assert os.path.basename(bundle_dir) == manifest["retrieval_run_id"]
    # Re-read straight from disk and re-validate everything, including checksum.
    with open(os.path.join(bundle_dir, MANIFEST_FILENAME), "rb") as handle:
        disk_manifest = json.loads(handle.read().decode("utf-8"))
    with open(os.path.join(bundle_dir, RANKINGS_FILENAME), "rb") as handle:
        disk_rankings = handle.read()
    columns, rows = read_rankings_bytes(disk_rankings)
    validate_raw_bundle(columns, rows, disk_manifest)
    validate_rankings_checksum(disk_rankings, disk_manifest)
    # Only the two contract files exist in the bundle.
    assert sorted(os.listdir(bundle_dir)) == [MANIFEST_FILENAME, RANKINGS_FILENAME]


def test_write_bundle_refuses_overwrite(tmp_path):
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 0.9), ("t2", 0.8), ("t3", 0.7)]),
               _batch([("u1", 0.6), ("u2", 0.5), ("u3", 0.4)])]
    manifest, data = _build_bundle("dense", "pooled", batches, ex, depth=3, corpus_size=5)

    run_root = str(tmp_path / "retrieval_runs")
    write_raw_bundle(run_root, manifest, data)
    with pytest.raises(RawSchemaError):
        write_raw_bundle(run_root, manifest, data)


def test_write_bundle_invalid_checksum_leaves_no_formal_dir(tmp_path):
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 0.9), ("t2", 0.8), ("t3", 0.7)]),
               _batch([("u1", 0.6), ("u2", 0.5), ("u3", 0.4)])]
    manifest, data = _build_bundle("dense", "pooled", batches, ex, depth=3, corpus_size=5)
    manifest["rankings_sha256"] = "f" * 64   # deliberately wrong checksum

    run_root = str(tmp_path / "retrieval_runs")
    with pytest.raises(RawSchemaError):
        write_raw_bundle(run_root, manifest, data)

    bundle_dir = os.path.join(run_root, manifest["retrieval_run_id"])
    assert not os.path.exists(bundle_dir)
    # No leftover temp directory either (the failed write cleaned up after itself).
    leftovers = os.listdir(run_root) if os.path.isdir(run_root) else []
    assert leftovers == []


def test_write_bundle_per_question_from_disk(tmp_path):
    e1, b1 = _perq_example_and_batch("q1", [("t1", 0.9), ("t2", 0.8), ("t3", 0.7)])
    e2, b2 = _perq_example_and_batch("q2", [("u1", 0.6), ("u2", 0.5)])
    manifest, data = _build_bundle("dense", "per_question", [b1, b2], [e1, e2], depth=3)

    run_root = str(tmp_path / "retrieval_runs")
    bundle_dir = write_raw_bundle(run_root, manifest, data)
    with open(os.path.join(bundle_dir, RANKINGS_FILENAME), "rb") as handle:
        disk_rankings = handle.read()
    columns, rows = read_rankings_bytes(disk_rankings)
    validate_raw_bundle(columns, rows, manifest)


# ---------------------------------------------------------------------------
# U4 -- row builder from already-retrieved batches
# ---------------------------------------------------------------------------


def test_build_rows_shape_and_ranks():
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 0.9), ("t2", 0.8)]), _batch([("u1", 0.5)])]
    rows = build_ranking_rows_from_batches(
        ex, batches, retrieval_run_id="dense_pooled_n2_d2_20260720_r01",
        method="dense", setting="pooled",
    )
    assert len(rows) == 3
    assert set(rows[0].keys()) == set(RANKING_COLUMNS)
    assert [(r["example_id"], r["rank"], r["title"]) for r in rows] == [
        ("q1", 1, "t1"), ("q1", 2, "t2"), ("q2", 1, "u1"),
    ]
    assert all(isinstance(r["score"], float) for r in rows)


def test_build_rows_length_mismatch_raises():
    with pytest.raises(RawSchemaError):
        build_ranking_rows_from_batches(
            [FakeExample("q1")], [_batch([("t1", 0.9)]), _batch([("u1", 0.5)])],
            retrieval_run_id="dense_pooled_n1_d1_20260720_r01",
            method="dense", setting="pooled",
        )


def test_build_rows_empty():
    assert build_ranking_rows_from_batches(
        [], [], retrieval_run_id="dense_pooled_n1_d1_20260720_r01",
        method="dense", setting="pooled",
    ) == []


# ---------------------------------------------------------------------------
# End-to-end offline: writer core produces validator-clean bundles for Dense and
# BM25 in both settings (the writer-core slice of the Phase 2 exit gate; runner
# integration is the Stage 3 second slice).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method,setting,model_config", [
    ("dense", "pooled", None),
    ("dense", "per_question", None),
    ("bm25", "pooled", "bm25"),
    ("bm25", "per_question", "bm25"),
])
def test_end_to_end_bundle_passes_all_validators(tmp_path, method, setting, model_config):
    if setting == "pooled":
        ex = [FakeExample("q1"), FakeExample("q2")]
        batches = [_batch([("t1", 3.0), ("t2", 2.0), ("t3", 1.0)]),
                   _batch([("u1", 3.0), ("u2", 2.0), ("u3", 1.0)])]
        kw = {"depth": 3, "corpus_size": 5}
    else:
        e1, b1 = _perq_example_and_batch("q1", [("t1", 3.0), ("t2", 2.0), ("t3", 1.0)])
        e2, b2 = _perq_example_and_batch("q2", [("u1", 2.0), ("u2", 1.0)])
        ex = [e1, e2]
        batches = [b1, b2]
        kw = {"depth": 3}
    config = _bm25_model_config() if model_config == "bm25" else _dense_model_config()

    manifest, data = _build_bundle(method, setting, batches, ex, model_config=config, **kw)
    columns, rows = read_rankings_bytes(data)
    validate_raw_bundle(columns, rows, manifest)
    validate_rankings_checksum(data, manifest)

    bundle_dir = write_raw_bundle(str(tmp_path / "runs"), manifest, data)
    assert os.path.isdir(bundle_dir)


# ---------------------------------------------------------------------------
# Regression fixtures for the confirmed writer-core findings (each negative is
# an otherwise internally consistent complete bundle paired with a legal twin
# that differs only in the property under test).
# ---------------------------------------------------------------------------


def _single_row_pooled_bundle():
    """A minimal, fully consistent one-row pooled bundle (score 0.5) whose
    canonical bytes are easy to mutate one field at a time."""
    return _build_bundle(
        "dense", "pooled", [_batch([("t1", 0.5)])], [FakeExample("q1")],
        depth=1, corpus_size=1,
    )


def _bm25_pooled_bundle():
    """A consistent BM25 pooled bundle with the exact frozen BM25 config."""
    ex = [FakeExample("q1"), FakeExample("q2")]
    batches = [_batch([("t1", 4.0), ("t2", 3.0)]), _batch([("u1", 2.0), ("u2", 1.0)])]
    return _build_bundle("bm25", "pooled", batches, ex, depth=2, corpus_size=5,
                         model_config=_bm25_model_config())


# ---------------------------------------------------------------------------
# Finding A -- per-question size map is the INDEPENDENT source mini-corpus size,
# not the saved batch depth (so a cap-truncated ranking cannot self-certify).
# ---------------------------------------------------------------------------


def test_per_example_corpus_size_map_uses_source_not_saved_depth():
    # Source mini-corpus has three paragraphs; only two were saved in the batch.
    ex = [FakeExample("q1", [_para("t1"), _para("t2"), _para("t3")])]
    batches = [_batch([("t1", 0.9), ("t2", 0.8)])]   # capped below the source size
    # The recorded size is the source 3, never the truncated saved 2.
    assert per_example_corpus_size_map(ex, batches) == {"q1": 3}


def test_per_example_corpus_size_map_rejects_empty_source():
    with pytest.raises(RawSchemaError):
        per_example_corpus_size_map([FakeExample("q1", [])], [_batch([("t1", 0.9)])])


def test_per_example_corpus_size_map_handles_variable_sizes():
    ex = [FakeExample("q1", [_para("a"), _para("b"), _para("c")]),
          FakeExample("q2", [_para("d"), _para("e")])]
    batches = [_batch([("a", 0.9), ("b", 0.8), ("c", 0.7)]), _batch([("d", 0.5), ("e", 0.4)])]
    assert per_example_corpus_size_map(ex, batches) == {"q1": 3, "q2": 2}


def test_write_bundle_per_question_rejects_cap_truncation(tmp_path):
    # q1's source mini-corpus is 3 but only 2 ranks were saved: saved_depth (2)
    # must not equal per_example_corpus_size (3), so the bundle is invalid.
    example, batch = _perq_example_and_batch(
        "q1", [("t1", 0.9), ("t2", 0.8)],
        source_paragraphs=[_para("t1"), _para("t2"), _para("t3")],
    )
    manifest, data = _build_bundle("dense", "per_question", [batch], [example], depth=3)
    assert manifest["per_example_corpus_size"] == {"q1": 3}
    run_root = str(tmp_path / "runs")
    with pytest.raises(RawSchemaError):
        write_raw_bundle(run_root, manifest, data)
    assert not os.path.exists(os.path.join(run_root, manifest["retrieval_run_id"]))


def test_write_bundle_per_question_accepts_complete_source(tmp_path):
    # The legal twin: the full three-paragraph mini-corpus is saved in full.
    example, batch = _perq_example_and_batch("q1", [("t1", 0.9), ("t2", 0.8), ("t3", 0.7)])
    manifest, data = _build_bundle("dense", "per_question", [batch], [example], depth=3)
    assert manifest["per_example_corpus_size"] == {"q1": 3}
    assert manifest["retrieval_depth"] == 3
    bundle_dir = write_raw_bundle(str(tmp_path / "runs"), manifest, data)
    assert os.path.isdir(bundle_dir)


# ---------------------------------------------------------------------------
# Finding B -- the formal writer rejects noncanonical rankings bytes even when
# the recorded checksum matches those wrong bytes; canonical bytes are accepted.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mutate,label", [
    (lambda b: b.replace(b"\n", b"\r\n"), "crlf"),
    (lambda b: b.replace(b",0.5\n", b",0.500000\n"), "noncanonical_float"),
    (lambda b: b.replace(b",q1,1,t1,", b",q1,01,t1,"), "noncanonical_integer"),
    (lambda b: b.replace(b",t1,", b',"t1",'), "unnecessary_quoting"),
    (lambda b: b.replace(b",t1,", b",t1,extra,"), "extra_cell"),
])
def test_write_bundle_rejects_noncanonical_rankings_bytes(tmp_path, mutate, label):
    manifest, data = _single_row_pooled_bundle()
    bad = mutate(data)
    assert bad != data
    # The checksum is recomputed over the WRONG bytes, so only the canonical-byte
    # gate can reject them.
    manifest["rankings_sha256"] = compute_sha256(bad)
    run_root = str(tmp_path / "runs")
    with pytest.raises(RawSchemaError):
        write_raw_bundle(run_root, manifest, bad)
    assert not os.path.exists(os.path.join(run_root, manifest["retrieval_run_id"]))
    assert (os.listdir(run_root) if os.path.isdir(run_root) else []) == []


def test_write_bundle_rejects_physically_reordered_rankings(tmp_path):
    ex = [FakeExample("q1"), FakeExample("q2")]
    manifest, data = _build_bundle(
        "dense", "pooled", [_batch([("t1", 0.9)]), _batch([("u1", 0.8)])], ex,
        depth=1, corpus_size=1,
    )
    header, row_q1, row_q2, _tail = data.split(b"\n")
    reordered = b"\n".join([header, row_q2, row_q1]) + b"\n"   # q2 block before q1
    assert reordered != data
    manifest["rankings_sha256"] = compute_sha256(reordered)
    run_root = str(tmp_path / "runs")
    with pytest.raises(RawSchemaError):
        write_raw_bundle(run_root, manifest, reordered)
    assert not os.path.exists(os.path.join(run_root, manifest["retrieval_run_id"]))


def test_write_bundle_accepts_canonical_rankings_bytes(tmp_path):
    # Legal twin for the noncanonical cases above: canonical LF/`0.5` bytes.
    manifest, data = _single_row_pooled_bundle()
    assert b"\r" not in data
    bundle_dir = write_raw_bundle(str(tmp_path / "runs"), manifest, data)
    assert os.path.isdir(bundle_dir)


# ---------------------------------------------------------------------------
# Finding C -- there is no public validation bypass; every supported call
# signature validates before the formal directory can appear.
# ---------------------------------------------------------------------------


def test_write_bundle_has_no_validation_bypass_parameter():
    params = inspect.signature(write_raw_bundle).parameters
    assert "validate" not in params
    # Only the three positional inputs remain (run_root, manifest, rankings_bytes).
    assert list(params) == ["run_root", "manifest", "rankings_bytes"]


def test_write_bundle_wrong_checksum_cannot_be_published(tmp_path):
    manifest, data = _single_row_pooled_bundle()
    manifest["rankings_sha256"] = "f" * 64   # structurally valid but wrong checksum
    run_root = str(tmp_path / "runs")
    with pytest.raises(RawSchemaError):
        write_raw_bundle(run_root, manifest, data)
    assert not os.path.exists(os.path.join(run_root, manifest["retrieval_run_id"]))
    # The same bundle with the correct checksum publishes through the one path.
    good_manifest, good_data = _single_row_pooled_bundle()
    bundle_dir = write_raw_bundle(str(tmp_path / "ok"), good_manifest, good_data)
    assert os.path.isdir(bundle_dir)


# ---------------------------------------------------------------------------
# Finding D -- the formal writer composes the method-specific BM25 config gate.
# ---------------------------------------------------------------------------


def _bad_bm25_configs():
    def base():
        return _bm25_model_config()
    configs = {}
    c = base(); c["implementation"] = "sentence_transformers"; configs["wrong_implementation"] = c
    c = base(); c["identifier"] = "all-MiniLM-L6-v2"; configs["wrong_identifier"] = c
    configs["dense_shaped"] = {"implementation": "sentence_transformers",
                               "identifier": "wrong", "parameters": {}}
    c = base(); del c["parameters"]["k1"]; configs["missing_param_key"] = c
    c = base(); c["parameters"]["extra"] = 1; configs["extra_param_key"] = c
    c = base(); c["parameters"]["tokenizer"] = "spacy"; configs["wrong_tokenizer"] = c
    c = base(); c["parameters"]["stopword_policy"] = "english"; configs["wrong_stopword_policy"] = c
    c = base(); c["parameters"]["lowercase"] = "yes"; configs["wrong_lowercase_type"] = c
    return configs


@pytest.mark.parametrize("config", list(_bad_bm25_configs().values()),
                         ids=list(_bad_bm25_configs().keys()))
def test_write_bundle_bm25_rejects_wrong_config(tmp_path, config):
    manifest, data = _bm25_pooled_bundle()
    manifest["model_or_retriever_config"] = config   # rankings/checksum unaffected
    run_root = str(tmp_path / "runs")
    with pytest.raises(RawSchemaError):
        write_raw_bundle(run_root, manifest, data)
    assert not os.path.exists(os.path.join(run_root, manifest["retrieval_run_id"]))


def test_write_bundle_bm25_rejects_non_finite_param(tmp_path):
    manifest, data = _bm25_pooled_bundle()
    manifest["model_or_retriever_config"]["parameters"]["k1"] = float("inf")
    run_root = str(tmp_path / "runs")
    # A non-finite config number is refused before publication (canonical manifest
    # serialization uses allow_nan=False; the BM25 gate would also reject it).
    with pytest.raises((RawSchemaError, ValueError)):
        write_raw_bundle(run_root, manifest, data)
    assert not os.path.exists(os.path.join(run_root, manifest["retrieval_run_id"]))


def test_write_bundle_bm25_accepts_exact_config(tmp_path):
    # Legal twin: the exact seven-key frozen BM25 config publishes.
    manifest, data = _bm25_pooled_bundle()
    bundle_dir = write_raw_bundle(str(tmp_path / "runs"), manifest, data)
    assert os.path.isdir(bundle_dir)


# ---------------------------------------------------------------------------
# Finding E -- score is a finite native real number; booleans and strings are
# never coerced, genuine float / NumPy scalars are accepted unchanged.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [True, False, "0.5", "abc", None, [0.5]])
def test_build_rows_rejects_non_real_score(bad):
    with pytest.raises(RawSchemaError):
        build_ranking_rows_from_batches(
            [FakeExample("q1")], [[(_para("t1"), bad)]],
            retrieval_run_id="dense_pooled_n1_d1_20260720_r01",
            method="dense", setting="pooled",
        )


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_build_rows_rejects_non_finite_score(bad):
    with pytest.raises(RawSchemaError):
        build_ranking_rows_from_batches(
            [FakeExample("q1")], [[(_para("t1"), bad)]],
            retrieval_run_id="dense_pooled_n1_d1_20260720_r01",
            method="dense", setting="pooled",
        )


@pytest.mark.parametrize("score", [0.5, -2.5, np.float64(0.5), np.float32(0.25), 3])
def test_build_rows_accepts_real_numeric_and_preserves_value(score):
    rows = build_ranking_rows_from_batches(
        [FakeExample("q1")], [[(_para("t1"), score)]],
        retrieval_run_id="dense_pooled_n1_d1_20260720_r01",
        method="dense", setting="pooled",
    )
    assert type(rows[0]["score"]) is float          # narrowed to a Python float
    assert rows[0]["score"] == float(score)          # genuine input value preserved


# ---------------------------------------------------------------------------
# Finding F -- the canonical run-ID builder cannot mint an impossible date.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("date", ["20260230", "20260231", "20260000",
                                  "20261301", "20260229", "20260431"])
def test_build_run_id_rejects_impossible_dates(date):
    with pytest.raises(RawSchemaError):
        build_retrieval_run_id("dense", "pooled", 500, 50, date, 1)


@pytest.mark.parametrize("date", ["20260228", "20240229", "20261231", "20260101"])
def test_build_run_id_accepts_real_dates_including_leap_day(date):
    run_id = build_retrieval_run_id("dense", "pooled", 500, 50, date, 1)
    # The builder's output is accepted by the single canonical validator.
    validate_retrieval_run_id(run_id, expected_method="dense", expected_setting="pooled",
                              expected_n=500, expected_depth=50)


def test_build_run_id_retains_sequence_bounds():
    assert build_retrieval_run_id("dense", "pooled", 500, 50, "20260720", 1).endswith("_r01")
    assert build_retrieval_run_id("dense", "pooled", 500, 50, "20260720", 99).endswith("_r99")


# ---------------------------------------------------------------------------
# Finding G -- fingerprint builders fail closed on non-string preimage fields.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ids", [[1], [None], [""], ["q1", 2], [True]])
def test_example_ids_fingerprint_rejects_non_string(ids):
    with pytest.raises(RawSchemaError):
        example_ids_fingerprint(ids)


def test_example_ids_fingerprint_accepts_string_control():
    fp = example_ids_fingerprint(["q1", "q2"])
    assert SHA256_FINGERPRINT_RE.fullmatch(fp) is not None


@pytest.mark.parametrize("title,text", [(1, "x"), ("t", 2), (None, "x"), (1.0, "x")])
def test_pooled_corpus_fingerprint_rejects_non_string_fields(title, text):
    with pytest.raises(RawSchemaError):
        pooled_corpus_fingerprint([Paragraph(title=title, text=text)])


def test_pooled_corpus_fingerprint_accepts_string_control():
    fp = pooled_corpus_fingerprint([Paragraph(title="A", text="x")])
    assert SHA256_FINGERPRINT_RE.fullmatch(fp) is not None


@pytest.mark.parametrize("example_id,title", [(1, "x"), ("q1", 2), ("", "x")])
def test_per_question_corpus_fingerprint_rejects_non_string(example_id, title):
    ex = [FakeExample(example_id, [Paragraph(title=title, text="x")])]
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint(ex)


def test_per_question_corpus_fingerprint_accepts_string_control():
    ex = [FakeExample("q1", [Paragraph(title="A", text="x")])]
    fp = per_question_corpus_fingerprint(ex)
    assert SHA256_FINGERPRINT_RE.fullmatch(fp) is not None


def test_dataset_fingerprint_rejects_non_string_object_key():
    with pytest.raises(RawSchemaError):
        dataset_fingerprint([{1: "x"}])   # a non-string JSON object key


def test_dataset_fingerprint_accepts_string_key_control():
    fp = dataset_fingerprint([{"_id": "q1", "question": "q?"}])
    assert SHA256_FINGERPRINT_RE.fullmatch(fp) is not None


# ---------------------------------------------------------------------------
# Finding H -- fingerprint builders fail closed on the outer collection/record
# shape and on empty formal collections (not just scalar record fields).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("builder", [dataset_fingerprint, example_ids_fingerprint,
                                     pooled_corpus_fingerprint, per_question_corpus_fingerprint])
def test_fingerprint_builders_reject_scalar_non_iterable(builder):
    with pytest.raises(RawSchemaError):
        builder(5)


@pytest.mark.parametrize("builder", [dataset_fingerprint, example_ids_fingerprint,
                                     pooled_corpus_fingerprint, per_question_corpus_fingerprint])
def test_fingerprint_builders_reject_empty_formal_collection(builder):
    with pytest.raises(RawSchemaError):
        builder([])


def test_fingerprint_builders_accept_single_item_collections():
    # Legal one-item twins for each empty-collection rejection above.
    assert SHA256_FINGERPRINT_RE.fullmatch(dataset_fingerprint([{"_id": "q1"}])) is not None
    assert SHA256_FINGERPRINT_RE.fullmatch(example_ids_fingerprint(["q1"])) is not None
    assert SHA256_FINGERPRINT_RE.fullmatch(pooled_corpus_fingerprint([_para("A")])) is not None
    assert SHA256_FINGERPRINT_RE.fullmatch(
        per_question_corpus_fingerprint([FakeExample("q1", [_para("A")])])) is not None


@pytest.mark.parametrize("bad", [[1], [None], ["q1"], [[1, 2]]])
def test_dataset_fingerprint_rejects_non_record_element(bad):
    # A dataset record is a JSON object; a scalar/string/list element is not.
    with pytest.raises(RawSchemaError):
        dataset_fingerprint(bad)


def test_dataset_fingerprint_rejects_bare_mapping_as_collection():
    # A single mapping would be iterated as its keys (["_id"]) -- reject it.
    with pytest.raises(RawSchemaError):
        dataset_fingerprint({"_id": "q1"})


def test_dataset_fingerprint_accepts_record_array_control():
    assert SHA256_FINGERPRINT_RE.fullmatch(dataset_fingerprint([{"_id": "q1"}])) is not None


@pytest.mark.parametrize("bad", ["q1", b"q1", bytearray(b"q1")])
def test_example_ids_fingerprint_rejects_bare_string_or_bytes(bad):
    # A bare string/bytes would be hashed as its individual characters/bytes.
    with pytest.raises(RawSchemaError):
        example_ids_fingerprint(bad)


def test_example_ids_fingerprint_no_longer_aliases_character_array():
    with pytest.raises(RawSchemaError):
        example_ids_fingerprint("q1")       # rejected, not split into ["q", "1"]
    # The genuine two-character list and singleton list are distinct valid inputs.
    assert example_ids_fingerprint(["q", "1"]) != example_ids_fingerprint(["q1"])


def test_fingerprint_builders_accept_generators_and_preserve_order():
    # Legitimate ordered generators are supported (consumed once).
    assert example_ids_fingerprint(x for x in ["q1", "q2"]) == \
        example_ids_fingerprint(["q1", "q2"])
    assert dataset_fingerprint(r for r in [{"_id": "q1"}, {"_id": "q2"}]) == \
        dataset_fingerprint([{"_id": "q1"}, {"_id": "q2"}])
    # Order sensitivity is retained.
    assert example_ids_fingerprint(["q1", "q2"]) != example_ids_fingerprint(["q2", "q1"])


def test_write_bundle_with_all_real_u2_fingerprints_publishes(tmp_path):
    # At least one complete positive path drives every real U2 fingerprint builder
    # into U3 publication (not the canned format-valid strings other tests use).
    paragraphs = [_para("t1"), _para("t2")]
    ex = [FakeExample("q1", paragraphs)]
    batches = [[(paragraphs[0], 0.9), (paragraphs[1], 0.8)]]
    run_id = build_retrieval_run_id("dense", "pooled", 1, 2, "20260720", 1)
    rows = build_ranking_rows_from_batches(ex, batches, retrieval_run_id=run_id,
                                           method="dense", setting="pooled")
    data = rankings_csv_bytes(rows)
    manifest = build_raw_manifest(
        method="dense", setting="pooled", split="validation", n_requested=1, n_loaded=1,
        retrieval_depth=2, date="20260720", seq=1, created_at="2026-07-20T12:00:00Z",
        model_or_retriever_config=_dense_model_config(),
        dataset_identifier="hotpotqa_distractor_v1",
        dataset_fingerprint=dataset_fingerprint([{"_id": "q1", "question": "q?"}]),
        example_ids_fingerprint=example_ids_fingerprint(["q1"]),
        corpus_fingerprint=pooled_corpus_fingerprint(paragraphs),
        git_commit="0" * 40, command="python scripts/run_x.py --setting pooled",
        rankings_sha256=compute_sha256(data), corpus_size=2,
    )
    bundle_dir = write_raw_bundle(str(tmp_path / "runs"), manifest, data)
    assert os.path.isdir(bundle_dir)


# ---------------------------------------------------------------------------
# Finding I -- every ordered fingerprint level rejects an UNORDERED collection
# (set / frozenset / mapping key view) that cannot carry the required selected/
# source order, and the per-question nested mini-corpus must itself be ordered
# and non-empty. Each rejection is paired with an ordered legal twin (list /
# tuple / deque / generator) that must still be accepted and order-sensitive.
# ---------------------------------------------------------------------------


class _HashableParagraph:
    """A hashable, duck-typed paragraph (default identity hash/eq) so that a
    ``set``/``frozenset`` of paragraphs is even constructible.

    The real ``Paragraph`` dataclass is unhashable (``@dataclass`` sets
    ``__hash__ = None``), so the shallow ordered-collection guard can only be
    probed with a hashable stand-in -- exactly what the review used for its set
    counterexamples. It exposes ``.title`` / ``.text`` like a real paragraph."""

    def __init__(self, title, text=None):
        self.title = title
        self.text = text if text is not None else f"text of {title}"


def _unordered_id_collections():
    """The three unordered example-ID collections the review flagged. Each is a
    ``collections.abc.Set`` and iterates in process-randomized order."""
    return {
        "set": {"q1", "q2"},
        "frozenset": frozenset(["q1", "q2"]),
        "dict_keys": {"q1": 1, "q2": 2}.keys(),
    }


@pytest.mark.parametrize("bad", list(_unordered_id_collections().values()),
                         ids=list(_unordered_id_collections().keys()))
def test_example_ids_fingerprint_rejects_unordered_collection(bad):
    # A set/frozenset/key-view cannot carry the selected dataset order the
    # fingerprint hashes, so it is rejected before hashing (never split/reordered).
    with pytest.raises(RawSchemaError):
        example_ids_fingerprint(bad)


def test_example_ids_fingerprint_accepts_ordered_twins_equal_and_order_sensitive():
    ref = example_ids_fingerprint(["q1", "q2"])
    assert SHA256_FINGERPRINT_RE.fullmatch(ref) is not None
    # Every ordered container form hashes identically to the canonical list.
    assert example_ids_fingerprint(("q1", "q2")) == ref
    assert example_ids_fingerprint(deque(["q1", "q2"])) == ref
    assert example_ids_fingerprint(x for x in ["q1", "q2"]) == ref
    # Order remains authoritative: a reordered list is a different fingerprint.
    assert example_ids_fingerprint(["q2", "q1"]) != ref


def test_dataset_fingerprint_rejects_unordered_collection():
    # The dataset preimage is the selected-order array of raw records; a set of
    # them (strings here, since dict records are unhashable) is unordered.
    with pytest.raises(RawSchemaError):
        dataset_fingerprint({"q1", "q2"})
    with pytest.raises(RawSchemaError):
        dataset_fingerprint(frozenset(["q1", "q2"]))


def test_pooled_corpus_fingerprint_rejects_unordered_collection():
    p_a = _HashableParagraph("A")
    p_b = _HashableParagraph("B")
    with pytest.raises(RawSchemaError):
        pooled_corpus_fingerprint({p_a, p_b})
    with pytest.raises(RawSchemaError):
        pooled_corpus_fingerprint(frozenset([p_a, p_b]))


def test_pooled_corpus_fingerprint_accepts_ordered_twins():
    ref = pooled_corpus_fingerprint([_para("A"), _para("B")])
    assert SHA256_FINGERPRINT_RE.fullmatch(ref) is not None
    assert pooled_corpus_fingerprint((_para("A"), _para("B"))) == ref
    assert pooled_corpus_fingerprint(deque([_para("A"), _para("B")])) == ref
    # Corpus input order is authoritative.
    assert pooled_corpus_fingerprint([_para("B"), _para("A")]) != ref


def test_per_question_corpus_fingerprint_rejects_unordered_outer_collection():
    e1 = FakeExample("q1", [_para("A")])
    e2 = FakeExample("q2", [_para("B")])
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint({e1, e2})
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint(frozenset([e1, e2]))


def test_per_question_corpus_fingerprint_rejects_unordered_nested_paragraphs():
    p_a = _HashableParagraph("A")
    p_b = _HashableParagraph("B")
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint([FakeExample("q1", {p_a, p_b})])
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint([FakeExample("q1", frozenset([p_a, p_b]))])


def test_per_question_corpus_fingerprint_rejects_empty_nested_mini_corpus():
    # A non-empty outer examples array containing an empty per-example corpus:
    # every formal mini-corpus must be positive.
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint([FakeExample("q1", [])])
    # Even when a legal example precedes it, the empty nested corpus still fails.
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint([FakeExample("q1", [_para("A")]),
                                         FakeExample("q2", [])])


def test_per_question_corpus_fingerprint_rejects_nested_string_or_mapping():
    # The nested mini-corpus routes through the same guard, so a bare string
    # (hashed as characters) or a mapping (hashed as keys) also fails closed.
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint([FakeExample("q1", "AB")])
    with pytest.raises(RawSchemaError):
        per_question_corpus_fingerprint([FakeExample("q1", {"A": 1})])


def test_per_question_corpus_fingerprint_accepts_ordered_nested_twins():
    # Ordered nested container forms all hash identically; a one-paragraph
    # mini-corpus is the legal twin of the empty-corpus rejection above.
    ref = per_question_corpus_fingerprint([FakeExample("q1", [_para("A"), _para("B")])])
    assert SHA256_FINGERPRINT_RE.fullmatch(ref) is not None
    assert per_question_corpus_fingerprint(
        [FakeExample("q1", (_para("A"), _para("B")))]) == ref
    assert per_question_corpus_fingerprint(
        [FakeExample("q1", deque([_para("A"), _para("B")]))]) == ref
    # A single-paragraph mini-corpus (positive, non-empty) is accepted.
    assert SHA256_FINGERPRINT_RE.fullmatch(
        per_question_corpus_fingerprint([FakeExample("q1", [_para("A")])])) is not None
    # Nested paragraph source-context order is authoritative.
    assert per_question_corpus_fingerprint(
        [FakeExample("q1", [_para("B"), _para("A")])]) != ref


def test_per_question_corpus_fingerprint_accepts_ordered_outer_twins():
    ref = per_question_corpus_fingerprint([FakeExample("q1", [_para("A")]),
                                           FakeExample("q2", [_para("B")])])
    assert SHA256_FINGERPRINT_RE.fullmatch(ref) is not None
    assert per_question_corpus_fingerprint(
        (FakeExample("q1", [_para("A")]), FakeExample("q2", [_para("B")]))) == ref
    assert per_question_corpus_fingerprint(
        e for e in [FakeExample("q1", [_para("A")]),
                    FakeExample("q2", [_para("B")])]) == ref
    # Outer selected order is authoritative.
    assert per_question_corpus_fingerprint([FakeExample("q2", [_para("B")]),
                                            FakeExample("q1", [_para("A")])]) != ref


def test_unordered_fingerprint_preimage_cannot_mint_publishable_digest():
    # The six exact review counterexamples: each U2 builder raises before hashing,
    # so an unordered/empty preimage can never mint an opaque sha256:<hex> to feed
    # a manifest and reach write_raw_bundle. The manifest validator sees only the
    # digest and could not recover such a preimage, so U2 is the only layer able
    # to fail closed here.
    p_a = _HashableParagraph("A")
    p_b = _HashableParagraph("B")
    bad_constructors = [
        lambda: example_ids_fingerprint({"q1", "q2"}),
        lambda: example_ids_fingerprint(frozenset(["q1", "q2"])),
        lambda: example_ids_fingerprint({"q1": 1, "q2": 2}.keys()),
        lambda: pooled_corpus_fingerprint({p_a, p_b}),
        lambda: per_question_corpus_fingerprint([FakeExample("q1", {p_a, p_b})]),
        lambda: per_question_corpus_fingerprint([FakeExample("q1", [])]),
    ]
    for build in bad_constructors:
        with pytest.raises(RawSchemaError):
            build()


def test_write_bundle_per_question_with_real_corpus_fingerprint_publishes(tmp_path):
    # The legal ordered/non-empty per-question path drives the real
    # per_question_corpus_fingerprint (ordered list mini-corpora) through the
    # tightened guard into a published bundle.
    e1, b1 = _perq_example_and_batch("q1", [("t1", 0.9), ("t2", 0.8)])
    e2, b2 = _perq_example_and_batch("q2", [("u1", 0.6)])
    examples = [e1, e2]
    batches = [b1, b2]
    run_id = build_retrieval_run_id("dense", "per_question", 2, 2, "20260720", 1)
    rows = build_ranking_rows_from_batches(examples, batches, retrieval_run_id=run_id,
                                           method="dense", setting="per_question")
    data = rankings_csv_bytes(rows)
    manifest = build_raw_manifest(
        method="dense", setting="per_question", split="validation", n_requested=2,
        n_loaded=2, retrieval_depth=2, date="20260720", seq=1,
        created_at="2026-07-20T12:00:00Z",
        model_or_retriever_config=_dense_model_config(),
        dataset_identifier="hotpotqa_distractor_v1",
        dataset_fingerprint=dataset_fingerprint([{"_id": "q1"}, {"_id": "q2"}]),
        example_ids_fingerprint=example_ids_fingerprint(["q1", "q2"]),
        corpus_fingerprint=per_question_corpus_fingerprint(examples),
        git_commit="0" * 40, command="python scripts/run_x.py --setting per_question",
        rankings_sha256=compute_sha256(data),
        per_example_corpus_size=per_example_corpus_size_map(examples, batches),
    )
    bundle_dir = write_raw_bundle(str(tmp_path / "runs"), manifest, data)
    assert os.path.isdir(bundle_dir)
