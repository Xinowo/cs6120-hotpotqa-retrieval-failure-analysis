---
status: draft
last_updated: 2026-07-27
---

# Manual Failure Review Protocol: Discussion Draft

**Design record:** DR-003  
**Audience:** Xin and Jiajun  
**Purpose:** agree on one reproducible notes-first review protocol before changing the HTML review tool or beginning the main manual-review batch  
**Decision status:** open; this document is not approved for implementation yet

## 1. How to use this document

This is a decision worksheet, not a finished research protocol. Xin and Jiajun
should discuss every item in Section 4, replace each `OPEN` entry with an agreed
decision and rationale, run the calibration exercise in Section 7, and sign the
approval table in Section 10.

The protocol becomes implementation-ready only when:

1. every blocking question is answered;
2. both reviewers have completed the same calibration cases independently;
3. calibration disagreements have been discussed and the notes rubric has been
   revised where necessary;
4. both reviewers approve the same document commit;
5. the document lifecycle is changed from `draft` to `active`; and
6. DR-003 is changed from `proposed` to `design-approved`.

Later changes must update `last_updated`, record the reason in the decision log,
and use a new protocol version or sampling-manifest version when the change can
affect which cases are reviewed or how annotations are interpreted.

## 2. Terms

### 2.1 Review unit

One review unit is one `(example_id, retriever)` pair. BM25 and Dense outputs
for the same HotpotQA example are two distinct review units.

### 2.2 Machine rank pattern

`rank_pattern` is the accepted, deterministic 10-class structural description
of where the two gold titles occur in the pooled top 50. It is generated for all
1,000 review units under `gold_rank_partition_v1` and is not a failure cause.
The canonical contract is
`docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md`.

### 2.3 Any@5 failure

An Any@5 failure has zero gold titles in the first five results. In the formal
pooled run, there are 82 such units: 63 BM25 and 19 Dense.

### 2.4 Full@5 failure

A Full@5 failure has fewer than both gold titles in the first five results. It
includes zero-coverage and one-gold-only cases. In the formal pooled run, there
are 598 such units: 349 BM25 and 249 Dense. Of these, 516 are partial cases that
would not appear in a strict Any@5 failure set.

The current accepted HTML's default 184-card universe is neither of these exact
sets: without `k` narrowing it includes a unit when Any Evidence Recall fails at
any of `k = 2, 5, 10`.

### 2.5 Notes-first review

The reviewer records evidence-bearing observations before choosing a causal
category. A non-empty `notes` value with an empty `label` is a completed
annotation during open coding. A blank label must not be treated as unfinished
when notes are present.

### 2.6 Calibration cases

A small shared set reviewed independently before the main batch. Its purpose is
to align evidence standards and use of the notes template, not to force the two
reviewers to invent or agree on a final taxonomy in advance.

### 2.7 Blind overlap

A subset of main-batch units reviewed independently by both people without
seeing the other person's notes first. The overlap reveals reviewer drift and
ambiguous instructions. “Blind” concerns the other annotation, not the identity
of the case.

### 2.8 Sampling manifest

A sampling manifest is a frozen CSV listing the exact review units selected,
why they were selected, their strata, their assigned reviewer, and the protocol
and random-seed provenance. It contains no failure interpretation. It prevents
the two reviewers from silently using different filters or hand-picked case
sets and makes the qualitative sample reproducible.

Proposed path:

```text
results/annotations/review_sample_manifest_v1.csv
```

## 3. Boundaries that should not be reopened in this protocol

Unless both owners explicitly revise an accepted upstream contract:

- `rank_pattern` remains machine-generated, read-only, exhaustive over all
  pooled top-50 two-gold units, and separate from human failure reasons;
- `rank_pattern` must never be written into `annotations.csv.label`;
- human causal labels must not be generated or prefilled automatically;
- `label` may be empty when `notes` is non-empty;
- machine counts and rank patterns are not research interpretations;
- failure-reason hypotheses must be supported by case-level evidence;
- the existing annotation CSV columns remain compatible:
  `run_id, example_id, retriever, k, label, notes, annotator, annotated_at`;
- the accepted any-based report remains available unless a separately approved
  migration explicitly replaces it; and
- final causal categories, category definitions, adjudication judgments, and
  report interpretations are authored and approved by the team.

