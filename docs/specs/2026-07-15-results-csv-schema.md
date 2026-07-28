---
status: active
last_updated: 2026-07-27
---

# Results CSV Schema

**Author:** Xin · **Original date:** 2026-07-15 · **Status:** Final, amended 2026-07-17 and 2026-07-27
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

### 2026-07-27 amendment — accepted physical spellings of a metric cell

The table above gives the **canonical write form**: a binary recall cell is
written `1`, `0`, or empty. Two existing formal artifacts do not match it.
Because the per-question `@10` rows are deliberately blank, pandas serialized
that whole column as float, so the **pooled `@10`** cells of
`results/bm25_results.csv` and `results/dense_results.csv` physically read
`0.0`/`1.0`. `results/rerank_results.csv` writes plain `0`/`1`.

Xin resolved this on 2026-07-27 by freezing a **narrow compatibility rule**
rather than regenerating the inputs. A reader of these files must accept
exactly the physical lexemes

```text
0    1    0.0    1.0    <empty, where this table permits a blank>
```

and must refuse every other spelling — fractions (including precision-adjacent
ones such as `0.00000000000000000001`), scientific notation, signs, padding
zeros, padding whitespace, booleans, and null-like words. The list is closed and
matched **on the raw text before any numeric conversion**, because a
nullable-integer cast rounds a near-0 or near-1 fraction into a clean integer
and hides the defect.

`0.0`/`1.0` are accepted for legacy-artifact compatibility only. New runners
should still write `1`/`0`; retiring the float spellings requires a further
owner decision and a regeneration of the affected inputs.

Missing-ness is decided per column, never by a global null-token set: only a
physically empty metric cell is missing, while the strings `None`, `NA`,
`null`, and `NaN` are ordinary text wherever they appear in a textual column.
An empty `retrieved_titles` cell means an empty retrieved list, and must not be
read as a missing value or stringified back into a title.

The phrase "where this table permits a blank" resolves to exactly three cells,
and a reader must enforce it as such: `any_evidence_recall@10`,
`full_evidence_recall@10`, and `partial_evidence_recall@10` in a `per_question`
row, per the storage and metric policy table below. Every other metric cell is
populated in a compliant artifact — pooled recall at all three cutoffs,
per-question recall at `@2`/`@5`, and both `reciprocal_rank_at_*` columns in
either setting — so a blank there indicates a truncated or partially generated
file and must be refused rather than read as an uncomputed metric. The `[0,1]`
float columns (rows 15–19) are likewise enforced as a **semantic domain**: the
exact written decimal must satisfy `0 <= value <= 1` before conversion, so a
negative, a value greater than one, and an overflow spelling such as `1e9999`
are refused even though each is a well-formed finite decimal.

The reader that implements this rule is
`scripts/reporting/formal_result_inputs.py`; the full contract, including the
refusal table, is `docs/specs/2026-07-27-bm25-dense-reporting-contracts.md` §1.1
and §1.2.

## Storage and metric policy

| Setting | `retrieved_titles` | Recall computed | Reciprocal rank |
|---|---:|---|---|
| `pooled` | top-50 | @2, @5, @10 | RR@10 and RR@50 |
| `per_question` | all available, capped at 10 | @2, @5; @10 empty | RR@10 and RR@50 (equal because the full corpus has at most about 10 candidates) |

Formal runners must not silently use a method-specific storage depth. In
particular, BM25 cannot remain at top-10 while Dense stores top-50.

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
