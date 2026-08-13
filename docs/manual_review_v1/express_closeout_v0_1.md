---
status: active
last_updated: 2026-08-13
---

# Express closeout v0.1 — final labels for the report

**This is a deliberately compressed, parallel closeout, produced under owner time
constraint on 2026-08-13 so the course report can be written.** It does **not**
replace Sections 15 to 26 of `taxonomy_todo.md`, does not tick a single checkbox
there, and does not freeze the taxonomy. The full process stays exactly as
specified and unstarted; the owner intends to run it after the report is
submitted. Where this document and the full process later disagree, the full
process wins and this document is superseded.

## 1. What this produces

| Artifact | Rows | Purpose |
|---|---:|---|
| `express_final_labels_v0_1.csv` | 30 | The Section 8 protocol content the report's counts must come from |
| `express_category_counts_v0_1.csv` | 7 + TOTAL | Calibration counts for the report, with the backend split |

Both are generated, and can be regenerated or verified, by
`tools/express_closeout.py`. `--check` re-derives everything and compares it with the
bytes on disk without writing, so the numbers quoted in the report can be confirmed
against the repository at any time rather than trusted.

`express_final_labels_v0_1.csv` carries the protocol's exact five columns,
`run_id,example_id,retriever,final_label,resolution`. **The names are deliberately
not the canonical ones.** Section 22 of `taxonomy_todo.md` creates `final_labels.csv`
and Section 24 creates `category_counts.csv` - the latter with a different column set,
`taxonomy_version, category, count, denominator, sample_scope` - so the express files
are namespaced to keep the full track's two filenames free and to make the two label
sets diffable rather than one silently overwriting the other. When the report is
submitted, the protocol's canonical path is
`results/annotations/manual_review_v1/final_labels.csv` in the main analysis
repository.

## 2. How the labels were derived — transcription, not new analysis

No retrieval measurement, ranking, score computation, corpus sweep, ablation or
oracle injection was run. No unit was re-analysed and no raw note was re-read for
a new judgement. Every label is transcribed from what is already landed:

1. **D-063 Track D** reapplied the candidate primary-selection order to all 30 full
   unit keys and landed the result: K1 10, K2 4, K3 6, K4 5, K5 1, K6 2 and
   `unresolved` 2, summing to 30, disjoint and exhaustive, splitting 15 BM25 and 15
   Dense.
2. The **per-unit** assignment was read out of `candidate_taxonomy_v0_1.md`'s six
   category blocks — each block's `supporting_units` list plus its
   **Primary-label units** line. K5 is the one category whose two sets differ, 7
   supporting against 1 primary-label, and its primary-label line names the single
   unit explicitly.
3. The two `unresolved` units are the two D-063 Track D names per unit, each with
   its own failing predicate recorded there.

The derivation was checked mechanically rather than asserted:

- the 30 derived keys are **exactly** the 30 keys of `case_memos_v2.csv` — no
  missing key, no foreign key, no duplicate;
- the seven derived counts match D-063 Track D **item for item**;
- the backend split is 15 BM25 / 15 Dense, and each category's own split matches
  the Section 7 capability matrix cell for cell — K1 10/0, K2 0/4, K3 3/3, K4 1/4,
  K5 0/1, K6 1/1, `unresolved` 0/2;
- named labels 28 + `unresolved` 2 = **30**, which is the protocol's arithmetic
  condition on this file.

## 3. The counts, in the form the report must use

| `final_label` | Count | BM25 | Dense |
|---|---:|---:|---:|
| `bm25_minimal_preprocessing_score_distortion` | 10 | 10 | 0 |
| `description_only_bridge_entity` | 4 | 0 | 4 |
| `cross_passage_conjunction_unresolved` | 6 | 3 | 3 |
| `near_neighbour_crowding_and_sense_drift` | 5 | 1 | 4 |
| `dense_peripheral_passage_content_dilution` | 1 | 0 | 1 |
| `evaluation_side_gold_chain_ambiguity` | 2 | 1 | 1 |
| `unresolved` | 2 | 0 | 2 |
| **TOTAL** | **30** | **15** | **15** |

