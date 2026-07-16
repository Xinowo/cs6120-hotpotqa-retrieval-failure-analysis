"""
top50_export.py

Exports, for a SHARED retrieval index, each question's top-K ranked
candidates (K=50 by default) as a long-format CSV: one row per
(example, rank). This is the candidate list that the Week 3 reranker
re-scores; the pooled export lands in
`results/dense_top50_pooled.csv` (rows = n_questions * K).

Why top-50 and why pooled: in the per-question setting each corpus is only
~10 paragraphs, so a top-50 list is degenerate (it is just the whole
corpus). The export is meaningful in the POOLED setting, where 50 candidates
are pulled out of thousands of paragraphs -- exactly the stage a cross-encoder
reranker is supposed to sharpen. The function itself is index-agnostic,
though: it works with any retriever exposing `retrieve_many` (dense today,
BM25 tomorrow), which is why offline tests can drive it with a fake encoder
and never touch the real model or the pooled corpus.

Schema (deliberately narrow -- "titles + scores", per the plan):

    example_id, rank, title, score

`score` is the raw retrieval score (cosine similarity for the dense index);
it carries the retriever's own ranking, not any evaluation metric -- this
module computes no recall/quality numbers (those are hand-written in
evaluator.py). Paragraph TEXT is intentionally NOT duplicated here: the
reranker joins each (example_id, title) back to the pooled corpus to fetch
text, which keeps a (n_questions * 50)-row file from ballooning.

AI-usage boundary: pure plumbing (ranked list -> CSV rows), no metric
computation, so this is agent-allowed per the project's AI boundary.
"""

import os
from typing import List

import pandas as pd

# Default candidate depth: the pooled export produces top-50 as the
# reranker's input.
TOP_K = 50

# Fixed column order for the exported CSV.
TOP50_COLUMNS = ["example_id", "rank", "title", "score"]


def build_top50_rows(retriever, examples, top_k: int = TOP_K) -> List[dict]:
    """For each example, retrieve its top_k candidates from the SHARED index
    and return schema-shaped rows (one dict per (example, rank)).

    `retriever` is any index exposing `retrieve_many(queries, top_k)` (the
    pooled DenseRetriever in practice); a single batch call scores every
    question against the one shared index. `examples` is a sequence of objects
    with `.example_id` and `.question` (HotpotExample). The per-example
    `.paragraphs` are ignored on purpose -- in the pooled setting the corpus
    lives in the shared index, not in each example.

    `rank` is 1-based and follows the retriever's ordering (highest score
    first, with the retriever's own stable tie-breaking). Row count is
    sum over examples of min(top_k, corpus_size); when the corpus has at
    least top_k paragraphs (the pooled case), that is exactly
    len(examples) * top_k. An empty `examples` yields an empty list.
    """
    questions = [ex.question for ex in examples]
    batches = retriever.retrieve_many(questions, top_k=top_k)

    rows = []
    for example, results in zip(examples, batches):
        for rank, (paragraph, score) in enumerate(results, start=1):
            rows.append(
                {
                    "example_id": example.example_id,
                    "rank": rank,
                    "title": paragraph.title,
                    "score": float(score),
                }
            )
    return rows


def write_top50_csv(rows: List[dict], out_path: str) -> None:
    """Write top-50 rows to `out_path` in the fixed column order, creating the
    parent directory if needed. An empty `rows` still writes a valid
    header-only CSV (so downstream readers get the schema, not a missing
    file)."""
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    pd.DataFrame(rows, columns=TOP50_COLUMNS).to_csv(out_path, index=False)
