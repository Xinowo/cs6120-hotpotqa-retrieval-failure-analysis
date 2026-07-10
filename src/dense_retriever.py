"""
dense_retriever.py

Xin's module: dense (embedding-based) retrieval, the semantic counterpart
to Jiajun's BM25 lexical retriever in retrievers.py.

It mirrors BM25Retriever's interface exactly -- same __init__(paragraphs),
retrieve(query, top_k) and retrieve_titles(query, top_k) -- so it is a
drop-in swap in the experiment/debug scripts and the two methods can be
compared fairly.

Design choices (Week 1, kept deliberately simple):
  - Per-question corpus: like BM25, the retriever is built PER QUESTION
    over that question's own ~10 context paragraphs, not all of Wikipedia.
    So paragraph embeddings are (re)computed per question. Embedding
    caching across questions is a Week 2 optimization, not a Week 1 goal.
  - Model: sentence-transformers/all-MiniLM-L6-v2, per the project plan.
  - Similarity: cosine similarity, computed as a dot product of
    L2-normalized embeddings.

Testability: an `encoder` callable can be injected. When it is None, the
real SentenceTransformer model is built lazily on first use. Tests inject a
tiny deterministic encoder so they never download the model.
"""

from typing import Callable, List, Optional, Tuple

import numpy as np

from src.data_loader import Paragraph

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
            dtype=float,
        )

    return encode


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalization. Zero-norm rows are left as zeros (their
    cosine similarity to anything is then 0), avoiding divide-by-zero."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return matrix / norms


class DenseRetriever:
    """Embedding-based retriever over a per-question paragraph set."""

    def __init__(
        self,
        paragraphs: List[Paragraph],
        encoder: Optional[Encoder] = None,
        model_name: str = DEFAULT_MODEL_NAME,
    ):
        self.paragraphs = paragraphs
        self._encoder = encoder if encoder is not None else _build_default_encoder(model_name)

        # Precompute (normalized) paragraph embeddings once for this question.
        doc_embeddings = self._encoder([p.text for p in paragraphs])
        self.doc_embeddings = _l2_normalize(np.asarray(doc_embeddings, dtype=float))

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Paragraph, float]]:
        """
        Returns the top_k paragraphs ranked by cosine similarity to the
        query, highest first, as (Paragraph, score) tuples.
        """
        query_embedding = self._encoder([query])
        query_vec = _l2_normalize(np.asarray(query_embedding, dtype=float))[0]

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
