---
status: draft
last_updated: 2026-08-13
---

# Provisional Open-Code Vocabulary Audit

## Scope and evidence boundary

This document records the stepwise vocabulary audit requested in section 7 of
`taxonomy_todo.md`. It is not a frozen taxonomy, a final mapping, or a
prevalence report. Counts of distinct names below describe the working
vocabulary only.

Evidence layers used in this first item:

- **Observed data:** values in `case_memos_v1.csv` and
  `case_memos_v2.csv.primary_open_code`.
- **Joint-review decisions:** candidate primary mechanisms adopted by D-010 and
  D-012 in `open_code_decision_log.md`.
- **Not yet decided:** normalization, synonym merging, category validity,
  primary-versus-secondary demotion, and final taxonomy boundaries.

## Section 7.1 — Extract all primary open codes

### Inventory result

The current primary vocabulary contains **25 distinct names**:

- 23 first-pass names preserved from `case_memos_v1.csv`;
- 1 implementation-supported primary added to
  `case_memos_v2.csv.primary_open_code` by D-012; and
- 1 implementation-supported candidate primary retained in
  `case_memos_v2.csv.candidate_category` and D-010, but not yet copied into the
  row's `primary_open_code` field.

The 25 names, preserved exactly as currently written, are:

1. `bridge_relation_underweighted`
2. `compound_two_sided_crowding`
3. `cross_entity_relation_unresolved`
4. `cross_passage_conjunction_unresolved`
5. `description_only_bridge_entity`
6. `entity_name_tokenization_mismatch`
7. `generic_term_lexical_crowding`
8. `literal_cue_topic_capture`
9. `minimal_preprocessing_score_distortion`
10. `multiword_title_token_fragmentation`
11. `named_entity_anchor_distraction`
12. `near_title_collision`
13. `one_sided_entity_crowding`
14. `partial_bridge_only`
15. `partial_match_constraint_omission`
16. `plausible_non_gold_answer`
17. `proper_name_homonym_collision`
18. `query_facet_fragmentation`
19. `question_wording_ambiguity`
20. `quoted_phrase_semantic_drift`
21. `related_document_crowding`
22. `same_domain_entity_crowding`
23. `same_entity_variant_crowding`
24. `two_named_entities_underprioritized`
25. `weak_cross_domain_bridge`

### Provenance exceptions created during overlap review

| Code | Current source | Decision | Taxonomy-defect unit |
|---|---|---|---|
| `entity_name_tokenization_mismatch` | `candidate_category` plus decision log; the row's first-pass `primary_open_code` remains `one_sided_entity_crowding` | D-010 | `5a78b209554299148911f93e|bm25` |
| `minimal_preprocessing_score_distortion` | `primary_open_code`, `candidate_category`, and decision log | D-012 | `5a7d61775542991319bc93b9|bm25` |

`one_sided_entity_crowding` remains in the inventory because it is still the
first-pass primary for another unit. D-010 supersedes it only for the Albee /
Barrie overlap unit; it does not establish a vocabulary-wide merge or deletion.

### Completion boundary

This item establishes membership in the current primary-code inventory only.
It does not yet:

- extract secondary codes;
- normalize spelling, case, number, or underscore style;
- merge semantically equivalent names;
- decide which names are causal mechanisms;
- demote structural descriptions;
- map every code to all unit keys; or
- append a vocabulary-audit decision to the decision log.

Those actions remain separate unchecked items in section 7.

### Completeness self-check

The extraction passed the following consistency checks:

- `case_memos_v2.csv` contains 30 rows and 30 unique analytical units;
- all 30 rows have a non-empty `primary_open_code`;
- the current raw `primary_open_code` column contains 20 distinct names;
- all 10 `jointly_reviewed` rows have a non-empty `candidate_category`;
- exactly 1 joint-review assignment overrides its first-pass primary:
  `one_sided_entity_crowding` to `entity_name_tokenization_mismatch` for
  `5a78b209554299148911f93e|bm25`;
- applying `candidate_category` to the 10 jointly reviewed rows yields 30
  effective assignments and 21 distinct current names; the union with preserved
  first-pass primary names still contains the 25 names listed above;
- the numbered inventory contains exactly 25 unique names; and
- set comparison found no missing names and no extra names.

A reverse scan of the analysis and implementation-reference documents found no
additional primary-code name outside this inventory. Result: **pass; no
inventory correction required**.

## Section 7.2 — Extract all secondary open codes

### Inventory result

The complete provisional secondary-name inventory contains **46 distinct
names**. This is a vocabulary inventory, not a count of validated mechanisms
and not a prevalence estimate.

Provenance reconciliation:

- `case_memos_v1.csv.secondary_open_codes` contains 39 distinct first-pass
  names;
- `case_memos_v2.csv.secondary_open_codes` contains 40 distinct names. Relative
  to v1 it adds `repeated_function_word_amplification` and
  `surface_form_tokenization_mismatch` through D-012,
  `repeated_content_word_amplification` through D-014, and
  `answer_property_semantic_crowding` through D-018. D-014 removes
  `metonymic_bridge_unresolved`, D-016 removes
  `superlative_bridge_underweighted`, and D-017 removes
  `short_answer_passage_underweighted` from their current v2 rows; all three
  first-pass names remain preserved in v1. D-017 retains
  `possible_type_mismatch` and adopts
  `cross_passage_conjunction_unresolved`; D-018 removes
  `low_context_name_query` from the Serri/John Fogerty unit, retains it
  elsewhere, and adopts the already inventoried
  `proper_name_homonym_collision`; and
- the registry and D-010 add
  `cross_entity_token_recombination`, which is adopted but is not currently
  written in the affected row's `secondary_open_codes` field.
- D-019 removes `same_topic_title_distractor` from the current v2 row, adopts
  the existing `surface_form_tokenization_mismatch`, and adds
  `generic_query_scaffold_score_inflation` plus
  `same_topic_passage_distractor` with complete registry entries.

The union of the CSV columns and the joint-review registry therefore contains
the following 46 names, preserved exactly as currently written:

1. `adjacent_event_crowding`
2. `answer_entity_missing_both_methods`
3. `answer_property_semantic_crowding`
4. `both_gold_chain_passages_missing`
5. `bridge_relation_underweighted`
6. `broad_adaptation_topic_crowding`
7. `broad_film_person_neighborhood`
8. `competing_valid_entity_cues`
9. `cross_entity_relation_unresolved`
10. `cross_entity_token_recombination`
11. `cross_passage_conjunction_unresolved`
12. `cutoff_sensitive_near_miss`
13. `description_only_bridge_entity`
14. `distributor_related_document_crowding`
15. `exact_string_source_dependency`
16. `film_series_entity_collision`
17. `general_answer_passage_missing`
18. `generic_context_substitution`
19. `generic_person_semantic_neighborhood`
20. `generic_query_scaffold_score_inflation`
21. `generic_term_lexical_crowding`
22. `gold_chain_not_unique`
23. `gold_chain_substitutability`
24. `location_chain_incomplete`
25. `low_context_name_query`
26. `low_information_title`
27. `metonymic_bridge_unresolved`
28. `missing_second_comparison_entity`
29. `near_duplicate_event_confusion`
30. `possible_type_mismatch`
31. `proper_name_homonym_collision`
32. `related_name_document_crowding`
33. `repeated_content_word_amplification`
34. `repeated_function_word_amplification`
35. `same_artist_work_crowding`
36. `same_topic_passage_distractor`
37. `same_topic_title_distractor`
38. `shared_retriever_failure`
39. `short_answer_passage_underweighted`
40. `subject_associate_crowding`
41. `superlative_bridge_underweighted`
42. `surface_form_tokenization_mismatch`
43. `surname_entity_confusion`
44. `technical_topic_crowding`
45. `underdetermined_question`
46. `weak_lexical_name_anchor`
### Adoption and registry status

- 21 names are adopted for jointly reviewed units and have complete registry
  entries sourced by D-006, D-009 through D-012, and D-014 through D-019.
- 20 unregistered names occur only on the remaining `needs_joint_review`
  single-note units. They remain provisional and will be evaluated during the
  7A validation gate.
- 4 unregistered historical names, `metonymic_bridge_unresolved`,
  `short_answer_passage_underweighted`, `superlative_bridge_underweighted`, and
  `same_topic_title_distractor`, remain in `case_memos_v1.csv` but were removed
  from their current v2 rows by D-014, D-017, D-016, and D-019 respectively.
- 1 unregistered name,
  `missing_second_comparison_entity`, remains in the jointly reviewed
  Albee/Barrie row from the first pass.

The last item is a synchronization discrepancy rather than a new semantic
decision:

- D-010 adopts `cross_entity_token_recombination` and
  `related_name_document_crowding`;
- the registry contains both adopted descriptors;
- the affected `case_memos_v2.csv` row still contains
  `related_name_document_crowding; missing_second_comparison_entity`; and
- D-010 does not retain `missing_second_comparison_entity`.

This extraction preserves both names and records the discrepancy. It does not
silently rewrite the row, delete the first-pass descriptor, or create a new
decision. The row-level synchronization will be handled explicitly during the
validation workflow.

### Completeness self-check

The extraction passed the following checks:

- both `case_memos_v1.csv` and `case_memos_v2.csv` import as 30-row tables;
- all 30 v2 rows have at least one secondary descriptor;
- v2 contains 60 secondary assignments and 41 distinct names;
- no row contains a duplicate secondary assignment;
- all 40 v2 names follow the current lowercase underscore form;
- the joint-review decision set contains 21 adopted descriptors;
- the registry contains exactly the same 21 adopted names, with no missing or
  extra entry;
- registry-to-v2 comparison identifies exactly one registry-only name,
  `cross_entity_token_recombination`;
- v2-to-registry comparison identifies exactly one unregistered name on a
  jointly reviewed row, `missing_second_comparison_entity`; and
- the final union contains 46 unique names with no duplicates.

Result: **pass with one documented row/registry synchronization discrepancy;
no vocabulary name is missing**.

### Completion boundary

This inventory remains descriptive rather than a prevalence result. D-014
through D-019 have now validated and revised 6 of the 26 single-note units; the
remaining 20 units must pass the section 7A gate before name normalization,
semantic merging, or primary-versus-secondary demotion begins.

## Section 7A.1 — Confirm the provisional status of 26 single-note units

### Method

This gate applies the evidence-preserving boundary from
`references/reusable_retrieval_failure_review_playbook.md`: first-pass open
codes are working comparison handles, not validated taxonomy categories.
Observed row state is checked separately from later mechanism interpretation.

For each `overlap_status=single_note` row, the audit requires:

- exactly one reviewer and exactly one non-empty original note;
- `analytic_status=provisional_open_coded_needs_joint_review`;
- `review_status=needs_joint_review`;
- non-empty first-pass `primary_open_code` and `secondary_open_codes`; and
- no populated joint-review result fields.

### Result

The status audit passed with zero exceptions:

- 30 total rows and 30 unique analytical units;
- 4 overlap rows, all `jointly_reviewed`;
- 26 single-note rows, all `needs_joint_review`;
- 13 Xin-only rows and 13 Jiajun-only rows;
- all 26 single-note rows have exactly one original note;
- all 26 have non-empty provisional primary and secondary assignments;
- all 26 retain
  `analytic_status=provisional_open_coded_needs_joint_review`; and
- none has a populated `joint_review_notes`, `boundary_issue`,
  `candidate_category`, `closest_competing_category`,
  `tie_break_result`, `candidate_confidence`, or
  `taxonomy_defect_flag`.

This result records the pre-validation baseline. After D-014 through D-019,
6 single-note rows are `jointly_reviewed` and 20 remain
`needs_joint_review`; their original `note_xin` and `note_jiajun` values remain
unchanged.

### Interpretation boundary

This result confirms only that all 26 assignments are explicitly provisional
and have not been silently promoted to reviewed categories. It does not support
retaining, revising, merging, or demoting any code. Those decisions require the
playbook's full evidence review, including actual passage text and the
run-specific implementation reference.

## Section 7A.2 — Build the 26-unit validation queue

The validation queue is recorded in
`manual_review_v1/analysis/single_note_validation_queue.md`.

- Units 1-13 are the Jiajun-only cases.
- Units 14-26 are the Xin-only cases.
- Source order is preserved within each reviewer group.
- Every queue row records the analytical unit, retriever, question type, and
  current provisional primary and secondary assignments.
- All 26 rows begin at `not_started`.

The queue controls review order only. It does not validate any assignment or
change `case_memos_v2.csv`.
## Section 7A.3 — Validate `5ab72a025542992aa3b8c7b8|bm25`

D-019 revises the primary from `multiword_title_token_fragmentation` to
`minimal_preprocessing_score_distortion`. Exact reconstruction reproduces the
formal 4,937-passage pooled top 50 and scores with zero error and places the two
golds at complete-corpus ranks 430 and 4067. Per-token decomposition verifies
punctuation-sensitive gold false negatives and material score from unfiltered
non-repeated question-scaffold terms.

All eight P×S×T conditions were run on the same complete corpus. Boundary
punctuation normalization is the strongest single factor (6/30); the complete
P+S+T combination reaches 1/6 but does not fully restore both golds to top five.
This supports the implementation-induced primary without claiming that
preprocessing fully explains the strict cutoff outcome.

The validated secondaries are `surface_form_tokenization_mismatch`, the new
`generic_query_scaffold_score_inflation`, and the new
`same_topic_passage_distractor`. The last replaces
`same_topic_title_distractor` because the actual implementation does not index
titles and the adopted descriptor requires passage-text evidence. The new names
remain provisional; this decision does not merge vocabulary, set taxonomy
boundaries, freeze the taxonomy, or turn counts into prevalence.

## Section 7A.4 — Validate `5ab978855542996be2020512|dense`

D-020 retains the primary `quoted_phrase_semantic_drift` and revises the
secondary set. Re-encoding the same 4,937-passage pooled corpus reproduces all
50 formal top-50 titles in order with a maximum absolute score error of
2.384e-07 and places the golds at complete-corpus ranks 465 and 13, so the
stored `not_in_top50` status means rank 465 of 4,937 rather than corpus
absence.

The complete A x B x C query-rewrite factorial was run, together with an
indexing condition T and three removal probes. Quotation-mark removal (A) and
title inclusion (T) are both inert, so neither punctuation nor title exclusion
is the mechanism. Naming the referent (B) repairs only the answer hop and
naming the source film (C) repairs only the source hop; only B+C restores both
to top five. The decisive non-oracle result is probe D: with the query reduced
to the verbatim epithet, the single passage that literally contains it ranks
106 of 4,937 behind afterlife-concept passages. Probe E shows the epithet also
costs the answer passage ranks, 13 to 5.

The validated secondaries are the newly registered
`exact_string_source_dependency`, the existing
`cross_passage_conjunction_unresolved` now adopted for a second unit, and the
new `question_frame_semantic_crowding`. The closest competitor is
`description_only_bridge_entity`, rejected as primary because its single-factor
oracle-name condition restores only one hop.

This unit carries `taxonomy_defect_flag=true` for a naming-versus-mechanism
problem: the primary name implies a quotation-punctuation or string-matching
mechanism that condition A excludes. The rename is deferred to the vocabulary
audit rather than performed during the validation pass.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**;
  `quoted_phrase_semantic_drift` is item 20 and was retained, not renamed.
- The secondary-name union grows from 46 to **47 distinct names** with the
  addition of `question_frame_semantic_crowding`.
- `case_memos_v2.csv` now holds 62 secondary assignments over 42 distinct
  names; `case_memos_v1.csv` is unchanged at 39 distinct names. The earlier
  "40 distinct v2 names" figure in section 7.2 was a stale restatement of the
  41 recorded in the same section's self-check; it is superseded here rather
  than silently corrected in place.
- The registry now contains **23 adopted descriptors**, adding
  `exact_string_source_dependency` and `question_frame_semantic_crowding`.
- `review_status` counts are now 11 `jointly_reviewed` and 19
  `needs_joint_review`.

These remain vocabulary counts, not validated mechanism counts and not
prevalence.

## Section 7A.5 — Validate `5ac1a3665542994ab5c67daf|bm25`

D-021 replaces the primary `description_only_bridge_entity` with
`minimal_preprocessing_score_distortion`. Rebuilding the first-occurrence,
title-deduplicated 4,937-passage pooled corpus reproduces all 50 formal top-50
titles in order with a maximum absolute score error of 0 and places the golds at
complete-corpus ranks 2074 and 14, so the stored `not_in_top50` status means
rank 2074 of 4,937 rather than corpus absence.

Per-token decomposition establishes that the answer passage receives its entire
9.070003 from `was`, `of`, and `the` and matches no content token. The one query
cue that uniquely identifies it, the date span, is destroyed by the tokenizer:
the query form `1990-2001?` and its punctuation-stripped form `1990-2001` are
both absent from the corpus vocabulary, so the date contributes exactly
0.000000. The query contains no repeated token, so this unit is the first
`minimal_preprocessing_score_distortion` case in which repeated-occurrence
amplification plays no part.

All 16 P x E x S x T cells and all 4 N x A cells were run on the same complete
candidate set, together with four probes. Title inclusion (T) is
inert-to-negative and is excluded as the mechanism. No single factor restores
both golds. The decisive interaction is P x E: the shared date cue differs on
two independent surface dimensions at once, so neither normalization alone
aligns it, while together they move the answer hop from 2074 to 7 with no oracle
content. P+E+S is the only non-oracle condition that places both golds inside
top five, at 5 and 1. Probe D is the decisive non-oracle demonstration: with the
query reduced to the normalized date span, the single passage containing it
ranks 1 while every other passage scores exactly 0.000000.

The validated secondaries are `surface_form_tokenization_mismatch`,
`generic_query_scaffold_score_inflation`, `description_only_bridge_entity`, the
newly registered `entity_alias_reference_mismatch`, and
`generic_term_lexical_crowding`. The unregistered first-pass secondary
`weak_lexical_name_anchor` is removed from the current v2 row as redundant with
`description_only_bridge_entity`; it remains preserved in `case_memos_v1.csv`
and in the vocabulary union.

The closest competitor is `description_only_bridge_entity`, rejected as primary
because its single-factor oracle-name condition restores only the answer hop
while leaving the second required passage at 15. This applies the D-020
disqualifier and is the inverse of D-017, where the same single-factor condition
restored both hops. This unit is therefore the first case in which a descriptor's
inclusion rule is met while the descriptor still loses the primary tie-break; the
precedent is held in D-021 and deliberately not written into the registry
definition, because primary-versus-secondary boundary rules are reserved for the
vocabulary audit.

Three descriptors were considered and explicitly not adopted:
`gold_chain_substitutability`, whose inclusion rule is met by two passages
stating "Prince Andrew, Duke of York" verbatim but which reach only ranks 14 and
10 even under P+E; `proper_name_homonym_collision`, which is real but not
outcome-determinative because P alone moves the affected gold to rank 1; and
`cross_passage_conjunction_unresolved`, because P+E+S restores both golds without
any cross-passage resolution.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**;
  `minimal_preprocessing_score_distortion` is item 9 and was already in the
  inventory. `description_only_bridge_entity` remains item 5 and is still the
  first-pass primary for two other `not_started` units, so this decision does
  not remove it from the inventory.
- The secondary-name union grows from 47 to **48 distinct names** with the
  addition of `entity_alias_reference_mismatch`.
  `weak_lexical_name_anchor` remains in the union as a historical first-pass
  name and now has no current v2 row.
- `case_memos_v2.csv` now holds **66 secondary assignments over 42 distinct
  names**, up from 62 over 42: five descriptors were added to this row and one
  removed, and the distinct count is unchanged because the removed name was
  unique to this row while the added new name is also unique to it.
  `case_memos_v1.csv` is unchanged at 39 distinct names.
- The registry now contains **24 adopted descriptors**, adding
  `entity_alias_reference_mismatch`.
- `review_status` counts are now 12 `jointly_reviewed` and 18
  `needs_joint_review`. Eight rows now carry a populated `candidate_category`.
- The `surface_form_tokenization_mismatch` include rule gains one worked
  illustration, the Unicode en-dash mismatch, recorded explicitly as an added
  example within the existing definition rather than as a widening.
- Section 7.2's "Completion boundary" still states that D-014 through D-019
  validated 6 of 26 units with 20 remaining. That figure was already stale after
  D-020 and is superseded here rather than silently corrected in place: the
  current state after D-021 is **8 of 26 validated, 18 remaining**.

These remain vocabulary counts, not validated mechanism counts and not
prevalence.

## Section 7A.6 — Validate `5ade42b55542992fa25da717|bm25`

D-022 replaces the primary `near_title_collision` with
`cross_passage_conjunction_unresolved`. Rebuilding the first-occurrence,
title-deduplicated 4,937-passage pooled corpus reproduces all 50 formal top-50
titles in order with a maximum absolute score error of 0.000000 and places the
golds at complete-corpus ranks 8 and 15. Both are retrieved; the answer hop is
0.952795 points, or 2.17 percent, below the rank-5 score.

Per-token decomposition, weighted by query-token occurrence, reconciles with
`get_scores` to within 1.4e-14 on every inspected passage. It establishes that
the answer hop, `Ender's Game (series)`, matches none of the query's
discriminating tokens `shadows`, `flight`, and `tenth`, so its entire rank rests
on generic book vocabulary and unfiltered function words; scaffold supplies 52
percent of its score, and 85.3 percent of that scaffold total comes from the
repeated tokens `in`, `the`, and `of`. The bridge hop, `Shadows in Flight`,
misses `novels` because its text uses the singular `novel`, and `series` because
its text carries only `series.` and `series"`. The query contains four repeated
tokens. One observed null is recorded: the question has a space before its final
question mark, so `?` is a standalone token whose idf 8.098947 is the highest in
the query, yet it occurs in exactly 1 of 4,937 passages and contributes exactly
0. High idf is not the same as discriminating power.

All 16 P x M x S x T cells and all 4 Rc x Rf cells were run on the same complete
candidate set, together with eight further combinations, four removal probes,
five reduced-query probes, two reachability probes, and six oracle conditions.
No condition of any kind recovers both hops except the oracle combinations
N1+N2+S and N1+N2+ST; even both oracle anchors without scaffold removal fail at
5 and 6. The two hops are antagonistic: their matched query-token sets are nearly
disjoint and six factors carry opposite signs across them. Probe Q1 shows the
bridge hop is uniquely reachable from its own name at rank 1, and probe K1 shows
the answer hop is uniquely reachable from the series name at rank 1, yet the
series name occurs nowhere in the query and only inside the bridge passage.

The provisional primary is falsified directly. This implementation does not index
titles, the shared token `shadows` in the competing passage comes from its body
text, and removal probe X1 shows that dropping `Merlin Book 10: Shadows on the
Stars` moves the result only from 8 and 15 to 8 and 14. That also resolves the
uncertainty the original reviewer note itself raised about whether that passage
was the decisive distractor.

The validated secondaries are `description_only_bridge_entity`,
`surface_form_tokenization_mismatch`, `generic_term_lexical_crowding`,
`repeated_content_word_amplification`, `repeated_function_word_amplification`,
and `cutoff_sensitive_near_miss`. The closest competitor is
`description_only_bridge_entity`, rejected as primary because its single-factor
oracle-name condition restores only the answer hop, at 1 and 20. This is the
third application of the D-020 disqualifier and the inverse of D-017.

Three descriptors were considered and explicitly not adopted:
`generic_query_scaffold_score_inflation`, because its exclude rule defers to
`repeated_function_word_amplification` when repeated occurrences are the material
mechanism, and 85.3 percent of the answer hop's scaffold contribution comes from
repeated tokens; `gold_chain_substitutability` and `plausible_non_gold_answer`,
because `ender's game` and `orson scott card` each occur in exactly two passages
which are the two golds themselves, so neither hop has any substitute; and
`compound_two_sided_crowding`, because the playbook's §4.10 precedent directs
this shape to the architectural reading.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**.
  `cross_passage_conjunction_unresolved` is item 4 and was already in the
  inventory, where it is also the provisional primary of queue item 24, so this
  decision introduces no new primary name. `near_title_collision` remains item 12
  of the inventory union but now has **no current `case_memos_v2.csv` row**,
  because this unit was the only one carrying it; it is preserved in
  `case_memos_v1.csv` as a historical first-pass name. This is the same treatment
  D-021 gave `weak_lexical_name_anchor` on the secondary side.
- The secondary-name union is unchanged at **48 distinct names**; D-022 adopts
  only already inventoried names.
- `case_memos_v2.csv` now holds **70 secondary assignments over 42 distinct
  names**, up from 66 over 42: this row went from two descriptors to six, all of
  them already present elsewhere in the column. The distinct
  `primary_open_code` count in v2 falls from 20 to **19**, because
  `near_title_collision` leaves and `cross_passage_conjunction_unresolved` was
  already present. `case_memos_v1.csv` is unchanged at 39 distinct secondary
  names.
- The registry still contains **24 adopted descriptors**; D-022 adds no new
  entry. Six existing entries gain this affected unit and D-022 as a decision
  source, and `cross_passage_conjunction_unresolved` gains a note recording its
  first primary use without any change to its definition, inclusion rule, or
  exclusion rule.
- `review_status` counts are now 13 `jointly_reviewed` and 17
  `needs_joint_review`. Thirteen rows now carry a populated `candidate_category`.
- The `surface_form_tokenization_mismatch` include rule gains one worked
  illustration, the singular/plural pair `novels` against `novel`, recorded
  explicitly as an added example within the existing definition rather than as a
  widening.
- Validation progress after D-022 is **9 of 26 validated, 17 remaining**,
  superseding the 8-of-26 figure recorded in section 7A.5.

These remain vocabulary counts, not validated mechanism counts and not
prevalence.

## Section 7A.7 — Validate `5ade69e455429975fa854ec5|dense`

D-023 replaces the primary `named_entity_anchor_distraction` with
`description_only_bridge_entity`. Re-encoding the same 4,937-passage pooled
corpus reproduces all 50 formal top-50 titles in order with a maximum absolute
score error of 3.576e-07 and places the golds at complete-corpus ranks 7
(0.495152) and 32 (0.400140). Both are retrieved. The rank-5 score is 0.516518,
so the answer hop is 0.021367 points, or 4.137 percent, below the cutoff and the
bridge hop is 0.116378 points, or 22.531 percent, below it. Both golds sit well
inside the 256-token sequence limit at 108 and 145 model tokens, so truncation is
excluded for them.

