---
last_updated: 2026-08-13
---

# Manual review v1 -- the imported analysis record

The manual failure review was carried out in a separate local analysis workspace,
because it needed a large append-only decision log and 19 long per-unit dossiers that
would have swamped this repository while the work was in progress. **That record is
now here.** Nothing in this repository's documents depends on reading anything
outside it.

Imported on 2026-08-13, as verbatim byte copies, from the analysis workspace at its
commit `4f44b46`. Two files were taken from that commit rather than from the
workspace's working tree, because the working tree carried uncommitted work belonging
to a later decision entry that this batch does not consume; those two are marked
below. Digests are SHA-256 of the bytes as imported.

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

## The record

| File | Bytes | Source | SHA-256 (first 16) |
|---|---:|---|---|
| `open_code_decision_log.md` | 814,967 | workspace HEAD | `c64c323b31adebbd` |
| `taxonomy_todo.md` | 410,661 | workspace HEAD | `2782685d5a0fc3a6` |
| `open_code_vocabulary_audit.md` | 246,422 | clean working tree | `e09e940655cf5eae` |
| `secondary_descriptor_registry.md` | 208,573 | clean working tree | `1253b1fcf6d32b29` |
| `candidate_taxonomy_v0_1.md` | 130,937 | clean working tree | `aa200997f83487f7` |
| `vocabulary_audit_triage.md` | 34,502 | clean working tree | `ca61e51538228f94` |
| `express_closeout_v0_1.md` | 8,320 | clean working tree | `e169219847e6979c` |
| `single_note_validation_queue.md` | 8,073 | clean working tree | `29268061e18c31ae` |
| `source_manifest.json` | 873 | clean working tree | `d91cc2e7331641ea` |
| `references/pooled_corpus_validation_500_title_text.jsonl` | 2,971,310 | clean working tree | `c5632c63910b776e` |
| `references/reusable_retrieval_failure_review_playbook.md` | 159,971 | clean working tree | `65dd0597896f46db` |
| `references/2026-08-05-parallel-failure-taxonomy-review-pipeline-design.md` | 68,852 | clean working tree | `8d5e1bb8a3d13252` |
| `references/bm25_implementation_reference.md` | 14,029 | clean working tree | `67a552e61f4d5e4e` |
| `references/2026-07-31_notes_first_grounded_taxonomy_workflow.md` | 13,158 | clean working tree | `8d00038d3dcacfc8` |
| `references/failure_annotation_guideline.md` | 12,944 | clean working tree | `6a74de3579a31989` |
| `references/dense_implementation_reference.md` | 11,473 | clean working tree | `b1ba655f77ea9311` |

Original filenames are kept, dates and all, because the imported record cites them
that way.

The analysis tooling, imported because the record cites it as authoritative -- most
importantly `tools/recount.py`, whose ordinal-series membership tables settle counts
that the prose defers to. These expect the analysis workspace's own layout and are
preserved for provenance, not as an entry point; this repository's own reproducible
entry point for the labels and counts is
`../../scripts/reporting/manual_review_category_counts.py`.

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `tools/README.md` | 191,701 | `3e7cf678f807a5b8` |
| `tools/recount.py` | 116,533 | `346680c952ffb4d3` |
| `tools/landing_kit.py` | 110,166 | `9898e2f33a4bb80d` |
| `tools/probe_kit.py` | 103,009 | `99f9e55ee7a1bdc9` |
| `tools/case_probe.py` | 46,370 | `380064624de209cf` |
| `tools/repro_template.py` | 30,241 | `81a745ab66dca551` |
| `tools/check_landing.py` | 25,890 | `b0873f1a671c958a` |
| `tools/landing_template.py` | 25,593 | `218eef2474019a91` |
| `tools/precedents.py` | 18,775 | `bf2c6e81ea6380ad` |
| `tools/make_repro.py` | 17,050 | `3553e50086aa0bd0` |
| `tools/units.py` | 17,065 | `97ffe6b56e499626` |
| `tools/cross_check.py` | 15,697 | `313cafca25636036` |
| `tools/make_tables.py` | 9,973 | `02dfdee501ffe6e9` |
| `tools/text_cache.py` | 8,347 | `33ed4194e91721ca` |
| `tools/case_results.py` | 8,072 | `e3e7a48fdc019e81` |
| `tools/dense_cache.py` | 7,036 | `c25d5eaacf5d3dfb` |
| `tools/express_closeout.py` | 13,736 | `337441660b215ac7` |

The 30-unit evidence table went to the annotation data directory rather than here,
because it is data and not prose:

| File | Bytes | SHA-256 (first 16) |
|---|---:|---|
| `../../results/annotations/manual_review_v1/case_memos_v2.csv` | 622,063 | `46cf59e1ec15c810` |

### The 19 per-unit dossiers, plus their index

`per_case_analysis/README.md` is the index, 35,879 bytes, `dfb11ada4c331480`.

