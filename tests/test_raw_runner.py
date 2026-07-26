"""
test_raw_runner.py

Synthetic, fully offline smoke tests for the RAW retrieval runner / CLI /
migration-audit layer (:mod:`src.raw_runner`, Stage 3 slice 2 / U5). Every test
drives a FAKE retriever: Dense uses a tiny deterministic bag-of-words encoder
injected into the real ``DenseRetriever`` (no model download), and BM25 uses the
real ``BM25Okapi`` over a handful of in-memory paragraphs. No network, no model,
no formal run bundle outside pytest's ``tmp_path``.

They exercise the runner half of Stage 3 on top of the accepted, frozen writer
core: single-pass batch production for Dense/BM25 in both settings, the atomic
refuse-overwrite bundle publication (validated on disk by the writer), the
``--setting both`` CLI path (two bundles, both run IDs reported), and the
migration-audit title-order parity comparison against a legacy
``retrieved_titles`` list. They never assert a metric value -- the raw layer has
none -- and they prove no second retrieval and no heavy backend import.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import shlex
import shutil
import subprocess
import types
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from src.data_loader import Paragraph
from src.dense_retriever import DenseRetriever
from src.retrievers import BM25Retriever
from src.results_schema import TITLE_SEPARATOR
from src.raw_schema import (
    SCORE_TYPE_BY_METHOD,
    RawSchemaError,
    validate_bm25_config,
    validate_raw_bundle,
    validate_rankings_checksum,
)
from src.raw_writer import (
    MANIFEST_FILENAME,
    RANKINGS_FILENAME,
    dataset_fingerprint,
    read_rankings_bytes,
)
from src import raw_runner
from src.raw_runner import (
    RawRunResult,
    TitleMismatch,
    bm25_model_config,
    build_legacy_audit_view_rows,
    default_model_config,
    default_retriever_factory,
    dense_model_config,
    legacy_titles_by_example,
    main,
    run_one_setting,
    title_parity_report,
    titles_by_example_from_rows,
)


# ---------------------------------------------------------------------------
# Fakes (a tiny bag-of-words encoder + duck-typed example; the runner only
# needs .example_id / .question / .paragraphs on an example and a retriever
# exposing .retrieve / optionally .retrieve_many)
# ---------------------------------------------------------------------------

VOCAB = ["cat", "dog", "fish", "bird", "tree", "sky", "sea", "sun"]


def fake_encode(texts):
    """Deterministic offline encoder: bag-of-words counts over a fixed vocab, so
    DenseRetriever needs no model. Shared-word texts score higher; this never
    downloads or loads sentence-transformers."""
    return np.asarray(
        [[float(text.lower().split().count(word)) for word in VOCAB] for text in texts],
        dtype=np.float32,
    )


def _para(title, text):
    return Paragraph(title=title, text=text)


class FakeExample:
    def __init__(self, example_id, question, paragraphs):
        self.example_id = example_id
        self.question = question
        self.paragraphs = paragraphs


def _examples():
    """Two questions whose paragraphs share the title 'A' (so pooled dedup keeps
    the first occurrence): pooled corpus = [A, B, C, D, E, F] (6 distinct)."""
    return [
        FakeExample("q1", "cat dog", [
            _para("A", "cat cat dog"),
            _para("B", "dog bird"),
            _para("C", "fish sea"),
            _para("D", "tree sky"),
        ]),
        FakeExample("q2", "fish sea", [
            _para("A", "cat cat dog"),   # duplicate title -> dedup keeps first
            _para("E", "fish fish sea"),
            _para("F", "sun sky"),
        ]),
    ]


def _raw_records(examples):
    """Minimal JSON-compatible raw dataset records for dataset_fingerprint."""
    return [{"_id": ex.example_id, "question": ex.question} for ex in examples]


def _dense_factory():
    return lambda paragraphs: DenseRetriever(paragraphs, encoder=fake_encode)


def _bm25_factory():
    return lambda paragraphs: BM25Retriever(paragraphs)


def _provenance(**over):
    """Common fixed provenance kwargs for run_one_setting."""
    kwargs = dict(
        dataset_identifier="hotpotqa_distractor_v1",
        split="validation",
        date="20260720",
        seq=1,
        created_at="2026-07-20T12:00:00Z",
        git_commit="0" * 40,
        command="python scripts/run_raw_retrieval.py --method x",
        pooled_depth=3,
    )
    kwargs.update(over)
    return kwargs


def _run(method, setting, run_root, *, model_config=None, **over):
    examples = _examples()
    config = model_config or (bm25_model_config() if method == "bm25" else dense_model_config())
    factory = _bm25_factory() if method == "bm25" else _dense_factory()
    return run_one_setting(
        method=method, setting=setting, examples=examples,
        raw_records=_raw_records(examples), make_retriever=factory, run_root=run_root,
        model_or_retriever_config=config, **_provenance(**over),
    )


def _validate_bundle_on_disk(bundle_dir):
    with open(os.path.join(bundle_dir, MANIFEST_FILENAME), "rb") as handle:
        manifest = json.loads(handle.read().decode("utf-8"))
    with open(os.path.join(bundle_dir, RANKINGS_FILENAME), "rb") as handle:
        data = handle.read()
    columns, rows = read_rankings_bytes(data)
    validate_raw_bundle(columns, rows, manifest)
    validate_rankings_checksum(data, manifest)
    return manifest, rows


# ---------------------------------------------------------------------------
# End-to-end: Dense/BM25 x pooled/per_question publish validator-clean bundles
# from a single retrieval pass.
# ---------------------------------------------------------------------------


def test_dense_pooled_publishes_valid_bundle(tmp_path):
    result = _run("dense", "pooled", str(tmp_path / "runs"))
    assert isinstance(result, RawRunResult)
    assert os.path.isdir(result.bundle_dir)
    assert sorted(os.listdir(result.bundle_dir)) == [MANIFEST_FILENAME, RANKINGS_FILENAME]
    manifest, rows = _validate_bundle_on_disk(result.bundle_dir)
    assert manifest["method"] == "dense" and manifest["setting"] == "pooled"
    assert manifest["score_type"] == SCORE_TYPE_BY_METHOD["dense"]
    assert manifest["corpus_size"] == 6
    assert manifest["retrieval_depth"] == 3
    assert "per_example_corpus_size" not in manifest
    # 2 examples x min(depth=3, corpus=6) = 6 rows.
    assert len(rows) == 6
    assert result.run_id == "dense_pooled_n2_d3_20260720_r01"


def test_dense_per_question_publishes_valid_bundle(tmp_path):
    result = _run("dense", "per_question", str(tmp_path / "runs"))
    manifest, rows = _validate_bundle_on_disk(result.bundle_dir)
    assert manifest["setting"] == "per_question"
    assert manifest["per_example_corpus_size"] == {"q1": 4, "q2": 3}
    assert manifest["retrieval_depth"] == 4   # max mini-corpus size
    assert "corpus_size" not in manifest
    # complete mini-corpora: 4 + 3 rows.
    assert len(rows) == 7
    assert result.run_id == "dense_per_question_n2_d4_20260720_r01"


def test_bm25_pooled_publishes_valid_bundle(tmp_path):
    result = _run("bm25", "pooled", str(tmp_path / "runs"))
    manifest, rows = _validate_bundle_on_disk(result.bundle_dir)
    assert manifest["method"] == "bm25"
    assert manifest["score_type"] == SCORE_TYPE_BY_METHOD["bm25"]
    # The writer's BM25 provenance gate accepted this exact frozen config.
    validate_bm25_config(manifest["model_or_retriever_config"])
    assert len(rows) == 6
    assert result.run_id == "bm25_pooled_n2_d3_20260720_r01"


def test_bm25_per_question_publishes_valid_bundle(tmp_path):
    result = _run("bm25", "per_question", str(tmp_path / "runs"))
    manifest, rows = _validate_bundle_on_disk(result.bundle_dir)
    assert manifest["setting"] == "per_question"
    assert manifest["per_example_corpus_size"] == {"q1": 4, "q2": 3}
    validate_bm25_config(manifest["model_or_retriever_config"])
    assert len(rows) == 7
    assert result.run_id == "bm25_per_question_n2_d4_20260720_r01"


# ---------------------------------------------------------------------------
# Single retrieval pass -- the runner never re-retrieves for export.
# ---------------------------------------------------------------------------


class CountingRetriever:
    """Wraps a real retriever and counts each retrieval call so a test can prove
    there is no second retrieval pass for export."""

    def __init__(self, inner):
        self.inner = inner
        self.retrieve_calls = 0
        self.retrieve_many_calls = 0

    def retrieve(self, query, top_k=10):
        self.retrieve_calls += 1
        return self.inner.retrieve(query, top_k=top_k)

    def retrieve_many(self, queries, top_k=10):
        self.retrieve_many_calls += 1
        return self.inner.retrieve_many(queries, top_k=top_k)


def test_pooled_dense_retrieves_once_no_second_pass(tmp_path):
    created = []

    def factory(paragraphs):
        retriever = CountingRetriever(DenseRetriever(paragraphs, encoder=fake_encode))
        created.append(retriever)
        return retriever

    examples = _examples()
    run_one_setting(
        method="dense", setting="pooled", examples=examples,
        raw_records=_raw_records(examples), make_retriever=factory,
        run_root=str(tmp_path / "runs"), model_or_retriever_config=dense_model_config(),
        **_provenance(),
    )
    # Exactly one shared pooled index, one batched retrieval, no per-query calls,
    # and no second pass for export.
    assert len(created) == 1
    assert created[0].retrieve_many_calls == 1
    assert created[0].retrieve_calls == 0


def test_per_question_retrieves_once_per_example(tmp_path):
    created = []

    def factory(paragraphs):
        retriever = CountingRetriever(DenseRetriever(paragraphs, encoder=fake_encode))
        created.append(retriever)
        return retriever

    examples = _examples()
    run_one_setting(
        method="dense", setting="per_question", examples=examples,
        raw_records=_raw_records(examples), make_retriever=factory,
        run_root=str(tmp_path / "runs"), model_or_retriever_config=dense_model_config(),
        **_provenance(),
    )
    # One index per example, each queried exactly once, never batched or re-run.
    assert len(created) == 2
    assert all(r.retrieve_calls == 1 and r.retrieve_many_calls == 0 for r in created)


# ---------------------------------------------------------------------------
# Refuse-overwrite (inherited from the writer's write-once collision policy).
# ---------------------------------------------------------------------------


def test_run_one_setting_refuses_overwrite(tmp_path):
    run_root = str(tmp_path / "runs")
    _run("dense", "pooled", run_root)
    with pytest.raises(RawSchemaError):
        _run("dense", "pooled", run_root)   # same run-id directory already exists


# ---------------------------------------------------------------------------
# CLI: --setting both publishes two independent bundles and reports both IDs;
# every external dependency is injected so the CLI stays offline.
# ---------------------------------------------------------------------------


def _fixed_now():
    return datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)


def test_main_setting_both_publishes_two_bundles(tmp_path, capsys):
    examples = _examples()
    raw_records = _raw_records(examples)
    run_root = str(tmp_path / "runs")

    code = main(
        ["--method", "dense", "--setting", "both", "--run-root", run_root,
         "--depth", "3", "--split", "validation"],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=lambda split, n: (raw_records, examples),
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now,
        git_commit="0" * 40,
    )
    assert code == 0
    pooled_dir = os.path.join(run_root, "dense_pooled_n2_d3_20260720_r01")
    per_q_dir = os.path.join(run_root, "dense_per_question_n2_d4_20260720_r01")
    assert os.path.isdir(pooled_dir) and os.path.isdir(per_q_dir)
    _validate_bundle_on_disk(pooled_dir)
    _validate_bundle_on_disk(per_q_dir)
    out = capsys.readouterr().out
    assert "dense_pooled_n2_d3_20260720_r01" in out
    assert "dense_per_question_n2_d4_20260720_r01" in out


def test_main_bm25_both_publishes_two_bundles(tmp_path):
    examples = _examples()
    raw_records = _raw_records(examples)
    run_root = str(tmp_path / "runs")

    code = main(
        ["--method", "bm25", "--setting", "both", "--run-root", run_root, "--depth", "3"],
        make_retriever_factory=lambda method: _bm25_factory(),
        load_dataset=lambda split, n: (raw_records, examples),
        model_config_for=lambda method: bm25_model_config(),
        now=_fixed_now,
        git_commit="0" * 40,
    )
    assert code == 0
    assert os.path.isdir(os.path.join(run_root, "bm25_pooled_n2_d3_20260720_r01"))
    assert os.path.isdir(os.path.join(run_root, "bm25_per_question_n2_d4_20260720_r01"))


# ---------------------------------------------------------------------------
# Migration-audit: title-order parity against legacy retrieved_titles.
# ---------------------------------------------------------------------------


def test_titles_by_example_from_rows_orders_by_rank():
    rows = [
        {"example_id": "q1", "rank": 2, "title": "B"},
        {"example_id": "q1", "rank": 1, "title": "A"},
        {"example_id": "q2", "rank": 1, "title": "C"},
    ]
    assert titles_by_example_from_rows(rows) == {"q1": ["A", "B"], "q2": ["C"]}


def test_legacy_titles_by_example_filters_method_setting_and_splits():
    legacy = [
        {"method": "dense", "setting": "pooled", "example_id": "q1",
         "retrieved_titles": TITLE_SEPARATOR.join(["A", "B", "C"])},
        {"method": "bm25", "setting": "pooled", "example_id": "q1",
         "retrieved_titles": TITLE_SEPARATOR.join(["X", "Y"])},
        {"method": "dense", "setting": "per_question", "example_id": "q1",
         "retrieved_titles": "D"},
    ]
    assert legacy_titles_by_example(legacy, "dense", "pooled") == {"q1": ["A", "B", "C"]}


def test_title_parity_zero_and_single_rank_mismatch():
    new = {"q1": ["A", "B", "C"], "q2": ["D", "E"]}
    assert title_parity_report(new, {"q1": ["A", "B", "C"], "q2": ["D", "E"]}) == []
    mismatches = title_parity_report(new, {"q1": ["A", "X", "C"], "q2": ["D", "E"]})
    assert mismatches == [TitleMismatch("q1", 2, "X", "B")]


def test_title_parity_flags_new_list_shorter_than_legacy():
    mismatches = title_parity_report({"q1": ["A"]}, {"q1": ["A", "B"]})
    assert mismatches == [TitleMismatch("q1", 2, "B", None)]


def test_title_parity_flags_missing_and_extra_examples():
    mismatches = title_parity_report({"q1": ["A"]}, {"q2": ["A"]})
    surfaced = {(m.example_id, m.legacy_title, m.new_title) for m in mismatches}
    assert ("q1", None, "<example absent from legacy>") in surfaced      # extra in new
    assert ("q2", "<example absent from new run>", None) in surfaced     # missing from new


def test_build_legacy_audit_view_roundtrips_and_truncates(tmp_path):
    result = _run("dense", "pooled", str(tmp_path / "runs"))
    view_rows = build_legacy_audit_view_rows(result)
    # The view's split titles equal the run's own per-example title order.
    assert legacy_titles_by_example(view_rows, "dense", "pooled") == \
        titles_by_example_from_rows(result.rows)
    truncated = build_legacy_audit_view_rows(result, store_depth=1)
    for row in truncated:
        assert len(row["retrieved_titles"].split(TITLE_SEPARATOR)) == 1


def test_legacy_audit_reads_csv_parity_and_mismatch(tmp_path):
    result = _run("dense", "pooled", str(tmp_path / "runs"))
    columns = ["method", "setting", "example_id", "retrieved_titles"]
    view_rows = build_legacy_audit_view_rows(result)

    good_path = str(tmp_path / "legacy_good.csv")
    pd.DataFrame(view_rows, columns=columns).to_csv(good_path, index=False)
    assert raw_runner._legacy_audit(result, good_path) == []

    bad_rows = [dict(row) for row in view_rows]
    parts = bad_rows[0]["retrieved_titles"].split(TITLE_SEPARATOR)
    parts[0] = "ZZZ_WRONG"
    bad_rows[0]["retrieved_titles"] = TITLE_SEPARATOR.join(parts)
    bad_path = str(tmp_path / "legacy_bad.csv")
    pd.DataFrame(bad_rows, columns=columns).to_csv(bad_path, index=False)
    assert len(raw_runner._legacy_audit(result, bad_path)) >= 1


def test_main_legacy_audit_parity_returns_zero(tmp_path):
    examples = _examples()
    raw_records = _raw_records(examples)
    # Seed run to capture the deterministic title order, then reuse it as legacy.
    seed = _run("dense", "pooled", str(tmp_path / "seed"))
    legacy_csv = str(tmp_path / "legacy.csv")
    pd.DataFrame(build_legacy_audit_view_rows(seed),
                 columns=["method", "setting", "example_id", "retrieved_titles"]).to_csv(
        legacy_csv, index=False)

    code = main(
        ["--method", "dense", "--setting", "pooled", "--run-root", str(tmp_path / "runs"),
         "--depth", "3", "--legacy-audit", legacy_csv],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=lambda split, n: (raw_records, examples),
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now,
        git_commit="0" * 40,
    )
    assert code == 0


def test_main_legacy_audit_mismatch_returns_nonzero(tmp_path, capsys):
    examples = _examples()
    raw_records = _raw_records(examples)
    legacy_csv = str(tmp_path / "legacy_wrong.csv")
    pd.DataFrame(
        [{"method": "dense", "setting": "pooled", "example_id": "q1",
          "retrieved_titles": "WRONG1"},
         {"method": "dense", "setting": "pooled", "example_id": "q2",
          "retrieved_titles": "WRONG2"}],
        columns=["method", "setting", "example_id", "retrieved_titles"],
    ).to_csv(legacy_csv, index=False)

    code = main(
        ["--method", "dense", "--setting", "pooled", "--run-root", str(tmp_path / "runs"),
         "--depth", "3", "--legacy-audit", legacy_csv],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=lambda split, n: (raw_records, examples),
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now,
        git_commit="0" * 40,
    )
    assert code == 1
    assert "MIGRATION-AUDIT" in capsys.readouterr().out
    # The bundle was still published (the audit is a post-publication comparison).
    assert os.path.isdir(os.path.join(str(tmp_path / "runs"),
                                      "dense_pooled_n2_d3_20260720_r01"))


# ---------------------------------------------------------------------------
# Defaults and offline guarantees.
# ---------------------------------------------------------------------------


def test_default_model_config_shapes():
    dense = default_model_config("dense", model_name="all-MiniLM-L6-v2")
    assert set(dense) == {"implementation", "identifier", "parameters"}
    bm25 = default_model_config("bm25")
    validate_bm25_config(bm25)


def test_default_retriever_factory_is_lazy_and_callable():
    # Building the factory must not require a model; it returns a callable.
    factory = default_retriever_factory("dense", encoder=fake_encode)
    retriever = factory([_para("A", "cat dog"), _para("B", "fish")])
    assert [p.title for p, _ in retriever.retrieve("cat", top_k=1)] == ["A"]


def test_importing_raw_runner_loads_no_heavy_backend():
    # Importing the runner must not pull in a model / dataset / BM25 / network
    # backend; those are lazily imported only inside the real factory paths.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    probe = (
        "import sys; import src.raw_runner; "
        "heavy = [m for m in ('sentence_transformers', 'datasets', 'rank_bm25', "
        "'torch', 'requests') if m in sys.modules]; "
        "print('HEAVY:' + ','.join(heavy))"
    )
    completed = subprocess.run([sys.executable, "-c", probe], cwd=repo_root,
                               capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    line = [ln for ln in completed.stdout.splitlines() if ln.startswith("HEAVY:")][0]
    assert line == "HEAVY:", f"raw_runner import pulled in heavy backends: {line}"


# ===========================================================================
# S3S2-A regressions -- dataset provenance is bound to the examples and cannot
# be forged. Each prohibited case rejects before publication; a property-matched
# legal control publishes with the derived digest.
# ===========================================================================


def _run_one_setting(setting, run_root, *, examples, raw_records,
                     dataset_fingerprint_value=None):
    return run_one_setting(
        method="dense", setting=setting, examples=examples,
        raw_records=raw_records, make_retriever=_dense_factory(), run_root=run_root,
        model_or_retriever_config=dense_model_config(),
        dataset_fingerprint_value=dataset_fingerprint_value, **_provenance(),
    )


def test_dataset_binding_rejects_wrong_record_count(tmp_path):
    examples = _examples()
    raw_records = _raw_records(examples)[:1]   # one record, two examples
    run_root = str(tmp_path / "runs")
    with pytest.raises(ValueError):
        _run_one_setting("pooled", run_root, examples=examples, raw_records=raw_records)
    assert not os.path.exists(run_root)   # rejected before any bundle is written


def test_dataset_binding_rejects_wrong_record_id(tmp_path):
    examples = _examples()
    raw_records = _raw_records(examples)
    raw_records[0] = {"_id": "other", "question": examples[0].question}
    run_root = str(tmp_path / "runs")
    with pytest.raises(ValueError):
        _run_one_setting("pooled", run_root, examples=examples, raw_records=raw_records)
    assert not os.path.exists(run_root)


def test_dataset_binding_rejects_swapped_order(tmp_path):
    examples = _examples()
    raw_records = list(reversed(_raw_records(examples)))   # q2, q1 vs examples q1, q2
    run_root = str(tmp_path / "runs")
    with pytest.raises(ValueError):
        _run_one_setting("pooled", run_root, examples=examples, raw_records=raw_records)
    assert not os.path.exists(run_root)


def test_dataset_forged_valid_digest_is_rejected(tmp_path):
    examples = _examples()
    forged = "sha256:" + "f" * 64   # valid-looking shape, wrong preimage
    run_root = str(tmp_path / "runs")
    with pytest.raises(ValueError):
        _run_one_setting("pooled", run_root, examples=examples,
                         raw_records=_raw_records(examples),
                         dataset_fingerprint_value=forged)
    assert not os.path.exists(run_root)


def test_dataset_binding_control_aligned_list_publishes_derived_digest(tmp_path):
    examples = _examples()
    result = _run_one_setting("pooled", str(tmp_path / "runs"),
                              examples=examples, raw_records=_raw_records(examples))
    manifest, _ = _validate_bundle_on_disk(result.bundle_dir)
    assert manifest["dataset_fingerprint"] == dataset_fingerprint(_raw_records(examples))


def test_dataset_binding_control_generator_and_correct_cache_publish(tmp_path):
    examples = _examples()
    expected = dataset_fingerprint(_raw_records(examples))
    # A generator of aligned records is materialized exactly once and publishes.
    gen = (dict(record) for record in _raw_records(examples))
    from_gen = _run_one_setting("pooled", str(tmp_path / "gen"),
                                examples=examples, raw_records=gen)
    assert from_gen.manifest["dataset_fingerprint"] == expected
    # A cache value equal to the derived digest is accepted (a correct cache, not
    # a bypass); the forged-digest test above proves a wrong cache is rejected.
    cached = _run_one_setting("per_question", str(tmp_path / "cache"), examples=examples,
                              raw_records=_raw_records(examples),
                              dataset_fingerprint_value=expected)
    assert cached.manifest["dataset_fingerprint"] == expected


def test_dataset_binding_supports_id_and_underscore_id(tmp_path):
    examples = _examples()
    # HotpotQA distractor uses `_id`; some snapshots use `id`. process_example
    # prefers `id`, so the binding must accept either shape.
    records_id = [{"id": ex.example_id, "question": ex.question} for ex in examples]
    result = _run_one_setting("pooled", str(tmp_path / "runs"),
                              examples=examples, raw_records=records_id)
    assert os.path.isdir(result.bundle_dir)


def test_both_settings_record_same_derived_dataset_digest(tmp_path):
    examples = _examples()
    raw_records = _raw_records(examples)
    run_root = str(tmp_path / "runs")
    code = main(
        ["--method", "dense", "--setting", "both", "--run-root", run_root, "--depth", "3"],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=lambda split, n: (raw_records, examples),
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now, git_commit="0" * 40,
    )
    assert code == 0
    pooled_manifest, _ = _validate_bundle_on_disk(
        os.path.join(run_root, "dense_pooled_n2_d3_20260720_r01"))
    perq_manifest, _ = _validate_bundle_on_disk(
        os.path.join(run_root, "dense_per_question_n2_d4_20260720_r01"))
    assert pooled_manifest["dataset_fingerprint"] == perq_manifest["dataset_fingerprint"]
    assert pooled_manifest["dataset_fingerprint"] == dataset_fingerprint(raw_records)


# ===========================================================================
# S3S2-B regressions -- default provenance helpers fail closed instead of
# fabricating a pinned-looking version or a placeholder commit.
# ===========================================================================


def test_installed_bm25_version_fails_closed_when_missing(monkeypatch):
    import importlib.metadata as importlib_metadata

    def _missing(_name):
        raise importlib_metadata.PackageNotFoundError("rank_bm25")

    monkeypatch.setattr(importlib_metadata, "version", _missing)
    with pytest.raises(RuntimeError):
        raw_runner._installed_bm25_version()


def test_installed_bm25_version_rejects_empty(monkeypatch):
    import importlib.metadata as importlib_metadata
    monkeypatch.setattr(importlib_metadata, "version", lambda name: "   ")
    with pytest.raises(RuntimeError):
        raw_runner._installed_bm25_version()


def test_installed_bm25_version_control_real_then_patched(monkeypatch):
    # The truly installed version is a non-empty factual string (rank_bm25 is a
    # test dependency), read BEFORE any patch.
    real = raw_runner._installed_bm25_version()
    assert isinstance(real, str) and real.strip() != ""
    # A patched metadata lookup records exactly that factual version, not a pin.
    import importlib.metadata as importlib_metadata
    monkeypatch.setattr(importlib_metadata, "version", lambda name: "9.9.9")
    assert raw_runner._installed_bm25_version() == "9.9.9"


def _fake_completed(returncode=0, stdout="", stderr=""):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_git_head_fails_closed_on_oserror(monkeypatch):
    def _raise(*args, **kwargs):
        raise OSError("git not found")

    monkeypatch.setattr(subprocess, "run", _raise)
    with pytest.raises(RuntimeError):
        raw_runner._git_head()


def test_git_head_fails_closed_on_nonzero_exit(monkeypatch):
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: _fake_completed(returncode=128, stderr="fatal"))
    with pytest.raises(RuntimeError):
        raw_runner._git_head()


def test_git_head_fails_closed_on_empty_output(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _fake_completed(stdout="\n"))
    with pytest.raises(RuntimeError):
        raw_runner._git_head()


def test_git_head_fails_closed_on_malformed_output(monkeypatch):
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: _fake_completed(stdout="not-a-real-sha\n"))
    with pytest.raises(RuntimeError):
        raw_runner._git_head()


def test_git_head_control_accepts_valid_commit(monkeypatch):
    sha = "a" * 40
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _fake_completed(stdout=sha + "\n"))
    assert raw_runner._git_head() == sha


def test_git_head_control_real_repo_head():
    if shutil.which("git") is None:
        pytest.skip("git not available")
    head = raw_runner._git_head()
    assert raw_runner.GIT_COMMIT_RE.fullmatch(head) is not None


# ===========================================================================
# S3S2-C regressions -- the recorded command is exact and replayable: an argv
# with spaces/quotes round-trips through shlex, and the real entry point is kept.
# ===========================================================================


def test_command_reconstruction_roundtrips_spaces_and_quotes(monkeypatch):
    argv = [sys.executable, "-m", "src.raw_runner", "--method", "dense",
            "--run-root", "/tmp/run root with spaces",
            "--dataset-identifier", 'quote"inside']
    monkeypatch.setattr(sys, "orig_argv", argv, raising=False)
    command = raw_runner._reconstruct_command()
    # A raw " ".join loses argument boundaries; shlex round-trips to the same argv.
    assert shlex.split(command) == argv
    # The module entry point is preserved verbatim.
    assert "-m" in shlex.split(command) and "src.raw_runner" in shlex.split(command)


def test_command_reconstruction_preserves_script_entry_point(monkeypatch):
    argv = [sys.executable, "scripts/run_raw_retrieval.py", "--method", "bm25"]
    monkeypatch.setattr(sys, "orig_argv", argv, raising=False)
    assert shlex.split(raw_runner._reconstruct_command()) == argv


def test_command_reconstruction_fallback_without_orig_argv(monkeypatch):
    # On interpreters lacking sys.orig_argv (< 3.10) the executable plus sys.argv
    # is used, still recording the real executable and entry-point path.
    monkeypatch.delattr(sys, "orig_argv", raising=False)
    monkeypatch.setattr(sys, "argv", ["scripts/run_raw_retrieval.py", "--method", "dense",
                                      "--run-root", "with space"])
    command = raw_runner._reconstruct_command()
    assert shlex.split(command) == [sys.executable, "scripts/run_raw_retrieval.py",
                                    "--method", "dense", "--run-root", "with space"]


def test_command_no_space_control_is_stable(monkeypatch):
    argv = [sys.executable, "-m", "src.raw_runner", "--method", "dense"]
    monkeypatch.setattr(sys, "orig_argv", argv, raising=False)
    command = raw_runner._reconstruct_command()
    assert command == shlex.join(argv)
    assert shlex.split(command) == argv


def test_main_records_replayable_command_with_spaces(tmp_path, monkeypatch):
    examples = _examples()
    raw_records = _raw_records(examples)
    run_root = str(tmp_path / "run root with spaces")   # a real path containing spaces
    launch_argv = [sys.executable, "-m", "src.raw_runner", "--method", "dense",
                   "--setting", "pooled", "--run-root", run_root, "--depth", "3"]
    monkeypatch.setattr(sys, "orig_argv", launch_argv, raising=False)
    code = main(
        ["--method", "dense", "--setting", "pooled", "--run-root", run_root, "--depth", "3"],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=lambda split, n: (raw_records, examples),
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now, git_commit="0" * 40,
    )
    assert code == 0
    manifest, _ = _validate_bundle_on_disk(
        os.path.join(run_root, "dense_pooled_n2_d3_20260720_r01"))
    # The stored command round-trips to the exact launching argv (boundaries kept).
    assert shlex.split(manifest["command"]) == launch_argv


# ===========================================================================
# S3S2-D regressions -- --setting both publishes and audits EVERY setting and
# aggregates the mismatch status, returning nonzero only after both complete.
# ===========================================================================


def _combined_legacy_csv(tmp_path, *, corrupt_setting=None):
    """Seed correct legacy views for both settings from deterministic runs, then
    optionally corrupt one setting's first title to force a parity mismatch."""
    pooled_seed = _run("dense", "pooled", str(tmp_path / "seed_pooled"))
    perq_seed = _run("dense", "per_question", str(tmp_path / "seed_perq"))
    rows = (build_legacy_audit_view_rows(pooled_seed)
            + build_legacy_audit_view_rows(perq_seed))
    if corrupt_setting is not None:
        for row in rows:
            if row["setting"] == corrupt_setting:
                parts = row["retrieved_titles"].split(TITLE_SEPARATOR)
                parts[0] = "ZZZ_WRONG"
                row["retrieved_titles"] = TITLE_SEPARATOR.join(parts)
                break
    path = str(tmp_path / "legacy_both.csv")
    pd.DataFrame(rows, columns=["method", "setting", "example_id", "retrieved_titles"]).to_csv(
        path, index=False)
    return path


