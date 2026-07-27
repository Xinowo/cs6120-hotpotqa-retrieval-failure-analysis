---
status: active
last_updated: 2026-07-27
---

# CS6120 Final Project Weekly Todo Plan

## Project Title

**When Multi-Hop Retrieval Fails: A Failure Analysis of BM25, Dense Retrieval, and Reranking on HotpotQA**

This is the title submitted in the proposal; reranking is part of the committed core scope.

---

## Core Scope

The core project is:

> **BM25 vs Dense Retrieval vs Dense + Reranking + Evidence Coverage Metrics + Failure Analysis**

The project focuses on **evidence retrieval**, not full answer generation.

The main question is not:

> Can a language model generate the correct final answer?

The main question is:

> Did the retrieval method recover the evidence passages needed to answer the question?

### Core Methods

- BM25 lexical retrieval
- Dense embedding-based retrieval
- Dense retrieval + cross-encoder reranking (committed in the proposal; off-the-shelf model, e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`, no training)

### Corpus Settings

- **Pooled corpus (primary):** merge all evaluation questions' context paragraphs (deduplicated by title) into one shared retrieval corpus (~5,000 paragraphs at 500 questions).
- **Per-question distractor corpus (contrast):** each question retrieves over its own ~10 paragraphs (the Week 1 setting). Note: Recall@10 is trivially 100% here; k = 2 is the informative cutoff.

### Core Metrics

Report metrics at:

```text
k = 2, 5, 10
```

Core metrics:

- Any Evidence Recall@k / Evidence Hit@k
- Full Evidence Recall@k
- Partial Evidence Recall@k
- MRR@10 (primary) and MRR@50 (deep-ranking diagnostic)

Note: if tables abbreviate Any Evidence Recall@k as Recall@k, the report should explicitly define it as “whether at least one mapped gold evidence paragraph appears in the top-k retrieved passages.”

AI-policy note: the metric definitions and their core computation logic in `evaluator.py` are part of the project's evaluation methodology and must be hand-written by team members (per the course policy on evaluation-heavy projects). Coding agents may generate only the surrounding infrastructure (CSV output, experiment runner, logging). Document this boundary in the AI Usage Declaration.

### Core Analysis

- BM25 vs dense disagreement cases
- Bridge vs comparison analysis
- Dense semantic drift examples
- First-hop-only failure examples
- Comparison coverage failure examples
- Lexical mismatch examples
- Distractor entity examples
- Reranker rescue and damage cases

### Optional Extension

Reranking is core (committed in the submitted proposal), **not** optional. Only one optional extension remains, added only if the core project including the reranker is on track:

- Contrastive fine-tuning of the dense retriever on HotpotQA train-split pairs, evaluated **per failure category** (which failures does fine-tuning fix, which persist). Training-pair construction and training loop must be hand-written per the AI policy. Must not compete with the reranker or the presentation for time: the go/no-go decision happens in Week 4, **after the 7/28 presentation**, and its results go into the report only.

### Out of Scope

Do **not** include these unless everything else is already complete:

- Full RAG answer generation
- Query decomposition
- Hybrid retrieval
- Full Wikipedia retrieval
- LLM-as-a-judge evaluation
- Complex dashboard or UI
- Large-scale full HotpotQA experiments

---

## AI Usage Boundary

Per the course AI policy (docs/CS6120_Final_Project_Ideas.pdf): coding agents may generate *supporting infrastructure*; the core algorithmic contribution, evaluation methodology, and all research content must be the team's own work. Applied to this project:

### May use coding agents (supporting infrastructure)

| Component / task | Notes |
|---|---|
| `data_loader.py` | Data ingestion pipeline; explicitly permitted category. |
| BM25 / dense / reranker plumbing | Library calls (`rank_bm25`, `sentence-transformers`, cross-encoder loading), batching, embedding caching, index building. The methods are off-the-shelf; no novel algorithm here. |
| Experiment runner | Config handling, argparse, logging, reproducibility plumbing. |
| CSV output and figures | Result serialization, matplotlib formatting, tables generation. |
| `demo.py` | Demonstration script around already-built components. |
| README, `requirements.txt` | Scaffolding and instructions. |
| Unit tests for utilities | Explicitly listed as recommended AI usage. |

Every agent session must be logged (see session-log rule below), and agent-generated components must be reviewed, understood, and modified by hand where needed — the Explanation Test applies to all code regardless of origin.

### Must be done by team members (no agent generation)

| Component / task | Why |
|---|---|
| `evaluator.py` metric logic (Any/Full/Partial Evidence Recall, reciprocal rank used for MRR@10/MRR@50) | The evidence coverage metrics are the project's evaluation methodology — a core intellectual contribution. |
| `failure_analyzer.py` decision rules | The failure taxonomy and its operational labeling rules (including the first-hop-only vs missing-bridge-entity disambiguation) are the project's main research contribution. |
| Fine-tuning pair construction and training loop (if the extension is chosen) | Training loop logic is explicitly listed as not permitted for agents. |
| Manual failure labeling and qualitative example analysis | Error analysis is research content. |
| Report: research questions, results interpretation, failure analysis, discussion | AI may only proofread and reword; it may not produce the intellectual content. |
| Presentation slides and speaker notes | AI-generated slide decks are explicitly prohibited; AI may give structural advice and proofread only. |

### Session-log rule

Keep an ongoing AI session log **as you go** (docs/Completion_Log/): for each coding-agent session record the date, tool, prompts used, and the scope of generated output (files/functions). This feeds directly into the AI Usage Declaration; reconstructing it at the end is error-prone. Updating the log is a recurring shared task every week.

---

## Team Division Overview

## Xin Ownership

Xin mainly owns:

```text
Dense retrieval
Dense retrieval experiments
Dense failure analysis
Dense semantic drift examples
Bridge vs comparison analysis
Results interpretation
Discussion section
Part of presentation explanation
```

Xin's core contribution can be framed as:

> Dense retrieval is not simply “more semantic = better.” It can help with lexical mismatch, but it can also fail through semantic drift and incomplete evidence coverage.

This connects well to representation learning, embeddings, semantic similarity, and vector-space reasoning.

## Jiajun Ownership

Jiajun mainly owns:

```text
HotpotQA data loader
BM25 baseline
Evaluator
Experiment runner
Result CSV generation
README
demo.py support
Packaging
```

Jiajun's core contribution can be framed as:

> We built a controlled retrieval evaluation pipeline that measures not only whether any evidence is retrieved, but whether all required multi-hop evidence is covered.

## Shared Ownership

Both Xin and Jiajun should contribute to:

```text
Final failure taxonomy
Qualitative example selection
Final report editing
Presentation slides
AI Usage Declaration
Explanation Test
```

The failure taxonomy should be shared because it is part of the project's intellectual contribution.

---

# Weekly Plan

**Two hard deadlines:**

- **7/28 — final presentation (slides due).** Present whatever is ready at that time — the instructor confirmed results do not need to be finished (or frozen) before the presentation. Slides are still built and rehearsed in Week 3.
- **8/14 — full submission** (code + report + demo.py + AI Usage Declaration).

## Week 1: 7/7–7/13

## Goal

> Build the first working retrieval-evaluation loop.

This week is not about making the pipeline elegant. The goal is to make the full path work:

```text
HotpotQA example -> paragraph corpus -> retriever -> top-k results -> basic metric
```

## Xin Tasks

- Understand the dense retrieval pipeline.
- Choose the first embedding model.
- Start with `sentence-transformers/all-MiniLM-L6-v2` unless there is a strong reason to switch.
- Build a minimal dense retriever prototype.
- Run dense retrieval on 10 HotpotQA examples.
- Manually inspect whether dense top-k results look reasonable.

## Jiajun Tasks

- Build the HotpotQA data loader.
- Extract the following fields:
  - question
  - context passages
  - supporting facts
  - question type
  - answer
- Build paragraph-level retrieval corpus from the provided HotpotQA contexts.
- Implement BM25 baseline.
- Implement the first version of Any Evidence Recall@k / Evidence Hit@k.

## Shared Tasks

- Create GitHub repo.
- Confirm code structure.
- Confirm retrieval unit is paragraph-level passage.
- Confirm evidence matching rule: map HotpotQA `supporting_facts` title + sentence-index annotations to paragraph-level gold evidence titles.
- Confirm corpus setting uses provided HotpotQA contexts only.
- Create a 10-example debug subset.
- Write README skeleton.
- Update the AI session log (docs/Completion_Log/) for any coding-agent sessions this week.

## Expected Output

By the end of Week 1, the team should be able to output this for 10 examples:

```text
question
gold supporting facts
BM25 top-k passages
dense top-k passages
basic Any Evidence Recall@k
```

## Week 1 Checkpoint

Ask:

```text
Can we load 10 HotpotQA examples?
Can we retrieve top-k passages using BM25?
Can we retrieve top-k passages using dense retrieval?
Can we compute basic Any Evidence Recall@k?
Can we inspect results manually?
```

---

## Week 2: 7/14–7/20

## Goal

> Complete BM25 vs dense retrieval main experiments.

This week should turn the prototype into a real experiment pipeline.

## Xin Tasks

- Finish stable dense retrieval implementation.
- Add embedding caching. For the pooled corpus, encode all ~5,000 paragraphs **once** and cache the embeddings to disk (e.g. `data/pooled_embeddings.npy` + a matching title list), so reruns and metric changes do not re-encode.
- Run dense retrieval on 100 examples.
- Then run dense retrieval on 500 examples if runtime is acceptable.
- Run dense retrieval in **both corpus settings** (pooled primary, per-question contrast). The retriever core logic is unchanged; only the calling pattern differs: per-question builds a small index per question, pooled builds **one shared index** queried by all questions.
- In the pooled setting, save dense top-50 candidate lists per question (titles + scores) — this is the reranker's input in Week 3.
- Save dense retrieval results to CSV (`results/dense_results.csv`), following `docs/specs/2026-07-15-results-csv-schema.md`.
- Start recording initial dense success/failure patterns.

## Jiajun Tasks

- Complete evaluator.
- Implement:
  - Any Evidence Recall@k / Evidence Hit@k
  - Full Evidence Recall@k
  - Partial Evidence Recall@k
  - MRR@10 (primary) and MRR@50 (pooled deep-ranking diagnostic)
- Run BM25 on 100 examples.
- Then run BM25 on 500 examples if runtime is acceptable.
- Run BM25 in **both corpus settings** (pooled primary, per-question contrast).
- Save BM25 top-50 titles in pooled formal results so its rank-11–50 behavior is directly comparable with Dense and rerank.
- Save BM25 results to CSV (`results/bm25_results.csv`), following the finalized results-CSV schema: `docs/specs/2026-07-15-results-csv-schema.md`. **Coding agents must read that spec before writing any results CSV** — it fixes the column set, `1`/`0` booleans, the `" | "` title separator, and the per-setting k policy.
- Make the experiment runner reproducible.

## Shared Tasks

- Build the pooled retrieval corpus (all evaluation questions' paragraphs, deduplicated by title) and share it across both retrievers.
  - Dedup rule: if the same title appears in multiple questions with slightly different paragraph text, keep the first occurrence and log the collision. Evaluation is unaffected because gold matching is by title.
  - The pooled corpus must be built once in `data_loader.py` and passed to both retrievers, so BM25 and dense query the identical paragraph set.
- Standardize result format across BM25 and dense retrieval, and across both corpus settings.
  - Every result CSV row must carry a `setting` field (`pooled` / `per_question`) in addition to method, example id, and metrics, so downstream analysis and figures can filter by setting.
  - **Done (Xin, 7/15; amended 7/17):** schema finalized in `docs/specs/2026-07-15-results-csv-schema.md` — long format, one row per (method, setting, example); one file per method with an identical column set; pooled rows store top-50 for BM25, Dense, and rerank. Per-example RR fields are explicit at 10 and 50.
- Reporting rule for tables: pooled setting reports k = 2, 5, 10; per-question setting reports k = 2 only (k = 5 near ceiling, k = 10 trivially 100%).
- Check whether gold evidence matching is correct.
- Generate the first main results table.
- Run the Week 2 stability checkpoint (see below); the fine-tuning go/no-go decision itself happens in Week 4, after the 7/28 presentation.
- Update the AI session log (docs/Completion_Log/) for any coding-agent sessions this week.

## Expected Output

By the end of Week 2, the team should have:

```text
results/bm25_results.csv
results/dense_results.csv
results/main_results_v1.csv
```

The main results table should look like:

| Method | Any Evidence Recall@2 | Any Evidence Recall@5 | Any Evidence Recall@10 | Full Evidence Recall@2 | Full Evidence Recall@5 | Full Evidence Recall@10 | Partial Evidence Recall@5 | MRR@10 | MRR@50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BM25 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Dense | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Week 2 Checkpoint

Reranking is core (promised in the proposal) and is scheduled for Week 3 regardless. The fine-tuning go/no-go decision has moved to Week 4, after the 7/28 presentation — Week 3 has no room for it (reranker + failure analysis + slides).

The Week 2 checkpoint is stability triage only:

If BM25 + dense + evaluation (including the pooled-corpus runs) are stable by 7/20:

> Proceed to Week 3 as planned (reranker, failure analysis, slides).

If they are not stable:

> Recover time by simplifying elsewhere (smaller final dataset, fewer figures) — the reranker and the 7/28 presentation cannot be cut. Anything not presentation-ready in time simply stays out of the slides (the instructor confirmed presenting whatever is done at that time is fine) and continues afterward toward the 8/14 submission.

---

## Week 3: 7/21–7/27

## Goal

> Complete core failure analysis and the final presentation deliverables. **The presentation is 7/28 — whatever is finished this week is what gets shown** (the instructor confirmed: results need not be complete by then; present whatever you have).

This is the most important week for the project's research contribution, and the busiest: reranker, failure analysis, and slides all land here. Pick the slide-content snapshot by ~7/26 (what goes into the deck) — this is a soft cut for slide-making, not a hard results freeze; work continues after the presentation.

The project should not only answer:

> Which retriever has higher scores?

It should answer:

> Why do the retrievers fail differently?

## Xin Tasks

- Implement the reranker: off-the-shelf cross-encoder (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) over dense top-50 (pooled) / all candidates (per-question); save reranked results to CSV.
- Build the failure review pipeline: structured run outputs (`results/runs/<run_id>/` with per-question details, metrics, and run config) + a static HTML page for browsing and manually labeling failures. Xin's personal tooling, can start early; design: `docs/specs/2026-07-12-failure-review-pipeline-design.md`. Labels export to `results/annotations/annotations.csv`.
- Analyze dense retrieval failures.
- Find dense semantic drift examples (the pooled corpus is where drift can actually occur).
- Analyze bridge vs comparison performance.
- Find cases where dense succeeds but BM25 fails.
- Find cases where dense retrieves topically similar but non-evidential passages.
- Compare dense behavior between the pooled and per-question settings.
- Write notes for dense retrieval interpretation.

## Jiajun Tasks

- Analyze BM25 failures.
- Find lexical mismatch examples.
- Find distractor entity examples.
- Implement disagreement case extractor.
- Extend the evaluator with reranker rescue/damage counting (compare gold coverage in top-k before vs after reranking).
- Export failure cases to CSV. *(To be discussed with Jiajun: the failure-review runner now writes structured per-run outputs (`results/runs/<run_id>/details.jsonl`); the code has landed, first real run still pending. Once a run exists, this export could be derived from it instead of re-implementing the filtering. Suggestion: hold off implementing this script until that first real run is available, to avoid rework — task content unchanged until discussed.)*
- Prepare BM25 interpretation notes.

## Shared Tasks

- Finalize failure taxonomy.
- Write explicit decision rules for each failure category (including the first-hop-only vs missing-bridge-entity disambiguation rule) and validate them against ~20 manually labeled examples. The manual labels live in `results/annotations/annotations.csv` (column schema: `docs/specs/2026-07-12-failure-review-pipeline-design.md` §6.1) — the shared contract is the CSV format, not the tool; label via Xin's HTML review page or any editor. **AI policy: these rules and their implementation in `failure_analyzer.py` are the project's core research contribution and must be hand-written by team members, not generated by a coding agent.**
- Select 10–20 qualitative examples.
- Build bridge vs comparison result table.
- Build disagreement cases table.
- Pick the slide-content snapshot by ~7/26: main results table, bridge vs comparison table, reranker rescue/damage table, failure-category highlights, 2–4 strongest qualitative examples. (Soft cut for building the slides — not a results freeze; results may keep evolving after the presentation.)
- Build the presentation slides together and rehearse. **AI policy: slides and speaker notes must be created by team members; AI may give structural advice and proofread only — no AI-generated decks.**
- Start writing Results and Failure Analysis notes (these feed both the slides and the report). **AI policy: results interpretation and failure analysis are research content — write them yourselves; AI may only proofread.**
- Update the AI session log (docs/Completion_Log/) for any coding-agent sessions this week.

## Failure Taxonomy

Use these failure categories:

| Failure mode | Meaning |
|---|---|
| First-hop-only failure | Retriever finds the passage related to the explicit entity but misses the second supporting passage. |
| Missing bridge entity | Retriever fails to retrieve evidence about the bridge entity needed for the second hop. |
| Comparison coverage failure | Retriever covers only one side of a comparison question. |
| Lexical mismatch | BM25 fails because the question and evidence use different surface forms. |
| Dense semantic drift | Dense retrieval finds semantically related but non-evidential passages. |
| Distractor entity failure | Retriever retrieves a similar-looking but wrong entity or passage. |

## Expected Output

By the end of Week 3, the team should have:

```text
results/subgroup_results.csv
results/disagreement_cases.csv
results/failure_cases.csv
results/rerank_results.csv
results/rerank_rescue_damage.csv
results/runs/<run_id>/          (details.jsonl / metrics.json / config.json per retrieval run)
results/annotations/annotations.csv   (manual failure labels; validation set for failure_analyzer.py)
final presentation slides (rehearsed, ready for 7/28)
```

The team should be able to answer:

```text
When does BM25 beat dense retrieval?
When does dense retrieval beat BM25?
Where do bridge questions fail?
Where do comparison questions fail?
Does dense retrieval show semantic drift?
Does BM25 show lexical mismatch?
How often do retrievers get partial evidence but not full evidence?
```

---

## Week 4: 7/28–8/3

## Goal

> **7/28: deliver the final presentation.** Then lock experiments and build final deliverables.

After the presentation, freeze the experiment setup. Do not keep adding new scope.

## Week 4 Decision Point (fine-tuning)

Right after the presentation, decide whether to add the fine-tuning extension:

> Add it only if the core project (BM25, dense, reranker, failure analysis) presented cleanly and the extension fits entirely inside this week (7/29–8/3). Otherwise drop it — its results go into the report only, and the report cannot wait past Week 4 for it. Training-pair construction and the training loop must be hand-written (AI policy).

## Xin Tasks

- Present the dense/reranker/failure-analysis half on 7/28; collect instructor and audience feedback.
- If fine-tuning is chosen at the decision point: construct training pairs, run fine-tuning (hand-written training code), run the fine-tuned encoder evaluation, and build the per-failure-category before/after table — all within this week.
- Write Dense Retrieval method section.
- Write dense failure analysis section.
- Write bridge vs comparison analysis discussion.
- Organize semantic drift examples.
- Organize comparison coverage examples.
- Help choose predefined examples for `demo.py`.

## Jiajun Tasks

- Finalize experiment runner.
- Run final BM25, dense, and dense + rerank experiments.
- Generate final CSV files.
- Generate final tables and figures.
- Implement `demo.py`.
- Write README.
- Add basic unit tests.

## Shared Tasks

- Decide final dataset size: 500 or 1000 examples.
- Freeze experiment configuration.
- Generate final tables.
- Generate final figures.
- Incorporate presentation feedback into the analysis and the report plan.
- Start report skeleton.
- Run first Explanation Test.
- Update the AI session log (docs/Completion_Log/) for any coding-agent sessions this week.

## Expected Output

By the end of Week 4, the repo should contain:

```text
results/main_results.csv
results/subgroup_results.csv
results/disagreement_cases.csv
results/failure_cases.csv
results/figures/
demo.py
README.md
requirements.txt
report_draft_v1.md
presentation feedback notes (presentation delivered 7/28)
```

## Scope Warning

Do not add these in Week 4:

```text
Full RAG answer generation
Query decomposition
Hybrid retrieval
Full Wikipedia retrieval
LLM judge
Complex UI
Large new model comparisons
```

At this point, stability is more important than ambition.

---

## Week 5: 8/4–8/10

## Goal

> Finish the report and explanation readiness (the presentation was delivered 7/28).

This week turns the project from “working code” into a complete submission.

**AI policy for all writing tasks this week:** the report's research content (research questions, methods rationale, results, failure analysis, discussion) must be written by team members. AI may be used only for proofreading, grammar, and structural advice — it may not generate the intellectual content.

## Xin Tasks

- Finish Introduction.
- Finish Research Questions.
- Finish Dense Retrieval method section.
- Finish Failure Analysis section.
- Finish Discussion section, incorporating presentation feedback.
- Check whether qualitative examples are convincing.

## Jiajun Tasks

- Finish Dataset section.
- Finish BM25 method section.
- Finish Evaluation Metrics section.
- Finish Implementation section.
- Finish README instructions.
- Check that `demo.py` is easy to run.

## Shared Tasks

- Merge report sections.
- Write AI Usage Declaration: compile it from the ongoing session log in docs/Completion_Log/; document tools used, nature of each significant interaction, affected files/functions, agent session prompts and output scope, and the agent-generated vs hand-written boundary (see the AI Usage Boundary section above).
- Update the AI session log (docs/Completion_Log/) for any coding-agent sessions this week.
- Run Explanation Test together.
- Check all figures and tables against result CSVs.
- Make sure both members can explain the metrics and code.

## Expected Output

By the end of Week 5, the team should have:

```text
final_report_draft_v2.pdf or .docx
AI Usage Declaration draft
clean README
working demo.py
```

## Explanation Test Questions

Both team members should be able to answer:

```text
What does Any Evidence Recall@k / Evidence Hit@k measure?
Why is Any Evidence Recall@k insufficient for multi-hop QA?
What does Full Evidence Recall@k measure?
What does Partial Evidence Recall@k measure?
What do MRR@10 and MRR@50 measure, and why is @10 primary?
How does BM25 retrieve passages?
How does dense retrieval retrieve passages?
How does the cross-encoder reranker score candidates, and how is that different from the bi-encoder?
Why can dense retrieval fail through semantic drift?
Why can BM25 fail through lexical mismatch?
Why can a reranker never rescue evidence that dense retrieval left out of the top-N candidate set?
What is a reranker rescue and a reranker damage case?
```

---

## Final Days: 8/11–8/14

## Goal

> Submit a clean final package.

No new features should be added during the final days.

## Xin Tasks

- Proofread report discussion.
- Check failure analysis clarity.
- Make sure dense retrieval code is explainable.
- Check that dense failure examples are accurate.

## Jiajun Tasks

- Clone repo from scratch and test README commands.
- Check `demo.py`.
- Check `requirements.txt`.
- Check result files.
- Prepare final zip package.

## Shared Tasks

- Freeze code.
- Check references.
- Check figures and tables.
- Run final demo.
- Confirm submission format.
- Submit final package.

## Final Submission Checklist

Before submission, ask:

```text
Can we clone the repo from scratch and run demo.py?
Can both people explain their own code?
Can both people explain the metrics?
Can both people explain why Full Evidence Recall matters more than Any Evidence Recall@k?
Can we explain the reranker rescue/damage results and their net effect on full evidence coverage?
Does the report clearly show failure analysis, not just score comparison?
Is the AI Usage Declaration honest and specific?
Are all figures and tables generated from saved result files?
Is the final package clean and reproducible?
```

---

# Simplified Weekly Milestone Table

| Week | Main goal | Xin | Jiajun | Shared deliverable |
|---|---|---|---|---|
| Week 1, 7/7–7/13 | Run first retrieval loop | Dense prototype | Data loader + BM25 + basic Any Evidence Recall@k | 10-example debug output |
| Week 2, 7/14–7/20 | Complete core experiments | Dense stable + pooled/distractor 500-example runs | Evaluator + BM25 pooled/distractor runs + pooled corpus build | Main results table v1 + stability checkpoint |
| Week 3, 7/21–7/27 | Reranker + failure analysis + slides (**presentation 7/28**) | Reranker implementation + dense semantic drift + bridge/comparison | BM25 lexical mismatch + disagreement extractor + rescue/damage metrics | Failure-labeling rules + qualitative examples + slide snapshot ~7/26 + rehearsed slides |
| Week 4, 7/28–8/3 | **Present 7/28**, then freeze experiments and demo | Present + fine-tuning decision/work (if chosen) + discussion draft | Final runner + demo.py + README | Final CSV/tables/figures + feedback notes + report skeleton |
| Week 5, 8/4–8/10 | Finish report | Discussion + failure analysis writing | Dataset/method/eval writing | Report v2 + AI declaration |
| Final, 8/11–8/14 | Clean submission | Proofread | Clone test + package | Final submission (8/14) |

---

# Most Important Advice

Start small.

The most important Week 1 goal is not to build the perfect framework. It is to run 10 examples end-to-end and see real retrieval outputs.

A successful final project should clearly show:

```text
BM25 and dense retrieval behave differently.
Any Evidence Recall@k alone is not enough for multi-hop QA.
Full evidence coverage matters.
Partial evidence retrieval explains many failures.
Bridge and comparison questions fail in different ways.
Dense retrieval can help with lexical mismatch but can also drift semantically.
BM25 can be strong on exact entity overlap but weak on paraphrases.
```
