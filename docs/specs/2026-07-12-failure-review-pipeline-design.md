# Failure Review Pipeline — Design Doc

- Date: 2026-07-12
- Status: implemented data layer; report UI pending
- Revision: 2026-07-13, four additions after review — annotation import/restore, `git_commit` and `corpus_setting` added to config.json, `annotator`/`annotated_at` columns added to annotations.csv
- Revision: 2026-07-17, pooled horizon fixed at top-50 and BM25 added beside Dense for deep-rank comparison
- Related work: the observation notes and the failure-case filtering script (originally planned for Week 3; this design pulls it earlier and expands it)

## 1. Background and pain points

The current Week 1 debug scripts (`scripts/run_week1_debug.py`, `scripts/run_week1_dense_debug.py`) have three problems:

1. **No designated place where failures are recorded**: the overall recall summary is only printed to the terminal and lost once the run ends; there is no run metadata (n, split, model, time), so results are not traceable.
2. **`results/*.csv` is too high-level for manual debugging**: top-k titles are joined with `|` inside a single cell, so it is hard to see at which rank a gold title landed; there is only the True/False of recall@k — no gold hit ranks, no retrieval scores, no paragraph text — yet judging semantic drift / lexical mismatch requires reading the gold and top-k texts side by side.
3. **No landing place for manual classification (annotation)**: Week 3's failure analysis needs ~20 manually labeled examples to validate `failure_analyzer.py`, and there is currently no file or process to hold those annotations.

## 2. Goals and non-goals

**Goals**

- Every retrieval run produces structured, traceable, complete results (data layer).
- Provide an annotator-friendly failure review interface: gold highlighting, hit ranks, collapsible text, filtering (view layer).
- Manual classification starts as **free-text labels**, persisted to a standalone `annotations.csv`, which serves as the human-labeled validation set for Week 3's `failure_analyzer.py` (annotation layer).

**Non-goals**

- No fixed taxonomy is presupposed: fill in free-form labels first, then converge to fixed categories after reviewing a batch of failures (convergence adds a small "label normalization" step; the `annotations.csv` structure is unchanged).
- No server and no new dependencies (no Streamlit / notebook server); the HTML is a pure static single file.
- The `failure_analyzer.py` decision rules are not implemented within this design (a Week 3 task, and part of what the AI boundary requires to be hand-written).

## 3. Overall architecture

```
runner (scripts/)
   └─> results/runs/<run_id>/
         ├── details.jsonl    ← single source of truth (full record per question)
         ├── metrics.json     ← aggregate metrics by retriever
         └── config.json      ← run parameters and metadata

scripts/build_failure_report.py
   └─> reads details.jsonl, filters questions that miss@k
   └─> results/runs/<run_id>/failures_review.html (self-contained single file)

annotator (human) fills in label/notes in the browser → exports annotations.csv
   └─> archived to results/annotations/, committed to git
   └─> the human validation set for Week 3's failure_analyzer.py
```

Core principle: **Python computes, HTML only displays.** All evaluation quantities (recall@k, gold hit ranks, etc.) are computed in `src/evaluator.py` and written into `details.jsonl` ahead of time; the JavaScript inside the HTML only does rendering, filtering, highlighting, annotation input, and export — it contains no metric computation.

## 4. Data layer

### 4.1 run_id and directory

`run_id = <YYYY-MM-DD>_<sequence letter>` (e.g. `2026-07-12_a`), directory `results/runs/<run_id>/`. The runner automatically takes the smallest unused letter for the day.

### 4.2 details.jsonl (one line per question)

```json
{
  "example_id": "5a8b57f25542995d1e6f1371",
  "question": "Were Scott Derrickson and Ed Wood of the same nationality?",
  "question_type": "comparison",
  "gold_titles": ["Ed Wood", "Scott Derrickson"],
  "retrievers": {
    "bm25": {
      "top_k": [
        {"rank": 1, "title": "Doctor Strange (2016 film)", "score": 12.34, "text": "…full paragraph text…"}
      ],
      "gold_ranks": {"Ed Wood": 10, "Scott Derrickson": 4},
      "metrics": {"any_evidence_recall@2": false, "any_evidence_recall@5": true, "any_evidence_recall@10": true, "reciprocal_rank_at_10": 0.25, "reciprocal_rank_at_50": 0.25}
    },
    "dense": { "…same structure…": null }
  }
}
```

- `top_k_max`: 10 for per-question and 50 for pooled by default. Dense and BM25 use the same horizon.
- `gold_ranks`: the rank (1-based) of each gold paragraph in that retriever's saved ordering; `null` means it did not make the saved horizon (rank > 50 for a standard pooled run), not that it is absent from the corpus.
- `text`: full paragraph text (collapsed by default in the HTML, expandable for reading).
- The formal long-format `results/*_results.csv` files are kept separately; pooled rows also store top-50 titles but omit scores/text.

### 4.3 metrics.json / config.json

- `metrics.json`: Dense and BM25 aggregate Recall@k, MRR@10, and MRR@50 values (using explicit reciprocal-rank field names in the per-example records).
- `config.json`: n, split, top_k_max, retriever and model names (e.g. `all-MiniLM-L6-v2`), timestamp, script name, plus:
  - `corpus_setting`: `per_question` / `pooled`. The Week 1 debug scripts are all `per_question`; from Week 2 on, pooled is the primary setting. Failures under the two settings are different in nature (a per-question miss@2 is "picked the wrong 2 out of 10", a pooled miss is "couldn't fish it out of ~5000 paragraphs"), so run metadata must be able to distinguish them.
  - `git_commit`: the runner executes `git rev-parse HEAD` and writes the result (`null` if unavailable, e.g. in a non-git environment), making results traceable to a code version.

