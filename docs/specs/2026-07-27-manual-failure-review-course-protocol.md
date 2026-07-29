---
status: draft
last_updated: 2026-07-28
---

# Manual Failure Review Protocol: Course-Project Edition

**Design record:** DR-003
**Owners:** Xin and Jiajun
**Purpose:** provide the smallest reliable workflow needed to inspect an
initial calibration/open-coding sample of retrieval failures, write independent
notes, compare a small overlap set, and derive a human-authored failure taxonomy
**Decision status:** Xin and Jiajun jointly approved this course-project
workflow offline on 2026-07-28. That approval also authorizes the narrowly
scoped corrective clarifications recorded in Section 12.2. Gate A still requires
a fresh independent review of the final corrected text and the course AI-usage
record; see Section 11.1

This document replaces the earlier infrastructure-heavy DR-003 draft. The
archived exploration at
`docs/Local/specs/2026-07-27-manual-failure-review-advanced-provenance.md`
remains historical reference only.

## 1. Goal and scope

The required course-project workflow is:

1. open a retrieval failure case in a static HTML page;
2. inspect its question, gold titles and ranks, retrieved titles and passages,
   and machine-generated rank pattern;
3. write a human note and, later, an optional human label;
4. keep Xin's and Jiajun's assigned cases and browser state separate;
5. double-review only a small overlap set so the owners can compare note
   quality and interpretation;
6. use the completed notes to create a team-authored taxonomy and qualitative
   failure analysis.

The protocol intentionally does **not** require annotation bundles, sidecar
hashes, hash chains, immutable ledgers, anchor registries, submission chains,
machine-enforced chronology, commit-by-commit release state machines, or a
machine-validated adjudication log. Those mechanisms do not answer the research
question and must not block failure analysis.

Git may retain the final shared artifacts, but ordinary file exchange is
sufficient for review. In particular, Xin may send Jiajun exactly:

```text
failure_review.html
jiajun_cases.json
```

Jiajun returns the notes file exported by the page. No local server, package
installation, repository checkout, or second HTML implementation is required.

## 2. Stable boundaries

These are the boundaries that do not move. Later sections may change quotas,
file names, output columns, or validation details; a change to one of the rules
below is a change of research method and requires new owner approval. Other
tools and specifications cite this section as the authority for the
notes-first separation, so its numbering and wording are load-bearing.

1. **Notes-first causal analysis stays human.** The reviewer records
   evidence-bearing observations before choosing a causal category, and
   no system or agent pre-fills a causal label. A machine may compute and
   display structure; it must never propose, infer, default, suggest, or copy a
   failure cause into a human field. A tool that surfaces failure candidates
   emits observable signals only.
2. **The machine rank pattern and the human failure label are different
   layers.** The ten-class `rank_pattern` from
   `docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md` is
   deterministic structural context. It is displayed read-only, it is never
   editable in the review UI, it is never written into a human `label` column,
   and it is never itself treated as a failure cause. The human failure label is
   a separate, editable, optional field that starts empty.
3. **The formal source run is read-only.** No part of this workflow may
   overwrite, rename, or edit anything under `results/runs/2026-07-17_a/`.
4. **Reviewers are separated until they have both submitted.** Neither reviewer
   sees the other's notes for a unit before both have independently recorded
   their own.
5. **A taxonomy is derived from completed notes, never assumed in advance.**
   Category names, definitions, and interpretations are human-authored research
   content.
6. **Review infrastructure may not outgrow the research question.** No
   provenance, serialization, or release mechanism may block annotation unless
   both owners add it to this document as a new research requirement.

### 2.1 Source of truth

The batch is extracted from the existing formal pooled run:

```text
results/runs/2026-07-17_a/details.jsonl
```

The entire `results/runs/2026-07-17_a/` directory is a **read-only source** for
this workflow. The extractor and HTML work must not overwrite, rename, or edit
`details.jsonl`, `failures_review.html`, `gold_rank_patterns.csv`, or any other
file in that run directory.

The existing `results/runs/2026-07-17_a/failures_review.html` is the
implementation starting point only: reuse or adapt its rendering code in the
new Section 4 HTML, while preserving the original file unchanged. The existing
`gold_rank_patterns.csv` supplies the already computed ten-class
`rank_pattern`. That value is read-only structural context, never a human
failure label.

The extractor does not reproduce the run or construct a new provenance system.
It only reads the existing run artifacts and writes new review artifacts under
`results/annotations/manual_review_v1/`. It must refuse an output path inside
`results/runs/2026-07-17_a/`.

### 2.2 Unit identity and criterion

One review unit is identified by:

```text
(run_id, example_id, retriever)
```

