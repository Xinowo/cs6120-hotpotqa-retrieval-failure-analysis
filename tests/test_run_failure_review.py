"""
test_run_failure_review.py

Tests the failure-review runner's plumbing fully offline: a fake bag-of-words
encoder drives real DenseRetrievers over tiny per-question corpora, so no model
is downloaded and no HotpotQA data is needed.

These tests check the PLUMBING contract only -- record shape, gold_ranks
forwarding, run-directory creation, JSON field completeness, empty-set
handling. The evaluator's metric/rank correctness itself is covered by
test_evaluator.py; here we only assert the runner moves that output into the
right place unchanged.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import tempfile

import numpy as np

from src.data_loader import HotpotExample, Paragraph
from scripts.run_failure_review import (
    BM25_RETRIEVER_NAME,
    METRIC_KS,
    RETRIEVER_NAME,
    build_config,
    build_details_record,
    build_retriever_record,
    merge_details_records,
    next_run_id,
    run_bm25_per_question,
    run_bm25_pooled,
    run_dense_per_question,
    run_dense_pooled,
    write_run,
)


VOCAB = ["cat", "dog", "fish", "bird"]


def fake_encode(texts):
    """Deterministic bag-of-words encoder over VOCAB, so cosine similarities
    are predictable (same style as the other offline tests)."""
    vecs = []
    for t in texts:
        tokens = t.lower().split()
        vecs.append([float(tokens.count(w)) for w in VOCAB])
    return np.array(vecs, dtype=float)


def make_examples():
    """Two per-question examples, each with its own ~4-paragraph corpus. In
    q1 the gold paragraph ('Cats') is the top hit; in q2 one gold ('Fish') is
    retrievable and the other ('Unicorns') is absent from the corpus, so its
    gold_rank must come back None."""
    q1 = HotpotExample(
        example_id="q1",
        question="cat",
        answer="",
        question_type="bridge",
        level="easy",
        paragraphs=[
            Paragraph(title="Cats", text="cat cat cat"),
            Paragraph(title="Dogs", text="dog dog dog"),
            Paragraph(title="Fish", text="fish fish fish"),
        ],
        gold_titles={"Cats"},
    )
    q2 = HotpotExample(
        example_id="q2",
        question="fish",
        answer="",
        question_type="comparison",
        level="hard",
        paragraphs=[
            Paragraph(title="Fish", text="fish fish fish"),
            Paragraph(title="Dogs", text="dog dog dog"),
        ],
        gold_titles={"Fish", "Unicorns"},  # Unicorns not in the corpus
    )
    return [q1, q2]


# ---- build_retriever_record -------------------------------------------------

def test_retriever_record_top_k_is_ranked_and_complete():
    ex = make_examples()[0]
    from src.dense_retriever import DenseRetriever

    ranked = DenseRetriever(ex.paragraphs, encoder=fake_encode).retrieve(ex.question, top_k=10)
    record = build_retriever_record(ranked, ex.gold_titles)

    # One entry per retrieved paragraph, ranks 1-based and contiguous.
    assert [e["rank"] for e in record["top_k"]] == list(range(1, len(ranked) + 1))
    # Each entry carries title, score, and the paragraph text (spec 4.2).
    for entry in record["top_k"]:
        assert set(entry) == {"rank", "title", "score", "text"}
        assert isinstance(entry["score"], float)
    # Ranking matches the retriever's own order.
    assert [e["title"] for e in record["top_k"]] == [p.title for p, _ in ranked]
    assert [e["text"] for e in record["top_k"]] == [p.text for p, _ in ranked]


def test_retriever_record_gold_ranks_match_evaluator():
    """gold_ranks must be forwarded from evaluator.gold_ranks verbatim,
    including None for a gold absent from the corpus."""
    ex = make_examples()[1]  # gold {Fish, Unicorns}; Unicorns absent
    from src.dense_retriever import DenseRetriever
    from src.evaluator import gold_ranks as eval_gold_ranks

    ranked = DenseRetriever(ex.paragraphs, encoder=fake_encode).retrieve(ex.question, top_k=10)
    record = build_retriever_record(ranked, ex.gold_titles)

    retrieved_titles = [p.title for p, _ in ranked]
    assert record["gold_ranks"] == eval_gold_ranks(retrieved_titles, ex.gold_titles)
    # Keys are exactly the gold set; the absent gold is present with value None.
    assert set(record["gold_ranks"]) == ex.gold_titles
    assert record["gold_ranks"]["Unicorns"] is None
    assert record["gold_ranks"]["Fish"] == 1


def test_retriever_record_metrics_cover_all_metric_ks():
    ex = make_examples()[0]
    from src.dense_retriever import DenseRetriever

    ranked = DenseRetriever(ex.paragraphs, encoder=fake_encode).retrieve(ex.question, top_k=10)
    record = build_retriever_record(ranked, ex.gold_titles)

    # The runner forwards evaluator.evaluate_example unchanged. The evaluator
    # now emits Full/Partial Recall + explicit RR horizons alongside Any Recall, so this
    # plumbing test asserts the fixed-k any_evidence_recall cutoffs the HTML
    # filter relies on are present -- not an exact key set that would break
    # whenever the evaluator gains another metric.
    any_recall_keys = {f"any_evidence_recall@{k}" for k in METRIC_KS}
    assert any_recall_keys <= set(record["metrics"])
    # 'Cats' is the top hit, so any-evidence recall is True at every cutoff.
    assert all(record["metrics"][key] for key in any_recall_keys)
    assert "mrr" not in record["metrics"]
    assert record["metrics"]["reciprocal_rank_at_10"] == 1.0
    assert record["metrics"]["reciprocal_rank_at_50"] == 1.0


# ---- build_details_record ---------------------------------------------------

def test_details_record_shape_and_sorted_gold():
    ex = make_examples()[1]
    record = build_details_record(ex, {RETRIEVER_NAME: {"stub": True}})

    assert record["example_id"] == "q2"
    assert record["question"] == "fish"
    assert record["question_type"] == "comparison"
    # gold_titles stored sorted for a stable, diff-friendly ordering.
    assert record["gold_titles"] == ["Fish", "Unicorns"]
    assert record["retrievers"] == {RETRIEVER_NAME: {"stub": True}}


# ---- run_dense_per_question -------------------------------------------------

def test_run_dense_per_question_produces_one_record_per_example():
    examples = make_examples()
    details, per_example_metrics = run_dense_per_question(examples, encoder=fake_encode)

    assert len(details) == len(examples)
    assert len(per_example_metrics) == len(examples)
    assert [r["example_id"] for r in details] == ["q1", "q2"]
    # Each record has exactly the dense retriever wired in.
    for record in details:
        assert list(record["retrievers"]) == [RETRIEVER_NAME]
    # per_example_metrics is the dense metric dict, usable by aggregate_results.
    for m in per_example_metrics:
        # any_evidence_recall cutoffs present for every fixed k (the evaluator
        # forwards extra metrics too -- see the note in
        # test_retriever_record_metrics_cover_all_metric_ks).
        assert {f"any_evidence_recall@{k}" for k in METRIC_KS} <= set(m)


def test_run_dense_per_question_empty_examples():
    details, per_example_metrics = run_dense_per_question([], encoder=fake_encode)
    assert details == []
    assert per_example_metrics == []


# ---- run_dense_pooled -------------------------------------------------------

def make_pooled_corpus():
    """Shared pooled corpus for the offline pooled tests: the union of both
    questions' retrievable paragraphs. 'Unicorns' (q2's second gold) is still
    absent, so its gold_rank must stay None even against the shared index."""
    return [
        Paragraph(title="Cats", text="cat cat cat"),
        Paragraph(title="Dogs", text="dog dog dog"),
        Paragraph(title="Fish", text="fish fish fish"),
    ]


def test_run_dense_pooled_one_record_per_example_over_shared_index():
    """Pooled path: one shared index, every question scored against it in a
    batch; record shape matches the per_question path."""
    examples = make_examples()
    details, per_example_metrics = run_dense_pooled(
        examples, make_pooled_corpus(), encoder=fake_encode
    )

    assert len(details) == len(examples)
    assert len(per_example_metrics) == len(examples)
    assert [r["example_id"] for r in details] == ["q1", "q2"]
    for record in details:
        assert list(record["retrievers"]) == [RETRIEVER_NAME]
        assert {f"any_evidence_recall@{k}" for k in METRIC_KS} <= set(
            record["retrievers"][RETRIEVER_NAME]["metrics"]
        )
    # q1's gold 'Cats' hits at rank 1; q2's gold 'Unicorns' is absent from the
    # shared corpus, so its gold_rank stays None (forwarded from evaluator).
    q1_ranks = details[0]["retrievers"][RETRIEVER_NAME]["gold_ranks"]
    q2_ranks = details[1]["retrievers"][RETRIEVER_NAME]["gold_ranks"]
    assert q1_ranks["Cats"] == 1
    assert q2_ranks["Fish"] == 1
    assert q2_ranks["Unicorns"] is None


def test_run_dense_pooled_empty_examples():
    details, per_example_metrics = run_dense_pooled(
        [], make_pooled_corpus(), encoder=fake_encode
    )
    assert details == []
    assert per_example_metrics == []


# ---- BM25 + multi-retriever merge ------------------------------------------

def test_run_bm25_per_question_matches_dense_record_shape():
    examples = make_examples()
    details, per_example_metrics = run_bm25_per_question(examples)

    assert len(details) == len(examples)
    assert len(per_example_metrics) == len(examples)
    assert all(list(record["retrievers"]) == [BM25_RETRIEVER_NAME] for record in details)
    assert details[0]["retrievers"][BM25_RETRIEVER_NAME]["gold_ranks"]["Cats"] == 1


def test_run_bm25_pooled_stores_shared_index_records():
    examples = make_examples()
    details, per_example_metrics = run_bm25_pooled(examples, make_pooled_corpus())

    assert len(details) == len(examples)
    assert len(per_example_metrics) == len(examples)
    assert details[1]["retrievers"][BM25_RETRIEVER_NAME]["gold_ranks"]["Unicorns"] is None


def test_merge_details_records_puts_dense_and_bm25_side_by_side():
    examples = make_examples()
    dense_details, _ = run_dense_per_question(examples, encoder=fake_encode)
    bm25_details, _ = run_bm25_per_question(examples)

    merged = merge_details_records(dense_details, bm25_details)

    assert [record["example_id"] for record in merged] == ["q1", "q2"]
    assert set(merged[0]["retrievers"]) == {RETRIEVER_NAME, BM25_RETRIEVER_NAME}


# ---- next_run_id ------------------------------------------------------------

def test_next_run_id_starts_at_a_when_dir_absent():
    with tempfile.TemporaryDirectory() as tmp:
        runs = os.path.join(tmp, "runs")  # does not exist
        assert next_run_id(runs, "2026-07-16") == "2026-07-16_a"


def test_next_run_id_skips_existing_letters():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "2026-07-16_a"))
        os.makedirs(os.path.join(tmp, "2026-07-16_b"))
        os.makedirs(os.path.join(tmp, "2026-07-15_a"))  # different day, ignored
        assert next_run_id(tmp, "2026-07-16") == "2026-07-16_c"


# ---- write_run (end-to-end file layout) -------------------------------------

def test_write_run_creates_three_files_with_complete_fields():
    examples = make_examples()
    details, per_example_metrics = run_dense_per_question(examples, encoder=fake_encode)
    from src.evaluator import aggregate_results

    metrics_by_retriever = {RETRIEVER_NAME: aggregate_results(per_example_metrics)}
    config = build_config(
        run_id="2026-07-16_a",
        n=len(examples),
        split="validation",
        setting="per_question",
        top_k_max=10,
        timestamp="2026-07-16T12:00:00",
        git_commit="deadbeef",
    )

    with tempfile.TemporaryDirectory() as tmp:
        run_dir = os.path.join(tmp, "2026-07-16_a")
        write_run(run_dir, details, metrics_by_retriever, config)

        # All three files exist.
        for name in ("details.jsonl", "metrics.json", "config.json"):
            assert os.path.exists(os.path.join(run_dir, name))

        # details.jsonl: one valid JSON object per line, round-trips.
        with open(os.path.join(run_dir, "details.jsonl"), encoding="utf-8") as f:
            lines = [json.loads(line) for line in f]
        assert len(lines) == len(examples)
        assert lines[0]["example_id"] == "q1"
        assert "top_k" in lines[0]["retrievers"][RETRIEVER_NAME]

        # config.json: the two traceability fields are present.
        with open(os.path.join(run_dir, "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        assert cfg["corpus_setting"] == "per_question"
        assert cfg["corpus_size"] is None  # null for per_question (own corpus per q)
        assert cfg["git_commit"] == "deadbeef"
        assert set(cfg["retrievers"]) == {RETRIEVER_NAME, BM25_RETRIEVER_NAME}

        # metrics.json: keyed by retriever, values are the aggregate recalls.
        with open(os.path.join(run_dir, "metrics.json"), encoding="utf-8") as f:
            metrics = json.load(f)
        assert set(metrics) == {RETRIEVER_NAME}
        assert {f"any_evidence_recall@{k}" for k in METRIC_KS} <= set(metrics[RETRIEVER_NAME])


def test_build_config_git_commit_none_is_preserved():
    """A non-git environment yields git_commit=None; it must survive into
    config unchanged (JSON null), not be dropped."""
    config = build_config(
        run_id="2026-07-16_a", n=1, split="validation", setting="per_question",
        top_k_max=10, timestamp="2026-07-16T12:00:00", git_commit=None,
    )
    assert config["git_commit"] is None


def test_build_config_records_pooled_corpus_size():
    """The pooled run records the shared corpus's paragraph count for
    traceability (per_question leaves it null)."""
    config = build_config(
        run_id="2026-07-17_a", n=2, split="validation", setting="pooled",
        top_k_max=50, timestamp="2026-07-17T12:00:00", git_commit=None,
        corpus_size=4937,
    )
    assert config["corpus_setting"] == "pooled"
    assert config["corpus_size"] == 4937
    assert config["top_k_max"] == 50


if __name__ == "__main__":
    test_retriever_record_top_k_is_ranked_and_complete()
    test_retriever_record_gold_ranks_match_evaluator()
    test_retriever_record_metrics_cover_all_metric_ks()
    test_details_record_shape_and_sorted_gold()
    test_run_dense_per_question_produces_one_record_per_example()
    test_run_dense_per_question_empty_examples()
    test_run_dense_pooled_one_record_per_example_over_shared_index()
    test_run_dense_pooled_empty_examples()
    test_run_bm25_per_question_matches_dense_record_shape()
    test_run_bm25_pooled_stores_shared_index_records()
    test_merge_details_records_puts_dense_and_bm25_side_by_side()
    test_next_run_id_starts_at_a_when_dir_absent()
    test_next_run_id_skips_existing_letters()
    test_write_run_creates_three_files_with_complete_fields()
    test_build_config_git_commit_none_is_preserved()
    test_build_config_records_pooled_corpus_size()
    print("All run_failure_review tests passed.")