The question never names the bridge film; it designates it only as "a film
starring actors Rajneesh Duggal and Adah Sharma". All eight cells of the defined
F x V x A query-deletion design were run, together with an indexing condition T,
five gold-targeted text ablations plus one length-matched control, four removal
probes, five oracle-name conditions, seven interaction cells, and ten
reduced-query probes: 37 conditions and 10 probes in total. Title inclusion (T)
is negative for both hops and is excluded as the mechanism. No non-oracle single
factor recovers both hops. Every one of the five oracle-name forms recovers both,
at 1 and 3, including the bare name `1920`, which makes this the second unit
after D-017 to pass the single-factor oracle-name test that D-020, D-021, and
D-022 each failed. Two probes separate absence of the name from weakness of the
name: probe Q4 reduces the query to `1920` alone and the golds rank 1 and 2,
while probe Q8 reduces it to the description alone and the two passages that
actually satisfy the description rank 21 and 26 behind the actors' own pages.

This unit records the project's first accepted dilution-shaped claim. The bridge
passage states every query constraint verbatim yet ranks 32; a controlled
index-side ablation retaining only its two query-relevant sentences moves it to
rank 1, with a monotone dose-response at 29 and 13 for intermediate reductions,
while a length-matched control retaining only its plot sentences moves it to 50.
D-013 and D-015 had recorded every such claim as speculation because no
controlled ablation had been run; the new descriptor's inclusion rule is the gate
that separates the two situations rather than a reversal of those decisions.

The validated secondaries are the newly registered
`peripheral_passage_content_dilution`, `gold_chain_substitutability`,
`generic_person_semantic_neighborhood`, and `cutoff_sensitive_near_miss`. The
closest competitor is `peripheral_passage_content_dilution`, rejected as primary
because it recovers only the bridge hop and requires a partner condition. Both
provisional secondaries are removed on direct evidence: `low_information_title`
fails under condition T on the indexing reading and under probe Q4 and condition
N3 on the semantic reading, and `film_series_entity_collision` has no third
confusable entity and no displacement mechanism under an independently scored
encoder.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**.
  `description_only_bridge_entity` is item 5, was already in the inventory, and
  remains the first-pass primary of queue item 12, so this decision introduces no
  new primary name. `named_entity_anchor_distraction` remains item 11 of the
  inventory union but now has **no current `case_memos_v2.csv` row**, because
  this unit was the only one carrying it; it is preserved in `case_memos_v1.csv`
  as a historical first-pass name. This is the same treatment D-022 gave
  `near_title_collision` and D-021 gave `weak_lexical_name_anchor`.
- The secondary-name union grows from 48 to **49 distinct names** with the
  addition of `peripheral_passage_content_dilution`. `low_information_title` and
  `film_series_entity_collision` remain in the union as historical first-pass
  names and now have no current v2 row.
- `case_memos_v2.csv` now holds **72 secondary assignments over 41 distinct
  names**, up from 70 over 42: this row went from two descriptors to four, the
  two removed names were unique to it, and the one added new name is also unique
  to it, so the distinct count falls by one. The distinct `primary_open_code`
  count in v2 falls from 19 to **18**, because `named_entity_anchor_distraction`
  leaves and `description_only_bridge_entity` was already present.
  `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry now contains **25 adopted descriptors**, adding
  `peripheral_passage_content_dilution`. Three existing entries,
  `cutoff_sensitive_near_miss`, `generic_person_semantic_neighborhood`, and
  `gold_chain_substitutability`, gain this affected unit and D-023 as a decision
  source, and `description_only_bridge_entity` gains a note recording its second
  primary use and the `for lexical retrieval` wording problem, without any change
  to its definition, inclusion rule, or exclusion rule.
- `review_status` counts are now 14 `jointly_reviewed` and 16
  `needs_joint_review`. Fourteen rows now carry a populated `candidate_category`.
- Validation progress after D-023 is **10 of 26 validated, 16 remaining**,
  superseding the 9-of-26 figure recorded in section 7A.6.

These remain vocabulary counts, not validated mechanism counts and not
prevalence.

## Section 7A.8 — Validate `5ae057fd55429945ae959328|bm25`

D-024 replaces the primary `compound_two_sided_crowding` with
`cross_passage_conjunction_unresolved`. Reconstruction over the same
4,937-passage pooled corpus reproduces all 50 formal top-50 titles in order with a
maximum absolute score error of exactly 0.000000 and places the golds at
complete-corpus ranks 8 (23.567502) for the bridge hop, Robert Smith (Illinois
politician), and 16 (19.841500) for the answer hop, General Mills. Both are
retrieved. The rank-5 score is 24.991523, so the bridge hop is 1.424021 points, or
5.698 percent, below the cutoff and the answer hop is 5.150023 points, or 20.607
percent, below it.

The question names the person but never names the company he founded. The query's
two facets each identify exactly one gold and are mutually antagonistic: the two
golds' matched query-token sets share only `in`, and 10 of the 19 single-factor
conditions move the two hops in opposite directions. All 16 cells of the defined
P x E x S x T design were run, together with four further preprocessing conditions,
two one-sided punctuation conditions, nine reduced-query probes, eight
single-query-token removals, four reachability probes, seven index-side removal
probes and nine oracle conditions: 59 conditions in total. Title inclusion (T) is
negative for the answer hop and is excluded as the mechanism, as in D-019, D-020,
D-021 and D-023. No single factor of any class places both hops in the top five,
and all four oracle-name forms fail, at 9 and 1, 21 and 1, 20 and 1, and 13 and 1,
which is the fourth failing application of the D-020 disqualifier against two
passes in D-017 and D-023.

Two removal probes carry the tie-break. Dropping the ten purely generic company
profiles above the answer hop, while leaving all four name-sharing rivals in place,
reaches 5 and 2 and is the only non-oracle condition that recovers both hops;
dropping the two Smith homonyms instead leaves the bridge hop at rank 8 unchanged,
and dropping all four name-sharing rivals still gives 12 and 7. Every one of the
seven passages above the bridge hop belongs to the generic-company family and not
one is a Smith homonym, which are ranked 9 and 11, below that gold. The original
note's stated uncertainty, whether company-token dilution or Smith-homonym
competition was decisive, is therefore resolved in favour of neither: one query cue
produces one competitor family that suppresses both sides.

The validated secondaries are `description_only_bridge_entity` and
`generic_term_lexical_crowding`. The closest competitor is
`description_only_bridge_entity`. The provisional secondary
`proper_name_homonym_collision` is removed on direct probe evidence.
`surface_form_tokenization_mismatch` and `minimal_preprocessing_score_distortion`
are considered and not adopted: the mismatch ladder finds no alignable form for any
unmatched query token in either gold, removing `city?` is bit-identical to the
baseline in every digit, and query-side punctuation normalization leaves the answer
hop unchanged while worsening the bridge hop. The `mills` against `mills,`
tokenization fact is real but lies on the diagnostic repair path rather than in the
observed run, and is recorded as a verified implementation fact and an attribution
boundary instead of as a mechanism.

Six further descriptors were considered and explicitly not adopted:
`generic_query_scaffold_score_inflation`, because content-bearing category terms
supply 23.351998 of the rank-1 passage's 30.370645 against 7.018647 from scaffold;
`cutoff_sensitive_near_miss`, because a bridge question needs both hops and the
answer hop is 20.607 percent below the rank-5 score at rank 16 of 4,937;
`gold_chain_substitutability`, `gold_chain_not_unique` and
`plausible_non_gold_answer`, because `robert smith` occurs in exactly 1 passage,
`general mills` in exactly 2 which are the two golds, and `golden valley` in
exactly 1, so neither hop has a substitute; and `same_topic_passage_distractor`,
because the competitors are generic category matches rather than passages in the
answer entity's own subject neighborhood. `entity_alias_reference_mismatch` and
`question_frame_semantic_crowding` are each excluded by their own routing clauses.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**.
  `cross_passage_conjunction_unresolved` is item 4, was already in the inventory,
  and is also the provisional primary of queue item 24. Unlike
  `near_title_collision` in D-022 and `named_entity_anchor_distraction` in D-023,
  the departing name `compound_two_sided_crowding` is item 2 and **keeps a current
  `case_memos_v2.csv` row**, because it remains the primary of
  `5a8d93ad554299653c1aa13d|dense` under D-018, so no name leaves the current v2
  primary column.
- The secondary-name union is unchanged at **49 distinct names**; D-024 adopts only
  already inventoried names. `proper_name_homonym_collision` also keeps a current v2
  row, as a registered secondary of `5a8d93ad554299653c1aa13d|dense` under D-018.
- `case_memos_v2.csv` still holds **72 secondary assignments over 41 distinct
  names**: this row went from two descriptors to two, one name left and one arrived,
  and both are present elsewhere in the column, so neither total moves. The distinct
  `primary_open_code` count in v2 is unchanged at **18**, because
  `compound_two_sided_crowding` remains present and
  `cross_passage_conjunction_unresolved` was already present.
  `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry still contains **25 adopted descriptors**; D-024 adds no new entry.
  Two existing entries, `description_only_bridge_entity` and
  `generic_term_lexical_crowding`, gain this affected unit and D-024 as a decision
  source, and `cross_passage_conjunction_unresolved` gains an extension to its
  existing primary-use note recording a second primary use, in every case without
  any change to a definition, inclusion rule, or exclusion rule.
- `review_status` counts are now 15 `jointly_reviewed` and 15
  `needs_joint_review`. Fifteen rows now carry a populated `candidate_category`.
- Validation progress after D-024 is **11 of 26 validated, 15 remaining**,
  superseding the 10-of-26 figure recorded in section 7A.7.
- One pending item is added to the vocabulary-audit backlog: whether the
  single-factor oracle-name test needs an explicit precondition that the injected
  anchor be matchable by the passage it names. D-024 holds that precondition as a
  registry usage note only.

These remain vocabulary counts, not validated mechanism counts and not
prevalence.

## Section 7A.9 - Validate `5ae0a59a55429945ae9593e2|dense`

D-025 replaces the primary `description_only_bridge_entity` with
`cross_passage_conjunction_unresolved`. Re-encoding the same 4,937-passage pooled
corpus reproduces all 50 formal top-50 titles in order with a maximum absolute
score error of 2.682e-07 and places the golds at complete-corpus ranks 8
(0.449564) for the answer hop, Catuvellauni, and 115 (0.222228) for the bridge
hop, Togodumnus, so the stored `not_in_top50` status means rank 115 of 4,937
rather than corpus absence. The rank-5 score is 0.470765, so the answer hop is
0.021201 points, or 4.503 percent, below the cutoff and the bridge hop is
0.248537 points, or 52.794 percent, below it. Both golds sit far inside the
256-token sequence limit at 29 and 45 model tokens, so truncation is excluded.

The question names neither gold. All eight cells of the defined A x B x C query
design were run, together with nine clause-level single factors, three further
wording conditions, an indexing condition T, twelve reduced-query probes, eleven
reachability probes, a five-step name-free ceiling search, eight oracle-name
conditions, seven index-side removal probes and three gold-targeted index-side
ablations: 66 conditions in total. Title inclusion is negative for the answer hop
and is excluded as the mechanism, as in D-019, D-020, D-021, D-023 and D-024. Ten
of the 20 single-factor conditions move the two hops in opposite score
directions, the same proportion D-024 recorded. All four bridge-name oracle forms
fail, at 10 and 2, 9 and 1, 8 and 1, and 8 and 1, and the two forms naming the
other gold fail at 1 and 66 and 1 and 54, which is the fifth failing application
of the D-020 disqualifier against two passes in D-017 and D-023, and the first
failing application on a Dense unit with the D-024 precondition verified in
advance. Only the two conditions that inject both names recover both hops, at 1
and 2 and at 2 and 1, and the name-free ceiling, reached by rewriting the question
from the bridge passage's own sentence with the name removed, is 4 and 14.

Three results carry the tie-break. First, both hops are individually reachable at
rank 1 from their own names, at 0.703075 and 0.532805, while each name demotes the
other hop, so the two required passages are antagonistic rather than jointly
addressable. Second, no removal probe helps the bridge hop: dropping all 11
corpus-wide March, Dunbar and Lothian passages leaves it at 107, dropping all 107
pooling-introduced passages above it returns it to exactly its per-question rank 8,
and only deleting all 113 non-gold passages above it recovers it, so its failure is
low absolute similarity rather than crowding and `compound_two_sided_crowding` has
nothing to compound. Third, deleting the entire descriptive referent clause
improves both hops, from 8 to 5 and from 115 to 70, so the clause meant to identify
the bridge entity is net negative for both required passages.

The validated secondaries are `description_only_bridge_entity`,
`question_frame_semantic_crowding`, `gold_chain_substitutability` and
`cutoff_sensitive_near_miss`. The closest competitor is
`description_only_bridge_entity`. Both provisional secondaries are removed:
`generic_context_substitution` because both readings of its name are already
covered by registered descriptors, the generic-context reading by
`question_frame_semantic_crowding` and the substitution reading by
`gold_chain_substitutability`; and `shared_retriever_failure` because it names
comparison-retriever behaviour rather than a mechanism, retriever identity being a
forbidden causal category under D-003. The underlying comparison observation is
preserved as provenance: complete-corpus BM25 ranks the answer hop 6 (28.287844)
and the bridge hop 846 (10.825051).

`peripheral_passage_content_dilution` is considered and explicitly excluded by its
own inclusion rule. The controlled ablation retaining the bridge passage's single
query-relevant sentence improves it from 115 to 39, but the control retaining only
its non-relevant sentence improves it further to 18, so the third include
condition, that the control must not improve the rank, fails in the strongest
possible direction and the effect is brevity rather than content. This is the first
application of that gate since D-023 created it, and it is a rejection, which is
what the gate was written to make possible. `generic_person_semantic_neighborhood`
is also considered and not adopted: the period-mismatched Scottish nobility family
is indeed a cluster of ruler biographies, but the descriptor's definition is scoped
to a question whose explicitly named target entities remain lower, and this question
names no entity at all, so adopting it would silently widen the definition.

This unit is the fourth in which per-question and pooled disagree on Any@5, after
D-022, D-023 and D-024, and it is of the D-022 and D-023 kind. Exactly 3 of the 7
passages above the answer hop are introduced by pooling, and they are exactly the
three Scottish nobility passages; dropping only those three returns the answer hop
to rank 5, precisely its per-question rank, and restores `any@5`. The idf and avgdl
check D-024 requires after a failed pooling-removal probe is inapplicable here and
was not run, because a cosine score carries no corpus statistic; the audit records
the verified consequence that a Dense per-question ranking is exactly the
restriction of the pooled ranking to that question's own paragraphs, which the
title-by-title reconstruction confirms. The bridge hop fails independently of
pooling, at rank 8 of 10 in HotpotQA's own context. Corpus setting remains
provenance under D-003.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**.
  `cross_passage_conjunction_unresolved` is item 4, was already in the inventory,
  and remains the provisional primary of queue item 24. The departing name
  `description_only_bridge_entity` is item 5 and **keeps two current
  `case_memos_v2.csv` primary rows**, `5a85cead5542991dd0999ea9|dense` under D-017
  and `5ade69e455429975fa854ec5|dense` under D-023, so no name leaves the current
  v2 primary column, as in D-024 and unlike D-021, D-022 and D-023.
- The secondary-name union is unchanged at **49 distinct names**; D-025 adopts only
  already inventoried names. `generic_context_substitution`, item 18, and
  `shared_retriever_failure`, item 38, remain in the union as historical first-pass
  names and now have **no current v2 row**, the treatment D-021 gave
  `weak_lexical_name_anchor` and D-023 gave `low_information_title` and
  `film_series_entity_collision`.
- `case_memos_v2.csv` now holds **74 secondary assignments over 39 distinct
  names**, up from 72 over 41: this row went from two descriptors to four, both
  removed names were unique to it, and all four adopted names already occur
  elsewhere in the column, so the assignment total rises by two and the distinct
  count falls by two. The distinct `primary_open_code` count in v2 is unchanged at
  **18**, because `description_only_bridge_entity` remains present and
  `cross_passage_conjunction_unresolved` was already present.
  `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry still contains **25 adopted descriptors**; D-025 adds no new entry.
  Four existing entries, `description_only_bridge_entity`,
  `question_frame_semantic_crowding`, `gold_chain_substitutability` and
  `cutoff_sensitive_near_miss`, gain this affected unit and D-025 as a decision
  source, and `cross_passage_conjunction_unresolved` gains an extension to its
  existing primary-use note recording a third primary use and the first on a Dense
  unit, in every case without any change to a definition, inclusion rule, or
  exclusion rule.
- `review_status` counts are now 16 `jointly_reviewed` and 14
  `needs_joint_review`. Sixteen rows now carry a populated `candidate_category`.
- Validation progress after D-025 is **12 of 26 validated, 14 remaining**,
  superseding the 11-of-26 figure recorded in section 7A.8.
- Three items are added to the vocabulary-audit backlog. First, whether
  `cross_passage_conjunction_unresolved` needs a primary-use contract now that it
  has three primary uses across both retrievers and that one leg of its D-022
  evidence set, disjoint matched token sets, has no Dense analogue. Second, whether
  `gold_chain_substitutability` requires its substitute to lie inside the evaluated
  cutoff, which this unit's rank-6 substitute does not. Third, whether the
  vocabulary needs a question-quality descriptor: this question states that the
  ruler was born in AD 43 while the gold passage records `(d. AD 43)`, the error is
  measured and found not decisive, and queue items 13 and 21 both carry a
  provisional `question_wording_ambiguity` that will have to be judged against it.

These remain vocabulary counts, not validated mechanism counts and not
prevalence.
## Section 7A.10 - Validate `5ae1f596554299234fd04372|dense`

D-026 replaces the primary `question_wording_ambiguity` with
`description_only_bridge_entity`. Re-encoding the same 4,937-passage pooled corpus
reproduces all 50 formal top-50 titles in order with a maximum absolute score error
of 2.980e-07 and places the golds at complete-corpus ranks 6 (0.473542) for the
bridge hop, 2008 Summer Olympics, and 13 (0.361134) for the answer hop, Summer
Olympic Games. Both are retrieved. The rank-5 score is 0.479079, so the bridge hop
is 0.005537 points, or 1.156 percent, below the cutoff, the smallest margin recorded
in this project, and the answer hop is 0.117945 points, or 24.619 percent, below it.
Both golds sit inside the 256-token sequence limit at 144 and 131 model tokens, so
truncation is excluded.

The question never names the required entity. All eight cells of the defined
A x B x C wording-repair design were run, together with six further wording
conditions, five name-free disambiguation conditions including an uncased null
control, a five-step name-free ceiling search, seven single-clause deletions, twelve
reduced-query probes, six reachability probes, seven oracle-name conditions, an
indexing condition T, six index-side removal probes, twelve gold-targeted index-side
text conditions including two null controls and eight length-matched controls, and
one combined ablation: 75 conditions in total. Title inclusion is negative for the
bridge hop and is excluded as the mechanism, as in D-019, D-020, D-021, D-023, D-024
and D-025.

The provisional primary is falsified by measurement rather than by argument, which is
the point of running the design in full. Repairing every grammatical defect of the
malformed question moves the pair only from 6 and 13 to 5 and 12, and the strongest
name-free rewrite of its vague head noun reaches only 2 and 7. Both readings of the
name were tested with explicit conditions, as pit 19e requires. By contrast all seven
oracle-name forms recover both hops, at 1 and 3, 1 and 2, 1 and 2, 1 and 2, 2 and 1,
1 and 2, and 1 and 3, which is the third pass of the single-factor oracle-name test
D-020 introduced, after D-017 and D-023, against five failures. The D-024 precondition
was verified in advance and holds in a stronger form than in any earlier unit: each
bare gold name ranks the passage it names 1 and also lifts the other required passage
to 2.

Two results carry the tie-break. First, the observed competitor family is the primary
mechanism's own output, and this unit is the first to test that in both directions:
the referent cue alone reproduces 10 of 10 of its top ten inside the baseline top
twelve, and deleting that cue leaves only 3 of 10, while the answer facet alone
reproduces 0 of 10. D-023 established the forward test and D-024 applied it to a
lexical retriever; the reverse test agrees here. Second,
`peripheral_passage_content_dilution` passes all four of its include conditions on
both required passages, the first unit in which that has happened, yet it loses the
primary tie-break because each ablation recovers only one hop and applying both at
once still leaves the answer hop at 8.

The validated secondaries are `peripheral_passage_content_dilution` and
`cutoff_sensitive_near_miss`. The closest competitor is
`peripheral_passage_content_dilution`. The unregistered provisional secondary
`adjacent_event_crowding` is removed and deliberately not registered, because a
registry entry for it would duplicate `question_frame_semantic_crowding`, which is
itself excluded here by its own inclusion rule. `cross_passage_conjunction_unresolved`
is considered and not adopted on three measurements: every name probe lifts both hops
together where D-025 recorded the opposite sign, only 4 of 19 single factors carry
opposite signs against 10 of 19 in D-024 and 10 of 20 in D-025, and one anchor reaches
both required passages, so no intermediate fact must be carried across passages.
`compound_two_sided_crowding` is excluded because one removal probe against a single
competitor family recovers both hops at 1 and 4.

This unit is the fifth in which per-question and pooled disagree, after D-022, D-023,
D-024 and D-025, and the **first in which they disagree on `full@5`** rather than only
on `any@5`: pooled `any@5` and `full@5` are both 0, while per-question places the two
golds at 2 and 3 of 10 so both metrics are 1. The four earlier units all had `full@5`
0 in both settings, and the handoff statement to that effect is superseded here. It is
also the first unit whose failure is confined entirely to the pooled setting, since
neither hop fails in HotpotQA's own context. Mechanically it is of the D-022, D-023
and D-025 kind: exactly 10 of the 12 passages above the answer hop are introduced by
pooling and dropping only those returns the ranking to 2 and 3, precisely the
per-question ranks. The idf and avgdl check D-024 requires after a failed
pooling-removal probe is inapplicable and was not run, because a cosine score carries
no corpus statistic; the audit records the verified consequence, first established in
D-025, that a Dense per-question ranking is exactly the restriction of the pooled
ranking to that question's own paragraphs, which the title-by-title reconstruction and
the identity of removal probes X2 and X6 both confirm. Corpus setting remains
provenance under D-003.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**.
  `description_only_bridge_entity` is item 5, was already in the inventory, and is
  now the primary of three current `case_memos_v2.csv` rows,
  `5a85cead5542991dd0999ea9|dense` under D-017, `5ade69e455429975fa854ec5|dense`
  under D-023 and this unit. The departing name `question_wording_ambiguity` is item
  19 and **keeps a current v2 primary row**, `5adc8977554299438c868de2|bm25` as queue
  item 21, so no name leaves the current v2 primary column, as in D-024 and D-025 and
  unlike D-021, D-022 and D-023.
- The secondary-name union is unchanged at **49 distinct names**; D-026 adopts only
  already inventoried names. `adjacent_event_crowding`, item 1, remains in the union
  as a historical first-pass name and now has **no current v2 row**, the treatment
  D-021 gave `weak_lexical_name_anchor`, D-023 gave `low_information_title` and
  `film_series_entity_collision`, and D-025 gave `generic_context_substitution` and
  `shared_retriever_failure`.
- `case_memos_v2.csv` now holds **74 secondary assignments over 38 distinct names**,
  unchanged from 74 but down from 39: this row went from two descriptors to two, the
  removed name was unique to it, and the adopted name already occurs elsewhere in the
  column, so the assignment total does not move and the distinct count falls by one.
  The distinct `primary_open_code` count in v2 is unchanged at **18**, because
  `question_wording_ambiguity` remains present and `description_only_bridge_entity`
  was already present. `case_memos_v1.csv` is unchanged at 39 distinct secondary
  names.
- The registry still contains **25 adopted descriptors**; D-026 adds no new entry.
  Two existing entries, `peripheral_passage_content_dilution` and
  `cutoff_sensitive_near_miss`, gain this affected unit and D-026 as a decision
  source, and `description_only_bridge_entity` gains an extension to its existing
  primary-use note recording a third primary use, in every case without any change to
  a definition, inclusion rule, or exclusion rule.
- `review_status` counts are now 17 `jointly_reviewed` and 13 `needs_joint_review`.
  Seventeen rows now carry a populated `candidate_category`.
- Validation progress after D-026 is **13 of 26 validated, 13 remaining**, superseding
  the 12-of-26 figure recorded in section 7A.9.
- One backlog item recorded in section 7A.9 receives its first measurement rather than
  a new entry. D-025 asked whether the vocabulary needs a question-quality descriptor
  and named queue items 13 and 21, both of which carried a provisional
  `question_wording_ambiguity`. Queue item 13 is this unit, and here the complete
  eight-cell grammatical-repair factorial and the four name-free disambiguation
  conditions together show the malformation is not outcome-determinative, so this unit
  argues against creating such a descriptor on the strength of surface malformation
  alone. Queue item 21 is a BM25 unit and must be judged separately.
- Two further items are added to the backlog. First, whether
  `description_only_bridge_entity` should distinguish a described entity that is a
  pure bridge, as in D-017 and D-023, from one that is also the subject of the answer
  passage, as here. Second, whether
  `peripheral_passage_content_dilution` should require its length-matched control to
  be run at more than one length, since in this unit the 30-word control ranks 101
  while the 68-word control ranks 23 and a single control point would have been
  readable either way.
- One synchronization correction is recorded rather than performed silently. The queue
  row for `5ae0a59a55429945ae9593e2|dense`, queue item 12, still carried its
  pre-validation provisional primary and secondary values after D-025 landed, while
  `case_memos_v2.csv`, D-025, the registry and this audit all carried the validated
  ones. D-026 corrects that row to match the other four sources. The queue's own
  header states that the two columns are snapshots copied from `case_memos_v2.csv`,
  so this is a transcription omission and not a semantic decision; it is not the same
  situation as the D-010 row discrepancy recorded in section 7.2, which concerns which
  descriptors a decision adopted and remains open.

## Section 7A.11 - Validate `5a78b209554299148911f93e|dense`

D-027 replaces the primary `related_document_crowding` with
`one_sided_entity_crowding`. Re-encoding the same 4,937-passage pooled corpus
reproduces all 50 formal top-50 titles in order with a maximum absolute score error of
2.384e-07 and places the two candidates at complete-corpus ranks 9 (0.432454) for
Edward Albee and 8 (0.434342) for J. M. Barrie. Both are retrieved. The rank-5 score is
0.538556, so they sit 0.106102 and 0.104214 points, or 19.701 and 19.351 percent, below
the cutoff, and a gap of 0.067081 separates rank 7 from rank 8. Both golds sit inside
the 256-token sequence limit at 95 and 167 model tokens, so truncation is excluded.

This is the first comparison unit in the single-note validation pass and the fourth
Dense unit. Both required passages are candidates the question names outright, and each
supplies one lifespan. Sixty-six distinct conditions were run on the same unchanged
candidate set, plus seven deliberate duplicates that all reproduced bit for bit: an
indexing condition T, all eight cells of an A x B x C wording-repair factorial, eleven
reachability probes, three further reduced-query probes, three reverse cue-deletion
probes, twelve index-side removal probes including a six-step cumulative dose-response
ladder and a restriction to the item's own ten passages, twenty-two gold-targeted
index-side text conditions including two single-row null controls and name-preserving
length-matched controls on both sides, and six oracle conditions. Title inclusion is
negative and is excluded as the mechanism, as in D-019, D-020, D-021, D-023, D-024,
D-025 and D-026.

Two results carry the tie-break. First, per-side reachability is radically asymmetric,
and this is the first unit in which the D-025 evidence leg, each side reachable at rank
1 from its own bare name, fails on one side. J. M. Barrie ranks 1 under all five distinct
non-oracle single-sided queries tried, while Edward Albee reaches the top five under none
of the five on its own side, at 6, 7, 8, 7 and 7. Its own satellite documents outrank it
even when the query is nothing but its name. The one Albee-directed query that does reach
the cutoff, at 5, is an oracle condition using the gold passage's own formal name form,
and it pushes the other side to 3221, so it recovers nothing. Second, index-side removal of the
Albee-related family is the only intervention of any kind that recovers both required
passages, and it is monotone: dropping them one at a time in baseline rank order gives
8 / 7, 7 / 6, 6 / 5, 5 / 4, 4 / 3 and 3 / 2, so the pair enters the top five once four
are removed. All eight wording-repair cells fail, all six oracle conditions fail, and
query splitting, the natural deployable repair for a comparison question, fails in three
forms, so no deployable non-oracle repair exists. Under every removal condition the
golds' own scores are unchanged, so the claim is that the competitors occupy the
top-five positions and never that they depress the golds' similarity.

The competitor family is verified in both directions, as pit 19i requires: the Albee
referent cue alone reproduces 6 of 10 of its top ten inside the baseline top seven and
8 of 10 inside the top twelve, while deleting that cue leaves 1 of 10 and no
Albee-related passage at all, the generic type cue alone gives 2 of 10 and the answer
facet alone gives 0 of 10. D-027 records an asymmetry with how D-023, D-024 and D-026
used that test: there the cue that reproduced the neighborhood was a descriptive
referent and the forward result routed the crowding descriptor away from the primary,
whereas here the cue is one of the two candidates the question must name, so there is no
more specific upstream mechanism to route to and the test identifies the mechanism
rather than demoting it.

The validated secondaries are `related_name_document_crowding` and
`peripheral_passage_content_dilution`, the latter scoped to Edward Albee only. The
closest competitor is `related_name_document_crowding`. `cutoff_sensitive_near_miss` is
removed on the score gap alone, the second removal after D-015 and the first on that
ground; the no-substitute condition that supported D-022, D-023 and D-026 is met here,
since exactly one passage in the corpus states each required lifespan, itself.
`related_document_crowding` is deliberately not registered, because a registry entry for
it would duplicate `related_name_document_crowding`, whose definition already covers
relatives, works, institutions and associates, the reason D-025 used for
`generic_context_substitution` and D-026 for `adjacent_event_crowding`.
`compound_two_sided_crowding` is excluded because one competitor family suppresses both
required passages under pit 19h and the Barrie side has no competitor family at all,
only 4 non-gold corpus passages containing the string barrie and none of them in the
reconstructed top 50. `generic_person_semantic_neighborhood` is excluded by its own
exclusion, which names the case where documents related to only one comparison entity
dominate. `same_artist_work_crowding` meets its inclusion rule, and the 4 Albee works
alone are sufficient to cause the double failure, but its definition is anchored on
sibling works outranking a gold work while the gold here is the creator's biography, and
its content is already covered by the adopted name.
`cross_passage_conjunction_unresolved` is considered and not adopted because its
inclusion rule requires an intermediate fact to be resolved in one passage and carried
into scoring another, and a comparison question's two lifespans are independent, so the
contract is bridge-shaped; this is the first unit in the pass to reject the name on that
clause specifically. `two_named_entities_underprioritized` is excluded because the Albee
name is not underweighted but overwhelmingly effective, merely at the wrong Albee
documents, the opposite of D-009.

This unit breaks the pooling series rather than extending it. Pooled and per-question
agree on both metrics, `any@5` 0 and `full@5` 0, the first unit in which the corpus
setting changes neither, after five consecutive units in which at least `any@5` flipped,
and the second after D-021 in which per-question failure excludes pooling outright. Six
of this item's own eight HotpotQA distractors are Albee-related and hold per-question
ranks 1 to 6 ahead of the golds at 7 and 8, so the competitor family is
annotator-constructed rather than pooling-introduced, which is a third source distinct
from both paths recorded so far, new competitors and idf scale. Pooling adds exactly one
competitor above the golds and dropping only it gives 8 / 7. Restricting the pooled
ranking to the item's ten paragraphs reproduces the official per-question window title
by title, confirming for the second time after D-025 that a Dense per-question ranking
is exactly the restriction of the pooled ranking, so the idf and avgdl check D-024
requires after a failed pooling-removal probe is inapplicable and was not run. Corpus
setting remains provenance under D-003.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**.
  `one_sided_entity_crowding` is item 13, was already in the inventory, and now has its
  **first validated primary use**. Before this unit it survived there only as a
  first-pass value on two rows: this example's BM25 unit, superseded by D-010 through
  `candidate_category`, and `5ab8f57b5542991b5579f097|bm25` as queue item 19, still
  `not_started`. The provenance sentence in section 7.1 therefore still holds, but the
  name is no longer inventoried on residual first-pass grounds alone. The departing name
  `related_document_crowding` is item 21 and **keeps no current v2 primary row**, the
  treatment D-021, D-022 and D-023 gave their departing names and unlike D-024, D-025
  and D-026.
- The secondary-name union is unchanged at **49 distinct names**; D-027 adopts only
  already inventoried names and registers no new descriptor.
- `case_memos_v2.csv` now holds **75 secondary assignments over 38 distinct names**, up
  from 74 and unchanged from 38: this row went from one descriptor to two, both adopted
  names already occur elsewhere in the column, and the removed name also occurs
  elsewhere. The distinct `primary_open_code` count in v2 falls from **18 to 17**,
  because `related_document_crowding` was unique to this row and
  `one_sided_entity_crowding` was already present on two others.
  `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry still contains **25 adopted descriptors**; D-027 adds no new entry. Two
  existing entries, `related_name_document_crowding` and
  `peripheral_passage_content_dilution`, gain this affected unit and D-027 as a decision
  source, and `cutoff_sensitive_near_miss` gains D-027 as a decision source recording a
  removal rather than an affected unit. In every case no definition, inclusion rule or
  exclusion rule is changed.
