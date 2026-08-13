---
status: active
last_updated: 2026-08-10
---

# Vocabulary-Audit Ruling Triage

## What this is

The section D step 2 product for the taxonomy phase: every question a landed decision
explicitly declined to settle and referred to the vocabulary audit, plus the
synchronization gaps section C of `taxonomy_todo.md` records as deliberately unfixed.

Built on 2026-08-08 by sweeping `open_code_decision_log.md` D-001 through D-039,
section C items 1-11 and section 13 of `taxonomy_todo.md`, every `### Inventory effect`
block of `open_code_vocabulary_audit.md`, the 26 adopted entries of
`secondary_descriptor_registry.md`, and the 30 rows of `case_memos_v2.csv`.

## What this is not

**This document rules on nothing.** It locates questions and their evidence. A ruling
is a consequential change and lives in an appended D-entry; this file records only which
entry settled which item.

It is also not a prevalence report and not a taxonomy. Nothing here may be read as a
count of how often a mechanism occurs (red line 5).

## How to read the columns

`§` is the section of `taxonomy_todo.md` that consumes the ruling. `New D?` is whether a
ruling would be a consequential change under section D - merging two descriptors, adding
a primary-use contract, or editing a definition, inclusion rule or exclusion rule - and
therefore requires an appended D-entry.

## Ruling status

Ruled by the owner on 2026-08-08 and on 2026-08-10.

| Item | Ruling chosen | D-entry |
|---|---|---|
| T-16 | Interventions that require knowing which passages are gold may not be used to refuse a causal descriptor under pit 19s; they are recorded and may limit confidence. Scoped to pit 19s; explicitly not extended to pit 15 | **D-040, landed** |
| T-01 | Split the single-factor oracle-name test in two: failing it bars `description_only_bridge_entity` from primary use, passing it supports without establishing | **D-041, landed** |
| T-34 | `cutoff_sensitive_near_miss` gets a 5.464 percent threshold; the never-decided band stays open; withholding on substitutability moves no band edge | **D-042, landed** |
| T-18 | Crowding-family names get one shared primary-use contract, with a gate: the competing family must be definable by a content rule that selects no required passage | **D-043, landed** |
| T-02 | The pit 19g precondition becomes a condition on the exclusion clause, binding on the failing half only; an unverified or failed precondition makes the application not applicable | **D-044, landed** |
| T-03 | The pit 24b degeneracy check is the second such condition, on the same terms, judged per injected form rather than per unit | **D-045, landed** |
| T-05 | The form set is one surface form of a required passage's own name, injected alone; the passing half stays existential, the failing half requires one form per required passage | **D-046, landed** |
| T-07 | `for lexical retrieval` is dropped from the definition, which is restated backend-neutrally, plus a scope line; T-09 is deliberately left open | **D-047, landed** |
| T-21 | `sharing a name or name token` is restated as a property of the competing passage's text, plus a scope line; recorded as **not** the same shape as T-07 | **D-048, landed** |
| T-29 | The mechanical-separability line is written down and scoped to the preprocessing vocabulary: a separable pipeline decision warrants a name, another value, side, passage or instance of the same normalization decision does not | **D-049, landed** |
| T-30 | `unindexed_title_name_anchor` is retained as an independent secondary and not folded into the preprocessing primary; its own contract is unchanged and T-31 to T-33 stay open | **D-050, landed** |
| T-28 | A prospective passage-level reverse boundary: 0 rank positions gold-targeted, or a negative deployable score effect, excludes. Both cells needed, an unrun cell is `not_applicable`; the zero-effect deployable case and all magnitude thresholds stay open | **D-051, landed** |
| T-27 | One `minimal_preprocessing_score_distortion` is retained, split neither by backend nor into six; narrowed prospectively by D-051; the six sub-mechanisms become a member enumeration; no registry entry is created for a pure primary | **D-052, landed** |
| T-09 | One `description_only_bridge_entity` is retained: not split into absent-name and unusable-anchor names, and not widened to an explicitly named but ineffective anchor. Four prospective routes are written instead, and a residue that no route carries is recorded as a measured fact without a name. It is explicitly **not** ruled that a future residual can never warrant a name | **D-053, landed** |
| T-19 | One `question_frame_semantic_crowding` is retained with no primary-use contract of its own: D-043's shared crowding contract plus this entry's own include and exclude clauses govern its primary use, and the stale note is rewritten. A precedent for T-10 by analogy only | **D-054, landed** |
| T-24 | `same_topic_passage_distractor` and `generic_term_lexical_crowding` are both retained and the boundary is written into both entries at passage level. Two subsets of one unit may take the two names; one passage set may not take both. No third route is added, `related_name_document_crowding` is not folded in, and D-048's cross-reference to this item is recorded as incorrect | **D-055, landed** |
| T-23 | Partial coverage of D-023's neighbourhood is kept: no widening, no Dense-only same-domain name, no reclassification. A prospective evidence-recording rule is added instead - a dossier claiming an enumerated family must name the members its descriptors do not cover | **D-056, landed** |
| T-50 | The Albee / Barrie row is synchronized with D-010: `entity_name_tokenization_mismatch` becomes its primary, `cross_entity_token_recombination` joins its secondary set and `missing_second_comparison_entity` leaves the v2 column, staying in `case_memos_v1.csv` as a first-pass name | **D-057, landed** |
| T-49 | Both remaining flags are cleared. The Bharatpur flag's stated gap is filled by D-052's member enumeration; the Albee flag is cleared **without** folding the name into the preprocessing primary, that fold being left prospective on D-051's two cells, and the boundary against `surface_form_tokenization_mismatch` is opened as T-63 | **D-058, landed** |
| T-48 | `quoted_phrase_semantic_drift` is renamed `verbatim_epithet_sense_drift`, reaching two label fields and three prose fields of its one row. No measurement, interpretation, tie-break, confidence or conclusion of D-020 changes and the old name stays in `case_memos_v1.csv` | **D-059, landed** |
| T-52 | No descriptor naming a defect of the question is adopted in either inventory. Observations route to the names that already carry them and a residue no route carries is recorded as a measured fact without a name; section 12's intake is corrected. It is **not** ruled that such a name can never be warranted | **D-060, landed** |

