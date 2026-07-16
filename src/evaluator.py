"""
evaluator.py

Week 1 scope: Any Evidence Recall@k / Evidence Hit@k only.

Definition (per the project scope doc): Any Evidence Recall@k is whether
AT LEAST ONE mapped gold evidence paragraph appears in the top-k retrieved
passages. This is a basic hit metric -- it does NOT check whether ALL
required evidence was found. Full Evidence Recall@k and Partial Evidence
Recall@k (Week 2 scope) will check that.
"""

from typing import List, Set, Dict, Optional


def any_evidence_recall_at_k(
    retrieved_titles: List[str],
    gold_titles: Set[str],
    k: int,
) -> bool:
    """
    Returns True if at least one gold evidence title appears in the top-k
    retrieved titles (ranked, highest-scored first).

    retrieved_titles: ranked list of paragraph titles from a retriever,
                       e.g. BM25Retriever.retrieve_titles(question, top_k=k)
    gold_titles: the set of gold evidence paragraph titles for this question
    k: cutoff -- only the first k retrieved titles are considered
    """
    top_k_titles = set(retrieved_titles[:k])
    return len(top_k_titles & gold_titles) > 0


def evaluate_example(
    retrieved_titles: List[str],
    gold_titles: Set[str],
    k_values: List[int] = [2, 5, 10],
) -> Dict[str, bool]:
    """
    Computes Any Evidence Recall@k for every k in k_values, for one example.

    Returns a dict like:
        {"any_evidence_recall@2": False, "any_evidence_recall@5": True, "any_evidence_recall@10": True}
    """
    return {
        f"any_evidence_recall@{k}": any_evidence_recall_at_k(retrieved_titles, gold_titles, k)
        for k in k_values
    }


def aggregate_results(per_example_results: List[Dict[str, bool]]) -> Dict[str, float]:
    """
    Averages per-example True/False results into overall recall rates.

    Input: a list of dicts, one per example, each produced by evaluate_example().
    Output: a dict mapping each metric name to its average (0.0-1.0) across
    all examples.
    """
    if not per_example_results:
        return {}

    metric_names = per_example_results[0].keys()
    n = len(per_example_results)

    return {
        metric: sum(int(r[metric]) for r in per_example_results) / n
        for metric in metric_names
    }


def gold_ranks(
    retrieved_titles: List[str],
    gold_titles: Set[str],
) -> Dict[str, Optional[int]]:
    """
    Returns the 1-based rank of each gold title in the ranked retrieved
    titles (rank 1 = first / highest-scored), or None if it was not
    retrieved. If a gold appears more than once, its first occurrence is used.

    The output always has exactly gold_titles as keys: a gold that was not
    retrieved maps to None, never omitted. No cutoff is applied -- absence
    from retrieved_titles is what means "not in top_k_max".

    retrieved_titles: ranked titles, highest-scored first (same list passed
                       to any_evidence_recall_at_k)
    gold_titles: the gold evidence titles for this question
    """

    ranks = {
        gold_title: None for gold_title in gold_titles
    }

    for i, title in enumerate(retrieved_titles):
        if title in gold_titles and ranks[title] is None:
            ranks[title] = i + 1

    return ranks

