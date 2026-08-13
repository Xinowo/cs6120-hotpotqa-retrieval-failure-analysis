---
status: draft
last_updated: 2026-08-13
---

# Candidate failure taxonomy v0.1 -- the category definitions behind `final_labels.csv`

This document is the citable source for the six category names, their definitions,
their evidence requirements and their boundaries, as used by
`results/annotations/manual_review_v1/final_labels.csv`.

## 0. What this document is, and what it is not

**It is** a compression of the full candidate-taxonomy document, which is in this
repository at `docs/manual_review_v1/candidate_taxonomy_v0_1.md`. That document is
1,600 lines written for the analysis workspace; this one carries the same categories
in the form a reader of the report needs. Every claim below can be checked against
the imported record without leaving this repository.

**It is not `taxonomy_v1`.** Section 8 of
`docs/specs/2026-07-27-manual-failure-review-course-protocol.md` reserves that name
for a jointly written and approved taxonomy. This document is a **candidate**
taxonomy: every category name in it is a candidate name, no boundary in it is
frozen, and it opens no gate. Its filename says `candidate` for that reason and it
is deliberately not called `taxonomy_v1.md`.

**It rules nothing.** Where this document and a later approved `taxonomy_v1`
disagree, `taxonomy_v1` wins and this document is superseded.

**No measurement was run to produce it.** No retrieval run, ranking, score
computation, corpus sweep, ablation or oracle injection was executed while writing
it. Every figure in it is transcribed from text that was already landed elsewhere;
the figures are reproduced here so they can be cited, not re-derived here.

## 1. Provenance

The category definitions, the required evidence, the inclusion and exclusion rules,
the tie-breaks, the examples, the counterexamples and the capability matrix are
human-authored research content. They were written and reviewed in
`docs/manual_review_v1/candidate_taxonomy_v0_1.md` sections 6 and 7, and landed as
decision entry **D-065** after three independent acceptance reviews of the document
and two of the landing.

Four landed decision entries govern what may be said with these categories, and are
cited by identifier throughout:

| Entry | What it fixed |
|---|---|
| **D-062** | The capability-boundary contract: the eight required fields per category, the closed value sets, and the rules on what a boundary value may rest on |
| **D-063** | One application of the candidate selection order to all 30 unit keys, and the rulings on the oracle-name test and the gold-targeted diagnostic class |
| **D-064** | The minimum-evidence correction: which categories carry a named evidence gap, and which of those gaps is an actionable request |
| **D-065** | The landing of the six category blocks and the capability matrix transcribed below |

Identifiers of the form `D-0nn` cite entries of the append-only decision log at
`docs/manual_review_v1/open_code_decision_log.md`, and `T-nn` cites triage items in
`docs/manual_review_v1/vocabulary_audit_triage.md`. Both are in this repository, as
are the secondary-descriptor registry, the vocabulary audit and the 19 per-unit
dossiers; `docs/manual_review_v1/README.md` says what each of them is.

## 2. Scope of the evidence base

Everything below rests on one read-only formal run and one manual review batch:

- run `2026-07-17_a`, two retrievers, evaluated cutoff fixed at 5;
- corpus: the 4,937-passage pooled corpus, formed by merging and de-duplicating the
  passage sets of 500 questions;
- BM25: one deliberately minimal bag-of-words implementation, titles excluded from
  the index, no stemming and no standard normalization;
- Dense: one symmetric `all-MiniLM-L6-v2` bi-encoder, mean pooling over the whole
  passage, L2 normalization, a 256-token window, no reranking and no cross-passage
  reasoning;
- two reviewers wrote 17 notes each, 34 review actions in total; 4 units were
  reviewed by both, so the batch is **30 unique analytical units**, 15 BM25 and 15
  Dense, over 24 bridge and 6 comparison questions;
- 19 of the 30 units carry a per-unit dossier; 11 do not and carry no factorial
  design.

**Consequence for every statement in this document.** This base supports bounded,
setup-scoped conclusions about the two evaluated implementations. It supports no
claim about BM25 as a family or about dense retrieval as a family, and the 30 counts
are calibration / open-coding counts, not prevalence estimates.

## 3. The analytical unit

A unit is one `(run_id, example_id, retriever)` triple. The full unit key used below
is `<example_id>|<retriever>`, where `run_id` is constant at `2026-07-17_a`.

The same `example_id` under BM25 and under Dense is **two different units** whose
evidence and whose label can differ. One `example_id` in this batch is exactly that
case: `5a78b209554299148911f93e|bm25` is a K1 member and
`5a78b209554299148911f93e|dense` is a K4 member.

## 4. Evidence typing, and what may never be a predicate

Only four kinds of fact satisfy any evidence requirement below.

| Tier | Meaning |
|---|---|
| **E1** deployable measurement | An intervention measured on that unit that needs no knowledge of which passages are gold |
| **E2** oracle measurement | An oracle intervention; it supports but never establishes, and any E1 result outranks it |
| **E2b** gold-targeted diagnostic | An intervention that adds no text and injects no answer information but requires knowing which passage is gold: the controlled content ablation with its equal-length control, and index-side family-removal probes. Admissible for a mechanism, **never** a deployable repair |
| **E3** verified content rule | A rule over passage text checked against the 4,937-passage pooled corpus |

Four things are **never** admissible as a predicate, in an inclusion rule, an
exclusion rule or a tie-break:

1. rank shape and rank position, including one-sided against two-sided crowding;
2. distance from the cutoff, which exists only as a descriptor and never as a
   mechanism;
3. corpus setting and retriever identity;
4. the mere presence of a descriptor in a reviewer's open codes, and the mere fact
   that a gate passed somewhere on the unit.

