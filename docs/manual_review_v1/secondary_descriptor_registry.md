---
status: draft
last_updated: 2026-08-10
---

# Provisional Secondary Descriptor Registry

## Purpose

This registry defines every secondary descriptor adopted during joint review.
Secondary descriptors preserve observable context, downstream effects,
uncertainty, or boundary information; they are not final taxonomy labels.

A descriptor must not be added to a jointly reviewed case unless this registry
contains its definition, inclusion rule, exclusion rule, and affected unit.
New entries are provisional until the vocabulary audit and candidate-taxonomy
stress test are complete.

## `cutoff_sensitive_near_miss`

- **Status:** provisional.
- **Definition:** One or more annotated gold passages sit just below the review
  cutoff, so a small rank movement would change the metric outcome.
- **Include when:** The relevant gold evidence is retrieved close to the cutoff
  and the descriptor is used only to record evaluation fragility. `Close to the
  cutoff` means at most 5.464 percent below the rank-5 score, the largest
  adopted measurement rather than a measured discontinuity (D-042).
- **Exclude when:** The gold is far below the cutoff or absent from the stored
  window, or when cutoff proximity is being presented as a causal mechanism. A
  withholding on substitutability rather than on the gap leaves all three band
  edges untouched, the ground not being the gap (D-042).
- **Affected units:** `5a83aaeb5542996488c2e483|dense`,
  `5ade42b55542992fa25da717|bm25`, `5ade69e455429975fa854ec5|dense`,
  `5ae0a59a55429945ae9593e2|dense`, `5ae1f596554299234fd04372|dense`,
  `5ab8f57b5542991b5579f097|bm25`, `5adf58f15542993a75d264d2|bm25`,
  `5ae1801955429901ffe4aec4|dense`, and `5ae60426554299546bf83019|bm25`.
- **Decision source:** D-006, D-011, D-022, D-023, D-025, D-026, D-027, D-028, D-029,
  D-030, D-031, D-032, D-033, D-034, D-035, D-036, D-038, D-039, and D-042.
  D-042 gives this entry a numeric threshold and adds no affected unit. A required passage
  qualifies only at most 5.464 percent below the rank-5 score, which is the largest adopted
  measurement rather than a measured discontinuity. The never-decided band between 5.464 and
  9.431 percent is deliberately not closed: D-024's 5.698 and D-035's 7.989 were both measured
  inside it and neither was decided on, so a future figure there must be ruled on explicitly
  and may move the edge. D-034's withholding on `5adc8977554299438c868de2|bm25` is written in
  as the exception: at 3.641 percent the passage lay inside the adopted range and the
  counter-evidence supported adoption, two removals giving 5 / 34.046411 and flipping `any@5`,
  yet the descriptor was withheld because four non-gold passages supplied the same intermediate
  fact and two of them sat inside the cutoff. A withholding on that ground moves no band edge.
  D-039 adopts this descriptor on `5ae60426554299546bf83019|bm25` for **both** required
  passages, the first two-sided adoption in this project and therefore the first unit on which
  it describes `full@5` rather than only `any@5` under the D-025 split rule. The answer hop
  sits 0.918846 points, or 4.860 percent, below the rank-5 score of 18.906282 and the
  constraint hop 0.136314 points, or 0.721 percent, below it; both lie inside the accepted
  band, so no band edge moves. The no-substitute condition D-015 established and D-034 applied
  holds on both sides, `space western` occurring in 1 of 4,937 bodies and `bravestarr` in 2,
  both of them golds. There is no cliff to invoke, the successive differences from rank 1 to
  rank 10 being 4.607950, 0.182242, 0.369736, 0.924993, 0.136314, 0.149563, 0.632968, 0.665362
  and 1.300240 with the largest of them below both golds, so the adoption rests on the
  percentages together with the counter-evidence, which is D-032's shape. That counter-evidence
  is the strongest recorded: the cumulative removal ladder runs 7 / 18.005555 and 5 /
  18.898807, 6 / 18.005524 and 4 / 19.036442, 5 / 18.005642 and 3 / 19.187204, 4 / 18.007802
  and 2 / 19.356178, 3 / 18.007533 and 1 / 19.544516, and 2 / 18.034096 and 1 / 19.550617, so
  three removals flip `full@5` where every earlier adoption's counter-evidence flipped `any@5`
  only. Whether the descriptor now needs separate contracts for its `any@5` and `full@5`
  readings is registered as an audit question.
  D-038 is the seventh decision to adopt this descriptor and the first to adopt it on a Dense
  unit since D-026. On `5ae1801955429901ffe4aec4|dense` the rank-5 score is 0.363764 and the
  two required passages sit 0.138340 and 0.018696 points, or 38.030 and 5.140 percent, below
  it. The nearer figure lies inside the accepted band and the farther one inside the excluded
  band, so no band edge moves. The descriptor is adopted for the answer passage only, the split
  D-023, D-025, D-026, D-032 and D-036 used, and the D-025 boundary is recorded again: with the
  other required passage 38.030 percent below the cutoff this entry can describe only the
  `any@5` outcome. The two statements of D-025's split rule this entry carries still disagree,
  and D-036's resolution is followed rather than reopened, the landed adoptions governing and
  the wording staying with the vocabulary audit. The no-substitute condition D-022 introduced
  is met: the answer's own token occurs in exactly 1 of 4,937 indexed bodies, which is that
  passage itself. No cliff can be cited, the successive differences from rank 1 to rank 10
  being 0.007904, 0.022156, 0.006458, 0.013765, 0.005969, 0.000119, 0.004331, 0.002993 and
  0.003683, the largest step in the region sitting between rank 2 and rank 3 above the cutoff
  rather than below it. The counter-evidence this entry has weighed since D-022, the cumulative
  index-side removal ladder, is unavailable in principle on a bi-encoder, as D-035 records;
  what is available instead is that deleting one parenthetical from the passage's own body
  already gives 5 / 0.376585 and flips `any@5`.
  D-036 is the sixth decision to adopt this descriptor and it sets a new lower edge for the
  accepted band. On `5adf58f15542993a75d264d2|bm25` the rank-5 score is 19.686227 and the two
  required passages sit 0.055261 and 10.433763 points, or 0.281 and 53.000 percent, below it.
  0.281 percent is the smallest margin this project has recorded in either direction, below
  D-026's 1.156 percent, so the accepted band now runs from 0.281 to 5.464 percent; 53.000
  percent lies just outside the previous excluded band and moves its upper edge from 52.794
  percent in D-025 to 53.000 percent in D-036, and the never-decided band is unchanged at 5.464
  to 9.431 percent. The descriptor is adopted for the near passage only, the split D-023,
  D-025, D-026 and D-032 used, and the D-025 boundary is recorded again: the other required
  passage is far below the cutoff, so this entry can describe only the `any@5` outcome. No
  cliff can be cited, the successive differences from rank 1 to rank 10 being 0.467669,
  0.491405, 0.159027, 0.284877, 0.055261, 0.224272, 0.288721, 0.118155 and 0.097356, the step
  immediately above the near passage being the smallest of the nine. The counter-evidence
  supports adoption in the D-032 sense: an index-side removal of a single competitor already
  gives 5 / 19.639773 and flips `any@5`. The no-substitute condition D-022 introduced is met, a
  full-corpus scan finding `comic strip presents` in exactly 2 passages which are the two
  required ones and `bad news` in exactly 2 which are the same two. Two boundaries are
  recorded. First, this entry now carries two statements of D-025's split rule that do not
  agree: D-025, D-026 and D-032 adopted the descriptor for the near hop while the far hop sat
  inside the excluded band, and D-035 restates the rule as forbidding the descriptor for the
  whole unit whatever the near figure does; D-036 follows the landed adoptions and refers the
  wording to the vocabulary audit. Second, this is the first unit on which a complete
  alternative answer already sits inside the cutoff, so what the descriptor records here is the
  fragility of the annotated title rather than of answer availability, a weaker reading than
  D-022 through D-032 gave it.
  D-035 is the ninth decision to withhold this
  descriptor and the first to withhold it on a figure that falls strictly inside the
  never-decided band. On `5add67915542992200553af8|dense` the rank-5 score is 0.476272 and the
  two required passages sit 0.038049 and 0.069500 points, or 7.989 and 14.592 percent, below
  it. The ground is the D-025 split rule for a bridge question needing both hops: the farther
  figure lies inside the excluded band of 9.431 to 52.794 percent, so the descriptor cannot
  cover this unit whatever the nearer figure does. **Because the ground is the split rule and
  not the nearer gap, no band edge moves:** the accepted band stays 1.156 to 5.464 percent, the
  excluded band stays 9.431 to 52.794 percent, and the never-decided band stays 5.464 to 9.431
  percent. 7.989 percent is recorded as measured but not band-setting, the treatment given to
  D-024's 5.698 percent and D-034's 3.641 percent. No cliff can be cited, the successive
  differences from rank 1 to rank 10 being 0.021442, 0.006520, 0.000134, 0.011859, 0.020891,
  0.017158, 0.012920, 0.002206 and 0.006805. D-035 also records that the counter-evidence this
  entry has weighed since D-022, the cumulative index-side removal ladder, is unavailable in
  principle on a bi-encoder: that ladder is an arithmetic identity, so the observation that two
  removals give 5 / 10 and flip `any@5` is a count read off the ranking rather than a
  measurement. Whether the ladder should have been read as counter-evidence on the earlier
  Dense units is a vocabulary-audit question and is not a re-judgment of any of them. D-034 is
  the eighth decision to withhold this
  descriptor, the first to withhold it on a figure inside the accepted band, and the first since
  D-015 to decide it on substitutability rather than on the score gap. On
  `5adc8977554299438c868de2|bm25` the rank-5 score is 34.644248 and the two required passages sit
  1.261380 and 17.488945 points, or 3.641 and 50.482 percent, below it. The nearer figure lies
  inside the accepted band of 1.156 to 5.464 percent and the counter-evidence would support
  adoption: the cumulative removal ladder gives 6 after one removal, 5 after two, 4 after three,
  3 after four, 2 after five and 1 after six, so dropping only two competitors already gives
  5 / 34.046411 and flips `any@5`. No cliff can be cited, the successive differences from rank 1
  to rank 10 being 1.492919, 3.224170, 0.967934, 1.461482, 0.480356, 0.781024, 2.525275, 3.247083
  and 1.188520. What fails is the no-substitute condition D-022 introduced and every adoption
  since has checked, and on which D-015 removed this descriptor: four non-gold passages supply
  the nearer passage's intermediate fact under the standard the gold itself uses, and two of them
  sit inside the cutoff at 1 and 4. Because the ground is substitutability and not the gap, no
  band edge moves: the accepted band stays 1.156 to 5.464 percent, the excluded band stays 9.431
  to 52.794 percent, and the never-decided band stays 5.464 to 9.431 percent. Whether a
  withholding that does not rest on the gap should be allowed to leave the bands untouched is a
  vocabulary-audit question. The farther required passage at 50.482 percent falls inside the
  excluded band, so the D-025 boundary would have applied in any case.
  D-033 is the seventh decision to withhold this descriptor, the
  sixth to do so on the score gap alone, and the first to narrow the never-decided band from
  above rather than from below. On `5abcc96c5542996583600492|bm25` the rank-5 score is 31.796696
  and the two required passages sit 2.998596 and 5.721776 points, or 9.431 and 17.995 percent,
  below it. The nearer figure lies inside the band this project had measured but never decided
  on, between 5.464 percent in D-032 and 12.518 percent in D-028, and the farther lies inside the
  excluded band. The counter-evidence is weak rather than strong, in the D-029, D-030 and D-031
  sense and not the D-032 sense: a cumulative index-side removal ladder gives 25 after one
  removal, 23 after three, 21 after five, 16 after ten, 11 after fifteen, 7 after twenty and 2
  after twenty-five, so twenty removals are needed before the nearer passage reaches 7. No score
  cliff can be cited, the successive differences from rank 1 to rank 10 being 1.153544, 1.384457,
  3.638157, 0.795088, 0.183632, 0.219417, 0.130204, 0.581458 and 0.113202, the one large step
  lying between ranks 3 and 4 above both required passages. The no-substitute condition would
  have been met, a full-corpus scan finding the answer film named in exactly 2 passages which are
  the two required ones, so the decision rests on the gap and the ladder. Withholding moves the
  excluded band's lower edge from 12.518 percent in D-028 to 9.431 percent in D-033 and narrows
  the never-decided band to 5.464 to 9.431 percent; no rule text is changed and setting an
  explicit threshold remains a vocabulary-audit matter.
  D-032 is the fifth decision to adopt this descriptor and the first to
  adopt it inside the band this project had never decided on. On `5ab8f57b5542991b5579f097|bm25` the
  rank-5 score is 28.423217 and the two required passages sit 1.553124 and 8.681607 points, or
  5.464 and 30.544 percent, below it. The nearer figure falls between the largest previous
  acceptance at 4.503 percent in D-025 and the smallest previous exclusion at 12.518 percent in
  D-028, so adopting it for that passage moves the accepted band's upper edge to 5.464 percent and
  narrows the never-decided band to 5.464 to 12.518 percent; no rule text is changed and setting an
  explicit threshold remains a vocabulary-audit matter. The descriptor is adopted for the near
  passage only, the split D-023, D-025 and D-026 used, and the D-025 boundary is recorded again:
  the other required passage sits at 30.544 percent inside the excluded band, so this descriptor
  can describe only the `any@5` outcome and no rank movement of the near passage alone can change
  `full@5`. There is no score cliff to appeal to, the successive differences from rank 1 to rank 10
  being 3.872190, 0.145559, 0.796755, 1.958705, 1.553124, 1.781180, 3.413115, 1.487109 and
  0.318694. The counter-evidence is the strongest this project has recorded in either direction and
  it supports adoption here rather than qualifying it: an index-side removal of a single competitor
  already lifts the near passage to 5 / 26.870018 and flips `any@5`. The no-substitute condition is
  met, a full-corpus scan finding `mcgrath` in exactly 1 of 4,937 passages, itself.
  D-031 is the sixth decision to withhold this descriptor and the fifth to do
  so on the score gap alone. On `5ab48c325542996a3a969f93|dense` the rank-5 score is 0.488627
  and the two required passages sit 0.146459 and 0.149314 points, or 29.974 and 30.558 percent,
  below it, so both fall inside the excluded band running from 12.518 percent in D-028 to
  52.794 percent in D-025 and far outside the accepted band of 1.156 to 4.503 percent; the
  never-decided band is therefore unchanged at 4.503 to 12.518 percent. Unlike D-028 and like D-027
  a real score cliff can be cited, 0.069056 separating rank 7 at 0.442921 from rank 8 at
  0.373865, with both required passages below it; the successive differences from rank 1 to
  rank 10 are 0.003115, 0.044988, 0.075249, 0.000442, 0.037176, 0.008530, 0.069056, 0.000616
  and 0.007934. As in D-028 and D-029 the counter-evidence is weak rather than absent: a
  cumulative index-side removal ladder gives 15 and 18 after three removals and needs sixteen
  before the answer hop reaches 5 and seventeen before both required passages enter the cutoff.
  The no-substitute condition is met, a full-corpus scan finding exactly one passage stating
  each required fact, itself.
  D-030 is the fifth decision to withhold this descriptor and the fourth to do so on the
  score gap alone. On `5a83880e554299123d8c214e|bm25` the rank-5 score is 18.467254 and the two
  required passages sit 5.881611 and 5.754192 points, or 31.849 and 31.159 percent, below it, so
  both fall inside the excluded band running from 12.518 percent in D-028 to 52.794 percent in
  D-025 and far outside the accepted band of 1.156 to 4.503 percent; the never-decided band is
  therefore unchanged at 4.503 to 12.518 percent. There is no score cliff, the successive
  differences from rank 1 to rank 10 being 0.129332, 1.401531, 0.613341, 0.984862, 1.684766,
  0.497086, 0.275489, 0.046511 and 0.322020. As in D-029 the counter-evidence is weak rather
  than absent: a cumulative index-side removal ladder needs sixty removals before either
  required passage reaches 4, three removals giving 65 and 59 and ten giving 58 and 50. The
  no-substitute condition is met, a full-corpus scan finding exactly one passage stating each
  required fact, itself.
  D-029 is the fourth decision to withhold this descriptor and the third to do so on
  the score gap alone. On `5a81ebee554299676cceb16d|dense` the rank-5 score is 0.460548 and
  the two required passages sit 0.095238 and 0.128157 points, or 20.679 and 27.827 percent,
  below it, so both fall inside the excluded band that now runs from 12.518 percent in D-028
  to 52.794 percent in D-025 and far outside the accepted band of 1.156 to 4.503 percent.
  There is no score cliff, the successive differences from rank 1 to rank 10 being 0.002518,
  0.010296, 0.034229, 0.007743, 0.004229, 0.006203, 0.004349, 0.001895 and 0.003646. Unlike
  D-027 and D-028 there is no counter-evidence either: removing the top three or the top five
  competitors leaves the nearer required passage at 40 and 38, and ninety-three removals are
  needed before both enter the cutoff, so this is the first exclusion in which no small
  index-side change moves the metric at all. The no-substitute condition is met, a full-corpus
  scan finding exactly one passage stating each required fact, itself.
  D-028 is the third decision to withhold or remove this descriptor and the second to do
  so on the score gap alone, following D-027. On `5a79b7f6554299029c4b5f6f|bm25` the
  rank-5 score is 31.122376 and the two required passages sit 3.895838 and 9.630026
  points, or 12.518 and 30.942 percent, below it. The nearer figure falls in a band this
  project had never decided on, between the largest acceptance at 4.503 percent in D-025
  and the smallest previous exclusion at 19.351 percent in D-027, so withholding the
  descriptor here narrows the never-decided band to 4.503 to 12.518 percent; the farther gold
  falls squarely inside the excluded band, so the D-025 boundary applies again and no rank
  movement of the near gold alone can change `full@5`. Unlike D-027 there is no score
  cliff to appeal to: the successive differences from rank 4 to rank 9 are 0.597253,
  1.720835, 0.694195, 1.480808 and 1.252255. The counter-evidence is recorded rather than
  suppressed, as in D-027: an index-side removal of only the top three competitors lifts
  the nearer gold to 5 / 27.859579, so the metric is again sensitive to a small
  index-side change even where the golds are not close to the cutoff in score. The
  no-substitute condition is also met, a full-corpus scan finding exactly one passage
  stating each required fact, itself, so nothing but the score gap carries the decision.
  D-026 adds
  the smallest margin recorded so far: the near-miss gold sits 0.005537 points,
  or 1.156 percent, below the rank-5 score at rank 6 of 4,937, and a full-corpus
  scan finds exactly one passage stating the fact it supplies, itself, so the
  no-substitute condition D-022 and D-023 used is met. The same D-025 boundary
  applies and is recorded again: the other required passage is 24.619 percent
  below the cutoff at rank 13, so this descriptor can describe only the `any@5`
  outcome and no rank movement of the near gold alone can change `full@5`.
  D-025 applies the
  same split D-023 used, on a unit where the two required passages sit 0.021201
  and 0.248537 points below the rank-5 score, that is 4.503 and 52.794 percent:
  the descriptor is adopted for the near-miss answer hop only, whose sole
  corpus-wide substitute lies outside the cutoff at rank 6, and the far gold at
  rank 115 of 4,937 is excluded from it by the existing exclusion. D-025 also
  records the boundary that this descriptor can only ever describe the `any@5`
  outcome in a bridge unit whose other required passage is far below the cutoff,
  since `full@5` cannot be changed by any rank movement of the near gold alone.
  D-022 records that this
  descriptor is retained where the gold's own score gap is measured and small,
  0.952795 points or 2.17 percent below the rank-5 score, and where no
  substitute exists, in contrast to D-015, which removed it because the affected
  gold was already substitutable inside the top five. D-023 applies the same
  distinction to a unit in which the two conditions fall on different passages:
  the near-miss gold is 0.021367 points or 4.137 percent below the rank-5 score
  and has no substitute anywhere in the corpus, while a different required
  passage does have an evidence-bearing substitute inside the top five.
  D-027 is the second decision to **remove** this descriptor from a unit, after D-015,
  and the first to remove it on the score-gap measurement alone rather than on
  substitutability. Both required passages of `5a78b209554299148911f93e|dense` sit
  0.106102 and 0.104214 points, or 19.701 and 19.351 percent, below the rank-5 score,
  which falls in the band already excluded, 24.619 percent in D-026 and 52.794 percent
  in D-025, and far outside the band accepted so far, 1.156 percent in D-026, 2.17 in
  D-022, 4.137 in D-023 and 4.503 in D-025. A gap of 0.067081 separates rank 7 from
  rank 8 there, so a real score cliff lies between the cutoff region and the two golds
  even though they sit only three and four rank positions below it. Note that this unit
  meets the no-substitute condition D-022, D-023 and D-026 relied on, since a
  full-corpus scan finds exactly one passage stating each required lifespan, itself, so
  the removal rests on the score gap and on nothing else. D-027 records the
  counter-evidence rather than suppressing it: an index-side removal of only three
  competitors already lifts one gold to 5, so the metric is sensitive to a small
  index-side change even where the golds are not close to the cutoff in score. D-027
  also records that this entry's exclusion says `far below the cutoff` without a
  numerical threshold, and that supplying one would edit this entry, so it is deferred
  to the vocabulary audit.

## `cross_entity_token_recombination`

- **Status:** provisional.
- **Definition:** An order-insensitive token matcher rewards a distractor that
  combines tokens originating from different queried entities or facets without
  preserving their original boundaries.
- **Include when:** The tokenizer and scoring implementation are known, and a
  retrieved distractor has score-bearing tokens drawn from different entities
  or query components.
- **Exclude when:** The evidence shows only ordinary same-entity overlap, or the
  retrieval method does not support a token-level boundary analysis.
- **Affected units:** `5a78b209554299148911f93e|bm25` and
  `5adf58f15542993a75d264d2|bm25`.
- **Decision source:** D-010 and D-036.
  D-036 is the second affected unit, the first since D-010, and the first in which the
  recombining passage is the one that defined the cutoff. On `5adf58f15542993a75d264d2|bm25`
  the question's only proper name is the quoted title "The Young Ones", which the implemented
  tokenizer splits into `"the`, `young` and the dead `ones"?`. `Gretchen Palmer` at 5 /
  19.686227 stood 0.055261 points above the bridge passage and took 7.949254, or 40.4 percent,
  of its score from the two surviving fragments while having no connection to the queried
  series: 4.111593 came from `young` supplied by The Young and the Restless and 3.837661 from
  `"the` supplied by three unrelated quoted series titles. The include rule's requirement that
  the score-bearing tokens be drawn from different entities is therefore met at the level of
  one query phrase rather than of two queried entities as in D-010; the definition already
  covers query components, so no rule text is changed.

## `generic_person_semantic_neighborhood`

