"""
test_top50_export.py

Tests the top-50 export plumbing fully offline: a fake bag-of-words encoder
drives a real DenseRetriever over a small pooled corpus, so no model is
downloaded and no pooled-corpus data is needed (the offline test criterion:
a fake index, no real data required).

These tests check the EXPORT contract only -- row shape, ranking order,
truncation, CSV round-trip. The retriever's ranking correctness itself is
covered by test_dense_retriever.py.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tempfile

import numpy as np
import pandas as pd
import pytest

from src.data_loader import HotpotExample, Paragraph
from src.dense_retriever import DenseRetriever
from src.top50_export import (
    TOP50_COLUMNS,
    TOP_K,
    build_top50_rows,
    build_top50_rows_from_batches,
    write_top50_csv,
)


VOCAB = ["cat", "dog", "fish", "bird"]


def fake_encode(texts):
    """Deterministic bag-of-words encoder over VOCAB (same style as
    test_dense_retriever.py), so cosine similarities are predictable."""
    vecs = []
    for t in texts:
        tokens = t.lower().split()
        vecs.append([float(tokens.count(w)) for w in VOCAB])
    return np.array(vecs, dtype=float)


def make_pooled_index():
    """A shared pooled index over several titled paragraphs -- the setting
    top-50 export is actually for."""
    paragraphs = [
        Paragraph(title="Cats", text="cat cat cat"),
        Paragraph(title="Dogs", text="dog dog dog"),
        Paragraph(title="Fish", text="fish fish fish"),
        Paragraph(title="Birds", text="bird bird bird"),
        Paragraph(title="CatDog", text="cat dog"),
    ]
    return DenseRetriever(paragraphs, encoder=fake_encode)


def make_examples():
    """Examples carry only example_id + question for the export; their own
    .paragraphs are irrelevant in the pooled setting (the corpus lives in the
    shared index), so we leave them empty on purpose."""
    return [
        HotpotExample(
            example_id="q1", question="cat", answer="",
            question_type="bridge", level="easy", paragraphs=[],
        ),
        HotpotExample(
            example_id="q2", question="fish bird", answer="",
            question_type="comparison", level="hard", paragraphs=[],
        ),
    ]


def test_row_count_is_examples_times_top_k_when_corpus_is_large_enough():
    retriever = make_pooled_index()  # 5 paragraphs
    examples = make_examples()       # 2 questions

    rows = build_top50_rows(retriever, examples, top_k=3)

    # Corpus (5) >= top_k (3), so every example contributes exactly top_k rows.
    assert len(rows) == len(examples) * 3


def test_ranks_are_1_based_and_contiguous_per_example():
    retriever = make_pooled_index()
    examples = make_examples()

    rows = build_top50_rows(retriever, examples, top_k=3)

    for ex in examples:
        ranks = [r["rank"] for r in rows if r["example_id"] == ex.example_id]
        assert ranks == [1, 2, 3]


def test_scores_are_descending_within_each_example():
    retriever = make_pooled_index()
    examples = make_examples()

    rows = build_top50_rows(retriever, examples, top_k=4)

    for ex in examples:
        scores = [r["score"] for r in rows if r["example_id"] == ex.example_id]
        assert scores == sorted(scores, reverse=True)


def test_rows_match_retrieve_many_ordering():
    """The export must reproduce the retriever's own ranking exactly --
    same titles, same scores, same order -- for each example."""
    retriever = make_pooled_index()
    examples = make_examples()
    top_k = 4

    rows = build_top50_rows(retriever, examples, top_k=top_k)
    batches = retriever.retrieve_many([ex.question for ex in examples], top_k=top_k)

    for ex, results in zip(examples, batches):
        ex_rows = [r for r in rows if r["example_id"] == ex.example_id]
        assert [r["title"] for r in ex_rows] == [p.title for p, _ in results]
        assert [r["score"] for r in ex_rows] == [float(s) for _, s in results]


def test_top_k_larger_than_corpus_returns_all_paragraphs():
    """When top_k exceeds the corpus size, an example simply gets one row per
    paragraph (no padding, no error)."""
    retriever = make_pooled_index()  # 5 paragraphs
    examples = make_examples()       # 2 questions

    rows = build_top50_rows(retriever, examples, top_k=50)

    for ex in examples:
        ex_rows = [r for r in rows if r["example_id"] == ex.example_id]
        assert len(ex_rows) == 5  # capped at corpus size, not 50


def test_empty_examples_yields_no_rows():
    retriever = make_pooled_index()
    assert build_top50_rows(retriever, [], top_k=3) == []


def test_from_batches_matches_wrapper():
    """build_top50_rows_from_batches (fed already-retrieved batches) must yield
    exactly what the retrieve-and-shape wrapper does -- this identity is what
    lets the dense runner emit the export from its own single retrieval pass."""
    retriever = make_pooled_index()
    examples = make_examples()
    top_k = 4

    batches = retriever.retrieve_many([ex.question for ex in examples], top_k=top_k)
    assert build_top50_rows_from_batches(examples, batches) == build_top50_rows(
        retriever, examples, top_k=top_k
    )


def test_from_batches_empty_yields_no_rows():
    assert build_top50_rows_from_batches([], []) == []


def test_from_batches_length_mismatch_raises():
    """examples and batches are aligned positionally, so a length mismatch
    would silently drop or misalign questions under plain zip. It must raise
    instead -- both when there are more examples than batches and vice versa."""
    examples = make_examples()  # 2 examples

    # More examples than batches: plain zip would drop example q2.
    with pytest.raises(ValueError):
        build_top50_rows_from_batches(examples, [[]])

    # More batches than examples: plain zip would drop the extra batch.
    with pytest.raises(ValueError):
        build_top50_rows_from_batches(examples, [[], [], []])


def test_full_top_50_gives_exactly_50_rows_per_example_when_corpus_large():
    """The pooled contract: with a corpus of at least 50 paragraphs and the
    default top_k=50, every example contributes EXACTLY 50 rows (this is what
    makes the formal export's row count == n_questions * 50)."""
    paragraphs = [
        Paragraph(title=f"P{i}", text=("cat " * (i + 1))) for i in range(60)
    ]
    retriever = DenseRetriever(paragraphs, encoder=fake_encode)
    examples = make_examples()  # 2 questions

    rows = build_top50_rows(retriever, examples, top_k=TOP_K)  # TOP_K == 50

    assert len(rows) == len(examples) * 50
    for ex in examples:
        ex_rows = [r for r in rows if r["example_id"] == ex.example_id]
        assert len(ex_rows) == 50


def test_default_top_k_is_50():
    assert TOP_K == 50


def test_write_csv_round_trip_preserves_schema_and_values():
    retriever = make_pooled_index()
    examples = make_examples()
    rows = build_top50_rows(retriever, examples, top_k=3)

    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "nested", "dense_top50.csv")
        write_top50_csv(rows, out_path)  # nested dir must be created
        assert os.path.exists(out_path)

        df = pd.read_csv(out_path)
        assert list(df.columns) == TOP50_COLUMNS
        assert len(df) == len(rows)
        # example_id round-trips as a string, rank as int, score as float.
        assert df["example_id"].tolist() == [r["example_id"] for r in rows]
        assert df["rank"].tolist() == [r["rank"] for r in rows]
        np.testing.assert_allclose(
            df["score"].tolist(), [r["score"] for r in rows]
        )


def test_write_empty_rows_still_writes_header_only_csv():
    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "empty_top50.csv")
        write_top50_csv([], out_path)

        df = pd.read_csv(out_path)
        assert list(df.columns) == TOP50_COLUMNS
        assert len(df) == 0


if __name__ == "__main__":
    test_row_count_is_examples_times_top_k_when_corpus_is_large_enough()
    test_ranks_are_1_based_and_contiguous_per_example()
    test_scores_are_descending_within_each_example()
    test_rows_match_retrieve_many_ordering()
    test_top_k_larger_than_corpus_returns_all_paragraphs()
    test_empty_examples_yields_no_rows()
    test_from_batches_matches_wrapper()
    test_from_batches_empty_yields_no_rows()
    test_from_batches_length_mismatch_raises()
    test_full_top_50_gives_exactly_50_rows_per_example_when_corpus_large()
    test_default_top_k_is_50()
    test_write_csv_round_trip_preserves_schema_and_values()
    test_write_empty_rows_still_writes_header_only_csv()
    print("All top50_export tests passed.")