Evidence tiers, used by the tie-breaks: `enumerated` (a content property or an
enumerated match set, with no measured rank effect), `measured (E2)` or
`measured (E2b)`, `measured (E1)`, and `recovered` (a deployable condition placing
every required passage inside the evaluated cutoff).

## 5. The candidate primary-selection order

Each unit is taken through seven steps in this order, and stops at the first step
whose inclusion rules it satisfies. The order is deliberate: an evaluation-side
finding precedes any retrieval claim, and an implementation-layer finding precedes
any method-layer claim.

| Step | Destination | Why it sits here |
|---|---|---|
| 1 | K6 evaluation-side answer ambiguity | If the annotation is not the only chain satisfying the question inside the cutoff, the ranking behaviour is not a retrieval failure |
| 2 | K1 evaluated lexical implementation artifact | A repairable implementation decision must be excluded before any method claim |
| 3 | K5 mean-pooling content dilution | Gated by four conditions including an equal-length control |
| 4 | K2 description-only bridge entity | Content property of the question plus no decisive E1 result for a later category |
| 5 | K3 unresolved cross-passage conjunction | Requires an enumerated near-disjoint split and an opposite-signed deployable factor |
| 6 | K4 near-neighbour crowding and sense drift | Positive include rules only; there is no `otherwise` branch |
| 7 | `unresolved` | Reached when no step's include rules are satisfied, or on an unbroken tie |

## 6. The six candidate categories

Each category carries D-062's eight fields, then the judgement contract: definition,
required observable evidence, inclusion rules, exclusion rules, closest competing
category, tie-break, positive examples, at least one counterexample, and known
limitations.

`supporting_units` is the evidence set a capability boundary rests on. The
**primary-label unit count** is the disjoint partition that `final_labels.csv`
carries, and it is stated separately because it is not one of the eight fields. The
two differ for K5 only, 7 against 1.

---

### K1 -- `bm25_minimal_preprocessing_score_distortion`

| Field | Value |
|---|---|
| `failure_layer` | `implementation` |
| `retriever_scope` | `BM25` |
| `BM25_capability_boundary` | `implementation_recoverable` |
| `Dense_capability_boundary` | `not_applicable` |
| `decisive_counterfactual` | run |
| `claim_strength` | `implementation_supported` |
| `supporting_units` | 10, all BM25 |
| primary-label units | the same 10 |

`supporting_units`: `5a78b209554299148911f93e|bm25`, `5a79b7f6554299029c4b5f6f|bm25`,
`5a7c9f325542990527d554e6|bm25`, `5a7d61775542991319bc93b9|bm25`,
`5a83880e554299123d8c214e|bm25`, `5a83a532554299334474606f|bm25`,
`5ab72a025542992aa3b8c7b8|bm25`, `5abcc96c5542996583600492|bm25`,
`5ac1a3665542994ab5c67daf|bm25`, `5adc8977554299438c868de2|bm25`.

**Definition.** A required passage is pushed below the evaluated cutoff because of a
named decision in the evaluated lexical pipeline -- how text is normalized before it
is indexed, which field is indexed, or how repeated tokens score -- and not because
of what the corpus contains or what the question asks.

**Required observable evidence.** (i) The pipeline decision named and verified from
the implementation reference, not inferred. (ii) Either a deployable change measured
on the unit with its rank effect on each required passage, or an enumerated set of
matched-token false negatives between the query and a required passage's own text.
(iii) An exact baseline reconstruction, so the score decomposition is attributable.

**Inclusion rules.** Step 2's two clauses: the named decision verified from the
implementation, and its effect on the required passage's own matchable content.

**Exclusion rules.** The reverse boundary -- 0 rank positions for the minimal
gold-targeted normalization of a covered passage, or a negative corpus-wide
deployable score effect -- judged per required passage, with an unrun cell recorded
`not_applicable`. An opposite-signed repair across the two required passages. A
positive control whose gain is a side effect rather than the passage's own matchable
content. And a further value of an already covered normalization decision does not
warrant a new name inside this category.

**Closest competing category.** K4 on the lexical side; secondarily K3 on bridge
units.

**Tie-break.** Against K4: prefer K1 when the score deficit decomposes onto a named
normalization or index-field decision acting on the required passage's own matchable
content, and K4 when a content-defined competing family is the measured driver.
Against K3: prefer K3 when the deployable repair is opposite-signed across the two
required passages, or when the reverse boundary fires.

**Positive examples.** `5a83880e554299123d8c214e|bm25` -- a single non-oracle
query-side token change recovers both hops, with eleven non-oracle conditions
placing both required passages inside the cutoff, and a possessive token occurring
in 0 of 4,937 passages whose deletion reproduces the ranking bit for bit.
`5a79b7f6554299029c4b5f6f|bm25` -- every condition recovering both hops contains
both boundary punctuation and title indexing, both non-oracle.

**Counterexamples.** `5ade42b55542992fa25da717|bm25`: two surface-form false
negatives on the bridge hop are measured and real, and one factor moves that hop
from 15 to 5, yet the same factor drives the answer hop from 8 to 16 and the answer
hop has no surface-form mismatch to repair at all; the primary was refused and the
evidence retained through a narrower secondary. Second:
`5ae057fd55429945ae959328|bm25`, where the punctuation factor is negative for both
required passages.

**Known limitations.** Five of the ten units have no dossier and no factorial
design, so on those the mechanism is enumerated rather than measured as a rank
effect, and the reverse-boundary cells were measured on none of that batch. The
boundary between two lexical-mismatch descriptor names is triage item T-63 and
stays open; the fold of one into the other stays conditional on those cells, so this
category deliberately carries two primary names and its category name must not be
read as having performed that merge.

