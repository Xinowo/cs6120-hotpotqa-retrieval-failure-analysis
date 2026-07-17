"""Offline plumbing tests for the formal BM25 result runner."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from src.data_loader import HotpotExample, Paragraph
from src.results_schema import RESULT_COLUMNS

import run_bm25_experiment as runner


def make_examples_with_large_pool():
    paragraphs = [
        Paragraph(title=f"Distractor {i:02d}", text=f"noise token{i}")
        for i in range(55)
    ]
    paragraphs.append(Paragraph(title="Gold", text="target target target"))
    example = HotpotExample(
        example_id="q1",
        question="target",
        answer="",
        question_type="bridge",
        level="hard",
        paragraphs=paragraphs[:10],
        gold_titles={"Gold"},
    )
    return [example], paragraphs


def test_bm25_pooled_stores_top_50_and_uses_shared_schema(monkeypatch):
    examples, pooled_paragraphs = make_examples_with_large_pool()
    monkeypatch.setattr(
        runner,
        "build_pooled_corpus",
        lambda _examples: (pooled_paragraphs, []),
    )

    rows = runner.run_pooled_setting(examples)
    row = rows[0]

    assert list(row) == RESULT_COLUMNS
    assert len(row["retrieved_titles"].split(" | ")) == 50
    assert "mrr" not in row
    assert row["reciprocal_rank_at_10"] == 1.0
    assert row["reciprocal_rank_at_50"] == 1.0


def test_bm25_per_question_stores_all_available_up_to_10():
    examples, _ = make_examples_with_large_pool()

    rows = runner.run_per_question_setting(examples)
    row = rows[0]

    assert list(row) == RESULT_COLUMNS
    assert len(row["retrieved_titles"].split(" | ")) == 10
    assert row["any_evidence_recall@10"] is None
    assert row["full_evidence_recall@10"] is None
    assert row["partial_evidence_recall@10"] is None

