---
status: active
last_updated: 2026-08-13
---

# Manual review v1 -- qualitative failure analysis

What the 30 reviewed retrieval failures actually consist of, what the evidence
behind each group supports, and what it does not support.

Category definitions are in `docs/taxonomy_candidate_v0_1.md`. The counts come from
`results/annotations/manual_review_v1/category_counts.csv`, which is recomputed from
the 30 rows of `final_labels.csv` by
`scripts/reporting/manual_review_category_counts.py`. How the review was run is in
`docs/manual_review_v1_open_coding_memo.md`.

**Read every count below as a calibration / open-coding count over a denominator of
30.** None of them is a prevalence estimate. Every conclusion is scoped to one
pooled run, one deliberately minimal bag-of-words BM25 implementation with titles
excluded from the index, and one symmetric `all-MiniLM-L6-v2` bi-encoder with mean
pooling, L2 normalization, a 256-token window and no reranking.

## 1. Findings

**1. The largest single group is an implementation artifact, and the strongest thing
we can say about it is that it is repairable.** Ten of the 30 units, all on the
lexical side, fail because of named decisions in the evaluated BM25 pipeline: titles
are not indexed, tokenization is lowercase whitespace splitting with no punctuation
normalization, and the scorer accumulates every occurrence of a query token, so
function words repeated in a query buy a passage large amounts of score. On two of
the ten, a single non-oracle change recovers **both** required passages into the top
5; on one of those, eleven different non-oracle conditions do. That is an
implementation-level result, and it stays at implementation level no matter how many
units share the symptom. It is not a finding about lexical retrieval as a method.

**2. On the dense side the failures are about what the vector averages, not about
which tokens overlap.** Four units fail because the question identifies a required
entity only by description, and supplying that entity's own name -- one surface form,
injected alone -- brings both required passages inside the cutoff. One unit fails
because decisive content in a long required passage is averaged against peripheral
content in the same mean-pooled vector: removing the peripheral content lifts the
passage to rank 3 and its partner to rank 1, while removing an equal length of
decisive content does not. Four of the five crowding units are dense. None of these
is a claim that a bi-encoder is unable to do the thing; each is a measured
observation about this encoder in this setup.

**3. On six units the binding constraint is a conjunction that spans two passages.**
The fact that identifies one required passage lives only inside the other, and a
retrieval stage that scores passages independently does not assemble it. On one unit
134 non-oracle conditions were tried and none placed both required passages inside
the cutoff; the only condition that did is gold-targeted and explicitly not
deployable. The honest wording is the one the evidence supports: the conjunction is
the binding constraint under every deployable pipeline tested. That is not an
impossibility claim about either retriever.

**4. Two of the 30 are not retrieval failures at all.** Inside the evaluated cutoff
there is a non-gold passage that satisfies every explicit constraint of the question,
under the same evidentiary standard the annotated chain itself uses. On one of them
the qualifying passage is at rank 1 while the annotated golds sit at 6 and 7. The
metric's gold-title miss does not establish an answer-retrieval failure there. This
is a measurement finding, not a claim that the questions are defective -- no
question-quality descriptor is used anywhere in this taxonomy.

**5. Two of the 30 are `unresolved`, and that is a result rather than a gap.** Both
were fully reviewed, both carry a plausible crowding story, and each fails a different
mandatory clause of the crowding category.

On `5a76387d554299109176e6ba|dense`, "Who was born first Am Rong or Ava DuVernay?",
the competing family is stated as passage content -- generic person and birth-related
material -- but **no intervention of any kind was measured** on the unit, and the
owner decision records that the ranking does not establish which component caused the
ordering. The measured-intervention clause fails. What the evidence cannot separate is
named in the unit's own memo: weak entity representations against a general limitation
of short, name-dominated comparison queries.

On `5a7d19d85542995ed0d165e8|dense`, "The Tennessee Volunteers football team plays as a
member for a conference in what city?", the failure is stronger than an unrun
measurement. **The question names no season**, so any content rule that picks out the
competing family of Tennessee Volunteers season pages also selects the annotated 1984
season page, which is one of the required passages. The family therefore cannot be
removed even in principle and the claim is untestable by any intervention, so the
clause is not merely unchecked but undischargeable as written.

The difference matters: the first is a gap that one measurement could close, the second
is a gap that no measurement on this unit can close. A rule set that had to guess in
order to avoid `unresolved` would be the incomplete one.

## 2. One question, two retrievers, two different mechanisms

This is the clearest single demonstration that the analytical unit has to be
`(example_id, retriever)` and not the question.

Question, verbatim:

```text
Which playwright lived a longer life, Edward Albee or J. M. Barrie?
```

