---
status: draft
last_updated: 2026-08-13
---

# Candidate Failure Taxonomy v0.1

**This document is not frozen.** It is the Section 14 candidate taxonomy for the
`manual_review_v1` HotpotQA retrieval-failure review. Every category name in it is a
**candidate** name, every boundary value is provisional, and no unit carries a final label
because of anything written here. The frozen artifact is `taxonomy_v1.md` at Section 21, and
`final_labels.csv` at Section 22; neither exists.

## 0. Purpose, mode and authority

**Purpose.** To state, in one place and in operative form, the six candidate categories that
D-063 landed, the ordered rule that assigns a candidate primary, the rules for compound units,
`unresolved` units and taxonomy defects, and the capability boundary each category may and may
not claim. Section 16 will apply this document to all 30 units; Sections 17 to 20 will stress
its boundaries and decide whether it may be frozen.

**Mode: transcription, not analysis.** This document is written from the six landed category
contracts and the landed compound / `unresolved` rules. No unit was re-analysed, no raw note or
open code was re-read for a new judgement, no retrieval measurement, ranking, corpus sweep or
score computation was run, and no prior decision was re-worded. Where a figure appears it is
carried from the decision that measured it, named inline.

**Authority order.** Frozen protocol and owner decisions first, then this document's own
governing decisions, then evidence artifacts, then tools. In detail:

1. `open_code_decision_log.md`, D-001 to D-063, append-only. A ruling lives there; a document
   that merely restates it has no independent authority. Where this document and a landed
   D-entry disagree, the D-entry wins and the disagreement is a defect in this document.
2. D-062, the capability-boundary contract, which fixes the eight per-category fields, the four
   `failure_layer` values, the four boundary values and the three claim strengths.
3. D-063, which landed the six candidate categories, the seven-step selection order, the
   clause-two discharge procedure, the four Section 13 rulings and the compound-case rule; and
   D-064, which corrects prospectively how D-063 attributes the named minimum-evidence items and
   governs that one point wherever the two disagree.
4. `case_memos_v2.csv`, the 30-row joint-review evidence table, whose open codes remain
   provisional; `secondary_descriptor_registry.md`; `per_case_analysis/` dossiers.
5. `tools/recount.py`, whose ordinal-series membership tables are authoritative for series
   counts wherever a prose tally in another file disagrees with them.

**What this document may not be read as doing.** It creates no mapping, closes no triage item,
grants no gate and freezes nothing. See section 20.

## 1. Analysis corpus scope

- One read-only formal experiment run, `2026-07-17_a`, two retrievers, BM25 and Dense, with the
  evaluated cutoff fixed at 5.
- Corpus: the 4,937-passage pooled corpus, formed by merging and de-duplicating the passage sets
  of 500 questions.
- BM25: one deliberately minimal bag-of-words implementation, titles excluded from the index, no
  stemming and no standard normalization.
- Dense: one symmetric `all-MiniLM-L6-v2` bi-encoder, mean pooling over the whole passage, L2
  normalization, a 256-token window, no reranking and no cross-passage reasoning.
- Two human reviewers wrote 17 notes each, 34 review actions in total; 4 cases overlap, so the
  corpus contains **30 unique analytical units**, 15 BM25 and 15 Dense, over 24 bridge and 6
  comparison questions.
- 19 of the 30 units carry a `per_case_analysis/` dossier; 11 do not and carry no factorial.
  That batch is item T-56 and every predicate satisfied by an enumerated match set rather than
  by a measured rank effect falls on it.

**Consequence for every claim in this document.** This base supports bounded, setup-scoped
conclusions about the evaluated implementations. It supports no claim about BM25 as a family or
about dense retrieval as a family, and the 30 open-code counts are not prevalence estimates.

## 2. Analytical unit

A unit is one `(run_id, example_id, retriever)` triple. The **full unit key** used everywhere in
this document is `<example_id>|<retriever>`, where `example_id` is 24 lowercase hex characters
and `<retriever>` is `bm25` or `dense`; `run_id` is constant at `2026-07-17_a` and is therefore
not repeated in the key.

The same `example_id` under BM25 and under Dense is **two different units**. A bare `example_id`
is not a unit and may not appear in any `supporting_units` field, because it silently pools two
units whose evidence and whose assignment can differ. One `example_id` in this sample is exactly
that case: `5a78b209554299148911f93e|bm25` is a K1 member and `5a78b209554299148911f93e|dense`
is a K4 member.

## 3. Analytical layering

**Five** artifact and lifecycle states exist and may not be collapsed into one another. The
count is the number of data rows in the table below and is checked against them in section 21.
Four of the five are artifacts of the notes-first derivation chain; the fifth, the legacy
routing hint, sits outside that chain and derives nothing. This five is **not** D-062's separate
four-value `failure_layer` vocabulary, which classifies a category's cause rather than an
artifact, and the two counts may not be read as the same four.

| State | Artifact | Status |
|---|---|---|
| Raw notes, retained verbatim | `note_xin` and `note_jiajun` in `case_memos_v2.csv`; `xin_notes.csv`, `jiajun_notes.csv` | Read-only source under red line 1. Never rewritten, never paraphrased into evidence |
| Provisional open codes | `primary_open_code`, `secondary_open_codes` | Jointly reviewed but provisional comparison handles, not categories |
| Legacy routing hint | `candidate_category` in `case_memos_v2.csv` | 29 cells mirror the then-current primary and 1 is blank. **Not** a candidate mapping and not evidence that a taxonomy exists. It may not prefill any mapping (D-062) |
| Candidate categories | this document | Provisional categories with explicit boundaries; not final labels |
| Final labels | `final_labels.csv`, Section 22 | Does not exist |

Two further status fields say only what they say: all 30 `analytic_status` cells read
`jointly_reviewed_validated_revised`, which is a memo and open-code state, and all 30
`review_status` cells read `jointly_reviewed`, which is joint-review completion. Neither is
evidence that a category applies.

**Direction of derivation.** Notes-first grounded coding: notes → open codes → candidate
categories → frozen taxonomy → final labels. Nothing flows backwards. A candidate category may
not be justified by the open code that happens to sit in a memo row, and the presence of a name
in `secondary_open_codes` is never evidence for anything (section 4).

## 4. Evidence typing

Only four kinds of fact may satisfy a predicate anywhere in this document.

- **E1, deployable measurement.** An intervention measured on that unit that needs no knowledge
  of which passages are gold.
- **E2, oracle measurement.** An oracle intervention, readable only through the clauses D-041
  sets and D-044 to D-046 condition, and outranked by any E1 result under pit 15.
- **E2b, gold-targeted diagnostic.** An intervention that adds no text and injects no answer
  information but requires knowing which passage is gold or which passages are rivals: the
  controlled content ablation with its equal-length control, and index-side family-removal
  probes. Standing, as ruled by D-063: admissible as evidence for a mechanism; **never** a
  deployable repair, so it can never trigger D-062's implementation clause and can never produce
  `implementation_recoverable`; outranked by any E1 result under pit 15; and unable to refuse a
  category under D-040, only to limit confidence.
- **E3, verified content rule.** A rule over passage text checked against the 4,937-passage
  pooled corpus.

**Never predicates**, in any step, include rule, exclude rule or tie-break:

1. rank shape and rank position, including one-sided against two-sided crowding (pit 17, D-003,
   D-043 clause one);
2. distance from the cutoff. D-042 gives it a threshold as a *descriptor*,
   `cutoff_sensitive_near_miss`, never as a mechanism;
3. corpus setting and retriever identity (D-003, D-062);
4. the mere presence of a descriptor in `secondary_open_codes`, and likewise the mere fact that
   a gate passed somewhere on the unit.

**Evidence tiers**, used by the tie-break in section 12 and by the strength fields: `enumerated`
(a content property or an enumerated match set, no measured rank effect), `measured (E2)` or
`measured (E2b)`, `measured (E1)`, and `recovered` (a deployable condition placing every
required passage inside the evaluated cutoff).

## 5. The candidate primary-selection order

Applied in order. The first step whose include rules hold and whose exclude rules do not fire
assigns the candidate primary. If no step fires the unit is `unresolved`, which is step 7 and a
real destination rather than a formality.

### Step 1 — K6, evaluation-side answer ambiguity

*Include:* a non-gold passage **inside the evaluated cutoff** satisfies every explicit
constraint of the question in one passage, identified by passage id with its rank and score, and
the constraint the annotated gold satisfies and it does not is stated.

*Exclude:* the qualifying passage lies outside the cutoff; or it substitutes an **intermediate**
annotated passage rather than answering the question, which is `gold_chain_substitutability` and
stays a secondary; or it satisfies only part of the question.

*Why first:* if the annotation is not the only chain satisfying the question inside the cutoff,
the ranking behaviour is not a retrieval failure (D-005, D-060).

*Rejection case that must be refused:* `5adc8977554299438c868de2|bm25` has evidence-bearing
substitutes at ranks 1 and 4, inside the cutoff, and D-034 withheld even the cutoff descriptor
on that ground. They substitute an intermediate passage, so step 1 does not fire. It ends at K1.

### Step 2 — K1, evaluated lexical implementation artifact

*Include, both clauses:*

- (a) a named property of the evaluated lexical pipeline — how text is normalized before it is
  indexed, which field is indexed, or how repeated tokens score — is measured on this unit
  either as rank positions cost to a required passage under a deployable change (E1), or as an
  enumerated set of matched-token false negatives on a required passage against that passage's
  own text; and
- (b) no deployable change is measured with **opposite signs** across the two required passages,
  and D-051's reverse boundary does not fire on a required passage the claim covers.

*Exclude:* D-051 fires — the minimal gold-targeted normalization of a covered passage is worth 0
rank positions, or the corresponding corpus-wide deployable normalization has a negative score
effect. Or the repair is opposite-signed across hops. Or the positive control's gain is
attributable to a side effect rather than to the passage's own matchable content (pit 19am,
D-036's length-normalization side effect, D-039's amplification of an already-matchable anchor).

*Not satisfiable on Dense, by implementation fact rather than by rule.* D-029 records that no
tokenizer or indexing artifact exists on a bi-encoder that strips accents and case, and D-020's
condition A, removing the quotation marks around the epithet, is inert in both directions,
465 / 0.112206 to 479 / 0.111678 and 13 / 0.317347 to 12 / 0.318517. The Dense-side
implementation property is mean pooling, and it is step 3.

*Rejection cases that must be refused:*

- `5ade42b55542992fa25da717|bm25` — clause (a) holds, two surface-form false negatives on the
  bridge hop, and clause (b) fails: M moves the bridge hop 15 to 5 and the answer hop 8 to 16,
  and D-022 records that the answer hop has no surface-form mismatch to repair at all.
- `5ae057fd55429945ae959328|bm25` — clause (a) holds, `mills,` against `mills`, and clause (b)
  fails: P, boundary punctuation on both sides, is 18 / 19.470404 and 12 / 22.345811, negative
  for both, and D-024 states "no surface deficit to repair" and rejects the preprocessing
  primary in terms.
- `5ae60426554299546bf83019|bm25` — clause (b) fails on D-051: the answer passage's
  gold-targeted repair is worth 0 rank positions and the deployable version -0.024046 points.
- `5ab8f57b5542991b5579f097|bm25` — T is materially positive at 3 / 31.744369, and clause (b)
  fails: D-032 records the name-anchor reading repaired to its limit in three forms, reaching 6,
  4 and 6, "twice at the other required passage's expense", and states "Failure layer: method.
  Not implementation, because no preprocessing or indexed-field change alone recovers the pair".

### Step 3 — K5, mean-pooling content dilution

*Include, both clauses:*

- (a) the four-condition dilution gate is satisfied on a required passage — mean pooling
  verified from the implementation, a controlled ablation materially raises rank, an
  **equal-length** control ablation does not, and the passage does not hit the 256-token
  truncation. This is E2b evidence, whose standing section 4 fixes; and
- (b) the controlled ablation places **every** required passage inside the evaluated cutoff.
  This is the ceiling D-037 names as the first time the gate won a primary.

*Exclude:* the gate is rejected on any of its four conditions; or the gate passes but clause (b)
is not reached, in which case the name is a **secondary** and the unit routes on; or no
equal-length control exists, in which case the gate must not be applied at all.

*Rejection cases that must be refused:* `5ade69e455429975fa854ec5|dense` and
`5add67915542992200553af8|dense`, where the gate passes on both required passages and clause (b)
is not reached, so they route on and end at K2 with the descriptor as a secondary;
`5ae1801955429901ffe4aec4|dense`, where the gate passes on the constraint passage and fails on
the answer passage, so clause (b) fails and it ends at K3; `5ae0a59a55429945ae9593e2|dense`
(D-025) and `5ab48c325542996a3a969f93|dense` (D-031), where the gate is rejected outright.

*Legal control that must be accepted:* `5ae048a255429924de1b708e|dense` — gate passed, ablation
at 3 / 0.469751 and 1 / 0.549310, both required passages inside the cutoff.

### Step 4 — K2, description-only bridge entity

*Include, two clauses, both necessary and neither sufficient:*

- (a) a required entity is identified in the question by description and not by name, so the
  descriptor's first exclusion, that the target entity is explicitly named, does not fire. This
  is the registry's own include clause, which states the content property and nothing else; and
- (b) no E1 result on this unit is decisive for another category. Two shapes: a deployable
  condition places every required passage inside the evaluated cutoff, which steps 2 and 3
  already discharge by ordering; or a later step's include clauses are satisfied on this unit
  **on E1 evidence** — step 5's clauses (a) and (b), or step 6's shape C — in which case that
  deployable evidence outranks K2's under pit 15 and the unit routes on.

*Optional support.* A valid pass of the single-factor oracle-name test is **supporting evidence
for K2 and is never required for it**. What a pass does is raise a member's evidence tier from
`enumerated` to `measured (E2)` and supply the supporting leg of a tie-break at equal tier under
section 12. What it may never do is decide membership by its absence. The three oracle states
and their consequences are section 8, which is binding on this step.

*Exclude, and this list is exhaustive:* the question names the target entity, however
ineffectively — D-053 refuses to widen the name to that case and routes the residue instead. Or
the oracle result is a **valid failure** in the sense of section 8, in which case D-041's
binding half bars the primary and the descriptor stays a secondary. **`not_run` and
`not_applicable` are not on this list and no consequence anywhere in this document may be read
as putting them there.**