**What this row does not claim.** No method-level claim about BM25 or about lexical
retrieval as a family. Nothing is claimed about analyzers that perform standard
normalization, stemming or title indexing. The 10-unit concentration reflects one
deliberately minimal implementation. Recovery in full is demonstrated on two units;
on two others no non-oracle condition achieves it, so those units are covered by the
category and do not carry the recovery claim.

---

### K2 -- `description_only_bridge_entity`

| Field | Value |
|---|---|
| `failure_layer` | `method` |
| `retriever_scope` | `Dense`, observational only |
| `BM25_capability_boundary` | `not_established` |
| `Dense_capability_boundary` | `not_established` |
| `decisive_counterfactual` | run and valid on 4 of 4, as optional support |
| `claim_strength` | `observed` |
| `supporting_units` | 4, all Dense |
| primary-label units | the same 4 |

`supporting_units`: `5a85cead5542991dd0999ea9|dense`, `5add67915542992200553af8|dense`,
`5ade69e455429975fa854ec5|dense`, `5ae1f596554299234fd04372|dense`.

**Definition.** A required entity is identified in the question by description
rather than by name, and reaching the required passages depends on resolving that
description to the name, which the evaluated retrieval stage does not do. Where the
single-factor oracle-name test has been run and passes, it is the direct observation
of that dependence -- supplying the name brings both required passages inside the
cutoff -- and it is recorded as supporting evidence rather than as part of the
definition.

**Required observable evidence.** (i) The question text, showing the entity
described and not named. (ii) The unit's oracle state typed and recorded as one of
three states; what is required is the typing, not any particular value. (iii) Where
a form was run: the form itself -- one surface form of a required passage's own
entity name, injected alone -- with its preconditions verified, and the rank and
score of each required passage under it. (iv) A statement that no deployable
condition places every required passage inside the cutoff.

**Inclusion rules.** Step 4's two clauses, both necessary and neither sufficient:
the content property, and no E1 result on the unit decisive for another category.
**A valid oracle pass is not an inclusion rule.** Where the oracle state is
`not_run` or `not_applicable`, nothing is inferred in either direction and
membership turns on the two clauses alone.

**Exclusion rules.** The question names the target entity, however ineffectively, in
which case the residue routes to one of four narrower descriptor names or is
recorded without a descriptor. A **valid failure** of the oracle-name test -- both
preconditions verified, at least one form of each required passage's own name run,
and every form run failing -- which bars the primary and leaves the descriptor as a
secondary. A two-anchor condition or another entity's name is not a form of this
test. `not_run` and `not_applicable` are **not** exclusions and not failed include
clauses; reading a missing pass into this list as a further exclusion is forbidden.

**Closest competing category.** K3.

**Tie-break.** Ordered by evidence strength first and the oracle test second. A
valid failure bars K2 outright and becomes contributory evidence for K3. Short of
that bar, K3 takes the unit whenever its own clauses are satisfied on E1 evidence,
because a deployable measurement outranks the oracle support K2 rests on. Only where
the two categories stand at the same evidence tier does a valid pass do tie-break
work, as support for K2 and never as a bar against K3. Against K5: a deployable or
index-side condition that double-recovers outranks the oracle pass.

**Positive examples.** `5ade69e455429975fa854ec5|dense` -- five surface forms, two
complete titles, the bare name and two natural insertions, all placing the two
required passages at 1 and 3. `5ae1f596554299234fd04372|dense` -- seven forms pass.

**Counterexamples.** `5a81ebee554299676cceb16d|dense`: the oracle-name test passes
in five of seven forms and the unit is still not K2, because the query carries the
name, the required passage contains it, and it is unique in the 4,937-passage
corpus, yet a query reduced to that name ranks the passage 2202 of 4,937 and the
bare surname 4243. The first exclusion fires and the unit ends at K4, which is the
cleanest demonstration that a valid pass is not sufficient. Second:
`5ab48c325542996a3a969f93|dense`, where a six-form failure is valid and the bar
fires, refusing the category from the other direction.

**Known limitations.** The criterion is partly definitional: the oracle test was
used to assign this primary, so the separation from K3 is not independent
confirmation. Stated rather than hidden: a unit satisfying the content property
whose oracle test was never run **is** a member if no bar fires and no stronger E1
evidence carries another category, and it is a member whose whole evidence is the
question's own wording, at the `enumerated` tier. All four current members carry a
valid pass, so no in-sample member sits at that tier; the exposure is prospective.
One member ran one form only and title indexing was never measured there. Whether
the described entity may be the answer passage's own subject is T-08 and open.

**Named minimum evidence gaps: two, and exactly one is a request.** This is the only
category carrying any, and under D-064 it carries exactly two. (1) An actionable,
narrowly scoped request: the title-indexing condition on
`5a85cead5542991dd0999ea9|dense`, which is what would raise this category's Dense
boundary off `not_established`; **no endpoint value is ruled for it here**. (2) A
gap that is **not** a request and is larger: the absence of any BM25 unit on which
this descriptor is the decisive primary, which is what raising the BM25 boundary off
`not_established` would need. No such unit exists in the 30, so no measurement on an
existing unit can close it and no request is made for it. Neither is run here.

**What this row does not claim.** No claim that a dense retriever is unable to
resolve descriptions to entities. No claim that the mechanism is unable to arise on
BM25, and no inference from the absence of a BM25 primary use to a BM25 boundary of
any kind: `retriever_scope=Dense` records where the primary uses landed, not where
the mechanism can occur. The descriptor is in fact carried on seven BM25 units as a
secondary open code. A passing oracle test establishes nothing on its own and is not
required; four passing applications outside this category landed in K1, K4, K6 and
K5. No comparison-retriever success is used to strengthen anything.

---

