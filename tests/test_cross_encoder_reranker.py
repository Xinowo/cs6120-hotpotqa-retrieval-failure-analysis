"""
test_cross_encoder_reranker.py

Tests the CrossEncoderReranker RANKING logic without downloading any
cross-encoder model. We inject a small deterministic fake scorer (query/passage
word overlap) so relevance scores are predictable -- this keeps the test fast
and fully offline, matching the style of test_dense_retriever.py.

The real model (cross-encoder/ms-marco-MiniLM-L-6-v2) is only built lazily when
no scorer is injected, so it is never touched here.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from src.data_loader import Paragraph
from src.cross_encoder_reranker import CrossEncoderReranker


def fake_score(pairs):
    """Deterministic relevance scorer: count how many query words appear in
    the passage (with multiplicity), so a passage sharing more query terms
    scores higher. Returns one float per (query, passage_text) pair."""
    scores = []
    for query, text in pairs:
        query_words = set(query.lower().split())
        passage_tokens = text.lower().split()
        scores.append(float(sum(1 for tok in passage_tokens if tok in query_words)))
    return scores


def make_counting_scorer():
    """Wraps fake_score with a call counter, so tests can assert the reranker
    scores ALL candidates for a query in a single batched call, not one call
    per candidate."""
    calls = {"n": 0}

    def counting_score(pairs):
        calls["n"] += 1
        return fake_score(pairs)

    return counting_score, calls


def make_candidates():
    """A candidate shortlist deliberately NOT in relevance order for the query
    'cat', so a correct rerank must reorder it."""
    return [
        Paragraph(title="Dogs", text="dog dog dog"),
        Paragraph(title="Cats", text="cat cat cat"),
        Paragraph(title="CatDog", text="cat dog"),
        Paragraph(title="Birds", text="bird bird"),
    ]


def test_rerank_orders_by_score_descending():
    reranker = CrossEncoderReranker(scorer=fake_score)

    results = reranker.rerank("cat", make_candidates(), top_k=4)

    # "cat cat cat" (score 3) > "cat dog" (score 1) > the two with no "cat".
    titles = [p.title for p, _ in results]
    assert titles[0] == "Cats"
    assert titles[1] == "CatDog"

    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)


def test_rerank_reorders_a_shuffled_shortlist():
    """The whole point of a reranker: candidates arrive in the retriever's
    order, and rerank must reorder them by the cross-encoder's own score."""
    reranker = CrossEncoderReranker(scorer=fake_score)

    incoming = [p.title for p in make_candidates()]
    reranked = reranker.rerank_titles("cat", make_candidates(), top_k=4)

    assert incoming[0] == "Dogs"          # shortlist starts with a non-match
    assert reranked[0] == "Cats"          # rerank promotes the real match
    assert reranked != incoming           # order actually changed


def test_rerank_top_k_truncates():
    reranker = CrossEncoderReranker(scorer=fake_score)

    assert len(reranker.rerank("cat", make_candidates(), top_k=2)) == 2
    assert len(reranker.rerank("cat", make_candidates(), top_k=1)) == 1


def test_rerank_top_k_larger_than_candidates_returns_all():
    reranker = CrossEncoderReranker(scorer=fake_score)

    results = reranker.rerank("cat", make_candidates(), top_k=100)

    assert len(results) == len(make_candidates())


def test_rerank_returns_paragraph_score_tuples():
    reranker = CrossEncoderReranker(scorer=fake_score)

    results = reranker.rerank("cat", make_candidates(), top_k=4)

    for paragraph, score in results:
        assert isinstance(paragraph, Paragraph)
        assert isinstance(score, float)


def test_rerank_scores_all_candidates_in_one_call():
    """Efficiency contract: scoring N candidates costs ONE scorer call, not N
    (one batched forward pass), mirroring DenseRetriever.retrieve_many."""
    scorer, calls = make_counting_scorer()
    reranker = CrossEncoderReranker(scorer=scorer)
    assert calls["n"] == 0  # constructing the reranker scores nothing

    reranker.rerank("cat", make_candidates(), top_k=4)
    assert calls["n"] == 1  # all four candidates in a single batch call


def test_rerank_empty_candidates_returns_empty_without_scoring():
    scorer, calls = make_counting_scorer()
    reranker = CrossEncoderReranker(scorer=scorer)

    assert reranker.rerank("cat", [], top_k=4) == []
    assert calls["n"] == 0  # nothing to score, so the scorer is never called


def test_rerank_ties_keep_incoming_order():
    """Equal scores must preserve the candidates' incoming order (stable
    sort), matching the retrievers' tie-breaking."""
    reranker = CrossEncoderReranker(scorer=fake_score)

    # None of these share a word with the query, so every score is 0 (a tie).
    tied = [
        Paragraph(title="First", text="alpha"),
        Paragraph(title="Second", text="beta"),
        Paragraph(title="Third", text="gamma"),
    ]

    titles = reranker.rerank_titles("cat", tied, top_k=3)
    assert titles == ["First", "Second", "Third"]


def test_rerank_titles_matches_rerank():
    reranker = CrossEncoderReranker(scorer=fake_score)

    tuples = reranker.rerank("cat", make_candidates(), top_k=3)
    titles = reranker.rerank_titles("cat", make_candidates(), top_k=3)

    assert titles == [p.title for p, _ in tuples]


def test_rerank_accepts_exact_scorer_cardinality():
    """Legal control for the cardinality guard: exactly one score per candidate
    is accepted and reranks all of them."""
    reranker = CrossEncoderReranker(scorer=fake_score)

    results = reranker.rerank("cat", make_candidates(), top_k=4)

    assert len(results) == len(make_candidates())


def test_rerank_rejects_scorer_returning_too_few_scores():
    """A scorer that under-returns must fail loudly: otherwise zip would
    silently drop candidates and shorten the reranked list."""
    def short_scorer(pairs):
        return [1.0]  # one score regardless of how many candidates

    reranker = CrossEncoderReranker(scorer=short_scorer)
    with pytest.raises(ValueError):
        reranker.rerank("cat", make_candidates(), top_k=4)


def test_rerank_rejects_scorer_returning_too_many_scores():
    """A scorer that over-returns must also fail loudly rather than silently
    discard the extra scores."""
    def long_scorer(pairs):
        return [1.0] * (len(pairs) + 1)

    reranker = CrossEncoderReranker(scorer=long_scorer)
    with pytest.raises(ValueError):
        reranker.rerank("cat", make_candidates(), top_k=4)


if __name__ == "__main__":
    test_rerank_orders_by_score_descending()
    test_rerank_reorders_a_shuffled_shortlist()
    test_rerank_top_k_truncates()
    test_rerank_top_k_larger_than_candidates_returns_all()
    test_rerank_returns_paragraph_score_tuples()
    test_rerank_scores_all_candidates_in_one_call()
    test_rerank_empty_candidates_returns_empty_without_scoring()
    test_rerank_ties_keep_incoming_order()
    test_rerank_titles_matches_rerank()
    test_rerank_accepts_exact_scorer_cardinality()
    test_rerank_rejects_scorer_returning_too_few_scores()
    test_rerank_rejects_scorer_returning_too_many_scores()
    print("All cross_encoder_reranker tests passed.")
