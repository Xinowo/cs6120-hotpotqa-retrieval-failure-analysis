---
status: active
last_updated: 2026-08-13
---

# Manual review v1 -- open-coding and decision memo

How the 30 labels in `results/annotations/manual_review_v1/final_labels.csv` were
produced: what was reviewed, by whom, in what order, which decisions were taken
along the way, and what those decisions forbid anyone from claiming afterwards.

This memo is the process record. The category definitions are in
`docs/taxonomy_candidate_v0_1.md`; the counts are in
`results/annotations/manual_review_v1/category_counts.csv`. The governing
specification is `docs/specs/2026-07-27-manual-failure-review-course-protocol.md`.

## 1. What was reviewed

One read-only formal run, `2026-07-17_a`, two retrievers, evaluated cutoff 5. The
batch contains only **strict Any@5 failures**: neither gold title appears in the
first five retrieved results for that `(example_id, retriever)` unit.

The eligible strict Any@5 population, recomputed from the run's `details.jsonl`:

| Retriever | Bridge eligible | Comparison eligible |
|---|---:|---:|
| BM25 | 51 | 12 |
| Dense | 16 | 3 |

The frozen batch drawn from it, exactly 30 unique units:

| Retriever | Bridge | Comparison | Total |
|---|---:|---:|---:|
| BM25 | 12 | 3 | 15 |
| Dense | 12 | 3 | 15 |
| Total | 24 | 6 | 30 |

Dense has exactly three strict Any@5 comparison failures, so that stratum's draw
is the whole stratum.

**Selection was frozen as an algorithm, not as a seed.** "Seeded with 6120" is not
a specification: on the 51 sorted BM25 bridge ids, drawing 12 with `sample` and
shuffling then slicing the first 12 are both ordinary readings of that phrase, and
they select disjoint sets. The protocol therefore fixes the steps literally --
partition by `(retriever, question_type)`, sort ids by ascending code point, create
a **fresh** `random.Random(6120)` per stratum, draw with `rng.sample`, sort the
draw, and concatenate the strata in one fixed order. Repeat generation reproduces
the selected key set, the overlap key set and the ordering exactly, and
`tests/test_build_manual_review_batch.py` holds both halves of the paired controls
for that.

**The unit of analysis is `(run_id, example_id, retriever)`.** The same question
under BM25 and under Dense is two units, because the evidence and the conclusion
can differ on each. One question in this batch is exactly that case and is worked
through in `docs/manual_review_v1_failure_analysis.md`.

## 2. Who reviewed, and the workload

Two reviewers, 17 units each, **34 review actions over 30 unique units**. Four of
the 30 were deliberately assigned to both:

| Retriever | Bridge overlap | Comparison overlap | Total |
|---|---:|---:|---:|
| BM25 | 1 | 1 | 2 |
| Dense | 1 | 1 | 2 |
| Total | 2 | 2 | 4 |

Order of work, per the protocol: both reviewers independently reviewed the four
overlap units first, neither reading the other's notes before saving that pass;
the four pairs were then compared to calibrate the evidence and note rubric; each
reviewer then completed their 13 private units under the calibrated rubric.

**Overlap is a consistency check on note quality and interpretation.** It is not an
agreement statistic, not a majority vote, and not a requirement to use identical
prose. Both original notes are retained for every overlap unit; nothing was
overwritten to make them agree.

**The 34 is workload, not prevalence.** Reviewer row counts may be reported as
workload or overlap evidence and never as category prevalence. The denominator for
every count is the 30 unique units.

## 3. The derivation chain, and its direction

Five artifact states exist and may not be collapsed into one another:

| State | Where it lives | Status |
|---|---|---|
| Raw notes, retained verbatim | the `note_xin`, `note_jiajun` and `joint_review_notes` columns of `results/annotations/manual_review_v1/case_memos_v2.csv`, exported by the reviewers as `<reviewer>_notes.csv` | Read-only source. Never rewritten, never paraphrased into evidence |
| Provisional open codes | that file's `primary_open_code` and `secondary_open_codes` | Jointly reviewed but provisional comparison handles, not categories |
| Legacy routing hint | that file's `candidate_category` | 29 cells mirror the then-current primary and 1 is blank. **Not** a candidate mapping and not evidence that a taxonomy exists. It may not prefill any mapping |
| Candidate categories | `docs/taxonomy_candidate_v0_1.md` | Provisional categories with explicit boundaries; not final labels |
| Final labels | `results/annotations/manual_review_v1/final_labels.csv` | One label per unique unit |