**T-18's fact check was run, and it landed as drafted.** The gate had been measured on
exactly one unit, D-039, while D-027 records that all six of its competitors literally
contain `Albee` in their text and so does the required Albee passage. D-043 ran the
check over the pooled corpus: excluding bodies that carry a month-day-year date selects
seven passages, all six competitors and `Oppenheimer Award`, and neither required
passage, and that predicate needs nothing from either required passage. The gate
therefore has two supporting units and landed unchanged. **This checked the gate's
evidence base and was not a re-judgment of D-027**, whose primary, conclusions and
confidence are unchanged, and red line 4 is untouched.

The numbering ran 040 / 041 / 042 for the three ruled first, with T-18 reserved as 043
rather than given a gap, because skipping an ID would break `recount.py`'s decision-log
contiguity check. The same rule fixed 044 to 048, and 049 to 052, which are numbered in
the order the owner set for them - T-29, T-30, T-28, T-27 - rather than in triage order,
because T-30 is a corollary of T-29 and T-27 adopts the boundary T-28 states. It fixed
D-053 to D-056 the same way, in the owner's order T-09, T-19, T-24, T-23 rather than in triage
order, because T-24 states the same-topic against generic-term boundary that T-23's
reaffirmation of partial coverage is read against, so the boundary is landed first.
It fixed D-057 to D-060 in the owner's order T-50, T-49, T-48, T-52, because the row
synchronization gives the two flag rulings a settled name to speak about and the rename
is read against it.

Every other item below is open, except T-57 to T-60, which family 11 records as
settled on 2026-08-08 without a D-entry. Counting those, **21 items are ruled, 4
are settled without a D-entry, and 37 remain open**, over 62 items in all.

