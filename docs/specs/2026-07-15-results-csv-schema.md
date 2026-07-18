# Results CSV Schema

**Author:** Xin · **Original date:** 2026-07-15 · **Status:** Final, amended 2026-07-17
**Applies to:** `results/dense_results.csv`, `results/bm25_results.csv`, and `results/rerank_results.csv`

## 2026-07-17 protocol amendment

The pooled-corpus protocol now stores top-50 ranked titles for every method.
This is an evaluation-protocol change, not a runner-only optimization. Dense,
BM25, and rerank formal runs must all use this schema before results are
compared or concatenated.

The protocol separates storage depth from the primary reporting depth:

- formal pooled rows store top-50; per-question rows store all available
  candidates up to 10;
- evidence Recall remains reported at @2/@5/@10;
- MRR@10 is the primary reciprocal-rank aggregate and MRR@50 is the pooled
  deep-ranking diagnostic;
- the ambiguous bare column `mrr` is removed.

## Goal and shape

One shared long-format schema is used by every method and corpus setting: one
row per `(method, setting, example)`. Identical columns allow method files to
be concatenated or joined on `example_id` without method-specific handling.

The implementation source of truth for column order and storage depths is
`src/results_schema.py`.

For metric computation, executable evaluator code and tests take precedence.
This schema freezes how those values are stored and compared across methods;
the Scope document supplies the report-level interpretation.

## Columns

| # | Column | Type | Values / format | Notes |
|---|---|---|---|---|
| 1 | `method` | str | `bm25` \| `dense` \| `rerank` | lowercase fixed vocabulary |
| 2 | `setting` | str | `pooled` \| `per_question` | corpus setting |
| 3 | `example_id` | str | HotpotQA `_id` | cross-method join key |
| 4 | `question_type` | str | `bridge` \| `comparison` | from the example |
| 5 | `level` | str | `easy` \| `medium` \| `hard` | analysis dimension |
| 6 | `question` | str | raw question text | human inspection |
| 7 | `gold_titles` | str | titles joined by `" | "` | sorted for stable output |
| 8 | `retrieved_titles` | str | ranked titles joined by `" | "` | pooled top-50; per-question all/up to 10 |
| 9–11 | `any_evidence_recall@{2,5,10}` | int | `1` \| `0` \| empty | per-question @10 is empty |
| 12–14 | `full_evidence_recall@{2,5,10}` | int | `1` \| `0` \| empty | per-question @10 is empty |
| 15–17 | `partial_evidence_recall@{2,5,10}` | float | `[0,1]` \| empty | per-question @10 is empty |
| 18 | `reciprocal_rank_at_10` | float | `[0,1]` | per-example value; aggregate name is MRR@10 |
| 19 | `reciprocal_rank_at_50` | float | `[0,1]` | per-example value; aggregate name is MRR@50 |

`partial_evidence_recall@k` is fractional gold-evidence coverage, not a binary
"some but not all" indicator. For unique gold-title set `G` and the titles in
the first `k` results `R_k`:

```text
partial_evidence_recall@k = |G ∩ R_k| / |G|
```

A separate derived concept, **Incomplete Evidence Indicator@k**, is
`1(0 < |G ∩ R_k| < |G|)`; its dataset mean is **Incomplete Evidence Rate@k**
(or Partial-Only Rate@k). It is useful for failure analysis but is not added to
the frozen `RESULT_COLUMNS` schema. Any implementation belongs to the team's
hand-written evaluation methodology.

The single-example fields use `reciprocal_rank_*`, not `mrr_*`, because the
mean is computed only during aggregation. `@` remains in recall-column names
to match evaluator output, while `_at_10` / `_at_50` keeps reciprocal-rank
columns convenient in pandas, SQL, and spreadsheet tools.

The aggregate MRR values must be computed from the per-example columns as:

```python
MRR_at_10 = df["reciprocal_rank_at_10"].mean()
MRR_at_50 = df["reciprocal_rank_at_50"].mean()
```

Report `MRR_at_10` and `MRR_at_50` as **MRR@10** and **MRR@50** in tables and
prose. In other words, `reciprocal_rank_at_*` names the value stored for one
question; `MRR@*` names its mean across the evaluated questions. Aggregation
must be performed separately for each intended group, normally at least by
`method` and `setting` (and optionally by `question_type`).

Booleans are written as `1`/`0`, never `True`/`False` strings. Empty cells
represent a deliberately uncomputed metric and are read as `NaN`; pandas
aggregation therefore skips them.

## Storage and metric policy

| Setting | `retrieved_titles` | Recall computed | Reciprocal rank |
|---|---:|---|---|
| `pooled` | top-50 | @2, @5, @10 | RR@10 and RR@50 |
| `per_question` | all available, capped at 10 | @2, @5; @10 empty | RR@10 and RR@50 (equal because the full corpus has at most about 10 candidates) |

Formal runners must not silently use a method-specific storage depth. In
particular, BM25 cannot remain at top-10 while Dense stores top-50.

The pooled top-50 depth is part of the frozen experiment protocol, not a
runtime tuning knob. If resources are constrained, reduce the number of
questions, batch or cache work, or use a smaller model. A future top-20 run
would require an explicit new protocol version, rerunning every affected
method, and separate reporting rather than direct comparison in the top-50
main table.

Reporting policy:

- pooled main tables report Recall@2/@5/@10 and MRR@10;
- pooled diagnostic/deep-ranking tables may additionally report MRR@50 and
  exact gold ranks from 11–50;
- per-question main tables report the existing primary cutoff @2; stored @5
  and reciprocal-rank values remain available for analysis;
- Recall@50 is not added to the main metric set.

## Interpretation of truncation

In any artifact whose storage horizon is 50, `gold_ranks = null` means only
that the gold title did not enter the saved top-50. It does not prove that the
title is absent from the corpus or irretrievable at every rank.

## Relationship to other artifacts

- `results/*_results.csv`: formal per-example metrics plus ranked titles.
- `results/dense_top50_pooled.csv`: retained as reranker input because it also
  stores one row per `(example_id, rank)` with title and dense score.
- `results/runs/<run_id>/details.jsonl`: failure-review record with rank,
  title, score, paragraph text, and gold ranks for Dense and BM25.
- run metadata (n, split, models, runtime, git commit) belongs in sidecar run
  configuration, not in every result row.

The overlap in title lists is intentional: the formal CSV supports direct
cross-method analysis, while the dense export supplies score-bearing
candidate rows to the reranker.

## Fixed column order

```text
method, setting, example_id, question_type, level, question,
gold_titles, retrieved_titles,
any_evidence_recall@2, any_evidence_recall@5, any_evidence_recall@10,
full_evidence_recall@2, full_evidence_recall@5, full_evidence_recall@10,
partial_evidence_recall@2, partial_evidence_recall@5, partial_evidence_recall@10,
reciprocal_rank_at_10, reciprocal_rank_at_50
```

MediaWiki page titles cannot contain `|`, so the `" | "` separator is
collision-free for these Wikipedia titles. Standard CSV quoting still applies
when a title or question contains a comma.
