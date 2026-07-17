"""
test_evaluator.py

Tests Any Evidence Recall@k logic in evaluator.py using synthetic
retrieval results -- no BM25 or dataset needed, so this runs instantly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluator import any_evidence_recall_at_k, evaluate_example, aggregate_results, gold_ranks


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
        "full_evidence_recall@2": False,
        "full_evidence_recall@5": True,
        "full_evidence_recall@10": True,
        "partial_evidence_recall@2": 0.0,
        "partial_evidence_recall@5": 1.0,
        "partial_evidence_recall@10": 1.0,
        "mrr": 1 / 3,
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

# Tests for function gold_ranks:
def test_gold_ranks_hit_returns_1based_rank():
    """Test if the returned rank is 1-based."""
    retrieved = ["Distractor A", "Distractor B", "Gold Paragraph", "Distractor C"]
    gold = {"Gold Paragraph"}

    ranks = gold_ranks(retrieved, gold)

    assert ranks["Gold Paragraph"] == 3


def test_gold_ranks_first_position_is_1():
    """Test if first position starts from 1."""
    retrieved = ["Gold Paragraph", "Distractor A", "Distractor B", "Distractor C"]
    gold = {"Gold Paragraph"}

    ranks = gold_ranks(retrieved, gold)

    assert ranks["Gold Paragraph"] == 1


def test_gold_ranks_missing_gold_is_none():
    """Test if missing gold has a 'rank' of None."""
    retrieved = ["Distractor A", "Distractor B", "Distractor C"]
    gold = {"Gold Paragraph"}

    ranks = gold_ranks(retrieved, gold)

    assert ranks["Gold Paragraph"] is None

def test_gold_ranks_all_golds_are_keys():
    """Test if the returned dict has all gold titles as keys."""
    retrieved = ["Distractor A", "Gold Paragraph 1", "Distractor B", "Distractor C"]
    gold = {"Gold Paragraph 1", "Gold Paragraph 2"}

    ranks = gold_ranks(retrieved, gold)

    assert set(ranks.keys()) == gold and ranks["Gold Paragraph 2"] is None

def test_gold_ranks_multiple_hits():
    """Test if all ranks are correct."""
    retrieved = ["Distractor A", "Gold Paragraph 1", "Distractor B", "Distractor C", "Gold Paragraph 2"]
    gold = {"Gold Paragraph 1", "Gold Paragraph 2"}
    
    ranks = gold_ranks(retrieved, gold)

    assert ranks["Gold Paragraph 1"] == 2 and ranks["Gold Paragraph 2"] == 5


def test_gold_ranks_empty_retrieved():
    """Test when no text were retrieved, whether all gold title has None as 'rank'."""
    retrieved = []
    gold = {"Gold Paragraph 1", "Gold Paragraph 2"}

    ranks = gold_ranks(retrieved, gold)

    assert ranks["Gold Paragraph 1"] is None and ranks["Gold Paragraph 2"] is None


def test_gold_ranks_empty_gold():
    """Test when there's no gold title, whether the returned rank is {}."""
    retrieved = ["Distractor A"]
    gold = set()

    ranks = gold_ranks(retrieved, gold)

    assert ranks == {}


def test_gold_ranks_duplicate_title_takes_first():
    """Test if each gold title gets the first position as its rank."""
    retrieved = ["Distractor A", "Gold Paragraph 1", "Distractor B", "Distractor C", "Gold Paragraph 2", "Distractor D", "Gold Paragraph 1", "Gold Paragraph 2"]
    gold = {"Gold Paragraph 1", "Gold Paragraph 2"}

    ranks = gold_ranks(retrieved, gold)

    assert ranks["Gold Paragraph 1"] == 2 and ranks["Gold Paragraph 2"] == 5



def test_gold_ranks_does_not_mutate_input():
    """Test whether the function gold_ranks will mutate input gold_titles or not."""
    retrieved = ["Distractor A", "Gold Paragraph 1", "Distractor B", "Distractor C", "Gold Paragraph 2", "Distractor D", "Gold Paragraph 1", "Gold Paragraph 2"]
    gold = {"Gold Paragraph 1", "Gold Paragraph 2"}

    original_gold = set(gold)

    ranks = gold_ranks(retrieved, gold)

    assert gold == original_gold


if __name__ == "__main__":
    test_any_evidence_recall_hit_within_k()
    test_any_evidence_recall_no_hit()
    test_evaluate_example_multiple_k()
    test_aggregate_results_averages_correctly()
    test_gold_ranks_hit_returns_1based_rank()
    test_gold_ranks_first_position_is_1()
    test_gold_ranks_missing_gold_is_none()
    test_gold_ranks_all_golds_are_keys()
    test_gold_ranks_multiple_hits()
    test_gold_ranks_empty_retrieved()
    test_gold_ranks_empty_gold()
    test_gold_ranks_duplicate_title_takes_first()
    test_gold_ranks_does_not_mutate_input()
    print("All evaluator tests passed.")
