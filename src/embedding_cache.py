"""
embedding_cache.py

Week 2 (A group): on-disk cache for paragraph embeddings, so the pooled
corpus is encoded once and reused across runs instead of re-encoding
~thousands of paragraphs every time.

Cache layout -- one directory holding three files that MUST stay in sync:

    <cache_dir>/embeddings.npy   float matrix, one row per paragraph
    <cache_dir>/titles.json      list of paragraph titles, same order as
                                 the matrix rows (row i <-> titles[i])
    <cache_dir>/meta.json        {"model_name": ...} -- which encoder
                                 produced the matrix

The row/title alignment is the whole contract: retrieval returns row
indices, and titles.json is how those indices map back to paragraph
titles for evaluation. That is why save refuses mismatched lengths up
front, and why load-time validation (task A2) re-checks it.

meta.json guards the other half of the cache's identity: the same titles
encoded by a DIFFERENT model are different vectors, so a cache is only
valid for the (corpus, model) pair it was built from. Callers compare the
loaded model_name against their own and treat a mismatch as a cache miss.

The matrix is stored with whatever dtype the caller passes in (MiniLM
natively produces float32; forcing float64 would double the file size for
no retrieval benefit).

This module is deliberately encoder-agnostic: it stores an
already-computed matrix and never imports sentence-transformers, so all
of its tests run offline.
"""

import json
from pathlib import Path
from typing import List, Sequence, Tuple

import numpy as np

EMBEDDINGS_FILENAME = "embeddings.npy"
TITLES_FILENAME = "titles.json"
META_FILENAME = "meta.json"


def save_embedding_cache(
    cache_dir,
    titles: Sequence[str],
    embeddings: np.ndarray,
    model_name: str,
) -> None:
    """
    Persists an embedding matrix, its same-order title list, and the name
    of the model that produced it under cache_dir (created if missing).

    The matrix dtype is preserved as passed in (no float64 upcast).

    Raises ValueError -- before writing anything -- if the matrix is not
    2D or the number of titles differs from the number of matrix rows,
    so a broken pair can never end up on disk.
    """
    matrix = np.asarray(embeddings)
    if matrix.ndim != 2:
        raise ValueError(
            f"embeddings must be a 2D (n_paragraphs, dim) matrix, got shape {matrix.shape}"
        )
    if len(titles) != matrix.shape[0]:
        raise ValueError(
            f"got {len(titles)} titles for {matrix.shape[0]} embedding rows; "
            "titles[i] must correspond to matrix row i"
        )

    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    np.save(cache_path / EMBEDDINGS_FILENAME, matrix)
    with open(cache_path / TITLES_FILENAME, "w", encoding="utf-8") as f:
        json.dump(list(titles), f, ensure_ascii=False, indent=0)
    with open(cache_path / META_FILENAME, "w", encoding="utf-8") as f:
        json.dump({"model_name": model_name}, f, ensure_ascii=False, indent=0)


def load_embedding_cache(cache_dir) -> Tuple[List[str], np.ndarray, str]:
    """
    Loads the (titles, embedding matrix, model_name) triple previously
    written by save_embedding_cache().

    Raises FileNotFoundError if any cache file is missing -- including
    meta.json, so a legacy cache written before model names were recorded
    is rejected here and treated as a miss by the caller rather than
    trusted blindly. Raises ValueError if the title count and matrix row
    count disagree -- a mismatched pair means the row<->title alignment
    contract is broken (e.g. a half-updated cache dir), and using it
    would silently map retrieval results to the wrong paragraph titles.
    """
    cache_path = Path(cache_dir)

    matrix = np.load(cache_path / EMBEDDINGS_FILENAME)
    with open(cache_path / TITLES_FILENAME, encoding="utf-8") as f:
        titles = json.load(f)
    with open(cache_path / META_FILENAME, encoding="utf-8") as f:
        model_name = json.load(f)["model_name"]

    if len(titles) != matrix.shape[0]:
        raise ValueError(
            f"corrupted embedding cache at {cache_path}: {TITLES_FILENAME} has "
            f"{len(titles)} titles but {EMBEDDINGS_FILENAME} has {matrix.shape[0]} rows"
        )
    return titles, matrix, model_name
