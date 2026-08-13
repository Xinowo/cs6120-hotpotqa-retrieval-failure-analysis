---
last_updated: 2026-08-13
---

# Manual review v1 -- the imported analysis record

The manual failure review was carried out in a separate local workspace, because it
needed a long append-only decision log and 19 long per-unit dossiers that would have
been in the way while the work was in progress. **That record is now here.** Nothing
in this repository's documents depends on reading anything outside it.

Imported on 2026-08-13 from that workspace. The decision log and the full-process
TODO were taken from its last commit rather than its working tree, so that a later
decision entry still being drafted there is not half-included here.

## What to open, for what

| Question | File |
|---|---|
| What are the six categories, and what does each require as evidence? | `../taxonomy_candidate_v0_1.md` -- the compressed, reader-facing version |
| The same, in full, with every figure and every boundary argument | `candidate_taxonomy_v0_1.md` |
| Why is this unit labelled that way? | `open_code_decision_log.md`, entry `D-0nn` |
| What did the reviewers actually write about a unit? | `../../results/annotations/manual_review_v1/case_memos_v2.csv` |
| What was measured on a unit, condition by condition? | `per_case_analysis/`, for the 19 units that have a dossier |
| What is still open? | `vocabulary_audit_triage.md`, items `T-nn` |
| How was the review run, and who decided what? | `../manual_review_v1_open_coding_memo.md` |
| What do the 30 labels mean, read as findings? | `../manual_review_v1_failure_analysis.md` |
| What does the full, unrun process specify? | `taxonomy_todo.md` |

## What is here

**The analysis record.** `open_code_decision_log.md` is the append-only log of every
decision, and the authority for anything cited as `D-0nn`.
`candidate_taxonomy_v0_1.md` is the full category document.
`open_code_vocabulary_audit.md` and `vocabulary_audit_triage.md` are the vocabulary
audit and its open-item table, the authority for anything cited as `T-nn`.
`secondary_descriptor_registry.md` holds the secondary descriptors the decisions
assign. `single_note_validation_queue.md` and `taxonomy_todo.md` are the process
record, the latter being the full 26-section process that this compressed path did
not run. `express_closeout_v0_1.md` is the authored account of the compressed path
itself. `source_manifest.json` records which reviewer files the analysis was bound
to.

**`per_case_analysis/`** holds the 19 per-unit dossiers and an index README. **11 of
the 30 units have no dossier** -- that is a stated limitation of the analysis, not an
import omission: those units were never given a factorial design, and every predicate
on them rests on an enumerated content property rather than a measured rank effect.

**`references/`** holds the documents the evidence rules cite: the BM25 and Dense
implementation references, the reviewer annotation guideline, the notes-first workflow
spec, the pooled-corpus validation dump the content rules were checked against, the
reusable review playbook and the parallel-pipeline design.

**`tools/`** holds the analysis tooling, imported because the record cites it -- most
importantly `recount.py`, whose membership tables settle counts the prose defers to.
These expect the workspace's own layout and are here for provenance, not as an entry
point. This repository's own entry point for the labels and counts is
`../../scripts/reporting/manual_review_category_counts.py`, which re-derives the
counts from `final_labels.csv` and can verify them with `--check`.

## How paths inside the record read

The record cites the workspace's own paths, which this import remaps. Nothing needs
editing inside those files for a citation to resolve -- editing an append-only log to
fix a path would damage the thing that makes it evidence -- so the mapping is here
instead.

| Cited as | Read as |
|---|---|
| `manual_review_v1/analysis/<name>` | `docs/manual_review_v1/<name>`, including the `per_case_analysis/` and `tools/` subdirectories |
| `manual_review_v1/analysis/case_memos_v2.csv` | `../../results/annotations/manual_review_v1/case_memos_v2.csv` |
| `references/<name>` | `docs/manual_review_v1/references/<name>`, where a citation relative to a record's own directory already lands |
| `references/2026-07-27-manual-failure-review-course-protocol.md` | `../specs/2026-07-27-manual-failure-review-course-protocol.md`. The workspace kept a copy of this repository's own tracked specification; the tracked one is authoritative and no second copy was imported |
| `manual_review_v1/<reviewer>_cases.json`, `<reviewer>_notes.csv` | `../../results/annotations/manual_review_v1/`, where they exist locally but are excluded from Git by the root `.gitignore` |
| `derived/case_results/`, `derived/dense_embeddings/`, `derived/dense_text_vectors/` | not imported; see below |
| `failure_review/tmp/...`, and absolute paths beginning with a drive letter | scratch directories of the analysis session. They were never deliverables and no conclusion depends on them |

## What was deliberately not imported

- **The derived caches**, about 34 MB of per-case result dumps, dense embeddings and
  text vectors. They are regenerable intermediates, and this repository already
  excludes its own equivalent (`results/runs/`) from Git for the same reason. No
  conclusion needs them: every dossier quotes the ranks and scores it argues from
  inline.
- **The superseded first-pass memo table**, `case_memos_v1.csv`, entirely replaced by
  v2.
- **The candidate mapping scaffold.** It belongs to the full process, which has not
  been run; it is an empty form, not evidence.
- **The express track's own TODO**, a checklist for the compressed path rather than
  evidence. Its authored account and its generator were imported.

## One practical note

`case_memos_v2.csv` begins with a UTF-8 BOM, which is how the workbook that produced
it wrote the file. Open it with `utf-8-sig`, or the first column will come back named
with the BOM stuck to the front of `batch_id` and every lookup on that column will
miss.