### K3 -- `cross_passage_conjunction_unresolved`

| Field | Value |
|---|---|
| `failure_layer` | `method` |
| `retriever_scope` | `cross_retriever` |
| `BM25_capability_boundary` | `not_established` |
| `Dense_capability_boundary` | `not_established` |
| `decisive_counterfactual` | run, with one cell `not_applicable` |
| `claim_strength` | `observed` |
| `supporting_units` | 6, 3 BM25 and 3 Dense |
| primary-label units | the same 6 |

`supporting_units`: `5ade42b55542992fa25da717|bm25`, `5ae057fd55429945ae959328|bm25`,
`5ae60426554299546bf83019|bm25`, `5ab48c325542996a3a969f93|dense`,
`5ae0a59a55429945ae9593e2|dense`, `5ae1801955429901ffe4aec4|dense`.

**Definition.** A required fact exists only as a conjunction spanning two passages
-- the name or fact that identifies one required passage lives only inside the other
-- and the evaluated retrieval stage, which scores passages independently with no
cross-passage reasoning, does not assemble it.

**Required observable evidence.** (i) The question text and both required passages'
texts, showing where the intermediate fact lives. (ii) An enumerated split of the
two required passages' matched query-evidence sets into shared and unshared.
(iii) At least one deployable single factor measured with opposite signs across the
two required passages. (iv) The conditioned oracle-name result for each required
passage, or an explicit `not_applicable` with its ground.

**Inclusion rules.** Step 5's clauses (a) and (b) required, (c) contributory.

**Exclusion rules.** The required passage is not reachable from its own distinctive
cue, so the obstruction is the cue and not the join. A gold-knowledge-requiring
condition is the only refutation offered, which may limit confidence but may not
refuse the category. A single passage already supplies a complete answer, in which
case step 1 fires. An earlier step fired.

**Closest competing category.** K2.

**Tie-break.** The conditioned oracle-name test, in the failing direction. Where the
test is `not_applicable`, the near-disjointness clause carries the step and the claim
stays `observed`. Against K1 on BM25 units: prefer K3 when the deployable repair is
opposite-signed across hops.

**Positive examples.** `5ae60426554299546bf83019|bm25` -- 134 non-oracle conditions,
none placing both required passages inside the cutoff, and the reverse-boundary
cells refuse the preprocessing primary at 0 rank positions.
`5ade42b55542992fa25da717|bm25` -- matched sets sharing only four function words and
one topic word, six factors carrying opposite signs, and the series name occurring
nowhere in the query and only inside the bridge passage.

**Counterexample.** `5ab978855542996be2020512|dense`. It carries the descriptor as a
secondary and its oracle-name test failed, so the shape looks right. The exclusion
fires: a non-oracle probe makes the query exactly the verbatim epithet, and the one
passage that literally contains it reaches only rank 106, so that passage is not
reachable from its own distinctive cue, and a second probe shows the same cue
suppressing the other required passage. The mechanism is sense drift, not an
unassembled join.

**Why `not_established` and not `setup_scoped_method_boundary`.** On the BM25 side
the threshold is in fact met on all three units, and BM25 taken alone would support
a setup-scoped method boundary. Two things cap the category. First, the Dense side
has a live implementation-adjacent alternative on `5ae1801955429901ffe4aec4|dense`,
where the dilution gate passes on the constraint passage. Second, one BM25 unit
contributes no interpretable oracle evidence at all, so the BM25 evidence base is
two units with a verified oracle failure and one without. Splitting the category by
retriever to harvest the stronger claim is deliberately **not** done: that would be
structure driven by claim convenience rather than by mechanism.

**Known limitations.** One of the six units carries no interpretable oracle cell, so
five of six carry the oracle evidence. Two of the three BM25 units' factor designs
are bounded 16- and 19-cell designs rather than the 134-condition exhaustion behind
the third. Where the oracle contract text belongs is T-10 and stays open as a
placement question.

**What this row does not claim.** No claim that BM25 or Dense is unable to perform
multi-hop retrieval. The limit is that the conjunction is the binding constraint
under every deployable pipeline tested, which is not an impossibility. The
comparison retriever's success on any unit is not treated as causal proof, and
per-hop reachability is not asserted as a necessary threshold.

---

### K4 -- `near_neighbour_crowding_and_sense_drift`

| Field | Value |
|---|---|
| `failure_layer` | `method` |
| `retriever_scope` | `cross_retriever` |
| `BM25_capability_boundary` | `not_established` |
| `Dense_capability_boundary` | `not_established` |
| `decisive_counterfactual` | `not_run` for the category; run per unit on all five |
| `claim_strength` | `observed` |
| `supporting_units` | 5, 1 BM25 and 4 Dense |
| primary-label units | the same 5 |

`supporting_units`: `5a78b209554299148911f93e|dense`, `5a81ebee554299676cceb16d|dense`,
`5a8d93ad554299653c1aa13d|dense`, `5ab978855542996be2020512|dense`,
`5ab8f57b5542991b5579f097|bm25`.

**Definition.** A set of non-gold passages, definable by a rule over their own text,
outranks a required passage and the required passage's own decisive content is not
what distinguishes it; or a query cue resolves to a sense neighbourhood other than
its source passage's and suppresses a required passage.

**Sub-readings recorded, not split.** (A) near-duplicate documents and entity
variants; (B) a question's framing facet; (C) the sense neighbourhood of one cue --
semantic drift on an L2-normalized whole-passage dot product, explicitly not any
form of string, phrase or exact-string matching. The three are kept inside one
category because this is the weakest-controlled group and a three-way split would
manufacture structure the evidence does not carry. This is not a ruling that they
are one mechanism; the split re-opens at the freeze gate if mapping produces
separating evidence.