| Dossier | Bytes | SHA-256 (first 12) |
|---|---:|---|
| `bm25_bridge_5a79b7f6554299029c4b5f6f.md` | 85,176 | `745abc68f1f1` |
| `bm25_bridge_5a83880e554299123d8c214e.md` | 102,998 | `bc108bc16e49` |
| `bm25_bridge_5abcc96c5542996583600492.md` | 87,550 | `3666b1a9b74d` |
| `bm25_bridge_5ac1a3665542994ab5c67daf.md` | 52,909 | `38e4a0e1d7dc` |
| `bm25_bridge_5adc8977554299438c868de2.md` | 78,775 | `83a401da0166` |
| `bm25_bridge_5ade42b55542992fa25da717.md` | 73,115 | `f48242f52b36` |
| `bm25_bridge_5adf58f15542993a75d264d2.md` | 94,972 | `c1e1ef087d87` |
| `bm25_bridge_5ae057fd55429945ae959328.md` | 84,425 | `302f2c437bbd` |
| `bm25_bridge_5ae60426554299546bf83019.md` | 146,274 | `1d889fbfc605` |
| `bm25_comparison_5ab8f57b5542991b5579f097.md` | 109,805 | `4d70281f9bdd` |
| `dense_bridge_5a81ebee554299676cceb16d.md` | 95,008 | `b369430a9c63` |
| `dense_bridge_5ab48c325542996a3a969f93.md` | 74,052 | `61299c323ff6` |
| `dense_bridge_5add67915542992200553af8.md` | 92,226 | `27158f594f0d` |
| `dense_bridge_5ade69e455429975fa854ec5.md` | 64,220 | `fb15ffcf62f5` |
| `dense_bridge_5ae048a255429924de1b708e.md` | 118,156 | `84dda76f0eae` |
| `dense_bridge_5ae0a59a55429945ae9593e2.md` | 82,083 | `1f2181d180e0` |
| `dense_bridge_5ae1801955429901ffe4aec4.md` | 155,569 | `5a755dc77e5d` |
| `dense_bridge_5ae1f596554299234fd04372.md` | 75,012 | `70ea96fc485d` |
| `dense_comparison_5a78b209554299148911f93e.md` | 93,853 | `ae5ce10bc730` |

**11 of the 30 units have no dossier.** That is a stated limitation of the analysis,
not an import omission: those units were never given a factorial design, and every
predicate on them is satisfied by an enumerated content property rather than by a
measured rank effect.

## How paths inside the imported record read

The record was written in the analysis workspace and cites its own paths, which this
import remaps. Nothing needs to be edited inside those files for the citations to
resolve -- editing an append-only log to fix a path would damage the thing that makes
it evidence -- so the mapping is stated here instead:

| Cited as | Read as |
|---|---|
| `manual_review_v1/analysis/<name>.md` | `docs/manual_review_v1/<name>.md` |
| `manual_review_v1/analysis/case_memos_v2.csv` | `../../results/annotations/manual_review_v1/case_memos_v2.csv` |
| `manual_review_v1/analysis/per_case_analysis/`, `manual_review_v1/analysis/tools/` | the same directory names under `docs/manual_review_v1/` |
| `references/<name>` | `docs/manual_review_v1/references/<name>`, which is where a citation relative to a record's own directory already lands |
| `references/2026-07-27-manual-failure-review-course-protocol.md` | `../specs/2026-07-27-manual-failure-review-course-protocol.md`. The workspace kept a copy of this repository's own tracked specification; the tracked one is authoritative and no second copy was imported |
| `manual_review_v1/<reviewer>_cases.json`, `<reviewer>_notes.csv` | `../../results/annotations/manual_review_v1/`, where they exist locally but are excluded from Git by the root `.gitignore` |
| `derived/case_results/`, `derived/dense_embeddings/`, `derived/dense_text_vectors/` | not imported; see below |
| `failure_review/tmp/...`, and absolute paths beginning with a drive letter | scratch directories of the analysis session. They were never deliverables and no conclusion depends on them |

## What was deliberately not imported

- **The derived caches**, about 34 MB across per-case result dumps, dense embeddings
  and text vectors. They are regenerable intermediates, and this repository already
  excludes its own equivalent (`results/runs/`) from Git for the same reason. Nothing
  in the record's conclusions rests on them being present: every dossier quotes the
  ranks and scores it argues from inline.
- **The superseded first-pass memo table.** `case_memos_v1.csv` is entirely replaced
  by v2.
- **The candidate mapping scaffold.** It belongs to the full process, which has not
  been run; it is an empty form, not evidence.
- **The express track's own TODO.** It is a checklist for the compressed path, not
  evidence; the authored account of that path, `express_closeout_v0_1.md`, was
  imported, and so was its generator, `tools/express_closeout.py`. That generator
  reads the workspace's own layout and is here for provenance rather than as
  something to run: the two files it produced are shipped at their protocol paths,
  and `../../scripts/reporting/manual_review_category_counts.py` re-derives the
  counts from `final_labels.csv` inside this repository.
- **A second copy of this repository's own course protocol.** The workspace kept one
  under `references/`; the tracked `../specs/` copy is authoritative.

## Byte notes

- The imported Markdown is untouched, including its original line endings. It is
  hand-authored prose and carries no digest-based identity contract in this
  repository, so it is left exactly as the analysis produced it.
- `case_memos_v2.csv` begins with a UTF-8 BOM, which is how it was written by the
  workbook that produced it. A reader parsing it should either strip the BOM or open
  it with `utf-8-sig`. It sits under `results/annotations/`, which the root
  `.gitattributes` exempts from end-of-line conversion, so its bytes are stable
  through commit and checkout.
- `source_manifest.json` records the SHA-256 of the read-only reviewer sources the
  analysis was bound to. It is the integrity record for inputs, not for the files
  listed above.