- **Status:** provisional.
- **Definition:** High-ranked dense passages form a broad cluster of person
  biographies or person-related content matching generic attributes of the
  question while the explicitly named target entities remain lower.
- **Include when:** Multiple leading passages share the broad person type or
  attribute semantics but do not identify the queried entities.
- **Exclude when:** Documents related to only one named comparison entity
  dominate, or when the descriptor is being used to claim an unobserved
  internal embedding component.
- **Affected units:** `5a76387d554299109176e6ba|dense`,
  `5ade69e455429975fa854ec5|dense`, `5a81ebee554299676cceb16d|dense`, and
  `5add67915542992200553af8|dense`.
- **Decision source:** D-009, D-023, D-029, D-031, D-035, and D-056.
  D-056 keeps this descriptor's partial coverage of the neighbourhood D-023 recorded, and adds
  no affected unit. The name is not widened past its definition, which is scoped to person
  biographies and person-related content while the uncovered half of that neighbourhood is
  unrelated films, and no Dense-only same-domain descriptor is coined: D-035 considered such a
  name on its own unit and deleted it, and D-023's removal probe over all four person
  biographies in its top six moves the required passages only to 3 / 0.495152 and 28 /
  0.400140, which that entry records as displacement rather than as an effect of its own. What
  the ruling adds is prospective and general rather than a clause of this entry: where a
  dossier or an entry states that a competing family has been enumerated and the adopted
  descriptors cover only part of it, the uncovered members must be identified explicitly in
  that dossier, so silence is never read as coverage. That is an evidence-recording rule and
  not a requirement that every high-ranked passage receive a descriptor. D-023's unit is not
  reclassified and gains no secondary.
  D-035 is the fourth affected unit and the first in which the question names no entity at all,
  so the definition's clause `while the explicitly named target entities remain lower` has no
  referent; that is recorded as a boundary and no wording is changed. On
  `5add67915542992200553af8|dense` all 6 passages above the bridge passage and 7 of the 10
  above the answer passage are biographies of criminals identifying neither required entity,
  `Calcedonio Di Pisa` 1 / 0.516227, `Antonio Rotolo` 2 / 0.494784, `Angelo La Barbera` 3 /
  0.488265, `Antonio Cottone` 4 / 0.488130, `Joseph LoPiccolo (organized crime)` 5 / 0.476272,
  `Salvatore La Barbera` 6 / 0.455380 and `Gaspare Spatuzza` 9 / 0.423097, six of them
  explicitly Sicilian Mafia members where 8 of 4,937 passages contain `sicilian mafia`. **The
  descriptor is adopted as a composition, explicitly not as a causal claim, and D-035 records
  why no materiality evidence is available to it on this backend:** cosine carries no
  collection statistic, so every index-side removal probe is an arithmetic identity in which
  `rank_after` equals `rank_before` minus the number of removed passages that ranked above the
  gold. Nine cells confirm it exactly with every score bit-identical, and two different random
  7-passage subsets of the same pool give the same answer-hop rank of 5, so dropping this
  family and dropping its complement, 1 / 5 against 7 / 9, differ only in size. Pit 19y treats
  the drop-everything cell as an identity and offers the family probe with a complement control
  as the discriminating alternative; on this evidence that alternative is an identity too,
  which is registered as a vocabulary-audit question about the earlier Dense applications and
  is not a re-judgment of any of them. What is measured instead is the query side, which does
  change the scores: the question's referring description alone reproduces 9 of the baseline
  top ten and 6 of this family, deleting that description leaves 0 and 0, deleting only its
  demonym half leaves 2 and 1, and the answer frame alone gives 0 and 0, so the family is
  produced by the referring description and is downstream of the adopted primary. D-031 records
  a non-adoption, not an
  affected unit. On `5ab48c325542996a3a969f93|dense` five of the eight passages above the
  required evidence are person biographies, `Tostig Godwinson` 1 / 0.612422,
  `Leofwine Godwinson` 2 / 0.609307, `Godwin, Earl of Wessex` 3 / 0.564319,
  `Gytha Thorkelsdottir` 6 / 0.451451 and `Edith the Fair` 9 / 0.373248, so the surface shape
  resembles this descriptor. It is not adopted because every one of them contains the string
  `Harold Godwinson` and states its own relationship to him in its own text, which is the
  `related_name_document_crowding` definition, and because this entry's definition is scoped to
  a cluster matching generic attributes while the explicitly named target entities remain
  lower, whereas here the cluster is organized by that named entity itself. This is the mirror
  image of the D-029 situation, where the descriptor was scoped to a counted subset of a larger
  family; here there is no generic half to scope it to. D-029 is the first unit in which this
  descriptor is scoped to a counted subset of a larger competing family that a
  crowding primary already covers. Its inclusion rule is met by the person biographies read
  in full above each required passage, 19 of the 42 above the bridge hop and 49 of the 92
  above the answer hop, every one of them a film director, actor, actress, model or presenter
  page that identifies neither queried entity, among them `Enrique Carreras` 1 / 0.515333,
  `Sebastian Mantilla` 3 / 0.502519, `Janine Gutierrez` 4 / 0.468290 and `Jackie Lou Blanco`
  7 / 0.450116. The exclusion does not fire, since no single named candidate organizes the
  set. D-029 registers, rather than closes, the question this nesting raises: D-023 recorded
  the converse shape, a neighbourhood whose non-biography half received no descriptor at all,
  whereas here `question_frame_semantic_crowding` is the primary and covers the whole family,
  so whether a scoped subset may also be carried as a secondary is a vocabulary-audit
  question. D-023 records that the descriptor covers
  only the biography half of the observed neighborhood in that unit; roughly
  half of the non-naming competitors above the lower gold are unrelated films
  rather than person pages, and no second descriptor was added for them during
  the validation pass.

## `generic_term_lexical_crowding`

- **Status:** provisional.
- **Definition:** Multiple high-ranked non-answer passages match broad category,
  institutional, or relational vocabulary from the query while omitting the
  decisive entity or conjunction needed by the evidence chain.
- **Include when:** Actual passage texts verify at least two higher-ranked
  competitors matching the same broad lexical facets, and those passages fail
  a concrete query constraint rather than supplying a complete alternative
  answer.
- **Exclude when:** The classification is based only on titles, only one
  competitor is present, or a passage supplies a complete answer. When a more
  specific implementation-supported score mechanism is established, use this
  as a secondary output description rather than the primary cause.
- **Boundary against `same_topic_passage_distractor`, prospective (D-055):** A competing
  passage belongs here when it matches broad category, institutional or relational vocabulary
  from the query and its body verifies no real connection to the queried entity, work or
  topic. Where the body does verify such a connection and also verifies the missing decisive
  constraint, the passage belongs to `same_topic_passage_distractor` instead. Different subsets
  of the passages above a required passage may carry the two descriptors within one unit; the
  same passage set must not carry both.
- **Affected units:** `5a83a532554299334474606f|bm25`,
  `5ac1a3665542994ab5c67daf|bm25`, `5ade42b55542992fa25da717|bm25`,
  `5ae057fd55429945ae959328|bm25`, `5a79b7f6554299029c4b5f6f|bm25`,
  `5a83880e554299123d8c214e|bm25`, `5abcc96c5542996583600492|bm25`,
  `5adf58f15542993a75d264d2|bm25`, and `5adc8977554299438c868de2|bm25`.
- **Decision source:** D-016, D-021, D-022, D-024, D-028, D-030, D-032, D-033, D-034,
  D-036, D-039, and D-055.
  D-055 retains this descriptor and `same_topic_passage_distractor` as two names, refuses the
  merge, and adds no affected unit. The prospective boundary bullet above states the
  passage-level line from this side: a competing passage matching broad category, institutional
  or relational vocabulary without a verified connection to the queried entity, work or topic
  belongs here rather than there. That is the routing D-028 already applied when it declined
  the sibling name because the shared material was the question's broad category vocabulary and
  this name was the more specific fit, and D-039 applied in the opposite direction on its own
  unit. The definition, the inclusion rule, the exclusion clause and the affected-units list
  are unchanged. That list then omitted `5adc8977554299438c868de2|bm25`, which
  `case_memos_v2.csv` carries; the omission was one of three of the same shape, and
  all three were repaired in the third batch's landing of 2026-08-10 under item
  T-55, which is bookkeeping against D-034 and carries no decision ID of its own.
  D-039 records a non-adoption, not an affected unit. On `5ae60426554299546bf83019|bm25` the
  five passages above the answer hop other than the scaffold artefact do share broad
  institutional vocabulary with the question, but the family is name-driven and not
  category-driven and pits 19f and 19i say so in both directions: `celebrity` alone reproduces
  5 of 5 of that family while the whole genre facet reproduces 0 of 5, and deleting the
  distributor name from the question collapses it to 0 of 5 while deleting the genre facet
  leaves it at 5 of 5. The observed family is therefore recorded under
  `related_name_document_crowding`. This is D-034's test with the outcome reversed: there the
  surface shape fitted this descriptor's sibling and the two directions routed it here, and
  here they route it back.
  D-036 is the ninth affected unit and the second, after D-033, in which the pit 19f and 19i
  test is weak in both directions. On `5adf58f15542993a75d264d2|bm25` the inclusion rule is met
  on read text by four of the five higher-ranked passages, `Sianoa Smit-McPhee` 1 / 21.089205,
  `Tzi Ma` 2 / 20.621536, `The Itchy &amp; Scratchy Show` 4 / 19.971104 and `Gretchen Palmer` 5
  / 19.686227, each taking between 32.9 and 63.4 percent of its score from the content-bearing
  category terms `television`, `series`, `actor`, `featured` and `performed` while stating
  nothing about the queried series. The fifth is kept out of the family by this entry's own
  exclusion for a passage supplying a complete alternative answer. Forward, the referent cue
  alone reproduces 2 of those five in its top ten; in reverse, the frame with the cue deleted
  reproduces a different 2 and the fifth is reproduced by neither, so neither family can be
  assigned to the other and the entry keeps this one as a secondary. Removing the four gives 2
  / 19.681225 against a size-matched null of 6 / 19.665899, and the statistics-matched control
  gives 2 / 19.630966 at a score bit-identical to the baseline, so unusually for a lexical
  backend the gain is entirely positional and the statistical half is exactly zero.
  D-034 is the eighth affected unit and the first in which the pit 19f and 19i test is strong in
  both directions and still leaves the family with this entry rather than assigning it to the
  primary. On `5adc8977554299438c868de2|bm25` the inclusion rule is met on read text by all six
  higher-ranked passages, `Eir` 1 / 41.790753, `Marzanna` 2 / 40.297834, `Nanna (Norse deity)`
  3 / 37.073664, `Sága and Sökkvabekkr` 4 / 36.105730, `Fensalir` 5 / 34.644248 and
  `Gná and Hófvarpnir` 6 / 34.163892, each earning between 16.552392 and 21.498698 from the
  broad category token `goddess` and none supplying a complete alternative answer, the
  question's other constraint being stated in exactly one passage in the corpus. Forward, the
  referent cue alone places 5, 6, 9 and 10 of its top ten inside the baseline top 5, 6, 10 and
  16 and `goddess` alone places 5, 6, 8 and 10; in reverse, deleting both occurrences of
  `goddess` leaves 0, 0, 1 and 5. The descriptor is kept as a secondary under the exclude rule's
  deferral clause and on a second, stronger ground: at baseline the family cannot be
  outcome-determinative on the answer passage at all, dropping every one of the 70 non-gold
  passages above it still leaving 14 / 17.293278. D-034 records that this second ground is
  itself baseline-dependent, the same cell giving 1 / 52.744000 and 2 / 23.271751 once the
  preprocessing defect is repaired, which extends D-033's pit from the family probe to pit 19u's
  own cell.
  D-033 is the
  seventh affected unit and the first in which the pit 19f and 19i test is weak in **both**
  directions, so neither this family nor the referent's can be assigned to the other. On
  `5abcc96c5542996583600492|bm25` the inclusion rule is met on read text by eleven higher-ranked
  passages that match only the question's broad film vocabulary, `film`, `name`, `starring`,
  `character` and `features`, and contain neither queried entity: `Dark Passage (film)`
  4 / 32.591784, `Bridge to Terabithia (1985 film)` 5 / 31.796696, `Nagaram (2010 film)`
  8 / 31.263442, `Penny (The Big Bang Theory)` 9 / 30.681984, `Silver Bells (film)`
  13 / 29.966798, `Beauty and the Beast (1991 film)` 14 / 29.958988, `Catwoman (video game)`
  17 / 29.665505, `Hoppy Serves a Writ` 21 / 28.972521, `Sons of the Pioneers (film)`
  23 / 28.895199, `The Testimony (1946 film)` 25 / 28.846896 and `Kingdom of Northumbria`
  27 / 28.757669, none of which supplies an alternative answer. Two of them occupy cutoff
  positions and thirteen of the twenty-five passages above the bridge passage belong to this
  family. Materiality holds and is the largest single removal effect measured at baseline in this
  unit, larger than the name family's: dropping the 95 passages above the answer passage that
  carry no queried name gives 10 / 29.270483 and 30 / 26.124391. The pit 19f and 19i test is weak
  both ways, the interrogative frame alone reproducing 3 of 10 of the baseline top ten and 4 of 10
  of its top sixteen, the referent cue alone reproducing 4 and 5, and deleting the two referent
  name tokens from the full question leaving 5 of 10 and 8 of 10 in place, so the observed
  neighbourhood does not collapse when the referent is removed. This is a third outcome for that
  test after the forward-strong results of D-024 and D-028 and the reverse-strong result of D-030,
  and it is why the descriptor is kept as a secondary here without the deferral clause having to
  be invoked. D-032 records a
  non-adoption, not an affected unit, and it is the first unit in this pass in which the inclusion
  rule fails outright rather than being met and deferred. On `5ab8f57b5542991b5579f097|bm25` the
  nine passages above the required evidence earn their ranks from proper-noun tokens, `thomas`,
  `h.` and `ince`, rather than from broad category, institutional or relational vocabulary, and the
  question's only category word, `nationality?`, occurs in 0 corpus passages and contributes
  exactly 0.000000. The pit 19f and 19i test settles it in both directions: a query reduced to the
  interrogative frame alone and a query reduced to `nationality` each place 0 of 10 of their top
  ten inside the baseline top five, top ten or top eleven, while the referent name alone places
  5 of 10, 8 of 10 and 9 of 10. The observed family therefore belongs to the question's referent
  and not to its generic vocabulary, which is the opposite of the D-030 result on the same test.
  D-030 is the first unit in
  which this descriptor is the closest competitor to the adopted primary and the first in which
  the pit 19f and 19i test comes out the other way round. Its inclusion rule is met on read
  text: 59 of the 64 passages above the answer hop are song or album profiles, each earning its
  rank from the same broad category vocabulary of `album`, `song`, `released`, `features` and
  `based`, and none supplying a complete alternative answer; 5 more carry a comic cue and 1 is
  neither, and not one of the 64 contains any of the question's proper nouns. The exclude rule's
  third clause, which assigns a family produced by the decisive referent cue to the primary
  mechanism, is tested and does **not** fire here, unlike D-024 and D-028: forward, the referent
  cue `Suicide's 1977 released album` alone puts only 2 of 10 of its top ten inside the baseline
  top ten and 4 of 10 inside the 64, while in reverse the frame alone puts 4 of 10 and 8 of 10,
  the probe `album features a song` puts 4 of 10 and 10 of 10, and deleting the band name from
  the full question leaves the top ten 10 of 10 identical, so the family belongs to the
  question's generic vocabulary rather than to its referent. The descriptor is nevertheless kept
  as a secondary output description under the exclude rule's deferral clause, and D-030 adds a
  second, stronger ground that no previous unit supplied: the crowding cannot be
  outcome-determinative here at all, because dropping every one of the 64 non-gold passages
  above the answer hop still leaves 8 / 13.038940 and 2 / 13.262049. The family-scoped probe and
  its complement control give 14 / 13.022572 and 7 / 13.216898 against 62 / 12.601801 and
  54 / 12.754929. D-028 is the first unit in
  which this name arrives as the *provisional primary* and is demoted to a secondary by
  the exclude rule's deferral clause, and the first in which the demotion rests on the
  pit 19f and 19i test run in **both** directions. Its inclusion rule is met on read
  text: fourteen higher-ranked competitors, every one a restaurant-chain profile or the
  generic fast-food definition, each earning between 18.094218 and 29.047969 from the
  same five-token category facet and exactly 0.000000 from the queried person's name, and
  none supplying a complete alternative answer. Forward, the descriptive referent cue
  alone puts 9 of 10 of its top ten inside the baseline top-fifteen non-gold set; in
  reverse, deleting that cue from the full question leaves 3 of 10, while deleting the
  person's name instead leaves the family untouched at 9 of 10. The more specific
  implementation-supported mechanism it defers to is the tokenizer and indexed-field pair,
  the only non-oracle conditions that place both required passages inside the cutoff. D-024 records the strongest
  application of the exclude rule's deferral clause so far: the descriptor's own
  inclusion rule is met by ten verified generic company profiles, and an index-side
  removal probe that drops exactly those ten, leaving every name-sharing rival in
  place, is the only non-oracle condition in that unit which places both required
  hops inside the top five. It is nevertheless kept as a secondary output
  description, because two reduced-query probes show that the question's own
  descriptive referent cue reproduces the entire observed neighborhood, ten of ten
  inside the baseline top sixteen and seven of ten inside the baseline top ten.
  That is the test D-023 used to demote `question_frame_semantic_crowding`, applied
  here to a lexical retriever.

## `gold_chain_not_unique`

- **Status:** provisional.
- **Definition:** The annotated supporting-fact chain is not the only evidence
  path that can satisfy the question under a consistent interpretation of its
  explicit constraints.
- **Include when:** A concrete alternative passage or chain supports a complete
  answer using the same evidentiary standard applied to the annotated gold.
- **Exclude when:** The alternative omits a decisive constraint, is merely
  topically related, or depends on applying a looser standard than the gold.
- **Affected units:** `5a83aaeb5542996488c2e483|dense` and
  `5adf58f15542993a75d264d2|bm25`.
- **Decision source:** D-011 and D-036.
  D-036 is the second affected unit and the first on a lexical retriever. On
  `5adf58f15542993a75d264d2|bm25` the question asks which television series featured an actor
  who also performed in "The Young Ones", and `Filthy Rich &amp; Catflap` at 3 / 20.130130
  states on read text that the BBC sitcom's series featured former "The Young Ones" co-stars
  Nigel Planer, Rik Mayall and Adrian Edmondson as its three title characters, so one passage
  inside the cutoff satisfies every explicit constraint. The include rule's requirement of the
  same evidentiary standard is met and then some: the annotated chain reaches its answer only
  by preferring one required passage's characterization of "The Comic Strip Presents..." as a
  television series over the other's characterization of it as a series of films, and the
  alternative needs no such reconciliation. The exclusion for a merely topical alternative was
  tested against all nine passages naming the Young Ones and seven fail it on read text,
  `Carole Gray` 18 / 17.701479 additionally changing the referent to the 1961 film of the same
  name.

## `gold_chain_substitutability`

- **Status:** provisional.
- **Definition:** A non-gold passage can replace at least one annotated gold
  passage by supplying the same answer-bearing intermediate fact, even when a
  complete alternative chain is not present within the evaluation cutoff.
- **Include when:** Actual passage text shows that the non-gold passage supports
  the same required intermediate fact under the evidentiary standard applied
  to the annotated gold.
- **Exclude when:** The passage is merely topically related, omits the decisive
  fact, changes the answer, or requires a looser interpretation than the gold.
- **Affected units:** `5a7c9f325542990527d554e6|bm25`,
  `5a7d19d85542995ed0d165e8|dense`, `5ade69e455429975fa854ec5|dense`,
  `5ae0a59a55429945ae9593e2|dense`, and `5adc8977554299438c868de2|bm25`.
- **Decision source:** D-014, D-015, D-023, D-025, D-034, and D-038.
  D-038 withholds this descriptor on `5ae1801955429901ffe4aec4|dense` and registers the
  boundary it turns on rather than closing it. `Cocoa Krispies` at 2 / 0.406143 states that the
  cereal is produced by the queried company, which names the bridge entity the question never
  names and links it to one of the question's two coordinated constraints. It is withheld
  because the fact it supplies is the required intermediate fact of neither annotated gold: the
  constraint passage's fact is the Superman sponsorship, which that body does not state, and
  the answer passage's decisive fact is the location, which it omits, so the exclusion for
  omitting the decisive fact fires. Adopting it would change no metric in any case, because the
  location is written in exactly 1 of 4,937 indexed bodies, the answer passage itself at 11 /
  0.345068, outside the cutoff, which is the boundary D-025 recorded on the position of a
  substitute. What is new here and goes to the vocabulary audit is the shape rather than the
  position: D-023 adopted a substitute that supplied its gold's own intermediate fact while
  verifying only one of the question's two constraints, whereas this passage reaches the same
  bridge entity through a different one of the question's constraints, and whether those are
  the same shape under the current include rule is not settled here.
  D-034 is the fifth affected
  unit, the first on a lexical retriever, and the first in which the substitutes are alternative
  referents of the question's own description rather than alternative statements of one entity's
  fact. On `5adc8977554299438c868de2|bm25` the question identifies the bridge entity only as the
  goddess associated with the goddess Frigg. Six non-gold passages mechanically name Frigg,
  `goddess` and Norse mythology; two fail on read text, `Fensalir` being a location rather than a
  goddess and `Nanna (Norse deity)` being associated with the god Baldr; and four supply the
  required intermediate fact in full, `Eir` 1 / 41.790753, `Sága and Sökkvabekkr` 4 / 36.105730,
  `Gná and Hófvarpnir` 6 / 34.163892 and `Fulla` 10 / 26.421990. The exclusion for a looser
  interpretation than the gold does not fire, because the bridge gold's own claim is of the same
  kind: it states that Hlín has been theorized as possibly another name for Frigg, against Eir
  having been theorized as a form of the goddess Frigg. Two of the four sit inside the cutoff, so
  unlike D-025's boundary the substitute's position raises no question here. D-034 uses this
  finding to withhold `cutoff_sensitive_near_miss`, which is the ground D-015 used and the first
  time since D-015 that substitutability rather than the score gap decides that entry.
  D-025 records a second
  boundary of the same kind, on the position of the substitute rather than on its
  completeness: `History of England` at rank 6 of 4,937 names the queried tribe
  among the Belgic tribes `in the south east` and dates the Roman conquest to
  AD 43, so it supplies the answer hop's intermediate fact in full, yet it sits
  above that gold and still outside the cutoff, so adopting the descriptor changes
  no metric here. Whether a substitute outside the evaluated set should count is
  left to the vocabulary audit; nothing in the current include or exclude rule
  requires it to be inside. D-023 records a boundary rather
  than widening the rule: the adopted substitute supplies the required
  intermediate fact in full, naming the unnamed bridge film and linking it to the
  queried director, and the film it identifies is unique in the corpus, but it
  verifies only one of the question's two actor constraints. Whether that meets
  or fails the exclusion for a looser interpretation than the gold is left to the
  vocabulary audit.