def _run_both_with_audit(tmp_path, legacy_csv):
    examples = _examples()
    raw_records = _raw_records(examples)
    run_root = str(tmp_path / "runs")
    code = main(
        ["--method", "dense", "--setting", "both", "--run-root", run_root,
         "--depth", "3", "--legacy-audit", legacy_csv],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=lambda split, n: (raw_records, examples),
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now, git_commit="0" * 40,
    )
    return code, run_root


def _assert_both_bundles_and_ids(run_root, out):
    pooled_dir = os.path.join(run_root, "dense_pooled_n2_d3_20260720_r01")
    perq_dir = os.path.join(run_root, "dense_per_question_n2_d4_20260720_r01")
    assert os.path.isdir(pooled_dir) and os.path.isdir(perq_dir)
    assert "dense_pooled_n2_d3_20260720_r01" in out
    assert "dense_per_question_n2_d4_20260720_r01" in out


def test_both_first_setting_mismatch_still_completes_second(tmp_path, capsys):
    legacy = _combined_legacy_csv(tmp_path, corrupt_setting="pooled")
    code, run_root = _run_both_with_audit(tmp_path, legacy)
    out = capsys.readouterr().out
    assert code == 1
    _assert_both_bundles_and_ids(run_root, out)
    # Both audits ran: one reported a mismatch, the other zero.
    assert out.count("MIGRATION-AUDIT") == 2
    assert "title-order mismatch(es)" in out
    assert "zero title-order mismatches" in out


