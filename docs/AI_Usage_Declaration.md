---
status: draft
last_updated: 2026-08-13
---

# AI Usage Declaration

CS6120 Final Project — HotpotQA Retrieval Failure Analysis
Xin Wang, Jiajun Fang

## 1. Tools, by team member

| Member | Tool | Period | How it was used |
|---|---|---|---|
| Xin Wang | Claude Code (Claude Opus 5) | 2026-07-07 to 2026-08-13 | Interactive coding-agent sessions inside the project repository |
| Xin Wang | OpenAI Codex | 2026-07-25 to 2026-08-13 | Interactive coding-agent sessions; also used as an independent reviewer of changes the other agent had made |
| Jiajun Fang | *[to be completed by Jiajun before submission]* | | |

Xin used two agents deliberately rather than one, so that neither agent was the
only reader of its own output: work produced in a Claude Code session was
routinely re-checked in a Codex session, and the reverse.

## 2. What the tools were used for

| Purpose | Used | What it covered |
|---|---|---|
| Code generation (supporting infrastructure) | Yes | Retriever plumbing around off-the-shelf models, embedding caching, experiment runners and their CLIs, result serialization and schema validation, reporting scripts, figures, and most unit tests. Enumerated in §3. |
| Debugging | Yes | Repairing HotpotQA loading after a `datasets` upgrade changed `trust_remote_code` behaviour; fixing integration-test breakage after merging a teammate's pooled-corpus commit; a byte-preserving merge of per-question reranker output; diagnosing Windows-specific pytest temporary-path failures that were environment errors rather than test failures. |
| Conceptual help | Yes | Explanations of cosine similarity as a dot product on L2-normalised vectors, bi-encoder versus cross-encoder trade-offs, MRR, and the difference between the per-question and pooled corpus settings. These explanations were used to check Xin's own understanding and fed his private study notes; no explanation text was carried into the report. |
| Code review | Yes | One agent reviewing the other's changes, plus specification-driven acceptance reviews of designs and implementations. Reviews produced written findings, which were corrected and re-verified. A substantial share of the sessions in §6 are review or corrective-pass sessions rather than feature work. |
| Writing assistance | Yes | Proofreading, wording, and structuring of English prose in the README, the repository documentation, the report and slides, and this declaration itself. Never used to produce research content: no finding, interpretation, or limitation was written by an AI tool. |

## 3. Files and functions that received AI assistance

All of the following were generated or substantially edited in Xin's agent
sessions, then reviewed and, where needed, corrected by hand.

**Retrieval and infrastructure modules**

| File | AI-assisted content |
|---|---|
| `src/dense_retriever.py` | Whole module: `DenseRetriever` (`retrieve`, `retrieve_titles`, `retrieve_many`, `retrieve_many_titles`, `_encode`, `_rank_paragraphs`, `_encode_queries`), plus `_build_default_encoder`, `_l2_normalize`, `_try_load_cached_embeddings` |
| `src/embedding_cache.py` | Whole module: `save_embedding_cache`, `load_embedding_cache` |
| `src/cross_encoder_reranker.py` | Whole module: `CrossEncoderReranker` (`rerank`, `rerank_titles`, `_score`) and `_build_default_scorer` |
| `src/top50_export.py` | Whole module: `build_top50_rows`, `build_top50_rows_from_batches`, `write_top50_csv` |
| `src/results_schema.py` | Whole module, including `validate_setting`; the schema decisions it enforces were Xin's |
| `src/rank_pattern.py` | Whole module: `rank_to_band`, `band_count_tuple`, `pattern_from_counts`, `classify_two_gold_rank_pattern`, `first_title_ranks`, `get_gold_ranks`. The partition design it implements is a hand-authored specification of Xin's; the agent wrote the code that implements it, and the module computes no metric and assigns no causal label |
| `src/__init__.py` | Package scaffolding |

**Scripts** — every file below was agent-generated, except `scripts/run_week1_debug.py`, which is Jiajun's.

- Experiment runners: `run_bm25_experiment.py`, `run_dense_experiment.py`, `run_rerank_experiment.py`, `run_failure_review.py`, `run_week1_dense_debug.py`, `smoke_test_reranker.py`
- Review and report builders: `build_failure_report.py`, `build_manual_review_batch.py`, `manual_review_page.py`
- `scripts/reporting/`: `bm25_failure_shortlist.py`, `build_gold_matching_audit.py`, `build_gold_rank_patterns.py`, `disagreement_cases.py`, `formal_result_inputs.py`, `manual_review_category_counts.py`, `plot_rescue_damage.py`, `rerank_rescue_damage_cases.py`, `rescue_damage.py`, `summarize_results.py`, `__init__.py`

