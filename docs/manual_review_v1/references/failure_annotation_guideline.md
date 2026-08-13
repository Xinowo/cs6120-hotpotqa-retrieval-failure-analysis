---
status: active
last_updated: 2026-08-12
---

# Failure Annotation Guideline

## 0. Status and scope

- **Design record:** DR-003, Manual Failure Review Protocol and Notes-First HTML.
- **Batch:** `manual_review_v1`.
- **Source run:** `results/runs/2026-07-17_a/` (read-only).
- **Reviewers:** Xin and Jiajun.
- **Current stage:** Gate C calibration/open coding; Gate A and Gate B passed in
  the Round 19 acceptance review.
- **Interface:** `results/annotations/manual_review_v1/failure_review.html`.
- **Inputs:** `xin_cases.json` and `jiajun_cases.json`.
- **Outputs:** `xin_notes.csv` and `jiajun_notes.csv`.

This is the operational guide for the frozen v1 review. The canonical method is
`docs/specs/2026-07-27-manual-failure-review-course-protocol.md`. Do not edit,
rename, replace, or regenerate anything under the formal source run.

## 1. Non-negotiable boundaries

### Notes first

Record evidence-bearing observations before choosing a cause. The taxonomy is
derived jointly from completed notes; it is not assumed in advance.

- No tool, agent, or vocabulary may pre-fill a human cause.
- **Human failure label (optional)** starts empty and may remain empty during
  open coding.
- A completed row requires a substantive note, not a label.
- Do not force uncertainty into a category merely to fill the label field.

### Machine structure is not a cause

The read-only **Machine rank pattern (10-class)** says where gold titles ranked,
not why retrieval failed. Never copy `rank_pattern` into the human label or use
it as a causal category.

### One target, one comparison

The **Review target** panel defines the exported unit. The other retriever is
**Read-only comparison** context.

- Diagnose only the target.
- Use the comparison panel as supporting or contradicting evidence.
- Do not create another note for the comparison panel.
- Do not infer a cause from "BM25 missed, Dense hit" (or the reverse) without
  reading the passages.
- BM25 and Dense scores have different scales; do not compare them numerically.

### BM25 implementation context

For BM25 cases from source run `2026-07-17_a`, consult
[`bm25_implementation_reference.md`](bm25_implementation_reference.md).
The reviewed implementation indexes paragraph text but not titles and uses
lowercase whitespace tokenization without punctuation or entity normalization.
Treat these as run-specific implementation facts and revalidate them before
reviewing results from another run.

### Dense implementation context

For Dense cases from source run `2026-07-17_a`, consult
[`dense_implementation_reference.md`](dense_implementation_reference.md).
The reviewed implementation is a symmetric `all-MiniLM-L6-v2` bi-encoder that
embeds paragraph text but not titles, L2-normalizes query and passage vectors,
and ranks independent passages by dot product, equivalent to cosine
similarity. The main Dense experiment has no reranker, threshold, or
cross-passage reasoning. Treat semantic-neighborhood descriptions as observed
ranking behavior, not as direct evidence of token-level attention or internal
feature weights. Revalidate model and environment details for another run.

### Reviewer independence

Xin and Jiajun must not read one another's notes before both independently
complete the four overlap cases. JSON inputs, browser drafts, imports, and
exports remain reviewer-specific.

## 2. Batch and unit

One review unit is:

```text
(run_id, example_id, retriever)
```

The retriever is part of the identity. The same `example_id` under BM25 and
Dense represents two distinct units.

Every v1 unit is a **strict Any@5 failure** for the target: neither gold title
appears in its first five results. `review_cutoff` is fixed at `5`; the old `k`
field is not used. This selection rule is not a causal explanation.

The batch contains 30 unique units:

| Retriever | Bridge | Comparison | Total |
|---|---:|---:|---:|
| BM25 | 12 | 3 | 15 |
| Dense | 12 | 3 | 15 |
| Total | 24 | 6 | 30 |

Four units overlap: one bridge and one comparison per retriever. Each reviewer
sees those four first, followed by 13 private units, for 17 rows total. The two
exports contain 34 review actions but only 30 unique units; overlap cases are
never double-counted in final category totals.