def test_both_second_setting_mismatch_still_completes_both(tmp_path, capsys):
    legacy = _combined_legacy_csv(tmp_path, corrupt_setting="per_question")
    code, run_root = _run_both_with_audit(tmp_path, legacy)
    out = capsys.readouterr().out
    assert code == 1
    _assert_both_bundles_and_ids(run_root, out)
    assert out.count("MIGRATION-AUDIT") == 2
    assert "title-order mismatch(es)" in out
    assert "zero title-order mismatches" in out


def test_both_clean_audit_returns_zero(tmp_path, capsys):
    legacy = _combined_legacy_csv(tmp_path, corrupt_setting=None)
    code, run_root = _run_both_with_audit(tmp_path, legacy)
    out = capsys.readouterr().out
    assert code == 0
    _assert_both_bundles_and_ids(run_root, out)
    assert out.count("zero title-order mismatches") == 2


# ===========================================================================
# S3S2-E regressions -- malformed/duplicate/empty legacy audit rows are rejected
# distinctly before any parity comparison; the intentional legal prefix passes.
# ===========================================================================


def _legacy_row(example_id, titles, *, method="dense", setting="pooled"):
    return {"method": method, "setting": setting, "example_id": example_id,
            "retrieved_titles": TITLE_SEPARATOR.join(titles)}


