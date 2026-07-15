"""
dense_retriever.py

Xin's module: dense (embedding-based) retrieval, the semantic counterpart
to Jiajun's BM25 lexical retriever in retrievers.py.

It mirrors BM25Retriever's interface exactly -- same __init__(paragraphs),
retrieve(query, top_k) and retrieve_titles(query, top_k) -- so it is a
drop-in swap in the experiment/debug scripts and the two methods can be
compared fairly.

Design choices:
  - Corpus granularity is the caller's choice: per-question (~10 context
    paragraphs, Week 1 default) or a pooled shared corpus (Week 2).
  - Model: sentence-transformers/all-MiniLM-L6-v2, per the project plan.
  - Similarity: cosine similarity, computed as a dot product of
    L2-normalized embeddings.
  - Embedding cache (Week 2 A3): pass `cache_dir` to persist the
    (normalized) document embedding matrix + title list via
    embedding_cache.py. On a warm cache that matches this corpus, the
    encoder is not called at all during construction -- for the real
    model that means no model load until the first query.
  - Cache identity is the (title list, model_name) pair: a cache written
    for a different corpus OR by a different model is a miss, never
    silently reused. If you inject a custom encoder AND use a cache_dir,
    pass a model_name that identifies that encoder.
  - Embeddings are kept as float32 (MiniLM's native output dtype);
    upcasting to float64 would double memory and cache size for no
    retrieval benefit.

Testability: an `encoder` callable can be injected. When it is None, the
real SentenceTransformer model is built lazily on first use. Tests inject a
tiny deterministic encoder so they never download the model.
"""

from typing import Callable, List, Optional, Tuple

import numpy as np

from src.data_loader import Paragraph
from src.embedding_cache import load_embedding_cache, save_embedding_cache

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# An encoder maps a list of strings to a 2D float array of shape
# (n_texts, embedding_dim).
Encoder = Callable[[List[str]], np.ndarray]


def _build_default_encoder(model_name: str) -> Encoder:
    """Lazily construct a SentenceTransformer-backed encoder. Imported here
    (not at module top) so that offline tests injecting their own encoder
    never need sentence-transformers installed."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)

    def encode(texts: List[str]) -> np.ndarray:
        return np.asarray(
            model.encode(texts, convert_to_numpy=True, show_progress_bar=False),
            dtype=np.float32,
        )

    return encode


def _try_load_cached_embeddings(
    cache_dir, titles: List[str], model_name: str
) -> Optional[np.ndarray]:
    """Returns the cached (already normalized) embedding matrix if cache_dir
    holds a cache for exactly this corpus AND this model, else None
    (= encode from scratch).

    "Exactly this corpus" means the cached title list equals `titles`,
    including order -- rows and paragraphs must line up index-for-index.
    Any of the following is treated as a cache MISS, so the caller
    re-encodes and overwrites:
      - cache files absent (never built here);
      - title mismatch (stale cache from another corpus, e.g. a
        different n or split);
      - model_name mismatch (same corpus encoded by a different model --
        those vectors live in a different embedding space, and reusing
        them would silently corrupt every similarity score);
      - legacy cache without meta.json (model unknown -> can't trust it).
    A structurally corrupted cache (title count != row count) still raises
    ValueError from load_embedding_cache: that is damage, not staleness,
    and should be loud.
    """
    if cache_dir is None:
        return None
    try:
        cached_titles, matrix, cached_model_name = load_embedding_cache(cache_dir)
    except FileNotFoundError:
        return None
    if cached_titles != titles or cached_model_name != model_name:
        return None
    return matrix


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalization. Zero-norm rows are left as zeros (their
    cosine similarity to anything is then 0), avoiding divide-by-zero."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return matrix / norms


class DenseRetriever:
    """Embedding-based retriever over a paragraph set (per-question or pooled)."""

    def __init__(
        self,
        paragraphs: List[Paragraph],
        encoder: Optional[Encoder] = None,
        model_name: str = DEFAULT_MODEL_NAME,
        cache_dir=None,
    ):
        self.paragraphs = paragraphs
        # The encoder is built/used lazily so a cache hit never pays for it.
        self._encoder = encoder
        self._model_name = model_name

        titles = [p.title for p in paragraphs]
        cached = _try_load_cached_embeddings(cache_dir, titles, model_name)
        if cached is not None:
            self.doc_embeddings = cached
            return

        # Cache miss (or no cache configured): encode + normalize once.
        doc_embeddings = self._encode([p.text for p in paragraphs])
        self.doc_embeddings = _l2_normalize(np.asarray(doc_embeddings, dtype=np.float32))
        if cache_dir is not None:
            save_embedding_cache(cache_dir, titles, self.doc_embeddings, model_name)

    def _encode(self, texts: List[str]) -> np.ndarray:
        """All encoding goes through here; the default model is only built
        on the first actual call (never on a warm-cache construction)."""
        if self._encoder is None:
            self._encoder = _build_default_encoder(self._model_name)
        return self._encoder(texts)

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Paragraph, float]]:
        """
        Returns the top_k paragraphs ranked by cosine similarity to the
        query, highest first, as (Paragraph, score) tuples.
        """
        query_embedding = self._encode([query])
        query_vec = _l2_normalize(np.asarray(query_embedding, dtype=np.float32))[0]

        scores = self.doc_embeddings @ query_vec

        ranked = sorted(
            zip(self.paragraphs, scores),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [(paragraph, float(score)) for paragraph, score in ranked[:top_k]]

    def retrieve_titles(self, query: str, top_k: int = 10) -> List[str]:
        """Convenience wrapper: same as retrieve(), but returns just the
        ranked list of paragraph titles (what the evaluator needs)."""
        return [p.title for p, _ in self.retrieve(query, top_k=top_k)]