It is a comparison question with no bridge hop. Each gold independently supplies one
lifespan fact and neither alone answers the question, so the criterion is `full@5`:
both passages must be inside the top 5. Albee lived 1928 to 2016, 88 years; Barrie
1860 to 1937, 77 years; the answer is Albee.

**BM25, stored formal results.**

| rank | title | score |
|---:|---|---:|
| 1 | Reed A. Albee | 28.259323 |
| 2 | Edward F. Albee Foundation | 26.509451 |
| 3 | Edward Albee's At Home at the Zoo | 20.918302 |
| 4 | Jack Gelber | 19.964317 |
| 5 | Finding the Sun | 19.757164 |
| 6 | **Edward Albee (GOLD)** | 19.520331 |
| 7 | Oppenheimer Award | 16.907052 |
| 8 | The Zoo Story | 14.680838 |

`J. M. Barrie` is not in the stored top 50 at all; its position in the full pooled
corpus is 640, at 4.908864. The mechanism is lexical and named: the query tokens are
`j.`, `m.` and `barrie?`, while the Barrie passage's own text writes `james`,
`matthew` and `barrie,`. Because titles are not indexed, the one field that would
have carried the exact name form is not searched, so nothing in the pipeline can
repair the mismatch. `J. Edward Snyder` at rank 15, at 12.738431, is the artifact in
miniature: it outranks the Barrie passage by matching `j.` from one queried entity
and `edward` from the other. The Albee cluster at ranks 1 to 8 was recorded as a
downstream ranking effect, not promoted to the cause. Label:
`bm25_minimal_preprocessing_score_distortion`.

**Dense, stored formal results.**

| rank | title | score |
|---:|---|---:|
| 1 | Reed A. Albee | 0.630886 |
| 2 | Finding the Sun | 0.597466 |
| 3 | Edward F. Albee Foundation | 0.567801 |
| 4 | Edward Albee's At Home at the Zoo | 0.542102 |
| 5 | The Zoo Story | 0.538556 |
| 6 | Three Tall Women | 0.519974 |
| 7 | Jeffrey Stanley | 0.501423 |
| 8 | **J. M. Barrie (GOLD)** | 0.434342 |
| 9 | **Edward Albee (GOLD)** | 0.432454 |

Both golds are retrieved, adjacently, just outside the cutoff -- and the mechanism is
completely different from the BM25 one. There is no tokenization artifact to find:
this encoder strips accents and case, so the name-form mismatch that drives the BM25
failure cannot arise here. What was measured instead is a content-defined competing
family. A rule written over passage text alone -- exclude bodies that carry a
month-day-year date -- selects all six competitors above the golds and **neither**
required passage, and the rule needs nothing from either gold to write, which is what
makes it a family rather than a description of the ranking. The passages that could
answer a "who lived longer" question are exactly the ones carrying full dates, and
they are the ones the ranking placed below same-topic passages that carry none.
Removal probes on that family were measured. Label:
`near_neighbour_crowding_and_sense_drift`.

**Two cautions on this example, both deliberate.**

First, do not read the dense side as a near miss. The rank-5 score is 0.538556, so
the two golds sit 19.351 percent and 19.701 percent below the cutoff score. This
project's accepted near-miss band is 1.156 percent to 4.503 percent; a 19 percent
shortfall is outside it, and "it only just missed" would be a false description.

Second, neither retriever's behaviour is used to strengthen a claim about the other.
That BM25 placed one gold at 6 while Dense placed both at 8 and 9 says nothing about
either method's limits; it is why the two units carry two different labels rather
than one shared explanation.

**Where these two tables can be checked.** The dense side, rank by rank, is in
`docs/manual_review_v1/open_code_decision_log.md`, entry D-027, which carries every
passage above the two golds with its score -- from `Reed A. Albee` at 1 / 0.630886 down
to `Jeffrey Stanley` at 7 / 0.501423 -- the rank-5 cutoff score of 0.538556, and the
golds themselves at 8 / 0.434342 and 9 / 0.432454. The per-unit dossier
`docs/manual_review_v1/per_case_analysis/dense_comparison_5a78b209554299148911f93e.md`
reports the same figures, but it is one of the dossiers held locally rather than in
Git; see `docs/manual_review_v1/README.md`, "What is held locally".
The BM25 side has no dossier -- it is one of the 11 units without one -- so its
mechanism and rank figures are in the same log, entry D-010 for the mechanism and
D-027 for `Edward Albee` at 6 / 19.520331 and `J. M. Barrie` at 640 / 4.908864, the
latter establishing that the stored `not_in_top50` is a real rank of 640 of 4,937 and
not absence from the corpus. Both units' review notes, gold ranks and open codes are
in `results/annotations/manual_review_v1/case_memos_v2.csv`.

