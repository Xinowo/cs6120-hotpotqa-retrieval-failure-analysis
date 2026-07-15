"""
test_embedding_cache.py

Tests the Week 2 A1 cache-WRITE step: saving an embedding matrix (.npy)
plus its same-order title list plus the producing model's name to disk.
Completion criterion: after saving, reloading from disk gives back a
matrix and title list identical to the originals.

Also tests the A2 cache-LOAD step: load_embedding_cache() must return
exactly what was saved (normal path) and raise a clear ValueError when the
title list and matrix row count disagree (corrupted / half-updated cache).

Cache identity hardening (post-A3 review): meta.json records which model
produced the matrix (missing meta.json -> FileNotFoundError, so legacy
caches are rejected rather than trusted), and the matrix dtype is
preserved as saved (float32 stays float32 -- no silent float64 upcast).

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
    META_FILENAME,
    TITLES_FILENAME,
    load_embedding_cache,
    save_embedding_cache,
)

MODEL_NAME = "fake-test-model/v1"


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
        save_embedding_cache(cache_dir, titles, embeddings, MODEL_NAME)

        loaded_matrix = np.load(os.path.join(cache_dir, EMBEDDINGS_FILENAME))
        with open(os.path.join(cache_dir, TITLES_FILENAME), encoding="utf-8") as f:
            loaded_titles = json.load(f)
        with open(os.path.join(cache_dir, META_FILENAME), encoding="utf-8") as f:
            loaded_meta = json.load(f)

    # Exact equality, not allclose: nothing here should be lossy.
    assert np.array_equal(loaded_matrix, embeddings)
    assert loaded_matrix.shape == embeddings.shape
    assert loaded_titles == titles
    assert loaded_meta == {"model_name": MODEL_NAME}


def test_save_creates_missing_cache_dir():
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as tmp:
        cache_dir = os.path.join(tmp, "nested", "cache")
        save_embedding_cache(cache_dir, titles, embeddings, MODEL_NAME)

        assert os.path.isfile(os.path.join(cache_dir, EMBEDDINGS_FILENAME))
        assert os.path.isfile(os.path.join(cache_dir, TITLES_FILENAME))
        assert os.path.isfile(os.path.join(cache_dir, META_FILENAME))


def test_save_rejects_title_matrix_length_mismatch():
    titles, embeddings = make_cache_payload()
    titles_too_short = titles[:-1]

    with tempfile.TemporaryDirectory() as cache_dir:
        try:
            save_embedding_cache(cache_dir, titles_too_short, embeddings, MODEL_NAME)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for 2 titles vs 3 rows")

        # A rejected save must not leave partial cache files behind.
        assert not os.listdir(cache_dir)


def test_save_preserves_matrix_dtype():
    """float32 in -> float32 on disk -> float32 back. The cache must not
    silently upcast to float64 (double the size, no retrieval benefit)."""
    titles, embeddings = make_cache_payload()
    embeddings32 = embeddings.astype(np.float32)

    with tempfile.TemporaryDirectory() as cache_dir:
        save_embedding_cache(cache_dir, titles, embeddings32, MODEL_NAME)
        _, loaded_matrix, _ = load_embedding_cache(cache_dir)

    assert loaded_matrix.dtype == np.float32
    assert np.array_equal(loaded_matrix, embeddings32)


def test_load_returns_exactly_what_was_saved():
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as cache_dir:
        save_embedding_cache(cache_dir, titles, embeddings, MODEL_NAME)
        loaded_titles, loaded_matrix, loaded_model_name = load_embedding_cache(cache_dir)

    assert loaded_titles == titles
    assert isinstance(loaded_titles, list)
    assert np.array_equal(loaded_matrix, embeddings)
    assert loaded_model_name == MODEL_NAME


def test_load_rejects_cache_without_meta_file():
    """A legacy cache dir written before model names were recorded has no
    meta.json: load must raise FileNotFoundError (callers treat it as a
    miss and re-encode) instead of trusting vectors of unknown origin."""
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as cache_dir:
        save_embedding_cache(cache_dir, titles, embeddings, MODEL_NAME)
        os.remove(os.path.join(cache_dir, META_FILENAME))

        try:
            load_embedding_cache(cache_dir)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("expected FileNotFoundError for missing meta.json")


def test_load_rejects_title_matrix_length_mismatch():
    titles, embeddings = make_cache_payload()

    with tempfile.TemporaryDirectory() as cache_dir:
        save_embedding_cache(cache_dir, titles, embeddings, MODEL_NAME)

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
    test_save_preserves_matrix_dtype()
    test_load_returns_exactly_what_was_saved()
    test_load_rejects_cache_without_meta_file()
    test_load_rejects_title_matrix_length_mismatch()
    print("All embedding_cache tests passed.")
