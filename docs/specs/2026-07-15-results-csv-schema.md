# Results CSV Schema

**Author:** Xin · **Date:** 2026-07-15 · **Status:** Final (2026-07-15) — open questions resolved below; content verified against `evaluator.py` / `data_loader.py`
**Applies to:** `results/dense_results.csv` (Xin), `results/bm25_results.csv` (Jiajun), later `results/rerank_results.csv` (Week 3 reranker)

## Goal

One shared per-example schema for all retrieval methods and both corpus settings, so that:

- BM25 / dense / rerank results can be concatenated or joined by `example_id` for disagreement analysis;
- the main results table (main_results_v1) is produced by one aggregation script grouping on `method` + `setting`;
- Week 3 failure analysis can filter miss rows without any per-method special-casing.

## Shape: long format, one row per (method, setting, example)

Week 1's debug CSV was wide (one `bm25_*` and one `dense_*` column group side by side). For the main experiment we switch to **long format**: each method writes its own file with the identical column set, and a `method` column makes cross-method concat trivial. Wide format doesn't scale to method × setting × k and forces schema changes every time a method is added.

## Columns

| # | Column | Type | Values / format | Notes |
|---|---|---|---|---|
| 1 | `method` | str | `bm25` \| `dense` \| `rerank` | lowercase, fixed vocabulary |
| 2 | `setting` | str | `pooled` \| `per_question` | corpus setting |
| 3 | `example_id` | str | HotpotQA `_id` | join key across files |
| 4 | `question_type` | str | `bridge` \| `comparison` | from `HotpotExample.question_type` |
| 5 | `level` | str | `easy` \| `medium` \| `hard` | from `HotpotExample.level`; free extra grouping dimension |
| 6 | `question` | str | raw question text | kept for human inspection of failure rows |
| 7 | `gold_titles` | str | titles joined by `" | "` | same convention as Week 1 CSVs |
| 8 | `retrieved_titles` | str | top-10 ranked titles joined by `" | "` | enough to recompute any metric at k ≤ 10; full top-50 lives in the separate top-50 export, not here |
| 9 | `any_evidence_recall@2` | int | `1` \| `0` | |
| 10 | `any_evidence_recall@5` | int | `1` \| `0` | |
| 11 | `any_evidence_recall@10` | int | `1` \| `0` \| empty | empty for `per_question` rows (see K policy) |

Booleans are written as `1`/`0`, not `True`/`False` strings (a deliberate change from the Week 1 debug CSVs). Rationale: combined with the empty-cell policy, `True`/`False` strings read back as object dtype where `"False"` is truthy — a classic silent bug in filters like `df[df[col]]`. `1`/`0` reads back as int64 (or float64 with NaN where a column contains empty cells) — either way `mean()` directly yields recall in the aggregation script, and the files stay Excel/R-friendly.

Metric column naming is `<metric_name>@<k>`, matching `evaluate_example()` output keys. When Full / Partial Evidence Recall land in `evaluator.py` (Jiajun, Week 2 scope), they append as new columns (`full_evidence_recall@2`, …) — no renames, no reordering of existing columns.

## K policy (which metric columns are filled per setting)

- `pooled` rows: k = 2, 5, 10 → all three metric columns filled.
- `per_question` rows: `@2` and `@5` computed, `@10` left **empty**, not computed. Rationale: the per-question corpus is ~10 paragraphs, so recall@10 is trivially 1.0 and an accidentally reported number is worse than a blank; recall@5 costs nothing to store and is useful for failure-analysis slicing, even though it sits near ceiling. Empty cells are self-explaining "not applicable by design", and pandas `mean()` skips NaN automatically — no filter logic needed at table time.
- **Table reporting is unchanged** and follows the joint plan's rule (Weekly Todo Plan, "Reporting rule for tables"): pooled tables report k = 2, 5, 10; per-question tables report k = 2 only. The stored per-question `@5` is analysis-only and does not go into the main results table.

## What is deliberately NOT in this CSV

- **Aggregate rows** (averages) — different grain; the table script computes them by grouping on `method` + `setting` (+ `question_type`).
- **Run metadata** (n, split, model name, runtime, git commit) — goes in the run's sidecar config/notes (formalized later by the failure-review runner's `results/runs/<run_id>/config.json`); runtime also goes into the run notes.
- **Scores** — the top-50 export carries `title` + `score`; this file only needs ranked titles for recall metrics.

## Resolved questions (2026-07-15)

1. **Per-question k coverage:** compute `@2` and `@5`, leave only `@10` empty. `@10` is trivially 1.0 on a ~10-paragraph corpus and must not leak into any table. `@5` is stored for analysis but stays out of the main table — the joint plan's table rule (per-question reports k = 2 only) is unchanged by this spec. (Encoded in the K policy above.)
2. **One file per method** — confirmed. Independent reruns don't touch each other's files, git diffs are isolated per method, and a shared append-file would need error-prone "delete my old rows first" logic. Merge cost is one `pd.concat`.
3. **Keep `level`** — zero cost, one free slicing dimension for Week 3 failure analysis. Caveat: the HotpotQA dev level distribution is skewed (mostly hard), so per-level slices may be small — reference only, not for the main table.
4. **Keep `" | "` separator** — stronger than it looks: MediaWiki forbids `|` in page titles, so the separator is strictly collision-free for Wikipedia titles, not just comma-safe.
5. **Booleans as `1`/`0`** — changed from the Week 1 `True`/`False` convention; rationale under the Columns table.

## Example rows

```csv
method,setting,example_id,question_type,level,question,gold_titles,retrieved_titles,any_evidence_recall@2,any_evidence_recall@5,any_evidence_recall@10
dense,per_question,5a8b57f25542995d1e6f1371,comparison,hard,Were Scott Derrickson and Ed Wood of the same nationality?,Ed Wood | Scott Derrickson,"Ed Wood (film) | Ed Wood | Adam Collis | Woodson, Arkansas | Conrad Brooks | Scott Derrickson | Sinister (film) | Tyler Bates | Deliver Us from Evil (2014 film) | Doctor Strange (2016 film)",1,1,
dense,pooled,5a8b57f25542995d1e6f1371,comparison,hard,Were Scott Derrickson and Ed Wood of the same nationality?,Ed Wood | Scott Derrickson,...top-10 from shared index...,1,1,1
```

Notes on the example rows:

- `...top-10 from shared index...` in the second row is a **placeholder**, not a real title list — replace with actual pooled-run output when available; do not diff against it as a reference.
- Row 1's `retrieved_titles` is quoted because one title (`Woodson, Arkansas`) contains a comma — standard CSV quoting, applied automatically by `csv`/pandas writers (the Week 1 CSVs show the same). Fields without commas need no quotes.