*Caliber note.* The retrieval output holds the Albee dense score as
`0.43245452642440796`, which rounds at six decimals to `0.432455`; the landed
decision entry and the per-unit dossier both write `0.432454`, and the landed form is
the one used above.

## 3. The six groups, read one at a time

| Group | Count | BM25 | Dense | Layer | Strongest claim it supports |
|---|---:|---:|---:|---|---|
| `bm25_minimal_preprocessing_score_distortion` | 10 | 10 | 0 | implementation | `implementation_supported` |
| `cross_passage_conjunction_unresolved` | 6 | 3 | 3 | method | `observed` |
| `near_neighbour_crowding_and_sense_drift` | 5 | 1 | 4 | method | `observed` |
| `description_only_bridge_entity` | 4 | 0 | 4 | method | `observed` |
| `evaluation_side_gold_chain_ambiguity` | 2 | 1 | 1 | evaluation | `observed` |
| `dense_peripheral_passage_content_dilution` | 1 | 0 | 1 | method | `setup_scoped_method_supported` |
| `unresolved` | 2 | 0 | 2 | -- | -- |
| **TOTAL** | **30** | **15** | **15** | | |

**Minimal preprocessing score distortion, 10 units.** Three named decisions do the
work: unindexed titles, whitespace-only tokenization with no punctuation handling,
and per-occurrence score accumulation. The clearest single reconstruction is the
Bharatpur unit, where rank 3 draws 23.07 of its 41.85 points from `of` and `the`
alone while failing to match the query token `bharatpur,`. Recovery in full is
demonstrated on two of the ten; on two others no non-oracle condition achieves it,
and those units are covered by the group without carrying the recovery claim. Five
of the ten have no dossier and no factorial design, so on those the mechanism is
enumerated from text rather than measured as a rank effect.

**Cross-passage conjunction unresolved, 6 units.** The evidence pattern is an
enumerated split of the two required passages' matched query evidence into shared and
unshared, plus at least one deployable factor that helps one required passage and
hurts the other. On the strongest member the two matched sets share only four
function words and one topic word, six factors carry opposite signs across the hops,
and the series name that would join them occurs nowhere in the query and only inside
the bridge passage. Both boundaries read `not_established`, deliberately: the BM25
side alone would support a setup-scoped method boundary, but one dense member still
has a live dilution alternative and one BM25 member contributes no interpretable
oracle evidence, and splitting the group by retriever to harvest the stronger claim
would be structure driven by convenience rather than by mechanism.

**Near-neighbour crowding and sense drift, 5 units.** Three sub-readings are recorded
inside one group rather than split: near-duplicate documents and entity variants, a
question's framing facet, and the sense neighbourhood of a single cue. This is the
least-controlled group in the project and the one most likely to change if the
taxonomy is stress-tested. Its category-level decisive counterfactual is `not_run`,
which caps its claim at `observed` by contract even though all five members carry
per-unit diagnostics. The largest battery behind any member read all 42 passages
above one required passage and all 51 between the two in full.

**Description-only bridge entity, 4 units.** The question describes a required entity
instead of naming it. Where an oracle-name form was run and passes, it is the direct
observation of the dependence: on one member, five surface forms -- two complete
titles, the bare name and two natural insertions -- all place the required passages
at 1 and 3; on another, seven forms pass. The pass is **support and not a membership
condition**: a valid failure bars the group, a pass raises a member's evidence tier,
and an unrun test infers nothing in either direction. The clearest counterexample is
a unit where the oracle test passes in five of seven forms and the unit still is not
a member, because the query already carries the name and the required passage
contains it, yet a query reduced to that name ranks the passage 2202 of 4,937.

**Evaluation-side gold chain ambiguity, 2 units.** Discussed under finding 4. The
group makes no capability claim about either retriever, because it is not a
method-layer group. Its exclusions are what keep it narrow: a passage that
substitutes an intermediate annotated fact rather than answering the question does
not qualify, and neither does one that satisfies only part of the question.

**Dense peripheral passage content dilution, 1 primary unit, 7 supporting.** The
strongest control in the project, and the only group reaching
`setup_scoped_method_supported`. Its four-condition gate requires mean pooling
verified from the implementation, a controlled ablation that materially raises rank,
an **equal-length** control ablation that does not, and a passage that does not hit
the 256-token truncation. Nine applications, seven passed, two rejected -- so the
group has a real counterexample set rather than an unfalsified rule. It reaches only
one primary label because the ceiling condition, placing every required passage
inside the cutoff, is met on one unit. Its ablation is a diagnostic and not a
deployable repair: no pipeline can delete content from a passage it is trying to
retrieve.