**Direction of derivation, and nothing flows backwards:** notes to open codes to
candidate categories to a frozen taxonomy to final labels. A candidate category may
not be justified by the open code that happens to sit in a memo row, and the
presence of a name among a unit's secondary codes is never evidence for anything.

Two status fields say only what they say. All 30 units read
`analytic_status=jointly_reviewed_validated_revised`, which is a memo and open-code
state, and all 30 read `review_status=jointly_reviewed`, which is joint-review
completion. Neither is evidence that a category applies.

## 4. The four double-reviewed units and how each was resolved

Each of the four carries an owner decision that **chose between competing readings**
after both notes were read. That is why `resolution` reads `overlap_resolved` and
not `overlap_agreed` on the three that reached a named category: the value records
a resolution, not a coincidence of wording. If the owners later judge any of them a
plain agreement, that row's `resolution` becomes `overlap_agreed` and nothing else
changes.

**`5a78b209554299148911f93e|bm25`** -- "Which playwright lived a longer life,
Edward Albee or J. M. Barrie?" The competing readings were an entity-name
tokenization mismatch and one-sided crowding by Albee-related documents. Resolved
in favour of the tokenization mismatch: the reviewed BM25 implementation indexes
paragraph text but not titles and tokenizes by lowercase whitespace splitting only,
with no punctuation normalization, phrase matching or initial expansion, so the
query tokens `j.`, `m.` and `barrie?` cannot meet the gold text's `james`,
`matthew` and `barrie,`; `J. Edward Snyder` at rank 15 matches `j.` from one queried
entity and `edward` from the other. The Albee cluster at ranks 1 to 8 was retained
as a downstream ranking effect rather than promoted to the cause. Final label:
`bm25_minimal_preprocessing_score_distortion`.

**`5a7d61775542991319bc93b9|bm25`** -- the Bharatpur unit. Competing reading was
query-facet fragmentation. Resolved in favour of implementation-induced score
distortion, on an exact score reconstruction: in the pinned `rank-bm25` version
`get_scores` iterates over every query-token occurrence, so the four occurrences of
`of`, two of `the` and two of `commander-in-chief` each accumulate repeatedly --
rank 3 `Siege of Bharatpur (1805)` draws 23.07 of its 41.85 points from `of` and
`the` alone and does not match the query token `bharatpur,`. Facet fragmentation was
kept as the closest competitor and observable pattern. Final label:
`bm25_minimal_preprocessing_score_distortion`.

**`5a83aaeb5542996488c2e483|dense`** -- the `Graduation` unit. Competing reading was
same-artist work crowding. Resolved in favour of an evaluation-side finding:
`Graduation (album)` ranks 1 and, under the same reading of the Roc-A-Fella relation
the annotated chain itself uses, satisfies every explicit question constraint in one
passage, with the annotated golds at 6 and 7. Per-question Dense results also rank
it first, which proves it was one of the item's original HotpotQA distractors rather
than a passage introduced by pooling 500 questions. Crowding explains why other
albums outrank the golds but cannot invalidate a complete alternative answer. Final
label: `evaluation_side_gold_chain_ambiguity`.

**`5a76387d554299109176e6ba|dense`** -- "who was born first" over Am Rong and Ava
DuVernay. Both reviewers observed the same thing: Dense ranks the two golds at 26
and 27 while its top results emphasize generic person and birth-related content,
including a passage containing the phrase "born first". The decision retained
two-sided entity under-prioritization as the open code and recorded explicitly that
**the retrieved ranking does not establish which internal embedding or scoring
component caused the ordering**. That sentence is why this unit later failed the
crowding category's measured-intervention clause. Final label: `unresolved`, and
`resolution` reads `unresolved` rather than `overlap_resolved`, per the protocol's
rule that the outcome is one resolved category or one `unresolved` unit and never
two votes.

## 5. The decisions that bound what may be claimed

Every one of these was taken during open coding, before the categories existed, and
each constrains the report rather than the data.