## 4. Blocking decision worksheet

The “proposed default” column is a starting point for discussion, not an
approved choice.

| ID | Open question | Options or information needed | Proposed default for discussion | Decision | Rationale |
|---|---|---|---|---|---|
| Q1 | What is the primary review criterion? | Strict Any@5; Full@5; another explicitly defined criterion | Full@5, because partial evidence coverage is central to multi-hop retrieval, while preserving the accepted Any-based page | OPEN | OPEN |
| Q2 | How is the new criterion delivered? | Separate `failures_review_full_at5.html`; explicit CLI criterion/cutoff; replacement of old output | Add an explicit Full@5 view and preserve the accepted Any-based output | OPEN | OPEN |
| Q3 | Is the human review full-universe or sampled? | All 598 Full@5 units; stratified sample; staged pilot followed by a go/no-go decision | Start with calibration plus a stratified main sample; use all 1,000 units only for machine statistics | OPEN | OPEN |
| Q4 | What is the initial human-review sample size? | Total number and per-retriever number; account for available time | Decide only after timing the calibration cases; record the resulting target here | OPEN | OPEN |
| Q5 | How are BM25 and Dense quotas chosen? | Equal counts; proportional to eligible failures (349:249 under Full@5); separate per-retriever targets based on research questions | Use explicit per-retriever targets so both retrievers receive enough qualitative coverage; do not let raw failure prevalence determine the entire sample | OPEN | OPEN |
| Q6 | Which strata control sampling? | Retriever; question type; rank pattern; zero-vs-partial coverage; combinations of these | Stratify by `retriever × question_type × rank_pattern`; merge only strata that are too sparse and document the merge | OPEN | OPEN |
| Q7 | How are rare and common strata handled? | Include all rare units; fixed quota per stratum; proportional allocation; capped proportional allocation | Include all units below an agreed rarity threshold and seeded-sample from larger strata | OPEN | OPEN |
| Q8 | What random seed and sampling algorithm are frozen? | Integer seed; stable sorting before seeded selection; exact script/version | Use one recorded integer seed and deterministic sort by `(example_id, retriever)` before sampling | OPEN | OPEN |
| Q9 | What must every note contain? | Minimum evidence fields; whether a reason hypothesis is required; how uncertainty is recorded | Use the Section 5 template; permit `Possible reason: unknown` rather than forcing a category | OPEN | OPEN |
| Q10 | What language is used for annotations? | English only; another shared language plus an export/UI change | English, matching the accepted HTML import/export validation and report language | OPEN | OPEN |
| Q11 | How many calibration cases are required? | Number; retriever/question-type/pattern coverage; who chooses them | 8 total: 4 BM25 and 4 Dense, covering bridge/comparison and several rank patterns | OPEN | OPEN |
| Q12 | What blind-overlap proportion is required? | Fixed count; percentage; minimum floor; balance across retrievers | 10–15% of the main sample, with an agreed minimum count and roughly equal BM25/Dense coverage | OPEN | OPEN |
| Q13 | How are overlap disagreements handled? | Discussion only; third adjudicator; retain both hypotheses; revise rubric and re-review | Use the process in Section 8; never force agreement when the evidence remains ambiguous | OPEN | OPEN |
| Q14 | When may human labels be introduced? | Never in this pass; after a fixed number of notes; after saturation and team approval | Keep labels optional during open coding; freeze a candidate codebook only after reviewing a pre-agreed batch | OPEN | OPEN |
| Q15 | How is criterion/sample provenance carried with annotations? | Change annotation schema; separate manifest; page metadata plus manifest | Preserve the eight-column annotation CSV and join it to a versioned manifest containing criterion, cutoff, sample, and protocol version | OPEN | OPEN |
| Q16 | Who is the primary reviewer for each retriever? | Xin/Dense and Jiajun/BM25; another split | Xin primarily reviews Dense; Jiajun primarily reviews BM25; both review the blind-overlap subset | OPEN | OPEN |
| Q17 | What ends the first review batch? | Fixed count; time budget; evidence saturation; presentation deadline | Fixed manifest count first; then jointly decide whether more strata or cases are needed | OPEN | OPEN |
| Q18 | What triggers protocol revision and re-review? | Any disagreement; only rubric ambiguity; material selection/schema changes | Revise when instructions caused a systematic ambiguity; decide explicitly whether affected completed cases must be revisited | OPEN | OPEN |