**Tests** — every file in `tests/` was agent-generated *except* `tests/test_evaluator.py` (hand-written, §4) and `tests/test_data_loader.py` (Jiajun's baseline, covered by his declaration in §7).

**Other** — `README.md`, `requirements.txt`, the specification and design documents under `docs/`, and the repository's local tooling.

**Files owned by Jiajun, whose AI involvement he declares in §7** —
`src/data_loader.py` (including `load_examples`, `process_example`,
`build_pooled_corpus`), `src/retrievers.py` (`BM25Retriever`),
`scripts/run_week1_debug.py`, `tests/test_data_loader.py`, and the original
`src/evaluator.py` metric implementations. Xin's later additions to
`src/data_loader.py` were limited to compatibility fixes.

## 4. Written by the team, without AI assistance

**Evaluation metric logic.** `src/evaluator.py` is hand-written throughout:
`any_evidence_recall_at_k`, `full_evidence_recall_at_k`,
`partial_evidence_recall_at_k`, `mrr_for_example` (the reciprocal rank behind
MRR@10 and MRR@50), `evaluate_example`, and `aggregate_results` by Jiajun;
`gold_ranks` by Xin. `build_pooled_corpus` in `src/data_loader.py` is likewise
Jiajun's. No agent produced a metric definition at any point in the project.

**The tests that guard the metrics.** `tests/test_evaluator.py`, including its
nine `gold_ranks` unit tests, is hand-written, as are the manual recomputations
used to confirm every reported number against the saved result artifacts.

**Project design.** The research questions, scope, experimental design, corpus
settings, the choice of metrics and cutoffs, the gold-rank partition
specification, and the manual review protocol.

**The entire failure analysis.** All reviewer notes on the 30 reviewed
retrieval failures, the open coding over those notes, the category definitions
and their evidence rules, the 30 final labels, and the findings and limitations
written from them. No agent wrote a note, proposed a category, or assigned a
label.

**The report and the slides.** AI was used for proofreading and wording only,
never for research content.

## 5. The boundary that mattered most

Machine-computed rank structure and human causal explanation are kept apart by
construction, not by convention. The manual-review protocol states that "no
system or agent pre-fills a causal label", and a committed test
(`tests/test_reporting_doc_references.py`) asserts that this sentence is still
present, so the guarantee cannot be quietly dropped. `src/rank_pattern.py`
computes only *where* the gold passages ranked; the failure categories and the
30 labels are our own judgements over our own review notes.

Everything an agent generated was reviewed and, where needed, changed by hand.
Both of us can explain any of it without reference to how it was first written.

## 6. Session-level record

Xin's agent sessions were logged as they happened, in a per-week completion log
that records each session's date, tool, scope of generated output, and the
verification run afterwards.

| Week | Sessions | Tools | What the sessions covered |
|---|---|---|---|
| Week 1 (7/7–7/13) | Recorded as a week-level summary rather than per session | Claude Code | Dense retriever, its offline tests, the side-by-side debug runner; one documentation-only session on the failure-review pipeline design |
| Week 2 (7/15–7/20) | 18 | Claude Code, OpenAI Codex | Embedding cache, pooled shared index and batch query, the formal dense runner, the results schema, top-50 export, the failure-review runner, quality reviews and acceptance checks, a cross-document consistency audit |
| Week 3 (7/25–7/29) | 35 | Claude Code, OpenAI Codex | Cross-encoder reranker and its integration, the failure-review HTML generator, the manual-review protocol, and a long series of independent-review corrective passes against those designs |
| Week 4 (7/29–8/13) | 16 | Claude Code, OpenAI Codex | The three-method results table, presentation figures, documentation of the case-selection procedure, repository documentation, and review corrections |

**Completeness of the prompt record, stated honestly.** From Week 4 onward,
every session entry records the verbatim user prompt alongside its scope. The
Week 1–3 entries record date, tool, scope of output, and verification, but not
verbatim prompt text, because the habit of logging prompts in real time began
later. One Week 3 prompt is recorded as permanently unrecoverable; it was
deliberately left marked as missing rather than reconstructed from memory,
since a plausible-sounding reconstruction would have been a fabrication.

Representative prompts, translated into English from the original Chinese:

- *"Please update `summarize_results.py` so it includes the reranker results."*
  — Codex; scope: default inputs, the three-method pooled table, its tests, and
  regenerating the main results file.
- *"Check the change I just made to `scripts/reporting/summarize_results.py` — I
  added the reranker results — and fix it."* — Claude Code; scope: independent
  verification of the previous session's change by recomputation, and cleanup
  of the follow-ups it found.
- *"Accept DR-003."* — Codex; scope: independent design review of the
  manual-review protocol, producing a written FAIL verdict with three findings.

The full per-session log is available on request.

## 7. Jiajun Fang's declaration

*[To be completed by Jiajun before submission. To meet the course requirement,
it needs to state: which AI tools he used; which of the five purposes in §2 he
used them for; which specific files and functions received assistance —
including `src/data_loader.py`, `src/retrievers.py`,
`scripts/run_week1_debug.py`, `tests/test_data_loader.py`, and the original
`src/evaluator.py` metric implementations; and, if he used a coding agent, a
session-level record of prompts and scope in the form used in §6.]*