| Decision | What it fixed |
|---|---|
| Cutoff sensitivity is secondary | Proximity to rank 5 records fragility and is never itself a causal explanation |
| **Counts are not prevalence** | Open-code counts may not be read as final taxonomy frequencies or population prevalence: the vocabulary is provisional, partly multi-label, and drawn from a bounded calibration corpus |
| **Do not freeze `taxonomy_v1` from this pass alone** | Owner review, constant comparison, clustering and boundary stress-testing are required before any freeze. This pass is evidence-preserving, not joint approval of stable categories |
| Rank shape is not a cause | One-sided against two-sided crowding is a description; corpus setting and retriever identity are never causal predicates |
| **The capability-boundary contract** | Every category carries eight fields, from closed value sets; a missing decisive counterfactual is recorded as `not_run` and caps claim strength at `observed`; unqualified "BM25 cannot ..." or "Dense cannot ..." claims are forbidden; comparison-retriever success alone can never strengthen a claim; a successful preprocessing or indexing repair keeps the conclusion at implementation level regardless of how many units share the symptom |
| The bounded-synthesis rule | Category work proceeds from the existing 30-unit evidence; no new general tooling or unbounded vocabulary work unless one named category boundary is demonstrably blocked by missing evidence |
| The oracle-name ruling | Supplying a required passage's own name is oracle evidence: it supports a reading, never establishes one, is outranked by any deployable measurement, and its absence vetoes nothing |
| The gold-targeted diagnostic ruling | An intervention that adds no text but requires knowing which passage is gold is admissible for a mechanism and is **never** a deployable repair, so it can never license an implementation-level conclusion |
| The minimum-evidence correction | Exactly two named evidence gaps exist, both under one category, and exactly one of them is an actionable request |

Each of these is one entry of the append-only decision log at
`docs/manual_review_v1/open_code_decision_log.md`, which holds them in full with
their per-unit evidence; entries are cited as `D-0nn` and open triage items as
`T-nn`, the latter in `docs/manual_review_v1/vocabulary_audit_triage.md`. In order,
the rows above are D-006, D-007, D-008, D-003 with D-010, D-062, D-062's
bounded-synthesis clause, D-041 with D-044 to D-047, D-063's ruling on the
gold-targeted class, and D-064.

## 6. The two `unresolved` units

Both were reviewed. `unresolved` records missing **counterfactual evidence**, not
missing review, and the two fail on different predicates, which is why each is
recorded per unit rather than pooled.

`5a76387d554299109176e6ba|dense` -- double-reviewed, two notes plus a joint note. A
competing family is stated as passage content, but no intervention of any kind was
measured on the unit, and the owner decision records that the ranking does not
establish the cause. The crowding category's measured-intervention clause fails.

`5a7d19d85542995ed0d165e8|dense` -- one reviewer's note plus a joint note. The
family rule that picks out the crowding neighbourhood -- Tennessee Volunteers season
and statistical passages -- also selects one of the required passages, the `1984`
season article itself, so the family cannot be removed even in principle and the
claim is untestable by any intervention. No controlled ablation was run.

Reaching `unresolved` twice is a property of writing positive inclusion rules. A
rule set that had to guess in order to avoid `unresolved` would be the incomplete
one.

## 7. What this memo does not do

- It does not freeze the taxonomy, and it approves no category name.
- It adds no decision of its own and changes no unit's label.
- It reports no prevalence, and no count in it has a denominator other than 30.
- It makes no claim about BM25 or dense retrieval as families. Every conclusion is
  scoped to one pooled run, one deliberately minimal bag-of-words BM25
  implementation with titles excluded from the index, and one symmetric
  `all-MiniLM-L6-v2` bi-encoder with mean pooling, L2 normalization, a 256-token
  window and no reranking.

## 8. Authorship boundary

Stated so the report's AI-usage declaration can be specific.

**Human-authored research content:** the 34 review notes and every joint note; the
open codes and their definitions; every decision entry and its per-unit evidence;
the category definitions, boundaries, required evidence, examples and
counterexamples; the capability-boundary contract and the selection order; and the
30-unit label assignment those rules produce.

**Agent-assisted supporting work:** the transcription of the landed labels into
`final_labels.csv`; the transcription and compression of the category definitions
into `docs/taxonomy_candidate_v0_1.md`; this memo and the qualitative analysis
document, written from landed text; and the counting plumbing in
`scripts/reporting/manual_review_category_counts.py` with its tests, which defines
no category and judges no unit.