- `review_status` counts are now 18 `jointly_reviewed` and 12 `needs_joint_review`.
  Eighteen rows now carry a populated `candidate_category`.
- Validation progress after D-027 is **14 of 26 validated, 12 remaining**, superseding
  the 13-of-26 figure recorded in section 7A.10.
- Three items are added to the backlog. First, whether crowding-family names need an
  explicit primary-use contract of the kind
  `cross_passage_conjunction_unresolved` already carries a note about, given that
  `one_sided_entity_crowding` is now a validated primary while D-010 described it as the
  resulting ranking pattern and less specific. D-027's position is narrower, that the
  name states which documents compete and which of the two named candidates they belong
  to rather than anything about rank itself, so pit 17 is not violated, on the same
  footing that let D-018 adopt `compound_two_sided_crowding`. Second, whether
  `related_name_document_crowding` needs rewording for a bi-encoder: its definition
  reads `sharing a name or name token`, which is lexical, and this is its first Dense
  use. All 6 competitors do literally contain `Albee`, so the surface fact holds. This is
  the same kind of question already open for `description_only_bridge_entity`, whose
  definition still says `for lexical retrieval` while all three of its primary uses are
  Dense. Third, whether `cutoff_sensitive_near_miss` should carry a numerical threshold
  for `far below the cutoff`. The measured band is now well populated, with acceptances
  at 1.156, 2.17, 4.137 and 4.503 percent and exclusions at 19.351, 19.701, 24.619 and
  52.794 percent, so the audit has the evidence to set one; doing so would edit that
  registry entry and is deferred under section 7A's rule.
- One earlier backlog item receives a second measurement rather than a new entry. D-026
  asked whether `peripheral_passage_content_dilution` should require its length-matched
  control at more than one length. This unit ran four length points per side and adds a
  second, independent requirement from measurement: the control must also **preserve the
  entity name**. Its first four Albee-side controls each dropped the name along with the
  non-relevant content and produced ranks between 14 and 630 with no relation to length,
  which is uninterpretable. The decisive pair is name-preserving and length-matched at
  once, 40 words at rank 2 against 41 words at rank 8, differing only in which
  non-relevant span is retained.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.12 - Validate `5a79b7f6554299029c4b5f6f|bm25`

D-028 replaces the primary `generic_term_lexical_crowding` with
`minimal_preprocessing_score_distortion`. Rebuilding the same 4,937-passage pooled BM25
index reproduces all 50 formal top-50 titles in order with a maximum absolute score error
of 0.000000, every per-token decomposition reconciles against `get_scores` within
7.105e-15, and the two required passages sit at complete-corpus ranks 16 (21.492350) for
Ron Joyce and 8 (27.226538) for Tim Hortons. Both are retrieved. The rank-5 score is
31.122376, so they sit 9.630026 and 3.895838 points, or 30.942 and 12.518 percent, below
the cutoff, and there is no score cliff, the successive differences from rank 4 to rank 9
being 0.597253, 1.720835, 0.694195, 1.480808 and 1.252255.

This is the sixth BM25 unit in the single-note validation pass and the ninth bridge unit.
Ninety-four conditions were run on the same unchanged candidate set, two of them deliberate
duplicates that reproduced bit for bit: all sixteen cells of a P x E x S x T preprocessing
and indexing factorial, six further cells adding a crude morphological stem, three
single-sided controls splitting the punctuation factor into its query-side and
document-side halves, five gold-targeted index-side single-token repairs including a null
control, six query wording conditions, fourteen single query-token deletions, twelve
reduced-query probes, five reverse cue-deletion probes, seven per-side reachability probes,
eleven index-side removal probes including a six-step cumulative dose-response ladder,
seven oracle conditions, and two corpus-setting reconstructions.

The structural fact is that the two required passages match completely disjoint
query-token sets. Ron Joyce scores 21.492350 from three tokens only, joyce 11.846012,
chain 6.841956 and the 2.804382, while Tim Hortons scores 27.226538 from four tokens that
all belong to the generic category facet and earns nothing from the queried person's name.
Each of the fifteen non-gold passages above the bridge gold earns between 18.094218 and
29.047969 from that same facet and exactly 0.000000 from ron and joyce, so the corpus's
only occurrence of joyce, one passage in 4,937 at an idf of 8.098947, is worth less to its
own passage than the generic facet is worth to any competitor; the facet sums to an idf of
25.249066 against 13.796955 for the name.

Two results carry the tie-break. First, the only non-oracle conditions that place both
required passages inside the cutoff are the four factorial cells containing both
boundary-punctuation normalization and title indexing, at 2 / 34.444959 and 4 / 32.279538
for the smallest of them, and the interaction is clean: punctuation normalization alone
recovers only the answer hop, at 7 / 29.569770 and 3 / 32.295791, and title indexing alone
recovers only the bridge hop, at 2 / 32.480848 and 9 / 27.212243, moving the answer hop the
wrong way. Without title indexing the bridge hop reaches 7 at best under any condition of
any kind; without punctuation normalization it reaches 7 at best and never enters the
cutoff. This is the
first unit in this project in which title indexing is materially positive, against D-019,
D-020, D-021, D-023, D-024, D-025 and D-026, all of which measured it inert or negative.
Second, the whole punctuation effect is index-side: query-side-only normalization
reproduces the baseline exactly, because the single query token it changes, found?, is
absent from the corpus vocabulary altogether, and index-side-only normalization reproduces
the full condition exactly. Single-token gold-targeted repairs against a null control price
each artifact separately, the quotation marks in `Ronald Vaughan "Ron" Joyce` at 8.247890
points and ten rank positions and the semicolon in `restaurant chain;` at 5.481747 points
and six, and repairing both at once still leaves the bridge hop at 7, so punctuation alone
is insufficient even as a gold-targeted intervention.

Eight of the eighteen single factors are completely inert, including the deletion of ron,
helped and found?; found? occurs in 0 corpus passages against 75 for found, the third
instance of an out-of-vocabulary query token after D-019 and D-021, and no wording
condition repairs it because co-founded? and founded? are equally absent. Six single
factors carry opposite signs across the hops, against 21 of 50 in D-027, 4 of 19 in D-026,
10 of 20 in D-025 and 10 of 19 in D-024.

The competitor family is verified in both directions, as pit 19i requires, and this is the
first unit in the pass where the two-way test demotes a name that arrived as the
provisional primary: forward, the descriptive referent cue alone puts 9 of 10 of its top
ten inside the baseline top-fifteen non-gold set; in reverse, deleting that cue leaves 3 of
10 while deleting the person's name instead leaves the family untouched at 9 of 10.
Index-side removal cannot recover the bridge hop, the cumulative ladder giving 15 / 7,
14 / 6, 13 / 5, 12 / 4, 11 / 3 and 10 / 2, so six removals move it only from 16 to 10.

The validated secondaries are `surface_form_tokenization_mismatch`, the newly registered
`unindexed_title_name_anchor`, `generic_term_lexical_crowding` and
`description_only_bridge_entity`. The closest competitor is
`description_only_bridge_entity`, whose single-factor oracle-name test passes in five forms
with the D-024 precondition verified, its fourth pass and its first on a BM25 unit, and
which still loses the primary because its entire support is oracle and because a
non-oracle condition moves the un-named hop from 8 / 27.226538 to 3 / 32.295791 on its own.
That extends the D-021 precedent to a case where the test passes rather than fails.
`cross_passage_conjunction_unresolved` is not adopted although all three legs of the D-022
and D-024 evidence set hold, because a non-oracle condition that supplies no intermediate
fact recovers both hops. `cutoff_sensitive_near_miss` is withheld on the score gap alone,
following D-027; the 12.518 percent figure falls in a previously unmeasured band and
narrows the untested range to 4.503 to 12.518 percent.
`generic_query_scaffold_score_inflation` is excluded by its own clause naming the case
where content-bearing category terms rather than query scaffold explain the competition.
The two repeated-amplification names are excluded because the query has no repeated token
under the implemented tokenizer; the conceptual repetition of the category noun becomes a
repeated token only under the stemming condition, which is negative on both hops.
`entity_alias_reference_mismatch` is excluded because the query's `Ron Joyce` and the
body's `"Ron" Joyce` are the same appellation and the mismatch is punctuation.
`bridge_relation_underweighted`, the provisional secondary, is deleted rather than
registered, because the name implies a weighting mechanism while both relation tokens are
measured completely inert, and `surface_form_tokenization_mismatch` already covers the real
fact; that is the reason D-025 used for `generic_context_substitution`, D-026 for
`adjacent_event_crowding` and D-027 for `related_document_crowding`.

This unit resumes the pooling series that D-027 broke, and it separates the two paths for
the first time. Pooled gives `any@5` 0 and `full@5` 0 while per-question gives `any@5` 1 and
`full@5` 0, with the golds at 3 and 7 of 10, so the divergence is again on `any@5` only.
The per-question rebuild reproduces the official window title by title. Restricting the
pooled scores to those same ten paragraphs puts the golds at 10 and 7 of 10, so with the
document set held fixed and only the collection statistics changed the bridge hop moves
from 3 to 10, which isolates the idf-scale path D-024 identified and establishes the
converse of the D-025 Dense property: a BM25 per-question ranking is not the restriction of
the pooled ranking. In the per-question index avgdl is 62.400000 against 90.884950, the
four category tokens all fall to an idf of 0.410358, restaurants falls from 5.480131 to
0.762140, joyce falls from 8.098947 to 1.845827, and how, many, comprise, ron and helped
are absent from the vocabulary entirely. The new-competitor path is present but secondary,
only 6 of the 14 passages above the bridge gold and only 1 of the 7 above the answer gold
being pooling-introduced and removing exactly those recovering neither, and the
annotator-constructed path D-027 identified is present too, eight of this item's own ten
paragraphs being restaurant-chain profiles. This is the first unit in which all three
recorded paths appear together. Corpus setting remains provenance under D-003.

### Inventory effect

- The primary inventory is unchanged at **25 distinct names**.
  `minimal_preprocessing_score_distortion` is item 9 and reaches its **sixth unit**, after
  D-012, D-014, D-016, D-019 and D-021, which makes the breadth question already recorded
  as open item 5 of the handoff sharper rather than settling it: the name now covers
  repeated function-word amplification, punctuation false negatives, scaffold inflation,
  Unicode dash mismatch and, here, a two-factor interaction between boundary punctuation
  and indexed-field selection. The departing name `generic_term_lexical_crowding` is item
  7 and **keeps no current v2 primary row**, the treatment D-021, D-022, D-023 and D-027
  gave their departing names.
- The secondary-name union grows from 49 to **50 distinct names** with
  `unindexed_title_name_anchor`.
- `case_memos_v2.csv` now holds **78 secondary assignments over 39 distinct names**, up
  from 75 and 38: this row went from one descriptor to four, three of which already occur
  elsewhere in the column, and the removed name `bridge_relation_underweighted` still
  occurs on two other rows, queue items 18 and 22, so it does not leave the column. The
  distinct `primary_open_code` count in v2 falls from **17 to 16**, because
  `generic_term_lexical_crowding` was unique to this row as a primary while
  `minimal_preprocessing_score_distortion` was already present on five others.
  `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry grows from 25 to **26 adopted descriptors** with
  `unindexed_title_name_anchor`. Three existing entries gain this affected unit and D-028
  as a decision source, `surface_form_tokenization_mismatch`,
  `generic_term_lexical_crowding` and `description_only_bridge_entity`, and two gain D-028
  as a decision source recording a non-adoption rather than an affected unit,
  `cutoff_sensitive_near_miss` and `cross_passage_conjunction_unresolved`. In every case no
  definition, inclusion rule or exclusion rule is changed.
- `review_status` counts are now 19 `jointly_reviewed` and 11 `needs_joint_review`.
  Nineteen rows now carry a populated `candidate_category`.

## Section 7A.13 - Validate `5a81ebee554299676cceb16d|dense`

D-029 replaces the primary `cross_entity_relation_unresolved` with
`question_frame_semantic_crowding`. Rebuilding the same 4,937-passage pooled Dense index
from the manifest-guarded document matrix reproduces all 50 formal top-50 titles in order
with a maximum absolute score error of 3.278e-07, and the two required passages sit at
complete-corpus ranks 43 (0.365309) for Matilda Lutz and 94 (0.332391) for Rings (2017
film), so the stored `not_in_top50` means rank 94 rather than absence. The rank-5 score is
0.460548, so they sit 0.095238 and 0.128157 points, or 20.679 and 27.827 percent, below the
cutoff, and there is no score cliff, the successive differences from rank 1 to rank 10 being
0.002518, 0.010296, 0.034229, 0.007743, 0.004229, 0.006203, 0.004349, 0.001895 and 0.003646.

This is queue item 16, the ninth Dense analytical unit and the thirteenth bridge unit among
the sixteen validated single-note units. One hundred and thirty-two conditions were run on
the same unchanged candidate set, twelve of them deliberate duplicates that reproduced bit
for bit, which makes it the largest single-unit diagnostic in the project so far: all eight
cells of an A x B x C query-wording factorial, the indexing condition and three of its
crossings, eight further wording conditions, eight name-free ceiling rewrites, ten
single-clause and single-token deletions from the full question, ten per-side reachability
probes, eight frame-only reduced-query probes, one query-splitting probe completing three
split pairs, eighteen name-position probes, twenty-two index-side removal probes including
two cumulative dose-response ladders, twenty-three gold-targeted content conditions
including a null control and length-matched controls on both required passages, ten oracle
conditions, one per-question reconstruction and the baseline.

The structural fact is that the question names exactly one entity, the director, that entity
has no passage of its own anywhere in the corpus, and both required passages are referred to
only by description. The name is measured to be unusable as an anchor: the corpus contains
the accented surname in exactly one passage, the answer gold, and the unaccented form in
exactly one other, and reducing the query to that name ranks the answer gold 2202 (0.057835)
while the bare surname ranks it 4243 (-0.047993). This is not a query-length effect, since
the four-word descriptive query `Italian model and actress` ranks the bridge gold 14
(0.459121), and not a spelling effect, since the tokenizer lower-cases and strips accents so
the accented and unaccented forms are bit-identical no-ops. Five further names taken from the
same answer passage behave the same way, between 533 and 2914, while the two names standing
in subject position at the start of their own passage rank those passages 1 (0.633059) and 1
(0.560012).

The competing family was verified in both directions, which is the D-026 standard under pit
19i. Every passage above the bridge gold and every passage between it and the answer gold was
read in full: of the 42 above the bridge gold, 36 carry a film or directing cue, 19 a
person-role cue, 16 both and 12 the word `italian`, and of the 92 above the answer gold the
same counts are 77, 48, 41 and 20, with exactly one sharing the queried surname and none
containing either required subject's name. Forward, a query reduced to the director's name
puts only 4 of 10 of its top ten inside the baseline top-42 and 2 of 10 inside the baseline
top ten, so the referent does not build the family; in reverse, deleting the whole director
name leaves 8 of 10 inside the top-42 and deleting the descriptive referent instead leaves 8
of 10 inside the top-42 and 6 of 10 inside the top ten, so the family survives deletion of
either cue. The third exclusion clause therefore does not fire and the family belongs to the
question's framing.

What carries the primary is that a family-scoped index-side removal is the only intervention
of any kind that moves both required passages together, and that it has a control on its
complement: dropping the 84 framing-family passages above the answer gold moves 43 (0.365309)
and 94 (0.332391) to 4 and 10, while dropping only the 8 non-framing passages above it moves
them to 40 and 86. Every query rewrite fails, the non-oracle ceiling being 12 (0.418804) and
28 (0.390005); every gold-passage repair fails, the ceiling with both required passages
ablated being 18 (0.412468) and 16 (0.420530); and the two combined still reach only 4
(0.462879) and 9 (0.438683). Eight of the thirteen single factors carry opposite signs across
the two hops, deleting the director clause giving 5 (0.466126) and 261 (0.277560) and
deleting the descriptive referent giving 351 (0.238875) and 47 (0.343038), and the A x B x C
factorial has no interaction at all because capitalization and accent restoration are exactly
inert in all eight cells. The indexing condition is negative for the eighth consecutive unit
at 79 (0.333927) and 155 (0.294327); the D-028 exception does not transfer, because neither
required passage's title is the query's name anchor.

The validated secondaries are `peripheral_passage_content_dilution`,
`description_only_bridge_entity` and `generic_person_semantic_neighborhood`. The
content-dilution gate is applied for the fourth time and passes for the third, on both
required passages, which had happened only in D-026: on the answer passage the ablation to
its query-relevant sentence gives 37 (0.373376) at 57 words and a truncation to director and
genre alone gives 16 (0.420530) at 14 words, while the three length-matched name-preserving
controls give 171, 342 and 405 at 10, 16 and 23 words, the first unit in which controls move
the rank the wrong way rather than merely failing to improve it; on the bridge passage
removing a four-word non-relevant parenthetical gives 17 (0.412468) against 37 (0.374462) for
removing four query-relevant words and 58 (0.353484) for the nearest constructible
length-matched control. A boundary is registered rather than closed there: the control the
inclusion rule literally describes cannot be constructed on a passage whose non-relevant
material is a parenthetical rather than a sentence. For the fourth consecutive unit, passing
the gate does not win the primary, because ablating both passages at once still leaves 18 and
16.

The closest competitor is `description_only_bridge_entity`, whose inclusion rule is met since
neither required subject is named and whose single-factor oracle-name test passes in five
forms with the D-024 precondition verified in the D-026 strong form, the bare answer-gold name
ranking its own passage 1 (0.791355) and lifting the other required passage to 2. It loses the
primary for three measured reasons: its entire support is oracle; deleting the director clause
alone puts the un-named bridge passage at 5 (0.466126), inside the cutoff, which is a stronger
form of the D-028 falsification because no repair was needed first; and on the answer side the
phrase `no unique name anchor` misdescribes what was measured, since the query does carry that
passage's name and the passage does contain it, uniquely in the corpus, yet a query consisting
of exactly that name ranks it 2202. `cross_passage_conjunction_unresolved` is not adopted
because its first exclusion fires directly, the answer gold stating the director, the genre and
the starring actress in one passage and so supplying a complete answer alone, and because the
removal probes supply no intermediate fact yet place both required passages inside the cutoff.
`cutoff_sensitive_near_miss` is withheld on the score gap, both figures falling inside the
excluded band, and for the first time with no counter-evidence at all, since ninety-three
removals are needed before both enter the cutoff. `proper_name_homonym_collision` and
`related_name_document_crowding` are excluded on materiality: exactly one non-gold passage
shares the surname and dropping it moves each required passage by one position, to 42 and 93.
`compound_two_sided_crowding` is excluded because one family suppresses both hops, the pit 19h
test. `surface_form_tokenization_mismatch` is excluded because the query's lower-case
unaccented spelling is a measured bit-identical no-op. `possible_type_mismatch` is excluded
because the four-word query `supernatural psychological horror film` ranks the answer gold 12
(0.414189). The two provisional secondaries `surname_entity_confusion` and
`broad_film_person_neighborhood` are deleted rather than registered, the first on the
materiality measurement above and the second because the adopted primary and
`generic_person_semantic_neighborhood` already cover both halves of what it names; that is the
reason D-025 used for `generic_context_substitution`, D-026 for `adjacent_event_crowding`,
D-027 for `related_document_crowding` and D-028 for `bridge_relation_underweighted`.

This unit continues the pooling series along the new-competitor path. Pooled gives `any@5` 0
and `full@5` 0 while per-question gives `any@5` 1 and `full@5` 1, with the two golds at 3 and
5 of 10, so it is the seventh unit in which the corpus setting changes a metric, the second in
which `full@5` also flips after D-026, and the second in which the failure is confined
entirely to the pooled setting. The per-question rebuild reproduces the official ten-title
window in order, verifying the D-025 Dense property for the fourth time. Forty of the 42
passages above the bridge gold and 89 of the 92 above the answer gold are pooling-introduced,
and removing exactly those gives 3 and 5. The D-024 idf-scale path cannot exist on a
bi-encoder and the D-027 annotator-constructed path is weak here, only 2 of this item's own 8
distractors ranking above the bridge gold. Corpus setting remains provenance under D-003 and
pit 17.

### Inventory effect

- The primary inventory grows from 25 to **26 distinct names** with
  `question_frame_semantic_crowding`. This is the first growth by promotion rather than by
  coinage: the name is not new, only new to this inventory, having been a registered secondary
  since D-020. Four names already sit in both inventories,
  `cross_passage_conjunction_unresolved`, `description_only_bridge_entity`,
  `generic_term_lexical_crowding` and `proper_name_homonym_collision`, but all four arrived
  there from the first pass. The departing name `cross_entity_relation_unresolved` is item 3
  and **keeps no current v2 primary row**, the treatment D-021, D-022, D-023, D-027 and D-028
  gave their departing names; it stays in the inventory union as a first-pass name in
  `case_memos_v1.csv` and remains a first-pass secondary on `5abcc96c5542996583600492|bm25`,
  queue item 20, which is still `not_started`.
- The secondary-name union is unchanged at **50 distinct names**;
  `broad_film_person_neighborhood`, item 7, and `surname_entity_confusion`, item 43, remain in
  the union as historical first-pass names, the treatment given to
  `generic_context_substitution`, `adjacent_event_crowding` and `related_document_crowding`.
- `case_memos_v2.csv` now holds **79 secondary assignments over 37 distinct names**, up from
  78 and down from 39: this row went from two descriptors to three, all three of which already
  occur elsewhere in the column, while both removed names were unique to this row. The
  distinct `primary_open_code` count in v2 is unchanged at **16**, because
  `cross_entity_relation_unresolved` was unique to this row as a primary and
  `question_frame_semantic_crowding` was not previously present as one. `case_memos_v1.csv` is
  unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**, because no new descriptor is
  registered. Three existing entries gain this affected unit and D-029 as a decision source,
  `peripheral_passage_content_dilution`, `description_only_bridge_entity` and
  `generic_person_semantic_neighborhood`; `question_frame_semantic_crowding` gains D-029 as a
  decision source and a note on primary use rather than a secondary affected unit, following
  the convention used for `cross_passage_conjunction_unresolved` and
  `description_only_bridge_entity`; and three gain D-029 as a decision source recording a
  non-adoption rather than an affected unit, `cutoff_sensitive_near_miss`,
  `cross_passage_conjunction_unresolved` and `related_name_document_crowding`. In every case no
  definition, inclusion rule or exclusion rule is changed.
- `review_status` counts are now 20 `jointly_reviewed` and 10 `needs_joint_review`. Twenty
  rows now carry a populated `candidate_category`.
- Three vocabulary-audit items are registered by this decision and settled by none of it:
  whether `question_frame_semantic_crowding` needs a primary-use contract of its own now that
  it has a primary use; whether a scoped subset of a crowding primary's family may also be
  carried as a secondary, which is the nesting `generic_person_semantic_neighborhood` creates
  here and the converse of the gap D-023 recorded; and whether the third inclusion condition of
  `peripheral_passage_content_dilution` should be reworded to cover passages whose
  non-query-relevant material is not a whole sentence.
## Section 7A.14 - Validate `5a83880e554299123d8c214e|bm25`

D-030 replaces the primary `query_facet_fragmentation` with
`minimal_preprocessing_score_distortion`. Reconstruction over the same 4,937-passage pooled
corpus reproduces all 50 stored top-50 titles in order with a maximum absolute score error of
exactly 0.000000, and every per-token decomposition reconciles against `get_scores` within
3.553e-15, so strong causal claims are supported. Complete-corpus ranks are 66 / 12.585642 for
the answer hop, Ghost Rider (Suicide song), and 61 / 12.713062 for the bridge hop, Suicide
(1977 album), so the stored `not_in_top50` status means rank 66 and rank 61 of 4,937 rather
than corpus absence. The rank-5 score is 18.467254, so the two required passages sit 5.881611
and 5.754192 points, or 31.849 and 31.159 percent, below the cutoff, with no score cliff.

The question names exactly one entity and names it in the possessive form. Under the verified
tokenizer `suicide's` occurs in 0 of 4,937 passages and contributes exactly 0.000000
everywhere, while the corpus form `suicide` occurs in 12 passages at an idf of 5.976452 and
stands in the indexed body of both required passages. Both that fact and the same fact about
the query's final token `character?` are verified in their strongest available form: deleting
either token reproduces the entire ranking bit for bit, 0 order mismatches and a maximum
absolute score difference of 0.000000. This is the fourth unit after D-019, D-021 and D-028 in
which a query token contributes exactly 0.000000 everywhere and the first in which that token
is the question's only entity name. The same unnormalized clitic also makes the interrogative
frame's head noun `brand's` the query's highest-idf token at 7.587919, worth 7.815653 points or
36.190 percent of the rank-1 passage's score and 0.000000 to both required passages, so one
missing normalization produces a false negative on the only name and a false positive on the
frame at once.

147 distinct conditions were run on the same unchanged candidate set: all 64 cells of a
P x E x G x M x S x T factorial, where G is a possessive-clitic normalization this unit
introduces; ten single-sided controls; three token-level decompositions of the query-side
possessive factor; six case-specific query-side conditions; ten non-oracle query rewrites;
sixteen reduced-query probes; thirteen single query-token deletions; eight oracle conditions;
eight per-side reachability probes; seven gold-targeted index-side repairs including a null
control; sixteen index-side removal probes including two complement controls and a seven-step
cumulative ladder; five further normalization completeness cells including a general
alphanumeric analyzer; and two corpus-setting reconstructions.

A single non-oracle change to one query token recovers both hops: rewriting only `suicide's` as
`suicide` gives 2 / 21.521304 and 5 / 19.568085, with increments of 8.935662 and 6.855023 that
are exactly the scores the two passages receive from a query consisting of that single token,
under which they rank 1 / 8.935662 and 3 / 6.855023. Normalizing both possessives blind gives 1 and 4, a general
alphanumeric analyzer gives 1 / 29.700487 and 4 / 21.348446, and the document-side half alone
gives 70 and 66, worse than the baseline, which makes this the mirror image of D-028's
document-side-only P and requires pit 19p to be read as a duty to measure both sides. Eleven
non-oracle conditions place both required passages inside the cutoff and every one contains a
preprocessing factor; none without one does.