## 5. Proposed shared notes template

The current CSV has one free-text `notes` field. Use the same labeled structure
inside that field rather than adding schema columns before the contract is
approved:

```text
Observed: <what the ranked output objectively shows>
Missing gold: <which required title/evidence is outside the cutoff or top 50>
Retrieved evidence/distractor: <specific retrieved title(s), rank(s), and why they matter>
Possible reason: <evidence-supported hypothesis, or "unknown">
Alternative/uncertainty: <plausible alternative or limitation of the evidence>
```

Discussion questions for the template:

1. Are all five lines required, or may `Alternative/uncertainty` be omitted when
   no meaningful alternative exists?
2. Must ranks be recorded for every cited title?
3. Is the reviewer expected to inspect passage text, or only titles and ranks?
4. What evidence is sufficient to call a result a distractor rather than merely
   a low-ranked non-gold result?
5. May a reviewer mention more than one possible cause?
6. How should unresolved gold-title ambiguity or annotation noise be recorded?
7. What makes a note too vague to count as complete?

Proposed completeness rule:

- `Observed`, `Missing gold`, and `Retrieved evidence/distractor` contain
  case-specific evidence;
- `Possible reason` contains either a supported hypothesis or the explicit word
  `unknown`;
- uncertainty is stated when the visible evidence cannot distinguish causes;
- no causal claim is copied from `rank_pattern`; and
- `label` may remain blank.

This template aligns *how evidence is recorded*. It does not require both
reviewers to reach the same causal hypothesis.

## 6. Proposed sampling-manifest contract

### 6.1 Why a manifest is needed

Without a manifest, “review some Full@5 failures” is not reproducible. The two
reviewers could unknowingly use different cutoff logic, over-select memorable
cases, omit rare rank patterns, or duplicate work. The manifest freezes the
case list before interpretation begins.

### 6.2 Proposed columns

```text
protocol_version
sample_manifest_version
source_run_id
example_id
retriever
question_type
rank_pattern
review_criterion
cutoff_k
sample_role
primary_reviewer
blind_overlap
selection_stratum
selection_seed
```

Proposed meanings:

| Column | Meaning |
|---|---|
| `protocol_version` | Approved protocol version, for example `manual_failure_review_v1`. |
| `sample_manifest_version` | Immutable manifest identifier, for example `review_sample_v1`. |
| `source_run_id` | Exact failure-review run supplying the cases. |
| `example_id`, `retriever` | Unique review-unit key. |
| `question_type`, `rank_pattern` | Mechanical sampling strata. |
| `review_criterion`, `cutoff_k` | Exact eligibility rule, for example `full_evidence_recall`, `5`. |
| `sample_role` | `calibration` or `main`; overlap remains a subset of the main sample. |
| `primary_reviewer` | Person responsible for the first independent note. |
| `blind_overlap` | `true` when both people must independently review the unit. |
| `selection_stratum` | Frozen stratum label used by the sampler. |
| `selection_seed` | Recorded deterministic seed. |

### 6.3 Proposed generation procedure

1. Validate the source run and join every eligible review unit to its exact
   `(example_id, retriever)` rank-pattern row.
2. Apply the approved criterion and cutoff mechanically.
3. Assign each eligible unit to the approved sampling stratum.
4. Sort deterministically before any seeded sampling.
5. Apply the approved rare-stratum and common-stratum quotas.
6. Select calibration and blind-overlap units according to the approved rules.
7. Validate unique keys, exact quotas, allowed vocabularies, and deterministic
   reproduction.
8. Write the manifest before manual notes begin. If the sample changes later,
   create `v2`; do not silently rewrite an in-use `v1`.

The manifest generator is mechanical infrastructure. It must not inspect or
predict a causal failure reason.

## 7. Calibration procedure

1. Freeze the draft notes template and choose the agreed number of calibration
   units from the manifest.
2. Xin and Jiajun review every calibration unit independently and do not read
   the other person's notes first.
3. Compare the notes field by field:
   - Did both identify the same missing gold evidence?
   - Did both cite concrete retrieved titles/ranks?
   - Did either make a causal claim unsupported by the visible evidence?
   - Did both distinguish observation from hypothesis?
   - Did both record uncertainty where appropriate?