def test_legacy_duplicate_rows_rejected_either_order():
    # Reviewer's exact counterexample: a WRONG duplicate followed by a correct row
    # must not silently overwrite into a false zero (and neither does the reverse).
    dup_then_correct = [_legacy_row("q1", ["WRONG", "A"]), _legacy_row("q1", ["A"])]
    with pytest.raises(RawSchemaError):
        legacy_titles_by_example(dup_then_correct, "dense", "pooled")
    correct_then_dup = [_legacy_row("q1", ["A"]), _legacy_row("q1", ["WRONG", "A"])]
    with pytest.raises(RawSchemaError):
        legacy_titles_by_example(correct_then_dup, "dense", "pooled")


def test_legacy_empty_title_cell_rejected():
    # An empty stored ranking (e.g. legacy {q1: []}) used to become [] and yield a
    # false zero-mismatch parity; it is now rejected at read time.
    with pytest.raises(RawSchemaError):
        legacy_titles_by_example([_legacy_row("q1", [])], "dense", "pooled")


def test_legacy_nan_title_cell_rejected():
    # pandas .fillna("") turns a NaN cell into "", which must still be rejected.
    rows = [{"method": "dense", "setting": "pooled", "example_id": "q1",
             "retrieved_titles": ""}]
    with pytest.raises(RawSchemaError):
        legacy_titles_by_example(rows, "dense", "pooled")