*Rejection case that must be refused:* `5a81ebee554299676cceb16d|dense`. The oracle-name test
passes there, five of seven forms recovering both required passages (D-046), and the unit is
still not K2, because the query carries the name, the required passage contains it and it is
unique in the 4,937-passage corpus, yet a query reduced to that name ranks the passage 2202 of
4,937 and the bare surname 4243 (D-029, D-053). Clause (a) fails and the unit routes on to step
6, where D-054 discharges D-043's clause two and it ends at K4.

*Second rejection case:* `5ae057fd55429945ae959328|bm25`. Clause (a) **holds** — D-024 states in
terms that the description-only reading "satisfies its inclusion rule, because the question
requires a specific company, designates it only as the multinational company Robert Smith
founded, and never names it" — and its oracle application is `not_applicable` under D-044, so no
bar fires. The unit is still not K2, and the ground is clause (b) rather than the absent pass:
step 5's clauses (a) and (b) are satisfied on E1 evidence, the two hops' matched query-token
sets sharing only `in` and 10 of 19 single factors carrying opposite signs, and under pit 15
that deployable evidence outranks anything K2 holds here.

*Precondition controls, one per state:* `5ade69e455429975fa854ec5|dense` is the
satisfied-and-passing control and enters K2 at `measured (E2)`; `5ab48c325542996a3a969f93|dense`
is the satisfied-and-failing control, where the bar fires and the unit reaches K3;
`5ae057fd55429945ae959328|bm25` is the failed-precondition control, where nothing is barred and
the unit reaches K3 on the stronger E1 evidence of step 5; `5a7d61775542991319bc93b9|bm25` is
the unrun control, where the descriptor is carried as a secondary, no bar exists, and the unit
ends at K1 because step 2 fires first. The adjacent state none of the four exercises — clause
(a) held, steps 1 to 3 silent, no competing E1 evidence, and the oracle unrun or uninterpretable
— lands **in K2 at the `enumerated` tier**, because on that state no rule in this document
refuses it.

### Step 5 — K3, unresolved cross-passage conjunction

*Include, clauses (a) and (b) required, (c) contributory:*

- (a) the required fact exists only as a conjunction spanning two passages: the intermediate
  name or fact is absent from the question and present only in the other required passage;
- (b) the two required passages' matched-evidence sets are near-disjoint, evidenced by an
  enumerated shared and unshared token split **and** by single factors carrying opposite signs
  across the two passages (E1); and
- (c) the conditioned oracle-name exclusion. Where every interpretable form fails under D-044 to
  D-046 this supports the step. Where the preconditions are not satisfied the application is
  `not_applicable`, contributes nothing, and (a) plus (b) carry the step at `observed` strength.

*Per-hop reachability.* Each required passage reaching the top of the ranking from its own name
alone is **supporting** evidence, not a necessary threshold; its measured negation is an
exclusion. That is D-063's ruling 1, which settles the item D-022 and D-024 registered, and the
ruling is verified against the one unit it could have moved: D-024's K1P places the answer hop
at 4 / 10.556421 inside the cutoff from its own bare name under one boundary-punctuation
normalization, against 51 for the unnormalized K1, so `5ae057fd55429945ae959328|bm25` holds
under either reading.

*Exclude:* an earlier step fired. Or the required passage is not reachable from its own
distinctive cue, so the obstruction is not the join but the cue itself. Or a
gold-knowledge-requiring condition is the only thing that refutes the step, which D-040 forbids
as a refusal ground and permits only as limiting confidence.

*Rejection case that must be refused:* `5ab978855542996be2020512|dense` carries
`cross_passage_conjunction_unresolved` as a secondary and its oracle-name test failed, so the
shape looks right. The exclude fires: D-059's probe D, which is not oracle, makes the query
exactly the verbatim epithet, and the one passage that literally contains it reaches only
106 / 0.219506, while the top five are a religious, mythological and death-related
neighbourhood; probe E, replacing the epithet with the plain noun `dwellings`, moves the
answer passage
13 / 0.317347 to 5 / 0.366752, showing the same cue suppressing the other side. It ends at K4,
sub-reading C.

### Step 6 — K4, near-neighbour crowding and sense drift

Positive include rules. `otherwise` is **not** one of them.

*Include, both clauses, in either of two shapes.*

Shape A/B, competing family:

- (a) the set of non-gold passages ranked above a required passage is stated as a rule over
  **passage content**, satisfying D-043 clause one, and that rule does not also select a
  required passage, which is D-043 clause two (E3); and
- (b) at least one intervention measured on this unit bears on that family — a removal or family
  probe, a complement or equal-length control, or a cue substitution that changes the family's
  composition (E1, E2 or E2b). Enumerating the family is not enough.

Shape C, sense drift:

- (a) a non-oracle cue-substitution probe measures the query cue resolving to a different sense
  neighbourhood than its source passage; and
- (b) a second non-oracle probe measures the same cue suppressing the other required passage.

*Exclude:*

- E1 — the family rule also selects a required passage (D-043 clause two). The family then
  cannot be removed even in principle and the claim is not testable by any intervention, so the
  unit does not reach K4 on that family.
- E2 — the competing set is stated as a rank range or a position (pit 17, D-003, D-043 clause
  one).
- E3 — an earlier step fired.
- E4 — no content family and no measured intervention. The unit is `unresolved`, **not** K4.

Plus D-055's passage-level boundary, restated in section 9.

*Clause two must be discharged*, in one of exactly three ways and in no other, searched in the
order section 9 gives. Entering K4 with clause two neither ruled, discharged nor routed is
forbidden, and "not checked" is not a pass. Shape C carries no clause-two obligation, D-043
governing crowding-family descriptors and `verbatim_epithet_sense_drift` not being one.

### Step 7 — `unresolved`

Reached in two ways, and only these two: no step fires, including step 6's E4; or two
categories' include rules are satisfied at the same evidence tier and section 12's tie-break
does not separate them. See section 11.

## 6. The six candidate categories

Each category below carries D-062's eight fields, stated with those exact field names, followed
by the nine-component judgement contract: definition, required observable evidence, inclusion
rules, exclusion rules, closest competing category, tie-break rule, at least two positive
examples, at least one counterexample, and known limitations.

`supporting_units` is the evidence set the capability boundary rests on, given as full unit keys
per D-062. It is stated as a bare enumeration and nothing else. The **primary-label unit
count**, which is the disjoint partition a candidate mapping would carry, is stated separately
below each field block because it is not one of the eight fields; the two differ for K5 only, 7
against 1.

The eight fields are written as labelled lines rather than as a table cell, deliberately: a full
unit key contains `|`, which a Markdown table cell must escape, and an escaped key is not the
key.

---

### K1 — `bm25_minimal_preprocessing_score_distortion`

- **`failure_layer`:** `implementation`
- **`retriever_scope`:** `BM25`
- **`BM25_capability_boundary`:** `implementation_recoverable` — recovery in full is measured on
  two units, `5a79b7f6554299029c4b5f6f|bm25` (D-028) and `5a83880e554299123d8c214e|bm25`
  (D-030); on the other eight the implementation mechanism is measured and explains the score
  deficit while no tested non-oracle condition restores the full chain, so recoverability is
  established for the mechanism and not for every unit's metric outcome.
- **`Dense_capability_boundary`:** `not_applicable` — no tokenizer, normalization or
  indexed-field artifact exists on the evaluated bi-encoder, which strips accents and case
  (D-029). This rests on a property of the backend, **not** on the fact that all ten primary
  uses are BM25; that distinction is the `not_applicable` discipline in section 7.
- **`supporting_units`:** 10, all BM25: `5a78b209554299148911f93e|bm25`,
  `5a79b7f6554299029c4b5f6f|bm25`, `5a7c9f325542990527d554e6|bm25`,
  `5a7d61775542991319bc93b9|bm25`, `5a83880e554299123d8c214e|bm25`,
  `5a83a532554299334474606f|bm25`, `5ab72a025542992aa3b8c7b8|bm25`,
  `5abcc96c5542996583600492|bm25`, `5ac1a3665542994ab5c67daf|bm25`,
  `5adc8977554299438c868de2|bm25`
- **`decisive_counterfactual`:** run. D-030: a single non-oracle query-side token change
  recovers both hops, with eleven non-oracle conditions placing both required passages inside
  the cutoff, and the possessive token `suicide's` occurring in 0 of 4,937 passages whose
  deletion reproduces the ranking bit for bit at 0 order mismatches. D-028: every condition
  recovering both hops contains both P, boundary punctuation, and T, title indexing, both
  non-oracle.
- **`claim_strength`:** `implementation_supported`
- **`non_claims`:** No method-level claim about BM25 or about lexical retrieval as a family.
  Nothing is claimed about analyzers performing standard normalization, stemming or title
  indexing; D-022's own boundary forbids claiming that any deployable analyzer would recover a
  case. The 9-unit concentration of one name reflects one deliberately minimal implementation,
  not a property of BM25. Recovery in full is demonstrated on two units; on
  `5ab72a025542992aa3b8c7b8|bm25` (D-019, best complete chain 1 / 6) and
  `5abcc96c5542996583600492|bm25` (D-033, `any@5` flips, `full@5` does not) no non-oracle
  condition achieves it, so those units are covered by the category and do not carry the
  recovery claim. Five of the ten units have no dossier and no factorial, so their evidence tier
  is `enumerated` or `measured`, never `recovered`.

**Primary-label units:** the same 10.

**Definition.** A required passage is pushed below the evaluated cutoff because of a named
decision in the evaluated lexical pipeline — how text is normalized before it is indexed, which
field is indexed, or how repeated tokens score — and not because of what the corpus contains or
what the question asks.

**Required observable evidence.** (i) The pipeline decision named and verified from the
implementation reference, not inferred. (ii) Either a deployable change measured on the unit
with its rank effect on each required passage, or an enumerated set of matched-token false
negatives between the query and a required passage's own text. (iii) An exact baseline
reconstruction, so the decomposition is attributable.

**Inclusion rules.** Step 2's clauses (a) and (b) of section 5, in full.

**Exclusion rules.** D-051's reverse boundary — 0 rank positions for the minimal gold-targeted
normalization of a covered passage, or a negative corpus-wide deployable score effect — judged
per required passage, with an unrun cell recorded `not_applicable`. An opposite-signed repair
across the two required passages (D-022). A positive control whose gain is a side effect rather
than the passage's own matchable content (pit 19am, D-036 and D-039). And, by D-049's scoped
naming line, a further value of an already covered normalization decision does not warrant a new
name inside this category.

**Closest competing category.** K4, on the lexical side. Secondarily K3 on bridge units.

**Tie-break.** Against K4: D-055's passage-level boundary — prefer K1 when the score deficit
decomposes onto a named normalization or index-field decision acting on the required passage's
own matchable content, and K4 when a content-defined competing family is the measured driver.
Against K3: prefer K3 when the deployable repair is opposite-signed across the two required
passages or when D-051 fires (D-022, D-024, D-039).

**Positive examples.** `5a83880e554299123d8c214e|bm25` — D-030's non-oracle double recovery,
eleven conditions placing both required passages inside the cutoff.
`5a79b7f6554299029c4b5f6f|bm25` — D-028's P-and-T interaction, the only coinage on the far side
of D-049's separability line.

**Counterexamples.** `5ade42b55542992fa25da717|bm25`: two surface-form false negatives on the
bridge hop are measured and real, and M moves that hop 15 to 5, yet the same factor drives the
answer hop 8 to 16 and the answer hop has no surface-form mismatch to repair at all. D-022
refused this primary and retained the evidence through the narrower secondary. Second:
`5ae057fd55429945ae959328|bm25`, where P is negative for both required passages at
18 / 19.470404 and 12 / 22.345811.

**Known limitations.** Five of the ten units have no dossier and no factorial (T-56), so on
those the mechanism is enumerated rather than measured as a rank effect, and D-051's two cells
have been measured on none of that batch. T-63, the boundary between
`entity_name_tokenization_mismatch` and `surface_form_tokenization_mismatch`, is open. D-058's
fold of `entity_name_tokenization_mismatch` into `minimal_preprocessing_score_distortion` stays
conditional on D-051's cells, so this category deliberately carries **two** primary names and
its category name must not be read as having performed that merge. D-050 keeps
`unindexed_title_name_anchor` outside the merged primary, so the index-field half of D-028's
interaction is carried by a separate secondary.

---

### K2 — `description_only_bridge_entity`

- **`failure_layer`:** `method`
- **`retriever_scope`:** `Dense` — **observational** under D-062, recording that all four
  primary uses fall on the bi-encoder. It is not a cause and, as the next field states, not a
  backend boundary.
- **`BM25_capability_boundary`:** `not_established` — D-047 makes the descriptor a property of
  the question and the required passage, measurable the same way on both backends, and its scope
  line is provenance that must not be read as scoping the descriptor to one backend. The
  descriptor is applicable on BM25 and is in fact carried there: `case_memos_v2.csv` puts it in
  `secondary_open_codes` on seven BM25 units — `5a79b7f6554299029c4b5f6f|bm25`,
  `5a7d61775542991319bc93b9|bm25`, `5ac1a3665542994ab5c67daf|bm25`,
  `5adc8977554299438c868de2|bm25`, `5ade42b55542992fa25da717|bm25`,
  `5adf58f15542993a75d264d2|bm25` and `5ae057fd55429945ae959328|bm25`. What is missing is a BM25
  **primary** use and therefore any BM25 evidence base for a boundary claim, and missing
  evidence is `not_established`, not inapplicability.
- **`Dense_capability_boundary`:** `not_established` — the only control the category's four
  members carry is an oracle injection, and an oracle result cannot carry a method boundary: it
  is outranked by any deployable result under pit 15 and establishes nothing on its own (D-041).
  This is a statement about what a pass can support, not about what membership requires: under
  section 8 a member may carry no pass at all, and such a member would supply even less boundary
  evidence than these four.
