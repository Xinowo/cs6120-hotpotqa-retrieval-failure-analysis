---
status: draft
last_updated: 2026-08-07
---

# Single-Note Validation Queue

## Purpose

This queue controls the section 7A validation pass over the 26 single-note
analytical units. It is a workflow index, not a taxonomy, decision log, or
source of final labels.

The order places the 13 Jiajun-only units first, followed by the 13 Xin-only
units. Within each group, source CSV order is preserved. Current primary and
secondary values are provisional snapshots copied from `case_memos_v2.csv`;
their presence here does not validate them.

## Validation contract

For each unit, use
`references/reusable_retrieval_failure_review_playbook.md` and the applicable
BM25 or Dense implementation reference. Review the complete original note,
question, both gold passages, actual target distractor passage texts, and
comparison evidence. Keep observed evidence, verified implementation facts,
supported interpretation, and speculation separate.

Allowed queue states:

- `not_started`
- `in_review`
- `validated_retained`
- `validated_revised`
- `boundary_flagged`
- `unresolved`

Queue state does not replace `case_memos_v2.review_status` or a required
decision-log entry.

## Queue

| # | Example ID | Retriever | Note source | Type | Current provisional primary | Current provisional secondary | Status |
|---:|---|---|---|---|---|---|---|
| 1 | 5a7c9f325542990527d554e6 | bm25 | Jiajun-only | bridge | minimal_preprocessing_score_distortion | repeated_content_word_amplification; surface_form_tokenization_mismatch; technical_topic_crowding; gold_chain_substitutability | validated_revised |
| 2 | 5a7d19d85542995ed0d165e8 | dense | Jiajun-only | bridge | same_entity_variant_crowding | gold_chain_substitutability | validated_revised |
| 3 | 5a83a532554299334474606f | bm25 | Jiajun-only | bridge | minimal_preprocessing_score_distortion | surface_form_tokenization_mismatch; repeated_function_word_amplification; generic_term_lexical_crowding | validated_revised |
| 4 | 5a85cead5542991dd0999ea9 | dense | Jiajun-only | bridge | description_only_bridge_entity | cross_passage_conjunction_unresolved; possible_type_mismatch | validated_revised |
| 5 | 5a8d93ad554299653c1aa13d | dense | Jiajun-only | comparison | compound_two_sided_crowding | proper_name_homonym_collision; answer_property_semantic_crowding | validated_revised |
| 6 | 5ab72a025542992aa3b8c7b8 | bm25 | Jiajun-only | comparison | minimal_preprocessing_score_distortion | surface_form_tokenization_mismatch; generic_query_scaffold_score_inflation; same_topic_passage_distractor | validated_revised |
| 7 | 5ab978855542996be2020512 | dense | Jiajun-only | bridge | quoted_phrase_semantic_drift | exact_string_source_dependency; cross_passage_conjunction_unresolved; question_frame_semantic_crowding | validated_revised |
| 8 | 5ac1a3665542994ab5c67daf | bm25 | Jiajun-only | bridge | minimal_preprocessing_score_distortion | surface_form_tokenization_mismatch; generic_query_scaffold_score_inflation; description_only_bridge_entity; entity_alias_reference_mismatch; generic_term_lexical_crowding | validated_revised |
| 9 | 5ade42b55542992fa25da717 | bm25 | Jiajun-only | bridge | cross_passage_conjunction_unresolved | description_only_bridge_entity; surface_form_tokenization_mismatch; generic_term_lexical_crowding; repeated_content_word_amplification; repeated_function_word_amplification; cutoff_sensitive_near_miss | validated_revised |
| 10 | 5ade69e455429975fa854ec5 | dense | Jiajun-only | bridge | description_only_bridge_entity | peripheral_passage_content_dilution; gold_chain_substitutability; generic_person_semantic_neighborhood; cutoff_sensitive_near_miss | validated_revised |
| 11 | 5ae057fd55429945ae959328 | bm25 | Jiajun-only | bridge | cross_passage_conjunction_unresolved | description_only_bridge_entity; generic_term_lexical_crowding | validated_revised |
| 12 | 5ae0a59a55429945ae9593e2 | dense | Jiajun-only | bridge | cross_passage_conjunction_unresolved | description_only_bridge_entity; question_frame_semantic_crowding; gold_chain_substitutability; cutoff_sensitive_near_miss | validated_revised |
| 13 | 5ae1f596554299234fd04372 | dense | Jiajun-only | bridge | description_only_bridge_entity | peripheral_passage_content_dilution; cutoff_sensitive_near_miss | validated_revised |
| 14 | 5a78b209554299148911f93e | dense | Xin-only | comparison | one_sided_entity_crowding | related_name_document_crowding; peripheral_passage_content_dilution | validated_revised |
| 15 | 5a79b7f6554299029c4b5f6f | bm25 | Xin-only | bridge | minimal_preprocessing_score_distortion | surface_form_tokenization_mismatch; unindexed_title_name_anchor; generic_term_lexical_crowding; description_only_bridge_entity | validated_revised |
| 16 | 5a81ebee554299676cceb16d | dense | Xin-only | bridge | question_frame_semantic_crowding | peripheral_passage_content_dilution; description_only_bridge_entity; generic_person_semantic_neighborhood | validated_revised |
| 17 | 5a83880e554299123d8c214e | bm25 | Xin-only | bridge | minimal_preprocessing_score_distortion | surface_form_tokenization_mismatch; generic_term_lexical_crowding | validated_revised |
| 18 | 5ab48c325542996a3a969f93 | dense | Xin-only | bridge | cross_passage_conjunction_unresolved | description_only_bridge_entity; related_name_document_crowding | validated_revised |
| 19 | 5ab8f57b5542991b5579f097 | bm25 | Xin-only | comparison | one_sided_entity_crowding | related_name_document_crowding; cutoff_sensitive_near_miss | validated_revised |
| 20 | 5abcc96c5542996583600492 | bm25 | Xin-only | bridge | minimal_preprocessing_score_distortion | surface_form_tokenization_mismatch; related_name_document_crowding; generic_term_lexical_crowding; generic_query_scaffold_score_inflation | validated_revised |
| 21 | 5adc8977554299438c868de2 | bm25 | Xin-only | bridge | minimal_preprocessing_score_distortion | surface_form_tokenization_mismatch; generic_term_lexical_crowding; repeated_function_word_amplification; gold_chain_substitutability; description_only_bridge_entity | validated_revised |
| 22 | 5add67915542992200553af8 | dense | Xin-only | bridge | description_only_bridge_entity | peripheral_passage_content_dilution; generic_person_semantic_neighborhood; same_topic_passage_distractor | validated_revised |
| 23 | 5adf58f15542993a75d264d2 | bm25 | Xin-only | bridge | plausible_non_gold_answer | gold_chain_not_unique; surface_form_tokenization_mismatch; generic_term_lexical_crowding; cross_entity_token_recombination; description_only_bridge_entity; cutoff_sensitive_near_miss | validated_revised |
| 24 | 5ae048a255429924de1b708e | dense | Xin-only | bridge | peripheral_passage_content_dilution | question_frame_semantic_crowding | validated_revised |
| 25 | 5ae1801955429901ffe4aec4 | dense | Xin-only | bridge | cross_passage_conjunction_unresolved | peripheral_passage_content_dilution; cutoff_sensitive_near_miss; same_topic_passage_distractor | validated_revised |
| 26 | 5ae60426554299546bf83019 | bm25 | Xin-only | bridge | cross_passage_conjunction_unresolved | related_name_document_crowding; cutoff_sensitive_near_miss; surface_form_tokenization_mismatch; generic_query_scaffold_score_inflation; same_topic_passage_distractor | validated_revised |

## Queue integrity

- Total rows: 26.
- Unique analytical units: 26.
- Jiajun-only rows: 13.
- Xin-only rows: 13.
- Initial `not_started` rows: 26; current state is tracked in the queue table.
- Validated and revised rows: 26.
- In-review rows: 0.
- Remaining `not_started` rows: 0.
- Duplicate units: 0.

## Recorded corrections

- D-026 corrected row 12 to match `case_memos_v2.csv`, D-025, the registry and
  the audit. That row still carried its pre-validation provisional primary and
  secondary values after D-025 landed. As the Purpose section above states, the
  two columns are snapshots copied from `case_memos_v2.csv`, so this was a
  transcription omission rather than a semantic change; it is recorded here and
  in D-026 rather than applied silently.