## `low_context_name_query`

- **Status:** provisional.
- **Definition:** The query is short and dominated by proper names, providing
  little relational or topical context beyond the named entities.
- **Include when:** The query form itself visibly supplies few discriminating
  contextual cues and this limitation is recorded as an alternative
  explanation.
- **Exclude when:** It is asserted as the primary cause without a controlled
  comparison, ablation, or other direct evidence.
- **Affected units:** `5a76387d554299109176e6ba|dense`.
- **Decision source:** D-009.

## `description_only_bridge_entity`

- **Status:** provisional.
- **Definition:** A necessary bridge entity is identified in the question by
  roles, attributes, dates, or actions but is not named, leaving the query with
  no unique person-name or entity-name anchor for that entity (D-047).
- **Scope, recorded as provenance and not as a category:** as of D-047 this name
  is the primary of four units, all four on the bi-encoder, and a secondary of
  ten, seven lexical and three Dense. Pit 17 applies: retriever identity is not
  a category, and this line does not scope the descriptor to a backend.
- **Include when:** The question requires a specific entity, the entity's name
  is absent from the query, and the gold passage must be reached through a
  descriptive clue even if other lexical mismatches also contribute. A passing
  single-factor oracle-name test supports this name without establishing it,
  and is outranked by a non-oracle result under pit 15 (D-041). One form
  bringing both required passages inside the cutoff is a pass; a form is one
  surface form of a required passage's own entity name injected on its own, so a
  two-anchor condition and an injection of another entity's name are not forms
  of this test (D-046).
- **Exclude when:** The target entity is explicitly named, when the evidence
  supports only a generic relation failure without a concrete unnamed bridge,
  or when no single-factor oracle-name condition brings both required passages
  inside the cutoff, in which case this name may still be a secondary but not
  the unit's primary (D-041). That bar fires only where both preconditions have
  been verified and hold for every form counted as a failure - the injected
  anchor must be matchable by the passage it names (D-044), and the injected
  string must contribute something the question does not already contain, judged
  per injected form (D-045) - and only where at least one form of each required
  passage's own name has been run and every form run fails (D-046). An
  application failing either precondition is neither a pass nor a failure.
- **Boundary and routing, prospective (D-053):** This name carries the absent-name property
  only, and is not widened to a required entity the question names explicitly but
  ineffectively. A failure of one name's surface form under the implemented tokenizer routes
  to `surface_form_tokenization_mismatch`; a failure between two conventional names of the
  same entity routes to `entity_alias_reference_mismatch`; competition from a distinct entity
  sharing a name form routes to `proper_name_homonym_collision`; and an explanation resting on
  how a required passage's own text is composed routes to
  `peripheral_passage_content_dilution` only where that entry's four inclusion conditions have
  been satisfied. Where no route carries it, a named-but-ineffective anchor is recorded as a
  measured fact of that unit and no descriptor is coined for it.
- **Affected units:** `5a7d61775542991319bc93b9|bm25`,
  `5ac1a3665542994ab5c67daf|bm25`, `5ade42b55542992fa25da717|bm25`,
  `5ae057fd55429945ae959328|bm25`, `5ae0a59a55429945ae9593e2|dense`,
  `5a79b7f6554299029c4b5f6f|bm25`, `5a81ebee554299676cceb16d|dense`,
  `5ab48c325542996a3a969f93|dense`, `5adf58f15542993a75d264d2|bm25`, and
  `5adc8977554299438c868de2|bm25`.
- **Decision source:** D-012, D-021, D-022, D-024, D-025, D-028, D-029, D-030, D-031,
  D-033, D-034, D-035, D-036, D-038, D-039, D-041, D-044, D-045, D-046, D-047,
  and D-053.
  D-053 retains one descriptor for this name instead of splitting it, and adds no affected
  unit. The absent-name property stays the definition's subject: the name is not widened to
  cover a required entity the question names explicitly but ineffectively, which would set the
  definition against this entry's own first exclusion. Every landed observation of the
  unusable-anchor shape already has a disposition. D-029's corpus-unique name, which ranks its
  bearer 2202 of 4,937 when the query is reduced to it, sits inside an adopted secondary use of
  this descriptor; D-030's unmatchable possessive is carried by
  `surface_form_tokenization_mismatch` while this entry's first exclusion refuses the name;
  D-035's verbatim, near-unique description sits inside this descriptor's own primary use; and
  D-037 attributes its unusable anchor to that unit's adopted primary. The prospective boundary
  bullet above collects the routes, three of which restate clauses already carried by
  `entity_alias_reference_mismatch`. A future residual whose evidence is genuinely separable
  remains eligible for a name of its own.
  D-047 repairs this entry's definition, which named a backend, and adds no affected unit. The
  phrase `for lexical retrieval` is dropped: being unnamed in the question is a property of the
  question and the required passage and not of a scorer, and as written the definition excluded
  all four units on which this descriptor is the primary, every one of them Dense. A scope line
  records four bi-encoder primary uses and ten secondary uses, seven of them lexical, as
  provenance under pit 17. The inclusion rule and the exclusion clause are unchanged by this
  decision.
  D-046 writes down this test's form set and the coverage its bar requires, and adds no
  affected unit. A form is one surface form of a required passage's own entity name injected on
  its own; a two-anchor condition and an injection of another entity's name are not forms of
  it, which is how D-038 and D-033 were already read. The passing half stays existential and
  the failing half requires at least one form of each required passage's own name, all of them
  failing. Nine of the ten failing applications already meet that; D-033 is the exception, both
  of its counted forms anchoring the same required passage.
  D-045 makes the pit 24b degeneracy check the second condition on the same clause, on D-044's
  terms, and adds no affected unit. It is judged per injected form and not per unit, which is
  what D-038 already did in recording one clean side and one half degenerate one. D-030 remains
  the one unit where degeneracy decides the reading and is already carried as not applicable.
  D-044 conditions the failing-test bar on the pit 19g precondition and adds no affected unit.
  The bar D-041 wrote may fire only where the injected anchor has been verified matchable by
  the passage it names, for every form counted as a failure; where that has not been verified,
  or where it fails, the application is not applicable and is neither a pass nor a failure,
  which is the treatment the membership table already gives a degenerate injection. D-024 is
  the one unit where the precondition fails, its bare test reading 9 and 1 and the same
  condition reading 2 and 1 once boundary-punctuation normalization removes the artifact; its
  membership row stays as written under red line 4 and the rule applies from D-044 onward.
  D-041 writes the single-factor oracle-name test into this entry as two clauses of unequal
  force and adds no affected unit. A failing test now bars this name from primary use, which
  records an exceptionless regularity: across the ten failing applications, D-020, D-021,
  D-022, D-024, D-025, D-031, D-033, D-034, D-038 and D-039, this descriptor is the primary on
  none of them. A passing test supports without establishing, because four of the eight passing
  applications, D-028, D-029, D-036 and D-037, lost the primary to another name. The D-024 and
  D-030 preconditions remain usage notes, and a test whose precondition fails counts as neither
  a pass nor a failure. The definition's `for lexical retrieval` wording is not repaired here.
  D-039 records a non-adoption on `5ae60426554299546bf83019|bm25` and **the tenth failing
  application of the single-factor oracle-name test**. It is the first unit on which the
  inclusion rule had already failed before the test was run and the test was run anyway: the
  question names the distributor explicitly, so no required entity is identified by description
  alone, and the test is reported only because both of its premises are worth recording as
  checked. Pit 19g's premise holds, the injected `bravestarr` having corpus document frequency
  1 with term frequency 1 in the passage it names and 0 in the other, so the anchor reaches the
  passage it is meant to reach; pit 24b's holds too, the injected string being absent from the
  question rather than a surface variant of something already in it. The test fails on every
  form: appending the answer gold's title gives 1 / 25.773537 and 7 / 18.769969, appending the
  constraint gold's gives 19 / 17.987437 and 5 / 35.207124, and appending both gives 9 /
  25.773537 and 5 / 35.207124. The failure is not a missing anchor at all - each required
  passage is reachable from its own name, at 1 / 7.786100 and 4 / 16.437155 - but that each
  name drives the other side to the bottom of the corpus, which is the adopted primary.
  D-038 records a non-adoption on `5ae1801955429901ffe4aec4|dense` and the ninth failing
  application of the single-factor oracle-name test, and it is the first unit on which the
  test's degenerate premise, pit 24b, is met on one injected name and not on the other. The
  inclusion rule holds in the D-029 form, neither required entity being named and the bridge
  entity identified only by two coordinated descriptions. The test fails: appending the
  constraint passage's title gives 1 / 0.483498 and 97 / 0.244636 and appending the answer
  passage's title gives 556 / 0.151134 and 1 / 0.542954, neither double-recovering, while
  appending both gives 2 / 0.416027 and 1 / 0.464131. Pit 19g's premise is verified, each
  injected title ranking the passage it names first on its own at 1 / 0.699497 and 1 /
  0.704330. Pit 24b's premise is met on the answer side, no form of that name occurring
  anywhere in the question, and only half met on the constraint side, one word of that title
  already being in the question, so appending the title without its disambiguator gives 2 /
  0.391687 and 43 / 0.267094; the half-degenerate side is recorded rather than smoothed over.
  The descriptor is nevertheless refused on the D-028 route: the absence of a name is not the
  binding constraint on either side, the question's own verbatim sub-phrase reaching the
  constraint passage at 2 / 0.415715, a two-word phrase reaching the answer passage at 2 /
  0.404215, and an index-side change that leaves the query untouched word for word reaching the
  constraint passage at 1 / 0.452921. Passing or failing the oracle-name criterion does not
  settle this entry, by pit 15 and the ground D-036 reused.
  D-036 is the tenth affected unit and the second, after D-034, in which a blind non-oracle
  repair makes the description sufficient on one side. On `5adf58f15542993a75d264d2|bm25` the
  inclusion rule is met in the D-029 form, neither required entity being named: the bridge
  entity is identified only as an actor who also performed in "The Young Ones" and the answer
  entity only as a television series, and the question's only proper name is neither of them.
  The D-024 precondition was checked before the verdict was read and it fires in a new way:
  `ade` occurs in exactly 1 of 4,937 passages and that passage is the other required one, the
  bridge passage writing its own subject as `Adrian Charles "Ade" Edmondson`, so the bare full
  name gives 3 / 9.639104 and 2 / 9.908532 and the injected anchor is delivered to the wrong
  passage. The single-factor oracle-name test passes on the answer side, appending that title
  giving 1 / 24.736194 and 3 / 21.929780 and appending both giving 1 / 34.375297 and 2 /
  31.838312, while no non-oracle condition among the 101 measured runs places both inside the
  cutoff. The entry is nevertheless taken as a secondary and not as the primary, because on the
  bridge side the absence of a name is not the binding constraint: a query-side repair that
  adds no information and names nothing reaches that passage at 2 / 25.786297.
  D-035 adopts this name as the *primary* mechanism and is recorded in
  the note on primary use below rather than as a secondary affected unit. D-034 is the ninth
  affected unit and the eighth failing application of the
  single-factor oracle-name test, and it is the first unit in which the test fails, the
  descriptor is adopted as a secondary, and a blind non-oracle repair nevertheless makes the
  description sufficient on one side. On `5adc8977554299438c868de2|bm25` the inclusion rule is
  met in the D-029 form, neither required entity being named: the question's only proper noun is
  Frigg, who is neither of them, the bridge entity is identified only as the goddess associated
  with her, and the answer entity is not referred to at all. The D-024 precondition holds and was
  checked before the verdict was read, `hlín` occurring in exactly 1 of 4,937 passages, itself,
  and a query consisting of that name ranking it 1 / 14.707262 while the answer title ranks its
  own passage 1 / 22.413786. Every available form recovers one side only: appending the bridge
  title gives 1 / 48.090129 and 72 / 17.155303, appending the answer title 4 / 42.390581 and
  8 / 39.569089, appending both 1 / 57.097842 and 8 / 39.569089, and appending both on top of the
  normalized pipeline 1 / 64.843767 and 8 / 31.344743. D-034 supplies a boundary sample of a
  third kind for the question D-029 registered here, whether an absent anchor and an unusable one
  belong under one descriptor: here the anchor is absent on both sides, yet the descriptive clue
  alone reaches the bridge passage at 1 / 43.328448 once a blind two-sided boundary normalization
  is applied, so on that side the absence of a name is not the binding constraint. D-033 records
  a non-adoption, not an affected unit. It is the seventh failing
  application of the single-factor oracle-name test and the first in which the inclusion rule
  fails before that test is read. On `5abcc96c5542996583600492|bm25` the unnamed entity is the
  queried character's daughter, but the required passage does not have to be reached through the
  description: the question names her father, `mcgraw` occurs in exactly 2 of 4,937 passages at
  an idf of 7.587919, and the query `Earl McGraw` ranks that passage 1 / 16.915365, so the
  inclusion rule's requirement that the gold be reached through a descriptive clue is not met.
  The test was run anyway and fails on both available forms, appending the daughter's name giving
  4 / 33.947871 and 116 / 26.074919 and naming her in place while keeping the description giving
  4 / 34.429059 and 116 / 26.074919, each recovering one side only. The D-024 precondition holds,
  both required passages ranking 1 from their own titles. The D-030 degeneracy check is recorded
  rather than passed: `dakota` already occurs in the bridge passage's indexed body and in 10
  other passages, so the injected name partly repeats content that passage already carries.
  D-031 is the sixth failing application of the single-factor oracle-name test and its second
  failing application on a Dense unit, after D-025. On `5ab48c325542996a3a969f93|dense` the
  inclusion rule is met by the burial site: the question asks in which county the named king is
  buried and never states where he is buried, so the necessary bridge entity, Waltham Abbey, is
  identified only by the relation, and the answer passage can be reached only through that
  descriptive clue. The D-024 precondition was checked before the verdict was read and it
  holds: the bare `Waltham Abbey` ranks the passage it names 1 / 0.671588. The D-030 degeneracy
  check was also run and the injected string is not degenerate, `waltham` occurring nowhere in
  the question and in exactly 2 of 4,937 passages, which are the two required ones. Six surface
  forms nevertheless each recover only one side, appending the bridge title giving
  2 / 0.592542 and 10 / 0.341887, appending the answer title giving 13 / 0.369595 and
  1 / 0.619579, appending the bare bridge entity giving 11 / 0.383531 and 1 / 0.587664, naming
  it in place giving 11 / 0.379033 and 1 / 0.654515, naming it inside the relation clause
  giving 11 / 0.388953 and 1 / 0.587664, and using the formal name from the gold body giving
  27 / 0.330167 and 1 / 0.720498; only the two conditions injecting both names recover both, at
  3 / 0.557395 and 1 / 0.588495 and at 1 / 0.644947 and 2 / 0.640705. The descriptor is
  therefore retained as a secondary and closest competitor rather than as the primary. D-031
  also supplies a second boundary sample for the question D-029 registered here, whether an
  absent anchor and an unusable one belong under one descriptor, and it is of a third kind
  again: on the bridge side of this unit nothing is missing from the query at all, since the
  question names the king, the bridge passage writes `English king Harold Godwinson` verbatim,
  and that passage still ranks 18 / 4,937, so the descriptor simply does not reach that side.
  D-030
  records a non-adoption, not an affected unit, and it supplies the first empirical boundary
  sample for the question D-029 registered here, whether an anchor that is absent and an anchor
  that is present but unusable belong under one descriptor. On
  `5a83880e554299123d8c214e|bm25` the exclusion fires on its first clause, the target entity
  being explicitly named: the question says `Suicide's`, the corpus token `suicide` occurs in 12
  of 4,937 passages at an idf of 5.976452, both required passages carry it in their indexed
  bodies, and a query consisting of that one token ranks them 1 / 8.935662 and 3 / 6.855023. The
  anchor is therefore present, unique enough and sufficient on its own; it is unusable only
  because one surface form is not normalized, and a single blind query-side rule repairs it to
  2 / 21.521304 and 5 / 19.568085. D-030 assigns that shape to
  `surface_form_tokenization_mismatch`, which is a different disposition from the D-029 case,
  where the name was present in query and passage yet a query consisting of exactly that name
  still ranked the passage 2202 of 4,937 with no normalization able to change it. The two units
  together give the audit a lexical case where the anchor is repairable and a bi-encoder case
  where it is not. D-029 is the
  second unit in which the single-factor oracle-name test passes and the descriptor still
  loses the primary, after D-028, and the first in which it passes on a unit where neither
  required subject is named: the question names only the director, who has no passage of his
  own in the corpus, while the film is identified only as the movie he directed and the
  actress only as an Italian model and actress. Five forms recover both required passages,
  appending the film title giving 2 / 0.561980 and 1 / 0.668976, appending both titles giving
  1 / 0.754741 and 2 / 0.636003, appending the bare film name giving 2 / 0.522003 and
  1 / 0.595248, naming the film in place giving 2 / 0.481639 and 1 / 0.753787, and naming the
  actress in place giving 1 / 0.603500 and 4 / 0.428868; two fail, appending the actress name
  alone giving 1 / 0.607632 and 19 / 0.397304 and replacing the whole description with her
  name giving 1 / 0.668300 and 11 / 0.368824. The D-024 precondition was checked before the
  verdict was read and holds in the D-026 strong form: the bare `Matilda Lutz` ranks its own
  passage 1 / 0.633059, and the bare `Rings (2017 film)` ranks its own passage 1 / 0.791355
  **and also lifts the other required passage to 2**. It loses the tie-break on three measured
  grounds, extending D-021 and D-028. Its entire support is oracle. A non-oracle condition
  contradicts it on the bridge side, deleting the director clause alone moving the un-named
  bridge passage from 43 / 0.365309 to 5 / 0.466126, inside the cutoff, so the descriptive
  referent is sufficient there without any repair at all, which is a stronger form of the
  D-028 falsification, where one tokenizer artifact first had to be neutralized. And on the
  answer side the definition's phrase `no unique person-name or entity-name anchor`
  misdescribes what was measured, because the query does carry a name for that passage and
  that passage does contain it, uniquely in the 4,937-passage corpus, yet a query consisting
  of exactly that name ranks it 2202 / 0.057835 while the bare surname ranks it
  4243 / -0.047993. Whether the definition should distinguish an absent anchor from an
  unusable one is a vocabulary-audit question and is not settled here. D-028 is the first
  unit in which the single-factor oracle-name test **passes** and the descriptor still
  loses the primary, and its first pass on a BM25 unit, the fourth overall after D-017,
  D-023 and D-026. The unnamed entity is the restaurant chain the question identifies
  only as the quick service restaurant chain a named person helped found, and it is the
  subject of the answer passage, the structural shape D-026 first recorded. Five forms
  all recover both required passages: appending the chain name gives 2 / 41.634087 and
  1 / 47.659615, appending both titles gives 1 / 53.480099 and 2 / 47.659615, naming the
  entity in place gives 2 / 41.634087 and 1 / 47.659615, replacing the whole description
  with the name gives 4 / 9.043185 and 1 / 14.681712, and the same append under an
  index-side normalized index gives 2 / 49.694769 and 1 / 52.705685. The D-024
  precondition was checked before the verdict was read and it holds: the injected anchor
  is matchable by the passage it names, with `tim` and `hortons` both at term frequency 2
  there, and it is also matchable by the other gold, at 2 and 1, which is why one anchor
  lifts both sides as in D-026. It nevertheless loses the tie-break on two measured
  grounds, extending the D-021 precedent: its entire support is oracle, and a non-oracle
  condition contradicts it directly, since index-side boundary-punctuation normalization
  alone moves the un-named hop from 8 / 27.226538 to 3 / 32.295791, so the descriptive
  referent is sufficient once one tokenizer artifact is repaired and the absent name
  anchor is not the binding constraint. D-025 is the fifth
  failing application of the single-factor oracle-name test and the first failing
  one on a Dense unit, in a unit where this descriptor had been the provisional
  primary and where the unnamed bridge entity is the ruler the question describes
  only by ethnicity, role, date and region. Four surface forms of the bridge name
  were run and all four leave the other required passage outside the cutoff:
  appending the bare name gives 10 and 2, naming the entity in place gives 9 and 1,
  replacing the whole description with the name gives 8 and 1, and adding a
  date-role correction on top gives 8 and 1; the two reverse forms that name the
  other gold give 1 and 66 and 1 and 54. **The D-024 precondition was checked
  before the verdict was read and it holds:** reducing the query to the bare
  `Togodumnus` ranks the passage it names 1 at 0.703075 and reducing it to the bare
  `Catuvellauni` ranks its own passage 1 at 0.532805, so each anchor is matchable
  by the passage it is meant to reach and the failure is a real insufficiency of one
  anchor rather than an anchor delivered elsewhere. D-025 also records one
  observation that no earlier application had: deleting the entire descriptive
  referent clause improves **both** required passages, from 8 to 5 and from 115 to
  70, so in this unit the description is not merely a weak anchor but a net-negative
  one. D-024 applies the
  single-factor oracle-name test a fourth time in the failing direction, in a unit
  where the unnamed bridge entity is the company that the named person founded:
  appending the company name gives 9 and 1, appending the other gold's title gives
  21 and 1, substituting the name into the description gives 20 and 1, and
  appending both titles gives 13 and 1, so the descriptor is again retained as a
  secondary and closest competitor rather than as the primary. D-024 also records a
  **precondition on that test itself**, discovered in this unit and held here as a
  usage note only: the injected anchor must be matchable by the passage it names.
  There the answer passage tokenizes `General Mills, Inc.,` into `general` and
  `mills,`, so the injected bare `mills` awards 9.426700 points to the *other* gold
  and nothing to the passage it was meant to reach; once one boundary-punctuation
  normalization neutralizes that artifact the same oracle-name condition reaches 2
  and 1. Whether this precondition belongs in this descriptor's exclusion rule is a
  vocabulary-audit question and is not settled here. D-022 applies the same
  single-factor oracle-name test a third time: the described entity there is the
  single-factor oracle-name test a third time: the described entity there is the
  answer-bearing book series, and the oracle-name condition restores only the
  answer hop, so the descriptor is again retained as a secondary and closest
  competitor rather than as the primary. D-021 records that this descriptor's
  inclusion rule can be met while the descriptor still loses the primary
  tie-break; that precedent is held in the decision log and is not written into
  this definition, because primary-versus-secondary boundary rules are reserved
  for the vocabulary audit.