4. Classify each disagreement using Section 8.
5. Revise the template or instructions when the disagreement exposes an
   ambiguous rule.
6. Repeat a smaller calibration round if the revision was material.
7. Freeze the protocol commit and main sampling manifest only after both people
   can apply the rubric consistently.

Calibration success is not “identical prose.” It means both notes meet the same
evidence standard and any remaining causal difference is explicit and
understandable.

## 8. Disagreement and drift procedure

Classify overlap disagreements as:

| Type | Example of the issue | Resolution |
|---|---|---|
| Factual | Different missing-gold title or rank recorded | Re-check the source artifact and correct the factual error. |
| Evidence sufficiency | One note cites concrete output evidence; the other is vague | Apply the completeness rule and revise the incomplete note. |
| Causal hypothesis | The same evidence supports different plausible explanations | Preserve both hypotheses or mark uncertainty; do not force a label. |
| Protocol ambiguity | The written instructions reasonably permit incompatible handling | Revise the protocol, version the change, and decide whether affected cases need re-review. |
| Reviewer drift | A reviewer applies a previously agreed rule differently later | Recalibrate on a small shared set and revisit affected cases if necessary. |

During notes-first open coding, do not use label agreement as the sole quality
measure. First check factual and evidence-template agreement. After the team
freezes a candidate codebook, both reviewers may independently label a separate
overlap set and report simple agreement plus an appropriate chance-corrected
measure if the label structure supports it.

Keep an adjudication log containing the case key, disagreement type, decision,
rationale, protocol version, and whether earlier cases require re-review. Do not
overwrite the original independent notes before the comparison is recorded.

## 9. Questions that must be answered before HTML implementation

The coding contract cannot be frozen until Q1–Q18 are resolved. In addition,
confirm that the HTML implementation will:

- show the protocol version, sampling-manifest version, review criterion, and
  cutoff;
- strictly join the selected unit to `gold_rank_patterns.csv` by
  `(example_id, card_retriever)` and fail on missing, duplicate, extra, or
  provenance-inconsistent data;
- display canonical and human-readable `rank_pattern` as read-only context;
- make notes visually primary and labels optional;
- count empty label plus non-empty notes as annotated everywhere, including
  autosave, progress, “unannotated” filtering, import, export, and round trips;
- never prefill a causal label;
- preserve the accepted eight-column annotations CSV unless Q15 approves a
  versioned schema change;
- prevent one reviewer from seeing the other's blind-overlap notes before both
  submit, or define a manual process that guarantees the same separation;
- preserve the accepted any-based report when the new criterion is not selected;
  and
- test the approved criterion, cutoff, sampling/provenance display, strict join,
  notes-only annotation behavior, and backward-compatible import/export.

## 10. Agreement and approval record

### 10.1 Decision log

| Date | Protocol version | Questions changed | Decision and rationale | Requires re-review? |
|---|---|---|---|---|
| OPEN | draft | OPEN | OPEN | OPEN |

### 10.2 Reviewer approval

| Reviewer | Responsibilities | Approved commit | Date | Approval |
|---|---|---|---|---|
| Xin | Dense primary review; shared calibration, overlap, taxonomy decisions | OPEN | OPEN | OPEN |
| Jiajun | BM25 primary review; shared calibration, overlap, taxonomy decisions | OPEN | OPEN | OPEN |

### 10.3 Design exit gate

Before changing this document to `status: active` and DR-003 to
`design-approved`, verify:

- [ ] Q1–Q18 have decisions and rationales.
- [ ] The exact notes template and completeness rule are frozen.
- [ ] The criterion, cutoff, sample size, strata, quotas, and seed are frozen.
- [ ] Calibration cases have been reviewed independently by both people.
- [ ] Calibration disagreements and resulting protocol edits are recorded.
- [ ] Blind-overlap count/proportion and adjudication process are frozen.
- [ ] Annotation and sampling provenance are reproducible.
- [ ] Both reviewers approve the same Git commit.
- [ ] The AI session log records any agent assistance used to scaffold or
      implement mechanical infrastructure.

Only after this exit gate is met should a coding agent receive the HTML and
sampling-manifest implementation prompt.