def test_legacy_missing_required_column_rejected():
    rows = [{"method": "dense", "setting": "pooled", "example_id": "q1"}]  # no titles column
    with pytest.raises(RawSchemaError):
        legacy_titles_by_example(rows, "dense", "pooled")


def test_legacy_empty_example_id_rejected():
    with pytest.raises(RawSchemaError):
        legacy_titles_by_example([_legacy_row("", ["A"])], "dense", "pooled")


def test_legacy_ordinary_single_row_mismatch_still_reports():
    legacy = legacy_titles_by_example([_legacy_row("q1", ["WRONG"])], "dense", "pooled")
    mismatches = title_parity_report({"q1": ["A", "B"]}, legacy)
    assert mismatches == [TitleMismatch("q1", 1, "WRONG", "A")]


def test_legacy_nonempty_prefix_shorter_than_new_passes():
    # The intentional legal case: a non-empty legacy prefix is a rank-by-rank
    # agreement with a complete per-question v1 list that is legitimately longer.
    legacy = legacy_titles_by_example([_legacy_row("q1", ["A"])], "dense", "pooled")
    assert title_parity_report({"q1": ["A", "B", "C"]}, legacy) == []


def test_legacy_exact_normal_parity_passes():
    legacy = legacy_titles_by_example(
        [_legacy_row("q1", ["A", "B"]), _legacy_row("q2", ["C"])], "dense", "pooled")
    assert title_parity_report({"q1": ["A", "B"], "q2": ["C"]}, legacy) == []