- **Note on primary use:** D-017, D-023, D-026 and D-035 adopt this name as the
  *primary* mechanism, for `5a85cead5542991dd0999ea9|dense`, `5ade69e455429975fa854ec5|dense`,
  `5ae1f596554299234fd04372|dense` and `5add67915542992200553af8|dense` respectively, which is
  why none of the four is listed above as a secondary affected unit. All four are Dense units,
  and in all four the single-factor oracle-name condition restores every required hop, which is the
  test D-020, D-021, D-022, D-024 and D-025 applied in the failing direction.
  D-026 is the third primary use and runs that test in seven surface forms, all
  of which recover both hops: appending either gold title gives 1 and 3 and 1 and
  2, appending both gives 1 and 2, naming the entity in place gives 1 and 2,
  replacing the description with the name gives 2 and 1, and substituting a bare
  partial name into the question gives 1 and 2 unrepaired and 1 and 3 repaired.
  Its D-024 precondition holds in a stronger form than in any earlier unit: each
  bare name ranks the passage it names 1, at 0.704012 and 0.714462, **and also
  lifts the other required passage to 2**, which is the opposite sign to D-025
  and is what excludes an antagonism reading there. D-026 also records a
  structural boundary that this definition does not currently address: in D-017
  and D-023 the unnamed described entity was a pure bridge entity, whereas in
  D-026 it is the subject of the answer passage itself and the bridge passage is
  what licenses the identification. The inclusion rule is met either way, since
  the question requires a specific entity, its name is absent from the query, and
  the gold can only be reached through the descriptive clue; whether the
  descriptor should distinguish the two shapes is a vocabulary-audit question and
  is not settled here. D-023 also
  records that this definition's phrase "for lexical retrieval" does not cover a
  bi-encoder, although the descriptor has now been adopted as the primary for two
  Dense units and was weighed as the closest competitor for a third in D-020.
  That wording is a vocabulary-audit question; this note records the usage
  and changes no definition, inclusion rule, or exclusion rule.
  D-035 is the fourth primary use and the fourth on a Dense unit, and it adds a form no earlier
  use recorded: **the descriptive substitute is present in the required passage verbatim, is
  near-unique in the corpus, and is still not discriminative.** On
  `5add67915542992200553af8|dense` the question carries no proper name at all, the organization
  being identified only as an Italian American Criminal Organization and the answer entity only
  as the hitman it hired. The bridge passage's indexed body contains `is an Italian American
  criminal organization` word for word and exactly 2 of 4,937 passages contain that string,
  that passage and `Los Angeles crime family` at 10 / 0.416292; reduced to that description
  alone the query ranks it 1 / 0.541525, while inside the full question it ranks 7 / 0.438223
  against a rank-5 score of 0.476272, the answer passage sitting at 12 / 0.406772. The
  description is also a net liability for the other required passage: deleting its demonym
  compound moves the answer passage to 5 / 0.371287 while moving the bridge passage to 15 /
  0.314556, and deleting the description entirely moves the bridge passage to 1650 / 0.087429
  and leaves the answer passage at 12 / 0.313102. The single-factor oracle-name test is the
  twelfth application and the sixth pass, recovering both hops in five forms: appending the
  bridge title gives 1 / 0.656474 and 3 / 0.516396, appending both titles 2 / 0.613032 and 1 /
  0.634903, adding `in Philadelphia` 1 / 0.551362 and 2 / 0.503404, appending the answer string
  2 / 0.600663 and 1 / 0.676290, and replacing the description with `the Philadelphia Mob` 2 /
  0.520939 and 1 / 0.561518. The D-024 precondition holds in the D-026 form, the bridge title
  alone ranking its own passage 1 / 0.706333 **and lifting the other required passage to 5 /
  0.440004**, and the answer title alone ranking its own passage 1 / 0.545298; the D-030
  degeneracy check of pit 24b is passed rather than merely recorded, the gain being carried by
  a token absent from the question, `Philadelphia` alone giving 1 / 0.554958 and 2 / 0.499144
  where `crime family` alone gives 1 / 0.564744 and 14 / 0.425469 and `Pennsylvania` gives 1 /
  0.488966 and 10 / 0.406492. What carries the primary is a partition of the condition set: of
  the labelled query conditions that keep the referring expression verbatim, every one that
  recovers both hops is an oracle injection and none is non-oracle, while the seven non-oracle
  conditions that do recover both all replace that expression and not one keeps the demonym
  `Italian`, the constraint-preserving variant that changes only the head noun giving 3 / 13
  and failing. This is the D-028 refutation path sliced by whether a condition leaves the
  referring expression intact, which is what distinguishes this unit from D-028, where the
  refuting condition was index-side and left the query untouched. D-035 also records that a
  16-cell non-oracle factorial on that expression locates two defects binding on different
  required passages: changing only the head noun gives 3 / 13, deleting only the demonym gives
  15 / 5, and both together give 1 / 0.585624 and 4 / 0.510640.

## `near_duplicate_event_confusion`

- **Status:** provisional.
- **Definition:** A retrieved passage describes a distinct historical event
  sharing the intended event's place, event type, name form, or action
  vocabulary and competes with or outranks the annotated event.
- **Include when:** The distractor can be shown to concern a different event,
  such as a different date, participants, or outcome, while retaining multiple
  distinctive event cues from the question.
- **Exclude when:** The passage is merely from the same historical domain, or
  when no concrete event substitution is present.
- **Affected units:** `5a7d61775542991319bc93b9|bm25`.
- **Decision source:** D-012.

## `repeated_content_word_amplification`

- **Status:** provisional.
- **Definition:** A content-bearing query token occurs more than once and the
  retriever scores every occurrence, materially amplifying passages that
  repeat that content term whether or not they satisfy the required relation.
- **Include when:** The actual tokenizer and scoring implementation are known,
  the repeated content token is verified in the query, and exact score
  decomposition or a controlled ablation shows a material ranking effect.
- **Exclude when:** The repeated token is a function word, the implementation
  deduplicates query terms, or its measured contribution is negligible.
- **Affected units:** `5a7c9f325542990527d554e6|bm25` and
  `5ade42b55542992fa25da717|bm25`.
- **Decision source:** D-014 and D-022.

## `repeated_function_word_amplification`

- **Status:** provisional.
- **Definition:** Unfiltered function words occurring repeatedly in a query
  are scored once per occurrence and collectively give large score gains to
  passages that repeat those words but lack the required relation.
- **Include when:** The actual tokenizer and scoring implementation are known,
  repeated query function words are verified, and score decomposition shows a
  material contribution to distractor ranking.
- **Exclude when:** Stop-word influence is inferred only from visible text, the
  implementation deduplicates or removes the terms, or their measured score
  contribution is negligible.
- **Affected units:** `5a7d61775542991319bc93b9|bm25`,
  `5a83a532554299334474606f|bm25`, `5ade42b55542992fa25da717|bm25`, and
  `5adc8977554299438c868de2|bm25`.
- **Decision source:** D-012, D-016, D-022, D-033, and D-034. D-034 is the fourth affected unit
  and the first adoption decided by the same direct experiment D-033 used to withhold the
  descriptor, run here with the opposite outcome. On `5adc8977554299438c868de2|bm25` the
  inclusion rule is met: the query repeats `what` and `the`, and `Treehouse (game)` at
  9 / 27.610510, a board-game description with no content relation to the question, takes
  100.0 percent of its score from scaffold, 33.0 percent of that from the second occurrences
  alone against 34.0 percent from the non-repeated tokens. Deleting only the second occurrence
  of each repeated token gives 7 / 29.473219 and 37 / 13.077942, worth 0 rank positions on one
  required passage and 35 on the other, while deleting the three non-repeated scaffold tokens
  instead gives 6 / 32.670088 and 77 / 13.077942, worth 1 and minus 5. Both halves remove the
  identical 4.077360 points from the answer passage, `the` and `of` sharing an idf of 1.917315,
  so the whole difference is what happens to the competitors and the repeated occurrences are
  the material mechanism. The sibling entry's second exclusion therefore fires and
  `generic_query_scaffold_score_inflation` is withheld here; D-033 ran the identical experiment
  and that exclusion did not fire, so the two units are the boundary samples that pair needs.
  D-033 records a non-adoption, not an
  affected unit, and it is the first occasion on which the boundary between this entry and
  `generic_query_scaffold_score_inflation` is settled by a direct experiment rather than by
  inspection. On `5abcc96c5542996583600492|bm25` the inclusion rule is met: the query's only
  repeated token, `the`, occurs three times and supplies between 24.3 and 40.7 percent of the
  scores of the ten passages above the cutoff, 12.475634 of the 30.681984 held by
  `Penny (The Big Bang Theory)` at rank 9, a passage containing neither queried entity. It is
  withheld because the repeated occurrences are not the material half: deleting the second and
  third occurrences alone gives 18 / 21.800059 and 118 / 18.393906, worth 8 rank positions on one
  required passage and minus 3 on the other, while deleting the four non-repeated scaffold tokens
  instead gives 17 / 21.284848 and 77 / 18.415555, worth 9 and 38. Both required passages are
  themselves large beneficiaries of the same token, taking 36.5 and 44.2 percent of their own
  scores from it. The choice between the two entries is exactly the one the sibling entry's
  second exclusion names, and the measurement assigns this unit to that entry; this descriptor is
  therefore withheld rather than excluded and no rule changes.

## `surface_form_tokenization_mismatch`

- **Status:** provisional.
- **Definition:** A minimal tokenizer treats punctuation-bearing or
  morphologically related surface forms as different tokens, preventing
  conceptually corresponding query and gold-passage words from matching.
- **Include when:** Exact query and gold tokens can be compared under the known
  tokenizer, with concrete mismatches such as `bharatpur,`/`bharatpur`,
  `commander-in-chief`/`commander-in-chief,`, or `storming`/`stormed`. A
  difference in Unicode punctuation character, not only in the presence of
  punctuation, is within this definition; D-021 adds the worked example
  `1990-2001?` against `1990–2001.`, where the query uses a hyphen-minus plus
  question mark and the passage uses U+2013 plus a period. This is recorded as
  an added illustration of the existing definition, not as a widening of it.
- **Exclude when:** The forms are identical after the implemented tokenizer,
  or when a missing entity name rather than surface form accounts for the
  failure.
- **Affected units:** `5a7d61775542991319bc93b9|bm25`,
  `5a7c9f325542990527d554e6|bm25`,
  `5a83a532554299334474606f|bm25`,
  `5ab72a025542992aa3b8c7b8|bm25`,
  `5ac1a3665542994ab5c67daf|bm25`, `5ade42b55542992fa25da717|bm25`,
  `5a79b7f6554299029c4b5f6f|bm25`, `5a83880e554299123d8c214e|bm25`, and
  `5abcc96c5542996583600492|bm25`, `5adc8977554299438c868de2|bm25`,
  `5adf58f15542993a75d264d2|bm25`, and `5ae60426554299546bf83019|bm25`.
- **Decision source:** D-012, D-014, D-016, D-019, D-021, D-022, D-028, D-030, D-032,
  D-033, D-034, D-036, and D-039.
  D-039 adopts this descriptor on `5ae60426554299546bf83019|bm25` for the constraint gold's own
  indexed body, which writes `(also known as simply "Celebrity Video")`. Under the implemented
  `text.lower().split()` the form `"Celebrity` is a different token from `celebrity`, so that
  passage's raw term frequency for the query's highest-idf token is 1 where boundary stripping
  makes it 2. Pit 19ae's pair of cells is run and the deployable version does not discount:
  stripping quotes in that passage alone gives 8 / 17.987437 and 2 / 21.350963, worth 2.580995
  points and 4 rank positions against a null control whose residual over all 4,937 rows is
  0.000e+00, and stripping quotes across the 2,387 passages they occur in gives 8 / 17.888265
  and 2 / 21.158602, worth 2.388634 points and the same 4 rank positions, with the corpus
  document frequency of `celebrity` moving from 11 to 12. This is the second unit after D-034
  at which that deployable cell costs nothing in rank. The answer hop carries a mismatch of its
  own, its body writing `animated series.` so that its raw term frequency for `series` is 2
  where stripping makes it 3, but there the gold-targeted repair is worth 0.628238 points and
  **0 rank positions** and the deployable one is worth **-0.024046 points**, the same repair
  giving more to its competitors than to it; that is the first recorded case in which the
  deployable version of a surface repair reverses the sign, and it is why
  `minimal_preprocessing_score_distortion` was refused the primary on this unit.
  D-036 is the eleventh affected unit and the first in which one of the two worked pairs falls
  inside a required passage's own subject name. On `5adf58f15542993a75d264d2|bm25` the
  query-side pair is `ones"?` against `ones"`: the query form occurs in 0 of 4,937 passages and
  contributes exactly 0.000000, deleting it leaving the 4,937-passage order 0 of 4937 changed
  at a maximum absolute score difference of 0.000000, while the bare corpus form occurs in 5
  passages at an idf of 6.798853 and stands in the bridge passage's indexed body. Normalizing
  that one character and nothing else moves it from 6 / 19.630966 to 2 / 25.786297, so the
  question mark is priced at 6.155330248 points and 4 rank positions, exactly the score a query
  consisting of the single token `ones"` gives it, 5 / 6.155330248, the two agreeing to
  8.882e-16. This is the eighth instance of a query token absent from the corpus contributing
  exactly 0.000000, after D-019, D-021, D-028, D-030, D-032, D-033 and D-034. The document-side
  pair falls inside the bridge passage's own name, which writes
  `Adrian Charles "Ade" Edmondson`, so `ade` has tf 0 there and tf 1 in the other required
  passage, and a query of that single token gives 2202 / 0.000000 and 1 / 9.908532. D-036 also
  records that a wider normalization can be worse than the exact one: the double quotes alone
  give 11 / 20.256894 on the query side against the question mark's 2 / 25.786297, because
  stripping boundary punctuation drops df(`ones"`) from 5 to 0 and raises df(`ones`) from 10 to
  24 at an idf of 5.301069.
  D-034 is the tenth affected unit and the second, after D-033, in which the
  mismatch on one required passage is on the query side while the mismatch on the other is on
  the document side; unlike D-033 the two sides bear on different words rather than on two
  surface forms of one name. On `5adc8977554299438c868de2|bm25` two worked pairs hold. The
  query's `tales?` occurs in 0 of 4,937 passages and contributes exactly 0.000000, the seventh
  such instance after D-019, D-021, D-028, D-030, D-032 and D-033, while the bare corpus form
  occurs in 9 passages and stands in the answer passage's indexed body; normalizing that one
  token and nothing else moves it from 72 / 17.155303 to 15 / 24.166533, so the question mark
  is priced at 7.011230 points and 57 rank positions, exactly the score a query consisting of
  the single token `tales` gives it, 4 / 7.011230, the two agreeing to the last digit. Deleting
  it instead leaves the 4,937-passage order 0 of 4937 changed at a maximum absolute score
  difference of 0.000000. The second pair is on the document side and falls on the other
  required passage: the bridge passage writes the question's only proper noun only as `Frigg.`,
  twice, so the query's bare `frigg`, at an idf of 6.631596 in 6 passages, scores 0.000000
  against it while four of the six passages above it take 4.748132, 6.141557, 6.660782 and
  6.795970 from that same token; stripping those two periods inside that passage alone moves it
  from 7 / 33.382868 to 1 / 43.747308, worth 10.364441 points and 6 rank positions, matching to
  6e-06 the score a single-token query `frigg` gives it on the repaired index, and repairing
  only the first gives 2 / 40.997962. D-034 adds one illustration and no widening, and it is
  the counter-sample to D-033 on the deployable form: the same repair applied corpus-wide
  touches only 2 passages and gives 1 / 43.747301, so where D-033 lost nine rank positions
  between the gold-targeted and deployable versions this unit loses none, because the
  unnormalized form is nearly unique to the required passage.
  D-033 is the ninth affected unit and the first in which the mismatch on one required
  passage is on the query side while the mismatch on the other is on the document side. On
  `5abcc96c5542996583600492|bm25` three worked pairs hold. The query's `mcgraw's` occurs in 0 of
  4,937 passages and contributes exactly 0.000000, the sixth such instance after D-019, D-021,
  D-028, D-030 and D-032, while the bare corpus form occurs in exactly 2 passages at an idf of
  7.587919 and stands in the required passage's own title and indexed body; normalizing that one
  token and nothing else moves it from 26 / 28.798100 to 2 / 37.789878, so the clitic is priced at
  8.991778 points and 24 rank positions, exactly the score a query consisting of the single token
  `mcgraw` gives it, 2 / 8.991778. The query's `daughter?` likewise occurs in 0 passages against
  52 for `daughter` at an idf of 4.533214, and its repair is worth 3.520270 points and 21 rank
  positions, again exactly the single-token query's score, 48 / 3.520270; the two repairs are
  additive at 1 / 41.310149. Deleting either token leaves the 4,937-passage order 0 of 4937
  changed at a maximum absolute score difference of 0.000000. The third pair is on the document
  side and is new for this entry: the answer passage writes `Rose McGowan,` so the query's bare
  `mcgowan` scores 0.000000 against it, the corpus splitting that name into 5 bare, 7
  comma-suffixed, 2 parenthesis-suffixed and 1 period-suffixed occurrences, and stripping that one
  comma inside that passage alone moves it from 115 / 26.074919 to 5 / 32.133137, worth 6.058218
  points and 110 rank positions. D-033 adds one illustration and no widening: the deployable form
  of a document-side repair is worth far less than its gold-targeted form, the same comma repair
  applied to every passage carrying it giving 11 / 31.534653 and a query-aware normalization
  giving 14 / 31.630834, because the fourteen other passages naming the same actress receive the
  identical repair. D-030's pit 25i boundary fires for the second time, the normalization ladder
  reporting `no corresponding form` for `mcgraw's` because the apostrophe is word-internal, while
  the corpus form stands in that passage's own title and body. D-032
  records a non-adoption, not an affected unit, and supplies the counter-sample to D-030's
  dead-token finding. On `5ab8f57b5542991b5579f097|bm25` the query's final token `nationality?`
  occurs in 0 corpus passages and contributes exactly 0.000000, the fifth such instance after
  D-019, D-021, D-028 and D-030, and deleting it leaves the 4,937-passage order 0 of 4937 changed
  with a maximum absolute score difference of 0.000000. Unlike D-030, where normalizing the
  equivalent token was worth 64 rank positions, **the repair is worth nothing here**: the corpus
  form `nationality` occurs in 7 passages but in neither required passage, so normalizing the token
  leaves them at 6 / 26.870093 and 11 / 19.741610, unchanged. The pair therefore exists and its
  measured contribution is negligible, which is this entry's third exclusion, and the descriptor is
  withheld under the D-018 materiality standard. D-032 also records that the unit's real name-form
  difference, the query's `h.` against the indexed body's `Harper`, lies **outside** this
  definition: it is an initial against an expanded middle name rather than a punctuation-bearing or
  morphologically related surface form, and this entry's second exclusion routes a missing entity
  name elsewhere. The two-sided boundary-punctuation condition is negative on both required
  passages there, at 8 / 26.567864 and 16 / 18.889345. D-030 adds
  the possessive clitic as a worked form of this definition and is the first unit in which the
  mismatched token is the question's only entity name. The question writes the band as
  `Suicide's`, a token occurring in 0 of 4,937 passages, while both required passages write the
  indexed body forms `band Suicide appearing` and `band Suicide.` and the corpus token
  `suicide` occurs in 12 passages at an idf of 5.976452. Normalizing that one query token and
  nothing else moves the two required passages from 66 / 12.585642 and 61 / 12.713062 to
  2 / 21.521304 and 5 / 19.568085, so the clitic is priced at 8.935662 points and 64 rank
  positions on the answer hop and 6.855023 points and 56 on the bridge hop; those two increments
  are exactly the scores the passages receive from a query consisting of the single token
  `suicide`, under which they rank 1 and 3. The pair is recorded as an added illustration within
  the existing definition, which already covers punctuation-bearing and morphologically related
  surface forms, and not as a widening. D-030 records one boundary of a different kind: the
  P, E, Q, U, M normalization ladder used by the project's evidence collector cannot align this
  pair, because the apostrophe is word-internal so boundary stripping does not reach it and the
  crude stem yields `suicide'`, so the ladder reports `no corresponding form` for a token whose
  corpus form stands in both required passages. Three further pairs from the same unit are
  within the existing coverage, the query's `character?` against the body's `character.`, its
  `comic` against `Comics` and its `features` against `featured`, the last two worth
  5 / 18.508871 and 14 / 15.650092 when a crude stem is applied. D-030 also records that
  `character?` occurs in 0 corpus passages and contributes exactly 0.000000 to every one of
  them, the fourth instance after D-019, D-021 and D-028. D-028 adds
  three worked pairs from one unit, two of them on the required passages' own decisive
  tokens: the query's `ron` against the body form `Ronald Vaughan "Ron" Joyce`, whose
  nickname tokenizes as `"ron"`, and the query's `chain` against `restaurant chain;`,
  whose token is `chain;`. Single-token gold-targeted repairs price them at 8.247890
  points and ten rank positions and at 5.481747 points and six. The third pair is
  derivational rather than punctuational, the query's `helped found` against the gold's
  `co-founded`, worth 6.960967 points and eight rank positions, which is within the
  existing definition's coverage of morphologically related surface forms and is recorded
  as an added illustration rather than a widening. D-028 also records that the query's
  final token `found?` occurs in 0 corpus passages against 75 for `found`, so it
  contributes exactly 0.000000 to every passage, the third instance after D-019 and
  D-021. D-022 adds
  the worked pair `novels` against a passage that uses only the singular `novel`,
  alongside `series` against `series.` and `series"`. Like D-021's illustration,
  this is recorded as an added example within the existing definition, which
  already covers morphologically related surface forms, and not as a widening.

## `related_name_document_crowding`

- **Status:** provisional.
- **Definition:** Relatives, works, institutions, or associates whose own text
  carries one queried entity's name, or a token of that name, occupy high ranks
  ahead of the required evidence (D-048).
- **Scope, recorded as provenance and not as a category:** on both bi-encoder
  adoptions every competitor carries the whole name verbatim, so the token half
  of the disjunction has never carried an adoption on that backend (D-048).
- **Include when:** The retrieved passages contain concrete name-linked
  documents and their relationship to the queried entity is visible in the
  passage text.
- **Exclude when:** A more specific implementation-supported name-form mismatch
  explains the primary failure; in that situation use this only as a downstream
  ranking description.
- **Affected units:** `5a78b209554299148911f93e|bm25`,
  `5a78b209554299148911f93e|dense`, `5ab48c325542996a3a969f93|dense`,
  `5ab8f57b5542991b5579f097|bm25`, `5abcc96c5542996583600492|bm25`, and
  `5ae60426554299546bf83019|bm25`.
