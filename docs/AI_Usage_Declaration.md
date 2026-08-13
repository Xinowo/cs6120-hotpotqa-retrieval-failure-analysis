---
status: draft
last_updated: 2026-08-13
---

# AI Usage Declaration

CS6120 Final Project — HotpotQA Retrieval Failure Analysis
Xin Wang, Jiajun Fang

## Tools

Claude Code and OpenAI Codex, used as coding agents inside the project repository.
Xin's sessions were logged as they happened in `docs/Completion_Log/`, each with its
date, tool, the prompt used, and the files it changed.

[Jiajun to confirm the tools he used and where his sessions are recorded, before
submission.]

## What we wrote ourselves

**Project design.** The research questions, scope, experimental design, corpus
settings, the choice of metrics and cutoffs, and the manual review protocol.

**Evaluation metric logic.** `src/evaluator.py` — Any / Full / Partial Evidence
Recall@k and the reciprocal rank behind MRR@10 and MRR@50 — is hand-written by us
(Jiajun in `ad21da0` and `fee74ac`, Xin's `gold_ranks` addition in `25ed1b7`), as is
`tests/test_evaluator.py`. No agent produced a metric definition.

**Part of the test suite,** including the metric tests above and the hand-checks used
to confirm reported numbers against the saved result artifacts.

**The entire failure analysis.** All reviewer notes on the 30 reviewed retrieval
failures, the open coding over those notes, the category definitions and their
evidence rules, the 30 final labels, and the findings and limitations written from
them. No agent wrote a note, proposed a category, or assigned a label.

**The report and the slides.** AI was used only for proofreading and wording, never
for research content.

## What the coding agents produced

Supporting infrastructure only, within the categories the course policy permits:

- data loading (`src/data_loader.py`);
- plumbing around off-the-shelf models: the BM25 wrapper, the `all-MiniLM-L6-v2`
  bi-encoder, the cross-encoder reranker, and the embedding cache;
- experiment runners, their CLIs, configuration and logging;
- result serialization, the reporting scripts, and the HTML/SVG figures;
- most of the test suite;
- `README.md`, `requirements.txt`, and repository documentation and tooling.

Everything an agent generated was reviewed and, where needed, changed by hand. Both
of us can explain any of it without reference to how it was first written.

## The boundary that mattered most

Machine-computed rank structure and human causal explanation are kept apart by
construction, not by convention. The review protocol
(`docs/specs/2026-07-27-manual-failure-review-course-protocol.md`) states that "no
system or agent pre-fills a causal label", and a committed test
(`tests/test_reporting_doc_references.py`) asserts that sentence is still there. The
machine side (`src/rank_pattern.py`) only computes where the gold passages ranked;
the categories in `docs/taxonomy_candidate_v0_1.md` and the labels in
`results/annotations/manual_review_v1/final_labels.csv` are our judgements over our
own review notes.