## 3. Start or resume a session

1. Double-click `failure_review.html`; no server or installation is needed.
2. Choose **Open my cases JSON...**.
3. Xin loads `xin_cases.json`; Jiajun loads `jiajun_cases.json`.
4. Confirm `batch_id=manual_review_v1`, your reviewer ID,
   `run_id=2026-07-17_a`, `review_cutoff=5`, and `cases=17`.
5. Review **calibration overlap only** first.
6. To resume from CSV, load the same reviewer JSON and then import that
   reviewer's own notes file.

Drafts are stored in browser local storage under both batch and reviewer ID.
After refresh, reopen the same reviewer JSON to restore them. Local storage is
not an archive: export CSV regularly. If storage is unavailable, the page warns
that drafts remain only in memory until exported.

## 4. Review one card

1. Confirm the target retriever, question type, `example_id`, and overlap/private
   badge.
2. Read the question and identify its required bridge, relation, or comparison.
3. Read both complete gold passages; do not diagnose from titles alone.
4. Inspect each gold rank for both methods. A rank 6--50 is below cutoff but
   retrieved. `not in top 50` means absent only from the stored top 50, not from
   the corpus.
5. Check both machine rank patterns as structural summaries only.
6. Inspect enough target top-50 passage text to identify what was retrieved
   instead of the gold evidence.
7. Inspect the comparison panel for evidence that supports or weakens the
   explanation.
8. Write observations first, then a possible reason and uncertainty.
9. Optionally add a human label; leave it blank if no category is defensible.

For bridge questions, inspect whether results expose or miss the linking entity
or relation. For comparison questions, inspect whether results over-focus on
one side, confuse the compared entities, or retrieve related but non-supporting
material. A relevant non-gold passage remains non-gold under the evaluation
contract.

## 5. Evidence-based note rubric

A useful note lets the other owner reconstruct the reasoning. It normally says:

1. the target and both observed gold ranks;
2. which gold evidence is below cutoff or absent from the stored top 50;
3. what the target retrieved instead, using concrete titles or passage content;
4. relevant behavior of the comparison retriever;
5. an evidence-grounded possible reason; and
6. an alternative or explicit uncertainty when needed.

Use the page prompt:

```text
Observed:
Missing gold:
Retrieved evidence or distractor:
Possible reason:
Alternative or uncertainty:
```

Example structure:

```text
Observed: Target BM25 has Gold A at rank [R] and Gold B at [R / not in top 50];
neither is inside the top 5.
Missing gold: [state the exact below-cutoff or stored-list status].
Retrieved evidence or distractor: Top results focus on [specific evidence],
while the gold passages require [specific relation]. Dense [relevant contrast].
Possible reason: [hypothesis supported by the visible evidence].
Alternative or uncertainty: [competing interpretation or limitation].
```

Do not merely repeat the Any@5 status or machine pattern, compare score
magnitudes, diagnose the comparison retriever, claim `not in top 50` means
absent from the corpus, or substitute a label for the note. There is no required
candidate-label list during open coding. Any provisional label is human-authored
and revisable.

## 6. Overlap-first calibration

1. Both reviewers independently complete all four overlap notes.
2. Neither reads the other's first-pass notes.
3. Each exports a CSV checkpoint so the originals are preserved.
4. Compare the four note pairs together.
5. Discuss factual mistakes, omitted evidence, unsupported causes, different
   uses of the comparison panel, unclear instructions, and uncertainty.
6. Calibrate the note rubric while preserving both original versions.
7. Only then does each reviewer complete the 13 private cases.

Overlap checks note quality and interpretation. It is not majority vote, an
agreement statistic, or a requirement to use identical prose.

## 7. Save, import, and export

The page exports one UTF-8 CSV per reviewer, `xin_notes.csv` or
`jiajun_notes.csv`, with:

```text
batch_id,run_id,example_id,retriever,review_cutoff,label,notes,annotator,annotated_at
```