- **Decision source:** D-010, D-027, D-029, D-031, D-032, D-033, D-034, D-039,
  and D-048.
  D-048 restates this entry's definition so that `sharing a name or name token` plainly
  describes the competing passage's own text rather than a matching mechanism, and adds no
  affected unit. The substance, the inclusion rule and the exclusion clause are unchanged. It
  is a smaller repair than D-047's and for a different reason: that wording named the retrieval
  mechanism and so excluded its own primary uses, while this one names a property of text that
  held literally on both bi-encoder adoptions, all six of D-027's competitors containing
  `Albee` in their bodies and all eight of D-031's containing `Harold Godwinson`. This
  descriptor is the primary of no unit, so no primary use turns on the wording.
  D-039 is the sixth unit for this descriptor and its third adoption on a lexical retriever. On
  `5ae60426554299546bf83019|bm25` the include rule is met on read text by five non-gold
  passages above the answer hop that name the queried distributor, each stating its own
  relationship to it in its own text: `COPS (animated TV series)` 1 / 24.991204 as a series it
  released, `Sterling Entertainment Group` 2 / 20.383253 as a competitor, `Noel C. Bloom` 3 /
  20.201011 as its founder, and `Locke the Superman` 4 / 19.831276 and `Tottoi` 5 / 18.906282
  as titles it released. Pit 19ad's three controls separate the family from the collection
  statistics more cleanly than at D-032: removing the family gives 3 / 18.007533 and 1 /
  19.544516, removing its complement, the single passage `Pergament Home Centers` 7 /
  18.620405, gives 7 / 18.013998 and 6 / 18.775924, a size-matched null removal gives 8 /
  18.069800 and 6 / 18.771378, and the statistics-matched control gives 3 / 17.987437 and 1 /
  18.769969, both scores bit for bit the baseline, so the family's whole effect is positional.
  Pits 19af and 19ag are satisfied and the two states agree, the family removal giving 3 /
  18.121392 and 1 / 25.293159 under the adopted normalization and the delete-everything-above
  cell giving 2 / 18.034096 and 1 / 19.550617 at baseline and 3 / 18.119172 and 1 / 25.043955
  under it. It is held at secondary on three grounds. Pits 19f and 19i agree in sign, so the
  family is the product of the question's own required naming: the distributor name alone
  reproduces 7 of the baseline top ten and 5 of 5 of the family and `celebrity` alone 6 and 5
  of 5, while the genre facet alone reproduces 1 and 0 of 5; deleting the distributor name from
  the question collapses the neighbourhood to 2 and 0 of 5 while deleting the genre facet
  leaves it at 8 and 5 of 5. The family and the required evidence are the same lexical class: a
  rule stated from the question alone selects six passages, one of which is the required
  constraint gold, and applying it gives 2 / 18.006690 with that gold gone from the index, so
  the descriptor names a set that cannot be separated from the evidence by any query-definable
  rule. And D-024 is the same shape on the same backend and settled the same way. Whether a
  crowding descriptor whose query-only definition contains a required gold should be excluded
  from primary use by rule is registered as an audit question.
  D-034 records a
  non-adoption, not an affected unit, and it is the first refusal of this descriptor on the pit
  19f and 19i test rather than on materiality or on the exclusion. On
  `5adc8977554299438c868de2|bm25` the surface shape fits: five of the six passages above the
  bridge passage contain the queried name Frigg and each states its own relationship to her in
  its own text. It is not adopted because the family is not name-driven. Deleting `frigg` from
  the question leaves the neighbourhood untouched, its top ten still placing 5, 6, 8 and 10
  inside the baseline top 5, 6, 10 and 16, while deleting both occurrences of the category token
  `goddess` collapses it to 0, 0, 1 and 5; forward, `frigg` alone places only 3, 4, 6 and 6 where
  `goddess` alone places 5, 6, 8 and 10. The observed family therefore belongs to the question's
  category vocabulary and is recorded under `generic_term_lexical_crowding`. A second observation
  points the same way: the query token `frigg` is a net liability at baseline, deleting it moving
  the bridge passage from 7 to 4, because the passage that should own the name writes it in a
  form the implemented tokenizer does not match.
  D-033 is the fifth unit for
  this descriptor, its second on a lexical retriever, and the first in which the entry's own first
  exclusion **does** fire and the descriptor is adopted anyway, because that exclusion's wording
  routes such a case to a downstream ranking description rather than out of the unit. On
  `5abcc96c5542996583600492|bm25` the more specific implementation-supported name-form mismatch
  exists and is priced, the answer passage's indexed `Rose McGowan,` costing it 6.058218 points and
  110 rank positions, so the exclusion applies and this name is used as the downstream description
  of what fills the ranking. The include rule is met on read text by fourteen non-gold passages
  naming the queried actress, of which `The Pastor's Wife (film)` 1 / 38.767942,
  `Conan the Barbarian (2011 film)` 2 / 37.614397 and `Paige Matthews` 3 / 36.229941 occupy three
  of the five cutoff positions, each stating its own relationship to her in its text as a film she
  stars in or a television character she played. D-033 is also the first unit in which this
  family's determinativeness depends on which baseline the probe is run against, which is recorded
  as a new pit rather than as a rule change. At baseline the family is not determinative and loses
  to its own complement: dropping the 18 passages above the answer passage that name her gives
  15 / 28.805372 and 73 / 26.630444, while dropping the other 95 gives 10 / 29.270483 and
  30 / 26.124391, with a statistics-matched control at 27 / 28.779802 and 90 / 26.622223 and a
  size-matched null control at 26 / 28.809076 and 115 / 26.068632. Under a fully normalized
  pipeline the same family is determinative: dropping the 14 non-gold passages naming her, a set
  definable from the query alone, gives 1 / 25.266887 and 3 / 15.335047, dropping all 41 passages
  naming her or carrying `rose` gives 1 / 25.246782 and 2 / 18.024994, the size-matched null
  control gives 1 / 25.981076 and 12 / 12.825312, and the cumulative ladder crosses the cutoff at
  the eighth removal at 1 / 25.273160 and 5 / 13.543318; ten of the 12 passages above the answer
  passage under that pipeline carry the name. Whether an include rule should be evaluated at
  baseline or after the adopted primary's repair is a vocabulary-audit question.
  D-032 is the fourth unit for this
  descriptor, its first adoption on a lexical retriever, and the first occasion on which its own
  first exclusion is tested on a lexical backend and does **not** fire. On
  `5ab8f57b5542991b5579f097|bm25` the include rule is met by seven competitors read in full, every
  one of which states its relationship to the queried entity in its own text: `Ralph Ince`
  1 / 35.196426 a brother, `Elinor Kershaw` 2 / 31.324236 the wife, `The Scourge of the Desert`
  3 / 31.178677 a film he produced, `John Ince (actor)` 4 / 30.381922 the eldest brother,
  `The Coward (1915 film)` 5 / 28.423217 a film he produced, `The Deserter (1912 film)`
  7 / 25.088913 a film he wrote and directed, and
  `Thomas Ince: Hollywood's Independent Pioneer` 8 / 21.675798 a biography of him. They occupy all
  five ranks above the nearer required passage and seven of the nine above the other, so they fill
  the entire cutoff region, and the other queried candidate has no competitors at all. Unlike
  D-010, which demoted `one_sided_entity_crowding` on this very clause because a name-form mismatch
  was more specific, the exclusion is checked and rejected on measurement here: a name-form
  mismatch exists and is exact, the query token `h.` contributing 0.000000 to the required passage
  whose body writes `Thomas Harper Ince` while eight of the nine passages above it take 4.461297 to
  7.814359 from it, but repairing that mismatch does not explain the failure. Rewriting the
  required body to the query's own name form gives 7 / 26.870096 and 6 / 27.091980, prefixing that
  passage's own title gives 7 / 26.870134 and 4 / 30.556564 and indexing all titles gives
  3 / 31.744369 and 6 / 30.547523, so every form of the repair leaves the pair outside the cutoff
  and two of them displace the other required passage. Unlike D-031, which kept the descriptor
  secondary because the family was not outcome-determinative, here it is: dropping the seven gives
  1 / 26.868145 and 2 / 22.167723 while dropping their two-passage complement gives 6 / 26.911596
  and 9 / 19.763251, the cumulative ladder crosses the cutoff at the fourth removal at
  2 / 26.869286 and 5 / 21.307440, a size-matched null control gives 6 / 26.861098 and
  11 / 19.734995 and a statistics-matched control gives 6 / 26.905808 and 11 / 19.829852. The
  descriptor is nevertheless kept secondary and `one_sided_entity_crowding` preferred, for the
  reason D-027 gave: this name says what the competitors are but cannot account for the other
  required passage, which has no name link to any of them and ranks 1 under five non-oracle
  single-sided queries. Whether the operational meaning of `explains the primary failure` in the
  first exclusion should be written as the test used here, a gold-targeted repair of the name form
  that still leaves the passage outside the cutoff, is a vocabulary-audit question.
  D-031 is the third unit for this
  descriptor, its second use on a bi-encoder and its first on a bridge question. On
  `5ab48c325542996a3a969f93|dense` the include rule is met by eight competitors read in full,
  every one of which contains the string `Harold Godwinson` and states its own relationship to
  the queried king in its own text: `Tostig Godwinson` 1 / 0.612422 a brother,
  `Leofwine Godwinson` 2 / 0.609307 a brother, `Godwin, Earl of Wessex` 3 / 0.564319 the
  father, `Battle of Stamford Bridge` 4 / 0.489070 his battle,
  `Cultural depictions of Harold Godwinson` 5 / 0.488627, `Gytha Thorkelsdottir` 6 / 0.451451
  the mother, `The Last English King` 7 / 0.442921 a novel about him, and `Edith the Fair`
  9 / 0.373248 the wife. They occupy ranks 1 to 7 and 9 and therefore fill the entire cutoff
  region. As in D-027 the exclusion does not fire on a bi-encoder, there being no name-form
  mismatch to prefer and the title-indexing condition being inert-to-negative at
  27 / 0.314097 and 24 / 0.323271. D-031 keeps the descriptor secondary on measurement rather
  than on the exclusion: an index-side removal of all eight moves the two required passages
  only from 18 / 0.342168 and 21 / 0.339314 to 10 / 0.342168 and 13 / 0.339314, an index-side
  removal of all eight non-gold passages naming the king corpus-wide gives the same, and the
  complement control that instead drops the eleven remaining passages above the answer hop
  gives 9 / 0.342168 and 10 / 0.339314, so neither family is outcome-determinative and
  seventeen of the nineteen must be dropped before both required passages enter the cutoff.
  Unlike D-029, which withheld the descriptor because a single name-sharing passage moved the
  required evidence by exactly one position, the D-018 materiality standard is met here in the
  weaker sense that the family moves both required passages by eight positions each; what it
  does not do is determine the outcome. D-029 records the first non-adoption of
  this descriptor on materiality rather than on the exclusion rule. On
  `5a81ebee554299676cceb16d|dense` the provisional secondary `surname_entity_confusion` would
  have mapped here or to `proper_name_homonym_collision`, and one competitor does share the
  queried surname, `Janine Gutierrez` at 4 / 0.468290, whose text names her as an actress,
  television host and commercial model and so matches the descriptive referent as well. But a
  full-corpus scan finds exactly one non-gold passage containing the surname, and an
  index-side removal of it, or of every non-gold passage containing the surname, moves each
  required passage by exactly one position, from 43 / 0.365309 and 94 / 0.332391 to
  42 / 0.365309 and 93 / 0.332391. The include rule's requirement that name-linked documents
  occupy high ranks ahead of the required evidence is met only in the trivial sense of one
  document, and the D-018 materiality standard fails, so the descriptor is not adopted and the
  provisional name is deleted rather than registered. D-027 adopts the descriptor for the Dense unit
  of the same `example_id`, which is the first Dense use of this name, and records two
  things without changing any rule. First, the exclusion does not fire on a bi-encoder:
  there is no name-form mismatch to prefer, since that backend performs no tokenization
  or literal matching and the title-indexing condition is inert at 9 / 8. The include
  rule is met by six competitors read in full, `Reed A. Albee` 1 / 0.630886 the adoptive
  father, `Finding the Sun` 2 / 0.597466, `Edward F. Albee Foundation` 3 / 0.567801,
  `Edward Albee's At Home at the Zoo` 4 / 0.542102, `The Zoo Story` 5 / 0.538556 and
  `Three Tall Women` 6 / 0.519974, each stating its relationship to the queried entity in
  its own text, and a cumulative index-side removal of them recovers both required
  passages once four are dropped, at 5 / 4. Second, a boundary is registered rather than
  closed: this definition's wording, `sharing a name or name token`, is lexical, and all
  six competitors do literally contain `Albee`, so the surface fact holds, but whether
  the definition needs rewording for a bi-encoder is a vocabulary-audit question of the
  same kind already open for `description_only_bridge_entity`. D-027 keeps the descriptor
  secondary and prefers `one_sided_entity_crowding` as the primary, because this name
  says what the competitors are but cannot account for the second required passage, which
  has no name link to any of them and ranks 1 under all five single-sided queries tried.

## `same_artist_work_crowding`

- **Status:** provisional.
- **Definition:** Multiple non-answer works by the same artist or creator form a
  close retrieval neighborhood and rank above the annotated gold work.
- **Include when:** At least two higher-ranked works share the same creator and
  broad work type but do not independently satisfy the full question.
- **Exclude when:** A same-artist work independently satisfies all explicit
  constraints; classify that passage as a plausible non-gold answer rather than
  calling it a distractor.
- **Affected units:** `5a83aaeb5542996488c2e483|dense`.
- **Decision source:** D-011.

## `technical_topic_crowding`

- **Status:** provisional.
- **Definition:** Multiple non-answer passages from the same technical topic
  match a technical query facet and occupy high ranks ahead of required
  evidence, creating a redundant topical neighborhood.
- **Include when:** Actual passage texts verify at least two non-answer
  technical documents that match the same technical facet and outrank required
  evidence.
- **Exclude when:** A passage supplies a required answer fact, only one
  technical document is present, or the classification is based on titles
  without inspecting passage text.
- **Affected units:** `5a7c9f325542990527d554e6|bm25`.
- **Decision source:** D-014.

## `cross_passage_conjunction_unresolved`

- **Status:** provisional.
- **Definition:** Evidence required by the question is split across separate
  passages, and an independently scored single-passage retriever cannot resolve
  an intermediate fact in one passage and carry it into scoring another.
- **Include when:** Complete passage texts show that no single passage contains
  the necessary conjunction, the missing intermediate link is concrete, and
  the verified retrieval implementation scores passages independently without
  cross-passage or iterative-hop reasoning.
- **Exclude when:** One passage supplies a complete answer, an evidence-bearing
  substitute completes the chain inside the evaluated set, the label is based
  only on the presence of two annotated golds, or the retrieval stage actually
  performs joint cross-passage reasoning. A condition that requires knowing
  which passages are gold fires none of these and may not be used to refuse
  this descriptor under pit 19s; it is recorded, and may be cited as limiting
  confidence, but is not a ground for refusal (D-040).
- **Affected units:** `5a85cead5542991dd0999ea9|dense` and
  `5ab978855542996be2020512|dense`.
- **Decision source:** D-017, D-020, D-035, D-037, D-038, D-039, and D-040.
  D-040 rules on this entry's exclusion rule and adds no affected unit. A condition that
  requires knowing which passages are gold, pit 19d's third intervention class, may not be used
  to refuse this descriptor under pit 19s; it is recorded and may be cited as limiting
  confidence. The rule follows the reading D-039 already used on
  `5ae60426554299546bf83019|bm25`, where the gold-targeted cell double-recovering at 5 /
  18.751159 and 1 / 25.187216 was placed under confidence as limiting while the descriptor took
  the primary, its deployable counterpart reaching 6 / 18.101334 and 2 / 24.260792. That unit
  is the only one on which the situation has arisen, so one unit is the whole of the direct
  evidence. D-040 rules on pit 19s only and does not extend to pit 15.
  D-039 is the sixth primary use of this name and its third on a lexical backend, on
  `5ae60426554299546bf83019|bm25`. Its three positive legs hold in the strongest forms this
  project has recorded. The matched-token leg is an empty intersection rather than a near one:
  the answer hop scores only on `animated` 5.482144, `space` 4.737610, `western` 3.490203,
  `series` 3.188841 and `american` 1.088638, the constraint hop only on `celebrity` 6.911643,
  `entertainment` 4.863113, `home` 4.662400 and `released` 2.332813, and the question's
  37.094684 of query idf splits into a genre facet of 15.934678 and a distributor facet of
  15.345775, so each required passage forfeits 21.160006 and 21.748909 of the question by
  construction, 57.04 and 58.63 percent. 6 of 11 single query tokens carry opposite signs
  across the hops, above D-024's 10 of 19, D-025's 10 of 20 and D-031's 8 of 22 in proportion
  and far above the 4 of 19 on which D-026 refused this name. Per-side reachability holds in
  D-025's shape and not D-026's, `BraveStarr` alone giving 1 / 7.786100 and 4607 / 0.000000 and
  `Celebrity Home Entertainment` alone giving 4625 / 0.000000 and 4 / 16.437155. The D-028
  route of pit 19s does not fire and was measured in its strongest form: none of 134 non-oracle
  conditions places both required passages inside the cutoff, the Pareto frontier has four
  corners, and at three of them the answer hop's score is bit for bit its baseline 17.987437,
  no non-oracle condition anywhere adding a single point to it; the closest deployable pipeline
  reaches 6 / 18.101334 and 2 / 24.260792. Neither exclusion fires: no single passage answers,
  and `space western` occurs in 1 of 4,937 bodies while `bravestarr` occurs in 2, both of them
  golds. One gold-targeted index-side condition does double-recover, at 5 / 18.751159 and 1 /
  25.187216, and is recorded rather than acted on: it is a pit 19d third-category intervention,
  its deployable counterpart is the 6 / 18.101334 and 2 / 24.260792 above, and the corpus-wide
  version of its answer-side half is negative at -0.024046 points. Whether pit 19s should be
  sliced on "supplies no intermediate fact" rather than on "non-oracle" is registered as an
  audit question.
  D-038 adopts this name as the primary for `5ae1801955429901ffe4aec4|dense` and is recorded in
  the note on primary use below rather than as a secondary affected unit. It is the first unit
  on which BOTH refusal routes were measured and neither fired. The three positive legs hold in
  their Dense-available forms. The matched-token leg has no Dense analogue, as D-025 records.
  Per-side reachability holds from the question's own wording rather than from a rewrite: the
  verbatim sub-phrase `former Superman sponsor` ranks the constraint passage 2 / 0.415715, the
  single word `Superman` ranks it 4 / 0.463022, `sponsored by cereal manufacturer` ranks the
  answer passage 1 / 0.592832 and `Cocoa Krispies` ranks it 2 / 0.404215, while the question as
  annotated gives 173 / 0.225424 and 11 / 0.345068 and deleting either referring expression
  from it restores one side and destroys the other, 3 / 0.444093 and 1554 / 0.092815 without
  `Cocoa Krispies` and 4481 / -0.058135 and 3 / 0.413657 without `Superman`. 8 of 16 single
  factors carry opposite signs across the hops, counting one change applied to the whole
  question or one index-side change, a proportion matching D-025's 10 of 20 and far above the 4
  of 19 on which D-026 refused this name. The missing intermediate fact is concrete and is
  written in exactly one body of 4,937, the constraint passage, while the linking name occurs
  in 3 and never in the question. The D-026 route does not fire: five single anchors were
  measured and each is one-sided with the other hop between 2731 and 4426, `Kellogg's` alone
  giving 4426 / -0.054776 and 1 / 0.704330 and the constraint title alone 1 / 0.699497 and 3930
  / -0.037222, the same sign as D-025 where the same probe demoted the other side to 2158 and
  the opposite of D-037. The D-028 route of pit 19s does not fire either: none of 48 non-oracle
  query conditions places both required passages inside the cutoff, the best presupposing facts
  written only in the golds at 1 / 0.559604 and 9 / 0.360985 and the best strictly deployable
  rewrite reaching 154 / 0.242010 and 2 / 0.527444, while the only query-side double recovery
  anywhere in the study is the pure oracle of appending both gold titles at 2 / 0.416027 and 1
  / 0.464131. Neither exclusion fires: the answer passage states the location and lists the
  cereal among its brands but never says the company sponsored Superman, and the one substitute
  in the corpus supplies neither required fact, the location occurring in exactly 1 of 4,937
  bodies which is that passage itself at 11 / 0.345068, outside the cutoff. Resolving the
  conjunction by hand behaves as the definition predicts and is recorded as such:
  `Where is Kellogg's located?` gives 4115 / -0.049557 and 1 / 0.662501 and
  `Where is Kellogg's headquartered?` 3877 / -0.034668 and 1 / 0.683682, lifting the answer hop
  to 1 and abandoning the constraint hop.
  D-037 records an eighth non-adoption, the first in which the D-026 route fires while the
  D-028 route explicitly does not, and the first in which the missing intermediate fact is
  written in BOTH required bodies rather than only in the other one. On
  `5ae048a255429924de1b708e|dense` two of the three positive legs fail. The matched-token leg
  has no Dense analogue, as D-025 records. The opposite-sign leg is 2 of 13 single factors,
  below the 4 of 19 on which D-026 refused this name and far below 10 of 19 at D-024, 10 of 20
  at D-025, 8 of 22 at D-031 and 8 of 14 at D-035. The third leg has the wrong shape: the
  linking name `Catwoman` occurs in 2 of 4,937 indexed bodies and those two are the required
  passages themselves, so neither has to resolve anything in the other and carry it across;
  what is missing is that the question never contains that name. The D-026 route then fires
  outright, a single anchor lifting both sides, `Catwoman` alone giving 2 / 0.769825 and 1 /
  0.788529, the answer title alone 1 / 0.821070 and 2 / 0.775806 and the constraint title alone
  2 / 0.707477 and 1 / 0.805008, which is the opposite sign to D-025 where the same probe
  demoted the other side to 2158. The D-028 route of pit 19s does NOT fire and the refusal does
  not rest on it: no non-oracle query condition places both required passages inside the
  cutoff, the best deployable one being title indexing at 125 / 0.273863 and 5 / 0.387651. The
  first exclusion, one passage supplying a complete answer, is recorded as a boundary and is
  not used as a ground, because the answer hop names Pitof, the year and the medium and `pitof`
  occurs in only that one body of 4,937, yet it never states that a tie-in game exists. The
  decisive point is that the name fails even under its own reading: both sides are separately
  unreachable, the corpus-unique name giving 1283 / 0.076500 and the referring clause 436 /
  0.189887, while an index-side change that leaves the question untouched word for word places
  both inside the cutoff at 3 / 0.469751 and 1 / 0.549310.
  D-035 records a seventh non-adoption, the first on a Dense bridge unit whose question names
  nothing and the first in which the D-028 route and the D-026 route both fire. On
  `5add67915542992200553af8|dense` the positive legs are strong: per-side reachability holds
  under non-oracle queries, the referring description with a mafia head noun ranking the bridge
  passage 1 / 0.723205 and the single word `gangster` ranking the answer passage 2 / 0.437038;
  8 of 14 single factors carry opposite signs across the hops, the highest proportion recorded,
  against 10 of 19 at D-024, 10 of 20 at D-025, 8 of 22 at D-031 and 4 of 19 at D-026; and the
  first exclusion does not fire, because the answer passage never states that its employer is
  Italian American and so does not answer alone. It is refused on the D-028 route of pit 19s:
  seven non-oracle conditions that supply no intermediate fact and perform no cross-passage
  reasoning place both required passages inside the cutoff, the best being `What was the
  nickname of the hitman hired by a Mafia crime family?` at 1 / 0.585624 and 4 / 0.510640. It
  is refused on the D-026 route as well: a single anchor lifts both sides, the bridge title
  alone giving 1 / 0.706333 and 5 / 0.440004, which is the opposite sign to D-025, where the
  same probe demoted the other side to 2158.