Two results carry the tie-break against the closest competitor. First, no index-side removal of
any composition recovers both hops: dropping all 64 non-gold passages above the answer hop
still leaves 8 / 13.038940 and 2 / 13.262049, the family-scoped probe gives 14 and 7 and its
complement control gives 62 and 54, and the cumulative ladder is monotone and insufficient
throughout. The binding constraint is the answer hop's own 12.585642 rather than which
documents sit above it. Second, the observed family is produced by the question's generic
category vocabulary rather than by its referent cue, forward 2 of 10 and reverse 4 of 10 and
10 of 10 under pit 19f and 19i, so the third exclusion clause of `generic_term_lexical_crowding`
does not fire and the descriptor is demoted by its deferral clause instead; the crowding is
downstream of the primary because that vocabulary is the golds' only scoring surface precisely
because the name anchor contributes 0.000000.

The one battery oracle condition that recovers both hops is degenerate. Appending the gold-2
title gives 2 / 21.521304 and 5 / 19.568085, but of its three appended tokens `(1977` is absent
from the vocabulary and `album)` has term frequency 0 in both required passages, so appending
the single token `Suicide` reproduces both gold scores to 0.000000 and the non-oracle repair
reproduces them to 3.553e-15. This is the first unit in which the D-020 single-factor
oracle-name test can pass without supplying oracle information, and it is registered as a
vocabulary-audit item beside the D-024 precondition.

The validated secondaries are `surface_form_tokenization_mismatch` and
`generic_term_lexical_crowding`. `cross_passage_conjunction_unresolved` is not adopted: two of
its three positive legs hold, matched token sets sharing only `on` and ten of twenty-six single
factors carrying opposite signs, but there is no missing intermediate fact because the question
names the band and both required passages contain that name, and pit 19s applies regardless in
a stronger form than D-028 since one factor suffices where D-028 needed two.
`description_only_bridge_entity` and `unindexed_title_name_anchor` are each excluded by their
own first exclusion clause and both readings of the title name were tested as D-023 requires,
the indexing reading at 78 and 61 and the semantic reading at 1 / 8.935662 and 4 / 6.855023.
`generic_query_scaffold_score_inflation` meets its inclusion rule in full and is still withheld,
on the exclusion's final clause and on the D-018 materiality standard, deleting the whole
interrogative frame moving the required passages only to 64 and 59.
`cutoff_sensitive_near_miss` is withheld on the score gap. `entity_alias_reference_mismatch`,
`proper_name_homonym_collision`, `same_topic_passage_distractor`,
`repeated_content_word_amplification`, `repeated_function_word_amplification`,
`gold_chain_substitutability`, `gold_chain_not_unique`, `plausible_non_gold_answer` and
`peripheral_passage_content_dilution` are each excluded by their own rules or are structurally
inapplicable. The provisional secondary `both_gold_chain_passages_missing` is deleted rather
than registered because it states gold missingness, a forbidden causal category under D-003 and
pit 17, and `query_facet_fragmentation` is deliberately not registered, following D-012, which
reached the same fork on the same name and recorded it as the closest observable ranking
pattern.

This unit is the eighth in which the corpus setting changes a metric and the sixth of the
`any@5`-only kind: pooled gives `any@5` 0 and `full@5` 0 while per-question gives `any@5` 1 and
`full@5` 0, the two required passages ranking 6 and 1 of 10. All three known paths are present
and each is measured insufficient, which is new. 57 of the 64 passages above the answer hop and
53 of the 60 above the bridge hop are pooling-introduced, yet dropping exactly those gives 15
and 9 while the complement control dropping this question's own 7 gives 59 and 54. The
per-question rebuild reproduces the official window and its ranks 6 and 1 exactly, while
scoring the same ten documents with pooled statistics gives 9 and 8, which isolates the D-024
idf-scale path for the second time after D-028 and confirms pit 19r. Corpus setting remains
provenance under D-003.

### Inventory effect

- The primary inventory is unchanged at **26 distinct names**.
  `minimal_preprocessing_score_distortion` is item 9, was already in the inventory, and this is
  its seventh unit after D-012, D-014, D-016, D-019, D-021 and D-028. The departing name
  `query_facet_fragmentation` is item 18 and **keeps no current `case_memos_v2.csv` primary
  row**, the treatment D-021, D-022, D-023, D-027, D-028 and D-029 gave their departing names;
  it stays in the inventory union as a first-pass name in `case_memos_v1.csv`, where it is the
  first-pass primary of `5a7d61775542991319bc93b9|bm25`.
- The secondary-name union is unchanged at **50 distinct names**;
  `both_gold_chain_passages_missing`, item 4, remains in the union as a historical first-pass
  name and now has **no current v2 row**, the treatment given to `generic_context_substitution`,
  `adjacent_event_crowding`, `related_document_crowding`, `broad_film_person_neighborhood` and
  `surname_entity_confusion`.
- `case_memos_v2.csv` now holds **80 secondary assignments over 36 distinct names**, up from 79
  and down from 37: this row went from one descriptor to two, both of which already occur
  elsewhere in the column, while the removed name was unique to this row. The distinct
  `primary_open_code` count in v2 falls from 16 to **15**, because `query_facet_fragmentation`
  was unique to this row as a primary and `minimal_preprocessing_score_distortion` was already
  present. `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**, because no new descriptor is
  registered. Two existing entries gain this affected unit and D-030 as a decision source,
  `surface_form_tokenization_mismatch`, which reaches eight affected units and gains the
  possessive clitic as a worked illustration, and `generic_term_lexical_crowding`, which reaches
  six; and four gain D-030 as a decision source recording a non-adoption rather than an affected
  unit, `cutoff_sensitive_near_miss`, `generic_query_scaffold_score_inflation`,
  `description_only_bridge_entity` and `unindexed_title_name_anchor`. In every case no
  definition, inclusion rule or exclusion rule is changed.
- `review_status` counts are now 21 `jointly_reviewed` and 9 `needs_joint_review`. Twenty-one
  rows now carry a populated `candidate_category`.
- Validation progress after D-030 is **17 of 26 validated, 9 remaining**, superseding the
  16-of-26 figure recorded in section 7A.13.
- Three vocabulary-audit items are registered by this decision and settled by none of it:
  whether the D-020 single-factor oracle-name test needs an explicit precondition that the
  injected string contribute something the question does not already contain, this being the
  first unit in which it passes degenerately; whether
  `minimal_preprocessing_score_distortion`, now on seven units and six distinct sub-mechanisms,
  should be narrowed rather than widened further; and whether the boundary D-029 registered
  against `description_only_bridge_entity`, between an anchor that is absent and one that is
  present but unusable, is settled by this unit's assignment of a present-but-unusable anchor to
  `surface_form_tokenization_mismatch`.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.15 - Validate `5ab48c325542996a3a969f93|dense`

D-031 replaces the primary `bridge_relation_underweighted` with
`cross_passage_conjunction_unresolved`, the fourth primary use of that name and its second on a
Dense unit. Re-encoding the same 4,937-passage pooled corpus reproduces all 50 stored top-50
titles in order, 0 of 50 mismatched, with a maximum absolute score error of 3.278e-07, so strong
causal claims are supported. Complete-corpus ranks are 18 / 0.342168 for the bridge hop,
Edith Walks, which states that the queried king is buried at Waltham Abbey, and 21 / 0.339314 for
the answer hop, Waltham Abbey Church, which places that town in Essex. The rank-5 score is
0.488627, so the two required passages sit 0.146459 and 0.149314 points, or 29.974 and 30.558
percent, below the cutoff, with a real cliff of 0.069056 between rank 7 and rank 8 and both
required passages below it. Both sit inside the 256-token sequence limit at 87 and 144 model
tokens, so truncation is excluded.

The question names the king and asks for a county but never states where he is buried. That
intermediate fact exists in exactly 2 of 4,937 passages, which are the two required ones; no
corpus passage contains both `Essex` and `Harold Godwinson`; the answer passage never names the
king; and neither required passage contains the word `county`, which itself occurs in 248
passages. All three inclusion conditions of the adopted primary hold on read text and against
the verified implementation, and all four exclusion clauses fail to fire.

107 distinct conditions were run on the same unchanged candidate set, plus 10 deliberate repeats
under a second label which reproduced their originals bit for bit: an indexing condition T; 40
non-oracle query rewrites made of 16 reduced queries, 9 single deletions, 12 wording variants and
a 5-step name-free ceiling search; 12 per-side reachability probes; 9 oracle conditions; 14
index-side removal probes including a mutual complement pair and a 10-step cumulative ladder; 28
gold-targeted index-side conditions including 2 null controls, 3 single-fact controls, 10
ablations and 11 length-matched controls; and 2 combined conditions.

Three results carry the primary. Per-side reachability holds at rank 1 on both sides while each
name demotes the other by two to three orders of magnitude, a query reduced to the bridge title
giving 1 / 0.759333 and 1386 / 0.067247 and one reduced to the answer title giving 98 / 0.248832
and 1 / 0.774335, which is the D-025 antagonism sign and the opposite of D-026. Every single
anchor recovers exactly one side across six surface forms and only injecting both names recovers
both, at 3 / 0.557395 and 1 / 0.588495 and at 1 / 0.644947 and 2 / 0.640705. And the non-oracle
direction is exhausted, its Pareto front reaching 10 / 0.371487 with the other hop at
25 / 0.338254 on one side and 3 / 0.545094 with the other hop at 27 / 0.347204 on the other, the
five name-free ceiling rewrites recovering the answer hop every time and the bridge hop never, so
the pit 19s route that falsified this name in D-028 is unavailable. One observation is new for
this name: what the answer hop lacks is the intermediate entity's category rather than its name,
since adding the single generic word `abbey` moves it from 21 / 0.339314 to 4 / 0.504249 while
the other required passage does not move at all.

The weakest leg is recorded rather than suppressed. Only 8 of the 22 single-factor conditions
carry opposite signs across the hops, against 10 of 19 in D-024 and 10 of 20 in D-025, and close
to the 4 of 19 that D-026 cited as one of three grounds for rejecting this same name. The
decision rests on the reachability and exhaustion legs instead, and whether the opposite-sign leg
belongs to the inclusion contract is registered below as a vocabulary-audit item.

This unit introduces the single-fact control, an index-side condition that deletes exactly the
fact the question needs and leaves every other word verbatim, run against two null controls that
reproduce the baseline. Deleting the burial clause from the bridge passage costs 31 rank
positions, 18 / 0.342168 to 49 / 0.291785; deleting the county name from the answer passage costs
2 positions and 0.003037 points, 21 / 0.339314 to 23 / 0.336277. The answer passage's rank is
therefore very nearly independent of whether it states the answer.

The validated secondaries are `description_only_bridge_entity`, which is also the closest
competitor, and `related_name_document_crowding`. All three provisional names are deleted rather
than registered. `bridge_relation_underweighted` is deleted for the second time after D-028, and
again on measurement: it is a token-level weighting claim that pit 18 forbids on a bi-encoder
without attribution, tripling the relation word gives 21 / 0.326115 and 24 / 0.320425 which is
worse than the baseline, six relation paraphrases never recover both hops, and the relation word
alone ranks the two passages 241 and 596. D-031 records one difference from D-028, where the
relation tokens were completely inert: here the relation is not inert, since deleting `buried`
worsens both hops to 21 / 0.333201 and 47 / 0.293346, the burial clause is worth 31 rank
positions in the passage's own text, and `is buried` occurs in exactly 1 corpus passage, the
bridge hop itself. The mechanism is real and the proposed name is still unmeasurable, which is
the ground for deletion. `subject_associate_crowding` duplicates the registered
`related_name_document_crowding` and `location_chain_incomplete` either restates gold missingness,
forbidden under D-003 and pit 17, or restates the adopted primary.

`peripheral_passage_content_dilution` is applied for the fifth time and rejected for the second,
and for the first time its two control forms disagree. The answer passage fails the second
inclusion condition outright, its query-relevant sentence alone giving 26 / 0.318641 against a
baseline of 21. On the bridge passage the literal D-023 control gives 2908 / -0.012338 and would
pass the gate, while the D-027 name-preserving controls give 1 / 0.649612 and 1 / 0.725954,
exactly the rank the ablations reach, so the effect is the query-relevant fraction of the passage
rather than which sentences remain. `question_frame_semantic_crowding` is not adopted because its
include rule's controlled condition fails, deleting the name leaving 2 of 10 and every frame-only
probe 0 of 10. `generic_person_semantic_neighborhood` is not adopted because the person pages all
name the queried entity explicitly. `unindexed_title_name_anchor` does not apply and its indexing
condition is inert-to-negative at 27 / 0.314097 and 24 / 0.323271, the ninth measurement of that
condition in this project and the eighth inert-or-negative result. `cutoff_sensitive_near_miss`
is withheld on the score gap. `gold_chain_substitutability` and `plausible_non_gold_answer` are
excluded because neither hop has a substitute anywhere in the corpus.

Two index-side facts bound the crowding readings. Dropping all 8 Harold-associate passages gives
10 / 0.342168 and 13 / 0.339314 and dropping their 11-passage complement gives 9 / 0.342168 and
10 / 0.339314, so neither family is outcome-determinative and 17 of the 19 must be dropped before
both required passages enter the cutoff. The condition that drops every non-gold passage above
the answer hop reaches 1 and 2, but on a bi-encoder that cell is a tautology rather than
evidence, since a cosine score carries no collection statistic and the two scores are
bit-identical to the baseline; pit 19u, established by D-030 on a lexical backend where removals
change `idf` and `avgdl`, is therefore a lexical-backend test, and its informative Dense form is
the family-scoped probe with a complement control.

Corpus setting is provenance under D-003 and pit 17. Pooled and per-question agree on both
metrics at `any@5` 0 and `full@5` 0, which happened before only in D-021 and D-027, and this is
the most extreme instance recorded: the two required passages rank 9 and 10 of the 10 paragraphs
HotpotQA supplies for this question, the bottom two. Of the three known paths only the
annotator-supplied one is present, this question's own 8 distractors occupying pooled ranks 1 to 7
and 9 and filling the whole cutoff region; dropping the 11 pooling-introduced passages above the
answer hop gives exactly the per-question result and no recovery, and the idf-scale path cannot
arise on a bi-encoder. Keeping only this question's own 10 paragraphs reproduces the official
per-question window item by item, 10 of 10 in order, which verifies the D-025 Dense restriction
property for the fifth time and in its strongest form. Complete-corpus BM25 ranks the two
passages 7 / 24.495360 and 901 / 10.499181 and its per-question ranks are 2 and 7; this is
reachability evidence only.

### Inventory effect

- The primary inventory is unchanged at **26 distinct names**.
  `cross_passage_conjunction_unresolved` is item 4, was already in the inventory, and this is its
  fourth validated primary use after D-022, D-024 and D-025. The departing name
  `bridge_relation_underweighted` is item 1 and now keeps **no current `case_memos_v2.csv`
  primary row**, the treatment D-021, D-022, D-023, D-027, D-028, D-029 and D-030 gave their
  departing names, but unlike every one of those it **keeps a current v2 secondary row**, being
  the provisional secondary of `5add67915542992200553af8|dense`, queue item 22, which is still
  `not_started`. It therefore leaves the current v2 primary column while remaining in the current
  v2 secondary column, a shape this audit has not previously recorded.
- The secondary-name union is unchanged at **50 distinct names**; `location_chain_incomplete`,
  item 24, and `subject_associate_crowding`, item 40, remain in the union as historical
  first-pass names and now have **no current v2 row**, the treatment given to
  `generic_context_substitution`, `adjacent_event_crowding`, `related_document_crowding`,
  `broad_film_person_neighborhood`, `surname_entity_confusion` and
  `both_gold_chain_passages_missing`.
- `case_memos_v2.csv` still holds **80 secondary assignments**, now over **34 distinct names**,
  down from 36: this row went from two descriptors to two, both removed names were unique to it,
  and both adopted names already occur elsewhere in the column. The distinct `primary_open_code`
  count in v2 falls from 15 to **14**, because `bridge_relation_underweighted` was unique to this
  row as a primary and `cross_passage_conjunction_unresolved` was already present.
  `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**, because no new descriptor is
  registered; this is the third consecutive decision to register none, after D-029 and D-030. Two
  existing entries gain this affected unit and D-031 as a decision source,
  `description_only_bridge_entity`, which reaches eight secondary affected units, and
  `related_name_document_crowding`, which reaches three; four gain D-031 as a decision source
  recording a non-adoption rather than an affected unit,
  `peripheral_passage_content_dilution`, `question_frame_semantic_crowding`,
  `cutoff_sensitive_near_miss` and `generic_person_semantic_neighborhood`; and
  `cross_passage_conjunction_unresolved` gains an extension to its existing primary-use note. In
  every case no definition, inclusion rule or exclusion rule is changed.
- `review_status` counts are now 22 `jointly_reviewed` and 8 `needs_joint_review`. Twenty-two
  rows now carry a populated `candidate_category`.
- Validation progress after D-031 is **18 of 26 validated, 8 remaining**, superseding the
  17-of-26 figure recorded in section 7A.14.
- Three vocabulary-audit items are registered by this decision and settled by none of it:
  whether the opposite-sign leg is part of the inclusion contract of
  `cross_passage_conjunction_unresolved`, given that it is met only 8 of 22 times on an adopted
  use here while D-026 cited 4 of 19 as a ground for rejection; whether the third inclusion
  condition of `peripheral_passage_content_dilution` can be reworded so that its literal form and
  the D-027 name-preserving form cannot disagree, as they do here; and whether the vocabulary
  needs anything to carry a required passage whose query-relevant material is a small fraction of
  its text but which fails that gate on the brevity direction, which is the converse of the gap
  D-023 recorded, where half of a competing neighborhood received no descriptor.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.16 - Validate `5ab8f57b5542991b5579f097|bm25`

D-032 retains the provisional primary `one_sided_entity_crowding`, which is its second validated
primary use and its first on a lexical retriever. This is the second comparison unit in the pass,
after `5a78b209554299148911f93e|dense`, and the first comparison unit on BM25. Rebuilding the index
over the same 4,937-passage pooled corpus reproduces all 50 stored top-50 titles in order, 0 of 50
mismatched, with a maximum absolute score error of 0.000000, and every per-token decomposition
reconciles against `get_scores` within 7.105e-15, so strong causal claims are supported.
Complete-corpus ranks are 6 / 26.870093 for Joseph McGrath (film director), which supplies the
Scottish nationality, and 11 / 19.741610 for Thomas H. Ince, which supplies the American one. The
rank-5 score is 28.423217, so the two required passages sit 1.553124 and 8.681607 points, or 5.464
and 30.544 percent, below the cutoff, with no cliff between the cutoff region and the nearer one.

151 distinct conditions were run on the same unchanged candidate set, plus 14 deliberate repeats
under a second label which reproduced their originals bit for bit. This is the largest battery in
the project, after D-030's 147. They are 16 P x E x S x T cells; 22 further preprocessing
conditions splitting P, E and M into query-side and document-side halves and crossing them with S
and T; 8 single-query-token conditions including the two-sided control that refutes them; 8 wording
cells and the same 8 with the scaffold removed; 11 single query-token deletions; 16 reduced-query
probes; 12 per-side reachability probes; 3 query-splitting pairs at three budgets each; 8
neighbourhood-overlap probes in both directions; 22 index-side removal probes including a family
probe, its complement control, 3 sub-family probes, a 9-step ladder, a size-matched null control
and a statistics-matched control; 4 corpus-setting reconstructions; 11 gold-targeted index-side
conditions including a null control and 4 single-fact controls; and 7 oracle conditions.