The v1 batch contains only strict Any@5 failures: neither gold title appears in
the first five retrieved results for that `(example_id, retriever)` unit.

`review_cutoff` is therefore exactly `5`. It is stored explicitly in every case
and notes row. The earlier annotation `k` field is not used by this simplified
workflow: an upstream export cutoff and the failure-selection cutoff are
different concepts, and v1 has no research need to join on upstream `k`.

## 3. Frozen v1 calibration/open-coding batch and assignments

### 3.1 Exact quotas

The v1 calibration/open-coding batch contains exactly 30 unique units:

| Retriever | Bridge | Comparison | Total |
|---|---:|---:|---:|
| BM25 | 12 | 3 | 15 |
| Dense | 12 | 3 | 15 |
| Total | 24 | 6 | 30 |

This allocation is feasible in the source run. The eligible strict Any@5
population, recomputed from `details.jsonl`, is:

| Retriever | Bridge eligible | Comparison eligible |
|---|---:|---:|
| BM25 | 51 | 12 |
| Dense | 16 | 3 |

Dense has exactly three strict Any@5 comparison failures, so all three are
included; that stratum's draw is the whole stratum.

### 3.1.1 Frozen selection algorithm

"Seeded with 6120" is not a specification: on the 51 sorted BM25 bridge IDs,
drawing 12 with `sample` and shuffling then slicing the first 12 are both
ordinary readings of that phrase, and they select disjoint sets. Exactly one
algorithm is therefore frozen here. An implementation must execute these steps
literally and must not substitute another pseudorandom generator, another
sampling operation, a shared generator stream, or another stratum order.

1. Partition the eligible units by `(retriever, question_type)`.
2. Within each stratum, sort the eligible `example_id` values in **ascending
   Unicode code-point order** (Python's default string comparison; no locale,
   case folding, or normalization).
3. For each stratum, create a **fresh** `random.Random(6120)` instance. Strata
   never share a generator and never continue a previous stream.
4. Draw that stratum's quota with `rng.sample(sorted_ids, quota)`.
5. Sort the drawn `example_id` values of that stratum ascending, by the same
   code-point order, before assembling the batch.
6. Assemble the batch by concatenating the sorted strata in this fixed order:

```text
1. bm25   bridge
2. bm25   comparison
3. dense  bridge
4. dense  comparison
```

That fixed order is both the stratum-processing order and the canonical output
order of `assignment.csv` and of the `cases` arrays. Because each stratum resets
the generator, processing order does not affect which units are drawn; it is
frozen so that the output ordering is reproducible.

Repeat generation must reproduce the exact selected key set, the exact overlap
key set, and the exact ordering. The expected keys are frozen in Section 3.4.

Rank patterns are displayed and considered when the owners inspect the selected
batch, but they are not additional blocking quotas. All 30 units are used to
calibrate the review method, develop evidence-based notes, and derive candidate
categories. They are a qualitative open-coding sample, not a held-out
validation set or a prevalence estimate.

### 3.2 Exact overlap and workload

Exactly four of the 30 units are double-reviewed:

| Retriever | Bridge overlap | Comparison overlap | Total overlap |
|---|---:|---:|---:|
| BM25 | 1 | 1 | 2 |
| Dense | 1 | 1 | 2 |
| Total | 2 | 2 | 4 |

The four overlap units are selected from the frozen 30-unit batch by repeating
the Section 3.1.1 procedure independently inside each `retriever x
question_type` stratum of the already selected batch:

1. take that stratum's already selected units;
2. sort their `example_id` values ascending by code point;
3. create a **fresh** `random.Random(6120)` instance;
4. draw exactly one unit with `rng.sample(sorted_selected_ids, 1)`.

The four drawn units are emitted in the same fixed stratum order as Section
3.1.1. The overlap draw reads only the selected batch, never the full eligible
population, and never reuses the generator state left by selection.

They appear in both reviewer files with byte-equivalent case content. Both
reviewers complete these four units first, without seeing each other's notes,
and then compare them to calibrate the note rubric before reviewing their
private assignments.

The other 26 units are split as follows:

- Xin receives 7 non-overlap BM25 units and 6 non-overlap Dense units;
- Jiajun receives 6 non-overlap BM25 units and 7 non-overlap Dense units.

Therefore each reviewer sees exactly 17 units: the same four calibration
overlap units followed by 13 private open-coding assignments. Double review
adds review actions, not unique units.

### 3.3 Machine-checkable assignment predicate

Let `X` and `J` be the unit-key sets in `xin_cases.json` and
`jiajun_cases.json`, and let `O = X intersection J` be the overlap set. A v1
assignment is valid exactly when all of the following hold:

```text
|X| = 17
|J| = 17
|X union J| = 30
|O| = 4

private counts, where X\O and J\O are the non-overlap assignments:
  |{u in X\O : u.retriever = bm25 }| = 7
  |{u in X\O : u.retriever = dense}| = 6
  |{u in J\O : u.retriever = bm25 }| = 6
  |{u in J\O : u.retriever = dense}| = 7
```

The four private-count clauses are part of the predicate, not commentary on it.
Without them the predicate accepts an assignment that Section 3.2 forbids: the
13 private BM25 units can all go to Xin and the 13 private Dense units all to
Jiajun while `|X|`, `|J|`, the union, the intersection, and both strata tables
remain exactly correct. Any validator that reports such a split as valid is not
implementing this section.

In addition:

- every unit is unique within each file;
- the union has the exact Section 3.1 quotas;
- the intersection has the exact Section 3.2 quotas;
- the union and the overlap set equal the frozen Section 3.4 key sets;
- every non-overlap unit appears in exactly one file;
- every overlap unit carries `is_overlap: true` in both files;
- every non-overlap unit carries `is_overlap: false`;
- every case's `rank_pattern` satisfies the Section 4 source binding;
- overlapping case objects have identical research content; only the top-level
  `reviewer_id` differs.

#### Paired controls

| ID | Assignment | Expected |
|---|---|---:|
| `AS-OK-1` | Xin private `{bm25: 7, dense: 6}`, Jiajun private `{bm25: 6, dense: 7}`, valid union/overlap strata | accept |
| `AS-NO-1` | identical to `AS-OK-1` except Xin private `{bm25: 13, dense: 0}` and Jiajun private `{bm25: 0, dense: 13}` | reject |
| `AS-NO-2` | Xin private `{bm25: 6, dense: 7}` and Jiajun private `{bm25: 7, dense: 6}` — the two reviewers' quotas swapped | reject |
| `AS-NO-3` | `AS-OK-1` with one private unit moved from Xin to Jiajun, so `\|X\| = 16` and `\|J\| = 18` | reject |
| `AS-NO-4` | `AS-OK-1` with a fifth unit placed in both files | reject |

`AS-NO-1` differs from `AS-OK-1` in exactly one property — how the 26 private
units are distributed between the reviewers — so a validator that accepts both
has not implemented the private-count clauses.

These set and quota checks replace the earlier conceptual partial-coverage
rules. Partial-coverage review is not a Gate A, MVP, or v1 requirement. If the
owners later want such a batch, they create a separate, explicitly quotaed
batch using the same HTML after the v1 analysis is complete.

### 3.4 Frozen v1 selection oracle

A frozen batch that only a program can name is not frozen. The exact keys the
Section 3.1.1 algorithm produces on the accepted source run are therefore
recorded here, in the canonical output order, so that a future Python or
library detail cannot silently change the batch without failing an explicit
comparison. Generation must reproduce this list exactly; a difference is a
rejection, not a new batch.

BM25 bridge (12):

```text
5a79b7f6554299029c4b5f6f
5a7c9f325542990527d554e6
5a7d61775542991319bc93b9
5a83880e554299123d8c214e
5a83a532554299334474606f
5abcc96c5542996583600492
5ac1a3665542994ab5c67daf
5adc8977554299438c868de2
5ade42b55542992fa25da717
5adf58f15542993a75d264d2
5ae057fd55429945ae959328
5ae60426554299546bf83019
```

BM25 comparison (3):

```text
5a78b209554299148911f93e
5ab72a025542992aa3b8c7b8
5ab8f57b5542991b5579f097
```

Dense bridge (12):

```text
5a7d19d85542995ed0d165e8
5a81ebee554299676cceb16d
5a83aaeb5542996488c2e483
5a85cead5542991dd0999ea9
5ab48c325542996a3a969f93
5ab978855542996be2020512
5add67915542992200553af8
5ade69e455429975fa854ec5
5ae048a255429924de1b708e
5ae0a59a55429945ae9593e2
5ae1801955429901ffe4aec4
5ae1f596554299234fd04372
```

Dense comparison (3, the entire eligible stratum):

```text
5a76387d554299109176e6ba
5a78b209554299148911f93e
5a8d93ad554299653c1aa13d
```

The four overlap units, in the same stratum order:

```text
5a7d61775542991319bc93b9  bm25   bridge
5a78b209554299148911f93e  bm25   comparison
5a83aaeb5542996488c2e483  dense  bridge
5a76387d554299109176e6ba  dense  comparison
```

`5a78b209554299148911f93e` appears once under BM25 comparison and once under
Dense comparison. Those are two distinct review units, because a unit key
includes the retriever; both are selected, and both happen to be overlap units
of their own stratum.

