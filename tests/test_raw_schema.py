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
    expected_manifest_fields,
)


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
            "parameters": {"k1": 1.5, "b": 0.75, "epsilon": 0.25},
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
    manifest = dense_pooled_manifest()
    manifest["n_loaded"] = 3  # rankings only have q1, q2
    with pytest.raises(RawSchemaError):
        validate_raw_bundle(RANKING_COLUMNS, dense_pooled_rows(), manifest)


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
