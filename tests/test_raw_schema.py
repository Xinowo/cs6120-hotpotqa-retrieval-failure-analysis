"""
test_raw_schema.py

Synthetic, offline tests for the RAW retrieval schema constants and
contract-only validators in :mod:`src.raw_schema`. Every fixture is a hand-built
dict/list plus in-memory bytes: no model download, no network, no real corpus.

These tests exercise the frozen ``retrieval_raw_schema_v1`` physical contract
(``docs/specs/2026-07-20-raw-retrieval-rankings-schema.md``): exact columns and
order, manifest field/type/shape rules, run-ID grammar, per-question complete
mini-corpus storage, pooled corpus-exhaustion vs cap-induced truncation, and the
rankings checksum. They never assert a metric value -- the raw layer has none.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import copy

import pytest

from src import raw_schema
from src.raw_schema import (
    RANKING_COLUMNS,
    RETRIEVAL_RAW_SCHEMA_V1,
    LEGACY_RAW_SCHEMA_V0,
    RawSchemaError,
    compute_sha256,
    validate_rankings_columns,
    validate_rankings_rows,
    validate_manifest,
    validate_pooled_depth,
    validate_per_question_completeness,
    validate_rankings_checksum,
    validate_raw_bundle,
    validate_bm25_config,
    validate_utc_timestamp,
    expected_manifest_fields,
)


def _full_bm25_parameters():
    """The complete frozen BM25 parameter set (raw spec)."""
    return {
        "b": 0.75,
        "epsilon": 0.25,
        "k1": 1.5,
        "lowercase": True,
        "package_version": "0.2.2",
        "stopword_policy": "none",
        "tokenizer": "python_str_split",
    }


# ---------------------------------------------------------------------------
# Fixtures (pure Python; no I/O)
# ---------------------------------------------------------------------------


def _model_config():
    return {
        "implementation": "sentence_transformers",
        "identifier": "fake-mini-lm",
        "parameters": {"normalize": True, "batch_size": 32},
    }


def dense_pooled_manifest(run_id="dense_pooled_n2_d3_20260720_r01", depth=3, corpus_size=5):
    return {
        "raw_schema_version": RETRIEVAL_RAW_SCHEMA_V1,
        "retrieval_run_id": run_id,
        "created_at": "2026-07-20T12:00:00Z",
        "method": "dense",
        "setting": "pooled",
        "split": "validation",
        "n_requested": 2,
        "n_loaded": 2,
        "retrieval_depth": depth,
        "score_type": "cosine_similarity",
        "score_direction": "higher_is_better",
        "model_or_retriever_config": _model_config(),
        "dataset_identifier": "hotpotqa_distractor_v1",
        "dataset_fingerprint": "sha256:" + "a" * 64,
        "example_ids_fingerprint": "sha256:" + "b" * 64,
        "corpus_fingerprint": "sha256:" + "c" * 64,
        "corpus_size": corpus_size,
        "deduplication_policy": "exact_title_keep_first_dataset_order",
        "tie_break_policy": "score_desc_then_corpus_order_asc",
        "git_commit": "0" * 40,
        "command": "python scripts/run_dense_experiment.py --setting pooled",
        "rankings_sha256": "d" * 64,
    }


def dense_pooled_rows(run_id="dense_pooled_n2_d3_20260720_r01", depth=3):
    rows = []
    for example_id in ("q1", "q2"):
        for rank in range(1, depth + 1):
            rows.append({
                "retrieval_run_id": run_id,
                "method": "dense",
                "setting": "pooled",
                "example_id": example_id,
                "rank": rank,
                "title": f"{example_id}_title_{rank}",
                "score": 1.0 - 0.1 * rank,
            })
    return rows


def bm25_per_question_manifest(run_id="bm25_per_question_n2_d4_20260720_r01"):
    manifest = {
        "raw_schema_version": RETRIEVAL_RAW_SCHEMA_V1,
        "retrieval_run_id": run_id,
        "created_at": "2026-07-20T12:00:00Z",
        "method": "bm25",
        "setting": "per_question",
        "split": "validation",
        "n_requested": 2,
        "n_loaded": 2,
        "retrieval_depth": 4,
        "score_type": "bm25_okapi",
        "score_direction": "higher_is_better",
        "model_or_retriever_config": {
            "implementation": "rank_bm25",
            "identifier": "BM25Okapi",
            "parameters": _full_bm25_parameters(),
        },
        "dataset_identifier": "hotpotqa_distractor_v1",
        "dataset_fingerprint": "sha256:" + "a" * 64,
        "example_ids_fingerprint": "sha256:" + "b" * 64,
        "corpus_fingerprint": "sha256:" + "c" * 64,
        "per_example_corpus_size": {"q1": 4, "q2": 2},
        "deduplication_policy": "none_preserve_source_order",
        "tie_break_policy": "score_desc_then_corpus_order_asc",
        "git_commit": "0" * 40,
        "command": "python scripts/run_bm25_experiment.py --setting per_question",
        "rankings_sha256": "d" * 64,
    }
    return manifest


def bm25_per_question_rows(run_id="bm25_per_question_n2_d4_20260720_r01"):
    rows = []
    for example_id, size in (("q1", 4), ("q2", 2)):
        for rank in range(1, size + 1):
            rows.append({
                "retrieval_run_id": run_id,
                "method": "bm25",
                "setting": "per_question",
                "example_id": example_id,
                "rank": rank,
                "title": f"{example_id}_t{rank}",
                "score": float(size - rank),
            })
    return rows


def rerank_manifest(run_id="rerank_pooled_n2_d3_20260720_r01"):
    manifest = dense_pooled_manifest(run_id=run_id)
    manifest["method"] = "rerank"
    manifest["score_type"] = "cross_encoder_logit"
    manifest["deduplication_policy"] = "none_parent_candidate_set_unchanged"
    manifest["tie_break_policy"] = "score_desc_then_parent_rank_asc"
    manifest["model_or_retriever_config"] = {
        "implementation": "sentence_transformers",
        "identifier": "cross-encoder/ms-marco",
        "parameters": {},
    }
    manifest["parent_retrieval_run_id"] = "dense_pooled_n2_d3_20260720_r01"
    manifest["parent_rankings_sha256"] = "e" * 64
    manifest["parent_candidate_depth"] = 3
    return manifest


# ---------------------------------------------------------------------------
# Column contract
# ---------------------------------------------------------------------------


def test_ranking_columns_frozen_order():
    assert RANKING_COLUMNS == [
        "retrieval_run_id", "method", "setting", "example_id", "rank", "title", "score"
    ]


def test_validate_columns_accepts_exact_order():
    validate_rankings_columns(RANKING_COLUMNS)


def test_validate_columns_rejects_missing_extra_and_reordered():
    with pytest.raises(RawSchemaError):
        validate_rankings_columns(RANKING_COLUMNS[:-1])  # missing score
    with pytest.raises(RawSchemaError):
        validate_rankings_columns(RANKING_COLUMNS + ["gold_titles"])  # extra
    reordered = list(RANKING_COLUMNS)
    reordered[4], reordered[5] = reordered[5], reordered[4]  # swap rank/title
    with pytest.raises(RawSchemaError):
        validate_rankings_columns(reordered)


def test_raw_layer_never_defines_metric_or_gold_columns():
    forbidden = {"gold_titles", "question_type", "level", "reciprocal_rank_at_10",
                 "any_evidence_recall@2"}
    assert forbidden.isdisjoint(RANKING_COLUMNS)


# ---------------------------------------------------------------------------
# Valid bundles
# ---------------------------------------------------------------------------


def test_valid_dense_pooled_bundle():
    validate_raw_bundle(RANKING_COLUMNS, dense_pooled_rows(), dense_pooled_manifest())


def test_valid_bm25_per_question_bundle():
    validate_raw_bundle(RANKING_COLUMNS, bm25_per_question_rows(),
                        bm25_per_question_manifest())


def test_valid_rerank_bundle():
    rows = dense_pooled_rows(run_id="rerank_pooled_n2_d3_20260720_r01")
    for row in rows:
        row["method"] = "rerank"
    validate_raw_bundle(RANKING_COLUMNS, rows, rerank_manifest())


# ---------------------------------------------------------------------------
# Rank continuity, uniqueness, scores
# ---------------------------------------------------------------------------


def test_ranks_must_start_at_one():
    rows = dense_pooled_rows()
    for row in rows:
        if row["example_id"] == "q1":
            row["rank"] += 1  # 2,3,4 -> zero-based-like gap at start
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())


def test_ranks_must_be_contiguous_no_gap():
    rows = dense_pooled_rows()
    # q1 ranks become 1,2,4 -> gap
    for row in rows:
        if row["example_id"] == "q1" and row["rank"] == 3:
            row["rank"] = 4
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())


def test_duplicate_rank_rejected():
    rows = dense_pooled_rows()
    for row in rows:
        if row["example_id"] == "q1" and row["rank"] == 2:
            row["rank"] = 1  # two rank-1 rows for q1
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())


def test_run_id_method_setting_mismatch_rejected():
    rows = dense_pooled_rows()
    rows[0]["retrieval_run_id"] = "other_run"
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())

    rows = dense_pooled_rows()
    rows[0]["method"] = "bm25"
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())

    rows = dense_pooled_rows()
    rows[0]["setting"] = "per_question"
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())


@pytest.mark.parametrize("bad_score", [float("nan"), float("inf"), float("-inf"),
                                       "0.5", None, True])
def test_non_finite_or_non_numeric_scores_rejected(bad_score):
    rows = dense_pooled_rows()
    rows[0]["score"] = bad_score
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())


def test_missing_score_would_be_legacy_v0_not_v1():
    # A missing score is not raw v1; the version constant makes the boundary
    # explicit and the validator rejects the v1 manifest declaring it.
    assert LEGACY_RAW_SCHEMA_V0 != RETRIEVAL_RAW_SCHEMA_V1
    manifest = dense_pooled_manifest()
    manifest["raw_schema_version"] = LEGACY_RAW_SCHEMA_V0
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


# ---------------------------------------------------------------------------
# Manifest field-set, types, closed shapes
# ---------------------------------------------------------------------------


def test_expected_manifest_fields_are_conditional():
    pooled = expected_manifest_fields("dense", "pooled")
    perq = expected_manifest_fields("dense", "per_question")
    rerank = expected_manifest_fields("rerank", "pooled")
    assert "corpus_size" in pooled and "per_example_corpus_size" not in pooled
    assert "per_example_corpus_size" in perq and "corpus_size" not in perq
    assert {"parent_retrieval_run_id", "parent_rankings_sha256",
            "parent_candidate_depth"} <= rerank


def test_manifest_rejects_extra_and_missing_fields():
    manifest = dense_pooled_manifest()
    manifest["surprise"] = 1
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)

    manifest = dense_pooled_manifest()
    del manifest["corpus_size"]
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_pooled_manifest_must_not_carry_per_question_field():
    manifest = dense_pooled_manifest()
    manifest["per_example_corpus_size"] = {"q1": 3, "q2": 3}
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_conditional_field_never_serialized_as_null():
    manifest = dense_pooled_manifest()
    manifest["corpus_size"] = None
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_score_type_must_match_method():
    manifest = dense_pooled_manifest()
    manifest["score_type"] = "bm25_okapi"
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_dedup_and_tie_policy_must_match_method_setting():
    manifest = dense_pooled_manifest()
    manifest["deduplication_policy"] = "none_preserve_source_order"  # per_question value
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)

    manifest = dense_pooled_manifest()
    manifest["tie_break_policy"] = "score_desc_then_parent_rank_asc"  # rerank value
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_model_config_outer_shape_is_closed():
    manifest = dense_pooled_manifest()
    manifest["model_or_retriever_config"]["extra"] = 1
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)

    manifest = dense_pooled_manifest()
    manifest["model_or_retriever_config"]["identifier"] = ""
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_model_config_parameters_reject_non_finite_number():
    manifest = dense_pooled_manifest()
    manifest["model_or_retriever_config"]["parameters"]["bad"] = float("nan")
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


@pytest.mark.parametrize("field", ["dataset_fingerprint", "example_ids_fingerprint",
                                   "corpus_fingerprint"])
def test_fingerprints_require_sha256_prefix(field):
    manifest = dense_pooled_manifest()
    manifest[field] = "d" * 64  # missing 'sha256:' prefix
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_rankings_sha256_is_bare_hex_not_prefixed():
    manifest = dense_pooled_manifest()
    manifest["rankings_sha256"] = "sha256:" + "d" * 64  # must be bare hex
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


# ---------------------------------------------------------------------------
# Run-ID grammar
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("run_id", [
    "dense_pooled_n2_d3_20260720_r01",
    "bm25_per_question_n500_d10_20260720_r01",
    "rerank_pooled_n500_d50_20260720_r09",
])
def test_valid_run_ids_accepted(run_id):
    method = "rerank" if run_id.startswith("rerank") else run_id.split("_")[0]
    setting = "per_question" if "per_question" in run_id else "pooled"
    if method == "rerank":
        manifest = rerank_manifest(run_id=run_id)
    elif setting == "per_question":
        manifest = bm25_per_question_manifest(run_id=run_id)
    else:
        manifest = dense_pooled_manifest(run_id=run_id)
    # Only the ID grammar/segment agreement is under test here.
    assert raw_schema.RETRIEVAL_RUN_ID_RE.match(manifest["retrieval_run_id"])


@pytest.mark.parametrize("bad_run_id", [
    "dense_pooled_n2_d3_20260720_r1",   # one-digit sequence
    "dense_pooled_n2_d3_2026720_r01",   # 7-digit date
    "dense_bothsettings_n2_d3_20260720_r01",  # invalid setting
    "svm_pooled_n2_d3_20260720_r01",    # invalid method
    "dense_pooled_d3_20260720_r01",     # missing n segment
])
def test_bad_run_ids_rejected(bad_run_id):
    manifest = dense_pooled_manifest()
    manifest["retrieval_run_id"] = bad_run_id
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_run_id_segment_must_agree_with_method():
    manifest = dense_pooled_manifest(run_id="bm25_pooled_n2_d3_20260720_r01")
    # manifest.method is still 'dense' -> segment/method disagreement
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


# ---------------------------------------------------------------------------
# Per-question completeness
# ---------------------------------------------------------------------------


def test_per_question_complete_variable_size_corpora_accepted():
    validate_per_question_completeness(bm25_per_question_rows(),
                                       bm25_per_question_manifest())


def test_per_question_saved_depth_must_equal_corpus_size():
    rows = bm25_per_question_rows()
    # Drop q1's last rank -> saved depth 3 != declared size 4 (cap-truncation).
    rows = [r for r in rows if not (r["example_id"] == "q1" and r["rank"] == 4)]
    with pytest.raises(RawSchemaError):
        validate_per_question_completeness(rows, bm25_per_question_manifest())


def test_per_question_size_map_key_mismatch_rejected():
    manifest = bm25_per_question_manifest()
    manifest["per_example_corpus_size"] = {"q1": 4, "q3": 2}  # extra/missing key
    with pytest.raises(RawSchemaError):
        validate_per_question_completeness(bm25_per_question_rows(), manifest)


def test_per_question_retrieval_depth_must_be_max_corpus_size():
    manifest = bm25_per_question_manifest()
    manifest["retrieval_depth"] = 10  # not max(4, 2)=4
    with pytest.raises(RawSchemaError):
        validate_per_question_completeness(bm25_per_question_rows(), manifest)


def test_per_question_size_must_be_positive_integer():
    manifest = bm25_per_question_manifest()
    manifest["per_example_corpus_size"] = {"q1": 4, "q2": 0}
    with pytest.raises(RawSchemaError):
        validate_per_question_completeness(bm25_per_question_rows(), manifest)


def test_per_question_deep_corpus_over_ten_is_valid_raw():
    # A complete mini-corpus deeper than 10 is legal raw; the @10 metric NaN
    # policy is an eval-layer concern, not a raw-depth cap.
    run_id = "dense_per_question_n1_d12_20260720_r01"
    rows = [{
        "retrieval_run_id": run_id, "method": "dense", "setting": "per_question",
        "example_id": "q1", "rank": rank, "title": f"t{rank}", "score": float(-rank),
    } for rank in range(1, 13)]
    manifest = {
        "raw_schema_version": RETRIEVAL_RAW_SCHEMA_V1,
        "retrieval_run_id": run_id,
        "created_at": "2026-07-20T12:00:00Z",
        "method": "dense", "setting": "per_question", "split": "validation",
        "n_requested": 1, "n_loaded": 1, "retrieval_depth": 12,
        "score_type": "cosine_similarity", "score_direction": "higher_is_better",
        "model_or_retriever_config": _model_config(),
        "dataset_identifier": "hotpotqa_distractor_v1",
        "dataset_fingerprint": "sha256:" + "a" * 64,
        "example_ids_fingerprint": "sha256:" + "b" * 64,
        "corpus_fingerprint": "sha256:" + "c" * 64,
        "per_example_corpus_size": {"q1": 12},
        "deduplication_policy": "none_preserve_source_order",
        "tie_break_policy": "score_desc_then_corpus_order_asc",
        "git_commit": "0" * 40, "command": "cmd", "rankings_sha256": "d" * 64,
    }
    validate_raw_bundle(RANKING_COLUMNS, rows, manifest)


# ---------------------------------------------------------------------------
# Pooled depth: corpus exhaustion vs cap-induced truncation
# ---------------------------------------------------------------------------


def test_pooled_full_depth_accepted():
    validate_pooled_depth(dense_pooled_rows(), dense_pooled_manifest())


def test_pooled_short_ranking_ok_only_when_corpus_exhausted():
    # corpus_size 3 < retrieval_depth 5 -> saving 3 ranks is legal exhaustion.
    manifest = dense_pooled_manifest(depth=5, corpus_size=3)
    rows = dense_pooled_rows(depth=3)
    validate_pooled_depth(rows, manifest)


def test_pooled_short_ranking_rejected_as_cap_truncation():
    # corpus_size 5 >= retrieval_depth 5 -> saving only 3 ranks is truncation.
    manifest = dense_pooled_manifest(depth=5, corpus_size=5)
    rows = dense_pooled_rows(depth=3)
    with pytest.raises(RawSchemaError):
        validate_pooled_depth(rows, manifest)


# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------


def test_rankings_checksum_roundtrip():
    manifest = dense_pooled_manifest()
    payload = b"retrieval_run_id,method,setting,example_id,rank,title,score\n"
    manifest["rankings_sha256"] = compute_sha256(payload)
    validate_rankings_checksum(payload, manifest)


def test_rankings_checksum_mismatch_rejected():
    manifest = dense_pooled_manifest()
    manifest["rankings_sha256"] = compute_sha256(b"a")
    with pytest.raises(RawSchemaError):
        validate_rankings_checksum(b"b", manifest)


# ---------------------------------------------------------------------------
# n_loaded agreement
# ---------------------------------------------------------------------------


def test_n_loaded_must_match_distinct_example_count():
    # Run-ID n segment set to 3 so the n<N>/n_loaded agreement check passes and
    # the distinct-example-count check is the one that fires.
    manifest = dense_pooled_manifest(run_id="dense_pooled_n3_d3_20260720_r01")
    manifest["n_loaded"] = 3  # rankings only have q1, q2
    with pytest.raises(RawSchemaError):
        validate_raw_bundle(RANKING_COLUMNS, dense_pooled_rows(), manifest)


# ---------------------------------------------------------------------------
# P4 regression — physical ranking order (not a sorted copy)
# ---------------------------------------------------------------------------


def test_disordered_ranks_within_example_rejected():
    # Physical order 2, 1, 3 for q1 — a sorted-copy check would wrongly accept.
    rows = dense_pooled_rows()
    q1 = [r for r in rows if r["example_id"] == "q1"]
    q1[0]["rank"], q1[1]["rank"] = 2, 1  # physical sequence becomes 2,1,3
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(rows, dense_pooled_manifest())


def test_example_blocks_out_of_order_rejected():
    # q2 block physically placed before q1 violates ascending example_id order.
    rows = dense_pooled_rows()
    q1 = [r for r in rows if r["example_id"] == "q1"]
    q2 = [r for r in rows if r["example_id"] == "q2"]
    with pytest.raises(RawSchemaError):
        validate_rankings_rows(q2 + q1, dense_pooled_manifest())


def test_correctly_ordered_rankings_accepted():
    validate_rankings_rows(dense_pooled_rows(), dense_pooled_manifest())


# ---------------------------------------------------------------------------
# P3 regression — frozen BM25 config shape (method-specific provenance check)
# ---------------------------------------------------------------------------


def test_valid_bm25_config_accepted():
    validate_bm25_config({
        "implementation": "rank_bm25",
        "identifier": "BM25Okapi",
        "parameters": _full_bm25_parameters(),
    })


def test_bm25_config_missing_required_parameter_key_rejected():
    params = _full_bm25_parameters()
    del params["tokenizer"]
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "rank_bm25", "identifier": "BM25Okapi",
                              "parameters": params})


def test_bm25_config_unexpected_parameter_key_rejected():
    params = _full_bm25_parameters()
    params["surprise"] = 1
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "rank_bm25", "identifier": "BM25Okapi",
                              "parameters": params})


def test_bm25_config_wrong_implementation_or_identifier_rejected():
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "whoosh", "identifier": "BM25Okapi",
                              "parameters": _full_bm25_parameters()})
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "rank_bm25", "identifier": "BM25Plus",
                              "parameters": _full_bm25_parameters()})


def test_bm25_config_wrong_parameter_types_rejected():
    params = _full_bm25_parameters()
    params["lowercase"] = "true"  # must be a real boolean
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "rank_bm25", "identifier": "BM25Okapi",
                              "parameters": params})

    params = _full_bm25_parameters()
    params["package_version"] = ""  # must be non-empty
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "rank_bm25", "identifier": "BM25Okapi",
                              "parameters": params})

    params = _full_bm25_parameters()
    params["tokenizer"] = "spacy"  # frozen value only
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "rank_bm25", "identifier": "BM25Okapi",
                              "parameters": params})

    params = _full_bm25_parameters()
    params["k1"] = float("nan")  # must be finite
    with pytest.raises(RawSchemaError):
        validate_bm25_config({"implementation": "rank_bm25", "identifier": "BM25Okapi",
                              "parameters": params})


def test_generic_manifest_validator_stays_method_agnostic():
    # The generic manifest validator must NOT enforce BM25 inner keys: a bm25
    # manifest whose parameters are only {b, epsilon, k1} still passes the
    # generic manifest check (the BM25-specific closure is validate_bm25_config).
    manifest = bm25_per_question_manifest()
    manifest["model_or_retriever_config"]["parameters"] = {"b": 0.75, "epsilon": 0.25, "k1": 1.5}
    validate_manifest(manifest)  # method-agnostic: accepts
    with pytest.raises(RawSchemaError):  # method-specific: rejects
        validate_bm25_config(manifest["model_or_retriever_config"])


# ---------------------------------------------------------------------------
# P5 regression — run-ID / timestamp / reranker-parent provenance
# ---------------------------------------------------------------------------


def test_run_id_n_and_depth_segments_must_match_manifest():
    manifest = dense_pooled_manifest(run_id="dense_pooled_n999_d3_20260720_r01")
    with pytest.raises(RawSchemaError):  # n999 != n_loaded 2
        validate_manifest(manifest)
    manifest = dense_pooled_manifest(run_id="dense_pooled_n2_d999_20260720_r01")
    with pytest.raises(RawSchemaError):  # d999 != retrieval_depth 3
        validate_manifest(manifest)


def test_run_id_invalid_calendar_date_rejected():
    manifest = dense_pooled_manifest(run_id="dense_pooled_n2_d3_20261340_r01")
    with pytest.raises(RawSchemaError):  # month 13, day 40
        validate_manifest(manifest)


def test_run_id_sequence_r00_rejected():
    manifest = dense_pooled_manifest(run_id="dense_pooled_n2_d3_20260720_r00")
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_created_at_must_be_real_utc_timestamp():
    manifest = dense_pooled_manifest()
    manifest["created_at"] = "2026-99-99T99:99:99Z"  # shape-valid but impossible
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_validate_utc_timestamp_helper():
    validate_utc_timestamp("2026-07-20T12:00:00Z", "created_at")
    with pytest.raises(RawSchemaError):
        validate_utc_timestamp("2026-13-01T00:00:00Z", "created_at")
    with pytest.raises(RawSchemaError):
        validate_utc_timestamp("2026-07-20 12:00:00", "created_at")  # wrong shape


def test_rerank_parent_must_be_dense_pooled():
    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "bm25_pooled_n2_d3_20260720_r01"  # not dense
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)

    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "dense_per_question_n2_d3_20260720_r01"  # not pooled
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)

    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "not-a-run-id"  # not even grammar-valid
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_rerank_parent_full_semantic_validation():
    # Dense/pooled-shaped but with an impossible date and r00 -> rejected
    # (foreign IDs get the same full validation as the primary run ID).
    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "dense_pooled_n2_d3_20261399_r01"  # bad date
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)

    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "dense_pooled_n2_d3_20260720_r00"  # r00
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


# ---------------------------------------------------------------------------
# Centralized retrieval-run-ID validator (reused for primary/parent/source/eval)
# ---------------------------------------------------------------------------


def test_validate_retrieval_run_id_accepts_valid():
    from src.raw_schema import validate_retrieval_run_id
    validate_retrieval_run_id("dense_pooled_n500_d50_20260720_r01")


def test_validate_retrieval_run_id_full_semantics():
    from src.raw_schema import validate_retrieval_run_id
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("dense_pooled_n2_d3_20261399_r01")  # bad date
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("dense_pooled_n2_d3_20260720_r00")  # r00
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("not-a-run-id")  # grammar


def test_validate_retrieval_run_id_optional_expected_segments():
    from src.raw_schema import validate_retrieval_run_id
    validate_retrieval_run_id("dense_pooled_n2_d3_20260720_r01",
                              expected_method="dense", expected_setting="pooled",
                              expected_n=2, expected_depth=3)
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("dense_pooled_n2_d3_20260720_r01", expected_n=5)
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("dense_pooled_n2_d3_20260720_r01", expected_method="bm25")


# ---------------------------------------------------------------------------
# Finding E — the canonical run-ID validator rejects non-positive n / depth
# ---------------------------------------------------------------------------


def test_validate_retrieval_run_id_rejects_zero_n():
    # n0 cannot name a conforming raw bundle (n_loaded >= 1), even with no
    # expected value supplied.
    from src.raw_schema import validate_retrieval_run_id
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("dense_pooled_n0_d50_20260720_r01")


def test_validate_retrieval_run_id_rejects_zero_depth():
    # d0 cannot name a conforming raw bundle (retrieval_depth >= 1).
    from src.raw_schema import validate_retrieval_run_id
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("dense_pooled_n2_d0_20260720_r01")


def test_primary_manifest_rejects_non_positive_run_id_segments():
    # Propagation point 1: the primary manifest reuse rejects n0/d0.
    manifest = dense_pooled_manifest(run_id="dense_pooled_n0_d3_20260720_r01")
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)
    manifest = dense_pooled_manifest(run_id="dense_pooled_n2_d0_20260720_r01")
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_rerank_parent_rejects_non_positive_run_id_segments():
    # Propagation point 2: the reranker parent reuse rejects n0/d0.
    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "dense_pooled_n0_d3_20260720_r01"
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)
    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "dense_pooled_n2_d0_20260720_r01"
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


# ---------------------------------------------------------------------------
# Finding G — canonical ID numeric grammar is ASCII-only; the rerun sequence is
# interpreted numerically (1..99), not string-compared to ASCII "00"
# ---------------------------------------------------------------------------

# Built with chr() so terminal/PowerShell encoding cannot silently replace the
# character with "?" and turn these into false (accidentally-ASCII) tests.
_AR_ZERO = chr(0x0660)   # ARABIC-INDIC DIGIT ZERO
_AR_ONE = chr(0x0661)    # ARABIC-INDIC DIGIT ONE
_FW_ONE = chr(0xFF11)    # FULLWIDTH DIGIT ONE


def test_validate_retrieval_run_id_rejects_arabic_indic_zero_sequence():
    # Two Arabic-Indic zero digits are numerically 0 but not ASCII "00", so the
    # old `seq != "00"` string compare accepted them, bypassing the r01 lower
    # bound. The ASCII-only regex must now reject the ID outright.
    from src.raw_schema import validate_retrieval_run_id
    bad = "dense_pooled_n2_d3_20260720_r" + _AR_ZERO * 2
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id(bad)


def test_primary_manifest_rejects_arabic_indic_zero_sequence():
    # Propagation: the primary raw manifest routes through the shared validator.
    manifest = dense_pooled_manifest(
        run_id="dense_pooled_n2_d3_20260720_r" + _AR_ZERO * 2)
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_rerank_parent_rejects_arabic_indic_zero_sequence():
    # Propagation: the reranker parent run ID uses the same validator.
    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "dense_pooled_n2_d3_20260720_r" + _AR_ZERO * 2
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


@pytest.mark.parametrize("bad_run_id", [
    "dense_pooled_n" + _AR_ONE + "_d3_20260720_r01",     # Unicode digit in n
    "dense_pooled_n2_d" + _AR_ONE + "_20260720_r01",     # Unicode digit in depth
    "dense_pooled_n2_d3_2026072" + _AR_ONE + "_r01",     # Unicode digit in date
    "dense_pooled_n2_d3_20260720_r0" + _AR_ONE,          # Unicode digit in r seq
    "dense_pooled_n" + _FW_ONE + "_d3_20260720_r01",     # fullwidth digit in n
])
def test_run_id_rejects_unicode_positive_digits(bad_run_id):
    # Positive non-ASCII decimal digits are not an alternate canonical spelling
    # of any numeric ID field.
    from src.raw_schema import validate_retrieval_run_id
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id(bad_run_id)


def test_run_id_ascii_sequence_bounds_r00_r01_r99():
    # ASCII r00 rejected (numeric 0); ASCII r01 and r99 are the legal endpoints.
    from src.raw_schema import validate_retrieval_run_id
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id("dense_pooled_n2_d3_20260720_r00")
    validate_retrieval_run_id("dense_pooled_n2_d3_20260720_r01")
    validate_retrieval_run_id("dense_pooled_n2_d3_20260720_r99")


# ---------------------------------------------------------------------------
# Finding H — a single trailing LF must be rejected by whole-string exact-format
# validation (run-ID grammar, bare SHA-256 checksums, and sha256: fingerprints).
# Each negative case differs from an accepted canonical control ONLY by one final
# LF, so the rejection cannot be blamed on any other earlier check, and no
# strip()/rstrip()/normalization is allowed to repair the extra byte.
# ---------------------------------------------------------------------------

_LF = "\n"


def test_run_id_helper_rejects_terminal_lf_but_accepts_canonical():
    # Case 1: the shared run-ID helper.
    from src.raw_schema import validate_retrieval_run_id
    canonical = "dense_pooled_n2_d3_20260720_r01"
    validate_retrieval_run_id(canonical)  # control: no-LF ID accepted
    with pytest.raises(RawSchemaError):
        validate_retrieval_run_id(canonical + _LF)


def test_primary_manifest_rejects_terminal_lf_run_id():
    # Case 2: propagation through the primary raw manifest.
    validate_manifest(dense_pooled_manifest())  # control
    manifest = dense_pooled_manifest(run_id="dense_pooled_n2_d3_20260720_r01" + _LF)
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_rerank_parent_rejects_terminal_lf_run_id():
    # Case 3: propagation through the reranker parent run ID.
    validate_manifest(rerank_manifest())  # control
    manifest = rerank_manifest()
    manifest["parent_retrieval_run_id"] = "dense_pooled_n2_d3_20260720_r01" + _LF
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_rankings_sha256_rejects_terminal_lf():
    # Case 6a: bare rankings_sha256.
    manifest = dense_pooled_manifest()
    validate_manifest(manifest)  # control: bare 64-hex accepted
    manifest["rankings_sha256"] = manifest["rankings_sha256"] + _LF
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_parent_rankings_sha256_rejects_terminal_lf():
    # Case 6b: bare parent_rankings_sha256.
    manifest = rerank_manifest()
    validate_manifest(manifest)  # control
    manifest["parent_rankings_sha256"] = manifest["parent_rankings_sha256"] + _LF
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


@pytest.mark.parametrize("field", ["dataset_fingerprint", "example_ids_fingerprint",
                                   "corpus_fingerprint"])
def test_fingerprint_fields_reject_terminal_lf(field):
    # Case 7: every sha256:-prefixed fingerprint field.
    manifest = dense_pooled_manifest()
    validate_manifest(manifest)  # control: 'sha256:' + 64-hex accepted
    manifest[field] = manifest[field] + _LF
    with pytest.raises(RawSchemaError):
        validate_manifest(manifest)


def test_created_at_rejects_terminal_lf():
    # Audit of CREATED_AT_RE for whole-string consistency: a trailing LF is
    # rejected by the fullmatch shape gate (strptime would also reject it, but the
    # regex now behaves consistently with the other exact-format patterns).
    validate_utc_timestamp("2026-07-20T12:00:00Z", "created_at")  # control
    with pytest.raises(RawSchemaError):
        validate_utc_timestamp("2026-07-20T12:00:00Z" + _LF, "created_at")


def test_fixtures_are_independent_copies():
    # Guard against fixture aliasing hiding mutation-based test bugs.
    a = dense_pooled_manifest()
    b = dense_pooled_manifest()
    a["model_or_retriever_config"]["parameters"]["batch_size"] = 999
    assert b["model_or_retriever_config"]["parameters"]["batch_size"] == 32
    assert a is not b and copy.deepcopy(a) == a


if __name__ == "__main__":
    import pytest as _pytest
    raise SystemExit(_pytest.main([__file__, "-q"]))
