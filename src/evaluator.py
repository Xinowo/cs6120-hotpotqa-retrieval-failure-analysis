"""
evaluator.py

Week 2 scope: Full Evidence Recall@k, Partial Evidence Recall@k, and MRR,
built on top of Week 1's Any Evidence Recall@k and the gold_ranks() helper.

Definitions (per the project scope doc):
  - Any Evidence Recall@k: at least ONE mapped gold evidence paragraph
    appears in the top-k retrieved passages.
  - Full Evidence Recall@k: ALL mapped gold evidence paragraphs appear in
    the top-k retrieved passages. This is the stricter, more meaningful
    metric for multi-hop QA -- a bridge question needs BOTH hops covered.
  - Partial Evidence Recall@k: the FRACTION of gold evidence paragraphs
    that appear in the top-k retrieved passages (0.0 to 1.0). Explains the
    gap between Any and Full -- e.g. 0.5 means exactly one of two gold
    paragraphs (for a 2-hop question) was found.
  - MRR (Mean Reciprocal Rank): 1 / rank of the FIRST gold evidence
    paragraph found (rank 1 = top of the list), averaged across examples.
    0 if no gold paragraph was retrieved at all. Reported without a k
    cutoff -- MRR looks at the retriever's full ranked list.
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
    """
    top_k_titles = set(retrieved_titles[:k])
    return len(top_k_titles & gold_titles) > 0


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
    """
    ranks: Dict[str, Optional[int]] = {gold_title: None for gold_title in gold_titles}

    for i, title in enumerate(retrieved_titles):
        if title in gold_titles and ranks[title] is None:
            ranks[title] = i + 1

    return ranks


def full_evidence_recall_at_k(
    retrieved_titles: List[str],
    gold_titles: Set[str],
    k: int,
) -> bool:
    """
    Returns True only if EVERY gold evidence title is found within the
    top-k retrieved titles. Stricter than any_evidence_recall_at_k --
    this is the metric that actually reflects multi-hop success, since a
    bridge question needs both hops' evidence to be usable downstream.

    Edge case: if gold_titles is empty, we count this as vacuously True
    (no requirement to satisfy) -- but HotpotQA questions always have at
    least one gold title, so this shouldn't come up in practice.
    """
    if not gold_titles:
        return True
    ranks = gold_ranks(retrieved_titles, gold_titles)
    return all(rank is not None and rank <= k for rank in ranks.values())


def partial_evidence_recall_at_k(
    retrieved_titles: List[str],
    gold_titles: Set[str],
    k: int,
) -> float:
    """
    Returns the fraction (0.0-1.0) of gold evidence titles found within
    the top-k retrieved titles. For a typical 2-gold-title bridge question,
    this can only be 0.0, 0.5, or 1.0 -- the 0.5 case is exactly what
    separates "any evidence" success from "full evidence" success, and is
    the number to point to when explaining that gap.
    """
    if not gold_titles:
        return 1.0
    ranks = gold_ranks(retrieved_titles, gold_titles)
    hits = sum(1 for rank in ranks.values() if rank is not None and rank <= k)
    return hits / len(gold_titles)


def mrr_for_example(
    retrieved_titles: List[str],
    gold_titles: Set[str],
) -> float:
    """
    Mean Reciprocal Rank for a single example: 1 / rank of the FIRST gold
    evidence title found anywhere in retrieved_titles (no k cutoff -- this
    looks at the retriever's whole ranked list). Returns 0.0 if no gold
    title was retrieved at all.
    """
    ranks = gold_ranks(retrieved_titles, gold_titles)
    found_ranks = [rank for rank in ranks.values() if rank is not None]
    if not found_ranks:
        return 0.0
    return 1.0 / min(found_ranks)


def evaluate_example(
    retrieved_titles: List[str],
    gold_titles: Set[str],
    k_values: List[int] = [2, 5, 10],
) -> Dict[str, object]:
    """
    Computes all Week 2 metrics for one example: Any/Full/Partial Evidence
    Recall@k for every k in k_values, plus MRR (single value, no k).

    Returns a dict like:
        {
          "any_evidence_recall@2": False, "any_evidence_recall@5": True, ...,
          "full_evidence_recall@2": False, "full_evidence_recall@5": False, ...,
          "partial_evidence_recall@2": 0.5, "partial_evidence_recall@5": 1.0, ...,
          "mrr": 0.333,
        }
    """
    metrics: Dict[str, object] = {}

    for k in k_values:
        metrics[f"any_evidence_recall@{k}"] = any_evidence_recall_at_k(retrieved_titles, gold_titles, k)
        metrics[f"full_evidence_recall@{k}"] = full_evidence_recall_at_k(retrieved_titles, gold_titles, k)
        metrics[f"partial_evidence_recall@{k}"] = partial_evidence_recall_at_k(retrieved_titles, gold_titles, k)

    metrics["mrr"] = mrr_for_example(retrieved_titles, gold_titles)

    return metrics


def aggregate_results(per_example_results: List[Dict[str, object]]) -> Dict[str, float]:
    """
    Averages per-example metric values into overall scores.

    Works for boolean metrics (True/False averages to a 0.0-1.0 rate) and
    float metrics (partial recall, MRR) the same way -- summing bools and
    floats both work fine in Python, so no special-casing is needed here.
    """
    if not per_example_results:
        return {}

    metric_names = per_example_results[0].keys()
    n = len(per_example_results)

    return {
        metric: sum(r[metric] for r in per_example_results) / n
        for metric in metric_names
    }