The 30 keys above are 30 distinct `(example_id, retriever)` pairs and 29
distinct `example_id` values. Cardinality checks must be applied to the unit
key, never to `example_id` alone.

If the owners ever intentionally refreeze the batch — a different source run, a
different quota, or a different criterion — they replace this section in the
same change that alters the rule, and the previous keys become historical
record.

#### Paired controls

| ID | Case | Expected |
|---|---|---:|
| `SS-OK-1` | run the Section 3.1.1 algorithm twice; compare selected keys, overlap keys, and order | identical both times |
| `SS-OK-2` | compare a generated batch against the Section 3.4 lists | exact match |
| `SS-NO-1` | `rng.shuffle(sorted_ids)` then take the first `quota` entries | rejected: not the frozen draw, and it selects different units |
| `SS-NO-2` | one generator instance shared across all four strata | rejected: strata must reset |
| `SS-NO-3` | strata emitted in an order other than the Section 3.1.1 list | rejected: output order is frozen |
| `SS-NO-4` | overlap drawn from the full eligible population rather than the selected batch | non-conforming; **not** detectable from the keys on this run — see below |

On the actual source run, `SS-NO-1` and `SS-OK-2` disagree in all 24 of 24
selected positions for BM25 bridge and all 6 of 6 for BM25 comparison, which is
why the draw operation has to be named rather than implied.

`SS-NO-4` is deliberately recorded as a procedural requirement rather than a
key-comparison control, because on this population the non-conforming reading
coincides with the frozen one. Drawing one unit from the full eligible stratum
yields the same four keys as drawing from the selected batch in all four strata,
and each of those keys happens to lie inside the selected batch. That is a
coincidence of this data, not a property of the rule: on a different population
the full-population draw can return a unit that was never selected, which would
put an unassigned unit in both reviewer files. The overlap draw must therefore be
verified by reading the generator, and a reviewer must not treat the matching
keys as evidence that either reading is acceptable.

## 4. Reviewer case files

The implementation writes new files outside the source run:

```text
results/annotations/manual_review_v1/failure_review.html
results/annotations/manual_review_v1/assignment.csv
results/annotations/manual_review_v1/xin_cases.json
results/annotations/manual_review_v1/jiajun_cases.json
```

`failure_review.html` is derived from the useful parts of the existing run
HTML, but it is a new artifact. The source run's `failures_review.html` remains
byte-for-byte untouched.

`assignment.csv` is the repository's compact record of the split:

```text
run_id,example_id,retriever,question_type,assigned_reviewer,is_overlap
```

An overlap unit has two rows, one for each reviewer. A non-overlap unit has one.
The two JSON files are the delivery artifacts; Jiajun does not need
`assignment.csv` to perform the review.

Each JSON file is one closed object:

```json
{
  "batch_id": "manual_review_v1",
  "reviewer_id": "jiajun",
  "run_id": "2026-07-17_a",
  "review_cutoff": 5,
  "cases": []
}
```

Every `cases` item contains only the material needed for review:

```text
example_id
retriever
question_type
question
gold_titles
gold_ranks
retrieved_results
rank_pattern
review_cutoff
is_overlap
```

`retrieved_results` preserves rank, title, score, and passage text through rank
50. The file contains no notes from either reviewer and no case assigned only to
the other reviewer. `review_cutoff` is the per-case integer required by Section
2.2; see Section 4.2 for its exact contract.

### 4.1 Exact `rank_pattern` source binding

Membership in the accepted ten-label vocabulary is not sufficient. Two selected
units with different valid labels can have those labels exchanged and every
vocabulary check still passes, while neither unit carries its own machine
context — a reviewer would then be reading a true label attached to the wrong
case. `rank_pattern` is therefore bound to an exact source row, not to a
vocabulary.

The source is exactly:

```text
results/runs/2026-07-17_a/gold_rank_patterns.csv
```

and the join key is exactly:

```text
(example_id, retriever)
```

within the fixed run `2026-07-17_a`. That file holds 1,000 rows and 1,000
distinct keys, so the join is total and unique for every selectable unit.

For the selected batch as a whole:

- the key set of the generated cases must join to the source file with **exactly
  one** matching row per case;
- the join must cover every selected unit — a missing source row is a rejection,
  never a blank or inferred label;
- a key must not appear twice among the selected cases;
- a case key that does not exist in the source file is a rejection;
- no selected unit may be silently dropped from, or added to, the joined set.

For each individual case:

- `rank_pattern` must equal that row's `rank_pattern` **byte for byte**, with no
  normalization, case folding, whitespace trimming, or relabeling;
- a value that is a valid vocabulary member but does not equal the value in its
  own source row is a rejection.

