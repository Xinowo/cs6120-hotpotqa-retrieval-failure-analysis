---
status: draft
last_updated: 2026-08-12
---

# Provisional Open-Code Decision Log

This is an append-only record for consequential decisions made while deriving
the taxonomy from the completed notes. Append new entries with the next ID.
Do not silently rewrite earlier decisions; supersede them with a later entry
that identifies the affected decision.

## D-001 — Preserve raw notes as primary evidence

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Treat `xin_notes.csv` and `jiajun_notes.csv` as immutable
  primary evidence.
- **Rationale:** Later interpretation must not silently rewrite the
  observations from which the taxonomy is derived.
- **Affected units:** all 30.

## D-002 — Use a unit key and preserve overlap notes

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Use `(run_id, example_id, retriever)` as the analytical unit
  key and preserve both notes for the four overlap units.
- **Rationale:** This produces 30 analytical units from 34 review actions
  without double-counting overlap.
- **Affected units:** all 30, especially the four overlap units.

## D-003 — Do not treat rank patterns as causes

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Keep gold ranks, missingness, and cutoff status as observable
  retrieval structure, not open-code causes.
- **Rationale:** These fields describe where evidence appeared but do not
  explain why it was ranked there.
- **Affected units:** all 30.

## D-004 — Permit compound open coding

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Allow one primary open code plus multiple secondary
  descriptors during constant comparison.
- **Rationale:** Several units expose compound mechanisms. Forcing one final
  category before boundary analysis would hide evidence.
- **Affected units:** all 30.

## D-005 — Separate evaluation ambiguity from retriever defects

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Keep plausible non-gold answers and question ambiguity
  analytically separate from ordinary retriever-defect mechanisms.
- **Rationale:** A defensible alternative answer or underdetermined question
  changes the evaluation contract.
- **Motivating units:** `5a83aaeb5542996488c2e483|dense` and
  `5adf58f15542993a75d264d2|bm25`, with additional ambiguity candidates retained
  for boundary review.

## D-006 — Treat cutoff sensitivity as secondary

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Use `cutoff_sensitive_near_miss` only as a secondary descriptor
  in this first pass.
- **Rationale:** Proximity to rank 5 records fragility but is not itself a
  causal explanation.
- **Affected units:** all near-cutoff units.

## D-007 — Do not report first-pass counts as prevalence

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Do not interpret open-code counts as final taxonomy frequencies
  or population prevalence.
- **Rationale:** The vocabulary is provisional, partly multi-label, and derived
  from a bounded calibration corpus.
- **Affected units:** all 30.

## D-008 — Do not freeze `taxonomy_v1` from this pass alone

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Require owner review, constant comparison, clustering, and
  boundary stress-testing before taxonomy freeze.
- **Rationale:** This artifact is an evidence-preserving first pass, not joint
  approval of stable categories.
- **Affected units:** all 30.

## D-009 — Separate two-sided entity under-prioritization from semantic-neighborhood description

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a76387d554299109176e6ba|dense`, retain
  `two_named_entities_underprioritized` as the primary open code. Treat
  `generic_person_semantic_neighborhood` as the closest competing secondary
  description and `low_context_name_query` as an alternative explanation.
- **Evidence:** Dense ranks `Am Rong` at 26 and `Ava DuVernay` at 27. Its top
  results emphasize generic person and birth-related content, including a
  `Despoina` passage containing the relation "born first." BM25 retrieves
  `Ava DuVernay` at 1 and `Am Rong` at 3.
- **Rationale:** The evidence is consistent with Dense overemphasizing broad
  person- and birth-order semantics—especially "born" and "born first"—while
  underweighting the two exact entity names. The two-sided entity code captures
  the observed failure; the generic semantic neighborhood describes the
  competing results. The retrieved ranking does not establish which internal
  embedding or scoring component caused the ordering.
- **Affected unit:** `5a76387d554299109176e6ba|dense`.
## D-010 — Prefer entity-name tokenization mismatch over one-sided crowding

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a78b209554299148911f93e|bm25`, use
  `entity_name_tokenization_mismatch` as the candidate primary mechanism.
  Retain `cross_entity_token_recombination` and
  `related_name_document_crowding` as secondary descriptors, with
  `one_sided_entity_crowding` as the closest competitor.
- **Implementation evidence:** The reviewed BM25 implementation indexes
  paragraph text but not titles and tokenizes queries and documents with
  lowercase whitespace splitting only. It has no punctuation normalization,
  phrase matching, entity boundaries, or initial expansion.
- **Case evidence:** Query tokens include `j.`, `m.`, and `barrie?`, while
  the J. M. Barrie gold text contains `james`, `matthew`, and `barrie,`.
  The unindexed title cannot repair this mismatch. `J. Edward Snyder` at rank
  15 instead matches `j.` from one queried entity and `edward` from the
  other. Albee-related documents occupy ranks 1–8.
- **Rationale:** Title exclusion and the exact name-form mismatch provide a more
  specific implementation-supported mechanism than crowding alone. The Albee
  cluster is retained as a downstream ranking effect, not treated as the most
  specific primary cause.
- **Taxonomy effect:** Mark `taxonomy_defect_flag=true` until vocabulary audit
  decides whether this mechanism should remain separate or merge into a broader
  lexical-cue category.
- **Reference:** `references/bm25_implementation_reference.md`.
- **Affected unit:** `5a78b209554299148911f93e|bm25`.
## D-011 — Treat `Graduation` as a complete alternative answer

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a83aaeb5542996488c2e483|dense`, use
  `plausible_non_gold_answer` as the candidate primary mechanism. Use
  `same_artist_work_crowding`, `gold_chain_not_unique`, and
  `cutoff_sensitive_near_miss` as secondary descriptors.
- **Evidence:** Dense ranks `Graduation (album)` first and the annotated golds
  `My Beautiful Dark Twisted Fantasy` and `Power (Kanye West song)` at 6 and 7.
  The `Graduation` passage identifies a Kanye West studio album released
  through Roc-A-Fella Records and includes Dwele among its guest contributors.
  Per-question Dense results also rank `Graduation` first, proving that it was
  one of the item's original eight HotpotQA distractors rather than a passage
  introduced only by pooling 500 questions.
- **Rationale:** Under the same interpretation of the Roc-A-Fella relation used
  by the annotated gold chain, `Graduation` satisfies all explicit question
  constraints in one passage. The annotated supporting-fact chain is therefore
  not unique, and the metric's gold-title miss does not establish a practical
  answer-retrieval failure.
- **Closest competitor:** `same_artist_work_crowding` explains why other Kanye
  West albums rank above the annotated golds, but it cannot invalidate the
  complete `Graduation` answer.
- **Secondary descriptor definitions:**
  - `same_artist_work_crowding`: multiple non-answer works by the same creator
    rank above the annotated gold; exclude any work that independently satisfies
    the complete question.
  - `gold_chain_not_unique`: a concrete alternative passage or chain satisfies
    the question under the same evidentiary standard as the annotated gold.
  - `cutoff_sensitive_near_miss`: annotated gold evidence lies just below the
    cutoff and records metric fragility, not a causal mechanism.
- **Excluded descriptor:** Do not assign
  `cross_passage_conjunction_unresolved`; a single rank-1 passage already
  supplies a complete alternative answer, so that descriptor's inclusion
  contract is not met.
- **Taxonomy effect:** `taxonomy_defect_flag=false`; the existing
  `plausible_non_gold_answer` primary code covers the case.
- **Registry:** `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Affected unit:** `5a83aaeb5542996488c2e483|dense`.

## D-012 - Treat the Bharatpur unit as implementation-induced score distortion with secondary bridge and event competition

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a7d61775542991319bc93b9|bm25`, use
  `minimal_preprocessing_score_distortion` as the candidate primary mechanism.
  Use `repeated_function_word_amplification`,
  `surface_form_tokenization_mismatch`, `near_duplicate_event_confusion`, and
  `description_only_bridge_entity` as secondary descriptors. Retain
  `query_facet_fragmentation` as the closest competitor and observable ranking
  pattern.
- **Implementation evidence:** Titles are not indexed. Query and paragraph
  text use lowercase whitespace splitting without stop-word removal,
  punctuation normalization, stemming, or lemmatization. In
  `rank-bm25==0.2.2`, `BM25Okapi.get_scores` iterates over every query-token
  occurrence, so the four occurrences of `of`, two of `the`, and two of
  `commander-in-chief` are each accumulated repeatedly.
- **Score evidence:** Exact reconstruction reproduces the stored scores. Rank
  1 `Commander-in-Chief, India` receives 17.31 points from `of`, 17.92 from
  `commander-in-chief`, 8.65 from `the`, and 8.89 from `india`. Rank 3
  `Siege of Bharatpur (1805)` receives 23.07 of its 41.85 points from `of` and
  `the`; it does not match the query token `bharatpur,`. Ranks 5-10 likewise
  obtain large `of`/`the` contributions plus only one content facet. The
  correct siege receives 34.79 from only `siege`, `of`, `the`, and `and`.
- **Gold mismatch evidence:** The correct passages lose matches including
  `bharatpur,`/`bharatpur`,
  `commander-in-chief`/`commander-in-chief,`, `india`/`india.`,
  `storming`/`stormed`, and `castle?`/`fortress`. Stapleton Cotton is also
  described rather than named in the question.
- **Compound interpretation:** Better preprocessing would address the broad
  distractor-score inflation and several gold false negatives, but it would
  not remove the genuine wrong-officeholder and 1805-event competitors. BM25
  still cannot enforce that a single person jointly satisfies the Ireland,
  India, and Bharatpur relations.
- **Tie-break:** Prefer `minimal_preprocessing_score_distortion` over
  `query_facet_fragmentation` because the implementation and per-token score
  decomposition directly establish the former, whereas fragmentation describes
  the resulting list. Keep event confusion and the unnamed bridge as
  secondaries because neither explains the broad set of rank-4-to-rank-10
  distractors.
- **Taxonomy effect:** Mark `taxonomy_defect_flag=true`; the current vocabulary
  lacks a general category covering both function-word score amplification and
  punctuation-sensitive false-negative matching.
- **References:** `references/bm25_implementation_reference.md` and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Affected unit:** `5a7d61775542991319bc93b9|bm25`.
## D-013 - Record the Dense implementation boundary without reclassifying the reviewed Dense overlap units

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** Record the run-specific Dense implementation contract in
  `references/dense_implementation_reference.md`. Do not change the candidate
  primary codes for `5a76387d554299109176e6ba|dense` or
  `5a83aaeb5542996488c2e483|dense`.
- **Verified implementation:** The main Dense run is a symmetric
  `sentence-transformers/all-MiniLM-L6-v2` bi-encoder. It embeds paragraph text
  but not titles, uses the same encoder for queries and passages, explicitly
  L2-normalizes both sides, and scores independent passages with dot product,
  equivalent to cosine similarity. It has no prompt, threshold, reranker, or
  cross-passage reasoning. The inspected model configuration uses a 256-token
  maximum and mean pooling.
- **Interpretation boundary:** A high-ranked semantic neighborhood can support
  an output-level description such as broad person/birth similarity or
  same-artist work proximity. It does not reveal token-level attention,
  internal feature weights, or interaction among retrieved passages.
- **Case check:** The verified contract is consistent with D-009 for the Am
  Rong/Ava DuVernay unit and D-011 for the Kanye/Graduation unit. Neither label
  depends on a reranker or cross-passage component. `Graduation` remains a
  complete single-passage alternative answer, while the Am Rong/Ava conclusion
  remains deliberately phrased as an output-supported interpretation rather
  than a claim about internal attention.
- **Reproducibility boundary:** The repository does not lock the transitive
  dependency versions or model revision, and historical result files contain
  no environment/model manifest. Current local versions and cached revision
  must not be asserted as the exact historical run environment.
- **Taxonomy effect:** No category or descriptor change. This decision narrows
  evidentiary language and adds run-specific implementation provenance.
- **Reference:** `references/dense_implementation_reference.md`.
- **Affected units:** `5a76387d554299109176e6ba|dense` and
  `5a83aaeb5542996488c2e483|dense`.

## D-014 - Reclassify the Blue/Innocent BM25 unit as implementation-supported score distortion

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a7c9f325542990527d554e6|bm25`, replace
  `literal_cue_topic_capture` with `minimal_preprocessing_score_distortion` as
  the candidate primary mechanism. Replace `metonymic_bridge_unresolved` with
  `repeated_content_word_amplification`,
  `surface_form_tokenization_mismatch`, `technical_topic_crowding`, and
  `gold_chain_substitutability` as secondary descriptors.
- **Observed passage evidence:** BM25 ranks `Innocent Records` ninth and `Blue`
  eighteenth. Ranks 1-8 concern RGB/color models or spaces, but rank 2
  `RGB color model` explicitly identifies blue as an additive primary color
  and therefore supplies useful answer evidence rather than being a pure
  distractor. Dense ranks `Innocent Records` fourth and annotated `Blue`
  seventh; Dense rank 1 `RGB color model` plus rank 4 `Innocent Records` forms
  a complete top-five alternative chain.
- **Verified implementation:** The formal run indexes paragraph text but not
  titles and tokenizes with lowercase whitespace splitting. BM25Okapi scores
  every query-token occurrence, so the query's two occurrences of `color` are
  accumulated twice. There is no punctuation normalization, stemming,
  lemmatization, spelling normalization, or query-term deduplication.
- **Exact score evidence:** Reconstructing the 4,937-passage pooled corpus
  reproduces the formal BM25 top 20 and scores with zero error. The repeated
  `color` token contributes about 19-24 points to each rank-1-to-rank-8
  technical passage. The `Blue` passage uses `colour` and receives no score
  from query token `color`. `Innocent Records` also loses exact matches through
  `act`/`act)`, `sales`/`sales.`, and `achieved`/`achieving` differences.
- **Controlled diagnostic evidence:** Deduplicating query tokens moves
  `Innocent Records` from rank 9 to rank 5 while `RGB color model` remains rank
  1 and supplies the other answer step. Punctuation plus `colour`/`color`
  normalization moves `Blue` from rank 18 to rank 6 and `Innocent Records`
  from rank 9 to rank 8. These are diagnostic counterfactuals, not observed
  production rankings or a proposed production configuration.
- **Supported interpretation:** Repeated content-word scoring and surface-form
  false negatives are directly established and are more proximal than the
  output-level description `literal_cue_topic_capture`. Technical-topic
  crowding remains secondary because it describes the resulting neighborhood;
  evidence-bearing `RGB color model` is excluded from the distractor set.
- **Boundary:** The exact-title gold contract treats `Blue` as missing even
  though `RGB color model` supplies the same primary-color fact. This supports
  `gold_chain_substitutability`, but the observed BM25 top five still lacks
  `Innocent Records`, so it is not a complete target-retriever top-five rescue.
  The original `metonymic_bridge_unresolved` interpretation is rejected: the
  annotated `Blue` passage is a color article, not a musical-act biography.
- **Tie-break:** Prefer `minimal_preprocessing_score_distortion` over
  `literal_cue_topic_capture` because the known tokenizer, repeated-token
  scoring loop, exact score decomposition, and controlled ablation identify a
  concrete score mechanism. Literal topic capture describes the ranking shape
  but does not explain the verified spelling, punctuation, and morphology
  mismatches.
- **Speculation boundary:** Do not infer that a particular stemmer, synonym
  system, or production normalization policy would place both annotated gold
  passages in the top five.
- **Taxonomy effect:** `taxonomy_defect_flag=false`; D-012 already established
  a candidate primary broad enough to cover implementation-induced
  amplification plus surface-form false negatives. The newly adopted
  secondary descriptors remain provisional and are registered for the
  vocabulary audit.
- **References:** `references/bm25_implementation_reference.md` and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Affected unit:** `5a7c9f325542990527d554e6|bm25`.

## D-015 - Retain same-entity variant crowding for the Tennessee Dense unit and remove the cutoff descriptor

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a7d19d85542995ed0d165e8|dense`, retain
  `same_entity_variant_crowding` as the candidate primary mechanism and retain
  `gold_chain_substitutability` as the only secondary descriptor. Remove
  `cutoff_sensitive_near_miss`. Use `cross_passage_conjunction_unresolved` as
  the closest competitor, not as an additional adopted descriptor.
- **Observed passage evidence:** Pooled Dense ranks annotated
  `1984 Tennessee Volunteers football team` eighth at 0.5847 and
  `Southeastern Conference` eleventh at 0.4914. Ranks 1-9 are Tennessee
  Volunteers season or statistical passages. Rank 1 repeats the full team
  phrase twice but does not state conference membership. Ranks 2 and 5 concern
  the SIAA, rank 9 concerns the Southern Conference, and rank 3 mentions SEC
  history without explicitly stating the membership relation.
- **Substitute evidence:** Rank 4 `1983 Tennessee Volunteers football team`,
  rank 6 `Tennessee Volunteers football statistical leaders`, and rank 7
  `1985 Tennessee Volunteers football team` explicitly establish the
  Tennessee-to-SEC bridge. They are evidence-bearing substitutes for the
  annotated 1984 passage, not ordinary distractors. None supplies the SEC
  headquarters city. The rank-11 conference passage states that the SEC is
  headquartered in Birmingham, Alabama.
- **Corpus provenance:** All nine Tennessee passages ahead of the conference
  passage are part of this item's original ten-passage HotpotQA context. The
  formal per-question Dense result retains the same order and places
  `Southeastern Conference` tenth. Pooling inserts `Shawnee Mission District
  Stadium` at pooled rank 10 and shifts the conference passage to 11, but it
  does not create the same-team neighborhood or the top-five failure.
- **Verified implementation:** Dense encodes paragraph text without titles
  using a symmetric `all-MiniLM-L6-v2` bi-encoder, explicitly L2-normalizes
  query and passage vectors, and ranks independent passage cosine similarities.
  The main run has no reranker, cross-attention, or cross-passage reasoning.
  The inspected model configuration uses mean pooling, but the run artifacts
  do not expose token-level contributions.
- **Supported interpretation:** The query contains no year and provides no
  basis for preferring the annotated 1984 season over other Tennessee season
  passages. A redundant same-entity neighborhood occupies the leading ranks,
  while the passage carrying the conference-to-Birmingham fact is lower. This
  is consistent with independent whole-passage similarity failing to enforce
  all steps of the team-to-conference-to-city chain.
- **Comparison correction:** BM25 ranks annotated 1984 second and does not
  retrieve `Southeastern Conference` in its stored top 50. The first-pass claim
  that BM25 benefited from an exact year-token match is rejected because the
  query contains no year. BM25 remains comparison evidence only and is not the
  cause of the Dense ordering.
- **Cutoff decision:** Do not retain `cutoff_sensitive_near_miss`. The score
  gap from rank 5 to annotated 1984 is about 0.050, but that passage is already
  substitutable inside the top five. The meaningful conference evidence is at
  rank 11, about 0.143 below rank 5, so the unit is not well described as a
  small cutoff fluctuation.
- **Tie-break:** Prefer `same_entity_variant_crowding` over
  `cross_passage_conjunction_unresolved` because actual passage texts and
  per-question provenance establish a concrete, repetitive same-team
  neighborhood occupying the first nine ranks. The cross-passage limitation is
  real but broader and does not distinguish why this list is unusually
  redundant.
- **Speculation boundary:** Rank 1's short, team-focused text and its
  Chattanooga location language may affect whole-passage similarity, while
  additional 1984 season details may change the mean-pooled vector. Without
  attribution or controlled text ablation, do not claim that Chattanooga
  raised the score or that mean pooling diluted the 1984 passage.
- **Boundary:** The annotated first gold is not unique because the query does
  not specify 1984 and several original-context passages provide the same SEC
  bridge. This does not yield a complete top-five answer chain because no
  top-five passage supplies Birmingham.
- **Taxonomy effect:** `taxonomy_defect_flag=false`; the retained primary and
  secondary already exist in the provisional vocabulary. D-015 introduces no
  new code name and does not freeze or merge any category.
- **References:** `references/dense_implementation_reference.md` and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Affected unit:** `5a7d19d85542995ed0d165e8|dense`.

## D-016 - Reclassify the Ian Harland BM25 unit as minimal-preprocessing score distortion

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a83a532554299334474606f|bm25`, replace
  `generic_term_lexical_crowding` with
  `minimal_preprocessing_score_distortion` as the candidate primary mechanism.
  Replace `superlative_bridge_underweighted` with
  `surface_form_tokenization_mismatch`,
  `repeated_function_word_amplification`, and
  `generic_term_lexical_crowding` as secondary descriptors.
- **Observed passage evidence:** Pooled BM25 ranks `Ian Harland` seventeenth and
  `Peterhouse, Cambridge` twentieth. The Ian passage states that he was
  educated at The Dragon School in Oxford before attending Peterhouse; the
  Peterhouse passage establishes that it is the oldest University of Cambridge
  college. The answer is `The Dragon School in Oxford`. Actual ranks 1-5 are
  partial competitors: Wolfson is a Cambridge college but not the oldest; UC
  Berkeley CNR is an oldest college in the wrong university system;
  Doehling-Heselton concerns an oldest college-football rivalry; College of
  Charleston is an oldest college elsewhere; and Trinity Hall Boat Club is an
  old Cambridge college boat club. None supplies the answer or a complete
  substitute hop.
- **Corpus and comparison evidence:** Per-question BM25 ranks Ian Harland third
  and Peterhouse ninth, so pooling adds substantial competition but does not
  create the entire Peterhouse miss. Dense pooled ranks the two gold passages
  first and second. These contrasts establish provenance and reachability, not
  the internal BM25 cause.
- **Verified implementation:** The formal run indexes paragraph text but not
  titles and tokenizes with lowercase whitespace splitting. It performs no
  punctuation normalization or stop-word removal. Under `rank-bm25==0.2.2`,
  each repeated query-token occurrence is scored separately.
- **Exact score evidence:** Reconstruction over all 4,937 pooled passages
  exactly reproduces the formal top 20 and scores. Query token `cambridge?`
  does not match `Cambridge,` in either gold passage; it also does not match the
  differently punctuated Cambridge tokens in Wolfson or other leading
  passages. Repeated `the` contributes about 7.8-8.7 points to each top-five
  passage and 6.76/7.80 points to Ian/Peterhouse, with repeated `at` adding
  further score where present.
- **Controlled diagnostics:** Punctuation normalization on both query and
  passage tokens moves Ian from rank 17 to 3 and Peterhouse from 20 to 4 in the
  complete pooled ranking. Stop-word removal without punctuation normalization
  improves them to ranks 12 and 7-8 but does not place both inside top five.
  Combining punctuation normalization and stop-word removal places Peterhouse
  third and Ian fourth. Deduplicating repeated query tokens alone leaves the
  top five unchanged. These are diagnostic counterfactuals, not proposed
  production settings.
- **Supported interpretation:** Punctuation-sensitive false-negative matching
  is outcome-determinative for the formal top-five result. Unfiltered and
  repeated function-word scoring materially amplifies the competing list but
  is not independently sufficient. Generic lexical crowding remains a real
  secondary output pattern because multiple verified passages match partial
  college, university, oldest, or Cambridge facets, and Wolfson plus Trinity
  remain above the golds after normalization.
- **Rejected descriptor:** Do not retain
  `superlative_bridge_underweighted`. The token `oldest` contributes about 5.18
  points to Peterhouse and large scores to several competitors; the evidence
  shows a scored but non-discriminating superlative cue, not an unweighted one.
- **Tie-break:** Prefer `minimal_preprocessing_score_distortion` over
  `generic_term_lexical_crowding` because the verified tokenizer, exact score
  reconstruction, and punctuation-only diagnostic identify a specific
  implementation mechanism that changes both golds into top-five hits. Retain
  generic crowding as the closest competitor and secondary because it explains
  the residual list shape that normalization does not remove.
- **Speculation boundary:** Do not claim that production Wolfson matched
  `cambridge?`; it did not. Do not claim that stop-word removal alone solves the
  case or prescribe a particular production analyzer. Title inclusion raises
  Ian in a separate diagnostic but does not explain Peterhouse.
- **Taxonomy effect:** `taxonomy_defect_flag=false`; D-012 already established a
  primary code covering implementation-induced amplification and surface-form
  false negatives. `generic_term_lexical_crowding` is newly adopted as a
  secondary use and is registered with explicit boundaries; the other retained
  descriptors already exist in the registry.
- **References:** `references/bm25_implementation_reference.md` and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Affected unit:** `5a83a532554299334474606f|bm25`.

## D-017 - Reclassify the Frank Thomas Dense unit as a description-only bridge failure

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a85cead5542991dd0999ea9|dense`, replace
  `weak_cross_domain_bridge` with `description_only_bridge_entity` as the
  candidate primary mechanism. Replace `short_answer_passage_underweighted`
  with `cross_passage_conjunction_unresolved`; retain
  `possible_type_mismatch` as an evaluation/wording secondary. Use
  `weak_cross_domain_bridge` as the closest competitor.
- **Observed passage evidence:** The dataset answer is `a pinball machine`.
  `Frank Thomas (designated hitter)` states that Thomas is the only
  major-league player with seven consecutive .300 seasons. The separate
  `Frank Thomas' Big Hurt` passage states that it is a pinball machine named
  after Frank Thomas. Pooled Dense ranks these passages tenth at 0.387911 and
  fiftieth at 0.295942. Actual ranks 1-5 are a batting-average reference and
  baseball biographies that match partial baseball or statistical facets but
  do not supply the Frank-Thomas-to-game relation. Rank 35 `Surround` mentions
  an arcade game but not Frank Thomas or the statistical clue. No inspected
  higher passage supplies a complete alternative answer.
- **Verified implementation:** The formal run encodes unchanged queries and
  paragraph text, excluding titles, with the symmetric
  `sentence-transformers/all-MiniLM-L6-v2` bi-encoder. It L2-normalizes vectors
  and ranks independent query-passage cosine scores, with no cross-passage
  attention, iterative hop expansion, or reranker. The game passage has 39
  model tokens including special tokens and is fully encoded. The player
  passage has 259, but the decisive clue occurs within the 256-token window.
- **Exact reconstruction:** Re-encoding the same 4,937 deduplicated pooled
  passages exactly reproduces the formal original top ten and both gold
  ranks/scores under the currently inspected local model snapshot.
- **Controlled full-corpus diagnostics:** Adding the oracle bridge name
  `Frank Thomas` to the otherwise preserved query moves the player and game
  golds from ranks 10/50 to 1/2. Replacing only `arcade game` with
  `pinball machine` moves them only to 6/12, and adding only `type of` leaves
  them at 10/53. Combining the name and type changes yields ranks 2/1. Every
  diagnostic re-scores the complete unchanged 4,937-passage candidate set;
  gold-only score changes are not treated as outcome evidence.
- **Supported interpretation:** The result-determinative condition is the
  unnamed description-only bridge entity interacting with independent
  passage scoring. The query describes Frank Thomas but does not name him;
  the player passage resolves the description, while the game passage contains
  the name and relation but not the identifying statistic. The retriever
  cannot carry the resolved entity from the first passage into the second.
- **Rejected descriptor:** Do not retain
  `short_answer_passage_underweighted`. Shortness is observable, but the
  passage is not truncated and neither implementation inspection nor an
  attribution/text ablation establishes a length-induced penalty.
- **Tie-break:** Prefer `description_only_bridge_entity` over
  `weak_cross_domain_bridge` because the complete-corpus, one-factor oracle-name
  diagnostic restores both required passages to top five, whereas type
  alignment alone does not. Cross-domain language is a broader description of
  the baseball-to-pinball transition and does not identify the missing anchor.
  Retain `cross_passage_conjunction_unresolved` as the architectural secondary.
- **Evaluation boundary:** `arcade game` in the question does not align cleanly
  with the passage and answer phrase `pinball machine`. This warrants
  `possible_type_mismatch`, but it is not independently outcome-determinative.
- **Speculation boundary:** The oracle-name rewrite is a diagnostic, not a
  proposed production query or evidence that a user should know the bridge
  answer in advance. Do not infer token-level Dense weights from these ranking
  changes or generalize this result beyond the inspected run and corpus.
- **Corpus and comparison evidence:** Per-question Dense ranks the golds 6/10,
  pooled BM25 ranks them 2/45, and per-question BM25 ranks them 1/5. Pooling
  increases competition but does not create the split evidence chain. Cross-
  method ranks establish reachability and provenance, not Dense internals.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. The primary already exists
  in the provisional vocabulary. D-017 registers
  `cross_passage_conjunction_unresolved` and `possible_type_mismatch` as
  bounded secondary descriptors; it does not merge or freeze vocabulary.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`, and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Affected unit:** `5a85cead5542991dd0999ea9|dense`.

## D-018 - Reclassify the Serri/John Fogerty Dense unit as compound two-sided crowding

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5a8d93ad554299653c1aa13d|dense`, replace
  `proper_name_homonym_collision` with `compound_two_sided_crowding` as
  primary. Remove `low_context_name_query`. Retain
  `proper_name_homonym_collision` for John and adopt
  `answer_property_semantic_crowding` for Serri/property as secondaries. Use
  `proper_name_homonym_collision` as closest competitor.
- **Observed passage evidence:** Pooled Dense ranks `John Fogerty` 8 at
  0.435380 and `Serri` 12 at 0.412001. John is described as musician,
  singer, and songwriter, not actor; Serri as singer, songwriter, and actress.
  Ranks 1/2/6 are different Fogerty engineers or relatives. Ranks 3-5/7
  explicitly describe actors or actor-adjacent people who are neither named
  candidate. No inspected higher passage supplies a valid answer.
- **Corpus provenance:** Per-question Dense ranks the golds 4/5. Pooling adds
  name-related and actor-property competitors and shifts them to 8/12, so the
  Fogerty family alone is real but insufficient. Pooled BM25 stores neither in
  top 50; per-question BM25 ranks them 8/10. A supplementary reranker gives
  2/5. These are provenance/reachability evidence, not Dense causes.
- **Verified implementation:** Symmetric
  `sentence-transformers/all-MiniLM-L6-v2` encodes unchanged queries and
  paragraph text without titles, L2-normalizes, and independently ranks cosine
  similarity; no cross-passage attention, iterative hop, or main-run reranker.
  Mean pooling has a 256-token limit. Golds use 74/53 tokens, so no truncation.
- **Exact reconstruction:** The same 4,937 deduplicated pooled passages under
  the inspected model snapshot exactly reproduce baseline ranks and scores.
- **Complete factorial diagnostic table:**

| Condition | Kind | Exact change | John rank/score | Serri rank/score | Both top-5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | original query | 8 / 0.435380 | 12 / 0.412001 | no | exact reconstruction |
| A | single | `actor` -> `actress` | 10 / 0.414732 | 2 / 0.464945 | no | repairs Serri only |
| B | single | `actor` -> `actor or actress` | 12 / 0.416848 | 10 / 0.424390 | no | inclusive wording fails |
| C | single | `John` -> `John Cameron` | 7 / 0.421266 | 13 / 0.395223 | no | name expansion fails |
| D | single/removal | `Serri or John Fogerty` | 6 / 0.344798 | 1 / 0.466418 | no | less context improves both |
| B+C | combination | inclusive property + full John name | 8 / 0.409887 | 10 / 0.406463 | no | tested combination fails |
| E | multi-factor | singers + inclusive property + full name | 3 / 0.443472 | 1 / 0.465869 | yes | only compound rewrite restores both |
| profession only | `not_run` | singers + original property/name | n/a | n/a | n/a | no attribution |
| profession+B | `not_run` | singers + inclusive property | n/a | n/a | n/a | E not credited here |
| profession+C | `not_run` | singers + full name + actor | n/a | n/a | n/a | E not credited here |

- **Single-factor effect:** A restores Serri only. B, C, and D fail to recover
  both. D is lower-context yet improves Serri to 1 and John to 6, rejecting
  `low_context_name_query` as causal.
- **Combination/interaction effect:** B+C fails at 8/10. Only E restores both
  at 3/1, but E changes profession anchor, gender wording, full name, and
  syntax. It supports compound interaction, not attribution to one component.
- **Supported interpretation:** Different-entity Fogerty passages support
  `proper_name_homonym_collision` for John. Non-candidate actor passages and
  pooled provenance support `answer_property_semantic_crowding` for
  Serri/property. Neither explains both; use `compound_two_sided_crowding`.
- **Tie-break:** Homonyms explain John but not uniquely named Serri or actor
  additions; property crowding explains Serri/property but not John homonyms.
  No single-factor repair restores both.
- **Speculation boundary:** Rewrites are oracle diagnostics, not production
  fixes. Do not independently credit `actress`, `Cameron`, `singers`, or
  syntax without unrun cells. Do not infer token-level weights or truncation.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. Compound primary already
  exists. D-018 registers `proper_name_homonym_collision` and introduces
  `answer_property_semantic_crowding` as provisional secondaries; no merge or
  freeze occurs.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`, and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Affected unit:** `5a8d93ad554299653c1aa13d|dense`.

## D-019 - Reclassify the A Summer in the Cage / American Hardcore BM25 unit as minimal-preprocessing score distortion

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5ab72a025542992aa3b8c7b8|bm25`, replace
  `multiword_title_token_fragmentation` with
  `minimal_preprocessing_score_distortion` as primary. Adopt
  `surface_form_tokenization_mismatch` and
  `generic_query_scaffold_score_inflation`; replace
  `same_topic_title_distractor` with `same_topic_passage_distractor`. Use
  `multiword_title_token_fragmentation` as the closest competitor.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. The primary and
  `surface_form_tokenization_mismatch` already exist. D-019 adds two bounded
  secondary descriptors to the provisional registry; it does not merge or
  freeze vocabulary.
- **Affected unit:** `5ab72a025542992aa3b8c7b8|bm25`.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`, and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.

### Complete case evidence

Observed evidence:
The question asks what kind of film both explicitly named works are. A Summer in the Cage states that it is a 2007 documentary film; American Hardcore states that it is a documentary. Exact full-corpus reconstruction places them at ranks 430 (15.585870) and 4067 (9.241837). The formal top five are All Ages: The Boston Hardcore Film 1 (25.568543), Treehouse 2 (24.087261), Libocedrus 3 (23.669757), Summer Olympic Games 4 (22.449722), and Murder of Grace Brown 5 (21.908651). Actual-text review shows that All Ages is a documentary about Boston hardcore and explicitly mentions "American Hardcore" Director Paul Rachman, but it contains no evidence about A Summer in the Cage and cannot answer the comparison. Treehouse and Libocedrus are unrelated. Summer Olympic Games matches the Summer facet but not either film. Murder of Grace Brown does not establish either film type.

Gold, provenance, and comparison evidence:
Per-question BM25 ranks A Summer in the Cage 3 and American Hardcore 8, with All Ages still rank 1. Pooling therefore amplifies generic competition but does not create the same-topic competitor or the original full-evidence miss. Pooled Dense ranks the golds 1 and 3 and independently confirms that both passages are present and reachable; Dense ranks are comparison evidence, not a BM25 cause.

Verified implementation facts and exact reconstruction:
The formal run indexes paragraph text only, not titles. Query and documents use lowercase whitespace splitting without punctuation normalization, stop-word removal, phrase matching, or entity boundaries. rank-bm25 0.2.2 BM25Okapi defaults apply. Rebuilding the first-occurrence, title-deduplicated 4,937-passage corpus reproduces all formal top-50 titles and scores exactly; maximum absolute score error is 0. The query tokens are ["a, summer, in, the, cage", and, "american, hardcore", are, both, what, kind, of, film?]. The quote and question-mark forms do not match gold-text a/cage, american/hardcore:, or film.

Baseline per-token evidence:
All Ages receives 25.568543: quoted-name tokens "american + hardcore" contribute 12.041429, while in/the/and/are/of contribute 13.527114. Treehouse receives all 24.087261 from in/the/and/what/kind/of. Libocedrus receives all 23.669757 from in/the/and/are/both/what/of. Summer Olympic Games receives 6.557348 from summer and 15.892374 from scaffold/function tokens. Murder of Grace Brown receives 5.038192 from the punctuation-bearing token "a and 16.870458 from scaffold/function tokens. A Summer receives 5.981429 from summer and 9.604441 from in/the/and; the other title/type forms do not match. American Hardcore receives only 9.241837 from the/and/of and zero from its title or film-type terms.

Complete 2x2x2 factorial diagnostic:
P = strip leading/trailing Unicode non-word punctuation from each lowercase whitespace token with ^\W+|\W+$ on both query and documents. S = remove exactly {a, the, in, and, are, both, what, of} after tokenization. T = prepend title plus one space to the indexed paragraph text. Every condition uses the same 4,937 passages, order, first-title deduplication, BM25Okapi defaults, and stable descending sort.
| Condition | Kind | Exact change | A Summer rank/score | American Hardcore rank/score | Both top-5 |
|---|---|---|---:|---:|---|
| baseline | baseline | none | 430 / 15.585870 | 4067 / 9.241837 | no |
| T | single | title prepended | 111 / 17.877157 | 4074 / 9.236677 | no |
| S | single | exact function/scaffold set removed | 30 / 6.055856 | 4193 / 0.000000 | no |
| S+T | combination | removal plus title | 11 / 8.014693 | 4193 / 0.000000 | no |
| P | single | boundary punctuation normalized | 6 / 29.111138 | 30 / 23.670245 | no |
| P+T | combination | normalization plus title | 1 / 33.808407 | 15 / 25.957566 | no |
| P+S | combination | normalization plus removal | 2 / 16.306188 | 14 / 11.471025 | no |
| P+S+T | three-factor combination | all tested changes | 1 / 20.598225 | 6 / 13.790434 | no |

Single-factor effects:
P is the strongest single factor, moving the golds from 430/4067 to 6/30, but it does not fully restore top five. S improves only A Summer and leaves American Hardcore at zero because its distinctive baseline forms still mismatch. T improves only A Summer and slightly worsens American Hardcore; title exclusion is real but title inclusion alone is not a rescue.

Combination and interaction effects:
P+T restores A Summer to 1 but American Hardcore only to 15. P+S reaches 2/14. P+S+T reaches 1/6, the best tested complete-chain result, but still fails strict full top-five recovery. The rank-6 American passage trails the fifth result by about 0.074 score; this counterfactual proximity is not an observed cutoff mechanism.

Supported interpretation:
Minimal-preprocessing score distortion is the most specific verified primary: boundary punctuation creates entity/type false negatives, and unfiltered query-scaffold scoring materially promotes unrelated passages. surface_form_tokenization_mismatch records the concrete false negatives. generic_query_scaffold_score_inflation records the exactly decomposed non-repeated grammar/interrogative contribution. same_topic_passage_distractor records the residual real-text competition from All Ages without implying that its displayed title was scored.

Closest competitor and tie-break:
multiword_title_token_fragmentation describes an orderless partial-token ranking pattern, but it is less specific and partly misleading here because titles are not indexed. Title inclusion alone does not recover either complete outcome, whereas tokenizer inspection, zero-error score reconstruction, per-token decomposition, and P/S/T diagnostics directly establish the broader preprocessing distortion. Retain same-topic competition as a secondary because no tested preprocessing combination recovers both golds into top five.

Not-run cells and attribution boundary:
All cells in the defined P x S x T factorial were run; there are no missing cells in that design. Phrase n-grams, stemming/lemmatization, arbitrary oracle title boosts, and production analyzer prescriptions were not run because they introduce additional mechanisms outside this tie-break. The diagnostics do not prove that any deployable preprocessing policy would fully recover both golds, do not make pooling a causal category, and do not support attributing the remaining rank-6 result to one untested feature.

Speculation boundary:
Do not claim that phrase preservation, stemming, a particular stop-word list, or title indexing would independently solve the case. Do not treat the counterfactual rank 6, observed gold missingness, cutoff, retriever identity, or comparison question type as a causal category.

## D-020 - Retain quoted-phrase semantic drift for the Flaming Feather / Montezuma Castle Dense unit and revise its secondary set

- **Date:** 2026-07-31
- **Status:** active
- **Decision:** For `5ab978855542996be2020512|dense`, retain
  `quoted_phrase_semantic_drift` as the candidate primary mechanism. Retain
  `exact_string_source_dependency` and register it. Adopt the existing
  `cross_passage_conjunction_unresolved` and introduce
  `question_frame_semantic_crowding` as additional secondary descriptors. Use
  `description_only_bridge_entity` as the closest competitor. Mark
  `taxonomy_defect_flag=true` for a naming-versus-mechanism problem described
  below.
- **Taxonomy effect:** The primary already exists in the provisional inventory
  and is not renamed here. D-020 registers one previously unregistered
  descriptor, adopts one registered descriptor for a second unit, and adds one
  new provisional descriptor with complete boundaries. It does not merge,
  demote, or freeze vocabulary, and it does not turn counts into prevalence.
- **Affected unit:** `5ab978855542996be2020512|dense`.
- **References:** `references/dense_implementation_reference.md`,
  `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`, and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.

### Complete case evidence

Observed evidence:
The question is `Over how many centuries were the "dwelling place of the dead" built?` Its only content cue is a verbatim epithet that occurs literally in exactly one corpus passage. Flaming Feather is a 1952 Technicolor Western film article in which the epithet appears as one embedded clause explaining why Yavapai extras refused to enter the cliff-dwellings. Montezuma Castle National Monument never contains the epithet; it states that the dwellings were "built over the course of three centuries". Exact reconstruction places the golds at complete-corpus ranks 465 (0.112206) and 13 (0.317347), so the stored `not_in_top50` status means rank 465 of 4,937 rather than corpus absence. Two verified competitor families outrank the answer passage. Question-frame competitors match old structures spanning many centuries with no dwelling or dead wording at all: List of oldest synagogues 1 (0.428425), Patan minara 2 (0.395695), History of England 4 (0.372366), Oldest synagogues in the United Kingdom 8 (0.330121), Asante Traditional Buildings 9 (0.326038). Epithet-sense competitors use the phrase in a religious or mythological sense: Tabernacle 3 (0.372944, "dwelling place" three times), Heaven in Judaism 5 (0.352418, "dwelling place of God", "realm of the dead"), Chateau de Druyes 6 (0.338059, "dwelling place of Peter II", built in the 12th century), Langston Hughes House 7 (0.330680, "dwelling built in 1869"), Vidblain 20 (0.297265, "dwelling place for the souls of the dead"). Every passage above rank 13 was checked against all explicit question constraints. None states a construction span for any dwelling place of the dead, so there is no complete plausible non-gold answer and no evidence-bearing substitute for either hop; Tabernacle's "some 300 years later" is a succession date, not a build duration.

Gold, provenance, and comparison evidence:
Per-question Dense over the item's own ten context passages ranks Flaming Feather 9 of 10, below seven of the eight distractors, and Montezuma Castle 6. Pooling therefore did not create this failure; it moved 9/10 to 465/4937 and 6/10 to 13/4937. Corpus setting is provenance, not a causal category. Pooled BM25 ranks the golds 1 and 85; per-question BM25 ranks them 3 and 1. The first-pass note's claim that BM25 succeeded "by exact-phrase match" is corrected: the verified BM25 implementation performs lowercase whitespace splitting with no phrase matching. Exact reconstruction reproduces the stored score 23.945524 and decomposes it as `"dwelling` 7.815653, `place` 3.340714, `the` 3.981535 twice, `of` 2.797241, and `were` 2.028846; the query token `dead"` does not match the passage token `dead."`, and neither `centuries` nor `built?` occurs in that passage. Montezuma Castle's pooled BM25 score of 16.508697 comes only from `over/were/the/of/the` because its `centuries.`, `built`, and `dwellings` forms all miss the query forms. All BM25 facts are reachability and comparison evidence and are not the Dense cause.

Verified implementation facts and exact reconstruction:
The formal Dense run encodes the unchanged question and paragraph text only, excluding titles, with the symmetric `sentence-transformers/all-MiniLM-L6-v2` bi-encoder, applies explicit row-wise L2 normalization to both sides, and ranks independent query-passage dot products equal to cosine similarity under a stable descending sort. There is no prompt, threshold, reranker, iterative hop, or cross-passage reasoning in the main run. The inspected snapshot uses mean pooling with a 256-token limit; the gold passages tokenize to 114 and 84 model tokens, so neither is truncated. Re-encoding the same 4,937 deduplicated pooled passages reproduces all 50 formal top-50 titles in order with a maximum absolute score error of 2.384e-07.

Factorial setting:
Every condition re-scores the same unchanged 4,937-passage pooled corpus under the same model snapshot, corpus order, first-title deduplication, explicit L2 normalization, dot-product scoring, stable descending sort, and cutoff 5. Factors are P-independent query rewrites: A removes the two quotation marks around the epithet; B names the unnamed referent by appending `at Montezuma Castle`; C names the source film by appending `in the film Flaming Feather`. All eight A x B x C cells were run. T is a separate indexing factor that prepends title plus one space to every indexed passage before re-encoding. D, D2, and E are removal probes.

| Condition | Kind | Exact change | Flaming Feather rank/score | Montezuma Castle rank/score | Both top-5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | none | 465 / 0.112206 | 13 / 0.317347 | no | exact reconstruction, max abs error 2.384e-07 |
| A | single | quotation marks removed | 479 / 0.111678 | 12 / 0.318517 | no | quotation punctuation is inert |
| B | single | oracle referent name added | 453 / 0.114506 | 1 / 0.647072 | no | repairs the answer hop only |
| C | single | oracle source-film name added | 1 / 0.642457 | 99 / 0.197916 | no | repairs the source hop only, worsens the other |
| A+B | combination | unquoted plus referent name | 452 / 0.117326 | 1 / 0.651049 | no | A adds nothing to B |
| A+C | combination | unquoted plus film name | 1 / 0.666199 | 128 / 0.184604 | no | A adds nothing to C |
| B+C | combination | both oracle names | 1 / 0.553056 | 2 / 0.505606 | yes | only the two-anchor rewrite restores both |
| A+B+C | three-factor combination | all three changes | 1 / 0.572109 | 2 / 0.499141 | yes | equivalent to B+C |
| T | single, indexing | title prepended, baseline query | 526 / 0.098571 | 16 / 0.298440 | no | title exclusion is not the mechanism |
| D | removal probe | query is the epithet alone, quoted | 106 / 0.219506 | 88 / 0.228047 | no | the verbatim string does not retrieve its own source |
| D2 | removal probe | query is the epithet alone, unquoted | 180 / 0.181538 | 67 / 0.230495 | no | same result without quotation marks |
| E | removal probe | epithet replaced by the plain noun `dwellings` | 1180 / 0.049846 | 5 / 0.366752 | no | the epithet itself costs the answer passage ranks |
| T x A, T x B, T x C | `not_run` | title inclusion combined with query rewrites | n/a | n/a | n/a | T alone is inert-to-negative and cannot change the tie-break |
| reranker condition | `not_run` | cross-encoder rescoring of Dense candidates | n/a | n/a | n/a | the main Dense run has no reranker |
| production rewrite policy | `not_run` | any deployable query-rewrite configuration | n/a | n/a | n/a | oracle anchors are diagnostics, not fixes |

Single-factor effects:
A is inert in both directions, 465 to 479 and 13 to 12, so quotation punctuation is excluded as a mechanism despite the code name. T is inert-to-negative, 465 to 526 and 13 to 16, so title exclusion is excluded as well. B repairs only the answer hop and leaves the source passage at 453 even though the Flaming Feather text explicitly contains "Montezuma Castle National Monument". C repairs only the source hop and pushes the answer passage from 13 to 99. Probe D is the decisive non-oracle result: when the query is exactly the verbatim string, the single passage that literally contains it ranks 106 of 4,937 while the top five are Heaven in Judaism, Buried Country, Dead at 17, Dead Jesus, and Vidblain. Probe E shows that the epithet also suppresses the answer passage, which moves from 13 to 5 when it is replaced by the plain noun `dwellings`.

Combination and interaction effects:
No single factor restores both required hops. Only B+C reaches 1/2, and A+B+C adds nothing over B+C. The reason no single oracle anchor suffices is architectural: the retriever scores passages independently, so resolving the referent for one passage cannot be carried into scoring the other. This supports a compound anchor requirement and the `cross_passage_conjunction_unresolved` secondary, not attribution of the outcome to B or C alone.

Supported interpretation:
The query designates its target only by a verbatim epithet lifted from one passage. Under titleless, independently scored whole-passage cosine similarity the epithet resolves to a religious, mythological, and death-related dwelling neighborhood instead of its source passage, and the same cue simultaneously displaces the answer passage. `exact_string_source_dependency` records that the source passage's only distinctive connection to the query is literal string overlap inside otherwise unrelated film-production content. `question_frame_semantic_crowding` records the independent competitor family at ranks 1, 2, 4, 8, and 9, which contains no dwelling or dead wording and which probe E shows persists after the epithet is removed. `cross_passage_conjunction_unresolved` records the architectural boundary demonstrated by B versus C versus B+C.

Closest competitor and tie-break:
Prefer `quoted_phrase_semantic_drift` over `description_only_bridge_entity`. The referent is genuinely unnamed, but unlike the D-017 Frank Thomas unit the single-factor oracle-name condition does not restore both hops: B lifts the answer passage to 1 while leaving the source passage at 453 despite that passage containing the oracle name in its own text. The description-only framing therefore does not explain the badly missed half. The drift mechanism has a direct non-oracle demonstration in probe D and explains degradation on both hops through probe E. `compound_two_sided_crowding` is rejected because B and C are oracle anchors for two passages rather than two independent mechanisms; both halves trace to the same epithet cue, and the compound reading would obscure that.

Taxonomy defect:
`taxonomy_defect_flag=true`. The name `quoted_phrase_semantic_drift` implies a quotation-punctuation or literal string-matching mechanism that condition A explicitly excludes. This is the same naming-versus-mechanism problem D-019 resolved by replacing `same_topic_title_distractor`. The defect is recorded now and the rename, for example to a verbatim-epithet formulation, is deferred to the vocabulary audit, because primary renaming and merging are not permitted before all 26 single-note units clear the section 7A gate.

Confidence:
Medium-high. The baseline is an exact reconstruction, the A x B x C factorial is complete, and both competitor families are verified from actual passage text. The limitation is that no single non-oracle condition restores both golds, so the primary explains the observed degradation without demonstrating a complete recovery path.

Speculation boundary:
Do not claim that mean pooling diluted the epithet inside the film passage, that the epithet's position raised or lowered any score, or that any individual token contributed a measurable amount to a Dense score; no attribution or controlled text ablation was run. Do not present the oracle anchors as deployable query rewrites. Do not describe the comparison BM25 result as exact-phrase retrieval. Do not treat pooling, cutoff proximity, retriever identity, gold missingness, or question type as a causal category.

## D-021 - Reclassify the Neil Blair / Prince Andrew BM25 unit as minimal-preprocessing score distortion

- **Date:** 2026-08-01
- **Status:** active
- **Decision:** For `5ac1a3665542994ab5c67daf|bm25`, replace
  `description_only_bridge_entity` with
  `minimal_preprocessing_score_distortion` as the candidate primary mechanism.
  Remove the unregistered secondary `weak_lexical_name_anchor`. Adopt
  `surface_form_tokenization_mismatch`,
  `generic_query_scaffold_score_inflation`,
  `description_only_bridge_entity`, and `generic_term_lexical_crowding` as
  secondary descriptors, and introduce one new registered descriptor,
  `entity_alias_reference_mismatch`. Use `description_only_bridge_entity` as the
  closest competitor.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. D-012 already established a
  primary broad enough to cover implementation-induced amplification together
  with surface-form false negatives, and D-019 already established the scaffold
  descriptor. D-021 adds one new provisional secondary with complete boundaries,
  adopts four already registered descriptors for one further unit, and adds one
  worked illustration to the `surface_form_tokenization_mismatch` include rule
  without widening its definition. It does not merge, rename, demote, or freeze
  vocabulary, does not settle any primary-versus-secondary boundary rule, and
  does not turn counts into prevalence. `weak_lexical_name_anchor` is dropped
  from this row but is preserved in `case_memos_v1.csv` and in the vocabulary
  union as a historical first-pass name.
- **Affected unit:** `5ac1a3665542994ab5c67daf|bm25`.
- **References:** `references/bm25_implementation_reference.md`,
  `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`, and
  `manual_review_v1/analysis/secondary_descriptor_registry.md`.

### Complete case evidence

Observed evidence:
The question is `What was position of the man who served Prince Andrew from 1990-2001? ` The annotated answer hop is Neil Blair, whose complete text is `Captain Robert Neil Blair CVO RN was Private Secretary and Treasurer to The Duke of York, 1990–2001.` The annotated second hop, Prince Andrew, Duke of York, supplies the identity between the personal name and the peerage title. Exact reconstruction places the golds at complete-corpus ranks 2074 (9.070003) and 14 (17.955882), so the stored `not_in_top50` status means rank 2074 of 4,937 rather than corpus absence. The formal top five are Princess Henriette of Nassau-Weilburg 1 (24.508123), Armie Hammer 2 (23.115175), Salvatore Testa 3 (23.067293), Krajmir 4 (21.909745), and Joe Gilmore 5 (20.322148). Every passage above the rank-14 gold was read in full. Krajmir states that a Serbian nobleman "served Prince Lazar", and John Hartmann 7 (19.283302) states that he "served Prince George, Duke of Cambridge"; both reproduce the query relation with the wrong prince. Armie Hammer matches `prince` and `andrew` through the fictional character "Prince Andrew Alcott" and `man` through "The Man from U.N.C.L.E."; Salvatore Testa matches `prince` through "The Crowned Prince of the Philadelphia Mob" and `served` through "served as a hitman"; Joe Gilmore matches `prince` three times in a cocktail dedication list and `position` through "a position he held"; Princess Henriette matches `prince` four times and `andrew` once through "Prince Andrew of Greece and Denmark". Man Booker International Prize 8 (18.397810) matches only `man` plus scaffold, Andrew Murray (Guyanese boxer) 10 (18.147708) only the forename `andrew` plus scaffold, Lord High Treasurer 11 (18.122616) only `position` plus scaffold, Jeff Hoover 12 (18.082329) only `served` and `position` plus scaffold, and Abteilungsleiter (NSDAP) 13 (18.073350) only `position` plus scaffold. No inspected higher passage names the man who served Prince Andrew or states his position, so there is no complete plausible non-gold answer. A full-corpus substring scan confirms that `private secretary`, `treasurer to`, and `neil blair` each occur in exactly one of the 4,937 passages, all in Neil Blair, so the answer hop has no substitute at all.

Gold, provenance, and comparison evidence:
Per-question BM25 over the item's own ten context passages ranks Prince Andrew 9 and Neil Blair 10, the last two of ten, behind Krajmir, Armie Hammer, Princess Henriette, Joe Gilmore, John Hartmann, Royal Marriages Act 1772, Wedding dress of Sarah Ferguson, and List of royal tours of Canada (21st century). Pooling therefore did not create this failure; the mechanism is fully present in the ten-passage index. Corpus setting is provenance, not a causal category. Pooled Dense ranks the golds 5 and 1 and per-question Dense ranks them 2 and 1, which establishes that both passages are present and reachable without lexical overlap. Dense evidence is comparison and reachability evidence only and is not the BM25 cause; Dense and BM25 score magnitudes are not compared.

Verified implementation facts and exact reconstruction:
The formal run indexes paragraph text only, not titles, and tokenizes both query and documents with lowercase whitespace splitting. There is no punctuation normalization, stop-word removal, stemming, lemmatization, Unicode normalization, phrase matching, entity-boundary preservation, or initial expansion. `rank-bm25==0.2.2` `BM25Okapi` defaults apply with `k1=1.5`, `b=0.75`, and `epsilon=0.25`, and every query-token occurrence is scored separately. The query contains no repeated token, so repeated-occurrence amplification is not available as a mechanism in this unit and `repeated_function_word_amplification` is inapplicable. The query tokens are `what`, `was`, `position`, `of`, `the`, `man`, `who`, `served`, `prince`, `andrew`, `from`, and `1990-2001?`. Rebuilding the first-occurrence, title-deduplicated 4,937-passage pooled corpus reproduces all 50 formal top-50 titles in order with a maximum absolute score error of 0. Corpus average document length is 90.884950.

Baseline per-token evidence:
Neil Blair, at 17 tokens, receives its entire 9.070003 from three low-IDF function words: `was` 3.023334, `of` 3.023334, and `the` 3.023334. It matches no content token. Its nine unmatched query tokens are `what`, `position`, `man`, `who`, `served`, `prince`, `andrew`, `from`, and `1990-2001?`. Four verified conditions account for this: the man is not named in the query, so `neil` and `blair` are unavailable; the passage designates the queried royal only as "The Duke of York", so `prince` (idf 5.080793) and `andrew` (idf 5.301069) cannot match; the passage says "was Private Secretary and Treasurer" rather than `position` or `served`; and the shared date span is destroyed by the tokenizer, because the query form is `1990-2001?` with a hyphen-minus and a question mark while the passage form is `1990–2001.` with U+2013 and a period. Both `1990-2001?` and `1990-2001` are absent from the entire corpus vocabulary, so the date contributes exactly 0.000000 at baseline. Prince Andrew, Duke of York receives its 17.955882 from `prince` 8.020928, `of` 4.012681, `the` 3.710542, and `was` 2.211732; the query token `andrew` does not match its passage forms `andrew,` and `(andrew`. Among the passages above the rank-14 gold, the six scaffold tokens supply 41 to 62 percent of the total score: Royal Marriages Act 1772 53 percent, John Hartmann 41 percent, Man Booker International Prize 62 percent, Prince of Persia: The Sands of Time 50 percent, Andrew Murray (Guyanese boxer) 61 percent, Lord High Treasurer 58 percent, Jeff Hoover 53 percent, and Abteilungsleiter (NSDAP) 55 percent.

Factorial setting:
Every condition re-scores the same unchanged 4,937-passage pooled corpus under the same corpus order, first-title deduplication, `BM25Okapi` defaults, stable descending sort, and cutoff 5. Preprocessing factors are applied to both query and documents: P strips leading and trailing Unicode non-word characters from each lowercase whitespace token with `^\W+|\W+$`; E replaces U+2013 and U+2014 with a hyphen-minus; S removes exactly {`what`, `was`, `of`, `the`, `who`, `from`} from the query after tokenization; T prepends title plus one space to every indexed paragraph. Query-content factors preserve the original query and append oracle text: N appends `Neil Blair`, the name of the described man; A appends `Duke of York`, the designation actually used in the answer passage. All 16 P x E x S x T cells and all 4 N x A cells were run.

| Condition | Kind | Exact change | Neil Blair rank/score | Prince Andrew rank/score | Both top-5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | none | 2074 / 9.070003 | 14 / 17.955882 | no | exact reconstruction, max abs error 0 |
| T | single | title prepended | 2168 / 8.974816 | 11 / 19.028574 | no | title exclusion is not the mechanism |
| S | single | scaffold set removed | 4537 / 0.000000 | 18 / 8.020928 | no | removes the answer hop's only matches |
| S+T | combination | removal plus title | 4537 / 0.000000 | 10 / 9.071567 | no | title cannot repair the zeroed answer hop |
| E | single | dash normalized | 2074 / 9.069582 | 14 / 17.955421 | no | inert alone; period still blocks the date |
| E+T | combination | dash plus title | 2168 / 8.974392 | 11 / 19.028104 | no | inert |
| E+S | combination | dash plus removal | 4537 / 0.000000 | 18 / 8.020928 | no | inert plus harmful |
| E+S+T | three-factor combination | dash, removal, title | 4537 / 0.000000 | 10 / 9.071567 | no | inert plus harmful |
| P | single | boundary punctuation normalized | 2130 / 8.912919 | 1 / 25.775418 | no | repairs the alias hop only; answer hop worsens |
| P+T | combination | normalization plus title | 2220 / 8.818454 | 1 / 27.798630 | no | title still does not help the answer hop |
| P+S | combination | normalization plus removal | 4539 / 0.000000 | 1 / 15.901130 | no | answer hop still zero without E |
| P+S+T | three-factor combination | normalization, removal, title | 4539 / 0.000000 | 1 / 17.911879 | no | answer hop still zero without E |
| P+E | combination | punctuation plus dash normalized | 7 / 21.673599 | 1 / 25.773671 | no | strongest non-oracle pair; +2067 ranks |
| P+E+T | three-factor combination | punctuation, dash, title | 9 / 21.444087 | 1 / 27.796855 | no | title degrades the answer hop |
| P+E+S | three-factor combination | punctuation, dash, scaffold removal | 5 / 12.762256 | 1 / 15.901130 | yes | only non-oracle condition restoring both |
| P+E+S+T | four-factor combination | all preprocessing factors | 6 / 12.627217 | 1 / 17.911879 | no | adding title breaks the recovery |
| N | single | oracle name appended | 1 / 32.297984 | 15 / 17.955882 | no | repairs the answer hop only |
| A | single | oracle designation appended | 46 / 20.157917 | 2 / 30.042440 | no | repairs the alias hop only |
| N+A | combination | both oracle anchors | 1 / 43.385898 | 3 / 30.042440 | yes | two-anchor oracle rewrite restores both |
| P+E+N | combination | normalization plus oracle name | 1 / 43.854781 | 3 / 25.773671 | yes | oracle name is redundant given P+E+S |
| P+E+A | combination | normalization plus oracle designation | 2 / 37.340579 | 1 / 41.390089 | yes | oracle designation also sufficient with P+E |
| R2 | removal probe | date span removed | 1891 / 9.070003 | 12 / 17.955882 | no | gold scores unchanged; date contributes 0 |
| G2 | removal probe | generic noun `man` removed | 2051 / 9.070003 | 13 / 17.955882 | no | gold scores unchanged; drops two competitors |
| D | removal probe | query is the normalized date span alone | 1 / 12.762256 | 4487 / 0.000000 | no | the date span uniquely identifies the answer hop |
| D0 | removal probe | query is the raw date token alone | 4487 / 0.000000 | 4486 / 0.000000 | no | `1990-2001?` is absent from the corpus vocabulary |
| K | reachability probe | query is the oracle role wording | 1 / 45.707388 | 9 / 21.035651 | no | answer hop is lexically reachable |
| N x T, A x T | `not_run` | oracle anchors combined with title indexing | n/a | n/a | n/a | T is inert-to-negative in every run cell and cannot change the tie-break |
| stemming, lemmatization, phrase n-grams | `not_run` | additional analyzer features | n/a | n/a | n/a | they introduce mechanisms outside this tie-break |
| production analyzer policy | `not_run` | any deployable preprocessing configuration | n/a | n/a | n/a | the tested cells are diagnostics, not fixes |

Single-factor effects:
No single factor restores both required hops. P repairs the alias hop from 14 to 1 because it makes `andrew,` and `(andrew` match the query token `andrew`, but it moves the answer hop the wrong way, from 2074 to 2130. E is inert in both directions, 2074 to 2074 and 14 to 14, because normalizing the en dash still leaves the query question mark against the passage period. S is actively harmful to the answer hop, driving it from 2074 to 4537 at score 0.000000, because the scaffold tokens were its only matches. T is inert-to-negative for the answer hop, 2074 to 2168, so title exclusion is excluded as the mechanism. N, the condition predicted by the description-only reading, repairs only the answer hop, taking it to 1 while the alias hop drifts from 14 to 15. A repairs only the alias hop, taking it to 2 while the answer hop stays at 46.

Combination and interaction effects:
The decisive result is the P x E interaction. The single shared discriminating cue between the query and the answer passage differs on two independent surface dimensions at once, so neither normalization alone can align it; together they move the answer hop from 2074 to 7, a 2067-rank improvement obtained with no oracle content. Adding S to P+E is what completes the recovery to 5 and 1, because removing the six scaffold tokens withdraws roughly 8.9 points from the 17-token answer passage but roughly 10.5 points from long competitors such as Princess Henriette. P+E+S is therefore the only non-oracle condition that places both golds inside top five, and it is a three-factor interaction: P alone, E alone, S alone, P+S, and E+S all fail, and P+E stops at 7. On the oracle side, only the two-anchor N+A rewrite restores both, at 1 and 3. Once P+E is in place, either oracle anchor alone also suffices, at 1/3 and 2/1, which shows the anchors are substitutable for one another rather than jointly necessary.

Supported interpretation:
Minimal-preprocessing score distortion is the most specific verified primary. The query did contain a cue that uniquely identifies the answer passage within this corpus, and the verified tokenizer converted it into a token that occurs nowhere in the 4,937-passage vocabulary, reducing the answer passage's entire lexical signal to three low-IDF function words. Probe D is the decisive non-oracle demonstration: with the query reduced to the normalized date span, the one passage that contains it ranks 1 at 12.762256 while every other passage scores exactly 0.000000. Probes R2 and G2 confirm from the other direction that the raw date token and the generic noun `man` contribute nothing at all to either gold. `surface_form_tokenization_mismatch` records the concrete false negatives `1990-2001?` against `1990–2001.` and `andrew` against `andrew,` and `(andrew`. `generic_query_scaffold_score_inflation` records the exactly decomposed 41-to-62-percent contribution of non-repeated grammatical and interrogative tokens to passages that lack the decisive content, together with the fact that scaffold removal is a necessary component of the only non-oracle recovery. `description_only_bridge_entity` records that the required person is designated only by role and date span, a real condition that preprocessing does not remove. `entity_alias_reference_mismatch` records that the query and the answer passage designate the same royal by two different conventional names, so a matcher with no alias resolution obtains zero overlap on the two highest-IDF query tokens. `generic_term_lexical_crowding` records the residual verified competition that survives normalization: at P+E the answer hop is still behind Royal Marriages Act 1772, Princess Henriette, Joe Gilmore, Salvatore Testa, and Armie Hammer.

Closest competitor and tie-break:
Prefer `minimal_preprocessing_score_distortion` over `description_only_bridge_entity`. The described person genuinely is unnamed and the registry inclusion rule for the description-only code is met, but the single-factor oracle-name condition N restores only the answer hop and leaves the alias hop at 15. This is the same disqualifier D-020 applied to its condition B, and it is the exact inverse of D-017, where the single-factor oracle-name condition moved both required passages to 1 and 2. The preprocessing reading has non-oracle outcome-determinative evidence: probe D shows the query already carried a corpus-unique cue for the answer passage, P+E recovers 2067 ranks without adding oracle content, and P+E+S places both golds inside top five. Under the playbook tie-break order, an implementation-supported mechanism verified by exact reconstruction, per-token decomposition, and a non-oracle counterfactual is preferred over a code that describes the query's referring form. `description_only_bridge_entity` is therefore retained as the closest competitor and as a secondary contributing condition, following the D-012 and D-016 pattern.

Considered and not adopted:
`gold_chain_substitutability` is not adopted even though its inclusion rule is objectively met. Wedding dress of Sarah Ferguson at rank 70 and List of royal tours of Canada (21st century) at rank 22 both state "Prince Andrew, Duke of York" verbatim and therefore supply the same intermediate identity as the annotated second gold. Neither reaches top five in any tested condition, standing at 14 and 10 even under P+E, and the answer hop is unique in the corpus, so no complete alternative chain exists and the descriptor would add no outcome-relevant information. `proper_name_homonym_collision` is not adopted although Armie Hammer's "Prince Andrew Alcott" shares the full queried name form and Andrew Murray (Guyanese boxer) shares the forename, and both outrank the rank-14 gold; P alone moves the alias hop to rank 1, so this competitor family is not outcome-determinative, and `generic_term_lexical_crowding` already covers the residual competition. `cross_passage_conjunction_unresolved` is not adopted because P+E+S restores both golds without any cross-passage resolution of the alias identity, so the architectural boundary is real but not outcome-determinative in this unit. `repeated_function_word_amplification` is inapplicable because the query has no repeated token.

Not-run cells and attribution boundary:
All 16 cells of the defined P x E x S x T design and all 4 cells of the N x A design were run; there are no missing cells in either design. The `not_run` rows are N x T and A x T, additional analyzer features such as stemming, lemmatization, and phrase n-grams, and any deployable preprocessing policy. T is inert-to-negative for the answer hop in every cell in which it was run, 2074 to 2168 alone, 7 to 9 on top of P+E, and 5 to 6 on top of P+E+S, so crossing it with the oracle anchors cannot change the tie-break. Attribution is bounded as follows. The recovery to 5 and 1 must be credited to the P+E+S interaction and not to P, E, or S individually: P alone worsens the answer hop to 2130, E alone is inert at 2074, S alone drives it to score 0.000000, and the two-factor P+S and E+S cells also fail. The 2067-rank improvement at P+E must likewise be credited to the pair, because the date cue differs on two surface dimensions at once. Probe D establishes that the normalized date span is unique within this 4,937-passage corpus and does not license any general claim about date tokens. The diagnostics do not establish that any deployable preprocessing configuration would recover this case, do not make pooling or the per-question versus pooled contrast a causal category, and do not attribute the residual competition above rank 5 to any untested feature.

Boundary:
Two boundaries are recorded rather than closed. First, this is the fifth unit assigned `minimal_preprocessing_score_distortion`, and its verified coverage now spans repeated function-word amplification, punctuation-sensitive false negatives, non-repeated scaffold inflation, and Unicode dash mismatch; whether the category is becoming too broad is a vocabulary-audit question and must not be settled during the validation pass. Second, the only non-oracle recovery is a three-factor interaction that places the answer hop exactly at rank 5, so preprocessing is the strongest verified mechanism without being a complete account of the strict cutoff outcome.

Confidence:
Medium-high. The baseline is a zero-error reconstruction, all 16 P x E x S x T cells and all 4 N x A cells were run, every passage above the rank-14 gold was read in full, and one non-oracle condition restores both golds. The limitation is that the recovery is a three-factor interaction rather than a single factor, and it is marginal: the answer hop lands exactly on the cutoff at rank 5, and adding the title factor pushes it back to 6.

Speculation boundary:
Do not claim that any deployable analyzer, stemmer, phrase index, or stop-word list would recover this case; the tested cells are diagnostics only. Do not treat the oracle anchors N and A as proposed query rewrites, since they contain the answer entity and the bridge identity. Do not present the rank-5 or rank-7 counterfactual positions as an observed cutoff mechanism. Do not generalize probe D's corpus-uniqueness result beyond this 4,937-passage corpus. Do not describe the Dense success as the BM25 cause or compare Dense and BM25 score magnitudes. Do not treat pooling, gold missingness, cutoff proximity, retriever identity, or question type as a causal category.

## D-022 - Reclassify the Shadows in Flight / Ender's Game BM25 unit as an unresolved cross-passage conjunction

- **Date:** 2026-08-01
- **Status:** active
- **Decision:** For `5ade42b55542992fa25da717|bm25`, replace `near_title_collision`
  with `cross_passage_conjunction_unresolved` as the candidate primary mechanism.
  Retain `generic_term_lexical_crowding` and `cutoff_sensitive_near_miss`, and
  additionally adopt `description_only_bridge_entity`,
  `surface_form_tokenization_mismatch`, `repeated_content_word_amplification`,
  and `repeated_function_word_amplification` as secondary descriptors. Use
  `description_only_bridge_entity` as the closest competitor. This is the first
  unit in which `cross_passage_conjunction_unresolved` is used as a primary
  rather than as a secondary.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. D-022 introduces no new code
  name and requires no new registry entry: all six secondaries and the new
  primary already exist with complete registry entries or, for the primary,
  already appear in the primary inventory and as the provisional primary of queue
  item 24. `near_title_collision` is dropped from this row and, because no other
  unit carries it, now has no current `case_memos_v2.csv` row; it remains
  preserved in `case_memos_v1.csv` and in the primary vocabulary union as a
  historical first-pass name. D-022 does not merge, rename, demote, or freeze
  vocabulary, does not settle whether `cross_passage_conjunction_unresolved` is
  suited to primary use, and does not turn counts into prevalence.
- **Affected unit:** `5ade42b55542992fa25da717|bm25`.
- **References:** `references/bm25_implementation_reference.md`,
  `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5ade42b55542992fa25da717.md`.

### Complete case evidence

Observed evidence:
The question is `How many novels are there in the series of novels of which Shadows in Flight is the tenth novel ?` The annotated answer hop is Ender's Game (series), whose text states that the series "currently consists of fifteen novels". The annotated bridge hop is Shadows in Flight, whose text states that it "became the tenth novel published in the "Ender's Game" series". No single passage answers the question: the count lives in one passage and the series name that identifies that passage lives only in the other. Exact reconstruction reproduces all 50 stored top-50 titles in order with a maximum absolute score error of 0.000000 and places the golds at complete-corpus ranks 8 (42.931612) and 15 (39.521244); both are retrieved and both sit below the cutoff. The rank-5 score is 43.884407, so the answer hop is 0.952795 points, or 2.17 percent, below the cutoff. All 14 passages above the rank-15 gold were read in full and form two families. Six instantiate the query's own descriptive frame with the wrong work: "J" Is for Judgment 1 (49.954631) "is the tenth novel in Sue Grafton's "Alphabet" series of mystery novels"; Merlin Book 10: Shadows on the Stars 3 (46.292869) "The book is the tenth novel in the 12-book series known as Merlin Saga"; "Q" Is for Quarry 5 (43.884407) repeats that frame with the 17th novel; Persistence of Memory 6 (43.834946) "is the tenth novel by American teen author Amelia Atwater-Rhodes and is the fifth novel in her Den of Shadows series"; Generosity: An Enhancement 11 (41.674058) "is the tenth novel by American author Richard Powers"; and Castle Richmond 14 (39.846449) "It was his tenth novel". The other seven score mainly on generic book vocabulary: Walter Sorrells 2 (48.010526) recombines `flight` from the television series "Flight 29 Down" with `many` from "many novels"; Kyle Craig 4 (44.249441) is a fictional character in a "series of novels"; Lake District Mysteries 7 (43.304639) is "a series of detective novels"; Shadow War 9 (42.750949) concerns "the Shadows" in Babylon 5; and The Rest of the Robots 10 (42.251384), Nebula Award for Best Novel 12 (40.828268), and Crime and Punishment 13 (40.006089) are generic book and award pages. No passage above either gold states how many novels the Ender's Game series contains, so there is no complete plausible non-gold answer. A full-corpus substring scan shows `ender's game` and `orson scott card` each in exactly 2 of 4,937 passages, which are the two golds themselves, and `enderverse`, `fifteen novels`, `speaker for the dead`, and `shadows in flight` each in exactly 1. Neither hop has any substitute, so `gold_chain_substitutability` and `plausible_non_gold_answer` are both inapplicable and there is no evaluation ambiguity.

Verified implementation facts and exact reconstruction:
The reviewed BM25 indexes paragraph text only and does not index titles. Tokenization is `text.lower().split()` with no punctuation handling, stop-word removal, stemming, lemmatization, Unicode normalization, phrase matching, or entity-boundary preservation. Scoring uses `rank_bm25.BM25Okapi` at library defaults `k1=1.5`, `b=0.75`, `epsilon=0.25` under `rank-bm25==0.2.2`, which iterates the tokenized query and accumulates a contribution for every occurrence rather than deduplicating. The pooled corpus holds 4,937 passages with 4,937 unique titles and avgdl 90.88495037472148. Per-token decomposition weighted by query-token occurrence reconciles with `get_scores` to within 1.4e-14 on every inspected passage. The answer hop's 42.931612 is `novels` (query x2, tf 2) 13.127511, `the` (query x2, tf 13) 8.557494, `of` (query x2, tf 4) 6.892707, `series` 3.773988, `in` (query x2, tf 1) 3.739912, `novel` 3.532943, `is` 1.869956, and `which` 1.437102. It matches none of the query's discriminating tokens: `shadows` at idf 6.999727, `flight` at 5.149023, `tenth` at 5.301069, `how` at 4.956745, and `many`, `are`, `there`, `?`. Its rank therefore rests entirely on generic book vocabulary and unfiltered function words. Scaffold contributes 22.497170, or 52 percent of its score, and 19.190113 of that scaffold total, or 85.3 percent, comes from the repeated tokens `in`, `the`, and `of`. The bridge hop's 39.521244 is `the` (query x2, tf 7) 7.836454, `in` (query x2, tf 4) 6.892707, `shadows` 6.826829, `tenth` 5.170129, `novel` (tf 2) 5.082934, `flight` 5.021839, and `is` 2.690353; it fails to match `novels`, because its text uses the singular `novel` twice, and `series`, because its text carries only `series.` and `series"`. The query contains four repeated tokens, `novels`, `in`, `the`, and `of`. One observed null is recorded: the question has a space before its final question mark, so `?` is a standalone query token whose idf 8.098947 is the highest of any query token, yet it occurs in exactly 1 of 4,937 passages and in none of the golds or inspected competitors, contributing exactly 0. High idf is not the same as discriminating power.

Gold, provenance, and comparison evidence:
Pooled BM25 ranks the golds 8 and 15, a strict Any@5 failure. Per-question BM25 over the item's own ten context passages, reconstructed here, ranks the answer hop 2 and the bridge hop 7, which is not a strict Any@5 failure; the formal results file records `any_evidence_recall@5` as 1 for `per_question` and 0 for `pooled`, and `full_evidence_recall@5` as 0 for both. Of the seven passages above the answer hop in the pooled index, four are original HotpotQA distractors ("J" Is for Judgment, Walter Sorrells, Merlin Book 10: Shadows on the Stars, Persistence of Memory) and three are introduced by pooling (Kyle Craig, "Q" Is for Quarry, Lake District Mysteries). Removal probe X3 shows that dropping only those three returns the answer hop to exactly rank 5. Pooling therefore materially affects whether this unit crosses the cutoff, unlike D-021 where per-question also failed and pooling was excluded as a source. Corpus setting nonetheless remains provenance under D-003 and is not used as a causal category: the mechanism is fully present in the ten-passage index, where the bridge hop is still 7th of 10 and no top-five passage supplies the count. Pooled Dense ranks the golds 31 and 1 and per-question Dense ranks them 7 and 1, so Dense is stronger on the bridge hop and weaker on the answer hop. Dense is used only as reachability evidence, is not written as the cause of the BM25 ordering, and the two score magnitudes are not compared.

Factorial diagnostic status: run. Baseline binds the pooled 4,937-passage index, first-occurrence title deduplication, `rank-bm25==0.2.2` `BM25Okapi` defaults, stable descending sort, and cutoff 5. Factors: **P** is two-sided boundary-punctuation stripping; **M** is crude two-sided suffix stemming removing a trailing `s` from tokens of length 4 or more not ending in `ss`; **S** removes the exact query-side set {`are`, `how`, `in`, `is`, `of`, `the`, `which`}; **S2** widens that set with {`there`, `many`, `?`}; **T** prepends the title into each indexed passage; **Rc** collapses the repeated content token `novels` to one occurrence; **Rf** collapses the repeated function tokens `in`, `the`, `of`; **X1** to **X3** drop named competitors from the index; **Q1** to **Q5** are reduced-query probes; **K1** and **K2** are reachability probes; **N1** appends the oracle series name `Ender's Game series` and **N2** the oracle work name `Shadows in Flight`. P, M, S, S2, T, Rc, Rf, X, Q, and K are non-oracle. N1 and N2 are oracle diagnostics containing the hidden series identity and are not deployable rewrites. All ranks are complete-corpus ranks over the same unchanged candidate set, except X1 to X3 where the stated passages are removed.

| Condition | Single or combination | Exact change | Answer hop rank/score | Bridge hop rank/score | Both top 5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | none | 8 / 42.931612 | 15 / 39.521244 | no | exact reconstruction, max abs error 0.000000 |
| T | single | title prepended into the index | 10 / 42.964314 | 4 / 45.172571 | no | title exclusion is not inert here, but it helps only the bridge hop |
| S | single | scaffold set removed | 7 / 20.434442 | 5 / 22.101731 | no | the only single factor that improves both hops |
| M | single | crude suffix stemming | 16 / 43.066332 | 5 / 48.514878 | no | repairs the bridge hop, harms the answer hop |
| P | single | boundary punctuation stripped | 7 / 43.781416 | 14 / 41.628907 | no | weakly positive on both |
| ST | combination | S plus title | 7 / 20.448673 | 1 / 27.331101 | no | bridge hop first, answer hop unmoved |
| MT | combination | M plus title | 16 / 43.093907 | 3 / 54.060543 | no | answer hop still 16 |
| MS | combination | M plus S | 12 / 20.569358 | 1 / 31.095528 | no | bridge hop first, answer hop worse |
| PT | combination | P plus title | 8 / 44.016083 | 5 / 47.079325 | no | answer hop unmoved |
| PS | combination | P plus S | 8 / 21.682900 | 5 / 24.516812 | no | answer hop unmoved |
| PM | combination | P plus M | 13 / 43.616236 | 3 / 52.851042 | no | answer hop worse |
| MST | three-factor | M, S, title | 12 / 20.578367 | 1 / 36.219158 | no | answer hop worse |
| PST | three-factor | P, S, title | 7 / 21.900318 | 1 / 29.552461 | no | best non-oracle position for the answer hop |
| PMT | three-factor | P, M, title | 13 / 43.845900 | 3 / 56.961479 | no | answer hop worse |
| PMS | three-factor | P, M, S | 10 / 21.537298 | 1 / 35.755142 | no | answer hop worse |
| PMST | four-factor | all preprocessing | 10 / 21.749567 | 1 / 39.451069 | no | answer hop worse |
| Rc | single | repeated `novels` collapsed | 12 / 36.367857 | 6 / 39.521244 | no | harms the answer hop, helps the bridge hop |
| Rf | single | repeated `in`, `the`, `of` collapsed | 7 / 33.336556 | 11 / 32.156664 | no | opposite sign to Rc |
| Rc+Rf | combination | all four repeats collapsed | 11 / 26.772801 | 5 / 32.156664 | no | still no joint recovery |
| M+Rc | combination | M plus Rc | 16 / 43.066332 | 5 / 48.514878 | no | Rc adds nothing over M |
| M+Rc+Rf | combination | M plus both dedups | 14 / 33.471365 | 4 / 41.150367 | no | answer hop still 14 |
| PMS+Rc | combination | PMS plus Rc | 10 / 21.537298 | 1 / 35.755142 | no | identical to PMS to the digit |
| PMS+Rc+Rf | combination | PMS plus both dedups | 10 / 21.537298 | 1 / 35.755142 | no | R is fully dominated by S |
| PMST+Rc+Rf | combination | all preprocessing plus both dedups | 10 / 21.749567 | 1 / 39.451069 | no | identical to PMST |
| S2 | single | widened scaffold set | 7 / 20.434442 | 5 / 22.101731 | no | identical to S |
| PMS2T | four-factor | P, M, widened S, title | 9 / 21.749567 | 1 / 39.451069 | no | marginal gain over PMST |
| PMS2T+Rc+Rf | combination | above plus both dedups | 9 / 21.749567 | 1 / 39.451069 | no | R adds nothing |
| X1 | removal probe | drop Merlin Book 10: Shadows on the Stars | 8 / 42.941939 | 14 / 39.817754 | no | the named near-title competitor is not decisive |
| X2 | removal probe | drop the five tenth-novel frame passages | 6 / 43.165891 | 9 / 40.372275 | no | the frame family as a whole is not decisive |
| X3 | removal probe | drop the three pooling-introduced rivals | 5 / 43.148830 | 12 / 39.541961 | no | answer hop returns to exactly rank 5 |
| X2+X3 | removal probe | drop all eight | 3 / 43.397720 | 6 / 40.393856 | no | still no joint recovery |
| Q1 | reduced-query probe | query is the work name alone | 3887 / 1.869956 | 1 / 15.295021 | no | the bridge hop is uniquely reachable from its own name |
| Q2 | reduced-query probe | query is `shadows flight` | 4186 / 0.000000 | 1 / 11.848668 | no | same result without the function word |
| Q3 | reduced-query probe | query is `tenth novel` | 126 / 3.532943 | 6 / 10.253063 | no | the descriptive frame is generic; no gold in its top five |
| Q4 | reduced-query probe | query is the counting clause alone | 7 / 16.486446 | 1772 / 7.364580 | no | the answer-seeking clause alone cannot surface the answer hop |
| Q5 | reduced-query probe | query is `novels` alone | 5 / 6.563755 | 4187 / 0.000000 | no | one generic repeated noun already reproduces the answer hop's position |
| K1 | reachability probe | query is `Ender's Game series` | 1 / 11.672885 | 4273 / 0.000000 | no | the answer hop is uniquely reachable from the series name |
| K2 | reachability probe | query is `Enderverse Orson Scott Card` | 3 / 11.665618 | 2 / 11.665618 | yes | both passages are jointly reachable from shared rare terms |
| N1 | single, oracle | oracle series name appended | 1 / 54.604497 | 20 / 39.521244 | no | repairs the answer hop only; the bridge hop drifts from 15 to 20 |
| N2 | single, oracle | oracle work name appended | 11 / 44.801568 | 4 / 54.816265 | no | repairs the bridge hop only |
| N1+N2 | combination, oracle | both oracle names | 5 / 56.474453 | 6 / 54.816265 | no | even both anchors together fail |
| N1+S | combination, oracle | oracle series name plus S | 1 / 32.107327 | 8 / 22.101731 | no | still one hop |
| N1+N2+S | combination, oracle | both anchors plus S | 3 / 32.107327 | 2 / 33.950399 | yes | first condition of any kind to recover both |
| N1+N2+ST | combination, oracle | both anchors plus S and title | 2 / 38.847514 | 1 / 44.396136 | yes | strongest condition, entirely oracle-dependent |
| remaining 36 cells of P x M x S x T x Rc x Rf | `not_run` | full six-factor crossing | n/a | n/a | n/a | Rc and Rf are dominated by P, M, and S in every run combination; PMS+Rc equals PMS+Rc+Rf to the digit |
| E | `not_run` here | en and em dash normalization | n/a | n/a | n/a | the harness ran it and found it completely inert; the corpus and query contain no such characters |
| stemming, lemmatization, phrase n-grams | `not_run` | real analyzer features | n/a | n/a | n/a | they introduce mechanisms outside this tie-break; M is an explicitly defined crude suffix rule, not a model of any production analyzer |
| oracle-by-indexing crossings beyond N1+N2+ST | `not_run` | N x T variants | n/a | n/a | n/a | T is inert-to-negative for the answer hop in every non-oracle cell |
| production analyzer policy | `not_run` | any deployable configuration | n/a | n/a | n/a | the tested cells are diagnostics, not fixes |

Single-factor effects:
No single factor places both required hops in the top five, and every factor that helps one hop harms the other. M moves the bridge hop from 15 to 5 and the answer hop from 8 to 16. T moves the bridge hop from 15 to 4 and the answer hop from 8 to 10; title exclusion is therefore not inert in this unit, unlike D-019, D-020, and D-021, but it also does not help the hop that fails hardest. Rc moves the bridge hop from 15 to 6 and the answer hop from 8 to 12, because the repeated `novels` is the answer hop's single largest score component at 13.127511, or 31 percent of its score. Rf moves the answer hop from 8 to 7 and the bridge hop from 15 to 11, the opposite sign to Rc. N1 moves the answer hop to 1 and the bridge hop from 15 to 20. N2 moves the bridge hop to 4 and the answer hop from 8 to 11. P is weakly positive on both, 8 to 7 and 15 to 14. S is the only single factor that improves both, 8 to 7 and 15 to 5, and it still does not recover the pair.

Combination and interaction effects:
The two hops are antagonistic, and the evidence for that is positive rather than merely the absence of a single fix. Their matched query-token sets are nearly disjoint: the answer hop matches {`novels`, `series`, `of`, `which`}, which the bridge hop entirely misses; the bridge hop matches {`shadows`, `flight`, `tenth`}, which the answer hop entirely misses; and only {`the`, `in`, `is`, `novel`} are shared. Six separate factors carry opposite signs across the two hops. Probe Q1 shows the bridge hop is uniquely reachable from its own name at rank 1, and probe K1 shows the answer hop is uniquely reachable from the series name at rank 1, yet the series name occurs nowhere in the query and only inside the bridge passage. Consequently each single oracle anchor rescues exactly one hop and degrades the other, N1+N2 together still fails at 5 and 6, and joint recovery requires N1+N2+S at 3 and 2 or N1+N2+ST at 2 and 1. Every non-oracle condition that places a gold first, namely ST, MS, MST, PST, PMS, and PMST, does so for the bridge hop while leaving the answer hop between 7 and 12. The repeated token `novels` plays a double role: it is simultaneously the answer hop's largest single score component and the largest single component of the purely generic competitors Lake District Mysteries (15.559850), Walter Sorrells (14.541960), and "Q" Is for Quarry (13.585525), which is why Rc improves one hop and worsens the other.

Supported interpretation:
`cross_passage_conjunction_unresolved` is the most specific verified primary. The question names the bridge work but never names the series that carries the answer; the series name exists only inside the bridge passage, and the verified implementation scores each passage independently with no cross-passage or iterative-hop reasoning, so it cannot resolve the name in one passage and carry it into scoring the other. Probes Q1 and K1 establish that each passage is individually and uniquely reachable from the corresponding name, which isolates the failure to the step that joins them. Because the answer hop has no discriminating query token of its own, it must compete on generic book vocabulary alone, which probe Q5 demonstrates directly: the single word `novels` already reproduces its position at rank 5. `description_only_bridge_entity` records that the answer-bearing series is designated only by the description "the series of novels of which Shadows in Flight is the tenth novel". `surface_form_tokenization_mismatch` records two concrete false negatives on the bridge hop, `novels` against the passage's singular `novel` and `series` against `series.` and `series"`, with M alone moving that hop from 15 to 5 and MS to 1. `generic_term_lexical_crowding` records the verified competition from the two distractor families, all fourteen of which were read in full. `repeated_content_word_amplification` records that `novels` occurs twice in the query and is scored twice, contributing 13.127511 to the answer hop and up to 15.559850 to a purely generic competitor, with Rc producing a measurable ranking effect. `repeated_function_word_amplification` records that `in`, `the`, and `of` each occur twice and supply 19.190113 of the answer hop's 22.497170 scaffold contribution, with Rf producing a measurable and oppositely signed effect. `cutoff_sensitive_near_miss` records evaluation fragility only: the answer hop is 0.952795 points, or 2.17 percent, below the rank-5 score, it has no substitute, and two independent lines of evidence, probe X3 and the per-question reconstruction, place it at rank 5 or better.

Closest competitor and tie-break:
Prefer `cross_passage_conjunction_unresolved` over `description_only_bridge_entity`. The description-only reading satisfies its inclusion rule, because the answer-bearing series is genuinely unnamed in the query, but the single-factor oracle-name condition N1 restores only the answer hop, at 1 and 20, with the bridge hop drifting from 15 to 20. That is the disqualifier D-020 applied to its condition B and D-021 applied to its condition N, and the inverse of D-017, where the same single-factor condition produced 1 and 2; this is its third application. The cross-passage reading instead explains the distinctive structure of this unit, and its registry exclude conditions do not fire: no single passage answers the question, no substitute completes the chain inside the evaluated set, the judgment does not rest on the mere presence of two annotated golds but on the observed antagonism and the Q1 and K1 reachability results, and the retrieval stage performs no joint cross-passage reasoning. The provisional primary `near_title_collision` is rejected on direct evidence: this implementation does not index titles, the shared token `shadows` in the competing passage comes from its body text rather than its title, and removal probe X1 shows that dropping that passage moves the result only from 8 and 15 to 8 and 14. That also resolves the uncertainty the original note itself raised about whether "Shadows on the Stars" was the decisive distractor; it was not. `minimal_preprocessing_score_distortion` is rejected as primary because preprocessing repairs only the bridge hop and actively harms the answer hop, M taking it from 8 to 16, and because the answer hop has no surface-form mismatch to repair at all; its evidence is retained through the narrower `surface_form_tokenization_mismatch`. `generic_term_lexical_crowding` is retained as a secondary under its own exclude rule, which defers to a more specific established mechanism. `description_only_bridge_entity` is retained as the closest competitor and as a secondary contributing condition, following D-012, D-016, and D-021.

Considered and not adopted:
`generic_query_scaffold_score_inflation` is not adopted although scaffold contributes between 38 and 74 percent of the score of every inspected passage and S is the only single factor that improves both hops. Its registry exclude rule defers to `repeated_function_word_amplification` when repeated occurrences are the material mechanism, and here 19.190113 of the answer hop's 22.497170 scaffold contribution, or 85.3 percent, comes from the repeated tokens `in`, `the`, and `of`. Only 3.307058 comes from the non-repeated scaffold tokens `is` and `which`. `gold_chain_substitutability` is not adopted because its inclusion rule is not met at all: `ender's game` and `orson scott card` each occur in exactly two passages, which are the two golds themselves, so neither hop has any substitute. `plausible_non_gold_answer` is not adopted for the same reason; no inspected passage states the Ender's Game series novel count. `proper_name_homonym_collision` is not adopted because the competitors are distinct works sharing generic vocabulary rather than distinct entities sharing a proper-name form, and because X1 shows the closest such competitor is not outcome-determinative. `question_frame_semantic_crowding` is not adopted because its exclude rule directs lexical retrievers whose contribution is established by score decomposition to `generic_term_lexical_crowding` instead. `compound_two_sided_crowding` was considered because the two hops fail for different reasons, but the playbook's §4.10 precedent directs this exact shape, where each single oracle anchor rescues one hop and only both together recover, to the architectural reading rather than to a compound with an independent mechanism on each side.

Not-run cells and attribution boundary:
All 16 cells of the defined P x M x S x T design and all 4 cells of the Rc x Rf design were run; there are no missing cells in either design. The `not_run` rows are the remaining 36 cells of the full six-factor crossing, the E factor, real stemming, lemmatization and phrase n-grams, oracle-by-indexing crossings beyond N1+N2+ST, and any deployable analyzer policy; reasons are recorded in the table. Attribution is bounded as follows. Do not attribute this failure to any single factor: six factors carry opposite signs on the two hops. Do not credit the N1+N2+S recovery to N1, N2, or S individually, since N1+N2 alone fails at 5 and 6 and S alone fails at 7 and 5, and N1 and N2 are oracle diagnostics containing the hidden series identity. Do not present M's repair of the bridge hop as the case mechanism, since the same factor drives the answer hop from 8 to 16. Do not treat corpus setting as a causal category; the defensible statement is that pooling adds three rivals above the answer hop, that removing exactly those three restores it to rank 5, and that the same mechanism is already present in the ten-passage per-question index where the bridge hop ranks 7 of 10 and no top-five passage supplies the count. Do not describe any removed passage as having caused the failure; X1 is the direct counter-demonstration. Do not generalize probes Q1, Q5, or K1 beyond this 4,937-passage corpus. Do not treat counterfactual ranks near the cutoff as an observed cutoff mechanism. Do not read M's harm to the answer hop as evidence that stemming is generally harmful.

Boundary:
Three boundaries are recorded rather than closed. First, this is the first unit to use `cross_passage_conjunction_unresolved` as a primary rather than a secondary; D-017 and D-020 both used it as a secondary alongside a different primary, and whether the descriptor is suited to primary use belongs to the vocabulary audit. Second, pooling materially affects whether this unit crosses the cutoff, since per-question BM25 places the answer hop at rank 2 and is not a strict Any@5 failure while pooled BM25 places it at 8, and X3 shows that dropping the three pooling-introduced rivals alone restores rank 5. This is recorded as provenance under D-003 and deliberately not promoted to a causal category, but it narrows the attribution compared with D-021. Third, no non-oracle condition recovers both hops, so the primary is the strongest structural account rather than a demonstrated sufficient cause.

Confidence:
Medium. The baseline is a zero-error reconstruction, all 16 P x M x S x T cells and all 4 Rc x Rf cells were run together with eight further combinations, four removal probes, five reduced-query probes, two reachability probes, and six oracle conditions, and every one of the 14 passages above the rank-15 gold was read in full. Probe X1 is a clean falsification of the provisional primary, and probes Q1, Q5, and K1 are non-oracle. The limitation is that no non-oracle condition recovers both hops, so the primary is a structural account rather than a demonstrated sufficient cause, and that pooling is materially implicated in the metric outcome, which narrows attribution relative to D-021.

Speculation boundary:
Do not claim that any deployable analyzer, stemmer, stop-word list, or phrase index would recover this case; the tested cells are diagnostics only. Do not treat N1 or N2 as proposed query rewrites, since they supply the hidden series identity. Do not treat the X1 to X3 corpus deletions as repair proposals. Do not present the counterfactual rank-5, rank-6, or rank-7 positions as an observed cutoff mechanism. Do not generalize the corpus-uniqueness results of Q1, Q5, or K1 beyond this 4,937-passage corpus. Do not describe the Dense bridge-hop success as the BM25 cause or compare Dense and BM25 score magnitudes. Do not treat pooling, gold missingness, cutoff proximity, retriever identity, or question type as a causal category. Do not claim that the high idf of the standalone `?` token affected any ranking; it contributes exactly 0.

## D-023 - Reclassify the 1920 film-series Dense unit as a description-only bridge entity

- **Date:** 2026-08-02
- **Status:** active
- **Decision:** For `5ade69e455429975fa854ec5|dense`, replace
  `named_entity_anchor_distraction` with `description_only_bridge_entity` as the
  candidate primary mechanism. Remove both provisional secondaries,
  `low_information_title` and `film_series_entity_collision`, and adopt
  `peripheral_passage_content_dilution`, `gold_chain_substitutability`,
  `generic_person_semantic_neighborhood`, and `cutoff_sensitive_near_miss` as
  secondary descriptors. Use `peripheral_passage_content_dilution` as the closest
  competitor. This is the second unit in which `description_only_bridge_entity`
  is used as a primary rather than a secondary, after D-017, and the second time
  the D-020 single-factor oracle-name test is passed rather than failed.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. D-023 registers one new
  secondary descriptor, `peripheral_passage_content_dilution`, with a complete
  entry whose inclusion rule requires both a controlled text ablation and a
  length-matched control ablation. It adds a usage note to
  `description_only_bridge_entity` recording the second primary use without
  changing that descriptor's definition, inclusion rule, or exclusion rule.
  `named_entity_anchor_distraction` is dropped from this row and, because no
  other unit carries it, now has no current `case_memos_v2.csv` row; it remains
  preserved in `case_memos_v1.csv` and in the primary vocabulary union as a
  historical first-pass name, the same treatment D-022 gave `near_title_collision`
  and D-021 gave `weak_lexical_name_anchor`. `low_information_title` and
  `film_series_entity_collision` were each carried only by this row and are
  likewise preserved in `case_memos_v1.csv` and in the secondary union without a
  current v2 row. D-023 does not merge, rename, demote, or freeze vocabulary,
  does not settle whether `description_only_bridge_entity` is suited to primary
  use or whether its `for lexical retrieval` wording should be widened, and does
  not turn counts into prevalence.
- **Affected unit:** `5ade69e455429975fa854ec5|dense`.
- **References:** `references/dense_implementation_reference.md`,
  `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ade69e455429975fa854ec5.md`.

### Complete case evidence

Observed evidence:
The question is `What director worked with Vikram Bhatt on a film starring actors Rajneesh Duggal and Adah Sharma?` The annotated answer hop is 1920 (film series), whose text states that the series "is directed by Vikram Bhatt, Bhushan Patel and Tinu Suresh Desai, in each of three films". The annotated bridge hop is 1920 (film), whose text states that it is "written and directed by Vikram Bhatt" and "stars debutant actors Rajneesh Duggal and Adah Sharma". The query never names the film; it designates it only by the description "a film starring actors Rajneesh Duggal and Adah Sharma". Exact reconstruction reproduces all 50 stored top-50 titles in order with a maximum absolute score error of 3.576e-07 and places the golds at complete-corpus ranks 7 (0.495152) and 32 (0.400140); both are retrieved and both sit below the cutoff. The rank-5 score is Udanchhoo at 0.516518, so the answer hop is 0.021367 points, or 4.137 percent, below the cutoff and the bridge hop is 0.116378 points, or 22.531 percent, below it. All 31 passages above the rank-32 gold were read in full. Only four of the 30 non-gold passages among them name any queried entity: Rajneesh Duggal 1 (0.601388) is the actor's own biography and states "He made his Bollywood debut with Vikram Bhatt's super-hit horror thriller "1920""; Ankahee (2006 film) 2 (0.549072) is a different Vikram Bhatt film with a different cast; Udanchhoo 5 (0.516518) is a different Rajneesh Duggal film; and Spark (2014 film) 22 (0.439687) is another Rajneesh Duggal film. The remaining 26 name none of Vikram Bhatt, Rajneesh Duggal, or Adah Sharma; they are Indian and regional cinema biographies such as Siddhartha Jadhav 3, Paresh Mokashi 4, Nagesh Bhonsle 6, Shoba Chandrasekhar 8, Anil Chatterjee 9, Utpal Dutt 11, and A. C. Tirulokchandar 17, unrelated Indian films such as Rupaye Dus Karod 12, Ithu Engal Neethi 13, and Neethiyin Marupakkam 30, and Bharatpur district 28, which entered the pooled index from another item. A full-corpus substring scan shows `bhushan patel` and `tinu suresh desai` each in exactly 1 of 4,937 passages, which is the answer hop itself, so the answer hop has no substitute and no passage supplies a complete plausible non-gold answer. `adah sharma` occurs in exactly 2 passages, the bridge hop and Phhir; Phhir names both queried actors but names no director and does not mention Vikram Bhatt, and it ranks 55, so it satisfies part of the description while supplying no answer. `vikram bhatt` occurs in 6 passages. The rank-1 passage Rajneesh Duggal is therefore not a distractor but an evidence-bearing substitute for the bridge hop, because it names the bridge entity `1920` and links it to Vikram Bhatt inside the top five. The pair Rajneesh Duggal and 1920 (film series) forms a complete alternative chain, but that chain is not contained inside the cutoff because the answer hop is at rank 7.

Verified implementation facts and exact reconstruction:
The reviewed Dense retriever is a symmetric `sentence-transformers/all-MiniLM-L6-v2` bi-encoder with one shared encoder for queries and passages, no role prefix, explicit row-wise L2 normalization, dot product equal to cosine, attention-mask-aware mean pooling, a 256-token maximum sequence length, stable descending sort, and no reranker or cross-passage reasoning in the main run. It encodes `[p.text for p in paragraphs]` and does not encode titles, so a displayed title is not evidence that its tokens contributed to similarity. The pooled corpus holds 4,937 passages with 4,937 unique titles under first-occurrence title deduplication. Both golds are well inside the sequence limit at 108 and 145 model tokens, so truncation is excluded for them; one competitor, Nagesh Bhonsle at 326 tokens, is truncated. Reconstruction reproduces the stored top-50 title order with 0 of 50 mismatches at a maximum absolute score error of 3.576e-07, the same order of magnitude as the 2.384e-07 recorded by D-020, which is consistent with float32 accumulation rather than with a different model. The repository does not pin the model revision or the transformers and torch versions, so identity of model contract and numerical agreement are asserted, not identity of environment. Per-token contribution decomposition was not performed and is not derivable from a cosine ranking; the harness raises `NotImplementedError` on the Dense path by design, and that guard was not bypassed. Every claim about passage content in this entry rests on passage-level controlled text ablation and never on token-level attribution.

Gold, provenance, and comparison evidence:
Pooled Dense ranks the golds 7 and 32, a strict Any@5 failure. Per-question Dense over the item's own ten context passages, reconstructed here and asserted equal to the official ordering title by title, ranks the answer hop 4 and the bridge hop 6, which is not a strict Any@5 failure; the formal results file records `any_evidence_recall@5` as 1 for `per_question` and 0 for `pooled`, and `full_evidence_recall@5` as 0 for both. Of the six passages above the answer hop in the pooled index, three are in the item's own context (Rajneesh Duggal, Ankahee (2006 film), Udanchhoo) and exactly three are introduced by pooling (Siddhartha Jadhav, Paresh Mokashi, Nagesh Bhonsle). Removal probe X2 shows that dropping only those three returns the answer hop to exactly rank 4, reproducing its per-question rank. This is the second unit after D-022 in which per-question and pooled disagree on Any@5, and the arithmetic is the same in both: exactly three pooling-introduced rivals separate the answer hop from the cutoff. Corpus setting nonetheless remains provenance under D-003 and is not used as a causal category; the mechanism is fully present in the ten-passage per-question index, where the bridge hop is still 6th of 10 and no top-five passage names the film. Pooled BM25 ranks the golds 13 and 1 and per-question BM25 ranks them 9 and 2, so BM25 is far stronger on the bridge hop and weaker on the answer hop. BM25 is used only as reachability evidence, is not written as the cause of the Dense ordering, and the two score magnitudes are not compared.

Factorial diagnostic status: run. Baseline binds the pooled 4,937-passage index, first-occurrence title deduplication, the `all-MiniLM-L6-v2` encoder with explicit L2 normalization and cosine scoring, stable descending sort, and cutoff 5. Factors: **F** deletes the answer-type frame `What director worked with `; **V** deletes `Vikram Bhatt `; **A** deletes ` Rajneesh Duggal and Adah Sharma`; **A1** deletes only `Rajneesh Duggal and `; **A2** deletes only ` and Adah Sharma`; **S1** replaces `What director` with `Who`; **S2** replaces `director` with `film`; **T** prepends the title into every indexed passage and re-encodes the whole corpus; **L1**, **L1b**, **L2**, **L2d**, and **L2e** are index-side controlled text ablations replacing one gold passage's text with a verbatim subset of its own sentences; **L2c** is the length-matched control retaining only that passage's non-query-relevant plot sentences; **X1** to **X4** drop named competitors from the index; **Q1** to **Q10** are reduced-query reachability probes; **N1** to **N5** append or insert the oracle bridge name in five surface forms. F, V, A, A1, A2, S1, S2, T, X, and Q are non-oracle. The L series adds no text and injects no answer information but requires knowing which passage is gold, so it is recorded as a third intervention class, a gold-targeted index-side ablation, and is not a deployable fix. N1 to N5 are oracle diagnostics containing the hidden film identity and are not deployable rewrites. All ranks are complete-corpus ranks over the same unchanged candidate set, except X1 to X4 where the stated passages are removed. Thirty-seven conditions and ten probes were run.

| Condition | Single or combination | Exact change | Answer hop rank/score | Bridge hop rank/score | Both top 5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | none | 7 / 0.495152 | 32 / 0.400140 | no | exact reconstruction, max abs error 3.576e-07 |
| F | single | answer-type frame deleted | 6 / 0.498257 | 35 / 0.389800 | no | nearly inert; the frame is not the mechanism |
| V | single | `Vikram Bhatt` deleted | 21 / 0.444728 | 36 / 0.411955 | no | harms both; the director name is a positive contributor |
| A | single | both actor names deleted | 4 / 0.491537 | 36 / 0.363284 | no | answer hop enters top five, bridge hop worsens |
| A1 | single | only `Rajneesh Duggal` deleted | 5 / 0.493448 | 44 / 0.372795 | no | the two actor names are not one factor |
| A2 | single | only `Adah Sharma` deleted | 10 / 0.479488 | 37 / 0.390612 | no | opposite sign to A1 on the answer hop |
| S1 | single | `What director` replaced by `Who` | 14 / 0.448645 | 35 / 0.370954 | no | removing the answer-type word harms the answer hop |
| S2 | single | `director` replaced by `film` | 5 / 0.521816 | 24 / 0.434123 | no | helps both, still no joint recovery |
| F+V | combination | frame plus `Vikram Bhatt` deleted | 14 / 0.438614 | 29 / 0.393367 | no | dominated by V |
| F+A | combination | frame plus actor names deleted | 4 / 0.504183 | 35 / 0.369448 | no | equals A on the answer hop |
| V+A | combination | `Vikram Bhatt` plus actor names deleted | 25 / 0.426993 | 79 / 0.379836 | no | worst non-degenerate cell |
| F+V+A | three-factor | all three spans deleted | 10 / 0.403267 | 69 / 0.356659 | no | query retains no entity cue |
| T | single, indexing | title prepended, full corpus re-encode | 10 / 0.469105 | 41 / 0.376438 | no | negative for both; title exclusion is not the mechanism |
| L2 | single, gold-targeted ablation | bridge passage reduced to its two query-relevant sentences | 8 / 0.495152 | 1 / 0.624424 | no | largest single movement in the unit |
| L2c | control ablation | bridge passage reduced to two plot sentences of comparable length | 7 / 0.495152 | 50 / 0.361773 | no | length-matched control; the effect is content, not length |
| L2d | single, gold-targeted ablation | bridge passage minus its final sentence | 7 / 0.495152 | 29 / 0.415966 | no | dose-response step |
| L2e | single, gold-targeted ablation | bridge passage first four sentences | 7 / 0.495152 | 13 / 0.465330 | no | dose-response step |
| L1 | single, gold-targeted ablation | answer passage reduced to its first two sentences | 7 / 0.488923 | 32 / 0.400140 | no | inert; the answer hop is not dilution-limited |
| L1b | single, gold-targeted ablation | answer passage reduced to its first sentence | 47 / 0.368533 | 31 / 0.400140 | no | strongly harmful; confirms the asymmetry |
| L1+L2 | combination, gold-targeted | both gold passages reduced | 8 / 0.488923 | 1 / 0.624424 | no | L1 adds nothing to L2 |
| X1 | removal probe | drop the `Rajneesh Duggal` biography | 6 / 0.495152 | 31 / 0.400140 | no | the named anchor is not decisive |
| X2 | removal probe | drop the three pooling-introduced rivals | 4 / 0.495152 | 29 / 0.400140 | no | answer hop returns to exactly its per-question rank 4 |
| X3 | removal probe | drop all four person biographies in the top six | 3 / 0.495152 | 28 / 0.400140 | no | displacement only |
| X4 | removal probe | drop all six passages above the answer hop | 1 / 0.495152 | 26 / 0.400140 | no | even the trivial upper bound leaves the bridge hop at 26 |
| A+L2 | combination, non-oracle plus ablation | actor names deleted, bridge passage reduced | 5 / 0.491537 | 1 / 0.514646 | yes | first joint recovery without oracle content |
| F+L2 | combination | frame deleted, bridge passage reduced | 7 / 0.498257 | 2 / 0.635759 | no | F cannot substitute for A |
| F+A+L2 | combination | frame and actor names deleted, bridge passage reduced | 5 / 0.504183 | 1 / 0.535820 | yes | no gain over A+L2 |
| X2+L2 | combination | three pooling rivals dropped, bridge passage reduced | 5 / 0.495152 | 1 / 0.624424 | yes | joint recovery with no query change |
| X2+A | combination | three pooling rivals dropped, actor names deleted | 2 / 0.491537 | 33 / 0.363284 | no | bridge hop untouched without the ablation |
| X2+L1+L2 | combination | three pooling rivals dropped, both golds reduced | 5 / 0.488923 | 1 / 0.624424 | yes | L1 again adds nothing |
| X2+A+L2 | combination | three pooling rivals dropped, actor names deleted, bridge passage reduced | 3 / 0.491537 | 1 / 0.514646 | yes | strongest non-oracle cell |
| N1 | single, oracle | full title `1920 (film series)` appended | 1 / 0.663116 | 3 / 0.591554 | yes | single factor recovers both hops |
| N2 | single, oracle | full title `1920 (film)` appended | 1 / 0.665735 | 3 / 0.593925 | yes | same result from the other title |
| N3 | single, oracle | bare name `1920` appended | 1 / 0.640248 | 3 / 0.568981 | yes | the bare name is as effective as the disambiguated title |
| N4 | single, oracle | natural insertion `on the film 1920` | 1 / 0.690604 | 3 / 0.621328 | yes | strongest oracle form |
| N5 | single, oracle | natural insertion `on the 1920 film series` | 1 / 0.657567 | 3 / 0.592587 | yes | series wording works equally |
| N4+F | combination, oracle | natural insertion plus frame deletion | 1 / 0.676159 | 3 / 0.584968 | yes | F contributes nothing once the name is present |
| L x T crossings | `not_run` | ablation crossed with title indexing | n/a | n/a | n/a | T is negative for both hops alone and each crossing costs a full-corpus re-encode |
| N x L crossings | `not_run` | oracle name crossed with ablation | n/a | n/a | n/a | N alone already recovers both hops, so the crossing carries no discriminating information |
| V x L2 and V x A x L2 | `not_run` | `Vikram Bhatt` deletion crossed with ablation | n/a | n/a | n/a | V is negative for both hops and no hypothesis predicts a sign reversal |
| removal probes on ranks 8 to 31 | `not_run` | further displacement probes | n/a | n/a | n/a | the bridge hop's deficit of 0.116378 makes displacement incapable of reaching the top five |
| per-question factorial | `not_run` | any factor on the ten-passage index | n/a | n/a | n/a | per-question already places the answer hop at rank 4; the diagnostic question concerns the pooled setting |
| Dense per-token decomposition | `not_run` | token-level contribution table | n/a | n/a | n/a | refused by design; not derivable from a cosine ranking without attribution |

| Probe | Query | Answer hop | Bridge hop | Interpretation |
|---|---|---:|---:|---|
| Q1 | `Rajneesh Duggal and Adah Sharma` | 102 / 0.258475 | 205 / 0.215314 | the actor names alone reach neither gold; the actor's biography ranks 1 |
| Q2 | `Adah Sharma` | 196 / 0.246542 | 806 / 0.155149 | the corpus has no Adah Sharma page and the name alone is unproductive |
| Q3 | `Rajneesh Duggal` | 236 / 0.210660 | 273 / 0.201718 | same for the other actor |
| Q4 | `1920` | 1 / 0.533558 | 2 / 0.463880 | the bare bridge name alone ranks both golds first and second |
| Q5 | `director` | 30 / 0.302080 | 251 / 0.217413 | the answer-type word retrieves director biographies, not the golds |
| Q6 | `Vikram Bhatt` | 18 / 0.333600 | 347 / 0.178692 | the director name alone favours the actor's biography |
| Q7 | `What director worked with` | 94 / 0.268891 | 439 / 0.193704 | the frame alone retrieves director biographies |
| Q8 | `a film starring actors Rajneesh Duggal and Adah Sharma` | 21 / 0.437301 | 26 / 0.429894 | the description alone retrieves the actors, not the described film |
| Q9 | `Indian horror film 1920` | 2 / 0.790643 | 1 / 0.791056 | both golds are jointly reachable once the name is present |
| Q10 | `1920 film series` | 1 / 0.736901 | 2 / 0.684484 | same result from the series wording |

Single-factor effects:
No single factor of any class places both required hops in the top five except the oracle name conditions. F is nearly inert, 7 to 6 and 32 to 35. V harms both, 7 to 21 and 32 to 36, so the director's name is a real positive contributor to the baseline. A moves the answer hop into the top five at 4 while pushing the bridge hop from 32 to 36. A1 and A2 are asymmetric: deleting only `Rajneesh Duggal` moves the answer hop to 5 while deleting only `Adah Sharma` moves it to 10. S1 harms the answer hop, 7 to 14; S2 helps both, 7 to 5 and 32 to 24. T is negative for both, 7 to 10 and 32 to 41, so title exclusion is excluded as the mechanism, as in D-019, D-020, and D-021 and unlike D-022. L2 moves the bridge hop from 32 to 1 while leaving the answer hop's score unchanged and displacing it to 8. L1 is inert for the answer hop and L1b is strongly harmful at 47, so the answer hop is not dilution-limited. X1 is nearly inert. X2, X3, and X4 move the answer hop to 4, 3, and 1 by displacement only, with the bridge hop never better than 26. Each of N1 to N5 places both hops inside the top five at 1 and 3.

Combination and interaction effects:
The decisive interaction is A x L2. A repairs the answer hop and harms the bridge hop; L2 repairs the bridge hop and does nothing for the answer hop. Neither alone recovers the pair, but A+L2 reaches 5 and 1, F+A+L2 reaches 5 and 1, X2+L2 reaches 5 and 1, X2+L1+L2 reaches 5 and 1, and X2+A+L2 reaches 3 and 1. This unit therefore differs from D-021 and D-022 in that non-oracle and gold-targeted combinations do recover both hops. The antagonism is partial rather than total: A and F carry opposite signs across the hops, but V, A2, and T harm both and S2 helps both, so this is not the fully antagonistic structure D-022 recorded. The L2 result is established by dose-response together with a length control and is the first dilution-shaped claim this project accepts. Reducing the bridge passage from its full 145 model tokens to the six sentences before its last moves it from 32 to 29; to its first four sentences, from 32 to 13; and to the two sentences carrying the query's constraints, 49 model tokens, to 1 at 0.624424. The control L2c replaces the same passage with two of its plot sentences of comparable length, 43 model tokens, naming none of the queried entities, and the passage falls to 50 at 0.361773. The effect is therefore attributable to which sentences remain and not to passage length.

Supported interpretation:
`description_only_bridge_entity` is the most specific verified primary. The question requires a specific film, names it nowhere, and reaches it only through the description "a film starring actors Rajneesh Duggal and Adah Sharma". Supplying the name is the only single factor of any class that places both hops inside the top five, and it does so in all five surface forms tested. Two independent probes separate absence of the name from weakness of the name. Probe Q4 reduces the query to `1920` alone and the two golds rank 1 and 2, so the bare name is highly discriminating in this corpus even though the numeral occurs in 48 passages. Probe Q8 reduces the query to the description alone and the two passages that actually satisfy it rank 21 and 26 while the actor's own biography ranks 1 and Udanchhoo 2, so the description retrieves the actors rather than the described film. `peripheral_passage_content_dilution` records the second, independently established condition: the bridge passage states every query constraint verbatim yet ranks 32, and the controlled ablation with its length-matched control shows that its non-query-relevant narrative sentences measurably depress its similarity. `gold_chain_substitutability` records that the rank-1 passage supplies the bridge hop's intermediate fact by naming `1920` as Vikram Bhatt's horror thriller starring Rajneesh Duggal. `generic_person_semantic_neighborhood` records the observed output pattern that Siddhartha Jadhav, Paresh Mokashi, and Nagesh Bhonsle occupy three of the top six positions as Indian-cinema person biographies naming none of the queried entities. `cutoff_sensitive_near_miss` records evaluation fragility only: the answer hop is 0.021367 points, or 4.137 percent, below the rank-5 score, it has no substitute anywhere in the corpus, and two independent lines of evidence, probe X2 and the per-question reconstruction, place it at rank 4. This follows D-022, which retained the descriptor where the gap was measured and small and no substitute existed, and is distinguished from D-015, which removed it because the affected gold was already substitutable inside the top five; here the substitutable hop and the near-miss hop are different passages.

Closest competitor and tie-break:
Prefer `description_only_bridge_entity` over `peripheral_passage_content_dilution`. The dilution reading satisfies its inclusion rule and produces the single largest movement observed in this unit, taking the bridge hop from 32 to 1, but L2 alone leaves the answer hop at 8 and cannot recover the pair; it requires A or X2 as a partner. The description-only reading is the only account whose single-factor intervention recovers both hops, under five independent surface forms of the same intervention. This applies the same standard D-021 used when it rejected `description_only_bridge_entity` as primary, in the opposite direction: an inclusion rule can be met while the descriptor loses the tie-break, and here the descriptor wins on exactly the criterion that defeated it in D-020, D-021, and D-022. The provisional primary `named_entity_anchor_distraction` is rejected on direct evidence. Removal probe X1 drops the named actor's own biography and moves the result only from 7 and 32 to 6 and 31, so the anchor is not outcome-determinative. Condition A shows the actor names do cost the answer hop three ranks, 7 to 4, but the same deletion harms the bridge hop, 32 to 36, so removing the anchor does not repair the unit. The rank-1 passage the descriptor treats as a distraction is in fact an evidence-bearing substitute for one required hop, which contradicts the name directly.

Considered and not adopted:
`low_information_title` is not adopted, and both readings of the name are excluded by explicit conditions. The indexing reading fails because the verified implementation encodes paragraph text only and condition T, which prepends every title and re-encodes the whole corpus, moves both golds the wrong way, 7 to 10 and 32 to 41. The semantic reading fails because probe Q4 ranks the two golds 1 and 2 from the bare name alone and because appending the bare `1920` in condition N3 gives 1 and 3, identical to appending the full disambiguated titles in N1 and N2. `film_series_entity_collision` is not adopted because there is no third confusable entity in the corpus, both parties to the supposed collision are annotated golds, and the verified implementation scores every passage independently so one gold cannot displace another except by outranking it; the observed inversion in which the series outranks the film is fully accounted for by the L2 ablation and its control. `cross_passage_conjunction_unresolved` is not adopted although its inclusion rule is met, because the single-factor oracle-name test recovers both hops, which locates the deficit in the missing name rather than in the joining step, and because the antagonism signature D-022 relied on does not hold here. `question_frame_semantic_crowding` is not adopted because its exclude rule fires: probe Q8 shows that the descriptive referent cue alone reproduces five of the six baseline top-six passages, so the competition is produced by the decisive referent cue itself and belongs to the primary mechanism rather than to a separate framing effect. `possible_type_mismatch` is not adopted because condition F is nearly inert at 6 and 35, so no counterfactual supports a type-alignment cause. `plausible_non_gold_answer` and `gold_chain_not_unique` are not adopted because `bhushan patel` and `tinu suresh desai` each occur in exactly one passage, which is the answer hop itself.

Not-run cells and attribution boundary:
The defined F x V x A design was run complete at all eight cells, and the L, N, X, and Q families were run as listed. The `not_run` rows are the L x T crossings, the N x L crossings, V x L2 and V x A x L2, removal probes on ranks 8 to 31, any factorial on the per-question index, and Dense per-token decomposition; reasons are recorded in the table. Attribution is bounded as follows. Do not make any token-level claim. The L series is a passage-level text ablation and supports only the statement that removing those sentences raises that passage's cosine similarity to this query; it does not establish that the encoder attended to, weighted, or averaged away any token, and no attribution experiment was run. Do not treat N1 to N5 as proposed query rewrites, since they supply the hidden film identity. Do not treat the L series as a deployable fix either, since it requires knowing which passage is gold. Do not treat the X removals as repair proposals. Do not present BM25's rank-1 placement of the bridge hop as the cause of the Dense ordering or compare Dense and BM25 score magnitudes. Do not treat corpus setting as a causal category; the defensible statement is that pooling adds exactly three rivals above the answer hop, that removing exactly those three restores it to rank 4, and that the mechanism is already present in the ten-passage per-question index. Do not treat cutoff proximity, rank, retriever identity, question type, or gold missingness as causal. Do not generalize the corpus-uniqueness results of Q4, Q8, or the substring scans beyond this 4,937-passage corpus.

Boundary:
Four boundaries are recorded rather than closed. First, this is the second unit to use `description_only_bridge_entity` as a primary rather than a secondary, after D-017, and both are Dense; the registry definition still says the missing name leaves no anchor "for lexical retrieval", wording that does not cover a bi-encoder. The wording is not amended here, because definition changes are reserved for the vocabulary audit; a usage note is added instead. Second, `gold_chain_substitutability` is adopted for a substitute that verifies one of the two actor constraints: Rajneesh Duggal names the film and links it to Vikram Bhatt but does not mention Adah Sharma. The intermediate fact the chain requires is supplied in full and the film so identified is unique in the corpus, but a stricter reading of the registry's exclusion for a looser interpretation than the gold could reject it; the boundary is recorded and the descriptor is adopted. Third, `peripheral_passage_content_dilution` is a new descriptor whose inclusion rule deliberately requires both an ablation and a length-matched control, because the project has until now recorded every dilution-shaped claim as speculation under D-013 and D-015; whether that gate is correctly placed belongs to the vocabulary audit. Fourth, the observed neighborhood is not purely person-typed: about half the non-naming competitors above the bridge hop are unrelated Indian films rather than biographies, and `generic_person_semantic_neighborhood` covers only the biography half. No second descriptor was added for the film half, to avoid multiplying near-synonyms during the validation pass.

Confidence:
Medium-high. The baseline reproduces the stored top-50 order with zero title mismatches at 3.576e-07, the per-question ordering is reproduced and asserted equal to the official file title by title, all eight cells of the defined F x V x A design were run together with 29 further conditions and 10 probes, and all 31 passages above the rank-32 gold were read in full. The primary rests on a single-factor intervention that succeeds in five independent surface forms and on two probes, Q4 and Q8, that separate absence of the name from weakness of the name. Probe X1 is a clean falsification of the provisional primary. The limitation is that the single-factor intervention which recovers both hops is oracle, that the strongest non-oracle movement, L2, is a gold-targeted index-side ablation rather than a deployable condition, and that no purely query-side non-oracle condition recovers both hops.

Speculation boundary:
Do not claim that mean pooling averaged away the cast sentence, that any token was diluted, or that the encoder down-weighted any part of the bridge passage; only passage-level ablation was performed and token-level attribution is not derivable from a cosine ranking. Do not claim that the encoder prefers person biographies because the question asks for a director; probe Q5 shows that `director` alone retrieves director biographies, but condition F is nearly inert and no counterfactual connects that neighborhood to this failure. Do not claim that the numeral `1920` is difficult for the encoder; probe Q4 falsifies it directly. Do not treat the identification of Bhushan Patel and Tinu Suresh Desai as the answer entities as observed evidence; the HotpotQA answer string is absent from every read-only artifact available here and that identification is an inference from the answer hop's own text. Do not treat the question's wording as verified: it asks about a director who worked with Vikram Bhatt "on a film", while the answer hop states that the co-directors directed later films of the same series, and no condition was run on that reading.

## D-024 - Reclassify the General Mills / Robert Smith BM25 unit as an unresolved cross-passage conjunction

- **Date:** 2026-08-03
- **Status:** active
- **Decision:** For `5ae057fd55429945ae959328|bm25`, replace
  `compound_two_sided_crowding` with `cross_passage_conjunction_unresolved` as the
  candidate primary mechanism. Remove the provisional secondary
  `proper_name_homonym_collision`, retain `generic_term_lexical_crowding`, and
  adopt `description_only_bridge_entity` as a secondary descriptor. Use
  `description_only_bridge_entity` as the closest competitor. This is the second
  unit in which `cross_passage_conjunction_unresolved` is used as a primary rather
  than a secondary, after D-022, and the first BM25 unit to use it that way.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. D-024 registers no new
  descriptor. It adds this affected unit and D-024 as a decision source to
  `description_only_bridge_entity` and `generic_term_lexical_crowding`, and it
  extends the existing usage note on `cross_passage_conjunction_unresolved` to
  record a second primary use, in each case without changing any definition,
  inclusion rule, or exclusion rule. `compound_two_sided_crowding` is dropped from
  this row but remains the primary of `5a8d93ad554299653c1aa13d|dense` under
  D-018, so unlike `near_title_collision` in D-022 and
  `named_entity_anchor_distraction` in D-023 it keeps a current
  `case_memos_v2.csv` row. `proper_name_homonym_collision` likewise remains a
  registered secondary of that same Dense unit. D-024 does not merge, rename,
  demote, or freeze vocabulary, does not settle whether
  `cross_passage_conjunction_unresolved` is suited to primary use, does not decide
  whether the new precondition recorded below belongs in the
  `description_only_bridge_entity` exclude rule, and does not turn counts into
  prevalence.
- **Affected unit:** `5ae057fd55429945ae959328|bm25`.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5ae057fd55429945ae959328.md`.

### Complete case evidence

Observed evidence:
The question is ` Robert Smith founded the multinational company headquartered in what city?` The annotated bridge hop is Robert Smith (Illinois politician), whose 31-token text states `Smith founded General Mills in 1856.` and so supplies the company identity. The annotated answer hop is General Mills, whose 75-token text states `It is headquartered in Golden Valley, Minnesota, a suburb of Minneapolis.` and so supplies the city. No single passage answers the question: the company identity lives in one passage and the city lives in the other. Exact reconstruction reproduces all 50 stored top-50 titles in order with a maximum absolute score error of 0.000000 and places the golds at complete-corpus ranks 8 (23.567502) for the bridge hop and 16 (19.841500) for the answer hop; both are retrieved and both sit below the cutoff. The rank-5 score is Tata Consultancy Services at 24.991523, so the bridge hop is 1.424021 points, or 5.698 percent, below the cutoff and the answer hop is 5.150023 points, or 20.607 percent, below it. All 14 non-gold passages above the rank-16 answer hop were read in full and form two families. Ten are generic multinational-company profiles that instantiate the query's descriptive facet and name no Robert Smith: RetailMeNot 1 (30.370645) `is an American multinational company headquartered in Austin`; Stevanato Group 2 (30.051240) `is an Italian multinational company headquartered in Piombino Dese`; Henkel 3 (28.060072) `is a multinational company active both in the consumer and industrial sector`; Namsung electronics 4 (26.151412) `is a South Korean multinational company headquartered in Seoul`; Tata Consultancy Services 5 (24.991523) `is an Indian multinational information technology (IT) service, consulting and business solutions company Headquartered in Mumbai`; Equinix 6 (24.625021) `is an American multinational company headquartered in Redwood City`; Carrefour 10 (22.930214) `is a French multinational retailer headquartered in Boulogne Billancourt`; Teleperformance 12 (22.600543) `is a multinational company headquartered in France`; PepsiCo 13 (22.470887) `is an American multinational food, snack, and beverage corporation headquartered in Purchase, New York`; and Kellogg's 15 (20.121490) `is an American multinational food manufacturing company headquartered in Battle Creek, Michigan`. Four share a name token with the query but none of them founded a multinational company: Physicians Mutual 7 (23.986692), whose founder is Edwin E. Elliott and whose only Robert is the chief executive Robert A. Reed; Hyrum W. Smith 9 (22.987720), who `founded the Franklin Quest Company in 1981`; Corey Smith (artist) 11 (22.873606), who `founded the snowboard company Spring Break Snowboards`; and Robert's American Gourmet Food 14 (20.488790), `Founded by businessman Robert Ehrlich in 1986`. Every one of the seven passages above the bridge hop belongs to the generic-company family; not one is a Smith homonym. A full-corpus substring scan shows `robert smith` in exactly 1 of 4,937 passages, which is the bridge hop itself; `general mills` in exactly 2, which are the two golds; and `golden valley` in exactly 1, which is the answer hop. Neither hop has any substitute, no complete alternative chain exists, and no passage supplies a complete plausible non-gold answer.

Per-token decomposition, reconciling with `get_scores` to within 1e-9 on every inspected passage:
The query tokenizes to robert, smith, founded, the, multinational, company, headquartered, in, what, city? with no repeated token, so repeated-occurrence amplification does not apply here; this is the second BM25 unit after D-021 in which it does not. The two golds match almost disjoint token sets. The answer hop's 19.841500 is multinational 5.947945, headquartered 5.288716, company 3.621793, the 2.902058, and in 2.080988, with robert, smith and founded contributing exactly 0. The bridge hop's 23.567502 is smith at document tf 4 giving 10.973922, robert 5.071737, founded 4.796412, and in 2.725430, with the, multinational, company and headquartered contributing exactly 0. The two matched sets share only `in`. The rank-1 passage RetailMeNot draws 23.351998 of its 30.370645, or 76.9 percent, from the four generic content tokens multinational, company, headquartered and founded, 7.018647 from the three scaffold tokens in, the and what, and exactly 0 from the name tokens. The query token `city?` is absent from the corpus vocabulary and therefore contributes exactly 0 to every passage; after boundary normalization `city` occurs in 412 passages and in neither gold, so the answer-type facet is inert in both forms. Corpus idf values are multinational 5.480131, smith 5.222190, headquartered 4.872752, what 4.263913, robert 3.567920, founded 3.374232, company 3.336934, and the and in 1.917315.

Verified implementation facts and exact reconstruction:
BM25 indexes paragraph text only and not titles, so a displayed title is not evidence that its tokens contributed to the score. Both documents and queries use `text.lower().split()` with no punctuation removal, stop-word removal, stemming, lemmatization, Unicode normalization, phrase matching, entity recognition, or initial expansion. Scoring is `rank-bm25==0.2.2` `BM25Okapi` with the library defaults k1=1.5, b=0.75, epsilon=0.25, iterating the tokenized query list and accumulating one contribution per occurrence. The pooled index holds 4,937 deduplicated passages with avgdl 90.88495037472148. Each passage is scored independently; there is no reranker, no threshold, and no cross-passage or iterative-hop reasoning, which is the implementation fact the primary rests on. Reconstruction reproduces the stored top-50 title order with 0 of 50 mismatches at a maximum absolute score error of exactly 0.000000, matching the zero-error reconstructions of D-019, D-021 and D-022. Two implementation facts are specific to this unit. First, `city?` is not in the corpus vocabulary. Second, the answer passage tokenizes `General Mills, Inc.,` into general, `mills,` and `inc.,`, so its only mills-bearing token carries a comma, whereas the bridge passage writes `founded General Mills in 1856.` and carries the bare token `mills`; six passages carry bare `mills` and three carry `mills,`. The per-token decomposition was asserted equal to `get_scores` on the two golds and on the whole reconstructed top 16 before any contribution was quoted, following the D-022 reconciliation requirement.

Gold, provenance, and comparison evidence:
Pooled BM25 ranks the golds 16 and 8, a strict Any@5 failure. Per-question BM25 over the item's own ten paragraphs, reconstructed here and asserted equal to the official ordering title by title, ranks the bridge hop 1 and the answer hop 10 of 10, which is not a strict Any@5 failure; the formal results file records `any_evidence_recall@5` as 1 for `per_question` and 0 for `pooled`, and `full_evidence_recall@5` as 0 for both. This is the third unit after D-022 and D-023 in which per-question and pooled disagree on Any@5, but the first in which the disagreement is not reducible to added competitors. Only two pooling-introduced passages sit above the bridge hop, Tata Consultancy Services at 5 and Physicians Mutual at 7, and removal probe X5 drops exactly those two and reaches only rank 6, not rank 5, whereas D-022's X3 and D-023's X2 each restored the cutoff exactly by dropping three. The driver here is instead the idf scale of a ten-document index in which six of the ten paragraphs are company profiles: idf(smith) is 0.762140 per-question against 5.222190 pooled, idf(multinational) is 0.421076 against 5.480131, idf(headquartered) is 0.421076 against 4.872752, and avgdl is 58.600000 against 90.884950. In the small index the descriptive facet carries almost no weight and the name tokens dominate, which is why the bridge hop ranks 1 there. The answer hop ranks last of ten in that same index, so its own failure is already complete in HotpotQA's own distractor set and is not pooling-induced at all. Corpus setting remains provenance under D-003 and is not used as a causal category. Dense complete-corpus ranks are 1 (0.624810) for the bridge hop and 98 (0.233225) for the answer hop; the answer hop's absence from the stored Dense top 50 is a stored-window miss and not absence from the corpus. Dense pooled `any_evidence_recall@5` is 1 and `full_evidence_recall@5` is 0, so Dense fails the same conjunction with the mirror-image gap. Dense is used only as reachability evidence, is not written as the cause of the BM25 ordering, and the two score magnitudes are not compared.

Factorial diagnostic status: run. Baseline binds the pooled 4,937-passage index, first-occurrence title deduplication, `text.lower().split()` tokenization, `rank-bm25==0.2.2` `BM25Okapi` at k1=1.5, b=0.75, epsilon=0.25, descending score sort, and cutoff 5. Factors: **P** normalizes leading and trailing punctuation on both sides; **E** maps en dash, em dash and minus sign to hyphen on both sides; **S** removes the exact scaffold set {in, the, what} from the query; **T** prepends the title into every indexed passage; **M** applies crude two-sided suffix stemming; **Pq** applies P to the query only and **Pd** to the documents only; **Q1** to **Q9** are reduced-query probes; **R1** to **R8** delete exactly one query token or one named token group; **K1** to **K3** are reachability probes; **X1** to **X7** are index-side removal probes; **N1** to **N4** and **Nboth** inject oracle names. P, E, S, T, M, Pq, Pd, Q and R are non-oracle and query-side or preprocessing-side. The X series adds no text and injects no answer information but requires knowing in advance which passages are rivals, so it is recorded as an index-side removal probe, a diagnostic and not a deployable fix, alongside the third intervention class D-023 introduced. K1, K1P, K2, K3 and the N series contain the hidden company identity or the hidden answer city and are oracle diagnostics, not deployable rewrites. All ranks are complete-corpus ranks over the same unchanged candidate set, except the X rows where the stated passages are removed. All 16 P x E x S x T cells were run; 59 conditions in total.

| Condition | Kind | Exact change | General Mills rank/score | Robert Smith (Illinois politician) rank/score | Both top-5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | original query, original index | 16 / 19.841500 | 8 / 23.567502 | no | exact reconstruction, 0 of 50 titles, max abs error 0.000000 |
| T | non-oracle, indexing | title prepended into the index | 17 / 19.900073 | 5 / 25.013761 | no | title exclusion excluded for the answer hop; signs oppose |
| S | non-oracle | scaffold {in, the, what} removed | 15 / 14.858454 | 5 / 20.842072 | no | both improve slightly, neither recovers |
| ST | non-oracle | S+T | 15 / 14.904132 | 4 / 22.341436 | no | bridge hop enters, answer hop does not |
| E | non-oracle | dash normalization | 16 / 19.841270 | 8 / 23.567376 | no | inert; no Unicode dash in query or golds |
| ET | non-oracle | E+T | 17 / 19.899838 | 5 / 25.013636 | no | E adds nothing to T |
| ES | non-oracle | E+S | 15 / 14.858454 | 5 / 20.842072 | no | identical to S |
| EST | non-oracle | E+S+T | 15 / 14.904132 | 4 / 22.341436 | no | identical to ST |
| P | non-oracle | boundary punctuation, both sides | 18 / 19.470404 | 12 / 22.345811 | no | negative for both; no surface deficit to repair |
| PT | non-oracle | P+T | 19 / 19.528532 | 10 / 23.741647 | no | negative for both |
| PS | non-oracle | P+S | 16 / 14.578626 | 6 / 19.649697 | no | no recovery |
| PST | non-oracle | P+S+T | 17 / 14.624237 | 5 / 21.099385 | no | bridge hop enters only |
| PE | non-oracle | P+E | 18 / 19.469539 | 12 / 22.345334 | no | E adds nothing to P, unlike D-021 |
| PET | non-oracle | P+E+T | 19 / 19.527651 | 10 / 23.741172 | no | negative for both |
| PES | non-oracle | P+E+S | 16 / 14.578626 | 6 / 19.649697 | no | identical to PS |
| PEST | non-oracle | P+E+S+T | 17 / 14.624237 | 5 / 21.099385 | no | identical to PST |
| M | non-oracle | crude two-sided suffix stemming | 17 / 19.300206 | 9 / 22.781348 | no | negative for both |
| PM | non-oracle | P+M | 19 / 18.805001 | 12 / 21.484497 | no | negative for both |
| PMS | non-oracle | P+M+S | 16 / 13.919168 | 7 / 18.791659 | no | no recovery |
| PMST | non-oracle | P+M+S+T | 16 / 13.962716 | 6 / 20.220004 | no | no recovery |
| Pq | non-oracle | P applied to the query only | 16 / 19.841500 | 9 / 23.567502 | no | answer hop bit-identical to baseline; bridge hop worse |
| Pd | non-oracle | P applied to the documents only | 17 / 19.470404 | 10 / 22.345811 | no | negative for both |
| Q1 | non-oracle probe | query = `Robert Smith` | 2060 / 0.000000 | 1 / 16.045660 | no | the bridge hop is uniquely reachable from its own name |
| Q2 | non-oracle probe | query = `Robert Smith founded` | 2151 / 0.000000 | 1 / 20.842072 | no | same, with the relation token added |
| Q3 | non-oracle probe | query = the description half alone | 11 / 19.841500 | 4696 / 2.725430 | no | the description does not reach the answer hop |
| Q4 | non-oracle probe | query = `multinational company headquartered` | 11 / 14.858454 | 2067 / 0.000000 | no | positions 1 to 11 all satisfy the description; answer hop last |
| Q5 | non-oracle probe | query = `founded` | 2064 / 0.000000 | 5 / 4.796412 | no | the relation token alone favours the bridge hop |
| Q6 | non-oracle probe | query = `city?` | 1967 / 0.000000 | 1966 / 0.000000 | no | corpus-absent token, contributes exactly 0 everywhere |
| Q7 | non-oracle probe | query = `city` | 2157 / 0.000000 | 2156 / 0.000000 | no | normalizing it still matches neither gold |
| Q8 | non-oracle probe | query = `headquartered` | 20 / 5.288716 | 1984 / 0.000000 | no | the most specific description token alone gives 20 |
| Q9 | non-oracle probe | multinational and headquartered deleted from the full query | 427 / 8.604839 | 1 / 23.567502 | no | the two facets are in direct competition |
| R1 | non-oracle | remove `multinational` | 48 / 13.893555 | 2 / 23.567502 | no | opposite signs |
| R2 | non-oracle | remove `company` | 15 / 16.219707 | 3 / 23.567502 | no | documented exception: helps both |
| R3 | non-oracle | remove `headquartered` | 31 / 14.552784 | 2 / 23.567502 | no | opposite signs |
| R4 | non-oracle | remove `multinational`, `company`, `headquartered` | 3951 / 4.983046 | 1 / 23.567502 | no | opposite signs, largest magnitude |
| R5 | non-oracle | remove `robert`, `smith` | 12 / 19.841500 | 946 / 7.521842 | no | opposite signs, reverse direction |
| R6 | non-oracle | remove `founded` | 11 / 19.841500 | 17 / 18.771090 | no | opposite signs, reverse direction |
| R7 | non-oracle | remove `city?` | 16 / 19.841500 | 8 / 23.567502 | no | bit-identical to baseline; the token is exactly inert |
| R8 | non-oracle | remove `multinational`, `headquartered` | 427 / 8.604839 | 1 / 23.567502 | no | opposite signs |
| K1 | oracle probe | query = `General Mills` | 51 / 3.923010 | 1 / 14.564592 | no | the answer hop is not reachable from its own bare name |
| K1P | oracle probe + P | query = `General Mills` under P | 4 / 10.556421 | 1 / 13.937044 | yes | one punctuation normalization moves it from 51 to 4 |
| K2 | oracle probe | query = `Robert Smith (Illinois politician)` | 2060 / 0.000000 | 1 / 16.045660 | no | the bridge title adds nothing beyond the two name tokens |
| K3 | oracle probe | query = `Golden Valley` | 49 / 4.728733 | 2031 / 0.000000 | no | the answer city is corpus-unique yet gives only 49 |
| X1 | removal probe | drop `Hyrum W. Smith` and `Corey Smith (artist)` | 14 / 19.854032 | 8 / 23.749540 | no | falsifies proper_name_homonym_collision; bridge hop unmoved |
| X2 | removal probe | drop all 4 name-sharing rivals above the answer hop | 12 / 19.895608 | 7 / 23.787455 | no | the name-overlap family is not outcome-determinative |
| X3 | removal probe | drop the 6 generic-company rivals above the bridge hop | 10 / 20.449471 | 2 / 23.599443 | no | that family alone drives the bridge hop's demotion |
| X4 | removal probe | drop the 10 generic-company rivals above the answer hop | 5 / 20.973881 | 2 / 23.595157 | yes | the outcome-determinative family, with all 4 name rivals kept |
| X5 | removal probe | drop the 2 pooling-introduced rivals above the bridge hop | 14 / 19.968150 | 6 / 23.585391 | no | pooling removal does not restore the cutoff here |
| X6 | removal probe | drop the 6 pooling-introduced rivals above the answer hop | 10 / 20.271477 | 6 / 23.601413 | no | same conclusion for the answer hop |
| X7 | removal probe | drop all 14 rivals above the answer hop | 2 / 21.040580 | 1 / 23.816022 | yes | upper bound on the displacement account |
| N1 | oracle | append `General Mills` | 9 / 23.764510 | 1 / 38.132094 | no | the single-factor oracle-name test fails |
| N1P | oracle + P | append `General Mills`, plus P | 2 / 30.026825 | 1 / 36.282855 | yes | the decisive interaction |
| N1S | oracle + S | append `General Mills`, plus S | 8 / 18.781464 | 1 / 35.406664 | no | S is not the missing partner |
| N1PS | oracle + P + S | append `General Mills`, plus P and S | 2 / 25.135047 | 1 / 33.586741 | yes | S adds nothing to N1P |
| N2 | oracle | append `Robert Smith (Illinois politician)` | 21 / 19.841500 | 1 / 39.613161 | no | the bridge title harms the answer hop |
| Nboth | oracle | append both gold titles | 13 / 23.764510 | 1 / 54.177754 | no | even both anchors together fail, as in D-022 |
| N3 | oracle | substitute `the multinational company` with `General Mills` | 20 / 11.292714 | 1 / 38.132094 | no | the natural insertion form also fails |
| N3P | oracle + P | N3 plus P | 5 / 17.876426 | 1 / 36.282855 | yes | recovery at the cutoff edge |
| N4 | oracle | append `Golden Valley Minnesota` | 7 / 24.570233 | 9 / 23.567502 | no | even the answer city does not recover the answer hop |
| oracle x T | `not_run` | N1T, N3T, K1T | n/a | n/a | n/a | T is inert-to-negative for the answer hop in every run cell |
| oracle x M | `not_run` | N1M and relatives | n/a | n/a | n/a | M is negative for both hops alone and in every P combination |
| removal x preprocessing | `not_run` | X4 x P and relatives | n/a | n/a | n/a | X4 already recovers both; adding a negative factor isolates nothing |
| one-sided stemming | `not_run` | query-only or document-only M | n/a | n/a | n/a | Pq and Pd already show the asymmetric split is inert-to-negative |
| real analyzer configurations | `not_run` | true stemmer, lemmatizer, phrase n-grams, entity-aware analyzer, wider stop list | n/a | n/a | n/a | outside the reviewed implementation contract |

Single-factor effects:
Of the 19 single-factor conditions, 10 carry opposite signs across the two hops: T, R1, R3, R4, R5, R6, R8, N2, N3 and N4. Each description token taken alone helps the bridge hop and harms the answer hop, R1 giving 48 and 2, R3 giving 31 and 2, R4 giving 3951 and 1, and R8 giving 427 and 1, while removing the name tokens has the reverse effect at 12 and 946 and removing `founded` gives 11 and 17. R2 is the documented exception and helps both hops slightly at 15 and 3, because `company` is the least discriminating of the three description tokens, occurring in 211 of 4,937 passages, and the answer hop carries document tf 1 against tf 3 in the leading rivals. R7 is bit-identical to the baseline in every digit, which confirms that `city?` is exactly inert; Q6 and Q7 show that neither its raw nor its normalized form reaches either gold. T is negative for the answer hop and positive for the bridge hop, so title exclusion is excluded as the mechanism, as in D-019, D-020, D-021 and D-023. P is negative for both and Pq leaves the answer hop bit-identical while worsening the bridge hop, so there is no surface-form deficit to repair in the baseline; the harness mismatch ladder independently reports no alignable form for any unmatched query token in either gold, which is the opposite of D-016, D-019 and D-021. E is inert throughout, so the D-021 P x E interaction has no analogue here. S helps both slightly but never brings the answer hop near the cutoff. M is negative for both. No single factor of any class places both hops in the top five: N1 gives 9 and 1, N2 gives 21 and 1, N3 gives 20 and 1, N4 gives 7 and 9, and even Nboth gives 13 and 1.

Combination and interaction effects:
Six conditions recover both hops, and every one of them is either an oracle-plus-preprocessing combination or an index-side removal: K1P, X4, X7, N1P, N1PS and N3P. The decisive interaction is the oracle name crossed with P. P alone is negative at 18 and 12, N1 alone gives 9 and 1, and N1P gives 2 and 1. The decomposition states the reason exactly: under N1 the answer hop gains only `general` 3.923010 and exactly nothing from `mills`, because its own text carries `mills,`, while the bridge hop gains `mills` 9.426700 from its bare `mills`, so injecting the answer hop's own name delivers 9.426700 points to the other gold. Under N1P the answer hop gains `mills` 6.771246 and reaches rank 2. The same effect appears without the surrounding question in the reachability pair: K1 reduces the query to the bare name and the answer hop still ranks only 51, while K1P ranks it 4. The competitor-family contrast is equally decisive and runs the other way from the original note's expectation. X4 drops the 10 purely generic company profiles above the answer hop while leaving all four name-sharing rivals in place and reaches 5 and 2; X3 drops only the six above the bridge hop and reaches 10 and 2; X7 drops all 14 and reaches 2 and 1. By contrast X1 drops the two Smith homonyms and leaves the bridge hop at rank 8 unchanged, and X2 drops all four name-sharing rivals and still gives 12 and 7. The outcome-determinative competitor family is therefore the generic-company profiles, for both hops, and there is no second family with an independent effect.

Supported interpretation:
`cross_passage_conjunction_unresolved` is the most specific verified primary. The query contains exactly two facets, each of which uniquely identifies one gold, and they are mutually antagonistic. The name facet identifies the bridge hop uniquely: `robert smith` occurs in exactly 1 passage and both name tokens together in 4, and probe Q1 places the bridge hop at rank 1 from the two name tokens alone. The description facet never names the company: 12 of 4,937 passages contain all three of `multinational`, `company` and `headquartered`, probe Q4 places positions 1 to 11 entirely within that satisfying set with the answer hop last at 11, and probe Q3 with the whole description half also gives 11. The missing intermediate fact is therefore the company name General Mills, which occurs in the whole corpus only inside the two gold passages and nowhere in the query, and the verified implementation scores each passage independently with no cross-passage or iterative-hop reasoning, so it cannot carry that name from the bridge passage into the scoring of the answer passage. All four registry exclude conditions were checked and none fires: no single passage answers the question, no substitute completes the chain, the judgment rests on reachability and sign evidence rather than on the mere presence of two annotated golds, and the retrieval stage performs no joint cross-passage reasoning. `description_only_bridge_entity` records the query-side half of the same structure, that the bridge entity is designated by relation and attributes and never named. `generic_term_lexical_crowding` records the verified output pattern, ten higher-ranked non-answer passages matching the same broad category vocabulary while failing the concrete founded-by-Robert-Smith constraint, with the rank-1 passage drawing 76.9 percent of its score from those category tokens and X4 showing that the family is outcome-determinative.

Closest competitor and tie-break:
Prefer `cross_passage_conjunction_unresolved` over `description_only_bridge_entity`. The description-only reading satisfies its inclusion rule, because the question requires a specific company, designates it only as the multinational company Robert Smith founded, and never names it, but every single-factor oracle-name condition fails the test D-020 applied to its condition B, D-021 to its condition N, and D-022 to its condition N1: appending the company name gives 9 and 1, appending the bridge title gives 21 and 1, substituting the name into the description gives 20 and 1, and appending both titles gives 13 and 1. This is the fourth failing application of that disqualifier, against two passes in D-017 and D-023. The cross-passage reading instead explains the distinctive structure of this unit with positive evidence of three kinds rather than by the absence of a single fix, which is the standard D-022 set. Lexically, the two golds' matched query-token sets are almost disjoint, sharing only `in`. By sign, 10 of the 19 single-factor conditions move the two hops in opposite directions. By reachability, probe Q1 places the bridge hop at rank 1 from its own two name tokens while the answer hop is not reachable from the description at all, at 11 under both Q3 and Q4, and is reachable from its own bare name only after boundary normalization, K1 at 51 against K1P at 4. This last point is where the unit differs from D-022, where both hops were individually reachable at rank 1 from their own names; the qualification is recorded rather than smoothed over, and it is itself explained by the verified `mills` against `mills,` fact. The provisional primary `compound_two_sided_crowding` is rejected on direct evidence: all seven passages above the bridge hop belong to the generic-company family and none is a Smith homonym, the two homonyms rank 9 and 11 below the bridge gold, removal probe X1 leaves the bridge hop at rank 8, and removal probe X2 dropping all four name-sharing rivals still gives 12 and 7. One competitor family suppresses both hops, so there is no second independent mechanism to compound, and the original note's own stated uncertainty about whether company-token dilution or Smith-homonym competition was decisive is thereby resolved in favour of neither: it is one cue producing one family that suppresses both sides. `generic_term_lexical_crowding` is retained as a secondary under its own exclude rule, which defers to a more specific established mechanism, and because probes Q3 and Q4 show that the descriptive referent cue alone reproduces the whole observed neighborhood, ten of ten inside the baseline top sixteen and seven of ten inside the baseline top ten, which is the test D-023 used to demote `question_frame_semantic_crowding`.

Considered and not adopted:
`proper_name_homonym_collision` is not adopted, because its exclude condition that competition must materially affect the named candidate fails: the homonyms rank below the bridge gold and X1 and X2 leave both hops unrecovered. `surface_form_tokenization_mismatch` is not adopted, because its exclude condition that a missing entity name rather than surface form accounts for the failure fires directly, because the mismatch ladder finds no alignable form for any unmatched query token in either gold, because R7 is bit-identical to the baseline, and because Pq leaves the answer hop unchanged while worsening the bridge hop. The `mills` against `mills,` mismatch is real and is recorded above as a verified implementation fact, but it lies on the diagnostic repair path and not in the observed run, where the query contains no mills token at all; recording it as a mechanism would have inverted the causal order. `minimal_preprocessing_score_distortion` is rejected as primary for the same reason, unlike D-012, D-014, D-016, D-019 and D-021. `generic_query_scaffold_score_inflation` is not adopted, because its exclude condition fires where content-bearing category terms rather than query scaffold explain the competition: the rank-1 passage draws 23.351998 from the category tokens against 7.018647 from scaffold. `repeated_content_word_amplification` and `repeated_function_word_amplification` are not applicable, since no query token repeats. `cutoff_sensitive_near_miss` is not adopted, because a bridge question needs both hops and the answer hop is 20.607 percent below the rank-5 score at rank 16 of 4,937, so the registry exclusion for a gold far below the cutoff fires; the bridge hop's own 5.698 percent gap is recorded but is not sufficient on its own. `gold_chain_substitutability`, `gold_chain_not_unique` and `plausible_non_gold_answer` are not adopted, because the full-corpus scans leave neither hop with any substitute and no passage supplies a complete answer; the only passage combining `robert`, `founded` and `headquartered` is Physicians Mutual, whose founder is Edwin E. Elliott and whose Robert is its chief executive. `same_topic_passage_distractor` is not adopted, because the competitors are generic category matches rather than passages in the answer entity's own subject neighborhood. `entity_alias_reference_mismatch` is not adopted by its own exclude clause, which routes an entity that is not named in the query at all to `description_only_bridge_entity`. `question_frame_semantic_crowding` is not adopted, because its definition is scoped to a whole-passage semantic scorer and its exclude rule routes a lexical retriever to `generic_term_lexical_crowding`.

Not-run cells and attribution boundary:
The defined P x E x S x T design was run complete at all 16 cells, and the M, Pq, Pd, Q, R, K, X and N families were run as listed, for 59 conditions in total. The `not_run` rows are the oracle x T crossings, the oracle x M crossings, the removal x preprocessing crossings, one-sided stemming, and any real analyzer configuration; reasons are recorded in the table. Attribution is bounded as follows. The strongest defensible statement is confined to this run, this 4,937-passage pooled corpus, and this tokenizer. Do not present K1P, X4, X7, N1P, N1PS or N3P as deployable fixes: the K and N conditions inject the hidden company identity or the hidden answer city, and the X conditions require knowing in advance which passages are rivals. Do not credit N1P to the oracle name alone or to P alone, since P alone is negative and only the combination recovers both hops. Do not write the `mills` against `mills,` mismatch as the cause of this failure, since the baseline query contains no mills token and both R7 and Pq show that the baseline loses nothing to surface form. Do not treat rank 8, rank 16, cutoff 5, retriever identity, question type, gold missingness or the pooled setting as causal. Do not present the comparison retriever's rank 1 as a cause of the BM25 ordering and do not compare BM25 and Dense score magnitudes. Do not generalize the corpus-uniqueness counts beyond this corpus, and do not generalize these minimal-tokenizer findings to BM25 in general.

Boundary:
Three boundaries are recorded rather than closed. First, this is the second unit to use `cross_passage_conjunction_unresolved` as a primary, after D-022, and the first BM25 unit to do so; whether the descriptor is suited to primary use remains the vocabulary-audit question D-022 registered. Second, this unit adds a precondition to the single-factor oracle-name test that D-017, D-020, D-021, D-022 and D-023 have now applied six times in total: the injected anchor must itself be matchable by the passage it names. Here it is not, because the answer passage carries `mills,` while the injected form supplies `mills`, so the bare test result of 9 and 1 is uninterpretable on its own and the test passes at 2 and 1 once P neutralizes the artifact. The precondition is recorded here and registered as a vocabulary-audit item; no registry definition, inclusion rule or exclusion rule is changed, following the rule that boundary rules belong to the vocabulary audit. Third, no non-oracle deployable condition recovers both hops, so the primary is the strongest structural account rather than a demonstrated sufficient cause, and X4 lands the answer hop at exactly rank 5, on the cutoff edge.

Confidence:
Medium. The baseline reproduces the stored top-50 order with zero title mismatches and a maximum absolute score error of exactly 0.000000, the per-question ordering is asserted equal to the official file title by title, all 16 cells of the defined design were run together with 43 further conditions, all 14 non-gold passages above the lower gold were read in full, and the dossier's reproduction script passes 335 assertions. The antagonism rests on three independent kinds of evidence, and the provisional primary and one provisional secondary are each falsified by a clean removal probe. The limitations are that no deployable non-oracle condition recovers both hops, that all four single-factor oracle-name forms fail, that the recovering conditions are all combinations or index-side removals, and that the reachability leg of the D-022 evidence set holds for the bridge hop only.

Speculation boundary:
Do not claim that the higher idf of `multinational` at 5.480131 against `robert` at 3.567920 is what makes the description facet overpower the name facet; no idf-perturbation experiment was run. Do not claim that HotpotQA's choice of six company profiles among this question's eight distractors reflects a bias in the annotation pipeline; that is outside this unit's evidence. Do not claim that the answer passage's brand list dilutes its match: under a lexical scorer, length effects belong to the b-normalization term, no controlled experiment isolated them here, and the D-023 dilution gate applies to a mean-pooled encoder and not to BM25. Do not treat the identification of Golden Valley as the answer string as observed evidence; it is an inference from the answer hop's own text, since the HotpotQA answer string is absent from the read-only artifacts available here.

## D-025 - Reclassify the Togodumnus / Catuvellauni Dense unit as an unresolved cross-passage conjunction

- **Date:** 2026-08-03
- **Status:** active
- **Decision:** For `5ae0a59a55429945ae9593e2|dense`, replace
  `description_only_bridge_entity` with `cross_passage_conjunction_unresolved`
  as the candidate primary mechanism. Remove the two provisional secondaries
  `generic_context_substitution` and `shared_retriever_failure`, and adopt
  `description_only_bridge_entity`, `question_frame_semantic_crowding`,
  `gold_chain_substitutability` and `cutoff_sensitive_near_miss` as the
  secondary descriptors. Use `description_only_bridge_entity` as the closest
  competitor. This is the third unit in which
  `cross_passage_conjunction_unresolved` is used as a primary rather than a
  secondary, after D-022 and D-024, and the first Dense unit to use it that
  way.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. D-025 registers no new
  descriptor. It adds this affected unit and D-025 as a decision source to
  `description_only_bridge_entity`, `question_frame_semantic_crowding`,
  `gold_chain_substitutability` and `cutoff_sensitive_near_miss`, and it
  extends the existing usage note on `cross_passage_conjunction_unresolved` to
  record a third primary use and the first on a Dense unit, in each case
  without changing any definition, inclusion rule, or exclusion rule.
  `description_only_bridge_entity` leaves this row's `primary_open_code` but
  keeps two current `case_memos_v2.csv` primary rows,
  `5a85cead5542991dd0999ea9|dense` under D-017 and
  `5ade69e455429975fa854ec5|dense` under D-023, so no name leaves the current
  v2 primary column. The two removed provisional secondaries were unique to
  this row and now have no current v2 row; both remain preserved in
  `case_memos_v1.csv` and in the vocabulary union, the treatment D-021 gave
  `weak_lexical_name_anchor` and D-023 gave `low_information_title`. D-025
  does not merge, rename, demote, or freeze vocabulary, does not settle
  whether `cross_passage_conjunction_unresolved` is suited to primary use,
  does not write the single-factor oracle-name test or its D-024 precondition
  into any exclusion rule, does not decide whether a substitute outside the
  cutoff satisfies `gold_chain_substitutability`, does not adopt any
  descriptor for the question's verified factual error, and does not turn
  counts into prevalence.
- **Affected unit:** `5ae0a59a55429945ae9593e2|dense`.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ae0a59a55429945ae9593e2.md`.

### Complete case evidence

Observed evidence:
The question is `This Celtic ruler who was born in AD 43 ruled southeastern Britain prior to conquest by which empire?` The annotated answer hop is Catuvellauni, whose 29-token text reads `The Catuvellauni were a Celtic tribe or state of southeastern Britain before the Roman conquest, attested by inscriptions into the 4th century.` and so supplies the conquering empire. The annotated bridge hop is Togodumnus, whose 45-token text reads `Togodumnus (d. AD 43) was a historical king of the British Catuvellauni tribe at the time of the Roman conquest. He can probably be identified with the legendary British king Guiderius.` and so supplies the identity of the ruler the question describes but never names. No single passage contains the required conjunction: the ruler's identity and his tribe membership live in one passage, the tribe's region and pre-conquest status live in the other, and the query names neither entity. Exact reconstruction reproduces all 50 stored top-50 titles in order with a maximum absolute score error of 2.682e-07 and places the golds at complete-corpus ranks 8 (0.449564) for the answer hop and 115 (0.222228) for the bridge hop, so the stored `not_in_top50` status means rank 115 of 4,937 rather than corpus absence. The rank-5 score is George I, Earl of March at 0.470765, so the answer hop is 0.021201 points, or 4.503 percent, below the cutoff and the bridge hop is 0.248537 points, or 52.794 percent, below it. Both golds sit far inside the 256-token sequence limit at 29 and 45 model tokens, so truncation is excluded for both.

All seven non-gold passages above the rank-8 answer hop were read in full and fall into exactly two families. Four are Roman-Britain context passages: Roman conquest of Britain 1 (0.594038), which states `beginning effectively in AD 43 under Emperor Claudius` and names the `Roman Republic and Roman Empire`; History of Wales 2 (0.535548), `The Romans, who began their conquest of Britain in AD 43`; Romano-British culture 3 (0.526695), `following the Roman conquest in AD 43`; and History of England 6 (0.462094), `including some Belgic tribes (e.g. the Atrebates, the Catuvellauni, the Trinovantes, etc.) in the south east` together with `In AD 43 the Roman conquest of Britain began`. The first three give the conquest date and the conquering power while naming neither the ruler nor his tribe. The fourth is not a distractor at all but an evidence-bearing substitute for the answer hop and is treated as such below. Three are Scottish nobility passages of the twelfth to fifteenth centuries: Patrick IV, Earl of March 4 (0.501982), `the most important magnate in the border regions of Scotland`; George I, Earl of March 5 (0.470765), `one of the most powerful nobles in Scotland of his time`; and Haddington, East Lothian 7 (0.461561), whose only ancient reference is `the sixth or seventh century AD when the area was incorporated into the kingdom of Bernicia`. None of the three mentions a Celtic tribe, the Roman conquest, or AD 43; all three are period-mismatched instantiations of the question's referent description. The same Scottish family continues below the gold at Earl of Dunbar 10 (0.435665), Aonghus Mór 12 (0.423312), Kingdom of the Isles 13 (0.419128), List of rulers of the Kingdom of the Isles 14 (0.416310), Kingdom of Northumbria 15 (0.410586), Gospatric, Earl of Northumbria 16 (0.390323), and Scottish Borders 17 (0.381336). A third and smaller group matches only the answer facet's `ruled` and `empire` and appears at Khosrow IV 18 (0.366349) and Sasanian Empire 19 (0.364182). British people 11 (0.429180) matches `Celtic` and `Britons` generically. Durotriges 9 (0.436452) and Corieltauvi 30 (0.335047) are other pre-conquest British tribes and are not substitutes, because neither is the tribe the described ruler ruled.

A full-corpus substring scan shows `togodumnus` in exactly 1 of 4,937 passages, which is the bridge hop itself; `guiderius` in exactly 1, the same passage; `historical king` in exactly 1, again the same passage; and `southeastern britain` in exactly 1, which is the answer hop. `catuvellauni` occurs in exactly 4 passages, the two golds plus Corieltauvi and History of England. The bridge hop therefore has no substitute anywhere in the corpus and no complete alternative chain exists. By contrast `ad 43` occurs in 7 passages, `roman conquest` in 8 and `roman empire` in 4, so the answer string is heavily over-determined in this corpus while the required supporting facts are not; this unit is a supporting-fact retrieval failure and not an answerability failure.

Encoding, neighborhood, and probe evidence, in place of a per-token decomposition:
Dense per-token contribution is not derivable from a cosine ranking and none is reported; `case_probe.py` refuses to emit one for this backend and no attribution experiment was run. The neighborhood is instead delimited by reduced-query probes, all of which use question wording only. Probe Q5 reduces the query to the referent clause `This Celtic ruler who was born in AD 43` and ranks the golds 26 (0.320169) and 144 (0.201746) while 10 of its top 10 titles fall inside the baseline top 16 and 8 of 10 inside the baseline top 10, with Patrick IV, Earl of March first; that cue alone reproduces the observed neighborhood. Probe Q1 isolates `Celtic ruler` at 13 (0.392818) and 31 (0.338248) and its top 20 contains 9 of the 10 Scottish family members and 0 of the 4 Roman-Britain family members, with George I, Earl of March first. Probe Q6 isolates the answer facet `prior to conquest by which empire?` at 5 (0.379224) and 53 (0.236968) and its top 20 contains 3 of the 4 Roman-Britain members and 0 of the 10 Scottish members. The two families therefore map one-to-one onto the question's two facets: the referent clause produces the Scottish nobility neighborhood and the answer facet produces the Roman-Britain neighborhood. Probe Q2 on `ruled southeastern Britain` gives 6 (0.435211) and 47 (0.298154) with 9 of 10 inside the baseline top 16. Probe Q10 reduces the query to the single word `ruler` and ranks the bridge hop 1 (0.277850) while the answer hop falls to 547 (0.083697). Probes Q3 and Q4 show that the date clue is not merely weak but points elsewhere: `born in AD 43` gives 2429 (0.057239) and 413 (0.182936) and `AD 43` gives 4289 (-0.029381) and 1252 (0.091998), with the year page AD 43 first in both and 0 of 10 top-10 titles inside the baseline top 16 in both. Q7 `which empire` gives 22 (0.282143) and 52 (0.233455); Q8 `southeastern Britain` gives 18 (0.361488) and 305 (0.181458); Q9 `Celtic` gives 32 (0.327726) and 1519 (0.081960) with Donegal Celtic F.C. first; Q11 gives 5 (0.447799) and 83 (0.211267); Q12 `This Celtic ruler` gives 14 (0.379171) and 96 (0.243323).

Verified implementation facts and exact reconstruction:
The Dense retriever is a symmetric `sentence-transformers/all-MiniLM-L6-v2` bi-encoder that encodes paragraph text only and never the title, so a displayed title is not evidence that its tokens contributed to a score. Query and passage receive no role prefix. Embeddings are explicitly L2 normalized and scored by dot product, which equals cosine similarity; results are sorted by descending score with a stable sort and no threshold. Pooling is attention-mask-aware mean pooling with a 256-token limit. Each passage is scored independently: there is no reranker, no cross-encoder in this run, and no cross-passage or iterative-hop reasoning. That last fact is the one the primary rests on. The pooled index holds 4,937 title-deduplicated passages retaining the first text observed per title. Two consequences are specific to this unit. First, because a cosine score contains no corpus statistic, a per-question Dense ranking is exactly the restriction of the pooled ranking to that question's own paragraphs; reconstructing this item's ten paragraphs from the pooled texts reproduces the official `per_question` ordering title by title, which verifies that property directly and means the idf-scale path D-024 found for BM25 cannot arise here. Second, both golds are far inside the sequence limit, at 29 and 45 model tokens, so no truncation claim is available. Reconstruction reproduces the stored top-50 order with 0 of 50 title mismatches at a maximum absolute score error of 2.682e-07, the same order of magnitude as the zero-title-mismatch Dense reconstructions of D-020 at 2.384e-07 and D-023 at 3.576e-07, and every gold rank is exact.

Gold, provenance, and comparison evidence:
Pooled Dense ranks the golds 8 and 115, and the formal results file records `any_evidence_recall@5` 0 and `full_evidence_recall@5` 0 for `pooled` against `any_evidence_recall@5` 1 and `full_evidence_recall@5` 0 for `per_question`; `any_evidence_recall@10` is 1.0 pooled. The reconstructed per-question ordering, asserted equal to the official file title by title, places the answer hop 5 and the bridge hop 8 of 10. This is the fourth unit in which per-question and pooled disagree on Any@5, after D-022, D-023 and D-024, and it is of the D-022 and D-023 kind rather than the D-024 kind. Exactly 3 of the 7 passages above the answer hop are introduced by pooling, and they are exactly the three Scottish nobility passages Patrick IV, Earl of March, George I, Earl of March and Haddington, East Lothian; removal probe X4 drops exactly those three and returns the answer hop to rank 5, precisely its per-question rank, restoring Any@5. Because Dense cosine carries no corpus statistic, the idf-and-avgdl check D-024 requires after a failed pooling-removal probe does not apply and was not needed. The bridge hop's failure is pooling-independent: 107 of the 114 passages above it are pooling-introduced, removal probe X7 drops exactly those 107 and returns it to rank 8, again precisely its per-question rank and still below the cutoff, and it already ranks 8 of 10 inside HotpotQA's own ten-paragraph context. Corpus setting remains provenance under D-003 and is not used as a causal category. The comparison retriever reaches the same conjunction failure with the same shape: complete-corpus pooled BM25 ranks the answer hop 6 (28.287844) and the bridge hop 846 (10.825051), and per-question BM25 ranks them 1 and 10 of 10, with `any_evidence_recall@5` 1 per-question and 0 pooled. BM25 is used only as reachability and shared-failure evidence, is not written as the cause of the Dense ordering, and the two score magnitudes are not compared.

Factorial diagnostic status: run. Baseline binds the pooled 4,937-passage index, first-occurrence title deduplication, `all-MiniLM-L6-v2` with explicit L2 normalization, dot-product scoring, mean pooling at the 256-token limit, descending stable sort, and cutoff 5. Factors: **A** replaces `southeastern Britain` with `Britain`; **B** replaces `ruler` with `king`; **C** replaces `was born in AD 43` with `died in AD 43` and is gold-informed, because only the gold text reveals that the date is a death date; **R1** to **R9** delete or substitute exactly one query element each; **D4** to **D6** are further wording conditions; **T** prepends every title into the index and re-encodes the whole corpus; **Q1** to **Q12** are reduced-query probes; **K1** to **K6** are reachability probes; **Z1** to **Z5** search for the best name-free question; **N1** to **N8** inject one or both oracle names; **X1** to **X7** are index-side removal probes; and **L1**, **L1c** and **L2** are gold-targeted index-side ablations. A, B, R, D4, D5, T, Q, K3, K4c, K4g and Z-with-no-date are non-oracle. C and every condition containing it, plus K4, K4d, K4e, K4f and the Z series, are gold-informed but inject no entity name. The X series adds no text and injects no answer information but requires knowing which passages are rivals, so it is a diagnostic and not a deployable fix. K1, K2, K6 and the N series contain a hidden gold name and are oracle diagnostics. The L series is the third intervention class D-023 introduced and is likewise not deployable. All ranks are complete-corpus ranks over the same unchanged candidate set, except the X rows where the listed passages are removed and the L rows where exactly one gold passage's own text is replaced by a verbatim subset of itself. All eight A x B x C cells were run; 66 conditions in total.

| Condition | Kind | Exact change | Catuvellauni rank/score | Togodumnus rank/score | Both top-5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | original query, original index | 8 / 0.449564 | 115 / 0.222228 | no | exact reconstruction, 0 of 50 titles, max abs error 2.682e-07 |
| A | non-oracle | `southeastern Britain` to `Britain` | 9 / 0.427479 | 122 / 0.216230 | no | the region qualifier is not the obstacle |
| B | non-oracle | `ruler` to `king` | 14 / 0.428554 | 113 / 0.231347 | no | opposite signs |
| C | gold-informed | `was born in AD 43` to `died in AD 43` | 8 / 0.427042 | 102 / 0.217700 | no | the question's date-role error is not decisive |
| AB | non-oracle | A+B | 14 / 0.405890 | 118 / 0.226822 | no | no recovery |
| AC | gold-informed | A+C | 12 / 0.404863 | 116 / 0.211978 | no | no recovery |
| BC | gold-informed | B+C | 14 / 0.409056 | 105 / 0.226782 | no | best bridge-hop cell of the design, still 105 |
| ABC | gold-informed | A+B+C | 15 / 0.386351 | 112 / 0.221338 | no | the complete design worsens both hops |
| R1 | non-oracle | delete `This` | 9 / 0.455383 | 110 / 0.233713 | no | opposite signs, small magnitude |
| R2 | non-oracle | delete `Celtic` | 8 / 0.382436 | 30 / 0.300654 | no | largest non-oracle bridge-hop gain; opposite signs |
| R3 | non-oracle | `ruler` to `person` | 9 / 0.463982 | 140 / 0.216910 | no | opposite signs |
| R4 | non-oracle | delete the date clause | 4 / 0.476682 | 138 / 0.196126 | no | answer hop enters the top five, bridge hop worsens |
| R5 | non-oracle | delete `southeastern`, identical query to A | 9 / 0.427479 | 122 / 0.216230 | no | reproduces A exactly |
| R6 | non-oracle | delete the geographic clause | 13 / 0.384495 | 121 / 0.203392 | no | both worsen |
| R7 | non-oracle | delete the answer facet | 16 / 0.388879 | 171 / 0.197573 | no | the answer facet is the answer hop's main support |
| R8 | non-oracle | `empire` to `state` | 11 / 0.436336 | 120 / 0.221596 | no | both worsen slightly |
| R9 | non-oracle | delete the whole referent clause | 5 / 0.449328 | 70 / 0.227445 | no | the referent clause harms both hops |
| D4 | non-oracle | `ruler` to `tribal king` | 5 / 0.468467 | 71 / 0.268019 | no | answer hop enters the top five |
| D5 | non-oracle | insert `a tribe of` | 4 / 0.505535 | 91 / 0.242314 | no | best non-oracle answer-hop cell |
| D6 | gold-informed | C plus B plus `a tribe of` | 4 / 0.482245 | 82 / 0.255680 | no | no recovery |
| T | non-oracle, indexing | every title prepended, whole corpus re-encoded | 11 / 0.430058 | 110 / 0.224717 | no | title exclusion excluded; opposite signs |
| Q1 | non-oracle probe | query = `Celtic ruler` | 13 / 0.392818 | 31 / 0.338248 | no | 9 of the 10 Scottish family in its top 20, 0 of 4 Roman |
| Q2 | non-oracle probe | query = `ruled southeastern Britain` | 6 / 0.435211 | 47 / 0.298154 | no | 9 of 10 inside the baseline top 16 |
| Q3 | non-oracle probe | query = `born in AD 43` | 2429 / 0.057239 | 413 / 0.182936 | no | 0 of 10 inside the baseline top 16; birth-year pages |
| Q4 | non-oracle probe | query = `AD 43` | 4289 / -0.029381 | 1252 / 0.091998 | no | the year page ranks 1; 0 of 10 overlap |
| Q5 | non-oracle probe | query = the referent clause alone | 26 / 0.320169 | 144 / 0.201746 | no | 10 of 10 inside the baseline top 16, 8 of 10 inside the top 10 |
| Q6 | non-oracle probe | query = the answer facet alone | 5 / 0.379224 | 53 / 0.236968 | no | 3 of the 4 Roman family in its top 20, 0 of 10 Scottish |
| Q7 | non-oracle probe | query = `which empire` | 22 / 0.282143 | 52 / 0.233455 | no | empire pages, neither gold |
| Q8 | non-oracle probe | query = `southeastern Britain` | 18 / 0.361488 | 305 / 0.181458 | no | region pages, mostly modern |
| Q9 | non-oracle probe | query = `Celtic` | 32 / 0.327726 | 1519 / 0.081960 | no | a football club ranks 1 |
| Q10 | non-oracle probe | query = `ruler` | 547 / 0.083697 | 1 / 0.277850 | no | the bridge hop is rank 1 from this one generic word |
| Q11 | non-oracle probe | query = the question without the referent clause | 5 / 0.447799 | 83 / 0.211267 | no | the answer hop reaches the cutoff without the referent |
| Q12 | non-oracle probe | query = `This Celtic ruler` | 14 / 0.379171 | 96 / 0.243323 | no | 8 of 10 inside the baseline top 16 |
| K1 | oracle probe | query = `Togodumnus` | 2158 / 0.045367 | 1 / 0.703075 | no | the bridge hop is reachable at rank 1 from its own name |
| K2 | oracle probe | query = `Catuvellauni` | 1 / 0.532805 | 28 / 0.281346 | no | the answer hop is reachable at rank 1 from its own name |
| K3 | non-oracle probe | query = `Celtic king of a British tribe at the time of the Roman conquest` | 2 / 0.556613 | 25 / 0.344128 | no | a name-free paraphrase favours the answer hop |
| K4 | gold-informed probe | query = `king of a tribe in Britain who died in AD 43` | 39 / 0.325903 | 3 / 0.438969 | no | the same for the bridge hop, in the other direction |
| K4b | non-oracle probe | K4 with the question's `was born in` | 33 / 0.344949 | 5 / 0.446765 | no | the date role is worth two ranks here, not the failure |
| K4c | non-oracle probe | K4 with no date at all | 11 / 0.400251 | 1 / 0.508966 | no | dropping the date helps the bridge hop most |
| K4d | gold-informed probe | K4 plus `Celtic` | 18 / 0.409398 | 40 / 0.328705 | no | adding `Celtic` costs the bridge hop 37 ranks |
| K4e | gold-informed probe | K4 with `southeastern Britain` | 17 / 0.364355 | 5 / 0.441132 | no | the region qualifier is nearly inert here |
| K4f | gold-informed probe | the referent clause with the date role fixed | 37 / 0.280625 | 126 / 0.197529 | no | fixing the date inside the referent clause helps neither |
| K4g | non-oracle probe | the referent clause with no date, plus `ruled a tribe` | 2 / 0.432445 | 99 / 0.218196 | no | the answer hop only |
| K6 | gold-text probe | query = `historical king`, a corpus-unique string of the bridge passage | 507 / 0.170548 | 1 / 0.484866 | no | the bridge passage is reachable from its own wording |
| Z1 | gold-informed, name-free | died + king + tribe + region + answer facet | 4 / 0.482245 | 82 / 0.255680 | no | ceiling search, step 1 |
| Z2 | gold-informed, name-free | Z1 without `Celtic` | 7 / 0.432919 | 25 / 0.336501 | no | ceiling search, step 2 |
| Z3 | gold-informed, name-free | Z2 with `historical king of the British tribe` | 7 / 0.441826 | 18 / 0.369641 | no | ceiling search, step 3 |
| Z4 | gold-informed, name-free | Z3 plus `at the time of the Roman conquest` | 4 / 0.512483 | 15 / 0.362099 | no | ceiling search, step 4 |
| Z5 | gold-informed, name-free | the bridge passage's own sentence minus its name, plus the answer facet | 4 / 0.519406 | 14 / 0.356395 | no | the name-free ceiling: 4 and 14 |
| N1 | oracle | append `Togodumnus` | 10 / 0.405082 | 2 / 0.526568 | no | single-factor oracle-name test fails |
| N2 | oracle | name the bridge entity in place | 9 / 0.421893 | 1 / 0.604819 | no | second surface form fails |
| N3 | oracle | the bridge name replaces the whole description | 8 / 0.338246 | 1 / 0.689980 | no | third surface form fails |
| N4 | oracle | append `Catuvellauni` | 1 / 0.640362 | 66 / 0.255184 | no | the reverse direction also fails |
| N5 | oracle | name the tribe in place | 1 / 0.674001 | 54 / 0.276084 | no | second reverse form fails |
| N6 | oracle | append both gold titles | 1 / 0.581589 | 2 / 0.547945 | yes | both anchors together recover both hops |
| N7 | oracle | both names in place | 2 / 0.603481 | 1 / 0.649643 | yes | the same with natural insertion |
| N8 | oracle | N2 plus the date-role fix | 8 / 0.408077 | 1 / 0.591607 | no | fourth bridge-name surface form fails |
| X1 | removal probe | drop the 3 Scottish rivals above the answer hop | 5 / 0.449564 | 112 / 0.222228 | no | one family alone accounts for the answer hop's slippage |
| X2 | removal probe | drop the 4 Roman-Britain rivals above the answer hop | 4 / 0.449564 | 111 / 0.222228 | no | so does the other; the two are additive, neither decisive |
| X3 | removal probe | drop all 7 rivals above the answer hop | 1 / 0.449564 | 108 / 0.222228 | no | displacement upper bound for the answer hop |
| X4 | removal probe | drop only the 3 pooling-introduced rivals above the answer hop | 5 / 0.449564 | 112 / 0.222228 | no | restores exactly the per-question rank 5 and Any@5 |
| X5 | removal probe | drop all 11 corpus-wide March, Dunbar and Lothian titles | 5 / 0.449564 | 107 / 0.222228 | no | the Scottish family is irrelevant to the bridge hop |
| X6 | removal probe | drop all 113 non-gold passages above the bridge hop | 1 / 0.449564 | 2 / 0.222228 | yes | trivial upper bound only |
| X7 | removal probe | drop the 107 pooling-introduced passages above the bridge hop | 5 / 0.449564 | 8 / 0.222228 | no | restores exactly the per-question rank 8, still below cutoff |
| L1 | gold-targeted index-side | bridge passage keeps only its query-relevant sentence 1 | 8 / 0.449564 | 39 / 0.307062 | no | ablation improves the bridge hop |
| L1c | gold-targeted index-side | control: bridge passage keeps only its non-relevant sentence 2 | 8 / 0.449564 | 18 / 0.367169 | no | the control improves it more, so dilution is excluded |
| L2 | gold-targeted index-side | answer passage trimmed to its query-relevant clause | 5 / 0.485107 | 115 / 0.222228 | no | answer hop enters the top five |
| equal-length L1 control | `not_run` | a 32-token non-relevant control text for the bridge passage | n/a | n/a | n/a | the shorter control already improves the rank more than the ablation, so the dilution include rule cannot be met; the passage has only two sentences and a longer control would require text it does not contain |
| dose-response for L1 | `not_run` | intermediate reductions of the bridge passage | n/a | n/a | n/a | the passage has exactly two sentences; L1 and L1c already exhaust its non-empty subsets |
| factorial on the per-question index | `not_run` | any factor over the 10-paragraph index | n/a | n/a | n/a | per-question already places the hops at 5 and 8, and a Dense per-question ranking is the restriction of the pooled one, verified by the exact reconstruction |
| removal probes on ranks 9 to 114 | `not_run` | individual or blockwise deletions below the answer hop | n/a | n/a | n/a | X6 gives the displacement upper bound and X5 and X7 bracket the families; intermediate cells have no diagnostic value |
| answer-string injection | `not_run` | append `Roman Empire` to the query | n/a | n/a | n/a | tests answerability rather than supporting-fact retrieval and says nothing about the hop structure |
| reranker conditions | `not_run` | cross-encoder rescoring of the pooled top 50 | n/a | n/a | n/a | the formal run contains no reranker, so this would change the object being explained |
| Dense per-token decomposition | `not_run` | token attribution for either gold | n/a | n/a | n/a | not derivable from a cosine ranking; the tool refuses it by design |

Single-factor effects:
Of the 20 single-factor conditions, 10 move the two hops in opposite score directions: B, N1, N2, N3, N8, R2, R3, R4, R9 and T. Deleting `Celtic` is the strongest non-oracle intervention on the bridge hop, taking it from 115 to 30 while costing the answer hop 0.067128 points, and the same asymmetry appears without the question frame in the probe pair K4 against K4d, where adding `Celtic` to a name-free description moves the bridge hop from 3 to 40. Deleting the date clause is the mirror image: R4 takes the answer hop from 8 to 4 and the bridge hop from 115 to 138. Two conditions help both hops and still recover neither: D4 gives 5 and 71 and D5 gives 4 and 91. R9 is the most instructive non-oracle cell, because deleting the entire referent clause improves the bridge hop as well, from 115 to 70, so the clause that is supposed to identify the bridge entity is net harmful to both required passages. T is negative for the answer hop and marginally positive for the bridge hop, so title exclusion is excluded as the mechanism, as in D-019, D-020, D-021, D-023 and D-024. The question's factual error is measured rather than assumed: C alone moves the bridge hop only from 115 to 102, K4b against K4 shows the born and died forms of the same name-free description give 5 and 3, and K4f shows that fixing the date inside the referent clause leaves both hops worse than baseline at 37 and 126. No single factor of any class places both hops in the top five: the four bridge-name oracle forms give 10 and 2, 9 and 1, 8 and 1, and 8 and 1, and the two tribe-name forms give 1 and 66 and 1 and 54.

Combination and interaction effects:
Only two conditions of the 66 recover both hops without trivially deleting the entire field above a gold, N6 at 1 and 2 and N7 at 2 and 1, and both require the two oracle names simultaneously. The decisive interaction is therefore bridge name crossed with tribe name: either alone recovers one hop and demotes the other, and only their conjunction recovers both, which is the same shape as D-020's B+C and D-022's N1+N2+S. The second interaction is `Celtic` crossed with the choice of frame: inside the full question deleting it helps the bridge hop and harms the answer hop, while inside the reduced description of K4 adding it back costs the bridge hop 37 ranks, so the factor's magnitude depends on its base and cannot be reported as a single case-level direction. The third is the ceiling search: no name-free question recovers both hops even when it is written from the bridge passage's own sentence with the name removed, and the ceiling is Z5 at 4 and 14, with Z2, Z3 and Z4 tracing a monotone approach at 25, 18 and 15 on the bridge hop while the answer hop stays between 4 and 7. The removal probes carry the provenance conclusion rather than the mechanism: X1 and X2 each place the answer hop inside the top five on its own, at 5 and 4, so the two families above it are additive and neither is individually decisive, and X4, which drops exactly the three pooling-introduced rivals, reproduces the per-question rank 5 exactly. For the bridge hop every removal probe fails: X5 drops all 11 corpus-wide March, Dunbar and Lothian passages and reaches only 107, X7 drops all 107 pooling-introduced passages above it and reaches exactly its per-question rank 8, and only X6, which deletes all 113 non-gold passages above it, reaches 2. The bridge hop's problem is absolute similarity, not competition. The L series separates content from length in the falsifying direction: L1 retains the bridge passage's query-relevant sentence and improves it from 115 to 39, but the control L1c, which retains only the non-relevant Guiderius sentence, improves it further to 18, so the direction of the effect is brevity rather than query-relevant content.

Supported interpretation:
`cross_passage_conjunction_unresolved` is the most specific verified primary. The question's two facets each address a different gold and are mutually antagonistic. The referent clause produces the Scottish nobility neighborhood, verified by Q1 at 9 of 10 family members in its top 20 and by Q5 at 10 of 10 top-10 titles inside the baseline top 16; the answer facet produces the Roman-Britain neighborhood, verified by Q6 at 3 of 4 family members and 0 of 10 Scottish members. The missing intermediate fact is concrete and unavailable by construction: the identity of the described ruler occurs in exactly 1 of 4,937 passages, which is the bridge hop itself, the query never contains it, and the only discriminating string the two golds share, `catuvellauni`, is written inside the bridge passage and not inside the answer passage, so it cannot be recovered from one and carried into the scoring of the other by an encoder that scores every passage independently. Positive evidence for the architectural reading is available in all three of the forms D-022 established. Reachability: K1 places the bridge hop at rank 1 from its own name and K2 places the answer hop at rank 1 from its own name, while K1 simultaneously drives the answer hop to 2158 and the descriptive probe K4c does the reverse, placing the bridge hop at 1 and the answer hop at 11. Sign: 10 of the 20 single-factor conditions carry opposite signs across the hops. Exhaustion in the non-oracle direction: 66 conditions were run and the only recoveries are the two conditions that inject both names, with the name-free ceiling at 4 and 14. All four registry exclude conditions were checked and none fires: no single passage supplies a complete answer under the standard D-011 applied, the one evidence-bearing substitute sits at rank 6 and therefore outside the evaluated top five and substitutes only one hop rather than completing the chain, the judgment rests on the reachability and sign evidence rather than on the mere presence of two annotated golds, and the retrieval stage performs no joint reasoning. `description_only_bridge_entity` records the query-side half of the same structure. `question_frame_semantic_crowding` records the verified Roman-Britain neighborhood, which persists when the referent cue is deleted and which the referent cue alone does not produce. `gold_chain_substitutability` records History of England at 6 (0.462094), which names the Catuvellauni among the Belgic tribes `in the south east` and dates the Roman conquest to AD 43, and so supplies the answer hop's intermediate fact in full while naming no ruler. `cutoff_sensitive_near_miss` records the answer hop's 4.503 percent gap and the exactness of the X4 result.

Closest competitor and tie-break:
Prefer `cross_passage_conjunction_unresolved` over `description_only_bridge_entity`. The description-only reading satisfies its inclusion rule without argument: the question requires a specific ruler, designates him only by ethnicity, role, date and region, and never names him. It loses the tie-break on the single-factor oracle-name test that D-020 applied to its condition B, D-021 to its condition N, D-022 to its N1 and D-024 to its four N forms. Four bridge-name surface forms were run and all four fail: appending the bare name gives 10 and 2, naming the entity in place gives 9 and 1, replacing the whole description with the name gives 8 and 1, and adding the date-role fix on top gives 8 and 1. The reverse direction fails as well, at 1 and 66 and 1 and 54. This is the fifth failing application of that disqualifier against two passes, D-017 and D-023. The D-024 precondition on that test was checked before the verdict was read and it holds here, which is what makes this the first clean failure on a Dense unit: the injected anchor is matchable by the passage it names, since K1 reduces the query to the bare `Togodumnus` and that passage ranks 1 at 0.703075, and K2 does the same for `Catuvellauni` at 1 and 0.532805. The failure is therefore a real insufficiency of one anchor, not an anchor delivered to the wrong passage. The cross-passage reading also explains what the description-only reading cannot, namely that the referent clause is net harmful to both hops: R9 deletes it and improves the answer hop from 8 to 5 and the bridge hop from 115 to 70. Two further candidate primaries were rejected on direct evidence. `compound_two_sided_crowding` fails because the bridge hop is not crowded at all: X5 removes every corpus-wide March, Dunbar and Lothian passage and leaves it at 107, X7 removes all 107 pooling-introduced passages above it and leaves it at exactly its per-question rank 8, and only the trivial X6 recovers it, so there is no second competitor family with an independent effect and nothing to compound. A descriptive-cue drift reading, on which the query's `Celtic` mismatches the bridge passage's `British`, is a real and large effect, R2 taking the bridge hop from 115 to 30 and K4d costing it 37 ranks, but it is not decisive, because R2 leaves both golds outside the top five and simultaneously costs the answer hop 0.067128 points, and because the name-free ceiling with `Celtic` removed is still only 25 at Z2 and 14 at Z5. It is recorded as observed evidence and an interpretation rather than promoted to a descriptor, which would require a new registration during a validation pass that defers vocabulary growth.

Considered and not adopted:
`generic_context_substitution`, a provisional first-pass secondary, is not adopted, because its content is exactly what the registered `question_frame_semantic_crowding` covers and registering it would create a near-synonym during the validation pass. Both readings of its name were tested separately: the generic-context reading is verified by Q6, Q11 and R9 and is recorded under the registered descriptor, and the substitution reading is verified by History of England and is recorded under `gold_chain_substitutability`. `shared_retriever_failure`, the other provisional first-pass secondary, is not adopted, because it names comparison-retriever behaviour rather than a mechanism of this unit, and retriever identity is a forbidden causal category under D-003; the underlying observation is true and is preserved in the provenance evidence, where complete-corpus BM25 ranks the bridge hop 846 of 4,937. `peripheral_passage_content_dilution` is not adopted and is excluded by its own inclusion rule, whose third condition requires that a control retaining only the non-query-relevant sentences must not improve the rank: here L1 improves the bridge hop from 115 to 39 but the control L1c improves it further to 18, so the effect runs the wrong way and the mechanism would be brevity rather than content. The fourth condition is satisfied, since both golds are far inside the sequence limit, but that is not sufficient. `generic_person_semantic_neighborhood` is not adopted although the Scottish family is indeed a cluster of ruler biographies, because its definition is scoped to a question whose `explicitly named target entities remain lower` and this question names no entity at all; adopting it would silently widen the definition, which the validation pass forbids. `compound_two_sided_crowding` and a `Celtic` drift descriptor are not adopted for the reasons given in the tie-break. `plausible_non_gold_answer` and `gold_chain_not_unique` are not adopted, because no single passage satisfies the explicit constraint of a Celtic ruler dated AD 43: `togodumnus`, `guiderius` and `historical king` each occur in exactly 1 passage, which is the bridge hop, and Roman conquest of Britain at rank 1 supplies the empire while naming neither the ruler nor the tribe. `same_entity_variant_crowding` is not adopted, because Durotriges and Corieltauvi are different tribes rather than variants of the Catuvellauni. `possible_type_mismatch` is not adopted, because the question asks for an empire and the answer hop states `before the Roman conquest`, so no category misalignment is present. `surface_form_tokenization_mismatch`, `repeated_content_word_amplification`, `repeated_function_word_amplification`, `generic_query_scaffold_score_inflation` and `minimal_preprocessing_score_distortion` are not applicable, because they are all scoped to a lexical scorer with an inspectable tokenizer and this unit is a bi-encoder for which no per-token decomposition exists. `generic_term_lexical_crowding` is likewise not adopted, because its own definition and D-024's usage are lexical; the Dense counterpart in the registry is `question_frame_semantic_crowding`. `exact_string_source_dependency` is not adopted, because the query contains no quoted or fixed string.

Not-run cells and attribution boundary:
The defined A x B x C design was run complete at all eight cells, and the R, D, T, Q, K, Z, N, X and L families were run as listed, for 66 conditions in total. The `not_run` rows are an equal-length control for L1, a dose-response curve for L1, any factorial over the per-question index, removal probes on ranks 9 to 114, answer-string injection, reranker conditions, and Dense per-token decomposition; reasons are recorded in the table. Attribution is bounded as follows. No token-level claim is licensed. The R2 and K4d results support only the query-level statement that deleting or adding `Celtic` moves the bridge hop's cosine similarity by the stated amounts; they do not establish that the encoder attended to, weighted, or represented that word in any particular way, and no attribution experiment was run. The L series supports only the passage-level statement that replacing the bridge passage's text with the stated verbatim subset changes its similarity as recorded, and because the control improves the rank more than the ablation, it supports no dilution claim at all. Do not present N1 to N8, K1, K2 or K6 as query rewrites, since they contain a hidden gold name, and do not present the Z series as deployable either, since it is written from the gold text. Do not present the X series as a repair proposal, since it requires knowing which passages are rivals. Do not present the L series as a fix, since it requires knowing which passage is gold. Do not treat rank 8, rank 115, cutoff 5, retriever identity, question type, gold missingness or corpus setting as causal; the defensible provenance statement is that pooling adds exactly three rivals above the answer hop, that removing exactly those three restores rank 5 and Any@5, and that the bridge hop reaches rank 8 in its own ten-paragraph context and so fails independently of pooling. Do not present BM25's ranks as the cause of the Dense ordering and do not compare Dense and BM25 score magnitudes. Do not claim truncation, which is excluded at 29 and 45 model tokens. Do not generalize the corpus-uniqueness counts or the neighborhood composition beyond this 4,937-passage corpus.

Boundary:
Four boundaries are recorded rather than closed. First, this is the third unit to use `cross_passage_conjunction_unresolved` as a primary, after D-022 and D-024, and the first Dense unit to do so; D-017 and D-020 used the name as a secondary on Dense units alongside a different primary. Whether the descriptor is suited to primary use, and whether its presence in both the primary and the secondary inventory needs splitting, remains the vocabulary-audit question D-022 registered. This unit adds one observation to that backlog: the two BM25 primary uses had almost disjoint matched token sets, a criterion that has no Dense analogue, so the Dense evidence set here rests on reachability, sign and non-oracle exhaustion only. Second, the single-factor oracle-name disqualifier now has five failing and two passing applications, and this is the first failing application on a Dense unit with the D-024 precondition explicitly verified beforehand. That strengthens the case for writing the test into the registry, which remains deferred to the vocabulary audit. Third, `gold_chain_substitutability` is adopted for a substitute that sits above its gold at rank 6 yet outside the cutoff, so it changes no metric; the descriptor's registry text does not require the substitute to be inside the evaluated set, and D-023 recorded a related boundary, but whether a substitute outside the cutoff should count is left open. Fourth, the question contains a verified factual error, since it says the ruler was born in AD 43 while the gold passage records `(d. AD 43)`. The error is measured and found not decisive, at 115 to 102 under C and 5 against 3 for the born and died forms of the same reduced description, and no descriptor is adopted for it; whether the vocabulary needs a question-quality descriptor is left to the later sections, where queue item 13 and queue item 21 both carry a provisional `question_wording_ambiguity`.

Confidence:
Medium. The baseline reproduces the stored top-50 order with zero title mismatches at a maximum absolute score error of 2.682e-07, the per-question ordering is asserted equal to the official file title by title, all eight cells of the defined design were run together with 58 further conditions, all seven non-gold passages above the answer hop and the whole neighborhood down to rank 30 were read in full, and the dossier's reproduction script passes 408 assertions. The antagonism rests on the three independent kinds of evidence D-022 established, and both provisional secondaries and two candidate primaries are each excluded by a specific condition rather than by argument. The limitations are that the only recovering conditions inject both oracle names, that no non-oracle or even name-free condition places both hops inside the top five, with a measured ceiling of 4 and 14, and that the bridge hop's low absolute similarity is characterized rather than explained: the strongest available account of it, the mismatch between the query's `Celtic` and the passage's `British`, is a query-level effect of measured size and not a mechanism established by attribution.

Speculation boundary:
Do not claim that mean pooling averaged away any part of the bridge passage or that its Guiderius sentence diluted it; the control ablation falsifies the direction and token-level attribution is not derivable from a cosine ranking. Do not claim that the encoder treats `Celtic` as a modern Scottish or Irish signal, even though Q9 ranks a football club first; that is a description of one probe's output, not an attribution. Do not claim that the Scottish nobility neighborhood arises through a border or march semantics linking `southeastern` to south-eastern Scotland; Q1 shows the family arises from `Celtic ruler` alone, but no experiment isolates why. Do not treat the identification of the Roman Empire as the answer string as observed evidence; the HotpotQA answer string is absent from every read-only artifact available here and this identification is an inference from the answer hop's own text. Do not treat the question's `born` as a mere transcription slip with a known cause; only its retrieval effect was measured. Do not read the 107 pooling-introduced passages above the bridge hop as evidence that pooling harmed it, since X7 shows removing all of them leaves it at rank 8.
## D-026 - Reclassify the 2008 Summer Olympics / Summer Olympic Games Dense unit as a description-only bridge entity

- **Date:** 2026-08-03
- **Status:** active
- **Decision:** For `5ae1f596554299234fd04372|dense`, replace
  `question_wording_ambiguity` with `description_only_bridge_entity` as the
  candidate primary mechanism. Remove the unregistered provisional secondary
  `adjacent_event_crowding`, retain `cutoff_sensitive_near_miss`, and adopt
  `peripheral_passage_content_dilution` as the second secondary descriptor. Use
  `peripheral_passage_content_dilution` as the closest competitor. This is the
  third unit in which `description_only_bridge_entity` is used as a primary
  rather than a secondary, after D-017 and D-023, and all three are Dense units.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. D-026 registers no new
  descriptor. It adds this affected unit and D-026 as a decision source to
  `description_only_bridge_entity`, `peripheral_passage_content_dilution` and
  `cutoff_sensitive_near_miss`, and it extends the existing primary-use note on
  `description_only_bridge_entity` to record a third primary use, in each case
  without changing any definition, inclusion rule, or exclusion rule.
  `question_wording_ambiguity` leaves this row's `primary_open_code` but keeps a
  current `case_memos_v2.csv` primary row, `5adc8977554299438c868de2|bm25` as
  queue item 21, so no name leaves the current v2 primary column, as in D-024 and
  D-025 and unlike D-021, D-022 and D-023. The removed provisional secondary
  `adjacent_event_crowding` was unique to this row and now has no current v2 row;
  it remains preserved in `case_memos_v1.csv` and in the vocabulary union, the
  treatment D-021 gave `weak_lexical_name_anchor`, D-023 gave
  `low_information_title` and D-025 gave `generic_context_substitution`. It is
  deliberately not registered, because a registry entry for it would duplicate
  `question_frame_semantic_crowding`. D-026 does not merge, rename, demote, or
  freeze vocabulary, does not settle whether `description_only_bridge_entity`
  should distinguish a bridge entity that is also the answer passage's own
  subject, does not repair that descriptor's `for lexical retrieval` wording,
  does not write the single-factor oracle-name test into any exclusion rule, does
  not revise the four include conditions of
  `peripheral_passage_content_dilution`, does not create a question-quality
  descriptor, and does not turn counts into prevalence.
- **Recorded synchronization correction:** the queue row for
  `5ae0a59a55429945ae9593e2|dense`, queue item 12, still carried the
  pre-validation provisional primary and secondary values after D-025 landed,
  while `case_memos_v2.csv`, D-025, the registry and the audit all carried the
  validated ones. D-026 corrects that queue row to match the other four sources.
  This is a transcription omission in a workflow index whose own header states
  that the two columns are snapshots copied from `case_memos_v2.csv`; it is not a
  semantic change, it alters no decision, and it is recorded here rather than
  applied silently.
- **Affected unit:** `5ae1f596554299234fd04372|dense`.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ae1f596554299234fd04372.md`.

### Complete case evidence

Observed evidence:
The question is `When did the game which held three times in  in East Asia first held `, reproduced here verbatim from the read-only reviewer JSON including the duplicated preposition, the double space and the missing final question mark; the CSV and the JSON agree character for character, so the malformation is in the source data and not a transcription error. The annotated bridge hop is 2008 Summer Olympics, whose 144-token text ends `It was the third time that the Summer Olympic Games were held in East Asia and Asia, after Tokyo, Japan, in 1964 and Seoul, South Korea, in 1988.` and so supplies the identification of the event the question describes but never names. The annotated answer hop is Summer Olympic Games, whose 131-token text opens `The Summer Olympic Games (French: "Jeux olympiques d'ete" ) or the Games of the Olympiad, first held in 1896, is an international multi-sport event that is hosted by a different city every four years.` and so supplies the answer fact. The strings Olympic, Olympics and Olympiad are absent from the query in every case. Exact reconstruction reproduces all 50 stored top-50 titles in order with a maximum absolute score error of 2.980e-07 and places the golds at complete-corpus ranks 6 (0.473542) for the bridge hop and 13 (0.361134) for the answer hop. The rank-5 score is 2010 Commonwealth Games medal table at 0.479079, so the bridge hop is 0.005537 points, or 1.156 percent, below the cutoff, which is the smallest margin recorded in this project, and the answer hop is 0.117945 points, or 24.619 percent, below it. Both golds sit inside the 256-token sequence limit at 144 and 131 model tokens, so truncation is excluded for both.

All 11 non-gold passages above the rank-13 answer hop were read in full and form a single family: other recurring multi-nation sporting events. They are 1984 South Asian Games 1 (0.611078), the first edition of a South Asian rather than East Asian series; EAFF E-1 Football Championship 2 (0.535314), an East Asian competition whose text does say `first held in 2003` but never claims a third edition in East Asia; 2010 Commonwealth Games 3 (0.514387), which states `the second time they were held in Asia`; Indonesia 2022 FIFA World Cup bid 4 (0.482185); 2010 Commonwealth Games medal table 5 (0.479079); Gymnastics at the 2002 Asian Games 7 (0.449724); EAFF E-1 Football Championship (women) 8 (0.405244); 2002 FIFA World Cup 9 (0.404563), which states `the first World Cup to be held in Asia`; South West Pacific theatre of World War II 10 (0.379377) and Battle of the Ch'ongch'on River 12 (0.361974), which match only the East Asian region wording; and 2011 Pan American Games 11 (0.363602), whose `first held in the state of Jalisco` matches the answer facet without any Asian connection. Not one of the 11 combines an East Asian location with a third-time or three-times claim, so none is a complete non-gold answer and none is an evidence-bearing substitute for either hop.

A full-corpus scan confirms that neither hop has a substitute. Exactly 1 of 4,937 passages states the bridge fact, an East Asian location together with a third-time or three-times claim, and it is the bridge gold itself; exactly 1 states the answer fact, the year 1896 together with an Olympic or Olympiad reference, and it is the answer gold itself; and the string `first held in 1896` occurs in exactly 1 passage. There is therefore no complete non-gold answer, no complete alternative chain, and no single-hop substitute, so `gold_chain_substitutability`, `gold_chain_not_unique` and `plausible_non_gold_answer` are all inapplicable.

Encoding, neighborhood, and probe evidence, in place of a per-token decomposition:
Dense per-token contribution is not derivable from a cosine ranking and none is reported; `case_probe.py` refuses to emit one for this backend and no attribution experiment was run. The neighborhood is instead delimited by reduced-query probes and, for the first time in this project, by the matching deletion in the opposite direction. Probe Q1 reduces the query to the referent clause alone and 10 of its top 10 titles fall inside the baseline top 12, with 1984 South Asian Games first, so the referent cue by itself reproduces the entire observed competitor family. Condition R1 deletes that same clause and only 3 of the top 10 remain inside the baseline top 12, the family being replaced by bowl games, tennis doubles and hockey all-star games, while the golds collapse to 39 (0.351654) and 34 (0.362962). Probe Q2 reduces the query to the answer facet `first held` alone and 0 of its top 10 fall inside the baseline top 12. The forward test is the one D-023 used to demote `question_frame_semantic_crowding` and D-024 applied to a lexical retriever; this unit runs it in both directions and the two agree, which is what excludes every crowding-shaped descriptor here. Probe Q8 on `multi-sport event` reaches the answer hop at 4 (0.445006) and Q12 on `international multi-sport event` reaches it at 2 (0.508778), so the answer hop is reachable from its category wording alone, while Q5 on `the game` gives 707 (0.117317) and 408 (0.139988) and Q9 on `game` gives 480 (0.116923) and 354 (0.128865), so the question's actual head noun is not an anchor at all.

Verified implementation facts and exact reconstruction:
The Dense retriever is a symmetric `sentence-transformers/all-MiniLM-L6-v2` bi-encoder that encodes paragraph text only and never the title, so a displayed title is not evidence that its tokens contributed to a score. Query and passage receive no role prefix. Embeddings are explicitly L2 normalized and scored by dot product, which equals cosine similarity; results are sorted by descending score with a stable sort and no threshold. Pooling is attention-mask-aware mean pooling with a 256-token limit. Each passage is scored independently: there is no reranker, no cross-encoder in this run, and no cross-passage or iterative-hop reasoning. Three consequences are specific to this unit. First, because each passage is embedded independently, replacing one row of the document matrix is exactly equivalent to re-encoding the whole corpus with that one passage changed; conditions L0 and L0b re-encode each gold's unchanged text and reproduce the baseline in every digit, which establishes that equivalence numerically before any ablation result is read. Second, because a cosine score contains no corpus statistic, a per-question Dense ranking is exactly the restriction of the pooled ranking to that question's own paragraphs; sorting this item's ten paragraphs by their pooled scores reproduces the official `per_question` ordering title by title, and removal probe X6, which keeps only those ten, equals removal probe X2 in every digit. Third, the model's tokenizer is uncased, which condition S5 verifies by reproducing condition D3 exactly. Reconstruction reproduces the stored top-50 order with 0 of 50 title mismatches at a maximum absolute score error of 2.980e-07, the same order of magnitude as the zero-title-mismatch Dense reconstructions of D-020 at 2.384e-07, D-023 at 3.576e-07 and D-025 at 2.682e-07, and both gold ranks are exact.

Gold, provenance, and comparison evidence:
Pooled Dense ranks the golds 6 and 13, so pooled `any@5` is 0 and pooled `full@5` is 0. The reconstructed per-question ordering, asserted equal to the official file title by title, places the bridge hop 2 and the answer hop 3 of 10, so per-question `any@5` is 1 and per-question `full@5` is also 1. This is the fifth unit in which the two corpus settings disagree, after D-022, D-023, D-024 and D-025, and the first in which they disagree on `full@5` rather than only on `any@5`; the four earlier units all had `full@5` 0 in both settings. It is also the first unit whose failure is confined entirely to the pooled setting, since both required passages sit in the top three of HotpotQA's own ten-paragraph context, whereas in D-024 and D-025 one hop failed independently of pooling. Mechanically it is of the D-022, D-023 and D-025 kind rather than the D-024 kind: exactly 10 of the 12 passages above the answer hop are introduced by pooling, and removal probe X2 drops exactly those ten and returns the ranking to 2 and 3, precisely the per-question ranks. Because a Dense cosine carries no corpus statistic, the idf-and-avgdl check D-024 requires after a failed pooling-removal probe does not apply and was not run. Corpus setting remains provenance under D-003 and is not used as a causal category: the primary explains why a described but unnamed entity loses to its category siblings in a large corpus, and the corpus setting determines only whether that ordering crosses the cutoff. The comparison retriever places the two passages at complete-corpus BM25 ranks 22 (24.133560) and 44 (20.949830), which agrees with the official pooled file title for title, and at per-question BM25 ranks 3 and 7 of 10. BM25 is used only as evidence that both passages are reachable, is not written as the cause of the Dense ordering, and the two score magnitudes are not compared.

Factorial diagnostic status: run. Baseline binds the pooled 4,937-passage index, first-occurrence title deduplication, `all-MiniLM-L6-v2` with explicit L2 normalization, dot-product scoring, mean pooling at the 256-token limit, descending stable sort, and cutoff 5. Factors: **A** collapses the duplicated preposition `in  in` to `in`; **B** repairs the relative clause `which held` to `which was held`; **C** repairs the main-clause auxiliary `When did` to `When was`; none of the three adds content the question does not already imply, and all eight A x B x C cells were run. **D1** to **D6** are further wording conditions; **S1** to **S4** replace the vague head noun `the game` with a category phrase and **S5** is an uncased null control; **Z1** to **Z5** search for the best question that contains no gold name; **R1** to **R7** delete exactly one query element each; **Q1** to **Q12** are reduced-query probes; **K1** to **K6** are reachability probes; **N1** to **N7** inject a gold name; **T** prepends every title into the index and re-encodes the whole corpus; **X1** to **X6** are index-side removal probes; **L0** and **L0b** are null controls for single-row substitution, **L1**, **L1c** to **L1f**, **L2**, **L2c** to **L2f** are gold-targeted index-side ablations with their length-matched controls, and **L3** ablates both golds at once. A, B, C, D, S, R, Q and T are non-oracle. The Z series injects no entity name but returns facts drawn from the gold passages and is therefore marked name-free and gold-informed rather than non-oracle. The X series adds no text and injects no answer information but requires knowing which passages are rivals, so it is a diagnostic and not a deployable fix. K and N contain a gold name and are oracle diagnostics. The L series is the third intervention class D-023 introduced and is likewise not deployable. All ranks are complete-corpus ranks over the same unchanged candidate set, except the X rows where the listed passages are removed and the L rows where exactly one gold passage's own text, or in L3 both, is replaced by a verbatim subset of itself. 75 conditions in total.

| Condition | Kind | Exact change | 2008 Summer Olympics rank/score | Summer Olympic Games rank/score | Both top-5 | Interpretation |
|---|---|---|---:|---:|---|---|
| baseline | baseline | original query, original index | 6 / 0.473542 | 13 / 0.361134 | no | exact reconstruction, 0 of 50 titles, max abs error 2.980e-07 |
| A | non-oracle | collapse the duplicated preposition `in  in` to `in` | 6 / 0.465842 | 12 / 0.351197 | no | removing the duplication is negative on both scores |
| B | non-oracle | `which held` to `which was held` | 6 / 0.479064 | 11 / 0.369280 | no | largest single grammatical gain; no rank crossing |
| C | non-oracle | `When did` to `When was` | 6 / 0.476802 | 11 / 0.365866 | no | same direction as B, smaller |
| AB | non-oracle | A+B | 6 / 0.472856 | 12 / 0.357917 | no | no recovery |
| AC | non-oracle | A+C | 6 / 0.469734 | 12 / 0.356363 | no | no recovery |
| BC | non-oracle | B+C | 6 / 0.481196 | 11 / 0.373662 | no | best two-factor cell; still no recovery |
| ABC | non-oracle | A+B+C | 5 / 0.475172 | 12 / 0.361902 | no | the complete grammatical repair moves the pair only from 6 and 13 to 5 and 12 |
| D1 | non-oracle | append the missing final question mark only | 6 / 0.472230 | 13 / 0.378853 | no | opposite signs; no rank change on either hop |
| D2 | non-oracle | strip the leading and trailing whitespace only | 6 / 0.473542 | 13 / 0.361134 | no | bit-identical to the baseline; whitespace is inert |
| D3 | non-oracle | A+B+C plus the question mark, a fully fluent question | 6 / 0.478597 | 12 / 0.381679 | no | fluency alone does not reach the cutoff |
| D4 | non-oracle | A+B+C with `which` replaced by `that` | 5 / 0.472287 | 11 / 0.361400 | no | no recovery |
| D5 | non-oracle | fluent repair in the perfect aspect | 6 / 0.478770 | 11 / 0.388446 | no | no recovery |
| D6 | non-oracle | fluent repair with `held three times` to `held for the third time` | 7 / 0.458305 | 15 / 0.361358 | no | aligning to the gold's own wording is negative for both hops |
| S1 | non-oracle | `the game` to `the multi-sport event` | 4 / 0.499784 | 8 / 0.440403 | no | naming the category, not the entity, lifts both hops |
| S2 | non-oracle | `the game` to `the sporting event` | 6 / 0.475048 | 9 / 0.416421 | no | weaker than S1 |
| S3 | non-oracle | `the game` to `the Games` | 4 / 0.518114 | 8 / 0.429262 | no | no recovery |
| S4 | non-oracle | `the game` to `the international multi-sport event` | 2 / 0.513077 | 7 / 0.468759 | no | strongest name-free single rewrite; still short of the cutoff on the answer hop |
| S5 | null control | D3 in upper case | 6 / 0.478597 | 12 / 0.381679 | no | equals D3 in every digit; the tokenizer is uncased |
| Z1 | name-free, gold-informed | S4 plus `in 2008` | 1 / 0.573634 | 10 / 0.416819 | no | bridge side only |
| Z2 | name-free, gold-informed | Z1 plus Tokyo 1964 and Seoul 1988 | 1 / 0.611326 | 6 / 0.450021 | no | bridge side saturated, answer hop still outside |
| Z3 | name-free, gold-informed | Z2 plus `hosted by a different city every four years` | 1 / 0.620961 | 2 / 0.541457 | yes | the name-free ceiling is reached, unlike D-025 |
| Z4 | name-free, gold-informed | the bridge passage's own sentence with the name removed | 3 / 0.572137 | 7 / 0.443012 | no | no recovery |
| Z5 | name-free, gold-informed | Z3 plus `Games of the Olympiad` | 1 / 0.694428 | 2 / 0.654954 | yes | strongest name-free condition |
| R1 | non-oracle | delete the whole referent clause | 39 / 0.351654 | 34 / 0.362962 | no | the description is net positive for both hops, the inverse of D-025 |
| R2 | non-oracle | delete `first held` | 5 / 0.473136 | 15 / 0.359977 | no | opposite signs by rank |
| R3 | non-oracle | delete `in  in East Asia` | 12 / 0.363965 | 7 / 0.385277 | no | opposite signs |
| R4 | non-oracle | delete `three times` | 7 / 0.457476 | 15 / 0.331495 | no | negative for both |
| R5 | non-oracle | delete `the game` | 6 / 0.390225 | 23 / 0.285117 | no | negative for both |
| R6 | non-oracle | delete `When did` | 7 / 0.459587 | 14 / 0.362919 | no | opposite signs, small |
| R7 | non-oracle | delete `East` | 4 / 0.492078 | 10 / 0.386454 | no | positive for both; still no recovery |
| Q1 | non-oracle probe | reduce to the referent clause alone | 6 / 0.437318 | 18 / 0.341210 | no | 10 of its top 10 lie inside the baseline top 12 |
| Q2 | non-oracle probe | reduce to `first held` | 241 / 0.198973 | 118 / 0.241051 | no | 0 of its top 10 lie inside the baseline top 12 |
| Q3 | non-oracle probe | reduce to `East Asia` | 135 / 0.212302 | 1408 / 0.068651 | no | neither hop is reachable |
| Q4 | non-oracle probe | reduce to `three times` | 1979 / 0.024835 | 795 / 0.061631 | no | inert cue |
| Q5 | non-oracle probe | reduce to `the game` | 707 / 0.117317 | 408 / 0.139988 | no | the head noun is not an anchor |
| Q6 | non-oracle probe | reduce to `When did the game first held` | 39 / 0.351654 | 34 / 0.362962 | no | equals R1, which contains the same tokens |
| Q7 | non-oracle probe | reduce to `three times in East Asia` | 21 / 0.241667 | 146 / 0.175661 | no | weak |
| Q8 | non-oracle probe | reduce to `multi-sport event` | 19 / 0.377593 | 4 / 0.445006 | no | the category phrase alone reaches the answer hop |
| Q9 | non-oracle probe | reduce to `game` | 480 / 0.116923 | 354 / 0.128865 | no | inert |
| Q10 | non-oracle probe | reduce to `When was it first held?` | 58 / 0.282614 | 29 / 0.319347 | no | weak |
| Q11 | non-oracle probe | reduce to `the game held for the third time in East Asia` | 8 / 0.422763 | 31 / 0.317180 | no | weaker than Q1 |
| Q12 | non-oracle probe | reduce to `international multi-sport event` | 11 / 0.439582 | 2 / 0.508778 | no | the answer hop is reachable from its category alone |
| K1 | oracle probe | reduce to the bridge gold's title | 1 / 0.704012 | 2 / 0.604224 | yes | D-024 precondition holds; the anchor also lifts the other hop |
| K2 | oracle probe | reduce to the answer gold's title | 2 / 0.662322 | 1 / 0.714462 | yes | same in the reverse direction |
| K3 | oracle probe | reduce to `Olympics` | 2 / 0.579752 | 1 / 0.625026 | yes | one bare word reaches both |
| K4 | oracle probe | reduce to `Olympic Games` | 2 / 0.642576 | 1 / 0.679302 | yes | as K3 |
| K5 | oracle probe | reduce to `Summer Olympics` | 2 / 0.624559 | 1 / 0.671807 | yes | as K3 |
| K6 | oracle probe | reduce to `Beijing 2008` | 1 / 0.577122 | 55 / 0.268544 | no | the one name form that reaches only one hop |
| N1 | oracle | append the bridge gold's title | 1 / 0.721951 | 3 / 0.526886 | yes | recovers both |
| N2 | oracle | append the answer gold's title | 1 / 0.669695 | 2 / 0.613922 | yes | recovers both |
| N3 | oracle | append both titles | 1 / 0.747634 | 2 / 0.563495 | yes | recovers both |
| N4 | oracle | name the entity in place, fluent | 1 / 0.653593 | 2 / 0.619747 | yes | recovers both |
| N5 | oracle | replace the whole description with the name | 2 / 0.639767 | 1 / 0.704515 | yes | recovers both |
| N6 | oracle | `the game` to `the Olympics` in the verbatim question | 1 / 0.562946 | 2 / 0.493941 | yes | recovers both from the unrepaired question |
| N7 | oracle | `the game` to `the Olympics` on the fluent repair | 1 / 0.556813 | 3 / 0.503440 | yes | recovers both |
| T | non-oracle, indexing | prepend every title and re-encode the corpus | 7 / 0.447820 | 12 / 0.354331 | no | negative for the bridge hop; title exclusion is not the mechanism |
| X1 | index-side removal | drop the 4 pooling-introduced passages above the bridge hop | 2 / 0.473542 | 9 / 0.361134 | no | answer hop unrecovered |
| X2 | index-side removal | drop the 10 pooling-introduced passages above the answer hop | 2 / 0.473542 | 3 / 0.361134 | yes | returns exactly the per-question ranking |
| X3 | index-side removal | drop all 5 passages above the bridge hop | 1 / 0.473542 | 8 / 0.361134 | no | answer hop unrecovered |
| X4 | index-side removal | drop the 39 corpus-wide sibling-event passages | 1 / 0.473542 | 4 / 0.361134 | yes | one competitor family suppresses both hops |
| X5 | index-side removal | drop only 1984 South Asian Games | 5 / 0.473542 | 12 / 0.361134 | no | the strongest single competitor is not decisive |
| X6 | index-side removal | keep only this question's own 10 paragraphs | 2 / 0.473542 | 3 / 0.361134 | yes | identical to X2 in every digit |
| L0 | null control | re-encode the answer gold's unchanged text alone | 6 / 0.473542 | 13 / 0.361134 | no | single-row substitution reproduces the baseline exactly |
| L0b | null control | re-encode the bridge gold's unchanged text alone | 6 / 0.473542 | 13 / 0.361134 | no | same for the other gold |
| L1 | gold-targeted index-side | answer gold reduced to its query-relevant first sentence, 34 words | 6 / 0.473542 | 8 / 0.425062 | no | dilution gate condition 2 holds for the answer hop |
| L1c | gold-targeted index-side | answer gold control, non-relevant sentences, 24 words | 6 / 0.473542 | 16 / 0.335471 | no | control does not improve |
| L1d | gold-targeted index-side | answer gold control, final sentence, 14 words | 6 / 0.473542 | 24 / 0.303537 | no | control does not improve |
| L1e | gold-targeted index-side | answer gold control, medal sentence, 30 words | 6 / 0.473542 | 101 / 0.222415 | no | nearest length-matched control; strongly worse |
| L1f | gold-targeted index-side | answer gold control, all four non-relevant sentences, 68 words | 6 / 0.473542 | 23 / 0.306344 | no | control does not improve; rank is not monotone in length |
| L2 | gold-targeted index-side | bridge gold reduced to its query-relevant final sentence, 28 words | 1 / 0.657794 | 13 / 0.361134 | no | dilution gate condition 2 holds for the bridge hop |
| L2c | gold-targeted index-side | bridge gold control, athlete-count sentence, 31 words | 76 / 0.240927 | 12 / 0.361134 | no | nearest length-matched control; strongly worse |
| L2d | gold-targeted index-side | bridge gold control, opening sentence, 39 words | 9 / 0.401914 | 13 / 0.361134 | no | control does not improve |
| L2e | gold-targeted index-side | bridge gold control, opening plus athlete sentences, 70 words | 9 / 0.381931 | 13 / 0.361134 | no | control does not improve |
| L2f | gold-targeted index-side | bridge gold control, all three non-relevant sentences, 89 words | 9 / 0.392902 | 13 / 0.361134 | no | control does not improve |
| L3 | gold-targeted index-side | both golds reduced to their query-relevant sentences at once | 1 / 0.657794 | 8 / 0.425062 | no | the dilution effect does not compose into a sufficient condition |

Single-factor effects:
The wording family is near-inert and inconsistent in direction. Its largest single effect is D1, appending the missing question mark, at plus 0.017719 on the answer hop with no rank change on either hop, and A, which removes the duplicated preposition, is negative on both scores. The complete grammatical repair moves the pair from 6 and 13 to 5 and 12, so the provisional primary's surface reading is falsified by measurement rather than by argument. The disambiguation family is uniformly positive on both hops and largest at S4, which reaches 2 and 7 without naming anything, so the second reading of the same provisional name is real and measurable but insufficient. Deleting the referent clause is strongly negative for the bridge hop at minus 0.121888 and neutral for the answer hop at plus 0.001828, so the description is a weak but net-positive anchor, the inverse of what D-025 recorded. Supplying the name is the only class of single factor that recovers both hops, and it does so in all seven surface forms. Title inclusion is negative for both hops and is excluded as the mechanism, as in D-019, D-020, D-021, D-023, D-024 and D-025. Of 19 single-factor conditions only 4 move the two hops in opposite score directions, against 10 of 19 in D-024 and 10 of 20 in D-025.

Combination and interaction effects:
A x B x C shows no material interaction: the three-factor cell lands in the same band as the best single factor and the best two-factor cell, and no cell of the design recovers either hop into the cutoff except the bridge hop's one-rank crossing in ABC. The only interaction that matters is additive and lies in the Z series, where the 2008 date and the two earlier host cities saturate the bridge hop at rank 1 while the answer hop needs its own defining phrase before Z3 reaches 1 and 2; success there must not be credited to any single one of those four facts. The combined ablation L3 gives 1 and 8, so the two dilution effects do not compose into a sufficient condition.

Supported interpretation:
The question requires a specific entity, the Summer Olympic Games, designates it only as `the game which held three times in East Asia`, and never names it. Under a whole-passage bi-encoder that scores each passage independently, that description matches every recurring multi-nation sporting event in the corpus about as well as it matches the two required passages, and the competitor family it produces is the same family that occupies the ranks above both golds. Supplying the name in any of seven forms resolves the ranking; repairing the question's grammar does not; refining the category wording without naming the entity helps measurably but not enough. Separately and independently, both required passages carry substantial text that bears none of the question's constraints, and removing that text raises each passage's similarity to this query while four length-matched controls per passage do not, which is the passage-level dilution statement D-023's gate licenses.

Closest competitor and tie-break:
The closest competitor is `peripheral_passage_content_dilution`. It satisfies all four of D-023's include conditions, and satisfies them on both required passages, which no earlier unit has achieved: the encoder's mean pooling and 256-token limit are verified from implementation and both golds sit inside it at 144 and 131 tokens; the controlled ablation improves the bridge hop from 6 to 1 and the answer hop from 13 to 8; and the length-matched controls do not improve either, the bridge hop's four controls at 31, 39, 70 and 89 words giving 76, 9, 9 and 9 and the answer hop's four at 14, 24, 30 and 68 words giving 24, 16, 101 and 23. It loses the primary tie-break on outcome determinacy: L2 recovers only the bridge hop, L1 only the answer hop, and L3, which applies both at once, still leaves the answer hop at 8. That is the same ground on which D-023 kept this descriptor out of the primary slot. The provisional primary `question_wording_ambiguity` is not the closest competitor because it is falsified rather than outranked, both of its readings having been tested with explicit conditions as pit 19e requires.

Considered and not adopted:
`question_wording_ambiguity`, unregistered, because the complete eight-cell grammatical-repair factorial reaches only 5 and 12 and the semantic reading of the same name reaches only 2 and 7; it is not registered. `adjacent_event_crowding`, unregistered, because Q1 shows the referent cue alone reproduces 10 of 10 of the observed family and R1 shows the family does not survive deletion of that cue, so the competition belongs to the primary mechanism; registering it would also duplicate `question_frame_semantic_crowding`. `question_frame_semantic_crowding`, because its include rule requires the competition to persist when the referent cue is removed, which R1 falsifies, and its third exclusion clause fires on the same evidence. `cross_passage_conjunction_unresolved`, because every name probe lifts both hops together, K1 raising the other gold to 2 and K2 raising the other gold to 2, where D-025 recorded the opposite sign; because only 4 of 19 single factors carry opposite signs against 10 of 19 in D-024 and 10 of 20 in D-025; and because one anchor reaches both required passages, so no intermediate fact has to be carried across passages. `compound_two_sided_crowding`, because removal probe X4 against one competitor family recovers both hops at 1 and 4, so there is no second mechanism to compound, which is the D-024 criterion. `gold_chain_substitutability`, `gold_chain_not_unique` and `plausible_non_gold_answer`, because each required fact occurs in exactly one passage, the gold itself. `generic_term_lexical_crowding`, by its own routing clause to lexical retrievers. `same_entity_variant_crowding`, because the competitors are distinct entities rather than variants of one, unlike D-015. `generic_person_semantic_neighborhood`, because the family is event pages rather than person biographies. `surface_form_tokenization_mismatch` and `minimal_preprocessing_score_distortion`, because this retriever has no lexical matching path and the two surface null controls, D2 for whitespace and S5 for letter case, are bit-identical to their comparators.

Not-run cells and attribution boundary:
Not run: Dense per-token decomposition, because the tool refuses it and a cosine ranking does not license token attribution; the idf-and-avgdl check D-024 requires after a failed pooling-removal probe, because a cosine carries no corpus statistic and X6 already reconstructs the per-question ranking exactly; oracle-plus-ablation combinations, because the single-factor name conditions already recover both hops and adding a second factor could only weaken the attribution; a removal probe against the Q2 family, because 0 of its top 10 appear in the baseline top 12 and it is therefore not present in the observed ranking; any BM25 factorial, because the comparison retriever is reachability evidence only. Attribution boundary: do not claim that the encoder attended to, weighted or averaged away any token; the L block licenses only the passage-level statement that replacing a passage's text with a verbatim subset of its own sentences changes that passage's similarity to this query. Do not read X2, X4 or X6 as repairs, since all three require knowing which passages are rivals. Do not read any N, K or Z condition as a deployable fix. Do not compare Dense and BM25 score magnitudes or treat the comparison retriever's ranking as a cause of the Dense ordering. Do not treat rank, cutoff proximity, retriever identity, question type or corpus setting as causal categories.

Boundary:
Four boundaries are recorded rather than closed. This is the third primary use of `description_only_bridge_entity` and all three are Dense, while the registry definition still reads `no unique person-name or entity-name anchor for lexical retrieval`, the wording problem D-023 registered for the vocabulary audit. The structure differs from both earlier primary uses in a way the inclusion rule does not address: in D-017 and D-023 the unnamed described entity was a pure bridge entity, whereas here it is the subject of the answer passage itself and the bridge passage is what licenses the identification; the inclusion rule is met either way. `peripheral_passage_content_dilution` now has two acceptances and one rejection, D-023, this unit and D-025, and this is the first unit in which its gate is passed on both required passages; whether four conditions is the right threshold remains the open audit question. Finally, the backlog item D-025 opened, whether the vocabulary needs a question-quality descriptor, receives its first measurement here and the measurement argues against creating one on the strength of surface malformation alone; queue item 21 carries the same provisional name on a BM25 unit and must be judged separately.

Confidence:
Medium-high. The baseline reproduces the stored top-50 order with zero title mismatches at a maximum absolute score error of 2.980e-07, the per-question ordering is asserted equal to the official file title by title, all eight cells of the defined design were run together with 67 further conditions, the single-row substitution used for the ablations is validated by two null controls that reproduce the baseline exactly, the dilution gate's control condition is tested at four separate lengths per passage rather than at one, all 11 non-gold passages above the answer hop were read in full, and the dossier's reproduction script passes 516 assertions. The provisional primary and each of the three candidate primaries are excluded by a specific measured condition rather than by argument. The limitations are that no deployable single factor recovers both hops, the only recovering conditions being oracle names, two index-side removal probes and a name-free rewrite that returns four gold facts to the query; that the bridge hop's margin of 0.005537 is small enough that the reconstruction's own environment boundary matters, since the dependency versions and model revision of the historical run cannot be asserted; and that the dilution result is a passage-level statement and not an attribution.

Speculation boundary:
Do not claim that the encoder maps `the game` to video-game semantics, even though probe Q5 returns Tron and Gamer pages first; that is one probe's output, not an attribution. Do not explain why 1984 South Asian Games holds rank 1; probe X5 shows it is not outcome-determinative and no experiment isolates the reason, in particular not that South Asian was read as East Asian. Do not treat the identification of 1896 as the HotpotQA answer string as observed evidence; the answer field is absent from every read-only artifact available here and this is an inference from the answer gold's own text. Do not treat the question's malformation as a known annotation-pipeline defect; only its retrieval effect was measured. Do not read the failure as caused by pooling merely because per-question succeeds; X2 measures how much of the ranking pooling supplies, and D-003 keeps corpus setting as provenance.
## D-027 - Reclassify the Albee / Barrie Dense comparison unit as one-sided entity crowding

- **Date:** 2026-08-04
- **Status:** active
- **Decision:** For `5a78b209554299148911f93e|dense`, replace the provisional primary
  `related_document_crowding` with `one_sided_entity_crowding`. Adopt
  `related_name_document_crowding` and `peripheral_passage_content_dilution` as
  secondaries, the latter scoped to `Edward Albee` only. Remove
  `cutoff_sensitive_near_miss`. Do not register `related_document_crowding`. Use
  `related_name_document_crowding` as the closest competitor.
- **Affected unit:** `5a78b209554299148911f93e|dense`.
- **Question:** `Which playwright lived a longer life, Edward Albee or J. M. Barrie?`
  This is a comparison unit, so both required passages are candidates the question
  names outright, and each supplies one lifespan, 1928 to 2016 for Albee and 1860 to
  1937 for Barrie.
- **Verified implementation:** Symmetric `sentence-transformers/all-MiniLM-L6-v2`
  encodes the unchanged query and paragraph text only, never titles, L2-normalizes
  explicitly so dot product equals cosine, and scores every passage independently with
  no cross-passage reasoning and no main-run reranker. Mean pooling has a 256-token
  limit and the golds use 95 and 167 model tokens, so truncation is excluded. Because
  each passage is encoded independently, replacing one row of the document matrix is
  exactly equivalent to re-encoding the whole corpus, and two single-row null controls
  confirm it, reproducing the baseline at matrix differences of 1.550e-07 and 9.220e-08.
  Reference: `references/dense_implementation_reference.md`.
- **Exact reconstruction:** Re-encoding the same 4,937 deduplicated pooled passages
  reproduces all 50 stored top-50 titles in order with a maximum absolute score error
  of 2.384e-07, so strong causal claims are supported. Complete-corpus ranks are
  9 / 0.432454 for `Edward Albee` and 8 / 0.434342 for `J. M. Barrie`; both are
  retrieved. The rank-5 score is 0.538556, so the two golds are 0.106102 points, or
  19.701 percent, and 0.104214 points, or 19.351 percent, below the cutoff, and a gap
  of 0.067081 separates rank 7 from rank 8.
- **Diagnostic scale:** 66 distinct conditions on the same unchanged candidate set,
  plus 7 deliberate duplicates that all reproduced bit for bit: an indexing condition
  T, all eight cells of an A x B x C wording-repair factorial, eleven reachability
  probes, three further reduced-query probes, three reverse cue-deletion probes, twelve
  index-side removal probes including a six-step cumulative dose-response ladder and a
  restriction to the item's own ten passages, twenty-two gold-targeted index-side text
  conditions including two single-row null controls and name-preserving length-matched
  controls on both sides, and six oracle conditions.
- **Observed passage evidence:** Every passage above both golds was read in full. Six
  of the seven are Albee-related and the seventh is unrelated to either candidate:
  `Reed A. Albee` 1 / 0.630886, his adoptive father; `Finding the Sun` 2 / 0.597466,
  `Edward F. Albee Foundation` 3 / 0.567801, `Edward Albee's At Home at the Zoo`
  4 / 0.542102, `The Zoo Story` 5 / 0.538556 and `Three Tall Women` 6 / 0.519974, his
  works and his namesake foundation; and `Jeffrey Stanley` 7 / 0.501423, a playwright
  unrelated to either candidate. None of the seven states either lifespan. There is no
  competitor family on the Barrie side: only 4 non-gold corpus passages contain the
  string `barrie` and none appears in the reconstructed top 50.
- **No substitute and no complete non-gold answer:** A full-corpus substring scan finds
  0 passages mentioning both playwrights, exactly 1 containing Albee's two dates, itself,
  and exactly 1 containing Barrie's two dates, itself. `Reed A. Albee` states that Edward
  Albee is an American playwright but gives its own subject's dates, 1885 to 1961, so
  under pit 19b it is a distractor and not an evidence-bearing substitute.
- **Index-side removal, the only intervention that works, with dose-response:**

| Condition | Kind | Exact change | `Edward Albee` rank/score | `J. M. Barrie` rank/score | Both top-5 |
|---|---|---|---:|---:|---|
| **baseline** | baseline | original query | 9 / 0.432454 | 8 / 0.434342 | **no** |
| **X1.1** | index-side removal | drop 1 Albee-related passage | 8 / 0.432454 | 7 / 0.434342 | **no** |
| **X1.2** | index-side removal | drop 2 | 7 / 0.432454 | 6 / 0.434342 | **no** |
| **X1.3** | index-side removal | drop 3 | 6 / 0.432454 | 5 / 0.434342 | **no** |
| **X1.4** | index-side removal | drop 4 | 5 / 0.432454 | 4 / 0.434342 | **yes** |
| **X1.5** | index-side removal | drop 5 | 4 / 0.432454 | 3 / 0.434342 | **yes** |
| **X1** | index-side removal | drop all 6 | 3 / 0.432454 | 2 / 0.434342 | **yes** |
| **X2** | index-side removal | drop only the 4 Albee works | 5 / 0.432454 | 4 / 0.434342 | **yes** |
| **X3** | index-side removal | drop only the relative and the foundation | 7 / 0.432454 | 6 / 0.434342 | **no** |
| **X4** | index-side removal | drop only `Jeffrey Stanley` | 8 / 0.432454 | 7 / 0.434342 | **no** |
| **X5** | index-side removal | drop all 8 non-gold passages containing `albee` | 3 / 0.432454 | 2 / 0.434342 | **yes** |
| **X6** | index-side restriction | keep only the item's own 10 passages | 8 / 0.432454 | 7 / 0.434342 | **no** |
| **X7** | index-side removal | drop the 6 plus `Jeffrey Stanley` | 2 / 0.432454 | 1 / 0.434342 | **yes** |

  X5 equals X1 because the 8 non-gold passages containing `albee` are exactly this
  item's 8 HotpotQA distractors. Under every removal condition the golds' own scores are
  unchanged, so the claim is strictly that the competitors occupy the top-five positions
  and never that they depress the golds' similarity.
- **No deployable non-oracle repair exists.** All eight wording-repair cells fail; the
  best are 8 / 9 when the interrogative frame is stripped and 10 / 7 when an explicit
  lifespan facet and a biography cue are combined, and both of those single factors move
  Albee the wrong way. Indexing the title is inert at 9 / 8. Query splitting, the natural
  deployable repair for a comparison question, was measured in three forms, the full
  frame with one side deleted, a natural how-long rephrasing and the bare names, and the
  union of the two single-sided top-five lists contains both golds in none of them.
- **Per-side reachability is radically asymmetric, and this carries the tie-break.**
  `J. M. Barrie` ranks 1 under all five single-sided queries tried: its bare name
  1 / 0.489864, the full frame with the Albee side deleted 1 / 0.563657, a how-long
  rephrasing 1 / 0.469371, a biography cue 1 / 0.560769, and deletion of the surname
  `Albee` alone 1 / 0.517261. `Edward Albee` reaches the top five under none of the five
  distinct non-oracle Albee-directed queries: 6 / 0.450564 from its own bare name,
  7 / 0.532719 from the full frame with the Barrie side deleted, 8 / 0.370142 from a
  how-long rephrasing, 7 / 0.498276 from a biography cue, and 7 / 0.493638 from the name
  plus lifespan vocabulary. Its satellite documents outrank it even when the query is
  nothing but its name. The one Albee-directed query that does reach the cutoff is an
  oracle condition using the gold passage's own formal name form
  `Edward Franklin Albee III`, at 5 / 0.398151, and it pushes the Barrie side to
  3221 / 0.010108, so it recovers nothing either. This is the first unit in which the
  D-025 evidence leg, each side reachable at rank 1 from its own bare name, fails on one
  side.
- **Oracle conditions all fail, and oracle-name injection is degenerate here.** Because
  the question already names both golds, appending a gold title is token duplication:
  appending `Edward Albee` gives 7 / 11, appending `J. M. Barrie` gives 9 / 8, appending
  both gives 8 / 9, appending the answer entity gives 7 / 12, injecting the four date
  tokens gives 9 / 10, and injecting both lifespans verbatim gives 9 / 10. The
  single-factor oracle-name test that D-020 introduced and D-017, D-023 and D-026 passed
  cannot be run in its usual form on a comparison unit, and the D-024 precondition about
  anchor matchability is likewise inapplicable.
- **Competitor family verified in both directions, as pit 19i requires.** The Albee
  referent cue alone reproduces 6 of 10 of its top ten inside the baseline top seven,
  7 of 10 inside the top ten and 8 of 10 inside the top twelve; deleting that cue from
  the full question leaves 1 of 10 and no Albee-related passage at all. The generic type
  cue alone gives 2 of 10, the answer facet alone gives 0 of 10, and the question frame
  without either name gives 1 of 10, which excludes `question_frame_semantic_crowding`
  by the same test. The forward result does not route the descriptor to a different
  primary here, because the cue that reproduces the family is one of the two candidates
  the question must name, so there is no more specific upstream mechanism to route to.
- **`peripheral_passage_content_dilution` passes on one side and fails on the other.**
  On `Edward Albee` all four include conditions hold: mean pooling is verified,
  truncation is excluded at 95 tokens, the controlled ablation to the query-relevant
  clause moves 9 / 0.432454 to 1 / 0.663123, and the length-matched controls do not
  improve it. The decisive control pair is name-preserving and length-matched at once:
  removing only the works list, 40 words, gives 2 / 0.601674, while removing only the
  awards sentence and keeping the works list, 41 words, gives 8 / 0.441928. Two 18-word
  name-preserving controls give 8 / 0.446975 and 7 / 0.512652 against 1 / 0.663123 for
  the 17-word ablation, and rank is not monotone in length anywhere on the curve.
  Keeping the name and `playwright` while deleting the dates still gives 1 / 0.632052,
  while keeping the name and the dates while deleting `playwright` gives 8 / 0.471766,
  so the decisive content is the playwright predicate and the works list suppresses it.
  On `J. M. Barrie` the same ablation moves 8 / 0.434342 only to 7 / 0.512680, so the
  material-improvement condition fails; ablating both golds at once still leaves
  1 / 0.663123 and 8 / 0.512680. This is the descriptor's third application, its second
  pass, its first single-sided pass, and the third time it does not win the primary.
- **Single-factor and interaction effects:** 21 of 50 conditions carry opposite signs
  across the two candidates, against 4 of 19 in D-026, 10 of 20 in D-025 and 10 of 19
  in D-024. The governing interaction is that removal and ablation point in different
  directions: removing the competitor family recovers both required passages, while
  repairing either gold's own text recovers only that one, and repairing both still
  leaves 1 / 0.663123 and 8 / 0.512680. So the binding constraint on the pair is the
  Albee family, neither gold's own content nor any Barrie-side competitor. Ablating
  Albee also pushes Barrie from 8 to 9, which is itself evidence that the two candidates
  compete for the same positions.
- **Corpus provenance:** Pooled and per-question agree on both metrics, `any@5` 0 and
  `full@5` 0. This is the first unit in this series where the corpus setting changes
  neither metric, after five consecutive units in which at least `any@5` flipped, and
  the second after D-021 in which per-question failure excludes pooling outright. Six of
  this item's own eight HotpotQA distractors are Albee-related and hold per-question
  ranks 1 to 6 ahead of the golds at 7 and 8, so the competitor family is
  annotator-constructed rather than pooling-introduced, a source distinct from both
  paths recorded so far. Pooling adds exactly one competitor above the golds,
  `Jeffrey Stanley`, moving each gold down one rank without crossing the cutoff, and
  dropping only it gives 8 / 7. Restricting the pooled ranking to the item's ten
  paragraphs reproduces the official per-question window title by title, confirming for
  the second time after D-025 that a Dense per-question ranking is exactly the
  restriction of the pooled ranking; the idf and avgdl check D-024 requires after a
  failed pooling-removal probe is therefore inapplicable and was not run. Corpus setting
  remains provenance under D-003.
- **Comparison-retriever evidence and its boundary:** Complete-corpus pooled BM25 places
  `Edward Albee` at 6 / 19.520331 and `J. M. Barrie` at 640 / 4.908864, so the stored
  `not_in_top50` for the BM25 unit is a real rank of 640 of 4,937 and not corpus absence.
  This establishes only that Dense reaches the Barrie passage where BM25 does not. It is
  not a Dense cause, the two backends' score magnitudes are not comparable, and the BM25
  unit for the same `example_id` is a different analytical unit whose mechanism D-010
  attributes to name-form tokenization mismatch; that attribution is not carried across.
- **Why `cutoff_sensitive_near_miss` is removed:** At 19.351 and 19.701 percent below
  the rank-5 score both golds fall in the band this project has excluded, 24.619 percent
  in D-026 and 52.794 percent in D-025, and far outside the band it has accepted, 1.156
  percent in D-026, 2.17 in D-022, 4.137 in D-023 and 4.503 in D-025. A gap of 0.067081
  separates rank 7 from rank 8, so there is a real score cliff between the cutoff region
  and the golds. The counter-evidence is recorded rather than suppressed: removing only
  three competitors already lifts Barrie to 5, so the metric is sensitive to a small
  index-side change even though the golds are not close to the cutoff in score. Giving
  `far below the cutoff` a numerical definition would require editing the registry entry
  and is deferred to the vocabulary audit.
- **Tie-break:** Prefer `one_sided_entity_crowding` over `related_name_document_crowding`.
  Both inclusion rules are satisfied, so the tie-break is not decided there, as pit 13
  requires, and both point at the same passages. The decision turns on which name
  accounts for both required passages. `related_name_document_crowding` says what the
  competitors are but cannot explain why `J. M. Barrie` fails, since Barrie has no name
  link to any of them and ranks 1 under all five single-sided queries; only the statement
  that all the crowding comes from one of the two named candidates, and therefore fills
  the top five that both candidates must share, covers the pair, and a comparison unit
  fails or succeeds as a pair. D-010's routing clause, which prefers a more specific
  implementation-supported name-form mismatch, does not fire here: the Dense backend
  performs no tokenization or literal matching and condition T is inert at 9 / 8. The two
  units have different unit keys, so reaching a different primary here is the unit-key
  rule working rather than D-010 being carried across.
- **Excluded descriptors:** `compound_two_sided_crowding`, because one competitor family
  suppresses both required passages under pit 19h and the Barrie side has no competitor
  family at all. `generic_person_semantic_neighborhood`, by its own exclusion, which
  names the case where documents related to only one comparison entity dominate; only
  1 of the 7 passages above the golds is a generic person biography.
  `same_artist_work_crowding`, whose inclusion rule is met by the 4 Albee works, and
  which X2 shows are sufficient on their own, but whose definition is anchored on sibling
  works outranking a gold *work* while the gold here is the creator's biography, and
  whose content is already covered by `related_name_document_crowding`.
  `two_named_entities_underprioritized`, because the Albee name is not underweighted but
  overwhelmingly effective, merely at the wrong Albee documents, the opposite of D-009.
  `same_entity_variant_crowding`, because the competitors are distinct entities rather
  than variants of one. `cross_passage_conjunction_unresolved`, because its inclusion
  rule requires an intermediate fact to be resolved in one passage and carried into
  scoring another, and a comparison question's two lifespans are independent, so the
  contract is bridge-shaped and is not met. `question_frame_semantic_crowding`, on the
  1 of 10 measurement above. `plausible_non_gold_answer`, `gold_chain_not_unique` and
  `gold_chain_substitutability`, on the substring scan. `missing_second_comparison_entity`,
  because both golds are retrieved at 8 and 9. `description_only_bridge_entity`, because
  there is no bridge entity and both candidates are named outright.
  `possible_type_mismatch`, because both golds call themselves `playwright`.
  `surface_form_tokenization_mismatch` and `minimal_preprocessing_score_distortion`,
  because no Dense preprocessing path is attributable and T is inert.
- **Speculation boundary:** Do not claim the satellite passages score higher because
  their text is almost entirely `playwright` plus `Edward Albee`; that needs
  distractor-side ablation, a fourth intervention class with no precedent contract here.
  Do not claim `Jeffrey Stanley` ranks 7 as a prototype playwright biography on one
  forward probe. Do not claim the shared query vector is what costs each side roughly
  0.10 of similarity, Albee 0.532719 to 0.432454 and Barrie 0.563657 to 0.434342,
  without an attribution experiment. Do not generalize the annotator-constructed
  one-sided distractor set from n equals 1. Do not upgrade the dilution finding to
  token-level attribution; pit 18 stands and only a passage-level statement is licensed.
  Do not write any L condition or any removal probe as a deployable repair. Do not read
  the 5 / 0.398151 reachability figure as non-oracle; it uses the gold passage's own
  formal name form.
- **Not run and why:** T crossed with the eight wording cells, because T is inert alone
  and the wording direction is already exhausted. Removal crossed with ablation, because
  removal alone already recovers both and the cross would merge two sufficient conditions
  in one cell. A Barrie-side removal probe, because there is nothing to remove, the 4
  non-gold `barrie` passages all being absent from the reconstructed top 50. A BM25
  per-question reconstruction, because BM25 serves only as reachability evidence and its
  complete-corpus pooled rank is what this unit needs. Further oracle date variants,
  because verbatim lifespan injection already failed at 9 / 10. Distractor-side text
  ablation, as above.
- **Taxonomy effect:** `taxonomy_defect_flag=false`; `one_sided_entity_crowding` is
  already item 13 of the primary inventory, so no name is created. Two boundaries are
  registered rather than closed. First, this is the first validated primary use of the
  name, which before this unit survived in the inventory only as a first-pass value on
  two rows, this example's BM25 unit, superseded by D-010 through `candidate_category`,
  and `5ab8f57b5542991b5579f097|bm25` as queue item 19, still `not_started`; whether
  crowding-family names need an explicit primary-use contract, as
  `cross_passage_conjunction_unresolved` does, is a vocabulary-audit question. D-010
  called this name the resulting ranking pattern and less specific; the position taken
  here is narrower, that it states which documents compete and which of the two named
  candidates they belong to rather than anything about rank itself, so pit 17 is not
  violated, on the same footing that let D-018 adopt `compound_two_sided_crowding` as a
  primary. Second, `related_name_document_crowding` is adopted on a Dense unit for the
  first time while its definition reads `sharing a name or name token`, which is lexical
  wording; all 6 competitors do literally contain `Albee` in their text so the surface
  fact holds, but whether the definition needs rewording for a bi-encoder is the same
  question already open for `description_only_bridge_entity` and is left to the audit.
  `related_document_crowding` is deliberately not registered, because a registry entry
  for it would duplicate `related_name_document_crowding`, whose definition already
  covers relatives, works, institutions and associates; this is the reason D-025 used
  for `generic_context_substitution` and D-026 for `adjacent_event_crowding`. No
  definition, inclusion rule or exclusion rule is changed.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_comparison_5a78b209554299148911f93e.md`.

## D-028 - Reclassify the Ron Joyce / Tim Hortons BM25 unit as minimal-preprocessing score distortion

- **Date:** 2026-08-04
- **Status:** active
- **Decision:** For `5a79b7f6554299029c4b5f6f|bm25`, replace the provisional primary
  `generic_term_lexical_crowding` with `minimal_preprocessing_score_distortion`. Adopt
  `surface_form_tokenization_mismatch`, the newly registered
  `unindexed_title_name_anchor`, `generic_term_lexical_crowding` and
  `description_only_bridge_entity` as secondaries. Delete the unregistered
  `bridge_relation_underweighted`. Use `description_only_bridge_entity` as the closest
  competitor. Do not adopt `cutoff_sensitive_near_miss`.
- **Affected unit:** `5a79b7f6554299029c4b5f6f|bm25`.
- **Question:** `How many restaurants comprise the quick service restaurant chain that Ron
  Joyce helped found?` This is a bridge unit. `Ron Joyce` states that he co-founded the Tim
  Hortons doughnut chain and `Tim Hortons` states that it had 4,613 restaurants as of
  December 31, 2016, so the person is named in the question and the chain that carries the
  answer is not.
- **Verified implementation:** Only paragraph text is indexed and the title is not;
  `_tokenize` is `text.lower().split()` with no punctuation removal, stop-word removal,
  stemming, Unicode normalization or phrase matching; `rank-bm25==0.2.2` `BM25Okapi` runs
  at the library defaults `k1=1.5`, `b=0.75`, `epsilon=0.25` and accumulates one
  contribution per query-token occurrence. Corpus avgdl is 90.88495037472148. Reference:
  `references/bm25_implementation_reference.md`.
- **Exact reconstruction:** Rebuilding the same 4,937 deduplicated pooled passages
  reproduces all 50 stored top-50 titles in order with a maximum absolute score error of
  0.000000, and every per-token decomposition reconciles against `get_scores` within
  7.105e-15, so strong causal claims are supported. Complete-corpus ranks are
  16 / 21.492350 for `Ron Joyce` and 8 / 27.226538 for `Tim Hortons`; both are retrieved.
  The rank-5 score is 31.122376, so the golds sit 9.630026 points, or 30.942 percent, and
  3.895838 points, or 12.518 percent, below the cutoff. There is no score cliff: the
  successive differences from rank 4 to rank 9 are 0.597253, 1.720835, 0.694195, 1.480808
  and 1.252255.
- **Diagnostic scale:** 94 conditions on the same unchanged candidate set, two of them
  deliberate duplicates that reproduced bit for bit: all sixteen cells of a P x E x S x T
  preprocessing and indexing factorial, six further cells adding a crude morphological stem
  M, three single-sided controls splitting P into its query-side and document-side halves,
  five gold-targeted index-side single-token repairs including a null control, six query
  wording conditions, fourteen single query-token deletions, twelve reduced-query probes,
  five reverse cue-deletion probes, seven per-side reachability probes, eleven index-side
  removal probes including a six-step cumulative dose-response ladder, seven oracle
  conditions, and two corpus-setting reconstructions.
- **The two hops match completely disjoint query-token sets.** `Ron Joyce` scores
  21.492350 from three tokens only, `joyce` 11.846012, `chain` 6.841956 and `the` 2.804382.
  `Tim Hortons` scores 27.226538 from four tokens, every one of them from the generic
  category facet, `restaurant` 8.607975, `quick` 7.267774, `restaurants` 6.664213 and
  `service` 4.686577. Each of the fifteen non-gold passages above the bridge gold earns
  between 18.094218 and 29.047969 from that same facet and exactly 0.000000 from `ron` and
  `joyce`, so the corpus's only occurrence of `joyce`, one passage in 4,937 at an idf of
  8.098947, is worth less to its own passage than the generic facet is worth to any
  competitor. The facet tokens sum to an idf of 25.249066 against 13.796955 for the name.
- **Three implementation choices block the golds' own tokens.** The bridge gold's body
  writes `Ronald Vaughan "Ron" Joyce`, so its nickname tokenizes as `"ron"` and the query's
  `ron` scores 0.000000 against it, while its title, which is exactly the query's name, is
  not indexed. The answer gold writes `restaurant chain;`, so its `chain` tokenizes as
  `chain;` and the query's `chain` scores 0.000000 against it. There is no stemming, so
  `restaurant` and `restaurants` are two distinct query tokens and the category facet is
  counted twice; adding a stem makes both golds worse at 19 / 21.398601 and 10 / 30.179957,
  because it merges those two into one repeated token that is accumulated per occurrence in
  favour of the same competitors.
- **The preprocessing and indexing factorial, with the two decisive cells:**

| Condition | Kind | Exact change | `Ron Joyce` rank/score | `Tim Hortons` rank/score | Both top-5 |
|---|---|---|---:|---:|---|
| **baseline** | baseline | original query and index | 16 / 21.492350 | 8 / 27.226538 | **no** |
| **P** | factorial, non-oracle | boundary punctuation normalized | 7 / 29.569770 | 3 / 32.295791 | **no** |
| **E** | factorial, non-oracle | Unicode dash normalized | 16 / 21.492221 | 8 / 27.226538 | **no** |
| **S** | factorial, non-oracle | scaffold `how`, `that`, `the` removed | 15 / 18.687969 | 7 / 27.226538 | **no** |
| **T** | factorial, non-oracle, indexing | title prefixed into the index | 2 / 32.480848 | 9 / 27.212243 | **no** |
| **PE** | factorial | P and E | 7 / 29.569283 | 3 / 32.295791 | **no** |
| **PS** | factorial | P and S | 8 / 26.814839 | 1 / 32.295791 | **no** |
| **PT** | factorial | P and T | 2 / 34.444959 | 4 / 32.279538 | **yes** |
| **ES** | factorial | E and S | 15 / 18.687969 | 7 / 27.226538 | **no** |
| **ET** | factorial | E and T | 2 / 32.480717 | 9 / 27.212243 | **no** |
| **ST** | factorial | S and T | 2 / 29.697112 | 8 / 27.212243 | **no** |
| **PES** | factorial | P, E and S | 8 / 26.814839 | 1 / 32.295791 | **no** |
| **PET** | factorial | P, E and T | 2 / 34.444468 | 4 / 32.279538 | **yes** |
| **PST** | factorial | P, S and T | 2 / 31.710535 | 1 / 32.279538 | **yes** |
| **EST** | factorial | E, S and T | 2 / 29.697112 | 8 / 27.212243 | **no** |
| **PEST** | factorial | all four | 2 / 31.710535 | 1 / 32.279538 | **yes** |
| **M** | factorial, non-oracle | crude morphological stem | 19 / 21.398601 | 10 / 30.179957 | **no** |
| **PM** | factorial | P and M | 15 / 29.421556 | 8 / 34.974296 | **no** |
| **PMS** | factorial | P, M and S | 12 / 26.669974 | 3 / 34.974296 | **no** |
| **PMT** | factorial | P, M and T | 9 / 34.297886 | 8 / 34.959874 | **no** |
| **PMST** | factorial | P, M, S and T | 9 / 31.566745 | 3 / 34.959874 | **no** |
| **MT** | factorial | M and T | 8 / 32.387814 | 11 / 30.167545 | **no** |
| **Pq** | single-sided control | P applied to the query only | 16 / 21.492350 | 8 / 27.226538 | **no** |
| **Pd** | single-sided control | P applied to the index only | 7 / 29.569770 | 3 / 32.295791 | **no** |
| **PdT** | single-sided control | Pd and T | 2 / 34.444959 | 4 / 32.279538 | **yes** |

  Every condition that recovers both hops contains both P and T, and the interaction is
  clean: P alone recovers only the answer hop and T alone recovers only the bridge hop while
  moving the answer hop the wrong way. Without T the bridge hop reaches 7 at best under any
  condition of any kind; without P the answer hop reaches 7 at best and never enters the
  cutoff. E is inert, changing no
  rank and only the fourth decimal of either score.
- **The whole P effect is index-side.** Query-side-only normalization reproduces the
  baseline exactly, because the single query token it changes is `found?`, which is absent
  from the corpus vocabulary altogether, and index-side-only normalization reproduces the
  full P condition exactly. Cleaning the question is therefore worth nothing on this unit
  and only re-tokenizing the corpus helps.
- **Gold-targeted index-side single-token repairs, against a null control:**

| Condition | Kind | Exact change | `Ron Joyce` rank/score | `Tim Hortons` rank/score | Both top-5 |
|---|---|---|---:|---:|---|
| **G0** | gold-targeted index-side, null control | both gold texts rebuilt unchanged | 16 / 21.492350 | 8 / 27.226538 | **no** |
| **G1** | gold-targeted index-side | bridge gold `"Ron"` becomes `Ron` | 6 / 29.740240 | 9 / 27.226538 | **no** |
| **G2** | gold-targeted index-side | answer gold `chain;` becomes `chain` | 16 / 21.460260 | 2 / 32.708285 | **no** |
| **G1+G2** | gold-targeted index-side | both of the above | 7 / 29.708153 | 2 / 32.708285 | **no** |
| **G3** | gold-targeted index-side | bridge gold `co-founded` becomes `helped found` | 8 / 28.453317 | 9 / 27.226556 | **no** |

  The quotation marks are worth 8.247890 points and ten rank positions, the semicolon
  5.481747 points and six, and the relation wording 6.960967 points and eight. Repairing
  exactly the two punctuation artifacts on both golds still leaves the bridge hop at 7, so
  punctuation alone is not sufficient even as a gold-targeted intervention. These are
  third-class interventions under pit 19d and are not deployable repairs.
- **Eight of the eighteen single factors are completely inert:** deleting `how`, `many`,
  `comprise`, `that`, `ron`, `helped` or `found?`, and E. Deleting `ron` changes neither
  gold's rank because `ron` matches nothing in either of them. `found?` occurs in 0 corpus
  passages against 75 for `found`, so the query's final token contributes exactly 0.000000
  to every passage, the third instance of this pattern after D-019 and D-021, and no wording
  condition repairs it: replacing `helped found` with `co-founded` or with `founded`, or
  merely dropping the question mark, all reproduce the baseline exactly, because
  `co-founded?` and `founded?` are equally absent from the vocabulary. `comprise` occurs in
  5 passages and in neither gold, and replacing it makes both golds worse at 18 / 21.492350
  and 10 / 29.558124.
- **Six single factors carry opposite signs across the hops**, T and the deletion of
  `restaurants`, `quick`, `service`, `restaurant` or `chain`, against three same-signed and
  one single-sided. Deleting `restaurant` alone gives 5 / 21.492350 and 12 / 18.618563,
  deleting `chain` alone gives 18 / 14.650394 and 2 / 27.226538, and deleting `joyce` gives
  100 / 9.646338 and 8 / 27.226538. Compare 21 of 50 in D-027, 4 of 19 in D-026, 10 of 20 in
  D-025 and 10 of 19 in D-024.
- **Observed passage evidence:** every one of the fourteen non-gold passages above the
  bridge gold was read in full, and every one is a restaurant-chain profile or the generic
  `Fast food restaurant` definition. None mentions Ron Joyce or Tim Hortons, which the
  decomposition confirms exactly, their `ron` and `joyce` contributions all being 0.000000,
  and none states the count for the chain he co-founded. Eight of them state a restaurant
  count, over 19, almost 60, more than 70, more than 50, 14, over 550, over 50 and 27, but
  every one counts a different chain.
- **No substitute and no complete non-gold answer:** a full-corpus substring scan finds
  exactly 2 passages containing `tim hortons`, the two golds themselves, exactly 1
  containing `4,613`, itself, exactly 1 containing `ronald vaughan`, itself, and exactly 1
  containing `co-founded the tim`, itself. The literal string `ron joyce` occurs in 0
  passages, not even in the bridge gold, whose body writes `"Ron" Joyce`.
- **The competitor family is verified in both directions, as pit 19i requires.** Forward,
  the descriptive referent cue `quick service restaurant chain` alone puts 9 of 10 of its top
  ten inside the baseline top-fifteen non-gold set, and the whole descriptive clause does the
  same at 9 of 10, while `restaurant chain` gives 8 of 10 and `quick service` gives 8 of 10.
  In reverse, deleting `quick service restaurant chain` from the full question leaves 3 of
  10 and deleting the whole descriptive referent leaves 3 of 10, whereas deleting the
  person's name leaves the family untouched at 9 of 10. The count facet alone gives 5 of 10
  and `comprise` alone gives 0 of 10. Both directions agree, which is what D-023 and D-024
  had only in the forward direction.
- **Per-side reachability is asymmetric but holds on both sides.** The bridge hop ranks
  1 / 11.846012 from the query's own name `Ron Joyce`, 1 / 20.073893 from that name under an
  index-side normalized index, 1 / 19.540866 from the unqueried full-name variant `Ronald
  Joyce`, and 1 / 9.646338 when only the name and the relation survive; the answer hop falls
  to 4892 or 4895 at 0.000000 in every one of these. The answer hop reaches 7 / 20.562326
  from its complete non-oracle description and 4 from the two-token `quick service`, and
  reaches 1 / 20.433077 only from its own name, which is oracle.
- **Index-side removal cannot recover the bridge hop:**

| Condition | Kind | Exact change | `Ron Joyce` rank/score | `Tim Hortons` rank/score | Both top-5 |
|---|---|---|---:|---:|---|
| **X1** | index-side removal | drop all 14 chain profiles above the bridge gold | 3 / 22.028031 | 1 / 30.380258 | **yes** |
| **X2** | index-side removal | drop only the 6 pooling-introduced ones | 10 / 21.698162 | 7 / 28.004571 | **no** |
| **X3** | index-side removal | drop only the 1 pooling-introduced one above the answer gold | 15 / 21.524871 | 7 / 27.353053 | **no** |
| **X4** | index-side removal | drop only the 8 containing the literal `quick service` | 8 / 21.773995 | 2 / 29.310706 | **no** |
| **X5** | index-side removal | drop only the item's own 8 | 8 / 21.773995 | 2 / 29.310706 | **no** |
| **X6.1** | index-side removal | drop the top 1 non-gold | 15 / 21.524265 | 7 / 27.465657 | **no** |
| **X6.2** | index-side removal | drop the top 2 | 14 / 21.557167 | 6 / 27.720597 | **no** |
| **X6.3** | index-side removal | drop the top 3 | 13 / 21.591201 | 5 / 27.859579 | **no** |
| **X6.4** | index-side removal | drop the top 4 | 12 / 21.626256 | 4 / 28.068777 | **no** |
| **X6.5** | index-side removal | drop the top 5 | 11 / 21.662030 | 3 / 28.294967 | **no** |
| **X6.6** | index-side removal | drop the top 6 | 10 / 21.698431 | 2 / 28.541581 | **no** |

  X4 and X5 coincide because the eight passages containing the literal `quick service` are
  exactly this item's own eight annotated distractors. The ladder is monotone and shallow for
  the bridge hop: six removals move it only from 16 to 10, so no removal short of emptying
  the family recovers it.
- **Oracle conditions succeed, and the D-024 precondition holds.** `Tim Hortons` appears in
  the passage it names with `tim` at term frequency 2 and `hortons` at term frequency 2, and
  in the other gold with `tim` at 2 and `hortons` at 1, so the injected anchor is matchable
  by the passage it is meant to reach. Appending `Tim Hortons` gives 2 / 41.634087 and
  1 / 47.659615, appending both titles gives 1 / 53.480099 and 2 / 47.659615, naming the
  entity in place gives 2 / 41.634087 and 1 / 47.659615, replacing the whole description with
  the name gives 4 / 9.043185 and 1 / 14.681712, and the same append under an index-side
  normalized index gives 2 / 49.694769 and 1 / 52.705685. Appending the query's own `Ron
  Joyce` is degenerate at 2 / 33.338362 and 9 / 27.226538, and injecting the answer string
  `4,613` verbatim gives 16 / 21.492350 and 1 / 37.075410. The single-factor oracle-name test
  D-020 introduced therefore passes in five forms, its fourth pass after D-017, D-023 and
  D-026 and its first on a BM25 unit, and it still does not win the primary.
- **Corpus provenance, with the two paths separated for the first time.** Pooled gives
  `any@5` 0 and `full@5` 0; per-question gives `any@5` 1 and `full@5` 0, with the golds at 3
  and 7 of 10, so this is the sixth unit in which the corpus setting changes a metric and
  again only `any@5`. The per-question rebuild reproduces the official window title by title.
  Restricting the pooled scores to those same ten paragraphs puts the golds at 10 and 7 of
  10, so with the document set held fixed and only the collection statistics changed the
  bridge hop moves from 3 to 10. That isolates the idf-scale path D-024 identified, which
  D-024 could not separate from the document set, and it establishes the converse of the
  D-025 Dense property: a BM25 per-question ranking is **not** the restriction of the pooled
  ranking. In the per-question index avgdl is 62.400000 against 90.884950, `quick`,
  `service`, `restaurant` and `chain` all fall to an idf of 0.410358, `restaurants` falls
  from 5.480131 to 0.762140, `joyce` falls from 8.098947 to 1.845827, and `how`, `many`,
  `comprise`, `ron` and `helped` are absent from the vocabulary entirely, so the facet to
  name idf ratio moves from 25.249066 against 13.796955 to 2.403572 against 1.845827. The
  new-competitor path is present but secondary: only 6 of the 14 passages above the bridge
  gold and only 1 of the 7 above the answer gold are pooling-introduced, and removing exactly
  those recovers neither. The answer hop is 7 of 10 in the per-question index, in the
  restricted pooled ordering and among the pooled passages above it, so its failure is
  independent of corpus setting. Eight of this item's own ten paragraphs are themselves
  restaurant-chain profiles, so the annotator-constructed path D-027 identified is present
  too, and this is the first unit in which all three recorded paths appear together. Corpus
  setting remains provenance under D-003.
- **Comparison-retriever evidence and its boundary:** complete-corpus pooled Dense, rebuilt
  from the manifest-guarded cached document matrix, places `Ron Joyce` at 2 / 0.467637 and
  `Tim Hortons` at 8 / 0.384094, matching the stored window exactly, so Dense gives `any@5` 1
  and `full@5` 0 and also fails. This establishes only that the bridge passage is reachable
  when the name is not subject to whitespace tokenization. It is not a BM25 cause and the two
  backends' score magnitudes are not comparable. Eight of Dense's own top ten are the same
  restaurant-chain family, recorded as an observation only. There is no Dense analytical unit
  for this `example_id`, so no attribution is carried across.
- **Why `cutoff_sensitive_near_miss` is not adopted:** at 12.518 percent below the rank-5
  score the answer hop falls in a band this project had never measured, between the largest
  acceptance at 4.503 percent in D-025 and the smallest previous exclusion at 19.351 percent
  in D-027, so this exclusion narrows the untested band to 4.503 to 12.518 percent. The
  bridge hop at 30.942 percent falls squarely inside the excluded band, so the D-025 boundary
  applies again and no movement of the near gold alone can change `full@5`. Unlike D-027 there
  is no score cliff to appeal to, the successive differences from rank 4 to rank 9 being
  0.597253, 1.720835, 0.694195, 1.480808 and 1.252255. The counter-evidence is recorded
  rather than suppressed: dropping only the top three competitors lifts the answer hop to
  5 / 27.859579, so the metric is again sensitive to a small index-side change. Giving `far
  below the cutoff` a numerical threshold would edit the registry entry and stays deferred.
- **Tie-break:** prefer `minimal_preprocessing_score_distortion` over
  `description_only_bridge_entity`. Step one, `generic_term_lexical_crowding` meets its
  inclusion rule on read text but is demoted by its own exclusion clause and by the two-way
  pit 19f and 19i measurement, so the family is the product of the question's own descriptive
  referent rather than an independent contributing condition. Step two,
  `description_only_bridge_entity` is the closest competitor and its inclusion rule is met,
  since the required chain is never named, and it loses on two measured grounds: its entire
  support is oracle, which pit 15 restricts to diagnosis, and it is directly contradicted by
  a non-oracle condition, index-side punctuation normalization moving the un-named hop from
  8 / 27.226538 to 3 / 32.295791, so the descriptive referent is sufficient once one
  tokenizer artifact is repaired and the absent name anchor is not the binding constraint.
  This is the second application of the D-021 precedent that the inclusion rule can be met
  while the descriptor loses the tie-break, and the first in which the losing argument is a
  non-oracle recovery of the un-named hop itself. Step three,
  `cross_passage_conjunction_unresolved` is not adopted although all three of its positive
  legs hold, because the PT condition supplies no intermediate fact and performs no
  cross-passage reasoning yet places both required passages inside the cutoff, which could
  not happen if the inability to carry that fact were the binding constraint; as in D-026 one
  anchor also reaches both required passages. Step four,
  `minimal_preprocessing_score_distortion` wins because it is the only candidate with a
  non-oracle counterfactual that recovers both hops and because both blocked tokens are
  attributed exactly against a null control. Failure layer: implementation. Not method, since
  the descriptive referent and the name anchor are each individually sufficient to reach
  their own passage once the tokenizer and the indexed field change; not corpus setting,
  since the answer hop is 7 of 10 in all three orderings and no removal probe recovers the
  bridge hop; not evaluation, since neither hop has a substitute and no passage supplies a
  complete non-gold answer.
- **Excluded descriptors:** `cross_passage_conjunction_unresolved`, on the PT argument
  above. `cutoff_sensitive_near_miss`, on the score gap. `gold_chain_substitutability`,
  `gold_chain_not_unique` and `plausible_non_gold_answer`, on the substring scan and on the
  eight competitor counts all belonging to other chains.
  `generic_query_scaffold_score_inflation`, by its own exclusion clause naming the case where
  content-bearing category terms rather than query scaffold explain the competition: the
  scaffold set is only `how`, `that`, `the`, it accounts for 8 to 22 percent of competitor
  scores, the query has no repeated token, and S alone moves each gold by one rank.
  `repeated_content_word_amplification` and `repeated_function_word_amplification`, because
  the query contains no repeated token under the implemented tokenizer; the conceptual
  repetition of the category noun becomes a repeated token only under the M condition, which
  is negative. `same_topic_passage_distractor`, because the shared material is the question's
  broad category vocabulary and `generic_term_lexical_crowding` is the more specific fit; the
  overlap between the two names is registered for the audit.
  `entity_alias_reference_mismatch`, because the query's `Ron Joyce` and the body's `"Ron"
  Joyce` are the same appellation and the mismatch is punctuation, which G1 isolates, while
  the full-name variant `Ronald Joyce` also reaches rank 1. `bridge_relation_underweighted`,
  the provisional secondary, is deleted rather than registered: the name implies a weighting
  mechanism, and both relation tokens are measured completely inert, so the real fact is that
  `found?` is out of vocabulary and `helped` is absent from the gold, which
  `surface_form_tokenization_mismatch` already covers with G3 quantifying it. This is the
  reason D-025 used for `generic_context_substitution`, D-026 for `adjacent_event_crowding`
  and D-027 for `related_document_crowding`. `peripheral_passage_content_dilution` is not
  applicable, see the not-run list.
- **Speculation boundary:** do not claim that the P and T configuration would improve the
  run's overall metrics; only this one query was measured. Do not read any G condition or any
  removal probe as a deployable repair. Do not claim that the eight inert query tokens
  dilute the effective signal, since passage length enters BM25 only through the dl and avgdl
  normalization that the decomposition already accounts for. Do not generalize the
  annotator-constructed share of the competitor family from n equals 1, nor the finding that
  title indexing helps, which is n equals 1 against seven prior units where it was inert or
  negative. Do not use the Dense ranks as a BM25 cause or compare the two backends' score
  magnitudes.
- **Not run and why:** the remaining sixteen cells of a full P x E x S x T x M design,
  because E is measured inert so every cell containing it is a translation of its
  counterpart, and because M is negative on both hops in all four forms run and never brings
  the bridge hop above 9. Document-side scaffold removal and a query-side T, because S is a
  query-side factor and T an index-side one in this implementation. A content ablation with
  length-matched controls for `peripheral_passage_content_dilution`, because under BM25
  passage length enters only through the dl and avgdl normalization, which the exact
  per-token decomposition already accounts for at dl 27 and dl 55, so the probe could add no
  attribution the decomposition does not already give; this is a boundary statement and not a
  rejection of that descriptor. A P or T factorial on the per-question index, because corpus
  setting is provenance under pit 17 and the two reconstructions run are what separate the
  two paths. Reranker conditions, because the main run has none.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. The primary inventory is unchanged at
  25 distinct names; `minimal_preprocessing_score_distortion` is item 9 and reaches its sixth
  unit, after D-012, D-014, D-016, D-019 and D-021. The departing name
  `generic_term_lexical_crowding` keeps no current v2 primary row, the treatment D-021,
  D-022, D-023 and D-027 gave their departing names. The secondary-name union grows from 49
  to 50 with `unindexed_title_name_anchor`, and the registry grows from 25 to 26 adopted
  descriptors. That entry is new because index-field selection is mechanically distinct from
  text normalization and is co-necessary here, and because this is the first unit in which
  indexing the title is materially positive against seven prior units where it was inert or
  negative; whether it should instead be folded into the primary is a vocabulary-audit
  question, and folding it in would widen a primary already flagged as possibly too broad,
  now on its fifth distinct sub-mechanism. Both readings of the new name were tested as pit
  19e requires, the indexing reading through T at 2 / 32.480848 and the semantic reading
  through a reduced query containing only that title at 1 / 11.846012. Three existing entries
  gain this affected unit and D-028 as a decision source,
  `surface_form_tokenization_mismatch`, `generic_term_lexical_crowding` and
  `description_only_bridge_entity`, and `cutoff_sensitive_near_miss` and
  `cross_passage_conjunction_unresolved` gain D-028 as a decision source recording a
  non-adoption rather than an affected unit. No definition, inclusion rule or exclusion rule
  is changed.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5a79b7f6554299029c4b5f6f.md`.

## D-029 - Reclassify the Matilda Lutz / Rings Dense unit as question-frame semantic crowding

- **Date:** 2026-08-04
- **Status:** active
- **Decision:** For `5a81ebee554299676cceb16d|dense`, replace the provisional primary
  `cross_entity_relation_unresolved` with `question_frame_semantic_crowding`, which is the
  first use of that name as a primary. Adopt `peripheral_passage_content_dilution`,
  `description_only_bridge_entity` and `generic_person_semantic_neighborhood` as
  secondaries. Delete the unregistered `cross_entity_relation_unresolved`,
  `surname_entity_confusion` and `broad_film_person_neighborhood`. Use
  `description_only_bridge_entity` as the closest competitor. Do not adopt
  `cutoff_sensitive_near_miss`.
- **Affected unit:** `5a81ebee554299676cceb16d|dense`.
- **Question:** `What kind of movie directed by F. Javier gutierrez did an Italian model and
  actress star in?` This is a bridge unit. `Matilda Lutz` states that she is an Italian model
  and actress who starred in the 2017 horror film `Rings`, and `Rings (2017 film)` states that
  it is a 2017 American supernatural psychological horror film directed by F. Javier Gutiérrez
  and starring Matilda Lutz. The question names exactly one entity, the director, and that
  entity has no passage of its own anywhere in the corpus; the subjects of both required
  passages are referred to only by description.
- **Verified implementation:** symmetric bi-encoder `all-MiniLM-L6-v2`, one shared instance
  for queries and passages, no prefix, only paragraph text encoded and the title excluded,
  explicit row-wise L2 normalization so the dot product equals cosine, attention-mask-aware
  mean pooling, a 256-token limit, no reranker and no cross-passage reasoning, stable
  descending sort with exact ties keeping corpus order. The tokenizer lower-cases and strips
  accents, so `F. Javier gutierrez` and `F. Javier Gutiérrez` both tokenize to `f`, `.`,
  `javier`, `gutierrez`. Both required passages are inside the sequence limit at 30 and 86
  tokens. Reference: `references/dense_implementation_reference.md`.
- **Exact reconstruction:** rebuilding the same 4,937 deduplicated pooled passages from the
  manifest-guarded document matrix reproduces all 50 stored top-50 titles in order with a
  maximum absolute score error of 3.278e-07, so strong causal claims are supported.
  Complete-corpus ranks are 43 / 0.365309 for `Matilda Lutz` and 94 / 0.332391 for
  `Rings (2017 film)`, so the stored `not_in_top50` means rank 94 rather than absence. The
  rank-5 score is 0.460548, so the two required passages sit 0.095238 and 0.128157 points, or
  20.679 and 27.827 percent, below the cutoff. There is no score cliff: the successive
  differences from rank 1 to rank 10 are 0.002518, 0.010296, 0.034229, 0.007743, 0.004229,
  0.006203, 0.004349, 0.001895 and 0.003646.
- **Diagnostic scale:** 132 conditions on the same unchanged candidate set, twelve of them
  deliberate duplicates that reproduced bit for bit, making this the largest single-unit
  diagnostic in the project so far. They are all eight cells of an A x B x C query-wording
  factorial, the indexing condition T and three T crossings, eight further wording
  conditions, eight name-free ceiling rewrites, ten single-clause and single-token deletions
  from the full question, ten per-side reachability probes, eight frame-only reduced-query
  probes, one query-splitting probe completing three split pairs, eighteen name-position
  probes, twenty-two index-side removal probes including two cumulative dose-response
  ladders, twenty-three gold-targeted content conditions including a null control and
  length-matched controls on both required passages, ten oracle conditions, one per-question
  reconstruction and the baseline.
- **The question's only named entity is not a usable anchor for this encoder.** The corpus
  contains `gutiérrez` in exactly one passage, the answer gold, and `gutierrez` in exactly one
  other, `Janine Gutierrez`. Reducing the query to `F. Javier Gutiérrez` ranks the answer gold
  2202 / 0.057835 and the bridge gold 1937 / 0.070732; the bare surname gives 4243 / -0.047993.
  This is not a query-length effect: the four-word descriptive query `Italian model and
  actress` ranks the bridge gold 14 / 0.459121. It is not a spelling effect either, since the
  accented and unaccented forms tokenize identically and score identically. Five further names
  taken from the same answer passage behave the same way, `David Loucka` 1523, `Alex Roe` 2515,
  `Vincent D'Onofrio` 1469, `Johnny Galecki` 533 and `Aimee Teegarden` 2914, while the two
  names that stand in subject position at the start of their own passage are perfectly
  reachable, the bare `Matilda Lutz` ranking its passage 1 / 0.633059 and the bare `Rings`
  ranking its passage 1 / 0.560012. Reducing the answer passage to a fourteen-word sentence
  ending in the director's name lifts that same bare-name query from 2202 to 120 / 0.263144,
  and reducing it to its non-relevant content pushes it to 3911, so the name's unreachability
  is bound up with what else the passage says.
- **The competing family, verified in both directions as pit 19i requires.** Every one of the
  42 passages above the bridge gold and every one of the 51 further passages between it and the
  answer gold was read in full. Above the bridge gold, 36 carry a film or directing cue, 19 a
  person-role cue, 16 both, 12 the word `italian` and exactly 1 the surname; above the answer
  gold the same counts are 77, 48, 41, 20 and 1. Not one contains `Matilda Lutz` or `Rings`,
  and not one states the genre of any film by the queried director. Forward, the referent cue
  alone does not build this family: `F. Javier Gutiérrez` puts only 4 of 10 of its top ten
  inside the baseline top-42 and 2 of 10 inside the baseline top ten, its own top five being
  racing drivers and footballers with similar name forms, and the bare surname gives 3 of 10.
  In reverse the family survives deletion of either cue: deleting the whole director name
  leaves 8 of 10 inside the baseline top-42, and deleting the descriptive referent instead
  leaves 8 of 10 inside the top-42 and 6 of 10 inside the top ten. The family is therefore the
  product of the question's framing facets and not of either referent, which is what the
  descriptor's third exclusion clause tests for.
- **Index-side removal probes, with a control on the complement:**

| Condition | Kind | Exact change | `Matilda Lutz` rank/score | `Rings (2017 film)` rank/score | Both top-5 |
|---|---|---|---:|---:|---|
| **baseline** | baseline | unchanged query and index | 43 / 0.365309 | 94 / 0.332391 | **no** |
| **X1** | index-side removal | drop the one surname-sharing passage | 42 / 0.365309 | 93 / 0.332391 | **no** |
| **X2** | index-side removal | drop every non-gold passage containing the surname | 42 / 0.365309 | 93 / 0.332391 | **no** |
| **X5** | index-side removal | drop the Italian model or actress passages above the bridge gold | 42 / 0.365309 | 93 / 0.332391 | **no** |
| **X6** | index-side removal | drop the 36 film-family passages above the bridge gold | 7 / 0.365309 | 58 / 0.332391 | **no** |
| **X8** | index-side removal | drop all 84 framing-family passages above the answer gold | 4 / 0.365309 | 10 / 0.332391 | **no** |
| **X9** | index-side removal, control | drop only the 8 non-framing passages above the answer gold | 40 / 0.365309 | 86 / 0.332391 | **no** |
| **X10** | index-side removal | drop all 89 pooling-introduced passages above the answer gold | 3 / 0.365309 | 5 / 0.332391 | **yes** |
| **PQ** | corpus setting | restrict the candidate set to the item's own ten passages | 3 / 0.365309 | 5 / 0.332391 | **yes** |

  Dropping the framing family moves the pair from 43 and 94 to 4 and 10 while dropping its
  complement moves it only to 40 and 86, so the attribution has a control and is not a
  one-sided assertion. The two cumulative ladders are monotone and shallow: removing the top
  5, 10, 15, 20, 30 and 42 non-gold passages moves the bridge gold to 38, 33, 28, 23, 13 and
  1 while the answer gold only reaches 52, and removing the top 50, 60, 70, 80, 85, 89 and 93
  moves the answer gold to 45, 35, 25, 15, 10, 6 and 2. Ninety-three removals are needed
  before both are inside the cutoff.
- **No query rewrite and no gold-passage repair recovers both hops; only removing competitors
  does.** The non-oracle query ceiling is 12 / 0.418804 and 28 / 0.390005, reached by dropping
  the surname and asking for a genre; the next best is 7 / 0.426707 and 37 / 0.373016 from
  dropping the surname alone. The gold-targeted repair ceiling is 18 / 0.412468 and
  16 / 0.420530 with both passages ablated at once. Combining the two ceilings still gives only
  4 / 0.462879 and 9 / 0.438683. Against that, restricting the candidate set to this item's own
  ten passages gives 3 and 5 immediately.
- **Single-factor effects are strongly antagonistic across the two hops.** Eight of the
  thirteen single factors carry opposite signs: deleting the director clause gives
  5 / 0.466126 and 261 / 0.277560, deleting the descriptive referent gives 351 / 0.238875 and
  47 / 0.343038, deleting `Italian` gives 60 / 0.328700 and 40 / 0.346540, deleting `model and`
  gives 45 / 0.375880 and 86 / 0.341370, deleting the answer-type frame gives 29 / 0.396772
  and 160 / 0.313877, deleting the forename initials gives 38 / 0.389649 and 266 / 0.278954,
  deleting the whole director name gives 7 / 0.463058 and 174 / 0.313724, and the genre
  wording gives 51 / 0.358808 and 68 / 0.348342. The only factor that improves both is
  deleting the surname alone at 7 / 0.426707 and 37 / 0.373016. Compare 6 of 18 in D-028, 21
  of 50 in D-027, 4 of 19 in D-026, 10 of 20 in D-025 and 10 of 19 in D-024. The A x B x C
  factorial has no interaction at all: capitalizing the surname and restoring its accent are
  exactly inert in all eight cells, as the tokenizer contract predicts, so the eight cells
  collapse to two distinct results.
- **The indexing condition is negative for the eighth consecutive unit.** T alone gives
  79 / 0.333927 and 155 / 0.294327, and crossing it with the genre wording, with the
  director-clause deletion and with the surname deletion gives 89 / 0.328441 and 130 / 0.310213,
  5 / 0.445752 and 338 / 0.243080, and 11 / 0.404894 and 85 / 0.333700. The D-028 exception
  does not transfer, because neither gold's title is the query's name anchor here.
- **The content-dilution gate passes on both required passages, the fourth application and
  third pass.** The null control rebuilding both gold rows from their own text reproduces the
  baseline bit for bit at 43 / 0.365309 and 94 / 0.332391. On the answer gold, the ablation to
  its single query-relevant sentence gives 37 / 0.373376 at 57 words, a further truncation to
  director, genre and writers gives 31 / 0.379862 at 24 words and to director and genre alone
  gives 16 / 0.420530 at 14 words, while the three length-matched name-preserving controls
  built from its non-relevant sentences give 171 / 0.298173 at 10 words, 342 / 0.246695 at 16
  words and 405 / 0.233411 at 23 words. This is the first unit in which the controls do not
  merely fail to improve the rank but move it 150 to 390 positions the wrong way, so the third
  inclusion condition holds in its strongest form. Dropping only the starring list and keeping
  the rest gives 187 / 0.292076, so the recovered material is the director and genre clause and
  not the cast. On the bridge gold, removing its only non-query-relevant material, a four-word
  birth parenthetical, gives 17 / 0.412468, while removing four query-relevant words instead
  gives 37 / 0.374462, removing two name-internal words gives 115 / 0.321464, and a
  fourteen-word control that keeps the birth date and drops the role clause gives
  58 / 0.353484. One boundary is registered rather than closed: that passage's non-relevant
  material is a parenthetical and not a sentence, so the control the inclusion rule literally
  describes, retaining only the non-query-relevant sentences, cannot be constructed there, and
  the gate is recorded as passing in its nearest constructible form on that side. As in D-023,
  D-026 and D-027, passing the gate does not win the primary: ablating both passages at once
  still leaves 18 and 16.
- **Oracle conditions succeed and the D-024 precondition holds in the D-026 strong form.**
  Appending `Rings (2017 film)` gives 2 / 0.561980 and 1 / 0.668976, appending both titles
  gives 1 / 0.754741 and 2 / 0.636003, appending the bare `Rings` gives 2 / 0.522003 and
  1 / 0.595248, naming the film in place gives 2 / 0.481639 and 1 / 0.753787, and naming the
  actress in place gives 1 / 0.603500 and 4 / 0.428868, so the single-factor oracle-name test
  D-020 introduced passes in five forms. Two forms fail: appending the actress name alone gives
  1 / 0.607632 and 19 / 0.397304 and replacing the whole description with her name gives
  1 / 0.668300 and 11 / 0.368824. The precondition was checked before the verdict was read: the
  bare `Matilda Lutz` ranks its own passage 1 / 0.633059, the bare `Rings (2017 film)` ranks
  its own passage 1 / 0.791355 and also lifts the other required passage to 2, and the bare
  `Rings` gives 1 / 0.560012 with the other at 2, so each injected anchor is matchable by the
  passage it names.
- **No substitute, no complete non-gold answer, and one required passage answers the question
  alone.** A full-corpus substring scan finds `matilda lutz` in exactly 1 passage, the answer
  gold, `film "rings` in exactly 1, the bridge gold, `supernatural psychological`,
  `psychological horror` and `javier gutiérrez` in exactly 1 each, the answer gold, and
  `italian model and actress` in exactly 3, the bridge gold plus `Eleonora Pedron` and
  `Margareth Madè`, neither of which has any connection to the film. Neither hop has a
  substitute. The answer gold does, however, state the director, the genre and the starring
  actress in one passage, so it supplies the answer on its own and the bridge hop is a
  redundant constraint for answering, which is what fires the exclusion of
  `cross_passage_conjunction_unresolved`.
- **Corpus provenance.** Pooled gives `any@5` 0 and `full@5` 0 while per-question gives
  `any@5` 1 and `full@5` 1, with the two golds at 3 and 5 of 10. This is the seventh unit in
  which the corpus setting changes a metric, the second in which `full@5` also flips after
  D-026, and the second in which the failure is confined entirely to the pooled setting. The
  per-question rebuild reproduces the official ten-title window in order, which verifies the
  D-025 Dense property for the fourth time: cosine carries no collection statistic, so the
  per-question ranking is the restriction of the pooled ranking, and the restricted rebuild and
  the official window are identical. The path is the new-competitor path of D-022, D-023, D-025
  and D-026: 40 of the 42 passages above the bridge gold and 89 of the 92 above the answer gold
  are pooling-introduced. The D-024 idf-scale path cannot exist on a bi-encoder, and the D-027
  annotator-constructed path is weak here, only 2 of this item's own 8 distractors ranking above
  the bridge gold. Corpus setting remains provenance under D-003 and pit 17 and is not the
  primary.
- **Comparison-retriever evidence and its boundary:** BM25 places `Rings (2017 film)` at 1 and
  `Matilda Lutz` at 17 pooled, and 1 and 9 per-question, so it gives `any@5` 1 and `full@5` 0
  in both settings. This establishes only that the answer passage is reachable by whitespace
  token overlap on the director's name. It is not a Dense cause, the two backends' score
  magnitudes are not comparable, and there is no BM25 analytical unit for this `example_id`, so
  no attribution is carried across.
- **Why `cutoff_sensitive_near_miss` is not adopted:** the two required passages sit 20.679 and
  27.827 percent below the rank-5 score, both inside the excluded band that now runs from
  12.518 percent in D-028 to 52.794 percent in D-025 and far outside the accepted band of 1.156
  to 4.503 percent. There is no score cliff to appeal to. Unlike D-027 and D-028 there is no
  counter-evidence either: removing the top three or top five competitors leaves the nearer
  gold at 40 and 38, and 93 removals are required before both enter the cutoff. The
  no-substitute condition is met, so the exclusion rests on the score gap and on the absence of
  any small index-side change that helps.
- **Tie-break:** prefer `question_frame_semantic_crowding` over
  `description_only_bridge_entity`. Step one, the provisional primary
  `cross_entity_relation_unresolved` is deleted rather than registered, for the reason D-025
  used for `generic_context_substitution`, D-026 for `adjacent_event_crowding`, D-027 for
  `related_document_crowding` and D-028 for `bridge_relation_underweighted`: the name asserts a
  failure to bind a director-film-actress relation, but the passage that states that relation
  verbatim is the one at 94, and the measured constraints are that the query's only name is
  unreachable and that the competing family is built by the question's framing, neither of
  which is a relation-binding claim. Step two, `description_only_bridge_entity` is the closest
  competitor and its inclusion rule is met, since neither required subject is named, and its
  oracle-name test passes in five forms with the D-024 precondition holding in the D-026 strong
  form. It loses on three measured grounds. Its entire support is oracle, which pit 15 restricts
  to diagnosis. A non-oracle condition contradicts it on the bridge side, where deleting the
  director clause alone puts the un-named bridge passage at 5 / 0.466126, inside the cutoff, so
  the descriptive referent is not a weak anchor there; this is the same falsification route
  D-028 used, and its second application. And on the answer side the phrase `no unique name
  anchor` misdescribes what was measured, since the query does carry a name for that passage
  and that passage does contain it, uniquely in the corpus, yet a query consisting of exactly
  that name ranks it 2202 of 4937. Step three, `cross_passage_conjunction_unresolved` is not
  adopted, because its first exclusion fires directly, the answer gold supplying the complete
  answer on its own, and because under pit 19s the removal probes supply no intermediate fact
  and perform no cross-passage reasoning yet place both required passages inside the cutoff.
  Step four, `question_frame_semantic_crowding` wins because it is the only candidate whose
  support is entirely non-oracle and complete: its inclusion rule is met on 42 and 92 read
  passages, its exclusion is tested and does not fire, the two-way pit 19i measurement assigns
  the family to the question's framing rather than to either referent, and a family-scoped
  removal probe with a control on the complement is the only intervention of any kind that
  moves both hops together, while every query rewrite and every gold-passage repair fails.
  This is the same footing on which D-018 adopted `compound_two_sided_crowding` and D-027
  adopted `one_sided_entity_crowding`: the name states which documents compete and why, not the
  rank itself, so pit 17 is not violated. Failure layer: method. Not implementation, since no
  tokenizer or indexing artifact exists on a bi-encoder that strips accents and case and since
  T is negative; not corpus setting, which is provenance, although this unit's failure is
  confined to it; not evaluation, since neither hop has a substitute and no passage supplies a
  complete non-gold answer.
- **Excluded descriptors:** `cross_passage_conjunction_unresolved`, on the two grounds above.
  `cutoff_sensitive_near_miss`, on the score gap. `gold_chain_substitutability`,
  `gold_chain_not_unique` and `plausible_non_gold_answer`, on the substring scan.
  `proper_name_homonym_collision` and `related_name_document_crowding`, which the provisional
  `surname_entity_confusion` would have mapped to: exactly one non-gold passage in the corpus
  shares the surname, and dropping it, or dropping every non-gold passage containing the
  surname, moves each required passage by one position, to 42 and 93, so the requirement that
  the competition materially affect the named candidate fails and the provisional name is
  deleted rather than registered. `compound_two_sided_crowding`, because one family suppresses
  both hops, which is the pit 19h test. `one_sided_entity_crowding`, because the competition is
  not organized around one named candidate. `surface_form_tokenization_mismatch`, because the
  query's lower-case unaccented spelling is measured to be a bit-identical no-op under this
  tokenizer. `low_context_name_query`, because the question is description-dominated rather
  than name-dominated. `exact_string_source_dependency`, because there is no quoted verbatim
  string. `possible_type_mismatch`, because the requested category and the passage's own wording
  align, the four-word query `supernatural psychological horror film` ranking the answer gold
  12 / 0.414189. `broad_film_person_neighborhood`, the second provisional secondary, is deleted
  rather than registered because `question_frame_semantic_crowding` and
  `generic_person_semantic_neighborhood` already cover both halves of what it names, which is
  the no-duplicate-entry rule applied for the fifth consecutive decision.
- **Speculation boundary:** do not claim that the encoder ignored, down-weighted or averaged
  away the director's name; no attribution experiment was run and pit 18 stands. What is
  licensed is the passage-level measurement that a query consisting of that name ranks the only
  passage containing it 2202 of 4937. Do not generalize the name-position finding into a
  property of the model: six mid-passage names from one passage and two subject-position
  controls were measured, which is n equals 1 at the passage level. Do not read any gold-targeted
  ablation or any removal probe as a deployable repair; both require knowing which passage is
  required. Do not read the oracle conditions as a fix. Do not use the BM25 ranks as a Dense
  cause or compare the two backends' score magnitudes. Do not claim that the pooled setting is
  the mechanism, notwithstanding that the failure is confined to it.
- **Not run and why:** the remaining cells of a full A x B x C x T design, because A and B are
  verified bit-identical no-ops under this tokenizer so every cell containing them is a copy of
  its counterpart, and because T is negative on both hops alone and in all three crossings run.
  Length-matched controls at 40 and 57 words on the answer gold, because its non-query-relevant
  material totals only 23 words and a longer control would have to add text that is not a
  verbatim subset of the passage. A control retaining only non-query-relevant sentences on the
  bridge gold, because that passage has no such sentence; the nearest constructible controls
  were run instead and the boundary is recorded above. Per-token decomposition, which
  `case_probe.py` refuses on this backend and which cannot be derived from a ranking. Reranker
  conditions, because the main run has none. A BM25 factorial for this `example_id`, because
  there is no BM25 analytical unit for it and the comparison panel is evidence of reachability
  only.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. The primary inventory grows from 25 to
  **26 distinct names** with `question_frame_semantic_crowding`. This is the first time the
  inventory grows through a promotion rather than a new coinage: the name is not new, it is an
  already registered secondary that four other names in the inventory,
  `cross_passage_conjunction_unresolved`, `description_only_bridge_entity`,
  `generic_term_lexical_crowding` and `proper_name_homonym_collision`, already share the
  property of appearing in both inventories, but all four arrived there from the first pass
  rather than by promotion. The departing name `cross_entity_relation_unresolved` is item 3
  and keeps no current v2 primary row, the treatment D-021, D-022, D-023, D-027 and D-028 gave
  their departing names; it stays in the inventory union as a first-pass name in
  `case_memos_v1.csv` and remains a first-pass secondary on
  `5abcc96c5542996583600492|bm25`, queue item 20, which is still `not_started`. The
  secondary-name union is unchanged at **50 distinct names**: `broad_film_person_neighborhood`,
  item 7, and `surname_entity_confusion`, item 43, remain in the union as historical first-pass
  names, the treatment given to `generic_context_substitution`, `adjacent_event_crowding` and
  `related_document_crowding`. `case_memos_v2.csv` now holds **79 secondary assignments over
  37 distinct names**, up from 78 and down from 39: this row went from two descriptors to
  three, all three of which already occur elsewhere in the column, while both removed names
  were unique to this row. The distinct `primary_open_code` count in v2 is unchanged at 16,
  because `cross_entity_relation_unresolved` was unique to this row as a primary and
  `question_frame_semantic_crowding` was not previously present as one. `case_memos_v1.csv` is
  unchanged. The registry stays at **26 adopted descriptors** because no new descriptor is
  registered. Four existing entries gain this affected unit and D-029 as a decision source,
  `question_frame_semantic_crowding` with a note on primary use,
  `peripheral_passage_content_dilution`, `description_only_bridge_entity` and
  `generic_person_semantic_neighborhood`, and `cutoff_sensitive_near_miss`,
  `cross_passage_conjunction_unresolved` and `related_name_document_crowding` gain D-029 as a
  decision source recording a non-adoption rather than an affected unit. No definition,
  inclusion rule or exclusion rule is changed.
  Three vocabulary-audit items are registered rather than settled: whether
  `question_frame_semantic_crowding` needs a primary-use contract of its own now that it has one;
  whether `generic_person_semantic_neighborhood` may be used as a scoped subset of a
  framing-crowding primary, which is the nesting D-023 left open in the opposite direction; and
  whether the dilution gate's third inclusion condition should be reworded to cover passages
  whose non-relevant material is not a whole sentence.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5a81ebee554299676cceb16d.md`.
## D-030 - Reclassify the Suicide / Ghost Rider BM25 unit as minimal-preprocessing score distortion

- **Date:** 2026-08-04
- **Status:** active
- **Decision:** For `5a83880e554299123d8c214e|bm25`, replace the provisional primary
  `query_facet_fragmentation` with `minimal_preprocessing_score_distortion`. Adopt
  `surface_form_tokenization_mismatch` and `generic_term_lexical_crowding` as secondaries.
  Delete the unregistered provisional secondary `both_gold_chain_passages_missing`. Use
  `generic_term_lexical_crowding` as the closest competitor. Do not register
  `query_facet_fragmentation`. Do not adopt `cutoff_sensitive_near_miss`,
  `generic_query_scaffold_score_inflation`, `description_only_bridge_entity`,
  `unindexed_title_name_anchor` or `cross_passage_conjunction_unresolved`.
- **Affected unit:** `5a83880e554299123d8c214e|bm25`.
- **Question:** `Suicide's 1977 released album features a song based on what brand's comic
  character?` This is a bridge unit. `Suicide (1977 album)` states that Suicide is the debut
  album of the American rock band Suicide, released in 1977 on Red Star Records, and
  `Ghost Rider (Suicide song)` states that Ghost Rider is a song by the protopunk band Suicide
  appearing on their debut album and that the song is based on the Marvel Comics character.
  The question names exactly one entity, the band, and it names it in the possessive form.
- **Verified implementation:** only paragraph text is indexed and the title is excluded;
  documents and queries are both tokenized by `text.lower().split()`, with no punctuation
  handling, no stop-word removal, no stemming, no Unicode normalization, no phrase matching and
  no entity-boundary preservation; `rank-bm25==0.2.2` `BM25Okapi` with `k1=1.5`, `b=0.75` and
  `epsilon=0.25` accumulates a contribution for every query-token occurrence. Under that
  tokenizer `suicide's`, `suicide` and `suicide.` are three distinct tokens and `character?`
  and `character.` are two. Reference: `references/bm25_implementation_reference.md`.
- **Exact reconstruction:** rebuilding the first-occurrence, title-deduplicated 4,937-passage
  pooled index reproduces all 50 stored top-50 titles in order with a maximum absolute score
  error of 0.000000, and every per-token decomposition reconciles against `get_scores` within
  3.553e-15, so strong causal claims are supported. Complete-corpus ranks are
  66 / 12.585642 for `Ghost Rider (Suicide song)` and 61 / 12.713062 for
  `Suicide (1977 album)`, so the stored `not_in_top50` means rank 66 and rank 61 of 4,937
  rather than corpus absence. The rank-5 score is 18.467254, so the two required passages sit
  5.881611 and 5.754192 points, or 31.849 and 31.159 percent, below the cutoff. There is no
  score cliff: the successive differences from rank 1 to rank 10 are 0.129332, 1.401531,
  0.613341, 0.984862, 1.684766, 0.497086, 0.275489, 0.046511 and 0.322020.
- **Diagnostic scale:** 147 distinct conditions on the same unchanged candidate set. They are
  all 64 cells of a P x E x G x M x S x T preprocessing and indexing factorial, where G is a
  possessive-clitic normalization this unit introduces; ten single-sided controls splitting P,
  G, M, PG and PGM into their query-side and document-side halves; three token-level
  decompositions of the query-side possessive factor; six case-specific query-side conditions;
  ten non-oracle query rewrites; sixteen reduced-query probes; thirteen single query-token
  deletions; eight oracle conditions; eight per-side reachability probes; seven gold-targeted
  index-side repairs including a null control; sixteen index-side removal probes including two
  complement controls and a seven-step cumulative dose-response ladder; five further
  normalization completeness cells including a general alphanumeric analyzer; and two
  corpus-setting reconstructions.
- **The question's only entity name contributes exactly 0.000000 to every passage.** The
  possessive token `suicide's` occurs in 0 of 4,937 passages, so it is absent from the corpus
  vocabulary and has no idf at all; the corpus form `suicide` occurs in 12 passages at an idf
  of 5.976452 and stands in the indexed body of both required passages, as `band Suicide
  appearing` and as `band Suicide.`. The question's final token `character?` is likewise absent
  from the vocabulary. Both facts are verified in their strongest available form rather than by
  inspection: deleting either token from the query reproduces the entire 4,937-passage ranking
  bit for bit, 0 order mismatches and a maximum absolute score difference of 0.000000. This is
  the fourth unit after D-019, D-021 and D-028 in which a query token contributes exactly
  0.000000 everywhere, and the first in which that token is the question's only entity name.
- **The same unnormalized clitic manufactures the query's rarest token on the false-positive
  side.** `brand's`, the head noun of the interrogative frame `what brand's comic character`,
  carries the highest idf in the query at 7.587919 only because the clitic makes it a separate
  token occurring in exactly 2 passages, `List of soft drinks by country` and
  `Deadwood (song)`, neither related to the question. It supplies 7.815653 points, or 36.190
  percent, of the rank-1 passage's 21.596320 through the phrase `Russell Brand's Got Issues`,
  and 0.000000 to both required passages; question-frame vocabulary supplies 11.493516, or
  53.220 percent, of that passage's score. The bare form `brand` occurs in 24 passages at an
  idf of 5.301069. One unnormalized surface form therefore produces a false negative on the
  only name and a false positive on the interrogative frame at the same time, which is the
  tightest instance of this primary's two-sided coverage the project has recorded.
- **What is left to match the required passages is generic music-catalogue vocabulary.** The
  answer hop's entire 12.585642 comes from `song` 5.561336, `based` 3.682955, `a` 2.866664 and
  `on` 0.474688 at a document length of 24. The bridge hop's entire 12.713062 comes from
  `1977` 5.827697, `album` 4.248330, `released` 2.346062 and `on` 0.290973 at a document length
  of 65. Neither matches any proper noun, and their matched token sets share only `on`. The
  query contains no repeated token, so repeated-occurrence amplification is inapplicable, as in
  D-021.
- **A single non-oracle change to that one token recovers both hops.** Rewriting only
  `suicide's` as `suicide` on the query side, changing nothing else, gives
  2 / 21.521304 and 5 / 19.568085. The increment is exactly attributable because the scorer is
  additive over query-token occurrences: the gains are 8.935662 and 6.855023, which are
  precisely the scores the two passages receive from a query consisting of the single token
  `suicide`, under which they rank 1 / 8.935662 and 3 / 6.855023 of 4,937. Normalizing both possessives blind gives
  1 / 21.521304 and 4 / 19.568085; normalizing only `brand's` leaves both hops at exactly
  66 / 12.585642 and 61 / 12.713062. The effect is entirely query-side, the document-side half
  alone giving 70 / 12.575389 and 66 / 12.648957, which is worse than the baseline. This is the
  mirror image of D-028, where the whole effect of P was document-side, so pit 19p must be read
  as a requirement to measure both sides rather than as an expectation about which side matters.
  The repair is not specific to this question: replacing the tokenizer with a general
  alphanumeric analyzer, `re.findall` over `[a-z0-9]+` applied blind to both sides with no
  possessive-specific rule, gives 1 / 29.700487 and 4 / 21.348446.
- **The one oracle condition that recovers both hops is degenerate.** Appending the gold-2
  title gives 2 / 21.521304 and 5 / 19.568085, which the standard battery reports as a pass of
  the single-factor oracle-name test D-020 introduced. Of the three appended tokens, `(1977` is
  absent from the corpus vocabulary and `album)` has a term frequency of 0 in both required
  passages, so appending the single token `Suicide` instead reproduces both gold scores to
  0.000000 and the non-oracle single-token repair reproduces them to 3.553e-15. The condition
  supplies nothing the question did not already contain in another surface form, and reading it
  as evidence of a missing name anchor would invert the mechanism. The other oracle forms behave
  normally and fail: appending `Ghost Rider` gives 1 / 33.845875 and 63 / 12.713062 and
  appending `Marvel Comics` gives 1 / 30.212444 and 70 / 12.713062, each recovering the answer
  hop only. This is the first unit in which that test can pass without supplying oracle
  information, and it is registered as a vocabulary-audit item beside the D-024 precondition.
- **No index-side removal recovers both hops, and that is a property of the unit.** Dropping
  every one of the 64 non-gold passages above the answer hop leaves 8 / 13.038940 and
  2 / 13.262049, because that hop's absolute score is low enough for seven further passages to
  rise past it. The 64 were read in full: 59 are song or album profiles matching the same broad
  category vocabulary, 5 carry a comic cue, `A Week of Garfield`, `Deceit (Doctor Who novel)`,
  `Nagaram (2010 film)`, `In My Country There Is Problem` and `Lev Yilmaz`, and 1 is neither,
  `Paddy O'Toole`; not one contains `suicide`, `ghost`, `rider` or `marvel`. Dropping the 59
  work profiles gives 14 / 13.022572 and 7 / 13.216898 while the complement control dropping
  only the other 5 gives 62 / 12.601801 and 54 / 12.754929; dropping the 5 comic-cue passages
  gives 61 / 12.609976 and 56 / 12.716510 while its complement gives 14 / 13.012495 and
  7 / 13.258067. The cumulative ladder is monotone and insufficient throughout, giving 65 and 59
  at three removals, 64 and 54 at five, 58 and 50 at ten, 48 and 43 at twenty, 30 and 23 at
  forty, 12 and 4 at sixty and 8 and 2 at sixty-five. Dropping the 2 passages containing
  `brand's` gives 65 / 12.592570 and 60 / 12.719437.
- **The crowding family is produced by the question's frame, not by its referent cue, and both
  directions were run.** Forward, the referent cue alone, `Suicide's 1977 released album`, puts
  2 of 10 of its top ten inside the baseline top ten and 4 of 10 inside the 64 above the answer
  hop. In reverse, keeping only the frame puts 4 of 10 and 8 of 10, `album features a song`
  puts 4 of 10 and 10 of 10, `released album features a song based on comic character` puts
  6 of 10 and 10 of 10, and deleting `suicide's` from the full question leaves the top ten
  10 of 10 identical. The third exclusion clause of `generic_term_lexical_crowding`, which
  assigns a family produced by the decisive referent cue to the primary mechanism, therefore
  does not fire here, unlike D-024 and D-028 where the forward direction carried it. The
  descriptor is demoted by its deferral clause and by the removal results instead.
- **Single-factor effects.** Sixteen of the 26 single-factor conditions move the two required
  passages in different or in no directions: ten carry opposite signs, four are inert and one is
  one-sided. `T` is inert-to-negative on its own at 78 / 12.352922 and 61 / 12.664186, the
  eighth measurement of that condition in this project after D-019, D-020, D-021, D-023, D-024,
  D-025 and D-026, and it turns positive only on top of the possessive normalization, moving
  1 and 5 to 4 and 1; both required titles carry the anchor but so do both indexed bodies, so
  title exclusion is not the constraint here. `M` is materially positive at 5 / 18.508871 and
  14 / 15.650092 with its whole effect on the document side at 3 and 53, aligning `comic` with
  `Comics` and `features` with `featured`; this is the opposite sign from D-028 because this
  query carries no singular-plural synonym pair, so pit 19t must not be extrapolated. `P` is
  strongly two-sided, 2 / 21.383272 and 143 / 11.482458, with its effect entirely document-side
  at 14 and 137. `E` is inert at 66 / 12.585510 and 61 / 12.713062, and curly-quote and accent
  normalization are structurally inert on these two passages, whose texts are entirely ASCII,
  measured at 66 and 61 and at 66 and 60.
- **Interaction effects.** The possessive normalization needs no partner, which is what
  separates this unit from D-021, where P+E+S was required, and from D-028, where P and T were
  co-necessary. Eleven non-oracle conditions place both required passages inside the cutoff and
  every one of them contains a preprocessing factor: G at 1 and 5, GT at 4 and 1, GS at 2 and 1,
  GM at 1 and 2, PG at 1 and 4, PGT at 1 and 2, PGM at 1 and 2, PGMT at 1 and 2, PMST at 1 and
  5, MS at 4 and 3 and the alphanumeric analyzer at 1 and 4. No condition without a
  preprocessing factor recovers both. Three non-oracle question rewrites also recover both, at
  2 and 1, 1 and 4 and 1 and 2, and each of them works by the same mechanism, writing the band
  name without its clitic; the one rewrite that keeps the possessive fails at 14 / 16.173327 and
  81 / 12.566171.
- **Gold-targeted index-side repairs, recorded as diagnostics and not as fixes.** Against a null
  control that reproduces the baseline bit for bit, repairing the answer passage's
  `debut album.` gives 7 / 16.619777, rewriting `Marvel Comics` as `Marvel comic` gives
  4 / 19.792814 and inserting `1977` gives 4 / 20.002202, while repairing the bridge passage's
  `band Suicide.` gives 66 / 12.585644 and 61 / 12.713062 and repairing the answer passage's
  `character.` gives 66 / 12.585643 and 61 / 12.713062. The two punctuation repairs are inert
  because the corresponding query tokens match no form at all; every repair that works moves the
  answer hop only and none of them ever touches the bridge hop.
- **No substitute and no complete non-gold answer.** A full-corpus scan finds `ghost rider` in
  exactly 1 passage, the answer gold itself, and `alan vega`, `martin rev` and
  `red star records` in exactly 1 each, the bridge gold itself. Thirteen non-gold passages
  contain the token `suicide` and all were read: they concern an EP title, several unrelated
  suicides, two films and a Boston hardcore band, and none refers to this band or its 1977
  album. Nine non-gold passages contain `marvel` and none links Marvel to any Suicide release.
  The nearest structural analogue, `A Boy in a Man's World` at 2 / 21.466987, is a 1989 album
  whose own text attributes its song `Batman` to an urban legend and a 1966 television theme
  rather than to a comic publisher, so it is a partial match and not a plausible non-gold
  answer. `gold_chain_substitutability`, `gold_chain_not_unique` and `plausible_non_gold_answer`
  are therefore all inapplicable.
- **Not-run cells and attribution boundary.** Not run: the query-side and document-side split of
  E, because E moves no rank at all and at most 1.4e-4 of score; the full crossing of curly-quote
  and accent normalization with G and M, because both required passages are entirely ASCII so
  those factors cannot change either gold's score and two confirming cells were run instead; the
  `peripheral_passage_content_dilution` gate, because D-028 records it as inapplicable to a
  lexical backend where length enters only through the length-normalization term that per-token
  decomposition already accounts for; and any evaluation of the possessive normalization or the
  alphanumeric analyzer on the run's other 499 questions, because that is a corpus-level
  measurement outside a single-unit validation and would require a separate gold mapping. The
  attribution boundary follows. It may not be said that the backend cannot carry an intermediate
  fact across passages, because a query-side single-token normalization supplying no
  intermediate fact places both hops inside the cutoff. It may not be said that the question
  lacks a name anchor, because the anchor is present in the query, present in both indexed
  bodies and unique enough to rank both required passages 1 and 3 on its own. It may not be said
  that the 64 competitors are the mechanism, because deleting all of them gives 8 and 2. It may
  not be said that the corpus setting is a cause, only provenance, under D-003 and pit 17. It
  may not be said that Dense's ranks explain the BM25 outcome, and the two score scales are not
  comparable. The gold-targeted repairs are a third intervention class under D-023 and are not
  deployable fixes. The possessive normalization and the alphanumeric analyzer are non-oracle
  and blind, so pit 15 does not restrict them to diagnosis, but the claim made for them is
  scoped to this unit only.
- **Corpus setting, recorded as provenance under D-003 and pit 17.** Pooled gives `any@5` 0 and
  `full@5` 0 while per-question gives `any@5` 1 and `full@5` 0, the two required passages
  ranking 6 and 1 of 10, so this is the eighth unit in which the setting changes a metric and
  the sixth of the `any@5`-only kind. All three known paths are present and each is measured
  insufficient, which is new. Of the 64 passages above the answer hop 57 are pooling-introduced
  and of the 60 above the bridge hop 53 are, yet dropping exactly those gives 15 / 12.990857 and
  9 / 13.231143, and the complement control dropping only the 7 from this question's own window
  gives 59 / 12.628019 and 54 / 12.739803. The per-question rebuild reproduces the official
  ten-title window and its ranks 6 and 1 exactly, while scoring the same ten documents with
  pooled statistics gives 9 and 8: with the document set held fixed and only the statistics
  changed, the bridge hop moves from 8 to 1. That isolates the D-024 idf-scale path for the
  second time after D-028 and confirms pit 19r, per-question avgdl being 73.600000 against a
  pooled 90.884950, `idf(1977)` 1.845827 against 5.080793, `idf(album)` 0.000000 against
  2.701588, and `what`, `brand's` and `brand` absent from the per-question vocabulary. The
  D-027 annotator-constructed path also exists, 7 of this question's own 10 passages ranking
  above both required passages, and is likewise insufficient.
- **Comparison retriever.** Complete-corpus Dense ranks the two passages 2 and 1 in both
  settings. This is reachability evidence only; it must not be written as the cause of the BM25
  outcome and the two score scales are not comparable.
- **Tie-break.** Prefer `minimal_preprocessing_score_distortion` over
  `generic_term_lexical_crowding`. Both inclusion rules are met, so the D-021 precedent applies
  and meeting the rule does not decide the tie. The crowding reading is testable and fails: no
  index-side removal of any composition places both required passages inside the cutoff, the
  binding constraint being the answer hop's own 12.585642. The preprocessing reading has a
  non-oracle counterfactual that recovers both, and it is a single query-side token. The two
  readings are causally ordered rather than merely ranked, because the category vocabulary is
  the golds' only scoring surface precisely because the name anchor contributes 0.000000, so the
  crowding is downstream of the primary and is kept as a secondary output description under its
  own deferral clause. `cross_passage_conjunction_unresolved` is not adopted: two of its three
  positive legs hold, matched token sets sharing only `on` and ten of twenty-six single factors
  carrying opposite signs, but the third does not, since there is no missing intermediate fact,
  the question naming the band and both required passages containing that name; and pit 19s
  applies regardless, in a stronger form than in D-028 because one factor suffices where D-028
  needed two. `description_only_bridge_entity` and `unindexed_title_name_anchor` are each
  excluded by their own first exclusion clause, the entity being explicitly named and the anchor
  being equally matchable in the indexed body, and both readings of the title name were tested
  as D-023 requires, the indexing reading through T at 78 / 12.352922 and 61 / 12.664186 and the
  semantic reading through a query reduced to the title at 1 / 8.935662 and 4 / 6.855023.
  `generic_query_scaffold_score_inflation` meets its inclusion rule, `brand's` supplying
  7.815653 of the rank-1 passage's 21.596320 as a non-repeated interrogative-frame token, and is
  still not adopted, because its own exclusion routes competition explained by content-bearing
  category terms elsewhere, 59 of the 64 passages above the answer hop being exactly that, and
  because the D-018 materiality standard fails, deleting the whole interrogative frame moving
  the required passages only to 64 / 12.585642 and 59 / 12.713062 and deleting the 2 passages
  containing `brand's` moving them only to 65 / 12.592570 and 60 / 12.719437. That observation
  is recorded as evidence for the primary's false-positive side instead of as a descriptor.
  `cutoff_sensitive_near_miss` is withheld on the score gap, 31.849 and 31.159 percent both
  falling inside the excluded band that runs from 12.518 percent in D-028 to 52.794 percent in
  D-025, with no score cliff and with the counter-evidence recorded rather than suppressed,
  sixty removals being needed before either passage reaches 4. `entity_alias_reference_mismatch`
  is excluded by its own final clause, which routes a punctuation or morphology variant of one
  name to `surface_form_tokenization_mismatch`. `proper_name_homonym_collision` is excluded
  because not one of the 64 passages above the answer hop contains any of the query's proper
  nouns. `same_topic_passage_distractor` is excluded because no competitor mentions any queried
  work. Failure layer: implementation. Not method, since the question's own name anchor is
  sufficient to reach both required passages once one surface form is normalized; not corpus
  setting, since all three pooling paths are measured insufficient and the answer hop fails in
  the per-question index as well, at 6 of 10; not evaluation, since neither hop has a substitute
  anywhere in the corpus and no passage supplies a complete non-gold answer.
- **Vocabulary handling.** `query_facet_fragmentation` is deliberately not registered. D-012
  reached the same fork on the same name, replacing it with this same primary and recording it
  as the closest observable ranking pattern rather than a mechanism; the observation it names is
  fully covered here by the registered `generic_term_lexical_crowding`, which has a contract,
  so registering it would duplicate an entry. That is the reason D-025 used for
  `generic_context_substitution`, D-026 for `adjacent_event_crowding`, D-027 for
  `related_document_crowding`, D-028 for `bridge_relation_underweighted` and D-029 for
  `cross_entity_relation_unresolved` and two others. `both_gold_chain_passages_missing` is
  deleted rather than registered because it states gold missingness, which D-003 and pit 17
  forbid as a causal category; the underlying observation is preserved as observed evidence, the
  two required passages standing at rank 66 and rank 61 of 4,937 rather than being absent. The
  possessive clitic is carried inside the existing primary and inside the existing
  `surface_form_tokenization_mismatch` rather than given a name of its own: D-028 registered a
  separate descriptor because the choice of indexed field is mechanically separable from the
  choice of text normalization, and that argument does not transfer to a normalization question.
- **Inventory effect.** The primary inventory is unchanged at **26 distinct names**.
  `minimal_preprocessing_score_distortion` is item 9 and was already in the inventory, and this
  is its seventh unit after D-012, D-014, D-016, D-019, D-021 and D-028. The departing name
  `query_facet_fragmentation` is item 18 and **keeps no current `case_memos_v2.csv` primary
  row**, the treatment D-021, D-022, D-023, D-027, D-028 and D-029 gave their departing names;
  it stays in the inventory union as a first-pass name in `case_memos_v1.csv`, where it is the
  first-pass primary of `5a7d61775542991319bc93b9|bm25`. The secondary-name union is unchanged
  at **50 distinct names**: `both_gold_chain_passages_missing`, item 4, remains in the union as
  a historical first-pass name and now has no current v2 row, the treatment given to
  `generic_context_substitution`, `adjacent_event_crowding`, `related_document_crowding`,
  `broad_film_person_neighborhood` and `surname_entity_confusion`. `case_memos_v2.csv` now holds
  **80 secondary assignments over 36 distinct names**, up from 79 and down from 37: this row
  went from one descriptor to two, both of which already occur elsewhere in the column, while
  the removed name was unique to this row. The distinct `primary_open_code` count in v2 falls
  from 16 to **15**, because `query_facet_fragmentation` was unique to this row as a primary and
  `minimal_preprocessing_score_distortion` was already present. `case_memos_v1.csv` is
  unchanged. The registry stays at **26 adopted descriptors** because no new descriptor is
  registered. Two existing entries gain this affected unit and D-030 as a decision source,
  `surface_form_tokenization_mismatch`, which reaches eight affected units and gains one worked
  illustration, and `generic_term_lexical_crowding`, which reaches six; and four gain D-030 as a
  decision source recording a non-adoption rather than an affected unit,
  `cutoff_sensitive_near_miss`, `generic_query_scaffold_score_inflation`,
  `description_only_bridge_entity` and `unindexed_title_name_anchor`. No definition, inclusion
  rule or exclusion rule is changed. `review_status` counts are now 21 `jointly_reviewed` and
  9 `needs_joint_review`, and twenty-one rows carry a populated `candidate_category`.
  Three vocabulary-audit items are registered rather than settled: whether the single-factor
  oracle-name test needs an explicit precondition that the injected string contribute something
  the question does not already contain, which is the same shape as the D-024 precondition;
  whether `minimal_preprocessing_score_distortion`, now on seven units and six sub-mechanisms,
  should be narrowed; and whether the boundary D-029 registered against
  `description_only_bridge_entity`, between an anchor that is absent and one that is present but
  unusable, is settled by this unit's assignment of a present-but-unusable anchor to
  `surface_form_tokenization_mismatch`.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5a83880e554299123d8c214e.md`.

## D-031 - Reclassify the Harold Godwinson burial-county Dense unit as an unresolved cross-passage conjunction

- **Date:** 2026-08-05
- **Status:** active
- **Decision:** For `5ab48c325542996a3a969f93|dense`, replace the provisional primary
  `bridge_relation_underweighted` with `cross_passage_conjunction_unresolved`. Adopt
  `description_only_bridge_entity` and `related_name_document_crowding` as secondaries. Delete
  the unregistered provisional names `bridge_relation_underweighted`,
  `subject_associate_crowding` and `location_chain_incomplete`, and register none of them. Use
  `description_only_bridge_entity` as the closest competitor. Do not adopt
  `peripheral_passage_content_dilution`, `question_frame_semantic_crowding`,
  `generic_person_semantic_neighborhood`, `cutoff_sensitive_near_miss`,
  `unindexed_title_name_anchor`, `gold_chain_substitutability` or `plausible_non_gold_answer`.
- **Affected unit:** `5ab48c325542996a3a969f93|dense`.
- **Question:** `In which county is the English king Harold Godwinson buried?` This is a bridge
  unit. `Edith Walks` is a passage about a 2017 documentary film which states in a subordinate
  clause that the film imagines a journey by Edith the Fair, wife of English king Harold
  Godwinson, from Waltham Abbey where he is buried; it is the bridge hop. `Waltham Abbey Church`
  states that the Abbey Church of Waltham Holy Cross and St Lawrence is the parish church of the
  town of Waltham Abbey, Essex, England; it is the answer hop and yields the answer Essex. The
  question names the king and asks for a county. It never states where he is buried.
- **Verified implementation:** a symmetric `all-MiniLM-L6-v2` bi-encoder, one shared encoder for
  queries and passages with no prompt or prefix, only the paragraph text encoded and the title
  excluded, explicit row-wise L2 normalization so the dot product equals cosine,
  attention-mask-aware mean pooling with a 256-token limit, stable descending sort, and no
  reranker and no cross-passage or iterative-hop step in the main Dense run. The tokenizer
  lower-cases and strips accents, so case and accent factors are identity operations on this
  backend and none was spent. Reference: `references/dense_implementation_reference.md`.
- **Exact reconstruction:** re-encoding the same first-occurrence, title-deduplicated
  4,937-passage pooled corpus reproduces all 50 stored top-50 titles in order, 0 of 50
  mismatched, with a maximum absolute score error of 3.278e-07, so strong causal claims are
  supported. Complete-corpus ranks are 18 / 0.342168 for `Edith Walks` and 21 / 0.339314 for
  `Waltham Abbey Church`. The rank-5 score is 0.488627, so the two required passages sit
  0.146459 and 0.149314 points, or 29.974 and 30.558 percent, below the cutoff. Both sit inside
  the sequence limit at 87 and 144 model tokens, so truncation is excluded. Document matrices and
  single-text vectors were read from the two manifest-guarded caches under `derived/`.
- **Diagnostic scale:** 107 distinct conditions on the same unchanged candidate set, plus 10
  deliberate repeats under a second label, every one of which reproduced its original bit for
  bit. They are the baseline; the indexing condition T; 40 non-oracle query rewrites made of 16
  reduced queries, 9 single deletions, 12 wording variants and a 5-step name-free ceiling search;
  12 per-side reachability probes; 9 oracle conditions; 14 index-side removal probes including a
  mutual complement pair and a 10-step cumulative ladder; 28 gold-targeted index-side conditions
  including 2 null controls, 3 single-fact controls, 10 ablations and 11 length-matched controls;
  and 2 combined conditions.
- **The missing intermediate fact is concrete and exists only inside the other required
  passage.** The chain is Harold Godwinson to Waltham Abbey to Essex, and the question supplies
  only its first term. A word-boundary corpus scan finds `waltham` in exactly 2 of 4,937
  passages, which are the two required passages themselves, and the word appears nowhere in the
  question. No passage anywhere in the corpus contains both `Essex` and `Harold Godwinson`. The
  answer passage never names Harold, the bridge passage never contains `Essex`, and neither
  contains the word `county`, which itself occurs in 248 passages. All three inclusion
  conditions therefore hold on read text and against the verified implementation, and all four
  exclusion clauses fail to fire.
- **Per-side reachability holds at rank 1 on both sides while each name demotes the other.**
  A query reduced to `Edith Walks` ranks its own passage 1 / 0.759333 and the other
  1386 / 0.067247; a query reduced to `Waltham Abbey Church` ranks its own 1 / 0.774335 and the
  other 98 / 0.248832; the bare `Waltham Abbey` ranks the answer passage 1 / 0.671588 and the
  bridge passage 18 / 0.319033; and the answer passage's subject-position formal name,
  `Abbey Church of Waltham Holy Cross and St Lawrence`, ranks it 1 / 0.755947 and the other
  113 / 0.237998. This is the D-025 antagonism sign and the opposite of D-026, where each bare
  name lifted the other required passage to 2, so the falsification route D-026 used against this
  name is not available here.
- **Every single anchor recovers exactly one side; only injecting both names recovers both.**
  Appending the bridge title gives 2 / 0.592542 and 10 / 0.341887; appending the answer title
  gives 13 / 0.369595 and 1 / 0.619579; appending the unnamed bridge entity gives
  11 / 0.383531 and 1 / 0.587664; naming it in place gives 11 / 0.379033 and 1 / 0.654515;
  naming it inside the relation clause gives 11 / 0.388953 and 1 / 0.587664; using the formal
  name from the gold body gives 27 / 0.330167 and 1 / 0.720498; appending the answer string
  `Essex` gives 34 / 0.328079 and 9 / 0.387997. Appending both titles gives
  3 / 0.557395 and 1 / 0.588495 and replacing the question with both titles gives
  1 / 0.644947 and 2 / 0.640705. This is the same shape D-025 recorded.
- **One generic type word, added non-oracle, carries the answer hop into the cutoff and leaves
  the bridge hop untouched.** Adding only `abbey` to the question gives 18 / 0.357596 and
  4 / 0.504249; adding `church` instead gives 29 / 0.326580 and 5 / 0.447542; adding `town` and
  `church` gives 29 / 0.326307 and 6 / 0.431341. What the answer passage lacks is the category of
  the burial site rather than a name, and that category is stated only in the other required
  passage. These conditions inject no gold identifier and no answer string and are classed as
  non-oracle, but they presuppose the intermediate fact, so they are recorded as evidence for the
  conjunction reading and explicitly not as deployable repairs.
- **The non-oracle direction is exhausted and its Pareto front never contains both hops.** Across
  40 non-oracle query conditions the best bridge result is 10 / 0.371487 with the answer hop at
  25 / 0.338254, and the best answer result is 3 / 0.545094 with the bridge hop at
  27 / 0.347204. The five name-free ceiling rewrites that spell the whole town, abbey and county
  chain into the question give 78 and 4, 27 and 3, 47 and 3, 31 and 5, and 45 and 4, recovering
  the answer hop every time and the bridge hop never. The pit 19s route that falsified this name
  in D-028 is therefore unavailable: no non-oracle condition of any kind places both required
  passages inside the cutoff.
- **Two single-fact controls price the two facts the question needs.** This unit introduces the
  intervention: delete exactly the required fact from a required passage and leave every other
  word verbatim, against the two null controls that re-encode each passage's own text into its
  own row and reproduce the baseline at 18 / 0.342168 and 21 / 0.339314. Deleting the clause
  `from Waltham Abbey where he is buried` from the bridge passage moves it from 18 / 0.342168 to
  49 / 0.291785, so the burial clause is worth 31 rank positions. Deleting `, Essex,` from the
  answer passage moves it from 21 / 0.339314 to only 23 / 0.336277, so the county name is worth
  2 rank positions and 0.003037 points. The answer passage's rank is very nearly independent of
  whether it states the answer.
- **Gold-targeted index-side repairs, recorded as diagnostics and not as fixes.** Rewriting the
  answer passage to say `in the county of Essex` gives 11 / 0.358665; inserting the county name
  into the bridge passage's burial clause gives 13 / 0.355607; doing both at once gives
  14 / 0.355607 and 11 / 0.358665. Ablating both required passages to their query-relevant
  clauses gives 1 / 0.741114 and 26 / 0.321757, and to their shortest verbatim clauses
  1 / 0.865787 and 11 / 0.365757. Only a third-class combination reaches the cutoff, ablating
  both passages under the strongest non-oracle two-hop paraphrase, at 1 / 0.740823 and
  5 / 0.491912; it requires knowing which passages are required and is not deployable.
- **The dilution gate is applied a fifth time and rejected a second time, and its two control
  forms disagree for the first time.** On the answer passage the second inclusion condition fails
  outright: reducing it to its single query-relevant sentence gives 26 / 0.318641, worse than the
  baseline 21, its 12-word verbatim county clause gives 26 / 0.321757, and only an 8-word
  truncation reaches 10 / 0.365757, still outside the cutoff, while the four length-matched
  controls at 37, 26, 54 and 38 words give 52 / 0.289974, 556 / 0.135978, 129 / 0.233163 and
  67 / 0.271233. On the bridge passage the literal D-023 control, retaining that passage's only
  non-query-relevant sentence, gives 2908 / -0.012338 and the gate would pass; but the D-027
  name-preserving control fails it, the 18-word and 14-word controls that keep the name and drop
  the burial clause giving 1 / 0.649612 and 1 / 0.725954 against ablations at 16, 13 and 11 words
  giving 1 / 0.741114, 1 / 0.817787 and 1 / 0.865787, with the 9-word name-only reduction also at
  1 / 0.643385 and the 7-word burial clause alone at 6 / 0.483665. Removing the name and keeping
  the film framing gives 2711 / -0.002227. The rank therefore tracks the fraction of the passage
  that is query-relevant rather than which sentences remain, which is the brevity direction D-025
  rejected. The descriptor is withheld and the conflict between the two control forms is
  registered rather than resolved: whenever the question's only content is the entity name, a
  name-preserving control necessarily retains query-relevant material, so the D-027 usage note
  and the D-023 wording cannot both be satisfied.
- **Single-factor effects.** Eight of the 22 single-factor conditions move the two required
  passages in opposite directions, eleven move them the same way and three are one-sided.
  Opposite: deleting the surname gives 21 / 0.330418 and 5 / 0.386949, deleting `county` gives
  10 / 0.371487 and 25 / 0.338254, a `Where` rewrite gives 16 / 0.364441 and 46 / 0.321551,
  `grave` gives 13 / 0.361337 and 34 / 0.320721, `laid to rest` gives 13 / 0.336144 and
  23 / 0.317154, adding `church` gives 29 / 0.326580 and 5 / 0.447542, adding `town` and `church`
  gives 29 / 0.326307 and 6 / 0.431341, and a name-free descriptive rewrite of the subject gives
  148 / 0.230491 and 12 / 0.390332. This is the weakest form of that leg the project has
  recorded on an adopted use of this name, against 10 of 19 in D-024 and 10 of 20 in D-025 and
  close to the 4 of 19 D-026 cited when rejecting it; the decision does not rest on it.
- **Interaction effects.** No interaction is needed to reach either hop separately and none
  suffices for both. The two families of intervention are strictly one-sided: everything that
  supplies the burial-site category or the answer facet moves only the answer hop, and everything
  that concentrates the subject name moves only the bridge hop. Combining a gold-targeted
  ablation with the removal of the framing family still gives 1 / 0.741114 and 15 / 0.321757, so
  the two one-sided levers do not add. The only interaction that crosses the cutoff on both sides
  pairs a gold-targeted ablation with the strongest non-oracle rewrite, which mixes two
  intervention classes and is recorded as such.
- **Index-side removal probes, and why the drop-everything cell is a tautology on this backend.**
  Dropping all 8 Harold-associate passages above the answer hop gives 10 / 0.342168 and
  13 / 0.339314; dropping their 11-passage complement, the framing family, gives 9 / 0.342168 and
  10 / 0.339314; dropping all 8 non-gold passages that name Harold Godwinson corpus-wide gives
  10 / 0.342168 and 13 / 0.339314; dropping all 248 non-gold passages containing `county` gives
  15 / 0.342168 and 17 / 0.339314. The cumulative ladder over the 19 non-gold passages above the
  answer hop runs 18 and 21, 15 and 18, 13 and 16, 10 and 13, 6 and 9, 3 and 6, 2 and 5, 1 and 4,
  1 and 3, and 1 and 2 at 0, 3, 5, 8, 12, 15, 16, 17, 18 and 19 removals, so 17 of the 19 must go
  before both enter the cutoff. Dropping all 19 gives 1 / 0.342168 and 2 / 0.339314, but on a
  bi-encoder that cell carries no information: a cosine score contains no collection statistic,
  so the two scores are bit-identical to the baseline and the ranks follow by construction. Pit
  19u, which D-030 established on a lexical backend where removals change `idf` and `avgdl`, is
  therefore a lexical-backend test, and its informative Dense form is the family-scoped probe
  with a complement control, which is run here and fails in both directions.
- **Both crowding readings lose on measurement rather than on their definitions.**
  `related_name_document_crowding` meets its inclusion rule on passages read in full: the 8
  Harold-associate passages occupy ranks 1 to 7 and 9 and fill the entire cutoff region, each
  stating its relationship to the queried entity in its own text, `Tostig Godwinson`
  1 / 0.612422 a brother, `Leofwine Godwinson` 2 / 0.609307 a brother, `Godwin, Earl of Wessex`
  3 / 0.564319 the father, `Battle of Stamford Bridge` 4 / 0.489070 his battle,
  `Cultural depictions of Harold Godwinson` 5 / 0.488627, `Gytha Thorkelsdottir` 6 / 0.451451 the
  mother, `The Last English King` 7 / 0.442921 a novel about him and `Edith the Fair` 9 / 0.373248
  the wife; every one of them contains the string `Harold Godwinson`. The exclusion does not fire
  on a bi-encoder, as D-027 recorded, because there is no name-form mismatch to prefer. It is
  adopted as a downstream ranking description only, because it is not outcome-determinative.
  `question_frame_semantic_crowding` is not adopted because its inclusion rule's controlled
  condition fails: deleting the whole name from the question leaves only 2 of 10 of that probe's
  top ten inside the 19 non-gold passages above the answer hop and 2 of 10 inside the baseline
  top ten, and every frame-only probe gives 0 of 10, so the framing family does not persist when
  the referent cue is removed. In the forward direction the referent cue does reproduce the other
  family, the full subject phrase giving 8 of 10 and 8 of 10 and the bare name 5 of 10 and
  5 of 10, so pits 19f and 19i agree that the Harold family belongs to the question's referent and
  the framing family belongs to neither probe.
  `generic_person_semantic_neighborhood` is not adopted because those person pages all name the
  queried entity explicitly, which is the `related_name_document_crowding` definition rather than
  a generic neighborhood, and because that entry's definition is scoped to a neighborhood that
  does not identify the queried entities.
- **No substitute and no complete non-gold answer.** `waltham` occurs in exactly 2 passages,
  which are the two required ones; the 8 word-boundary matches for `essex` outside the answer
  passage are `June Thomson`, `Paulus Hook, Jersey City`, `VMF-213`, `USS Essex (CV-9)`,
  `Essex dialect`, `Deadwood (song)` and `Newark, New Jersey`, none of which connects Waltham
  Abbey to that county; `is buried` occurs in exactly 1 passage, the bridge hop itself; and no
  passage contains both `Essex` and `Harold Godwinson`. Neither hop has a substitute, no complete
  alternative chain exists, and none of the 19 passages above the answer hop supplies either
  required fact, so all 19 are true distractors under pit 19b.
- **Not-run cells and attribution boundary.** Not run: BM25 per-token decomposition and the
  normalization ladder, which the evidence collector refuses on this backend and which have no
  cosine analogue; case and accent factors, which are identity operations under the verified
  tokenizer; a per-question statistics rebuild, which is BM25-specific under pit 19r and which
  the keep-only-ten condition already settles here; query splitting, which is the
  comparison-unit repair candidate of pit 19o and which does not apply to two hops in a
  dependency relation, with the two-hop paraphrases Z4 and Z5 already measuring that ceiling at
  31 and 5 and 45 and 4; a reranker condition, which belongs to a different experiment; and
  sub-family probes inside the framing family, since removing all 11 already fails at 9 and 10.
  On the bridge passage the literal D-023 control curve cannot be run at more than one point,
  because that passage has only two sentences. Attribution boundary: every claim here is at
  passage level. Nothing in this entry licenses a statement that the encoder attended to,
  weighted or averaged away any token, and the phrase `underweighted` is rejected for exactly
  that reason. The nine oracle conditions are diagnostics and must never be written as repairs,
  the 28 gold-targeted conditions are a third class that requires knowing which passage is
  required and are likewise not repairs, and the type-word conditions presuppose the intermediate
  fact. The drop-everything removal cell is not evidence on this backend.
- **Corpus setting, recorded as provenance under D-003 and pit 17.** Pooled and per-question
  agree on both metrics, `any@5` 0 and `full@5` 0 in each, which has happened only in D-021 and
  D-027 before, and this is the most extreme instance recorded: the two required passages rank 9
  and 10 of the 10 paragraphs HotpotQA supplies for this question, the bottom two. Of the three
  known paths only the annotator-supplied one is present. This question's own 8 distractors
  occupy pooled ranks 1 to 7 and 9; 9 of the 17 non-gold passages above the bridge hop and 11 of
  the 19 above the answer hop are pooling-introduced, and dropping exactly those gives
  9 / 0.342168 and 10 / 0.339314, which is precisely the per-question result and no recovery. The
  `idf` scale path cannot arise on a bi-encoder. Keeping only this question's own 10 paragraphs
  reproduces the official per-question window item by item, 10 of 10 in order, which verifies the
  D-025 Dense restriction property for the fifth time and in its strongest form, and it gives the
  same 9 / 0.342168 and 10 / 0.339314.
- **Comparison retriever.** Complete-corpus BM25 ranks the two passages 7 / 24.495360 and
  901 / 10.499181, so the stored `not_in_top50` status for the answer hop means rank 901 of
  4,937 rather than corpus absence; BM25 per-question ranks them 2 and 7. This is reachability
  evidence only. It must not be written as a cause of the Dense outcome, and the two backends'
  score magnitudes are not comparable.
- **Tie-break.** Prefer `cross_passage_conjunction_unresolved` over
  `description_only_bridge_entity`. Both meet their inclusion rules, so the D-021 precedent
  applies and meeting the rule does not decide the tie; the competitor is met because the
  necessary bridge entity, Waltham Abbey, is never named in the question and the answer passage
  can be reached only through the descriptive burial clue. The D-024 precondition recorded as pit
  19g is checked before the verdict is read and it holds, the bare `Waltham Abbey` ranking the
  passage it names 1 / 0.671588. The D-030 degeneracy check recorded as pit 24b is also run and
  the injected string is not degenerate, `waltham` occurring 0 times in the question and in only 2
  corpus passages. The single-factor oracle-name test that D-020 introduced then fails in six
  surface forms, at 2 and 10, 13 and 1, 11 and 1, 11 and 1, 11 and 1, and 27 and 1, and only
  injecting both names recovers both hops; this is the eleventh application of that test, its
  sixth failure, and its second failure on a Dense unit after D-025. The competitor's entire
  support is oracle, and it misdescribes the bridge side, where nothing is missing from the query
  at all: the question names Harold Godwinson, the bridge passage writes `English king Harold
  Godwinson` verbatim, and it still ranks 18 of 4,937. Ordering non-oracle evidence above oracle
  evidence follows D-028 and D-029 under pit 15. The adopted name covers both sides with one
  structural cause and survives every falsification route available to it.
- **Vocabulary handling.** No new descriptor is registered, the third consecutive decision to
  register none after D-029 and D-030. `bridge_relation_underweighted` is deleted for the second
  time, after D-028, and again on measurement rather than on precedent: it is a token-level
  weighting claim that pit 18 forbids on a bi-encoder without attribution, and its one testable
  reading is falsified, since tripling the relation word gives 21 / 0.326115 and 24 / 0.320425,
  worse than the baseline, six relation paraphrases never recover both hops, and the relation word
  alone ranks the two passages 241 and 596. D-031 records one difference from D-028, where the
  relation tokens were measured completely inert: here the relation is not inert at all, deleting
  `buried` from the question worsening both hops to 21 / 0.333201 and 47 / 0.293346 and deleting
  the burial clause from the bridge passage's indexed text costing it 31 rank positions, and the
  string `is buried` occurring in exactly 1 corpus passage, so the relation is already maximally
  discriminative in surface terms and the passage still ranks 18. The name is nevertheless wrong,
  which is the point: a mechanism can be real and its proposed name still unmeasurable.
  `subject_associate_crowding` duplicates the registered `related_name_document_crowding` and
  `location_chain_incomplete` either restates gold missingness, forbidden under D-003 and pit 17,
  or restates the adopted primary; both are deleted for the reason D-025, D-026, D-027, D-028,
  D-029 and D-030 gave for their own duplicates. `cutoff_sensitive_near_miss` is withheld on the
  score gap, 29.974 and 30.558 percent falling inside the excluded band from 12.518 percent in
  D-028 to 52.794 percent in D-025, leaving the untested band unchanged at 4.503 to 12.518
  percent; as in D-027 a real cliff can be cited, 0.069056 between rank 7 at 0.442921 and rank 8
  at 0.373865 with both required passages below it, the successive differences from rank 1 to
  rank 10 being 0.003115, 0.044988, 0.075249, 0.000442, 0.037176, 0.008530, 0.069056, 0.000616
  and 0.007934, and the counter-evidence is weak, three removals giving 15 and 18 and sixteen
  being needed before the answer hop reaches 5. `unindexed_title_name_anchor` does not apply,
  neither required title being the query's anchor, and the title-indexing condition is
  inert-to-negative at 27 / 0.314097 and 24 / 0.323271, which is the ninth measurement of that
  condition in this project and the eighth inert-or-negative result, so D-028 remains the only
  materially positive one.
- **Inventory effect.** The primary inventory is unchanged at **26 distinct names**.
  `cross_passage_conjunction_unresolved` is item 4, was already in the inventory, and this is its
  fourth validated primary use after D-022, D-024 and D-025 and its second on a Dense unit. The
  departing name `bridge_relation_underweighted` is item 1 of the primary inventory and now keeps
  **no current `case_memos_v2.csv` primary row**, but unlike every earlier departing primary it
  **keeps a current v2 secondary row**, being the provisional secondary of
  `5add67915542992200553af8|dense`, queue item 22, which is still `not_started`. The
  secondary-name union is unchanged at **50 distinct names**; `location_chain_incomplete`, item
  24, and `subject_associate_crowding`, item 40, remain in the union as historical first-pass
  names and now have **no current v2 row**, the treatment given to `generic_context_substitution`,
  `adjacent_event_crowding`, `related_document_crowding`, `broad_film_person_neighborhood`,
  `surname_entity_confusion` and `both_gold_chain_passages_missing`. `case_memos_v2.csv` still
  holds **80 secondary assignments**, now over **34 distinct names**, down from 36: this row went
  from two descriptors to two, both removed names were unique to it, and both adopted names
  already occur elsewhere in the column. The distinct `primary_open_code` count in v2 falls from
  15 to **14**. `case_memos_v1.csv` is unchanged at 39 distinct secondary names. The registry is
  unchanged at **26 adopted descriptors**. Two existing entries gain this affected unit and D-031
  as a decision source, `description_only_bridge_entity`, which reaches eight secondary affected
  units, and `related_name_document_crowding`, which reaches three; four gain D-031 as a decision
  source recording a non-adoption rather than an affected unit,
  `peripheral_passage_content_dilution`, `question_frame_semantic_crowding`,
  `cutoff_sensitive_near_miss` and `generic_person_semantic_neighborhood`; and
  `cross_passage_conjunction_unresolved` gains an extension to its existing primary-use note. In
  every case no definition, inclusion rule or exclusion rule is changed. `review_status` counts
  are now 22 `jointly_reviewed` and 8 `needs_joint_review`, and twenty-two rows carry a populated
  `candidate_category`. Validation progress after D-031 is **18 of 26 validated, 8 remaining**,
  superseding the 17-of-26 figure recorded in section 7A.14. Three vocabulary-audit items are
  registered and settled by none of this: whether the opposite-sign leg is part of this name's
  inclusion contract, given that it is met only 8 of 22 times here while D-026 cited 4 of 19 as a
  ground for rejection; whether the third inclusion condition of
  `peripheral_passage_content_dilution` can be stated so that its literal form and the D-027
  name-preserving form cannot disagree; and whether the vocabulary needs anything to carry a
  required passage whose query-relevant material is a small fraction of its text but which fails
  that gate on the brevity direction, which is the converse of the gap D-023 recorded.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ab48c325542996a3a969f93.md`.

## D-032 - Retain one-sided entity crowding for the Ince / McGrath BM25 comparison unit

- **Date:** 2026-08-05
- **Status:** active
- **Decision:** For `5ab8f57b5542991b5579f097|bm25`, retain the provisional primary
  `one_sided_entity_crowding`. Retain `related_name_document_crowding` and adopt
  `cutoff_sensitive_near_miss` for the `Joseph McGrath (film director)` passage only. Add
  `unindexed_title_name_anchor` and `generic_query_scaffold_score_inflation` as secondaries. Use
  `unindexed_title_name_anchor` as the closest competitor. Register no new descriptor. Do not
  adopt `minimal_preprocessing_score_distortion`, `surface_form_tokenization_mismatch`,
  `entity_alias_reference_mismatch`, `generic_term_lexical_crowding`,
  `proper_name_homonym_collision`, `compound_two_sided_crowding`,
  `cross_passage_conjunction_unresolved`, `same_artist_work_crowding`,
  `same_topic_passage_distractor`, `two_named_entities_underprioritized`,
  `repeated_function_word_amplification`, `repeated_content_word_amplification`,
  `question_frame_semantic_crowding`, `answer_property_semantic_crowding`,
  `plausible_non_gold_answer`, `gold_chain_not_unique` or `gold_chain_substitutability`.
  `peripheral_passage_content_dilution` is inapplicable on this backend and its gate was not
  applied.
- **Affected unit:** `5ab8f57b5542991b5579f097|bm25`.
- **Question:** `Were Thomas H. Ince and Joseph McGrath of the same nationality?` This is a
  comparison unit and the second in this pass, after `5a78b209554299148911f93e|dense`, and the
  first comparison unit on a lexical retriever. `Joseph McGrath (film director)` states that he
  was born in 1930 in Glasgow and is a Scottish film and television director and screenwriter.
  `Thomas H. Ince` states that Thomas Harper Ince, 1880 to 1924, was an American silent film
  producer, director, screenwriter and actor. The two passages supply the two nationalities and
  the answer is no. Each required passage is independent of the other; nothing has to be resolved
  in one and carried into the other.
- **Verified implementation:** only paragraph text is indexed and titles are excluded;
  `text.lower().split()` is the whole analyzer, with no punctuation handling, stop-word removal,
  stemming, Unicode normalization, phrase matching or initial expansion; `rank-bm25==0.2.2`
  `BM25Okapi` with the library defaults `k1=1.5`, `b=0.75` and `epsilon=0.25`; every occurrence of
  a repeated query token is accumulated. Implication 4 of
  `references/bm25_implementation_reference.md` applies verbatim to this unit: the implementation
  cannot connect an initial to an expanded name without literal token overlap. Reference:
  `references/bm25_implementation_reference.md`.
- **Exact reconstruction:** rebuilding the index over the read-only 4,937-passage pooled corpus
  reproduces all 50 stored top-50 titles in order, 0 of 50 mismatched, with a maximum absolute
  score error of 0.000000, and every per-token decomposition reconciles against `get_scores`
  within 7.105e-15, so strong causal claims are supported. Complete-corpus ranks are
  6 / 26.870093 for `Joseph McGrath (film director)` and 11 / 19.741610 for `Thomas H. Ince`. The
  rank-5 score is 28.423217, so the two required passages sit 1.553124 and 8.681607 points, or
  5.464 and 30.544 percent, below the cutoff; the successive differences from rank 1 to rank 10
  are 3.872190, 0.145559, 0.796755, 1.958705, 1.553124, 1.781180, 3.413115, 1.487109 and
  0.318694, so no score cliff separates the cutoff region from the nearer required passage. The
  gold-targeted substitution path was verified with a null control that re-indexes both required
  bodies verbatim and reproduces the baseline with 0 of 4937 order changes and a maximum absolute
  score difference of 0.000000.
- **Diagnostic scale:** 151 distinct conditions on the same unchanged candidate set, plus 14
  deliberate repeats under a second label, every one of which reproduced its original bit for
  bit. This is the largest battery in the project, after D-030's 147. They are all 16 cells of a
  P x E x S x T factorial; 22 further preprocessing conditions splitting P, E and M into
  query-side and document-side halves and crossing them with S and T; 8 conditions isolating a
  single query token, including the two-sided control that refutes them; all 8 cells of a wording
  factorial and the same 8 again with the scaffold removed; 11 single query-token deletions; 16
  reduced-query probes; 12 per-side reachability probes; 3 query-splitting pairs measured at three
  budgets each; 8 neighbourhood-overlap probes in both directions; 22 index-side removal probes
  including a family probe, its complement control, 3 sub-family probes, a 9-step cumulative
  ladder, a size-matched null control and a statistics-matched control; 4 corpus-setting
  reconstructions; 11 gold-targeted index-side conditions including a null control and 4
  single-fact controls; and 7 oracle conditions.
- **One query token scores nothing for either required passage and a great deal for one
  candidate's satellites.** The `Thomas H. Ince` passage's indexed body writes `Thomas Harper
  Ince`, so the query token `h.` contributes exactly 0.000000 to it, while eight of the nine
  non-gold passages above it write `Thomas H. Ince` verbatim and take between 4.461297 and
  7.814359 from that single token: `Ralph Ince` 6.368065, `Elinor Kershaw` 7.482306,
  `The Scourge of the Desert` 7.814359, `John Ince (actor)` 6.540080,
  `The Coward (1915 film)` 5.563285, `The Deserter (1912 film)` 7.570034,
  `Thomas Ince: Hollywood's Independent Pioneer` 5.500095 and `Thomas H. Gale House` 4.461297.
  Under pit 19x the whole ranking is compared rather than the two gold ranks: deleting `h.`
  changes 4896 of 4937 order positions with a maximum absolute score difference of 8.333161 while
  leaving both required passages' scores bit-identical. Three reduced queries state the mechanism
  in one line. The question's own name form, which is also that passage's title, ranks it
  6 / 16.787469; the same name with only the middle initial removed ranks it 2 / 16.787469 at a
  bit-identical score; and the body's own form `Thomas Harper Ince`, an oracle condition, ranks it
  1 / 27.005232. A corpus scan explains the asymmetry: the string `Thomas H. Ince` occurs in 8
  non-gold passages and 0 times in that passage's own body, `Thomas Harper Ince` occurs in exactly
  1 passage which is itself, and `mcgrath` occurs in exactly 1 of 4,937 passages at the query's
  highest idf of 8.098947.
- **The question's only statement of the compared property is inert, and so is its repair.**
  `nationality?` occurs in 0 corpus passages and contributes exactly 0.000000; deleting it leaves
  the 4,937-passage order 0 of 4937 changed with a maximum absolute score difference of 0.000000.
  This is the fifth such token after D-019, D-021, D-028 and D-030. It is also the first for which
  the repair is measured and is worth nothing either: normalizing it to the corpus form
  `nationality`, which occurs in 7 passages, leaves both required passages at 6 / 26.870093 and
  11 / 19.741610, because neither contains that word. In D-030 the corresponding repair was worth
  64 rank positions, so this pair of results is a boundary sample rather than a repetition.
- **The competitor family is one-sided, fills the entire cutoff region, and is
  outcome-determinative under a falsifiable pair of probes.** All 5 passages above the McGrath
  passage and 7 of the 9 above the Ince passage are Ince-side documents, each stating its
  relationship in its own text: `Ralph Ince` 1 / 35.196426 a brother, `Elinor Kershaw`
  2 / 31.324236 the wife, `The Scourge of the Desert` 3 / 31.178677 a film he produced,
  `John Ince (actor)` 4 / 30.381922 the eldest brother, `The Coward (1915 film)` 5 / 28.423217 a
  film he produced, `The Deserter (1912 film)` 7 / 25.088913 a film he wrote and directed, and
  `Thomas Ince: Hollywood's Independent Pioneer` 8 / 21.675798 a biography of him. The McGrath
  side has 0 competitors. Dropping the 7 gives 1 / 26.868145 and 2 / 22.167723 while dropping
  their 2-passage complement gives 6 / 26.911596 and 9 / 19.763251. The cumulative ladder over the
  9 non-gold passages above the worse required passage runs 6 and 11, 5 and 9, 4 and 7, 3 and 6,
  2 and 5, 1 and 3, 1 and 2, 1 and 2, 1 and 2, and 1 and 2 at 0 through 9 removals, crossing the
  cutoff at the fourth at 2 / 26.869286 and 5 / 21.307440. No sub-family suffices: 3 relatives
  give 3 / 26.869559 and 6 / 20.765099, 3 films give 4 / 26.869075 and 6 / 20.377303, the
  biography alone gives 6 / 26.869693 and 10 / 19.764063, and relatives plus films give
  1 / 26.868542 and 2 / 22.143053. Dropping all 8 non-gold passages containing the string
  `Thomas H. Ince` gives 1 / 26.867443 and 2 / 22.192635, and dropping the 5 non-gold passages
  carrying the bare token `ince` gives 1 / 26.868958 and 3 / 22.118781.
- **Two removal controls this unit introduces, because on a lexical backend a removal changes the
  scoring function as well as the candidate set.** D-027 could record that gold scores were
  bit-identical under every removal because cosine carries no collection statistic; that sentence
  must not be copied here, since the Ince passage's score rises from 19.741610 to 22.167723 under
  the family probe as `idf(ince)` increases. A size-matched null control dropping the 7 most
  highly ranked passages that contain none of the query's name tokens gives 6 / 26.861098 and
  11 / 19.734995, and a statistics-matched control dropping 7 passages that do contain `thomas` or
  `h.` but all rank below the worse required passage gives 6 / 26.905808 and 11 / 19.829852, worth
  0.088242 points and 0 rank positions. Neither corpus shrinkage nor idf drift accounts for the
  family probe. A third control in the same family, dropping all 31 non-gold passages carrying the
  bare token `joseph`, gives 4 / 31.046130 and 10 / 19.764622, and is recorded as an idf effect
  rather than a competitor removal, because none of those passages ranks above the McGrath
  passage; its score rises from 26.870093 to 31.046130 as `df(joseph)` falls from 32 to 1.
- **The pit 19u drop-everything cell has discriminative power on this backend and succeeds.**
  Dropping all 9 non-gold passages above the worse required passage gives 1 / 26.909654 and
  2 / 22.191974. This is the opposite outcome to D-030, where dropping all 64 still gave 8 and 2
  and one cell disposed of the whole crowding reading, and it is informative here in a way it is
  not on a bi-encoder, where D-031 showed the cell is a tautology.
- **The pit 19f and 19i test runs in both directions with the same sign, and identifies the
  mechanism rather than routing it away.** Forward, a query reduced to `Thomas H. Ince` puts 5 of
  10 of its top ten inside the baseline top five, 8 of 10 inside the top ten and 9 of 10 inside
  the top eleven; `ince` alone gives 5 of 10, 5 of 10 and 6 of 10. In reverse, deleting
  `Thomas H. Ince` from the question leaves 0 of 10, 2 of 10 and 2 of 10. The interrogative frame
  alone and `nationality` alone each give 0 of 10 at every depth, so neither produces any part of
  this neighbourhood, and `Joseph McGrath` alone gives 0 of 10, 1 of 10 and 1 of 10. Deleting only
  `h.` still leaves 5 of 10, 7 of 10 and 8 of 10, so the family is not an artefact of the initial.
  As D-027 recorded for the same descriptor, the cue that reproduces the neighbourhood is one of
  the two named candidates and a comparison question must contain it, so there is no more specific
  upstream mechanism to route to and the criterion names the mechanism.
- **Per-side reachability, which pit 25f substitutes for oracle-name injection on a comparison
  unit, is extremely asymmetric.** The McGrath passage ranks 1 under seven single-sided queries,
  five of them non-oracle: `Joseph McGrath` 1 / 17.888493, its own title 1 / 17.888493,
  `Joseph McGrath nationality` 1 / 17.888493, `Joseph McGrath biography` 1 / 17.888493,
  `Joseph McGrath film director` 1 / 25.504577, the framed query with the Ince side deleted
  1 / 25.733496, and the answer-injecting `Was Joseph McGrath Scottish?` 1 / 20.503494; only
  `What nationality was Joseph McGrath?` falls short, at 6 / 9.457447. The Ince passage never
  reaches the cutoff under the name form the question uses: 6 / 16.787469 bare, 6 / 16.787469 with
  `nationality`, 7 / 16.787469 with `biography`, 6 / 19.655078 with `film director`,
  9 / 19.741610 for the framed one-sided query, 13 / 9.523848 for the natural rewrite and
  5 / 19.741610 only when the answer word is injected. It reaches 2 / 16.787469 when the middle
  initial is dropped and 1 / 27.005232 only under the oracle body form. Pit 19n therefore holds in
  a new form here: not that a passage fails under its own bare name, as with D-027's Albee side,
  but that it fails under the name form the question uses and succeeds under the form without the
  initial.
- **Query splitting, the comparison-unit repair candidate of pit 19o, was measured in three forms
  and never returns both required passages.** Keeping the full frame per side gives 9 and 1, the
  natural single-sided rewrite gives 13 and 6, and bare names give 6 and 1. At budgets of 2, 3 and
  5 results per side the union never contains both, because the Ince passage sits outside the top
  five of a query consisting only of its own side, whose top five is five family documents. Having
  measured it, this entry may state that no deployable query-decomposition repair exists here.
- **Fifteen non-oracle conditions place both required passages inside the cutoff and every one of
  them removes or lacks the query scaffold; no single factor does.** They form two families:
  removing or destroying `h.` together with scaffold removal, giving 2 / 17.888493 and
  3 / 16.787469, and indexing titles together with scaffold removal, giving 4 / 22.885192 and
  1 / 27.642683. Scaffold removal alone gives 6 / 17.888493 and 7 / 16.787469 and the
  title-indexing condition alone gives 3 / 31.744369 and 6 / 30.547523.
- **A one-sided preprocessing gain can be a broken match rather than a repair, which is a new
  interaction shape.** Normalizing `h.` on the query side alone gives 2 / 26.870093 and
  8 / 19.741610, and on the document side alone 2 / 26.870094 and 8 / 19.741610; each recovers both
  required passages once the scaffold is removed, at 2 / 17.888493 and 3 / 16.787469. Normalizing
  both sides so the token realigns returns the baseline at 6 / 26.870094 and 11 / 19.741610, and
  with scaffold removal gives 6 / 17.888493 and 7 / 16.787469, bit-identical to scaffold removal
  alone on both required passages. The sign is therefore not additive: both single sides are
  positive and the pair is inert. This is neither D-028's shape, where the effect was wholly
  document-side, nor D-030's, where it was wholly query-side, and it is recorded as a new pit
  extending pits 19p and 19v: after splitting a preprocessing factor into its two sides, the cell
  with both sides applied must also be run. The two-sided P factor is negative on both required
  passages at 8 / 26.567864 and 16 / 18.889345, and document-side punctuation stripping alone
  moves the Ince passage the wrong way, from 11 / 19.741610 to 13 / 18.889345, because it merges
  `ince.` and `ince,` into `ince` and enlarges the name-sharing family. Crude stemming is strongly
  negative on the query side, sending that passage to 212 / 13.171903 by damaging the surname, and
  becomes positive only once titles are indexed, giving 4 / 22.885192 and 1 / 27.642683 with
  scaffold removal; this is a third source of sign for the M factor after D-028's negative and
  D-030's positive, and unlike either it is a proper-noun effect rather than a plural or
  derivational one.
- **The wording direction is exhausted and inert.** All 8 cells of a wording factorial over a
  `Did ... have` rewrite, an added `biography` and the removal of the leading interrogative and
  the final question mark leave the two required passages between 6 and 7 and between 8 and 12,
  and the same 8 cells with the scaffold removed leave them between 6 and 7 and between 7 and 8.
  No wording cell recovers both. The entire effect of the `Did ... have` rewrite is that it
  removes `of`, its scores matching that single deletion exactly.
- **Two single-fact controls under pit 19z give the unit's most informative measurement.**
  Deleting `American` from the Ince body and leaving every other word verbatim moves it from
  11 / 19.741610 to 10 / 19.893367, and deleting `Scottish` from the McGrath body moves it from
  6 / 26.870093 to 6 / 27.039416; both are marginally better, because the passage is shorter.
  Deleting both gives 6 / 27.039402 and 10 / 19.893361. Deleting the whole name instead gives
  4800 / 3.023334 and 3006 / 9.077577. These passages' ranks are determined by their name tokens
  and are very nearly independent of whether they state the answer at all, which is the same
  finding D-031 recorded for a county name and here holds for both required passages at once.
- **Gold-targeted name-form repairs, recorded as third-class diagnostics and not as fixes.**
  Rewriting the Ince body from `Thomas Harper Ince` to `Thomas H. Ince` gives 7 / 26.870096 and
  6 / 27.091980; prefixing only that passage's own title to its own body gives 7 / 26.870134 and
  4 / 30.556564; prefixing only the McGrath passage's title gives 2 / 31.546942 and
  11 / 19.741637; prefixing both gives 2 / 31.546981 and 5 / 30.556598, the only one of the four
  that recovers both and the one that requires knowing which passages are required. Adding
  scaffold removal to the first gives 7 / 17.888493 and 2 / 24.137838. Every deployable form of
  the anchor repair is defeated by the family, because indexing all titles also feeds three family
  documents whose titles contain `ince` or `thomas`.
- **The oracle direction is degenerate, as pit 25f predicts, and was checked token by token under
  pit 24b.** Appending the Ince title injects `thomas`, `h.` and `ince`, all three of which the
  question already contains, so the condition is pure token repetition; it gives
  11 / 26.870093 and 7 / 36.529080, demoting the other required passage. Appending the McGrath
  title injects `(film` at an idf of 8.098947 with term frequency 0 in both required passages and
  `director)` which is out of vocabulary, and gives 1 / 44.758586 and 27 / 19.741610. Appending
  both titles gives 6 / 44.758586 and 8 / 36.529080; appending the two answers verbatim gives
  2 / 33.670928 and 10 / 21.486347; appending the Ince body's own name form gives 9 / 26.870093
  and 2 / 46.746842; adding the answers to that gives 7 / 33.670928 and 2 / 48.491578. Only
  verbatim injection of both bodies' identifying clauses recovers both, at 2 / 69.032806 and
  3 / 65.413184. Six of the seven oracle conditions fail, so the single-factor oracle-name test
  D-020 introduced is again unavailable in the form D-017, D-023 and D-026 used, exactly as pit
  25f requires on a comparison unit, and the decision rests on the reduction side instead.
- **Corpus setting, recorded as provenance under D-003 and pit 17.** Pooled gives `any@5` 0 and
  `full@5` 0 at 6 and 11; the official per-question setting gives `any@5` 1 and `full@5` 0 at 1
  and 10, and the per-question index was rebuilt and reproduces the stored CSV order title by
  title. This is the ninth `any@5` divergence in the series, D-030 being the eighth, and the third unit after D-028 and D-030 to
  present more than one path at once. New competitors is measured and fails: all 5 passages above
  the McGrath passage come from the item's own window and 0 are pooling-introduced, 7 of the 9
  above the Ince passage come from the window, and dropping the 2 pooling-introduced passages
  gives 6 / 26.911596 and 9 / 19.763251. The idf-scale path carries the whole flip and is cleanly
  isolated as in D-028: the pooled scores themselves restricted to those 10 paragraphs give
  6 / 26.870093 and 9 / 19.741610, the same 10 documents with pooled idf and pooled `avgdl`
  substituted reproduce that title by title, and with pooled idf but per-question `avgdl` kept both
  required passages hold their positions at 6 / 23.173455 and 9 / 17.855162 and only one adjacent
  non-gold pair swaps, so `avgdl` carries none of the flip. This is the same division D-028
  recorded, where `avgdl` adjusted magnitudes and two adjacent non-gold pairs and nothing else. In the
  ten-document index `ince` has document frequency 6 of 10, `thomas` 9, `h.` 8, and `and`, `of`
  and `the` 9 each, and all six are floored to the identical 0.390062 by `epsilon`, while
  `mcgrath` and `joseph` have document frequency 1 and idf 1.845827 and `were` and `same` have
  document frequency 0; `avgdl` falls from 90.884950 to 53.700000 and `average_idf` from 7.669260
  to 1.560249. The small index therefore destroys exactly the tokens that drive the crowding and
  preserves exactly the McGrath side's two, which is why the McGrath passage ranks 1 there while
  the Ince passage, whose entire score rests on the floored tokens, ranks 10 of 10 and so fails
  independently of pooling. This is the second measured instance of the setting-dependent gold
  swap recorded in the corpus-setting subsection of
  `references/bm25_implementation_reference.md`, with a different fingerprint: there one token hit
  document frequency 5 of 10 and took an idf of exactly 0, here six distinct tokens are floored to
  one identical value. The annotator-supplied path is present in its maximal form, all 8 of this
  question's own HotpotQA distractors being Ince-side against 6 of 8 in D-027.
- **No substitute and no complete non-gold answer.** No passage in the corpus contains both `ince`
  and `mcgrath`; `mcgrath` occurs in exactly 1 passage and `thomas harper ince` in exactly 1, each
  being the required passage itself; `scottish` together with `mcgrath` occurs in exactly 1, the
  same passage. Five passages name Ince and contain `american`, but on read text the word
  describes a brother, the wife or a film in every case and none states Thomas H. Ince's own
  nationality, so they license an inference from a sibling's nationality rather than supplying the
  required fact. This is the treatment D-027 gave `Reed A. Albee`. Under pit 19b all nine passages
  above the required evidence are true distractors, seven family documents and two pure name
  collisions.
- **Comparison retriever.** Dense places `Joseph McGrath (film director)` at 1 and
  `Thomas H. Ince` at 4, both inside the stored window of 50, so these are exact complete-corpus
  ranks and no reconstruction was needed under pit 7. The Dense results CSV carries no scores and
  none is quoted, per pit 22. This is reachability evidence only: it must not be written as a cause
  of the BM25 outcome, the two backends' score magnitudes are not comparable, and
  `5ab8f57b5542991b5579f097|dense` is not one of the 26 single-note units and receives no
  conclusion here.
- **Tie-break.** Prefer `one_sided_entity_crowding` over `unindexed_title_name_anchor`. Both meet
  their inclusion rules, so under pit 13 meeting the rule does not decide the tie: the competitor's
  three inclusion conditions all hold, since titles are verifiably not indexed, the title contains
  the query's anchor tokens in a matchable form, and the title-indexing condition measurably
  improves that passage by 10.805913 points and 5 rank positions. The tie turns on three
  measurements. First, the name-anchor reading is repaired to its limit in three forms and the
  failure survives all three, reaching 6, 4 and 6 respectively and twice at the other required
  passage's expense; only the non-deployable both-golds form recovers the pair. Second, the
  crowding reading is testable in both directions and passes, with a family probe that recovers
  both, a complement control that recovers neither, and two further controls showing the result is
  not corpus shrinkage or idf drift. Third, and decisively for a comparison unit, which succeeds
  or fails as a pair, only the crowding reading accounts for the McGrath passage, which has no
  name-form problem of any kind, ranks 1 under five non-oracle single-sided queries, and fails
  solely because five Ince-side documents occupy the top five that both candidates must share.
  This is the same tie-break D-027 used on the Dense unit of a different example. D-010's routing
  clause, which prefers a more specific implementation-supported name-form mismatch, is tested on
  a lexical backend for the first time and does not fire; unlike D-010's Barrie passage, where all
  three query name tokens missed the body, two of the three hit here. The two units have different
  unit keys, so reaching a different primary is the unit-key rule working rather than D-010 being
  carried across. Non-oracle evidence is ordered above oracle evidence under pit 15, following
  D-028, D-029 and D-031. Failure layer: method. Not implementation, because no preprocessing or
  indexed-field change alone recovers the pair, the two that do are pipeline design choices rather
  than defects, and repairing the name form to its limit still fails. Not corpus setting, because
  all three pooling paths are measured, the new-competitor path fails outright, and the Ince
  passage ranks 10 of 10 in its own per-question index. Not evaluation, because neither required
  fact has a substitute anywhere in the corpus and no passage supplies a complete non-gold answer.
- **Not-run cells and attribution boundary.** Not run: the full 4 x 4 crossing of the single-token
  `h.` conditions with the scaffold factor, because the two-sided control already settles that the
  one-sided gain is a broken match and expanding the cross would only repeat that finding, at the
  cost of leaving the joint-effect decomposition unstated; the title-indexing condition crossed
  with all 16 wording cells, because the wording direction is exhausted and inert and T is already
  crossed with S, both sides of P, M and both single-token conditions; removal probes crossed with
  gold-targeted conditions, because each class already recovers both and the cross would merge two
  sufficient conditions in one cell; a McGrath-side family removal probe, because there is no
  McGrath-side family to remove, all 5 passages above it being Ince-side, with the `joseph`
  homonym set covered instead; the `peripheral_passage_content_dilution` gate and its
  length-matched control curve, because that definition is scoped to a whole-passage mean-pooled
  encoder and the precondition fails on a lexical backend, so it was deliberately not applied;
  any Dense reconstruction, because the comparison retriever serves only as reachability evidence
  and both required passages lie inside the stored window; further oracle variants, because
  verbatim injection of both bodies' identifying clauses is already the strongest form and already
  recovers both, and pit 25f establishes that this direction lacks discriminative power on a
  comparison unit; and distractor-side text ablation, a fourth intervention class with no
  precedent contract, as in D-027. Attribution boundary: the one-sided `h.` conditions must not be
  read as evidence that boundary-punctuation normalization repairs this unit, the two-sided cell
  being bit-identical to scaffold removal alone. D-027's statement that gold scores are
  bit-identical under every removal must not be copied to this backend. The title-indexing result
  must not be read as establishing that the anchor's confinement to the title is the primary
  cause, the semantic reading giving 6 / 16.787469 and all three anchor repairs failing. The
  observation that dropping the middle initial helps must not be written as a recommended query
  normalization rule, since it is reversed wherever an initial disambiguates and that case was not
  measured here. No X or L condition and no oracle condition is a deployable repair, under pits
  15 and 19d. The per-question `any@5` of 1 must not be read as making pooling the cause, under
  pit 17 and D-003. The statement that `h.` and the scaffold each carry about half the gap to rank
  1 is a decomposition of the baseline score difference and not of any intervention's effect.
- **Vocabulary handling.** No new descriptor is registered, the fourth consecutive decision to
  register none after D-029, D-030 and D-031, and the first in this pass in which a provisional
  primary is retained unchanged while the secondary set grows. `one_sided_entity_crowding` gains
  its second validated primary use and its first on a lexical retriever.
  `unindexed_title_name_anchor` gains its second affected unit and only its second materially
  positive measurement of the title-indexing condition in nine, so the seven inert-or-negative
  results must still not be extrapolated; the entry's semantic reading is recorded as disagreeing
  with D-028's, 6 / 16.787469 against 1, because the title string occurs verbatim in 8 non-gold
  passages, which makes it matchable but not corpus-discriminative.
  `generic_query_scaffold_score_inflation` gains its third affected unit and is adopted on
  co-necessity rather than solo materiality, the form D-028 used for the title-indexing condition
  and the opposite outcome to D-030, where the same descriptor met its inclusion rule and was
  withheld; its inclusion rule is met on four non-repeated scaffold tokens supplying 29.4 to 53.4
  percent of the competitor scores, with `Joe Scarborough` 9 / 20.188689 taking 53.4 percent while
  containing no Ince or McGrath content and `Thomas H. Gale House` 10 / 19.869995 taking 48.4
  percent while being a Frank Lloyd Wright house, and its category-term exclusion, which fired in
  D-030, does not fire here because the competition is carried by proper-noun tokens.
  `related_name_document_crowding` gains its fourth affected unit, its first on a lexical
  retriever, and the first test in which its own first exclusion is checked on a lexical backend
  and does not fire. `cutoff_sensitive_near_miss` is adopted for the nearer required passage only,
  the split D-023, D-025 and D-026 used, at 5.464 percent, which lands in the band this project
  had never measured; accepting it moves the accepted band's upper edge from 4.503 to 5.464 percent
  and narrows the untested band to 5.464 to 12.518 percent without editing any rule text. The
  counter-evidence that carries it is the strongest this project has recorded in either direction
  and it supports adoption rather than qualifying it: an index-side removal of a single competitor
  already lifts that passage to 5 / 26.870018 and flips `any@5`, while the no-substitute condition
  holds, `mcgrath` occurring in exactly 1 of 4,937 passages, itself, and no score cliff can be
  cited. The other required passage sits at 30.544 percent inside the excluded band, so this
  descriptor can describe only the `any@5` outcome and no rank movement of the near passage alone
  can change `full@5`, the D-025 and D-026 boundary again.
  Three entries gain D-032 as a decision source recording a non-adoption rather than an affected
  unit: `surface_form_tokenization_mismatch`, whose fifth dead-token instance this is and whose
  first inert repair; `proper_name_homonym_collision`, withheld on the D-018 materiality standard
  for the second time after D-029's treatment of a different descriptor; and
  `generic_term_lexical_crowding`, withheld with a 0 of 10 measurement in both directions. No
  definition, inclusion rule or exclusion rule is changed anywhere.
- **Inventory effect.** The primary inventory is unchanged at **26 distinct names**.
  `one_sided_entity_crowding` is item 13 and was already in the inventory; before this unit its
  only validated primary use was D-027's, and the provenance sentence recorded in D-027, that the
  name also survived as the first-pass primary of this row while it was still `not_started`, is
  now discharged. No name departs, so nothing needs the treatment D-021 through D-031 gave their
  departing names. The secondary-name union is unchanged at **50 distinct names**; both added
  names already occur in the column. `case_memos_v2.csv` now holds **82 secondary assignments
  over 34 distinct names**, up from 80 and unchanged from 34: this row went from two descriptors
  to four and both additions already occur elsewhere. The distinct `primary_open_code` count in
  v2 is unchanged, since the primary is retained. `case_memos_v1.csv` is unchanged. The registry
  stays at **26 adopted descriptors** because no new descriptor is registered; four existing
  entries gain this affected unit and D-032 as a decision source and three gain D-032 as a
  decision source recording a non-adoption. `review_status` counts are now 23 `jointly_reviewed`
  and 7 `needs_joint_review`, and twenty-three rows carry a populated `candidate_category`.
  Validation progress after D-032 is **19 of 26 validated, 7 remaining**, superseding the
  18-of-26 figure recorded in section 7A.15. Four vocabulary-audit items are registered and
  settled by none of this: whether crowding-family names need an explicit primary-use contract,
  now that this name has a validated primary use on each backend; whether
  `unindexed_title_name_anchor` should require its semantic reading to reach the cutoff, given two
  affected units at 1 and at 6 / 16.787469; whether co-necessity is a sufficient ground for a
  secondary, given that D-030 refused `generic_query_scaffold_score_inflation` on solo materiality
  and this entry accepts it on co-necessity; and whether the operational meaning of `explains the
  primary failure` in `related_name_document_crowding`'s first exclusion should be written as the
  test used here, a gold-targeted repair of the name form that still leaves the passage outside
  the cutoff.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_comparison_5ab8f57b5542991b5579f097.md`.

## D-033 - Reclassify the Rose McGowan / Planet Terror BM25 unit as minimal-preprocessing score distortion

- **Date:** 2026-08-05
- **Status:** active
- **Decision:** For `5abcc96c5542996583600492|bm25`, replace the provisional primary
  `partial_match_constraint_omission` with `minimal_preprocessing_score_distortion`. Adopt
  `surface_form_tokenization_mismatch`, `related_name_document_crowding`,
  `generic_term_lexical_crowding` and `generic_query_scaffold_score_inflation` as secondaries.
  Use `cross_passage_conjunction_unresolved` as the closest competitor. Delete the provisional
  names `partial_match_constraint_omission`, `cross_entity_relation_unresolved` and
  `answer_entity_missing_both_methods` rather than registering any of them. Register no new
  descriptor. Do not adopt `cross_passage_conjunction_unresolved`,
  `unindexed_title_name_anchor`, `cutoff_sensitive_near_miss`, `description_only_bridge_entity`,
  `repeated_function_word_amplification`, `proper_name_homonym_collision`,
  `repeated_content_word_amplification`, `compound_two_sided_crowding`,
  `same_topic_passage_distractor`, `entity_alias_reference_mismatch`, `gold_chain_not_unique`
  or `gold_chain_substitutability`. `peripheral_passage_content_dilution` is inapplicable on
  this backend and its gate was not applied.
- **Affected unit:** `5abcc96c5542996583600492|bm25`.
- **Question:** `What is the name of the film starring Rose McGowan and features the character
  Earl McGraw's daughter?` This is a bridge unit. `Earl and Edgar McGraw` states that Earl has a
  daughter introduced in the Grindhouse films, named Dakota, played by Marley Shelton, who plays
  a large role in Planet Terror. `Planet Terror` states that the film stars Rose McGowan among
  others. The answer is Planet Terror. The question carries two constraints and each required
  passage satisfies exactly one of them.
- **Verified implementation:** only paragraph text is indexed and titles are excluded;
  `text.lower().split()` is the whole analyzer, with no punctuation handling, stop-word removal,
  stemming, Unicode normalization or phrase matching; `rank-bm25==0.2.2` `BM25Okapi` with the
  library defaults `k1=1.5`, `b=0.75` and `epsilon=0.25`; every occurrence of a repeated query
  token is scored separately; the pooled corpus holds 4,937 passages at an average document
  length of 90.884950.
- **Exact reconstruction:** rebuilding the index over the read-only 4,937-passage pooled corpus
  reproduces all 50 stored top-50 titles in order, 0 of 50 mismatched, with a maximum absolute
  score error of 0.000000, and every per-token decomposition reconciles against `get_scores`
  within 3.553e-15, so strong causal claims are supported. Complete-corpus ranks are
  26 / 28.798100 for `Earl and Edgar McGraw` and 115 / 26.074919 for `Planet Terror`; pit 7
  applies, since the stored window records the second as `not_in_top50` while it is in the
  corpus at 115 of 4,937. The rank-5 score is 31.796696, so the two required passages sit
  2.998596 and 5.721776 points, or 9.431 and 17.995 percent, below the rank-5 score; the
  successive differences from rank 1 to rank 10 are 1.153544, 1.384457, 3.638157, 0.795088,
  0.183632, 0.219417, 0.130204, 0.581458 and 0.113202, so the only cliff lies between ranks 3
  and 4 and both required passages are below it. The gold-targeted substitution path was
  verified with a null control that re-indexes both required bodies verbatim and reproduces the
  baseline at 26 / 28.798100 and 115 / 26.074919.
- **Diagnostic scale:** 201 distinct labelled conditions on the same unchanged candidate set,
  16 of them deliberately repeated under a second label with every repeat reproducing its
  original bit for bit, for 218 recorded rows. They are all 64 cells of a P x E x G x M x S x T
  factorial, where G is the possessive-clitic normalization D-030 introduced and this unit
  reuses unchanged; 14 one-sided controls splitting P, E, G and M into their query-side and
  document-side halves and crossing P with G; 8 conditions built on a generic analyzer that
  contains no possessive-specific rule; 17 single query-token deletions, each judged on the
  whole 4,937-passage ranking; 13 reduced-query probes; 6 per-side reachability probes; 5
  neighbourhood-overlap probes in both directions; 4 corpus-setting reconstructions including
  two statistics grafts; 26 index-side removal probes including two cumulative ladders, a
  complement control, a size-matched null control and a statistics-matched control; 4
  gold-targeted single-fact controls with a null control; 4 single-token surface repairs with a
  null control; 6 query-aware normalization conditions; and 8 oracle conditions. The battery was
  built on `tools/probe_kit.py`, the first case to use it.
- **The two most discriminative tokens of the question score nothing anywhere in the corpus.**
  The question writes the bridge entity as `McGraw's`, a token occurring in 0 of 4,937 passages,
  while the required passage's title and indexed body both write the bare form, which occurs in
  exactly 2 passages at an idf of 7.587919; and it writes the relation as `daughter?`, also 0
  occurrences, against 52 for `daughter` at an idf of 4.533214. Both are established in pit
  19x's strongest form rather than on gold ranks: deleting either token leaves the
  4,937-passage order 0 of 4937 changed with a maximum absolute score difference of 0.000000.
  The question's second constraint therefore participates in scoring only through `earl`, at
  df 35, and `character`, at df 120. This is the second unit in which pit 25i fires, the
  evidence collector's normalization ladder reporting `no corresponding form` for a token whose
  corpus form stands in the required passage's own title and body.
- **The same class of missing normalization produces a false negative on the query side for one
  required passage and on the document side for the other.** `Planet Terror` writes
  `Rose McGowan,` with a trailing comma, so the query's bare `mcgowan` scores 0.000000 against
  it and the single-token query `mcgowan` gives it 4441 / 0.000000. Corpus-wide the name is
  split into four tokens by punctuation, 5 passages writing the bare form, 7 writing `mcgowan,`,
  2 writing `mcgowan)` and 1 writing `mcgowan.`. D-030 recorded one unnormalized clitic
  producing a false negative and a false positive on the same side; this is the first unit in
  which one class of missing normalization disables a different required passage on each side.
- **Every repair is priced exactly, and each price is confirmed by an independent single-token
  query.** Query-side possessive normalization alone gives 2 / 37.789878 and 116 / 26.074919,
  worth 8.991778 points and 24 rank positions, and that increment is bit-identical to the score
  the single-token query `mcgraw` gives that passage, 2 / 8.991778. Query-side
  boundary-punctuation normalization alone gives 5 / 32.318370 and 134 / 26.074919, worth
  3.520270 points and 21 positions, bit-identical to the single-token query `daughter` at
  48 / 3.520270. Applied together they are additive at 1 / 41.310149 and 135 / 26.074919, the
  two increments summing to 12.512048. On the other hop, stripping the one comma inside
  `Planet Terror` and changing nothing else gives 27 / 28.798099 and 5 / 32.133137, worth
  6.058218 points and 110 rank positions.
- **A single non-oracle factor flips `any@5`, and no non-oracle condition flips `full@5`.**
  Query-side possessive normalization alone moves the bridge passage from 26 to 2. The best
  non-oracle conditions are a generic analyzer with scaffold removal at 2 / 22.769010 and
  13 / 12.716647 and the same with titles indexed at 1 / 25.259118 and 14 / 12.806919. This is
  the shape D-021 accepted for this primary, where the best non-oracle condition was 5 and 6,
  and not the shape of D-028 and D-030, where a non-oracle condition recovered both.
- **The gold-targeted repair and its deployable form differ by nine rank positions, and the
  difference is the finding.** Repairing only the required passage gives 5 / 32.133137;
  applying the identical repair to every corpus passage carrying the same mismatch gives
  11 / 31.534653; a query-aware normalization that normalizes a document token only when its
  normalized form is a query token gives 14 / 31.630834. Nothing deployable can give that
  passage its 6.058218 points without giving the same points to the fourteen other Rose McGowan
  works. This is recorded as a new pit rather than as a property of this unit.
- **The two sides of one preprocessing factor repair different required passages and damage the
  other, which is a third non-additive form.** Query-side P gives 5 / 32.318370 and
  134 / 26.074919, document-side P gives 38 / 28.345032 and 12 / 31.262470, and the two-sided
  cell gives 13 / 31.744210 and 14 / 31.262470. D-028 recorded an effect 100 percent on the
  document side, D-030 one 100 percent on the query side, and D-032 two positive one-sided
  effects cancelling when combined; here each side is strongly positive on a different hop.
  G is 100 percent query-side, `Gd` alone giving 28 / 28.758989 and 117 / 26.054015. E is inert
  on both hops in every combination. M is positive here at 5 / 32.824456 and 117 / 26.383585,
  against negative in D-028, positive in D-030 and strongly negative in D-032, and query-side M
  changes no gold score while moving both ranks, because it turns `starring` into `starr` and
  `features` into `featur`, neither of which is in the vocabulary. Eight of seventeen single
  factors carry opposite signs across the two hops.
- **The competitor family is not determinative at baseline and is determinative after the
  repair, which is the second new pit this unit records.** At baseline, dropping the 18 Rose or
  McGowan passages above the answer passage gives 15 / 28.805372 and 73 / 26.630444 while
  dropping the other 95 gives 10 / 29.270483 and 30 / 26.124391, so the complement beats the
  family. Under full normalization, dropping the 14 non-gold McGowan passages, a set definable
  from the query alone, gives 1 / 25.266887 and 3 / 15.335047; dropping all 41 Rose or McGowan
  passages gives 1 / 25.246782 and 2 / 18.024994; and the cumulative ladder crosses the cutoff
  at the eighth removal at 1 / 25.273160 and 5 / 13.543318. Ten of the 12 passages above the
  answer passage under that pipeline carry a McGowan form.
- **The two removal controls pit 19ad requires separate position from statistics.** A
  statistics-matched removal of 18 same-family passages that all rank below the answer passage
  gives 27 / 28.779802 and 90 / 26.622223, so 25 of the family probe's rank positions are idf
  drift rather than vacated positions; a size-matched null control of 18 top-ranked passages
  carrying no query name token gives 26 / 28.809076 and 115 / 26.068632. Under full
  normalization the size-matched null control gives 1 / 25.981076 and 12 / 12.825312 against
  the family probe's 3.
- **The pit 19u drop-everything cell has discriminative power on this backend and succeeds.**
  Dropping all 113 non-gold passages above the answer passage gives 1 / 29.285779 and
  2 / 26.680825, so no crowding reading is ruled out a priori, unlike D-030 where the same cell
  reached only 8 and 2.
- **The pit 19f and 19i test is weak in both directions, which is why no crowding name takes the
  primary.** Forward, the actress cue alone places 4 of 10 of its top ten inside the baseline
  top ten and 5 of 10 inside the top sixteen, and the whole actress facet places 4 and 6. In
  reverse, deleting the actress facet leaves 3 of 10 and deleting only the two name tokens
  leaves 5 of 10 and 8 of 16, so the observed neighbourhood does not collapse when the referent
  cue is removed and is not mainly the referent's product. The interrogative frame alone places
  3 of 10 and 4 of 16.
- **Per-side reachability holds in its strongest recorded form and each name demotes the
  other.** The bridge passage's own title as the whole query gives 1 / 30.558101 and sends the
  other required passage to 3444 / 2.565580; the answer passage's own title gives
  1 / 12.467933 and sends the other to 4437 / 0.000000. This is the D-025 and D-031 sign and it
  excludes the D-026 route. The answer passage is nevertheless unreachable from its own queried
  actress, `Rose McGowan` alone giving it 28 / 4.403606 and `film starring Rose McGowan` giving
  it 64 / 6.894036, behind the actress's own biography and several of her other films, which is
  pit 19n on a lexical backend.
- **Query splitting was measured although this is a bridge unit.** The top five of the
  actress-side query and the top five of the daughter-side query are disjoint from the gold
  set, so their union contains neither required passage.
- **Two single-fact controls under pit 19z.** Deleting only the sentence that links Dakota to
  Planet Terror from the bridge passage, leaving the rest verbatim, moves it from
  26 / 28.798100 to 34 / 28.265136, so that passage's position depends on whether it states the
  bridge fact at all by 8 rank positions and 0.532964 points. Deleting only `Rose McGowan, `
  from the answer passage's cast list moves it from 115 / 26.074919 to 1001 / 21.768235, so 886
  rank positions rest on the actress's name. Writing the missing conjunction into the answer
  passage gives 28 / 28.746748 and 3 / 37.216520 and recovers one side only.
- **The title-indexing condition is positive on one hop and negative on the other, and its gain
  contains none of the anchor.** Prefixing titles into the index gives 18 / 29.565356 and
  121 / 26.195125. Per-token decomposition shows the entire gain on the bridge passage is
  `earl` rising from 7.923587 to 8.548780 and `and` from 3.752318 to 3.850022, with the title's
  `mcgraw` contributing nothing, because the query token is `mcgraw's`. Both readings required
  by `unindexed_title_name_anchor` were tested: the semantic reading, the title as the whole
  query, gives 1 / 30.558101.
- **The oracle direction, recorded as diagnosis and never as a repair.** Appending the bridge
  title gives 1 / 59.356201 and 199 / 28.640499, the answer title 31 / 28.798100 and
  2 / 38.542852, both titles 1 / 59.356201 and 3 / 41.108432, the daughter's name
  4 / 33.947871 and 116 / 26.074919, her name in place of the description 1465 / 20.874513 and
  107 / 26.074919 because that rewrite also deletes `Earl`, her name inserted while keeping the
  description 4 / 34.429059 and 116 / 26.074919, and the actress who plays her 4 / 34.429059
  and 5 / 32.699209. The pit 24b degeneracy check records that `dakota` already occurs in the
  bridge passage's body.
- **Corpus setting, recorded as provenance under D-003 and pit 17.** Pooled gives `any@5` 0 and
  `full@5` 0; per-question gives `any@5` 1 and `full@5` 0, ranking the two required passages 4
  and 10, so this is the sixth unit in which the two corpus settings disagree on a metric. A
  rebuild on this question's ten passages reproduces the official window order item for item at
  4 / 7.173319 and 10 / 5.095757. Pit 19r holds again and the split is clean: restricting the
  pooled scores to the same ten gives 8 / 28.798100 and 10 / 26.074919; grafting the pooled
  `idf` and the pooled `avgdl` onto the same ten documents reproduces that restriction bit for
  bit; and grafting the pooled `idf` while keeping the per-question `avgdl` of 92.100000 gives
  8 / 28.915674 and 10 / 26.174250 in the same order, so `avgdl` carries none of the swing and
  `idf` carries all of it, the division of labour D-028 and D-032 recorded. The mechanism is
  that the ten-document index collapses `rose` from 4.820384 to 0.414338, `film` from 1.861154
  to 0.414338 and `character` from 3.688361 to 0.367725 while `earl` keeps 1.845827, so the
  small index destroys exactly the vocabulary that crowds the bridge passage and preserves the
  one token that lifts it, which is the mirror image of the D-032 fingerprint. The
  new-competitor path exists and is insufficient, 18 of the 25 passages above the bridge
  passage and 105 of the 113 above the answer passage being pooling-introduced while dropping
  only those gives 8 / 29.265784 and 12 / 26.384932, which is not the per-question result. The
  annotator-supplied path is weak, 5 of this question's own 10 passages being Rose McGowan
  documents.
- **No substitute and no complete non-gold answer.** A full-corpus substring scan finds
  `Planet Terror` in exactly 2 passages, which are the two required ones, `Marley Shelton` in
  the same 2, `Grindhouse` in the same 2 and `Death Proof` in 1, the answer passage. `McGraw`
  occurs in 3 passages, the two others being a 1987 CBS series about an unrelated Harry McGraw
  and a music festival. `Dakota` occurs in 11 passages, of which only the bridge passage
  concerns this Dakota.
- **Comparison retriever.** Dense places `Earl and Edgar McGraw` at 1 / 0.534788 and
  `Planet Terror` at 144 / 0.292530 over the complete corpus, its pooled top ten matching the
  official CSV item for item, so Dense also fails `full@5` and also does not retrieve the answer
  passage. This establishes only that the bridge passage is reachable under a different scorer;
  the two backends' score magnitudes are not comparable and nothing here explains why BM25
  fails.
- **Tie-break.** Prefer `minimal_preprocessing_score_distortion` over
  `cross_passage_conjunction_unresolved`. Both meet their rules, so under pit 13 that does not
  decide it. All three legs of the D-022 and D-024 evidence set hold for the conjunction
  reading, with per-side reachability in its strongest recorded form, which makes this the
  first BM25 bridge unit to satisfy every positive leg and still not adopt the name. It is
  refused on the D-028 route of pit 19s: a condition that supplies no intermediate fact and
  performs no cross-passage reasoning, generic normalization plus an index-side removal of the
  14 non-gold McGowan passages, a set definable from the query without knowing which passages
  are required, places both inside the cutoff at 1 / 25.266887 and 3 / 15.335047. In D-022,
  D-024, D-025 and D-031 no such condition existed. The preprocessing reading wins on the
  playbook's Step 8 ordering as well, a mechanism supported directly by the implementation and
  by exact score decomposition outranking a code that describes the shape of the ranking, which
  is the ruling D-021 made on the same pair of readings. A second ground against the conjunction
  reading is recorded but deliberately not used to carry the decision, because it is an
  interpretation rather than a measurement: the bridge passage names the answer film outright
  while satisfying only one of the question's two constraints, so whether the exclusion's first
  clause fires on a passage that supplies the answer string without verifying every constraint
  is registered as a vocabulary-audit question. D-029, the only prior use of that clause, had an
  answer passage satisfying all three of its question's facets.
- **Why the three provisional names are deleted rather than registered.**
  `partial_match_constraint_omission` names the shape of the ranking rather than a mechanism,
  which pit 17 and D-010's comment on a resulting ranking pattern warn against, and it is
  dissolved by the adopted primary, since one query-side token normalization restores the
  omitted constraint and moves the bridge passage to 2. It remains the provisional primary of
  queue item 26 and this decision does not touch that row.
  `cross_entity_relation_unresolved` is deleted as a duplicate of
  `cross_passage_conjunction_unresolved`, on the test D-031 used to delete
  `subject_associate_crowding`, and the name it duplicates is itself not adopted here.
  `answer_entity_missing_both_methods` is deleted on two independent grounds: it states gold
  missingness, which pit 17 and D-003 forbid as a causal category, and it is factually wrong,
  the answer passage being present at 115 of 4,937 under BM25 and 144 of 4,937 under Dense.
- **Why the other candidates are not adopted.** `unindexed_title_name_anchor` fails its second
  inclusion condition and its first exclusion in a configuration no earlier unit produced: the
  semantic reading is maximal at 1 / 30.558101 and the indexing reading is positive on that hop
  at 18 / 29.565356, yet the title does not contain the query's anchor in a form the implemented
  tokenizer matches, tokenizing to `earl`, `and`, `edgar` and `mcgraw` against the query's
  `mcgraw's`, and the indexed body writes the same unmatchable form.
  `description_only_bridge_entity` fails its inclusion rule directly, the required passage
  having a unique name anchor at df 2 and ranking 1 / 16.915365 under the query `Earl McGraw`,
  so it need not be reached through a descriptive clue; this is nevertheless the seventh failing
  application of the single-factor oracle-name test, appending `Dakota` giving 4 / 33.947871 and
  116 / 26.074919 and naming her in place while keeping the description giving 4 / 34.429059 and
  116 / 26.074919. `related_name_document_crowding` is routed to a secondary by its own first
  exclusion, a more specific implementation-supported name-form mismatch explaining the primary
  failure at a measured 6.058218 points and 110 rank positions.
  `repeated_function_word_amplification` is withheld on the judgment its own exclusion shares
  with `generic_query_scaffold_score_inflation`: deleting the second and third occurrences of
  the only repeated token gives 18 / 21.800059 and 118 / 18.393906, worth 8 rank positions on
  one hop and minus 3 on the other, while deleting the four non-repeated scaffold tokens instead
  gives 17 / 21.284848 and 77 / 18.415555, worth 9 and 38, so the repeated occurrences are not
  the material mechanism and the scaffold entry's corresponding exclusion does not fire.
  `proper_name_homonym_collision` fails the D-018 materiality standard exactly as in D-029, the
  one non-gold passage sharing the surname ranking 69 under the possessive normalization with
  its removal leaving the bridge passage at 2, and ranking 13 under the normalized pipeline with
  its removal moving the answer passage by one position, from 14 to 13.
  `gold_chain_substitutability` and `gold_chain_not_unique` are inapplicable on the substring
  scan. `compound_two_sided_crowding` is excluded under pit 19h, one family sitting above both
  required passages and the second constraint having no competitor family of its own.
  `peripheral_passage_content_dilution` is inapplicable, its first inclusion condition requiring
  a verified mean-pooled encoder, so its gate was not applied and no length-matched control was
  run.
- **`cutoff_sensitive_near_miss` is withheld, and the never-decided band narrows from above for
  the first time.** The nearer required passage sits 9.431 percent below the rank-5 score, inside
  the band this project had measured but never decided on, and the other sits 17.995 percent
  below it, inside the excluded band. The counter-evidence is weak in the D-029, D-030 and D-031
  sense rather than strong in the D-032 sense: the cumulative removal ladder gives 25 after one
  removal, 23 after three, 21 after five, 16 after ten, 11 after fifteen, 7 after twenty and 2
  after twenty-five, and no cliff can be cited. Withholding moves the excluded band's lower edge
  from 12.518 percent in D-028 to 9.431 percent in D-033 and narrows the never-decided band to
  5.464 to 9.431 percent. No rule text changes and setting an explicit threshold remains a
  vocabulary-audit matter. The no-substitute condition would have been met, which is why the
  decision rests on the gap and the ladder.
- **Not-run cells and attribution boundary.** Not run: splitting query side from document side
  again inside each of the 64 factorial cells, because every factor's one-sided split was
  measured on its own and the tie-break turns on `Gq` against `Pd`, both measured; a Dense
  factorial, because the unit key includes the retriever and Dense enters only as a reachability
  comparison under pit 16; lemmatization, phrase n-grams and any sweep of `k1`, `b` or
  `epsilon`, because they introduce mechanisms outside this tie-break; crossings of the oracle
  conditions with preprocessing, because oracle conditions are diagnostic only and the seven
  already run locate reachability; the `peripheral_passage_content_dilution` ablation and
  length-matched control curve, because the gate's first inclusion condition is scoped to a
  mean-pooled encoder; and the semantic-neighbourhood probes of
  `question_frame_semantic_crowding`, whose lexical counterpart
  `generic_term_lexical_crowding` was tested instead in both directions. Attribution boundary:
  every figure is specific to this unit, this 4,937-passage pooled corpus and run
  `2026-07-17_a`, and no factor was measured on the other 499 questions, so nothing here
  supports a claim about the run's aggregate `Any@5`. The four gold-targeted index-side
  conditions are third-class interventions under pit 19d, not deployable repairs. The 26 removal
  probes exist only to test whether a family is outcome-determinative and are not repairs
  either; under pit 19ad their gains mix vacated positions with idf drift, which is why each is
  reported with its controls. The eight oracle conditions are barred from being read as fixes
  under red line 15. The Dense figures establish reachability under a different scorer and
  nothing about BM25's cause, and the two backends' magnitudes are not comparable. The statement
  that the possessive clitic is worth 8.991778 points is exact for this passage under this
  index and is not a general claim about possessives.
- **Evidence layers.** Observed: the reconstruction, the document frequencies, the 201
  conditions, the whole-ranking deletion diffs and the Dense comparison. Verified implementation
  fact: the analyzer and scorer contract above, the per-token reconciliation, the exclusion of
  titles from the index, and that a BM25 per-question ranking is not the pooled ranking
  restricted to those ten documents. Supported interpretation: that the first-order determinant
  of both required passages' positions is unnormalized surface form, and that what survives
  every normalization is a name-linked family plus a constraint stated only in the other
  required passage. Speculation, explicitly marked: that a production analyzer would improve
  this run's aggregate metrics; that HotpotQA's bridge templates systematically produce
  possessive anchors, for which this pass has two samples; and that the bridge passage supplies
  a complete answer in the sense of the conjunction entry's first exclusion, which is a reading
  of the question's constraints rather than a measurement.
- **Bookkeeping corrections landed with this decision.** Three corrections settled on
  2026-08-05 and deliberately deferred to this landing, because the log is append-only and
  changing the registry alone would have left the two inconsistent for a whole session. First,
  `unindexed_title_name_anchor`'s inert-or-negative list gains `D-029`, which the list omitted
  while its own count was right. Second, `peripheral_passage_content_dilution`'s running tally
  is replaced by a member enumeration, six applications by D-023, D-025, D-026, D-027, D-029 and
  D-031, four passes by D-023, D-026, D-027 and D-029, and two documented rejections by D-025
  and D-031; the tally slipped at D-027, which omitted D-026, and D-029 and D-031 inherited the
  offset, so each sentence was internally consistent and the chain was not. The affected
  sentences in this append-only log stay as written and the enumeration governs. That entry's
  `Decision source` line also gains D-025. Third, the word `untested` is replaced by
  `never decided on` in the D-028 and D-032 paragraphs of `cutoff_sensitive_near_miss`, because
  D-024 measured 5.698 percent inside both bands without deciding on it; neither entry's
  substantive conclusion changes. A vocabulary-audit question is registered and nothing is
  re-judged: D-024's 5.698 percent sits above the current accepted upper edge and was not
  adopted, which looks like a reverse precedent, but its rejection ground was superseded by the
  split rule at D-025, so the precedent set mixes two rules.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. The primary inventory is unchanged at
  **26 distinct names**. `minimal_preprocessing_score_distortion` is item 9 and gains its eighth
  unit, which widens a primary already flagged as possibly too broad; it adds no seventh
  sub-mechanism, the possessive clitic being D-030's sixth and boundary punctuation the oldest,
  but it does add a new shape of the same sub-mechanism, one class of missing normalization
  disabling a different required passage on each side. Folding that in rather than coining a
  name follows D-030's reasoning and not D-028's, since which side a normalization fails on is
  not a different level of decision. The departing name
  `partial_match_constraint_omission` is item 15 and keeps a current v2 primary row, queue item
  26, so unlike the departing names of D-021, D-022, D-023, D-027, D-028 and D-029 it needs no
  historical-preservation treatment. `cross_entity_relation_unresolved`, item 3 of the primary
  inventory and item 9 of the secondary union, loses its last v2 occurrence and stays in both
  unions as a first-pass name in `case_memos_v1.csv`, the treatment D-029 gave it when it lost
  its last v2 primary row.
- **Inventory effect.** The primary inventory is unchanged at **26 distinct names** and the
  secondary-name union is unchanged at **50 distinct names**; all four adopted secondaries
  already occur in the column. `case_memos_v2.csv` now holds **84 secondary assignments over 33
  distinct names**, up from 82 and down from 34: this row went from two descriptors to four, and
  `cross_entity_relation_unresolved` was unique to this row. The distinct `primary_open_code`
  count in v2 is unchanged at 14, because `minimal_preprocessing_score_distortion` was already
  present and `partial_match_constraint_omission` survives on another row.
  `case_memos_v1.csv` is unchanged. The registry stays at **26 adopted descriptors** because no
  new descriptor is registered; four existing entries gain this affected unit and D-033 as a
  decision source, and six gain D-033 as a decision source recording a non-adoption. `review_status`
  counts are now 24 `jointly_reviewed` and 6 `needs_joint_review`, and twenty-four rows carry a
  populated `candidate_category`. Validation progress after D-033 is **20 of 26 validated, 6
  remaining**, superseding the 19-of-26 figure recorded by D-032. Four vocabulary-audit items
  are registered and settled by none of this: whether
  `cross_passage_conjunction_unresolved`'s first exclusion fires on a passage that supplies the
  answer string while verifying only one of the question's constraints; whether
  `unindexed_title_name_anchor` should still be refused when its semantic reading is maximal and
  its indexing reading positive, on the form of the anchor alone; whether the never-decided band
  between 5.464 and 9.431 percent should be closed by an explicit threshold; and whether
  `minimal_preprocessing_score_distortion`, now at eight units and six sub-mechanisms, should be
  narrowed.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5abcc96c5542996583600492.md`.
## D-034 - Reclassify the Hlin / Norse mythology BM25 unit as minimal-preprocessing score distortion

- **Date:** 2026-08-06
- **Status:** active
- **Decision:** For `5adc8977554299438c868de2|bm25`, replace the provisional primary
  `question_wording_ambiguity` with `minimal_preprocessing_score_distortion`. Adopt
  `surface_form_tokenization_mismatch`, `generic_term_lexical_crowding`,
  `repeated_function_word_amplification`, `gold_chain_substitutability` and
  `description_only_bridge_entity` as secondaries. Use
  `cross_passage_conjunction_unresolved` as the closest competitor. Delete the provisional
  names `question_wording_ambiguity`, `competing_valid_entity_cues` and
  `general_answer_passage_missing` rather than registering any of them. Register no new
  descriptor. Do not adopt `cross_passage_conjunction_unresolved`,
  `cutoff_sensitive_near_miss`, `generic_query_scaffold_score_inflation`,
  `related_name_document_crowding`, `same_topic_passage_distractor`, `gold_chain_not_unique`
  or `compound_two_sided_crowding`. `peripheral_passage_content_dilution` is inapplicable on
  this backend and its gate was not applied.
- **Affected unit:** `5adc8977554299438c868de2|bm25`.
- **Question:** `What does the goddess associated with the goddess frigg  consists of what
  tales?` This is a bridge unit, and the question is malformed: it carries two interrogative
  words, an auxiliary that disagrees with its verb, and a double space. `Hlin` states that
  Hlin is a goddess associated with the goddess Frigg and places her in Norse mythology.
  `Norse mythology` states that Norse mythology consists of tales of various deities, beings
  and heroes. The answer is that body of tales. The question names neither required entity;
  its only proper noun is Frigg, who is neither of them.
- **Verified implementation:** only paragraph text is indexed and titles are excluded;
  `text.lower().split()` is the whole analyzer, with no punctuation handling, stop-word
  removal, stemming, Unicode normalization or phrase matching; `rank-bm25==0.2.2`
  `BM25Okapi` with the library defaults `k1=1.5`, `b=0.75` and `epsilon=0.25`; every
  occurrence of a repeated query token is scored separately, and this question repeats
  `what`, `the` and `goddess`; the pooled corpus holds 4,937 passages at an average document
  length of 90.884950. Because the analyzer is `lower().split()`, the double space is
  provably inert before any measurement, and the measurement confirms it.
- **Exact reconstruction:** rebuilding the index over the read-only 4,937-passage pooled
  corpus reproduces all 50 stored top-50 titles in order, 0 of 50 mismatched, with a maximum
  absolute score error of 0.000e+00, and every per-token decomposition reconciles against
  `get_scores` within 1.421e-14, so strong causal claims are supported. Complete-corpus ranks
  are 7 / 33.382868 and 72 / 17.155303. Pit 7 applies: the stored window records the answer
  passage as `not_in_top50`, but it sits at 72 of 4,937.
- **Diagnostic scale:** 201 distinct labelled conditions on the same unchanged candidate
  set, 18 of them deliberately repeated under a second label with every repeat reproducing
  its original bit for bit, for 219 recorded rows in `derived/case_results`, of which 3 are
  `not_run` cells with reasons. The reproduction script carries 221 assertions and all pass.
- **The question's final token scores nothing anywhere in the corpus.** `tales?` occurs in
  0 of 4,937 passages and contributes exactly 0.000000 to every one of them. Deleting it
  leaves the whole 4,937-passage order 0 of 4937 changed at a maximum absolute score
  difference of 0.000000, which is pit 19x's strongest form. This is the seventh such
  instance after D-019, D-021, D-028, D-030, D-032 and D-033.
- **The bridge passage's own copy of the queried name is unmatchable, and the mismatch is on
  the document side.** The question's only proper noun is `frigg`, at an idf of 6.631596 and
  a document frequency of 6. The bridge passage writes it only as `Frigg.`, twice, so it
  takes exactly 0.000000 from that token while four of the six passages above it take
  4.748132, 6.141557, 6.660782 and 6.795970 from it. The token is a net liability at
  baseline: deleting `frigg` from the question moves the bridge passage from 7 to 4.
- **The same class of missing normalization disables one required passage on the query side
  and the other on the document side.** This is the second unit with that shape, after
  D-033, and the two are not the same case: there both sides bore on surface forms of the
  same name, here the query-side failure is on the answer passage's only content token and
  the document-side failure is on the bridge passage's only name anchor.
- **Every repair is priced exactly, and each price is confirmed by an independent
  single-token query.** Normalizing `tales?` on the query side alone moves the answer
  passage from 72 / 17.155303 to 15 / 24.166533, worth 7.011230 points, which is exactly the
  score the single-token query `tales` gives it at 4 / 7.011230, the two agreeing to the last
  digit. Stripping the two periods inside the bridge passage alone moves it from
  7 / 33.382868 to 1 / 43.747308, worth 10.364441 points and 6 rank positions, matching the
  10.364435 that the single-token query `frigg` gives it on the repaired index to 6e-06;
  repairing only the first period gives 2 / 40.997962.
- **Unlike D-033, the deployable form of the document-side repair costs nothing.** The same
  repair applied to every passage carrying the string touches only 2 passages, the bridge
  gold and `Frigg gas field`, and gives 1 / 43.747301 against the gold-targeted
  1 / 43.747308. Pit 19ae is therefore satisfied with a null answer, which is itself the
  finding: where D-033 lost 9 rank positions between the two forms, here there is nothing to
  lose because the unnormalized form is nearly unique to the required passage. A full
  generic analyzer applied on both sides gives 2 / 43.012398 and 18 / 23.252024.
- **A single non-oracle factor flips `any@5`, and nothing flips `full@5`.** Both-sided
  boundary-punctuation normalization alone gives 1 / 43.328448 and 18 / 23.247555. No
  condition of any kind places the answer passage inside the cutoff without an index-side
  removal, including the oracle condition that appends both gold titles at 1 / 57.097842 and
  8 / 39.569089.
- **The two sides of one preprocessing factor act on different required passages and
  conflict on one of them, which is a fourth non-additive form.** Query-side normalization
  alone is exactly inert on the bridge passage at 7 / 33.382868 and moves the answer passage
  to 15 / 24.166533; document-side normalization alone moves the bridge passage to
  1 / 43.328448 and moves the answer passage the wrong way, to 79 / 16.935628; both sides
  together give 1 / 43.328448 and 18 / 23.247555, which is worse on the answer passage than
  the query side alone. This is neither D-028's document-side-only form, nor D-030's
  query-side-only form, nor D-032's two-positives-cancelling form, nor D-033's
  each-side-saves-one-and-breaks-the-other form. The text-level and index-level versions of
  the factor agree on 0 of 4937 positions at a maximum absolute delta of 0.000e+00.
- **The wording defect named by the provisional primary is exactly inert on one required
  passage in both preprocessing states.** The A x B x C repair factorial, where A restores
  subject-verb agreement, B deletes the redundant leading `What does` and C collapses the
  double space, leaves the bridge passage at exactly 7 / 33.382868 in all eight cells at
  baseline preprocessing and at exactly 1 / 43.328448 in all eight cells under both-sided
  normalization. On the answer passage the grammatically correct repair is the worst cell,
  545 / 12.232081 and 60 / 18.333932, because the corpus writes `consists` in 60 passages
  against `consist` in 9 and that token is the answer passage's only content match; the only
  positive wording factor is deleting the interrogative frame, at 25 / 17.155303 and
  12 / 23.247555. Pit 19k is why this is known: the single fluent-repair cell alone would
  have read as materially positive at 5 / 33.382868 and 20 / 15.165951, and that cell changes
  four things at once, including creating the dead token `of?`.
- **What moves the answer passage is a content addition, not a wording repair.** Adding the
  generic category word `mythology` gives 7 / 37.292516 and 8 / 35.734170, and under
  both-sided normalization 1 / 53.381039 and 10 / 36.477795. This is the D-031 `abbey` shape
  and is not deployable under pit 19ab: the category is stated only in the other gold.
- **The pit 19u drop-everything cell reverses its verdict with the baseline it is run
  against, which extends pit 19af.** At baseline, dropping every one of the 70 non-gold
  passages above the answer passage still leaves it at 14 / 17.293278, which on D-030's
  reading rules out any crowding descriptor as primary. Under both-sided normalization only
  16 non-gold sit above it, and dropping those gives 1 / 52.744000 and 2 / 23.271751. D-033
  established that a family probe's verdict depends on which baseline it runs on; this unit
  shows the same is true of pit 19u's own cell, which is recorded as a new pit.
- **The removal controls separate position from statistics, and here the gain is entirely
  positional.** At baseline, dropping the five Frigg-naming passages above the bridge passage
  gives 2 / 35.283477, the complement control 6 / 33.699777, the size-matched null control
  7 / 33.431527, and the statistics-matched control 2 / 33.382868 with the score unchanged to
  the last digit. The broad-category family behaves the same way: dropping the 10 non-gold
  passages carrying `goddess` above the answer passage gives 1 / 39.993981 with a
  statistics-matched control at 1 / 33.382868, again with the bridge score unchanged.
- **The pit 19f and 19i test is decisive in both directions and identifies the category
  token, not the name.** Forward, the referent cue alone places 5, 6, 9 and 10 of its top ten
  inside the baseline top 5, 6, 10 and 16; `goddess` alone places 5, 6, 8 and 10; `frigg`
  alone only 3, 4, 6 and 6; the interrogative frame alone 0, 0, 1 and 3. In reverse, deleting
  both occurrences of `goddess` leaves 0, 0, 1 and 5 while deleting `frigg` leaves the
  neighbourhood untouched at 5, 6, 8 and 10.
- **Which half of the scaffold is material is settled by direct experiment, and the answer
  is the opposite of D-033's.** Deleting only the second occurrence of each repeated scaffold
  token gives 7 / 29.473219 and 37 / 13.077942, worth 0 rank positions on one required
  passage and 35 on the other; deleting the three non-repeated scaffold tokens instead gives
  6 / 32.670088 and 77 / 13.077942, worth 1 and minus 5. The two halves remove the identical
  4.077360 points from the answer passage, because `the` and `of` share an idf of 1.917315,
  so the whole difference is what happens to the competitors. `Treehouse (game)` at
  9 / 27.610510 is a board-game description with no content relation to the question and
  takes 100.0 percent of its score from scaffold, 33.0 percent of it from second occurrences
  and 34.0 percent from non-repeated tokens.
- **Per-side reachability holds at rank 1 from each gold's own title.** `Hlin` gives
  1 / 14.707262 and 4528 / 0.000000; `Norse mythology` gives 6 / 9.007713 and 1 / 22.413786.
  The single-factor oracle-name test introduced by D-020 therefore fails here, which is
  the eighth failing application: appending the bridge title recovers only that side at
  1 / 48.090129 and 72 / 17.155303, appending the answer title only the other at
  4 / 42.390581 and 8 / 39.569089, and naming either in place likewise recovers one side.
  The D-024 precondition was checked before any oracle verdict was read: `hlín` occurs in
  exactly 1 of 4,937 passages, itself, and the answer title's tokens occur in the answer
  passage.
- **The title-indexing condition is inert to negative.** T alone gives 8 / 33.521272 and
  77 / 17.172945, and 1 / 43.510531 and 19 / 23.277873 combined with boundary normalization,
  against 1 / 43.328448 and 18 / 23.247555 without it. Neither gold's title is a token of the
  question, so pit 19q's trigger does not fire; it was measured anyway.
- **Two single-fact controls under pit 19z.** Removing the clause that states the Frigg
  association from the bridge passage, leaving the rest of its text word for word, takes it
  from 7 / 33.382868 to 4198 / 7.566065, so that one clause carries the passage entirely.
  Removing the `consists of tales` sentence from the answer passage takes it from
  72 / 17.155303 to 388 / 12.502695. Null controls that re-index each untouched body
  reproduce the baseline exactly.
- **The oracle direction, recorded as diagnosis and never as a repair.** Appending the bridge
  title gives 1 / 48.090129 and 72 / 17.155303; appending the answer title gives 4 / 42.390581
  and 8 / 39.569089; appending both gives 1 / 57.097842 and 8 / 39.569089; appending both on
  top of the normalized pipeline gives 1 / 64.843767 and 8 / 31.344743. No oracle condition
  places both required passages inside the cutoff.
- **Corpus setting, recorded as provenance under D-003 and pit 17.** Pooled `any@5` and
  `full@5` are 0 and 0 at 7 and 72; per-question they are 1 and 0 at 10 and 1, so the two
  settings disagree on `any@5` and the passage that wins in the small index is the other
  gold. This is the seventh unit in which the two corpus settings disagree on a metric,
  after D-022, D-023, D-024, D-025, D-026 and D-033. All four cells of pit 19r were run: the index rebuilt on the item's ten paragraphs
  reproduces the stored per-question order title by title at 10 / 2.811824 and 1 / 4.597127;
  the pooled scores restricted to the same ten give 7 and 10; grafting pooled `idf` and
  pooled `avgdl` back reproduces that at 7 / 33.382868 and 10 / 17.155303; and grafting
  pooled `idf` alone, keeping the per-question `avgdl` of 100.300000, gives 7 / 34.136404 and
  10 / 17.459327 in the same title order. **So `avgdl` carries none of the flip and `idf`
  carries all of it**, as in D-028, D-032 and D-033. The mechanism is that the ten-document
  index collapses `frigg`, `goddess`, `of` and `the` to the epsilon floor of 0.380244 and
  `associated`, `does`, `what` and `with` to 0.000000 while keeping `consists` at 1.845827,
  and `consists` is exactly the token the answer passage has and the bridge passage lacks.
  Of the three paths, new competitors is impossible on the bridge passage, all 6 above it
  coming from this item's own window and 0 from pooling, and fails on the answer passage,
  62 of the 70 above it being pooling-introduced while dropping exactly those gives
  21 / 17.298833 rather than 1; the annotator-supplied path holds strongly, 7 of the item's
  8 distractors being Frigg-related Norse mythology entries occupying pooled ranks 1 to 6
  and 8.
- **The answer fact has no substitute; the bridge fact has four, two of them inside the
  cutoff.** A full-corpus substring scan finds exactly one passage stating what Norse
  mythology consists of, the answer gold itself, and exactly one containing the answer string
  `various deities`, so there is no complete non-gold answer and no complete alternative
  chain. Six non-gold passages mechanically name Frigg, `goddess` and Norse mythology; two
  fail on read text, `Fensalir` being a location rather than a goddess and
  `Nanna (Norse deity)` being associated with the god Baldr; the remaining four supply the
  same intermediate fact under the evidentiary standard the gold itself uses, `Eir` at 1,
  `Sága and Sökkvabekkr` at 4, `Gná and Hófvarpnir` at 6 and `Fulla` at 10. The standard is
  identical because the bridge gold's own claim is of the same kind, `Hlín has been theorized
  as possibly another name for Frigg` against `Eir has been theorized as a form of the goddess
  Frigg`.
- **Comparison retriever.** Dense places the two required passages at 1 and 8 pooled and at
  1 and 6 per-question. Under pit 16 that shows only that both are reachable on another
  backend; the two scales are not comparable, the Dense run of this `example_id` is not an
  analytical unit, and no Dense figure is used as a cause of the BM25 outcome. Its cosine
  scores are deliberately not carried into any shared file.
- **Tie-break.** Under pit 13, meeting an inclusion rule does not decide the tie.
  `cross_passage_conjunction_unresolved` is the closest competitor and two of the three legs
  of the D-022 and D-024 evidence set hold: the matched query-token sets are disjoint in
  content, the bridge passage matching `associated`, `goddess`, `the` and `with` and the
  answer passage `consists`, `of` and `the`, meeting only in the scaffold token `the`; and
  per-side reachability holds at rank 1 from each gold's own title. The opposite-sign leg is
  the weakest recorded in any application of this name, 3 of 22, against 4 of 19 in D-026
  which cited that weakness as one of three grounds for rejection, 8 of 22 in D-031 which
  recorded it as not carrying the decision, 8 of 17 in D-033, 10 of 19 in D-024 and 10 of 20
  in D-025. It is refused on the D-028 route of pit 19s: both-sided boundary normalization
  plus scaffold removal plus an index-side removal of the 7 non-gold passages naming Frigg, a
  set definable from the query without knowing which passages are gold, gives 1 / 40.778471
  and 5 / 11.221051; widening the family to the 10 non-gold passages carrying `goddess` gives
  1 / 44.308999 and 2 / 11.219467; the size-matched null control gives 1 / 35.981180 and
  9 / 11.452994, the complement control 1 / 35.931195 and 9 / 11.223968, and the cumulative
  ladder crosses the cutoff at the seventh removal. None of these supplies an intermediate
  fact or performs cross-passage reasoning, so the inability to carry a fact between passages
  cannot be the binding constraint. The three components are co-necessary: the removal
  without the normalization gives 2 / 27.925263 and 28 / 4.921043, the normalization without
  scaffold removal gives 1 / 49.162696 and 11 / 23.240625, and the normalization and scaffold
  removal without the removal give 1 / 34.943086 and 12 / 11.225549.
- **Why the three provisional names are deleted rather than registered.**
  `question_wording_ambiguity` names a defect of the question rather than a retrieval
  mechanism, which is what pit 17 warns against, and the sixteen-cell factorial shows its
  effect on the bridge passage is exactly zero in both preprocessing states while its one
  grammatically correct component is the worst cell on the other passage. Under the
  playbook's Step 8 ordering, a mechanism supported directly by the implementation and by
  score decomposition outranks a code that names a property of the question.
  `competing_valid_entity_cues` is deleted as a duplicate, on the test D-031 used to delete
  `subject_associate_crowding` and D-033 used to delete `cross_entity_relation_unresolved`:
  its crowding half is `generic_term_lexical_crowding`, its alternative-referent half is
  `gold_chain_substitutability`, and it is not outcome-determinative, since the bridge
  passage ranks 1 above every one of those valid competitors once the document-side surface
  form is repaired. `general_answer_passage_missing` is deleted on two independent grounds:
  it states gold missingness, which pit 17 and D-003 forbid as a causal category, and it is
  factually wrong, the answer passage being present at 72 of 4,937 under BM25 and 8 under
  Dense. This is the second consecutive decision to delete all three of a row's provisional
  names, after D-033, and the sixth consecutive decision to register no new descriptor.
- **Why the other candidates are not adopted.** `related_name_document_crowding` is refused
  because the family is not name-driven, deleting `frigg` from the question leaving the
  neighbourhood at 5, 6, 8 and 10 of the baseline top 5, 6, 10 and 16 while deleting
  `goddess` collapses it to 0, 0, 1 and 5. `same_topic_passage_distractor` is withheld as a
  duplicate description of the same family. `gold_chain_not_unique` is inapplicable because
  the answer fact occurs in exactly one passage, so no complete alternative chain exists.
  `compound_two_sided_crowding` is excluded under pit 19h, one family sitting above both
  required passages. `peripheral_passage_content_dilution` is inapplicable on a lexical
  backend, its first inclusion condition requiring a verified mean-pooled encoder, so its
  gate was not applied and no length-matched control was run.
- **`generic_query_scaffold_score_inflation` is withheld, and the boundary it shares with
  `repeated_function_word_amplification` is settled the other way from D-033.** All three of
  its inclusion conditions hold, and `Treehouse (game)` at 9 / 27.610510 is as clean an
  instance as this project has recorded, a passage with no content relation to the question
  taking 100.0 percent of its score from scaffold. Its second exclusion nevertheless fires
  for the first time in this pass: the repeated occurrences are the material mechanism, worth
  35 rank positions on the answer passage against minus 5 for the non-repeated tokens, so the
  unit belongs to the sibling entry. D-033 ran the identical experiment and the exclusion did
  not fire there, so the two units are the boundary samples that pair needs.
- **`cutoff_sensitive_near_miss` is withheld inside the accepted band, on the no-substitute
  condition and not on the gap.** The bridge passage sits 1.261380 points, or 3.641 percent,
  below the rank-5 score of 34.644248, which lies inside the accepted band of 1.156 to 5.464
  percent, and the counter-evidence would support adoption, a cumulative removal ladder
  giving 6, 5, 4, 3, 2 and 1 so that dropping only two competitors already gives
  5 / 34.046411 and flips `any@5`; there is no cliff, the successive differences from rank 1
  to rank 10 being 1.492919, 3.224170, 0.967934, 1.461482, 0.480356, 0.781024, 2.525275,
  3.247083 and 1.188520. What fails is the no-substitute condition every adoption since D-022
  has checked and on which D-015 removed this descriptor: the near passage has
  evidence-bearing substitutes inside the cutoff, at 1 and 4. **Because the ground is
  substitutability and not the score gap, no band edge moves**: the accepted band stays 1.156
  to 5.464 percent, the excluded band stays 9.431 to 52.794 percent, and the never-decided
  band stays 5.464 to 9.431 percent. Whether a non-gap withholding should be allowed to leave
  the bands untouched is registered as a vocabulary-audit question. The other required passage
  is at 50.482 percent, inside the excluded band, so the D-025 boundary would have applied in
  any case.
- **Not-run cells and attribution boundary.** The possessive-clitic factor of D-030 was not
  run because no query token ends in a clitic, and pit 25i's manual check of the bare stems
  confirms the normalization ladder has nothing to miss here. The dilution gate and its
  length-matched control curve were not run because the descriptor is inapplicable on a
  lexical backend. No Dense factorial was run because the unit key names bm25. Query
  splitting was not run because pit 19o requires it on comparison units and this is a bridge
  unit. The bridge passage's failure is attributed in full to the document-side surface form,
  priced three ways that agree. The answer passage's failure is attributed to no single
  factor: the query-side dead token is worth 57 rank positions, the repeated function words
  35, and the query-definable family removal 7 more once the preprocessing is repaired, and
  the three are co-necessary. This unit's `any@5` failure is attributed and its `full@5`
  failure is not.
- **Evidence layers.** Observed: the complete-corpus ranks and scores, the 201 conditions,
  the read text of every passage above the bridge passage and of the answer passage's
  neighbourhood. Verified implementation: the analyzer, the scoring library and its defaults,
  the per-occurrence accumulation, the document frequencies and idf values quoted above, and
  the provable inertness of the double space. Supported interpretation: the `any@5` failure
  is explained by a deployable surface-form defect, and the `full@5` failure by a second
  defect of the same class combined with the question never naming the intermediate entity.
  Speculation, recorded and not used: that the malformed question is an artifact of
  generation or transcription, and that the multiplicity of Frigg-associated goddesses
  reflects how the item's distractors were constructed.
- **Taxonomy effect:** `minimal_preprocessing_score_distortion` is now the validated primary
  of nine units and remains flagged as possibly too broad. It gains no seventh sub-mechanism
  here, boundary punctuation being the oldest of the six, but it gains the second instance of
  D-033's two-sided shape and the first instance in which the deployable form of a
  document-side repair costs nothing. `question_wording_ambiguity` leaves the current v2
  primary column entirely; it is item 19 of the primary inventory, D-026 recorded that it
  kept exactly this row, and it now stays in the union as a first-pass name in
  `case_memos_v1.csv`, where it is the primary of 2 rows, the treatment D-021 gave
  `weak_lexical_name_anchor` and D-026 gave `adjacent_event_crowding`.
  `competing_valid_entity_cues`, item 8 of the secondary union, and
  `general_answer_passage_missing`, item 17, likewise lose their only v2 occurrence and stay
  in the union as first-pass names, each occurring once as a secondary in
  `case_memos_v1.csv`.
- **Inventory effect.** The primary inventory is unchanged at **26 distinct names** and the
  secondary-name union is unchanged at **50 distinct names**; all five adopted secondaries
  already occur in the column and the three deleted names survive in `case_memos_v1.csv`.
  `case_memos_v2.csv` now holds **87 secondary assignments over 31 distinct names**, up from
  84 and down from 33: this row went from two descriptors to five, and
  `competing_valid_entity_cues` and `general_answer_passage_missing` were unique to it. The
  distinct `primary_open_code` count in v2 falls from 14 to **13**, because
  `question_wording_ambiguity` was unique to this row. `case_memos_v1.csv` is unchanged at 39
  distinct secondary names. The registry stays at **26 adopted descriptors** because no new
  descriptor is registered; five existing entries gain this affected unit and D-034 as a
  decision source, and four gain D-034 as a decision source recording a non-adoption.
  `review_status` counts are now 25 `jointly_reviewed` and 5 `needs_joint_review`.
  Validation progress after D-034 is **21 of 26 validated, 5 remaining**, superseding the
  20-of-26 figure recorded by D-033. Three vocabulary-audit items are registered and settled
  by none of this: whether a withholding of `cutoff_sensitive_near_miss` on substitutability
  rather than on the gap should leave the percentage bands untouched; whether co-necessity of
  the repeated-occurrence half is enough to route a unit to
  `repeated_function_word_amplification` when the sibling entry's inclusion rule is also
  fully met; and whether `minimal_preprocessing_score_distortion`, now at nine units and six
  sub-mechanisms, should be narrowed.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5adc8977554299438c868de2.md`.

## D-035 - Reclassify the Philadelphia crime family / Salvatore Testa Dense unit as a description-only bridge entity

- **Date:** 2026-08-06
- **Status:** active
- **Decision:** For `5add67915542992200553af8|dense`, replace the provisional primary
  `same_domain_entity_crowding` with `description_only_bridge_entity`. Adopt
  `peripheral_passage_content_dilution`, `generic_person_semantic_neighborhood` and
  `same_topic_passage_distractor` as secondaries. Use
  `cross_passage_conjunction_unresolved` as the closest competitor. Delete the provisional
  names `same_domain_entity_crowding` and `bridge_relation_underweighted` rather than
  registering either. Register no new descriptor. Do not adopt
  `cross_passage_conjunction_unresolved`, `question_frame_semantic_crowding`,
  `cutoff_sensitive_near_miss`, `gold_chain_not_unique`, `gold_chain_substitutability`,
  `possible_type_mismatch`, `entity_alias_reference_mismatch`, `low_context_name_query`,
  `related_name_document_crowding` or `technical_topic_crowding`.
- **Affected unit:** `5add67915542992200553af8|dense`.
- **Question:** `What was the nickname of the hitman hired by an Italian American Criminal
  Organization?` This is a bridge unit. `Philadelphia crime family` states that the
  Philadelphia crime family is an Italian American criminal organization based in
  Philadelphia, Pennsylvania. `Salvatore Testa` states that Salvatore Testa was nicknamed The
  Crowned Prince of the Philadelphia Mob and served as a hitman for the Philadelphia crime
  family. The answer is that nickname. **The question contains no proper name for either
  required entity, and no proper name at all**: the organization is identified only by a
  category description and the answer entity only by a role and a relation to it. This is the
  first unit in this pass whose question names nothing.
- **Verified implementation:** `all-MiniLM-L6-v2`, a symmetric bi-encoder; only paragraph
  text is encoded and titles are excluded; explicit row-wise L2 normalization, so a dot
  product is a cosine; mean pooling with a 256-token sequence limit; no reranker and no
  cross-passage inference in the main run. The tokenizer lower-cases and strips accents, so
  case and accent factors are identity operations and were deliberately not spent as factors.
  **Cosine carries no collection statistic**, and that single fact governs the whole
  diagnostic below.
- **Exact reconstruction:** re-encoding the read-only 4,937-passage pooled corpus reproduces
  all 50 stored top-50 titles in order, 0 of 50 mismatched, at a maximum absolute score error
  of 2.980e-07, so strong causal claims are supported. Complete-corpus ranks are 7 / 0.438223
  and 12 / 0.406772 against a rank-5 score of 0.476272. Both required passages sit inside the
  256-token limit at 120 and 82 model tokens, so truncation is excluded; the question is 18
  tokens.
- **Diagnostic scale:** 196 distinct labelled rows on the same unchanged candidate set, of
  which 195 are experimental conditions and one only tabulates the pooled position of every
  passage this entry names,
  5 of them deliberately repeated under a second producer with every repeat reproducing its
  original bit for bit, plus 4 `not_run` cells with reasons. The reproduction script carries
  154 assertions and all pass.
- **On this backend every index-side removal probe is an arithmetic identity, not only the
  drop-everything cell.** Because cosine has no collection term, removing documents leaves
  every score unchanged, so a removed set's outcome is fully determined by how many of the
  removed passages ranked above the gold. Nine removal cells were run against the prediction
  `rank_after = rank_before - |removed and ranked above it|`: the 7 person biographies give
  1 / 5, the 3 organization pages 7 / 9, the 6 Sicilian biographies 2 / 6, the best-ranked 7
  above the answer hop 1 / 5, the worst-ranked 7 above it 4 / 5, a random 7 above it 2 / 5, a
  different random 7 above it 4 / 5, all 10 above it 1 / 2, and 7 passages ranked below it
  7 / 12. **All nine agree exactly and every score is bit-identical to the baseline**, and the
  two different random subsets of the same pool give the same answer-hop rank. Pit 19y records
  that the drop-everything cell is an identity and offers the family probe with a complement
  control as the discriminating alternative; that alternative is an identity too, because the
  family and its complement differ only in size. This is registered as a vocabulary-audit
  question about how family probes were read on the earlier Dense units and is **not** a
  re-judgment of any landed decision, the log being append-only. The consequence here is
  direct: **no crowding reading can take the primary on this unit**, because the only causal
  evidence form available to it produces counts rather than effects. The cumulative ladder
  over the ten, 6 / 11, 5 / 10, 4 / 9, 3 / 8, 2 / 7, 1 / 6, 1 / 5, 1 / 4, 1 / 3 and 1 / 2,
  is therefore read as a count as well: 7 of the 10 must go before both enter the cutoff.
- **The discriminating Dense evidence is the query-side cue test, because it changes the
  scores, and it is decisive in both directions.** Comparing each state's top ten against the
  baseline top ten and against the 7-passage person family: the referring description alone
  gives 9 and 6, deleting the whole description gives 0 and 0, deleting only its demonym half
  gives 2 and 1, the answer frame `nickname of the hitman` gives 0 and 0, the question frame
  alone gives 0 and 0, and the best non-oracle state gives 7 and 4 against the baseline's own
  10 and 7. **The competing family is produced by the question's referring description and by
  nothing else**, which is what pit 19f and pit 19i ask and what the third exclusion of
  `question_frame_semantic_crowding` routes to the primary mechanism.
- **A 16-cell factorial on the referring expression, every cell non-oracle.** `I` keeps
  `Italian`, `A` keeps `American`, `C` writes `Mafia crime family` in place of `Criminal
  Organization`, `G` inserts `gangster`. P[IA--] is the question itself and reproduces
  7 / 0.438223 and 12 / 0.406772. The other fifteen: P[IA-G] 7 / 0.496649 and 9 / 0.483800;
  P[IAC-] 3 / 0.607513 and 13 / 0.493241; P[IACG] 3 / 0.609495 and 11 / 0.516003; P[I---]
  9 / 0.427975 and 13 / 0.406516; P[I--G] 8 / 0.492468 and 9 / 0.485390; P[I-C-] 5 / 0.598532
  and 12 / 0.493266; P[I-CG] 5 / 0.603182 and 10 / 0.516186; P[-A--] 20 / 0.313033 and
  10 / 0.352700; P[-A-G] 9 / 0.408186 and 2 / 0.452920; P[-AC-] 1 / 0.578255 and
  7 / 0.489991; P[-ACG] 1 / 0.581736 and 6 / 0.511005; P[----] 15 / 0.314556 and
  5 / 0.371287; P[---G] 8 / 0.416667 and 2 / 0.472123; **P[--C-] 1 / 0.585624 and
  4 / 0.510640**; **P[--CG] 1 / 0.586023 and 5 / 0.526723**. Only the last two recover both.
- **Single-factor effects, as mean rank deltas over the other three factors.** `I` gives
  -1.12 on the bridge passage and +6.00 on the answer passage; `A` gives -0.12 and +1.25;
  `C` gives -7.88 and +0.75; `G` gives -2.38 and -2.75. Three of the four factors carry
  opposite signs on the two required passages, and the one that discriminates the question's
  own constraint, `American`, is very nearly inert.
- **Interaction effect: the two defects of the referring expression bind on different
  required passages, and neither repair alone is enough.** Changing only the head noun gives
  3 / 13, deleting only the demonym gives 15 / 5, and doing both gives 1 / 4. The head-noun
  change serves the bridge passage and costs the answer passage a position; the demonym
  deletion serves the answer passage and costs the bridge passage eight. **The demonym's sign
  on the bridge passage reverses with the head noun**: 7 / 12 becomes 20 / 10 under `Criminal
  Organization` and 3 / 13 becomes 1 / 7 under `Mafia crime family`. This is pit 12 on the
  query side.
- **The partition that decides the tie-break.** Of every labelled query condition that keeps
  `Italian American Criminal Organization` verbatim, the ones that put both required passages
  inside the cutoff are appending `Philadelphia` at 1 / 0.554958 and 2 / 0.499144, appending
  `Philly` at 1 / 0.561057 and 3 / 0.495821, appending the bridge title at 1 / 0.656474 and
  3 / 0.516396, appending both titles at 2 / 0.613032 and 1 / 0.634903, adding `in
  Philadelphia` at 1 / 0.551362 and 2 / 0.503404, and appending the answer string at
  2 / 0.600663 and 1 / 0.676290. **Every one is an oracle injection and there is no non-oracle
  condition among them.** The non-oracle conditions that do recover both are `mafia hitman` at
  2 / 0.473937 and 3 / 0.468212, P[--C-], P[--CG], `What was the nickname of the mafia
  gangster hitman?` at 5 / 0.478093 and 2 / 0.508918, `What was the nickname of the mafia
  hitman?` at 4 / 0.478172 and 2 / 0.490345, the American-Mafia rewrite at 1 / 0.566312 and
  5 / 0.515729, and `United States Mafia hitman nickname` at 2 / 0.469649 and 5 / 0.408042 -
  **seven conditions, every one of which replaces the referring expression, and not one of
  which keeps the demonym `Italian`.** The constraint-preserving variant that changes only the
  head noun gives 3 / 13 and fails. **There is therefore no constraint-preserving non-oracle
  repair, and none of the seven is deployable.**
- **The single-factor oracle-name test passes in five forms, with both preconditions
  checked.** The five are listed above. The D-024 precondition of pit 19g holds and was
  checked before the verdict was read: the bridge title alone ranks its own passage
  1 / 0.706333 **and lifts the other required passage to 5 / 0.440004**, both inside the
  cutoff, which is D-026's strongest form of that precondition, and the answer title alone
  ranks its own passage 1 / 0.545298. The D-030 degeneracy check of pit 24b is passed rather
  than merely recorded: the gain is carried by a token absent from the question, appending
  `Philadelphia` alone giving 1 / 0.554958 and 2 / 0.499144 while appending `crime family`
  alone gives 1 / 0.564744 and 14 / 0.425469 and appending `Pennsylvania` gives 1 / 0.488966
  and 10 / 0.406492. This is the twelfth application of the test and its sixth pass.
- **The required passage states the question's referring description verbatim, that
  description is near-unique in the corpus, and it is still not discriminative.** The bridge
  passage's indexed body contains `is an Italian American criminal organization` word for
  word, and exactly 2 of 4,937 passages contain that string, the bridge gold and
  `Los Angeles crime family` at 10 / 0.416292. Reduced to that description alone the query
  ranks the bridge passage 1 / 0.541525; inside the full question it ranks 7 / 0.438223. This
  is a new form for this descriptor: previous uses recorded an anchor that was absent or one
  that was unusable, and here the descriptive substitute is present, verbatim, nearly unique,
  and still insufficient.
- **The description is a net liability for one of the two required passages.** Deleting the
  demonym compound moves the answer passage from 12 / 0.406772 to 5 / 0.371287 and the bridge
  passage from 7 / 0.438223 to 15 / 0.314556, while deleting the description entirely moves
  the bridge passage to 1650 / 0.087429 and leaves the answer passage at 12 / 0.313102. The
  description is necessary for the passage it describes and costs the other passage seven
  positions.
- **Three single-fact controls under pit 19z, against three null controls that reproduce the
  baseline bit for bit.** Deleting `an Italian American criminal organization` from the bridge
  passage moves it from 7 / 0.438223 to 12 / 0.406714, worth 5 rank positions and 0.031509
  points. **Deleting the whole nickname clause from the answer passage moves it from
  12 / 0.406772 to 6 / 0.463775**, so removing the answer improves the passage by 6 rank
  positions and 0.057003 points. Deleting only `for the Philadelphia crime family` gives
  12 / 0.407196, worth 0 rank positions. Deleting the hitman clause gives 16 / 0.377405.
  Rewriting the answer passage to name its employer the way the question does gives
  7 / 0.449149, still outside the cutoff, and appending the question's organization phrase to
  it gives 7 / 0.442143. Replacing every `Philadelphia` in the bridge passage gives
  23 / 0.347247 and in the answer passage 16 / 0.381008.
- **The gold-side ceiling is 1 and 7, so no index-side repair of the required passages is
  enough.** Reducing both to their query-relevant cores gives 1 / 0.585251 and 7 / 0.460718.
  The best non-oracle query with the passages untouched gives 1 / 0.585624 and 4 / 0.510640,
  and the two together give 4 / 0.512778 and 2 / 0.547486. The query-side change is necessary
  and sufficient; the passage-side change is neither.
- **The dilution gate passes on both required passages, and passing it required
  decontaminating the controls word by word.** All four inclusion conditions hold. The
  contract is verified from implementation, not inferred. The controlled ablation materially
  improves both: the bridge passage reaches 1 / 0.585251 at 10 words and 2 / 0.501900 at 14
  words, the answer passage 6 / 0.460718 at 20 words. The length-matched controls that retain
  only non-query-relevant material and keep the entity name do not improve either: on the
  bridge passage 67 / 0.268422 at 16 words, 61 / 0.271585 at 11 words, 16 / 0.377309 at 22
  words and 100 / 0.244156 at 24 words; on the answer passage 23 / 0.348350 at 12 words,
  42 / 0.298109 at 17 words, 26 / 0.338078 at 10 words and 27 / 0.331535 at 20 words. Both
  passages sit inside the sequence limit at 120 and 82 tokens. **Two controls did improve the
  rank and had to be decontaminated at the level of single words**: the bridge passage's alias
  list gives 6 / 0.466902 at 16 words, and removing only `Mafia` and `Mob` from that same
  control gives 11 / 0.407230 at 18 words; the answer passage's gangster clause gives
  7 / 0.445466 at 14 words, and removing only `gangster` gives 23 / 0.350442 at the same 14
  words. Pit 19l requires a control to keep the entity name; this unit adds that a control
  must also be stripped of every query-relevant **word**, not only of every query-relevant
  sentence. A construction boundary is recorded rather than papered over: on both passages the
  query-relevant material is embedded inside a sentence, an appositive list on one and a
  relative clause on the other, so a sentence-level verbatim subset is not constructible and
  only word-level subsets were available, the same limit D-029 recorded for a parenthetical.
- **The title-indexing condition is inert to negative, and it undoes a recovery.** T alone
  gives 7 / 0.428354 and 12 / 0.401174, worse on both. Applied on top of the best non-oracle
  query it gives 1 / 0.568534 and 6 / 0.500008, turning 1 / 4 into a failure. Neither required
  title is the question's anchor, the question having no anchor at all.
- **Per-side reachability holds, and holds under non-oracle queries.** The description with
  the mafia head noun ranks the bridge passage 1 / 0.723205, and the single word `gangster`
  ranks the answer passage 2 / 0.437038. `mafia` alone gives 1 / 0.618731 and 17 / 0.353613,
  `hitman` alone 1599 / 0.084070 and 33 / 0.251615, `nickname` alone 660 / 0.133528 and
  123 / 0.196047, and `nickname of the hitman` 1756 / 0.076803 and 19 / 0.285135.
- **Corpus setting, recorded as provenance under D-003 and pit 17.** Pooled `any@5` and
  `full@5` are 0 and 0; the official per-question window gives 2 and 6, so `any@5` is 1 and
  `full@5` is 0. The settings disagree on `any@5` only, which makes this the eighth unit in which
  the two corpus settings disagree. Rebuilding over this question's own 10
  passages gives 2 / 0.438223 and 6 / 0.406772 and reproduces the official window **item by
  item**, and `restrict_scores` over the same 10 gives the same order, which is the seventh
  verification of D-025's Dense restriction property and its strongest form. Of the 10
  passages above the answer hop, 6 were introduced by pooling, and **those 6 are exactly the
  Sicilian-Mafia biographies**, the first unit in which the pooling-introduced set coincides
  with one readable family; 5 of the 6 above the bridge hop were introduced by pooling. Under
  the arithmetic identity above, the observation that dropping only the pooling-introduced
  passages returns exactly the per-question ranks is guaranteed once the window is the corpus
  restricted to those 10, so it confirms the restriction property rather than measuring a
  pooling effect. That reading is registered as an audit question and changes no landed
  decision.
- **The competing set, read in full rather than from titles.** All 6 passages above the bridge
  hop and 7 of the 10 above the answer hop are biographies of criminals that identify neither
  required entity: `Calcedonio Di Pisa` 1 / 0.516227, `Antonio Rotolo` 2 / 0.494784,
  `Angelo La Barbera` 3 / 0.488265, `Antonio Cottone` 4 / 0.488130,
  `Joseph LoPiccolo (organized crime)` 5 / 0.476272, `Salvatore La Barbera` 6 / 0.455380 and
  `Gaspare Spatuzza` 9 / 0.423097. Six of these are explicitly Sicilian Mafia members, and 8
  of 4,937 passages contain `sicilian mafia`. The remaining 3 are organization or ethnic-body
  pages that are in the same subject neighbourhood and each omits a decisive constraint:
  `Mexican Mafia` 8 / 0.425303 is a criminal organization but Mexican American,
  `Los Angeles crime family` 10 / 0.416292 carries the question's referring description word
  for word but names no hitman and no nickname, and
  `Italian American One Voice Coalition` 11 / 0.408984 is an Italian American organization but
  an anti-bias one. The two groups partition the ten exactly.
- **No substitute and no complete alternative answer inside the cutoff.** Exactly 3 passages
  in the corpus carry a nickname marker together with a hired-killer role and a criminal
  organization: the answer gold itself, `William Cammisano` 26 / 0.343312, and
  `Gaspare Spatuzza` 9 / 0.423097. `William Cammisano` is the nearest alternative chain,
  giving a nickname, an enforcer role and a Kansas City crime family in one passage, but it
  requires a looser standard than the gold on two counts, `enforcer` rather than a hired
  hitman and no statement that the organization is Italian American, so the exclusion for a
  looser interpretation fires. `Gaspare Spatuzza` supplies the role, having been a killer for
  a Sicilian family, but no nickname. `crowned prince` occurs in 1 of 4,937 passages,
  `philadelphia crime family` in 2, both of them the golds, `hitman` in 8 and `hit man` in 0.
- **Comparison retriever.** BM25 places the answer passage at 3 and the bridge passage at 29
  pooled, and at 2 and 8 per question. Both pooled figures lie inside the stored top-50 and
  are therefore complete-corpus ranks. This shows only that both passages are reachable on
  another backend; per pit 16 it is not a cause of the Dense outcome and the two score scales
  are not compared. Worth recording as a contrast: the two backends disagree about which
  required passage is the easier one.
- **Tie-break.** Under pit 13, meeting an inclusion rule does not decide the tie, and both
  candidates meet theirs. The conjunction reading's legs are checked individually and are
  strong: per-side reachability holds under non-oracle queries at 1 / 0.723205 and
  2 / 0.437038; 8 of 14 single factors carry opposite signs, five of the ten single deletions
  and three of the four factorial factors, which is the highest proportion recorded in this
  pass against 10 of 19 at D-024, 10 of 20 at D-025, 8 of 22 at D-031 and 4 of 19 at D-026;
  and the first exclusion does not fire, because the answer passage alone does not answer the
  question, never stating that its employer is Italian American. It loses on two independent
  grounds. First, pit 19s: seven non-oracle conditions that supply no intermediate fact and
  perform no cross-passage reasoning put both required passages inside the cutoff, and if
  carrying a fact across passages were the binding constraint that could not happen. Second,
  D-026's measurable criterion for separating these two names: a single anchor lifts both
  sides, the bridge title alone giving 1 / 0.706333 and 5 / 0.440004, which is the form D-026
  used to refuse this name and the opposite of D-025, where the same probe pushed the other
  side to 2158. The two grounds agree, so the name is not adopted at all, not even as a
  secondary. `description_only_bridge_entity` wins on the partition recorded above: no
  non-oracle condition that leaves the question's referring expression intact recovers both,
  while every condition that does recover both either injects a gold identifier or replaces
  that expression. This is the correct slicing of the D-028 refutation path, and it is what
  distinguishes this unit from D-028, where the refuting condition was index-side and left the
  query untouched, showing the description as given to be sufficient. Here 35 conditions leave
  the description untouched and not one of them recovers both without an oracle injection.
- **Why the two provisional names are deleted rather than registered.**
  `same_domain_entity_crowding` is deleted on three independent grounds. It is a crowding name
  and on this backend no crowding reading can be given primary-level evidence at all, because
  every removal cell is an arithmetic identity. The composition it points at is already
  partitioned exactly by two registered names, the 7 person biographies by
  `generic_person_semantic_neighborhood` and the 3 organization pages by
  `same_topic_passage_distractor`, so registering it would duplicate, which is the ground on
  which D-031 deleted `subject_associate_crowding`, D-033 deleted
  `cross_entity_relation_unresolved` and D-034 deleted `competing_valid_entity_cues`. And the
  family it names is produced by the adopted primary's own referring description, so it is
  downstream of it. This is the seventh consecutive decision to create no new name.
  `bridge_relation_underweighted` is deleted for the third time, and **not** by citing D-028
  and D-031, because playbook section 4.22 records that a deletion of this name must rest on
  this unit's own measurements: there the relation tokens were measured completely inert and
  here they are not. Deleting `hitman` from the question moves the answer passage from
  12 / 0.406772 to 28 / 0.336713, so that relation word is worth 16 rank positions and is one
  of the strongest tokens in the query; inserting `gangster` helps both required passages,
  -2.38 and -2.75 across the factorial; tripling `hitman` gives 9 / 0.362312 and
  6 / 0.399817, so emphasising the relation helps one side by six positions and costs the
  other two, recovering neither; and on the index side deleting the relation from the answer
  passage is worth 0 rank positions, 12 / 0.407196. The name asserts that the relation is
  underweighted, which is a token-level weighting claim that pit 18 forbids without
  attribution, and the measurements point the other way on the query side and to zero on the
  document side. This deletion removes the name's last current `case_memos_v2.csv` row.
- **Why the other candidates are not adopted.** `question_frame_semantic_crowding` meets the
  first half of its inclusion rule on read text but its third exclusion fires and is measured
  in both directions: the referring cue alone reproduces 9 of 10 of the baseline top ten and 6
  of the 7 person biographies, while the frame alone reproduces 0 of 10, so the family belongs
  to the primary mechanism. `possible_type_mismatch` fails its first exclusion, the terms
  aligning directly rather than mismatching, the bridge passage carrying the question's
  description word for word. `entity_alias_reference_mismatch` is excluded by its own rule,
  which routes an entity not named in the query to `description_only_bridge_entity`.
  `low_context_name_query` is the mirror image of its definition, which requires a query
  dominated by proper names where this query has none. `related_name_document_crowding`
  requires a shared name and the question names nothing. `technical_topic_crowding` requires a
  technical facet. `gold_chain_not_unique` and `gold_chain_substitutability` are refused on
  the read text recorded above. `answer_property_semantic_crowding` is defined for comparison
  questions, and `generic_query_scaffold_score_inflation`,
  `surface_form_tokenization_mismatch` and `minimal_preprocessing_score_distortion` are
  lexical mechanisms that this backend does not have, its tokenizer making case and accent
  identity operations.
- **`cutoff_sensitive_near_miss` is withheld, and no band edge moves.** The rank-5 score is
  0.476272 and the two required passages sit 0.038049 and 0.069500 points, or 7.989 and 14.592
  percent, below it. The ground is the D-025 split rule, a bridge question needing both hops:
  the farther figure lies inside the excluded band of 9.431 to 52.794 percent, so the
  descriptor cannot cover this unit whatever the nearer figure does. Because the ground is the
  split rule and not the nearer gap, no band edge moves: the accepted band stays 1.156 to
  5.464 percent, the excluded band stays 9.431 to 52.794 percent and the never-decided band
  stays 5.464 to 9.431 percent. **7.989 percent is the first measured figure to fall strictly
  inside the never-decided band**, and it is recorded as measured but not band-setting, the
  treatment given to D-024's 5.698 percent and D-034's 3.641 percent. No cliff can be cited,
  the successive differences from rank 1 to rank 10 being 0.021442, 0.006520, 0.000134,
  0.011859, 0.020891, 0.017158, 0.012920, 0.002206 and 0.006805. This is also the first unit
  in which the counter-evidence this entry has always weighed, the cumulative removal ladder,
  is unavailable in principle: on a bi-encoder that ladder is an arithmetic identity, so the
  observation that two removals give 5 / 10 and flip `any@5` is a count and not a measurement.
  Whether the ladder should have been read as counter-evidence on the earlier Dense units is
  an audit question.
- **Not-run cells and attribution boundary.** Per-token decomposition and the dead-token
  ranking diff were not run: `probe_kit` refuses both on Dense because cosine yields no token
  contribution (pit 18), and the query-side substitute used here is whole-token deletion
  re-ranked over the full corpus. The query-splitting union of pit 19o was not run: it is
  defined for comparison questions, and this bridge question has a single referring expression
  with no two sides to split. The BM25 preprocessing factors were not run: they are lexical,
  and on this backend case and accent normalization are identity operations. The
  statistics-matched control of pit 19ad was not run: it exists because a lexical removal
  moves `idf` and `avgdl`, and cosine has no collection term, which is the same fact that
  makes every removal cell here an identity. **Attribution boundary:** nothing above licenses
  a claim about which tokens the encoder weighted, attended to or averaged away; the dilution
  finding licenses only the passage-level statement that removing the named material raises
  that passage's similarity to that query, and it is a diagnostic rather than a deployable
  fix, because it requires knowing which passage is required. The seven non-oracle recoveries
  must not be written as repairs: each drops a stated constraint of the question. The
  comparison retriever's ranks are not a cause. The corpus setting is provenance, not a
  mechanism.
- **Evidence layers.** Observed: the complete-corpus ranks and scores, the 196 conditions, the
  full text of every passage above either required passage, and the corpus counts. Verified
  implementation fact: the encoder contract above, and in particular that cosine carries no
  collection statistic, which is what makes every index-side removal an identity and what
  makes case and accent factors identities. Supported interpretation: both required passages
  are reachable only through the question's description; that description carries two defects
  which bind on different required passages and interact; no constraint-preserving non-oracle
  condition recovers both; naming the organization recovers both in five forms. Speculation,
  explicitly not written into any conclusion: why `Italian` dominates `American` on this
  encoder, how mean pooling folds four facets into one vector, and whether `Mafia` outperforms
  `Criminal Organization` because of corpus frequency. All three are token-level attributions
  that pit 18 forbids without an attribution experiment, and none was run.
- **Taxonomy effect:** `description_only_bridge_entity` becomes the validated primary for a
  fourth unit and a fourth Dense unit, after D-017, D-023 and D-026, and gains its first form
  in which the descriptive substitute is present verbatim in the required passage and
  near-unique in the corpus and still insufficient. The already-registered audit question
  about that entry's definition, which is worded `for lexical retrieval` while all four of its
  primary uses are Dense, is recorded again and not resolved here (pit 2).
- **Inventory effect.** The primary inventory is unchanged at **26 distinct names**.
  `description_only_bridge_entity` is item 5, was already in the inventory, and this is its
  fourth validated primary use. The departing name `same_domain_entity_crowding` is item 22 of
  the primary inventory and now keeps no current `case_memos_v2.csv` row of either kind, this
  unit having been its only holder. The secondary-name union is unchanged at **50 distinct
  names**; the departing name `bridge_relation_underweighted` is item 1 of the primary
  inventory and now keeps **no current `case_memos_v2.csv` row at all**, this having been its
  last, which is the treatment given to `location_chain_incomplete`,
  `subject_associate_crowding`, `generic_context_substitution`, `adjacent_event_crowding`,
  `related_document_crowding`, `broad_film_person_neighborhood`, `surname_entity_confusion`
  and `both_gold_chain_passages_missing`. `case_memos_v2.csv` now holds **89 secondary
  assignments over 30 distinct names**, up from 87 over 31: this row went from one descriptor
  to three, the departing name was unique to it, and all three adopted names already occur
  elsewhere in the column. The distinct `primary_open_code` count in v2 falls from 13 to
  **12**. `case_memos_v1.csv` is unchanged at 39 distinct secondary names. The registry is
  unchanged at **26 adopted descriptors**. Three existing entries gain this affected unit and
  D-035 as a decision source, `peripheral_passage_content_dilution`, which reaches five
  affected units, `generic_person_semantic_neighborhood`, which reaches four, and
  `same_topic_passage_distractor`, which reaches two and gains its first Dense unit; three
  gain D-035 as a decision source recording a non-adoption rather than an affected unit,
  `cross_passage_conjunction_unresolved`, `question_frame_semantic_crowding` and
  `cutoff_sensitive_near_miss`; and `description_only_bridge_entity` gains D-035 as a primary
  use, which is why this unit is not listed there as a secondary affected unit.
  `review_status` counts are now 26 `jointly_reviewed` and 4 `needs_joint_review`.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5add67915542992200553af8.md`.

## D-036 - Retain the plausible non-gold answer for the Ade Edmondson / Bad News BM25 unit and revise its secondary set

- **Date:** 2026-08-06
- **Status:** active
- **Decision:** For `5adf58f15542993a75d264d2|bm25`, retain the provisional primary
  `plausible_non_gold_answer`. Retain `gold_chain_not_unique` and adopt
  `surface_form_tokenization_mismatch`, `generic_term_lexical_crowding`,
  `cross_entity_token_recombination`, `description_only_bridge_entity` and, for the bridge
  hop only, `cutoff_sensitive_near_miss`. Delete the provisional name
  `underdetermined_question` rather than registering it. Register no new descriptor. Use
  `minimal_preprocessing_score_distortion` as the closest competitor. Do not adopt
  `cross_passage_conjunction_unresolved`, `gold_chain_substitutability`,
  `generic_query_scaffold_score_inflation`, `repeated_function_word_amplification`,
  `unindexed_title_name_anchor`, `same_topic_passage_distractor`,
  `peripheral_passage_content_dilution` or `proper_name_homonym_collision`.
- **Affected unit:** `5adf58f15542993a75d264d2|bm25`.
- **This is the fourth decision to retain a unit's provisional primary**, after D-015, D-020
  and D-032, and the first single-note unit to carry `plausible_non_gold_answer`, which had
  been used once before, on the overlap unit of D-011. It is the second affected unit of
  `gold_chain_not_unique`, whose only previous unit is that same D-011 one.
- **Question:** `Which television series featured an actor who also performed in "The Young
  Ones"?` This is a bridge unit. `Ade Edmondson` states that Edmondson is an English
  comedian and actor best known for the television series "The Young Ones" and "Bottom", and
  that he also appeared in "The Comic Strip Presents..." series of films, for one episode of
  which he created the spoof heavy metal band Bad News. `Bad News (band)` states that Bad
  News were an English spoof heavy metal band created for the Channel 4 television series
  "The Comic Strip Presents...", played by Ade Edmondson, Nigel Planer, Rik Mayall and Peter
  Richardson. The annotated answer is that series, and the answer string itself is not
  recorded anywhere on disk in this repository, so it is read off the two required passages
  and is treated as a supported interpretation rather than as given. **Neither required
  entity is named in the question**: the actor is identified only by a role and a relation,
  and the answer series only by a category noun. The question's only proper name, "The Young
  Ones", is neither of them.
- **Verified implementation:** `rank-bm25==0.2.2` BM25Okapi with the package defaults
  `k1=1.5`, `b=0.75` and `epsilon=0.25`; only paragraph text is indexed and titles are
  excluded; the tokenizer is `text.lower().split()` with no punctuation stripping, no stop
  words, no stemming, no Unicode normalization and no phrase matching; a repeated query token
  contributes once per occurrence. Corpus avgdl is 90.884950375 over 4,937 passages. The
  per-token decomposition reconciles with `get_scores` on the two required passages and on
  the top 16, so it may be quoted (pit 24).
- **Exact reconstruction:** rebuilding the same 4,937-passage pooled index reproduces all 50
  stored top-50 titles in order, 0 of 50 mismatched, at a maximum absolute score error of
  0.000e+00, so strong causal claims are supported. Complete-corpus ranks are 6 / 19.630966
  and 329 / 9.252464 against a rank-5 score of 19.686227. The indexed bodies are 112 and 54
  tokens.
- **Diagnostic scale:** 112 labelled rows on the same unchanged candidate set, of which 101
  are measured runs, one of those being a deliberate repeat of the baseline under a second
  producer that reproduced it bit for bit, 7 tabulate the positions of passages this entry
  names, and 4 are `not_run` cells with reasons. The reproduction script carries 206
  assertions and all pass.
- **A complete alternative answer sits inside the cutoff, and it survives every repair.**
  `Filthy Rich &amp; Catflap` at 3 / 20.130130 states that it is a BBC sitcom broadcast in
  1987 and that the series featured former "The Young Ones" co-stars Nigel Planer, Rik Mayall
  and Adrian Edmondson as its three title characters. One passage therefore satisfies all
  three explicit constraints of the question. It satisfies them under a **stricter** standard
  than the annotated chain uses: reaching "The Comic Strip Presents..." requires accepting one
  required passage's characterization over the other's, `Ade Edmondson` calling it a series of
  films and `Bad News (band)` calling it a Channel 4 television series, and the alternative
  needs no such reconciliation. The alternative is not an artefact of any defect measured
  below: it ranks 1 / 27.168933 under the deployable query-side repair, 1 / 29.428445 under
  full two-sided boundary normalization and 3 / 0.633169 on the comparison retriever, ahead
  of the bridge hop in each. **The one setting that reverses the two is the official
  per-question one**, where the bridge hop is 1 of 10 and the alternative 2 of 10; restricting
  the pooled scores to those same 10 passages instead leaves the alternative first and the
  bridge hop at 2 / 19.630966, so the reversal is carried by the per-question idf rather than
  by the smaller document set.
- **A full-corpus read of every rival candidate leaves exactly one.** Nine passages name the
  Young Ones. Besides the bridge hop and the alternative answer, `Oh, No! Not THEM!`
  16 / 17.834466 is a remake and never says it featured a Young Ones performer;
  `Carole Gray` 18 / 17.701479 appeared in the television series "The Avengers" and made her
  film debut in the 1961 film of the same name, so it changes the referent of the question's
  only proper name; `Roland Rat` 19 / 17.584079 concerns a puppeteer and a character rather
  than an actor and a series; `David Mirkin` 23 / 17.407047 and `Ben Elton` 46 / 14.837377 are
  a director and a writer on read text; `The Young Ones (TV series)` 35 / 15.688549 is the
  queried series itself and `The Young Ones (video game)` 45 / 14.873266 is a video game.
- **The one-character preprocessing defect, priced exactly.** The query's quoted title
  tokenizes to `"the`, `young` and `ones"?`. The last of these occurs in 0 of 4,937 passages,
  is absent from the index vocabulary, and contributes exactly 0.000000: deleting it leaves
  the 4,937-passage order 0 of 4937 changed at a maximum absolute score difference of
  0.000000. The bare corpus form `ones"` occurs in 5 passages at an idf of 6.798853, the
  highest idf of any form available to this question. **Stripping that one character on the
  query side and changing nothing else** moves the bridge hop from 6 / 19.630966 to
  2 / 25.786297, worth 6.155330248 points and 4 rank positions, which is exactly the score a
  query consisting of the single token `ones"` gives it, 5 / 6.155330248, the two agreeing to
  8.882e-16. The same change is worth 0.000000000 on the answer hop. This is the eighth
  instance of a query token absent from the corpus contributing exactly 0.000000, after
  D-019, D-021, D-028, D-030, D-032, D-033 and D-034. The effect is 100 percent query-side,
  the D-030 shape: the document side alone gives 6 / 19.630899 against a baseline of
  6 / 19.630966, and the two sides together give 2 / 25.786223.
- **The thorough normalization is worse than the one-character one, and that is a new shape.**
  Splitting the boundary-punctuation factor by character shows the two halves carry opposite
  signs on the query side: the question mark alone gives 2 / 25.786297 and the double quotes
  alone give 11 / 20.256894, while the combined factor gives 13 / 20.256894. The reason is in
  the vocabulary. Stripping boundary punctuation dissolves the anchor: df(`ones"`) falls from
  5 to 0 while df(`ones`) rises from 10 to 24 at an idf of 5.301069, and df(`"the`) falls from
  494 to 0 while df(`the`) rises from 4715 to 4726 at an idf of 1.885384. Measured on both
  sides the ordering is that the minimal repair beats the general one: 2 / 25.786297 for the
  question mark alone, 3 / 27.760767 for full boundary stripping over 4,936 of 4,937 passages,
  and 3 / 27.442933 for a generic `[a-z0-9]+` analyzer over all 4,937. All three flip `any@5`;
  none moves the answer hop, which goes to 330, 1087 and 1078 respectively.
- **A second surface-form pair, on the document side, and it decides how one oracle condition
  reads.** The bridge hop writes its own subject as `Adrian Charles "Ade" Edmondson`, so the
  token `ade` has tf 0 inside its own indexed body while `"ade"` has tf 1; `ade` occurs in
  exactly 1 of 4,937 passages, the other required one, where its tf is 1. A query that is the
  single token `ade` therefore gives 2202 / 0.000000 and 1 / 9.908532, and the bare full name
  gives 3 / 9.639104 and 2 / 9.908532 - **the bridge hop's own name scores its own passage
  below the other gold.** Pit 19g's precondition check is what makes N1, appending the bridge
  title, readable at all: its 1 / 29.270070 and 8 / 19.160996 is not evidence that the name is
  a weak anchor, it is evidence that this anchor is delivered to the wrong passage.
- **No non-oracle condition recovers both hops, and the oracle boundary is sharp.** Across the
  measured runs not one non-oracle cell places both required passages inside the cutoff. The
  answer hop's best non-oracle position anywhere is 77 / 6.009257, reached by a query reduced
  to the two category nouns, which leaves the bridge hop at 28 / 7.172356; the best from a
  factor applied to the full question is 100 / 8.695492 under scaffold removal, which is
  negative on the bridge hop at 8 / 14.671657. Every oracle condition that names the answer
  side recovers both: appending the answer title 1 / 24.736194 and 3 / 21.929780, appending
  both titles 1 / 34.375297 and 2 / 31.838312, appending the answer entity 1 / 32.617840 and
  5 / 24.357889. The single-factor oracle-name test D-020 introduced therefore **passes**
  here, its thirteenth application and its seventh pass, after D-017, D-023, D-026, D-028,
  D-029 and D-035.
- **The wording factorial, run in two preprocessing states, is what deletes
  `underdetermined_question`.** Pits 19k and 19ah require the repair to be a full factorial
  and to be run twice. Factor A repairs the title's surface, B replaces `performed in` with
  the corpus idiom `appeared in`, and C adds the constraint that the actor created a spoof
  heavy metal band for the series - **C is oracle**, because that fact is stated only in the
  two required passages. In the raw state the eight cells give 6 / 19.630966,
  3 / 22.868072, 13 / 20.256894 and 9 / 23.494000 on the bridge hop for the four non-oracle
  combinations, so A alone is negative and B alone is positive and only the factorial shows
  it; under two-sided boundary normalization A is exactly inert, A0 and A1 agreeing bit for
  bit at 3 / 27.760767 and at 1 / 30.982730, and the eight cells collapse to two results.
  **All 8 oracle cells put both hops inside the cutoff and all 8 non-oracle cells fail**, in
  both states. A question property that only a fact from inside the golds can repair is not a
  retrieval mechanism (pit 17); this is the same ground on which D-034 deleted
  `question_wording_ambiguity`, and what `underdetermined_question` was recording is already
  carried, with a passage behind it, by `gold_chain_not_unique`.
- **The removal probe's gain is entirely positional, which is unusual on a lexical backend.**
  Five non-gold passages sit above the bridge hop. Four of them fail the question on read text
  and form the family; the fifth is the alternative answer and forms the complement. Removing
  the family gives 2 / 19.681225; removing the complement alone gives 5 / 19.644641; a
  size-matched null of four high-ranked passages carrying no `young` gives 6 / 19.665899, that
  is no movement at all; and the statistics-matched cell, the family removed with the pooled
  idf and avgdl grafted back, gives 2 / 19.630966 - **the same rank at a score bit-identical
  to the baseline.** Pit 19ad exists because a lexical removal moves idf as well as position;
  here the two are cleanly separated and the statistical half is exactly zero.
- **Pit 19u's cell was run in both states and agrees, unlike D-034.** Removing all 5 non-gold
  passages above the bridge hop gives 1 / 19.695018; removing all 327 above the answer hop
  gives 1 / 22.488063 and 3 / 11.231877, both inside the cutoff. Under two-sided
  normalization the same cells give 1 / 27.862895 with 2 removals and 1 / 37.325376 and
  2 / 13.115875 with 1,085. The cumulative ladder shows how differently the two hops behave:
  one removal already gives the bridge hop 5 / 19.639773 and flips `any@5`, while the answer
  hop is still at 123 / 10.279798 after 160 removals and needs all 327.
- **The crowding test is weak in both directions, the D-033 shape.** The referent cue alone
  reproduces 2 of the 5 passages above the bridge hop in its top ten, and the frame with the
  cue deleted reproduces a different 2; the fifth is reproduced by neither. Pit 19i requires
  both directions to agree in sign before a crowding descriptor may be promoted, and neither
  family can be assigned to the other here, so `generic_term_lexical_crowding` stays a
  secondary under its own deferral clause.
- **Corpus setting is provenance, and both paths are present.** Pooled gives `any@5` 0 and
  `full@5` 0 at 6 and 329; the official per-question setting gives `any@5` 1 and `full@5` 0 at
  1 and 10, and the rebuilt per-question index reproduces the stored CSV order title by title.
  New competitors is measured and holds: 4 of the 5 passages above the bridge hop and 319 of
  the 327 above the answer hop are introduced by pooling. The statistics path is measured too
  and holds independently: restricting the pooled scores to the same 10 passages gives
  2 / 19.630966 and 10 / 9.252464, so the alternative answer still outranks the bridge hop
  inside the window, while rebuilding on the window gives 1 / 5.186791 and 10 / 1.870318.
  Grafting the pooled idf and avgdl back onto the window reproduces the restricted order title
  by title at 2 / 19.630966, and grafting the pooled idf alone gives 2 / 18.817663, so idf
  carries the whole difference and avgdl carries none of it, the D-032 split. **This is
  the ninth unit in which the two corpus settings disagree.**
- **The title-indexing condition is materially positive and is not a title-anchor effect.**
  T alone moves the bridge hop from 6 / 19.630966 to 5 / 19.745864 and flips `any@5`, the
  second materially positive T after D-028. It is not the D-028 mechanism. **No query token
  appears in either gold title.** avgdl moves from 90.884950 to 94.023496, the bridge hop
  gains 0.114897 and the passage that had defined the cutoff gains 0.038857, and they exchange
  places with a final margin of 0.020780. This is a length-normalization side effect, and
  `unindexed_title_name_anchor` is refused on its second inclusion condition even though its
  third one holds.
- **Secondary descriptor grounds:**
  - `gold_chain_not_unique`: retained. `Filthy Rich &amp; Catflap` at 3 / 20.130130 supports a
    complete answer under the same evidentiary standard as the annotated chain, and on read
    text under a stricter one.
  - `surface_form_tokenization_mismatch`: adopted, its eleventh unit. Two worked pairs,
    `ones"?` against `ones"` on the query side and `ade` against `"ade"` on the document side.
  - `generic_term_lexical_crowding`: adopted, its ninth unit. The inclusion rule is met on
    read text by the four higher-ranked passages that fail the question, `Sianoa Smit-McPhee`
    1 / 21.089205, `Tzi Ma` 2 / 20.621536, `The Itchy &amp; Scratchy Show` 4 / 19.971104 and
    `Gretchen Palmer` 5 / 19.686227, each taking between 32.9 and 63.4 percent of its score
    from the content-bearing category terms `television`, `series`, `actor`, `featured` and
    `performed`. The exclusion for a passage that supplies a complete alternative answer is
    what keeps the fifth out of the family.
  - `cross_entity_token_recombination`: adopted, its second unit and the first on this
    question shape. `Gretchen Palmer`, the passage that defined the cutoff at 5 / 19.686227
    and stood 0.055261 above the bridge hop, takes 7.949254 or 40.4 percent of its score from
    the question's referent cue while having no connection to the queried series: 4.111593
    comes from `young` supplied by The Young and the Restless and 3.837661 from `"the`
    supplied by three unrelated quoted series titles.
  - `description_only_bridge_entity`: adopted as a secondary, its tenth unit. Neither required
    entity is named, in the D-029 and D-034 form, and the D-024 precondition was checked
    before the verdict was read. It is a secondary rather than the primary because the
    descriptive material is not the binding constraint on the bridge side: a blind query-side
    repair that adds no information reaches that passage at 2 / 25.786297, the D-034 boundary.
  - `cutoff_sensitive_near_miss`: adopted for the bridge hop only. The rank-5 score is
    19.686227 and the two required passages sit 0.055261 and 10.433763 points, or 0.281 and
    53.000 percent, below it. **0.281 percent is the smallest margin this project has
    recorded**, below D-026's 1.156 percent, so adopting it moves the accepted band's lower
    edge to 0.281 percent; 53.000 percent moves the excluded band's upper edge from D-025's
    52.794 percent. There is no cliff, the successive differences from rank 1 to rank 10 being
    0.467669, 0.491405, 0.159027, 0.284877, 0.055261, 0.224272, 0.288721, 0.118155 and
    0.097356, the step just above the gold being the smallest of the nine. The counter-evidence
    supports adoption in the D-032 sense: an index-side removal of one competitor already gives
    5 / 19.639773 and flips `any@5`. The no-substitute condition D-022 introduced is met, a
    full-corpus scan finding `comic strip presents` in exactly 2 passages which are the two
    required ones, `bad news` in exactly 2 which are the same two, and `ade edmondson` in
    exactly 1, which is the other required passage and does not state the fact this one
    supplies.
- **Excluded descriptors:** `cross_passage_conjunction_unresolved` is refused on its first
  exclusion, one passage supplying a complete answer, which is the exclusion D-011 also used.
  `gold_chain_substitutability` is refused on its own exclusion for an alternative that
  changes the answer. `generic_query_scaffold_score_inflation` is refused on its second
  exclusion: content-bearing category terms outweigh scaffold in every one of the five
  passages above the bridge hop, for instance `Sianoa Smit-McPhee` taking 13.367157 from
  category terms against 6.140381 from scaffold. `repeated_function_word_amplification` and
  `repeated_content_word_amplification` are inapplicable, the query repeating no token.
  `unindexed_title_name_anchor` is refused on its second inclusion condition although its
  third holds. `same_topic_passage_distractor` is refused because the competitors are generic
  category matches rather than passages in the answer entity's own neighbourhood, the D-024
  ground. `peripheral_passage_content_dilution` is inapplicable, its definition being scoped
  to a mean-pooled encoder. `proper_name_homonym_collision` is not adopted: the 1961 film
  sharing the queried title is real but its passage sits at 18 / 17.701479, below the bridge
  hop, so it is not outcome-determinative.
- **Closest competitor:** `minimal_preprocessing_score_distortion`, which would be that name's
  tenth unit. It wins on outcome-determinacy for `any@5`, one deployable query-side character
  being worth 4 rank positions and flipping the metric. It loses on three grounds. First, the
  repair does not turn a wrong result into a right one: it promotes the complete alternative
  answer to 1 / 27.168933 and the annotated bridge hop to 2 / 25.786297, so what the defect
  suppressed was an already-correct top-5. Second, `full@5` is untouched by it and by
  everything else non-oracle, the answer hop's best non-oracle position being 77 / 6.009257.
  Third, D-005 is active and names this very unit as one of its two motivating units, and
  D-011 decided the same shape the same way on the other one.
- **Not-run cells and attribution boundary:** four cells were not run. M split by side, because
  the query holds no singular/plural pair so pit 19t's mechanism is absent and neither
  mismatch is morphological. A gold-targeted index-side surface repair with its corpus-wide
  counterpart, because pit 19ae applies only when the repair must be aimed at a gold and this
  mismatch is wholly query-side, so the deployable version is the query-side cell already run.
  Length-matched dilution controls, because that gate is scoped to a mean-pooled encoder.
  Query splitting, because pit 19o is a comparison-unit requirement and this is a bridge unit
  whose answer hop shares no query token beyond the generic frame. **Attribution boundary:**
  what is established is that a complete alternative answer is retrieved inside the cutoff and
  survives every intervention, that one query character is worth 6.155330248 points on the
  bridge hop, that the family removal's gain is entirely positional, and that no non-oracle
  condition reaches the answer hop. What is **not** established is why the annotated chain was
  chosen over the alternative by the dataset's annotators, the answer string not being on disk
  here; nor that the alternative would be accepted by the benchmark's own scorer, which
  compares titles. The comparison retriever is cited only for reachability: `Ade Edmondson`
  4 / 0.619434 and `Bad News (band)` 184 / 0.263856 over the same 4,937 passages, with scales
  not comparable across backends.
- **Taxonomy effect:** `taxonomy_defect_flag=false`. The existing primary code covers the
  case, no new descriptor is created, and one provisional name is deleted.
- **Registry:** `manual_review_v1/analysis/secondary_descriptor_registry.md`.
- **Boundary:** three are recorded rather than closed. First, the two statements of D-025's
  split rule now in the `cutoff_sensitive_near_miss` entry do not agree: D-025, D-026 and
  D-032 adopted the descriptor for the near hop while the far hop sat inside the excluded
  band, and D-035 restates the rule as forbidding the descriptor for the whole unit whatever
  the near figure does. This decision follows the four landed adoptions and registers the
  wording as a vocabulary-audit question. Second, when a complete alternative answer already
  sits inside the cutoff, `cutoff_sensitive_near_miss` records the fragility of the annotated
  title rather than of answer availability, which is a weaker reading than the one D-022
  through D-032 gave it; that distinction is registered and not resolved. Third, whether
  `description_only_bridge_entity` and `plausible_non_gold_answer` should be allowed to sit
  on the same unit is left open: the first says the annotated chain is unreachable without a
  name, the second says the chain did not have to be reached, and both are measured here.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5adf58f15542993a75d264d2.md`.

## D-037 - Reclassify the Pitof / Catwoman Dense unit as peripheral passage content dilution and delete two provisional names

- **Date:** 2026-08-06
- **Status:** active
- **Decision:** For `5ae048a255429924de1b708e|dense`, replace the provisional primary
  `cross_passage_conjunction_unresolved` with `peripheral_passage_content_dilution`, and
  adopt `question_frame_semantic_crowding` as the only secondary. Delete the two
  provisional names `broad_adaptation_topic_crowding` and
  `answer_entity_missing_both_methods` rather than registering either. Register no new
  descriptor. Use `question_frame_semantic_crowding` as the closest competitor. Do not
  adopt `cross_passage_conjunction_unresolved`, `description_only_bridge_entity`,
  `same_topic_passage_distractor`, `generic_person_semantic_neighborhood`,
  `unindexed_title_name_anchor`, `cutoff_sensitive_near_miss`,
  `gold_chain_substitutability`, `gold_chain_not_unique`, `plausible_non_gold_answer` or
  `low_context_name_query`.
- **Affected unit:** `5ae048a255429924de1b708e|dense`.
- **This is the first primary use of `peripheral_passage_content_dilution`.** The gate had
  been applied seven times before, by D-023, D-025, D-026, D-027, D-029, D-031 and D-035,
  passing five of those times, and every pass stopped at secondary on one stated ground:
  the ablation ceiling with both required passages reduced to their cores still left one
  of them outside the cutoff. D-035 records that ceiling as 1 / 0.585251 and 7 / 0.460718.
  **That ground is measured here and does not hold**: the same two-sided ablation gives
  3 / 0.469751 and 1 / 0.549310, and its own length-matched control gives 863 / 0.144759
  and 871 / 0.143892. This is the eighth application and the sixth pass, and the fourth
  unit after D-026, D-029 and D-035 in which the gate passes on both required passages.
  It is also the eighth consecutive decision that registers no new descriptor, and the
  third to delete two or more provisional names at once, after D-031 and D-033.
- **Question:** `What movie did Pitof direct which had an action-adventure tie-in video
  game based off of it in 2004?` This is a bridge unit. `Catwoman (film)` states that
  Catwoman is a 2004 American action superhero film loosely based on the DC Comics
  character of the same name directed by Pitof, produced by Denise Di Novi and Edward
  McDonnell, written by John Rogers, John Brancato and Michael Ferris, with music by Klaus
  Badelt, and that it stars Halle Berry, Sharon Stone, Benjamin Bratt, Lambert Wilson,
  Frances Conroy and Alex Borstein. `Catwoman (video game)` states that Catwoman is an
  action-adventure tie-in video game based on the 2004 film of the same name based on the
  fictional character, and that it features the likeness of the film's lead actress, Halle
  Berry, though the character's voice is provided by actress Jennifer Hale. The answer is
  the film, so `Catwoman (film)` is the answer hop and `Catwoman (video game)` supplies the
  tie-in constraint. **The question names exactly one entity, `Pitof`, and that name is
  corpus-unique**: 1 of 4,937 indexed bodies contains it, and that body is the answer hop.
  The linking name `Catwoman` appears in 2 of 4,937 bodies, which are the two required
  passages, and appears nowhere in the question.
- **Verified implementation:** `all-MiniLM-L6-v2` used as a symmetric bi-encoder; only
  paragraph text is encoded and titles are excluded; mean pooling with an explicit
  row-wise L2 so that a dot product is a cosine; a 256-token sequence limit. The two
  required passages are 82 and 57 model tokens and the question is 26, so truncation is
  excluded on both sides. Cosine carries no collection statistic, which has two
  consequences used throughout: a subset ranking is the pooled ranking restricted to that
  subset, and every index-side removal probe is an arithmetic identity rather than a
  measurement (pit 19ai). Per-token contribution is not derivable on this backend and none
  is claimed (pit 18).
- **Exact reconstruction:** rebuilding the same 4,937-passage pooled index reproduces all
  50 stored top-50 titles in order, 0 of 50 mismatched, at a maximum absolute score error
  of 2.086e-07, so strong causal claims are supported. Complete-corpus ranks are
  263 / 0.244736 and 39 / 0.320936 against a rank-5 score of 0.396391. **Neither gold is
  absent from the corpus**, which is one of the two grounds for deleting
  `answer_entity_missing_both_methods` below.
- **Diagnostic scale:** 199 labelled rows on the same unchanged candidate set, of which 191
  are measured runs covering 188 distinct conditions, 3 of those being deliberate repeats
  across producers that reproduced the baseline and the title-indexing condition bit for
  bit, 3 tabulate the positions of passages this entry names, and 5 are `not_run` cells
  with reasons. The reproduction script carries 217 assertions and all pass.
- **The dilution gate passes on both required passages, in its strongest recorded form.**
  All four include conditions hold on each side. The pooling and scoring contract is
  verified from implementation rather than inferred, and both passages sit inside the
  sequence limit at 82 and 57 model tokens. On the answer hop, whose body is 60 words, a
  verbatim subset of its own query-relevant material gives 11 / 0.378848 at 22 words and
  2 / 0.469751 at 11 words, against a baseline of 263 / 0.244736; dropping only the cast
  sentence gives 187 / 0.264044 at 45 words, and an 8-word subset gives 1 / 0.514763. The
  length-matched controls, which keep the passage's subject name and carry no
  query-relevant word, improve nothing at any length: 864 / 0.144759 at 12 words,
  1052 / 0.124028 at 25 words, 921 / 0.137778 at 40 words and 788 / 0.153279 at 53 words,
  every one of them far below the untouched 263. On the constraint hop, whose body is 42
  words, the first sentence taken verbatim gives 3 / 0.450154 at 21 words and a 12-word
  subset gives 1 / 0.549310, against a baseline of 39 / 0.320936, while the controls give
  745 / 0.158364 at 20 words and 803 / 0.151917 at 23 words. **The decisive comparison is a
  matched pair rather than a curve endpoint**: 11 words of query-relevant material rank
  2 / 0.469751 and 12 words of non-relevant material from the same body rank
  864 / 0.144759.
- **The controls are decontaminated word by word, as D-035 requires.** Adding one single
  query-relevant word back into the 25-word answer-side control moves it several hundred
  rank positions while leaving it far below the baseline: the word `film` gives
  790 / 0.153217 and the year `2004` gives 808 / 0.151573, against 1052 / 0.124028 without
  either. The constraint-side control behaves the same way, 745 / 0.158364 becoming
  484 / 0.199321 when the single word `film's` is restored. The controls are therefore not
  passing the gate by accident of wording.
- **The two-sided ablation places both required passages inside the cutoff, and this is the
  first time that has happened.** Reducing both bodies to their minimal verbatim subsets
  gives 3 / 0.469751 and 1 / 0.549310; the answer hop's 11-word subset with the constraint
  hop's whole first sentence gives 2 / 0.469751 and 4 / 0.450154; shorter subsets still
  give 2 / 0.514763 and 1 / 0.541608. Replacing the same two rows with length-matched
  controls instead gives 863 / 0.144759 and 871 / 0.143892, and the two asymmetric cells
  confirm that each side's core rescues only its own side, 2 / 0.469751 with
  871 / 0.143892 and 864 / 0.144759 with 1 / 0.549310. The less aggressive pairing, both
  bodies cut to their query-relevant subsets rather than their minimal ones, does not
  double-recover at 12 / 0.378848 and 3 / 0.450154, so the ceiling depends on how far the
  ablation is taken and that dependence is reported rather than smoothed over.
- **The null control is reported as a measured residual rather than as equality.** Pit 25d
  asks a null control to show that substituting one matrix row equals re-encoding the
  corpus. Re-encoding each unchanged body into its own row reproduces the baseline pair
  263 / 0.244736 and 39 / 0.320936 to every printed digit, which is the sense in which
  D-026, D-029 and D-035 report their null controls; measured to the float, the largest
  absolute score difference over all 4,937 rows is 5.960e-08 on each side, because the
  batch encode behind the document matrix and the single-element encode behind a
  substituted row are not bit-identical. The equivalence is exact in the ranking and
  approximate in the last two digits of the float, and every ablation figure above sits
  many orders of magnitude above that residual.
- **The question's only name is a corpus-unique anchor that this encoder cannot use, and
  that fact is produced by the same dilution.** Reduced to the single word `Pitof`, the
  query ranks its sole bearer 1283 / 0.076500. A four-word descriptive control with no
  connection to the case, `a French film director`, ranks the same passage
  448 / 0.230280, so the bare corpus-unique name is 835 rank positions worse than a
  generic phrase; repeating it three times gives 1571 / 0.057080. Adding generic context
  helps rather than hurts, `directed by Pitof` giving 329 / 0.228811 and `Pitof director`
  297 / 0.214813. Other names written in the same body behave the same way, `Denise Di
  Novi` 418 / 0.170030, `John Brancato` 393 / 0.194881, `Klaus Badelt` 592 / 0.161732 and
  `Sharon Stone` 1014 / 0.128881. **The attribution is closed by repeating the probe
  against the un-diluted body**: the query `Pitof`, unchanged, ranks that passage
  2 / 0.330683 once its body is the 11-word subset and 1 / 0.391955 once it is the 8-word
  subset, and 894 / 0.095909 against the 12-word length-matched control; `directed by
  Pitof` gives 1 / 0.436933 against the 11-word subset. The same ablation moves a probe
  matching the removed material in the opposite direction, `Halle Berry` going from
  141 / 0.249922 to 426 / 0.183656, and the constraint side behaves identically, `Jennifer
  Hale` going from 31 / 0.307791 to 420 / 0.177707 while `tie-in video game` goes from
  85 / 0.227871 to 3 / 0.419730. The effect is therefore directional and content-specific
  rather than a brevity effect. **This gives D-029's open boundary its first mechanical
  account**: that entry recorded an anchor that exists in the query and in the passage,
  is corpus-unique, and still ranks its bearer 2202 / 4937, and left open whether "no
  anchor" and "an unusable anchor" belong to one descriptor. Here the unusable anchor is
  a consequence of the adopted primary, so no separate descriptor is needed for it.
- **One shared name gives a controlled contrast between the two bodies.** `Halle Berry` is
  written in both required passages. The same query ranks the 60-word answer hop
  141 / 0.249922 and the 42-word constraint hop 9 / 0.354602, a gap of 0.104681 in score
  and 132 rank positions, with the shorter and less padded body ahead.
- **`question_frame_semantic_crowding` is adopted as a secondary, and both directions of
  the crowding criterion agree.** The first half of the include rule holds on read text:
  all 38 non-gold passages above the constraint hop match the question's framing facets, a
  film, a video game, an adaptation or a director, and 0 of the 38 contain `Catwoman` and 0
  contain `Pitof`; the same two counts are 0 and 0 among the 261 above the answer hop, of
  which 245 carry a film word or a game word. The forward direction holds: the game clause
  alone reproduces 6 of the baseline top ten, the same clause with the year 6 of ten, and
  `a video game based on a film` 5 of ten, while the referring clause alone reproduces 1 of
  ten and the bare name 0 of ten. The reverse direction agrees: deleting the single word
  `Pitof` from the full question leaves 8 of the baseline top ten in place, at
  222 / 0.245012 and 18 / 0.352078. The third exclusion therefore does not fire, which is
  the reverse of D-035 and the same shape as D-025. **It is adopted as a composition and
  not as a causal claim**, following D-035, because on a bi-encoder no removal probe can
  supply causal evidence for a crowding descriptor.
- **Every index-side removal probe is an arithmetic identity, verified cell by cell.**
  Twenty-two removal cells were run and all twenty-two match
  `rank_after = rank_before − |dropped and ranked above it|` with the gold scores identical
  to the last bit. Dropping all 38 above the constraint hop gives 225 / 0.244736 and
  1 / 0.320936; dropping all 261 above the answer hop gives 2 / 0.244736 and 1 / 0.320936;
  the 16-passage video-game family gives 247 / 0.244736 and 23 / 0.320936 and its
  22-passage complement gives 241 / 0.244736 and 17 / 0.320936, the two differing only by
  their sizes; a size-matched null drawn from below the constraint hop leaves it at
  39 / 0.320936. The cumulative ladder runs 258, 253, 243, 224, 184, 104, 63, 23 and 2 on
  the answer hop for 5, 10, 20, 40, 80, 160, 200, 240 and 261 passages dropped. The
  identity also holds in the repaired state, where only 1 non-gold remains above the answer
  hop and dropping it gives 2. This is the second independent verification of pit 19ai
  after D-035, and it is why no crowding descriptor can be primary on this unit.
- **The only query-side lever on the crowding family points the other way.** Deleting the
  whole game clause, which is the cue that produces the competitor family, moves both
  required passages further from the cutoff, to 545 / 0.203382 and 937 / 0.150986 from
  263 / 0.244736 and 39 / 0.320936. The family is real and it is produced by the frame, but
  the required passages need that frame rather than being suppressed by it.
- **Title indexing is materially positive and by itself flips `any@5`, but the anchor
  reading of it is wrong.** The deployable corpus-wide condition gives 125 / 0.273863 and
  5 / 0.387651, putting the constraint hop inside the cutoff. Decomposing it on the two
  gold rows shows the gain does not come from the title's name: prepending the bare name
  `Catwoman` gives 260 / 0.247282 and 26 / 0.333190, close to inert, while prepending only
  the parenthetical disambiguator gives 91 / 0.292896 and 8 / 0.388039, and prepending the
  whole title gives 146 / 0.273863 and 8 / 0.387651, so restoring the name makes the answer
  side worse. The disambiguators are `(film)` and `(video game)`, which are the question's
  own facet words. `unindexed_title_name_anchor` therefore fails its second include
  condition at the first step, because neither title carries the query's anchor `Pitof`;
  this is the second unit after D-036 where a materially positive title condition has a
  mechanism other than a title-borne name (pit 19am), and the first where the alternative
  mechanism is isolated by a three-cell decomposition rather than argued from a length
  normalization side effect.
- **No non-oracle condition places both required passages inside the cutoff.** The search
  covered a 16-cell wording factorial run in two preprocessing states, a 8-cell NAME by
  GAME by YEAR component factorial, 14 reduced queries, 10 single-cue deletions, 12
  ceiling rewrites with and without title indexing, and 3 query splittings. The best
  deployable condition is title indexing at 125 / 0.273863 and 5 / 0.387651. The best
  condition of any non-oracle kind is a rewrite that presupposes a fact written only in the
  answer gold and is therefore not deployable under pit 19ab, giving 10 / 0.376168 and
  6 / 0.395653. Sliced as pit 19ak requires, by whether the condition preserves the
  question's referring expression word for word, the non-oracle double recoveries number
  0; the 10 conditions that do place both passages inside the cutoff are 6 oracle
  injections of the name `Catwoman` and 4 gold-targeted index-side ablations.
- **Query splitting fails in all three forms.** Splitting the question into an answer-side
  query and a constraint-side query and taking the union of the two top-5 sets contains
  neither required passage under any of the three splittings; the best single side reaches
  15 / 0.356396 on the constraint hop and 388 / 0.207485 on the answer hop.
- **The wording of the question is not the mechanism, in either preprocessing state.** The
  A by B by C repair, which fixes the non-standard `based off of it`, swaps the head noun
  and moves the year into the game phrase, was run in the baseline state and again under
  title indexing, 16 cells in all. In the baseline state the answer hop stays within
  244 to 273 and the constraint hop within 33 to 63; under title indexing they stay within
  95 to 125 and 5 to 10. Running the second state is what shows the inertness is not
  masked by the first (pit 19ah).
- **The single-fact controls price the facts the question actually needs, and they are not
  enough.** Deleting `directed by Pitof` from the answer hop's body and changing nothing
  else moves it from 263 / 0.244736 to 553 / 0.187165; deleting `2004` gives
  334 / 0.226723; replacing `Pitof` with `the director` gives 407 / 0.210516. On the
  constraint hop, deleting `action-adventure tie-in` gives 88 / 0.293724 and deleting the
  2004-film clause gives 77 / 0.297823. The queried facts do carry score, so the failure is
  not that the passages omit the answer; what determines the rank is the rest of each body.
- **The single-factor oracle-name test passes in six forms and still loses the primary.** Appending the
  answer title gives 2 / 0.586489 and 1 / 0.647057, the constraint title 2 / 0.553469 and
  1 / 0.640847, both titles 2 / 0.610733 and 1 / 0.693891 and the bare name 2 / 0.569072
  and 1 / 0.631444; the query reduced to `Catwoman` alone gives 2 / 0.769825 and
  1 / 0.788529. Pit 19g's premise is verified, the injected name being written verbatim in
  both bodies and in only those two of 4,937, and pit 24b's is too, the name appearing in
  no surface form anywhere in the question, so the condition is not degenerate. This is the
  thirteenth application of the criterion and the seventh pass. It loses for the reason
  D-028 established and pit 15 states: a non-oracle-side result outranks an oracle one, and
  here an index-side repair that leaves the query untouched word for word double-recovers.
- **`cross_passage_conjunction_unresolved` is not adopted, on the D-026 route.** Two of its
  three positive legs fail. The matched-token leg has no Dense analogue, as D-025 records.
  The opposite-sign leg is 2 of 13 single factors, below the 4 of 19 on which D-026 refused
  the same name, and far below 10 of 19 at D-024, 10 of 20 at D-025, 8 of 22 at D-031 and 8
  of 14 at D-035. The third leg has the wrong shape: the linking name `Catwoman` is written
  in both required bodies rather than only in the other one, so neither passage has to
  resolve anything in the other and carry it across; what is missing is that the question
  never contains that name. The D-026 route then fires outright, a single anchor lifting
  both sides, `Catwoman` alone giving 2 / 0.769825 and 1 / 0.788529, the answer title alone
  1 / 0.821070 and 2 / 0.775806 and the constraint title alone 2 / 0.707477 and
  1 / 0.805008; this is the opposite sign to D-025, where the same probe demoted the other
  side to 2158. **The D-028 route explicitly does not fire and the refusal does not rely on
  it**: no non-oracle query condition double-recovers. The first exclusion, one passage
  supplying a complete answer, is recorded as a boundary and is not used as a ground: the
  answer hop alone names Pitof, the year and the medium, and `pitof` occurs in only that
  one body, so it locates the answer, but it never states that a tie-in game exists, so the
  question's second constraint cannot be checked from it. The decisive point is that the
  name is not adopted even under its own reading, because both sides are separately
  unreachable, the corpus-unique name giving 1283 / 0.076500 and the referring clause
  436 / 0.189887, while an index-side change that leaves the question untouched puts both
  inside the cutoff.
- **`description_only_bridge_entity` is not adopted, on the D-028 route.** Its definition
  requires that the question leave no unique entity-name anchor, and this question supplies
  one, `Pitof`, unique in the corpus and written in the required passage it points at. More
  decisively, the condition that double-recovers is an index-side one with the query
  unchanged word for word, which is exactly what D-028 treats as showing that the
  description itself is sufficient. Passing the oracle-name criterion in six forms does not
  override that, by pit 15.
- **`broad_adaptation_topic_crowding` is deleted rather than registered.** It names the same
  set of competitors as the registered `question_frame_semantic_crowding` under a narrower
  label, the broad adaptation topic being one of that descriptor's framing facets, and this
  unit is its only holder anywhere on disk. This follows the ground on which D-031 deleted
  `subject_associate_crowding` and D-033 deleted `cross_entity_relation_unresolved`, that a
  provisional name duplicating a registered one is deleted rather than registered.
- **`answer_entity_missing_both_methods` is deleted on the two independent grounds D-033
  used for the same name.** First, it states gold missingness, which is a result and not a
  mechanism (pit 17, D-003). Second, it is factually wrong: the passage it calls missing is
  in the corpus, at 263 / 0.244736 on this retriever and 3241 / 5.756382 on BM25, and
  `not_in_top50` describes only the stored window (pit 7). **This unit is the name's last
  holder**, so the deletion clears it from the vocabulary; D-033 deleted it on
  `5abcc96c5542996583600492|bm25` for the same two reasons.
- **`cutoff_sensitive_near_miss` is not adopted and no band edge moves.** The two required
  passages sit 0.151655 and 0.075455 below the rank-5 score of 0.396391, which is 38.259
  and 19.036 percent, both inside the established excluded band. There is no cliff to
  appeal to below the cutoff: the successive differences from rank 1 to rank 10 are
  0.007612, 0.017155, 0.001583, 0.048638, 0.004194, 0.003336, 0.002790, 0.000182 and
  0.005142, so the largest step in the region sits between rank 4 and rank 5, above the
  cutoff rather than below it.
- **No substitute exists for either hop and there is no complete non-gold answer.** The
  token `pitof` occurs in 1 of 4,937 indexed bodies, which is the answer hop itself, so
  nothing else in the corpus can answer which film Pitof directed. The token `catwoman`
  occurs in 2 of 4,937, which are the two required passages, so nothing else states that a
  2004 Catwoman film had an action-adventure tie-in game. Neither token occurs in any of
  the 261 passages above the answer hop. `Tron Evolution: Battle Grids` at 2 / 0.463768
  carries the phrase `action-adventure tie-in video game` word for word but is based on a
  2010 film and never mentions Pitof, so it is a partial-match competitor and not an
  evidence-bearing substitute (pit 19b). `gold_chain_substitutability`,
  `gold_chain_not_unique` and `plausible_non_gold_answer` are all refused on this reading.
- **Corpus setting does not carry the failure: per-question failure excludes pooling, and the two settings agree on both metrics.**
  Pooled gives `any@5` 0 and `full@5` 0 at 263 / 0.244736 and 39 / 0.320936; the official
  per-question window of 10 passages gives `any@5` 0 and `full@5` 0 at 10 / 0.244736 and
  7 / 0.320936. Restricting the pooled scores to those same 10 reproduces both gold scores
  bit for bit and reproduces the official window exactly, the eighth verification of the
  Dense restriction property D-025 established. This is the fourth unit whose two settings
  agree on both metrics, after D-021 on BM25 and D-027 and D-031 on Dense. Of the three
  paths by which corpus setting can move a metric, the added-competitor path is excluded
  because dropping only the passages pooling introduced above each gold, 253 and 32 of
  them, returns exactly the per-question ranks 10 and 7, which on this backend is the
  restriction identity rather than a measurement; the idf-scale path cannot apply to a
  bi-encoder; and the annotator-supplied path does hold, this question's own 8 distractors
  standing above the constraint hop 6 times and above the answer hop 8 times, with the
  answer hop last of the ten in its own window. Recorded as provenance under D-003 and not
  promoted to a causal category.
- **Comparison retriever, reachability only.** BM25 over the same pooled corpus places the
  two required passages at 3241 / 5.756382 and 2 / 34.118716, and over this question's 10
  at 10 / 1.352624 and 3 / 4.367514. One implementation fact is worth recording because it
  shows the two backends fail for unrelated reasons: **`df(pitof)` is 0 in the BM25 index**,
  because the answer hop's body writes `Pitof,` and that run tokenizes with
  `text.lower().split()` and strips no boundary punctuation, so the query token `pitof`
  contributes nothing and the query reduced to that name gives 2698 / 0.000000. Per pit 16
  this is not offered as a cause of the Dense outcome and the two score scales are not
  comparable; it establishes only that the passage is present in the corpus and that the
  lexical failure has a different mechanism. **The example has no BM25 analytical unit in
  the queue**, so this preprocessing fact has no unit of its own to belong to.
- **`not_run` cells.** Five, each with a reason recorded in the results file: the BM25
  preprocessing factorial, because this unit is Dense and the same example has no BM25
  unit; per-token score decomposition, which is not derivable on a bi-encoder; index-side
  removal probes read as causal evidence for a crowding descriptor, which pit 19ai forbids
  and which is why the 22 cells that were run are reported as identity verification; the
  statistics-matched removal control of pit 19ad, which exists because dropping documents
  changes idf and avgdl on BM25 and has no analogue where cosine carries no collection
  statistic; and a deployable query rewrite reaching both passages, which is reported as a
  measured ceiling rather than an untried cell.
- **Attribution boundary.** What is licensed is the passage-level statement that removing
  the named material from each required body raises that body's similarity to this query on
  this unchanged candidate set. Not licensed: any claim that the encoder attended to,
  weighted or averaged away any token; any reading of the gold-targeted ablations as a
  deployable repair, since they require knowing which passage is required; any causal claim
  for the competitor family, whose composition is read from passage text while every
  removal cell is an identity; and any use of the BM25 figures as a cause of the Dense
  outcome.
- **Confidence:** medium-high. Supporting it: an exact baseline reconstruction, a gate that
  passes on both sides with a four-point control curve and word-level decontamination, a
  two-sided ablation that double-recovers against a control that does not, and a closing
  attribution for the inert anchor. Limiting it: the double recovery requires the more
  aggressive of the two ablation levels, the less aggressive pairing giving 12 / 0.378848
  and 3 / 0.450154; the adopted primary is a diagnostic rather than a deployable repair by
  its own registered attribution boundary; and the exact word count at which the answer hop
  crosses the cutoff was not bracketed between 11 and 22 words.
- **Audit questions registered, not resolved.** Whether a dilution primary needs a
  primary-use contract, given that the descriptor's own attribution boundary calls it a
  diagnostic while a primary is normally read as a mechanism. And whether D-029's open
  boundary between "no anchor" and "an unusable anchor" still needs a descriptor of its
  own, given that this unit attributes the unusable anchor to the adopted primary.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ae048a255429924de1b708e.md`.

## D-038 - Reclassify the Cocoa Krispies / Kellogg's Dense unit as cross passage conjunction unresolved and delete one provisional name

- **Date:** 2026-08-07
- **Status:** active
- **Decision:** For `5ae1801955429901ffe4aec4|dense`, replace the provisional primary
  `partial_bridge_only` with `cross_passage_conjunction_unresolved`, and adopt three
  secondaries, each scoped: `peripheral_passage_content_dilution` on
  `Adventures of Superman (TV series)` only, `cutoff_sensitive_near_miss` on `Kellogg's`
  only, and `same_topic_passage_distractor` on `Superman: Tower of Power`, `Twisties` and
  `General Mills` only. Delete the provisional name `partial_bridge_only` rather than
  registering it. Register no new descriptor. Use
  `peripheral_passage_content_dilution` as the closest competitor. Do not adopt
  `gold_chain_substitutability`, `question_frame_semantic_crowding`,
  `description_only_bridge_entity`, `gold_chain_not_unique`, `plausible_non_gold_answer`,
  `low_context_name_query`, `unindexed_title_name_anchor`,
  `generic_person_semantic_neighborhood` or `compound_two_sided_crowding`.
- **Affected unit:** `5ae1801955429901ffe4aec4|dense`.
- **This is the fourth primary use of `cross_passage_conjunction_unresolved`**, after
  D-022 and D-024 on BM25 and D-025 on Dense, and the second Dense primary use. It is the
  ninth consecutive decision that registers no new descriptor, and the fourth to delete a
  provisional name outright, after D-031, D-033 and D-037.
- **Question:** `Where is the Cocoa Krispies and former Superman sponsor located?` This is
  a bridge unit. `Adventures of Superman (TV series)` is 185 model tokens over six
  sentences, of which exactly one carries anything the question asks for,
  `It was sponsored by cereal manufacturer Kellogg's.`; the rest are the creators, the
  filming location, the syndication and air dates, the black-and-white and colour seasons,
  and the 1965 colour broadcast. `Kellogg's` is 166 model tokens over four sentences: the
  first states that the company is headquartered in Battle Creek, Michigan and carries an
  alias parenthetical, the third lists brands including `Cocoa Krispies`. The bridge entity
  is therefore identified by two coordinated referring expressions and **never named**: the
  question contains no form of `Kellogg`. The answer hop alone satisfies one of the two
  constraints and states the location; the only intermediate fact written nowhere else is
  that the former Superman sponsor is Kellogg's.
- **Verified implementation:** `all-MiniLM-L6-v2` used as a symmetric bi-encoder; only
  paragraph text is encoded and titles are excluded; mean pooling with an explicit row-wise
  L2 so that a dot product is a cosine; a 256-token sequence limit; passages scored
  independently, with no reranker and no cross-passage or iterative-hop reasoning. The two
  required passages are 185 and 166 model tokens and the question is 14, so truncation is
  excluded on both sides. Cosine carries no collection statistic, with the two consequences
  used throughout: a subset ranking is the pooled ranking restricted to that subset, and
  every index-side removal probe is an arithmetic identity rather than a measurement
  (pit 19ai). Per-token contribution is not derivable on this backend and none is claimed
  (pit 18).
- **Exact reconstruction:** rebuilding the same 4,937-passage pooled index reproduces all
  50 stored top-50 titles in order, 0 of 50 mismatched, at a maximum absolute score error
  of 3.576e-07, so strong causal claims are supported. Complete-corpus ranks are
  173 / 0.225424 and 11 / 0.345068 against a rank-5 score of 0.363764. **Neither gold is
  absent from the corpus**; `not_in_top50` describes the stored window only (pit 7).
- **Diagnostic scale:** 146 labelled rows on the same unchanged candidate set, of which 138
  are measured runs covering 135 distinct conditions, 3 of those being deliberate repeats
  of the baseline across four producers that reproduced it bit for bit, 2 tabulate the
  positions of passages this entry names, and 6 are `not_run` cells with reasons. The
  reproduction script carries 214 assertions and all pass.
- **The two coordinated referring expressions are antagonistic, and that is the whole
  measurement.** Each one alone places its own required passage inside the cutoff and
  drives the other one out: `former Superman sponsor` gives 2 / 0.415715 and
  2046 / 0.070734, `Cocoa Krispies` gives 4713 / -0.087899 and 2 / 0.404215. Put together
  in the question as annotated they give 173 / 0.225424 and 11 / 0.345068, and deleting
  either one from the question restores its partner's side while destroying the other:
  deleting `Cocoa Krispies` gives 3 / 0.444093 and 1554 / 0.092815, deleting `Superman`
  gives 4481 / -0.058135 and 3 / 0.413657. Dropping the interrogative frame and keeping
  both referring expressions gives 108 / 0.229726 and 5 / 0.350304, which is the best any
  reduced form of the question reaches on the constraint side while the answer side stays
  in. **8 of 16 single factors carry opposite signs across the hops**, counting one change
  applied to the whole question or one index-side change; that ratio matches D-025's 10 of
  20, sits above D-024's 10 of 19 in proportion and far above the 4 of 19 on which D-026
  refused this name.
- **Per-side reachability holds under non-oracle queries, so neither passage is
  unreachable on its own.** On the constraint hop, the question's own verbatim
  sub-phrase `former Superman sponsor` gives 2 / 0.415715, the single word `Superman`
  gives 4 / 0.463022 and `Superman television series sponsor` gives 1 / 0.612244. On the
  answer hop, `sponsored by cereal manufacturer` gives 1 / 0.592832,
  `cereal manufacturer headquarters` gives 2 / 0.601672 and `Cocoa Krispies` gives
  2 / 0.404215. This is D-025's leg and it holds in its strongest form so far, both sides
  being reachable at rank 1 or 2 by wording drawn from the question itself.
- **The D-026 route does not fire: no single anchor lifts both sides.** Five were measured
  and every one is one-sided, with the other hop pushed between 2731 and 4426. `Kellogg's`
  alone gives 4426 / -0.054776 and 1 / 0.704330; the constraint hop's own title alone gives
  1 / 0.699497 and 3930 / -0.037222; `Adventures of Superman` alone gives 1 / 0.605818 and
  4096 / -0.039585; `Cocoa Krispies` alone gives 4713 / -0.087899 and 2 / 0.404215; and
  `Superman` alone gives 4 / 0.463022 and 4085 / -0.030170. This is the same sign as D-025,
  where the same probe demoted the other side to 2158, and the opposite of D-037, where a
  single anchor lifted both.
- **The D-028 route of pit 19s does not fire either.** Forty-eight non-oracle query
  conditions were scanned, 24 queries each with and without title indexing, and none places
  both required passages inside the cutoff. The best of them presupposes facts written only
  in the golds and is therefore not deployable in the sense of pit 19ab,
  `Where is the cereal company that sponsored the Superman television series located?`
  giving 1 / 0.559604 and 9 / 0.360985; the best strictly deployable rewrite,
  `Where is the headquarters of the cereal company that makes Cocoa Krispies and formerly
  sponsored Superman?`, gives 154 / 0.242010 and 2 / 0.527444, and title indexing alone
  gives 135 / 0.226319 and 9 / 0.328467. **The only query-side condition anywhere in this
  study that double-recovers is appending both gold titles**, 2 / 0.416027 and
  1 / 0.464131, which is a pure oracle and by pit 15 is not a repair. Resolving the
  conjunction by hand behaves exactly as the descriptor predicts: supplying the bridge
  entity's name lifts the answer hop and abandons the constraint hop,
  `Where is Kellogg's located?` giving 4115 / -0.049557 and 1 / 0.662501,
  `Where is Kellogg's headquartered?` 3877 / -0.034668 and 1 / 0.683682,
  `Where is the Kellogg Company located?` 4213 / -0.047955 and 1 / 0.692879 and
  `Kellogg's headquarters` 4218 / -0.051305 and 1 / 0.633972.
- **Neither exclusion fires.** No single passage supplies a complete answer: the answer hop
  states the location and lists `Cocoa Krispies` among its brands but never says the
  company sponsored Superman, so the question's second constraint cannot be checked from
  it, and the constraint hop names the sponsor but no location. No evidence-bearing
  substitute completes the chain inside the evaluated set: `Cocoa Krispies` at
  2 / 0.406143 states that the cereal is produced by Kellogg's, but the location is written
  in exactly 1 of 4,937 indexed bodies, which is the answer hop itself at 11 / 0.345068,
  outside the cutoff. The linking name `kellogg` occurs in 3 of 4,937 bodies, the two
  required passages and `Cocoa Krispies`; `battle creek` in 1; `adventures of superman`
  in 1; `cocoa krispies` in 2. The implementation is verified to score passages
  independently.
- **The dilution gate passes on the constraint hop, in its strongest recorded form for a
  single side.** All four include conditions hold there. The contract is verified from
  implementation and the body sits inside the sequence limit at 185 model tokens. The
  controlled ablation to verbatim subsets of the passage's own query-relevant material
  moves 173 / 0.225424 to 1 / 0.452921 at 7 words, 1 / 0.509545 at 15 words,
  1 / 0.502081 at 23 words, 4 / 0.383756 at 31 words, 13 / 0.337426 at a different 31 words
  and 51 / 0.275368 at 58 words. **The length-matched controls that carry no query-relevant
  word improve nothing at any length and move the passage hundreds of positions the wrong
  way**: 425 / 0.178357 at 9 words, 967 / 0.129091 at 11 words and 2517 / 0.053330 at 12
  words. **The decisive comparison is a matched pair rather than a curve endpoint**: 7 words
  of query-relevant material rank 1 / 0.452921 and 9 words of non-relevant material from
  the same body rank 425 / 0.178357, a difference of 0.274563 in score.
- **The controls are decontaminated word by word, as D-035 requires, and here that step
  decides the verdict rather than merely confirming it.** Six controls built from the
  passage's non-relevant sentences do improve the rank, to 37 / 0.288547 at 8 words,
  135 / 0.237579 at 16 words, 117 / 0.243064 and 144 / 0.236000 at 24 words,
  147 / 0.234285 at 51 words and 170 / 0.226848 at 40 words, and every one of them retains
  the query word `Superman`. Removing just the two words `of Superman` from the 24-word
  control moves it from 144 / 0.236000 to 569 / 0.160981, a change of 0.075020 in score and
  425 rank positions, which is why the decontaminated controls above are the ones the gate
  is read on. The control curve is also not monotone in length, running 425, 967, 2517,
  135, 117, 144, 170, 172, 147 and 208 at 9, 11, 12, 16, 24, 24, 40, 44, 51 and 57 words,
  so no single control point could have been read either way (D-026).
- **The directional control of pit 19ao holds on the constraint hop.** The same ablation
  that lifts a probe matching the retained material lowers probes matching the removed
  material: `sponsored by cereal manufacturer` goes from 2357 / 0.031166 to 1 / 0.889812,
  while `Jerry Siegel and Joe Shuster` goes from 1510 / 0.119830 to 2535 / 0.064414 and
  `filmed in black-and-white and color` from 168 / 0.267384 to 1617 / 0.099776. A brevity
  effect cannot produce a sign that depends on what the probe matches.
- **The gate fails on the answer hop, on the second include condition outright.** Reducing
  that body to its single query-relevant sentence, the one that states the answer, gives
  89 / 0.254490 against a baseline of 11 / 0.345068, so the controlled ablation makes the
  rank worse; the same clause without the alias parenthetical gives 12 / 0.334115. The
  third condition fails as well: a control that retains only the brand sentence gives
  1 / 0.454983 at 30 words, and even after removing both `Rice Krispies` and
  `Cocoa Krispies` from it word by word it still improves the rank, to 5 / 0.365993 at 26
  words. The other two controls do not improve it, 36 / 0.284072 at 20 words and
  47 / 0.276768 at 32 words. This is the D-025 and D-031 direction and the conservative
  reading is taken: **the descriptor is scoped to the constraint hop alone**, the split
  D-027 used.
- **The two-sided ceiling with gate-licensed edits leaves the answer hop outside the
  cutoff, which is the ground on which this descriptor does not take the primary.**
  Ablating the constraint hop alone gives 1 / 0.509545 and 12 / 0.345068. Combining that
  with the only answer-side edit that helps, deleting the alias parenthetical, gives
  1 / 0.509545 and 6 / 0.376585, and the more aggressive constraint-side subset gives
  1 / 0.452921 and 6 / 0.376585; the answer-side edit on its own gives 173 / 0.225424 and
  5 / 0.376585. **One cell does double-recover and it is reported rather than smoothed
  over**: the constraint hop at 15 words together with a 43-word answer-side subset that
  reaches through the brand list to `Cocoa Krispies` gives 1 / 0.509545 and 3 / 0.406656.
  It is not licensed by this descriptor, because on that side the gate fails on its second
  condition, and it is not a deployable repair in any case (pit 19d). The asymmetric cells
  confirm that each side's edit rescues only its own side, 1 / 0.452921 with 37 / 0.284072
  and 117 / 0.243064 with 89 / 0.254490, and both controls together give 117 / 0.243064 and
  36 / 0.284072. This is the same ground D-023, D-026, D-027, D-029 and D-035 recorded, and
  the reason D-037 broke it does not apply here: there the gate passed on both sides.
- **The single-fact controls price the facts the question needs, and the answer hop's
  rank turns out not to depend on the answer at all.** Deleting the sponsorship sentence
  from the constraint hop and changing nothing else moves it from 173 / 0.225424 to
  315 / 0.194534, and replacing `Kellogg's` in it with `a company` gives 277 / 0.201155, so
  the fact does carry score and keeping it is still not enough. On the answer hop, deleting
  the entire clause `headquartered in Battle Creek, Michigan, United States` leaves the
  rank at 11 / 0.344304, **unchanged to the position and 0.000764 in score**: that
  passage's rank is very nearly independent of whether it states the answer. Deleting
  `Cocoa Krispies, ` from its brand list gives 14 / 0.326893, deleting the whole brand
  sentence gives 26 / 0.300536, and **deleting only the alias parenthetical
  `(also Kellogg's, Kellogg, and Kellogg's of Battle Creek)` gives 5 / 0.376585 and flips
  `any@5` by itself**, worth 0.031517 in score. This last figure is recorded as a boundary
  and not used to support the dilution gate, because what it removes is query-relevant
  material rather than peripheral material, which is the opposite direction from the one
  the include rule describes.
- **The null control is reported as a measured residual rather than as equality.**
  Re-encoding each unchanged body into its own row reproduces the baseline pair
  173 / 0.225424 and 11 / 0.345068 to every printed digit, which is the sense D-026, D-029,
  D-035 and D-037 use; measured to the float, the largest absolute score difference over
  all 4,937 rows is 5.960e-08 for the constraint hop, 8.941e-08 for the answer hop and
  8.941e-08 for both together. Every ablation figure above sits many orders of magnitude
  above that residual.
- **Every index-side removal probe is an arithmetic identity, verified cell by cell.**
  Fourteen removal cells were run and all fourteen match
  `rank_after = rank_before - |dropped and ranked above it|` with the gold scores identical
  to the last bit. Dropping all 171 non-golds above the constraint hop gives
  2 / 0.225424; dropping all 10 above the answer hop gives 1 / 0.345068; the 68-passage
  location-word family above the constraint hop gives 105 / 0.225424 and its 103-passage
  complement gives 70 / 0.225424, the two differing only by their sizes; a 42-passage
  food-word family gives 131 / 0.225424. The cumulative ladder runs 168, 163, 153, 133, 93
  and 13 for 5, 10, 20, 40, 80 and 160 passages dropped. This is the third independent
  verification of pit 19ai after D-035 and D-037, and it is why no crowding descriptor can
  be primary on this unit and why the one that is adopted is adopted as a composition.
- **`same_topic_passage_distractor` is adopted for three of the ten passages above the
  answer hop, and the other seven are named as not covered.** On read text,
  `Superman: Tower of Power` at 8 / 0.353345 carries the question's words `Superman`,
  `former` and `located` in twenty-two words but is a drop tower ride and names no sponsor;
  `Twisties` at 9 / 0.350352 is a snack-food brand with an owner history and no connection
  to either required fact; `General Mills` at 10 / 0.346669 is an American multinational
  food company with a headquarters and a brand list that includes `Cocoa Puffs` but neither
  `Cocoa Krispies` nor any Superman sponsorship. Each verifies both halves of the include
  rule and none of the three exclusions fires. Not covered: `Cocoa Krispies` at
  2 / 0.406143, which is evidence-bearing for one link and is treated under pit 19b rather
  than as a distractor, and six passages whose only connection is the location frame,
  `Hero Certified Burgers` 1 / 0.414047, `Schwartz's` 3 / 0.383988,
  `The Works (restaurant)` 4 / 0.377530, `Tim Hortons` 5 / 0.363764,
  `Spencer Gifts` 6 / 0.357795 and `Digital Media Factory` 7 / 0.357676, for which the
  third exclusion fires. Following D-035 this is **adopted as a composition and not as a
  causal claim**, because every removal cell on this backend is an identity.
- **`question_frame_semantic_crowding` is not adopted, and the reason is measured in both
  directions.** The second half of the include rule fails outright: the frame alone does
  not reproduce the neighbourhood. `Where is it located?` reproduces 1 of the baseline top
  ten at 3507 / -0.012833 and 1318 / 0.089585, `Where is the sponsor located?` 1 of ten at
  3166 / 0.017899 and 543 / 0.165542, `Where is the company located?` 2 of ten at
  4095 / -0.029858 and 79 / 0.309746, and the bare word `located` 2 of ten at
  4820 / -0.087862 and 1085 / 0.106555. The referring expressions do reproduce it:
  `Cocoa Krispies` alone gives 4 of ten and both referring expressions without the frame
  give 6 of ten. Reverse, deleting `Cocoa Krispies` from the full question leaves 2 of ten
  while deleting `Superman` leaves 6 of ten. The competition is therefore produced by a
  decisive referent cue rather than by the framing, which is what the third exclusion
  names; this is the reverse of D-037 and the same shape as D-035. Read text agrees that
  the family is not a frame family in the D-037 sense either: 2 of the 10 passages above
  the answer hop contain `cocoa` or `krispies` and 1 contains `superman`, so the count of
  competitors free of the decisive referent wording is not 0 of 10.
- **`description_only_bridge_entity` is not adopted, on the D-028 route.** The inclusion
  rule is met in the D-029 form, neither required entity being named and the bridge entity
  identified only by two descriptions, and the single-factor oracle-name test fails:
  appending the constraint hop's title gives 1 / 0.483498 and 97 / 0.244636 and appending
  the answer hop's title gives 556 / 0.151134 and 1 / 0.542954, neither double-recovering.
  Pit 19g's premise is verified, each injected title ranking the passage it names first on
  its own, 1 / 0.699497 and 1 / 0.704330. Pit 24b's premise is only half met and that is
  recorded rather than glossed: the word `Superman` is already in the question, so the
  constraint-side injection is partly degenerate, appending `Adventures of Superman` alone
  giving 2 / 0.391687 and 43 / 0.267094, while the answer-side injection is not degenerate
  at all because no form of `Kellogg` appears in the question. The descriptor is
  nevertheless refused because the absence of a name is not the binding constraint on
  either side: the question's own verbatim sub-phrase reaches the constraint hop at
  2 / 0.415715 and a two-word phrase reaches the answer hop at 2 / 0.404215, and an
  index-side change with the query untouched word for word reaches the constraint hop at
  1 / 0.452921. This is the ground D-028 established and D-036 reused.
- **`cutoff_sensitive_near_miss` is adopted for the answer hop only and no band edge
  moves.** The two required passages sit 0.138340 and 0.018696 below the rank-5 score of
  0.363764, which is 38.030 and 5.140 percent. The nearer figure lies inside the accepted
  band of 0.281 to 5.464 percent and the farther one inside the excluded band of 9.431 to
  53.000 percent, so both are inside established bands and neither edge moves. The
  no-substitute condition D-022 introduced is met, `battle creek` occurring in exactly 1 of
  4,937 bodies which is that passage itself. **This entry carries two statements of D-025's
  split rule that do not agree, and D-036's resolution is followed**: D-025, D-026, D-032
  and D-036 adopted the descriptor for the near hop while the far hop sat inside the
  excluded band, D-035 restates the rule as forbidding the descriptor for the whole unit,
  and D-036 followed the landed adoptions and referred the wording to the vocabulary audit.
  The D-025 boundary is recorded again: with the other hop 38.030 percent below the cutoff,
  this entry can describe only the `any@5` outcome. No cliff can be cited, the successive
  differences from rank 1 to rank 10 being 0.007904, 0.022156, 0.006458, 0.013765,
  0.005969, 0.000119, 0.004331, 0.002993 and 0.003683, the largest step in the region
  sitting between rank 2 and rank 3, above the cutoff rather than below it. The
  counter-evidence this entry has weighed since D-022, the cumulative index-side removal
  ladder, is unavailable in principle on a bi-encoder (D-035); what is available instead is
  that a single deletion inside the passage's own body, of the alias parenthetical, already
  gives 5 / 0.376585 and flips `any@5`.
- **`gold_chain_substitutability` is withheld and the tension is recorded as an audit
  question.** `Cocoa Krispies` at 2 / 0.406143 states that the cereal is produced by
  Kellogg's, which names the unnamed bridge entity and links it to one of the question's
  two constraints, the shape D-023 adopted while recording that its substitute verified
  only one of two constraints. It is withheld because the fact it supplies is not the
  required intermediate fact of either annotated gold: the constraint hop's fact is the
  Superman sponsorship, which that body does not state, and the answer hop's decisive fact
  is the location, which it omits, so the exclusion for omitting the decisive fact fires.
  Adopting it would change no metric in any case, because the location is written only in
  the answer hop at 11 / 0.345068, outside the cutoff, which is D-025's recorded boundary
  on the position of a substitute. Whether a passage that reaches the same bridge entity by
  a different one of the question's constraints counts under this rule is registered for
  the vocabulary audit and is not settled here.
- **`partial_bridge_only` is deleted rather than registered, on two independent grounds.**
  First, it states an outcome shape, that only half the bridge was retrieved, rather than a
  mechanism, which is pit 17 and D-003; this is the ground D-033 and D-037 used to delete
  `answer_entity_missing_both_methods` and D-031 used for `subject_associate_crowding`.
  Second, the shape it names is a consequence of the adopted primary and is measured as
  such above: each referring expression alone reaches its own side at 2 / 0.415715 and
  2 / 0.404215 and the two together reach neither. **This unit is the name's only holder in
  the working vocabulary**, so the deletion clears it; the preserved inventory in the
  vocabulary audit keeps it, as it keeps every deleted name.
- **Title indexing is inert on the metrics and is recorded as such.** The deployable
  corpus-wide condition gives 135 / 0.226319 and 9 / 0.328467 from 173 / 0.225424 and
  11 / 0.345068. Both ranks improve slightly, **the answer hop's score falls by 0.016601**,
  and neither `any@5` nor `full@5` changes, so it is classed with the inert-or-negative
  measurements rather than with the materially positive ones of D-028 and D-036. Combined
  with the two best query rewrites it gives 134 / 0.239401 and 1 / 0.509617, and
  1 / 0.564265 and 10 / 0.344878, so it does not turn either of them into a double
  recovery.
- **Corpus setting: the two corpus settings disagree on `any@5`, and the difference is
  entirely the competitors pooling adds.** This is the tenth unit in which the two corpus
  settings disagree. Pooled gives `any@5` 0 and `full@5` 0 at 173 / 0.225424
  and 11 / 0.345068; the official per-question window of 10 passages gives `any@5` 1 and
  `full@5` 0 at 6 / 0.225424 and 3 / 0.345068. Restricting the pooled scores to those same
  10 reproduces the official window exactly, title for title, and reproduces both gold
  scores to every printed digit at a largest absolute difference of 2.980e-08 over the ten,
  which is the ninth verification of the Dense restriction property D-025 established. Of
  the three paths by which corpus setting can move a metric, the added-competitor path
  holds, only 2 of the 10 passages above the answer hop coming from this question's own
  window; the idf-scale path cannot apply to a bi-encoder; and the annotator-supplied path
  holds in part, this question's own 8 distractors standing above the constraint hop 4
  times and above the answer hop 2 times. Recorded as provenance under D-003 and not
  promoted to a causal category (pit 17).
- **Comparison retriever, reachability only.** BM25 over the same pooled corpus places the
  two required passages at 6 / 17.470717 and 13 / 16.030646, and over this question's 10 at
  2 / 3.969599 and 6 / 2.700103, so it reaches both inside the stored window and neither
  inside the cutoff. Per pit 16 this is not offered as a cause of the Dense outcome and the
  two score scales are not comparable. One implementation fact is recorded because it shows
  the backends fail differently: **`df(krispies)` is 0 in the BM25 index**, because both
  bodies write `Krispies,` and that run tokenizes with `text.lower().split()` and strips no
  boundary punctuation, while `df(superman)` is 3, `df(kellogg's)` is 1, `df(cocoa)` is 6
  and `df(sponsor)` is 6. **The example has no BM25 analytical unit in the queue**, so this
  preprocessing fact has no unit of its own to belong to.
- **`not_run` cells.** Six, each with a reason recorded in the results file: the BM25
  preprocessing factorial, because this unit is Dense and the same example has no BM25
  unit; per-token score decomposition, which is not derivable on a bi-encoder; index-side
  removal probes read as causal evidence for a crowding descriptor, which pit 19ai forbids
  and which is why the 14 cells that were run are reported as identity verification; the
  statistics-matched removal control of pit 19ad, which has no analogue where cosine
  carries no collection statistic; a deployable query rewrite reaching both passages, which
  is reported as a measured ceiling over 48 non-oracle conditions rather than as an untried
  cell; and the exact word count at which the constraint hop crosses the cutoff, which is
  bracketed only between 7 and 31 words.
- **Attribution boundary.** What is licensed is the passage-level statement that removing
  the named material from the constraint hop's body raises that body's similarity to this
  query on this unchanged candidate set, and the per-side reachability of each required
  passage under the reduced queries named above. Not licensed: any claim that the encoder
  attended to, weighted or averaged away any token (pit 18); any reading of the
  gold-targeted ablations as a deployable repair, since they require knowing which passage
  is required (pit 19d); any causal claim for the competitor composition, whose membership
  is read from passage text while every removal cell is an identity (pit 19ai); any use of
  the BM25 figures as a cause of the Dense outcome (pit 16); and any reading of the oracle
  conditions as repairs (pit 15).
- **Confidence:** medium-high. Supporting it: an exact baseline reconstruction; both
  refusal routes for the adopted name measured and neither firing; per-side reachability
  measured at rank 1 or 2 from the question's own wording on both sides; a ceiling over 48
  non-oracle conditions; 14 of 14 identity cells; and a dilution gate that passes on one
  side with a three-point uncontaminated control curve and a decisive matched pair.
  Limiting it: the adopted name supplies no intervention, so its evidence is the
  combination of per-side reachability with the exhaustion of every joint condition rather
  than a single flipping cell; one gold-targeted index-side pairing does double-recover at
  1 / 0.509545 and 3 / 0.406656 and is excluded on the gate rather than on its
  measurement; and the exact word count at which the constraint hop crosses the cutoff was
  not bracketed between 7 and 31 words.
- **Audit questions registered, not resolved.** Whether a non-gold passage that reaches the
  same bridge entity through a different one of the question's constraints counts under
  `gold_chain_substitutability`, which sharpens the boundary D-023 left open. And whether
  `cutoff_sensitive_near_miss` should be readable at all on a unit whose other required
  passage sits 38.030 percent below the cutoff, which is the wording D-036 referred to the
  audit and which this decision follows rather than settles.
- **References:** `references/dense_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ae1801955429901ffe4aec4.md`.

## D-039 - Reclassify the BraveStarr / Celebrity Home Entertainment BM25 unit as cross passage conjunction unresolved and delete two provisional names

- **Date:** 2026-08-07
- **Status:** active
- **Decision:** For `5ae60426554299546bf83019|bm25`, replace the provisional primary
  `partial_match_constraint_omission` with `cross_passage_conjunction_unresolved`, and
  adopt five secondaries: `related_name_document_crowding` on the five non-gold passages
  above the answer hop that name the distributor, `cutoff_sensitive_near_miss` on both
  required passages, `surface_form_tokenization_mismatch` on the constraint gold's own
  indexed body, `generic_query_scaffold_score_inflation` on `Pergament Home Centers`, and
  `same_topic_passage_distractor` on `COPS (animated TV series)`. Delete the provisional
  names `partial_match_constraint_omission` and `distributor_related_document_crowding`
  rather than registering either. Register no new descriptor. Use
  `related_name_document_crowding` as the closest competitor. Do not adopt
  `unindexed_title_name_anchor`, `minimal_preprocessing_score_distortion`,
  `generic_term_lexical_crowding`, `plausible_non_gold_answer`, `gold_chain_not_unique`,
  `gold_chain_substitutability`, `description_only_bridge_entity`,
  `repeated_content_word_amplification`, `repeated_function_word_amplification`,
  `one_sided_entity_crowding`, `compound_two_sided_crowding` or
  `peripheral_passage_content_dilution`.
- **Affected unit:** `5ae60426554299546bf83019|bm25`.
- **This is the sixth primary use of `cross_passage_conjunction_unresolved`**, the full
  enumeration being D-022 and D-024 on BM25, D-025, D-031 and D-038 on Dense, and this
  one; it is the third primary use on a lexical backend. **The registry's own member
  enumeration omitted D-031**, which is why D-038's sentence calls itself the fourth
  when it is the fifth; that sentence stays as written because the log is append-only,
  and the enumeration is corrected in this landing in the way section E rule 4 asks for -
  a missing member is visible the moment it is enumerated, which a running tally never
  makes visible. It is the tenth consecutive decision that
  registers no new descriptor, the fifth to delete a provisional name outright after
  D-031, D-033, D-037 and D-038, and the first to delete two in one landing. This unit
  was the last holder of `partial_match_constraint_omission`, which D-033 deleted without
  registering it, so the name now leaves the inventory entirely.
- **Question:** `Which American Space Western animated series did Celebrity Home
  Entertainment released ` - reproduced exactly, including the trailing space, the absent
  question mark and the tense disagreement. This is a bridge unit. `BraveStarr` is 99 BM25
  tokens and opens `BraveStarr is a 1980s American Space Western animated series.`; it
  never names the distributor. `Celebrity Home Entertainment` is 66 BM25 tokens and lists
  the titles it released verbatim, `"BraveStarr"`, `"Filmation's Ghostbusters"` and
  `"C.O.P.S."`; it never says which of them is a Space Western. The missing intermediate
  fact runs in both directions and each half is written in exactly one passage.
- **Verified implementation:** `rank-bm25==0.2.2` BM25Okapi at its defaults
  `k1=1.5`, `b=0.75`, `epsilon=0.25`; only paragraph text is indexed and titles are
  excluded; the tokenizer is `text.lower().split()` with no punctuation stripping, no stop
  words, no stemming, no Unicode normalization and no phrase matching; a repeated query
  token accumulates once per occurrence, which does not arise here because no query token
  repeats. The pooled `avgdl` is 90.884950. Passages are scored independently, with no
  reranker and no cross-passage or iterative-hop reasoning.
- **Exact reconstruction:** rebuilding the same 4,937-passage pooled index reproduces all
  50 stored top-50 titles in order, 0 of 50 mismatched, at a maximum absolute score error
  of 0.000e+00, so strong causal claims are supported. Complete-corpus ranks are
  8 / 17.987437 and 6 / 18.769969 against a rank-5 score of 18.906282. **Neither gold is
  absent from the corpus**; `not_in_top50` describes the stored window only (pit 7). Every
  per-token decomposition quoted below reconciles against `get_scores` to 3.553e-15 on the
  answer hop and 0.000e+00 on the constraint hop, which is the precondition pit 24 imposes
  before a decomposition may be quoted at all.
- **Diagnostic scale:** 177 labelled rows on the same unchanged candidate set, of which
  168 are measured runs covering 165 distinct conditions, 3 of those being deliberate
  repeats of `baseline`, `T` and `S` across two producers that reproduced them bit for
  bit, 4 tabulate the positions of passages this entry names, and 5 are `not_run` cells
  with reasons. By intervention type there are 134 non-oracle conditions, 8 oracle
  conditions and 26 gold-targeted or index-side conditions. The reproduction script
  carries 266 assertions and all pass.
- **The two required passages match disjoint halves of the question, and that is the whole
  measurement.** `BraveStarr` scores on `animated` 5.482144, `space` 4.737610, `western`
  3.490203, `series` 3.188841 and `american` 1.088638. `Celebrity Home Entertainment`
  scores on `celebrity` 6.911643, `entertainment` 4.863113, `home` 4.662400 and `released`
  2.332813. **The two hit sets intersect in nothing at all.** The question's total query
  idf is 37.094684, split into two near-equal halves: the genre facet is 15.934678, or
  42.96 percent, the distributor facet is 15.345775, or 41.37 percent, and the
  interrogative scaffold is 5.814231, or 15.67 percent. Each required passage therefore
  forfeits more than half the question by construction: 21.160006, or 57.04 percent, is
  unreachable by the answer hop and 21.748909, or 58.63 percent, by the constraint hop.
  This is the strongest form of the first leg this descriptor asks for; D-028 recorded
  disjoint hit sets and this is an empty intersection with the idf mass priced.
- **Single query tokens carry opposite signs across the hops in 6 of 11 cases**, the
  highest proportion this project has measured. Deleting `celebrity` gives
  3 / 17.987437 and 19 / 11.858326; `home` gives 2 / 17.987437 and 8 / 14.107569;
  `entertainment` gives 3 / 17.987437 and 7 / 13.906856; `released` gives 6 / 17.987437
  and 8 / 16.437155; `american` gives 9 / 16.898798 and 5 / 18.769969; `series` gives
  10 / 14.798596 and 5 / 18.769969. Four more move one hop only and against it - `space`
  18 / 13.249827, `western` 12 / 14.497234, `animated` 10 / 12.505292 and `did`
  7 / 17.987437 - and only `which`, at 6 / 17.987437 and 4 / 18.769969, moves both the same
  way. The ratio 6 of 11 sits above D-024's 10 of 19, D-025's 10 of 20 and D-031's 8 of 22
  in proportion, and far above the 4 of 19 on which D-026 refused this name.
- **Per-side reachability holds and each name annihilates the other side.** `BraveStarr`
  alone as the query gives 1 / 7.786100 and 4607 / 0.000000; `Celebrity Home
  Entertainment` alone gives 4625 / 0.000000 and 4 / 16.437155. This is D-025's shape,
  where each anchor lifts its own side and drives the other out, not D-026's shape, where
  a single anchor lifted both and the name was refused on that ground. One detail belongs
  with the crowding secondary rather than here: even its own full name places the
  distributor's own page only 4 / 16.437155, because its own name family sits above it.
- **The D-028 route of pit 19s does not fire, and it was measured in its strongest form.**
  Across 134 non-oracle conditions **not one places both required passages inside the
  cutoff**, and the Pareto frontier has exactly four corners: 1 / 17.987437 with
  1095 / 2.332813 when the distributor name is deleted from the question,
  2 / 17.987437 with 8 / 14.107569 when `home` is deleted, 3 / 17.987437 with
  7 / 13.906856 when `entertainment` is deleted, and 6 / 18.127467 with 1 / 23.750585
  under scaffold removal plus title indexing. **At three of those four corners the answer
  hop's score is bit for bit its baseline 17.987437**: no non-oracle condition anywhere in
  this diagnostic adds a single point to it, its only score movement being the 0.140030
  that title indexing contributes. Every improvement it records is a competitor falling
  below it. What D-028 used to refuse this name was a deployable index-side repair;
  the closest thing to it here, document-side boundary-punctuation normalization with
  scaffold removal and title indexing, reaches 6 / 18.101334 and 2 / 24.260792, leaving
  the answer hop 0.134368 points and 0.737 percent short.
- **The deployable version of the repair that would help the answer hop is negative, and
  that is the sharpest form of pit 19ae recorded so far.** The answer hop does carry a
  boundary-punctuation loss of its own: its body writes `animated series.`, so its raw
  `series` term frequency is 2 where boundary stripping makes it 3. Repairing that one
  passage and nothing else gives 8 / 18.615675 and 6 / 18.769954, worth 0.628238 points and
  **0 rank positions**; applying the same repair to the whole corpus gives 8 / 17.963391
  and 3 / 20.702955, worth **-0.024046 points**, because the identical repair gives more to
  its competitors than to it. The null control that licenses the row-substitution technique
  is reported as a measured residual: re-substituting each gold's own unchanged text
  reproduces all 4,937 scores at a maximum absolute difference of 0.000e+00. Earlier units
  measured a discount between the gold-targeted and deployable versions of a repair -
  9 rank positions at D-033, 0.000007 points at D-034 - and this is the first at which the
  deployable version reverses the sign.
- **Neither exclusion fires.** No single passage supplies a complete answer: the
  constraint gold lists three titles without a genre and the answer gold states the genre
  without a distributor. No evidence-bearing substitute exists on either side: the only
  corpus passage containing `space western` is `BraveStarr` and the only two containing
  `bravestarr` are the two golds, so `bravestarr` has corpus document frequency 1 raw and
  2 after boundary stripping, with term frequency 1 and 2 in the answer gold and 0 and 1 in
  the constraint gold. The label does not rest on the presence of two annotated golds; it
  rests on the empty hit-set intersection, the 6 of 11 sign reversals and the 134
  non-oracle conditions. The retrieval stage performs no joint reasoning.
- **`related_name_document_crowding` is adopted as a secondary and is the closest
  competitor, and it is refused the primary on three independent grounds.** The family is
  five non-gold passages above the answer hop whose text names the distributor -
  `COPS (animated TV series)` 1 / 24.991204, `Sterling Entertainment Group`
  2 / 20.383253, `Noel C. Bloom` 3 / 20.201011, `Locke the Superman` 4 / 19.831276 and
  `Tottoi` 5 / 18.906282 - each of which states its own relationship to the distributor in
  its own text, as a title it released, a competitor, or its founder. The three controls
  pit 19ad requires separate cleanly: removing the family gives 3 / 18.007533 and
  1 / 19.544516, removing its complement, the single passage `Pergament Home Centers`
  7 / 18.620405, gives 7 / 18.013998 and 6 / 18.775924, a size-matched null removal of
  five high-ranked passages carrying none of `celebrity`, `home` or `entertainment` gives
  8 / 18.069800 and 6 / 18.771378, and the statistics-matched control, the family removed
  with pooled `idf` and `avgdl` grafted back, gives 3 / 17.987437 and 1 / 18.769969.
  **Both scores in that last cell are bit for bit the baseline**, so the family's whole
  effect is positional and the collection statistics carry none of it, which is cleaner
  than D-032, where the same probe moved a gold's score from 19.741610 to 22.167723.
  Pits 19af and 19ag are satisfied and the two states agree: removing the family gives
  3 / 18.007533 and 1 / 19.544516 at baseline and 3 / 18.121392 and 1 / 25.293159 under
  the document-side normalization, and removing every non-gold above the answer hop gives
  2 / 18.034096 and 1 / 19.550617 at baseline and 3 / 18.119172 and 1 / 25.043955 under it.
  The pit 19u cell therefore succeeds here, so no crowding descriptor is excluded by it,
  which is the opposite of D-030.
  The three grounds for keeping it a secondary are: **first**, the two directions pit 19f
  and pit 19i require agree in sign, so the family is the product of the question's own
  required naming rather than an independent contributing condition, which is the ground
  D-023 used to refuse `question_frame_semantic_crowding` and D-024 used to hold
  `generic_term_lexical_crowding` at secondary. Forward, the distributor name alone
  reproduces 7 of the baseline top ten and 5 of 5 of the family, and `celebrity` alone
  reproduces 6 and 5 of 5, while the genre facet alone reproduces 1 and **0 of 5**.
  Reverse, deleting the distributor name from the question collapses the neighbourhood to
  2 and **0 of 5**, while deleting the genre facet leaves it at 8 and 5 of 5.
  **Second**, the family and the required evidence are the same lexical class. A rule
  stated from the question alone, drop every passage whose text names Celebrity Home
  Entertainment, selects six passages and **one of them is the required constraint gold**;
  applied, it puts the answer hop at 2 / 18.006690 and removes the constraint gold from the
  index altogether. The gold-exempt version, which needs to know which passage is gold and
  is therefore a pit 19d third-category intervention, gives 3 / 18.013117 and
  1 / 21.212668 over the eleven non-gold passages carrying `celebrity`. What distinguishes
  the constraint gold from its own name family - that the title it released is a Space
  Western - is written only in the other gold, which is the adopted primary restated.
  **Third**, D-024 is the same shape on the same backend and settled the same way: disjoint
  hit sets, a family removal that double-recovers, and the primary going to this name.
- **`cutoff_sensitive_near_miss` is adopted on both required passages, the first two-sided
  adoption in this project, and no band edge moves.** The answer hop sits 0.918846 points,
  or **4.860 percent**, below the rank-5 score and the constraint hop 0.136314 points, or
  **0.721 percent**, below the rank-5 score. Both lie inside the accepted band, whose
  measured members already run from 0.281 to 5.464 percent, so the accepted upper edge,
  the excluded lower edge and the never-decided band are all unchanged. The no-substitute
  condition that D-015 established and D-034 applied holds on both sides, as recorded
  above. There is no cliff to invoke: the successive differences from rank 1 to rank 10 are
  4.607950, 0.182242, 0.369736, 0.924993, 0.136314, 0.149563, 0.632968, 0.665362 and
  1.300240, and the largest of them lies below both golds, so the adoption rests on the
  percentages together with the counter-evidence, which is D-032's shape. That
  counter-evidence is the strongest recorded: the cumulative removal ladder runs
  7 / 18.005555 and 5 / 18.898807, 6 / 18.005524 and 4 / 19.036442, 5 / 18.005642 and
  3 / 19.187204, 4 / 18.007802 and 2 / 19.356178, 3 / 18.007533 and 1 / 19.544516,
  2 / 18.034096 and 1 / 19.550617, so **three removals flip `full@5`**, where every earlier
  adoption's counter-evidence flipped `any@5` only. Every earlier adoption also had to be
  scoped to one side under the D-025 split rule because the other sat in the excluded band;
  this is the first unit in which the descriptor describes `full@5` rather than `any@5`.
- **`surface_form_tokenization_mismatch` is adopted on the constraint gold's own indexed
  body, and its deployable version does not discount.** That body writes
  `(also known as simply "Celebrity Video")`, and under the implemented
  `text.lower().split()` the form `"Celebrity` is a different token from `celebrity`, so
  the passage's raw term frequency for `celebrity` is 1 where boundary stripping makes it
  2. Stripping quotes in that passage alone gives 8 / 17.987437 and 2 / 21.350963, worth
  2.580995 points and 4 rank positions against a null control whose residual over the whole
  corpus is 0.000e+00. Stripping quotes across the corpus, which touches 2,387 passages,
  gives 8 / 17.888265 and 2 / 21.158602, worth 2.388634 points and **the same 4 rank
  positions**; the corpus document frequency of `celebrity` moves from 11 to 12. This is
  the second unit after D-034 at which pit 19ae's deployable cell costs nothing in rank.
- **`generic_query_scaffold_score_inflation` is adopted for one passage that has no
  relation to the question at all.** `Pergament Home Centers` is a home-improvement store
  chain and it ranks 7 / 18.620405, above the answer hop. Its decomposition gives `did`
  6.402224 and `which` 1.541303, so 7.943527 of its score, or 42.7 percent, is
  interrogative scaffold and only 10.676878 is content, far below the answer hop's
  17.987437. The exclusion for repeated occurrences does not fire: **no query token
  repeats**, so the doubled `did` is ordinary document term frequency and not the
  per-occurrence query accumulation that `repeated_function_word_amplification` names.
  Scaffold removal alone moves the two golds from 8 / 17.987437 and 6 / 18.769969 to
  6 / 17.987437 and 4 / 18.769969, with both scores unmoved, because this passage and
  `Locke the Superman`, whose scaffold share is 2.111606 or 10.6 percent, both fall below
  the answer hop; under scaffold removal with title indexing `Pergament Home Centers` is
  23 / 10.924670 and under the document-side normalization 34 / 10.451708. For comparison
  `COPS (animated TV series)` draws 1.352214 or 5.4 percent from scaffold and
  `Noel C. Bloom` 1.625490 or 8.0 percent, while both golds, `Sterling Entertainment Group`
  and `Tottoi` draw 0.000000.
- **`same_topic_passage_distractor` is adopted for `COPS (animated TV series)` alone.**
  Its text states that it is `an American animated television series released by DIC
  Entertainment ... and Celebrity Home Entertainment`, so it matches 8 of the question's 11
  tokens - all but `space`, `western` and `did` - and ranks 1 / 24.991204. Its text
  contains neither `space` nor `western`, which is the missing decisive constraint the
  include rule asks to be verified rather than inferred. This is the observation the
  original note was built on, and it is recorded under a registered name.
- **`unindexed_title_name_anchor` is not adopted, although all three of its include
  conditions are met and the title-indexing condition is materially positive.** Titles are
  verifiably not indexed; the constraint gold's title tokenizes to exactly
  `celebrity`, `home`, `entertainment`, all three of them query tokens in matchable form;
  and the title-indexing condition moves that passage from 6 / 18.769969 to
  2 / 23.750585. **The first exclusion fires all the same: the anchor is equally matchable
  in the indexed body**, whose raw term frequencies are `celebrity` 1, `home` 2 and
  `entertainment` 1. The mechanism is therefore term-frequency amplification of an anchor
  that already matched, taking those three to 2, 3 and 2, and not the recovery of an
  unmatchable one. That is a third distinct route to a materially positive title-indexing
  condition, after D-028, where the anchor existed only in the title, and D-036, where the
  gain was a length-normalization side effect and the descriptor failed its *second*
  include condition. Both readings the D-023 rule requires were run: the indexing reading
  is the condition above, and the semantic reading, the question reduced to that title,
  gives 4625 / 0.000000 and 4 / 16.437155, or 4625 / 0.000000 and 1 / 21.426914 with the
  title indexed, so it enters the cutoff and is not what refuses the name.
- **`minimal_preprocessing_score_distortion` is not adopted as the primary.** The defect it
  names is real on both passages and is priced above, but it explains only the constraint
  hop: the answer hop moves 0 rank positions under the gold-targeted repair and loses
  0.024046 points under the deployable one. Its concrete mismatches are carried by
  `surface_form_tokenization_mismatch` as a secondary instead. The compound
  boundary-punctuation factor was also split by character as pit 19al requires, and the
  minimal repair beats the general one again: quotes alone on the document side give
  8 / 17.888265 and 2 / 21.158602, while full boundary stripping gives 8 / 17.963391 and
  3 / 20.702955, with the parenthesis component at 8 / 17.973279 and 6 / 18.726473, the
  comma at 8 / 17.784879 and 6 / 18.560611, the full stop at 8 / 18.323720 and
  6 / 18.450567 and the apostrophe at 8 / 17.984055 and 6 / 18.769969. Three of the four
  components are negative on the constraint hop, so a positive compound factor was hiding
  them.
- **Every preprocessing factor was measured on the query side, the document side and both,
  and the query side is inert by construction here.** The question contains no punctuation
  and no dash, so its token list is unchanged by either normalization and the query-side
  cells of `P` and `E` reproduce the baseline exactly at 8 / 17.987437 and 6 / 18.769969;
  that is stated as a measured cell rather than assumed. The stemming factor gives the
  opposite of D-032's shape: the query side alone gives 16 / 9.316451 and 5 / 16.437155,
  the document side alone 16 / 9.304520 and 5 / 16.437155, and the two together
  8 / 17.975506 and 6 / 18.758624, back at the baseline. **Both one-sided cells are
  strongly negative and the two together are inert**, which is the same structure D-032
  recorded - a one-sided normalization breaking a match that already worked - with the
  sign reversed.
- **The wording factorial is inert on the answer hop across all sixteen cells.** The
  dataset string carries exactly three defects and each is a factor: A repairs the tense,
  B appends the missing question mark, C strips the trailing space. At baseline the eight
  cells give the answer hop 8 / 17.987437 or, whenever B is on, 6 / 17.987437, and the
  constraint hop 6 / 18.769969, 8 / 16.437155, 3 / 20.821301 or 8 / 16.437155. Under
  document-side normalization with scaffold removal and title indexing they give the answer
  hop 6 / 18.101334 or 7 / 18.101334 and the constraint hop 2 / 24.260792, 2 / 21.944594,
  1 / 26.047692 or 2 / 21.944594. **The answer hop's score takes exactly two values across
  the sixteen cells, one per preprocessing state, and neither depends on A, B or C**, so
  the question's three defects are not its mechanism. Two of them are not even repairs on
  the constraint side: appending the question mark makes `released?` a token the corpus
  does not carry, which costs that passage 2.332813 points, and C is inert by construction
  under `lower().split()`, verified rather than asserted. Only A helps, and only there,
  because the constraint gold's body carries `release` as well as `released`.
- **Corpus setting: this is a setting-dependent gold swap and the two corpus settings
  disagree on `any@5`.** Pooled gives `any@5` 0 and `full@5` 0 with the golds at 8 and 6;
  per-question gives `any@5` 1 and `full@5` 0 with them at 1 and 9, so **the two golds
  exchange order between the settings**. The four cells separate the paths. Restricting the
  pooled scores to this item's ten passages gives 7 / 17.987437 and 6 / 18.769969;
  rebuilding the index on those same ten gives 1 / 4.781835 and 9 / 1.511055 and reproduces
  the official per-question window title for title; grafting pooled `idf` and pooled
  `avgdl` back onto that document set reproduces the restricted cell exactly at
  7 / 17.987437 and 6 / 18.769969; grafting pooled `idf` only, leaving the per-question
  `avgdl` of 83.800000 against the pooled 90.884950, gives 7 / 17.387936 and
  6 / 18.240251 with the order unchanged. **`avgdl` therefore carries none of the flip**,
  as at D-028, D-032, D-033 and D-034. The mechanism is that the ten-passage index floors
  `celebrity`, `home` and `entertainment` to the same epsilon value 0.403526 and takes
  `series` and `released` to 0.000000, while `space` and `western` keep 1.845827,
  `animated` keeps 0.762140, `which` keeps 0.762140, `american` keeps 0.367725 and `did` is
  absent from the vocabulary altogether: **the small index destroys the distributor facet
  and preserves the genre facet**. The new-competitor path is very weak here - of the six
  non-gold passages above the answer hop only one is introduced by pooling, and of the five
  above the constraint hop none is - and the annotator-supplied path is strong, eight of
  the item's own ten passages being distributor-related. Recorded as provenance under
  D-003, not as a causal category (pit 17).
- **The single-factor oracle-name test fails, with both premises checked.** Appending the
  answer gold's title gives 1 / 25.773537 and 7 / 18.769969; appending the constraint
  gold's title gives 19 / 17.987437 and 5 / 35.207124; appending both gives
  9 / 25.773537 and 5 / 35.207124. None double-recovers. Pit 19g's premise holds - the
  injected `bravestarr` has corpus document frequency 1 and term frequency 1 in the passage
  it names and 0 in the other, so the anchor reaches the passage it is meant to reach - and
  pit 24b's does too, the injected string being absent from the question rather than a
  surface variant of something already in it. `description_only_bridge_entity` had already
  failed its inclusion rule before the test was run, the distributor being explicitly
  named. For completeness, the oracle injection does double-recover once combined with
  other factors, at 2 / 28.519007 and 1 / 29.389990 under document-side normalization,
  1 / 29.465736 and 2 / 23.750585 with scaffold removal and title indexing, and
  2 / 30.566563 and 1 / 32.912200 under both, but those are oracle conditions and pit 15
  forbids reading them as repairs.
- **One gold-targeted condition does double-recover, and it is reported rather than acted
  on.** Repairing the boundary punctuation of both required passages and nothing else gives
  8 / 18.615659 and 2 / 21.446908, and adding scaffold removal and title indexing to that
  gives **5 / 18.751159 and 1 / 25.187216**. It is a pit 19d third-category intervention:
  it injects no answer information and adds no text, but it needs to know which two
  passages are gold, and it is not a deployable repair - its deployable counterpart is the
  6 / 18.101334 and 2 / 24.260792 recorded above, and the corpus-wide version of the
  answer-side half of it is negative. Pit 19s is written against a *non-oracle* condition,
  which this is not, so it does not fire; the cell is recorded here because it is the
  closest this unit comes to the D-028 rebuttal and because whether pit 19s should be
  sliced on "supplies no intermediate fact" rather than on "non-oracle" is a question for
  the audit rather than for this entry.
- **`generic_term_lexical_crowding` is not adopted.** The family is name-driven, not
  category-driven: `celebrity` alone reproduces 5 of 5 of it while the genre facet alone
  reproduces 0 of 5. This is the mirror of D-034, which refused
  `related_name_document_crowding` on the same test with the outcome reversed.
- **`plausible_non_gold_answer`, `gold_chain_not_unique` and `gold_chain_substitutability`
  are not adopted, on one shared measurement.** No corpus passage other than the answer
  gold contains `space western` or `western animated`, and `COPS (animated TV series)`,
  the only passage that satisfies every other constraint, contains neither `space` nor
  `western`. Only the two golds contain `bravestarr`. Under the evidentiary standard
  applied to the annotated golds there is no alternative answer, no alternative chain and
  no substitute for either hop.
- **`one_sided_entity_crowding` and a compound reading are not adopted.** One family
  suppresses both hops - all five non-gold passages above the constraint hop belong to it,
  as do five of the six above the answer hop - which by pit 19h means there is no compound
  and nothing one-sided.
- **`partial_match_constraint_omission` is deleted rather than registered, on three
  independent grounds.** It states a ranking pattern rather than a retrieval mechanism,
  which is pit 17 and is word for word the ground on which D-033 deleted this same name at
  queue item 20, and the same criticism D-010 made of `one_sided_entity_crowding`. The
  observation it names is already partitioned between two registered names,
  `same_topic_passage_distractor` for `COPS (animated TV series)` and
  `related_name_document_crowding` for the family. And the adopted primary dissolves it:
  the constraint is "omitted" because no single passage can carry both halves of the
  question, which is a property of the evidence layout and not of the competitors.
- **`distributor_related_document_crowding` is deleted as a duplicate**, on the criterion
  D-031 used for `subject_associate_crowding`, D-033 for `cross_entity_relation_unresolved`
  and D-037 for `broad_adaptation_topic_crowding`. `related_name_document_crowding` is
  defined over "relatives, works, **institutions**, or **associates** sharing a name or
  name token", and a distributor is this case's instance of that, not a separate class.
- **`peripheral_passage_content_dilution` is not applicable on this backend and the gate
  was not run.** The gate is defined on a bi-encoder's mean pooling; a lexical scorer has
  no pooled representation to dilute, length effects belonging instead to its own
  normalization term, and pit 18 forbids the token-level substitute that would be needed.
- **`not_run` cells.** Five, each with a reason recorded in the results file: the three
  Dense contract cells, since this is a BM25 unit and pit 19y forbids carrying the Dense
  reading of an index-side removal onto a lexical backend; the dilution gate, as above;
  query splitting, which pit 19o requires on comparison units and this is a bridge unit
  where the two facets are one entity and one constraint on another rather than two
  candidates; the equal-length control curve, whose gate is inapplicable and whose premise
  is absent, neither required passage carrying non-query-relevant bulk; and the wording
  factorial cell in which the tense factor is applied under a passive-voice rewrite, where
  it has no target and the cell would be a copy of its neighbour rather than a measurement.
- **Comparison retriever, reachability only.** Dense over the same pooled corpus places the
  constraint gold 1 and the answer gold 2, so both required passages are reachable by some
  method. That is all it establishes: it is not evidence about why BM25 failed, and the two
  score scales are not comparable (pit 16). Ranks only are quoted for that reason.
- **Attribution boundary.** What is licensed is that the two required passages match
  disjoint halves of the question, that no non-oracle condition among 134 places both
  inside the cutoff, and that the family above them is definable only by a rule that also
  removes one of them. What is **not** licensed: reading any of the removal, ladder,
  deployability, gold-targeted or oracle conditions as a deployable repair; reading the
  corpus setting as a cause; reading the comparison retriever's success as an explanation;
  or attributing the answer hop's rank to the question's wording, which sixteen cells
  measured and none moved.
- **Confidence:** medium-high. Supporting it: an exact zero-error baseline reconstruction;
  an empty hit-set intersection with the idf mass priced on both sides; 134 non-oracle
  conditions with no double recovery and a four-corner frontier; the pit 19ad controls
  separating position from statistics with the statistics-matched cell bit for bit at
  baseline; and a direct precedent in D-024 on the same backend with the same shape.
  Limiting it: one gold-targeted condition does double-recover, so the conjunction is the
  binding constraint under every deployable pipeline tested rather than an impossibility;
  and the closest competitor's evidence is strong enough that the decision turns on the
  reading of pit 19f and pit 19i rather than on a failed control.
- **Audit questions registered, not resolved.** Whether pit 19s should be sliced on
  "supplies no intermediate fact" rather than on "non-oracle", given the gold-targeted cell
  above. Whether a crowding descriptor whose query-only definition contains a required gold
  should be excluded from primary use by rule rather than by this entry's argument.
  Whether `cutoff_sensitive_near_miss`, now that it has a two-sided adoption, needs
  separate contracts for the `any@5` and `full@5` readings. And whether
  `unindexed_title_name_anchor`'s first exclusion should be stated as a term-frequency
  test, since a materially positive title-indexing condition has now been produced by three
  different mechanisms.
- **Tooling note, recorded because it produced wrong figures.**
  `make_repro.py --emit-case` generated one condition wrongly and eight more that happened
  to coincide. `probe_kit.Recorder.call_of()` records only truthy flags, so a document-side
  factor written `M=True, Mq=False` and a two-sided one written `M=True` record the same
  call; the generator replayed `M doc side` as a two-sided run answering 8 / 17.975506
  where the record holds 16 / 9.304520, and it replayed the eight PST cells of the wording
  factorial two-sided as well, which strips the question mark the B factor had just added
  and turns 2 / 21.944594 into 2 / 24.260792. This is pit 25l's failure mode in a second
  dimension: the wrong call is generated silently and the condition does not appear in the
  generator's NOT REPLAYED list. All nine were removed from the generated block and written
  by hand, and the removal is documented in the reproduction script's own header.
- **References:** `references/bm25_implementation_reference.md`,
  `references/reusable_retrieval_failure_review_playbook.md`,
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5ae60426554299546bf83019.md`.

## D-040 - Restrict the pit 19s refutation path to conditions that need no gold knowledge

- **Date:** 2026-08-08
- **Status:** active
- **Decision:** A condition that requires knowing which passages are gold, pit 19d's third
  intervention class, may not be used to refuse `cross_passage_conjunction_unresolved` under
  pit 19s. That refutation path is restricted to conditions deployable without gold knowledge.
  A gold-targeted condition that double-recovers is recorded, and may be cited as limiting
  confidence, but is not a ground for refusal.
- **Scope:** this rules on pit 19s only. It does **not** change pit 15, which orders a
  non-oracle result above an oracle one and turns on the same word. See the open item below.
- **Rationale:** Pit 19d already separates this class of intervention on the ground that it is
  not a deployable repair. Extending that separation from the classification to the inference
  applies an existing distinction one step later rather than introducing a new one. A condition
  no pipeline can make should not be able to establish that some other mechanism was not the
  cause.
- **Evidence, and its extent:** D-039 is the only unit on which the situation has arisen. One
  gold-targeted index-side condition double-recovers there, at 5 / 18.751159 and
  1 / 25.187216, while supplying no intermediate fact and doing no cross-passage reasoning;
  its deployable counterpart reaches 6 / 18.101334 and 2 / 24.260792, and the corpus-wide
  version of its answer-side half is negative at -0.024046 points. D-039 adopted the descriptor
  as the primary anyway and placed that cell under confidence as limiting rather than refuting.
  This decision makes that reading the rule, and **D-039's landed outcome is unchanged by it**.
  One unit, read the same way before and after, is the whole of the direct evidence.
- **Registry effect:** `cross_passage_conjunction_unresolved` gains one exclusion clause. No
  definition and no inclusion rule changes. Pit 19s gains the same qualifier in the handoff.
- **What this does not settle, and one item it opens.** Pit 15 contains the same word and is
  not covered here. D-037's tie-break, which placed `peripheral_passage_content_dilution` above
  `description_only_bridge_entity`, rests on an index-side repair that double-recovers at
  3 / 0.469751 and 1 / 0.549310 while leaving the query untouched word for word, and D-037's
  own dossier classifies that family of interventions as gold-targeted index-side rather than
  as non-oracle. Under a reading of this decision extended to pit 15, that tie-break would not
  have been available. **D-037 stands as written under red line 4, this decision does not
  extend to pit 15, and whether it should is registered as a new vocabulary-audit item.** Also
  untouched: whether D-028's refutation path, which used a genuinely non-oracle condition,
  should become an exclusion clause of its own.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
  `5ae60426554299546bf83019|bm25` supplies the measurement the rule rests on.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-16, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5ae60426554299546bf83019.md`.

## D-041 - Split the single-factor oracle-name test into a binding negative and a non-binding positive

- **Date:** 2026-08-08
- **Status:** active
- **Decision:** The test is written into `description_only_bridge_entity`'s registry entry as
  two clauses of unequal force. **Binding, as an exclusion:** if no single-factor oracle-name
  condition brings both required passages inside the cutoff, this descriptor may not be that
  unit's primary; it may still be adopted as a secondary. **Non-binding, as an inclusion
  note:** a passing test supports the descriptor without establishing it, and is outranked by
  a non-oracle result under pit 15.
- **Rationale:** The two halves have different empirical standing, and writing them as one
  rule would overstate the weaker one.
- **Evidence:** the eighteen-member series in `recount.py` section 7a, joined to the effective
  primary of each unit in `case_memos_v2.csv`. **Ten failing applications** - D-020, D-021,
  D-022, D-024, D-025, D-031, D-033, D-034, D-038 and D-039 - and on none of the ten is
  `description_only_bridge_entity` the primary. The binding clause therefore records an
  exceptionless observed regularity and forbids nothing this project has done. **Eight passing
  applications** - D-017, D-023, D-026 and D-035 took the primary, D-028, D-029, D-036 and
  D-037 did not. Four of eight is why the positive half is written as support rather than as
  an inclusion condition.
- **Preconditions carried, not settled:** D-024's, that the injected anchor be matchable by the
  passage it names (pit 19g), and D-030's, that the injected string contribute something the
  question does not already contain (pit 24b). Both remain usage notes. A test whose
  precondition fails is uninterpretable and counts as neither a pass nor a failure.
- **What this does not settle:** whether the test requires multi-form consistency; whether the
  definition's `for lexical retrieval` wording should be repaired, all four primary uses being
  Dense; the structural boundary D-026 recorded; and the boundary D-029 opened between an
  absent anchor and an unusable one. The definition is **not** amended here.
- **Correction of record, not a re-judgment:** `recount.py`'s source comment called D-037 the
  third unit to pass the test and lose the primary, after D-028 and D-029. The join above makes
  it the fourth, D-036 having also passed with its primary going to `plausible_non_gold_answer`.
  The comment is corrected in this landing. No landed sentence changes and that comment is not
  an anchor any check reads.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md` and
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-01.

## D-042 - Give `cutoff_sensitive_near_miss` a numeric threshold, with a substitutability exception

- **Date:** 2026-08-08
- **Status:** active
- **Decision:** three clauses. **One, the threshold.** A required passage qualifies only if it
  sits at most 5.464 percent below the rank-5 score. That figure is the largest adopted
  measurement to date; it is **not** a discovered discontinuity, and no cliff, gap or change of
  behaviour was measured at it. **Two, the never-decided band is not closed by clause one.**
  Two figures were measured inside 5.464 to 9.431 percent and neither was decided on, D-024's
  5.698 and D-035's 7.989. A future measurement in that band must be ruled on explicitly and
  may move the edge; it may **not** be disposed of by reading clause one as a boundary.
  **Three, the exception D-034 established.** A withholding on substitutability, where non-gold
  passages supply the same intermediate fact under the gold's own evidence standard, leaves all
  three band edges untouched, because the ground is not the gap.
- **Rationale:** The bands were already being used as if they were a rule, at D-028, D-032 and
  D-033, without one being written. Writing the threshold down makes the practice checkable.
  Clauses two and three keep it from claiming more than the measurements support.
- **Evidence:** adopted at 0.281, 0.721, 1.156, 2.170, 4.137, 4.503, 4.860, 5.140 and 5.464
  percent; excluded from 9.431 through 53.000 percent; measured but not band-setting at D-024's
  5.698, D-034's 3.641 and D-035's 7.989. The membership is `recount.py` section 7c, which
  derives all three bands from the registry rows and reports that no adoption or exclusion lies
  inside the never-decided band. D-034 is the sole non-gap withholding: 3.641 percent, inside
  the adopted range, with counter-evidence that supported adoption, two removals giving
  5 / 34.046411 and flipping `any@5`, withheld because four non-gold passages supply the same
  intermediate fact and two of them sit inside the cutoff.
- **Consistency with the landed record:** D-024's 5.698 percent lies above the threshold and
  was not adopted, so clause one does not contradict it. But D-024's rejection ground was
  superseded by the split rule at D-025, so that unit is not evidence *for* the threshold
  either, and whether pre-D-025 units should be re-read under the split rule stays open.
- **What this does not settle:** the two statements of D-025's split rule inside this same
  entry, which D-036 recorded as disagreeing; the weaker reading D-036 identified when a
  complete alternative answer already sits inside the cutoff; and whether `any@5` and `full@5`
  now need separate contracts.
- **Registry effect:** the entry gains a threshold clause and an exception clause. The four
  strings `recount.py` is anchored to are left byte for byte intact, so no check string
  changes and `recount.py` needs no edit for this decision. The word `untested` does not
  reappear; `recount.py` fails on it.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md` and
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-34.

## D-043 - One shared primary-use contract for crowding-family descriptors

- **Date:** 2026-08-08
- **Status:** active
- **Decision:** A crowding-family descriptor, meaning one whose content is that a set of
  non-gold passages competes with a required passage, may be a unit's primary only if both
  clauses hold. **One:** the competing set is stated as a rule over passage content, not as a
  rank range or a position. **Two:** that rule does not also select a required passage.
- **Rationale:** Clause one is the footing D-018, D-027, D-029 and D-032 already used to
  satisfy pit 17, and the point on which D-010 demoted `one_sided_entity_crowding`; it adds no
  requirement and is written down so that it can be checked rather than argued each time.
  Clause two is new. It separates a competing family from a restatement of the ranking: if the
  only rule that picks out the family also removes a passage the question needs, the family
  cannot be removed even in principle, and the claim that it caused the failure is not testable
  by any intervention.
- **Evidence, two units.** **D-039, where clause two fires.** The family above the two
  required passages is definable only by a rule that also removes one of them, six members of
  which one is a required gold, and crowding was held to secondary on that ground; the entry's
  attribution boundary states this as a licensed conclusion. **D-027, where clause two is
  satisfied.** That entry states the family as `all six competitors literally contain Albee in
  their text`, and the required `Edward Albee` passage contains that name too, so the stated
  rule selects a required passage. A fact check over the pooled corpus, run for this decision
  and recorded in full below, finds that a different content-only rule selects all six and
  neither required passage, so the family is definable within clause two and D-027 satisfies
  the contract.
- **The fact check, and what it did and did not do.** It evaluated candidate content
  predicates over the 4,937-passage pooled corpus and reported which passages each selects. It
  computed no ranking and no score, and **it is not a re-judgment of D-027**: that entry's
  primary, conclusions, tie-break and confidence are unchanged, and red line 4 is untouched.
  The stated rule, a body containing `albee`, selects nine passages including the required
  `Edward Albee`. Adding one predicate fixes it two different ways. Excluding bodies that carry
  both `1928` and `2016` selects eight, all six competitors and no required passage; that
  predicate is Edward Albee's own life dates, which appear in the required passage and not in
  the question, so writing it needs that passage's content. Excluding bodies that carry a
  month-day-year date selects seven, all six competitors, `Oppenheimer Award`, and no required
  passage; **that predicate needs nothing from either required passage**, so the family is
  definable within clause two even under the strictest reading of what a content rule may
  know. It works because the required passage writes `March 12, 1928 - September 16, 2016`
  while `Reed A. Albee` writes `8 September 1885 - 2 August 1961`, which is a difference of
  date format rather than of meaning; the contract asks whether such a rule exists, and it
  does, but the entry records that this one is not semantically motivated.
- **Applies from D-043 onward.** D-027, D-029 and D-032 are not re-judged. D-027 is now
  checked against clause two and satisfies it; D-029 and D-032 have not been checked and this
  decision asserts nothing about them.
- **Where the contract lives, which is not settled here.** Section 13 records the position that
  a primary-use contract belongs in `candidate_taxonomy_v0_1.md` rather than in the secondary
  descriptor registry. That file does not exist yet, and `one_sided_entity_crowding` has no
  registry entry at all, being a primary name. The contract is therefore stated in this entry,
  noted in `question_frame_semantic_crowding`'s registry entry, which is the one
  crowding-family entry with a validated primary use, and **must be carried into
  `candidate_taxonomy_v0_1.md` when section 14 writes it**. The same carry-over applies to
  D-041's oracle-name clauses.
- **What this does not settle:** whether `question_frame_semantic_crowding` needs splitting
  across the two inventories; whether a secondary may be a scoped subset of its own primary's
  family; the lexical wording of `related_name_document_crowding`'s definition; the operational
  meaning of `explains the primary failure` in its first exclusion; the half-neighborhood D-023
  left uncovered; and its overlap with `same_topic_passage_distractor`. In particular this
  contract has **no clause about what counts as measuring a family's effect on a bi-encoder**,
  where index-side removal is an arithmetic identity by D-035; that remains open.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-18, and
  `manual_review_v1/analysis/per_case_analysis/dense_comparison_5a78b209554299148911f93e.md`.

## D-044 - Condition the oracle-name exclusion on the pit 19g precondition

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** The D-024 precondition, that an injected anchor be matchable by the passage
  it names, becomes a condition on `description_only_bridge_entity`'s exclusion clause
  rather than a usage note. The bar D-041 wrote, that a failing single-factor oracle-name
  test forbids this descriptor's primary use, may fire only where that precondition has been
  verified and holds for every injected form counted as a failure. Where it has not been
  verified, or where it fails, the application is recorded as not applicable and is neither a
  pass nor a failure, which is the treatment the membership table already gives the other
  precondition.
- **Applies from D-044 onward.** No landed application is reclassified, no membership row
  moves and no landed primary changes.
- **Rationale:** D-041 changed the standing of the failing half from an argument an entry
  could make into a bar it must obey. A bar and a usage note are not the same kind of object:
  a note can be weighed against other evidence, a bar cannot, so a premise the bar depends on
  has to carry the bar's own standing. This adds no new test and no new measurement; it
  states when the existing one may be read.
- **Evidence, and its extent.** Three facts, all from landed text. **One, the precondition
  has failed exactly once, and there it inverted the reading.** D-024's answer passage
  tokenizes `General Mills, Inc.,` so that its only mills-bearing token carries a comma while
  the other required passage carries the bare token, and the injected bare form gave its
  points to that other passage; the bare test reads 9 and 1, which D-024's own boundary
  paragraph calls uninterpretable on its own, and the same condition reads 2 and 1 once
  boundary-punctuation normalization removes the artifact. **Two, the two preconditions are
  already applied asymmetrically to the same table.** Section 7a of `tools/recount.py`
  records D-030 as not applicable because its only double-recovering oracle condition was
  degenerate under pit 24b, while D-024 is carried as a failure; D-041's own sentence, that a
  test whose precondition fails is neither a pass nor a failure, matches the first treatment
  and not the second. **Three, verification is uneven across the ten failing applications.**
  D-020, D-021 and D-022 precede D-024 and could not have checked it; D-025, D-031, D-034,
  D-038 and D-039 record the check and it holds; D-033 records only an adjacent observation;
  D-024 is the one where it fails. The extent is one unit for the failure mode and one
  membership table for the asymmetry, and the rule forbids nothing this project has done,
  this descriptor being the primary on none of the ten.
- **Registry effect:** `description_only_bridge_entity`'s exclusion clause gains this
  condition and the entry gains D-044 as a decision source. No definition, no inclusion rule
  and no affected unit changes here. Pit 19g gains the same qualifier in the handoff.
- **Record note, not a re-judgment.** D-024 stays in the membership table as a failure and
  this decision does not move that row. Moving it would take the failing count from ten to
  nine and contradict four anchored sentences the recount checks, one of them D-041's own
  evidence sentence, and the log is append-only. The tension is registered here instead: read
  prospectively, D-024's application would be recorded as not applicable rather than as a
  failure.
- **What this does not settle:** whether the same conditioning belongs on the passing half,
  which stays non-binding under D-041; the second precondition, which D-045 rules on; which
  injected forms count and how many are required, which D-046 rules on; the definition's
  wording, which D-047 repairs; and the boundary D-029 opened between an absent anchor and
  one that is present but unusable, which stays open as triage item T-09.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
  `5ae057fd55429945ae959328|bm25` supplies the one measurement the rule rests on.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-02, and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5ae057fd55429945ae959328.md`.

## D-045 - Register the pit 24b degeneracy check as the second precondition

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** The D-030 precondition, that an injected string contribute something the
  question does not already contain, is the second condition on the same exclusion clause, on
  the same terms D-044 sets: an application whose injected form is degenerate is neither a
  pass nor a failure. It is evaluated **per injected form and not per unit**, so a unit may
  carry interpretable forms and degenerate ones at once and only the interpretable ones
  count.
- **Applies from D-045 onward.** No landed application is reclassified and no membership row
  moves.
- **Rationale:** A degenerate injection does not make a result false, it makes it
  uninterpretable: the condition measured something other than what the test asks about.
  Recording such a condition as either a pass or a failure writes down a measurement that was
  not made. The per-form reading is what D-038 already did and is the only reading under
  which a unit with one clean side and one degenerate side can be reported at all.
- **Evidence, and its extent.** D-030 registered the check and is the one unit where it
  decides the reading: the only double-recovering oracle condition there injected three
  tokens, one absent from the corpus vocabulary and one with term frequency 0 in both
  required passages, so its whole effect was to restore a name the question already carried
  in a form the tokenizer had destroyed. The recount already records D-030 as not applicable
  on that ground, which is the precedent D-044 relies on. D-035 is where the check is passed
  rather than merely recorded, the gain being carried by a token the question does not
  contain: appending `Philadelphia` alone gives 1 / 0.554958 and 2 / 0.499144 while appending
  `crime family` alone gives 1 / 0.564744 and 14 / 0.425469. D-038 supplies the per-form
  reading directly: the premise is met on the answer side, no form of that name occurring in
  the question, and half met on the constraint side, one word of that title already being in
  the question, and D-038 recorded the two sides separately rather than declaring the whole
  application degenerate.
- **Registry effect:** the same exclusion clause gains the second condition and the entry
  gains D-045 as a decision source. No definition, no inclusion rule and no affected unit
  changes here. Pit 24b gains the same qualifier in the handoff.
- **What this does not settle:** whether a degenerate passing condition is evidence *against*
  the descriptor. It is not read that way here, and D-030's unit was routed to
  `surface_form_tokenization_mismatch` on independent grounds. Also untouched: the first
  precondition, which D-044 rules on, and the form set and its required coverage, which D-046
  rules on.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
  `5a83880e554299123d8c214e|bm25`, `5add67915542992200553af8|dense` and
  `5ae1801955429901ffe4aec4|dense` supply the measurements.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-03,
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5a83880e554299123d8c214e.md` and
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5add67915542992200553af8.md`.

## D-046 - Define the oracle-name test's form set, and require per-passage coverage before the bar fires

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** Two clauses. **The form set.** A form of the single-factor oracle-name test
  is one surface form of a required passage's own entity name, injected on its own. A
  condition that injects two anchors at once, and a condition that injects some other
  entity's name, are not forms of this test; they are recorded as oracle evidence and read
  under pit 15 like any other oracle condition. **Coverage.** The passing half stays
  existential: one form bringing both required passages inside the cutoff is a pass. The
  failing half requires that at least one form of each required passage's own name has been
  run, and that all forms run fail, before the bar may fire.
- **Applies from D-046 onward.** No landed application is reclassified and no membership row
  moves.
- **Rationale:** The asymmetry follows D-041's own. A signal that only supports does not need
  an exhaustive battery behind it, and putting the stricter gate on the half D-041 made
  non-binding would buy nothing. A bar that forbids does need one, because a bar resting on a
  battery that never addressed one of the two required passages forbids on evidence about the
  other. The form set is written down because both boundaries have already been applied
  correctly in landed entries without ever being stated, which leaves the next reader to
  rediscover them.
- **Evidence, and its extent.** **Consistency, for the coverage clause on the passing half.**
  Of the four units where the test passes and this descriptor takes the primary, D-017 ran
  one form, D-023 five, D-026 seven and D-035 five, and none of the four is a mixed result,
  so a universal reading of the passing half would flip none of them. The one mixed
  application is D-029, five of seven forms recovering both required passages, and there the
  primary went to another name. The existential reading is therefore not carrying any unit
  that a universal reading would take away. **The form set.** D-038 ran two single injected
  titles, each recovering one side, and appending both together gives 2 / 0.416027 and
  1 / 0.464131, a double recovery, and the application is still recorded as a failure: a
  two-anchor condition is not a form of this test. D-033 is the converse case: injecting the
  name of the actress who plays the described entity gives 4 / 34.429059 and 5 / 32.699209,
  both inside the cutoff, and it is correctly outside the tally because the injected name is
  not the described entity's own; the two forms D-033 counts are appending `Dakota` at 4 and
  116 and naming her in place while keeping the description at 4 and 116. **Coverage.** Nine
  of the ten failing applications ran at least one form for each required passage: D-020,
  D-021, D-022 and D-038 two each, one per side, D-024 four, D-025 six, D-031 six, D-034 four
  and D-039 three. D-033 is the exception, both of its counted forms being anchors of the
  same required passage. The clause therefore describes what nine of ten did and names the
  tenth.
- **Registry effect:** the inclusion note and the exclusion clause of
  `description_only_bridge_entity` each gain one sentence, and the entry gains D-046 as a
  decision source. No definition and no affected unit changes here.
- **What this does not settle:** the two preconditions, which D-044 and D-045 rule on. A form
  that fails a precondition does not count toward coverage, because under those two decisions
  it is not an application at all. Pit 15's own scope is untouched: D-040 declined to extend
  its gold-knowledge restriction there and triage item T-61 carries that question.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
  `5ae1801955429901ffe4aec4|dense` and `5abcc96c5542996583600492|bm25` supply the two
  form-set measurements.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-05,
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ae1801955429901ffe4aec4.md` and
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5abcc96c5542996583600492.md`.

## D-047 - Repair `description_only_bridge_entity`'s definition, which names a backend

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** The definition drops the phrase `for lexical retrieval`. It states a property
  of the question and the required passage, that a required entity is identified by
  description rather than by name, and not a property of any scorer. A scope line records
  where the descriptor has actually been used, as provenance and not as a category.
- **Rationale:** A definition that names a retrieval mechanism as part of what it describes
  cannot cover uses on another mechanism, and here it excludes every unit on which the
  descriptor is the primary. Being unnamed in the question is a fact about the question; it
  is measurable the same way on both backends and was measured that way.
- **Evidence, and its extent.** The descriptor is the primary of four units and all four are
  Dense - `5a85cead5542991dd0999ea9|dense` at D-017, `5ade69e455429975fa854ec5|dense` at
  D-023, `5ae1f596554299234fd04372|dense` at D-026 and `5add67915542992200553af8|dense` at
  D-035 - counted from `case_memos_v2.csv`, and it is a secondary on ten further units, seven
  lexical and three Dense. The wording as written therefore excludes every unit on which it
  is the primary. D-023 registered the mismatch as a usage note without amending the
  definition, and D-026, D-035 and D-041 each restated it without amending it either. D-029
  measured the strongest form of the mismatch: on a Dense unit the query does carry the name,
  the required passage does contain it, and it is unique in the 4,937-passage corpus, yet a
  query consisting of exactly that name ranks the passage 2202 of 4,937 and the bare surname
  4243.
- **Registry effect:** the definition changes. The inclusion rule, the exclusion clause and
  the affected-units list are unchanged, and the entry gains D-047 as a decision source. A
  scope line is added recording four Dense primary uses and ten secondary uses, seven of them
  lexical. That line is provenance under pit 17 and must not be read as making retriever
  identity a category or as scoping the descriptor to one backend.
- **What this does not settle:** whether an anchor that is present but unusable falls inside
  this name or outside it. That is triage item T-09 and the repaired wording deliberately
  takes no position on it, so ruling T-09 either way needs no second repair here. Also
  untouched: the structural boundary D-026 recorded, triage item T-08, and the wording of any
  other entry, D-048 ruling separately on the one entry two handoff passages had grouped with
  this one.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-07, and
  `manual_review_v1/analysis/case_memos_v2.csv`.

## D-048 - Restate `related_name_document_crowding`'s name-token wording as a property of passage text

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** The definition's `sharing a name or name token` is restated so that it
  plainly describes the competing passage's own text - its body carries the queried entity's
  name, or a token of that name - rather than anything about how a scorer matches. The
  substance of the definition, the inclusion rule and the exclusion clause are unchanged. A
  scope line records that on both bi-encoder adoptions the whole name is present verbatim, so
  the token half of the disjunction has never carried an adoption on that backend.
- **Rationale:** This is a smaller repair than D-047's and for a different reason, and the
  difference is worth stating because two landed handoff passages call the two cases the same
  shape. D-047's wording named the retrieval mechanism, so that definition excluded its own
  primary uses. This wording names a property of passage text, which both backends have, and
  it held literally on both bi-encoder adoptions. What is repaired is only that `name token`
  can be read as naming a matching mechanism.
- **Evidence, and its extent.** D-027 adopted the descriptor on a Dense unit and recorded in
  the same paragraph that all six competitors literally contain `Albee` in their text, so
  that the surface fact holds, registering the wording question rather than closing it. D-031
  is the other bi-encoder adoption and all eight of its competitors contain the string
  `Harold Godwinson`. The token half of the disjunction has therefore never been the operative
  one on that backend. The descriptor is the primary of no unit and a secondary of six, four
  lexical and two Dense, counted from `case_memos_v2.csv`, so no primary use turns on this
  wording and D-043's crowding primary-use contract does not reach it.
- **Registry effect:** the definition's wording changes and its substance does not. The
  inclusion rule, the exclusion clause and the affected-units list are unchanged, and the
  entry gains D-048 as a decision source.
- **What this does not settle:** the overlap with `same_topic_passage_distractor`, triage
  item T-24; the operational meaning of `explains the primary failure` in this entry's first
  exclusion, item T-22; and whether a crowding descriptor whose query-only definition
  contains a required gold should be barred from primary use by rule, item T-25. The
  handoff's description of items T-07 and T-21 as the same shape is corrected in this landing
  as prose, which is a correction of record and not a decision.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-21,
  `manual_review_v1/analysis/per_case_analysis/dense_comparison_5a78b209554299148911f93e.md`
  and `manual_review_v1/analysis/case_memos_v2.csv`.

## D-049 - Write down the mechanical-separability line the D-028 and D-030 pair implies

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** Within the preprocessing vocabulary, a distinct descriptor is warranted only
  when the implementation choice at issue is a separable pipeline decision, such as which field
  is indexed, rather than another value, side, affected passage or instance of the same
  normalization decision. Another value of an already covered decision is folded into the
  existing name. This line is scoped to the preprocessing vocabulary and is **not** adopted as
  a universal naming law for other taxonomy families.
- **Rationale:** The line already exists in two landed entries and has been applied three
  times, once to coin a name and twice to refuse one, with consistent results. What it lacked
  was a place sections 8 to 13 can cite without re-deriving it from two entries' prose. The
  scoping is deliberate rather than cautious: the evidence behind the line is entirely about
  text normalization and index-field choice, so a naming law written from it would carry no
  measurement behind it in the crowding, bridge or evaluation families.
- **Evidence, and its extent.** D-030 states the line, recording that D-028 registered a
  separate descriptor because the choice of indexed field is mechanically separable from the
  choice of text normalization, and that the argument does not transfer to a normalization
  question; on that ground D-030 refused to coin a name for the possessive clitic and
  registered no new entry. D-033 applied the same line in the same direction, recording that
  folding its two-sided shape in follows D-030's reasoning and not D-028's, since which side a
  normalization fails on is not a different level of decision. D-028 is the one coinage on the
  other side of the line. The extent is three applications, all on lexical units and all inside
  one primary's evidence base, which is why the scope above is part of the decision rather than
  a caveat on it. Two candidate lines are recorded as rejected on the evidence and not on
  preference. Co-necessity does not discriminate: D-028 offers it as a second reason for
  coining, but the possessive clitic D-030 declined to name is co-necessary too, being the
  whole primary there. Recurrence does not discriminate either: it would have coined nothing at
  D-028, the first occurrence of that interaction, and something at D-030, whose sub-mechanism
  recurs at D-033.
- **Registry effect:** none. No entry is created or deleted and no entry's definition,
  inclusion rule, exclusion rule or affected-units list changes. The line is a naming rule over
  a group of names rather than a clause of any one entry, so it lands in this entry and in the
  audit, and it is carried into `candidate_taxonomy_v0_1.md` at the categories stage alongside
  D-041's and D-043's primary-use contracts.
- **What this does not settle:** whether the primary this line has been applied around should
  be narrowed, triage item T-27, and whether `unindexed_title_name_anchor` should be folded
  into it, item T-30; both are ruled separately in this landing. It takes no position on any
  naming question outside the preprocessing vocabulary, and in particular does not reach the
  split and overlap items T-09, T-19, T-23 and T-24.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/open_code_decision_log.md` D-028, D-030 and D-033,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-29, and
  `manual_review_v1/analysis/taxonomy_todo.md` section C item 5.

## D-050 - Retain `unindexed_title_name_anchor` instead of folding it into the preprocessing primary

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** `unindexed_title_name_anchor` stays an independent provisional secondary
  descriptor and is not folded into `minimal_preprocessing_score_distortion`. Its definition,
  inclusion rule, exclusion rule and affected-units list are unchanged by this decision.
- **Rationale:** This is the corollary of D-049 read on the side of the line D-028 was on:
  which field is indexed is a separable pipeline decision, not another value of the
  normalization decision. Folding would keep the two refusals that line produced and discard
  the one coinage they were justified against. Two further grounds do not depend on D-049. When
  this fold was put, the entry carried a full written contract and the receiving primary had no
  registry entry and no stated contract at all, so the fold would move a specified name into an
  unspecified one; D-052 gives that primary a prospective primary-use contract later in this
  same landing, which is one exclusion gate and not a definition, inclusion rule and exclusion
  rule, so the asymmetry this ground rests on narrows but does not close. And the fold would
  widen a primary that D-028, D-030, D-033 and D-034 each record as possibly too broad, which
  is the ground D-028 itself gave for registering this name instead of folding it.
- **Evidence, and its extent.** The entry is adopted on two units,
  `5a79b7f6554299029c4b5f6f|bm25` at D-028 and `5ab8f57b5542991b5579f097|bm25` at D-032, and it
  records three non-adoptions, D-030, D-033 and D-039, each firing one of its own exclusion
  clauses rather than an argument from outside the entry. Its measured behaviour comes apart
  from the primary's: the title-indexing series in `tools/recount.py` section 7a has
  twenty-one members, fourteen inert or negative, five materially positive and two one-sided
  positive, and this descriptor is adopted on two of the twenty-one while the primary holds
  nine units. D-039 is the sharpest separation, the title-indexing condition being materially
  positive there at 6 / 18.769969 to 2 / 23.750585 and the entry still refused, because the
  indexed body's raw term frequencies of 1, 2 and 1 show title indexing amplifying an anchor
  that already matched rather than recovering an unmatchable one. The counter-argument is
  recorded and not adopted: both names concern the same indexing pipeline and both are repaired
  by changing the indexer. It fails because D-028 and D-030 already drew a line inside that
  pipeline, and drew it between which field and which normalization.
- **Registry effect:** the entry gains D-050 as a decision source and one paragraph recording
  that the fold was considered and refused. It gains no affected unit, this decision adopting
  it on nothing. No definition, inclusion rule or exclusion rule changes, and the registry
  stays at 26 adopted descriptors.
- **What this does not settle:** the entry's own conditions, which stay open as triage items
  T-31, T-32 and T-33 - whether it must require its semantic reading to reach the cutoff,
  whether it should still be refused on the form of the anchor alone when the semantic reading
  is maximal and the indexing reading positive, and whether its first exclusion should be
  stated as a term-frequency test. This decision settles only that there is a name for those
  three items to be about.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-30,
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5ae60426554299546bf83019.md`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-028, D-032 and D-039.

## D-051 - A prospective passage-level reverse boundary for the preprocessing primary

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** For a required passage whose failure `minimal_preprocessing_score_distortion`
  is claimed to explain, the exclusion fires if the minimal gold-targeted normalization of that
  passage changes **0 rank positions**, or if the corresponding corpus-wide deployable
  normalization has a **negative** score effect. Both cells are needed to apply this gate; an
  unrun cell is recorded `not_applicable`, which is neither a pass nor a failure and is not
  positive evidence. The boundary is judged per required passage and not per unit. It is
  prospective: no existing unit is reclassified.
- **Rationale:** That an unperformed normalization exists is not by itself the mechanism. What
  the gate adds is that the normalization must be worth rank positions and that its deployable
  form must not be negative. Stating it as an exclusion rather than an inclusion condition is
  deliberate. The pair of cells only became mandatory with pit 19ae, which D-036 and D-039
  established, and pit 19ae itself records that D-028's single-token repair ran the
  gold-targeted version and a null control but not the corpus-wide one. As an inclusion
  condition the gate would retroactively invalidate landed adoptions that could not have run
  it; as an exclusion with a `not_applicable` escape those applications simply fall outside it
  and the append-only log is untouched.
- **Evidence, and its extent.** D-039 is the one unit supplying both halves, and it splits
  across its two required passages, which is why the gate is stated per passage. On the
  constraint passage the gold-targeted repair moves 8 / 17.987437 to 2 / 21.350963, worth
  2.580995 points and 4 rank positions against a null control whose residual over all 4,937
  rows is 0.000e+00, and the deployable version over the 2,387 passages the form occurs in
  moves 8 / 17.888265 to 2 / 21.158602, worth 2.388634 points and the same 4 rank positions. On
  the answer passage the gold-targeted repair is worth 0.628238 points and **0 rank positions**
  and the deployable version is worth **-0.024046 points**, the same repair giving more to the
  competitors than to the passage; that is the recorded ground on which D-039 refused this
  primary. The extent is one unit, two required passages, one measured negative deployable case
  and no measured zero deployable case. The `not_applicable` treatment of an unrun cell is not
  new reasoning: D-044 and D-045 gave the two preconditions of the single-factor oracle-name
  test this same shape, and D-046 settled the per-passage against existential question for that
  test's form set the same way.
- **Registry effect:** none. This primary has no registry entry, that file defining adopted
  secondaries, so the gate lands in this entry and in the audit and is carried into
  `candidate_taxonomy_v0_1.md` at the categories stage.
  `surface_form_tokenization_mismatch`, which carries the D-039 measurements quoted above as a
  secondary, is not edited: the gate constrains a primary-use claim and not that entry's own
  contract.
- **What this does not settle:** the deployable zero-effect case, which no unit supplies and
  which this gate therefore leaves outside itself in both directions, and every nonzero numeric
  magnitude threshold, since neither a score threshold nor a rank-position threshold above zero
  is derivable from one unit. Those are left open the way D-042 left the never-decided
  percentage band open. Under pit 17 the rank positions and score deltas above are properties
  of an intervention and not a category, and this gate creates no category named after a rank,
  a score or a cutoff.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/open_code_decision_log.md` D-039,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-28,
  `manual_review_v1/analysis/per_case_analysis/bm25_bridge_5ae60426554299546bf83019.md`, and
  `manual_review_v1/analysis/taxonomy_todo.md` section F pit 19ae.

## D-052 - Retain one `minimal_preprocessing_score_distortion` primary and narrow it prospectively

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** One name is retained. The primary is not split by backend and not split into
  one descriptor per sub-mechanism. Its prospective primary-use contract is narrowed by the
  reverse boundary D-051 states. The six sub-mechanisms it covers are recorded below as an
  explicit member enumeration, and future text states that enumeration rather than an ordinal
  such as `the seventh sub-mechanism`. The name is **not** added to the Provisional Secondary
  Descriptor Registry, whose stated purpose is to define adopted secondaries; the primary-use
  contract lives in this entry and in the audit and is carried into
  `candidate_taxonomy_v0_1.md` at the categories stage. No memo row is reclassified.
- **Rationale:** Breadth is a defect where the covered sub-mechanisms need different evidence
  or different repairs. The ground for one name here is narrower than any claim about all six
  members. The primary names one implementation decision, how text is normalized before it is
  indexed and matched, and five of the six members are values of that one decision: repeated
  function words, punctuation false negatives, query-scaffold inflation, the Unicode dash and
  the possessive clitic. Which side the normalization fails on and which required passage it
  costs are not further decisions, per D-030 and D-033. Splitting those five would be splitting
  one decision by its values, which is what D-049 writes down as not warranting a separate name.
  The sixth member is stated here as an exception rather than absorbed into a universal claim.
  D-028's member is a two-factor interaction between boundary punctuation and which field is
  indexed, and the index-field factor is exactly the separable pipeline decision D-049
  identifies and D-050 has just kept outside this primary under a name of its own. The two are
  reconciled by what this enumeration does and does not assert. The index-field half of that
  interaction is carried by `unindexed_title_name_anchor`, registered for it at D-028 and
  retained independent at D-050; this primary carries the punctuation half only, which is
  already the second member of the enumeration. The interaction is listed because at that unit
  the punctuation factor was decisive only in combination with the indexing choice, which is a
  property of how the normalization effect had to be measured there and not a second decision
  taken inside this name. So the member neither widens the primary past that one decision nor
  argues for a split, what it would be split into already existing under another name.
  Splitting would also run against the reason D-025 through D-030 each gave for declining to
  register a name whose observation an existing contract already covers. What the width
  complaint does identify correctly is that the name had no stated limit, and D-051 now
  supplies one, so the narrowing is done by contract rather than by division. The enumeration
  is recorded because the count had been carried as an ordinal in
  four landed entries; the ordinal form is what broke the title-indexing, dilution-gate and
  oracle-name series, and the 2026-08-05 ruling retiring the global measurement ordinal applies
  to a sub-mechanism count for the same reason.
- **Evidence, and its extent.** The primary holds nine of the thirty units, counted from
  `case_memos_v2.csv`: `5a7d61775542991319bc93b9|bm25` at D-012,
  `5a7c9f325542990527d554e6|bm25` at D-014, `5a83a532554299334474606f|bm25` at D-016,
  `5ab72a025542992aa3b8c7b8|bm25` at D-019, `5ac1a3665542994ab5c67daf|bm25` at D-021,
  `5a79b7f6554299029c4b5f6f|bm25` at D-028, `5a83880e554299123d8c214e|bm25` at D-030,
  `5abcc96c5542996583600492|bm25` at D-033 and `5adc8977554299438c868de2|bm25` at D-034. The
  six sub-mechanisms, as already enumerated in `taxonomy_todo.md` section C item 5, are
  repeated-function-word amplification; punctuation false negatives; query-scaffold score
  inflation; Unicode-dash mismatch; the two-factor interaction between boundary punctuation and
  which field is indexed, added by D-028; and the possessive clitic, added by D-030. Boundary
  punctuation is the oldest of the six per D-034 and the clitic is the sixth per D-033, and
  D-033 and D-034 each add a new shape of an existing member rather than a seventh member. All
  nine units are lexical. That is provenance under pit 17 and not a ground for a backend split:
  the reasoning D-047 used when it removed a backend from a definition applies here in the
  other direction, so the distribution is recorded as scope and the name is not written around
  a retriever.
- **Registry effect:** none. No entry is created for this primary, and no existing entry's
  definition, inclusion rule, exclusion rule or affected-units list changes.
- **What this does not settle:** whether this primary belongs to any final candidate category.
  Section 8's intake does not currently list it, which is a planning gap to be reconciled
  before the categories stage rather than by this entry. It does not touch the
  `taxonomy_defect_flag=true` row `5a7d61775542991319bc93b9|bm25`, whose flag is evidence for
  triage item T-49 and is ruled on with the other two flagged rows in the third batch. It sets
  no numeric magnitude threshold, D-051 leaving those open, and it reclassifies nothing.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/taxonomy_todo.md` section C item 5,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-27,
  `manual_review_v1/analysis/case_memos_v2.csv`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-012, D-014, D-016, D-019, D-021,
  D-028, D-030, D-033 and D-034.

## D-053 - Retain one `description_only_bridge_entity` and route the unusable-anchor residue

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** One `description_only_bridge_entity` is retained. It is not split into an
  absent-name descriptor and an unusable-anchor descriptor, and it is not widened to cover a
  required entity the question names explicitly but ineffectively. The definition's property,
  that a required entity is identified by description rather than by name, is unchanged, as
  are the inclusion rule and the exclusion clause. A prospective boundary and routing note is
  added to the entry: a failure of one name's surface form under the implemented tokenizer
  routes to `surface_form_tokenization_mismatch`; a failure between two conventional names of
  the same entity routes to `entity_alias_reference_mismatch`; competition from a distinct
  entity sharing a name form routes to `proper_name_homonym_collision`; and an explanation
  resting on how a required passage's own text is composed may route to
  `peripheral_passage_content_dilution` only where that entry's four inclusion conditions have
  been satisfied. Where no route carries it, a named-but-ineffective anchor is recorded as a
  measured fact of that unit without coining a descriptor. No unit is reclassified.
- **Rationale:** Splitting needs a second name with its own definition, inclusion rule and
  exclusion clause, and every landed observation of the unusable shape already has a
  disposition: it is carried by another registered name, attributed to that unit's own adopted
  primary, or recorded inside an adopted use of this same descriptor. A second name would
  therefore be written for a residue of zero units. Widening is worse than splitting. The
  exclusion clause fires when the target entity is explicitly named, so a reading that also
  covered an explicitly named but ineffective anchor would put the definition against its own
  first exclusion, and it would unsettle the subject of D-041's bar, since the units where the
  anchor is present are exactly the configuration D-039 records as making the inclusion rule
  fail before the test is run. Keeping the absent-name property is the narrower claim. What the
  routes add is that the residue stays visible instead of being absorbed by the widest name in
  its neighbourhood, which is the failure mode pit 17 describes for a name that states an
  output pattern.
- **Evidence, and its extent.** The shape is recorded on four landed entries, each from a
  different side. D-029 opened it in its strongest measured form: on
  `5a81ebee554299676cceb16d|dense` the query carries the name, the required passage contains
  it and it is unique in the 4,937-passage corpus, yet a query reduced to that name ranks the
  passage 2202 of 4,937 and the bare surname 4243. This descriptor is a secondary of that
  unit, so the observation already sits inside an adopted use of it. D-030 routes the same
  shape elsewhere on `5a83880e554299123d8c214e|bm25`, where the question's only entity name is
  explicitly present in both required passages, the possessive token `suicide's` occurs in 0
  of 4,937 passages, and deleting it reproduces the whole ranking bit for bit at 0 order
  mismatches; this entry's first exclusion refuses the name there and
  `surface_form_tokenization_mismatch` carries the surface form. D-035 adds a third form on
  `5add67915542992200553af8|dense`, where the descriptive substitute is present verbatim and
  near-unique and is still not discriminative: exactly 2 of 4,937 passages contain
  `is an Italian American criminal organization`, the reduced query ranks the bridge passage
  1 / 0.541525 and the full question ranks it 7 / 0.438223. That unit's primary is this
  descriptor, so the observation lies inside its own evidence base. D-037 gives the boundary
  its first mechanical account on `5ae048a255429924de1b708e|dense`, attributing the unusable
  anchor to that unit's adopted primary and stating that no separate descriptor is needed for
  it; the same entry registers the question this decision answers. Counted from
  `case_memos_v2.csv` the descriptor is the primary of 4 units and a secondary of 10. The
  extent is four units and no unit on which a named-but-ineffective anchor is the only
  unexplained property, which is why the ruling is one name plus routes and not two names.
- **Registry effect:** the entry gains D-053 as a decision source, one paragraph and one
  boundary-and-routing bullet, and it gains no affected unit, this decision adopting it on
  nothing. The definition, the inclusion rule, the exclusion clause and the affected-units
  list are unchanged, and the registry stays at 26 adopted descriptors. Three of the four
  routes restate clauses already on disk: `entity_alias_reference_mismatch`'s exclusion
  already sends an entity that is not named at all to this descriptor, a punctuation or
  morphology variant of one name to `surface_form_tokenization_mismatch`, and a distinct
  entity sharing a name form to `proper_name_homonym_collision`. What is new is that they are
  collected under this entry and that the fourth route carries the receiving entry's gate as a
  condition rather than as advice.
- **What this does not settle:** the structural boundary D-026 recorded, whether the described
  entity may be the answer passage's own subject, item T-08; the ordering between a passing
  test and a refuting non-oracle condition, item T-04; and what the test means when it
  excludes without naming a winner, item T-06. It sets no threshold at which an anchor counts
  as unusable, no unit supplying a graded series, and it does not touch the placement of the
  dilution gate the fourth route depends on, item T-40. It is explicitly **not** a ruling that
  a residual case can never warrant a new name: an observation with genuinely separable
  evidence remains eligible for a later owner ruling, and this decision pre-empts none.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-09,
  `manual_review_v1/analysis/case_memos_v2.csv`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-029, D-030, D-035 and D-037.

## D-054 - One `question_frame_semantic_crowding`, governed by the shared crowding contract

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** One `question_frame_semantic_crowding` is retained. It is not split into a
  primary-facing name and a secondary-facing name, and it is given no primary-use contract of
  its own. Its primary use is governed by D-043's shared crowding-family contract together
  with this entry's existing inclusion rule and exclusion clause. The stale sentence in the
  entry's note on primary use, which still calls this a vocabulary-audit question, is replaced
  by a statement of that governance. The definition, the inclusion rule, the exclusion clause
  and the affected-units list are unchanged, and no primary or secondary assignment moves.
- **Rationale:** Standing in both inventories is not by itself a defect. A primary use and a
  secondary use of this name rest on the same inclusion rule, that at least two higher-ranked
  passages match the framing facets while containing none of the decisive referent wording and
  that the competition persists when the referent cue is removed or replaced; they are two
  strengths of one body of evidence rather than two mechanisms. What distinguishes the primary
  use is that the family-scoped intervention is the one that moves both required passages,
  which is a claim about outcome and not about a different competing family. A second,
  descriptor-specific contract would restate D-043's gate for one member of the family that
  gate was written over, and D-043 was written over the family exactly so that each member
  would not need one. The note is edited nevertheless: leaving a settled question described as
  open is the kind of stale cross-reference this audit exists to remove.
- **Evidence, and its extent.** Counted from `case_memos_v2.csv` the name is the primary of 1
  unit and a secondary of 3. D-029 is the primary use, on `5a81ebee554299676cceb16d|dense`,
  and it is the first time the project's primary inventory grew by promoting a registered
  secondary rather than by coining a name. Its footing is a rule over passage content: of the
  42 passages above the bridge hop, 36 carry a film or directing cue, 19 a person-role cue, 16
  both and 12 the word `italian`, with the same four counts running 77, 48, 41 and 20 among
  the 92 above the answer hop, and not one of them names either required subject. D-043's
  second clause holds there, no required passage falling inside that content rule, so the
  shared contract is satisfied on the one unit where primary use exists. The three secondary
  uses turn on the same inclusion rule at lower strength, D-025 adopting the descriptor for
  the family the answer facet produces while assigning the other family to the primary
  mechanism under the third exclusion, and D-037 measuring both directions with 0 of the 38
  passages above the constraint hop containing either decisive name. Three recorded
  non-adoptions bound it from the other side: D-031, where the inclusion rule's controlled
  condition fails outright; D-035, where the third exclusion fires because the referring cue
  reproduces the family and the frame reproduces none of it; and D-038, where the frame cannot
  reproduce its own family in the forward direction. The extent is four adoptions and three
  refusals, every one of them on the bi-encoder. That distribution is scope under pit 17 and
  not a ground for writing a retriever into the name, which is the direction D-047 settled.
- **Registry effect:** the entry gains D-054 as a decision source, one paragraph, and one
  replaced sentence inside its note on primary use. It gains no affected unit. The definition,
  the inclusion rule, the exclusion clause and the affected-units list are unchanged, and the
  registry stays at 26 adopted descriptors. No second contract is written anywhere, and
  D-043's text is not amended.
- **What this does not settle:** whether this descriptor was rightly the closest competitor
  rather than the primary at D-037, which turned on outcome-determinacy and is not reopened;
  what counts as measuring a family's effect on a bi-encoder, where every index-side removal
  is an arithmetic identity by D-035, which D-043 left open and which is item T-26; whether a
  secondary may be adopted as a scoped subset of its own primary's competing family, item
  T-20; and whether a crowding descriptor whose query-only definition contains a required gold
  should be barred from primary use by rule, item T-25. This ruling is a precedent for the
  parallel question about `cross_passage_conjunction_unresolved`, item T-10, **by analogy
  only**: that name's evidence base and its position in the two inventories are different, and
  T-10 stays open and is not disposed of here.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-19,
  `manual_review_v1/analysis/case_memos_v2.csv`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-025, D-029, D-031, D-035, D-037,
  D-038 and D-043.

## D-055 - Keep `same_topic_passage_distractor` and `generic_term_lexical_crowding` apart, on a passage-level boundary

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** `same_topic_passage_distractor` and `generic_term_lexical_crowding` are both
  retained and are not merged. Item T-24 covers exactly this pair. The boundary between them
  is written into both entries at passage level: a competing passage whose body verifies a
  real connection to the queried entity, work or topic and also verifies a missing decisive
  constraint is described by `same_topic_passage_distractor`; a competing passage matching
  broad category, institutional or relational vocabulary from the query without that verified
  connection is described by `generic_term_lexical_crowding`. Different subsets of the
  passages above a required passage may carry the two descriptors within one unit; the same
  passage set must not carry both. No definition, inclusion rule or exclusion clause changes,
  and no assignment moves.
- **Rationale:** The overlap is real and was registered as such, D-028 declining
  `same_topic_passage_distractor` because the shared material was the question's broad
  category vocabulary and the sibling name was the more specific fit. That is already the
  boundary; what it lacked was a place outside one entry's non-adoption prose, so each later
  unit re-derived it. Stating it as a property of a passage rather than of a unit is what the
  landed uses did in practice: three of the four adoptions of the topical name enumerate the
  individual passages they cover and say which passages they do not. The boundary is
  deliberately **not** made three-way. A route to `question_frame_semantic_crowding` would put
  a backend-shaped name inside a boundary whose two sides are drawn on read passage text, and
  it would decide by side effect the questions items T-19 and T-26 hold.
  `related_name_document_crowding` is likewise not folded in. D-048's sentence identifying its
  overlap with `same_topic_passage_distractor` as item T-24 is an incorrect cross-reference:
  T-24 is the pair ruled here. D-048 is append-only and stays as written; the related-name
  overlap is opened as its own triage item and is not ruled on in this landing.
- **Evidence, and its extent.** Counted from `case_memos_v2.csv`, the topical name is the
  primary of no unit and a secondary of 4, two lexical and two on the bi-encoder, and
  `generic_term_lexical_crowding` is the primary of no unit and a secondary of 9, all
  lexical. The two names co-occur on no unit at all, so the no-double-description rule
  records a regularity rather than repairing a violation. The boundary has been measured in
  both directions inside one unit. On `5ae60426554299546bf83019|bm25` D-039 adopts the topical
  name for a single passage, `COPS (animated TV series)` 1 / 24.991204, whose body states the
  connection to the queried distributor rather than leaving it to the title, and whose text
  contains neither `space` nor `western`, the only corpus passage containing `space western`
  being the answer gold itself; in the same unit it refuses the lexical name for the
  five-passage name family above the answer hop, recording that `celebrity` alone reproduces
  5 of 5 of that family while the whole genre facet reproduces 0 of 5, and that deleting the
  distributor name collapses it to 0 of 5 while deleting the genre facet leaves it at 5 of 5.
  That family is D-039's `related_name_document_crowding` set, and the topical name's single
  passage is one of its five members rather than a sixth passage beside them: the related-name
  set is `COPS (animated TV series)` 1 / 24.991204, `Sterling Entertainment Group`
  2 / 20.383253, `Noel C. Bloom` 3 / 20.201011, `Locke the Superman` 4 / 19.831276 and
  `Tottoi` 5 / 18.906282, the topical set is `COPS (animated TV series)` alone, the
  intersection of the two is that one passage, and four members carry the related name only.
  The pair this entry separates is unaffected by that nesting, the topical name and the
  lexical one being adopted together on no unit and on no passage set. On
  `5ae1801955429901ffe4aec4|dense` D-038 adopts the topical name for three of the ten passages
  above the answer hop and names the other seven as not covered, six of them excluded by the
  clause this boundary states, their only connection being the question's location frame. On
  `5add67915542992200553af8|dense` D-035 has the topical name and
  `generic_person_semantic_neighborhood` partition the ten passages above the answer passage
  exactly, 7 and 3. The negative side is D-028, which routes to the lexical sibling on the
  ground quoted above, and D-030, which excludes the topical name because no competitor
  mentions any queried work. The extent is thirteen units across the two names, no unit
  carrying both, and one unit in which the routing was measured rather than read.
- **Registry effect:** two entries are edited and neither gains an affected unit.
  `same_topic_passage_distractor` gains D-055 as a decision source, one paragraph and one
  boundary bullet; `generic_term_lexical_crowding` gains the same three. No definition,
  inclusion rule or exclusion clause changes anywhere in the file, and the registry stays at
  26 adopted descriptors. One known difference is deliberately left alone: the registry's
  affected-unit list for `generic_term_lexical_crowding` omits `5adc8977554299438c868de2|bm25`,
  which `case_memos_v2.csv` carries. That omission is one of three of the same shape, all
  three from the same landing, and it belongs to the third batch's synchronization work under
  item T-55; correcting it inside this landing is the silent repair section C forbids.
- **What this does not settle:** the operational meaning of `explains the primary failure` in
  `related_name_document_crowding`'s first exclusion, item T-22; the overlap between that name
  and `same_topic_passage_distractor`, which this landing opens as a separate triage item and
  leaves unresolved; whether the crowding vocabulary needs a rule barring primary use where a
  query-only family definition contains a required gold, item T-25; and what counts as
  measuring a family's effect on a bi-encoder, item T-26. It sets no threshold for how many
  passages a description must cover, it does not touch either entry's exclusion for a passage
  supplying a complete alternative answer, and it re-judges neither D-028 nor D-048.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-24,
  `manual_review_v1/analysis/case_memos_v2.csv`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-028, D-030, D-035, D-038, D-039 and
  D-048.

## D-056 - Keep partial coverage of the D-023 neighbourhood, and name the uncovered members

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** `generic_person_semantic_neighborhood` keeps the partial coverage D-023
  recorded. The name is not widened past its definition, no Dense-only same-domain descriptor
  is coined, and D-023's unit is neither reclassified nor given an added secondary. One
  prospective evidence-recording rule is added: where a dossier or an entry states that a
  competing family has been enumerated and the adopted descriptors cover only part of it, the
  uncovered members must be identified explicitly in that dossier, so that silence is never
  read as coverage. This is a rule about recording evidence and **not** a requirement that
  every high-ranked passage receive a descriptor. The entry's definition, inclusion rule and
  exclusion clause are unchanged; only decision provenance and boundary prose are added.
- **Rationale:** Of the three options section 10 names, two fail on the evidence rather than on
  preference. Widening fails on the definition, which is scoped to person biographies and
  person-related content while the uncovered half of that neighbourhood is unrelated films;
  covering both would mean deleting the person clause and leaving a name that says only that
  the competitors are semantically near, which is the shape pit 17 refuses. Coining a
  Dense-only same-domain name fails on measurement: D-035 considered such a name on its own
  unit and deleted it on three grounds, one being that the family it pointed at was already
  partitioned exactly by two registered names, and the D-023 evidence gives the film half no
  materiality of its own, its removal probe over all four person biographies in the top six
  moving the required passages only to 3 / 0.495152 and 28 / 0.400140, which that entry itself
  records as displacement. Keeping partial coverage is the remaining option. What it costs is
  legibility, and that is what the recording rule pays for: D-023 states that all 31 passages
  above the lower required passage were read in full, that 26 of the 30 non-gold passages among
  them name none of the queried entities, roughly half biographies and half unrelated films,
  and that no second descriptor was added for the film half. That last sentence is the only
  reason the gap is visible; the rule makes writing it obligatory rather than conscientious.
- **Evidence, and its extent.** Counted from `case_memos_v2.csv` the descriptor is the primary
  of no unit and a secondary of 4, all on the bi-encoder, the four adoptions being D-009,
  D-023, D-029 and D-035. D-023 is the unit that leaves the gap and says so in its own
  boundary section. Three later entries bound the reading. D-029 scopes the name to a counted
  subset of a larger family that a crowding primary already covers, 19 of the 42 passages
  above the bridge hop and 49 of the 92 above the answer hop, and registers that nesting as a
  question rather than closing it. D-031 is the one recorded refusal, every one of the five
  person biographies above the required evidence containing the string `Harold Godwinson` and
  stating its own relation to him, so that cluster is organized by the named entity and there
  is no generic half for the name to be scoped to. D-035 is the fourth adoption and the first
  unit whose question names no entity at all, so the definition's clause about explicitly
  named target entities has no referent there, which that entry carries as a boundary. The
  extent is four adoptions and one recorded refusal, all on the bi-encoder, and one unit
  supplying the uncovered half this decision declines to name. No unit measures that half's
  effect on its own, which is the reason no name is coined for it.
- **Ordering, and what it does not imply.** This decision lands after the ruling on the
  same-topic against generic-term boundary so that the boundary is already written when partial
  coverage is reaffirmed. The ordering concerns the record only. This decision does not
  re-analyse D-023, does not read that unit's film half against the boundary the previous
  decision states, and takes no position on which name would cover it if one were ever coined.
- **Registry effect:** the entry gains D-056 as a decision source and one paragraph recording
  the ruling and its boundary. It gains no affected unit. The definition, the inclusion rule,
  the exclusion clause and the affected-units list are unchanged, no entry is created, and the
  registry stays at 26 adopted descriptors. The recording rule governs dossiers and entries
  generally rather than any one entry's contract, so it lands in this decision and in the audit
  and is carried into `candidate_taxonomy_v0_1.md` at the categories stage alongside D-049's
  naming line and the primary-use contracts D-041, D-043 and D-052 state.
- **What this does not settle:** whether a secondary may be adopted as a scoped subset of its
  own primary's competing family, item T-20, which D-029's shape raises and which this decision
  deliberately leaves untouched; whether the converse gap D-031 recorded, a required passage's
  own measurable property left with no carrier once the dilution gate rejects, needs one, item
  T-45; and where that gate belongs, item T-40. It sets no threshold for how much of a family
  must be covered. It reclassifies nothing: D-023's primary, secondary set, tie-break,
  confidence and conclusions stand unchanged under red line 4.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-23,
  `manual_review_v1/analysis/case_memos_v2.csv`,
  `manual_review_v1/analysis/per_case_analysis/dense_bridge_5ade69e455429975fa854ec5.md`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-023, D-029, D-031 and D-035.

## D-057 - Synchronize the Albee / Barrie row with D-010

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** The row `5a78b209554299148911f93e|bm25` in `case_memos_v2.csv` is brought into
  agreement with D-010, which ruled on that unit on 2026-07-31. Its `primary_open_code`
  becomes `entity_name_tokenization_mismatch`, the name D-010 chose and the name the row
  already carries in `candidate_category`. Its `secondary_open_codes` become
  `cross_entity_token_recombination` followed by `related_name_document_crowding`: the first
  is the descriptor D-010 adopted and the row never received, the second is unchanged, and
  `missing_second_comparison_entity` departs because D-010 does not retain it.
  `closest_competing_category` already reads `one_sided_entity_crowding` and is left alone.
  This decision makes no new semantic judgment, re-reads no passage and re-runs no condition.
  It transcribes a landed ruling into the two fields that ruling was about.
- **Rationale:** Three grounds, none of them new. First, the project already classified this
  difference. Section 7.2 of `open_code_vocabulary_audit.md` calls it a synchronization
  discrepancy rather than a new semantic decision and states that the row-level
  synchronization will be handled explicitly during the validation workflow. That workflow
  closed at 26 of 26 with D-039, so the deferral has run out. Second, section C of
  `taxonomy_todo.md` forbids correcting the row *silently*, not correcting it at all; this
  entry is the decision that clause was waiting for. Third, the departing name states gold
  missingness, which pit 17 and D-003 forbid as a causal category, and D-034 deleted
  `general_answer_passage_missing` on exactly that ground. D-027, reviewing the Dense side of
  the same example, also declined the name, there because both required passages were
  retrieved at 8 and 9.
- **Evidence, and its extent.** The evidence is D-010's and is not re-opened here. That entry
  records that the reviewed lexical implementation indexes paragraph text but not titles and
  tokenizes by lowercasing and splitting on whitespace, with no punctuation normalization, no
  phrase matching, no entity boundaries and no initial expansion; that the query carries `j.`,
  `m.` and `barrie?` while the second required passage's text carries `james`, `matthew` and
  `barrie,`; that `J. Edward Snyder` reaches 15 by matching `j.` from one queried entity and
  `edward` from the other; and that Albee-related documents occupy 1 to 8. The extent is one
  lexical comparison unit reviewed in the D-009 to D-012 overlap batch, before the section 7A
  gate existed, with no factorial, no exact baseline reconstruction and no dossier. That
  extent is why this decision transcribes rather than re-reasons.
- **Counts, measured from disk before the write.** The distinct `primary_open_code` count in
  `case_memos_v2.csv` rises from 11 to 12: `one_sided_entity_crowding` falls from 3 rows to 2
  and stays in the column, and `entity_name_tokenization_mismatch` enters it for the first
  time. Secondary assignments stay at 96, one name replacing one name, while distinct
  secondary names fall from 27 to 26 because the departing name occurred on this row alone. It
  survives in the secondary-name union as a first-pass name, occurring once in
  `case_memos_v1.csv`, which is the treatment D-034 gave `general_answer_passage_missing` and
  D-036 gave `underdetermined_question`. The union is therefore unchanged at 50 distinct
  names. The derived union of primary names rises from 26 to 27 as a consequence, because
  `entity_name_tokenization_mismatch` had until now lived only in `candidate_category`; the
  curated primary inventory, which already counts it, is unchanged at 27.
- **Registry effect:** none is required. `cross_entity_token_recombination`'s affected-units
  list already carries `5a78b209554299148911f93e|bm25`, entered when D-010 registered the
  descriptor, and `related_name_document_crowding`'s carries it too, so both the arriving and
  the retained secondary are already recorded on the registry side and it was the memo row
  that was behind. The departing name has no entry, never having been adopted. No definition,
  inclusion rule, exclusion rule or affected-units list changes and the registry stays at 26
  adopted descriptors.
- **What this does not settle:** whether `entity_name_tokenization_mismatch` should eventually
  be folded into `minimal_preprocessing_score_distortion`, which the next decision leaves
  prospective; the boundary between that name and `surface_form_tokenization_mismatch`, which
  the next decision opens as a triage item; and anything about `one_sided_entity_crowding`,
  which keeps two other current primary rows and whose primary use D-043's shared crowding
  contract governs. It re-judges neither D-010 nor D-027, adds no unit to any registry entry,
  and touches no other row.
- **Affected units:** `5a78b209554299148911f93e|bm25`; three cells of one memo row change, the
  third being the `taxonomy_defect_flag` the next decision clears. No queue row, no dossier
  and no landed conclusion changes.
- **References:** `manual_review_v1/analysis/case_memos_v2.csv`,
  `manual_review_v1/analysis/open_code_vocabulary_audit.md` section 7.2,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-50,
  `manual_review_v1/analysis/taxonomy_todo.md` section C item 3, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-003, D-010, D-027 and D-034.

## D-058 - Clear the two remaining taxonomy-defect flags, and keep the fold prospective

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** `taxonomy_defect_flag` is set to `false` on `5a7d61775542991319bc93b9|bm25`
  and on `5a78b209554299148911f93e|bm25`. Neither row's primary, secondary set, closest
  competitor, tie-break, confidence or notes changes. On the first row the flag's stated
  ground no longer exists. On the second the flag is cleared **without** folding
  `entity_name_tokenization_mismatch` into `minimal_preprocessing_score_distortion`: that fold
  is left prospective under a stated condition, namely that D-051's two cells be measured on
  the unit first. The boundary between `entity_name_tokenization_mismatch` and
  `surface_form_tokenization_mismatch` is **opened** as a triage item and is not ruled on
  here.
- **Rationale:** The two flags carry different questions and are answered separately. On
  `5a7d61775542991319bc93b9|bm25`, D-012 set the flag because the vocabulary then lacked a
  general category covering both function-word score amplification and punctuation-sensitive
  false-negative matching. D-052 supplies exactly that: one retained
  `minimal_preprocessing_score_distortion` whose member enumeration opens with
  repeated-function-word amplification and punctuation false negatives. This row already
  carries that name as its primary and is the first of the nine units D-052 counts, so the
  flag now marks a gap that has been filled. D-052 declined to touch the flag and named this
  triage item as the place for it, which is where it is answered. On
  `5a78b209554299148911f93e|bm25`, D-010 set the flag to ask whether the mechanism should
  remain separate or merge into a broader lexical-cue category. Read on its face D-049's
  separability line points at merging, since a query-side name form the document side does not
  match is another value of the one normalization decision rather than a separable pipeline
  decision, and D-052's second member already covers punctuation false negatives. Three
  grounds hold the merge back, and they are recorded rather than weighed away. First, D-049 is
  scoped and prospective: it was written from three applications inside one primary's evidence
  base, and using it to overturn a ruling landed on 2026-07-31 would be the re-judgment red
  line 4 forbids. Second, the separable decision this unit does contain already has a name.
  Titles are not indexed here, which is precisely the index-field choice D-049 identifies and
  D-050 kept outside the primary under `unindexed_title_name_anchor`; on that reading the unit
  is an early instance of D-052's fifth member, the interaction between boundary punctuation
  and which field is indexed, rather than a unit needing a fresh name. Third, D-051 now
  governs entry to that primary and requires two cells on each required passage, the rank
  positions a gold-targeted repair is worth and the sign of the deployable version's score
  effect. This unit has neither, and it will not acquire them in this phase, which runs no
  measurement. Folding it in would add a tenth unit to that primary on evidence D-051 requires
  and this unit does not have.
- **Why the flag is cleared anyway.** `taxonomy_defect_flag` is a boolean, so it cannot record
  a retention under a prospective condition, and a `true` whose stated question has changed is
  worse than no marker: it would leave section 22 reading the row as undecided. The open part
  is therefore moved to where open parts belong. The fold is recorded here with its condition,
  and the never-written boundary between `entity_name_tokenization_mismatch` and the
  registered `surface_form_tokenization_mismatch` is opened as a new item in
  `vocabulary_audit_triage.md`. Opening an item repairs the record rather than deciding
  anything and carries no decision ID of its own, on the precedent D-055 set when it opened
  its own item and the precedent T-57 to T-60 set before that.
- **Evidence, and its extent.** For the first row the evidence is D-012's and D-052's and
  neither is re-opened: D-012 records that the scorer accumulates every query-token
  occurrence, so the four occurrences of `of`, the two of `the` and the two of
  `commander-in-chief` are each counted repeatedly, and that the required passages lose
  matches across `bharatpur,` against `bharatpur`, `india.` against `india`, `storming`
  against `stormed` and `castle?` against `fortress`; D-052 records the enumeration those two
  shapes are the first two members of. For the second row the evidence is D-010's, restated in
  the previous decision and not repeated. The extent of the merge question is one unit, and
  the reason it stays open is that the two cells D-051 requires have been measured on no unit
  of the D-009 to D-012 batch. Item T-56 records that all eleven units of that batch still
  have no dossier, so the gap is a known property of the batch and not a fresh finding.
- **Registry effect:** none. No entry is created or deleted, no definition, inclusion rule,
  exclusion rule or affected-units list changes, and the registry stays at 26 adopted
  descriptors. `entity_name_tokenization_mismatch` remains outside the registry because that
  file defines adopted secondaries and this is a primary, which is the treatment D-052 gave
  `minimal_preprocessing_score_distortion`.
- **What this does not settle:** whether `entity_name_tokenization_mismatch` and
  `surface_form_tokenization_mismatch` are one name or two, which is the item opened here;
  whether the fold should happen once D-051's cells exist, which this entry states as a
  condition and not as a promise; any numeric magnitude for those cells, D-051 having left
  every threshold open; and whether the D-009 to D-012 units should ever be re-run, item T-56.
  It reclassifies nothing and re-judges neither D-010, D-012, D-049, D-051 nor D-052.
- **Affected units:** `5a7d61775542991319bc93b9|bm25` and `5a78b209554299148911f93e|bm25`; one
  cell of each memo row changes. No primary, secondary, queue row, dossier or landed
  conclusion changes.
- **References:** `manual_review_v1/analysis/case_memos_v2.csv`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-49,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-010, D-012, D-028, D-049, D-050,
  D-051 and D-052.

## D-059 - Rename `quoted_phrase_semantic_drift` to `verbatim_epithet_sense_drift`

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** The primary `quoted_phrase_semantic_drift` is renamed
  `verbatim_epithet_sense_drift`. The rename reaches the two label fields of its one row,
  `5ab978855542996be2020512|dense`, and replaces the old name where it appears in that row's
  three prose fields, with a note that the name was changed by this decision. **No
  measurement, interpretation, tie-break, confidence or conclusion of D-020 changes**, and
  `case_memos_v1.csv` is not touched, so the old name survives there as a first-pass name. The
  row's `taxonomy_defect_flag` is set to `false`, the flag having been set for this rename and
  for nothing else. No registry entry is created: the registry defines adopted secondaries and
  this is a primary, the treatment D-052 gave the preprocessing primary.
- **Rationale:** The name asserts two things the unit's own conditions exclude. Condition A
  removes the quotation marks around the epithet and is inert in both directions, 465 /
  0.112206 to 479 / 0.111678 and 13 / 0.317347 to 12 / 0.318517, so quotation punctuation is
  not the mechanism. The backend performs no literal string matching at all, being a symmetric
  bi-encoder scoring L2-normalized whole-passage dot products, so the phrase-matching reading
  the name invites has no implementation behind it either. What the conditions do support is a
  sense drift: probe D, which is **not** oracle, makes the query exactly the verbatim epithet,
  and the single passage that literally contains it reaches only 106 / 0.219506 while the top
  five are `Heaven in Judaism`, `Buried Country`, `Dead at 17`, `Dead Jesus` and `Vidblain`, a
  religious, mythological and death-related neighbourhood. Probe E replaces the epithet with
  the plain noun `dwellings` and the required answer passage moves from 13 / 0.317347 to 5 /
  0.366752, so the same cue is also suppressing the other side. The new name states that: a
  verbatim epithet borrowed from one passage resolves to the sense neighbourhood of the
  epithet rather than to its source. This is the naming-versus-mechanism repair D-019
  performed when it replaced `same_topic_title_distractor`, the precedent D-020 itself cites,
  and the wording repair D-047 performed when it removed a backend from a definition rather
  than adding a note beside it.
- **Why not the alternatives.** Leaving the name and adding a usage note is refused on D-047's
  ground: the defect is in the name, and a note cannot stop the name from being carried into a
  candidate category at section 14. Reusing `literal_cue_topic_capture` is refused because
  D-014 judged it an output-level description and demoted it to closest competitor, and it has
  no entry, no inclusion rule and no exclusion rule to inherit. Folding the primary into
  `exact_string_source_dependency` is refused because that registered secondary is adopted on
  this same unit for the source hop only, its definition resting on the epithet being the
  passage's one distinctive connection to the query, whereas the primary also carries probe
  E's half, the suppression of the answer passage. Folding would leave one half of the unit
  with no carrier, which is the shape D-056's recording rule exists to make visible.
- **Why the new name is not a question property.** The name must not be read as saying that
  the question is defective, which is the shape pit 17 refuses and on which
  `question_wording_ambiguity` and `underdetermined_question` were deleted. It names a
  retrieval behaviour and is supported by two non-oracle conditions on the retriever's own
  scores, probe D and probe E. The question's use of an epithet is the input those conditions
  vary, not the claim.
- **Evidence, and its extent.** All figures are D-020's and none is re-measured. The baseline
  is an exact reconstruction with maximum absolute score error 2.384e-07, placing the required
  passages at 465 / 0.112206 and 13 / 0.317347, so the stored `not_in_top50` means 465 of
  4,937 rather than absence. The indexing condition T is inert to negative at 465 to 526 and
  13 to 16. The extent is one Dense bridge unit and one row; the name has never been used on
  any other unit, which `case_memos_v2.csv` confirms, so the rename moves no other label.
- **Counts, measured from disk before the write.** The curated primary inventory rises from 27
  to 28 distinct names, the arriving name being `verbatim_epithet_sense_drift` and the
  departing name `quoted_phrase_semantic_drift` remaining as a historical first-pass name in
  `case_memos_v1.csv`, the treatment D-019 gave `same_topic_title_distractor`. The distinct
  `primary_open_code` count in `case_memos_v2.csv` is unchanged, one name replacing one name.
  The secondary-name union is unchanged at 50 and the registry at 26 adopted descriptors.
- **Registry effect:** none. `exact_string_source_dependency` and
  `question_frame_semantic_crowding`, the two entries D-020 touched, keep their definitions,
  inclusion rules, exclusion rules and affected-units lists; neither names the renamed primary
  in its own text, which was verified before the write.
- **What this does not settle:** which candidate category this primary belongs to, a section
  14 question; whether the mechanism it names generalizes past one unit, which one unit cannot
  establish; and the boundary against `description_only_bridge_entity`, which D-020 settled
  for this unit by tie-break and D-053 has since bounded from the other side. It re-judges
  nothing in D-020, whose primary, secondary set, tie-break, confidence and speculation
  boundary all stand under red line 4.
- **Affected units:** `5ab978855542996be2020512|dense`; six cells of one memo row change, two
  labels, three prose fields in which only the name is replaced, and the defect flag. No queue
  row, no dossier and no landed conclusion changes.
- **References:** `manual_review_v1/analysis/case_memos_v2.csv`,
  `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-48,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-014, D-019, D-020, D-047, D-052,
  D-053 and D-056.

## D-060 - The vocabulary carries no question-quality descriptor

- **Date:** 2026-08-10
- **Status:** active
- **Decision:** No descriptor naming a defect, ambiguity or underspecification of the question
  is adopted, in either inventory. Observations of that shape are routed to the names that
  already carry them with a passage behind them: a passage inside the cutoff satisfying every
  explicit constraint goes to `plausible_non_gold_answer` or `gold_chain_not_unique`; an
  annotated chain with a substitute goes to `gold_chain_substitutability`; a question that
  describes its target instead of naming it goes to `description_only_bridge_entity`, whose
  own four routes D-053 fixed; a question wording that differs from the corpus wording goes to
  `surface_form_tokenization_mismatch` or `entity_alias_reference_mismatch`. A residue no
  route carries is recorded as a measured fact without a name, which is what D-025 already did
  and what D-053 states as the general treatment. Section 12 of `taxonomy_todo.md` is
  corrected in the same landing: its intake list drops the two deleted names and gains the
  routing above. It is **not** ruled that such a name may never be warranted in future.
- **Rationale:** The candidate names for this category have been coined twice and deleted
  twice, each time after a complete factorial rather than on preference, and each time on pit
  17. A third unit measured a real question defect and found it not decisive. The pattern is
  that a property of the question is not a retrieval mechanism, and that the observations
  behind every such name are already carried by a name that points at a passage. Adopting one
  now would reintroduce, by the front door, what two entries removed. What the rule costs is a
  place to put the residue, and the answer is D-025's and D-053's: record the measurement, do
  not name it.
- **Evidence, and its extent.** D-034 deleted `question_wording_ambiguity` after a
  sixteen-cell factorial in which its effect on the bridge passage was exactly zero in both
  preprocessing states while its one grammatically correct component was the worst cell on the
  other passage; the entry's stated ground is that the name states a defect of the question
  rather than a retrieval mechanism, which is what pit 17 warns against. The same entry
  deleted `general_answer_passage_missing` for stating gold missingness. D-036 deleted
  `underdetermined_question` after a full A by B by C factorial run in two preprocessing
  states in which all 8 cells whose added constraint is oracle placed both required passages
  inside the cutoff and all 8 non-oracle cells failed, in both states; its stated ground is
  that a question property only a fact from inside the golds can repair is not a retrieval
  mechanism, and that what the name recorded is already carried, with a passage behind it, by
  `gold_chain_not_unique`. Both entries satisfied pits 19k and 19ah before the verdict was
  read, which is why they are quotable here without re-measurement. D-025 supplies the third
  shape: a verified factual error in the question, which says the ruler was born in AD 43
  while the required passage records `(d. AD 43)`, measured and found not decisive at 115 to
  102 under its condition C and at 5 against 3 for the born and died forms of the same reduced
  description, with no descriptor adopted for it. The extent is two deletions and one
  measured-but-unnamed defect, across two backends, all three landed before this ruling.
- **What is deliberately not touched.** `possible_type_mismatch` stays as it is: it describes
  a passage's type against the question's expected answer type, not the quality of the
  question, and no unit is re-read against it here. `plausible_non_gold_answer`,
  `gold_chain_not_unique` and `gold_chain_substitutability` keep their definitions, inclusion
  rules and exclusion rules unchanged; this decision routes to them and does not widen them.
  No unit is reclassified and no adoption or non-adoption in any landed entry is revisited.
- **Registry effect:** none. No entry is created, deleted or edited, and the registry stays at
  26 adopted descriptors. The routing is a rule over a group of names rather than a clause of
  any one entry, so it lands in this decision and in the audit and is carried into
  `candidate_taxonomy_v0_1.md` at the categories stage, alongside D-049's naming line, D-053's
  routes and the primary-use contracts D-041, D-043 and D-052 state.
- **Section 12 effect.** The intake list of section 12 of `taxonomy_todo.md` still collects
  `question_wording_ambiguity` and `underdetermined_question`, both deleted, and its heading
  pairs question ambiguity with evaluation ambiguity. The list is corrected to the four names
  that remain and the routing above is recorded beside it. This is the same class of planning
  gap D-052 found in section 8, whose intake omits the largest primary in the column, and it
  is repaired here rather than left for the intake reconciliation because this ruling is what
  determines the list.
- **What this does not settle:** whether a future residue could ever warrant a name, which is
  left open on D-053's wording; the boundary between `plausible_non_gold_answer` and
  `description_only_bridge_entity` on one unit, item T-54; whether a substitute outside the
  cutoff counts, item T-51; and what section 12's category is finally called, a section 14
  question. It re-judges neither D-025, D-034 nor D-036.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/vocabulary_audit_triage.md` item T-52,
  `manual_review_v1/analysis/taxonomy_todo.md` section 12,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-003, D-025, D-034, D-036 and D-053.

## D-061 - Align the intake lists of sections 8 to 13 with the effective vocabulary

- **Date:** 2026-08-11
- **Status:** active
- **Decision:** The intake lists of sections 8 to 13 of `taxonomy_todo.md` are aligned to the
  effective vocabulary. Twelve collection lines naming retired names are removed, as a
  consequence of the decisions that retired them and with no successor name substituted for any
  of them. All 34 distinct effective names, held as 12 primary roles and 26 secondary roles over
  the 30 units of `case_memos_v2.csv`, are assigned at least one section in which each must be
  considered at the categories stage, as tabulated below; four names hold both roles and take
  the same section in each, which is why the distinct total is 34 and not 38. In the tables as
  landed every name takes exactly one home section, with eight further cross-references recorded
  from a second section. Section 8A, `Retriever Implementation Artifacts`, is opened for the
  retriever-implementation family, under a preamble landed in that section's own first paragraph
  stating that it is an intake workstream and not a sixth candidate category. An assignment
  states where a name is considered. It states nothing about whether that name warrants a
  category of its own, a merge into another name, or a place in `candidate_taxonomy_v0_1.md`. No
  unit is reclassified and no measurement is run.
- **Rationale:** Sections 8 to 13 were written before open coding. D-052 found one symptom of
  the gap, the absence of the largest primary from section 8's intake, and D-060 repaired
  section 12's list because its own ruling determined that list. The full check finds the same
  gap over 22 names and finds 12 collection lines pointing at names that no unit carries.
  Entering the categories stage against that list would mean building categories from an input
  that is both incomplete and partly dead. Aligning the list is a planning act over the whole
  intake rather than a ruling about any one name, which is why it is one entry rather than one
  entry per name, and why it is kept strictly separate from any merge, split or rename.
- **Track A, the twelve collection lines removed.** By the end of the four-overlap plus 26-unit
  validation sequence each name below had lost every carrying row. None was renamed; in each
  case the unit was re-coded and the name survives only in `case_memos_v1.csv`. The successor
  primary of the same unit is shown as evidence of where the observation went and is **not** a
  replacement name for the removed line. Nothing is written into a section in place of a removed
  line except by Track B:

| § | Line removed | Retirement basis | Successor primary of the same unit, for information only |
|---|---|---|---|
| 8 | `query_facet_fragmentation` | D-012 on `5a7d6177…\|bm25`; D-030 on `5a83880e…\|bm25` | `minimal_preprocessing_score_distortion` on both |
| 8 | `multiword_title_token_fragmentation` | D-019 on `5ab72a02…\|bm25` | `minimal_preprocessing_score_distortion` |
| 8 | `literal_cue_topic_capture` | D-014 on `5a7c9f32…\|bm25` | `minimal_preprocessing_score_distortion` |
| 8 | `near_title_collision` | D-022 on `5ade42b5…\|bm25` | `cross_passage_conjunction_unresolved` |
| 9 | `named_entity_anchor_distraction` | D-023 on `5ade69e4…\|dense` | `description_only_bridge_entity` |
| 10 | `related_document_crowding` | D-027 on `5a78b209…\|dense` | `one_sided_entity_crowding` |
| 10 | `same_domain_entity_crowding` | D-035 on `5add6791…\|dense` | `description_only_bridge_entity` |
| 10 | `adjacent_event_crowding` | D-026 on `5ae1f596…\|dense` | `description_only_bridge_entity` |
| 11 | `bridge_relation_underweighted` | D-031 on `5ab48c32…\|dense`; secondary use retired at D-028 and D-035 | `cross_passage_conjunction_unresolved` |
| 11 | `cross_entity_relation_unresolved` | D-029 on `5a81ebee…\|dense`; secondary use retired at D-033 | `question_frame_semantic_crowding` |
| 11 | `partial_bridge_only` | D-038 on `5ae18019…\|dense` | `cross_passage_conjunction_unresolved` |
| 11 | `weak_cross_domain_bridge` | D-017 on `5a85cead…\|dense` | `description_only_bridge_entity` |

  Removing a collection line whose name a landed decision already retired records a consequence
  of that decision and makes no new ruling of its own. Section 8 also carries three judgement
  lines that name retired mechanisms in prose rather than in code form, on title fragmentation,
  literal cue capture and near-title collision. Those are not collection lines, this decision
  does not remove them, and their subject matter is now carried by
  `minimal_preprocessing_score_distortion` and `cross_passage_conjunction_unresolved`. Whether
  to restate or drop them is left open.
- **Track B1, the 12 effective primaries, by primary role.** Units are the count of
  `case_memos_v2.csv` rows on which the name is the `primary_open_code`:

| Name | Units | Section | Ground | Decisions relied on | Prejudges a category? |
|---|---:|---|---|---|---|
| `minimal_preprocessing_score_distortion` | 9 | §8A | Names one implementation decision, how text is normalized before indexing, with six enumerated members; it absorbed three of section 8's removed names | D-012, D-030, D-049, D-051, D-052 | No |
| `cross_passage_conjunction_unresolved` | 6 | §11, already collected | Split-evidence mechanism; section 13 separately holds its unresolved primary-use question | D-017, D-020, D-022, D-024, D-040 | No, and the section-13 item stays open |
| `description_only_bridge_entity` | 4 | §11, already collected | Unnamed bridge entity; D-047 made the definition backend-neutral | D-041, D-044 to D-047, D-053 | No |
| `one_sided_entity_crowding` | 2 | §9, already collected | Crowding on one side of a named candidate set | D-010, D-027, D-032, D-043 | No |
| `plausible_non_gold_answer` | 2 | §12, already collected | D-060 makes it the first target of the evaluation-side routing | D-036, D-060 | No |
| `two_named_entities_underprioritized` | 1 | §9, already collected | Both named candidates under-ranked | D-009 | No |
| `entity_name_tokenization_mismatch` | 1 | §8A, cross-referenced from §9 | A tokenization failure on an entity name; D-010 chose it over an entity-competition name and already establishes an implementation-supported tokenization mechanism, so §8A carries the mechanism while the §9 cross-reference preserves the entity-competition context | D-010, D-057, D-058 | Ruled, approved as arranged; see the two non-settlements below |
| `same_entity_variant_crowding` | 1 | §10, already collected | Variants of one entity crowding the required passage | D-015 | No |
| `question_frame_semantic_crowding` | 1 | §10 | Crowding by the question's broad framing facets; D-043's shared crowding contract governs its primary use | D-020, D-043, D-054 | Mild; see the heading note below |
| `compound_two_sided_crowding` | 1 | §13, cross-referenced from §9 and §10 | Section 13's first item already collects units carrying two or more independent mechanisms, which is what D-018 found when it selected the compound primary | D-018 | Ruled, §13 retained; see below |
| `verbatim_epithet_sense_drift` | 1 | §10, cross-referenced from §8 and §11 | D-059 measures the mechanism as semantic sense-neighbourhood drift, explicitly not literal, exact-string or phrase matching; §8 is cross-referenced for the co-descriptor `exact_string_source_dependency`, which carries the source hop only, and §11 for `description_only_bridge_entity`, which D-020 names closest competitor | D-020, D-059 | Mild, in the same direction as the heading note below |
| `peripheral_passage_content_dilution` | 1 | §8A; its section-13 evidence-threshold item stays | A property of mean-pooled whole-passage encoding, verified at implementation level | D-023, D-025 to D-027, D-029, D-031, D-035, D-037, D-038 | No; the D-023 threshold question stays open in section 13 exactly as written |

  Distribution by primary role: §8A takes 3, §9 takes 2, §10 takes 3, §11 takes 2, §12 takes 1
  and §13 takes 1, which sums to 12. Section 8 proper receives no primary and keeps three
  secondaries.

  Three rows carry more than the table can hold. **`entity_name_tokenization_mismatch`** is
  approved as arranged, and the arrangement does not itself merge the name with
  `surface_form_tokenization_mismatch` or with the preprocessing primary; the two open questions
  travel with it and are restated under what this does not settle.
  **`compound_two_sided_crowding`** keeps §13 because the placement is faithful to an existing
  ruling rather than a new prejudgment: D-018 already found two independently evidenced crowding
  mechanisms on that unit. §10 was weighed and rejected, because it would carry the stronger new
  implication that the name is a unitary crowding-category candidate, which D-018 did not rule.
  What stays open is the name's final taxonomy representation.
  **`question_frame_semantic_crowding` and `verbatim_epithet_sense_drift`** are the mild cases,
  in one direction: section 10's heading says `Near-Neighbor`, framing crowding is not
  neighbourhood crowding, and the drift primary's neighbourhood is the sense neighbourhood of a
  cue rather than a set of near-duplicate documents or entity variants. Placement is about where
  a name is discussed, and the heading question is recorded as an open point below rather than
  settled here.
- **Track B2, the 26 effective secondaries, by secondary role.** The registry's 26 entries and
  the 26 distinct secondaries carried in `case_memos_v2.csv` are the same set, with no
  registry-only and no v2-only name, so this table is complete in both directions. Units are the
  count of rows carrying the name in `secondary_open_codes`:

| Name | Units | Section | Ground | Decisions relied on |
|---|---:|---|---|---|
| `surface_form_tokenization_mismatch` | 12 | §8A | Minimal tokenizer splits corresponding forms; D-060 routes wording mismatches here | D-012 to D-039 series, D-060 |
| `generic_term_lexical_crowding` | 9 | §8, already collected | Broad category vocabulary matched without the decisive entity | D-016, D-055 |
| `cutoff_sensitive_near_miss` | 9 | §13 | An outcome descriptor about metric fragility, not a mechanism; D-042 gives it a numeric threshold and an exception | D-042 |
| `related_name_document_crowding` | 6 | §10 | Passages whose own text carries the queried name or a token of it | D-010, D-048 |
| `peripheral_passage_content_dilution` | 6 | §8A | Same ground as its primary role above | D-023, D-038 |
| `gold_chain_substitutability` | 5 | §12, already collected | Evaluation-side substitution of an annotated passage | D-014, D-038 |
| `generic_query_scaffold_score_inflation` | 5 | §8A | Scaffold tokens scoring under a minimally processed scorer; a member of D-052's enumeration | D-019, D-039, D-052 |
| `generic_person_semantic_neighborhood` | 4 | §10, in prose today | Broad dense person cluster; D-056 keeps its coverage partial | D-009, D-023, D-056 |
| `repeated_function_word_amplification` | 4 | §8A | Unfiltered function words scored per occurrence; a member of D-052's enumeration | D-012, D-034, D-052 |
| `same_topic_passage_distractor` | 4 | §10 | Genuine same-topic passage missing a decisive element; D-055 fixes its boundary at passage level | D-019, D-055 |
| `question_frame_semantic_crowding` | 3 | §10 | Same ground as its primary role above | D-020, D-043, D-054 |
| `cross_entity_token_recombination` | 2 | §8A, cross-referenced from §9 | An order-insensitive matcher rewarding recombined tokens across entities | D-010, D-036, D-057 |
| `unindexed_title_name_anchor` | 2 | §8A | Which field is indexed; D-050 keeps it independent of the preprocessing primary | D-028, D-050 |
| `repeated_content_word_amplification` | 2 | §8A | Content token scored once per occurrence | D-014, D-022 |
| `gold_chain_not_unique` | 2 | §12, already collected | Evaluation-side non-uniqueness of the annotated chain | D-011, D-036, D-060 |
| `cross_passage_conjunction_unresolved` | 2 | §11, already collected | Same ground as its primary role above | D-040 |
| `description_only_bridge_entity` | 10 | §11, already collected | Same ground as its primary role above | D-047, D-053 |
| `low_context_name_query` | 1 | §9, in prose today, gains a collection line | A query property feeding entity competition; section 9 already asks whether it is an independent mechanism | D-009 |
| `technical_topic_crowding` | 1 | §10 | Redundant same-topic technical neighbourhood | D-014 |
| `near_duplicate_event_confusion` | 1 | §10 | A distinct event sharing place, type or name form | D-012 |
| `same_artist_work_crowding` | 1 | §10, already collected | Same-creator works forming a close neighbourhood | D-011 |
| `possible_type_mismatch` | 1 | §12, already collected | D-060 confirms it describes a passage's type, not the question's quality | D-017, D-060 |
| `proper_name_homonym_collision` | 1 | §9, already collected | Distinct entities sharing a name form | D-018, D-033 |
| `answer_property_semantic_crowding` | 1 | §9 | Passages matching a comparison question's answer property from outside the named candidate set | D-018 |
| `exact_string_source_dependency` | 1 | §8, cross-referenced from §10 | Its registry definition rests reachability of the required passage on literal surface overlap, so §8 is the right container, but for the source hop only; D-059 kept it a separate secondary precisely because its primary carries the two-sided semantic behaviour instead, and the §10 cross-reference keeps the pair visible without importing the surface-matching reading into the primary | D-020, D-059 |
| `entity_alias_reference_mismatch` | 1 | §8, cross-referenced from §9 | Two conventional names for one entity, with no alias resolution; a D-060 routing target | D-021, D-060 |

  Distribution by secondary role: §8 takes 3, §8A takes 7, §9 takes 3, §10 takes 7, §11 takes 2,
  §12 takes 3 and §13 takes 1, which sums to 26.
- **Section 8A.** Nine distinct names are routed to it, being the union of its three
  primary-role and seven secondary-role rows: `cross_entity_token_recombination`,
  `entity_name_tokenization_mismatch`, `generic_query_scaffold_score_inflation`,
  `minimal_preprocessing_score_distortion`, `peripheral_passage_content_dilution`,
  `repeated_content_word_amplification`, `repeated_function_word_amplification`,
  `surface_form_tokenization_mismatch` and `unindexed_title_name_anchor`. Sections 8 to 12 were
  written before open coding and all five describe mechanisms of query or corpus content, while
  this family describes mechanisms of the retriever implementation: how text is normalized
  before indexing, which field is indexed, how repeated tokens score, and how mean pooling
  dilutes a passage. It holds the largest primary and the largest secondary in the vocabulary
  and had no section at all. Two alternatives were weighed and refused. Putting the family in
  section 8 is cheapest but requires that section's heading to change too, and filing a Dense
  pooling mechanism under a lexical heading would quietly assert a family resemblance no
  decision has ruled. Routing the whole family to section 13 is defensible on D-003, which holds
  that corpus setting is not a causal category, but it would treat nine names, including a
  9-unit primary with its own primary-use contract from D-051 and D-052, as compound-rule
  material rather than as category candidates, which pre-empts more than it settles. The `8A`
  numbering follows the existing 7A precedent, so sections 9 to 26 are not renumbered. The
  section's verb is deliberately `收集…机制` rather than sections 8 to 13's `建立候选类别`, so
  that the heading itself does not promise a category, and the neutralizing preamble sits under
  the heading rather than only in this entry, because a later agent may enter `taxonomy_todo.md`
  at section 8A without rereading the decision log.
- **The wording constraint this routing carries.** Neither the retrieval mechanism nor the
  primary `verbatim_epithet_sense_drift` may be described as literal matching, exact-string
  matching, phrase matching or surface matching, in this entry or in sections 8 to 13. D-059
  renamed the primary precisely to remove that reading, and it is the same defect class D-019
  repaired on `same_topic_title_distractor`. The ground is factual: the backend is a symmetric
  bi-encoder over L2-normalized whole-passage dot products and performs no string matching at
  all, so attributing string matching to it is false about the implementation. What is not
  forbidden is stating that a query cue is verbatim or literal, or that a passage literally
  contains a given string, which is an observed input or corpus fact; D-059 states both. The
  same four terms also stay legal applied to the secondary `exact_string_source_dependency`,
  whose registry definition does rest on literal surface overlap for the source hop. The
  constraint is therefore about attribution and not about vocabulary: a rejected sentence and a
  legal one can use the same four words and differ only in what they predicate them of. It
  reaches this entry and sections 8 to 13 and no further, and it requires no paraphrase of
  D-059's own factual wording.
- **Evidence, and its extent.** The effective sets are read from `case_memos_v2.csv`: 30 rows
  carrying 12 distinct primaries and 96 secondary assignments over 26 distinct secondaries, of
  which 4 names hold both roles, giving a union of 34. The secondary set is verified equal to
  the 26 registry entries in both directions, with no registry-only and no v2-only name.
  Sections 8 to 13 currently carry 24 collection lines; 12 of them name a name no unit carries,
  and those 12 are exactly Track A. Of the 34 effective names, 22 have no collection line at
  all: 5 appear in those sections only in prose and 17 do not appear at all. Each retirement in
  Track A is tied to the decision that re-coded the carrying unit, and each assignment in Track
  B cites the decisions that fix the name's content. The evidence supports where a name is
  discussed. It measures nothing new, no retrieval measurement was rerun, and this entry adds no
  rank or score figure of its own.
- **A companion figure corrected.** The working intake check written alongside this decision
  reports 18 effective names absent from sections 8 to 13 entirely. The correct figure is 17. A
  snake_case scan of those sections does return 18, but `low_context_name_query` is present in
  section 9 as the prose line `判断 low-context name query 是否是独立机制`, which that scan
  missed. It is a judgement line and not a collection line, so the name is still uncollected and
  still gains a collection line under Track B2; only the claim that it was absent entirely was
  wrong. Every other row of that check stands. The working document is not a tracked artifact
  and is not edited; the corrected figure is stated here.
- **Registry effect:** none. No entry's definition, inclusion rule, exclusion rule or
  affected-units list changes, no entry is created or removed, and the registry stays at 26
  adopted descriptors. A routing of the intake is a statement about `taxonomy_todo.md` and not a
  clause of any registry entry, so it lands in this decision and in the audit, as D-060's
  routing did, and is carried into `candidate_taxonomy_v0_1.md` at the categories stage.
- **Sections 8 to 13 effect.** Twelve collection lines are removed and twenty are added, so
  those sections carry 32 collection lines where they carried 24. By section the counts move 5
  to 3 for section 8, 0 to 9 for the new section 8A, 4 to 5 for section 9, 5 to 9 for section
  10, 6 to 2 for section 11 and 4 to 4 for section 12, section 12's list having already been
  corrected by D-060. Section 13 gains no collection line, because it collects rules rather than
  cases; its two assigned names are recorded there in a routing note instead,
  `compound_two_sided_crowding` against the item that already collects units carrying two or
  more independent mechanisms, and `cutoff_sensitive_near_miss` against the item that already
  separates a causal mechanism from a cutoff outcome. Eight cross-references are added, each
  pointing from one section to a name whose home is another. No section heading is changed and
  no existing judgement line is removed.
- **Open points this routing surfaces without settling.** Section 10's heading reads
  `Near-Neighbor Crowding` while the section now collects three distinct readings of
  neighbourhood, so either the heading widens to the crowding-and-drift family or the framing
  and drift names move. D-055 keeps `generic_term_lexical_crowding` and
  `same_topic_passage_distractor` apart on one passage-level boundary, and this routing puts the
  first in section 8 and the second in section 10, so a single ruled boundary would be discussed
  in two places; the same issue, smaller, applies to D-043's shared crowding contract across
  sections 9 and 10. Section 8's three prose judgement lines may be restated against the
  successor names or dropped. Section 12's heading still reads `Question or Evaluation
  Ambiguity` although D-060 already requires the category to be written on the evaluation side.
  None of these is required before the stage switch; they are recorded so that the categories
  stage does not rediscover them.
- **What this does not settle:** whether any assigned name warrants a category of its own, a
  merge into another, or no category at all. Whether section 8A's members share a mechanism;
  co-location in 8A is an intake arrangement and not a category decision. T-63's boundary
  between `entity_name_tokenization_mismatch` and `surface_form_tokenization_mismatch` stays
  open, and D-058's prospective fold of `entity_name_tokenization_mismatch` into
  `minimal_preprocessing_score_distortion` remains conditional on D-051's two cells existing;
  the §8A placement of that name settles neither. The final taxonomy representation of
  `compound_two_sided_crowding` stays open: §13 records what D-018 already found and asserts
  nothing further. The section-13 items registered by D-021 to D-024 are untouched, as is the
  evidence-threshold item D-023 registered for `peripheral_passage_content_dilution`. The four
  heading and boundary questions listed as open points above are recorded, not ruled. It rules
  nothing about `case_memos_v1.csv`, the closed validation queue, or any measurement, and it
  re-judges no landed entry.
- **Affected units:** none reclassified; no memo row, queue row or label changes.
- **References:** `manual_review_v1/analysis/taxonomy_todo.md` sections 8 to 13,
  `manual_review_v1/analysis/case_memos_v2.csv`,
  `manual_review_v1/analysis/secondary_descriptor_registry.md`,
  `manual_review_v1/analysis/open_code_vocabulary_audit.md` section 8.7, and
  `manual_review_v1/analysis/open_code_decision_log.md` D-003, D-010, D-018, D-020, D-023,
  D-043, D-049 to D-053, and D-057 to D-060.

## D-062 - Require scoped category-by-retriever capability boundaries and bounded synthesis

- **Date:** 2026-08-12
- **Status:** active
- **Decision:** The candidate taxonomy, frozen taxonomy and final qualitative analysis must
  answer the project-specific capability question for every category. Each category carries
  eight fields: `failure_layer`, `retriever_scope`, `BM25_capability_boundary`,
  `Dense_capability_boundary`, `supporting_units`, `decisive_counterfactual`,
  `claim_strength` and `non_claims`. The final analysis carries one category-by-retriever
  matrix over the same fields. Category work now proceeds as bounded synthesis from the
  existing 30-unit evidence; no new general tool or unbounded vocabulary audit is allowed
  unless one named category boundary is demonstrably blocked by missing evidence.
- **Rationale:** The notes-first evidence chain is complete enough to form categories, but the
  prior output contract could be satisfied without stating whether a recurring failure is
  implementation-induced, method-level under the evaluated setup, corpus-induced or
  evaluation-induced. That would omit an explicit owner goal. At the same time, the canonical
  course protocol says review infrastructure may not outgrow the research question. The
  correction therefore strengthens the research deliverable while reducing further process
  work; it does not reopen the case evidence.
- **Capability-boundary contract:** `failure_layer` is exactly one of `implementation`,
  `method`, `corpus` and `evaluation`. `retriever_scope` is observational scope in this bounded
  sample, not a cause. Each method boundary is one of `implementation_recoverable`,
  `setup_scoped_method_boundary`, `not_established` and `not_applicable`, with a supporting
  sentence. A missing decisive counterfactual is recorded as `not_run` and caps
  `claim_strength` at `observed`.
- **Allowed claim strength:** `observed` states only the evaluated run's behavior;
  `implementation_supported` requires a tested implementation control;
  `setup_scoped_method_supported` requires relevant implementation alternatives to be ruled
  out and names the evaluated method or architecture and retrieval setup. Unqualified claims
  such as `BM25 cannot ...` or `Dense cannot ...` are forbidden. Comparison-retriever success
  alone cannot strengthen a claim. A successful preprocessing or indexing repair keeps the
  conclusion at implementation level, regardless of how many units share the symptom.
- **Artifact-separation effect:** `case_memos_v2.csv.primary_open_code` and
  `secondary_open_codes` remain provisional open-code evidence. Its legacy
  `candidate_category` cells are provisional routing hints only: 29 mirror the then-current
  primary and one is blank. They are not counted, copied into candidate mappings or treated as
  evidence that a taxonomy exists. The 30 `analytic_status` cells are synchronized to
  `jointly_reviewed_validated_revised`; the 30 `review_status` cells remain
  `jointly_reviewed`. A candidate mapping begins only in `candidate_mapping_v0_N.csv`, with
  empty categories and `mapping_status=not_tested`.
- **Regression cases and legal controls:** A category missing one of the eight fields is
  rejected, while a complete category with `decisive_counterfactual=not_run` is legal when its
  claim stays `observed`. An unconditional method-incapability sentence is rejected, while a
  claim scoped to the evaluated bag-of-words BM25 or independent symmetric bi-encoder setup is
  legal when the cited controls support it. A preprocessing-recovered case is rejected as a
  method boundary and accepted as `implementation_recoverable`. A candidate mapping prefilled
  from the legacy routing column is rejected; an empty, `not_tested` mapping is the legal
  control. A general tool or sweep without a named blocking boundary is rejected; reuse of the
  existing evidence, or a narrowly stated minimum-evidence request for one blocked boundary,
  is legal.
- **Evidence, and its extent:** The project contains 30 unique jointly reviewed units, 15 BM25
  and 15 Dense, from one pooled run, one minimal BM25 implementation and one symmetric MiniLM
  bi-encoder without reranking or cross-passage reasoning. This supports bounded and
  setup-scoped conclusions, not universal claims over all BM25 or Dense retrievers. No new
  retrieval measurement is run for this decision.
- **Files and workflow effect:** The current-output and freeze contracts in
  `taxonomy_todo.md`, the operational taxonomy contract in
  `failure_annotation_guideline.md`, the `case_memos_v2.csv` field semantics and status cells,
  and the analysis README are aligned. The project stays in `categories`; after this corrective
  pass receives a fresh independent review, the next action is direct category synthesis from
  sections 8 to 13, not another general audit.
- **What this does not settle:** No candidate category is created, merged, split, renamed or
  removed. No unit is reclassified, no primary or secondary open code moves, and no prior
  decision or dossier conclusion is re-judged. The actual capability boundary of each future
  category remains to be synthesized from its supporting units under this contract.
- **Affected units:** none reclassified. All 30 memo rows receive the same metadata-only
  `analytic_status` synchronization; raw notes, analytic evidence, open codes, routing hints,
  tie-breaks and review conclusions are unchanged.
- **References:** project-goal alignment round 1 review in
  `docs/Local/Reviews/2026-08-12_project_goal_alignment_round1_independent_review.md`,
  findings F-01 to F-04; `references/2026-07-27-manual-failure-review-course-protocol.md`
  sections 1, 2 and 10; `references/reusable_retrieval_failure_review_playbook.md` section 2.4;
  `references/2026-07-31_notes_first_grounded_taxonomy_workflow.md` sections 3 and 4; and
  `references/failure_annotation_guideline.md` section 8.

## D-063 - Land the sections 8 to 13 bounded synthesis as six candidate categories

- **Date:** 2026-08-12
- **Status:** active
- **Decision:** The bounded synthesis of sections 8 to 13 is landed. Sections 8 to 12 yield
  **six** candidate categories, not five: `bm25_minimal_preprocessing_score_distortion` (K1),
  `description_only_bridge_entity` (K2), `cross_passage_conjunction_unresolved` (K3),
  `near_neighbour_crowding_and_sense_drift` (K4), `dense_peripheral_passage_content_dilution`
  (K5) and `evaluation_side_gold_chain_ambiguity` (K6). Section 8 is **dissolved** and writes no
  category, section 8A yields K1 and routes one name to K5, section 9 **folds** into K4, section
  10 yields K4 under a **corrected title**, section 11 **splits** into K2 and K3, and section 12
  yields K6. Each category carries D-062's eight capability fields plus the nine-component
  judgement contract that sections 8 to 12 require. Section 13 is landed as a seven-step ordered
  candidate primary-selection rule with an evidence-typing preamble, a three-route discharge
  procedure for D-043's second clause, a tie-break order, a `taxonomy_defect_flag` rule, a
  secondary-descriptor rule, the one-final-label rule, two `unresolved` assignments, the four
  rulings the section registered as open, and the compound-case rule this entry appends. Every
  category name here is a **candidate** name. No candidate taxonomy file, candidate mapping,
  frozen taxonomy, final label or category count is created, no unit is reclassified, no open
  code moves, and no measurement is run.
- **Rationale:** D-062 required category work to proceed as bounded synthesis from the existing
  30-unit evidence and to answer the capability question per category. The synthesis was written
  and rewritten against five independent acceptance reviews, whose round 5 verdict is PASS with
  no confirmed finding. What remained after that verdict was not a judgement but a landing: the
  decision log is the authority for a ruling, and until a ruling is appended it is a proposal.
  This entry appends the rulings and their contracts so that section 14 can be entered against
  landed text rather than against an untracked working document. It is one entry rather than
  seven because the six category contracts, the selection order and the section 13 rules are one
  interlocking output: the order decides which contract applies, and the contracts cite the
  order's steps as their own inclusion rules.
- **Track A, the six section outcomes.** Each row states the outcome and the ground that forces
  it. Section 8A is an intake workstream under D-061 and is listed with the five category
  sections because it is where K1's two primary names sit:

| § | Outcome | Ground |
|---|---|---|
| 8 Lexical Cue Capture | **dissolved**, no category | Its three names are zero-primary across all 30 units. Six of the nine `generic_term_lexical_crowding` units are K1 primaries; the rest fall in K3 and K6, and the one Dense name falls in K4. The three names survive as secondary descriptors. `literal_cue_topic_capture` is the nearest thing to a carrier and D-014 demoted it as an output-level description, which D-059 refused to revive |
| 8A Retriever Implementation Artifacts | **K1**, plus one name routed to **K5** | Eight BM25 names describe one lexical pipeline and carry both of K1's primary names; `peripheral_passage_content_dilution` describes mean-pooled whole-passage encoding and is not the same mechanism. The section splits by mechanism and is not merged |
| 9 Entity Competition or Ambiguity | **folds into K4** | Its names reach four units, three of which also sit in section 10's intake, and no control series separates entity competition from near-neighbour crowding on any of them. Its five names are carried into K4 as members and secondaries |
| 10 Near-Neighbour Crowding | **K4**, title corrected to `near_neighbour_crowding_and_sense_drift` | D-061 registered without ruling that the title no longer covers what the section collects. Three readings of neighbourhood are present - near-duplicate documents and entity variants, a question's framing facet, and the sense neighbourhood of one cue - and they are kept as **sub-readings inside one category** because the group is the project's weakest-controlled one and a three-way split would manufacture structure the evidence does not carry |
| 11 Bridge or Relation Failure | **splits into K2 and K3** | The two live bridge names carry ten units between them, four and six, and the conditioned oracle-name outcome coincides with the split on every landed application: passed on all four `description_only_bridge_entity` units, failed on five of six `cross_passage_conjunction_unresolved` units with the sixth `not_applicable` under D-044 |
| 12 Question or Evaluation Ambiguity | **K6**, written from the evaluation side | D-060 forbids any question-quality descriptor. The category names a property of the annotation and the metric - the annotated chain is not the only chain satisfying the question inside the evaluated cutoff - and never a defect in the question |

  Why the Dense name in section 8A is K5 and not K1, since D-062 says a successful preprocessing
  or indexing repair keeps the conclusion at implementation level: the four-condition gate's
  controlled ablation removes content from a required passage, which no pipeline can do, so it
  is a diagnostic and not a deployable change, and mean pooling over the whole passage is a
  property of the evaluated encoder's architecture rather than a preprocessing choice made
  before it. D-062's implementation clause is therefore not triggered and K5 is `method`-layer.
  This is stated because it is the one place a reader could think the clause was being avoided.
- **Track B, the six candidate categories and their capability boundaries.** The full
  nine-component contract for each - definition, required observable evidence, inclusion rules,
  exclusion rules, closest competing category, tie-break rule, two or more positive examples,
  one or more counterexamples and known limitations - plus each category's `supporting_units` as
  full unit keys, is carried in section 10 of the landed synthesis named under references. The
  eight D-062 fields are:

| Category | Layer | Scope | BM25 boundary | Dense boundary | Primary-label units | Counterfactual | Strength |
|---|---|---|---|---|---:|---|---|
| K1 `bm25_minimal_preprocessing_score_distortion` | `implementation` | BM25 | `implementation_recoverable` | `not_applicable` | 10 | run: non-oracle double recovery on two units (D-028, D-030) | `implementation_supported` |
| K2 `description_only_bridge_entity` | `method` | Dense, observational | `not_established` | `not_established` | 4 | run and valid on four of four, as optional support and not as a membership condition | `observed` |
| K3 `cross_passage_conjunction_unresolved` | `method` | cross-retriever | `not_established` | `not_established` | 6 | run: failed on five of five interpretable applications, one `not_applicable`; 134 non-oracle conditions excluded on one BM25 unit (D-039) | `observed` |
| K4 `near_neighbour_crowding_and_sense_drift` | `method` | cross-retriever | `not_established` | `not_established` | 5 | `not_run` for the category, run per unit on all five | `observed` |
| K5 `dense_peripheral_passage_content_dilution` | `method` | Dense | `not_applicable` | `setup_scoped_method_boundary` | 1, with 7 supporting | run: the four-condition gate, and the two-sided ablation ceiling reached on one unit (D-037) | `setup_scoped_method_supported` |
| K6 `evaluation_side_gold_chain_ambiguity` | `evaluation` | cross-retriever | `not_applicable` | `not_applicable` | 2 | partially run | `observed` |

  Two boundary disciplines are landed with the table. First, `not_applicable` asserts that the
  category's mechanism cannot arise on that backend and is legal on exactly two grounds and no
  other: a backend property makes the mechanism impossible, which is K1's Dense cell on D-029's
  accent-and-case-stripping bi-encoder and K5's BM25 cell on the descriptor's own exclusion; or
  the category is not method-layer and makes no capability claim at all, which is K6's two
  cells. **The absence of a primary use on a backend is never a ground**: `retriever_scope` is
  observational under D-062, a descriptor whose definition states a property of the question and
  the required passage is measurable on both backends under D-047, and the correct value there
  is `not_established`, which records missing evidence. Second, K4 records
  `decisive_counterfactual=not_run` at category level and therefore stays at `observed` despite
  unit-level diagnostics, and K3 is held at `not_established` on both backends rather than split
  by retriever to harvest the stronger claim its BM25 units alone would support, because that
  would be structure driven by claim convenience.
- **Track C, the candidate primary-selection order.** Applied in order; the first step whose
  include rules hold and whose exclude rules do not fire assigns the candidate primary. Step 1
  K6, evaluation-side answer ambiguity, restricted to the answer side and refusing an
  intermediate-passage substitution. Step 2 K1, an evaluated lexical implementation artifact.
  Step 3 K5, mean-pooling content dilution, which requires the gate **and** the two-sided
  ablation ceiling. Step 4 K2, description-only bridge entity. Step 5 K3, unresolved
  cross-passage conjunction. Step 6 K4, near-neighbour crowding and sense drift, with positive
  include rules in two shapes and **not** an `otherwise`. Step 7 `unresolved`, which is a real
  destination reached either because no step fires or because two categories' include rules are
  satisfied at the same evidence tier and the tie-break does not separate them.

  Four things are landed with the order. **One,** an evidence-typing preamble: only a deployable
  measurement (E1), an oracle measurement (E2), a gold-targeted diagnostic (E2b) or a verified
  content rule (E3) may satisfy a predicate, and rank shape or position, distance from the
  cutoff, corpus setting, retriever identity and the mere presence of a name in
  `secondary_open_codes` are never predicates. **Two,** the tie-break order, which applies only
  where two categories' include rules are both satisfied on one unit at the same evidence tier:
  prefer the category whose decisive counterfactual was actually run on that unit; then the
  deployable result over the oracle result under pit 15, a gold-knowledge-requiring condition
  being unable to refuse a category at all under D-040; then the lower-numbered step; then
  `unresolved`. Where only one category's include rules are satisfied **no tie-break runs**, and
  clause 1 in particular may not be used to refuse that category for want of a run
  counterfactual. **Three,** `taxonomy_defect_flag=true` marks a unit whose evidence satisfies a
  category's include and exclude conditions simultaneously; a unit reaching `unresolved` does
  **not** get the flag, because `unresolved` records absent evidence and the flag records
  contradictory evidence. All 30 rows currently read `false` after D-057, D-058 and D-059, and
  the flag stays available. **Four,** a secondary descriptor is allowed whenever its own
  registry include conditions hold, independently of the primary, and there is exactly **one**
  final label per unit; every other mechanism on that unit is a secondary descriptor.

  **The three-route discharge procedure for D-043's second clause**, which is a mandatory
  include predicate for any crowding-family primary, is landed as part of step 6 and is searched
  in this order. **Ruled, by a later decision:** a decision later than D-043 states, for that
  unit, that the clause holds; that ruling is the answer and a synthesis may not re-derive it.
  D-054 is the instance. Where this route fires the other two are not consulted. **Discharged,
  from landed text:** no later decision rules the clause, but landed decision text supplies a
  rule stated purely over passage content - no rank, no position, no gold status in the rule
  itself - together with corpus-scoped facts showing that the rule selects no required passage.
  The rule need not be the one the entry's prose chose and it may over-select non-gold passages,
  which is the strength D-043 itself accepted when it repaired D-027's family rule. **Not
  discharged:** no later decision rules the clause, the stated family rule's own content
  predicate is carried by a required passage, and no position-free content rule with
  corpus-scoped selection facts is recorded; the unit then reaches step 7 and the missing fact
  check is named rather than assumed in either direction. Entering K4 with the clause neither
  ruled, discharged nor routed is forbidden. The sense-drift shape is outside this rule, because
  D-043 governs crowding-family descriptors and `verbatim_epithet_sense_drift` is not one.
- **Track D, the rerun result and the two `unresolved` assignments.** Reapplying the order to
  all 30 full unit keys gives K1 10, K2 4, K3 6, K4 5, K5 1, K6 2 and `unresolved` 2, which sums
  to 30, is disjoint and exhaustive, and splits 15 BM25 and 15 Dense against
  `case_memos_v2.csv`. It agrees with 28 of the 30 landed `primary_open_code` groupings once the
  section folds are applied. The two exceptions are the `unresolved` assignments, and they fail
  on **different** predicates, which is why each is recorded per unit rather than pooled:

| Unit | Landed `primary_open_code` | Why no category's include rules are reached |
|---|---|---|
| `5a76387d554299109176e6ba\|dense` | `two_named_entities_underprioritized` | Step 6's fourth exclusion fires. A family is stated as passage content, generic person and birth-related material, but **no intervention of any kind was measured** on the unit, and D-009 states that the ranking does not establish which internal embedding or scoring component caused the ordering. The unit carries no ordinal-series membership at all |
| `5a7d19d85542995ed0d165e8\|dense` | `same_entity_variant_crowding` | D-043's second clause fails and is not discharged: the family rule D-015 states also selects one of the required passages, so the family cannot be removed even in principle and the claim is untestable by any intervention. No decision later than D-043 rules the clause on this unit, so the first discharge route does not fire either, and no controlled ablation was run |

  An `unresolved` output is a completeness property of the rule set, not a gap in it: a rule set
  that had to guess in order to avoid `unresolved` would be the incomplete one. Neither unit's
  `primary_open_code` is changed by this entry; what is recorded is a candidate-category
  assignment, and no candidate mapping exists yet.
- **Track E, the four rulings section 13 registered as open, now made.** Each is made from
  landed decision text, `case_memos_v2.csv` and `recount.py`'s membership tables only, with no
  new measurement.

  **Ruling 1, the D-022 and D-024 item on `cross_passage_conjunction_unresolved` as a primary.**
  One name, two usages, with an explicit primary-use threshold. Six primary uses and two
  secondary uses are counted from `case_memos_v2.csv`, and on both secondary uses an earlier
  step of the order fires while the structure is present but not decisive, so the two usages are
  one mechanism that is decisive six times and non-decisive twice rather than two mechanisms.
  Splitting would mint a second name whose only content is "the same structure, not decisive",
  which the evidence-typing rule already forbids reading as a mechanism, and the precedent is
  consistent across D-052, D-053 and D-054. On the threshold: **per-hop reachability is
  supporting evidence, not a necessary gate.** A probe whose query is a required passage's own
  name injects that passage's own entity name and is therefore E2, so making it necessary for a
  primary that otherwise rests on E1 evidence would let an oracle condition's absence veto a
  category deployable measurements establish; the landed record additionally types those probes
  two ways, D-022 listing its K probes among the non-oracle factors while D-024 records its K
  and N series as oracle diagnostics, and a mandatory threshold cannot rest on a probe class the
  record reads two ways. Measured **un**reachability remains an exclusion, which is the same
  bar-versus-support asymmetry D-041 and D-046 already use. The conditional half is settled with
  a measured figure rather than an assertion: read at the same normalization level as the rest
  of that unit's design, D-024's one-sided appearance is the tokenizer artifact D-044 rules on
  and the answer hop is inside the evaluated cutoff, so `5ae057fd55429945ae959328|bm25`
  qualifies even under the stricter reading this ruling rejects, and **no assignment turns on
  the ruling's direction**. Where the contract text finally lives is triage item T-10 and stays
  open.

  **Ruling 2, the D-021 and D-023 item on the single-factor oracle-name criterion's status.** A
  **binding exclusion** in the failing direction, and in the passing direction **optional,
  non-sufficient supporting evidence that is never an inclusion condition**. It is never
  sufficient, never necessary, never designates a winner, and needs no restatement beyond what
  D-041, D-044 to D-046 and D-047 have landed. **Multi-form consistency is not required**, D-046
  having already made the passing half existential and the failing half coverage-bound, and none
  of the four passing primary uses is a mixed result so a universal reading would flip none of
  them. Three oracle states are typed separately and only one of them binds. A **valid pass** -
  at least one form inside D-046's form set, both preconditions verified and holding for that
  form, every required passage inside the evaluated cutoff - is optional support: it raises a
  member's evidence tier and can supply the supporting leg of a tie at equal tier, and it
  decides no membership by its absence. A **valid failure** - every form run fails, both
  preconditions verified and holding for every form counted, and at least one form of each
  required passage's own name run - is the only binding oracle reading, and it bars the primary.
  **`not_run` and `not_applicable`** is a third state, neither pass nor failure: **nothing
  follows from it in either direction**, no bar is recorded, no include clause fails, and a unit
  satisfying the content property with no competing E1 evidence is a member at the `enumerated`
  tier. Reading a missing optional support as a second exclusion, an implicit exclusion or a
  failed include clause is forbidden, and the ground is D-041's own text: its decision sentence
  writes the passing half as non-binding, an inclusion note that supports without establishing,
  and its evidence paragraph closes that four of eight is why the positive half is written as
  support rather than as an inclusion condition. That the four landed primary uses all happen to
  pass is provenance about a four-unit sample and may not be converted into a condition, which
  is what D-041 itself declined to do with the same four units in front of it. The D-022 gap the
  item asked about - what the criterion does when no competitor carries non-oracle
  result-decisive evidence - is answered directly: **it bars and stops there**, never
  designating the winner, and if no step's positive include rules are satisfied the unit is
  `unresolved`. The item's two sub-questions were already closed elsewhere and are named so this
  ruling is not read as reopening them: the definition's lexical-retrieval wording by D-047, and
  the injected-anchor precondition by D-044 with D-045 adding the per-form degeneracy condition.

  **Ruling 3, the D-023 item on the dilution gate's threshold, placement and third intervention
  class.** Three parts. **Placement is kept unchanged:** the four conditions stay the
  descriptor's own include gate, evaluated per required passage, and primary use additionally
  requires the two-sided ablation ceiling that is step 3's outcome clause. The landed split of
  nine applications, seven passes and two rejections with exactly one primary win shows the
  placement doing include-level work rather than primary-selection work, and folding the outcome
  clause into the gate would retroactively reject six landed passes, which red line 4 forbids.
  **Generalisation is yes as a floor and no as a licence:** the four conditions generalise to
  every Dense claim that attributes a required passage's score deficit to that passage's own
  content, no such claim may be adopted without all four, and where no equal-length control
  exists the gate must not be applied at all; they do not generalise into a sufficient condition
  for any primary. Read as a floor the rule reproduces the whole landed record, D-013 and D-015
  having recorded every earlier dilution-shaped claim as speculation and D-035 having added that
  the control must be decontaminated word by word. **The third intervention class gets formal
  standing as `E2b`:** an intervention that adds no text and injects no answer information but
  requires knowing which passage is gold or which passages are rivals - the controlled content
  ablation with its equal-length control, and index-side family-removal probes. Its standing is
  admissible as evidence for a mechanism, **never** a deployable repair so it can never trigger
  D-062's implementation clause or produce `implementation_recoverable`, outranked by any E1
  result under pit 15, and unable to refuse a category under D-040, only to limit confidence. K5
  therefore keeps `setup_scoped_method_supported` because its implementation alternatives were
  measured and refused, **not** because its ablation is deployable, and its `non_claims` says
  so. Where the gate's contract text finally lives across the registry and the candidate
  taxonomy is triage item T-40 and stays open.

  **Ruling 4, the D-024 item on the two corpus-setting paths.** Record the two paths separately,
  as **mapping-level provenance modifiers with distinct values, never as a category, a layer or
  a cause**, and add one precision rule rather than re-wording D-003. The two paths are
  measurably different objects and the landed evidence separates them on the three units where
  the disagreement was decomposed: on two of them dropping the pooling-introduced rivals
  restores the cutoff exactly, so the candidate set changed; on the third, dropping the only two
  pooling-introduced passages above the bridge hop does not restore it and the driver is the
  ten-document index's own scale, its inverse document frequencies and average document length,
  so the scoring function changed. The modifier field carries `pooling_added_competitors`,
  `collection_statistics_shift`, `both` and `not_decomposed`, the last being the honest default
  since only three of the sixteen applications were decomposed to that granularity. **D-003 is
  not re-worded**, the log being append-only; the precision the second path needs is added as a
  rule for the candidate taxonomy instead - corpus setting stays provenance under **both**
  paths, and the second path may not be re-described as an implementation property of the
  scorer, because `k1`, `b`, `epsilon` and the analyzer are identical between the two settings
  and only the collection over which the statistics are computed differs.
- **Track F, the compound-case rule, appended here as section 13's last item requires.** Five
  clauses. **One,** a compound primary is legal only when each constituent mechanism
  independently satisfies its own include conditions and no step of the candidate
  primary-selection order separates them. **Two,** where a constituent is a crowding-family
  descriptor, D-043's two clauses apply to that constituent on its own. **Three,** a compound
  primary creates no category: it is recorded as a unit-level property of the candidate mapping,
  one compound flag plus the constituent list, and never as a fifth `failure_layer` value, which
  D-062 fixes at four, and never as a second final label, which the one-final-label rule
  forbids. **Four,** a compound primary is not a route around `unresolved`: if the constituents
  do not each satisfy their own include conditions, the unit is `unresolved`. **Five,** compound
  status is recorded on the unit, not on the category, so a category's `supporting_units` and
  claim strength are unaffected by a member's compound status.

  Rationale for the rule: D-018 found two crowding mechanisms on one unit, each with independent
  evidence and neither explaining both required passages, and never ruled that the compound name
  denotes a unified category; D-061 recorded that question as open and placed the name in
  section 13 rather than section 10 precisely to avoid importing that claim. Clauses one, two
  and four keep the compound from becoming a way to assign a category on evidence that fails the
  category's own gate; clauses three and five keep it from silently adding a layer value or a
  second label. Evidence and its extent: exactly one unit, `5a8d93ad554299653c1aa13d|dense`
  (D-018), where two content-defined families occupy disjoint rank positions and conditions A to
  E are measured, one of them moving a required passage inside the cutoff and another falsifying
  `low_context_name_query`. One unit is the whole basis; the rule forbids nothing landed,
  registers no new name and reclassifies nothing. `compound_two_sided_crowding` is retained
  **inside K4 as a compound member**, not promoted to its own category. What the rule does not
  settle: whether a compound whose constituents belong to two different candidate categories is
  legal, there being no in-sample instance; whether `compound_two_sided_crowding` survives the
  taxonomy naming pass; and the weakness D-018 itself records, that its interventions are
  query-side rewrites it calls oracle diagnostics rather than family removals.
- **Evidence, and its extent:** 30 unique jointly reviewed analytical units, 15 BM25 and 15
  Dense, 24 bridge and 6 comparison questions, from one pooled run over the 4,937-passage pooled
  corpus, one deliberately minimal bag-of-words BM25 implementation with titles excluded from
  the index, and one symmetric `all-MiniLM-L6-v2` bi-encoder with mean pooling, L2
  normalization, a 256-token window and no reranking or cross-passage reasoning. 19 of the 30
  units carry a `per_case_analysis/` dossier and 11 do not; the eleven without one carry no
  factorial, item T-56 records that gap, and every predicate satisfied by an enumerated match
  set rather than by a measured rank effect falls on that batch. The counterfactual weight is
  carried by four control series whose membership `recount.py` declares: the single-factor
  oracle-name test, 18 applications, 8 passed and 10 failed; the title-indexing condition, 21
  applications, 5 materially positive, 2 one-sided positive and 14 inert or negative; the
  dilution gate, 9 applications, 7 passed and 2 rejected; and corpus setting, 16 applications.
  The corpus-setting series stays provenance under D-003 and is used as a cause nowhere. This
  supports bounded, setup-scoped and mostly `observed` conclusions and supports no universal
  claim about BM25 or about dense retrieval. **No retrieval measurement, title-indexing rerun,
  corpus sweep, ranking or score computation was performed for this entry**, and the 30-row
  rerun was a one-off join over `case_memos_v2.csv` and `recount.py`'s membership tables, adding
  nothing to `tools/`.
- **Registry effect:** none. No `secondary_descriptor_registry.md` entry is created, renamed,
  merged, split or given a new definition, include rule or exclude rule. Every name this entry
  discusses keeps the contract it already had; the six category names are candidate names at a
  different layer and are not registry names. Nothing is added to
  `open_code_vocabulary_audit.md`, because no name enters or leaves either inventory and the
  primary and secondary counts are unchanged.
- **Files and workflow effect:** the decision log gains this entry; the intake and judgement
  checkboxes of sections 8 to 13 of `taxonomy_todo.md` are ticked, with a per-section note
  recording what discharges each group, and that file's next-decision, stage and handoff
  statements are brought current; `recount.py` registers this entry as `not_applicable` in every
  ordinal series whose marker its text matches, because a rule entry that quotes another
  decision's measurement is not a new application of that series. `case_memos_v2.csv`, the
  registry, the audit, the triage table, the queue, every dossier, the guideline, the analysis
  README and the session prompts are **not** edited. `$STAGE` stays `categories`: this entry
  completes section D steps 5 and 6 and does not authorize section 14, which needs its own owner
  authorization after a fresh independent review of this landing.
- **What this does not settle:** No `candidate_taxonomy_v0_1.md`, `candidate_mapping_v0_N.csv`,
  frozen taxonomy, `final_labels.csv` or category count is created, and no candidate mapping is
  prefilled from `case_memos_v2.csv`'s legacy `candidate_category` column, which holds 29
  mirrors of the then-current primary and one blank. **No triage item is closed by this entry**:
  the ruled, no-D-entry and open counts of `vocabulary_audit_triage.md` are unchanged, and the
  items each category carries are named in its own limitations rather than resolved. Named as
  still open: T-10, where the conjunction primary's contract text lives; T-40, where the
  dilution gate's contract text lives across the registry and the candidate taxonomy; T-51,
  whether a substitute outside the cutoff counts at all; T-08 and T-09, the two boundaries
  around the description-only primary; T-56, the eleven-unit no-dossier batch; T-62 and T-63,
  the two unwritten descriptor boundaries. K1 deliberately carries **two** primary names because
  D-058 leaves the fold of `entity_name_tokenization_mismatch` into
  `minimal_preprocessing_score_distortion` conditional on D-051's two unmeasured cells, and K1's
  category name must not be read as having performed that merge. K4's three sub-readings are
  **not** ruled to be one mechanism; the split is re-opened at the freeze gate if mapping
  produces separating evidence. No prior decision, dossier conclusion, measurement, tie-break or
  confidence is re-judged, and D-003, D-018, D-041, D-043 and D-054 in particular are applied as
  landed rather than re-worded. Whether the six candidate names survive the naming pass, and
  whether any category's boundary can be raised off `not_established`, are section 14 to section
  20 questions; the two minimum-evidence requests the synthesis names under K2 and K5 are
  recorded there and **neither is run here**.
- **Affected units:** none reclassified. No `primary_open_code`, `secondary_open_codes`,
  `candidate_category`, `review_status`, `analytic_status`, `taxonomy_defect_flag` or narrative
  cell of `case_memos_v2.csv` changes, and no raw note, analytic memo or dossier conclusion
  changes. The two units routed to `unresolved` keep their landed open codes; the assignment is
  a candidate-category proposal recorded in this entry, not a relabelling.
- **References:** the landed synthesis
  `docs/Local/Synthesis/2026-08-12_sections_8_13_bounded_category_synthesis.md`, sections 1 to
  16; its five independent acceptance reviews
  `docs/Local/Reviews/2026-08-12_sections_8_13_bounded_synthesis_round1_independent_review.md`
  through `..._round5_independent_review.md`, whose round 5 verdict is PASS with no confirmed
  finding; D-062 for the capability-boundary contract and the bounded-synthesis mandate; D-061
  for the intake routing this synthesis consumes; D-041 and D-044 to D-047 for the oracle-name
  contract; D-043 and D-054 for the crowding-family contract and its one later ruling; D-040 and
  D-049 to D-060 for the rules the category contracts carry;
  `references/2026-07-27-manual-failure-review-course-protocol.md` sections 1, 2 and 10;
  `references/failure_annotation_guideline.md` section 8; and
  `references/reusable_retrieval_failure_review_playbook.md` section 2.4.

## D-064 - Correct D-063's minimum-evidence attribution, prospectively

- **Date:** 2026-08-12
- **Status:** active
- **Decision:** D-063's sentence "the two minimum-evidence requests the synthesis names under
  K2 and K5" is corrected **prospectively**. The corrected statement, which every later
  document must match, is this. **K2 carries two named evidence gaps.** Exactly **one** of them
  is an actionable minimum-evidence request: the title-indexing condition T on
  `5a85cead5542991dd0999ea9|dense`, which is what would raise K2's Dense boundary off
  `not_established`. The second is the **absence** of any BM25 unit in the current 30 on which
  `description_only_bridge_entity` is the decisive primary; it is a larger evidence gap that no
  measurement on an existing unit can close, and **no measurement request is made for it**.
  **K4 and K5 carry no named minimum-evidence gap.** A restatement of this must agree in three
  respects at once: the count of named gaps, the category each one sits under, and which of them
  is a request rather than only a gap.
- **Affected decision:** D-063, at its `What this does not settle` bullet. D-063 is **not
  rewritten**: red line 4 makes this log append-only, and that sentence stays on disk as landed
  historical text. This entry is the vehicle the log's own header prescribes, a later entry that
  identifies the affected decision, and from here on it is the authority wherever the two
  disagree.
- **Rationale:** The round 1 independent review of `candidate_taxonomy_v0_1.md` confirmed this
  conflict as its finding F-02. Read as sets, D-063 says `{K2, K5}` while the landed synthesis
  and the candidate both say `{K2, K2}`. The synthesis is the source D-063 lands, and it is
  unambiguous: its section 10 carries exactly one `Named minimum evidence gap` paragraph, in the
  K2 block, and that one paragraph holds both items; the K4 block states in terms that no gap is
  named for it; and the K5 block names none at all. The substantive content was therefore never
  in doubt and only D-063's attribution sentence was wrong. Two further grounds fix the vehicle.
  The candidate declares a landed D-entry to outrank itself, so it cannot resolve a conflict in
  which it is the losing party. And a `draft` file is not an authority: a correction written
  only there would leave the winning source still saying something else.
- **Why no gap can sit under K5 or under K4:** K5's BM25 boundary is `not_applicable` and its
  Dense boundary is already `setup_scoped_method_boundary`, so no K5 boundary is blocked by a
  missing measurement and a minimum-evidence request would have nothing to raise. K4's only
  candidate request is the one recorded as withdrawn under finding F-10 in the synthesis's
  section 15, because it asked for evidence establishing a point D-054 had already ruled, and
  nothing replaced it. What would move K4's two boundaries off `not_established` is larger than
  one measurement - implementation alternatives excluded across the category rather than per
  unit - and D-062 permits a narrowly stated request only for one named blocked boundary, which
  that is not.
- **Regression cases and legal controls:** A restatement that places a named minimum-evidence
  gap under K4 or under K5 is rejected; the legal control is the corrected K2-only placement. A
  restatement that calls the BM25 item a measurement request is rejected; the legal control
  names it as a gap and says in the same breath that no request is made for it, because the unit
  it would need does not exist in the 30. A restatement that collapses the two K2 items into
  one, or that raises the count to three by counting a blocked boundary as a further gap, is
  rejected; the legal control is exactly two named gaps under K2, of which exactly one is a
  request. A restatement that reads this entry as raising a boundary, as closing T-08 or T-09,
  or as running the named condition is rejected; the legal control records that request as
  unrun.
- **Evidence, and its extent:** No retrieval measurement, ranking, score computation, corpus
  sweep or ablation is run for this entry, and none is authorized by it. The title-indexing
  condition T on `5a85cead5542991dd0999ea9|dense` stays **unrun**: that unit ran one form only,
  and this entry names the request without making it. The landed class counts of the four
  control series are unchanged, and `tools/recount.py`'s membership tables stay authoritative
  for every series count.
- **Files and workflow effect:** `candidate_taxonomy_v0_1.md` is aligned to this entry wherever
  it states the named gaps, and its mechanical verification record gains the cross-document
  check the review requires. `taxonomy_todo.md` receives only the mechanical
  next-unused-decision-ID synchronization this append forces, to D-065. `tools/recount.py`
  registers this entry as `not_applicable` in the title-indexing series, on the same ground as
  D-050, D-052, D-059 and D-063: the entry names the condition and measures it on no unit, so a
  membership row would claim a measurement it did not make.
- **What this does not settle:** Section 14 is **not** authorized to land by this entry, no
  `taxonomy_todo.md` checkbox is ticked, `$STAGE` stays `categories`, and the candidate stays
  `draft` pending a fresh independent review. No candidate mapping, frozen taxonomy,
  `final_labels.csv` or category count is created. No category boundary is raised or lowered, no
  `claim_strength` changes, and no unit is reclassified. **No triage item is closed**: T-08 and
  T-09 stay open around the description-only primary, T-10 and T-40 stay open as placement
  questions, and the ruled, no-D-entry and open counts of `vocabulary_audit_triage.md` are
  unchanged. Nothing here re-judges D-054, F-10's restoration, or any measurement, tie-break or
  confidence, and D-063's six candidate categories, its seven-step selection order and its
  compound-case rule stand exactly as landed.
- **Affected units:** none reclassified. `5a85cead5542991dd0999ea9|dense` is named only as the
  target of an unrun request, and nothing about it changes: no `primary_open_code`,
  `secondary_open_codes`, `candidate_category`, `review_status`, `analytic_status`,
  `taxonomy_defect_flag` or narrative cell of `case_memos_v2.csv` is edited, and no raw note,
  analytic memo or dossier conclusion changes.
- **References:** the round 1 candidate-taxonomy acceptance review
  `docs/Local/Reviews/2026-08-12_candidate_taxonomy_v0_1_round1_independent_review.md`, its
  finding F-02 and its section 10; D-063's `What this does not settle` bullet; D-062 for the
  capability-boundary contract and its minimum-evidence clause; the landed synthesis
  `docs/Local/Synthesis/2026-08-12_sections_8_13_bounded_category_synthesis.md` section 10, the
  K2, K4 and K5 blocks, and its section 15 row for F-10; D-054 for the ruling that made K4's
  request a re-derivation; and
  `references/2026-07-27-manual-failure-review-course-protocol.md` sections 1 and 10.

## D-065 - Land Section 14's candidate taxonomy as a tracked draft

- **Date:** 2026-08-12
- **Status:** active
- **Decision:** Section 14 is landed. `manual_review_v1/analysis/candidate_taxonomy_v0_1.md`
  enters version control and stays at `status: draft`, and Section 14's 35 checklist items in
  `taxonomy_todo.md` are ticked against its text, item by item, as the table below records. The
  document is a **transcription** of landed rulings and decides nothing on its own authority.
  It carries D-063's six candidate categories with D-062's eight capability fields and the
  nine-component judgement contract for each; D-063's seven-step candidate primary-selection
  order; the oracle-name contract in its three typed states; the crowding-family contract with
  the three-route discharge of D-043's second clause; the dilution gate contract; the
  compound-case rule's five clauses; the `unresolved` rule; the `taxonomy_defect_flag` rule;
  the prohibitions that keep rank shape, retriever identity, question type, corpus setting,
  cutoff distance and gold missingness out of the taxonomy; the category-by-backend
  capability-boundary matrix; and D-064's corrected account of the two named minimum-evidence
  items. Where the document and a landed D-entry disagree, the D-entry wins and the
  disagreement is a defect in the document. **Nothing downstream is landed by this entry**: no
  candidate mapping, no frozen taxonomy, no final label, no category count, no `$STAGE` change
  and no triage closure.
- **Rationale:** The document had passed three independent acceptance reviews, the third with
  PASS and no confirmed finding, and it was still untracked and outside this log's authority
  chain. Two things therefore needed an entry rather than only a file write. First, ticking 35
  checkboxes is a state change in a shared file, and the ground for each tick - which passage
  of which section satisfies that item - is exactly the kind of claim this log exists to hold.
  Second, a `draft` file is not an authority, so a document that transcribes this many landed
  rulings has to be pinned to them by an entry stating which rulings it carries and what
  happens where it disagrees with one. It is one entry rather than several because the ticks,
  the file's tracked status and its authority relation to D-062 through D-064 are one act.
- **What the 35 items were checked against.** Read against the document as landed, not against
  the plan that asked for it. The groups sum to 35:

| Items | What they ask for | Where it is |
|---:|---|---|
| 1-3 | YAML front matter, `status: draft`, `last_updated` | The three front-matter lines; `status: draft` is retained deliberately, not left over |
| 4-7 | Document purpose, analysis corpus scope, analytical unit definition, the raw-notes-to-final-labels layering | Sections 0, 1, 2 and 3, the last declaring five artifact and lifecycle states and typing that count apart from D-062's four `failure_layer` values |
| 8-25 | All candidate categories, each with definition, required observable evidence, inclusion rules, exclusion rules, closest competing category, tie-break, positive examples, counterexamples and known limitations, plus D-062's eight capability fields | Section 6, six blocks K1 to K6, each carrying the eight fields under their exact names and all nine judgement components, with the primary-label count stated outside the field block so the eight-field count stays unambiguous |
| 26 | Verification that the eight capability fields obey D-062's closed sets, scope rules and downgrade rule | Section 7's closed-value paragraph and Section 21's field-completeness, closed-value and derived-count assertions, including the `not_run` cap holding on K4 |
| 27-28 | The category-by-backend capability-boundary matrix, and a check that the implementation-induced category makes no method-limit claim on either backend | Section 7's matrix, its two-ground `not_applicable` discipline, and its paragraph deriving that no cell, value or sentence of the K1 row claims a method limit |
| 29-31 | The compound-case rule, the `unresolved` rule, the taxonomy-defect rule | Sections 14, 11 and 13, with Section 11's eight paired legal controls and rejection cases |
| 32-34 | The prohibitions on rank pattern, retriever identity and question type as categories | Section 15 items 1, 2 and 3, item 3 also carrying D-060's ban on any question-quality descriptor and the routing for such observations |
| 35 | A statement that the document is not frozen | The paragraph under the title and Section 20's first bullet |

- **The narrow revision this landing makes to the document.** Sections 0 to 19 are unchanged
  from what the round 3 review read **except for two corrected spans**, both of them the same
  T-09 misstatement F-01 names: K2's known-limitations paragraph in Section 6, which called the
  D-029 boundary open, and Section 19's open-triage-item bullet, which listed T-09 beside T-08
  under K2. Both now record T-09 as ruled by D-053 with only the residual-name question left
  open. That correction moves no boundary value, no `claim_strength`, no unit classification,
  no count and no contract clause, and nothing else in Sections 0 to 19 moves at all. **The
  byte-identity of the rest is a maintainer claim, not an independently verifiable fact**: this
  file has never been committed, so its pre-revision bytes exist nowhere in Git and no reviewer
  can confirm or refute byte-identity; the round 1 review of this landing records it that way
  and re-derived every substantive Section 0 to 19 property instead. Sections 20 and 21 are
  revised, because their own wording described the pre-landing state and would have become
  false the moment this entry landed: Section 20 asserted that all 35 boxes stay unchecked,
  that nothing was staged or committed and that the next action was a fresh review of the file,
  and Section 21 fixed its verification to a HEAD two commits behind and described the tracked
  diff as the D-064 corrective pass's three files. The revision restates the Git state and the
  four-file diff against this landing; the one paragraph classifying the `taxonomy_todo.md`
  diff span by span is now **explicitly scoped as a historical record of the D-064 pass** and
  is followed by a fresh classification of this landing's own +86/-65 TODO diff, so no
  present-tense figure in Section 21 describes a diff other than the one on disk. The revision
  keeps every substantive `does not do` clause, adds no new taxonomy claim — what it adds
  besides the restatement is three verification assertions, each with the negative and legal
  control the round 1 review names for F-01, F-02 and F-03, in the shape Section 21 already
  uses for rounds 1 and 2's findings — and repairs one rendering defect the
  round 3 review classified as cosmetic rather than as a finding, where two `does not do` items
  sat inside a preceding item's prose instead of standing as their own list items. **The
  revised sections were not read by the round 3 review**, and the corrections above were made
  after the round 1 review of this landing and have not been read by any review either; both
  are recorded here rather than left for a later reader to discover.
- **Evidence, and its extent:** no retrieval measurement, ranking, score computation, corpus
  sweep, ablation or oracle injection is run for this entry, and none is authorized by it. The
  title-indexing condition the document names as K2's one actionable minimum-evidence request
  stays **unrun**, and the second named gap is not a request at all, exactly as D-064 fixes it.
  Every figure the document quotes is carried from the decision that measured it and named
  inline there, which was checked mechanically rather than asserted: audited as a draft slice
  the document carries 29 rank-and-score pairs, and every one is found in the landed text of
  the eight decisions it cites for them, D-020, D-024, D-032, D-035, D-036, D-037, D-051 and
  D-059. This entry adds no figure of its own. The landed class counts of the control series
  are unchanged, and `tools/recount.py`'s membership tables stay authoritative for every series
  count.
- **Files and workflow effect:** four files. `candidate_taxonomy_v0_1.md` becomes tracked, with
  the revision above and nothing else. `taxonomy_todo.md` receives the 35 ticks, a Section 14
  landing note in the shape D-061 and D-063 used, the handoff-state and next-unused-decision-ID
  synchronization this append forces, and the correction of the D-section progress lines that
  named Section 14 as not started. `open_code_decision_log.md` receives this entry and nothing
  else. `tools/recount.py` registers this entry as `not_applicable` in every series its text
  matches, on the same ground as D-050, D-052, D-059, D-063 and D-064: the entry names those
  conditions and measures none of them on any unit, so a membership row would claim a
  measurement it did not make.
- **What this does not settle:** Section 15 is **not** open and no `candidate_mapping_v0_1.csv`
  exists; `$STAGE` stays `categories`, and the switch to `mapping-v0` is a separate act needing
  its own authorization. The document stays `draft`, and `taxonomy_v1.md`, `final_labels.csv`
  and `category_counts.csv` do not exist. **No triage item is closed**: T-08, T-10, T-20, T-26,
  T-40, T-45, T-51, T-54, T-56, T-62 and T-63 all stay open, T-10 and T-40 in particular
  staying open as placement questions even though the document carries the contract text they
  concern, and the ruled, no-D-entry and open counts of `vocabulary_audit_triage.md` are
  unchanged. **T-09 is not one of them.** `vocabulary_audit_triage.md`'s `Ruling status` table
  records T-09 as **D-053, landed**, and D-053's own `What this does not settle` names T-08,
  T-04, T-06 and T-40 without naming T-09. What D-053 leaves open there is only whether a
  future residual with genuinely separable evidence could warrant a name, which is eligibility
  for a later ruling and not an open triage item. An earlier draft of this sentence listed
  T-09 among the open items; the round 1 independent review of this landing rejected that as
  its blocking finding F-01 and it was corrected before this entry was committed, under the
  same rule this entry states above: where the document and a landed D-entry disagree, the
  D-entry wins. No category boundary is raised or lowered, no `claim_strength` changes, no
  unit is reclassified, and no `primary_open_code` or `secondary_open_codes` cell moves. The two
  `unresolved` assignments stay as D-063 landed them, and the two units carrying a K4-family
  primary that the category declines are not re-judged. Nothing here re-judges D-001 to D-064,
  and D-063's six categories, its seven-step selection order and its compound-case rule stand
  exactly as landed.
- **Affected units:** none reclassified. No row of `case_memos_v2.csv` is edited, no raw note,
  analytic memo or dossier conclusion changes, and no protected source is touched.
- **References:** `manual_review_v1/analysis/candidate_taxonomy_v0_1.md` as landed, and Section
  14 of `taxonomy_todo.md` for the 35 items; the three independent acceptance reviews of that
  document,
  `docs/Local/Reviews/2026-08-12_candidate_taxonomy_v0_1_round1_independent_review.md` and its
  round 2 and round 3 successors, the third carrying the PASS and the closure of findings F-03
  to F-05; the round 1 independent acceptance review of **this landing**,
  `docs/Local/Reviews/2026-08-12_D-065_section14_landing_round1_independent_review.md`, whose
  FAIL verdict and blocking finding F-01 the corrections above answer, and whose appended
  maintainer response records what was changed; `vocabulary_audit_triage.md`'s `Ruling status`
  table and D-053 for T-09's landed status; D-062 for the capability-boundary contract, D-063
  for the six categories, the
  selection order and the compound-case rule, and D-064 for the minimum-evidence correction;
  the landed synthesis
  `docs/Local/Synthesis/2026-08-12_sections_8_13_bounded_category_synthesis.md`; and
  `references/2026-07-27-manual-failure-review-course-protocol.md` sections 1 and 10.