## 4. What the counts mean, and what they do not

The denominator is always 30. Named-category counts, 28, plus the `unresolved`
count, 2, equal 30, which is the arithmetic condition the protocol places on the
label file. The 34 review actions by two reviewers are workload and overlap evidence
and are never reported as category prevalence.

Three categories carry `not_established` on **both** backends. That value records
**missing evidence**, not inapplicability. It is used precisely where a mechanism is
plainly available on a backend but this batch contains no primary use of it there,
or no measurement that would rule out the implementation alternatives. The
`not_applicable` value is stronger and is used on only two grounds: a backend
property makes the mechanism impossible -- no tokenizer or indexed-field artifact
exists on the evaluated bi-encoder -- or the group is not a method-layer group at
all. The absence of primary uses on a backend is never a ground for it.

## 5. Strengths of the method

- **Evidence typing before conclusions.** Four admissible kinds of fact, an explicit
  ranking among them, and four things that may never serve as a predicate -- rank
  shape, distance from the cutoff, retriever identity, and the mere presence of a
  descriptor in a note.
- **Positive inclusion rules, with `unresolved` as a real destination.** Two units
  reach it, and each names the specific clause it fails. A taxonomy whose categories
  had an `otherwise` branch would have absorbed both and looked more complete than
  the evidence is.
- **Claim strength is contractual, not rhetorical.** A missing decisive
  counterfactual is recorded and caps the claim; a successful repair pins the
  conclusion at implementation level; oracle evidence supports without establishing.
- **The artifacts are checkable rather than trusted.** The label file's schema,
  cardinality and vocabulary, and the counts derived from it, are re-derived and
  byte-compared by `scripts/reporting/manual_review_category_counts.py --check`, and
  its unit tests exercise both halves of each rejection pair.

## 6. Challenges encountered

- **Eleven of the 30 units have no dossier and no factorial design.** Every predicate
  satisfied by an enumerated match set rather than a measured rank effect falls on
  that batch, and it is the single largest limit on evidence quality here.
- **One category's criterion is partly definitional.** The oracle-name test was used
  to assign the description-only group, so the separation between it and the
  conjunction group is not independent confirmation, and this is stated in the
  category rather than netted out of its claim.
- **The gold-targeted diagnostic class needed a ruling of its own.** Removing content
  from a gold passage, or removing a competing family from the index, is admissible
  evidence for a mechanism but can never be a deployable repair. Without that
  distinction the dilution result would have drifted into an implementation-level
  claim it does not support.
- **Reviewer agreement is not the goal, and the overlap design had to say so.** Four
  units were double-reviewed to calibrate the note rubric; all four ended in an owner
  decision that chose between competing readings, which is why `overlap_agreed` is
  unused in the label file.

## 7. Limitations

- **The taxonomy is not frozen.** Every category name above is a candidate name, and
  `taxonomy_v1` does not exist. The labels come from a candidate taxonomy.
- **No independent per-unit mapping pass was run.** The full process specifies three
  passes over all 30 units; none was run. The 30 labels are a transcription of one
  landed application of the selection order, not an independent re-derivation.
- **No boundary stress-test was run.** No category boundary was stressed, revised or
  confirmed by a second pass, so the sub-reading structure inside the crowding group
  in particular is untested.
- **The sample is a calibration batch, not a held-out set.** It is 30 strict Any@5
  failures drawn from one run; it estimates no frequency and validates no taxonomy.
- **Twelve triage items remain open** in
  `docs/manual_review_v1/vocabulary_audit_triage.md`, including two placement
  questions and three category-boundary questions.

## 8. What would change a conclusion

- **One named, actionable measurement request exists**, and only one: the
  title-indexing condition on a single description-only unit, which is what would
  raise that group's dense boundary off `not_established`. No endpoint value is
  claimed for it in advance.
- **One named gap is explicitly not a request:** there is no BM25 unit on which the
  description-only descriptor is the decisive primary, so no measurement on an
  existing unit could raise that group's BM25 boundary.
- **One membership contingency is left in the open.** The single BM25 member of the
  crowding group rests on a reading in which the competing family's non-selection of
  the second gold follows from the containing set being reported as non-gold rather
  than from a separately stated measured zero. A reader who declines that reading
  routes the unit to `unresolved`, which changes that group's counts to 4, all dense,
  and changes no boundary value and no claim strength.
- **If the full process is later run**, the most informative thing it can produce is
  a diff: which of these 30 labels move. That difference is direct evidence of what
  the compressed path cost. If none moves, that is also a result worth stating.
