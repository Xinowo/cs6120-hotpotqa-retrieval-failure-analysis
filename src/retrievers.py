"""
retrievers.py

Week 1 scope: BM25 retriever only. Dense retrieval is Xin's module and
will live alongside this one (e.g. src/dense_retriever.py) without needing
changes here.

Design choice: BM25 is built PER QUESTION, not once globally. Each
HotpotQA question ships with its own small context (~10 paragraphs), and
per the project scope, that is the retrieval corpus for that question.
So every call to `retrieve()` builds a fresh BM25 index over that
question's paragraphs. This is intentionally simple for Week 1; if this
becomes a runtime bottleneck at 500+ examples, revisit with caching.
"""

from typing import List, Tuple
from rank_bm25 import BM25Okapi

from src.data_loader import Paragraph


def _tokenize(text: str) -> List[str]:
    """Minimal whitespace + lowercase tokenizer. BM25 just needs consistent
    tokens on both sides (query and documents); no need for anything fancier
    in Week 1."""
    return text.lower().split()


class BM25Retriever:
    """Lexical (keyword-overlap) retriever over a per-question paragraph set."""

    def __init__(self, paragraphs: List[Paragraph]):
        self.paragraphs = paragraphs
        tokenized_corpus = [_tokenize(p.text) for p in paragraphs]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Paragraph, float]]:
        """
        Returns the top_k paragraphs ranked by BM25 score, highest first,
        as (Paragraph, score) tuples.
        """
        tokenized_query = _tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        ranked = sorted(
            zip(self.paragraphs, scores),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return ranked[:top_k]

    def retrieve_titles(self, query: str, top_k: int = 10) -> List[str]:
        """Convenience wrapper: same as retrieve(), but returns just the
        ranked list of paragraph titles (what the evaluator needs)."""
        return [p.title for p, _ in self.retrieve(query, top_k=top_k)]