Generation must perform this comparison against the source file, and validation
must repeat it independently rather than trusting the generator. The value stays
read-only structural context in every downstream artifact and is never written
into a human `label` field (Section 2, boundary 2).

#### Paired controls

| ID | Case | Expected |
|---|---|---:|
| `RP-OK-1` | every case's `rank_pattern` copied from its own `(example_id, retriever)` source row | accept |
| `RP-NO-1` | `RP-OK-1` with two units' distinct valid labels exchanged | reject |
| `RP-NO-2` | `RP-OK-1` with one case's label replaced by a different valid vocabulary member | reject |
| `RP-NO-3` | `RP-OK-1` with one selected case's source row absent from the join | reject |
| `RP-NO-4` | `RP-OK-1` with one case key present twice | reject |
| `RP-NO-5` | `RP-OK-1` plus one extra case whose key is not in the source file | reject |
| `RP-NO-6` | `RP-OK-1` with a case key matched on `example_id` only, ignoring `retriever` | reject |

`RP-NO-1` and `RP-NO-2` both pass a vocabulary-only check and both fail the
source binding; that difference is the whole point of this subsection.
`RP-NO-6` matters because 29 of the 30 selected `example_id` values are unique
but one appears under both retrievers, so an `example_id`-only join can attach
BM25 structure to a Dense unit.

### 4.2 Exact `review_cutoff` per-case storage

Section 2.2 requires `review_cutoff` to be stored explicitly in every case, not
only once at the top level of the reviewer file. Each case object therefore
carries its own `review_cutoff` field, in addition to the file-level
`review_cutoff` in Section 4's JSON skeleton and the per-row `review_cutoff` in
the Section 6 notes export; all three equal the same frozen integer `5` for v1.

- every case's `review_cutoff` is present and equals the JSON literal integer
  `5`;
- a boolean, string, float, or any value other than integer `5` is a rejection;
- a case object missing this field is a rejection.

#### Paired controls

| ID | Case | Expected |
|---|---|---:|
| `RC-OK-1` | every case carries integer `review_cutoff: 5` | accept |
| `RC-NO-1` | one case is missing the `review_cutoff` field | reject |
| `RC-NO-2` | one case has `review_cutoff: "5"` (string) or `true` (boolean) instead of the integer | reject |
| `RC-NO-3` | one case has `review_cutoff: 10` | reject |

## 5. Shared HTML behavior

There is one new shared
`results/annotations/manual_review_v1/failure_review.html`, not one page per
reviewer. It must:

1. use a browser file picker to load either reviewer JSON file, so opening the
   HTML by double-click works without `fetch`, a local server, or CORS setup;
2. read `reviewer_id` from the loaded file and show exactly its 17 cases, with
   an overlap-first filter or ordering for the calibration step;
3. display question, question type, retriever, gold titles and ranks, top-50
   results with passage text, overlap status, and a clearly named read-only
   **Machine rank pattern (10-class)** field containing that unit's own
   source-bound `rank_pattern` (Section 4.1);
4. provide one notes textarea and a separate editable **Human failure label
   (optional)** field per case; the human label starts empty and may remain
   empty throughout calibration/open coding;
5. save draft state under a key containing both `batch_id` and `reviewer_id`, so
   Xin's and Jiajun's browser state cannot collide;
6. never load or display the other reviewer's notes;
7. export only the active reviewer's 17 rows;
8. support re-import of that reviewer's own exported notes file;
9. reject a notes import whose `batch_id` or `annotator` does not match the
   active reviewer file.

The machine rank-pattern display and the human label input must be visually and
semantically distinct. The page must never prefill, infer, or copy the
ten-class `rank_pattern` into the human `label` field.

The page may show a suggested note template, but one free-form evidence-based
note is the actual requirement. A useful prompt is:

```text
Observed:
Missing gold:
Retrieved evidence or distractor:
Possible reason:
Alternative or uncertainty:
```

`label` may remain empty during open coding. An empty human label does not hide
the read-only ten-class machine rank pattern.

## 6. Notes export

The page exports one UTF-8 CSV per reviewer:

```text
<reviewer_id>_notes.csv
```

with columns:

```text
batch_id,run_id,example_id,retriever,review_cutoff,label,notes,annotator,annotated_at
```

Rules:

- the file has exactly 17 data rows and one row per displayed unit;
- `batch_id` is `manual_review_v1`;
- `run_id` is `2026-07-17_a`;
- `review_cutoff` is the integer `5`;
- `annotator` equals the loaded file's `reviewer_id`;
- `notes` is non-empty for a completed row;
- `label` may be empty until the taxonomy is approved;
- `annotated_at` is an ISO 8601 timestamp produced by the page;
- an export never contains the other reviewer's rows or notes.