**Required observable evidence.** For shapes A and B: (i) the competing set
enumerated passage by passage, with each passage's own text quoted for the property
the rule names; (ii) the rule stated over passage content, with a check that it does
not also select a required passage; (iii) at least one measured intervention on that
family. For shape C: two non-oracle probes, one showing the cue's own neighbourhood
and one showing its suppression of the other required passage. Where the adopted
descriptors cover only part of an enumerated family, the uncovered members must be
named explicitly.

**Inclusion rules.** Step 6's clauses, shape A/B or shape C, together with the
crowding-family contract's two clauses for any crowding descriptor used as the
primary. Clause two -- that the family rule does not also select a required passage
-- must be **discharged**; an unchecked clause two is not an include, and the unit
routes to step 7 until it is discharged. Shape C carries no clause-two obligation.

**Exclusion rules.** The family rule also selects a required passage; the set is
stated as a rank range or position; an earlier step fired; or there is no content
family and no measured intervention, in which case the unit is `unresolved`. Plus
the passage-level boundary: the same passage set must not carry both of two
competing descriptor names, and a passage whose body verifies a real connection to
the queried entity **and** verifies a missing decisive constraint belongs to the
first of them.

**Closest competing category.** K1 on the lexical side and K3 on bridge units.

**Tie-break.** Against K1: the passage-level boundary, as under K1. Against K3:
prefer K3 when the required fact is a conjunction across passages and the two
required passages' matched-evidence sets are near-disjoint; prefer K4 when a
content-defined family above a required passage is measured and the required passage
is reachable from its own cue. Against K6: prefer K6 only when a within-cutoff
passage satisfies **every** explicit constraint; a partial match is K4.

**Positive examples.** `5a78b209554299148911f93e|dense` -- a fact check over the
4,937-passage corpus finds a content-only rule, excluding bodies that carry a
month-day-year date, that selects all six competitors and neither required passage,
and needs nothing from either required passage to write; removal probes measured.
`5ab8f57b5542991b5579f097|bm25` -- the family is 7 documents each stating its own
relationship in its own text, filling all 5 positions above one required passage and
7 of the 9 above the other; a position-free content rule over one name string selects
8 non-gold passages including all 7, with 0 occurrences in the required passage's own
body, which writes the name differently; dropping those 8 gives ranks 1 and 2, the
complement control gives 6 and 9, and a size-matched null control and a
statistics-matched control exclude corpus shrinkage and idf drift.
`5a81ebee554299676cceb16d|dense` -- the largest battery behind any member: all 42
passages above the bridge hop and all 51 between the two required passages read in
full, with the framing-family removal reaching rank 4 where its complement control
reaches only 40.

**Counterexamples.** `5a7d19d85542995ed0d165e8|dense`: ranks 1 to 9 are a redundant
same-team neighbourhood and the shape is exactly sub-reading A, yet the rule that
picks the family out also selects one of the required passages, so clause two fails
and the family cannot be removed even in principle; and no controlled text ablation
was run. It reaches `unresolved`, not K4. Second:
`5a76387d554299109176e6ba|dense`, where a content-stated family exists and no
intervention of any kind was measured. Between them the two show that the include
rule is a rule and not a summary of what the review notes concluded: one fails the
mandatory clause two, the other fails the measured-intervention clause, and each
carries a landed K4-family open code that this category declines.

**Why `method` and not `corpus`.** Two members carry an explicit landed
failure-layer statement and both say `method`, each ruling out implementation on
that unit's own measured grounds and treating corpus setting as provenance. No
landed entry for any unit this category holds states `corpus`. Corpus composition is
recorded as a mapping-level modifier, not as this category's explanatory layer.

**Known limitations.** This is the least-controlled category and the one most likely
to change at the freeze gate; its decisive counterfactual is `not_run` at category
level. The residual reading on the BM25 member is stated rather than buried: the
non-selection of the second gold follows from the containing set being reported as
non-gold rather than from a separately stated measured 0. A reader who declines that
reading routes the unit to `unresolved`, in which case K4 falls to 4 primary-label
units, all Dense, `retriever_scope` becomes `Dense`, and the BM25 boundary stays
`not_established` on no units rather than one. That contingency changes no boundary
**value** and no claim strength, which is why the admission is made in the open.
The compound member `5a8d93ad554299653c1aa13d|dense` has the weakest clause-(b)
satisfaction in the category: its interventions are query-side rewrites, which are
oracle diagnostics rather than family removals. T-20 and T-26 stay open.

**No minimum evidence gap is named for this category.** What would raise its two
boundaries off `not_established` is implementation alternatives excluded across the
category rather than per unit, and no scoped request for that is made here.

**What this row does not claim.** No capability claim about either retriever. Rank
shape -- one-sided against two-sided crowding -- is a description, not a cause. The
category does not claim that the competing family is removable in production: its
family probes are E2b, which may not be read as deployable repairs.

---

### K5 -- `dense_peripheral_passage_content_dilution`

| Field | Value |
|---|---|
| `failure_layer` | `method` |
| `retriever_scope` | `Dense` |
| `BM25_capability_boundary` | `not_applicable` |
| `Dense_capability_boundary` | `setup_scoped_method_boundary` |
| `decisive_counterfactual` | run; 9 applications, 7 passed, 2 rejected |
| `claim_strength` | `setup_scoped_method_supported` |
| `supporting_units` | 7, all Dense |
| primary-label units | **1** |

`supporting_units`: `5a78b209554299148911f93e|dense`, `5a81ebee554299676cceb16d|dense`,
`5add67915542992200553af8|dense`, `5ade69e455429975fa854ec5|dense`,
`5ae048a255429924de1b708e|dense`, `5ae1801955429901ffe4aec4|dense`,
`5ae1f596554299234fd04372|dense`. Primary-label unit:
`5ae048a255429924de1b708e|dense`. This is the one category whose two sets differ.