- **`supporting_units`:** 4, all Dense: `5a85cead5542991dd0999ea9|dense`,
  `5add67915542992200553af8|dense`, `5ade69e455429975fa854ec5|dense`,
  `5ae1f596554299234fd04372|dense`
- **`decisive_counterfactual`:** run and valid on 4 of 4, as optional support and not as a
  membership condition. The single-factor oracle-name test passes on all four with both D-044
  and D-045 preconditions satisfied: D-017 one form giving 1 / 2; D-023 five forms all giving
  1 / 3; D-026 seven forms; D-035 five forms, `Philadelphia` alone giving 1 / 0.554958 and
  2 / 0.499144. That all four members happen to carry a pass is provenance about this four-unit
  sample, not a rule: under D-041 the pass supports without establishing, is outranked by any
  deployable result under pit 15, bars nothing, and is never required, so a fifth member whose
  oracle state were `not_run` or `not_applicable` would be a legal member at the `enumerated`
  tier. Title-indexing T is inert or negative on 3 of the 4 and was not measured on
  `5a85cead5542991dd0999ea9|dense`.
- **`claim_strength`:** `observed`
- **`non_claims`:** No claim that a dense retriever cannot resolve descriptions to entities.
  **No claim that the mechanism cannot arise on BM25**, and no inference from the absence of a
  BM25 primary use to a BM25 boundary of any kind: `retriever_scope=Dense` is where the primary
  uses landed, not where the mechanism can occur (D-047, D-062). The oracle criterion was used
  by D-021 and D-023 to assign this primary, so the separation between this category and K3 is
  partly definitional and is not independent confirmation. A passing test establishes nothing on
  its own and is not required: it is outranked by any deployable result under pit 15, it bars no
  competing category, and four passing applications outside this category — D-028, D-029, D-036
  and D-037 — landed in K1, K4, K6 and K5 respectively. No claim is made that a pass is
  sufficient, none that it is necessary, and none that an unrun or uninterpretable test is
  evidence against the mechanism; the absence of a pass is the absence of support and nothing
  else. The dilution gate also passes on 3 of the 4 units, so a co-mechanism is present even
  though the oracle pass shows naming overcomes it. No comparison-retriever success is used to
  strengthen anything.

**Primary-label units:** the same 4.

**Definition.** A required entity is identified in the question by description rather than by
name, and reaching the required passages depends on resolving that description to the name,
which the evaluated retrieval stage does not do. Where the single-factor oracle-name test has
been run and passes, it is the direct observation of that dependence — supplying the name brings
both required passages inside the cutoff — and it is recorded as the category's supporting
evidence. It is support and not part of the definition, because D-041 wrote the passing half "as
support rather than as an inclusion condition" and the registry's include clause states only the
content property.

**Required observable evidence.** (i) The question text, showing the entity described and not
named. (ii) The unit's oracle state **typed and recorded**, as one of the three states section 8
defines. What is required is the typing, not any particular value: a valid failure excludes the
unit, a valid pass supports it, and `not_run` or `not_applicable` does neither, so recording the
state is what keeps the reader from inferring the wrong one. (iii) Where a form was run: the
form itself, from D-046's form set — one surface form of a required passage's own entity name,
injected alone — with the pit 19g and pit 24b preconditions verified for that form, and the rank
and score of each required passage under it. (iv) A statement that no deployable condition
places every required passage inside the cutoff, and that no later step's include clauses are
satisfied on this unit on E1 evidence.

**Inclusion rules.** Step 4's clauses (a) and (b) of section 5, both necessary and neither
sufficient: the content property, and no E1 result on the unit decisive for another category.
**A valid oracle pass is not an inclusion rule.** It is optional supporting evidence which,
where present, raises the member's evidence tier and can supply the supporting leg of a section
12 tie at equal tier; where the oracle state is `not_run` or `not_applicable`, nothing is
inferred in either direction and membership turns on (a) and (b) alone.

**Exclusion rules.** The question names the target entity, however ineffectively — D-053 refuses
the widening and routes the residue to `surface_form_tokenization_mismatch`,
`entity_alias_reference_mismatch`, `proper_name_homonym_collision`, or
`peripheral_passage_content_dilution` where that entry's four inclusion conditions hold; where
no route carries it the fact is recorded without a descriptor. A **valid failure** — both
preconditions verified and holding for every form counted, at least one form of each required
passage's own name run, and every form run failing — in which case D-041's binding half bars the
primary and the descriptor may stay a secondary. A two-anchor condition or another entity's name
is not a form of this test (D-046). **`not_run` and `not_applicable` are not exclusions, and
they are not failed include clauses either.** They record that the optional support was not
obtained: no bar is recorded, no include clause is violated, the unit is a member at the
`enumerated` tier if (a) and (b) hold, and an interpretable form run later would raise its tier
without re-judging any landed conclusion. This list is exhaustive, and reading a missing pass
into it as a further exclusion is forbidden.

**Closest competing category.** K3.

**Tie-break.** Against K3 the ordering is by evidence strength first and by the oracle test
second. A valid failure — preconditions verified, one form per required passage run, all failing
— bars K2 outright and becomes contributory evidence for K3 (D-041, D-044, D-045, D-046). Short
of that bar, K3 takes the unit whenever its clauses (a) and (b) are satisfied on E1 evidence,
because pit 15 puts a deployable measurement above the oracle support K2 rests on; that is what
happens on `5ae057fd55429945ae959328|bm25`, where the oracle state is `not_applicable` and the
separation is done entirely by D-024's near-disjointness and sign evidence. Only where the two
categories stand at the same evidence tier does a valid pass do tie-break work, as support for
K2 and never as a bar against K3. Against K5, D-037's tie-break governs: a deployable or
index-side condition that double-recovers outranks the oracle pass under pit 15.

**Positive examples.** `5ade69e455429975fa854ec5|dense` — five surface forms, two complete
titles, the bare name and two natural insertions, all giving 1 / 3.
`5ae1f596554299234fd04372|dense` — seven forms pass.

**Counterexamples.** `5a81ebee554299676cceb16d|dense`: the oracle-name test passes there in five
of seven forms and the unit is still not K2, because the query carries the name, the required
passage contains it, and it is unique in the 4,937-passage corpus, yet a query reduced to that
name ranks the passage 2202 of 4,937 and the bare surname 4243. The first exclusion fires. The
unit ends at K4 under D-054, so it is the cleanest available demonstration that a valid pass is
not sufficient. Second: `5ab48c325542996a3a969f93|dense`, where the six-form failure is valid
and the bar fires, which is the same criterion refusing the category from the other direction.

**Known limitations.** The criterion is partly definitional, as above. Its status is not open:
D-063's ruling 2 makes it a binding exclusion in the failing direction and optional,
non-sufficient support in the passing direction, with no multi-form requirement. **What that
costs, stated rather than hidden:** a unit that satisfies the content property but whose oracle
test was never run, or whose preconditions cannot be met, **is** a member of this category if no
bar fires and no stronger E1 evidence carries another category — and it is a member whose whole
evidence is the question's own wording, at the `enumerated` tier, with no measured observation
of the naming dependence behind it. All four current members carry a valid pass, so no in-sample
member sits at that tier; the exposure is prospective and it is a strength exposure, not a
membership one. The evidence that would lift such a member is one interpretable form of a
required passage's own name, inside D-046's form set, with both preconditions verified, and
nothing here requests that measurement on any existing unit. `5a85cead5542991dd0999ea9|dense`
ran one form only, and T was never measured there. D-026's structural boundary, whether the
described entity may be the answer passage's own subject, is T-08 and open. The boundary D-029
opened between an absent anchor and a present-but-unusable one is T-09, and T-09 is **ruled**:
`vocabulary_audit_triage.md`'s `Ruling status` table records it as **D-053, landed**. D-053
retains one descriptor, does not split it into an absent-name and an unusable-anchor name, and
writes four routes plus a record-without-a-name disposition for the residue. What stays open
is only D-053's own reservation, that a future residual with genuinely separable evidence
remains eligible for a later owner ruling — a residual-name question, not an open triage item.

**Named minimum evidence gaps: two, and exactly one of them is a request.** This category is the
only one that carries any, and under D-064 it carries exactly two.

1. **An actionable minimum-evidence request,** narrowly scoped under D-062: the title-indexing
   condition T on `5a85cead5542991dd0999ea9|dense`. What it would raise is this category's Dense
   capability boundary **off** `not_established`. **The endpoint is not ruled.** D-064 names
   none, and the owner's ruling for this corrective pass is that this document names none
   either. The landed synthesis words that target as `setup_scoped_method_supported`, which is
   a `claim_strength` value under D-062 and not one of that entry's four capability-boundary
   values, so it is recorded here as the synthesis's wording and is **not** restated as this
   category's boundary target. That unit ran one form only and T was never measured there.
2. **A gap that is not a request,** named separately so it is not mistaken for the same thing
   and larger than it: the **absence** of any BM25 unit on which this descriptor is the decisive
   primary, which is what raising the **BM25** boundary off `not_established` would need. No
   such unit exists in the 30, so no measurement on an existing unit can close it and **no
   measurement request is made for it at all**.

**Neither is run in this document and this document requests neither.** The count, the placement
and the request-versus-gap status above are D-064's, which prospectively corrects D-063's
sentence attributing the two items to K2 and K5. Both sit under K2; K4 and K5 carry none.
D-063's own sentence stays on disk unedited as append-only history, and where the two disagree
D-064 governs.

---

### K3 — `cross_passage_conjunction_unresolved`

- **`failure_layer`:** `method`
- **`retriever_scope`:** `cross_retriever`
- **`BM25_capability_boundary`:** `not_established` — see the paragraph below on why this is not
  `setup_scoped_method_boundary`.
- **`Dense_capability_boundary`:** `not_established` — the dilution alternative is excluded on
  two of the three Dense units and **live** on the third, `5ae1801955429901ffe4aec4|dense`,
  where the gate passes on the constraint passage.
- **`supporting_units`:** 6: `5ade42b55542992fa25da717|bm25`, `5ae057fd55429945ae959328|bm25`,
  `5ae60426554299546bf83019|bm25`, `5ab48c325542996a3a969f93|dense`,
  `5ae0a59a55429945ae9593e2|dense`, `5ae1801955429901ffe4aec4|dense`
- **`decisive_counterfactual`:** run, with one cell `not_applicable`. The conditioned
  oracle-name test fails on 5 of 5 interpretable applications — D-022, D-025, D-031, D-038,
  D-039 — with the D-044 and D-045 preconditions verified on each and D-046's coverage clause
  met. On `5ae057fd55429945ae959328|bm25` the application is `not_applicable` under D-044,
  neither pass nor failure. D-039 exhausted 134 non-oracle conditions on
  `5ae60426554299546bf83019|bm25` with no double recovery, and its one double-recovering
  condition is gold-targeted and explicitly not deployable (D-040). Dilution was rejected on
  `5ab48c325542996a3a969f93|dense` (D-031) and `5ae0a59a55429945ae9593e2|dense` (D-025).
- **`claim_strength`:** `observed`
- **`non_claims`:** No claim that BM25 or Dense cannot perform multi-hop retrieval. D-039's own
  wording is the limit: the conjunction is the binding constraint under every deployable
  pipeline tested, **not** an impossibility. On `5ae1801955429901ffe4aec4|dense` the dilution
  alternative is live. On `5ae057fd55429945ae959328|bm25` the oracle cell is uninterpretable, so
  five of the six units carry the oracle evidence and the sixth carries only the conjunction and
  near-disjointness clauses. The comparison retriever's success on any unit is not treated as
  causal proof. Per-hop reachability is not asserted as a necessary threshold, and D-063's
  ruling 1 settles why: a probe that injects a required passage's own name is E2 support, so its
  absence cannot veto a primary built on E1 evidence.

**Primary-label units:** the same 6, 3 BM25 and 3 Dense.

**Why `not_established` and not `setup_scoped_method_boundary`.** D-062's threshold for a
method-level assertion is that relevant implementation alternatives be ruled out. On the BM25
side that threshold is in fact met on all three units — D-022's 16-cell P×M×S×T design plus four
Rc×Rf cells and eight combinations, D-024's P negative on both required passages, and D-039's
134 non-oracle conditions with D-051's two cells — and BM25 taken alone would support
`setup_scoped_method_boundary` with `setup_scoped_method_supported`. Two things cap the
category. First, the Dense side has a live implementation-adjacent alternative on
`5ae1801955429901ffe4aec4|dense`. Second, `5ae057fd55429945ae959328|bm25` contributes no oracle
evidence at all under D-044, so the BM25 evidence base for the method claim is two units with a
verified oracle failure and one without. Splitting K3 by retriever to harvest the stronger claim
is deliberately **not** done — it would be structure driven by claim convenience rather than by
mechanism, and D-062 forbids raising claim strength to make fields look aligned.

**Definition.** A required fact exists only as a conjunction spanning two passages — the name or
fact that identifies one required passage lives only inside the other — and the evaluated
retrieval stage, which scores passages independently with no cross-passage reasoning, does not
assemble it.

**Required observable evidence.** (i) The question text and both required passages' texts,
showing where the intermediate fact lives. (ii) An enumerated split of the two required
passages' matched query-evidence sets into shared and unshared. (iii) At least one deployable
single factor measured with opposite signs across the two required passages. (iv) The
conditioned oracle-name result for each required passage, or an explicit `not_applicable` with
its ground.

**Inclusion rules.** Step 5's clauses (a) and (b) required, (c) contributory, of section 5.