The item count rose from 60 to 61 with T-62, which D-055 opened in family 3 without ruling on
it, and to 62 with T-63, which D-058 opened in family 9 on the same terms. Opening an item
repairs this record rather than deciding anything, so it carries no
D-entry, on the T-57 to T-60 precedent. **T-46 is still deliberately unused**, so the IDs now
run T-01 to T-63 with one gap.

---

## Family 1 - `description_only_bridge_entity` and the single-factor oracle-name test

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-01 | Is the single-factor oracle-name test part of the primary-decision contract, only a tie-break heuristic, or in need of restatement? It exists in the D-entries and in registry usage notes, never in an exclusion rule. | Registered D-021; restated D-022, D-023, D-024. Membership: `recount.py` section 7a oracle-name series, 18 members, 8 passed / 10 failed, 3 not applicable | 11, 13 | yes |
| T-02 | Is the precondition "the injected anchor must itself be matchable by the passage it names" part of the test, an exclusion-rule clause, or a harness pre-check? | D-024 (pit 19g); `general` / `mills,` split, bare test 9 / 1 uninterpretable, 2 / 1 after punctuation normalization | 11 | yes |
| T-03 | Is there a second precondition, that the injected string must contribute something the question does not already contain? | D-030, first unit where the test passes without supplying oracle information | 11 | yes |
| T-04 | When the test passes but a non-oracle condition refutes it, what is the ordering? D-028 used non-oracle-first (pit 15). | D-028 (first pass-but-lose), D-029, D-036, D-037 | 11, 13 | yes |
| T-05 | Does the test require multi-form consistency, or is a single injected form enough? The harness N factor and hand-written natural insertions can disagree. | D-023 (five forms, all 1 / 3), D-026 (seven forms); `tools/README.md` known-difference 2 | 11 | yes |
| T-06 | What does the test mean when no competitor has non-oracle outcome-decisive evidence, so the test excludes without naming a winner? | D-022 | 11, 13 | yes |
| T-07 | The definition reads "no unique person-name or entity-name anchor **for lexical retrieval**", which does not cover a bi-encoder, while all four primary uses are Dense. Narrow the definition, or was the wording a slip? | Registered D-023 (usage note only); restated D-026, D-035 (pit 2) | 11 | yes |
| T-08 | Structural boundary: in D-017 / D-023 the described entity is a pure bridge entity; in D-026 it is the subject of the answer passage itself. The inclusion rule is met either way. Split or not? | D-026 | 11 | yes |
| T-09 | "No anchor" versus "an anchor that exists but is unusable" - one descriptor or two? | Opened D-029; D-030 routes the unusable case to `surface_form_tokenization_mismatch`; D-035 adds the verbatim-and-near-unique-yet-insufficient form; D-037 asks whether a separate descriptor is still needed | 8, 11 | yes |

