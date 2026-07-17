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
    METRIC_KS,
    RETRIEVER_NAME,
    build_config,
    build_details_record,
    build_retriever_record,
    next_run_id,
    run_dense_per_question,
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

    assert set(record["metrics"]) == {f"any_evidence_recall@{k}" for k in METRIC_KS}
    # 'Cats' is the top hit, so recall is True at every cutoff.
    assert all(record["metrics"].values())


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
        assert set(m) == {f"any_evidence_recall@{k}" for k in METRIC_KS}


def test_run_dense_per_question_empty_examples():
    details, per_example_metrics = run_dense_per_question([], encoder=fake_encode)
    assert details == []
    assert per_example_metrics == []


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
        assert cfg["git_commit"] == "deadbeef"
        assert cfg["retrievers"] == {RETRIEVER_NAME: cfg["retrievers"][RETRIEVER_NAME]}

        # metrics.json: keyed by retriever, values are the aggregate recalls.
        with open(os.path.join(run_dir, "metrics.json"), encoding="utf-8") as f:
            metrics = json.load(f)
        assert set(metrics) == {RETRIEVER_NAME}
        assert set(metrics[RETRIEVER_NAME]) == {f"any_evidence_recall@{k}" for k in METRIC_KS}


def test_build_config_git_commit_none_is_preserved():
    """A non-git environment yields git_commit=None; it must survive into
    config unchanged (JSON null), not be dropped."""
    config = build_config(
        run_id="2026-07-16_a", n=1, split="validation", setting="per_question",
        top_k_max=10, timestamp="2026-07-16T12:00:00", git_commit=None,
    )
    assert config["git_commit"] is None


if __name__ == "__main__":
    test_retriever_record_top_k_is_ranked_and_complete()
    test_retriever_record_gold_ranks_match_evaluator()
    test_retriever_record_metrics_cover_all_metric_ks()
    test_details_record_shape_and_sorted_gold()
    test_run_dense_per_question_produces_one_record_per_example()
    test_run_dense_per_question_empty_examples()
    test_next_run_id_starts_at_a_when_dir_absent()
    test_next_run_id_skips_existing_letters()
    test_write_run_creates_three_files_with_complete_fields()
    test_build_config_git_commit_none_is_preserved()
    print("All run_failure_review tests passed.")
