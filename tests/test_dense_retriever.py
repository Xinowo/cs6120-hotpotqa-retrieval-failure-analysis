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

import tempfile

import numpy as np

from src.data_loader import Paragraph
from src.dense_retriever import DenseRetriever
from src.embedding_cache import META_FILENAME


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


def make_counting_encoder():
    """Wraps fake_encode with a call counter, so tests can assert exactly
    how many times the retriever actually invoked the encoder (Week 2 A3:
    a cache hit must mean ZERO encoder calls at construction time)."""
    calls = {"n": 0}

    def counting_encode(texts):
        calls["n"] += 1
        return fake_encode(texts)

    return counting_encode, calls


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


def test_cache_hit_skips_encoding_entirely():
    """Week 2 A3 completion criterion: building a second retriever over the
    same corpus with the same cache dir must make ZERO encoder calls."""
    with tempfile.TemporaryDirectory() as cache_dir:
        # First build: cold cache, encoder must run (once, for the docs).
        enc1, calls1 = make_counting_encoder()
        first = DenseRetriever(make_paragraphs(), encoder=enc1, cache_dir=cache_dir)
        assert calls1["n"] == 1

        # Second build: warm cache, encoder must NOT run at all.
        enc2, calls2 = make_counting_encoder()
        second = DenseRetriever(make_paragraphs(), encoder=enc2, cache_dir=cache_dir)
        assert calls2["n"] == 0

        # And the cached index must behave identically to the fresh one.
        assert np.array_equal(second.doc_embeddings, first.doc_embeddings)
        assert second.retrieve_titles("cat", top_k=3) == first.retrieve_titles(
            "cat", top_k=3
        )

        # Embeddings stay float32 end to end (no float64 upcast in either
        # the fresh-encode path or the cache round-trip).
        assert first.doc_embeddings.dtype == np.float32
        assert second.doc_embeddings.dtype == np.float32


def test_stale_cache_for_different_corpus_is_reencoded_and_overwritten():
    """A cache dir written for one corpus must not be silently reused for a
    different one: titles mismatch -> re-encode and overwrite the cache."""
    other_paragraphs = [
        Paragraph(title="Birds", text="bird bird"),
        Paragraph(title="Fish", text="fish fish"),
    ]

    with tempfile.TemporaryDirectory() as cache_dir:
        DenseRetriever(make_paragraphs(), encoder=fake_encode, cache_dir=cache_dir)

        # Same cache dir, different corpus: must re-encode, not reuse.
        enc2, calls2 = make_counting_encoder()
        retriever = DenseRetriever(other_paragraphs, encoder=enc2, cache_dir=cache_dir)
        assert calls2["n"] == 1
        assert retriever.retrieve_titles("bird", top_k=1) == ["Birds"]

        # The overwritten cache now serves the NEW corpus as a hit.
        enc3, calls3 = make_counting_encoder()
        DenseRetriever(other_paragraphs, encoder=enc3, cache_dir=cache_dir)
        assert calls3["n"] == 0


def test_cache_for_different_model_is_treated_as_miss():
    """Same corpus, same cache dir, different model_name: the cached
    vectors live in a different embedding space, so this must be a MISS
    (re-encode + overwrite), never a silent reuse."""
    with tempfile.TemporaryDirectory() as cache_dir:
        DenseRetriever(
            make_paragraphs(), encoder=fake_encode,
            model_name="model-a", cache_dir=cache_dir,
        )

        # Different model over the same titles: must re-encode.
        enc2, calls2 = make_counting_encoder()
        DenseRetriever(
            make_paragraphs(), encoder=enc2,
            model_name="model-b", cache_dir=cache_dir,
        )
        assert calls2["n"] == 1

        # The overwritten cache now serves model-b as a hit...
        enc3, calls3 = make_counting_encoder()
        DenseRetriever(
            make_paragraphs(), encoder=enc3,
            model_name="model-b", cache_dir=cache_dir,
        )
        assert calls3["n"] == 0

        # ...and model-a no longer hits.
        enc4, calls4 = make_counting_encoder()
        DenseRetriever(
            make_paragraphs(), encoder=enc4,
            model_name="model-a", cache_dir=cache_dir,
        )
        assert calls4["n"] == 1


def test_legacy_cache_without_meta_is_treated_as_miss():
    """A cache dir from before model names were recorded (no meta.json)
    must be re-encoded and overwritten, not trusted blindly."""
    with tempfile.TemporaryDirectory() as cache_dir:
        DenseRetriever(make_paragraphs(), encoder=fake_encode, cache_dir=cache_dir)
        os.remove(os.path.join(cache_dir, META_FILENAME))

        enc2, calls2 = make_counting_encoder()
        DenseRetriever(make_paragraphs(), encoder=enc2, cache_dir=cache_dir)
        assert calls2["n"] == 1

        # The rewrite restored meta.json, so the next build is a hit again.
        enc3, calls3 = make_counting_encoder()
        DenseRetriever(make_paragraphs(), encoder=enc3, cache_dir=cache_dir)
        assert calls3["n"] == 0


def test_no_cache_dir_keeps_week1_behavior():
    """Without cache_dir, every construction encodes (Week 1 behavior)."""
    enc, calls = make_counting_encoder()
    DenseRetriever(make_paragraphs(), encoder=enc)
    DenseRetriever(make_paragraphs(), encoder=enc)
    assert calls["n"] == 2


if __name__ == "__main__":
    test_retrieve_titles_ranks_most_similar_first()
    test_top_k_limits_number_of_results()
    test_retrieve_returns_paragraph_score_tuples_descending()
    test_cache_hit_skips_encoding_entirely()
    test_stale_cache_for_different_corpus_is_reencoded_and_overwritten()
    test_cache_for_different_model_is_treated_as_miss()
    test_legacy_cache_without_meta_is_treated_as_miss()
    test_no_cache_dir_keeps_week1_behavior()
    print("All dense_retriever tests passed.")