# --- S3S2-E at the PUBLIC parity-helper boundary: title_parity_report itself
#     fails closed on a direct empty legacy ranking (the CSV adapter is only one
#     caller; a direct caller must not be able to certify a false zero). ---


def test_title_parity_direct_empty_legacy_list_rejected():
    # The reviewer's exact direct counterexample: an empty legacy ranking at the
    # public helper boundary used to loop zero times and return [] -- the exact
    # zero-mismatch approval signal. It now fails closed before any comparison.
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": []})


def test_title_parity_direct_empty_legacy_among_others_rejected():
    # Even one empty legacy ranking mixed with valid ones is rejected (the empty
    # entry cannot silently drop out of an otherwise-clean parity result).
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"], "q2": ["B"]}, {"q1": ["A"], "q2": []})


def test_title_parity_direct_nonempty_prefix_passes():
    # The legal twin: a non-empty legacy prefix shorter than the complete new list
    # is rank-by-rank agreement (not emptiness) and still certifies parity.
    assert title_parity_report({"q1": ["A", "B", "C"]}, {"q1": ["A"]}) == []


def test_title_parity_direct_ordinary_mismatch_still_reports():
    # An ordinary non-empty legacy disagreement is still surfaced: the fix rejects
    # only empty rankings, never a legitimate mismatch.
    assert title_parity_report({"q1": ["B"]}, {"q1": ["A"]}) == [
        TitleMismatch("q1", 1, "A", "B")]


