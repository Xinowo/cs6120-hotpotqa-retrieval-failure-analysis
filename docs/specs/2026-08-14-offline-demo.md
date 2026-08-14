---
status: active
last_updated: 2026-08-14
---

# Offline Demonstration Script — Spec

- Date: 2026-08-14
- Status: submission deliverable; describes `demo.py` only
- Applies to (inputs): `results/main_results_v1.csv`, `results/disagreement_cases.csv`,
  `results/rerank_rescue_damage_cases.csv`
- Produces (output): formatted text on stdout; no file is written
- Related: `docs/specs/2026-07-15-results-csv-schema.md` (the long-format schema the
  runners write), `docs/specs/2026-07-26-reranker-rescue-damage.md` and
  `docs/specs/2026-08-12-rerank-rescue-damage-cases.md` (the aggregate and per-example
  rescue/damage contracts whose accepted outputs this script displays)

## 1. Purpose

`demo.py` is one of the four required items of the 8/14 full submission
(`docs/Plans/CS6120_Final_Project_Weekly_Todo_Plan.md`, "8/14 — full submission").
Its job is to let a reader who has just cloned the repository see the project's
actual finding in one command, without a network connection and without a GPU.

It is a presentation layer over already-accepted artifacts. It computes no
metric, defines no failure category, and re-runs no retrieval.

## 2. Scope and non-goals

In scope: reading three accepted result CSVs and printing a fixed three-part
walkthrough.

Explicitly out of scope for this spec:

- Live retrieval. An opt-in `--live` mode that runs BM25/dense/cross-encoder over
  a handful of examples was considered and deferred by the owner on 2026-08-14.
  If it is added later it needs its own spec section; it must never become the
  default, because the default path must stay offline.
- Recomputing any number. Every figure printed must be read from a CSV cell. A
  demo that recomputes a metric can disagree with the accepted results, and the
  accepted results are the authority.
- Writing files, downloading data, or reading anything under `results/runs/`.

## 3. Inputs

All three are tracked, so a clean checkout has them.

| File | Columns consumed |
|---|---|
| `results/main_results_v1.csv` | all 10 columns, all 3 rows |
| `results/disagreement_cases.csv` | `example_id`, `question`, `gold_titles`, `k`, `bm25_hit`, `dense_hit`, `direction`, `bm25_retrieved_titles`, `dense_retrieved_titles` |
| `results/rerank_rescue_damage_cases.csv` | `setting`, `example_id`, `question`, `gold_titles`, `k`, `dense_gold_ranks`, `rerank_gold_ranks`, `transition` |

`gold_titles`, `bm25_retrieved_titles`, and `dense_retrieved_titles` are
` | `-separated title lists. `dense_gold_ranks` and `rerank_gold_ranks` are JSON
objects mapping a gold title to its 1-based rank, or to `null` when that title was
not retrieved within the stored depth.

## 4. Output contract

Three sections, in this order, on stdout.

### 4.1 Headline comparison

Print all three rows of `results/main_results_v1.csv` as an aligned table, cells
verbatim from the file. Follow it with one sentence naming the Full Evidence Hit
Rate@5 column as the project's primary criterion, since "recovered some evidence"
and "recovered all evidence needed to answer" are what the project separates.

### 4.2 One BM25-versus-dense disagreement

`results/disagreement_cases.csv` is already restricted to `pooled`,
`full_evidence_recall`, `k=5`. Select `direction == "dense_only"`, sort by
`example_id`, take the first row.

Print the question, its gold titles, and the **first `k` titles** of each of
`bm25_retrieved_titles` and `dense_retrieved_titles`, marking titles that are gold.
The stored lists hold 50 titles; the demo must say it is showing the top `k` of a
longer stored list rather than implying the list is 5 long.

Gold marking is display formatting only. Whatever it marks must agree with the
row's own `bm25_hit` / `dense_hit` cells; see §6.

### 4.3 One reranker rescue and one damage

From `results/rerank_rescue_damage_cases.csv` select `setting == "pooled"` and
`k == 5`; sort by `example_id`; take the first `transition == "rescue"` row and the
first `transition == "damage"` row.

For each, print the question, the gold titles, and each gold title's rank before
and after reranking, read from `dense_gold_ranks` and `rerank_gold_ranks`. Render a
`null` rank as "not retrieved" rather than as a number.

The damage case is not optional. The reranker moves questions in both directions,
and a demo that shows only rescues misrepresents the result.

## 5. Interface and failure behavior

```text
python demo.py
```

No required arguments. `--help` describes the script and states that it reads
checked-in results and performs no retrieval.

Fail closed and fail early: if an input file is missing, or a required column is
absent, or a selection rule matches no row, exit non-zero with a message naming
the file and what was expected. Printing a partial walkthrough that silently omits
a section is not acceptable — a grader would read the missing section as a result.

Exit code is 0 only when all three sections printed.

## 6. Test obligations

`tests/test_demo.py`, offline, no network, no model download. Required coverage:

1. The default invocation returns exit code 0 and prints all three section
   headings.
2. Every number printed in §4.1 is present in `results/main_results_v1.csv`. A
   hard-coded figure that no longer matches the CSV must fail this test.
3. Gold marking in §4.2 agrees with the selected row's `bm25_hit` / `dense_hit`
   cells. The criterion these rows were scored under is full evidence, so a hit
   cell of 1 is the statement that *every* gold title is inside the cutoff: the
   marked titles must equal the row's gold titles if and only if that cell is 1.
   A marked title on its own does not imply a hit — one of two gold titles
   inside the cutoff is a marked title on a row whose hit cell is 0, which is
   the case for 131 of the 320 retriever-units among this file's `dense_only`
   rows — every row carries exactly two gold titles.
4. A missing input file produces a non-zero exit and an error naming that file,
   and prints no partial walkthrough.
5. Selection is deterministic: two invocations select the same three example_ids.

Keep this suite proportionate. It guards the demo's honesty about the accepted
results, not the formatting of its output.

## 7. Boundary note for the AI Usage Declaration

`demo.py` falls in the agent-permitted column of the project's AI Usage Boundary
("Demonstration script around already-built components"). It contains no metric
definition, no failure taxonomy, and no research claim beyond the one sentence in
§4.1, which restates the criterion already defined in `src/evaluator.py` and the
report. Record it as agent-generated infrastructure under Xin's records; Xin took
ownership of this deliverable from Jiajun on 2026-08-14.