- **Note on primary use:** D-022 adopts this name as the *primary* mechanism for
  `5ade42b55542992fa25da717|bm25`, D-024 adopts it as the primary for
  `5ae057fd55429945ae959328|bm25`, D-025 adopts it as the primary for
  `5ae0a59a55429945ae9593e2|dense`, D-031 adopts it as the primary for
  `5ab48c325542996a3a969f93|dense`, D-038 adopts it as the primary for
  `5ae1801955429901ffe4aec4|dense`, and D-039 adopts it as the primary for
  `5ae60426554299546bf83019|bm25`; none is therefore listed above as a
  secondary affected unit. The enumeration in full is D-022 first, D-024 second,
  D-025 third, D-031 fourth, D-038 fifth and D-039 sixth. **D-031 was missing
  from this list until D-039 restored it**, which is why D-038's own entry calls
  itself the fourth primary use when it is the fifth; that entry stays as written
  under red line 4 and the enumeration is what changes, which is exactly the
  failure mode section E rule 4 replaced running tallies to expose; D-017 and D-020 both used it as a secondary alongside
  a different primary, both on Dense units, so D-025 is the first Dense unit to use
  it as the primary. D-025 records that one leg of the D-022 evidence set has no
  Dense analogue: matched query-token sets cannot be compared under a bi-encoder,
  so the Dense evidence there rests on the remaining three, namely per-side
  reachability at rank 1 from each gold's own name, 10 of 20 single-factor
  conditions carrying opposite signs across the hops, and exhaustion of the
  non-oracle direction over 66 conditions whose name-free ceiling is 4 and 14. It
  further records that in that unit no removal probe helps the far hop at all,
  which is what distinguishes the reading from `compound_two_sided_crowding`.
  Both BM25 primary uses are bridge units in which the two required hops
  match almost disjoint query-token sets, several single factors carry opposite
  signs across the hops, and the missing intermediate fact is a name that occurs
  nowhere in the query and only inside the other gold passage. D-024 records one
  qualification to the D-022 evidence set: there both hops were individually
  reachable at rank 1 from their own names, whereas in D-024 only the bridge hop is,
  the answer hop reaching rank 51 from its own bare name because of a verified
  tokenizer artifact and rank 4 once that artifact is neutralized. Whether the
  descriptor is suited to primary use is a vocabulary-audit question and is not
  settled here; this note records the usage and changes no definition, inclusion
  rule, or exclusion rule. D-028 records the first non-adoption of this name on a unit
  where all three legs of the D-022 and D-024 evidence set hold: on
  `5a79b7f6554299029c4b5f6f|bm25` the two required passages match **completely** disjoint
  query-token sets, six of eighteen single factors carry opposite signs across the hops,
  and the missing intermediate fact is a name that occurs nowhere in the query and only
  inside the other gold, the string appearing in exactly 2 corpus passages which are the
  two golds. It is not adopted because one non-oracle condition, boundary-punctuation
  normalization combined with indexing the title, supplies no intermediate fact and
  performs no cross-passage reasoning yet places both required passages inside the cutoff
  at 2 / 34.444959 and 4 / 32.279538, which could not happen if the inability to resolve
  a fact in one passage and carry it into scoring another were the binding constraint. As
  in D-026, a single anchor also reaches both required passages. This is a falsification
  route the earlier applications did not have available, since in D-022, D-024 and D-025
  no non-oracle condition recovered both hops; whether it should be written into the
  exclusion rule is a vocabulary-audit question and is not settled here. D-029 records a
  second non-adoption, on a Dense bridge unit and on the exclusion rule's **first** clause
  rather than on the D-028 argument. On `5a81ebee554299676cceb16d|dense` the answer gold
  states the director, the genre and the starring actress in one passage, so it supplies a
  complete answer on its own and the other required passage is a redundant constraint for
  answering, which is the situation the first exclusion names. The D-028 route is available as
  well and agrees: index-side removal probes that supply no intermediate fact and perform no
  cross-passage reasoning place both required passages inside the cutoff at 3 / 0.365309 and
  5 / 0.332391. D-031 adopts this name as the primary for `5ab48c325542996a3a969f93|dense`,
  the fourth primary use and the second on a Dense unit after D-025, which is why that unit is
  not listed above as a secondary affected unit. The missing intermediate fact is where the
  named king is buried: the chain runs from him to Waltham Abbey to Essex, the question
  supplies only its first term, `waltham` occurs in exactly 2 of 4,937 passages which are the
  two required ones and nowhere in the question, and no corpus passage contains both `Essex`
  and `Harold Godwinson`. Of the three legs of the D-022 and D-024 evidence set, per-side
  reachability holds in its strongest recorded form and the exhaustion leg holds over 107
  conditions, while the opposite-sign leg is explicitly weak at 8 of 22 and does not carry the
  decision; D-031 records that weakness rather than suppressing it, since D-026 cited 4 of 19
  as one of three grounds for rejecting this same name. Each required passage is reachable at
  rank 1 from its own name, at 0.759333 and 0.774335, and each name demotes the other to
  1386 / 0.067247 and 98 / 0.248832, which is the D-025 sign and excludes the D-026 route.
  Every single anchor recovers exactly one side and only injecting both names recovers both.
  The D-028 route under pit 19s is unavailable, no non-oracle condition, no index-side removal
  and no gold-targeted repair placing both required passages inside the cutoff; rewriting both
  passages so each states the county explicitly still gives 14 / 0.355607 and 11 / 0.358665.
  D-031 adds one observation no earlier application recorded: what the answer hop lacks is the
  category rather than the name of the intermediate entity, since adding the single generic
  word `abbey` to the question moves it from 21 / 0.339314 to 4 / 0.504249 while leaving the
  other required passage at 18 / 0.357596, and that category is stated only in the other gold.
  D-033 records a fifth non-adoption and the first on a BM25 bridge unit in which every positive
  leg of the D-022 and D-024 evidence set holds. On `5abcc96c5542996583600492|bm25` the two
  required passages match disjoint content tokens, their matched sets meeting only in the scaffold
  `the`, `and`, `is` and `of`; eight of seventeen single factors carry opposite signs across the
  hops; the missing intermediate fact is concrete and occurs in exactly 1 of 4,937 passages, the
  link from the queried character's daughter Dakota to the answer film, with `Marley Shelton` and
  `Grindhouse` each occurring in exactly the two required passages and in no others; and per-side
  reachability holds in its strongest recorded form, each required passage ranking 1 from its own
  title, at 30.558101 and 12.467933, while demoting the other to 3444 / 2.565580 and
  4437 / 0.000000, which is the D-025 sign and excludes the D-026 route. It is not adopted on the
  D-028 route of pit 19s: a condition that supplies no intermediate fact and performs no
  cross-passage reasoning, a generic analyzer with scaffold removal and title indexing combined
  with an index-side removal of the 14 non-gold passages naming the queried actress, a set
  definable from the query alone, places both required passages inside the cutoff at
  1 / 25.266887 and 3 / 15.335047, and widening that family to all 41 gives 1 / 25.246782 and
  2 / 18.024994. D-033 registers a boundary on the first exclusion rather than deciding it: the
  bridge passage names the answer film outright while verifying only one of the question's two
  constraints, and whether `One passage supplies a complete answer` fires on a passage that
  supplies the answer string without verifying every constraint is a vocabulary-audit question.
  D-029 is the only prior use of that clause and its answer passage satisfied all three of its
  question's facets. D-034 records a sixth non-adoption, on a BM25 bridge unit, on the D-028
  route of pit 19s, and it is the first in which the opposite-sign leg is the weakest yet
  measured. On `5adc8977554299438c868de2|bm25` two positive legs hold: the matched query-token
  sets are disjoint in content, the bridge passage matching `associated`, `goddess`, `the` and
  `with` and the answer passage `consists`, `of` and `the`, so they meet only in the scaffold
  token `the`; and per-side reachability holds at rank 1 from each gold's own title,
  1 / 14.707262 and 1 / 22.413786. The opposite-sign leg is 3 of 22, weaker than the 4 of 19
  D-026 cited as one of three grounds for rejecting this name. It is refused because a condition
  that supplies no intermediate fact and performs no cross-passage reasoning, two-sided boundary
  normalization plus scaffold removal plus an index-side removal of the 7 non-gold passages
  naming Frigg, a set definable from the query alone, places both required passages inside the
  cutoff at 1 / 40.778471 and 5 / 11.221051, and widening the family to the 10 non-gold passages
  carrying `goddess` gives 1 / 44.308999 and 2 / 11.219467, against a size-matched null control
  at 1 / 35.981180 and 9 / 11.452994 and a complement control at 1 / 35.931195 and
  9 / 11.223968. D-034 also records that the second exclusion is engaged but not used to carry
  the decision: evidence-bearing substitutes complete the bridge leg inside the cutoff at 1 and
  4 while the answer leg has no substitute anywhere in the corpus, so whether `an
  evidence-bearing substitute completes the chain` fires when only one leg is substitutable is
  left open beside the boundary D-033 registered on the first exclusion.

## `possible_type_mismatch`

- **Status:** provisional.
- **Definition:** The answer category or wording requested by the question does
  not align cleanly with the category wording in the annotated passage or
  answer, creating retrieval-alignment or evaluation ambiguity.
- **Include when:** Actual question, answer, and passage text verify a concrete
  category mismatch, such as `arcade game` versus `pinball machine`, and it is
  recorded as uncertainty or a secondary contributing condition.
- **Exclude when:** The terms align directly, the difference is inferred only
  from titles, or the mismatch is asserted as the primary causal mechanism
  despite a complete-corpus single-factor diagnostic that does not change the
  target retrieval outcome.
- **Affected units:** `5a85cead5542991dd0999ea9|dense`.
- **Decision source:** D-017.

## `proper_name_homonym_collision`

- **Status:** provisional.
- **Definition:** Passages about distinct entities sharing a full name, surname,
  forename, or close proper-name form with an explicitly queried candidate
  occupy higher ranks and displace that candidate's required evidence.
- **Include when:** Actual passage text confirms different entities, the name
  overlap is concrete, and competition materially affects the named candidate.
- **Exclude when:** Passages are variants or works of the same entity, collision
  is inferred from titles alone, or competitors match only a queried property.
- **Affected units:** `5a8d93ad554299653c1aa13d|dense`.
- **Decision source:** D-018, D-032, and D-033. D-033 records a non-adoption, not an affected
  unit, and is the third withholding of a name-overlap descriptor on the D-018 materiality
  standard, after D-029 and D-032. On `5abcc96c5542996583600492|bm25` the inclusion rule is met by
  exactly one passage, `The Law &amp; Harry McGraw`, a 1987 CBS mystery series about an unrelated
  Harry McGraw, which is one of only 2 corpus passages carrying the queried surname. Materiality
  fails on both baselines. Under the query-side possessive normalization it ranks 69 / 27.138678,
  below the required passage, and removing it leaves that passage at 2 / 38.395992, unchanged in
  rank; under the fully normalized pipeline it ranks 13, one position above the answer passage,
  and removing it moves that passage from 14 / 12.806919 to 13 / 12.806578, exactly one position,
  which is the D-029 figure.
  D-032 records a non-adoption, not an affected unit, and is
  the second withholding of a name-overlap descriptor on the D-018 materiality standard after
  D-029. On `5ab8f57b5542991b5579f097|bm25` the include rule is met on read text by two passages
  about entities distinct from either queried candidate that nevertheless outrank a required
  passage: `Joe Scarborough` 9 / 20.188689, whose text names Charles Joseph Scarborough, a cable
  news and talk radio host, and `Thomas H. Gale House` 10 / 19.869995, a Frank Lloyd Wright house
  in Oak Park. Materiality fails: an index-side removal of both moves the required passage only
  from 11 / 19.741610 to 9 / 19.763251, two rank positions and no change of outcome, and the pair
  sits above only one of the two required passages. A wider probe that drops all 31 non-gold
  passages carrying the bare token `joseph` gives 4 / 31.046130 and 10 / 19.764622 and is recorded
  as an idf effect rather than a collision effect, since none of those passages ranks above the
  passage it moves and its gain comes from `df(joseph)` falling from 32 to 1.

## `answer_property_semantic_crowding`

- **Status:** provisional.
- **Definition:** Multiple passages match a comparison question's answer
  property but refer to entities outside the explicitly named candidate set,
  occupying high ranks ahead of required candidate evidence.
- **Include when:** Actual texts verify at least two higher non-candidate
  entities explicitly expressing the property, and provenance or controlled
  full-corpus diagnostics support a material ranking effect.
- **Exclude when:** Property match is inferred from titles, the passage is a
  named candidate or valid substitute, or competition is solely name overlap.
- **Affected units:** `5a8d93ad554299653c1aa13d|dense`.
- **Decision source:** D-018.

## `generic_query_scaffold_score_inflation`

- **Status:** provisional.
- **Definition:** Under a minimally processed lexical scorer, grammatical or
  interrogative query-scaffold tokens receive enough aggregate score to promote
  passages that lack the named entities, works, or answer relation.
- **Include when:** The actual tokenizer and scoring implementation are known,
  exact score decomposition verifies material contributions from non-repeated
  scaffold terms, and at least one higher-ranked passage lacks the decisive
  content evidence.
- **Exclude when:** The contribution is inferred only from visible overlap,
  repeated occurrences are the material mechanism (use
  `repeated_function_word_amplification`), or content-bearing category terms
  rather than query scaffold explain the competition.
- **Affected units:** `5ab72a025542992aa3b8c7b8|bm25`, `5ac1a3665542994ab5c67daf|bm25`,
  `5ab8f57b5542991b5579f097|bm25`, `5abcc96c5542996583600492|bm25`, and
  `5ae60426554299546bf83019|bm25`.
- **Decision source:** D-019, D-021, D-030, D-032, D-033, D-034, and D-039.
  D-039 adopts this descriptor on `5ae60426554299546bf83019|bm25` for one passage with no
  relation to the question at all. `Pergament Home Centers`, a home-improvement store chain,
  ranks 7 / 18.620405, above the answer hop at 8 / 17.987437. Its reconciled decomposition
  gives `did` 6.402224 and `which` 1.541303, so 7.943527 of its score, 42.7 percent, is
  interrogative scaffold and only 10.676878 is content, far below the answer hop's own
  17.987437. The exclusion for repeated occurrences does not fire: no query token repeats, so
  the doubled `did` in that body is ordinary document term frequency and not the per-occurrence
  query accumulation `repeated_function_word_amplification` names. Scaffold removal alone moves
  the two required passages from 8 / 17.987437 and 6 / 18.769969 to 6 / 17.987437 and 4 /
  18.769969 with both scores unmoved, this passage and `Locke the Superman`, whose scaffold
  share is 2.111606 or 10.6 percent, both falling below the answer hop; under scaffold removal
  with title indexing it is 23 / 10.924670 and under the document-side normalization 34 /
  10.451708. For contrast `COPS (animated TV series)` draws 1.352214 or 5.4 percent from
  scaffold and `Noel C. Bloom` 1.625490 or 8.0 percent, while both required passages,
  `Sterling Entertainment Group` and `Tottoi` draw 0.000000.
  D-034 records a
  non-adoption, not an affected unit, and it is the first occasion on which this entry's second
  exclusion fires. On `5adc8977554299438c868de2|bm25` all three inclusion conditions hold, and
  the third holds in the cleanest form this project has recorded: `Treehouse (game)` at
  9 / 27.610510 is a board-game description containing none of the question's content and takes
  100.0 percent of its score from scaffold, of which the non-repeated tokens `does`, `of` and
  `with` supply 34.0 percent. The exclusion nevertheless fires, on the same direct experiment
  D-033 ran: deleting only the second occurrence of each repeated scaffold token is worth 0 rank
  positions on one required passage and 35 on the other, while deleting the three non-repeated
  tokens is worth 1 and minus 5, so the repeated occurrences are the material mechanism and
  `repeated_function_word_amplification` takes the unit. This is the mirror of D-033, where the
  identical experiment sent the unit here instead, and the two are the boundary samples the audit
  question D-032 opened about co-necessity now needs alongside it.
  D-033 is the fourth affected unit
  and the first in which this entry's repeated-occurrence exclusion is settled by a direct
  experiment rather than by inspection. On `5abcc96c5542996583600492|bm25` all three inclusion
  conditions hold: the implementation is verified; exact decomposition shows the four
  **non-repeated** scaffold tokens `what`, `is`, `of` and `and` supplying between 24.3 and 32.9
  percent of the competitor scores, for instance 10.079898 of the 32.591784 held by
  `Dark Passage (film)` at rank 4; and several higher-ranked passages lack the decisive content
  entirely, `Penny (The Big Bang Theory)` 9 / 30.681984 containing neither queried entity while
  taking 22.530752, or 73.4 percent, of its score from scaffold. The repeated-occurrence exclusion
  is tested and does not fire: the query's only repeated token is `the`, three times, and deleting
  its second and third occurrences alone gives 18 / 21.800059 and 118 / 18.393906, worth 8 rank
  positions on one required passage and minus 3 on the other, while deleting the four
  non-repeated scaffold tokens instead gives 17 / 21.284848 and 77 / 18.415555, worth 9 and 38, so
  the non-repeated tokens are the material half. The category-term exclusion that fired in D-030
  does not fire either: the same competitor set is separately carried by broad film vocabulary and
  is recorded under `generic_term_lexical_crowding` for that reason, and the two are additive here
  rather than alternatives. Unlike D-032 this adoption rests on **solo** materiality, scaffold
  removal on its own being positive on both required passages at 13 / 10.787786 and
  103 / 6.894036, so the audit question D-032 opened about co-necessity is not reached here.
  D-032 is the third affected unit and the
  first adoption resting on **co-necessity** rather than on solo materiality, which makes it the
  paired counter-sample to D-030, where the same inclusion rule was met and the descriptor was
  withheld. On `5ab8f57b5542991b5579f097|bm25` all three inclusion conditions hold: the
  implementation is verified; exact score decomposition shows the four **non-repeated** scaffold
  tokens `and`, `of`, `the` and `were`, each occurring once in the query, supplying 29.4 to 53.4
  percent of the competitor scores; and two passages above a required passage lack the decisive
  content entirely, `Joe Scarborough` 9 / 20.188689 taking 53.4 percent from scaffold while its
  text concerns a cable-news host and matches only `joseph` and `same`, and
  `Thomas H. Gale House` 10 / 19.869995 taking 48.4 percent while being a Frank Lloyd Wright house.
  The exclusion's repeated-occurrence clause cannot fire, the query containing no repeated token at
  all, and its category-term clause, which fired in D-030, does not fire here because the
  competition is carried by proper-noun tokens rather than by broad category vocabulary; the
  interrogative frame alone and `nationality` alone each reproduce 0 of 10 of the observed
  neighbourhood at every depth. Solo materiality is modest, scaffold removal alone giving
  6 / 17.888493 and 7 / 16.787469, four rank positions on one required passage and none on the
  other. What carries the adoption is that scaffold removal is present in **all 15** non-oracle
  conditions that place both required passages inside the cutoff and in none that does not, and
  that no single factor recovers the pair; this is the form D-028 used for the title-indexing
  condition. Whether co-necessity is a sufficient ground for a secondary, given D-030's refusal on
  solo materiality, is registered as a vocabulary-audit question, and these two units are the
  boundary samples it needs. D-030 records a non-adoption, not an affected
  unit, and it is the first in which this descriptor's inclusion rule is fully met and the
  descriptor is still withheld. On `5a83880e554299123d8c214e|bm25` the interrogative frame
  `what brand's comic character` supplies the query's highest-idf token, `brand's` at 7.587919,
  which occurs in exactly 2 corpus passages and gives 7.815653 points, or 36.190 percent, of the
  rank-1 passage's 21.596320 through the unrelated phrase `Russell Brand's Got Issues`, with
  question-frame vocabulary supplying 11.493516, or 53.220 percent, of that score; the token is
  not repeated and that passage lacks every decisive content cue, so all three inclusion
  conditions hold. Two grounds withhold it. The exclusion's final clause routes competition
  explained by content-bearing category terms elsewhere, and 59 of the 64 passages above the
  answer hop are song or album profiles earning their ranks from exactly such terms. And the
  D-018 materiality standard fails: deleting the entire interrogative frame from the query moves
  the two required passages only from 66 / 12.585642 and 61 / 12.713062 to 64 / 12.585642 and
  59 / 12.713062, and an index-side removal of both passages containing `brand's` moves them
  only to 65 / 12.592570 and 60 / 12.719437. The observation is instead recorded inside D-030's
  primary, because the same unnormalized possessive clitic that reduces the question's only name
  anchor to a token with 0 corpus occurrences is what makes this frame word rare enough to
  matter, so the two effects are one mechanism rather than two descriptors.

## `same_topic_passage_distractor`

- **Status:** provisional.
- **Definition:** A higher-ranked non-gold passage is genuinely in the same
  subject or work neighborhood and may explicitly mention one queried work, but
  its actual text omits another decisive entity, comparison side, or relation
  required to answer the question.
- **Include when:** Complete passage text verifies the topical or explicit-work
  connection and also verifies the missing decisive constraint.
- **Exclude when:** The classification is based only on the displayed title,
  the passage supplies a complete alternative answer or valid substitute chain,
  or it matches only generic query scaffold without a real topical connection.
- **Boundary against `generic_term_lexical_crowding`, prospective (D-055):** A competing
  passage belongs here when its body verifies a real connection to the queried entity, work or
  topic and also verifies the missing decisive constraint. A competing passage that matches
  broad category, institutional or relational vocabulary from the query without that verified
  connection belongs to `generic_term_lexical_crowding` instead. Different subsets of the
  passages above a required passage may carry the two descriptors within one unit; the same
  passage set must not carry both.
- **Affected units:** `5ab72a025542992aa3b8c7b8|bm25`,
  `5add67915542992200553af8|dense`, `5ae1801955429901ffe4aec4|dense`, and
  `5ae60426554299546bf83019|bm25`.