**Definition.** Decisive content in a long required passage is averaged against
peripheral content in the passage's own mean-pooled whole-passage vector, so the
passage scores below competitors, and removing the peripheral content raises it
while removing an equal length of decisive content does not.

**Required observable evidence.** All four gate conditions, each with its figures:
mean pooling read from the implementation rather than inferred; the controlled
ablation's rank and score; the **equal-length** control ablation's rank and score,
decontaminated word by word rather than sentence by sentence; and the passage's
token count against the 256-token window. For primary use, additionally the
ablation's effect on **every** required passage.

**Inclusion rules.** Step 3's two clauses.

**Exclusion rules.** Any of the four gate conditions fails. No equal-length control
exists, in which case the gate must not be applied at all. The ablation does not
place every required passage inside the cutoff, in which case the name is a
secondary and the unit routes on. A lexical backend, where the descriptor's own
exclusion fires.

**Closest competing category.** K2.

**Tie-break.** Prefer K5 when the deployable-side ablation ceiling places every
required passage inside the cutoff; prefer K2 when only an oracle-name form does.
Where both a passing gate and a passing oracle test are present and neither reaches
the ceiling, the general tie-break applies and the unit routes on.

**Positive examples.** `5ae048a255429924de1b708e|dense` -- the primary-label unit,
gate passed and ceiling reached at ranks 3 and 1.
`5ae1f596554299234fd04372|dense` and `5add67915542992200553af8|dense` -- the gate
passes on **both** required passages on each, which is the mechanism at full
strength; the ceiling is not reached, so the descriptor is a secondary there and the
units are supporting rather than primary-label. The distinction is stated because a
positive example for this category's *mechanism* and for its *primary use* are not
the same set.

**Counterexamples.** `5ae0a59a55429945ae9593e2|dense` and
`5ab48c325542996a3a969f93|dense` -- the gate is rejected on both, so the category has
a real counterexample set of two rather than an unfalsified rule. Third:
`5ae1801955429901ffe4aec4|dense`, where the gate passes on the constraint passage
and fails on the answer passage, so it is one application, one pass and no primary.

**Known limitations.** One primary-label unit only. The gate's generalisation is a
**floor** -- no other Dense content claim may be adopted without all four conditions
-- and never a licence for a primary. Where the gate's text belongs across the
registry is T-40 and stays open as a placement question. The converse gap, a
required passage's own measurable property left with no carrier once the gate
rejects, is T-45 and open.

**No minimum evidence gap is named for this category.** Its BM25 boundary is
`not_applicable` and its Dense boundary is already `setup_scoped_method_boundary`, so
no boundary of it is blocked by a missing measurement.

**What this row does not claim.** No claim about dense retrieval generally, about
other pooling strategies, about rerankers, or about longer context windows. The
controlled ablation is a **diagnostic, not a deployable repair** -- it removes
content from a required passage, which no pipeline can do -- so the conclusion is not
pushed to implementation level by it. On the primary-label unit title indexing is
materially positive and by itself flips `any@5`; that alternative was measured and
refused on its own grounds rather than ignored. The category keeps
`setup_scoped_method_supported` because its implementation alternatives were measured
and refused, not because its ablation is deployable.

---

### K6 -- `evaluation_side_gold_chain_ambiguity`

| Field | Value |
|---|---|
| `failure_layer` | `evaluation` |
| `retriever_scope` | `cross_retriever` |
| `BM25_capability_boundary` | `not_applicable`, because a non-method layer makes no capability claim |
| `Dense_capability_boundary` | `not_applicable`, same ground |
| `decisive_counterfactual` | partially run |
| `claim_strength` | `observed` |
| `supporting_units` | 2, 1 BM25 and 1 Dense |
| primary-label units | the same 2 |

`supporting_units`: `5a83aaeb5542996488c2e483|dense`, `5adf58f15542993a75d264d2|bm25`.

**Definition.** Inside the evaluated cutoff there is a non-gold passage that
satisfies every explicit constraint of the question, so the metric's gold-title miss
does not establish an answer-retrieval failure.

**Required observable evidence.** The qualifying passage identified by title, rank
and score; the question's explicit constraints enumerated and each shown satisfied by
that passage's own text; the evidentiary standard shown to be the same one the
annotated chain uses; and the annotated golds' ranks.

**Inclusion rules.** Step 1's include clause.

**Exclusion rules.** The qualifying passage lies outside the cutoff (T-51 open). It
substitutes an intermediate annotated passage rather than answering the question --
that is a separate descriptor, a secondary on five units and a primary on none. It
satisfies only part of the question, which is K4. And no descriptor naming a defect,
ambiguity or underspecification of the **question** may be used here; such
observations route elsewhere, and an unroutable residue is recorded as a measured
fact without a name.

**Closest competing category.** K4.

**Tie-break.** Prefer K6 only when a within-cutoff passage satisfies **every**
explicit constraint in one passage; a partial match is crowding and belongs to K4.
Against K5 and K2: step 1 precedes both, because if the annotation is not unique the
ranking behaviour is not a retrieval failure.

**Positive examples.** `5a83aaeb5542996488c2e483|dense` -- a studio-album passage at
rank 1 satisfying all explicit constraints in one passage, with the annotated golds
at 6 and 7. `5adf58f15542993a75d264d2|bm25` -- an alternative answer at rank 3 that
survives every repair across 112 labelled rows, of which 101 are measured.

