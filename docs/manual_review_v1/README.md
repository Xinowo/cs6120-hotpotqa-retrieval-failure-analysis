---
last_updated: 2026-08-13
---

# Manual review v1 -- the imported analysis record

The manual failure review was carried out in a separate local workspace, because it
needed a long append-only decision log and 19 long per-unit dossiers that would have
been in the way while the work was in progress. **That record is now here**, except for
the author's own working documents, which stay on their machine and are listed under
"What is held locally" below. Every conclusion this repository states is argued in the
documents that are here.

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
| What was measured on a unit, condition by condition? | `per_case_analysis/`, for the 19 units that have a dossier -- held locally, not in Git |
| What is still open? | `vocabulary_audit_triage.md`, items `T-nn` |
| How was the review run, and who decided what? | `../manual_review_v1_open_coding_memo.md` |
| What do the 30 labels mean, read as findings? | `../manual_review_v1_failure_analysis.md` |
| What does the full, unrun process specify? | `taxonomy_todo.md` -- held locally, not in Git |

## What is here

**The analysis record.** `open_code_decision_log.md` is the append-only log of every
decision, and the authority for anything cited as `D-0nn`.
`candidate_taxonomy_v0_1.md` is the full category document.
`open_code_vocabulary_audit.md` and `vocabulary_audit_triage.md` are the vocabulary
audit and its open-item table, the authority for anything cited as `T-nn`.
`secondary_descriptor_registry.md` holds the secondary descriptors the decisions
assign. `single_note_validation_queue.md` and `taxonomy_todo.md` are the process
record, the latter being the full 26-section process that this compressed path did
not run and being held locally rather than in Git.
`express_closeout_v0_1.md` is the authored account of the compressed path
itself. `source_manifest.json` records which reviewer files the analysis was bound
to.

**`per_case_analysis/`** holds the 19 per-unit dossiers and an index README, and is
**held locally, not in Git**. **11 of the 30 units have no dossier** -- that is a
stated limitation of the analysis, not an import omission: those units were never
given a factorial design, and every predicate on them rests on an enumerated content
property rather than a measured rank effect.

**`references/`** holds the documents the evidence rules cite: the BM25 and Dense
implementation references, the reviewer annotation guideline, the notes-first workflow
spec, the pooled-corpus validation dump the content rules were checked against, and
the reusable review playbook. The parallel-pipeline design note is also part of this
directory but is held locally, not in Git.

**`tools/`** holds the analysis tooling, kept because the record cites it -- most
importantly `recount.py`, whose membership tables settle counts the prose defers to.
It is **held locally, not in Git**: it runs only against the working record and the
workspace's own layout, since `check_landing.py` and `make_tables.py` are written
against those documents and `units.py` imports `recount.py`, so the directory is one
coupled unit rather than something that can be kept piecemeal. It was always
provenance rather than an entry point. This repository's own entry point for the
labels and counts is
`../../scripts/reporting/manual_review_category_counts.py`, which re-derives the
counts from `final_labels.csv`, can verify them with `--check`, and needs none of the
local-only tooling.

## What is held locally

Four parts of the imported record are the author's own working material rather than
part of the published record. They are excluded from Git by the root `.gitignore` and
stay on the author's machine:

| Held locally | What it is |
|---|---|
| `per_case_analysis/` | the 19 per-unit dossiers and their index |
| `taxonomy_todo.md` | the full 26-section process specification |
| `tools/` | the analysis tooling |
| `references/2026-08-05-parallel-failure-taxonomy-review-pipeline-design.md` | the parallel-pipeline design note |

They were excluded whole rather than edited down, and that is deliberate.
`open_code_decision_log.md` is append-only, and the argument that forbids editing it to
fix a path forbids just as strongly reworking the material it was argued against. A
rewritten dossier would be a new document asserting the same thing, not the record the
decisions were actually made against.

**What this costs, stated plainly.** The documents here cite these four by name
**146 times**, and those citations are left exactly as written. A reference to
`taxonomy_todo.md`, to a `per_case_analysis/` dossier or to `tools/recount.py`
therefore names a document that is real and unchanged but not in this repository. What
each citation is offered as evidence *for* is restated where it is used; what is not
available here is the ability to open the underlying record. It can be supplied on
request.

**What this does not cost.** No figure this repository reports depends on the
local-only set. The labels and counts re-derive from
`../../results/annotations/manual_review_v1/final_labels.csv` through
`../../scripts/reporting/manual_review_category_counts.py --check`, and every dossier
result the analysis leans on is quoted inline at the point of use.

## How paths inside the record read

The record cites the workspace's own paths, which this import remaps. Nothing needs
editing inside those files for a citation to resolve -- editing an append-only log to
fix a path would damage the thing that makes it evidence -- so the mapping is here
instead.

| Cited as | Read as |
|---|---|
| `manual_review_v1/analysis/<name>` | `docs/manual_review_v1/<name>`, including the `per_case_analysis/` and `tools/` subdirectories, which resolve to that path locally but are not in Git |
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