The mechanism is a query token that scores nothing for either required passage and a great deal for
one candidate's satellites. The Ince passage's indexed body writes Thomas Harper Ince, so the query
token `h.` contributes exactly 0.000000 to it while eight of the nine non-gold passages above it
write Thomas H. Ince verbatim and take 4.461297 to 7.814359 from that one token. Under pit 19x the
whole ranking is compared rather than the two gold ranks: deleting `h.` changes 4896 of 4937 order
positions with a maximum absolute score difference of 8.333161 while both required passages' scores
stay bit-identical. Three reduced queries state it in one line. The question's own name form, which
is also that passage's title, ranks it 6 / 16.787469; the same name without the middle initial ranks
it 2 / 16.787469 at a bit-identical score; the body's own form, an oracle condition, ranks it
1 / 27.005232. A corpus scan explains the asymmetry: the string Thomas H. Ince occurs in 8 non-gold
passages and 0 times in that passage's own body, Thomas Harper Ince occurs in exactly 1 passage
which is itself, and `mcgrath` occurs in exactly 1 of 4,937 passages at the query's highest idf of
8.098947.

The question's only statement of the compared property is inert and so is its repair. `nationality?`
occurs in 0 passages and contributes exactly 0.000000; deleting it leaves the 4,937-passage order
0 of 4937 changed with a maximum absolute score difference of 0.000000. This is the fifth such token
after D-019, D-021, D-028 and D-030, and the first whose repair is also worth nothing: the corpus
form `nationality` occurs in 7 passages but in neither required passage, so normalizing the token
leaves them at 6 / 26.870093 and 11 / 19.741610. In D-030 the corresponding repair was worth 64 rank
positions, so this pair is a boundary sample rather than a repetition.

Three results carry the primary. The competitor family is one-sided and fills the entire cutoff
region: all 5 passages above the nearer required passage and 7 of the 9 above the other are
Ince-side documents read in full, and the other queried candidate has 0 competitors. Family
attribution is falsifiable and passes in four directions: dropping the 7 gives 1 / 26.868145 and
2 / 22.167723, dropping their 2-passage complement gives 6 / 26.911596 and 9 / 19.763251, a
size-matched null control that drops 7 highly ranked passages carrying none of the query's name
tokens gives 6 / 26.861098 and 11 / 19.734995, and a statistics-matched control that drops 7
passages carrying `thomas` or `h.` from below the required evidence gives 6 / 26.905808 and
11 / 19.829852, worth 0.088242 points and 0 rank positions. And only this reading accounts for both
required passages, which is what a comparison unit needs: the McGrath passage has no name-form
problem at all, ranks 1 under five non-oracle single-sided queries, and fails solely because five
Ince-side documents occupy the top five that both candidates must share. The last is the tie-break
D-027 used on the Dense unit of a different example.

Two controls this unit introduces separate effects a lexical removal probe conflates, because on
BM25 a removal changes `idf` and `avgdl` as well as the candidate set. D-027's statement that gold
scores are bit-identical under every removal must not be carried to this backend: the Ince passage's
score rises from 19.741610 to 22.167723 under the family probe as `idf(ince)` increases. The
size-matched and statistics-matched controls above show that neither corpus shrinkage nor idf drift
accounts for the family probe. A third control in the same family, dropping all 31 non-gold passages
carrying the bare token `joseph`, gives 4 / 31.046130 and 10 / 19.764622 and is recorded as an idf
effect rather than a competitor removal, since none of those passages ranks above the passage it
moves. The pit 19u drop-everything cell has discriminative power on this backend and succeeds at
1 / 26.909654 and 2 / 22.191974, the opposite of D-030's lexical result and informative in a way it
is not on the bi-encoder D-031 examined.

The pit 19f and 19i test runs in both directions with the same sign and identifies the mechanism
rather than routing it away, which is the asymmetry D-027 recorded for this same descriptor: the cue
that reproduces the neighbourhood is one of the two named candidates and a comparison question must
contain it, so there is no more specific upstream mechanism to route to. Forward, the referent name
alone places 5 of 10 of its top ten inside the baseline top five, 8 of 10 inside the top ten and
9 of 10 inside the top eleven; in reverse, deleting it leaves 0 of 10, 2 of 10 and 2 of 10. The
interrogative frame alone and `nationality` alone each give 0 of 10 at every depth, and the other
candidate's name gives 0 of 10, 1 of 10 and 1 of 10. Deleting only `h.` still leaves 5 of 10, 7 of 10
and 8 of 10, so the family is not an artefact of the initial.

Query splitting, the comparison-unit repair candidate of pit 19o, was measured in three forms and
never returns both required passages. Keeping the full frame per side gives 9 and 1, the natural
single-sided rewrite gives 13 and 6, bare names give 6 and 1, and at budgets of 2, 3 and 5 per side
the union never contains both, because the Ince passage sits outside the top five of a query
consisting only of its own side, whose top five is five family documents. Pit 19n therefore holds in
a new form: not that a passage fails under its own bare name, as with D-027's Albee side, but that
it fails under the name form the question uses and succeeds under the form without the initial.

The validated secondaries are `related_name_document_crowding`, `cutoff_sensitive_near_miss` for the
nearer required passage only, `unindexed_title_name_anchor`, which is also the closest competitor,
and `generic_query_scaffold_score_inflation`. The closest competitor is decided on three
measurements rather than on inclusion rules, since both candidates meet theirs: the name-anchor
reading is repaired to its limit in three forms and the failure survives all three, reaching 6, 4
and 6 and twice at the other required passage's expense, with only the non-deployable both-golds
title prefix recovering the pair at 2 / 31.546981 and 5 / 30.556598; the crowding reading passes its
two-directional test; and only the crowding reading accounts for the second required passage. D-010's
routing clause, which prefers a more specific implementation-supported name-form mismatch, is tested
on a lexical backend for the first time and does not fire, and unlike D-010's Barrie passage, where
all three query name tokens missed the body, two of the three hit here. The two units have different
unit keys, so reaching a different primary is the unit-key rule working rather than D-010 being
carried across.

Fifteen non-oracle conditions place both required passages inside the cutoff and every one of them
removes or lacks the query scaffold; no single factor does. They form two families, removing or
destroying `h.` with scaffold removal at 2 / 17.888493 and 3 / 16.787469, and indexing titles with
scaffold removal at 4 / 22.885192 and 1 / 27.642683. The apparent preprocessing gains are refuted by
their own two-sided control, a new interaction shape for this project: normalizing `h.` on the query
side alone gives 2 / 26.870093 and 8 / 19.741610 and on the document side alone 2 / 26.870094 and
8 / 19.741610, each recovering both once the scaffold is removed, while normalizing both sides so the
token realigns returns the baseline at 6 / 26.870094 and 11 / 19.741610 and with scaffold removal
gives 6 / 17.888493 and 7 / 16.787469, bit-identical to scaffold removal alone. Both single sides are
positive and the pair is inert, which is neither D-028's wholly document-side shape nor D-030's
wholly query-side one. Accordingly `minimal_preprocessing_score_distortion` is not adopted: the
two-sided P factor is negative on both required passages at 8 / 26.567864 and 16 / 18.889345,
document-side punctuation stripping alone moves the Ince passage the wrong way from 11 / 19.741610 to
13 / 18.889345 by merging `ince.` and `ince,` into `ince` and enlarging the name-sharing family, and
no preprocessing repair of any kind exists in this unit. Crude stemming is strongly negative on the
query side at 212 / 13.171903 by damaging the surname and turns positive only once titles are
indexed, a third source of sign for M after D-028's negative and D-030's positive and unlike either a
proper-noun effect.

Two single-fact controls under pit 19z give the unit's most informative measurement, against a null
control that re-indexes both required bodies verbatim and reproduces the baseline with 0 of 4937
order changes and a maximum absolute score difference of 0.000000. Deleting `American` from the Ince
body moves it from 11 / 19.741610 to 10 / 19.893367 and deleting `Scottish` from the McGrath body
moves it from 6 / 26.870093 to 6 / 27.039416, both marginally better because the passage is shorter,
while deleting the whole name gives 4800 / 3.023334 and 3006 / 9.077577. These passages' ranks are
determined by their name tokens and are very nearly independent of whether they state the answer,
which is the finding D-031 recorded for one county name and which holds here for both required
passages at once.

The oracle direction is degenerate as pit 25f predicts and was checked token by token under pit 24b.
Appending the Ince title injects `thomas`, `h.` and `ince`, all of which the question already
contains, so the condition is pure token repetition and it demotes the other required passage, at
11 / 26.870093 and 7 / 36.529080; appending the McGrath title injects `(film` with term frequency 0
in both required passages and `director)` which is out of vocabulary, at 1 / 44.758586 and
27 / 19.741610. Six of the seven oracle conditions fail and only verbatim injection of both bodies'
identifying clauses recovers both, at 2 / 69.032806 and 3 / 65.413184, so the D-020 single-factor
oracle-name test is again unavailable in the form D-017, D-023 and D-026 used and the decision rests
on the reduction side instead. The wording direction is also exhausted and inert, all 8 cells and all
8 with the scaffold removed leaving the pair outside the cutoff.

The remaining descriptors are excluded on measurement. `surface_form_tokenization_mismatch` fails
materiality as above, and the unit's real name-form difference, `h.` against `Harper`, lies outside
its definition, being an initial against an expanded middle name.
`entity_alias_reference_mismatch` is excluded by its own third exclusion, the two forms already
sharing the scored tokens `thomas` and `ince`. `generic_term_lexical_crowding` fails its inclusion
rule outright, the competitors matching proper nouns rather than category vocabulary and both
generic probes giving 0 of 10. `proper_name_homonym_collision` meets its inclusion rule on
Joe Scarborough 9 / 20.188689 and Thomas H. Gale House 10 / 19.869995 but fails materiality, dropping
both moving the required passage only from 11 / 19.741610 to 9 / 19.763251.
`compound_two_sided_crowding` is excluded under pit 19h, one family suppressing both required
passages and the other side having none. `cross_passage_conjunction_unresolved` is excluded at the
contract level as in D-027, a comparison question's two nationalities being independent.
`same_artist_work_crowding` meets its inclusion rule on three films at 3, 5 and 7 but its definition
is anchored on works outranking a gold work while the required passage is the creator's biography,
the boundary D-027 recorded, and dropping only those three gives 4 / 26.869075 and 6 / 20.377303.
`peripheral_passage_content_dilution` is inapplicable, its definition being scoped to a whole-passage
mean-pooled encoder, so its gate was deliberately not applied and no length-matched control was run.
`plausible_non_gold_answer`, `gold_chain_not_unique` and `gold_chain_substitutability` are excluded
on the substring scan: no passage contains both `ince` and `mcgrath`, `mcgrath` and
`thomas harper ince` each occur in exactly 1 passage which is the required one, and the five passages
that name Ince and contain `american` use that word of a brother, the wife or a film in every case,
so under pit 19b all nine passages above the required evidence are true distractors.

Corpus setting is provenance under D-003 and pit 17, and the two settings disagree on `any@5`.
Pooled gives `any@5` 0 and `full@5` 0 at 6 and 11 and the official per-question setting gives
`any@5` 1 and `full@5` 0 at 1 and 10, the rebuilt per-question index reproducing the stored CSV order
title by title. This is the ninth `any@5` divergence in the series, D-030 being the eighth, and the
third unit after D-028 and D-030 to present more than one path at once. New competitors is measured and fails: all 5 passages above
the nearer required passage come from the item's own window and 0 are pooling-introduced, 7 of the 9
above the other come from the window, and dropping the 2 pooling-introduced passages gives
6 / 26.911596 and 9 / 19.763251. The idf-scale path carries the whole flip and is cleanly isolated as
in D-028: the pooled scores themselves restricted to those 10 paragraphs give 6 / 26.870093 and
9 / 19.741610, the same 10 documents with pooled idf and pooled `avgdl` substituted reproduce that
title by title, and with pooled idf but per-question `avgdl` kept both required passages hold their
positions at 6 / 23.173455 and 9 / 17.855162 and only one adjacent non-gold pair swaps, so `avgdl`
carries none of the flip, the same division D-028 recorded. In the ten-document index `ince` has
document frequency 6 of 10, `thomas` 9, `h.` 8 and `and`, `of` and `the` 9 each, and all six are
floored to the identical 0.390062 by `epsilon`, while `mcgrath` and `joseph` have document frequency
1 and idf 1.845827 and `were` and `same` have document frequency 0; `avgdl` falls from 90.884950 to
53.700000 and `average_idf` from 7.669260 to 1.560249. The small index destroys exactly the tokens
that drive the crowding and preserves exactly the other side's two, which is why the McGrath passage
ranks 1 there while the Ince passage, whose entire score rests on the floored tokens, ranks 10 of 10
and so fails independently of pooling. This is the second measured instance of the setting-dependent
gold swap recorded in the corpus-setting subsection of
`references/bm25_implementation_reference.md`, with a different fingerprint: there one token hit
document frequency 5 of 10 and took an idf of exactly 0, here six distinct tokens are floored to one
identical value. The annotator-supplied path is present in its maximal form, all 8 of this question's
own HotpotQA distractors being Ince-side against 6 of 8 in D-027. Dense places the two passages at
1 and 4, both inside the stored window of 50, so these are exact complete-corpus ranks; the Dense
results CSV carries no scores and none is quoted. This is reachability evidence only.

### Inventory effect

- The primary inventory is unchanged at **26 distinct names**. `one_sided_entity_crowding` is
  item 13, was already in the inventory, and this is its **second validated primary use and its
  first on a lexical retriever**. The provenance sentence D-027 recorded, that the name also
  survived as the first-pass primary of this row while it was still `not_started`, is now
  discharged. No name departs, so nothing needs the treatment D-021 through D-031 gave their
  departing names, and this is the first decision in the pass to retain a provisional primary
  unchanged while the secondary set grows.
- The secondary-name union is unchanged at **50 distinct names**; both added names already occur in
  the column and none departs.
- `case_memos_v2.csv` now holds **82 secondary assignments over 34 distinct names**, up from 80 and
  unchanged from 34: this row went from two descriptors to four and both additions already occur
  elsewhere in the column. The distinct `primary_open_code` count in v2 is unchanged at **14**,
  because the primary is retained. `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**, because no new descriptor is registered;
  this is the fourth consecutive decision to register none, after D-029, D-030 and D-031. Four
  existing entries gain this affected unit and D-032 as a decision source:
  `related_name_document_crowding`, which reaches four affected units and its first lexical use;
  `cutoff_sensitive_near_miss`, which reaches six; `unindexed_title_name_anchor`, which reaches
  two; and `generic_query_scaffold_score_inflation`, which reaches three. Three gain D-032 as a
  decision source recording a non-adoption rather than an affected unit,
  `surface_form_tokenization_mismatch`, `proper_name_homonym_collision` and
  `generic_term_lexical_crowding`. In every case no definition, inclusion rule or exclusion rule is
  changed.
- `review_status` counts are now 23 `jointly_reviewed` and 7 `needs_joint_review`. Twenty-three rows
  now carry a populated `candidate_category`.
- Validation progress after D-032 is **19 of 26 validated, 7 remaining**, superseding the 18-of-26
  figure recorded in section 7A.15.
- Four vocabulary-audit items are registered by this decision and settled by none of it: whether
  crowding-family names need an explicit primary-use contract, now that `one_sided_entity_crowding`
  has a validated primary use on each backend and D-010 described it as the resulting ranking
  pattern; whether `unindexed_title_name_anchor` should require its semantic reading to reach the
  cutoff, given two affected units whose readings disagree at 1 and at 6 / 16.787469; whether
  co-necessity is a sufficient ground for a secondary, given that D-030 refused
  `generic_query_scaffold_score_inflation` on solo materiality while this decision accepts it on
  co-necessity, the two units being the boundary samples the audit needs; and whether the
  operational meaning of `explains the primary failure` in
  `related_name_document_crowding`'s first exclusion should be written as the test used here, a
  gold-targeted repair of the name form that still leaves the passage outside the cutoff.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.17 - Validate `5abcc96c5542996583600492|bm25`

D-033 replaces the provisional primary `partial_match_constraint_omission` with
`minimal_preprocessing_score_distortion`, which is that name's eighth unit and the fifth
consecutive decision to register no new descriptor. Rebuilding the index over the same
4,937-passage pooled corpus reproduces all 50 stored top-50 titles in order, 0 of 50 mismatched,
with a maximum absolute score error of 0.000000, and every per-token decomposition reconciles
against `get_scores` within 3.553e-15, so strong causal claims are supported. Complete-corpus
ranks are 26 / 28.798100 for Earl and Edgar McGraw, which supplies the link from the queried
character's daughter to the answer film, and 115 / 26.074919 for Planet Terror, which supplies
the actress; pit 7 applies, the stored window recording the second as `not_in_top50` while it is
in the corpus at 115 of 4,937. The rank-5 score is 31.796696, so the two required passages sit
2.998596 and 5.721776 points, or 9.431 and 17.995 percent, below the cutoff, the only cliff lying
between ranks 3 and 4 above both of them.

201 distinct labelled conditions were run on the same unchanged candidate set, 16 of them
deliberately repeated under a second label with every repeat reproducing its original bit for bit,
for 218 recorded rows. They are 64 P x E x G x M x S x T cells, G being the possessive-clitic
normalization D-030 introduced; 14 one-sided controls; 8 generic-analyzer conditions; 17 single
query-token deletions judged on the whole ranking; 13 reduced-query probes; 6 per-side
reachability probes; 5 neighbourhood-overlap probes in both directions; 4 corpus-setting
reconstructions with two statistics grafts; 26 index-side removal probes with two ladders, a
complement control, a size-matched null control and a statistics-matched control; 4 single-fact
controls and 4 single-token surface repairs, each with a null control; 6 query-aware normalization
conditions; and 8 oracle conditions. This is the first case built on `tools/probe_kit.py`.

The decision rests on three measurements. The question's two most discriminative tokens,
`McGraw's` and `daughter?`, each occur in 0 of 4,937 passages and contribute exactly 0.000000, and
deleting either leaves the whole 4,937-passage order 0 of 4937 changed at a maximum absolute score
difference of 0.000000. Each repair is priced exactly and is confirmed by an independent
single-token query: the clitic is worth 8.991778 points and 24 rank positions, moving that passage
to 2 / 37.789878 and flipping `any@5` on its own, and the boundary punctuation is worth 3.520270
points and 21 positions, the two being additive at 1 / 41.310149. On the other required passage
the mismatch is on the document side, its indexed body writing `Rose McGowan,`, and stripping that
one comma moves it from 115 / 26.074919 to 5 / 32.133137. No non-oracle condition places both
inside the cutoff, which is the shape D-021 accepted for this primary rather than the shape of
D-028 and D-030.

Two items are recorded as new pits rather than as rule changes. A surface repair's gold-targeted
and deployable forms differ by nine rank positions here, 5 / 32.133137 against 11 / 31.534653 for
the same repair applied corpus-wide and 14 / 31.630834 for a query-aware normalization, because
the fourteen other passages naming the same actress receive the identical repair; both cells must
be run or the gold-targeted figure reads as a deployable gain. And a crowding family can be
non-determinative at baseline and determinative after the primary's repair: at baseline the family
probe gives 15 / 28.805372 and 73 / 26.630444 against its complement's 10 / 29.270483 and
30 / 26.124391, while under full normalization the same family gives 1 / 25.266887 and
3 / 15.335047 against a size-matched null control's 1 / 25.981076 and 12 / 12.825312.

### Inventory effect

- The primary inventory is unchanged at **26 distinct names**.
  `minimal_preprocessing_score_distortion` is item 9 and reaches its eighth unit, which widens a
  primary already flagged as possibly too broad; it adds no seventh sub-mechanism but does add a
  new shape of an existing one, a single class of missing normalization disabling a different
  required passage on each side. The departing name `partial_match_constraint_omission` is item 15
  and keeps a current v2 primary row, queue item 26, so unlike the departing names of D-021,
  D-022, D-023, D-027, D-028 and D-029 it needs no historical-preservation treatment; it is
  refused registration rather than merged, on pit 17, because it names the shape of the ranking
  and is dissolved by the adopted primary.
- The secondary-name union is unchanged at **50 distinct names**; all four adopted secondaries
  already occur in the column, and the two departing ones remain in the union,
  `cross_entity_relation_unresolved` as a first-pass name in `case_memos_v1.csv` after losing its
  last v2 occurrence, which is the treatment D-029 gave it when it lost its last v2 primary row,
  and `answer_entity_missing_both_methods` because it still occurs on another row.
- `case_memos_v2.csv` now holds **84 secondary assignments over 33 distinct names**, up from 82
  and down from 34: this row went from two descriptors to four, all four of which already occur
  elsewhere, while `cross_entity_relation_unresolved` was unique to this row. The distinct
  `primary_open_code` count in v2 is unchanged at **14**, because
  `minimal_preprocessing_score_distortion` was already present and
  `partial_match_constraint_omission` survives on another row. `case_memos_v1.csv` is unchanged at
  39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**, because no new descriptor is
  registered; this is the fifth consecutive decision to register none, after D-029, D-030, D-031
  and D-032. Four existing entries gain this affected unit and D-033 as a decision source:
  `surface_form_tokenization_mismatch`, which reaches nine affected units;
  `related_name_document_crowding`, which reaches five and its second lexical use;
  `generic_term_lexical_crowding`, which reaches seven; and
  `generic_query_scaffold_score_inflation`, which reaches four. Six gain D-033 as a decision
  source recording a non-adoption rather than an affected unit,
  `cross_passage_conjunction_unresolved`, `unindexed_title_name_anchor`,
  `cutoff_sensitive_near_miss`, `description_only_bridge_entity`,
  `repeated_function_word_amplification` and `proper_name_homonym_collision`. In every case no
  definition, inclusion rule or exclusion rule is changed.
- `review_status` counts are now 24 `jointly_reviewed` and 6 `needs_joint_review`. Twenty-four
  rows now carry a populated `candidate_category`.
- Validation progress after D-033 is **20 of 26 validated, 6 remaining**, superseding the
  19-of-26 figure recorded in section 7A.16.
- Three bookkeeping corrections settled on 2026-08-05 land with this decision, all in the
  registry and none of them changing a count that was already right:
  `unindexed_title_name_anchor`'s inert-or-negative list gains `D-029`;
  `peripheral_passage_content_dilution`'s running tallies are replaced by a member enumeration of
  six applications, four passes and two documented rejections, and its `Decision source` line
  gains `D-025`, which applied the gate and rejected without becoming an affected unit; and the
  word `untested` is replaced by `never decided on` throughout `cutoff_sensitive_near_miss`,
  because D-024 measured 5.698 percent inside those bands without deciding on it. The owner's
  ruling named the D-028 and D-032 paragraphs; the two later paragraphs that merely restate
  D-028's band, in D-030 and D-031, are corrected with them so the entry does not remain
  internally inconsistent, and no numeric band in any of the four is altered.
- Four vocabulary-audit items are registered by this decision and settled by none of it: whether
  `cross_passage_conjunction_unresolved`'s first exclusion fires on a passage that supplies the
  answer string while verifying only one of the question's constraints, the bridge passage here
  naming the answer film outright, where D-029's answer passage satisfied all three of its
  question's facets; whether `unindexed_title_name_anchor` should still be refused on the form of
  the anchor alone when its semantic reading is maximal at 1 / 30.558101 and its indexing reading
  positive at 18 / 29.565356; whether the never-decided band, now 5.464 to 9.431 percent after
  this decision narrowed it from above for the first time, should be closed by an explicit
  threshold; and whether `minimal_preprocessing_score_distortion`, now at eight units and six
  sub-mechanisms, should be narrowed, together with the related question of whether an inclusion
  rule such as `related_name_document_crowding`'s should be evaluated at baseline or after the
  adopted primary's repair, the two giving opposite verdicts here.

These remain vocabulary counts, not validated mechanism counts and not prevalence.
## Section 7A.18 - Validate `5adc8977554299438c868de2|bm25`

D-034 replaces the provisional primary `question_wording_ambiguity` with
`minimal_preprocessing_score_distortion`, which is that name's ninth unit and the sixth
consecutive decision to register no new descriptor. Rebuilding the index over the same
4,937-passage pooled corpus reproduces all 50 stored top-50 titles in order, 0 of 50 mismatched,
with a maximum absolute score error of 0.000e+00, and every per-token decomposition reconciles
against `get_scores` within 1.421e-14, so strong causal claims are supported. Complete-corpus
ranks are 7 / 33.382868 for Hlin, which supplies the bridge fact that the goddess associated
with Frigg belongs to Norse mythology, and 72 / 17.155303 for Norse mythology, which supplies
the answer fact; pit 7 applies, the stored window recording the second as `not_in_top50` while
it sits at 72 of 4,937. The rank-5 score is 34.644248, so the two required passages sit 1.261380
and 17.488945 points, or 3.641 and 50.482 percent, below the cutoff, and no cliff separates the
cutoff region from the nearer one.

201 distinct labelled conditions were run on the same unchanged candidate set, 18 of them
deliberately repeated under a second label with every repeat reproducing its original bit for
bit, for 219 recorded rows, of which 3 are `not_run` cells with reasons. The reproduction script
carries 221 assertions and all pass.

The mechanism is one class of missing normalization failing on a different side for each
required passage. The question's final token `tales?` occurs in 0 of 4,937 passages and
contributes exactly 0.000000; deleting it leaves the whole 4,937-passage order 0 of 4937 changed
at a maximum absolute score difference of 0.000000, and normalizing it moves the answer passage
from 72 / 17.155303 to 15 / 24.166533, worth exactly the 7.011230 a single-token query `tales`
gives it. The bridge passage writes the question's only proper noun only as `Frigg.`, twice, so
the query's bare `frigg` contributes 0.000000 to it while four of the six passages above it take
between 4.748132 and 6.795970 from that token; repairing that alone gives 1 / 43.747308 and its
corpus-wide deployable form, touching 2 passages, gives 1 / 43.747301. Two-sided normalization
alone gives 1 / 43.328448 and 18 / 23.247555 and flips `any@5`. Nothing flips `full@5`.

The provisional primary is measured and refuted rather than merely displaced. The A x B x C
wording-repair factorial, run in both preprocessing states for sixteen cells, leaves the bridge
passage at exactly 7 / 33.382868 in all eight baseline cells and at exactly 1 / 43.328448 in all
eight normalized cells, and on the answer passage the grammatically correct repair is the worst
cell at 545 / 12.232081. The double space is provably inert under `lower().split()` and measures
inert. What moves the answer passage is a content addition, adding the generic category word
`mythology` giving 7 / 37.292516 and 8 / 35.734170, which is not deployable under pit 19ab.

### Inventory effect