Saving a newer file does not require a formal submission chain. Reviewers keep
the latest file and may retain earlier copies through ordinary filenames or Git
if useful.

## 7. Review workflow and overlap comparison

1. Generate the 30-unit assignment and both reviewer files with the Section
   3.1.1 algorithm, then validate them against the Section 3.4 oracle, the
   complete Section 3.3 predicate, the Section 4.1 source binding, and the
   Section 4.2 per-case `review_cutoff` storage.
2. Xin opens the HTML with `xin_cases.json`; Jiajun opens the same HTML with
   `jiajun_cases.json`.
3. Both independently review the four overlap units first. Neither reads the
   other's notes before saving this first pass.
4. Compare the four overlap pairs and calibrate the evidence and note rubric.
   Discuss factual mistakes, missing evidence, unsupported causal claims, and
   ambiguous instructions. Preserve both original overlap notes.
5. Each reviewer then completes the 13 private units using the calibrated
   rubric and exports a 17-row notes CSV.
6. If a note needs correction, edit it in a new export or record the correction
   in the shared analysis notes. A ledger is not required.

Overlap is a consistency check on note quality and interpretation. It is not an
agreement statistic, majority vote, or requirement to use identical prose.

## 8. Taxonomy and final category counts

After all 30 calibration/open-coding units are complete, Xin and Jiajun jointly
write `taxonomy_v1`. Category names, definitions, evidence requirements,
examples, and interpretations are human-authored research content.

Raw reviewer labels and final analytical labels are different layers:

- the two reviewer notes for an overlap unit are both retained;
- each of the 30 unique units receives exactly one final analytical label;
- the owners jointly resolve differing proposed labels after reading both
  notes;
- if they cannot resolve a unit without forcing agreement, its final label is
  `unresolved`;
- no overlap unit is counted twice.

The final unit-level file is:

```text
results/annotations/manual_review_v1/final_labels.csv
```

with columns:

```text
run_id,example_id,retriever,final_label,resolution
```

where `resolution` is `single_review`, `overlap_agreed`,
`overlap_resolved`, or `unresolved`.

Any descriptive category counts for this calibration batch are computed only
from the 30 rows of `final_labels.csv`. The denominator is always 30;
named-category counts plus the `unresolved` count must equal 30. The report must
call these calibration/open-coding counts, not prevalence estimates. Reviewer
row counts may be reported separately as workload or overlap evidence, but
never as category prevalence.

This rule fully determines how post-taxonomy disagreement affects the
calibration-batch counts: it produces one resolved category or one `unresolved`
unit, never two votes.

If the owners want evidence that `taxonomy_v1` transfers beyond the cases used
to create it, they may later freeze a separate validation batch. That batch is
not selected or annotated until this calibration batch and taxonomy are
complete, and it is not a Gate A requirement.

## 9. Minimal validation and acceptance

Implementation validation is limited to checks that protect the research
workflow:

- all generated output paths are under
  `results/annotations/manual_review_v1/`, and generation refuses to write
  inside `results/runs/2026-07-17_a/`;
- the source run files, including its original `failures_review.html`, remain
  unchanged after extraction and HTML generation;
- source filtering returns strict Any@5 failures only, and the eligible
  population reproduces the Section 3.1 table (BM25 bridge 51, BM25 comparison
  12, Dense bridge 16, Dense comparison 3);
- generation follows the Section 3.1.1 algorithm and reproduces the Section 3.4
  selected and overlap key sets and their order exactly, on a repeat run as well
  as the first;
- the complete Section 3.3 predicate passes, **including the four
  reviewer-private retriever counts**, and rejects the `AS-NO-1` all-BM25 /
  all-Dense split;
- the Section 4.1 `rank_pattern` source binding passes: the selected key set
  joins one-to-one to `results/runs/2026-07-17_a/gold_rank_patterns.csv` on
  `(example_id, retriever)`, and every displayed value equals its own source
  row's value byte for byte. Missing, duplicate, extra-key, mismatched, and
  swapped-label cases are rejected, and a vocabulary-membership check alone does
  not satisfy this item;
- the Section 4.2 per-case `review_cutoff` check passes: every case carries its
  own integer `review_cutoff` equal to `5`, and a case missing the field or
  carrying a non-integer or non-`5` value is rejected;
- overlap content is identical across the two reviewer JSON files;
- the HTML loads each file through the picker, shows the four overlap cases
  first, and shows 17 cases in total;
- every card displays that unit's own source-bound ten-class `rank_pattern` as
  read-only machine context beside a separate human label input that is empty by
  default;
- saving notes with an empty human label succeeds, and no code path copies
  `rank_pattern` into `label`;
