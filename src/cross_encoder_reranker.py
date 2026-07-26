"""
cross_encoder_reranker.py

Xin's module: cross-encoder reranking, the third retrieval stage after
BM25 (retrievers.py) and dense retrieval (dense_retriever.py).

Where the retrievers score every corpus paragraph independently (a bi-encoder
embeds query and document separately, then compares), a cross-encoder scores
each (query, passage) PAIR jointly in one forward pass. That joint attention
is more accurate but far more expensive, so it is used as a SECOND stage: the
dense retriever narrows thousands of pooled paragraphs to a top-50 shortlist,
and this reranker re-scores just those 50 to sharpen the ordering.

Interface: `rerank(query, candidates, top_k)` takes the shortlist (a list of
Paragraph, exactly what `DenseRetriever.retrieve`/`retrieve_many` returns the
paragraphs of) and returns the reranked top_k as (Paragraph, score) tuples,
highest first -- the same shape the retrievers return, so the reranked list is
a drop-in for the evaluator.

Design choices:
  - Model: cross-encoder/ms-marco-MiniLM-L-6-v2, per the project plan. It is
    trained on MS MARCO to score query/passage relevance.
  - The reranker holds NO corpus/index (unlike the retrievers): it is built
    once and re-used across all queries, scoring whatever shortlist each
    call passes in.
  - All candidate pairs for one query are scored in a SINGLE scorer call
    (one batched forward pass), mirroring DenseRetriever.retrieve_many's
    one-call efficiency rather than looping per candidate.
  - Sorting is stable and descending by score, so candidates with equal
    scores keep their incoming order (matching the retrievers' tie-breaking).

Testability: a `scorer` callable can be injected. When it is None, the real
CrossEncoder model is built lazily on first use. Tests inject a tiny
deterministic scorer so they never download the model. The scorer maps a list
of (query, passage_text) pairs to a 1D array of relevance scores, one per pair
-- exactly the signature of `sentence_transformers.CrossEncoder.predict`.

AI-usage boundary: pure ranking plumbing (score pairs -> sort -> truncate),
no evaluation-metric computation (recall/MRR stay hand-written in
evaluator.py), so this is agent-allowed per the project's AI boundary.
"""

from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

from src.data_loader import Paragraph

DEFAULT_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# A scorer maps a list of (query, passage_text) pairs to a 1D float array of
# relevance scores, one per pair (higher = more relevant).
Scorer = Callable[[List[Tuple[str, str]]], Sequence[float]]


def _build_default_scorer(model_name: str) -> Scorer:
    """Lazily construct a CrossEncoder-backed scorer. Imported here (not at
    module top) so that offline tests injecting their own scorer never need
    sentence-transformers installed."""
    from sentence_transformers import CrossEncoder

    model = CrossEncoder(model_name)

    def score(pairs: List[Tuple[str, str]]) -> np.ndarray:
        # CrossEncoder.predict wants a list of [query, passage] pairs and
        # returns one score per pair.
        return np.asarray(
            model.predict(
                [[query, text] for query, text in pairs],
                show_progress_bar=False,
            ),
            dtype=np.float32,
        )

    return score


class CrossEncoderReranker:
    """Re-scores a retrieved candidate shortlist with a cross-encoder."""

    def __init__(
        self,
        scorer: Optional[Scorer] = None,
        model_name: str = DEFAULT_MODEL_NAME,
    ):
        # The scorer is built/used lazily so constructing the reranker never
        # loads the real model until the first actual rerank call.
        self._scorer = scorer
        self._model_name = model_name

    def _score(self, pairs: List[Tuple[str, str]]) -> Sequence[float]:
        """All scoring goes through here; the default model is only built on
        the first actual call."""
        if self._scorer is None:
            self._scorer = _build_default_scorer(self._model_name)
        return self._scorer(pairs)

    def rerank(
        self, query: str, candidates: List[Paragraph], top_k: int = 10
    ) -> List[Tuple[Paragraph, float]]:
        """Re-score `candidates` for `query` and return the top_k as
        (Paragraph, score) tuples, highest score first.

        All (query, candidate.text) pairs are scored in a single scorer call.
        Sorting is stable, so candidates with equal scores keep their incoming
        order. When there are fewer than top_k candidates, all of them are
        returned (reranked). An empty `candidates` yields an empty list without
        invoking the scorer.

        The scorer contract is one score per candidate. We verify that exactly
        before zipping: a scorer that returns too few or too many scores would
        otherwise let `zip` silently drop candidates (or drop trailing scores),
        producing a shorter reranked list with no error -- which downstream a
        formal runner could serialize as an invalid, too-short result. Failing
        here keeps that corruption from ever reaching an output file.
        """
        if not candidates:
            return []
        pairs = [(query, paragraph.text) for paragraph in candidates]
        scores = self._score(pairs)
        if len(scores) != len(candidates):
            raise ValueError(
                f"scorer returned {len(scores)} score(s) for {len(candidates)} "
                f"candidate(s); the scorer contract is exactly one score per "
                f"candidate (a mismatch would silently drop candidates via zip)."
            )
        ranked = sorted(
            zip(candidates, scores),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [(paragraph, float(score)) for paragraph, score in ranked[:top_k]]

    def rerank_titles(
        self, query: str, candidates: List[Paragraph], top_k: int = 10
    ) -> List[str]:
        """Convenience wrapper: same as rerank(), but returns just the
        reranked list of paragraph titles (what the evaluator needs)."""
        return [p.title for p, _ in self.rerank(query, candidates, top_k=top_k)]