- The primary inventory is unchanged at **26 distinct names**.
  `minimal_preprocessing_score_distortion` was already in the inventory and is now the primary
  of nine current `case_memos_v2.csv` rows. The departing name `question_wording_ambiguity` is
  item 19 and **loses its last current v2 primary row**, the one D-026 recorded it as keeping,
  so it stays in the union as a historical first-pass name, where it is the primary of 2 rows in
  `case_memos_v1.csv`; that is the treatment D-021 gave `weak_lexical_name_anchor` and D-026 gave
  `adjacent_event_crowding`.
- The secondary-name union is unchanged at **50 distinct names**; D-034 adopts only already
  inventoried names. `competing_valid_entity_cues`, item 8, and `general_answer_passage_missing`,
  item 17, each lose their only current v2 occurrence and remain in the union as historical
  first-pass names, each occurring once as a secondary in `case_memos_v1.csv`.
- `case_memos_v2.csv` now holds **87 secondary assignments over 31 distinct names**, up from 84
  and down from 33: this row went from two descriptors to five, and the two departing names were
  unique to it. The distinct `primary_open_code` count in v2 falls from 14 to **13**, because
  `question_wording_ambiguity` was unique to this row. `case_memos_v1.csv` is unchanged at 39
  distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**. Five existing entries gain this
  affected unit and D-034 as a decision source, `surface_form_tokenization_mismatch`,
  `generic_term_lexical_crowding`, `repeated_function_word_amplification`,
  `gold_chain_substitutability` and `description_only_bridge_entity`; four gain D-034 as a
  decision source recording a non-adoption, `cutoff_sensitive_near_miss`,
  `generic_query_scaffold_score_inflation`, `related_name_document_crowding` and
  `cross_passage_conjunction_unresolved`; and `unindexed_title_name_anchor`'s inert-or-negative
  list gains D-034. In every case no definition, inclusion rule or exclusion rule is changed.
- `review_status` counts are now 25 `jointly_reviewed` and 5 `needs_joint_review`. Twenty-five
  rows now carry a populated `candidate_category`.
- Validation progress after D-034 is **21 of 26 validated, 5 remaining**, superseding the
  20-of-26 figure recorded in section 7A.17.
- Three vocabulary-audit items are registered by this decision and settled by none of it:
  whether a withholding of `cutoff_sensitive_near_miss` that rests on substitutability rather
  than on the score gap should be allowed to leave the percentage bands untouched, this being
  the first withholding at a figure inside the accepted band and the first since D-015 to turn
  on substitutability; whether the direct experiment that separates
  `repeated_function_word_amplification` from `generic_query_scaffold_score_inflation` should be
  written into both entries as the test, D-033 and D-034 now supplying one boundary sample in
  each direction; and whether `minimal_preprocessing_score_distortion`, now at nine units and
  six sub-mechanisms, should be narrowed. To the last of these D-034 adds that the crowding
  family here is outcome-determinative only after the primary's repair, which is the same
  baseline-dependence D-033 registered, now shown to reach pit 19u's own cell.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.19 - Validate `5add67915542992200553af8|dense`

D-035 replaces the provisional primary `same_domain_entity_crowding` with
`description_only_bridge_entity`, which is that name's fourth validated primary use and its
fourth on a Dense unit, and the seventh consecutive decision to register no new descriptor.
Re-encoding the same 4,937-passage pooled corpus reproduces all 50 stored top-50 titles in order,
0 of 50 mismatched, at a maximum absolute score error of 2.980e-07, so strong causal claims are
supported. Complete-corpus ranks are 7 / 0.438223 for `Philadelphia crime family`, which supplies
the bridge fact that the Philadelphia crime family is an Italian American criminal organization,
and 12 / 0.406772 for `Salvatore Testa`, which supplies the nickname and the hitman relation. The
rank-5 score is 0.476272, so the two required passages sit 0.038049 and 0.069500 points, or 7.989
and 14.592 percent, below the cutoff, and no cliff separates the cutoff region from either. Both
passages sit inside the 256-token sequence limit at 120 and 82 model tokens, so truncation is
excluded. The question contains no proper name for either required entity and no proper name at
all, which is the first such question in this pass.

196 distinct labelled conditions were run on the same unchanged candidate set, 5 of them
deliberately repeated under a second producer with every repeat reproducing its original bit for
bit, plus 4 `not_run` cells with reasons. The reproduction script carries 154 assertions and all
pass.

One implementation fact governs the whole diagnostic and it is the reason the provisional primary
cannot stand. Cosine carries no collection statistic, so removing documents leaves every score
unchanged and every index-side removal probe is an arithmetic identity in which `rank_after`
equals `rank_before` minus the number of removed passages that ranked above the gold. Nine cells
confirm it exactly with every score bit-identical, and two different random 7-passage subsets of
the same pool give the same answer-hop rank of 5. Pit 19y treats only the drop-everything cell as
an identity and offers the family probe with a complement control as the discriminating
alternative; on this evidence that alternative is an identity too, the family and its complement
differing only in size. No crowding reading can therefore take the primary on this unit, because
the only causal evidence form available to it produces counts rather than effects.

What is measured instead is the query side, which does change the scores, and it is decisive in
both directions. The question's referring description alone reproduces 9 of the baseline top ten
and 6 of the 7 person biographies above the answer passage; deleting that description leaves 0
and 0; deleting only its demonym half leaves 2 and 1; the answer frame alone gives 0 and 0. A
16-cell non-oracle factorial on that expression locates two defects binding on different required
passages: changing only the head noun gives 3 / 13, deleting only the demonym gives 15 / 5, and
both together give 1 / 0.585624 and 4 / 0.510640. Single-factor mean rank deltas are -1.12 and
+6.00 for keeping `Italian`, -0.12 and +1.25 for keeping `American`, -7.88 and +0.75 for the head
noun and -2.38 and -2.75 for inserting `gangster`, so three of the four factors carry opposite
signs and the factor that discriminates the question's own constraint is very nearly inert.

The adopted primary is carried by a partition of the condition set. Of the labelled query
conditions that keep `Italian American Criminal Organization` verbatim, every one that puts both
required passages inside the cutoff is an oracle injection and none is non-oracle; the seven
non-oracle conditions that do recover both all replace that expression, and not one keeps the
demonym `Italian`, the constraint-preserving variant that changes only the head noun giving
3 / 13 and failing. That is the D-028 refutation path sliced by whether a condition leaves the
referring expression intact, and it is what distinguishes this unit from D-028, where the
refuting condition was index-side and left the query untouched. The single-factor oracle-name test
is the twelfth application and the sixth pass, recovering both hops in five forms, with the D-024
precondition holding in the D-026 form, the bridge title alone giving 1 / 0.706333 and lifting the
other required passage to 5 / 0.440004, and the D-030 degeneracy check passed, `Philadelphia`
alone giving 1 / 0.554958 and 2 / 0.499144. The gold-side ceiling is 1 / 0.585251 and
7 / 0.460718, so no index-side repair of the required passages suffices, and title indexing is
inert to negative at 7 / 0.428354 and 12 / 0.401174.

The descriptor gains a form no earlier use recorded: the descriptive substitute is present in the
required passage verbatim, `is an Italian American criminal organization` occurring word for word
in exactly 2 of 4,937 passages, and is still not discriminative, ranking that passage 1 / 0.541525
on its own and 7 / 0.438223 inside the full question. It is also a net liability for the other
required passage, whose rank improves by 7 positions when the demonym compound is deleted. Two
single-fact controls are worth recording beside it: deleting the whole nickname clause from the
answer passage moves it from 12 / 0.406772 to 6 / 0.463775, so removing the answer improves the
passage, and deleting only the bridge link is worth 0 rank positions at 12 / 0.407196.

### Inventory effect

- The primary inventory is unchanged at **26 distinct names**.
  `description_only_bridge_entity` is item 5, was already in the inventory, and this is its
  fourth validated primary use. The departing name `same_domain_entity_crowding` is item 22 and
  now keeps no current `case_memos_v2.csv` row of either kind, this unit having been its only
  holder.
- The secondary-name union is unchanged at **50 distinct names**. The departing name
  `bridge_relation_underweighted` is item 1 of the primary inventory and now keeps no current
  `case_memos_v2.csv` row at all, this having been its last; it remains in the union as a
  historical first-pass name, the treatment given to `location_chain_incomplete`,
  `subject_associate_crowding`, `generic_context_substitution`, `adjacent_event_crowding`,
  `related_document_crowding`, `broad_film_person_neighborhood`, `surname_entity_confusion` and
  `both_gold_chain_passages_missing`.
- `case_memos_v2.csv` now holds **89 secondary assignments over 30 distinct names**, up from 87
  and down from 31: this row went from one descriptor to three, the departing name was unique to
  it, and all three adopted names already occur elsewhere in the column. The distinct
  `primary_open_code` count in v2 falls from 13 to **12**, because `same_domain_entity_crowding`
  was unique to this row. `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**. Three existing entries gain this
  affected unit and D-035 as a decision source, `peripheral_passage_content_dilution`, which
  reaches five affected units, `generic_person_semantic_neighborhood`, which reaches four, and
  `same_topic_passage_distractor`, which reaches two and gains its first Dense unit; three gain
  D-035 as a decision source recording a non-adoption, `cross_passage_conjunction_unresolved`,
  `question_frame_semantic_crowding` and `cutoff_sensitive_near_miss`; and
  `description_only_bridge_entity` gains D-035 in its note on primary use, which is why this unit
  is not listed there as a secondary affected unit. In every case no definition, inclusion rule or
  exclusion rule is changed, although the dilution gate's third condition gains a usage
  requirement at the level of single words rather than sentences.
- `review_status` counts are now 26 `jointly_reviewed` and 4 `needs_joint_review`. Twenty-six
  rows now carry a populated `candidate_category`.
- Validation progress after D-035 is **22 of 26 validated, 4 remaining**, superseding the
  21-of-26 figure recorded in section 7A.18.
- Four vocabulary-audit items are registered by this decision and settled by none of it. First,
  whether the family probes on the earlier Dense units should be re-read now that every
  index-side removal probe on a bi-encoder is shown to be an arithmetic identity, which reaches
  D-023, D-025, D-026, D-029 and D-031 and is not a re-judgment of any of them; the same
  observation removes the counter-evidence `cutoff_sensitive_near_miss` has weighed since D-022
  whenever the retriever is Dense. Second, whether an absent name anchor, an unusable one and an
  insufficient verbatim description belong under one descriptor, this unit being the third
  boundary sample after the one D-029 registered and the one D-034 added. Third, the
  already-registered question about that entry's definition, worded `for lexical retrieval` while
  all four of its primary uses are Dense. Fourth, whether the length-matched control of the
  dilution gate should be required to be decontaminated word by word rather than sentence by
  sentence, this being the first unit in which two controls passed the sentence-level form and
  failed the word-level one.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.20 - Validate `5adf58f15542993a75d264d2|bm25`

Queue item 23, a Xin-only BM25 bridge unit, landed as D-036. This is the fourth decision to
retain a unit's provisional primary, after D-015, D-020 and D-032, and the first single-note
unit to carry `plausible_non_gold_answer`, which had been used once before on the D-011
overlap unit.

`plausible_non_gold_answer` is retained on read text and on measurement. `Filthy Rich &amp;
Catflap` at 3 / 20.130130 states that the BBC sitcom's series featured former "The Young Ones"
co-stars Nigel Planer, Rik Mayall and Adrian Edmondson, so one passage inside the cutoff
satisfies every explicit constraint of the question, and it does so without the reconciliation
the annotated chain needs between one required passage calling "The Comic Strip Presents..." a
series of films and the other calling it a television series. It is not an artefact of the
preprocessing defect measured below: it ranks 1 / 27.168933 under the deployable query-side
repair, 1 / 29.428445 under full two-sided normalization and 3 / 0.633169 on the comparison
retriever, and only the official per-question setting puts the annotated bridge passage above
it.

`underdetermined_question` is deleted rather than registered, the second deletion of a
question-property name after D-034 removed `question_wording_ambiguity` and on the same
ground. Pits 19k and 19ah were satisfied before the verdict was read: the repair was run as a
full A by B by C factorial in two preprocessing states, and all 8 cells whose added constraint
is oracle place both required passages inside the cutoff while all 8 non-oracle cells fail, in
both states. A question property that only a fact stated inside the golds can repair is not a
retrieval mechanism, and what the name was recording is carried, with a passage behind it, by
`gold_chain_not_unique`.

Five descriptors are adopted, none of them new. `surface_form_tokenization_mismatch` on two
worked pairs, `ones"?` against `ones"` on the query side and `ade` against `"ade"` inside the
bridge passage's own name. `generic_term_lexical_crowding` on the four higher-ranked passages
that fail the question. `cross_entity_token_recombination` on the passage that defined the
cutoff, which took 40.4 percent of its score from two fragments of the query's quoted title
supplied by four unrelated works. `description_only_bridge_entity` as a secondary, its
inclusion rule met in the D-029 form and the D-020 oracle-name test passing, but not as the
primary because a blind query-side repair reaches the bridge passage at 2 / 25.786297.
`cutoff_sensitive_near_miss` for the near hop only, at 0.281 percent, the smallest margin this
project has recorded.

Eight further descriptors were considered and explicitly not adopted:
`cross_passage_conjunction_unresolved`, on its first exclusion, one passage supplying a
complete answer, which is the exclusion D-011 also used; `gold_chain_substitutability`,
because the alternative changes the answer; `generic_query_scaffold_score_inflation`, on its
second exclusion, content-bearing category terms outweighing scaffold in every one of the five
passages above the near hop; `repeated_function_word_amplification` and
`repeated_content_word_amplification`, the query repeating no token;
`unindexed_title_name_anchor`, on its second inclusion condition although its third holds, the
title-indexing condition being measurably positive at 5 / 19.745864 while neither gold title
contains a query token; `same_topic_passage_distractor`, the competitors being generic category
matches rather than passages in the answer entity's own neighbourhood;
`peripheral_passage_content_dilution`, scoped to a mean-pooled encoder; and
`proper_name_homonym_collision`, whose real instance sits at 18 / 17.701479, below the near hop
and so not outcome-determinative.

Corpus setting is provenance under D-003 and pit 17, and the two settings disagree on `any@5`.
Pooled gives `any@5` 0 and `full@5` 0 at 6 and 329 and the official per-question setting gives
`any@5` 1 and `full@5` 0 at 1 and 10, the rebuilt per-question index reproducing the stored CSV
order title by title. This is the ninth `any@5` divergence in the series and the fourth unit,
after D-028, D-030 and D-033, to present more than one path at once: 4 of the 5 passages above
the near hop are pooling-introduced, and restricting the pooled scores to the item's own 10
still leaves the alternative answer above it, so the per-question idf carries the swap on its
own.

### Inventory effect

- The primary inventory is unchanged at **26 distinct names**. `plausible_non_gold_answer` is
  item 16, was already in the inventory, and this is the first single-note row to carry it as a
  primary; no name enters or leaves it, because the deleted name was a secondary.
- The secondary-name union is unchanged at **50 distinct names**. The departing name
  `underdetermined_question` is item 45 of the union and now keeps no current
  `case_memos_v2.csv` row at all, this having been its only one; it remains in the union as a
  historical first-pass name, the treatment given to `question_wording_ambiguity` at D-034 and
  to `location_chain_incomplete` and its fellows before that.
- `case_memos_v2.csv` now holds **93 secondary assignments over 30 distinct names**, up from 89
  and unchanged on the distinct count: this row went from two descriptors to six, the departing
  name was unique to it, and of the five arriving names four already occur elsewhere in the
  column while `cross_entity_token_recombination` did not, so the two movements cancel. The
  distinct `primary_open_code` count in v2 is unchanged at **12**, the primary having been
  retained. `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**. Six existing entries gain this
  affected unit and D-036 as a decision source, `gold_chain_not_unique`, which reaches two
  affected units and its first lexical one, `surface_form_tokenization_mismatch`, which reaches
  eleven, `generic_term_lexical_crowding`, which reaches nine,
  `cross_entity_token_recombination`, which reaches two and its first since D-010,
  `description_only_bridge_entity`, which reaches ten, and `cutoff_sensitive_near_miss`, which
  reaches seven and is adopted for the near passage only. In every case no definition,
  inclusion rule or exclusion rule is changed. Two band edges move inside the
  `cutoff_sensitive_near_miss` entry, the accepted band's lower edge to 0.281 percent and the
  excluded band's upper edge to 53.000 percent; the never-decided band is unchanged at 5.464 to
  9.431 percent.
- `review_status` counts are now 27 `jointly_reviewed` and 3 `needs_joint_review`. Twenty-seven
  rows now carry a populated `candidate_category`.
- Validation progress after D-036 is **23 of 26 validated, 3 remaining**, superseding the
  22-of-26 figure recorded in section 7A.19.
- Three vocabulary-audit items are registered by this decision and settled by none of it.
  First, the `cutoff_sensitive_near_miss` entry now carries two statements of D-025's split
  rule that do not agree, D-025, D-026 and D-032 having adopted the descriptor for the near hop
  while the far hop sat inside the excluded band, and D-035 restating the rule as forbidding the
  descriptor for the whole unit whatever the near figure does; D-036 follows the landed
  adoptions and refers the wording here. Second, whether that descriptor means the same thing on
  a unit where a complete alternative answer already sits inside the cutoff, since what it
  records there is the fragility of the annotated title rather than of answer availability.
  Third, whether `description_only_bridge_entity` and `plausible_non_gold_answer` may sit on one
  unit at all, the first saying the annotated chain is unreachable without a name and the second
  saying it did not have to be reached.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.21 - Validate `5ae048a255429924de1b708e|dense`

Queue item 24, a Xin-only Dense bridge unit, landed as D-037. This is the first primary use
of `peripheral_passage_content_dilution`, the second growth of the primary inventory by
promoting a registered secondary rather than by coining a name after D-029, and the eighth
consecutive decision to register no new descriptor.

`peripheral_passage_content_dilution` passes all four include conditions on both required
passages and takes the primary. The contract is verified from implementation and both
passages sit inside the sequence limit at 82 and 57 model tokens. The answer hop goes from
263 / 0.244736 to 11 / 0.378848 at a 22-word verbatim subset of its own body and to
2 / 0.469751 at 11 words, while length-matched controls that keep its subject name and carry
no query-relevant word give 864 / 0.144759, 1052 / 0.124028, 921 / 0.137778 and
788 / 0.153279 at 12, 25, 40 and 53 words; the constraint hop goes from 39 / 0.320936 to
3 / 0.450154 and 1 / 0.549310 against controls of 745 / 0.158364 and 803 / 0.151917. The
ground on which this gate was withheld from the primary five times before is measured here
and does not hold: reducing both bodies at once gives 3 / 0.469751 and 1 / 0.549310, the
first two-sided ablation ceiling in this project to place both required passages inside the
cutoff, against 863 / 0.144759 and 871 / 0.143892 for the same two rows at matched length.

The unit adds a second, directional form of the third include condition. The same ablation
that lifts a probe matching the retained material lowers a probe matching the removed
material, `Halle Berry` going from 141 / 0.249922 to 426 / 0.183656 and `Jennifer Hale` from
31 / 0.307791 to 420 / 0.177707, so content and brevity are separated twice over.

`question_frame_semantic_crowding` is adopted as the only secondary and is the closest
competitor for the primary. Both halves of its include rule hold on read text, all 38
non-gold passages above the constraint hop matching the question's framing facets while 0 of
them contain `Catwoman` and 0 contain `Pitof`, and both directions of the crowding criterion
agree, the frame alone reproducing 6 of the baseline top ten and the referring cue 1 of ten,
with 8 of ten surviving the deletion of the word `Pitof`. It loses the primary on
outcome-determinacy rather than on its rule: 22 removal cells all reduce to
`rank_after = rank_before - |removed and ranked above it|` with the gold scores identical to
the last bit, so on this backend the reading cannot be given outcome-determinative evidence,
and the one query-side lever on the family points the other way, deleting the whole game
clause moving both required passages to 545 / 0.203382 and 937 / 0.150986.

Two provisional names are deleted rather than registered, the third landing to delete two or
more at once after D-031 and D-033. `broad_adaptation_topic_crowding` names the same
competitor set as the registered `question_frame_semantic_crowding` under a narrower label
and this unit was its only holder, the ground D-031 used for `subject_associate_crowding` and
D-033 for `cross_entity_relation_unresolved`. `answer_entity_missing_both_methods` is deleted
on the two independent grounds D-033 used for the same name: it states gold missingness,
which is a result and not a mechanism, and it is factually wrong, the passage it calls
missing sitting at 263 / 0.244736 on this retriever and 3241 / 5.756382 on BM25. This unit
was its last holder, so the name now keeps no current `case_memos_v2.csv` row at all.

Eight further descriptors were considered and explicitly not adopted:
`cross_passage_conjunction_unresolved`, on the D-026 route, a single anchor lifting both
sides at 2 / 0.769825 and 1 / 0.788529 while the opposite-sign leg is only 2 of 13 and the
linking name is written in both required bodies rather than only in the other;
`description_only_bridge_entity`, on the D-028 route, the double recovery being an index-side
change with the query untouched word for word, and although the oracle-name test passes in
six forms pit 15 puts the non-oracle result first; `same_topic_passage_distractor`, which
would duplicate the adopted secondary with no partition available, unlike the 7 and 3 split
at D-035; `generic_person_semantic_neighborhood`, only 1 of the 38 being a person page;
`unindexed_title_name_anchor`, on its second inclusion condition, the title-indexing
condition being materially positive at 125 / 0.273863 and 5 / 0.387651 while neither title
carries the query's anchor `Pitof`, a three-cell decomposition showing the gain comes from
the parenthetical type words rather than the name, 260 / 0.247282 and 26 / 0.333190 for the
bare name against 91 / 0.292896 and 8 / 0.388039 for the disambiguator alone;
`cutoff_sensitive_near_miss`, both hops sitting inside the excluded band at 38.259 and 19.036
percent with no cliff below the cutoff; and `gold_chain_substitutability`,
`gold_chain_not_unique` and `plausible_non_gold_answer`, `pitof` occurring in 1 of 4,937
bodies and `catwoman` in 2, so no substitute, no alternative chain and no complete non-gold
answer exists. `low_context_name_query` is refused on its own terms, the question being a
19-word relational sentence rather than a short name-dominated one.

Corpus setting is provenance under D-003 and pit 17, and the two settings agree on both
metrics. Pooled gives `any@5` 0 and `full@5` 0 at 263 and 39 and the official per-question
setting gives `any@5` 0 and `full@5` 0 at 10 and 7, restricting the pooled scores to those
same 10 reproducing both gold scores bit for bit and the official window exactly, the eighth
verification of the Dense restriction property. This is the fourth unit whose two settings
agree on both metrics, after D-021 on BM25 and D-027 and D-031 on Dense. Of the three paths,
the added-competitor one is excluded because dropping only the 253 and 32 pooling-introduced
passages returns exactly the per-question ranks, which on this backend is the restriction
identity rather than a measurement; the idf-scale path cannot apply to a bi-encoder; and the
annotator-supplied path holds, the answer hop being last of the ten in its own window.

### Inventory effect

- The primary inventory is now **27 distinct names**, up from 26, the arriving name being
  `peripheral_passage_content_dilution`. This is the second growth by promotion rather than by
  coinage, after D-029 promoted `question_frame_semantic_crowding`; the name is not new, only
  new to this inventory, having been a registered secondary since D-023. The departing name
  `cross_passage_conjunction_unresolved` is item 4 and **keeps four other current v2 primary
  rows**, those of D-022, D-024, D-025 and D-031, so unlike the departing names of D-021,
  D-022, D-023, D-027, D-028 and D-029 it does not become a historical-only entry.
- The secondary-name union is unchanged at **50 distinct names**. Both departing names now
  keep no current `case_memos_v2.csv` row at all: `broad_adaptation_topic_crowding` had this
  row as its only one, and `answer_entity_missing_both_methods` had this row as its last one
  after D-033 removed the other. They remain in the union as historical first-pass names, the
  treatment given to `underdetermined_question` at D-036 and to `question_wording_ambiguity`
  at D-034.
- `case_memos_v2.csv` now holds **92 secondary assignments over 28 distinct names**, down from
  93 and 30: this row went from two descriptors to one, both departing names were unique to it
  in the column, and the arriving `question_frame_semantic_crowding` already occurs elsewhere.
  The distinct `primary_open_code` count in v2 rises to **13**, the arriving primary being new
  to that column while the departing one keeps four other rows. `case_memos_v1.csv` is
  unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**. Three existing entries are edited
  and none of them gains a definition, inclusion-rule or exclusion-rule change.
  `question_frame_semantic_crowding` gains this affected unit and D-037 as a decision source,
  reaching three affected units. `peripheral_passage_content_dilution` gains D-037 as a
  decision source and a usage paragraph but **not** this affected unit, because the project
  does not list a unit as affected when the name is that unit's primary.
  `cross_passage_conjunction_unresolved` gains D-037 as a decision source recording an eighth
  non-adoption. No band edge moves anywhere in the file.
- `review_status` counts are now 28 `jointly_reviewed` and 2 `needs_joint_review`.
  Twenty-eight rows now carry a populated `candidate_category`.
- Validation progress after D-037 is **24 of 26 validated, 2 remaining**, superseding the
  23-of-26 figure recorded in section 7A.20.
- Two vocabulary-audit items are registered by this decision and settled by none of it.
  First, whether a primary use of `peripheral_passage_content_dilution` needs a primary-use
  contract, since that entry's attribution boundary calls the descriptor a diagnostic rather
  than a deployable fix while a primary is normally read as a mechanism. Second, whether
  D-029's open boundary between an absent name anchor and an unusable one still needs a
  descriptor of its own, since this unit attributes the unusable anchor to the adopted
  primary: the corpus-unique name `Pitof` ranks its sole bearer 1283 / 0.076500 against the
  untouched body, 1 / 0.391955 against an 8-word verbatim subset of that same body and
  894 / 0.095909 against a 12-word length-matched control.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.22 - Validate `5ae1801955429901ffe4aec4|dense`

Queue item 25, a Xin-only Dense bridge unit, landed as D-038. This is the fourth primary use
of `cross_passage_conjunction_unresolved` and its second on Dense, the ninth consecutive
decision to register no new descriptor, and the first unit on which both of that name's
refusal routes were measured and neither fired.