# ===========================================================================
# S3S2-F regressions -- a one-shot raw_records loader composes with --setting
# both: main materializes the loaded records once, before any publication, so
# both settings hash and publish the same snapshot. The list-valued twin is the
# adjacent legal control.
# ===========================================================================


def _both_dense_manifests(run_root):
    """Validate and return the pooled + per_question manifests for a dense
    --setting both run at the deterministic (n2, depth 3) run IDs."""
    pooled_manifest, _ = _validate_bundle_on_disk(
        os.path.join(run_root, "dense_pooled_n2_d3_20260720_r01"))
    perq_manifest, _ = _validate_bundle_on_disk(
        os.path.join(run_root, "dense_per_question_n2_d4_20260720_r01"))
    return pooled_manifest, perq_manifest


def test_main_both_with_one_shot_generator_loader_publishes_two_bundles(tmp_path, capsys):
    # A loader returning a ONE-SHOT generator of aligned raw records (consumable
    # exactly once) previously let pooled consume + publish, then per_question
    # bound an empty list and raised -- leaving a misleading half-run. main now
    # materializes the records once before the settings loop, so both bundles
    # publish, rc is 0, both run IDs print, and both manifests carry the same
    # derived dataset fingerprint.
    examples = _examples()
    aligned = _raw_records(examples)
    expected_fp = dataset_fingerprint(aligned)
    run_root = str(tmp_path / "runs")

    def load_one_shot_generator(split, n):
        return (dict(record) for record in aligned), examples

    code = main(
        ["--method", "dense", "--setting", "both", "--run-root", run_root, "--depth", "3"],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=load_one_shot_generator,
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now, git_commit="0" * 40,
    )
    assert code == 0
    pooled_manifest, perq_manifest = _both_dense_manifests(run_root)
    assert pooled_manifest["dataset_fingerprint"] == expected_fp
    assert perq_manifest["dataset_fingerprint"] == expected_fp
    assert pooled_manifest["dataset_fingerprint"] == perq_manifest["dataset_fingerprint"]
    out = capsys.readouterr().out
    assert "dense_pooled_n2_d3_20260720_r01" in out
    assert "dense_per_question_n2_d4_20260720_r01" in out


