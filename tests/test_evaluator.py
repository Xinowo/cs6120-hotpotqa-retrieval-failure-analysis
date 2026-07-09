"""
test_evaluator.py

Tests Any Evidence Recall@k logic in evaluator.py using synthetic
retrieval results -- no BM25 or dataset needed, so this runs instantly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluator import any_evidence_recall_at_k, evaluate_example, aggregate_results


def test_any_evidence_recall_hit_within_k():
    retrieved = ["Distractor A", "Gold Paragraph", "Distractor B"]
    gold = {"Gold Paragraph", "Other Gold Paragraph"}

    assert any_evidence_recall_at_k(retrieved, gold, k=2) is True  # gold is at rank 2
    assert any_evidence_recall_at_k(retrieved, gold, k=1) is False  # not within top-1


def test_any_evidence_recall_no_hit():
    retrieved = ["Distractor A", "Distractor B", "Distractor C"]
    gold = {"Gold Paragraph"}

    assert any_evidence_recall_at_k(retrieved, gold, k=10) is False


def test_evaluate_example_multiple_k():
    retrieved = ["Distractor A", "Distractor B", "Gold Paragraph", "Distractor C"]
    gold = {"Gold Paragraph"}

    metrics = evaluate_example(retrieved, gold, k_values=[2, 5, 10])
    assert metrics == {
        "any_evidence_recall@2": False,
        "any_evidence_recall@5": True,
        "any_evidence_recall@10": True,
    }


def test_aggregate_results_averages_correctly():
    per_example = [
        {"any_evidence_recall@5": True},
        {"any_evidence_recall@5": True},
        {"any_evidence_recall@5": False},
        {"any_evidence_recall@5": False},
    ]
    overall = aggregate_results(per_example)
    assert overall["any_evidence_recall@5"] == 0.5


if __name__ == "__main__":
    test_any_evidence_recall_hit_within_k()
    test_any_evidence_recall_no_hit()
    test_evaluate_example_multiple_k()
    test_aggregate_results_averages_correctly()
    print("All evaluator tests passed.")