`cross_passage_conjunction_unresolved` takes the primary. The three positive legs hold in
their Dense-available forms: the matched-token leg has no Dense analogue as D-025 records;
8 of 16 single factors carry opposite signs across the hops, a proportion matching D-025's
10 of 20 and far above the 4 of 19 on which D-026 refused this name; and the missing
intermediate fact is concrete and written in exactly 1 of 4,937 indexed bodies. Per-side
reachability holds from the question's own wording rather than from a rewrite, `former
Superman sponsor` giving the constraint hop 2 / 0.415715 and `sponsored by cereal
manufacturer` giving the answer hop 1 / 0.592832, while the question as annotated gives
173 / 0.225424 and 11 / 0.345068 and deleting either referring expression restores one side
and destroys the other, 3 / 0.444093 and 1554 / 0.092815 without one and 4481 / -0.058135
and 3 / 0.413657 without the other. The D-026 route does not fire: five single anchors are
one-sided with the far hop between 2731 and 4426, `Kellogg's` alone giving 4426 / -0.054776
and 1 / 0.704330. The D-028 route of pit 19s does not fire either: none of 48 non-oracle
query conditions places both required passages inside the cutoff, the best deployable one
reaching 154 / 0.242010 and 2 / 0.527444, and the only query-side double recovery anywhere
is the pure oracle of appending both gold titles at 2 / 0.416027 and 1 / 0.464131. Neither
exclusion fires.

`peripheral_passage_content_dilution` is the closest competitor and is adopted as a
secondary scoped to `Adventures of Superman (TV series)`. The gate passes there in a strong
form, 7 words of query-relevant material giving 1 / 0.452921 against 9 words of non-relevant
material from the same body at 425 / 0.178357, with uncontaminated controls at
967 / 0.129091 and 2517 / 0.053330 and D-035's word-level decontamination doing the deciding:
six controls that improve the rank all retain the query word `Superman`, and removing just
those two words from the 24-word control moves it from 144 / 0.236000 to 569 / 0.160981. It
fails on the answer hop on the second include condition outright, that body reduced to the
sentence stating the answer giving 89 / 0.254490 against a baseline of 11 / 0.345068, and on
the third as well. It loses the primary on the ground D-023, D-026, D-027, D-029 and D-035
recorded and D-037 broke: the licensed two-sided ceiling is 1 / 0.509545 and 12 / 0.345068,
and adding the only answer-side edit that helps gives 1 / 0.509545 and 6 / 0.376585. One
unlicensed gold-targeted pairing does double-recover at 1 / 0.509545 and 3 / 0.406656 and is
recorded rather than smoothed over.

`cutoff_sensitive_near_miss` is adopted scoped to `Kellogg's`, the two required passages
sitting 38.030 and 5.140 percent below the rank-5 score of 0.363764, and no band edge moves.
`same_topic_passage_distractor` is adopted scoped to `Superman: Tower of Power`
8 / 0.353345, `Twisties` 9 / 0.350352 and `General Mills` 10 / 0.346669, as a composition and
not as a causal claim, the other seven passages above the answer hop being named as not
covered.

One provisional name is deleted rather than registered. `partial_bridge_only` states an
outcome shape and not a mechanism, which is pit 17 and D-003, the ground D-033 and D-037 used
for `answer_entity_missing_both_methods` and D-031 for `subject_associate_crowding`; and the
shape it names is a consequence of the adopted primary, each referring expression alone
reaching its own side at 2 / 0.415715 and 2 / 0.404215 while the two together reach neither.
This unit was its only holder, so the name now keeps no current `case_memos_v2.csv` row.

Six further descriptors were considered and explicitly not adopted:
`question_frame_semantic_crowding`, whose include rule fails in the forward direction, the
frame alone reproducing 1, 1, 2 and 2 of the baseline top ten while the referring expressions
reproduce 4 and 6, so the third exclusion fires and the shape is the reverse of D-037;
`description_only_bridge_entity`, on the D-028 route, the single-factor oracle-name test
failing at 1 / 0.483498 and 97 / 0.244636 and at 556 / 0.151134 and 1 / 0.542954 while the
absence of a name is not the binding constraint, the question's own sub-phrase reaching the
constraint hop at 2 / 0.415715 and an index-side change with the query untouched reaching it
at 1 / 0.452921; `gold_chain_substitutability`, the one substitute supplying the required
intermediate fact of neither gold; `gold_chain_not_unique` and `plausible_non_gold_answer`,
`battle creek` occurring in 1 of 4,937 bodies and `adventures of superman` in 1;
`unindexed_title_name_anchor`, title indexing moving 173 / 0.225424 and 11 / 0.345068 only to
135 / 0.226319 and 9 / 0.328467 and flipping neither metric; and `compound_two_sided_crowding`
together with `generic_person_semantic_neighborhood`, no removal probe being able to help the
far hop at all because on this backend all 14 that were run are arithmetic identities.
`low_context_name_query` is refused on its own terms, the question being a relational
sentence rather than a short name-dominated one.

Corpus setting is provenance under D-003 and pit 17, and here the two settings disagree on
one metric. Pooled gives `any@5` 0 and `full@5` 0 at 173 / 0.225424 and 11 / 0.345068, and
the official per-question setting gives `any@5` 1 and `full@5` 0 at 6 / 0.225424 and
3 / 0.345068. Restricting the pooled scores to those same 10 reproduces the official window
exactly and both gold scores to every printed digit, at a largest absolute difference of
2.980e-08 over the ten, the ninth verification of the Dense restriction property. Of the
three paths, the added-competitor one holds, only 2 of the 10 passages above the answer hop
coming from this question's own window; the idf-scale path cannot apply to a bi-encoder; and
the annotator-supplied path holds in part, this question's own 8 distractors standing above
the constraint hop 4 times and above the answer hop 2 times.

### Inventory effect

- The primary inventory is unchanged at **27 distinct names**. The departing name
  `partial_bridge_only` is item 14 of the preserved list and now keeps no current v2 row at
  all, the treatment given to `broad_adaptation_topic_crowding` and
  `answer_entity_missing_both_methods` at D-037; the arriving name
  `cross_passage_conjunction_unresolved` was already in the inventory and already the primary
  of four other current rows, so this landing adds no name to either side.
- The secondary-name union is unchanged at **50 distinct names**. The two departing
  secondaries both keep other current rows, `cross_passage_conjunction_unresolved` in the
  rows of D-017 and D-020 and `gold_chain_substitutability` in the rows of D-014, D-015,
  D-023, D-025 and D-034, and all three arriving secondaries were already in the column.
- `case_memos_v2.csv` now holds **93 secondary assignments over 28 distinct names**, up from
  92 over 28: this row went from two descriptors to three and every arriving and departing
  name occurs elsewhere in the column. The distinct `primary_open_code` count in v2 falls to
  **12**, the departing primary having had this row as its only one while the arriving one
  already held four. `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**. Six existing entries are edited
  and none of them gains a definition, inclusion-rule or exclusion-rule change.
  `peripheral_passage_content_dilution`, `cutoff_sensitive_near_miss` and
  `same_topic_passage_distractor` each gain this affected unit and D-038 as a decision source.
  `cross_passage_conjunction_unresolved` gains D-038 as a decision source and a usage
  paragraph but **not** this affected unit, because the project does not list a unit as
  affected when the name is that unit's primary; its note on primary use gains a fourth
  member. `question_frame_semantic_crowding` and `gold_chain_substitutability` each gain
  D-038 as a decision source recording a non-adoption, and neither gains an affected unit.
  No band edge moves anywhere in the file.
- `review_status` counts are now 29 `jointly_reviewed` and 1 `needs_joint_review`.
  Twenty-nine rows now carry a populated `candidate_category`.
- Validation progress after D-038 is **25 of 26 validated, 1 remaining**, superseding the
  24-of-26 figure recorded in section 7A.21.
- Two vocabulary-audit items are registered by this decision and settled by none of it.
  First, whether a non-gold passage that reaches the same bridge entity through a different
  one of the question's constraints counts under `gold_chain_substitutability`: `Cocoa
  Krispies` at 2 / 0.406143 names the bridge entity the question never names but supplies the
  required intermediate fact of neither gold, while D-023 adopted a substitute that supplied
  its own gold's fact and verified only one of two constraints. Second, whether
  `cutoff_sensitive_near_miss` should be readable at all on a unit whose other required
  passage sits 38.030 percent below the cutoff, which is the split-rule wording D-036
  referred to the audit and which this decision follows rather than settles.

These remain vocabulary counts, not validated mechanism counts and not prevalence.

## Section 7A.23 - Validate `5ae60426554299546bf83019|bm25`

Queue item 26, a Xin-only BM25 bridge unit, landed as D-039. This is the **last item in the
26-unit queue**, so the section 7A validation gate is now complete. It is the sixth primary
use of `cross_passage_conjunction_unresolved` and its third on a lexical backend, the tenth
consecutive decision to register no new descriptor, and the first landing to delete two
provisional names at once. It also corrects the registry's member enumeration for that
name, which omitted D-031 and so made D-038 call itself the fourth primary use when it was
the fifth; D-038's sentence stays as written under red line 4 and the enumeration is what
changes, which is the treatment section E rule 4 prescribes.

`cross_passage_conjunction_unresolved` takes the primary. The three positive legs hold in
their strongest recorded forms. The matched-token leg is an **empty intersection**: the
answer hop scores only on `animated` 5.482144, `space` 4.737610, `western` 3.490203,
`series` 3.188841 and `american` 1.088638, the constraint hop only on `celebrity` 6.911643,
`entertainment` 4.863113, `home` 4.662400 and `released` 2.332813, and the question's
37.094684 of query idf divides into a genre facet of 15.934678, or 42.96 percent, and a
distributor facet of 15.345775, or 41.37 percent, so each required passage forfeits
21.160006 and 21.748909 respectively, 57.04 and 58.63 percent of the question, by
construction. 6 of 11 single query tokens carry opposite signs across the hops, the highest
proportion measured in this project, above D-024's 10 of 19, D-025's 10 of 20 and D-031's
8 of 22 and far above the 4 of 19 on which D-026 refused this name. Per-side reachability
holds in D-025's shape rather than D-026's, each name lifting its own side and annihilating
the other, `BraveStarr` alone giving 1 / 7.786100 and 4607 / 0.000000 and `Celebrity Home
Entertainment` alone giving 4625 / 0.000000 and 4 / 16.437155. The D-028 route of pit 19s
does not fire: none of **134 non-oracle conditions** places both required passages inside
the cutoff, the Pareto frontier has exactly four corners, and at three of them the answer
hop's score is bit for bit its baseline 17.987437, no non-oracle condition anywhere adding a
single point to it. The closest deployable pipeline reaches 6 / 18.101334 and
2 / 24.260792, short by 0.134368 points and 0.737 percent. Neither exclusion fires.

`related_name_document_crowding` is the closest competitor and is adopted as a secondary.
Its include rule is met on read text by five non-gold passages above the answer hop that name
the distributor, and pit 19ad's three controls separate cleanly: removing the family gives
3 / 18.007533 and 1 / 19.544516, its complement gives 7 / 18.013998 and 6 / 18.775924, a
size-matched null gives 8 / 18.069800 and 6 / 18.771378, and the statistics-matched control
gives 3 / 17.987437 and 1 / 18.769969, **both scores bit for bit the baseline**, so the whole
effect is positional and the collection statistics carry none of it. Pits 19af and 19ag are
satisfied and the two states agree. It loses the primary on three grounds. Pits 19f and 19i
agree in sign, the distributor name alone reproducing 7 of the baseline top ten and 5 of 5 of
the family while the genre facet reproduces 1 and 0 of 5, and deleting the distributor name
collapsing the family to 0 of 5 while deleting the genre facet leaves it at 5 of 5, which is
D-023's and D-024's ground for holding a crowding name at secondary. **The family and the
required evidence are the same lexical class**: a rule stated from the question alone selects
six passages, one of which is the required constraint gold, and applying it gives
2 / 18.006690 with that gold gone from the index; what separates the gold from its own name
family is written only in the other gold. And D-024 is the same shape on the same backend and
settled the same way.

`cutoff_sensitive_near_miss` is adopted on **both** required passages, at 4.860 and 0.721
percent below the rank-5 score of 18.906282, and no band edge moves, both figures lying
inside the accepted band. This is the first two-sided adoption in the project and therefore
the first on which the descriptor describes `full@5` rather than `any@5` under the D-025
split rule. The no-substitute condition holds on both sides and the counter-evidence is the
strongest recorded, the cumulative ladder crossing at the third removal with
5 / 18.005642 and 3 / 19.187204. `surface_form_tokenization_mismatch` is adopted for the
constraint gold's own indexed `"Celebrity`, worth 2.580995 points and 4 rank positions
gold-targeted and 2.388634 points and the same 4 positions deployable, the second unit after
D-034 at which pit 19ae's deployable cell costs nothing in rank.
`generic_query_scaffold_score_inflation` is adopted for `Pergament Home Centers`
7 / 18.620405, an unrelated home-improvement chain drawing 7.943527 of its score, 42.7
percent, from `did` and `which` and only 10.676878 from content, against the answer hop's
17.987437. `same_topic_passage_distractor` is adopted for `COPS (animated TV series)`
1 / 24.991204, which matches 8 of the question's 11 tokens and whose text contains neither
`space` nor `western`.

Two provisional names are deleted rather than registered, the first landing to delete two.
`partial_match_constraint_omission` states a ranking pattern and not a mechanism, which is
pit 17 and word for word the ground on which D-033 deleted this same name at queue item 20;
the observation it names is already partitioned between `same_topic_passage_distractor` and
`related_name_document_crowding`; and the adopted primary dissolves it, the constraint being
omitted because no single passage carries both halves of the question. **This unit was its
last holder**, so the name now keeps no current `case_memos_v2.csv` row at all.
`distributor_related_document_crowding` duplicates `related_name_document_crowding`, whose
definition covers "institutions, or associates sharing a name or name token", on the
criterion D-031 used for `subject_associate_crowding`, D-033 for
`cross_entity_relation_unresolved` and D-037 for `broad_adaptation_topic_crowding`.

Eight further descriptors were considered and explicitly not adopted.
`unindexed_title_name_anchor`, whose three include conditions are all met and whose
title-indexing condition is materially positive at 6 / 18.769969 to 2 / 23.750585, fails on
its **first exclusion**: the anchor is equally matchable in the indexed body, whose raw term
frequencies are 1, 2 and 1, so the mechanism is term-frequency amplification of an anchor
that already matched. That is a third distinct route to a materially positive title-indexing
condition after D-028 and D-036, and both readings the D-023 rule requires were run, the
semantic one giving 4 / 16.437155. `minimal_preprocessing_score_distortion` is refused the
primary because the defect it names moves the answer hop 0 rank positions gold-targeted and
**-0.024046 points** deployable; its concrete mismatches are carried by
`surface_form_tokenization_mismatch` instead. `generic_term_lexical_crowding` is refused
because the family is name-driven and not category-driven, `celebrity` alone reproducing 5 of
5 of it and the genre facet 0 of 5, which is D-034's test with the outcome reversed.
`plausible_non_gold_answer`, `gold_chain_not_unique` and `gold_chain_substitutability` are
refused on one shared measurement: `space western` occurs in 1 of 4,937 bodies and
`bravestarr` in 2, both of them golds, and `COPS (animated TV series)` contains neither
`space` nor `western`. `description_only_bridge_entity` fails its inclusion rule outright,
the distributor being explicitly named, and the single-factor oracle-name test was run
anyway and failed at 1 / 25.773537 and 7 / 18.769969 and at 19 / 17.987437 and
5 / 35.207124 with both of pit 19g's and pit 24b's premises checked.
`one_sided_entity_crowding` and a compound reading are refused because one family suppresses
both hops, which is pit 19h. `peripheral_passage_content_dilution` is not applicable on a
lexical backend and the gate was not run.

Corpus setting is provenance under D-003 and pit 17, and here it is a **setting-dependent
gold swap**: pooled gives `any@5` 0 and `full@5` 0 with the golds at 8 and 6 while
per-question gives `any@5` 1 and `full@5` 0 with them at 1 and 9, so the two exchange order.
The four cells attribute the swap entirely to `idf`. Restricting the pooled scores to the
item's ten gives 7 / 17.987437 and 6 / 18.769969; rebuilding on those ten gives
1 / 4.781835 and 9 / 1.511055 and reproduces the official window title for title; grafting
pooled `idf` and `avgdl` back reproduces the restricted cell exactly; grafting pooled `idf`
alone, against a per-question `avgdl` of 83.800000 and a pooled 90.884950, leaves the order
unchanged at 7 / 17.387936 and 6 / 18.240251, so **`avgdl` carries none of it**, as at
D-028, D-032, D-033 and D-034. The mechanism is that the ten-passage index floors
`celebrity`, `home` and `entertainment` to 0.403526 and takes `series` and `released` to
0.000000 while `space` and `western` keep 1.845827: the small index destroys the distributor
facet and preserves the genre facet. Of the three paths the added-competitor one is very
weak, 1 of the 6 passages above the answer hop and 0 of the 5 above the constraint hop being
pooling-introduced; the idf-scale path carries the whole flip; and the annotator-supplied
path is strong, 8 of the item's own 10 passages being distributor-related.

### Inventory effect

- The primary inventory is unchanged at **27 distinct names**. The departing name
  `partial_match_constraint_omission` now keeps no current v2 row at all, the treatment given
  to `broad_adaptation_topic_crowding` and `answer_entity_missing_both_methods` at D-037 and
  to `partial_bridge_only` at D-038; the arriving name
  `cross_passage_conjunction_unresolved` was already in the inventory and already the primary
  of five other current rows, so this landing adds no name to either side.
- The secondary-name union is unchanged at **50 distinct names**. The departing secondary
  `distributor_related_document_crowding` had this row as its only holder and is deleted
  rather than registered, so the curated union keeps it as a preserved name in the same way
  the primary inventory keeps deleted primaries; all five arriving secondaries were already
  in the column.
- `case_memos_v2.csv` now holds **96 secondary assignments over 27 distinct names**, up from
  93 over 28: this row went from two descriptors to five, every arriving name occurs
  elsewhere in the column, and the single departing name occurred nowhere else. The distinct
  `primary_open_code` count in v2 falls to **11**, the departing primary having had this row
  as its only one while the arriving one already held five. `case_memos_v1.csv` is unchanged
  at 39 distinct secondary names.
- The registry is unchanged at **26 adopted descriptors**. Eight existing entries are edited
  and none of them gains a definition, inclusion-rule or exclusion-rule change.
  `related_name_document_crowding`, `cutoff_sensitive_near_miss`,
  `surface_form_tokenization_mismatch`, `generic_query_scaffold_score_inflation` and
  `same_topic_passage_distractor` each gain this affected unit and D-039 as a decision
  source. `cross_passage_conjunction_unresolved` gains D-039 as a decision source and a usage
  paragraph but **not** this affected unit, because the project does not list a unit as
  affected when the name is that unit's primary; its note on primary use gains this landing
  as a member and gains back D-031, which the enumeration had omitted, so it runs to six.
  `unindexed_title_name_anchor` and `generic_term_lexical_crowding` each gain D-039
  as a decision source recording a non-adoption, and neither gains an affected unit. No band
  edge moves anywhere in the file.
- `review_status` counts are now 30 `jointly_reviewed` and 0 `needs_joint_review`. Thirty
  rows now carry a populated `candidate_category`.
- Validation progress after D-039 is **26 of 26 validated, 0 remaining**, superseding the
  25-of-26 figure recorded in section 7A.22. **The section 7A gate is closed**: every one of
  the 26 single-note units and all 4 overlap units have been validated, and the merge,
  boundary and freeze work that section 7A blocked may now begin.
- Four vocabulary-audit items are registered by this decision and settled by none of it.
  First, whether pit 19s should be sliced on "supplies no intermediate fact" rather than on
  "non-oracle": one gold-targeted index-side condition here does double-recover, at
  5 / 18.751159 and 1 / 25.187216, while supplying no intermediate fact and doing no
  cross-passage reasoning. Second, whether a crowding descriptor whose query-only definition
  contains a required gold should be excluded from primary use by rule rather than by this
  entry's argument. Third, whether `cutoff_sensitive_near_miss` now needs separate contracts
  for its `any@5` and `full@5` readings, this being the first unit on which both required
  passages qualify. Fourth, whether `unindexed_title_name_anchor`'s first exclusion should be
  stated as a term-frequency test, a materially positive title-indexing condition having now
  been produced by three different mechanisms.

## Section 8 - Vocabulary-audit rulings

The section 7A validation gate closed with D-039, and the questions it deferred are
enumerated in `manual_review_v1/analysis/vocabulary_audit_triage.md` as T-01 to T-63. This
section records the rulings. Each is a consequential change and carries its own D-entry;
items settled without one are marked as such in that file's ruling-status table.

### Section 8.1 - D-040, D-041 and D-042

D-040 restricts the pit 19s refutation path to conditions that are deployable without
knowing which passages are gold, settling T-16. It rules on pit 19s only and explicitly does
not extend to pit 15, where D-037's landed tie-break rests on a gold-targeted condition; that
extension is registered as a new audit item and D-037 stands as written.

D-041 splits the single-factor oracle-name test into a binding exclusion, that a failing test
bars `description_only_bridge_entity` from primary use, and a non-binding inclusion note,
that a passing test supports without establishing. This settles T-01. The evidence is the
eighteen-member series joined to each unit's effective primary: ten failing applications with
the descriptor primary on none of them, and eight passing applications with the descriptor
primary on four.

D-042 gives `cutoff_sensitive_near_miss` a threshold of 5.464 percent below the rank-5 score,
declines to close the never-decided band between 5.464 and 9.431 percent, and writes D-034's
substitutability exception into the entry. This settles T-34.

T-18, the shared primary-use contract for crowding-family descriptors, was ruled on but is
**not** landed here: the owner deferred it pending a fact check on whether D-027's competing
family can be defined by a content rule that does not also select a required passage. It is
reserved as D-043.

### Inventory effect

- The primary inventory is unchanged at **27 distinct names**. No name is created, deleted,
  renamed or merged by these three decisions.
- The secondary-name union is unchanged at **50 distinct names**, for the same reason.
- `case_memos_v2.csv` is not edited. It still holds **96 secondary assignments over 27
  distinct names**, the distinct `primary_open_code` count in v2 is 11, and no row's primary,
  secondary set, `candidate_category` or `taxonomy_defect_flag` changes. `case_memos_v1.csv`
  is unchanged at 39 distinct secondary names.
- `review_status` counts are unchanged at 30 `jointly_reviewed` and 0 `needs_joint_review`.
- The registry is unchanged at **26 adopted descriptors**. Three existing entries are edited
  and none of them gains an affected unit, these decisions reclassifying no unit.
  `cross_passage_conjunction_unresolved` gains D-040 as a decision source and one exclusion
  clause; `description_only_bridge_entity` gains D-041, one exclusion clause and one inclusion
  note; `cutoff_sensitive_near_miss` gains D-042, one inclusion clause and one exclusion
  clause. No definition changes anywhere in the file, and no band edge moves.
- The validation queue is not edited. Progress remains 26 of 26 validated, 0 remaining.
- Three rule-shaped decisions land without a per-case dossier, the first since D-013: they
  reclassify no unit and produce no new conditions, so there is nothing for a dossier to
  hold. The dossier count stays at nineteen.

### Section 8.2 - D-043

D-043 lands the crowding-family primary-use contract T-18 deferred. The fact check the owner
required was run: a content-only rule defining D-027's competing family without selecting a
required passage does exist, and one form of it needs nothing from either required passage, so
the gate has two supporting units rather than one and lands as drafted. D-027 is not
re-judged; its primary, conclusions and confidence are unchanged.

### Inventory effect

- The primary inventory is unchanged at **27 distinct names** and the secondary-name union is
  unchanged at **50 distinct names**. D-043 creates, deletes, renames and merges nothing.
- `case_memos_v2.csv` is not edited and `review_status` counts stay at 30 `jointly_reviewed`
  and 0 `needs_joint_review`. The registry is unchanged at **26 adopted descriptors**; one
  entry, `question_frame_semantic_crowding`, gains D-043 as a decision source and a paragraph,
  and gains no affected unit. No definition, inclusion rule or exclusion rule changes.
- The queue is not edited and the dossier count stays at nineteen.
### Section 8.3 - D-044 to D-048

D-044 and D-045 turn the two preconditions of the single-factor oracle-name test into
conditions on the exclusion clause D-041 made binding, settling T-02 and T-03. A bar and a
usage note are not the same kind of object, and the two preconditions had until now been
applied asymmetrically to the same membership table: a degenerate injection made D-030 not
applicable while D-024, whose injected anchor was matchable by the wrong passage, was
carried as a failure. Both are now conditions on the bar, judged per injected form. D-024's
membership row is not moved; the tension is registered in D-044 instead.

D-046 defines that test's form set and requires per-passage coverage before the bar fires,
settling T-05. A form is one surface form of a required passage's own entity name injected
on its own, which is how D-038's two-anchor double recovery and D-033's injection of a third
party's name were already read without the rule being written down. The passing half stays
existential, because none of the four units where the test passes and this descriptor takes
the primary is a mixed result, so a universal reading would carry nothing the existential
one does not.

D-047 repairs `description_only_bridge_entity`'s definition, which named a backend, settling
T-07. The descriptor is the primary of four units and all four are on the bi-encoder, so the
phrase `for lexical retrieval` excluded every unit on which it is the primary.

D-048 restates `related_name_document_crowding`'s `sharing a name or name token` as a
property of the competing passage's text, settling T-21, and records that this and T-07 are
**not** the same shape, which two handoff passages had said they were. That wording names a
property of text rather than a scorer, and it held literally on both bi-encoder adoptions.

### Inventory effect

- The primary inventory is unchanged at **27 distinct names** and the secondary-name union
  is unchanged at **50 distinct names**. These five decisions create, delete, rename and
  merge nothing.
- `case_memos_v2.csv` is not edited. It still holds **96 secondary assignments over 27
  distinct names**, the distinct `primary_open_code` count in v2 is 11, and no row's
  primary, secondary set, `candidate_category` or `taxonomy_defect_flag` changes.
  `case_memos_v1.csv` is unchanged at 39 distinct secondary names.
- `review_status` counts are unchanged at 30 `jointly_reviewed` and 0 `needs_joint_review`.
- The registry is unchanged at **26 adopted descriptors**. Two entries are edited and
  neither gains an affected unit: `description_only_bridge_entity` gains D-044, D-045,
  D-046 and D-047, one definition change, one scope line, one inclusion sentence and one
  set of conditions on its existing exclusion clause; `related_name_document_crowding`
  gains D-048, one definition restatement and one scope line. **Two definitions change,
  and they are the first definition changes any vocabulary-audit ruling has made**, D-040
  to D-043 having changed none.