## 5. View layer: failures_review.html

`scripts/build_failure_report.py --run <run_id> [--retriever dense --k 2]`:

- Default filtering rule: a question qualifies if any retriever misses at any k ∈ {2,5,10}; parameters can narrow it (e.g. only dense miss@2, the original failure-case filtering task).
- **Card granularity = one failure unit (example_id, retriever)**: if a retriever misses at least one k on a question, a card is generated for it (the card header lists all the k values it misses; on export, k takes the smallest of them). If both retrievers fail on the same question, each gets its own card. Inside a card, both retrievers' top-k are still shown side by side for comparison, but label/notes belong to the retriever the card is for.
- Produces a **self-contained single-file HTML** (data embedded as JSON, opens on double-click, no network, no dependencies).
- One card per failure, containing:
  - question, question_type, example_id;
  - gold titles: hits annotated with `rank N`, those outside top-k marked in red;
  - both retrievers' top-k side by side: scores, gold entries highlighted, paragraph text collapsible;
  - **free-text label input** (a datalist autocompletes previously used labels, avoiding synonymous spellings) + a multi-line notes input.
- The page header shows run metadata (run_id, corpus_setting, model, n/split), so while annotating it is always visible which corpus setting the current run belongs to, avoiding confusion between the two settings' different failure natures.
- Page features: filter by retriever / k / question_type / annotated-or-not; sort by "worst gold rank" (most severe failures first); an "Export annotations.csv" button at the bottom.
- Annotation state is stored in localStorage (keyed by run_id + example_id + retriever); exporting is what persists it.
- **"Import annotations.csv" button**: localStorage is volatile (clearing browser data loses it; localStorage isolation rules for `file://` pages differ across browsers — e.g. Firefox isolates per directory), and switching browsers / machines or annotating across multiple sittings all require restoring existing annotations. On import, entries are merged with existing localStorage annotations by the (run_id, example_id, retriever) key; on key conflict the imported file wins (a confirmation prompt is shown before import). The workflow is: annotate a batch → export and archive → next time, import the previous CSV first and continue.

## 6. Annotation layer

### 6.1 annotations.csv

| Column | Meaning |
|---|---|
| run_id | the run the annotation is based on |
| example_id | HotpotQA question id |
| retriever | bm25 / dense |
| k | the smallest k this retriever misses (consistent with the card export rule) |
| label | free text (normalized to the fixed taxonomy later) |
| notes | remarks |
| annotator | who annotated (Xin / Jiajun). Filled in once at the top of the page and written into every exported row; in a two-person project, discussing annotation disagreements when validating failure_analyzer requires knowing who labeled what |
| annotated_at | when this entry was last modified (ISO 8601, recorded automatically by the page) |

After export, a human places the file into `results/annotations/` and commits it to git. Other fields such as the question text are not duplicated into the CSV; Week 3 scripts join `details.jsonl` by example_id to get them, and join `config.json` by run_id to get corpus_setting.

### 6.2 Handoff to Week 3

- `annotations.csv` is the carrier for the manual failure annotation and the `failure_analyzer.py` validation set;
- after the taxonomy converges, add a small script or one manual pass to map free-form labels to the final categories (a new column or a new file; original labels are kept);
- case snippets for the report / slides are generated as markdown by a script from `details.jsonl` + `annotations.csv`, not copied out of the HTML.

## 7. AI-usage boundary split

| Component | Location | Who writes it |
|---|---|---|
| recall@k, gold hit ranks, and all other evaluation quantities | `src/evaluator.py` (new gold_ranks computation) | **Xin, hand-written** |
| failure decision rules | Week 3 `failure_analyzer.py` | **Xin, hand-written** |
| runner rework; JSONL/CSV/JSON persistence | `scripts/` | agent-allowed |
| `build_failure_report.py` + HTML/JS (rendering, filtering, highlighting, annotation, export) | `scripts/` | agent-allowed (pure display layer, no metric computation) |
| tests for the plumbing above | `tests/` | agent-allowed |

Convention: if the HTML page ever needs any "value computed from the ranked list and the gold set", it always goes back to Python (the evaluator) to be precomputed and embedded as data; JS implements no computation logic. Agent sessions are logged in `docs/Completion_Log/` per course requirements.

## 8. Plan synchronization

This design pulls the failure-case filtering work earlier and expands its content, which counts as a task-content change, so per convention it must be **synchronized across both** the personal implementation plan and the joint `CS6120_Final_Project_Weekly_Todo_Plan.md`. (Relation between the observation-notes file and this pipeline: dense_observations.md continues as narrative notes, while structured annotation is owned by annotations.csv — the two complement each other.)

## 9. Testing and acceptance

- The evaluator's new gold_ranks logic: Xin hand-writes the implementation and unit tests (the existing `tests/test_evaluator.py` style can serve as reference).
- Plumbing: JSONL field completeness; run-directory creation; config.json contains corpus_setting and git_commit; the report generator handles an empty failure set (produces a "no failures" page instead of erroring).
- End-to-end acceptance: on the Week 1 ten-example debug subset, run runner → HTML → manually annotate 2–3 entries → export annotations.csv → file lands in place.
- Import round-trip acceptance: export annotations.csv → clear localStorage (simulating a browser switch) → import that CSV → the page's annotation state matches the pre-export state (including annotator, annotated_at).
