---
status: active
last_updated: 2026-07-29
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
- Exhaustive machine-generated gold-rank patterns for every pooled top-50 `(example_id, retriever)` unit
- Notes-first manual review of selected coverage failures (Full@5 is the proposed follow-up criterion, pending owner freeze); reviewer notes may later support causal themes such as semantic drift, lexical mismatch, missing bridge evidence, incomplete comparison coverage, or distractor entities
- Jointly derive, merge, split, and validate any human failure-reason taxonomy from the reviewed evidence instead of freezing categories in advance
- Reranker rescue and damage cases

### Optional Extension

Reranking is core (committed in the submitted proposal), **not** optional. Only one optional extension remains, added only if the core project including the reranker is on track:

- Contrastive fine-tuning of the dense retriever on HotpotQA train-split pairs, evaluated **per failure category** (which failures does fine-tuning fix, which persist). Training-pair construction and training loop must be hand-written per the AI policy. Must not compete with the reranker or the presentation for time: the go/no-go decision happens in Week 5, **after the 8/4 presentation**, and its results go into the report only.

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
| Human failure-reason taxonomy and any later `failure_analyzer.py` decision rules | The causal categories must be derived from reviewed evidence. If the team later operationalizes them, the definitions, merge/split decisions, and labeling rules are part of the project's main research contribution. |
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
Evidence-bearing manual review notes and the jointly derived/refined failure-reason taxonomy
Qualitative example selection
Final report editing
Presentation slides
AI Usage Declaration
Explanation Test
```

The manual interpretation and any eventual failure-reason taxonomy should be shared because they are part of the project's intellectual contribution. Machine-generated `rank_pattern` values are structural descriptions, not causal labels.

---

# Weekly Plan

**Two hard deadlines:**

- **8/4 — final presentation (slides due).** Present whatever is ready at that time — the instructor confirmed results do not need to be finished (or frozen) before the presentation. Slides are finalized and rehearsed in Week 4.
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
- Run the Week 2 stability checkpoint (see below); the fine-tuning go/no-go decision itself happens in Week 5, after the 8/4 presentation.
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

Reranking is core (promised in the proposal) and is scheduled for Week 3 regardless. The fine-tuning go/no-go decision has moved to Week 5, after the 8/4 presentation — Week 3 remains focused on the reranker and failure analysis.

The Week 2 checkpoint is stability triage only:

If BM25 + dense + evaluation (including the pooled-corpus runs) are stable by 7/20:

> Proceed to Week 3 as planned (reranker, failure analysis, slides).

If they are not stable:

> Recover time by simplifying elsewhere (smaller final dataset, fewer figures) — the reranker and the 8/4 presentation cannot be cut. Anything not presentation-ready in time simply stays out of the slides (the instructor confirmed presenting whatever is done at that time is fine) and continues afterward toward the 8/14 submission.

---

## Week 3: 7/21–7/27

## Goal

> Complete core failure analysis and prepare the presentation inputs. **The presentation is 8/4**, so Week 4 remains available to finalize the deck and rehearse.

This is the most important week for the project's research contribution: the reranker and failure analysis land here, while the deck is finalized in Week 4. Pick the slide-content snapshot by ~8/2 — this is a soft cut for slide-making, not a hard results freeze; work continues after the presentation.

The project should not only answer:

> Which retriever has higher scores?

It should answer:

> Why do the retrievers fail differently?

## Xin Tasks

- Implement the reranker: off-the-shelf cross-encoder (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) over dense top-50 (pooled) / all candidates (per-question); save reranked results to CSV.
- Maintain the failure review pipeline: structured run outputs (`results/runs/<run_id>/` with per-question details, metrics, and run config), the accepted pooled top-50 rank-pattern artifact (`gold_rank_patterns.csv`), and a static HTML review page. The v1 calibration/open-coding review uses the frozen strict Any@5 criterion and the `results/annotations/manual_review_v1/` file family (`failure_review.html`, `assignment.csv`, `xin_cases.json`, `jiajun_cases.json`), as frozen in `docs/specs/2026-07-27-manual-failure-review-course-protocol.md`. Those four files are generated by `scripts/build_manual_review_batch.py` (with the shared page in `scripts/manual_review_page.py`), which reads `results/runs/2026-07-17_a/` as a read-only source and writes nothing inside it. Each reviewer opens the shared `failure_review.html` by double-click, picks their own cases JSON, and exports a 17-row `<reviewer_id>_notes.csv`; `label` may remain blank during open coding. The legacy singleton `results/annotations/annotations.csv` is informal only and is not a formal review artifact.
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
- Implement disagreement case extractor. **Accepted in DR-004 round 7 and integrated on local `main` in `0c7f00b`.**
- Add reranker rescue/damage counting (compare gold coverage in top-k before vs after reranking). **Accepted in DR-004 round 7 and integrated on local `main` in `0c7f00b`.**
- Coordinate any separate failure-case CSV export with the existing structured run outputs and accepted `gold_rank_patterns.csv`; decide whether it is still needed after the incoming disagreement extractor is available for audit.
- Prepare BM25 interpretation notes.

## Shared Tasks

- Use the deterministic 10-class `rank_pattern` partition from `docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md` for machine-readable structure. The accepted implementation is `src/rank_pattern.py` plus `scripts/reporting/build_gold_rank_patterns.py` (rebased commit `741a34f`); `rank_pattern` must never be written into any annotation `label` column.
- Conduct notes-first manual review: record concrete evidence in each reviewer's `results/annotations/manual_review_v1/<reviewer_id>_notes.csv` export, not in the legacy informal `results/annotations/annotations.csv`; a non-empty note with an empty `label` counts as reviewed during open coding. After a review batch, jointly group, refine, merge, or split candidate causal reasons. Only after the categories converge should the team hand-write definitions/decision rules and validate them against reviewed examples. **AI policy: the human interpretations, category decisions, and any operational rules are the project's core research contribution and must be written by team members.**
- Before changing the HTML or starting the main manual-review batch, jointly approve `docs/specs/2026-07-27-manual-failure-review-course-protocol.md`. The course workflow uses one shared HTML implementation that loads reviewer-specific assigned cases; Xin and Jiajun export separate annotation files. Bundle/ledger/anchor-registry provenance is deferred until after the course.
- Select 10–20 qualitative examples.
- Build bridge vs comparison result table.
- Build disagreement cases table.
- Pick the slide-content snapshot by ~8/2: main results table, bridge vs comparison table, reranker rescue/damage table, structural rank-pattern highlights, any manually supported reason themes, and 2–4 strongest qualitative examples. (Soft cut for building the slides — not a results freeze; results may keep evolving after the presentation.)
- Start building the presentation slides; finalize and rehearse them in Week 4. **AI policy: slides and speaker notes must be created by team members; AI may give structural advice and proofread only — no AI-generated decks.**
- Start writing Results and Failure Analysis notes (these feed both the slides and the report). **AI policy: results interpretation and failure analysis are research content — write them yourselves; AI may only proofread.**
- Update the AI session log (docs/Completion_Log/) for any coding-agent sessions this week.

## Failure Analysis: Machine Structure + Human Reasons

Keep the two layers separate:

| Layer | Contract |
|---|---|
| Machine structure | `rank_pattern` is a deterministic, mutually exclusive, collectively exhaustive 10-class partition over the two gold ranks in bands 1–5, 6–10, 11–50, and absent from top 50. It is generated for all pooled top-50 units under `gold_rank_partition_v1`; see `docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md`. It describes *where* the gold evidence ranked and computes no metric or causal failure reason. |
| Human reason | Reviewers first write evidence-bearing notes explaining *why* a selected case may have failed. Semantic drift, lexical mismatch, missing bridge evidence, incomplete comparison coverage, and distractor entities are candidate themes—not a frozen or exhaustive label set. The team derives and validates any taxonomy only after reviewing a batch. |

The HTML review criterion is a separate owner decision. The current Any@5 failure filter excludes every unit with at least one gold in the top five; switching to Full@5 would include partial-coverage cases and therefore increase the manual-review workload. Do not change that criterion, its cutoff, or its delivery model until the next review-stage design is frozen.

## Expected Output

By the end of Week 3, the team should have:

```text
results/subgroup_results.csv
results/rerank_results.csv
results/runs/<run_id>/          (details.jsonl / metrics.json / config.json per retrieval run)
results/runs/<run_id>/gold_rank_patterns.csv   (accepted 10-class machine partition; all pooled top-50 units)
results/annotations/manual_review_v1/failure_review.html  (the one shared file-picker review page; open by double-click)
results/annotations/manual_review_v1/assignment.csv     (frozen 30-unit assignment; Section 3.4 oracle)
results/annotations/manual_review_v1/xin_cases.json      (Xin's 17-case reviewer file)
results/annotations/manual_review_v1/jiajun_cases.json   (Jiajun's 17-case reviewer file)
results/annotations/manual_review_v1/<reviewer_id>_notes.csv (17-row notes export; label may be blank during open coding)
results/annotations/annotations.csv                                          (legacy informal singleton; not a formal review artifact)
results/disagreement_cases.csv        (accepted in DR-004 round 7; integrated in 0c7f00b)
results/rerank_rescue_damage.csv      (accepted in DR-004 round 7; integrated in 0c7f00b)
presentation content snapshot and draft slides for Week 4 finalization
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

## Week 4: 7/28–8/4

## Goal

> Produce, validate, rehearse, and submit the team-authored final presentation on 8/4.

Week 4 is a **presentation-first sprint**. Work that does not directly support the deck, the talk, Q&A readiness, or the Canvas submission moves to Week 5. Use a validated presentation results snapshot; this is a soft content snapshot for the slides, not a claim that every report experiment is permanently frozen.

The team must create the final slides and speaker material. AI may provide structural advice, proofreading, or permitted visualization support, but it must not generate the deck, speaker notes, results interpretation, qualitative analysis, or other intellectual content.

## Non-Negotiable Priority Order

1. Validate the presentation result inputs and experimental facts.
2. Prepare only the tables, figures, and qualitative examples needed for the talk.
3. Assemble the complete deck and divide speaking responsibilities.
4. Run timed rehearsals, fix readability and timing, and prepare for Q&A.
5. Upload the final deck to Canvas before class on 8/4.

Until the presentation is submitted, do not prioritize `demo.py`, report drafting, optional fine-tuning, new models, larger datasets, or figures that will not appear in the main deck or backup slides.

## Presentation Results Snapshot

By 7/31, validate and record the following presentation inputs:

- Experiment scope: 500 HotpotQA validation examples, including 404 bridge and 96 comparison questions.
- Primary pooled corpus: 4,937 deduplicated passages.
- Methods: BM25, Dense, and Dense + Rerank.
- Model names, retrieval depth, reranking candidate depth, corpus settings, and k cutoffs.
- One compact pooled-corpus main results table comparing the same metrics across all three methods.
- A bridge-vs-comparison subgroup table containing only the values needed for the talk or backup.
- Reranker rescue/damage counts at the selected presentation cutoff.
- The number and selection procedure for machine rank-pattern units and manually reviewed cases.
- Two to four team-selected qualitative examples supported by human-written review notes.

Every displayed value must be traceable to a saved CSV or run configuration. Use two decimal places consistently. Machine rank patterns may describe where gold evidence ranked, but only the team members may interpret why a case failed.

## Presentation Tables and Visualizations

Keep the main deck selective:

- Use one compact main table or grouped bar chart emphasizing the difference between Any Evidence and Full Evidence coverage at a presentation-relevant cutoff such as k = 5.
- Use at most one additional main-deck visualization: either bridge vs comparison Full Evidence Recall or reranker rescue/damage. Put the other analysis in backup slides if it is ready.
- Keep secondary cutoffs, MRR@50, the per-question contrast setting, and detailed rank-pattern counts in backup unless they are essential to the spoken argument.
- Include a small worked example that distinguishes no evidence, partial evidence, and full evidence retrieval.
- Generate every numeric table and figure from saved result files; do not manually retype values without cross-checking them.

## Presentation Slide Ownership Map

“Primary owner” means the person responsible for producing the first complete, presentation-ready version and explaining it during the talk. “Required reviewer” must check correctness and clarity before the content is frozen. Shared review does not transfer or blur primary ownership.

| Presentation content | Primary owner | Required reviewer / contribution |
|---|---|---|
| Title and introductions | Shared | Each member writes and delivers their own introduction. |
| Motivation, problem statement, project goal, and retrieval-only scope | Xin | Jiajun checks consistency with the implemented system. |
| Dataset overview and bridge/comparison dataset examples | Jiajun | Xin checks that the examples support the research motivation. |
| Overall experimental workflow | Jiajun | Xin checks the Dense and reranking branches. |
| **BM25 concept and expected strengths/limitations** | **Jiajun** | Xin checks the cross-method comparison wording. |
| **Dense Retrieval concept and expected strengths/limitations** | **Xin** | Jiajun checks implementation details and model naming. |
| **Dense + Cross-Encoder Reranking concept and candidate flow** | **Xin** | Jiajun checks retrieval depth, candidate depth, and saved-result consistency. |
| Evaluation metrics and worked metric example | Jiajun | Xin checks that the example supports the multi-hop motivation. |
| Experimental setup and reproducibility facts | Jiajun | Xin checks Dense/reranker settings. |
| Main-results table/figure generation and numeric validation | Jiajun | Xin independently cross-checks the selected values. |
| Main-results interpretation and spoken comparison | Xin | Jiajun checks that every claim matches the validated values. |
| BM25-specific result and failure explanation | Jiajun | Xin checks consistency with the joint failure analysis. |
| Dense/reranker result, rescue/damage, and failure explanation | Xin | Jiajun checks consistency with saved artifacts. |
| Manual-review procedure | Jiajun | Xin checks that it matches the review actually performed. |
| Human failure reasons and qualitative-case interpretation | Shared | Both members must contribute review notes and jointly approve every presented reason; Xin assembles the slide. |
| Discussion, limitations, and conclusion | Xin | Jiajun checks technical and scope accuracy. |
| Team contributions | Shared | Each member writes their own contribution bullets; Jiajun assembles the slide without changing ownership claims. |
| AI Usage Disclosure | Shared | Each member supplies their own usage record; Jiajun assembles it and both members approve it. |
| Final deck integration, formatting, export, and Canvas upload | Jiajun | Xin performs the final content check; both approve the exact file before Jiajun uploads it. |
| Presentation feedback notes | Jiajun | Xin adds research-content feedback and verifies the final notes before report planning. |

## Xin Tasks

- Independently interpret and verify the dense and reranker results that may appear in the presentation.
- Verify bridge-vs-comparison observations against the saved subgroup data.
- Complete Xin's assigned manual-review notes and select evidence-backed qualitative examples with Jiajun.
- Draft, in Xin's own words, the Dense Retrieval concept, Dense + Cross-Encoder Reranking concept, cross-method results interpretation, dense/reranker failure analysis, discussion, limitation, and conclusion slides assigned in the ownership map.
- Prepare and rehearse Xin's speaking portion so the results and failure analysis are not rushed.
- Prepare concise answers about dense semantic matching, semantic drift, subgroup behavior, reranker rescue/damage, and the limits of the evidence.

## Jiajun Tasks

- Validate the presentation snapshot against the formal BM25, Dense, and rerank CSVs and the saved run configuration.
- Generate the presentation-specific aggregate table, subgroup table, and one to two figures from saved results.
- Verify dataset counts, corpus size, model names, retrieval depth, cutoffs, duplicate-title handling, and missing-gold handling.
- Complete Jiajun's assigned manual-review notes and select evidence-backed qualitative examples with Xin.
- Draft, in Jiajun's own words, the dataset, overall workflow, BM25 concept, evaluation-metric, experimental-setup, BM25-specific result/failure, contribution-integration, and AI-disclosure-integration slides assigned in the ownership map.
- Perform the deck's final technical check, including fonts, image resolution, links, animations, and PDF export.

## Shared Tasks

- Agree on the research questions and the single presentation narrative before polishing individual slides.
- Build the final deck together and keep motivation, problem statement, and project goal distinct.
- Explicitly show that the project evaluates the retriever rather than final answer generation.
- Review and integrate the owner-produced dataset details, workflow, three method descriptions, metric definitions, worked metric example, results, failure-review procedure, evidence-backed findings, limitations, contributions, AI usage, and conclusion; the ownership map determines who produces each first complete version.
- Keep the main talk visually readable and short enough for 8–10 minutes; move nonessential details to backup slides.
- Assign every main slide to a speaker. Both members must introduce themselves and participate.
- Cross-check every number, axis, legend, caption, example, and claim against its source.
- Clearly distinguish measured findings from hypotheses and avoid claiming a causal failure category without human-reviewed evidence.
- Prepare answers for likely questions about metric definitions, corpus settings, method differences, reranker limits, manual-review validity, AI usage, and project limitations.
- Run at least two timed full-team rehearsals and revise the deck after each rehearsal.
- Complete a final checklist against `docs/Local/From_Professor/CS6120_Final_Project_Presentation_Requirements.md`.
- Upload the final deck to Canvas before class on 8/4 and retain a PDF backup copy.
- Record presentation-related coding-agent use in `docs/Completion_Log/` as it occurs.

## Daily Checkpoints

- **7/28–7/29:** validate the result snapshot, choose the main metrics, agree on the narrative, and assign slides.
- **7/30–7/31:** finish presentation tables/figures, manual-review notes needed for the talk, and qualitative-example selection.
- **8/1:** complete the first full team-authored deck with all required sections present.
- **8/2:** soft-freeze slide content; remove nonessential results and finish backup slides.
- **8/3:** run at least two timed rehearsals, make only clarity/timing corrections, export the final files, and complete the submission check.
- **8/4:** Xin approves the final content; Jiajun performs the file check and uploads the approved deck before class; both present; Jiajun records instructor/audience feedback and Xin verifies the research-content notes.

## Week 4 Exit Criteria

Week 4 is complete only when:

```text
all presentation numbers have been independently cross-checked
the deck covers the professor's required sections
the main talk fits within 8–10 minutes
both members have rehearsed their assigned portions
the team can answer the core metric, method, result, and limitation questions
the deck has been uploaded to Canvas before class
a PDF backup and presentation feedback notes have been retained
```

## Scope Warning

Do not add these before the presentation:

```text
fine-tuning
new retrievers or rerankers
larger evaluation samples
full RAG answer generation
query decomposition
hybrid retrieval
full Wikipedia retrieval
LLM-as-a-judge evaluation
complex UI or dashboard work
report-only tables or figures
```

---

## Week 5: 8/5–8/10

## Goal

> Convert the validated presentation work into a complete, submission-ready report draft and reproducible project package by 8/10.

The report must be complete by 8/10, including all required sections, figures, references, and disclosures. The final four days are reserved for verification and correction, not first-draft writing.

**AI policy for all writing tasks:** the report's research content—including research questions, method rationale, results interpretation, failure analysis, and discussion—must be written by team members. AI may be used only for permitted proofreading, grammar, and structural advice.

## Fine-Tuning Decision Gate

Fine-tuning is optional and **off by default**. Xin and Jiajun make a single joint go/no-go decision on 8/5 after reviewing presentation feedback; both must approve a go decision, and any disagreement means no-go. If approved, Xin owns the hand-written implementation, experiment, validation, and report subsection.

Proceed only if all of the following are true:

- the core BM25, Dense, reranker, evaluation, and failure-analysis results are stable;
- the report outline, section ownership, and required final figures are already fixed;
- the hand-written training-pair and training-loop work can finish, be validated, and be written up by 8/8;
- the extension will not delay the 8/10 complete-report checkpoint.

If any condition is false, record a no-go decision and omit fine-tuning. If a chosen run is incomplete or unstable by 8/8, stop it and submit the core project without the extension.

## Report and Final-Package Ownership Map

The primary owner writes the first complete version and resolves review comments. The required reviewer checks it before the 8/10 report freeze.

| Report/package content | Primary owner | Required reviewer / contribution |
|---|---|---|
| Introduction and Research Questions | Xin | Jiajun checks consistency with the implemented scope. |
| Dataset, split, corpus construction, and dataset statistics | Jiajun | Xin checks bridge/comparison framing. |
| **BM25 concept and method** | **Jiajun** | Xin checks comparison terminology. |
| **Dense Retrieval concept and method** | **Xin** | Jiajun checks implementation details and model naming. |
| **Dense + Cross-Encoder Reranking concept and method** | **Xin** | Jiajun checks candidate flow and retrieval depths. |
| Evaluation Metrics and worked example | Jiajun | Xin checks connection to the research questions. |
| Experimental Setup, implementation, and reproducibility | Jiajun | Xin checks Dense/reranker configuration. |
| Final table/figure generation and numeric validation | Jiajun | Xin independently checks all values used in interpretation. |
| Cross-method quantitative-results interpretation | Xin | Jiajun checks every claim against the final tables. |
| BM25-specific results and failure subsection | Jiajun | Xin checks consistency with the cross-method narrative. |
| Dense/reranker results, rescue/damage, subgroup analysis, and failure subsection | Xin | Jiajun checks consistency with saved artifacts. |
| Human failure-reason definitions and qualitative-case judgments | Shared | Both derive and approve them from their own review notes; Xin integrates the approved material into the report. |
| Discussion, Limitations, and Conclusion | Xin | Jiajun checks technical accuracy and scope. |
| Per-member Contributions | Shared | Each writes their own entry; Jiajun assembles without changing ownership claims. |
| AI Usage Declaration | Jiajun | Each member supplies their own usage records; both approve the final declaration. |
| Citations and references | Section owner | Jiajun performs the final bibliography and cross-reference check. |
| `README.md`, `requirements.txt`, `demo.py`, test record, and submission inventory | Jiajun | Xin performs the final usability/content check. |
| Master report merge, formatting, rendering, and package assembly | Jiajun | Xin performs the final research-content check; both approve submission. |

## Xin Tasks

- Convert presentation feedback into a short list of report corrections; do not expand the project scope.
- Write the Introduction and final Research Questions.
- Write the Dense Retrieval and reranking method sections.
- Write the cross-method quantitative-results interpretation, Dense/reranker results, rescue/damage analysis, bridge-vs-comparison analysis, integrated Failure Analysis, Discussion, Limitations, and Conclusion in Xin's own words.
- Verify every qualitative example and ensure claims remain within the reviewed evidence.
- If and only if the fine-tuning gate passes, complete the permitted hand-written extension work and its evaluation by 8/8.
- Proofread Jiajun's sections for conceptual consistency with the research questions and findings.

## Jiajun Tasks

- Write the Dataset, corpus construction, BM25 concept/method, Evaluation Metrics, Experimental Setup, and Implementation/Reproducibility sections.
- Write the BM25-specific results and failure subsection from Jiajun's own reviewed evidence.
- Finalize presentation-derived tables and figures for report quality, adding secondary results only when they answer a stated research question.
- Finalize `README.md`, `requirements.txt`, and `demo.py` instructions and behavior.
- Run targeted tests for changed reporting, demo, and experiment-runner paths; record the actual test scope.
- Verify that saved result files, run configurations, and reported sample counts agree.
- Proofread Xin's sections for technical consistency with the implementation and saved results.

## Shared Tasks

- Freeze the report outline, final experiment scope, and section ownership on 8/5.
- Derive any final human failure taxonomy jointly from completed review notes; do not let machine rank patterns substitute for causal labels.
- Jiajun maintains and merges the master report document; Xin performs the research-content review. The merged document must contain no placeholder text by 8/7.
- Check that every research question is answered by a result, analysis, or explicit limitation.
- Check every table and figure against the formal result CSVs and use consistent naming, cutoffs, settings, captions, and two-decimal formatting.
- Each section owner adds and verifies citations for their own section; Jiajun completes the final bibliography and cross-reference check.
- Each member supplies their own usage records; Jiajun writes and assembles the AI Usage Declaration from `docs/Completion_Log/`, including tools, significant interactions, affected files/functions, and the agent-generated versus team-written boundary; both members approve it.
- Each member writes their own concrete contribution entry; Jiajun assembles the contribution statement without rewriting ownership claims, and both approve it.
- Incorporate presentation feedback only when it improves correctness or clarity.
- Run the Explanation Test together and resolve any topic that either member cannot yet explain.
- Create a submission inventory covering report, code, data/result artifacts, README, demo, requirements, and AI disclosure.
- Stop adding experiments and freeze report inputs by the end of 8/10.

## Daily Checkpoints

- **8/5:** review presentation feedback, freeze report scope and outline, assign sections, and make the fine-tuning go/no-go decision.
- **8/6:** finish first drafts of all method, dataset, metric, setup, and introduction sections.
- **8/7:** finish results, failure analysis, discussion, limitations, and conclusion; merge a complete draft with no placeholders.
- **8/8:** finalize tables, figures, citations, contributions, and AI Usage Declaration; stop any incomplete optional extension.
- **8/9:** perform cross-review, run the Explanation Test, and verify README/demo/test instructions.
- **8/10:** produce the complete submission-candidate report and freeze code/result/report inputs except for corrective fixes.

## Week 5 Exit Criteria

By the end of 8/10, the team must have:

```text
a complete final-report draft with no placeholder sections
all final tables and figures linked to saved result files
complete references and in-text citations
verified qualitative examples and failure-analysis claims
a specific AI Usage Declaration draft
per-member contribution statements
a clean README, requirements file, and working demo.py
a recorded targeted-test result and reproducibility checklist
a complete submission inventory
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
How were manual-review cases selected, and what evidence supports the final human failure reasons?
Which findings are directly measured, and which are interpretations or hypotheses?
What are the project's main validity and generalization limitations?
```

---

## Final Days: 8/11–8/14

## Goal

> Verify, polish, and submit the final report and project package by 8/14, with an internal submission target of 8/13.

No new features, datasets, models, metrics, experiments, or analyses may be added during the final days. Only correctness, clarity, reproducibility, formatting, and submission fixes are allowed.

## Xin Tasks

- Proofread the full report for research-story coherence and consistency with the stated research questions.
- Recheck results interpretation, failure-analysis language, qualitative examples, discussion, and limitations.
- Confirm that claims about dense retrieval, semantic drift, reranking, and subgroup behavior do not exceed the evidence.
- Make sure Xin can explain all owned code, results, and report sections without relying on the slides.
- Approve the final rendered report and submission package.

## Jiajun Tasks

- Test the documented setup and `demo.py` from a clean clone or equivalent clean environment.
- Check `README.md`, `requirements.txt`, paths, commands, seeds/configuration, and expected outputs.
- Verify that required result files and figure assets are present and that no report link or reference is broken.
- Run the proportionate final test set and record exactly what ran; treat environment/setup errors separately from test failures.
- Prepare the final archive or upload package without caches, secrets, large disposable artifacts, or machine-specific paths; after both members approve it, Jiajun performs the final submission upload.
- Approve the final rendered report and submission package.

## Shared Tasks

- **8/11:** complete content proofreading, citation checking, figure/table checking, and formatting review.
- **8/12:** perform clean-environment reproducibility checks, final demo, and final Explanation Test.
- **8/13:** Jiajun renders and packages the final report/project; Xin completes the research-content check; both approve the exact files; Jiajun submits early if Canvas permits.
- **8/14:** use only as a contingency window for upload verification or critical corrective fixes; Jiajun confirms successful submission before the deadline and Xin independently checks the confirmation.
- Check page layout, figure readability, table overflow, captions, numbering, references, and appendix placement in the final rendered report.
- Confirm that the report, repository/package, demo, AI Usage Declaration, and contribution statement all describe the same final scope.
- Retain a local copy of the exact submitted report and package plus submission confirmation.

## Final Submission Checklist

Before submission, confirm:

```text
The report contains no placeholders, tracked changes, comments, or broken references.
Every research question is answered or explicitly bounded by a limitation.
Every reported number is traceable to a saved result artifact.
Every figure and table is readable, captioned, and consistent with the text.
The failure analysis is based on human-written review evidence rather than machine rank patterns alone.
The repository/package can be set up using the README instructions.
demo.py runs using the documented command and inputs.
Both members can explain their code, metrics, results, and methodological choices.
The AI Usage Declaration is honest, specific, and consistent with the session logs.
The package contains no secrets, caches, temporary files, or avoidable large artifacts.
The final report and all required project files have been uploaded successfully.
A copy of the submitted files and submission confirmation has been retained.
```

---

# Simplified Weekly Milestone Table

| Week | Main goal | Xin | Jiajun | Shared deliverable |
|---|---|---|---|---|
| Week 1, 7/7–7/13 | Run first retrieval loop | Dense prototype | Data loader + BM25 + basic Any Evidence Recall@k | 10-example debug output |
| Week 2, 7/14–7/20 | Complete core experiments | Dense stable + pooled/distractor 500-example runs | Evaluator + BM25 pooled/distractor runs + pooled corpus build | Main results table v1 + stability checkpoint |
| Week 3, 7/21–7/27 | Reranker + failure analysis + presentation inputs | Reranker implementation + rank-pattern artifact + dense/bridge/comparison review | BM25 review + disagreement extractor + rescue/damage metrics (accepted in DR-004 round 7; integrated in `0c7f00b`) | Accepted machine rank-pattern partition + notes-first review plan + qualitative evidence |
| Week 4, 7/28–8/4 | **Presentation-first sprint; present 8/4** | Dense and Dense + Rerank concepts; cross-method interpretation; failure-analysis/discussion slides; rehearsal | BM25 concept; workflow/dataset/metrics/setup slides; generate and validate presentation tables/figures; deck integration | Cross-checked deck, two timed rehearsals, Canvas upload, presentation feedback |
| Week 5, 8/5–8/10 | Complete report and reproducible package | Dense/rerank methods and results; cross-method interpretation; integrated failure analysis, discussion, limitations, conclusion | Dataset/corpus; BM25 method and BM25-specific analysis; metrics/setup; tables/figures; README/demo/tests; master report/package | Complete report draft, final figures, approved AI declaration, submission candidate by 8/10 |
| Final, 8/11–8/14 | Verify, polish, and submit | Research-content final check | Clean-environment and packaging check | Internal submission target 8/13; hard deadline 8/14 |

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