- The validation queue is not edited. Progress remains 26 of 26 validated, 0 remaining.
- Five rule-shaped decisions land without a per-case dossier, as D-040 to D-043 did: they
  reclassify no unit and produce no new conditions, so there is nothing for a dossier to
  hold. The dossier count stays at nineteen.

### Section 8.4 - D-049 to D-052

These four settle the first batch of the first wave, the questions about whether a name stays
on the list at all. They are taken in dependency order rather than in triage order.

D-049 writes down the mechanical-separability line the D-028 and D-030 pair implies, settling
T-29. Within the preprocessing vocabulary a distinct descriptor is warranted only when the
implementation choice is a separable pipeline decision, such as which field is indexed, rather
than another value, side, affected passage or instance of the same normalization decision. The
line is scoped to that vocabulary and is deliberately not adopted as a universal naming law,
because the three applications behind it are all lexical and all inside one primary's evidence
base.

D-050 retains `unindexed_title_name_anchor` as an independent provisional secondary rather than
folding it into `minimal_preprocessing_score_distortion`, settling T-30. It is the corollary of
D-049 taken on the side of the line D-028 was on, and it rests additionally on the entry having
a full contract where the receiving primary had none when the fold was put; D-052 gives that
primary one prospective exclusion gate later in the same landing, which narrows that asymmetry
without closing it. The entry's own three questions stay open as T-31, T-32 and T-33.

D-051 gives the preprocessing primary a prospective passage-level reverse boundary, settling
T-28. For a required passage the claim is made about, the exclusion fires if the minimal
gold-targeted normalization changes 0 rank positions or if the corresponding corpus-wide
deployable normalization has a negative score effect. Both cells are needed; an unrun cell is
`not_applicable`. D-039 supplies both halves and splits across its two required passages, which
is why the gate is stated per passage. The deployable zero-effect case and every nonzero
magnitude threshold are left open, one unit supporting neither.

D-052 retains one `minimal_preprocessing_score_distortion` primary, settling T-27. It is not
split by backend and not split into one descriptor per sub-mechanism; the narrowing is done by
D-051's contract instead. The six sub-mechanisms are recorded as an explicit member
enumeration - repeated-function-word amplification, punctuation false negatives, query-scaffold
score inflation, Unicode-dash mismatch, the boundary-punctuation by indexed-field interaction
added by D-028, and the possessive clitic added by D-030 - and future text states that
enumeration rather than an ordinal, the ordinal form being what broke three earlier series.
Five of those members are values of the one normalization decision the primary names; the
D-028 member is enumerated for its boundary-punctuation factor only, its indexed-field factor
being the separable decision D-049 describes and the one D-050 has just kept under
`unindexed_title_name_anchor`. The
name is not added to this project's Provisional Secondary Descriptor Registry, which defines
adopted secondaries; its primary-use contract is carried into `candidate_taxonomy_v0_1.md` at
the categories stage.

### Inventory effect

- The primary inventory is unchanged at **27 distinct names** and the secondary-name union is
  unchanged at **50 distinct names**. These four decisions create, delete, rename and merge
  nothing; T-30 and T-27 are both rulings that a name stays as it is.
- `case_memos_v2.csv` is not edited. It still holds **96 secondary assignments over 27
  distinct names**, the distinct `primary_open_code` count in v2 is 11, and no row's primary,
  secondary set, `candidate_category` or `taxonomy_defect_flag` changes. `case_memos_v1.csv`
  is unchanged at 39 distinct secondary names.
- `review_status` counts are unchanged at 30 `jointly_reviewed` and 0 `needs_joint_review`.
- The registry is unchanged at **26 adopted descriptors**. One entry is edited and it gains no
  affected unit: `unindexed_title_name_anchor` gains D-050 as a decision source and one
  paragraph recording that the fold was considered and refused. **No definition, inclusion
  rule or exclusion rule changes anywhere in the file**, unlike the D-044 to D-048 landing,
  which changed two definitions. No entry is created, and in particular none is created for
  `minimal_preprocessing_score_distortion`, D-052 ruling that this file is not where a pure
  primary belongs.
- The validation queue is not edited. Progress remains 26 of 26 validated, 0 remaining.
- Four rule-shaped decisions land without a per-case dossier, as D-040 to D-048 did: they
  reclassify no unit and produce no new conditions. The dossier count stays at nineteen.
- Two of the four narrow a name's future use without touching its past use. D-051 is
  prospective by its own terms and D-052 narrows by adopting it, so the nine units listed in
  D-052 keep their landed primary and none of them is re-read against the new boundary.

### Section 8.5 - D-053 to D-056

These four settle the second batch of the first wave, the questions about how many names the
list should carry where two shapes overlap. They are taken in the order the owner set, the
three split-and-overlap questions first and the partial-coverage question last.

D-053 retains one `description_only_bridge_entity`, settling T-09. The absent-name property
stays the definition's subject: the name is neither split into an absent-name descriptor and an
unusable-anchor descriptor, nor widened to a required entity the question names explicitly but
ineffectively. A prospective boundary and routing note is added instead, sending a surface-form
failure to `surface_form_tokenization_mismatch`, an alias or reference failure to
`entity_alias_reference_mismatch`, a homonym to `proper_name_homonym_collision`, and a
passage-composition explanation to `peripheral_passage_content_dilution` only where that
entry's four inclusion conditions hold. Where no route carries it, a named-but-ineffective
anchor is recorded as a measured fact of the unit without a descriptor being coined. The entry
does **not** rule that a future residual can never warrant a name.

D-054 retains one `question_frame_semantic_crowding` and gives it no primary-use contract of
its own, settling T-19. Standing in both inventories is two strengths of one body of evidence
rather than two mechanisms, so D-043's shared crowding contract governs the primary use
together with the entry's own inclusion rule and exclusion clause. The stale sentence in the
entry's note on primary use, which still called this an open audit question, is replaced. The
ruling is a precedent for T-10 by analogy only, and T-10 stays open.

D-055 keeps `same_topic_passage_distractor` and `generic_term_lexical_crowding` apart, settling
T-24, and writes the passage-level boundary into both entries: a verified connection in the
passage body together with a verified missing decisive constraint routes a passage to the first
name, and broad category, institutional or relational vocabulary without that connection routes
it to the second. Different passage subsets within one unit may take the two descriptors; one
passage set may not take both. No route to `question_frame_semantic_crowding` is added, which
would make the boundary three-way and reach into T-19 and T-26.
`related_name_document_crowding` is not folded in either: D-048's sentence identifying its
overlap with `same_topic_passage_distractor` as T-24 is an incorrect cross-reference, D-048
stands as written under red line 4, and that overlap is opened as a separate triage item, T-62,
and left unresolved.

D-056 keeps the partial coverage of the neighbourhood D-023 recorded, settling T-23. The name
is not widened, no Dense-only same-domain descriptor is coined, and D-023 is neither
reclassified nor given an added secondary. What is added is a prospective evidence-recording
rule: where a dossier or an entry claims that a competing family has been enumerated and the
adopted descriptors cover only part of it, the uncovered members must be identified explicitly
in that dossier, so that silence is never read as coverage. That is a rule about recording
evidence and not a requirement that every high-ranked passage carry a descriptor.

The order puts D-055 before D-056 so that the same-topic against generic-term boundary is
explicit before partial coverage is reaffirmed. That is a property of the record and not of the
evidence: D-056 re-analyses nothing and does not read D-023's uncovered half against the
boundary D-055 states.

### Inventory effect

- The primary inventory is unchanged at **27 distinct names** and the secondary-name union is
  unchanged at **50 distinct names**. These four decisions create, delete, rename and merge
  nothing; T-09, T-19, T-24 and T-23 are all rulings that the names stay as they are.
- `case_memos_v2.csv` is not edited. It still holds **96 secondary assignments over 27
  distinct names**, the distinct `primary_open_code` count in v2 is 11, and no row's primary,
  secondary set, `candidate_category` or `taxonomy_defect_flag` changes. `case_memos_v1.csv`
  is unchanged at 39 distinct secondary names.
- `review_status` counts are unchanged at 30 `jointly_reviewed` and 0 `needs_joint_review`.
- The registry is unchanged at **26 adopted descriptors**. Five entries are edited and none of
  them gains an affected unit: `description_only_bridge_entity` gains D-053, one paragraph and
  one prospective boundary-and-routing bullet; `question_frame_semantic_crowding` gains D-054,
  one paragraph and one replaced sentence inside its note on primary use;
  `same_topic_passage_distractor` and `generic_term_lexical_crowding` each gain D-055, one
  paragraph and one boundary bullet; `generic_person_semantic_neighborhood` gains D-056 and one
  paragraph. **No definition, inclusion rule or exclusion clause changes anywhere in the
  file**, as in the D-049 to D-052 landing and unlike D-044 to D-048, which changed two
  definitions. The three new boundary bullets sit beside the four rule bullets without
  altering any of them, which is the shape this file already uses for a `Scope`, a
  `Note on primary use` and an `Attribution boundary` bullet.
- The validation queue is not edited. Progress remains 26 of 26 validated, 0 remaining.
- Four rule-shaped decisions land without a per-case dossier, as D-040 to D-052 did: they
  reclassify no unit and produce no new conditions. The dossier count stays at nineteen.
- One triage item is opened rather than ruled on: the overlap between
  `related_name_document_crowding` and `same_topic_passage_distractor`, recorded as T-62. That
  is a repair to the triage record forced by an incorrect cross-reference in append-only
  D-048, and it is not a ruling on the overlap, so the item count in
  `vocabulary_audit_triage.md` rises by one while the ruled count rises by four.
- Three known synchronization differences are confirmed and deliberately left unrepaired: the
  affected-unit lists of `generic_term_lexical_crowding`, `gold_chain_substitutability` and
  `description_only_bridge_entity` each omit `5adc8977554299438c868de2|bm25`, which
  `case_memos_v2.csv` carries. All three belong to the third batch under item T-55, and
  repairing one of them inside this landing would be the silent correction section C forbids.

### Section 8.6 - D-057 to D-060

These four settle the third batch of the first wave: the naming defects, the one
row-against-registry difference the project had deliberately left unrepaired, and whether the
vocabulary needs a question-quality name at all. They are taken in the order the owner set.
The row synchronization lands first so that the flag rulings have a settled name to speak
about, then the two flags, then the rename, then the question-quality ruling.

D-057 brings `5a78b209554299148911f93e|bm25` into agreement with D-010, settling T-50. Its
`primary_open_code` becomes `entity_name_tokenization_mismatch`, which the row already carried
in `candidate_category`; `cross_entity_token_recombination` joins the secondary set and
`missing_second_comparison_entity` leaves it, D-010 having adopted the first and not retained
the second. Section 7.2 of this file had classed the difference as a synchronization
discrepancy rather than a semantic decision and deferred it to the validation workflow, which
closed at 26 of 26 with D-039; section C of `taxonomy_todo.md` forbade correcting it silently
rather than correcting it at all. The departing name states gold missingness, which pit 17 and
D-003 forbid as a causal category and on which D-034 deleted `general_answer_passage_missing`,
and D-027 declined it on the Dense side of the same example because both required passages
were retrieved at 8 and 9. No evidence is re-read and no condition is re-run.

D-058 clears the two remaining `taxonomy_defect_flag=true` rows, settling T-49, and changes no
other cell of either. On `5a7d61775542991319bc93b9|bm25` the flag's stated ground has been
filled: D-012 set it because the vocabulary lacked a general category covering both
function-word score amplification and punctuation-sensitive false-negative matching, and
D-052's retained `minimal_preprocessing_score_distortion` opens its member enumeration with
exactly those two, with this row the first of the nine units it counts. On
`5a78b209554299148911f93e|bm25` the flag asked whether the mechanism should stay separate or
merge into a broader lexical-cue category, and the merge is neither performed nor refused: it
is left prospective under D-051's contract, which requires a gold-targeted repair's rank
positions and the sign of its deployable version on each required passage, two cells this unit
does not have and will not acquire in a phase that runs no measurement. D-049's separability
line, read on its face, points at merging, but it is scoped and prospective and using it to
overturn a ruling landed on 2026-07-31 would be the re-judgment red line 4 forbids; the
separable decision this unit does contain, that titles are not indexed, already has a name in
`unindexed_title_name_anchor`, which D-050 kept outside the primary. The never-written boundary
between `entity_name_tokenization_mismatch` and the registered
`surface_form_tokenization_mismatch` is opened as a triage item rather than ruled on.

D-059 renames the primary `quoted_phrase_semantic_drift` to `verbatim_epithet_sense_drift`,
settling T-48. The old name asserts two things D-020's own conditions exclude: condition A
removes the quotation marks and is inert in both directions, 465 / 0.112206 to 479 / 0.111678
and 13 / 0.317347 to 12 / 0.318517, and the backend performs no literal string matching at all.
What the conditions support is a sense drift, and two of them are not oracle: probe D makes the
query exactly the verbatim epithet and the one passage that literally contains it reaches
106 / 0.219506 behind a religious, mythological and death-related neighbourhood, while probe E
replaces the epithet with the plain noun `dwellings` and the required answer passage moves from
13 / 0.317347 to 5 / 0.366752. This is the naming-against-mechanism repair D-019 performed on
`same_topic_title_distractor`, the precedent D-020 itself cites. Three alternatives are refused
on the evidence: a usage note beside the old name, on D-047's ground that a note cannot stop a
defective name reaching a candidate category; reuse of `literal_cue_topic_capture`, which D-014
judged an output-level description and which has no inclusion or exclusion rule to inherit; and
a fold into `exact_string_source_dependency`, which is adopted on this same unit for the source
hop only and would leave probe E's half with no carrier, the shape D-056's recording rule
exists to make visible. The rename reaches the two label fields and replaces the name in the
row's three prose fields with a note recording the change; no measurement, interpretation,
tie-break, confidence or conclusion of D-020 changes, and `case_memos_v1.csv` is not touched.

D-060 rules that no descriptor naming a defect, ambiguity or underspecification of the question
is adopted in either inventory, settling T-52. The candidate names for such a category have
been coined twice and deleted twice, each time after a complete factorial and each time on
pit 17. D-034 deleted `question_wording_ambiguity` after a sixteen-cell factorial in which its
effect on the bridge passage was exactly zero in both preprocessing states while its one
grammatically correct component was the worst cell on the other passage. D-036 deleted
`underdetermined_question` after a full A by B by C factorial run in two preprocessing states,
in which all 8 oracle cells placed both required passages inside the cutoff and all 8
non-oracle cells failed, in both states, and recorded that what the name carried is already
carried, with a passage behind it, by `gold_chain_not_unique`; pits 19k and 19ah were satisfied
in both entries before the verdict was read. D-025 supplies the third shape, a verified
factual error in the question, measured and found not decisive at 115 to 102 and at 5
against 3, with no descriptor adopted for it. The ruling therefore routes rather than names: a
passage inside the cutoff satisfying every explicit constraint to `plausible_non_gold_answer` or
`gold_chain_not_unique`, an annotated chain with a substitute to `gold_chain_substitutability`,
a described rather than named target to `description_only_bridge_entity` under D-053's own four
routes, and a question wording differing from the corpus wording to
`surface_form_tokenization_mismatch` or `entity_alias_reference_mismatch`. A residue no route
carries is recorded as a measured fact without a name, which is what D-025 did and what D-053
states as the general treatment. `possible_type_mismatch` is untouched, describing a passage's
type rather than the question's quality. Section 12 of `taxonomy_todo.md` is corrected in the
same landing, its intake list still collecting the two deleted names; this is the class of
planning gap D-052 found in section 8 and it is repaired here because this ruling is what
determines the list. It is not ruled that such a name may never be warranted in future.

The three synchronization differences D-055 confirmed and left unrepaired are repaired in this
landing under item T-55: the affected-unit lists of `generic_term_lexical_crowding`,
`gold_chain_substitutability` and `description_only_bridge_entity` each gain
`5adc8977554299438c868de2|bm25`, which `case_memos_v2.csv` carries and which D-034 adopted on
all three. D-034 was already a decision source on each entry, so this adds no decision source
and no prose beyond correcting the one present-tense sentence in
`generic_term_lexical_crowding` that said the omission was still outstanding. It consumes no
decision ID, on the precedent T-57 to T-60 set. No tool checks these enumerations, which is
what item T-55 records, so the three lists were compared against the memo row by hand.

### Inventory effect

- The primary inventory is now **28 distinct names**, up from 27. The arriving name is
  `verbatim_epithet_sense_drift` and the departing name `quoted_phrase_semantic_drift` is item
  20 and stays as a historical first-pass name in `case_memos_v1.csv`, the treatment D-019 gave
  `same_topic_title_distractor`. This is the first entry in this inventory to change by rename
  rather than by coinage, promotion or deletion.
- The secondary-name union is unchanged at **50 distinct names**. The departing name
  `missing_second_comparison_entity` is item 28 of the union and now keeps no current
  `case_memos_v2.csv` row at all, this having been its only one; it remains in the union as a
  historical first-pass name, the treatment given to `question_wording_ambiguity` at D-034 and
  to `underdetermined_question` at D-036.
- `case_memos_v2.csv` now holds **96 secondary assignments over 26 distinct names**, unchanged
  in total and down from 27 distinct: one row exchanged one secondary for another that already
  occurred elsewhere in the column, and the departing name was unique to that row. The distinct
  `primary_open_code` count in v2 is **12**, up from 11, because
  `entity_name_tokenization_mismatch` enters the column for the first time while
  `one_sided_entity_crowding` falls from three rows to two and stays, and the rename replaces
  one name with one name. `case_memos_v1.csv` is unchanged at 39 distinct secondary names and
  is not edited.
- The derived union of primary names over the two CSVs rises from 26 to **28** and now equals
  the curated inventory. The two had differed by one because
  `entity_name_tokenization_mismatch` lived only in `candidate_category`; D-057 puts it in the
  column and D-059's arriving name
  enters both counts, so the difference closes as a consequence of the rulings and not by any
  adjustment to either figure.
- `review_status` counts are unchanged at 30 `jointly_reviewed` and 0 `needs_joint_review`.
- Three memo rows are edited and no other row is touched. `taxonomy_defect_flag` is now `false`
  on all 30 rows, down from 3 `true`, D-058 clearing two and D-059 the third, whose flag had
  been set for this rename and for nothing else.
- The registry is unchanged at **26 adopted descriptors**. No entry is created or deleted and
  no definition, inclusion rule or exclusion rule changes anywhere in the file, as in the
  D-049 to D-052 and D-053 to D-056 landings. Three entries gain one affected unit each, which
  is the T-55 repair and not an adoption by any of these four decisions; one sentence in
  `generic_term_lexical_crowding` is corrected because it stated that omission as outstanding.
- The validation queue is not edited. Progress remains 26 of 26 validated, 0 remaining. Its
  row 7 still shows `quoted_phrase_semantic_drift`, which that file's own header declares to be
  a provisional snapshot copied from `case_memos_v2.csv` whose presence there validates
  nothing; the snapshot is recorded as stale rather than refreshed, since the workflow it
  indexes closed with D-039.
- Four decisions land without a per-case dossier, as D-040 to D-056 did. Three of them edit
  memo cells only and one is a pure rule; none produces a new condition, and the dossier count
  stays at nineteen.
- One triage item is opened rather than ruled on: the boundary between
  `entity_name_tokenization_mismatch` and `surface_form_tokenization_mismatch`, recorded as
  T-63. Opening an item repairs the record rather than deciding anything, so it carries no
  decision ID, on the precedent D-055 set with T-62. The item count in
  `vocabulary_audit_triage.md` therefore rises by one while the ruled count rises by four.

### Section 8.7 - D-061

This one settles the pre-`categories` intake reconciliation that section D of `taxonomy_todo.md`
registered as a process step when D-049 to D-052 landed. It is not part of the first wave's
three batches and it settles no triage item; what it settles is the input the categories stage
will be built from.

D-061 aligns the intake lists of sections 8 to 13 with the effective vocabulary. Twelve
collection lines are removed because no unit carries their names any longer, each one a
consequence of the decision that re-coded the carrying unit rather than a new ruling, and no
successor name is written in place of any of them. All 34 distinct effective names, held as 12
primary roles and 26 secondary roles over the 30 rows of `case_memos_v2.csv`, are assigned a
section in which each must be considered, with four names holding both roles and taking the same
section in each. Section 8A, `Retriever Implementation Artifacts`, is opened for the
retriever-implementation family under a preamble, landed in that section's own first paragraph,
stating that it is an intake workstream and not a sixth candidate category. An assignment states
where a name is considered and states nothing about whether it warrants a category, a merge, or
a place in `candidate_taxonomy_v0_1.md`.

The gap this repairs was visible twice before it was measured. D-052 found that section 8's
intake omitted `minimal_preprocessing_score_distortion`, the largest primary in the column, and
D-060 repaired section 12's list in its own landing because its ruling was what determined that
list. The full check finds the same shape over 22 names, of which 5 appear in sections 8 to 13
only in prose and 17 do not appear at all, and finds that half of the 24 collection lines then
present named a name no unit carries. Sections 8 to 13 were written before open coding, which is
the whole of the explanation; the omission is a planning gap and not evidence that any omitted
name is unworthy of a category, and neither reading is adopted here.

Three placements carried more than a table cell. `entity_name_tokenization_mismatch` goes to
section 8A with a cross-reference from section 9, which does not merge it with
`surface_form_tokenization_mismatch` or with the preprocessing primary; T-63's boundary stays
open and D-058's fold stays prospective on D-051's two cells. `compound_two_sided_crowding`
stays in section 13, where the existing first item already collects units carrying two or more
independent mechanisms, which is what D-018 found on that unit; section 10 was weighed and
refused because it would assert the name to be a unitary crowding-category candidate, which
D-018 did not rule. `verbatim_epithet_sense_drift` goes to section 10 because D-059 measures the
mechanism as semantic sense-neighbourhood drift, with section 8 cross-referenced for the
co-descriptor `exact_string_source_dependency`, which carries the source hop only.

The entry carries one wording constraint over itself and over sections 8 to 13: neither the
mechanism nor `verbatim_epithet_sense_drift` may be described as literal, exact-string, phrase
or surface matching, because the backend is a symmetric bi-encoder over L2-normalized
whole-passage dot products and performs no string matching at all. Stating that a query cue is
verbatim, or that a passage literally contains a string, stays legal as an observed input or
corpus fact, and the four terms stay legal on `exact_string_source_dependency`, whose registry
definition does rest on literal surface overlap for the source hop. The constraint is about
attribution rather than vocabulary. It is recorded because an earlier draft of the same routing
asserted the opposite and sent the primary to section 8 on a ground the decision it cited had
already excluded.

Four questions are recorded as open rather than settled: section 10's `Near-Neighbor` heading
against the three readings of neighbourhood it now collects, D-055's passage-level boundary now
being discussed in two sections, section 8's three prose judgement lines naming retired
mechanisms, and section 12's heading still reading `Question or Evaluation Ambiguity` after
D-060 required the category to be written on the evaluation side. None of them blocks the stage
switch.

One figure in the working intake check written alongside this decision is corrected in the entry
rather than in that document, which is untracked: it reports 18 effective names absent from
sections 8 to 13 entirely, and the correct figure is 17. A snake_case scan does return 18, but
section 9 carries `low_context_name_query` in a prose judgement line asking whether it is an
independent mechanism, which that scan missed. The name is still uncollected and still gains a
collection line; only the absent-entirely claim was wrong.

### Inventory effect

- The primary inventory is unchanged at **28 distinct names** and the secondary-name union is
  unchanged at **50 distinct names**. This decision creates, deletes, renames and merges
  nothing; it moves no name between the two inventories and changes no name's spelling.
- `case_memos_v2.csv` is not edited. It still holds **96 secondary assignments over 26 distinct
  names**, the distinct `primary_open_code` count in v2 is still 12, and `case_memos_v1.csv` is
  unchanged at 39 distinct secondary names. `review_status` counts are unchanged at 30
  `jointly_reviewed` and 0 `needs_joint_review`. The 12, the 26 and the 34 this entry tabulates
  are read out of that file and are not written into it.
- The registry is unchanged at **26 adopted descriptors**. No entry is created or deleted, no
  affected-units list gains or loses a unit, and no definition, inclusion rule or exclusion rule
  changes anywhere in the file. The registry's 26 entries were verified equal, in both
  directions, to the 26 distinct secondaries `case_memos_v2.csv` carries, with no registry-only
  and no v2-only name; that check is evidence for the routing table's completeness and changed
  nothing in either file.
- The validation queue is not edited. Progress remains 26 of 26 validated, 0 remaining, and its
  row 7 still shows `quoted_phrase_semantic_drift`, recorded as a known stale snapshot at D-059
  and still not refreshed here.
- The dossier count stays at **nineteen**. This decision produces no condition, no measurement
  and no dossier, as D-040 to D-056 and D-060 did not.
- Sections 8 to 13 of `taxonomy_todo.md` are the file this decision does change. Their
  collection lines go from **24 to 32**: twelve are removed and twenty are added. By section the
  counts move 5 to 3 for section 8, 0 to 9 for the new section 8A, 4 to 5 for section 9, 5 to 9
  for section 10, 6 to 2 for section 11, and 4 to 4 for section 12. Section 13 gains no
  collection line because it collects rules rather than cases; its two assigned names are
  recorded there in a routing note. Eight cross-references are added, each pointing from one
  section to a name whose home is another. No section heading is changed and no existing
  judgement line is removed.
- Section 8A is the first section added to `taxonomy_todo.md` since 7A, and it follows 7A's
  numbering precedent so that sections 9 to 26 are not renumbered. Nine distinct names are
  routed to it. Its heading verb is to collect mechanisms rather than to establish candidate
  categories, which is what every section from 8 to 12 opens with, and that is deliberate: the
  heading must not promise a category that only the categories stage can grant.
- **No triage item is settled.** D-061 is the first entry in the vocabulary-audit series D-040
  to D-061 that rules on no item of `vocabulary_audit_triage.md`, the twenty-one before it
  having settled twenty-one items between them. That file is therefore not edited, and its
  counts stand unchanged at 21 items ruled, 4 settled without a D-entry, 37 open, over 62 items.
  The intake reconciliation was registered in section D of `taxonomy_todo.md` as a process step
  rather than as a triage item, and it keeps that provenance.
- `$STAGE` is **not** advanced. It remains `audit-rulings`. Recording that the intake is now
  aligned, and switching the stage to `categories`, are the next steps and are deliberately not
  part of this landing.