## Family 2 - `cross_passage_conjunction_unresolved`

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-10 | Is the name suited to primary use; does primary use need a stronger evidence gate than the current inclusion rule; and does the name need splitting into a primary mechanism and a secondary structural description, given it sits in both inventories? | Registered D-022; primary uses D-022, D-024, D-025, D-031, D-038, D-039 (six, per the registry's member enumeration after D-039 restored D-031) | 11, 13 | yes |
| T-11 | If reachability controls are the gate, does "one side reachable, the other unreachable only through a tokenizer artifact" satisfy it? | D-024 (bridge hop reaches 1, answer hop 51 bare / 4 normalized) | 11 | yes |
| T-12 | Is the opposite-sign single-factor leg part of the inclusion contract or one optional evidence form? D-031 met it 8 of 22 while D-026 cited 4 of 19 as a ground for rejection. | D-031; comparators D-024 10/19, D-025 10/20, D-026 4/19 | 11 | yes |
| T-13 | The same primary rests on different evidence combinations per backend: Dense has no "matched token set" leg at all. How is that written? **Must not become a per-retriever category (pit 17).** | D-025 | 11, 13 | yes |
| T-14 | Should the name be explicitly restricted to bridge-shaped units? D-027 rejected it at the contract level on a comparison unit. | D-027 | 11, 12 | yes |
| T-15 | Should D-028's refutation path - a non-oracle condition that double-recovers while supplying no intermediate fact - be written into the exclusion rule? | D-028 (three positive legs all held and it was still rejected) | 11, 13 | yes |
| T-16 | **Should pit 19s be sliced on "supplies no intermediate fact" rather than on "non-oracle"? The two readings give different primaries.** | D-039; the gold-targeted index-side cell double-recovers at 5 / 18.751159 and 1 / 25.187216 | 11, 13 | yes |
| T-17 | Does the first exclusion fire on a passage that supplies the answer string while verifying only one of the question's constraints? | D-033; D-029 is the only prior use of that clause and its answer passage met all three facets | 11, 12 | yes |

## Family 3 - the crowding family

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-18 | Do crowding-family names need an explicit primary-use contract, as `cross_passage_conjunction_unresolved` does? | Registered D-027 (`one_sided_entity_crowding` first validated primary); D-029; D-032 (one validated primary per backend). D-010 had called the name a ranking pattern | 9, 10, 13 | yes |
| T-19 | `question_frame_semantic_crowding` now sits in both the primary and the secondary inventory. Split, or write a primary-use contract? | D-029, first primary grown by promoting a registered secondary | 9, 10 | yes |
| T-20 | May a secondary be adopted as a scoped **subset** of its own primary's competing family, or is that double counting? | D-029 (42 of which 19; 92 of which 49). D-023 records the opposite shape, half the neighborhood having no descriptor | 10, 13 | yes |
| T-21 | `related_name_document_crowding`'s definition says "sharing a name **or name token**", lexical wording, but it is now used on Dense. Same shape as T-07. | D-027 | 10 | yes |
| T-22 | Should the operational meaning of "explains the primary failure" in that entry's first exclusion be written as D-032's test, a gold-targeted repair of the name form that still leaves the passage outside the cutoff? | D-032 (6 / 27.091980, and the other gold pushed to 7) | 10 | yes |
| T-23 | The half-neighborhood D-023 left uncovered: widen `generic_person_semantic_neighborhood`, add a Dense-only same-domain name, or keep partial coverage? Section 10 already names these three options. | D-023; 26 of 30 non-gold above the bridge hop, roughly half biographies and half unrelated films; X3 removes all 4 biographies for only 3 / 28 | 10 | yes |
| T-24 | The overlap between `same_topic_passage_distractor` and `generic_term_lexical_crowding`. | D-028 (non-adoption recorded on that ground) | 8, 10 | yes |
| T-25 | Should a crowding descriptor whose query-only definition contains a required gold be barred from primary use **by rule** rather than by one entry's argument? | D-039 (1 of the 6 family members is a gold) | 9, 10, 13 | yes |
| T-26 | On a bi-encoder both the family probe and the cumulative removal ladder are arithmetic identities. How were those two evidence forms read on the earlier Dense units? **Explicitly not a re-judgment of any landed decision (red line 4).** | D-035, two separate registrations: nine removal cells agree exactly and every score is bit-identical; the ladder question is registered separately | 10, 13 | no (records a reading; any consequent change would need one) |
| T-62 | **Opened by D-055, and not ruled on there.** The overlap between `related_name_document_crowding` and `same_topic_passage_distractor`. Both describe a competing passage by what its own body says, and the boundary between them has never been written down. This is **not** the T-24 pair: D-048 identified this overlap as T-24, D-055 records that cross-reference as incorrect, and D-048 stands as written under red line 4 | Both names are adopted on the same unit, `5ae60426554299546bf83019|bm25` at D-039, over passage sets that overlap rather than partition: the related-name set has five members above the answer hop - `COPS (animated TV series)`, `Sterling Entertainment Group`, `Noel C. Bloom`, `Locke the Superman` and `Tottoi` - while the topical name is adopted for `COPS (animated TV series)` alone, so the intersection of the two is that one passage and the other four members carry the related name only. Unlike the T-24 pair these two therefore do co-occur, and they co-occur at passage level and not only at unit level, which is part of what the boundary has to settle. D-048's `What this does not settle`; adoptions of the related-name entry at D-010, D-027, D-031, D-032, D-033 and D-039, counted from `case_memos_v2.csv` | 8, 10 | yes |

## Family 4 - `minimal_preprocessing_score_distortion` width

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-27 | Should this primary be narrowed? It now holds 9 units over 6 sub-mechanisms. | Registered D-021; restated D-030, D-033, D-034. Units D-012, D-014, D-016, D-019, D-021, D-028, D-030, D-033, D-034 | 8 | yes |
| T-28 | D-039 supplies the first reverse boundary and a possible narrowing rule: an unperformed normalization existing is not enough, it must be worth rank positions and its deployable version must not be negative. | D-039: constraint hop 2.580995 and 4 rank positions, answer hop 0 rank positions, deployable version -0.024046 | 8 | yes |
| T-29 | Write down the dividing line the D-028 / D-030 pair implies - "is this a decision at the same layer?" D-028 registered a separate name for index-field choice, D-030 refused one for possessive clitics. | D-028, D-030 | 8 | yes |

## Family 5 - `unindexed_title_name_anchor`

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-30 | Should it be folded into the primary instead of standing as its own entry? Folding widens a primary already flagged as possibly too broad. | D-028 (the entry's own registration paragraph) | 8 | yes |
| T-31 | Should the entry require its semantic reading to reach the cutoff? | D-032 (D-028 gives 1, D-032 gives 6 / 16.787469, the string occurring verbatim in 8 non-gold passages) | 8 | yes |
| T-32 | Should it still be refused when the semantic reading is maximal and the indexing reading positive, on the form of the anchor alone? | D-033 | 8 | yes |
| T-33 | Should the first exclusion be stated as a term-frequency test? A materially positive title-indexing condition has now been produced by three different mechanisms, and on two of the three the descriptor should not have been adopted. | D-039; mechanisms per D-028 (anchor only in the title), D-036 (length-normalization side effect), D-039 (tf amplification of an already matchable body anchor) | 8 | yes |

## Family 6 - `cutoff_sensitive_near_miss`

Pit 17 flag: cutoff is an outcome, not a cause. Every item here is about how an outcome
descriptor is contracted, not about promoting it to a category.

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-34 | Give "far below the cutoff" a numeric threshold, and close the never-decided band? | Registered D-027; bands per `recount.py` section 7c: accepted upper edge 5.464, excluded lower edge 9.431, excluded upper 53.000, never-decided 5.464 to 9.431 | 12, 13 | yes |
| T-35 | Should a withholding on substitutability rather than on the gap leave the percentage bands untouched? `recount.py` already isolates it as `withheld_on_substitutability`. | D-034 (3.641 percent inside the accepted band, withheld; four non-gold supply the same intermediate fact, two inside the cutoff) | 12 | yes |
| T-36 | The two statements of D-025's split rule in the entry do not agree: D-025 / D-026 / D-032 adopted for the near hop while the far hop sat in the excluded band, D-035 restates the rule as forbidding the descriptor for the whole unit. | Registered D-036; D-038 follows the landed adoptions rather than settling it | 12 | yes |
| T-37 | When a complete alternative answer already sits inside the cutoff, the descriptor records the fragility of the annotated title rather than of answer availability - a weaker reading than D-022 through D-032 gave it. Separate contract? | D-036 | 12 | yes |
| T-38 | Now that a two-sided adoption exists, does the descriptor need separate contracts for the `any@5` and `full@5` readings? | D-039, first unit where both required passages qualify, 4.860 and 0.721 percent | 12, 13 | yes |
| T-39 | Is D-024's 5.698 percent a reverse precedent, and should pre-D-025 units be re-read under the split rule? Its rejection ground was superseded at D-025, so the precedent set mixes two rules. | Registered D-033; `recount.py` section 7c prints this as an audit question, not a re-judgment | 12, 13 | yes |

## Family 7 - `peripheral_passage_content_dilution`

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-40 | Is the four-condition gate correctly placed, and should it generalize to all Dense content-shaped claims? Sub-question from D-026: should the length-matched control be required as a curve rather than a single point? | Registered D-023 and section 13; gate history per `recount.py` section 7a dilution series, 9 applications, 7 passed / 2 rejected. D-026: 30-word control ranks 101 while the 68-word control ranks 23 | 10, 11, 13 | yes |
| T-41 | Should the third inclusion condition be reworded to cover a passage whose non-relevant material is a parenthetical rather than a whole sentence, where the literal control cannot be constructed? | D-029 | 13 | yes |
| T-42 | The literal control ("keep only the non-relevant sentences") and D-027's added requirement ("the control must preserve the entity name") are constructionally incompatible when the question is essentially the name. State the rule so the two cannot disagree. | D-031: literal control 2908 / -0.012338 passes, name-preserving controls 1 / 0.649612 and 1 / 0.725954 fail. Interim rule: run and report both | 13 | yes |
| T-43 | Does a dilution primary need a primary-use contract? The entry's own attribution boundary calls it a diagnostic while a primary is normally read as a mechanism. | D-037, its first primary use, after five passes that stopped at secondary | 10, 13 | yes |
| T-44 | Does gold-targeted index-side ablation - the third intervention class, which injects no answer information but requires knowing which passage is gold - need formal standing in the candidate taxonomy? | Registered D-023 and section 13; pit 19d | 13 | yes |
| T-45 | After the gate rejects, nothing carries the measurable property "this required passage's query-relevant material is a small fraction of its text". Converse of the gap D-023 recorded. | D-031: 11 of 73 words; name only 1 / 0.643385, name removed 2711 / -0.002227 | 10, 13 | yes |

T-46 is deliberately unused: D-026's "the length-matched control must be run as a curve,
not a single point" is folded into T-40 as a sub-question rather than triaged separately.

## Family 8 - corpus setting

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-47 | Must the candidate taxonomy record the three paths separately - pooling-introduced rivals, idf / length scale change (lexical only), and an annotator-supplied one-sided distractor set - and does D-003's wording need sharpening for the latter two? Also: the design must handle the three paths **stacking**, not only a three-way choice. **Corpus setting must not be promoted to a causal category (pit 17, red line 5).** | Registered D-024; third path added D-027; stacking shown D-028, D-030, D-032; eleven examples recorded across C item 7 | 13 | yes (taxonomy text only, not a category) |

## Family 9 - naming defects and row / registry synchronization

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-48 | Rename `quoted_phrase_semantic_drift`. The name implies quotation punctuation or literal string matching, which D-020's condition A experimentally excluded. | D-020; unit `5ab978855542996be2020512|dense`, `taxonomy_defect_flag=true` | 8, 12 | yes |
| T-49 | Disposition of the other two `taxonomy_defect_flag=true` units. | `5a78b209554299148911f93e|bm25` (D-010), `5a7d61775542991319bc93b9|bm25` (D-012). Confirmed on disk: exactly 3 rows carry the flag | 9, 10 | yes |
| T-50 | The Albee / Barrie row still carries its first-pass primary / secondary fields while D-010 and the registry use `entity_name_tokenization_mismatch`, `cross_entity_token_recombination`, `related_name_document_crowding`; the row also still holds `missing_second_comparison_entity`, which D-010 does not retain. **Must not be silently corrected.** | C item 3; audit section 7.2 "Adoption and registry status" | 9, 10, 22 | yes |
| T-63 | **Opened by D-058, and not ruled on there.** The boundary between the primary `entity_name_tokenization_mismatch` and the registered secondary `surface_form_tokenization_mismatch` has never been written down. The registry defines the second as a minimal tokenizer treating punctuation-bearing or morphologically related surface forms as different tokens, which is also what the first names on its one unit, and the two have never been used on the same unit, so nothing yet forces the line. The item carries the fold question with it: D-049's separability line points at folding the first into `minimal_preprocessing_score_distortion`, and D-058 leaves that prospective on D-051's two cells rather than refusing it | D-010, D-049, D-051, D-052 and D-058; the second name's registry entry, adopted on twelve `case_memos_v2.csv` rows against the first name's one | 8, 9 | yes |

## Family 10 - cross-entry rules

| ID | Question to rule on | Evidence | § | New D? |
|---|---|---|---|---|
| T-51 | `gold_chain_substitutability`: does a substitute outside the cutoff count (D-025), and does a non-gold passage that reaches the same bridge entity through a **different** one of the question's constraints count (D-038)? Both sharpen the boundary D-023 left open. | D-023, D-025, D-038 | 12 | yes |
| T-52 | Does the vocabulary need a question-quality descriptor at all? **Pit 17 deleted `question_wording_ambiguity` for stating a defect of the question rather than a retrieval mechanism.** | Opened D-025 (verified factual error, measured not decisive, 115 to 102); D-026 first measurement argues against; D-034 deleted the provisional name after a sixteen-cell wording factorial left the bridge hop fixed | 12, 13 | yes |
| T-53 | Is co-necessity a sufficient ground for adopting a secondary? D-030 refused `generic_query_scaffold_score_inflation` on solo materiality and D-032 accepted it on co-necessity. Same shape at D-034 for routing to `repeated_function_word_amplification`. | D-030, D-032, D-034 | 13 | yes |
| T-61 | **Opened by D-040.** Pit 15 orders a non-oracle result above an oracle one and turns on the same word D-040 restricted in pit 19s. Should the same restriction apply there? D-037's landed tie-break rests on a gold-targeted index-side condition, so extending it would remove that entry's stated ground. D-037 stands under red line 4 whatever is decided. | D-040; D-037's dossier classifies its L / M / D / TA / TB / TC / S families as gold-targeted index-side, and the double recovery is 3 / 0.469751 and 1 / 0.549310 | 11, 13 | yes |
| T-54 | May `description_only_bridge_entity` and `plausible_non_gold_answer` sit on the same unit? One says the annotated chain is unreachable without a name, the other says it did not have to be reached; both are measured on D-036's unit. | D-036 | 12, 13 | yes |

## Family 11 - process and bookkeeping, not vocabulary rulings

| ID | Item | Evidence | § | New D? |
|---|---|---|---|---|
| T-55 | No tool checks the registry's member enumerations; they are not among `recount.py`'s five ordinal series. The `cross_passage_conjunction_unresolved` primary-use enumeration omitted D-031, so D-038 called itself the fourth primary use when it was the fifth. Any section 8-26 sentence of the form "the Nth primary use" must be counted by hand from `case_memos_v2.csv` first. | C item 11 | all | no |
| T-56 | Eleven reviewed units (D-009 to D-020) still have no per-case dossier. Buildable by **transcription only** from the existing D-entries and memos; no re-analysis, no change to landed conclusions. | C item 6; 19 dossiers exist, confirmed by `recount.py` | all | no |
| T-57 | **Settled 2026-08-08, not by a D-entry.** How to invoke `cross_check.py` on a landing with no case; the measured answer is written into section D of `taxonomy_todo.md`. | Measured on the T-58 / T-59 / T-60 landing: `--queue-no 26 --no-run`, exit 0 | landing | no |
| T-58 | **Settled 2026-08-08, not by a D-entry.** Front-matter `last_updated` was behind the last substantive edit on five shared files; each was set to the date of its own last commit. | Disk front matter versus `git log -1 --date=short` per file | all | no |
| T-59 | **Settled 2026-08-08, not by a D-entry.** Section C's lead sentence counted 7 open items over a list of 14. | Section C | all | no |
| T-60 | **Settled 2026-08-08, not by a D-entry.** Section C item 4's oracle-name tally disagreed with the authoritative membership table. See below. | See below | 11 | no |

---

## T-60 in full: the correction section C item 4 needed

`recount.py` exits 0 and its section 7a table is authoritative; section C item 4 itself
says so. The registry's anchored sentences agree with the table - `recount.py` verifies
"seventh failing application" at D-033, "eighth" at D-034, "ninth" at D-038 and "tenth"
today, and all four pass. Only the handoff restatement was wrong.

Authoritative membership, 18 rows, running counts as application / pass / fail:

```
 1 D-017 5a85cead|dense passed   1/1/0      10 D-029 5a81ebee|dense passed  10/5/5
 2 D-020 5ab97885|dense failed   2/1/1      11 D-031 5ab48c32|dense failed  11/5/6
 3 D-021 5ac1a366|bm25  failed   3/1/2      12 D-033 5abcc96c|bm25  failed  12/5/7
 4 D-022 5ade42b5|bm25  failed   4/1/3      13 D-034 5adc8977|bm25  failed  13/5/8
 5 D-023 5ade69e4|dense passed   5/2/3      14 D-035 5add6791|dense passed  14/6/8
 6 D-024 5ae057fd|bm25  failed   6/2/4      15 D-036 5adf58f1|bm25  passed  15/7/8
 7 D-025 5ae0a59a|dense failed   7/2/5      16 D-037 5ae048a2|dense passed  16/8/8
 8 D-026 5ae1f596|dense passed   8/3/5      17 D-038 5ae18019|dense failed  17/8/9
 9 D-028 5a79b7f6|bm25  passed   9/4/5      18 D-039 5ae60426|bm25  failed  18/8/10
```

Not applicable, and therefore not applications at all: D-027 and D-032 (comparison units,
the test is degenerate, pit 25f) and D-030 (its passing oracle condition was itself
degenerate, pit 24b).

What section C item 4 said, and what the table says:

| Section C said | Table says |
|---|---|
| D-035 is the 12th application, 6th pass | 14th application, 6th pass |
| D-036 is the 13th application, 7th pass | 15th application, 7th pass |
| D-037 is the 14th application, 8th pass | 16th application, 8th pass |
| D-038 is the 15th application, 10th failure | 17th application, 9th failure |
| D-039 is the 16th application, 11th failure | 18th application, 10th failure |
| 16 applications, 8 passes, 11 failures of which 8 in the series | 18 applications, 8 passes, 10 failures, all 10 in the series |

Diagnosis, in two parts. The failure ordinals in the registry are correct and were not
touched: `recount.py` verifies "seventh failing application" at D-033, "eighth" at
D-034, "ninth" at D-038 and "tenth" today, and all four pass. The handoff had counted
the three not-applicable decisions as failures, which inflated the failure total to 11
and forced the "8 of 11 in the series" phrasing; that part was a transcription error and
is corrected.

The application ordinals are a different matter and are **not** the handoff's error.
Three landed entries state them, and all three are two or more low against the table:
D-035 says "the twelfth application of the test and its sixth pass" where the table gives
the fourteenth; D-036 says "its thirteenth application and its seventh pass" where the
table gives the fifteenth; D-037 says "the thirteenth application of the criterion and
the seventh pass", which does not advance at all and duplicates D-036's ordinal, where
the table gives the sixteenth. D-031's "eleventh application" agrees with the table, so
the drift begins at D-035: D-033 and D-034 both applied the test and failed and are
recorded as the seventh and eighth failing applications, but D-035's sentence advanced
the failure count without advancing the application count, and the next two inherited it.

Those three sentences stay as written under red line 4. They are registered in
`recount.py`'s section 7d legacy block, the treatment already given to the title-indexing
and dilution-gate series - **this is the third ordinal series to break the same way**,
which is what the owner's 2026-08-05 ruling retiring the global measurement ordinal was
meant to stop. Sections 8-26 must state class counts, never "the Nth application".

Corrected in `taxonomy_todo.md` and registered in `recount.py` on 2026-08-08; no D-entry,
because no case conclusion and no registry rule changed.