**Counterexamples.** `5adc8977554299438c868de2|bm25`: four non-gold passages supply
the same intermediate fact under the gold's own evidence standard and two of them sit
inside the cutoff, at ranks 1 and 4, so the surface shape is a within-cutoff
alternative. The exclusion fires -- they substitute an intermediate passage rather
than answering the question -- and the unit ends at K1. Second:
`5ade42b55542992fa25da717|bm25`, where a full-corpus substring scan leaves neither
required passage any substitute at all, so both evaluation names are recorded as
inapplicable.

**Known limitations.** Two units, one of them with no control series and no dossier.
Whether a substitute outside the cutoff counts is T-51 and open. The category's final
name is a naming-pass question; the name used here is written on the evaluation side
as required.

**What this row does not claim.** No capability claim about either retriever. It is
not a claim that the questions are defective; question-quality descriptors are
forbidden here and two of them were deleted during open coding. It is a statement
that the annotated gold chain is not the only chain satisfying the question inside
the evaluated cutoff.

## 7. `unresolved`

`unresolved` is a legitimate assignment and a real destination, per the annotation
guideline's rule that an unsupported decision must not be forced, and per section 8
of the course protocol. It is reached in exactly two ways: no step's include rules
fire, with the failing predicate recorded per unit; or two categories' include rules
are satisfied at the same evidence tier and the tie-break does not separate them.

An `unresolved` output is a **completeness property of the rule set, not a gap in
it**: a rule set that had to guess in order to avoid `unresolved` would be the
incomplete one.

Two units in this batch are `unresolved`, and they fail on **different** predicates,
which is why each is recorded per unit rather than pooled. Both were reviewed: the
first carries two reviewers' notes plus a joint note, the second one reviewer's note
plus a joint note. `unresolved` records missing *counterfactual evidence*, not
missing review.

The two are listed as labelled blocks rather than as a table, because a full unit key
contains `|`, which a Markdown table cell would require escaping, and an escaped key
is not the key.

**`5a76387d554299109176e6ba|dense`** -- comparison question; open code carried,
`two_named_entities_underprioritized`. Step 6's fourth exclusion fires. A family is
stated as passage content -- generic person and birth-related material -- but **no
intervention of any kind was measured** on the unit, and the landed entry states that
the ranking does not establish which internal component caused the ordering. The unit
carries no ordinal-series membership at all. It is also one of the four
double-reviewed units.

**`5a7d19d85542995ed0d165e8|dense`** -- bridge question; open code carried,
`same_entity_variant_crowding`. The crowding contract's second clause fails and is
not discharged: the family rule also selects one of the required passages, so the
family cannot be removed even in principle and the claim is untestable by any
intervention. No later decision rules the clause on this unit, and no controlled
ablation was run.

## 8. Category x BM25/Dense capability-boundary matrix

| Category | `failure_layer` | `retriever_scope` | `BM25_capability_boundary` | `Dense_capability_boundary` | BM25 units | Dense units | `claim_strength` |
|---|---|---|---|---|---:|---:|---|
| K1 `bm25_minimal_preprocessing_score_distortion` | `implementation` | `BM25` | `implementation_recoverable` | `not_applicable` | 10 | 0 | `implementation_supported` |
| K2 `description_only_bridge_entity` | `method` | `Dense` | `not_established` | `not_established` | 0 | 4 | `observed` |
| K3 `cross_passage_conjunction_unresolved` | `method` | `cross_retriever` | `not_established` | `not_established` | 3 | 3 | `observed` |
| K4 `near_neighbour_crowding_and_sense_drift` | `method` | `cross_retriever` | `not_established` | `not_established` | 1 | 4 | `observed` |
| K5 `dense_peripheral_passage_content_dilution` | `method` | `Dense` | `not_applicable` | `setup_scoped_method_boundary` | 0 | 1 | `setup_scoped_method_supported` |
| K6 `evaluation_side_gold_chain_ambiguity` | `evaluation` | `cross_retriever` | `not_applicable` | `not_applicable` | 1 | 1 | `observed` |
| -- `unresolved` | -- | -- | -- | -- | 0 | 2 | -- |

The two unit columns are **primary-label** counts: 10 + 4 + 6 + 5 + 1 + 2 = 28, plus
the 2 `unresolved` = 30, splitting 15 BM25 and 15 Dense.