**The denominator is always 30.** The protocol requires these to be called
**calibration / open-coding counts, never prevalence estimates**. Reviewer row
counts — 34 review actions by two reviewers over 30 unique units — may be reported
separately as workload or overlap evidence, but never as category prevalence.

Two further framing rules the report must not break, both from D-062: no
unqualified `BM25 cannot ...` or `Dense cannot ...` claim anywhere, and
comparison-retriever success alone never strengthens a claim. Only K1 reaches
`implementation_supported` and only K5 reaches `setup_scoped_method_supported`;
three of the six categories carry `not_established` on both backends, which records
missing evidence and not inapplicability.

## 4. The `resolution` column, including one judgement call

26 units carry `overlap_status=single_note` and 4 carry `overlap`, matching the
34-review-action / 30-unique-unit structure.

| `resolution` | Rows | Ground |
|---|---:|---|
| `single_review` | 25 | one reviewer, and a named category was reached |
| `overlap_resolved` | 3 | two reviewers, and an owner decision selected among competing readings — D-010, D-011, D-012 |
| `unresolved` | 2 | no category's include rules are reached, per D-063 Track D |

**The judgement call, stated so it can be overridden in one cell each.** All four
overlap units have an owner decision that *chose* between competing readings
(D-009 to D-012), so none was recorded as `overlap_agreed`. If the owner considers
any of them a plain agreement rather than a resolution, that row's `resolution`
becomes `overlap_agreed` and nothing else changes.

`5a76387d554299109176e6ba|dense` is both an overlap unit (D-009) and a category
`unresolved` unit, so it appears once, under `unresolved`. That follows the
protocol's own rule that the outcome is "one resolved category or one `unresolved`
unit, never two votes", which is why `overlap_resolved` reads 3 and not 4.

## 5. What this closeout does **not** do — cite these as report limitations

- **The taxonomy is not frozen.** `candidate_taxonomy_v0_1.md` is still `draft` and
  `taxonomy_v1.md` does not exist. These labels therefore come from a **candidate**
  taxonomy, and every category name in them is a candidate name.
- **No independent per-unit mapping pass was run.** Sections 16, 19 and 22 each
  specify a full pass over all 30 units, three passes in total. None was run. The
  labels are a transcription of D-063 Track D's single landed application of the
  selection order, not an independent re-derivation of it.
- **No boundary stress-test.** Sections 17 and 18 were not run, so no category
  boundary was stressed, revised or confirmed by a second pass.
- **No triage item is closed by this closeout, and it changes no `$STAGE`.** Whatever
  value `$STAGE` holds is set by the full track, not here.
- **This closeout appends no decision entry of its own** and rules nothing. It
  consumes D-062, D-063, D-064 and D-065 and adds no authority to them, so the
  owner's later full run of Sections 15 to 26 is not constrained by it. Any decision
  entry later than D-065 belongs to that full run, not to this closeout, and where
  such an entry and this document disagree, the entry wins.
- The **known limitations of the taxonomy itself** are unchanged and are listed in
  `candidate_taxonomy_v0_1.md` section 19 — 11 of the 30 units carry no dossier and
  no factorial, K4 is the weakest-controlled category, and twelve triage items stay
  open.

## 6. Provenance for the report

Every number above traces to landed text. The categories, their definitions,
boundaries, positive examples, counterexamples and the capability matrix are in
`candidate_taxonomy_v0_1.md` sections 6 and 7, landed as **D-065** (commit
`cb0e476`) after three independent acceptance reviews of the document and two of
the landing. The 30-unit assignment is **D-063** Track D. The capability-boundary
contract is **D-062**. The minimum-evidence correction is **D-064**. The two
`unresolved` units' failing predicates are recorded per unit in D-063 Track D and
restated in `candidate_taxonomy_v0_1.md` section 18.