**Exclusion rules.** The required passage is not reachable from its own distinctive cue, so the
obstruction is the cue and not the join (D-020, D-059). A gold-knowledge-requiring condition is
the only refutation offered, which D-040 forbids as a refusal ground and permits only as
limiting confidence. A single passage already supplies a complete answer, in which case step 1
fires (D-011's exclusion). An earlier step fired.

**Closest competing category.** K2.

**Tie-break.** The conditioned oracle-name test, in the failing direction. Where the test is
`not_applicable`, the near-disjointness clause carries the step and the claim stays `observed`.
Against K1 on BM25 units: prefer K3 when the deployable repair is opposite-signed across hops or
D-051 fires.

**Positive examples.** `5ae60426554299546bf83019|bm25` — 134 non-oracle conditions, none placing
both required passages inside the cutoff; D-051's two cells refuse the preprocessing primary at
0 rank positions and -0.024046 points. `5ade42b55542992fa25da717|bm25` — matched sets sharing
only {`the`, `in`, `is`, `novel`}, six factors carrying opposite signs, Q1 reaching the bridge
hop at 1 and K1 the answer hop at 1, and the series name occurring nowhere in the query and only
inside the bridge passage.

**Counterexample.** `5ab978855542996be2020512|dense`. It carries the descriptor as a secondary
and its oracle-name test failed, so the shape looks right. The exclusion fires: probe D,
non-oracle, makes the query exactly the verbatim epithet and the one passage that literally
contains it reaches only 106 / 0.219506, so that passage is not reachable from its own
distinctive cue, and probe E shows the same cue suppressing the other required passage. The
mechanism is sense drift, not an unassembled join.

**Known limitations.** The primary-use threshold is ruled — reachability is supporting, not
necessary — and the ruling is verified against the one unit it could have moved: D-024's K1P
places the answer hop at 4 / 10.556421 inside the cutoff, so `5ae057fd55429945ae959328|bm25`
holds under either reading. What remains a limitation is narrower and real:
`5ae057fd55429945ae959328|bm25` carries no interpretable oracle cell at all, so five of the six
units carry the oracle evidence. The ruling keeps one name; **where** the contract text lives is
triage item T-10 and stays open as a placement question, with D-054 a precedent by analogy only.
Two of the three BM25 units' factor designs are bounded 16- and 19-cell designs rather than
D-039's 134-condition exhaustion.

---

### K4 — `near_neighbour_crowding_and_sense_drift`

- **`failure_layer`:** `method` — see the paragraph below.
- **`retriever_scope`:** `cross_retriever`
- **`BM25_capability_boundary`:** `not_established` — one BM25 unit,
  `5ab8f57b5542991b5579f097|bm25`, with a family probe that recovers both required passages and
  a complement control that recovers neither, which establishes the family and not a method
  boundary. This is a missing-evidence value, not an inapplicability value; the mechanism is
  plainly available on a lexical backend, this unit being the instance.
- **`Dense_capability_boundary`:** `not_established` — four Dense units, on none of which an
  implementation alternative is excluded across the category.
- **`supporting_units`:** 5: `5a78b209554299148911f93e|dense`, `5a81ebee554299676cceb16d|dense`,
  `5a8d93ad554299653c1aa13d|dense`, `5ab978855542996be2020512|dense`,
  `5ab8f57b5542991b5579f097|bm25`
- **`decisive_counterfactual`:** `not_run` for the category, run per unit on all five. No single
  control separates this category from its competitors across the five. Per unit:
  `5a78b209554299148911f93e|dense` removal probes plus D-043's corpus-wide content-rule fact
  check; `5ab8f57b5542991b5579f097|bm25` a family probe recovering both, a complement control
  recovering neither, and two controls excluding corpus shrinkage and idf drift;
  `5a81ebee554299676cceb16d|dense` the framing-family removal X8 at 4 / 10 against its
  complement control X9 at 40 / 86, with X6 at 7 / 58 on the film-cue subset alone, inside a
  132-condition battery; `5a8d93ad554299653c1aa13d|dense` conditions A to E, of which A moves
  one required passage 12 to 2 and D falsifies `low_context_name_query` at 6 and 1;
  `5ab978855542996be2020512|dense` probes D and E. All five are E2b or E1; none is a deployable
  repair, and none is read as one.
- **`claim_strength`:** `observed`
- **`non_claims`:** No capability claim about either retriever. Rank shape — one-sided versus
  two-sided crowding — is a description, not a cause (pit 17, D-010). Corpus composition is
  recorded as a mapping-level modifier under D-062, with the two values section 16 defines, and
  is **not** the category's explanatory layer; D-003's rule that corpus setting is not a causal
  category is unaffected. The category does not claim that the competing family is removable in
  production; its family probes are E2b, which section 4 bars from being read as deployable
  repairs. **No member is admitted on an undischarged D-043 clause two**: each of the five is
  either ruled by a later decision or discharged from landed text. Membership of
  `5a81ebee554299676cceb16d|dense` rests on D-054's ruling, not on any re-reading of D-029's
  passage descriptions.

**Primary-label units:** the same 5, 1 BM25 and 4 Dense. **Two** further units carry a K4-family
`primary_open_code` in `case_memos_v2.csv` and do **not** satisfy this category's include rules:
`5a76387d554299109176e6ba|dense` and `5a7d19d85542995ed0d165e8|dense`, which D-063 routes to
`unresolved`. That is a real cost of writing positive include rules and is stated rather than
absorbed.

**Why `method` and not `corpus`.** Two units whose landed primary is a K4-family name carry an
explicit landed failure-layer statement and both say `method`: D-029 on
`5a81ebee554299676cceb16d|dense` — "Failure layer: method. Not implementation, since no
tokenizer or indexing artifact exists on a bi-encoder that strips accents and case and since T
is negative; not corpus setting, which is provenance" — and D-032 on
`5ab8f57b5542991b5579f097|bm25` — "Failure layer: method. Not implementation, because no
preprocessing or indexed-field change alone recovers the pair ... Not corpus setting, because
all three pooling paths are measured". Both units are members of this category, so both
statements are a member's own landed failure-layer sentence. No landed entry for any unit this
category holds states `corpus`, and assigning `corpus` would contradict two landed entries and
sit uncomfortably close to what D-003 forbids. Corpus composition belongs in the mapping-level
modifiers of section 16.

**Definition.** A set of non-gold passages, definable by a rule over their own text, outranks a
required passage and the required passage's own decisive content is not what distinguishes it;
or a query cue resolves to a sense neighbourhood other than its source passage's and suppresses
a required passage.

**Sub-readings recorded, not split.** (A) near-duplicate documents and entity variants; (B) a
question's framing facet; (C) the sense neighbourhood of one cue
(`verbatim_epithet_sense_drift`, D-059 — semantic drift on an L2-normalized whole-passage dot
product, explicitly **not** any form of string, phrase, exact-string or surface matching). The
three are kept inside one category because this is the project's weakest-controlled group and a
three-way split would manufacture structure the evidence does not carry. D-063 does **not** rule
that they are one mechanism; the split is re-opened at the Section 20 freeze gate if mapping
produces separating evidence.

**Required observable evidence.** For shapes A and B: (i) the competing set enumerated passage
by passage, with each passage's own text quoted for the property the rule names; (ii) the rule
stated over passage content, with a check that it does not also select a required passage; (iii)
at least one measured intervention on that family. For shape C: two non-oracle probes, one
showing the cue's own neighbourhood and one showing its suppression of the other required
passage. Under D-056, where the adopted descriptors cover only part of an enumerated family, the
uncovered members must be named explicitly.

**Inclusion rules.** Step 6's clauses of section 5, shape A/B or shape C, together with D-043's
two clauses for any crowding-family descriptor used as the primary. Clause two must be
**discharged** in one of the three ways section 9 names; an unchecked clause two is not an
include, and the unit routes to step 7 until it is discharged. Shape C carries no clause-two
obligation.

**Exclusion rules.** E1 to E4 of step 6: the family rule also selects a required passage; the
set is stated as a rank range or position; an earlier step fired; or there is no content family
and no measured intervention, in which case the unit is `unresolved`. Plus D-055's passage-level
boundary — the same passage set must not carry both `same_topic_passage_distractor` and
`generic_term_lexical_crowding`, and a passage whose body verifies a real connection to the
queried entity **and** verifies a missing decisive constraint belongs to the former.

**Closest competing category.** K1 on the lexical side and K3 on bridge units.

**Tie-break.** Against K1: D-055's passage-level boundary, as under K1. Against K3: prefer K3
when the required fact is a conjunction across passages and the two required passages'
matched-evidence sets are near-disjoint; prefer K4 when a content-defined family above a
required passage is measured and the required passage is reachable from its own cue. Against K6:
prefer K6 only when a within-cutoff passage satisfies **every** explicit constraint; a partial
match is K4.

**Positive examples.** `5a78b209554299148911f93e|dense` — D-043's fact check over the
4,937-passage corpus finds a content-only rule, excluding bodies that carry a month-day-year
date, that selects all six competitors and neither required passage, and needs nothing from
either required passage to write; removal probes measured. `5ab8f57b5542991b5579f097|bm25` — the
family is 7 Ince-side documents each stating its own relationship in its own text, filling all 5
positions above one required passage and 7 of the 9 above the other; the position-free content
rule "body contains the string `Thomas H. Ince`" selects 8 non-gold passages including all 7,
and 0 occurrences in the required passage's own body, which writes `Thomas Harper Ince`;
dropping those 8 gives 1 / 26.867443 and 2 / 22.192635, the complement control gives
6 / 26.911596 and 9 / 19.763251, and a size-matched null control and a statistics-matched
control exclude corpus shrinkage and idf drift. Third, and the largest battery behind any
member:
`5a81ebee554299676cceb16d|dense` — all 42 passages above the bridge hop and all 51 between the
two required passages read in full, 36 / 19 / 16 / 12 carrying a film-or-directing cue, a
person-role cue, both and `italian`, not one naming either required subject, and the family
verified in reverse as well, since deleting the director name leaves 8 of 10 inside the baseline
top-42 and deleting the descriptive referent instead leaves 8 of 10; the framing-family removal
X8 reaches 4 / 10 where its complement control X9 reaches only 40 / 86. D-054 rules D-043's
clause two satisfied on this unit.

**Counterexamples.** `5a7d19d85542995ed0d165e8|dense`: ranks 1 to 9 are a redundant same-team
neighbourhood and the shape is exactly sub-reading A, yet the rule that picks the family out —
Tennessee Volunteers season or statistical passages — also selects the required `1984 Tennessee
Volunteers football team` passage, so D-043 clause two fails and the family cannot be removed
even in principle; and D-015 states that no controlled text ablation was run. It reaches
`unresolved`, not K4. Second: `5a76387d554299109176e6ba|dense`, where a content-stated family
exists and no intervention of any kind was measured. Between them the two show that the include
rule is a rule and not a summary of what the entries concluded: one fails the mandatory clause
two, the other fails clause (b), and each carries a landed K4-family primary that this category
declines.

**Known limitations.** This is the least-controlled category and the one most likely to change
at the freeze gate. Its decisive counterfactual is `not_run` at category level. D-043 applies
from D-043 onward and asserts nothing about `5a81ebee554299676cceb16d|dense` or
`5ab8f57b5542991b5579f097|bm25`, but that sentence is chronological and not a reservation: D-054
later ruled the clause on the first, and the second is discharged from D-032's own landed corpus
scan. Both are members. **The residual reading on the second one is stated rather than buried.**
D-032 records the containing set of the string `Thomas H. Ince` as "8 non-gold passages" and
separately records 0 occurrences in the `Thomas H. Ince` gold's own body; the `Joseph McGrath
(film director)` gold's non-selection follows from that sentence's own scope, the containing set
being reported as non-gold, and is not separately stated as a measured 0. A reader who declines
that reading should route this unit to `unresolved`, in which case K4 falls to 4 primary-label
units, all Dense, `retriever_scope` becomes `Dense`, and the BM25 boundary stays
`not_established` on no units rather than one. That contingency changes no boundary **value**
and no claim strength, which is why the admission is made in the open. It is also the only
remaining contingency in this category's membership. D-056's requirement stands: the half of
D-023's neighbourhood that `generic_person_semantic_neighborhood` does not cover — roughly half
of the 26 non-gold passages above the lower required passage, unrelated Indian films rather than
person biographies — must be named in the dossier, not passed over. Whether a secondary may be
adopted as a scoped subset of its own primary's family is T-20 and open. What counts as
measuring a family's effect on a bi-encoder, where index-side removal is an arithmetic identity
by D-035, is T-26 and open. The compound member `5a8d93ad554299653c1aa13d|dense` has the weakest
clause-(b) satisfaction in the category: its interventions are query-side rewrites which D-018
calls oracle diagnostics, not family removals.

**No minimum evidence gap is named for this category.** What would raise its two boundaries off
`not_established` is implementation alternatives excluded across the category rather than per
unit, and no scoped request for that is made here.

---

### K5 — `dense_peripheral_passage_content_dilution`

- **`failure_layer`:** `method`
- **`retriever_scope`:** `Dense`
- **`BM25_capability_boundary`:** `not_applicable` — the gate's own exclusion says the
  descriptor does not apply to a lexical retriever, where length effects belong to the scorer's
  normalization term; nine BM25 entries name it only to record that.
- **`Dense_capability_boundary`:** `setup_scoped_method_boundary` — under the evaluated
  symmetric MiniLM bi-encoder with mean pooling over the whole passage, L2 normalization and a
  256-token window; the index-field alternative was measured and refused on the primary-label
  unit and no tokenizer or normalization alternative exists on this backend.
- **`supporting_units`:** 7, all Dense: `5a78b209554299148911f93e|dense`,
  `5a81ebee554299676cceb16d|dense`, `5add67915542992200553af8|dense`,
  `5ade69e455429975fa854ec5|dense`, `5ae048a255429924de1b708e|dense`,
  `5ae1801955429901ffe4aec4|dense`, `5ae1f596554299234fd04372|dense`
- **`decisive_counterfactual`:** run, and it is the project's strongest control. The
  four-condition gate: mean pooling verified from the implementation, a controlled ablation
  materially raises rank, an **equal-length** control ablation does not, and the passage does
  not hit the 256-token truncation. 9 applications, 7 passed, 2 rejected —
  `5ae0a59a55429945ae9593e2|dense` (D-025) and `5ab48c325542996a3a969f93|dense` (D-031). On the
  primary-label unit the ablation reaches 3 / 0.469751 and 1 / 0.549310, placing both required
  passages inside the cutoff. T is inert or negative on 6 of the 7 passing units.
- **`claim_strength`:** `setup_scoped_method_supported`
- **`non_claims`:** No claim about dense retrieval generally, about other pooling strategies,
  about rerankers, or about longer context windows. The gate generalises to other Dense content
  claims **only as a floor** — no such claim may be adopted without all four conditions — and
  never as a licence for a primary; it is widened in no other sense and is applied to no case
  lacking an equal-length control. The controlled ablation is a **diagnostic, not a deployable
  repair** — it removes content from a required passage, which no pipeline can do — so D-062's
  implementation clause is not triggered and the conclusion is not pushed to implementation
  level by it. On `5ae048a255429924de1b708e|dense` title indexing is materially positive and by
  itself flips `any@5`; that alternative is excluded rather than ignored, because D-037's
  three-cell decomposition attributes the gain to parenthetical type words rather than to a
  title-borne name and its best deployable condition leaves the answer hop at 125, on which
  ground D-037 refused the indexing route under `unindexed_title_name_anchor`'s own include
  conditions. The category keeps `setup_scoped_method_supported` because its implementation
  alternatives were measured and refused, **not** because its ablation is deployable.

**Primary-label units:** 1: `5ae048a255429924de1b708e|dense`. This is the one category whose
`supporting_units` and primary-label set differ, 7 against 1.

**Definition.** Decisive content in a long required passage is averaged against peripheral
content in the passage's own mean-pooled whole-passage vector, so the passage scores below
competitors, and removing the peripheral content raises it while removing an equal length of
decisive content does not.

**Required observable evidence.** All four gate conditions, each with its figures: mean pooling
read from the implementation rather than inferred; the controlled ablation's rank and score; the
**equal-length** control ablation's rank and score, decontaminated word by word rather than
sentence by sentence (D-035's usage requirement); and the passage's token count against the
256-token window. For primary use, additionally the ablation's effect on **every** required
passage.

**Inclusion rules.** Step 3's clauses (a) and (b) of section 5.

**Exclusion rules.** Any of the four gate conditions fails. No equal-length control exists, in
which case the gate must not be applied at all. The ablation does not place every required
passage inside the cutoff, in which case the name is a secondary and the unit routes on. A
lexical backend, where the descriptor's own exclusion fires.

**Closest competing category.** K2. This is D-037's actual tie-break, and pit 15 is its ground.

**Tie-break.** Prefer K5 when the deployable-side ablation ceiling places every required passage
inside the cutoff; prefer K2 when only an oracle-name form does. Where both a passing gate and a
passing oracle test are present and neither reaches the ceiling, section 12's tie-break applies
and the unit routes on to a later step.

**Positive examples.** `5ae048a255429924de1b708e|dense` — the primary-label unit, gate passed
and ceiling reached at 3 / 0.469751 and 1 / 0.549310. `5ae1f596554299234fd04372|dense` and
`5add67915542992200553af8|dense` — the gate passes on **both** required passages on each, which
is the mechanism at full strength; the ceiling is not reached, so the descriptor is a secondary
there and the units are supporting rather than primary-label. That distinction is stated because
"positive example" for this category's *mechanism* and for its *primary use* are not the same
set.

**Counterexamples.** `5ae0a59a55429945ae9593e2|dense` (D-025) and
`5ab48c325542996a3a969f93|dense` (D-031) — the gate is rejected on both, so the category has a
real counterexample set of two rather than an unfalsified rule. Third:
`5ae1801955429901ffe4aec4|dense`, where the gate passes on the constraint passage and fails on
the answer passage, so it is one application, one pass, and no primary.

**Known limitations.** One primary-label unit only. The gate's placement is kept unchanged and
its generalisation is a floor and not a licence; where the gate's **text** belongs across the
registry and this document is T-40 and stays open as a placement question. The registry carries
a running tally from D-027 onward that undercounts applications and passes by one because
D-027's sentence omits D-026; the member enumeration in `recount.py` is authoritative and this
document uses it. The third intervention class — gold-targeted index-side, injecting no answer
information but requiring knowledge of which passage is gold — has standing as E2b under section
4, and what that standing costs this category is stated in `non_claims` rather than netted out
of the claim strength. The converse gap D-031 recorded, a required passage's own measurable
property left with no carrier once the gate rejects, is T-45 and open.

**No minimum evidence gap is named for this category.** Its BM25 boundary is `not_applicable`
and its Dense boundary is already `setup_scoped_method_boundary`, so no boundary of it is
blocked by a missing measurement and a request would have nothing to raise. This is stated
rather than left silent because D-063 attributed one of K2's two named items to K5, which D-064
corrects.

---

### K6 — `evaluation_side_gold_chain_ambiguity`

- **`failure_layer`:** `evaluation`
- **`retriever_scope`:** `cross_retriever`
- **`BM25_capability_boundary`:** `not_applicable` — a non-method layer makes no capability
  claim, as D-062 requires.
- **`Dense_capability_boundary`:** `not_applicable` — same ground.
- **`supporting_units`:** 2: `5a83aaeb5542996488c2e483|dense`, `5adf58f15542993a75d264d2|bm25`
- **`decisive_counterfactual`:** partially run. On `5adf58f15542993a75d264d2|bm25` the
  alternative answer `Filthy Rich & Catflap` sits at 3 / 20.130130, inside the cutoff, and
  survives every repair across 112 labelled rows of which 101 are measured; the oracle test
  passed, T was materially positive, and the cutoff band was adopted at 0.281 percent (D-036).
  On `5a83aaeb5542996488c2e483|dense` no control series was run; the finding rests on
  `Graduation (album)` at rank 1 satisfying all explicit question constraints in one passage
  under the same reading of the Roc-A-Fella relation the gold chain uses, with the annotated
  golds at 6 and 7 (D-011).
- **`claim_strength`:** `observed`
- **`non_claims`:** This category makes **no** capability claim about either retriever, as D-062
  requires of a non-method layer. It is not a claim that the questions are defective — D-060
  forbids any question-quality descriptor, and both `question_wording_ambiguity` and
  `underdetermined_question` were deleted on pit 17. It is a statement that the annotated gold
  chain is not the only chain satisfying the question inside the evaluated cutoff. It makes no
  claim about substitutes outside the cutoff, which is T-51 and open.

**Primary-label units:** the same 2, 1 BM25 and 1 Dense.

**Definition.** Inside the evaluated cutoff there is a non-gold passage that satisfies every
explicit constraint of the question, so the metric's gold-title miss does not establish an
answer-retrieval failure.

**Required observable evidence.** The qualifying passage identified by title, rank and score;
the question's explicit constraints enumerated and each shown satisfied by that passage's own
text; the evidentiary standard shown to be the same one the annotated chain uses; and the
annotated golds' ranks.

**Inclusion rules.** Step 1's include clause of section 5.

**Exclusion rules.** The qualifying passage lies outside the cutoff (T-51 open). It substitutes
an intermediate annotated passage rather than answering the question — that is
`gold_chain_substitutability`, a secondary on five units and a primary on none. It satisfies
only part of the question, which is K4. And by D-060, no descriptor naming a defect, ambiguity
or underspecification of the question may be used here; such observations route to the four
names D-060 names, and an unroutable residue is recorded as a measured fact without a name.

**Closest competing category.** K4.

**Tie-break.** Prefer K6 only when a within-cutoff passage satisfies **every** explicit
constraint in one passage; a partial match is crowding and belongs to K4. Against K5 and K2:
step 1 precedes both, because if the annotation is not unique the ranking behaviour is not a
retrieval failure.

**Positive examples.** `5a83aaeb5542996488c2e483|dense` — `Graduation (album)` at rank 1, a
Kanye West studio album released through Roc-A-Fella Records with Dwele among its guest
contributors, satisfying all explicit constraints in one passage.
`5adf58f15542993a75d264d2|bm25` — `Filthy Rich & Catflap` at 3 / 20.130130, a 1987 BBC sitcom
featuring the three former "The Young Ones" co-stars.

**Counterexamples.** `5adc8977554299438c868de2|bm25`: four non-gold passages supply the same
intermediate fact under the gold's own evidence standard and two of them sit inside the cutoff,
at ranks 1 and 4, so the surface shape is a within-cutoff alternative. The exclusion fires: they
substitute an intermediate passage rather than answering the question, and D-034 withheld even
the cutoff descriptor on that ground. It ends at K1. Second: `5ade42b55542992fa25da717|bm25`,
where a full-corpus substring scan leaves neither required passage any substitute at all and no
inspected passage states the answer, so D-022 records both evaluation names as inapplicable.

**Known limitations.** Two units, one of them with no control series and no dossier. Whether a
substitute outside the cutoff counts is T-51 and open. The boundary between
`plausible_non_gold_answer` and `description_only_bridge_entity` on one unit is T-54 and open.
The category's final name is a naming-pass question per D-060; the name used here is written on
the evaluation side as D-060 requires, and Section 12's heading in `taxonomy_todo.md` still
reads "Question or Evaluation Ambiguity", which D-061 recorded as an open heading question.

## 7. Category × BM25/Dense capability-boundary matrix

| Category | `failure_layer` | `retriever_scope` | `BM25_capability_boundary` | `Dense_capability_boundary` | BM25 primary-label units | Dense primary-label units | `decisive_counterfactual` | `claim_strength` |
|---|---|---|---|---|---:|---:|---|---|
| K1 `bm25_minimal_preprocessing_score_distortion` | `implementation` | `BM25` | `implementation_recoverable` | `not_applicable` | 10 | 0 | run: non-oracle double recovery on 2 units (D-028, D-030) | `implementation_supported` |
| K2 `description_only_bridge_entity` | `method` | `Dense` | `not_established` | `not_established` | 0 | 4 | run and valid 4 of 4: oracle-name passed, as optional support and not as a condition | `observed` |
| K3 `cross_passage_conjunction_unresolved` | `method` | `cross_retriever` | `not_established` | `not_established` | 3 | 3 | run: oracle-name failed 5 of 5 interpretable, 1 `not_applicable`; 134 non-oracle conditions excluded on one BM25 unit | `observed` |
| K4 `near_neighbour_crowding_and_sense_drift` | `method` | `cross_retriever` | `not_established` | `not_established` | 1 | 4 | `not_run` for the category; run per unit on all 5 | `observed` |
| K5 `dense_peripheral_passage_content_dilution` | `method` | `Dense` | `not_applicable` | `setup_scoped_method_boundary` | 0 | 1, with 7 supporting | run: 4-condition gate, 7 passed / 2 rejected, ceiling reached on 1 | `setup_scoped_method_supported` |
| K6 `evaluation_side_gold_chain_ambiguity` | `evaluation` | `cross_retriever` | `not_applicable` | `not_applicable` | 1 | 1 | partially run | `observed` |
| — `unresolved` | — | — | — | — | 0 | 2 | none | — |

**The two unit columns are primary-label counts**, transcribed from D-063 Track D, not
`supporting_units` counts: 10 + 4 + 6 + 5 + 1 + 2 = 28, plus the 2 `unresolved` = 30, splitting
15 BM25 and 15 Dense against `case_memos_v2.csv`. They are landed reference figures and **not a
candidate mapping**; see section 18.

**When a boundary may read `not_applicable`.** `not_applicable` asserts that the category's
mechanism cannot arise on that backend. It is legal on exactly two grounds and on no other:

1. **A backend property makes the mechanism impossible.** K1's Dense cell — no tokenizer,
   normalization or indexed-field artifact exists on the evaluated bi-encoder, which strips
   accents and case (D-029). K5's BM25 cell — the descriptor's own exclusion says it does not
   apply to a lexical retriever, where length effects belong to the scorer's normalization term.
2. **The category is not a method-layer category**, so it makes no capability claim at all. K6's
   two cells, as D-062 requires of a non-method layer.

**Absence of primary uses on a backend is never a ground.** `retriever_scope` is observational
under D-062, and a descriptor whose definition states a property of the question and the
required passage is measurable on both backends (D-047). The correct value when a backend
carries no primary use is `not_established`, which records missing evidence rather than
asserting inapplicability. That is why K2's BM25 cell and K4's BM25 cell read `not_established`.
Neither K1's Dense cell nor K5's BM25 cell rests on unit counts, which is the difference between
them and a cell that would be wrong.

**The implementation-induced row makes no method-limit claim on either method.** K1 is the only
`implementation`-layer category. Its BM25 cell is `implementation_recoverable`, which is a
statement about a repairable implementation decision and not a limit of lexical retrieval as a
method; its Dense cell is `not_applicable`, which asserts that the mechanism cannot arise on
that backend and therefore also asserts no method limit. Its `claim_strength` is
`implementation_supported`, which by D-062 is not a method-level strength. So no cell, value or
sentence in the K1 row claims that BM25 or Dense as a method cannot do something. Conversely, a
successful preprocessing or indexing repair keeps a conclusion at implementation level
regardless of how many units share the symptom, and no category in this document converts a
repaired case into a method boundary.

**Scope caveat, applying to every row.** One pooled run; one deliberately minimal bag-of-words
BM25 implementation with titles excluded from the index; one symmetric `all-MiniLM-L6-v2`
bi-encoder with mean pooling, L2 normalization, a 256-token window and no reranking; 30 jointly
reviewed units, 15 per retriever, 24 bridge and 6 comparison questions; 19 of the 30 with a
dossier. Nothing in this table is a claim about BM25 or dense retrieval in general, and no row
uses comparison-retriever success to strengthen a claim.

**Closed value sets, per D-062, which a mapping validator may enforce literally.**

- `failure_layer` ∈ {`implementation`, `method`, `corpus`, `evaluation`}. Exactly one per
  category. There is no fifth value, and `compound` is not a value.
- each capability boundary ∈ {`implementation_recoverable`, `setup_scoped_method_boundary`,
  `not_established`, `not_applicable`}, each with a supporting sentence.
- `claim_strength` ∈ {`observed`, `implementation_supported`, `setup_scoped_method_supported`}.
- `retriever_scope` is observational scope in this bounded sample, never a cause.
- A missing decisive counterfactual is recorded as `not_run` and **caps `claim_strength` at
  `observed`**. K4 is the instance: `not_run` at category level, `observed`, despite unit-level
  diagnostics on all five members.
- A category missing any one of the eight fields is rejected. A complete category with
  `decisive_counterfactual=not_run` is legal when its claim stays `observed`.
- Unqualified claims of the form "BM25 cannot ..." or "Dense cannot ..." are forbidden anywhere.
  Comparison-retriever success alone can never strengthen a claim.

## 8. The oracle-name contract, carried in full

This is the single-factor oracle-name test's contract, ruled by D-041 and conditioned by D-044
to D-047, as landed by D-063. **One contract holds everywhere in this document** — in the
selection order, in K2's and K3's fields, in the required evidence, in the inclusion and
exclusion rules and in the tie-break.

**Three states, typed separately, because only one of them binds.**

| State | Definition | Consequence |
|---|---|---|
| Valid pass | at least one form inside D-046's form set, both preconditions verified and holding for that form, every required passage inside the evaluated cutoff | **Optional, non-sufficient support.** Raises a member's evidence tier to `measured (E2)`; may supply the supporting leg of a tie at equal tier; decides no membership; bars no competing category; never an inclusion condition |
| Valid failure | every form run fails, both preconditions verified and holding for every form counted as a failure, and at least one form of each required passage's own name run (D-046's coverage clause) | **Binding exclusion.** Bars the descriptor as a primary; it may stay a secondary. This is the only binding oracle reading |
| `not_run` / `not_applicable` | no form was run, or the preconditions were never verified, or a precondition fails, so under D-044 and D-045 the application is neither a pass nor a failure | **Nothing follows in either direction.** No bar is recorded, no include clause fails. A unit satisfying the content property with no competing E1 evidence is a member at the `enumerated` tier. Running an interpretable form later raises its tier and re-judges nothing |

**Preconditions**, both required before any state other than `not_applicable` may be recorded,
and judged **per injected form** rather than per unit (D-045):

1. pit 19g, from D-044: the injected anchor must actually be matchable in the passage it names.
   D-024 is the instance where it is not — the answer passage splits `General Mills, Inc.,` into
   `general` and `mills,` while the other gold carries a bare `mills`, so injecting the answer
   hop's own name gave 9.426700 points to the other gold and 0 to the target, and the bare test
   result is uninterpretable.
2. pit 24b, from D-045: the per-form degeneracy condition.

**Form set** (D-046): one surface form of a required passage's own entity name, injected alone.
A two-anchor condition, or another entity's name, is **not** a form of this test. The passing
half is existential — one qualifying form suffices — and the failing half is coverage-bound: at
least one form of each required passage's own name must have been run before the bar fires.
**Multi-form consistency is not required.**

**What the criterion never does.** It is never sufficient, never necessary, never designates a
winner. Where it bars, it bars and stops there; if no step's positive include rules are then
satisfied, the unit is `unresolved`. Reading a missing optional support as a second exclusion,
an implicit exclusion or a failed include clause is forbidden. That the four landed K2 primary
uses all happen to pass is provenance about a four-unit sample and may not be converted into a
condition.

**Two sub-questions of this item are closed elsewhere and are not reopened here:** the
definition's former "for lexical retrieval" wording, by D-047; and the injected-anchor
precondition, by D-044 with D-045 adding the per-form degeneracy condition.

**Series membership.** `recount.py` declares 18 applications, 8 passed and 10 failed. D-024
remains historical failure evidence while being prospectively `not_applicable` under D-044; that
distinction must be preserved, not netted out.

## 9. The crowding-family contract and clause-two discharge

**D-043's two clauses**, a mandatory include predicate for any crowding-family descriptor used
as a primary:

1. the family must be defined by a rule over **passage content**, never by a rank range or a
   position;
2. that rule must **not** also select any required passage.

**Clause two must be discharged** in one of exactly three ways and in no other, searched in this
order.

1. **Ruled, by a later decision.** A decision later than D-043 states, for that unit, that
   clause two holds. That ruling is the answer and no document may re-derive it: the decision
   log is the authority and a reinterpretation does not outrank an owner ruling. D-054 is the
   instance, on `5a81ebee554299676cceb16d|dense`. Where this route fires the other two are not
   consulted.
2. **Discharged, from landed text.** No later decision rules the clause, but landed decision
   text supplies a rule stated purely over passage content — no rank, no position, no gold
   status in the rule itself — together with corpus-scoped facts showing that the rule selects
   no required passage. The rule need not be the one the entry's prose chose and it may
   over-select non-gold passages, which is the strength D-043 itself accepted when it repaired
   D-027's family rule, replacing "a body containing albee" with "a body carrying no
   month-day-year date". D-043 also counted as a fix a predicate that excludes the required
   passages using their own subject names. `5ab8f57b5542991b5579f097|bm25` is the instance.
3. **Not discharged.** No later decision rules the clause, the stated family rule's own content
   predicate is carried by a required passage, and no position-free content rule with
   corpus-scoped selection facts is recorded. The unit then reaches step 7 and the missing fact
   check is **named rather than assumed in either direction**. `5a7d19d85542995ed0d165e8|dense`
   is the instance.

Entering K4 with clause two neither ruled, discharged nor routed is forbidden; "not checked" is
not a pass, and strong evidence on clause one and on clause (b) does not substitute for a
mandatory predicate. Shape C is outside this rule, D-043 governing crowding-family descriptors
and `verbatim_epithet_sense_drift` not being one.

**Where a constituent of a compound primary is a crowding-family descriptor**, D-043's two
clauses apply to that constituent on its own and clause two must be discharged the same way.

**D-055's passage-level boundary.** The same passage set must not carry both
`same_topic_passage_distractor` and `generic_term_lexical_crowding`. A passage whose body
verifies a real connection to the queried entity, work or topic **and** verifies a missing
decisive constraint belongs to the former; a passage matching only a broad category, institution
or relation word without that connection belongs to the latter. Different passage subsets inside
one unit may fall to different names; the same subset may not.

**D-056's evidence-recording rule.** Where a dossier claims to have enumerated a competing
family and the adopted descriptors cover only part of it, the uncovered members must be named
explicitly in that dossier. Silence may not be read as coverage. This is a recording rule, not a
requirement that every high-ranked passage carry a descriptor.

## 10. The dilution gate contract

**Placement.** The four gate conditions are the descriptor's own **include** gate, evaluated per
required passage. Primary use additionally requires the two-sided ablation ceiling, which is
step 3's clause (b). This placement is kept unchanged: the landed split of nine applications,
seven passes and two rejections with exactly one primary win shows the gate doing include-level
work rather than primary-selection work, and folding the ceiling into the gate would
retroactively reject six landed passes.

**The four conditions**, all required together: mean pooling verified from the implementation,
not inferred; a controlled ablation materially raises the required passage's rank; an
**equal-length** control ablation does not, decontaminated word by word rather than sentence by
sentence (D-035); and the passage does not hit the 256-token truncation.

**Generalisation: yes as a floor, no as a licence.** The four conditions generalise to **every**
Dense claim that attributes a required passage's score deficit to that passage's own content: no
such claim may be adopted without all four. Where no equal-length control exists the gate must
not be applied at all. They do **not** generalise into a sufficient condition for any primary.

**The third intervention class has formal standing as E2b**, defined in section 4: admissible as
evidence for a mechanism, never a deployable repair, never able to trigger D-062's
implementation clause or produce `implementation_recoverable`, outranked by any E1 result under
pit 15, and unable to refuse a category under D-040, only to limit confidence.

**Placement of this contract's text is triage item T-40 and stays open.** Carrying the text here
does not close it; see section 20.

## 11. `unresolved`

`unresolved` is a legitimate candidate assignment and a real destination, per the annotation
guideline's rule that an unsupported decision must not be forced. It is reached in exactly two
ways:

1. **No step fires.** Every step's include rules fail, or step 6's E4 fires. The reason is
   recorded per unit, naming the predicate that failed.
2. **Unbroken tie.** Two categories' include rules are satisfied at the same evidence tier and
   section 12's tie-break does not separate them.

An `unresolved` output is a **completeness property of the rule set, not a gap in it**: a rule
set that had to guess in order to avoid `unresolved` would be the incomplete one.

**Paired controls, which any revision of this document must keep exercising.**

| | Unit | Outcome | Why |
|---|---|---|---|
| Legal control, must be accepted | `5a78b209554299148911f93e\|dense` | K4 | D-043's verified content rule selects all six competitors and neither required passage; removal probes measured. Both K4 clauses hold on checked evidence |
| Legal control, must be accepted | `5a76387d554299109176e6ba\|dense` | `unresolved` | A content-stated family exists but no intervention of any kind was measured; D-009 states the ranking does not establish the cause. Clause (b) fails, E4 fires |
| Rejection case, must be refused | any unit reaching K4 through `otherwise` | rejected | Step 6 has positive include rules; E4 sends the residue to step 7 |
| Rejection case, must be refused | `5a7d19d85542995ed0d165e8\|dense` reaching K4 on its stated family | rejected | The family rule also selects the required `1984` passage, so clause two fails and the claim is untestable by any intervention. No later decision rules the clause on this unit |
| Rejection case, must be refused | any unit reaching K4 with clause two neither ruled, discharged nor routed | rejected | An unasserted mandatory predicate is not positive evidence for the category that requires it |
| Rejection case, must be refused | re-deriving clause two against a later decision that already ruled it | rejected | The decision log is the authority. A document may apply a landed ruling or record that none exists; it may not overturn one |
| Ruling control, must be accepted | `5a81ebee554299676cceb16d\|dense` | K4 | Route 1: D-054 rules clause two on this unit in terms; the family interventions are measured, so clause (b) holds |
| Discharge control, must be accepted | `5ab8f57b5542991b5579f097\|bm25` | K4 | Route 2: a position-free content rule and its corpus-scoped selection facts are recorded, and the rule selects no required passage |

The unit keys in this table are full keys; the `|` is written `\|` because a Markdown table cell
requires it. Everywhere outside a table cell the keys are literal.

## 12. Tie-break

**These clauses apply only where two categories' include rules are both satisfied on the same
unit at the same evidence tier.** Where only one category's include rules are satisfied, **no
tie-break runs**, and clause 1 in particular may not be used to refuse that category for want of
a run counterfactual; doing so would rebuild a mandatory positive predicate that the contract
does not have.

1. Prefer the category whose decisive counterfactual was actually **run on that unit** over one
   whose counterfactual is `not_run` or `not_applicable`. This is where a valid oracle pass does
   its legitimate work: as the supporting leg of a genuine tie, never as an include condition
   and never as a bar against the competitor.
2. If both were run, prefer the **deployable** result over the oracle result (pit 15). A
   gold-knowledge-requiring condition may not refuse a category at all (D-040).
3. If both are deployable, prefer the **lower-numbered step** of section 5.
4. If none of the three separates them, the unit is `unresolved`.

## 13. `taxonomy_defect_flag`

Set `taxonomy_defect_flag=true` on a unit whose evidence satisfies a category's include
conditions **and** its exclude conditions simultaneously. That is a defect in this document, not
in the unit, and it is what Sections 17 and 18 consume.

A unit reaching `unresolved` does **not** get the flag: `unresolved` records **absent** evidence
and the flag records **contradictory** evidence. All 30 rows of `case_memos_v2.csv` currently
read `false`, the three earlier flags having been cleared at D-057, D-058 and D-059, and the
flag stays available.

**Handling.** A flagged unit is not silently resolved by choosing the more attractive category.
The flag is recorded on the unit with the two conflicting conditions named, the unit's candidate
category is `unresolved` unless a tie-break in section 12 separates the pair on evidence, and
the conflicting condition pair is carried into the Section 17 boundary stress-test summary,
where the taxonomy text is what changes.

## 14. Compound units, secondary descriptors and the one-final-label rule

**One final label per unit.** Every other mechanism present on that unit is a secondary
descriptor.

**Secondary descriptors.** A secondary is allowed whenever its own registry include conditions
hold, independently of which category takes the primary. A secondary's presence is never
evidence for a category (section 4), and losing the primary does not remove a descriptor's own
evidence.

**The compound-case rule, five clauses**, exactly as D-063 Track F landed them:

1. A compound primary is legal only when each constituent mechanism **independently** satisfies
   its own include conditions and **no step** of the selection order in section 5 separates
   them.
2. Where a constituent is a crowding-family descriptor, D-043's two clauses apply to that
   constituent on its own, and clause two must be discharged the way section 9 requires.
3. A compound primary **creates no category**. It is recorded as a unit-level property of the
   candidate mapping — one compound flag plus the constituent list — and never as a fifth
   `failure_layer` value, which D-062 fixes at four, and never as a second final label, which
   the one-final-label rule forbids.
4. A compound primary is **not a route around `unresolved`**: if the constituents do not each
   satisfy their own include conditions, the unit is `unresolved`.
5. Compound status is recorded on the **unit**, not on the category, so a category's
   `supporting_units` and `claim_strength` are unaffected by a member's compound status.

**In-sample extent: exactly one unit.** `5a8d93ad554299653c1aa13d|dense`
(`compound_two_sided_crowding`, D-018), where two content-defined crowding families occupy
disjoint rank positions, each has independent evidence, neither explains both required passages,
and conditions A to E are measured, A moving one required passage 12 to 2 and D falsifying
`low_context_name_query` at 6 and 1. Both constituents discharge clause two from their own
landed wording. The name is retained **inside K4 as a compound member**, not promoted to its own
category: D-018 never ruled that the name denotes a unified category, and D-061 recorded that
question as open.

**What the compound rule does not settle.** Whether a compound whose constituents belong to two
different candidate categories is legal, there being no in-sample instance; whether
`compound_two_sided_crowding` survives the naming pass; and the weakness D-018 itself records,
that its interventions are query-side rewrites it calls oracle diagnostics rather than family
removals.

## 15. What may never be a category

These are prohibitions on the taxonomy's shape, not observations about the sample. Each names
what the observation may be recorded as instead.

1. **A rank pattern is never a category.** One-sided against two-sided crowding, a rank range, a
   position, "gold at 6 and 7", "family at ranks 1 to 5" — these describe an output, not a
   mechanism (pit 17, D-003, D-010). A family must be defined by a rule over passage **content**
   (D-043 clause one); rank positions may be reported as the observation the rule explains.
2. **Retriever identity is never a category.** "BM25 failures" and "Dense failures" are not
   categories and not causes. Backend difference enters only as `retriever_scope`, which is
   observational, and as the two capability-boundary fields, which are scoped claims with named
   evidence (D-003, D-062, D-047). A category may not be split by retriever to harvest a
   stronger claim than the pooled evidence supports; K3 is the worked instance of refusing that.
3. **A question type is never a category.** Bridge against comparison is a property of the
   dataset's question construction; it may be reported as scope, never as a mechanism. Nor may
   any **question defect** be a category or a descriptor: D-060 forbids every question-quality
   descriptor, and both `question_wording_ambiguity` and `underdetermined_question` were deleted
   on pit 17. Such observations route to existing names — a within-cutoff passage satisfying all
   explicit constraints goes to `plausible_non_gold_answer` or `gold_chain_not_unique`; a
   substitutable annotated chain to `gold_chain_substitutability`; a described-not-named entity
   to `description_only_bridge_entity`; question wording differing from corpus wording to
   `surface_form_tokenization_mismatch` or `entity_alias_reference_mismatch` — and a residue no
   route carries is recorded as a measured fact **without** a name (D-025, D-053).
4. **Corpus setting is never a category, a layer or a cause** (D-003). It is mapping-level
   provenance; see section 16.
5. **Distance from the cutoff is never a mechanism.** D-042 gives it a threshold as the
   descriptor `cutoff_sensitive_near_miss`, with its never-decided band left open and its
   substitutability exception intact.
6. **Gold missingness is never a mechanism.** Stating that a required passage was not retrieved
   restates the metric.

## 16. Mapping-level modifiers

These fields belong to the candidate mapping, not to any category. They exist so that provenance
is recorded rather than promoted.

**Corpus setting, with the two paths recorded separately.** Pooled against per-question `any@5`
disagreement has two measurably different drivers and they are recorded as **distinct values of
one provenance modifier, never as a category, a layer or a cause**:

- `pooling_added_competitors` — the candidate set changed. Dropping exactly the
  pooling-introduced rivals restores the cutoff.
- `collection_statistics_shift` — the scoring function's inputs changed. Dropping the
  pooling-introduced passages above a required passage does not restore it, and the driver is
  the ten-document index's own scale: `idf(smith)` 0.762140 against pooled 5.222190,
  `idf(multinational)` 0.421076 against 5.480131, and avgdl 58.600000 against 90.884950 (D-024).
- `both`.
- `not_decomposed` — the honest default, since only 3 of the 16 landed applications were
  decomposed to that granularity.

D-003 is **not** re-worded; the precision the second path needs lives here as a rule instead:
corpus setting stays provenance under **both** paths, and the second path may **not** be
re-described as an implementation property of the scorer, because `k1`, `b`, `epsilon` and the
analyzer are identical between the two settings and only the collection over which the
statistics are computed differs.

**Compound status.** One flag plus the constituent list, per section 14 clause 3.

**Cutoff proximity.** `cutoff_sensitive_near_miss` where D-042's threshold is met, as a
descriptor and never as a mechanism.

## 17. Carry-over rules, with their sources

Each row is a rule that a landed decision requires this document to carry, with where it is
operative here. This table is the complete carry-over set.

| Rule | Source | Operative here |
|---|---|---|
| Oracle-name test: binding negative; positive half optional, non-sufficient support and never an inclusion condition, with `not_run` / `not_applicable` typed as neither pass nor failure and never as an exclusion | D-041, D-044 to D-046, ruled by D-063 | §5 step 4 and step 5 clause (c); §8; §12; K2 definition, required evidence, inclusion, exclusion, tie-break; K3 `decisive_counterfactual` |
| Pit 19g precondition on the exclusion | D-044 | §5 step 5 clause (c); §8; K3 `decisive_counterfactual` |
| Pit 24b precondition, judged per injected form | D-045 | §5 step 4; §8; K2 required evidence |
| Form set, and per-passage coverage before the bar fires | D-046 | §5 steps 4 and 5; §8; K2 exclusion rules |
| Crowding-family primary-use contract, two clauses | D-043 | §5 step 6 shape A/B and E1; §9; K4 inclusion and exclusion |
| How clause two is discharged, in three ordered routes, and that an unchecked clause is not an include | D-043's own D-027 fact check read as the procedure it is, plus D-054 as the instance of a later ruling | §5 step 6; §9; §11's controls; K4 inclusion rules |
| Descriptor definitions state a property of the question and the required passage, not a backend; the scope line is provenance | D-047 | K2 `retriever_scope` and both boundary fields; §7's `not_applicable` discipline |
| `not_applicable` requires a backend property or a non-method layer; absent primary uses give `not_established` | D-062 with D-047 | §7's discipline paragraph; K1, K2, K4, K5 and K6 boundary fields |
| The third intervention class is a diagnostic with standing, never a repair | D-023 and D-024, ruled by D-063 | §4's E2b typing; §5 steps 3 and 6; §10; K4 and K5 `decisive_counterfactual` and `non_claims` |
| Corpus setting's two paths are recorded separately as mapping modifiers, never as a category | D-024 and D-003, ruled by D-063 | §4; §15 item 4; §16; K4 `non_claims` |
| The compound-case rule, five clauses | D-018, D-061, landed as D-063 Track F | §14 |
| Gold-knowledge conditions may not refuse the conjunction primary | D-040 | §4's E2b standing; §5 step 5 exclusion; §12 clause 2; K3 exclusion |
| `cutoff_sensitive_near_miss` threshold, never-decided band, substitutability exception | D-042 | §4's non-predicate list; §15 item 5; §16; K1 and K6 counterexamples |
| Mechanical-separability naming line, scoped to preprocessing | D-049 | K1 exclusion rules |
| Reverse boundary for the preprocessing primary, judged per passage | D-051 | §5 step 2 clause (b); K1 exclusion rules |
| One preprocessing primary, six-member enumeration, prospective narrowing | D-052 | K1 definition and limitations |
| Four routes for the unusable-anchor residue | D-053, carry-over required by D-060 | K2 exclusion rules; §15 item 3 |
| `question_frame_semantic_crowding` governed by D-043 with no second contract, and D-043's clause two ruled satisfied on its one primary use | D-054 | §9 route 1; §11's ruling control; K4 inclusion rules and membership |
| Passage-level boundary between the topical and lexical crowding names | D-055 | §9; K1 and K4 tie-break; K4 exclusion rules |
| Uncovered members of an enumerated family must be named | D-056 | §9; K4 required evidence and limitations |
| No question-quality descriptor; evaluation-side routing | D-060 | §15 item 3; K6 definition, exclusion rules and limitations |
| Intake routing of sections 8 to 13, and the D-059 wording constraint that the sense-drift mechanism is never described as string, phrase, exact-string or surface matching | D-061, D-059 | §6 K4 sub-reading C; §5 step 5's rejection case |
| Rank shape, corpus setting and retriever identity are never categories | D-003, pit 17 | §4; §15; every `non_claims` |
| Eight capability fields, four layers, four boundary values, three claim strengths | D-062 | §6 and §7 |
| Primary-use contracts belong in the candidate taxonomy rather than in the secondary registry | D-021's dossier note, D-041, D-043, D-049, D-051, D-052, D-053, D-055, D-056, and Section 13's recorded position | §5, §8, §9, §10 and this table |

## 18. Landed reference counts, which are not a candidate mapping

D-063 Track D reapplied the selection order to all 30 full unit keys and landed these counts: K1
10, K2 4, K3 6, K4 5, K5 1, K6 2 and `unresolved` 2, summing to 30, disjoint and exhaustive, and
splitting 15 BM25 and 15 Dense against `case_memos_v2.csv`. It agrees with 28 of the 30 landed
`primary_open_code` groupings once the section folds are applied.

The two exceptions are the `unresolved` assignments, and they fail on **different** predicates,
which is why each is recorded per unit rather than pooled:

| Unit | Landed `primary_open_code` | Why no category's include rules are reached |
|---|---|---|
| `5a76387d554299109176e6ba\|dense` | `two_named_entities_underprioritized` | Step 6's fourth exclusion fires. A family is stated as passage content, generic person and birth-related material, but **no intervention of any kind was measured** on the unit, and D-009 states that the ranking does not establish which internal embedding or scoring component caused the ordering. The unit carries no ordinal-series membership at all |
| `5a7d19d85542995ed0d165e8\|dense` | `same_entity_variant_crowding` | D-043's second clause fails and is not discharged: the family rule D-015 states also selects one of the required passages, so the family cannot be removed even in principle and the claim is untestable by any intervention. No decision later than D-043 rules the clause on this unit, so the first discharge route does not fire either, and no controlled ablation was run |

**These figures are transcribed reference, not a mapping.** No mapping exists. Neither unit's
`primary_open_code` is changed by anything here. Section 15 of `taxonomy_todo.md` creates
`candidate_mapping_v0_1.csv` with all 30 `candidate_category` cells **empty** and all 30
`mapping_status` cells `not_tested`, and Section 16 then performs the mapping unit by unit; the
legacy `candidate_category` column of `case_memos_v2.csv`, which holds 29 mirrors of the
then-current primary and 1 blank, may **not** prefill it (D-062). The counts above are what the
mapping will be compared against, not a substitute for running it.

## 19. Known limitations of the taxonomy as a whole

- **Evidence base.** 30 units from one pooled run, one minimal BM25 implementation and one
  symmetric bi-encoder. 11 units carry no dossier and no factorial (T-56), and every predicate
  satisfied by an enumerated match set rather than a measured rank effect falls on that batch.
- **Control coverage.** Four control series carry the counterfactual weight, with membership
  declared by `recount.py`: the single-factor oracle-name test, 18 applications, 8 passed and 10
  failed; the title-indexing condition T, 21 applications, 5 materially positive, 2 one-sided
  positive and 14 inert or negative; the dilution gate, 9 applications, 7 passed and 2 rejected;
  and corpus setting, 16 applications, which stays provenance under D-003 and is used as a cause
  nowhere.
- **Claim strengths are mostly `observed`.** Only K1 reaches `implementation_supported` and only
  K5 reaches `setup_scoped_method_supported`. **Three** of the six categories carry
  `not_established` on both backends, which records missing evidence and not inapplicability.
  That three is **derived** by reading the two boundary fields of each of the six field blocks
  rather than asserted: K2, K3 and K4 match on both sides; K1 is
  `implementation_recoverable`/`not_applicable`, K5 is
  `not_applicable`/`setup_scoped_method_boundary`, and K6 is `not_applicable` on both.
- **K4 is the weakest-controlled category** and the one most likely to change at the freeze
  gate; its three sub-readings are recorded and deliberately not split, and that split is
  re-opened at Section 20 if mapping produces separating evidence.
- **Two units reach `unresolved`,** which is a property of a complete rule set and not a gap.
- **Open triage items each category carries** are named in its own limitations: T-08 under K2;
  T-10 under K3; T-20, T-26 and T-56 under K4; T-40 and T-45 under K5; T-51 and T-54 under K6;
  T-62 and T-63 around K1's two primary names. None is closed by this document. **T-09 is not
  on that list**: K2's limitations name it, but `vocabulary_audit_triage.md`'s `Ruling status`
  table records it as **D-053, landed**, so what K2 carries there is D-053's ruling plus the
  residual-name question that ruling expressly leaves eligible for a later owner decision.
- **Two named minimum-evidence gaps** exist, **both under K2**, and **exactly one of them is an
  actionable request**: the title-indexing condition T on `5a85cead5542991dd0999ea9|dense`,
  narrowly scoped under D-062. The second is the **absence** of any BM25 unit on which the
  description-only descriptor is the decisive primary; no such unit exists in the 30, so no
  measurement on an existing unit can close it and **no measurement request is made for it at
  all**. K4 and K5 carry no named gap. **Neither is run and neither is requested by this
  document.** The count, the placement and the request-versus-gap status are D-064's, which
  corrects D-063's `{K2, K5}` attribution prospectively without editing D-063.
- **The six names are candidate names.** Whether each survives the naming pass, and whether any
  boundary can be raised off `not_established`, are Section 17 to Section 20 questions.

## 20. What this document does not do

- It is **not frozen** and is not `taxonomy_v1.md`. Its `status` is `draft` and stays `draft`
  until an independent review and the owner say otherwise.
- It creates **no** `candidate_mapping_v0_1.csv`, performs **no** candidate mapping over the 30
  units, and creates no frozen taxonomy, `final_labels.csv` or `category_counts.csv`.
- It **reclassifies no unit**, moves no primary or secondary open code, and edits no memo row,
  registry entry, dossier, manifest or protected source. It **rewrites** no prior review or
  synthesis: the round 1 and round 2 acceptance reviews of this file, and the round 1 review of
  the D-065 landing, each receive an appended and clearly separated maintainer response, and in
  every case that review's findings, verdict and gate lines stay exactly as written.
- It runs **no** retrieval measurement, ranking, score computation, title-indexing rerun,
  dilution ablation, oracle injection or corpus sweep, and adds no tool or validator. The
  corrective pass behind this revision added none either: `tools/recount.py` receives one
  `not_applicable` registration for D-064 in the title-indexing series, which records that the
  entry names the condition and measures it on no unit.
- It is **not a decision entry** and appends nothing to `open_code_decision_log.md` on its own
  authority. D-001 to D-065 stand as landed. The corrective pass that resolved the round 1
  review's F-02 appended exactly **one** entry, D-064, under separate owner authorization, and
  this document transcribes that entry rather than deciding anything itself. The entry that
  lands this file is D-065, appended under its own owner authorization, and the next unused
  decision ID is D-066, which must still be recomputed with `recount.py` at landing time rather
  than taken from any document.
- It **closes no triage item.** In particular T-10, where the conjunction primary's contract
  text finally lives, and T-40, where the dilution gate's contract text lives across the
  registry and this document, are **placement** questions and stay open. This document carries
  the text because `taxonomy_todo.md` requires Section 14 to carry it; carrying it is not a
  ruling on where it finally belongs, and closing either item needs its own owner decision.
- It **changes no `$STAGE` statement**: `$STAGE` stays `categories`, and the `mapping-v0`
  value Section 15 runs under is not set by this landing. Section 14's 35 checkboxes in
  `taxonomy_todo.md` are ticked by D-065, the entry that lands this file and that records which
  passage of which section each item was checked against. Those ticks are that entry's act, not
  a claim this document makes about itself.
- It claims **no gate beyond Section 14**. It does not declare Section 15 open and does not
  request the candidate mapping. The round 3 independent acceptance review of this file recorded
  PASS with no confirmed finding; D-065 records the narrow revision made to this section and to
  Section 21 after that verdict, which is the only part of this file no review has read.
- It is **not staged, committed or pushed on its own authority**. Staging over an explicit path
  list, the commit and any push are the owner's.

## 21. Mechanical verification record

Every assertion below was run against this file's own bytes. The Git state at the time of that
verification was HEAD `13824274eb372686752f9f54d614e14c6434ab32`, with the D-064 corrective
pass's three tracked edits uncommitted and nothing staged; that pass is now commit `c5955a5`,
the header refresh after it is commit `f41c2e6`, and this file's Section 14 landing is D-065,
uncommitted at the time of writing. Sections 0 to 19 are unchanged since the round 3 review
read them **except for the two T-09 spans** the round 1 review of this landing rejected as its
blocking finding F-01 — K2's known limitations in Section 6, and Section 19's open-triage-item
bullet — both of which now record T-09 as ruled by D-053. Byte-identity of the rest is a
maintainer claim and not independently verifiable, since this file has no committed
predecessor; what is verifiable is that every substantive Section 0 to 19 property recorded
below still holds on disk. Sections 20 and 21 carry the narrow revision D-065 describes.

**Field completeness.** Six categories, each carrying all eight D-062 fields under their exact
names, and each carrying all nine judgement components. No category carries a ninth field name
inside its field block; `primary-label units` is stated outside the block precisely so the
eight-field count is unambiguous.

**Closed value sets.** Every `failure_layer` value is one of the four; every capability boundary
is one of the four, each with a supporting sentence; every `claim_strength` is one of the three.
The one category whose `decisive_counterfactual` is `not_run` at category level, K4, carries
`claim_strength=observed`, so the cap holds. No unqualified method-incapability sentence
appears.

**Full unit keys.** Every unit reference in a `supporting_units` field, in a positive example,
in a counterexample, in a control table and in section 18 is a full `<24-hex>|<retriever>` key.
Inside Markdown table cells the pipe is escaped `\|`, which is the cell encoding of the same
key; outside table cells the keys are literal. No bare `example_id` is used as a unit anywhere.

**Counts.** For each category the claimed `supporting_units` count equals the number of key
tokens listed and equals the number of **unique** keys listed, with zero duplicates: K1 10, K2
4, K3 6, K4 5, K5 7, K6 2. Every key is a member of the 30 in `case_memos_v2.csv`. Scope agrees
with membership: K1's members are all BM25 and it declares `BM25`; K2's and K5's are all Dense
and each declares `Dense`; K3's, K4's and K6's are mixed and each declares `cross_retriever`.

**Partition.** The primary-label counts sum to 28 across the six categories, plus 2
`unresolved`, equalling 30, and split 15 BM25 and 15 Dense. This is transcribed from D-063 and
is not a mapping.

**Physical form.** Pure CRLF with no lone LF, matching the sibling shared Markdown in this
directory under red line 2a; no BOM; no tab; every non-table, non-heading line at most 96
characters; and no `N / D.DDDDDD` rank-and-score pair broken across a line, so the exact string
comparison other artifacts use still finds each pair intact.

**Declared artifact-state count against the rendered table.** Section 3 declares **five**
artifact and lifecycle states, and its table renders exactly **five** data rows, counted as the
`|`-prefixed lines below the header and separator: raw notes, provisional open codes, legacy
routing hint, candidate categories and final labels. The declared count is compared with the
rendered count rather than assumed, and the two agree. This quantity is separate from D-062's
four `failure_layer` values, which all six categories still draw from and which section 3 says
in terms. Negative control: declaring four states against this table is rejected, four against
five. This assertion exists because round 1's finding F-01 was exactly that mismatch.

**Named minimum-evidence gaps against the controlling D-entry.** What this document says about
named minimum-evidence gaps is compared with the latest D-entry that rules them, D-064, on three
axes at once: the count, the category each sits under, and whether each is a request or only a
gap. D-064 holds two named gaps, both under K2, exactly one of them an actionable request, that
request being the title-indexing condition T on `5a85cead5542991dd0999ea9|dense`, no request at
all for the BM25 item, and no named gap under K4 or K5. This document agrees on every axis: K2's
paragraph and section 19's summary each state two under K2 with exactly one a request and name
the same unit; K4 and K5 each state in terms that they carry none; K1, K3 and K6 name none; and
exactly one category block carries a positive named-gap heading. Negative controls: moving one
item to K5, and calling the BM25 item a measurement request, are each rejected against D-064's
text. D-063's own `{K2, K5}` sentence was confirmed still present on disk and unedited. This
assertion exists because round 1's finding F-02 was exactly this cross-document disagreement.

**Triage status checked against the ruling-status table rather than against prose.** Every
triage item this file calls open is looked up in `vocabulary_audit_triage.md`'s `Ruling status`
table, which is that file's own authoritative record of which entry settled which item. An item
absent from that table is open; an item present with a landed D-entry is ruled, whatever any
prose elsewhere in that file or this one says. Section 19's list — T-08, T-10, T-20, T-26,
T-40, T-45, T-51, T-54, T-56, T-62 and T-63 — was checked item by item, and none of the eleven
appears in the table. T-09 does appear, reading `D-053, landed`, and D-053's own `What this
does not settle` names T-08, T-04, T-06 and T-40 without naming T-09; so T-09 is off the open
list, and K2's limitations and Section 19 both record it as ruled with only D-053's residual-
name reservation left open. Negative control: any sentence here listing a triage item as open
while the ruling-status table records a landed D-entry for it — which T-09 was, in these two
places — is rejected. Legal control: the eleven items above, none of which appears in the
table, each correctly described as open; a sentence listing exactly those eleven passes. This
assertion exists because the round 1 review of this landing raised finding F-01 against exactly
that error, and because the entry that lands this file is append-only once committed.

**Two-sided `not_established` count derived from the six field blocks.** Section 19's count of
categories carrying `not_established` on **both** capability boundaries is **derived** by
reading only the two boundary fields of each of the six field blocks, then compared with every
summary sentence that states it, rather than hard-coded. The derivation is K1
`implementation_recoverable`/`not_applicable`; K2 both `not_established`; K3 both
`not_established`; K4 both `not_established`; K5
`not_applicable`/`setup_scoped_method_boundary`; K6 both `not_applicable`. That gives **three**,
namely K2, K3 and K4. Section 19 states three, and the section 7 matrix rows agree field for
field with the six blocks. No category field was changed to reach the agreement. Negative
control: stating **four** against these same six field blocks is rejected, four against three;
the legal control is the same derivation stating three. This assertion exists because round 2's
finding F-03 was exactly that hard-coded miscount.

**Every stated boundary endpoint type-checked against the boundary vocabulary.** Each sentence
naming what a capability boundary would be raised **to** is membership-tested against D-062's
four-value boundary set — `implementation_recoverable`, `setup_scoped_method_boundary`,
`not_established`, `not_applicable` — separately from D-062's three-value `claim_strength` set
of `observed`, `implementation_supported` and `setup_scoped_method_supported`. Two places state
an endpoint and both pass. K3 pairs the boundary `setup_scoped_method_boundary` with the
strength `setup_scoped_method_supported`, each token drawn from its own vocabulary. K2's request
states only that the Dense boundary would move **off** `not_established`, with the endpoint
expressly **not ruled**, which is D-064's scope and the owner's ruling for this pass.
`setup_scoped_method_supported` survives in K2's paragraph only as an attributed quote of the
landed synthesis's wording, labelled there as a `claim_strength` value and explicitly not
adopted as this category's boundary target. Negative control: a sentence whose boundary target
is a token belonging only to the `claim_strength` set is rejected; the two legal controls are a
boundary token from the four-value set, and an explicitly unspecified endpoint. This assertion
exists because round 2's finding F-04 was exactly that type confusion.

**The `taxonomy_todo.md` diff classified span by span — historical record of the D-064 pass.**
This paragraph is retained as a **historical** record of the superseded D-064 corrective pass
and describes no diff now on disk; the paragraph after it classifies this landing's own TODO
diff. That pass's tracked TODO edit was classified against owner ruling 3 and D-064's `Files
and workflow effect`, which between them authorized only the mechanical
next-unused-decision-ID synchronization and the append-only range it names. That diff was seven
hunks covering nine changed lines on each side, +9/-9 by `git diff --numstat`, and it is now
inside commit `c5955a5`, where `git show --numstat c5955a5 -- taxonomy_todo.md` still reports
nine and nine. Each changed line was compared with its predecessor with the digits removed:
every one consisted only of `D-063`-to-`D-064` or `D-064`-to-`D-065` identifier substitutions,
or the matching `D-001`-range extension, and no changed line added, removed or re-meant a
clause. Negative control, as applied to that pass: a changed span carrying a new semantic
clause — such as a sentence describing what D-064 lands — was rejected as outside the
authorized collateral even when it sat beside a legal ID substitution; the legal control was
the identifier or range substitution alone, leaving the surrounding sentence untouched. This
assertion exists because round 2's finding F-05 was exactly such an unauthorized clause, which
that pass removed. It is marked historical because the round 1 review of **this landing** found
it still written in the present tense against a diff that had since been replaced, which is
that review's finding F-02.

**The `taxonomy_todo.md` diff classified span by span — this landing.** The tracked TODO edit
on disk for D-065 is **+86/-65** by `git diff --numstat`, in **17** hunks at `git diff -U0` and
14 at the default three-line context. It is not an identifier-substitution diff and is not
classified as one. It is classified against D-065's own `Files and workflow effect`, which
authorizes exactly four classes of change to this file, and every changed span falls in one of
them. **One,** Section 14's 35 checkboxes go from `[ ]` to `[x]` and the block gains a landing
note in the shape D-061 and D-063 used; this is the single largest span. **Two,** three further
landing notes: the D-063 disclaimer block, the D-section step-7 line and the carry-over step
each gain a sentence recording that Section 14 is now landed as D-065. **Three,**
next-unused-decision-ID and append-only-range synchronization: `D-065` to `D-066` for the next
ID, and `D-001` to `D-064` becoming `D-001` to `D-065` for the protected range. **Four,**
handoff-state synchronization: the handoff header, the A.1 zero-context recovery point, the
current-blocker and next-step-plan blocks, the commit-hash record, the
allowed-uncommitted-work sentence
and the D-section progress lines that named Section 14 as not started. Because classes one, two
and four carry new prose by authorization, the D-064 paragraph's negative control does not
apply here and would wrongly reject this diff; the control that applies here is scope. Negative
control: a changed span that rules or closes a triage item, moves a category boundary or a
`claim_strength`, reclassifies a unit, sets `$STAGE` to anything but `categories`, or states
that a mapping, frozen taxonomy, final label or category count now exists is rejected as
outside D-065's authorization even where it sits beside a legal state synchronization. Legal
control: a span that ticks a Section 14 item, records the Section 14 landing, advances the
next-unused ID or the append-only range, or restates handoff state, changing no ruling and no
count. Checked against the diff rather than assumed: the triage counts stay 21 ruled, 4 closed
without a D-entry and 37 open; every changed line naming `$STAGE` still sets it to
`categories`, the one `mapping-v0` mention being the value Section 15 would run under after a
separate owner authorization, exactly as the line it replaces said; no changed line asserts
that a mapping, frozen taxonomy, final label or category-count artifact exists; and the batch-2
line recording T-09 among the items landed by D-053 to D-056 is unchanged, which is the same
record that makes F-01's correction necessary. This assertion exists because the round 1 review
of this landing raised finding F-02 against a present-tense diff record that did not match the
diff on disk.

**Tool coverage, stated because it is partial.** `recount.py`, `check_landing.py`,
`landing_kit.py --eol-table`, `cross_check.py` and `git diff --check` do **not** read this file:
recount derives its counts from the decision log, queue, memo CSV and dossier index;
check_landing scans the decision log, the memo CSV's narrative fields and `per_case_analysis/`;
the EOL table covers a declared ten-file list plus the dossiers; and the two git checks see only
tracked changes. This file becomes one of them at the D-065 landing, whose diff is four files —
the D-065 append, this file entering version control, Section 14's ticks with the handoff
synchronization in `taxonomy_todo.md`, and the series registration in `tools/recount.py` — and
both git checks are green over it: `git diff --check` reports no whitespace error and
`cross_check.py --queue-no 26 --no-run` accounts for every figure the tracked part of that diff
adds, zero rank-and-score pairs and zero standalone decimals. Every rank-and-score pair in this
file is quoted from the decision that measured it, so auditing this file as a draft slice needs
those decisions cited rather than re-measured: run whole, the file carries 29 pairs and 8
standalone decimals, and all 29 are found in the landed text of the eight decisions they name
— D-020, D-024, D-032, D-035, D-036, D-037, D-051 and D-059 — with no pair belonging to this
file itself. `recount.py` reports 65 contiguous decisions and
next D-066, with every series this landing's entry matches registered as measuring its condition
on no unit. Everything asserted above about this file was checked directly against its bytes.

**The landing's file list, stated so that a bulk stage becomes a detectable error.** D-065
declares a four-file landing: `open_code_decision_log.md`, `taxonomy_todo.md`,
`tools/recount.py` and this file. The worktree at landing time also carries changes that are
**not** part of it — `manual_review_v1/analysis/prompts/README.md` and
`manual_review_v1/analysis/prompts/landing_review_prompt.md`, which concern review-prompt
infrastructure and came from a concurrent session, alongside the long-standing untracked
`docs/Local/Reviews/`, `docs/Local/Synthesis/`, `docs/related_work/` and `references/` paths.
Negative control: a D-065 commit whose file list is not exactly those four paths — which is
what `git add .` or `git commit -a` would produce in this worktree — is rejected, because it
would sweep an undeclared file in and make D-065's own file list false. Legal control: a commit
staged over the explicit four-path list, leaving every other modified or untracked path
unstaged and uncommitted, so `git status` after staging still shows them. This assertion exists
because the round 1 review of this landing recorded that worktree drift as its observation
F-03, and because `taxonomy_todo.md` already carries the standing rule that landing must use an
explicit path list and must not `git add .`.

**The 30-unit partition is unchanged**, no mapping file exists, and no provisional CSV routing
column was read as a candidate mapping.