- **Decision source:** D-019, D-035, D-038, D-039, and D-055.
  D-055 retains this descriptor and `generic_term_lexical_crowding` as two names, refuses the
  merge, and adds no affected unit. The prospective boundary bullet above states the
  passage-level line both entries now carry, and the two names co-occur on no unit in
  `case_memos_v2.csv`, so the rule against describing one passage set twice records a
  regularity rather than repairing a violation. The line was measured in both directions inside
  one unit: on `5ae60426554299546bf83019|bm25` this descriptor is adopted for
  `COPS (animated TV series)` 1 / 24.991204, whose body verifies the connection to the queried
  distributor and verifies the missing constraint, while the sibling name is refused for the
  five-passage name family above the answer hop that contains that same passage, where
  `celebrity` alone reproduces 5 of 5 of that family and the whole genre facet reproduces
  0 of 5. That family is D-039's `related_name_document_crowding` set, five members including
  `COPS (animated TV series)`, so this descriptor's single-passage adoption is nested inside
  it: the intersection of the two sets is that one passage and the remaining four members
  carry the related name only. No route to
  `question_frame_semantic_crowding` is added, that would decide by side effect the questions
  T-19 and T-26 hold, and `related_name_document_crowding` is not folded in: D-048's sentence
  calling its overlap with this descriptor item T-24 is an incorrect cross-reference, D-048
  stands as written under red line 4, and that overlap is opened as its own triage item.
  D-039 adopts this descriptor on `5ae60426554299546bf83019|bm25` for a single passage,
  `COPS (animated TV series)` 1 / 24.991204. Its text states that it is
  `an American animated television series released by DIC Entertainment ... and Celebrity Home Entertainment`,
  so it matches 8 of the question's 11 tokens, every one but `space`, `western` and `did`, and
  its explicit connection to the queried distributor is verified in the body rather than
  inferred from the title. The missing decisive constraint is verified in the same way: that
  text contains neither `space` nor `western`, and the only corpus passage containing
  `space western` is the answer gold itself. It is adopted as a composition and not as a causal
  claim; the other four non-gold passages above the answer hop are covered by
  `related_name_document_crowding` and `Pergament Home Centers` by
  `generic_query_scaffold_score_inflation`, so no passage above the answer hop is left without
  a descriptor.
  D-038 is the third affected unit and the second on a Dense retriever. On
  `5ae1801955429901ffe4aec4|dense` the descriptor is adopted for three of the ten passages
  above the answer hop and the other seven are named as not covered. On read text
  `Superman: Tower of Power` at 8 / 0.353345 carries three of the question's words in
  twenty-two words but is a drop tower ride and names no sponsor, `Twisties` at 9 / 0.350352 is
  a snack-food brand with an owner history and neither required fact, and `General Mills` at 10
  / 0.346669 is an American multinational food company with a headquarters and a brand list
  that contains neither the queried cereal nor any sponsorship. Each verifies both halves of
  the include rule and none of the three exclusions fires. Not covered are `Cocoa Krispies` at
  2 / 0.406143, which supplies one link of the chain and is therefore treated under pit 19b
  rather than as a distractor, and six passages whose only connection is the question's
  location frame, `Hero Certified Burgers` at 1 / 0.414047, `Schwartz's` at 3 / 0.383988,
  `The Works (restaurant)` at 4 / 0.377530, `Tim Hortons` at 5 / 0.363764, `Spencer Gifts` at 6
  / 0.357795 and `Digital Media Factory` at 7 / 0.357676, for which the third exclusion fires.
  Like D-035 this is adopted as a COMPOSITION and not as a causal claim: on a bi-encoder every
  index-side removal probe is an arithmetic identity, and 14 cells were run here and all 14
  match `rank_after = rank_before - |removed and ranked above it|` with the gold scores
  identical to the last bit.
  D-035 is the second affected unit and the first on a Dense retriever. On
  `5add67915542992200553af8|dense` the 3 passages above the answer passage that are not person
  biographies are organization or ethnic-body pages in the same subject neighbourhood, each
  verified on read text to omit a decisive constraint: `Mexican Mafia` 8 / 0.425303 is a
  criminal organization but Mexican American, `Los Angeles crime family` 10 / 0.416292 carries
  the question's referring description word for word but names no hitman and no nickname, and
  `Italian American One Voice Coalition` 11 / 0.408984 is an Italian American organization but
  an anti-bias one. Together with `generic_person_semantic_neighborhood` these partition the
  ten passages above the answer passage exactly, 7 and 3. Neither exclusion fires: the
  classifications rest on full passage text, none of the three supplies a complete alternative
  answer or a valid substitute chain, and each has a real topical connection rather than a
  scaffold match. The definition's clause `may explicitly mention one queried work` is
  permissive and none of the three names either required entity, which is recorded as a
  boundary. Like the neighbourhood descriptor above it, this is adopted as a composition and
  not as a causal claim, because on a bi-encoder every index-side removal probe is an
  arithmetic identity; dropping these 3 gives 7 / 9 and a size-matched null drawn from below
  the answer passage gives 7 / 12.

## `exact_string_source_dependency`

- **Status:** provisional.
- **Definition:** A required passage's only distinctive connection to the query
  is verbatim string overlap with a quotation or fixed phrase embedded in that
  passage, so reaching it depends on literal surface matching rather than on
  whole-passage semantic similarity.
- **Include when:** Actual passage text verifies that the shared string occurs
  literally in the required passage and nowhere else that matters, the passage's
  remaining content belongs to an unrelated topic, and a controlled full-corpus
  condition shows that the target retriever does not surface the passage even
  when the query is reduced to that string.
- **Exclude when:** The passage shares substantive topical content with the
  query beyond the quoted string, a named entity rather than the string is the
  effective anchor, or the descriptor is used to assert that a comparison
  retriever performed phrase matching. Under a whitespace tokenizer with no
  phrase support, describe the comparison result as single-token surface
  overlap, not as exact-phrase retrieval.
- **Affected units:** `5ab978855542996be2020512|dense`.
- **Decision source:** D-020.

## `question_frame_semantic_crowding`

- **Status:** provisional.
- **Definition:** Under a whole-passage semantic scorer, multiple non-answer
  passages match the question's broad framing facets, such as its answer type,
  temporal span, or generic object class, while omitting the decisive referent,
  and they outrank the answer-bearing passage.
- **Include when:** Actual passage texts verify at least two higher-ranked
  passages that match the framing facets but contain none of the decisive
  referent wording, and a controlled full-corpus condition shows that this
  competition persists when the referent cue is removed or replaced.
- **Exclude when:** The classification rests on titles, a competitor supplies a
  complete alternative answer or a valid substitute hop, the competition is
  produced by the decisive referent cue itself and therefore belongs to the
  primary mechanism, or the retriever is lexical and the contribution is better
  established by score decomposition, in which case use
  `generic_query_scaffold_score_inflation` or
  `generic_term_lexical_crowding`.
- **Affected units:** `5ab978855542996be2020512|dense`,
  `5ae0a59a55429945ae9593e2|dense`, and `5ae048a255429924de1b708e|dense`.
- **Decision source:** D-020, D-025, D-029, D-031, D-035, D-037, D-038, D-043,
  and D-054.
  D-054 retains one descriptor for this name, gives it no primary-use contract of its own, and
  adds no affected unit. A primary use and a secondary use of this name rest on the same
  inclusion rule and differ in evidential strength rather than in mechanism, so the name is not
  split across the two inventories; its primary use is governed by D-043's shared
  crowding-family contract together with this entry's own inclusion rule and exclusion clause.
  A second, descriptor-specific contract would restate D-043's gate for one member of the
  family that gate was written over. The stale sentence in the note on primary use below is
  replaced accordingly. The definition, the inclusion rule, the exclusion clause and the
  affected-units list are unchanged, and no primary or secondary assignment moves.
  D-043 states the crowding-family primary-use contract and adds no affected unit. A descriptor
  of this family may be a unit's primary only if the competing set is stated as a rule over
  passage content rather than as a rank range, which is the footing this entry's own primary
  use rested on, and only if that rule does not also select a required passage. The second
  clause is grounded on two units: D-039, where the family is definable only by a rule that
  also removes a required gold and crowding was held to secondary, and D-027, where a fact
  check over the pooled corpus found a content-only rule selecting all six competitors and
  neither required passage without needing anything from either of them. Neither D-027 nor this
  entry's own unit is re-judged. The contract carries no clause on what counts as measuring a
  family's effect on a bi-encoder, where index-side removal is an arithmetic identity by D-035,
  and it must be carried into the candidate taxonomy when that file is written.
  D-038 records a non-adoption on `5ae1801955429901ffe4aec4|dense`, and it is the second unit
  after D-035 in which the third exclusion fires, this time because the framing cannot
  reproduce its own family. The second half of the include rule fails outright in the forward
  direction: `Where is it located?` reproduces 1 of the baseline top ten at 3507 / -0.012833
  and 1318 / 0.089585, `Where is the sponsor located?` 1 of ten at 3166 / 0.017899 and 543 /
  0.165542, `Where is the company located?` 2 of ten at 4095 / -0.029858 and 79 / 0.309746 and
  the bare word `located` 2 of ten at 4820 / -0.087862 and 1085 / 0.106555, while the
  question's referring expressions do reproduce it, `Cocoa Krispies` alone giving 4 of ten and
  both referring expressions without the frame 6 of ten at 108 / 0.229726 and 5 / 0.350304. The
  reverse direction agrees: deleting `Cocoa Krispies` from the full question leaves 2 of ten
  while deleting `Superman` leaves 6 of ten. The competition is therefore produced by a
  decisive referent cue rather than by the framing. Read text agrees that this is not a frame
  family in the D-037 sense either: 2 of the 10 passages above the answer hop contain the
  queried cereal's words and 1 contains the queried character's, so the count of competitors
  free of the decisive referent wording is not 0 of 10.
  D-037 is the third affected unit and the third Dense one. On `5ae048a255429924de1b708e|dense`
  both halves of the include rule hold and no exclusion fires, and the third exclusion is
  measured in both directions and does NOT fire, which is the reverse of D-035 and the same
  shape as D-025. On read text all 38 non-gold passages above the constraint hop match the
  question's framing facets, a film, a video game, an adaptation or a director, and 0 of the 38
  contain the decisive referent wording `Catwoman` and 0 contain `Pitof`; the same two counts
  are 0 and 0 among the 261 above the answer hop, of which 245 carry a film word or a game
  word. Forward, the frame alone reproduces the neighbourhood, the game clause giving 6 of the
  baseline top ten, the same clause with the year 6 of ten and `a video game based on a film` 5
  of ten, while the referring cue alone gives 1 of ten and the bare corpus-unique name 0 of
  ten. Reverse, deleting the single word `Pitof` from the full question leaves 8 of the
  baseline top ten in place at 222 / 0.245012 and 18 / 0.352078. The family is therefore
  produced by the frame and not by the decisive referent cue, so it is not downstream of the
  adopted primary. Following D-035 it is adopted as a COMPOSITION and not as a causal claim,
  because on a bi-encoder every index-side removal probe is an arithmetic identity: 22 cells
  were run and all 22 match `rank_after = rank_before - |removed and ranked above it|` with the
  gold scores identical to the last bit, the 16-passage video-game family giving 23 / 0.320936
  and its 22-passage complement 17 / 0.320936. One further measurement is recorded because it
  bears on how this descriptor should be read: the only query-side lever on the family points
  the other way, deleting the whole game clause moving both required passages further from the
  cutoff, to 545 / 0.203382 and 937 / 0.150986. The descriptor is the closest competitor for
  the primary and loses it on outcome-determinacy, not on its inclusion rule.
  D-035 records a non-adoption, not an affected unit, and it is the first unit in which the
  third exclusion is measured in both directions and fires. On `5add67915542992200553af8|dense`
  the first half of the include rule is met on read text, 7 of the 10 passages above the answer
  passage matching the question's person-role and criminal-organization framing while
  containing none of the decisive referent wording. The third exclusion assigns the family to
  the primary mechanism: the referring cue alone reproduces 9 of the baseline top ten and 6 of
  the 7 person biographies, while the frame alone reproduces 0 of 10, whether it is `nickname
  of the hitman`, `What was the nickname of the` or `nickname` on its own, and deleting the
  referring cue from the full question leaves 0 of 10 as well. The family is therefore produced
  by the decisive referent cue rather than by the frame, which is the reverse of the D-025
  structure, where the two cues built disjoint neighbourhoods and the descriptor was adopted
  for the one the answer facet produced. D-031 records a non-adoption, not an
  affected unit, and it is the first unit in which this descriptor is refused because the
  include rule's controlled condition fails outright rather than because the exclude rule's
  third clause fires. On `5ab48c325542996a3a969f93|dense` eleven of the nineteen passages above
  the answer hop are English place, memorial and county documents that carry none of the
  question's proper nouns, among them `Tower Hill Memorial` 8 / 0.373865,
  `Manchester Cenotaph` 14 / 0.347829, `Viscount Wimborne` 15 / 0.344431, `Maiwand Lion`
  16 / 0.344281 and `Forbury Gardens` 19 / 0.340212, so the first half of the include rule is
  met on read text. The controlled condition is not: deleting the whole name from the question
  leaves only 2 of 10 of that probe's top ten inside those nineteen and 2 of 10 inside the
  baseline top ten, and every frame-only probe tried gives 0 of 10, the frame head alone, the
  answer-type word alone, the pronominal frame and `English county` alike. The competition
  therefore does not persist when the referent cue is removed, which is what this rule
  requires, and the family is not reproduced by the frame either, so it belongs to neither
  probe. The exclude rule's third clause was also tested and does not fire on this family,
  though it would on the other one: forward, the full subject phrase alone puts 8 of 10 of its
  top ten inside those nineteen and 8 of 10 inside the baseline top ten, which is why the
  name-linked family is carried by `related_name_document_crowding` as a downstream
  description. D-025 is the first unit in which this
  descriptor and the exclusion that D-023 used to reject it are both tested on the
  same ranking and separated by facet. The question carries two cues, and two
  reduced-query probes show they build two disjoint neighborhoods: the referent cue
  `Celtic ruler` alone returns 9 of the 10 period-mismatched Scottish nobility
  passages in its top 20 and 0 of the 4 Roman-Britain context passages, while the
  answer facet `prior to conquest by which empire?` alone returns 3 of those 4 and 0
  of the 10. The descriptor is therefore adopted for the Roman-Britain family, which
  satisfies the include rule's controlled condition because the competition persists
  when the referent cue is deleted, and is deliberately not extended to the Scottish
  family, which the exclude rule's third clause assigns to the primary mechanism
  because the referent cue alone produces it. Two members of the adopted family, at
  ranks 2 and 3, contain none of the referent wording; the rank-1 passage supplies
  the answer string without either gold entity and the rank-6 passage is an
  evidence-bearing substitute, and neither is counted toward the include rule.
- **Note on primary use:** D-029 adopts this name as the *primary* mechanism for
  `5a81ebee554299676cceb16d|dense`, which is why that unit is not listed above as a secondary
  affected unit. This is the first primary use of the name and the first time the project's
  primary inventory grows by promoting an already registered secondary rather than by
  coining a name. The inclusion rule is met on passages read in full rather than on titles:
  of the 42 passages above the bridge hop, 36 carry a film or directing cue, 19 a person-role
  cue, 16 both and 12 the word `italian`, and of the 92 above the answer hop the same counts
  are 77, 48, 41 and 20; not one contains either required subject's name and not one states
  the genre of any film by the queried director. The include rule's controlled condition is
  met in both directions, which is the D-026 standard under pit 19i: deleting the whole
  director name from the question leaves 8 of 10 of its top ten inside the baseline top-42,
  and deleting the descriptive referent instead leaves 8 of 10 inside the top-42 and 6 of 10
  inside the top ten. The third exclusion clause, which assigns a family produced by the
  decisive referent cue to the primary mechanism, is tested and does not fire: a query
  reduced to the director's name puts only 4 of 10 of its top ten inside the baseline top-42
  and 2 of 10 inside the baseline top ten, its own top five being racing drivers and
  footballers of similar name form, and the bare surname gives 3 of 10. What carries the
  primary is that a family-scoped index-side removal is the only intervention of any kind
  that moves both required passages together, and it has a control on its complement:
  dropping the 84 framing-family passages above the answer hop moves 43 / 0.365309 and
  94 / 0.332391 to 4 / 0.365309 and 10 / 0.332391, while dropping only the 8 non-framing
  passages above it moves them to 40 / 0.365309 and 86 / 0.332391. Every query rewrite fails,
  the non-oracle ceiling being 12 / 0.418804 and 28 / 0.390005, and every gold-passage repair
  fails, the ceiling with both required passages ablated being 18 / 0.412468 and
  16 / 0.420530; the two combined still reach only 4 / 0.462879 and 9 / 0.438683. The
  descriptor states which documents compete and why rather than restating a rank, which is
  the footing on which D-018 adopted `compound_two_sided_crowding` and D-027 adopted
  `one_sided_entity_crowding`, so pit 17 is not violated. D-054 settles the question this
  note left open: a name carried in both inventories needs no primary-use contract of its
  own, its primary use being governed by D-043's shared crowding-family contract together
  with this entry's own inclusion rule and exclusion clause. This note records the usage and
  changes no definition, inclusion rule, or exclusion rule.

## `entity_alias_reference_mismatch`

- **Status:** provisional.
- **Definition:** The query and a required passage designate the same entity by
  two different conventional names, such as a personal name against a peerage
  title, an official title, a stage name, or a former name. A retriever with no
  alias resolution therefore obtains no name overlap on that entity even though
  the entity is explicitly named in the query and explicitly present in the
  passage.
- **Include when:** Actual passage text verifies that the required passage
  designates the entity only by the alternative form, the query uses only the
  other form, the two forms are shown to refer to the same entity by a concrete
  source such as the other gold passage, and the resulting absence of overlap is
  verified under the run's actual tokenizer or encoder rather than inferred from
  reading. For a lexical retriever, exact score decomposition must show that the
  affected query tokens contribute nothing to that passage.
- **Exclude when:** The entity is not named in the query at all, in which case
  use `description_only_bridge_entity`; the competing passages concern different
  entities that merely share a name form, in which case use
  `proper_name_homonym_collision`; the two forms already share a scored token
  under the implemented tokenizer; or the mismatch is a punctuation or
  morphology variant of one name, in which case use
  `surface_form_tokenization_mismatch`.
- **Affected units:** `5ac1a3665542994ab5c67daf|bm25`.
- **Decision source:** D-021.

## `peripheral_passage_content_dilution`

- **Status:** provisional.
- **Definition:** Under a whole-passage mean-pooled encoder, sentences of a
  required passage that carry none of the question's constraints measurably
  depress that passage's similarity to the query, so a passage that states every
  query constraint verbatim can still rank far below passages that state none of
  them.
- **Include when:** All four conditions hold. First, the encoder's pooling and
  scoring contract is verified from implementation, not inferred. Second, a
  controlled index-side ablation that replaces the passage's text with a verbatim
  subset of its own query-relevant sentences, adding no new text, materially
  improves its rank on the same unchanged candidate set. Third, a length-matched
  control ablation that instead retains only the passage's non-query-relevant
  sentences does not improve the rank, so the effect is attributable to which
  sentences remain rather than to passage length. Fourth, the passage is verified
  to sit inside the model's sequence limit, so truncation is excluded.
- **Exclude when:** The claim rests on passage length, on reading the passage, on
  score margins, or on any token-level attention or attribution statement without
  the ablation and its length-matched control; the passage exceeds the sequence
  limit, in which case the mechanism is truncation and must be measured as such;
  the retriever is lexical, where length effects belong to the scorer's own
  normalization term and must be established by score decomposition; or the
  ablation improves the rank but the length-matched control improves it as well.
- **Attribution boundary:** This descriptor licenses only the passage-level
  statement that removing the named sentences raises that passage's similarity to
  that query. It does not license any claim that the encoder attended to,
  weighted, or averaged away any token, and it is a diagnostic, not a deployable
  fix, because it requires knowing which passage is required.
- **Affected units:** `5ade69e455429975fa854ec5|dense`,
  `5ae1f596554299234fd04372|dense`, `5a78b209554299148911f93e|dense`, the third scoped to
  `Edward Albee` only, `5a81ebee554299676cceb16d|dense`, `5add67915542992200553af8|dense`, and
  `5ae1801955429901ffe4aec4|dense`.
