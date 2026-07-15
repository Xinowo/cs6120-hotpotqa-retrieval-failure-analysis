"""
test_embedding_cache.py

Tests the Week 2 A1 cache-WRITE step: saving an embedding matrix (.npy)
plus its same-order title list to disk. Completion criterion: after
saving, reloading from disk gives back a matrix and title list identical
to the originals.

Also tests the A2 cache-LOAD step: load_embedding_cache() must return
exactly what was saved (normal path) and raise a clear ValueError when the
title list and matrix row count disagree (corrupted / half-updated cache).

Fully offline: no encoder or model involved -- the cache layer only deals
with an already-computed matrix and a list of titles. The A1 round-trip
test below reloads with raw np.load / json.load on purpose, so it verifies
the on-disk format itself independently of the loader.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import tempfile

import numpy as np

from src.embedding_cache import (
    EMBEDDINGS_FILENAME,
    TITLES_FILENAME,
    load_embedding_cache,
    save_embedding_cache,
)


def make_cache_payload():
    """A small, distinctive matrix + titles (incl. non-ASCII) so any
    reordering, truncation or encoding bug breaks the equality checks."""
    embeddings = np.array(
        [
            [0.1, -2.5, 3.0, 0.0],
            [4.0, 5.5, -6.25, 1.0],
            [-7.0, 8.0, 9.125, 2.0],
        ],
        dtype=float,
    )
    titles = ["Scott Derrickson", "Ed Wood (film)", "Šarūnas Marčiulionis"]
    return titles, embeddings


def test_save_then_reload_is_identical():
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as cache_dir:
        save_embedding_cache(cache_dir, titles, embeddings)

        loaded_matrix = np.load(os.path.join(cache_dir, EMBEDDINGS_FILENAME))
        with open(os.path.join(cache_dir, TITLES_FILENAME), encoding="utf-8") as f:
            loaded_titles = json.load(f)

    # Exact equality, not allclose: nothing here should be lossy.
    assert np.array_equal(loaded_matrix, embeddings)
    assert loaded_matrix.shape == embeddings.shape
    assert loaded_titles == titles


def test_save_creates_missing_cache_dir():
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = os.path.join(tmp, "nested", "cache")
        save_embedding_cache(cache_dir, titles, embeddings)

        assert os.path.isfile(os.path.join(cache_dir, EMBEDDINGS_FILENAME))
        assert os.path.isfile(os.path.join(cache_dir, TITLES_FILENAME))


def test_save_rejects_title_matrix_length_mismatch():
    titles, embeddings = make_cache_payload()
    titles_too_short = titles[:-1]

    with tempfile.TemporaryDirectory() as cache_dir:
        try:
            save_embedding_cache(cache_dir, titles_too_short, embeddings)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for 2 titles vs 3 rows")

        # A rejected save must not leave partial cache files behind.
        assert not os.listdir(cache_dir)


def test_load_returns_exactly_what_was_saved():
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as cache_dir:
        save_embedding_cache(cache_dir, titles, embeddings)
        loaded_titles, loaded_matrix = load_embedding_cache(cache_dir)

    assert loaded_titles == titles
    assert isinstance(loaded_titles, list)
    assert np.array_equal(loaded_matrix, embeddings)


def test_load_rejects_title_matrix_length_mismatch():
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as cache_dir:
        save_embedding_cache(cache_dir, titles, embeddings)

        # Corrupt the cache: drop one title so titles.json says 2 but the
        # matrix still has 3 rows (simulates a half-updated cache dir).
        titles_path = os.path.join(cache_dir, TITLES_FILENAME)
        with open(titles_path, "w", encoding="utf-8") as f:
            json.dump(titles[:-1], f, ensure_ascii=False)

        try:
            load_embedding_cache(cache_dir)
        except ValueError as e:
            # The error must say what is wrong, not just that something is.
            assert "2" in str(e) and "3" in str(e)
        else:
            raise AssertionError("expected ValueError for 2 titles vs 3 rows")


if __name__ == "__main__":
    test_save_then_reload_is_identical()
    test_save_creates_missing_cache_dir()
    test_save_rejects_title_matrix_length_mismatch()
    test_load_returns_exactly_what_was_saved()
    test_load_rejects_title_matrix_length_mismatch()
    print("All embedding_cache tests passed.")