**When a boundary may read `not_applicable`.** `not_applicable` asserts that the
category's mechanism cannot arise on that backend. It is legal on exactly two
grounds and no other: a backend property makes the mechanism impossible (K1's Dense
cell, since no tokenizer, normalization or indexed-field artifact exists on the
evaluated bi-encoder, which strips accents and case; K5's BM25 cell, where the
descriptor's own exclusion places length effects in the scorer's normalization
term); or the category is not a method-layer category and therefore makes no
capability claim at all (K6's two cells).

**Absence of primary uses on a backend is never a ground.** `retriever_scope` is
observational, and a descriptor whose definition states a property of the question
and the required passage is measurable on both backends. The correct value when a
backend carries no primary use is `not_established`, which records **missing
evidence** rather than asserting inapplicability. That is why K2's BM25 cell and
K4's BM25 cell read `not_established`, and why three of the six categories carry
`not_established` on both backends.

**The implementation-induced row makes no method-limit claim on either method.** K1
is the only `implementation`-layer category. Its BM25 cell states a repairable
implementation decision, not a limit of lexical retrieval as a method; its Dense
cell asserts that the mechanism cannot arise on that backend and therefore also
asserts no method limit. A successful preprocessing or indexing repair keeps a
conclusion at implementation level regardless of how many units share the symptom.

**Closed value sets.** `failure_layer` is one of `implementation`, `method`,
`corpus`, `evaluation`, exactly one per category, with no fifth value and no
`compound`. Each capability boundary is one of `implementation_recoverable`,
`setup_scoped_method_boundary`, `not_established`, `not_applicable`, each with a
supporting sentence. `claim_strength` is one of `observed`,
`implementation_supported`, `setup_scoped_method_supported`. A missing decisive
counterfactual is recorded as `not_run` and **caps `claim_strength` at `observed`**;
K4 is the instance.

**Scope caveat, applying to every row.** One pooled run; one deliberately minimal
bag-of-words BM25 implementation with titles excluded from the index; one symmetric
`all-MiniLM-L6-v2` bi-encoder with mean pooling, L2 normalization, a 256-token
window and no reranking; 30 jointly reviewed units, 15 per retriever, 24 bridge and
6 comparison questions; 19 of the 30 with a dossier. Nothing in this table is a
claim about BM25 or dense retrieval in general.

## 9. Three framing rules any report using these labels must obey

1. **The denominator is always 30**, and the counts are **calibration / open-coding
   counts, never prevalence estimates**. Reviewer row counts -- 34 review actions by
   two reviewers over 30 unique units -- may be reported separately as workload or
   overlap evidence, but never as category prevalence.
2. **No unqualified claim of the form "BM25 cannot ..." or "Dense cannot ..."**
   anywhere. Only K1 reaches `implementation_supported` and only K5 reaches
   `setup_scoped_method_supported`; the other four categories stay at `observed`.
3. **Comparison-retriever success alone never strengthens a claim.** That one
   retriever placed a required passage inside the cutoff is an observation about
   this bounded sample, not evidence about the other retriever's limits.

## 10. Calibration counts for the batch

Computed only from the 30 rows of `results/annotations/manual_review_v1/final_labels.csv`.

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

Named-category counts 28 plus the `unresolved` count 2 equal 30, which is the
protocol's arithmetic condition on that file.

## 11. The label vocabulary of `final_labels.csv`

`final_label` takes exactly one of these seven values, and no other:

```text
bm25_minimal_preprocessing_score_distortion
description_only_bridge_entity
cross_passage_conjunction_unresolved
near_neighbour_crowding_and_sense_drift
dense_peripheral_passage_content_dilution
evaluation_side_gold_chain_ambiguity
unresolved
```

Every one of the six category names is a **candidate** name from this document, not
an approved `taxonomy_v1` name. `resolution` takes one of `single_review`,
`overlap_agreed`, `overlap_resolved`, `unresolved`, per section 8 of the course
protocol; in this batch `overlap_agreed` is unused, because each of the four
double-reviewed units carries an owner decision that chose between competing
readings rather than a plain agreement. Where a unit's category outcome is
`unresolved`, `resolution` reads `unresolved` rather than its review provenance,
which is the protocol's own rule that the outcome is one resolved category or one
`unresolved` unit and never two votes.

**The file carries no reason column**, because the protocol fixes its five columns and
a sixth may not be added. So a row reading `unresolved` says only that no category's
include rules were reached. **Which clause failed, on which unit, is in section 7
above**, and the landed per-unit wording is in
`docs/manual_review_v1/candidate_taxonomy_v0_1.md` section 18 and in the decision log
entry that ruled it. Neither `unresolved` row should be read as an unreviewed unit:
both were reviewed, one of them by both reviewers.

## 12. Limitations of this document

These are the limitations a report citing this document must state.

- **The taxonomy is not frozen.** This is a candidate taxonomy and every category
  name in it is a candidate name. `taxonomy_v1` does not exist.
- **No independent per-unit mapping pass was run.** The full process specifies three
  separate passes over all 30 units. None was run. The 30 labels are a transcription
  of one landed application of the selection order, not an independent re-derivation
  of it.
- **No boundary stress-test was run.** No category boundary was stressed, revised or
  confirmed by a second pass.
- **11 of the 30 units carry no dossier and no factorial design**, so on those the
  mechanism is enumerated rather than measured as a rank effect.
- **K4 is the weakest-controlled category** and the one most likely to change at a
  freeze gate; its decisive counterfactual is `not_run` at category level.
- **Twelve triage items remain open** in
  `docs/manual_review_v1/vocabulary_audit_triage.md`, including the placement
  questions T-10 and T-40 and the boundary questions T-08, T-51 and T-63 cited above.
- **One judgement call is exposed rather than hidden**, in K4's known limitations:
  declining the residual reading on the single BM25 member routes it to `unresolved`
  and changes that category's counts, though no boundary value and no claim strength.

## 13. Where the fuller record lives

All of it is in this repository. This document carries what a reader needs in order
to check a label against a definition; the files below carry the derivation behind
every figure.

| Record | Path |
|---|---|
| The full candidate taxonomy, 1,600 lines | `docs/manual_review_v1/candidate_taxonomy_v0_1.md` |
| The append-only open-coding decision log, `D-0nn` | `docs/manual_review_v1/open_code_decision_log.md` |
| The vocabulary audit and its triage table, `T-nn` | `docs/manual_review_v1/open_code_vocabulary_audit.md`, `docs/manual_review_v1/vocabulary_audit_triage.md` |
| The secondary-descriptor registry | `docs/manual_review_v1/secondary_descriptor_registry.md` |
| The 19 per-unit dossiers | `docs/manual_review_v1/per_case_analysis/` |
| The 30-unit evidence table, with both reviewers' verbatim notes | `results/annotations/manual_review_v1/case_memos_v2.csv` |
| The implementation references the evidence rules cite | `docs/manual_review_v1/references/` |
| The full process this compressed path did not run | `docs/manual_review_v1/taxonomy_todo.md` |
| The compressed path's own account | `docs/manual_review_v1/express_closeout_v0_1.md` |
| What each imported file is | `docs/manual_review_v1/README.md` |
