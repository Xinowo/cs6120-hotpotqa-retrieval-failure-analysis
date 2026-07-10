"""
test_dense_retriever.py

Tests the DenseRetriever RANKING logic without downloading any embedding
model. We inject a small deterministic fake encoder (bag-of-words over a
fixed vocab) so cosine similarities are predictable -- this keeps the test
fast and fully offline, matching the style of the other tests here.

The real embedding model (sentence-transformers/all-MiniLM-L6-v2) is only
built lazily when no encoder is injected, so it is never touched here.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np

from src.data_loader import Paragraph
from src.dense_retriever import DenseRetriever


VOCAB = ["cat", "dog", "fish", "bird"]


def fake_encode(texts):
    """Deterministic bag-of-words encoder over VOCAB. Returns an
    (n_texts, len(VOCAB)) float array so cosine similarity is predictable."""
    vecs = []
    for t in texts:
        tokens = t.lower().split()
        vecs.append([float(tokens.count(w)) for w in VOCAB])
    return np.array(vecs, dtype=float)


def make_paragraphs():
    return [
        Paragraph(title="Cats", text="cat cat"),
        Paragraph(title="Dogs", text="dog dog"),
        Paragraph(title="SeaAndSky", text="fish bird"),
    ]


def test_retrieve_titles_ranks_most_similar_first():
    retriever = DenseRetriever(make_paragraphs(), encoder=fake_encode)

    titles = retriever.retrieve_titles("cat", top_k=3)

    # Query "cat" is most similar to the "Cats" paragraph.
    assert titles[0] == "Cats"


def test_top_k_limits_number_of_results():
    retriever = DenseRetriever(make_paragraphs(), encoder=fake_encode)

    assert len(retriever.retrieve_titles("dog", top_k=2)) == 2
    assert len(retriever.retrieve("dog", top_k=1)) == 1


def test_retrieve_returns_paragraph_score_tuples_descending():
    retriever = DenseRetriever(make_paragraphs(), encoder=fake_encode)

    results = retriever.retrieve("fish", top_k=3)

    # Each result is a (Paragraph, float score) pair.
    for paragraph, score in results:
        assert isinstance(paragraph, Paragraph)
        assert isinstance(score, float)

    # Scores must be sorted highest-first.
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)

    # "fish" query should rank the fish/bird paragraph top.
    assert results[0][0].title == "SeaAndSky"


if __name__ == "__main__":
    test_retrieve_titles_ranks_most_similar_first()
    test_top_k_limits_number_of_results()
    test_retrieve_returns_paragraph_score_tuples_descending()
    print("All dense_retriever tests passed.")