- browser state is separated by batch and reviewer;
- each exported CSV has the Section 6 header, identity, and 17-row cardinality;
- cross-reviewer import is rejected;
- the union of the two exports covers 30 unique units with four duplicated
  overlap units;
- `final_labels.csv` contains exactly 30 unique units and its counts sum to 30.

Each of the four frozen contracts above ships with paired controls, and Gate B
requires both halves of every pair: the named legal control must be accepted and
the named rejection must be rejected. The pairs are `AS-OK-1` / `AS-NO-1..4`
(Section 3.3), `RP-OK-1` / `RP-NO-1..6` (Section 4.1), `RC-OK-1` / `RC-NO-1..3`
(Section 4.2), and `SS-OK-1..2` / `SS-NO-1..4` (Section 3.4). Each rejection
differs from its legal control in exactly one property, so a validator that
accepts both halves of a pair has not implemented that contract.

No additional provenance or serialization feature may block annotation unless
both owners add it to this document as a new research requirement.

## 10. Feasibility and stopping rule

The implementation reuses the existing `results/runs/2026-07-17_a/` data and
HTML. Required new work is limited to:

1. one small extractor for the frozen assignment and reviewer JSON files;
2. one HTML file-picker/reviewer-isolation/notes-export path;
3. the focused validation checks in Section 9.

The team starts annotation as soon as those three items work. Improvements to
packaging, provenance, UI polish, or automation are non-blocking. The retrieval
failure analysis, reranker evaluation, presentation, and report take priority
over annotation infrastructure.

## 11. Gates

### 11.1 Gate A - protocol approval

Gate A passes only when all of the following are true:

- [x] the joint owner approval of the Section 12.1 decisions is recorded — Xin
      and Jiajun approved them offline on 2026-07-28 (Section 12.2);
- [ ] a fresh independent review of the final corrected canonical text passes;
- [x] AI assistance is recorded as required by the course policy — satisfied
      per the owner decision on the round-13 prompt-record gap (Section 12.2).

There is no separate commit-SHA approval condition. The owners approve the
workflow, not a Git object; requiring both owners to sign the same commit added
an administrative ceremony that answered no research question and blocked the
review it was supposed to protect.

Gate A approves the workflow and authorizes the focused implementation. It does
not assert that the HTML or extractor already works.

### 11.2 Fresh independent review

For Gate A, **independent** means the review is performed by a person or agent
session that did not author or edit any content difference between the last
reviewed revision and the reviewed text. An owner approval is not an independent
review.

**Fresh** means all of the following:

1. it identifies the exact bytes it reviewed. A Git commit SHA is one acceptable
   identifier; the SHA-256 digest of the reviewed file plus its working-tree
   state is another, equally acceptable one. A pre-existing commit is **not**
   required, and a review may not be deferred for the absence of one;
2. it reads the complete current document rather than carrying forward an old
   verdict;
3. it explicitly checks the Section 3.3 predicate including the reviewer-private
   counts, the Section 3.4 selection oracle, the Section 4.1 `rank_pattern`
   source binding, the Section 4.2 per-case `review_cutoff` storage, reviewer
   separation, overlap arithmetic, notes export, unit-level taxonomy counting,
   and the infrastructure scope cap;
4. it persists a new review artifact and records a clear PASS or FAIL in DR-003.

A PASS for earlier bytes does not satisfy Gate A. Any substantive change after a
PASS invalidates that PASS, and the new text requires a new review. The
agent/session that made a corrective edit is ineligible to issue the independent
Gate A verdict on it.

The recorded joint owner approval in Section 12.2 is **not** invalidated by a
corrective clarification, because it approves the workflow rather than a
revision. It is invalidated only by a change that materially alters the agreed
workflow — a different source run, criterion, sample size, overlap scheme,
reviewer-separation model, or delivery mechanism — which requires a new owner
decision.

### 11.3 Gate B - implementation acceptance

Gate B passes when the Section 9 checks pass against the actual HTML, extractor,
two reviewer JSON files, and notes round trip. Four of those checks are
non-negotiable and must be demonstrated with both halves of their paired
controls: the complete Section 3.3 assignment predicate including the four
reviewer-private retriever counts, the Section 3.4 selection oracle under repeat
generation, the Section 4.1 exact `rank_pattern` source binding, and the Section
4.2 per-case `review_cutoff` storage. A separate implementation review may
inspect those artifacts, but no release ledger or sidecar system is added.

### 11.4 Gate C - review completion

Gate C passes when:

- both reviewers independently complete and compare the four overlap cases
  before reviewing their private cases;