def test_main_both_with_list_loader_control_publishes_two_bundles(tmp_path):
    # The adjacent legal twin: the identical records supplied as a reusable list
    # also publish both bundles with the same derived fingerprint. Pairing the two
    # proves the generator failure was one-shot consumption, not the records.
    examples = _examples()
    aligned = _raw_records(examples)
    expected_fp = dataset_fingerprint(aligned)
    run_root = str(tmp_path / "runs")

    code = main(
        ["--method", "dense", "--setting", "both", "--run-root", run_root, "--depth", "3"],
        make_retriever_factory=lambda method: _dense_factory(),
        load_dataset=lambda split, n: (list(aligned), examples),
        model_config_for=lambda method: dense_model_config(),
        now=_fixed_now, git_commit="0" * 40,
    )
    assert code == 0
    pooled_manifest, perq_manifest = _both_dense_manifests(run_root)
    assert pooled_manifest["dataset_fingerprint"] == expected_fp
    assert perq_manifest["dataset_fingerprint"] == expected_fp


# ===========================================================================
# S3S2-G regressions -- title_parity_report validates each legacy ranking's
# nested SHAPE (not just container truthiness) and materializes ordered
# iterators exactly once, before any comparison. A truthy-but-empty
# generator/iterator, a bare str/bytes, a mapping, an unordered set, and a
# non-iterable can no longer become the false [] zero-mismatch approval signal;
# ordered iterable prefixes stay legal.
# ===========================================================================


class _CountingIterable:
    """An ordered iterable that records how many times it is iterated, so a test
    can prove title_parity_report materializes an accepted iterator EXACTLY once."""

    def __init__(self, items):
        self._items = list(items)
        self.iter_calls = 0

    def __iter__(self):
        self.iter_calls += 1
        return iter(self._items)


def test_title_parity_rejects_empty_generator_ranking():
    # A generator object is truthy even when it yields nothing, so the old
    # `if not ranking` precheck passed it and the per-rank loop ran zero times ->
    # false []. It now fails closed.
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": (t for t in [])})


def test_title_parity_rejects_empty_iterator_ranking():
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": iter([])})


def test_title_parity_rejects_bare_string_ranking():
    # A bare string is truthy and iterable; it used to be compared character by
    # character as if each char were a title. It is now rejected outright.
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": "A"})


def test_title_parity_rejects_bytes_ranking():
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": b"A"})


def test_title_parity_rejects_bytearray_ranking():
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": bytearray(b"A")})


def test_title_parity_rejects_mapping_ranking():
    # Iterating a mapping yields only its keys; it is not an ordered title list.
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": {"A": 1}})


def test_title_parity_rejects_unordered_set_ranking():
    # A set/frozenset carries no saved rank order to compare against.
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": {"A", "B"}})
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": frozenset({"A"})})


def test_title_parity_rejects_keys_view_ranking():
    # A dict keys-view is an unordered Set; reject it like set/frozenset.
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": {"A": 1, "B": 2}.keys()})


def test_title_parity_rejects_noniterable_ranking():
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": 5})
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": None})


def test_title_parity_rejects_nonstring_title_element():
    # Shape includes the element type: a materialized ranking must hold strings.
    with pytest.raises(RawSchemaError):
        title_parity_report({"q1": ["A"]}, {"q1": [1, 2]})


def test_title_parity_accepts_nonempty_generator_prefix():
    # Legal control: a non-empty generator prefix shorter than the complete new
    # list is materialized and certifies parity (ordered-iterator support kept).
    gen = (t for t in ["A"])
    assert title_parity_report({"q1": ["A", "B", "C"]}, {"q1": gen}) == []


def test_title_parity_materializes_ordered_iterable_exactly_once():
    # Prove one-shot materialization: an accepted ordered iterable is iterated
    # exactly once (never re-consumed), matching the raw-record one-shot contract.
    ranking = _CountingIterable(["A"])
    assert title_parity_report({"q1": ["A", "B"]}, {"q1": ranking}) == []
    assert ranking.iter_calls == 1


def test_title_parity_accepts_list_and_tuple_prefix_controls():
    # Concrete ordered-collection controls: both a list and a tuple prefix pass.
    assert title_parity_report({"q1": ["A", "B"]}, {"q1": ["A"]}) == []
    assert title_parity_report({"q1": ["A", "B"]}, {"q1": ("A",)}) == []


def test_title_parity_generator_ordinary_mismatch_still_reports():
    # An ordinary non-empty disagreement supplied as a generator is still surfaced
    # (materialization does not swallow a legitimate mismatch).
    gen = (t for t in ["A"])
    assert title_parity_report({"q1": ["B"]}, {"q1": gen}) == [
        TitleMismatch("q1", 1, "A", "B")]