- **Decision source:** D-023, D-025, D-026, D-027, D-029, D-031, D-035, D-037,
  and D-038.
  D-038 is the ninth application and the seventh pass, and the second unit after D-027 in which
  the gate passes on one required passage only. On `5ae1801955429901ffe4aec4|dense` all four
  include conditions hold on the constraint passage and the descriptor is adopted for
  `Adventures of Superman (TV series)` alone. The contract is verified from implementation and
  that body sits inside the sequence limit at 185 model tokens, of which one seven-word
  sentence carries everything the question asks for. The controlled ablation to verbatim
  subsets of its own query-relevant material moves 173 / 0.225424 to 1 / 0.452921 at 7 words, 1
  / 0.509545 at 15 words, 1 / 0.502081 at 23 words, 4 / 0.383756 at 31 words and 51 / 0.275368
  at 58 words. The length-matched controls that carry no query-relevant word improve nothing at
  any length and move it hundreds of positions the wrong way, 425 / 0.178357 at 9 words, 967 /
  0.129091 at 11 words and 2517 / 0.053330 at 12 words, so the decisive comparison is a matched
  pair rather than a curve endpoint: 7 words of query-relevant material rank 1 / 0.452921 and 9
  words of non-relevant material from the same body rank 425 / 0.178357. D-035's word-level
  decontamination decides the verdict here rather than merely confirming it. Six controls built
  from the non-relevant sentences do improve the rank, to 37 / 0.288547 at 8 words, 135 /
  0.237579 at 16 words, 117 / 0.243064 and 144 / 0.236000 at 24 words, 147 / 0.234285 at 51
  words and 170 / 0.226848 at 40 words, and every one of them retains the query word `Superman`;
  removing just the two words `of Superman` from the 24-word control moves it from 144 /
  0.236000 to 569 / 0.160981. The control curve is not monotone in length either, running 425,
  967, 2517, 135, 117, 144, 170, 172, 147 and 208 at 9, 11, 12, 16, 24, 24, 40, 44, 51 and 57
  words. D-037's directional control holds: the same ablation lifts
  `sponsored by cereal manufacturer` from 2357 / 0.031166 to 1 / 0.889812 while lowering
  `Jerry Siegel and Joe Shuster` from 1510 / 0.119830 to 2535 / 0.064414 and
  `filmed in black-and-white and color` from 168 / 0.267384 to 1617 / 0.099776. The null
  control is reported as a measured residual, the baseline pair reproduced to every printed
  digit and the largest absolute score difference over all 4,937 rows being 5.960e-08. On the
  answer passage the gate FAILS on the second include condition outright, reducing that body to
  the single sentence that states the answer giving 89 / 0.254490 against a baseline of 11 /
  0.345068, and on the third as well, a control retaining only its brand sentence giving 1 /
  0.454983 at 30 words and still improving the rank to 5 / 0.365993 at 26 words after both
  `Rice Krispies` and `Cocoa Krispies` are removed from it word by word, while its other two
  controls give 36 / 0.284072 and 47 / 0.276768. This is the D-025 and D-031 direction and the
  conservative reading is taken. Passing on one side does not win the primary, for the ground
  D-023, D-026, D-027, D-029 and D-035 recorded: the licensed two-sided ceiling is the
  constraint passage alone at 1 / 0.509545 and 12 / 0.345068, and adding the only answer-side
  edit that helps gives 1 / 0.509545 and 6 / 0.376585. One unlicensed gold-targeted pairing
  does double-recover at 1 / 0.509545 and 3 / 0.406656 and is recorded rather than smoothed
  over; it is not licensed because the gate fails on that side, and it is not a deployable
  repair in any case.
  D-037 is the eighth application and the sixth pass, the fourth unit after D-026, D-029 and
  D-035 in which the gate passes on both required passages, and the FIRST PRIMARY USE of this
  descriptor; the unit is therefore not listed as an affected unit above. Every earlier pass
  stopped at secondary on one stated ground, that the ablation ceiling with both required
  passages reduced to their cores still left one of them outside the cutoff, which D-035
  records as 1 / 0.585251 and 7 / 0.460718. On `5ae048a255429924de1b708e|dense` that ground is
  measured and does not hold: reducing both bodies to minimal verbatim subsets of themselves
  gives 3 / 0.469751 and 1 / 0.549310, an 11-word answer-side subset with the constraint side's
  whole first sentence gives 2 / 0.469751 and 4 / 0.450154, and shorter subsets still give 2 /
  0.514763 and 1 / 0.541608, while the same two rows replaced by length-matched controls give
  863 / 0.144759 and 871 / 0.143892 and the two asymmetric cells show each core rescuing only
  its own side, 2 / 0.469751 with 871 / 0.143892 and 864 / 0.144759 with 1 / 0.549310. All four
  include conditions hold on each side, the contract verified from implementation and both
  passages inside the sequence limit at 82 and 57 model tokens; the answer hop moves from 263 /
  0.244736 to 187 / 0.264044 at 45 words, 11 / 0.378848 at 22 words, 2 / 0.469751 at 11 words
  and 1 / 0.514763 at 8 words, against controls of 864 / 0.144759, 1052 / 0.124028, 921 /
  0.137778 and 788 / 0.153279 at 12, 25, 40 and 53 words, and the constraint hop from 39 /
  0.320936 to 3 / 0.450154 and 1 / 0.549310 against controls of 745 / 0.158364 and 803 /
  0.151917. The word-level decontamination D-035 added is applied and holds: restoring the
  single word `film` to the 25-word answer-side control gives 790 / 0.153217 and the year
  `2004` gives 808 / 0.151573, and restoring `film's` to the constraint-side control gives 484
  / 0.199321. D-037 adds two usage records. First, a DIRECTIONAL control: the same ablation
  that lifts a probe matching the retained material lowers a probe matching the removed
  material, `Halle Berry` going from 141 / 0.249922 to 426 / 0.183656 on the answer side and
  `Jennifer Hale` from 31 / 0.307791 to 420 / 0.177707 on the constraint side, which separates
  content from brevity in a second, independent direction. Second, the null control of pit 25d
  is reported as a measured residual rather than as equality: re-encoding each unchanged body
  into its own row reproduces the baseline pair to every printed digit, which is the sense
  D-026, D-029 and D-035 use, while the largest absolute score difference over all 4,937 rows
  is 5.960e-08 on each side, because the batch encode behind the document matrix and the
  single-element encode behind a substituted row are not bit-identical. Two limits are recorded
  rather than smoothed over: the double recovery needs the more aggressive of the two ablation
  levels, the less aggressive pairing giving 12 / 0.378848 and 3 / 0.450154, and the exact word
  count at which the answer hop crosses the cutoff was not bracketed between 11 and 22 words.
  Whether a primary use of this descriptor needs a primary-use contract, given that the
  attribution boundary above calls it a diagnostic rather than a deployable fix, is registered
  as a vocabulary-audit question and is not settled here; no definition, inclusion rule,
  exclusion rule or attribution boundary is changed.
  **Membership, which replaces the running tallies in the paragraphs below and governs wherever
  they disagree:** the gate has been applied nine times, by D-023, D-025, D-026, D-027, D-029,
  D-031, D-035, D-037 and D-038, with seven passes, by D-023, D-026, D-027, D-029, D-035,
  D-037 and D-038, and two documented rejections, by D-025 and D-031.
  D-025 applied the gate and rejected without becoming an affected unit, which is why this line
  had omitted it. The tallies slipped at D-027, whose sentence omits D-026, and D-029 and D-031
  inherited the offset, so each sentence is internally consistent while the chain is not; the
  corresponding sentences in the append-only decision log stay as written and this enumeration
  governs. Per the owner's ruling of 2026-08-05 this registry no longer writes running ordinal
  tallies, only member enumerations, because a tally that omits one member is inherited by every
  later sentence while an enumeration that omits one is visible on the spot.
  D-035 is the seventh application and the fifth pass, and it is the second unit after
  D-026 in which the gate passes on both required passages. On `5add67915542992200553af8|dense` all four
  conditions hold. The contract is verified from implementation: mean pooling, explicit
  row-wise L2 and a 256-token limit, with the two passages at 120 and 82 model tokens. The
  controlled ablation materially improves both, the bridge passage reaching 1 / 0.585251 at 10
  words and 2 / 0.501900 at 14 words from 7 / 0.438223, and the answer passage 6 / 0.460718 at
  20 words from 12 / 0.406772. The length-matched controls that retain only non-query-relevant
  material and keep the entity name improve neither: on the bridge passage 67 / 0.268422 at 16
  words, 61 / 0.271585 at 11 words, 16 / 0.377309 at 22 words and 100 / 0.244156 at 24 words;
  on the answer passage 23 / 0.348350 at 12 words, 42 / 0.298109 at 17 words, 26 / 0.338078 at
  10 words and 27 / 0.331535 at 20 words. **D-035 adds a usage requirement to the third
  condition, at the level of single words rather than sentences.** Two controls did improve the
  rank and were only disqualified once a single query-relevant word was removed from each: the
  bridge passage's alias list gives 6 / 0.466902 at 16 words and the same control without
  `Mafia` and `Mob` gives 11 / 0.407230 at 18 words, and the answer passage's gangster clause
  gives 7 / 0.445466 at 14 words and the same control without `gangster` gives 23 / 0.350442 at
  the same 14 words. D-027 required a control to preserve the entity name; this adds that it
  must also be stripped of every query-relevant word. A construction limit is recorded rather
  than papered over, the same one D-029 met with a parenthetical: on both passages the
  query-relevant material is embedded inside a sentence, an appositive list on one and a
  relative clause on the other, so a sentence-level verbatim subset is not constructible and
  only word-level subsets were available. The gate passing does not win the primary here
  either, the ablation ceiling with both passages reduced to their cores being 1 / 0.585251 and
  7 / 0.460718.
D-031 is the fifth application
  and the second rejection, after D-025, and the first in which the two available forms of the
  third inclusion condition give opposite verdicts. On `5ab48c325542996a3a969f93|dense` the
  answer passage fails the second condition outright: reducing it to its single query-relevant
  sentence gives 26 / 0.318641 against a baseline of 21 / 0.339314, so the controlled ablation
  makes the rank worse, its 12-word verbatim county clause gives 26 / 0.321757, and only an
  8-word truncation reaches 10 / 0.365757, still outside the cutoff, while its four
  length-matched controls at 37, 26, 54 and 38 words give 52 / 0.289974, 556 / 0.135978,
  129 / 0.233163 and 67 / 0.271233. On the bridge passage the ablations do improve the rank,
  from 18 / 0.342168 to 8 / 0.376926 at 52 words and to 1 / 0.741114, 1 / 0.817787 and
  1 / 0.865787 at 16, 13 and 11 words, but the third condition then fails under the D-027
  usage note: the length-matched controls that preserve the entity name and drop the burial
  clause reach exactly the same rank, 1 / 0.649612 at 18 words and 1 / 0.725954 at 14 words,
  and reducing the passage to the name alone gives 1 / 0.643385 at 9 words while the burial
  clause alone gives 6 / 0.483665 at 7 words and the film framing without the name gives
  2711 / -0.002227 at 19 words. The rank tracks the fraction of the passage that is
  query-relevant rather than which sentences remain, which is the brevity direction the
  exclusion names and which D-025 rejected on. D-031 registers a boundary and changes no rule:
  the control this inclusion rule literally describes, retaining only the non-query-relevant
  sentences, is constructible here and gives 2908 / -0.012338, so the literal form would pass
  the gate while the D-027 name-preserving form fails it. The two requirements are in tension
  whenever the question's only content is the entity name, because a name-preserving control
  must then retain query-relevant material; the conservative reading is taken and whether the
  condition can be reworded so the two forms cannot disagree is a vocabulary-audit question.
  The gate stands where the membership enumeration on the `Decision source` line above puts it, and
  passing it has still never won a primary tie-break. D-029 is the fourth application, the
  third pass, and the second unit in which the gate is passed on both required passages,
  after D-026. On the answer passage the ablation to its single query-relevant sentence moves
  94 / 0.332391 to 37 / 0.373376 at 57 words, a further truncation to director, genre and
  writers gives 31 / 0.379862 at 24 words and to director and genre alone gives
  16 / 0.420530 at 14 words, while the three length-matched name-preserving controls built
  from its non-relevant sentences give 171 / 0.298173 at 10 words, 342 / 0.246695 at 16 words
  and 405 / 0.233411 at 23 words. This is the first unit in which the controls do not merely
  fail to improve the rank but move it 150 to 390 positions the wrong way, so the third
  inclusion condition holds in its strongest form so far; dropping only the starring list and
  keeping the rest gives 187 / 0.292076, so the recovered material is the director and genre
  clause and not the cast. On the bridge passage, removing its only non-query-relevant
  material, a four-word birth parenthetical, moves 43 / 0.365309 to 17 / 0.412468, while
  removing four query-relevant words instead gives 37 / 0.374462, removing two name-internal
  words gives 115 / 0.321464, and a fourteen-word control that keeps the birth date and drops
  the role clause gives 58 / 0.353484. D-029 adds one boundary and changes no rule: on that
  passage the control this inclusion rule literally describes, retaining only the
  non-query-relevant **sentences**, cannot be constructed, because its non-relevant material
  is a parenthetical inside a sentence rather than a sentence, so the gate is recorded as
  passing in its nearest constructible form there and whether the third condition should be
  reworded for such passages is a vocabulary-audit question. D-029 also connects the
  descriptor to that unit's primary: reducing the answer passage to its fourteen-word core
  lifts a query consisting only of the queried director's name from 2202 / 0.057835 to
  120 / 0.263144, while reducing it to its non-relevant content pushes that query to 3911, so
  the same peripheral content that depresses the passage also makes the query's one name
  anchor unusable. This is the fourth consecutive unit in which passing the gate does not win
  the primary tie-break, for the reason D-023, D-026 and D-027 recorded: ablating both
  required passages at once still leaves 18 and 16. The gate stands where the membership
  enumeration on the `Decision source` line above puts it. D-027 is the third application, the
  second pass, and the first pass on only one side of a two-candidate unit: on
  `Edward Albee` the ablation to a 17-word query-relevant clause moves 9 / 0.432454
  to 1 / 0.663123, while on `J. M. Barrie` the same ablation moves 8 / 0.434342 only
  to 7 / 0.512680, so the second include condition fails there and the descriptor is
  adopted for the Albee side alone. D-027 adds one usage note and changes no rule:
  a length-matched control must also **preserve the entity name**, or it deletes the
  name together with the non-relevant content and cannot separate content composition
  from name presence. That unit's first four controls each dropped the name and gave
  ranks between 14 and 630 with no relation to length; the decisive pair is
  name-preserving and length-matched at once, removing only the works list at 40 words
  giving 2 / 0.601674 against removing only the awards sentence and keeping the works
  list at 41 words giving 8 / 0.441928. Two 18-word name-preserving controls give
  8 / 0.446975 and 7 / 0.512652 against 1 / 0.663123 for the 17-word ablation. D-027
  is also the third consecutive unit in which passing the gate does not win the primary
  tie-break, for the same reason D-023 and D-026 recorded. The gate stands where the membership
  enumeration on the `Decision source` line above puts it. D-023 is the first
  dilution-shaped claim
  the project accepts. D-013 and D-015 previously recorded every such claim as
  speculation because no controlled text ablation had been run; this entry's
  inclusion rule is the gate that separates the two situations rather than a
  reversal of those decisions. D-026 is the second acceptance and the first unit
  in which the gate is passed on **both** required passages of one unit: the
  bridge hop improves from 6 to 1 when reduced to its own 28-word query-relevant
  sentence and the answer hop from 13 to 8 when reduced to its own 34-word one,
  while every length-matched control fails to improve either, the bridge hop's
  four controls at 31, 39, 70 and 89 words giving 76, 9, 9 and 9 and the answer
  hop's four at 14, 24, 30 and 68 words giving 24, 16, 101 and 23. D-026 records
  two usage notes and changes no rule. First, the control condition is more
  informative when it is run at several lengths rather than one: here the 30-word
  control ranks 101 while the 68-word control ranks 23, so control rank is not
  monotone in length and a single control point could have been read either way.
  Second, passing the gate on both passages still did not win the primary
  tie-break, because the ablations recover one hop each and applying both at once
  leaves the second required passage at 8; that is the same ground D-023 used.
  Between the two acceptances lies D-025, where the gate was applied and
  **rejected** because the control improved the rank further than the ablation,
  so the gate had at that point two passes and one documented failure; the current membership is
  enumerated on the `Decision source` line above.

## `unindexed_title_name_anchor`

- **Status:** provisional.
- **Definition:** The query's discriminative name anchor for a required passage is
  available in a directly matchable form only in that passage's title, which the verified
  implementation excludes from the index, while the indexed body writes the same name in a
  form the implemented tokenizer does not match.
- **Include when:** It is verified that the implementation does not index titles; the
  title contains the query's anchor token or tokens in a form the implemented tokenizer
  matches; and an indexing condition that adds the title measurably improves that
  passage's rank on the complete unchanged candidate set.
- **Exclude when:** The anchor is equally matchable in the indexed body, the
  title-indexing condition is inert or negative, or the claim rests on the title's content
  without running that condition. Both readings of the field name must be tested, as
  D-023 required for `low_information_title`: the indexing reading through the
  title-indexing condition, and the semantic reading through a query reduced to the title
  itself.
- **Affected units:** `5a79b7f6554299029c4b5f6f|bm25` and `5ab8f57b5542991b5579f097|bm25`.
- **Decision source:** D-028, D-030, D-032, D-033, D-039, and D-050.
  D-050 refuses the fold into `minimal_preprocessing_score_distortion` that D-028 registered as
  an open question when it created this entry, so the descriptor stays independent and this
  paragraph records no new affected unit. The ground is the mechanical-separability line D-049
  writes down: which field is indexed is a separable pipeline decision, not another value, side
  or affected passage of the normalization decision that primary already covers. Two further
  grounds are independent of that line. This entry carries a definition, three inclusion
  conditions and three exclusion clauses while that primary has no registry entry at all, so
  folding would move a specified name into an unspecified one; and folding would widen a
  primary D-028, D-030, D-033 and D-034 each record as possibly too broad, which is the reason
  D-028 gave for registering this name rather than folding it. The definition, the inclusion
  rule, the exclusion rule and the affected-units list are unchanged, and the three questions
  this entry's own conditions raise stay open as triage items T-31, T-32 and T-33.
  D-039 records a non-adoption, not an affected unit, and it is the first refusal of this
  descriptor on its **first** exclusion. On `5ae60426554299546bf83019|bm25` all three include
  conditions are met: titles are verifiably not indexed, the constraint gold's title tokenizes
  to exactly `celebrity`, `home`, `entertainment`, all three of them query tokens in matchable
  form, and the title-indexing condition moves that passage from 6 / 18.769969 to 2 /
  23.750585, which is materially positive on the D-032 reading. The first exclusion fires all
  the same: the anchor is equally matchable in the indexed body, whose raw term frequencies are
  `celebrity` 1, `home` 2 and `entertainment` 1, so what title indexing does is amplify an
  anchor that already matched, taking those three to 2, 3 and 2, rather than recover an
  unmatchable one. That is a third distinct route to a materially positive title-indexing
  condition, after D-028, where the anchor existed only in the title, and D-036, where the gain
  was a length-normalization side effect and this descriptor failed its second include
  condition instead. Both readings the D-023 rule requires were run: the indexing reading is
  the condition above and the semantic reading, the question reduced to that title, gives 4 /
  16.437155, or 1 / 21.426914 with the title indexed, so it enters the cutoff and is not what
  refuses the name. Whether this exclusion should be stated as a term-frequency test is
  registered as an audit question.
  D-033 records a non-adoption, not an
  affected unit, and it is the first unit in which the semantic reading is maximal and the
  indexing reading positive while the entry is still refused. On `5abcc96c5542996583600492|bm25`
  the title-indexing condition is measurably positive on the bridge passage, moving it from
  26 / 28.798100 to 18 / 29.565356, and one-sided, the other required passage going from
  115 / 26.074919 to 121 / 26.195125; the semantic reading, that title as the whole query, gives
  1 / 30.558101, the strongest form this entry has recorded. The second inclusion condition
  nevertheless fails: the title `Earl and Edgar McGraw` tokenizes to `earl`, `and`, `edgar` and
  `mcgraw` while the query's anchor token is `mcgraw's`, so the title does not carry the anchor in
  a form the implemented tokenizer matches, and per-token decomposition confirms that the whole
  indexing gain is `earl` rising from 7.923587 to 8.548780 and `and` from 3.752318 to 3.850022,
  with the title's `mcgraw` contributing nothing. The first exclusion fires as well, the indexed
  body writing the same unmatchable bare form, so the anchor is equally unmatchable in body and
  title. Once the query's clitic is normalized the condition becomes a beneficiary of the adopted
  primary rather than an independent mechanism, 2 / 37.789878 becoming 1 / 40.497571, which is the
  D-030 pattern. Whether an entry should still be refused on the form of the anchor when its
  semantic reading is maximal and its indexing reading positive is a vocabulary-audit question.
  D-032 is the second affected unit and only the
  **second materially positive** measurement of the title-indexing condition in this project, D-028
  being the first, so the inert-or-negative results recorded by D-019, D-020, D-021, D-023, D-024,
  D-025, D-026, D-027, D-029, D-030, D-031, D-034, D-035 and D-038 still must not be extrapolated. No global count of
  measurements is asserted here, because the running tallies in this entry and in D-031 disagree by
  one and reconciling them is a bookkeeping matter for the vocabulary audit.
  On `5ab8f57b5542991b5579f097|bm25` all three inclusion conditions hold and none of the three
  exclusions fires: titles are verifiably not indexed; the title `Thomas H. Ince` contains the
  query's anchor tokens in a form the implemented tokenizer matches, while the indexed body writes
  `Thomas Harper Ince` so the query token `h.` scores 0.000000 against it and the anchor is
  therefore not equally matchable in the body; and the title-indexing condition on its own moves
  that passage from 11 / 19.741610 to 6 / 30.547523, a gain of 10.805913 points and five rank
  positions. Both readings were tested as this entry requires, and D-032 records that they
  **disagree with D-028's**. The indexing reading is positive as above. The semantic reading, a
  query reduced to the title itself, gives 6 / 16.787469 rather than D-028's 1, because the string
  `Thomas H. Ince` occurs verbatim in 8 non-gold passages while `Thomas Harper Ince` occurs in
  exactly 1, the required passage itself; the same query with only the middle initial removed gives
  2 / 16.787469 at a bit-identical score. The title here is therefore matchable but not
  corpus-discriminative, and whether this entry should additionally require the semantic reading to
  reach the cutoff, which would turn the word `discriminative` in its definition into an
  operational test, is registered as a vocabulary-audit question rather than settled. The
  descriptor is kept secondary and is the closest competitor to the adopted primary: the
  title-indexing condition alone gives 3 / 31.744369 and 6 / 30.547523 and does not recover the
  pair, because indexing all titles also feeds three of the seven competitors whose own titles
  contain `ince` or `thomas`; it enters the cutoff on both sides only in combination with query
  scaffold removal, at 4 / 22.885192 and 1 / 27.642683. Restricting the title prefix to the two
  required passages does recover both, at 2 / 31.546981 and 5 / 30.556598, but that is a
  third-class intervention requiring prior knowledge of which passages are required and is not a
  deployable repair. D-030 records a non-adoption, not an affected unit, and
  it is the first unit in which both of this entry's first two exclusions fire together. On
  `5a83880e554299123d8c214e|bm25` both required titles do contain the query's anchor, `Suicide
  (1977 album)` and `Ghost Rider (Suicide song)`, but so do both indexed bodies, as `band
  Suicide appearing` and `band Suicide.`, so the anchor is equally matchable in the indexed text
  and the first exclusion applies; and the title-indexing condition on its own is
  inert-to-negative at 78 / 12.352922 and 61 / 12.664186, so the second applies as well. Both
  readings were tested as this entry requires: the indexing reading through that condition, and
  the semantic reading through a query reduced to the title, which gives 1 / 8.935662 and
  4 / 6.855023. The condition turns positive only on top of a query-side possessive
  normalization, moving 1 and 5 to 4 and 1, which makes it a beneficiary of the adopted primary
  rather than an independent mechanism. This is the eighth measurement of the title-indexing
  condition in this project and the seventh inert-or-negative result, so D-028 remains the only
  materially positive one. This is the first unit in this project in which indexing the
  title is materially positive. D-019, D-020, D-021, D-023, D-024, D-025 and D-026 all
  measured that condition inert or negative, which is why the third inclusion condition is
  written as a hard requirement rather than an expectation, and those seven results must
  not be extrapolated to a unit whose gold title is the query's own name. Here the bridge
  gold's title is exactly the queried name, its body writes `Ronald Vaughan "Ron" Joyce`
  so the query's `ron` scores 0.000000 against the indexed text, and prefixing titles into
  the index moves it from 16 / 21.492350 to 2 / 32.480848, the second occurrence of
  `joyce` raising that token's contribution from 11.846012 to 14.876898 and the title
  supplying a matchable `ron` worth 8.029012. The condition is co-necessary rather than
  sufficient: it is present in every non-oracle condition that places both required
  passages inside the cutoff, and on its own it moves the other required passage the wrong
  way, from 8 / 27.226538 to 9 / 27.212243. Both readings were tested as the exclusion
  requires: the semantic reading, a query reduced to that title alone, ranks the passage
  1 / 11.846012, so the title string is highly discriminative and only its exclusion from
  the index is at issue. Whether index-field selection should instead be folded into
  `minimal_preprocessing_score_distortion` is a vocabulary-audit question and is not
  settled here; folding it in would widen a primary already flagged as possibly too broad.

## Maintenance rule

When a new secondary descriptor is adopted:

1. add or update its registry entry in the same change;
2. identify at least one affected unit and decision-log source;
3. state observable inclusion and exclusion rules;
4. do not silently broaden an existing definition; and
5. preserve earlier decision-log entries if the descriptor is later renamed,
   merged, split, or retired.