- both 17-row notes exports are complete;
- `taxonomy_v1` is jointly approved;
- `final_labels.csv` has 30 unique unit rows and category counts sum to 30.

## 12. Owner decisions and approval

### 12.1 Decision-level approval

This table records the **substantive workflow decisions** and who approved them.

| Topic | Governing decision | Status |
|---|---|---|
| Source | Reuse `results/runs/2026-07-17_a/` as read-only input; write all new artifacts under `results/annotations/manual_review_v1/` and never overwrite the original run or HTML | Approved by Xin and Jiajun, 2026-07-28 |
| Interface | One new shared static HTML, derived from but not overwriting the original run HTML, using a local file picker | Approved by Xin and Jiajun, 2026-07-28 |
| Labels | Display the existing ten-class `rank_pattern` as read-only machine context; keep the separate human failure label editable, empty by default, and optional during open coding | Approved by Xin and Jiajun, 2026-07-28 |
| Separation | Reviewer-specific JSON and browser state; no access to the other reviewer's notes before overlap comparison | Approved by Xin and Jiajun, 2026-07-28 |
| Sample | 30 strict Any@5 units as the calibration/open-coding batch, with the exact Section 3.1 quotas | Approved by Xin and Jiajun, 2026-07-28 |
| Sampling rule | One frozen selection algorithm (Section 3.1.1) and the frozen key oracle (Section 3.4) | Approved by Xin and Jiajun, 2026-07-28 |
| Overlap | Exactly four units reviewed first for calibration, one bridge and one comparison per retriever | Approved by Xin and Jiajun, 2026-07-28 |
| Workload split | Xin 7 BM25 + 6 Dense private units; Jiajun 6 BM25 + 7 Dense; enforced by the Section 3.3 predicate | Approved by Xin and Jiajun, 2026-07-28 |
| Notes | Separate 17-row exports; labels optional during open coding | Approved by Xin and Jiajun, 2026-07-28 |
| Counting | One final label per unique unit; unresolved overlap disagreement counts once as `unresolved` | Approved by Xin and Jiajun, 2026-07-28 |
| Partial cases | Not part of v1 or any gate; a later batch requires its own explicit quotas | Approved by Xin and Jiajun, 2026-07-28 |
| Infrastructure | No sidecars, hash chains, ledgers, submission chains, or chronology machinery | Approved by Xin and Jiajun, 2026-07-28 |

Jiajun's earlier written verdict, "APPROVE WITH REQUIRED CLARIFICATIONS; Gate A
not yet met," is superseded by the joint approval in Section 12.2: the
clarifications he asked for are incorporated in this text.

### 12.2 Owner-approval record

Xin and Jiajun discussed the course-project workflow and **jointly approved it
offline on 2026-07-28**. Xin recorded that approval in this document on the same
date.

Scope and effect of that approval:

- it covers every Section 12.1 decision;
- it authorizes the narrowly scoped corrective clarifications that the
  independent review required — completing the assignment predicate, binding
  `rank_pattern` to its exact source row, freezing one selection algorithm, and
  restoring the Section 2 boundary section — because those make the agreed
  workflow precise rather than changing it;
- it does **not** authorize expanding the agreed workflow. A change to the source
  run, criterion, sample size, overlap scheme, reviewer-separation model,
  delivery mechanism, or gate structure requires a new owner decision;
- it remains effective across later revisions of this document unless such a
  material change occurs.

**No commit-SHA approval is required.** The earlier requirement that both owners
sign off on the same Git commit is withdrawn. Provenance for the approval is this
record plus the append-only session history in
`docs/Completion_Log/Xin_Week3_Completion_Log.md`.

**AI-usage prompt-record gap decision (2026-07-28).** The round-14 independent
review found that one append-only session-log entry — the 2026-07-28 course
simplification / round-13 corrective-pass entry in
`docs/Completion_Log/Xin_Week3_Completion_Log.md` — has no recoverable prompt
text; Xin confirmed the prompt cannot be recovered from his records. Xin decided
this gap is immaterial and directed that it not block Gate A. The AI-usage
record is treated as satisfied with that one entry's prompt field honestly
documented as unrecoverable rather than fabricated or reconstructed. This
decision resolves that one already-past, already-disclosed gap; it does not
authorize skipping the session-log rule for any future session.

The remaining Gate A condition is the fresh independent review (Section 11.2).
Recording the owner approval and the AI-usage decision here does not assert that
Gate A has passed.

## 13. Historical reference

Earlier DR-003 reviews and the archived advanced-provenance document preserve
the rationale for the abandoned infrastructure-heavy approach. They are not
requirements for this course-project protocol. Earlier PASS verdicts apply only
to their named revisions and do not satisfy the fresh-review rule in Section
11.2.