- Every export has exactly 17 rows, including incomplete rows.
- `annotator` comes from the loaded reviewer file; `annotated_at` is generated.
- `label` may remain empty; all 17 `notes` must be non-empty for completion.
- An export never includes the other reviewer's cases or notes.
- Import replaces the active reviewer's notes and labels after confirmation.
- Wrong batch, annotator, unit set, cutoff, or row count is rejected.

Export after the overlap pass, after each private-case session, and at the end.
Keep the previous verified checkpoint until the new one has been checked.

## 8. From notes to `taxonomy_v1`

After all 30 unique units have notes, Xin and Jiajun jointly write
`taxonomy_v1`: category definitions, evidence requirements, inclusion/exclusion
rules, examples, and ambiguity handling.

The taxonomy must also answer the project's capability-boundary question. Each
category in the candidate and frozen taxonomy records:

```text
failure_layer
retriever_scope
BM25_capability_boundary
Dense_capability_boundary
supporting_units
decisive_counterfactual
claim_strength
non_claims
```

`failure_layer` is one of `implementation`, `method`, `corpus`, or
`evaluation`. A retriever scope records where the bounded 30-unit sample
supports the category; it is not itself a cause. Capability boundaries use the
scoped contract in `manual_review_v1/analysis/taxonomy_todo.md` D-062: a tested
implementation repair cannot be promoted to a method limitation, a missing
counterfactual caps the claim at `observed`, and a method-level conclusion must
name the evaluated method or architecture and retrieval setup. Unqualified
universal claims such as “Dense cannot resolve bridge entities” are forbidden.

The final qualitative analysis includes one category-by-retriever matrix with
BM25 and Dense supporting units, failure layer, both capability boundaries,
decisive evidence or counterfactual, claim strength, and scope caveat. It must
allow the legal conclusion “implementation-induced; not beyond BM25” rather
than forcing every recurring pattern to become a method limitation.

Reviewer labels and final analytical labels remain separate:

- retain both notes for each overlap unit;
- treat `case_memos_v2.csv.primary_open_code` and its legacy
  `candidate_category` routing as provisional inputs, not candidate or final
  labels;
- create candidate mappings only in a versioned `candidate_mapping_v0_N.csv`,
  initially with empty categories and `mapping_status=not_tested`;
- assign one final label to each of 30 unique units;
- resolve overlap differences jointly;
- use `unresolved` rather than force an unsupported decision; and
- never count overlap twice.

The final file is
`results/annotations/manual_review_v1/final_labels.csv`:

```text
run_id,example_id,retriever,final_label,resolution
```

`resolution` is `single_review`, `overlap_agreed`, `overlap_resolved`, or
`unresolved`. Category counts come only from these 30 rows and must sum to 30,
including `unresolved`. Report them as calibration/open-coding counts, not
prevalence estimates.

## 9. Checklists

### Before review

- [ ] My JSON identity, run, cutoff, and 17-case count are correct.
- [ ] I have not read the other reviewer's overlap notes.
- [ ] I am doing the four overlap cases before private cases.

### Per card

- [ ] I confirmed the target and unit identity.
- [ ] I read the question and both complete gold passages.
- [ ] I checked target and comparison ranks and passages.
- [ ] I distinguished below-cutoff from `not in top 50`.
- [ ] I treated machine patterns as structure, not causes.
- [ ] My note contains evidence, a possible reason, and uncertainty as needed.
- [ ] I left the optional label blank when no category is defensible.

### Session and Gate C

- [ ] I exported and retained a verified 17-row checkpoint.
- [ ] Both original overlap-note versions were preserved.
- [ ] Both reviewer CSVs ultimately contain 17 non-empty notes.
- [ ] `taxonomy_v1` is jointly approved.
- [ ] `final_labels.csv` has 30 unique units and counts sum to 30.

## References

- `docs/specs/2026-07-27-manual-failure-review-course-protocol.md`
- `docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md`
- `docs/specs/2026-07-12-failure-review-pipeline-design.md`
- `scripts/manual_review_page.py`
- `.claude/design_records/reviews/2026-07-29_DR-003_course-scope-owner-acceptance_round19_independent_review.md`
