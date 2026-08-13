---
status: active
last_updated: 2026-08-06
---

# Reusable Retrieval Failure Review Method

## 1. Purpose and scope

This playbook consolidates the method developed during the `manual_review_v1`
overlap joint review and the subsequent single-note validation pass. It is
intended for later analysis of BM25, Dense, or other passage-retriever failures.

The goal is not to attach a label to a failure quickly, but to answer four
questions:

1. What do the top-ranked passages actually say?
2. Why were they able to score highly?
3. Why did the gold passage not receive an equal or stronger retrieval signal?
4. Does the failure come from the current implementation, from the retrieval
   method itself, from the corpus setting, or from the evaluation contract?

## 2. Four core principles

### 2.0 Temporary scripts and intermediate files must stay in the current workspace

Any temporary script, encoded payload, diagnostic output, CSV/JSON intermediate,
or other helper file created during review must go under `tmp/<task_name>/` in
the current project root. For this project, case-level validation must use
`failure_review/tmp/<case_or_task_name>/` and must not switch to another disk or
to a user directory.

- Do not write project temporary files to `C:\tmp`, system temp, a user profile,
  a Codex cache, a home directory, or any location outside the workspace, unless
  the user has explicitly authorized that specific location.
- If a workspace-local `tmp/` does not exist, it may be created inside the
  current project. If it is not writable, stop and report the blocker; do not
  silently fall back to another disk or directory.
- Invoking a shell or runtime installed on the system drive does not grant
  permission to write project data into its install directory, its cache, or
  system temp. Scripts, payloads, intermediate data, and outputs must still stay
  in the current workspace.
- Use a clear, task-scoped directory name. Before cleanup, resolve and verify
  that the absolute path really lies under the current workspace `tmp/`. Delete
  only the temporary directory this task created; never recursively delete the
  whole workspace `tmp/` or any broader directory.
- Clean up this task's temporary directory only after the formal files have been
  written and have passed cross-validation. If validation fails, preserve the
  working state until the problem is located, so auditable evidence is not lost.

### 2.1 The distractor's body text must be read

Do not guess from a title why a passage ranked highly. The title may be result
metadata only, and it may not even be indexed. For every important distractor,
record at least:

| Field | Question it must answer |
|---|---|
| rank / score | How far above the gold is it? Is it only a small gap near the cutoff? |
| actual text | What information genuinely appears in the body text? |
| matched cues | Which query tokens, entities, roles, or semantic attributes did it match? |
| missing constraints | Which decisive condition from the question does it lack? |
| distractor type | Wrong person, wrong event, related work, generic category, or a complete non-gold answer? |
| corpus provenance | Does it come from the original per-question distractors, or was it introduced by the pooled corpus? |

After reading the text, distinguish three situations:

- **Genuine strong competitor:** the text really does satisfy several important
  conditions, but the person, period, or relation is wrong.
- **Partial match:** it satisfies only one query facet, for example matching only
  `Ireland` or `Commander-in-Chief`.
- **Implementation-induced pseudo-relevance:** it scores highly mainly through
  stop words, punctuation-sensitive tokens, repeated query terms, or
  cross-entity token recombination.

### 2.2 The actual implementation must be inspected

Do not imagine every BM25 or Dense implementation as the same system. Failure
review must be grounded in the actual code and configuration that produced the
run.

Checks common to both:

- Which fields were actually indexed: `text`, `title + text`, or other metadata?
- Do the query and the document use the same preprocessing?
- Is the corpus pooled or per-question?
- What is the deduplication rule? How are same-title collisions handled?
- What are the top-k and the stored window? `not_in_top50` does not mean absent
  from the corpus.

Additional BM25 checks:

- how the tokenizer splits text;
- whether it lowercases;
- whether it strips punctuation;
- whether it removes stop words;
- whether it performs stemming, lemmatization, or Unicode normalization;
- whether it preserves phrases, token order, and entity boundaries;
- whether it expands personal-name initials;
- the BM25 version and `k1`, `b`, `epsilon`;
- whether repeated query tokens are scored repeatedly;
- whether the title genuinely contributes to the score.

Additional Dense checks:

- the embedding model;
- how passages and queries are encoded;
- whether vectors are normalized;
- whether scoring uses cosine, dot product, or another distance;
- whether passages are encoded independently;
- whether a cross-encoder reranker or cross-passage reasoning exists.

### 2.3 Record "observation", "implementation fact", and "causal explanation" separately

Use the following evidence layers:

1. **Observed:** passage text, rank, score, gold missingness.
2. **Verified implementation fact:** confirmed directly from code, dependency
   version, or run configuration.
3. **Reconstructed mechanism:** the result can be reproduced using the actual
   tokenizer or scoring formula.
4. **Supported interpretation:** several pieces of evidence agree, but the
   model's internal state cannot be observed.
5. **Speculation:** not yet verified by implementation inspection, ablation, or
   score decomposition.

For example, when the leading Dense ranks contain many birth-related
biographies, it is acceptable to write:

> The ranking is consistent with broad person and birth-related semantics being
> weighted more strongly than the exact entity names.

Do not instead write:

> Dense internally attends to `born` and ignores the names.

The second sentence claims knowledge of internal attention or feature weights
and normally exceeds the available evidence.

### 2.4 Separate implementation-induced failure from method limitation

One case can contain mechanisms at several levels at once:

| Level | Meaning | Example |
|---|---|---|
| Implementation-induced | Caused or amplified by a current implementation choice | punctuation not stripped, stop words not removed, title not indexed |
| Method-inherent | May persist even after preprocessing improves | BM25 does not understand relation composition, event dates, or entity boundaries |
| Corpus-induced | The retrieval-space setting adds competition | pooling 500 questions introduces more same-name or same-topic passages |
| Evaluation-induced | The gold contract cannot cover a defensible answer | a non-gold passage already fully supports the question's answer |

A useful counterfactual test:

> If preprocessing were corrected, would this distractor still be plausible?

- If not, the failure is mainly implementation-induced.
- If it would, for example a same-named siege from the wrong period, retain a
  method-level secondary mechanism.
- If the passage already answers the question completely, check evaluation
  ambiguity first instead of continuing to call it a distractor.

## 3. Standard review procedure

### Step 1: Fix the analytical unit

Use `(run_id, example_id, retriever)` as the unit key, and record:

- the question and question type;
- the review cutoff;
- both gold titles, the complete gold texts, and their ranks;
- the target retriever and the comparison retriever;
- the pooled/per-question setting;
- all reviewer notes for an overlap unit.

### Step 2: Understand the gold evidence chain first

Answer point by point:

- What bridge does the first gold passage supply?
- What final answer does the second gold passage supply?
- Does the question explicitly name the bridge entity?
- Must the two passages be combined?
- Is there a single passage that already answers the question completely?

Without first understanding the evidence chain, it is easy to mistake a related
passage for the answer, or to mislabel a genuine alternative answer as a
distractor.

### Step 3: Check the top-ranked distractors one by one

Read at least the top 5. If a gold sits at rank 6-20, continue reading every key
passage ranked above it. A suggested worksheet:

| Rank | Title | Score | Body-text evidence | Matched query cues | Missing condition | Preliminary explanation |
|---:|---|---:|---|---|---|---|
| 1 |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |

Do not merely write "top results are related". State how they are related, and
why they still are not the correct evidence.

### Step 4: Build a query-facet and constraint map

Decompose the question into:

- explicitly named entities;
- description-only entities;
- roles and attributes;
- dates and locations;
- actions and relations;
- answer type;
- the conjunction that must hold simultaneously.

Then check which facets each distractor satisfies and which decisive constraint
it lacks. This step separates `query_facet_fragmentation`, partial match, wrong
entity, and complete alternative answer.

### Step 5: Check the actual tokenizer or embedding pipeline

For BM25, expand the query and the key passages with the real tokenizer rather
than judging by human intuition that "these words look the same". For example:

```text
bharatpur,             != bharatpur
commander-in-chief     != commander-in-chief,
barrie?                != barrie,
storming               != stormed
```

Also confirm whether the title is indexed. If only `text` is indexed, title
overlap must not be used to explain the ranking.

For Dense, compare the actual passage semantics, entity names, and relations,
but do not read a cosine score directly as attention on some internal token.

### Step 6: Perform score decomposition when necessary

When "why did an unrelated passage rank this high" remains unclear, rebuild the
scores using the same corpus, tokenizer, dependency version, and parameters, and
output each query token's contribution.

While decomposing, check:

- query-term occurrence counts;
- document term frequency;
- IDF;
- document-length normalization;
- the single contribution versus the total contribution of a repeated query term.

Only when the decomposition reproduces the exported total score may a specific
token contribution be written as established evidence.

### Step 6A: Verify the outcome-determinative factor on the complete candidate set

When several explanations can each raise the gold's own score, comparing gold
scores is not enough. Any query, tokenizer, or text rewrite also changes the
scores of the other candidate passages, so only re-ranking on the same complete
corpus can determine whether a factor genuinely changes the target retrieval
outcome.

Use a controlled factorial diagnostic:

1. First reproduce the original ranking exactly, using the same implementation,
   model, corpus order, and deduplication rule. If the original top results,
   gold ranks, and scores cannot be reproduced, stop making strong causal
   claims.
2. Change exactly one factor at a time, and only a factor supported by body-text
   evidence, for example supplying a description-only entity, aligning one
   answer-type wording, or normalizing one token surface form. Keep the rest of
   the query unchanged.
3. Re-score the complete candidate set, not just the similarity between the
   modified query and the gold.
4. Record the new ranks of all required gold/evidence passages and whether
   top-k recovered as a whole. A single gold's score increase, a single hop
   entering top-k, or the success of a multi-factor rewrite are each
   insufficient to designate one factor as primary.
5. Run A, B, and A+B separately. Only if A alone changes the target outcome and
   B alone does not does A have outcome-determinative evidence; B may be
   retained as a secondary. If only A+B succeeds, record the interaction and do
   not silently credit the success to either single factor.
6. Distinguish a diagnostic oracle rewrite from a deployable fix. Adding the
   hidden bridge answer to the query can diagnose a missing entity anchor, but
   it does not imply that a real user or a production system knows that answer in
   advance.

Once a factorial diagnostic is used for a primary, secondary, or tie-break
judgment, it must become a complete case-level evidence table, rather than
scattered results left in the analysis process or in a single file:

- The table must contain the original baseline, every single-factor condition,
  and every combination condition that affects the conclusion (at minimum A, B,
  A+B). Conditions that were not run must be explicitly marked `not_run` with a
  reason; a blank must not stand in for them.
- Each row must record at least: the condition name, the single factor changed,
  the exact rewrite or preprocessing operation, the complete-corpus ranks of all
  required gold/evidence passages (with scores when available), whether the
  target top-k recovered as a whole, and which explanation that row supports or
  excludes.
- The baseline row must record whether exact reconstruction succeeded, and must
  bind the retriever implementation, model snapshot, corpus size and order,
  deduplication rule, and cutoff. Experiments whose settings differ on these
  points must not be placed in the same factorial comparison for strong causal
  inference.
- The complete table must be written, in content-equivalent form, into both
  `joint_review_notes` in `case_memos_v2.csv` and the corresponding consequential
  decision. Single-factor results must not exist only in the case memo while
  combination results exist only in the decision log, or vice versa; a playbook
  case example cannot substitute for either case-level record.
- After the table, write out the single-factor effect, the
  combination/interaction effect, and the attribution boundary separately. When
  only A+B succeeds, only a compound/interaction interpretation is supported;
  the success must not be silently attributed to A or to B.
- If a case does not need, or cannot run, a factorial diagnostic, state
  `factorial diagnostic not run` explicitly in `joint_review_notes`, together
  with the reason and the other evidence types the current conclusion relies on.

Complete-candidate-set counterfactuals raise the evidential strength of a
mechanism judgment. They do not directly reveal Dense token-level attention, and
they do not automatically generalize to another model, run, or corpus.

### Step 7: Check the comparison retriever and corpus provenance

The comparison retriever helps determine:

- whether the passage genuinely exists and is retrievable;
- whether the failure belongs mainly to lexical or to semantic retrieval;
- whether both methods are limited by the same bridge.

But a better ranking from the comparison retriever cannot by itself prove the
target retriever's internal cause.

For a plausible answer or a strong distractor that appears in the pooled corpus,
also check in the per-question corpus whether it was already a HotpotQA
distractor. This separates an original data issue from competition introduced by
pooling.

Read the two corpus settings according to the backend. For Dense, cosine carries
no collection statistic, so the per-question ranking is the pooled ranking
restricted to the item's paragraphs, and reconstructing it by restriction is
valid. For BM25 it is not: `idf` and `avgdl` are recomputed per index, so the
setting change is a change of scoring function and the two settings can disagree
about which required passage ranks higher. When they disagree, restrict the
pooled scores to the item's paragraphs (C1) before saying anything about the
smaller index; if C1 does not reproduce the per-question order, substitute the
pooled `idf` (C2) and then also the pooled `avgdl` (C3) to see which statistic
carries the effect. See 4.21.

### Step 8: Choose the primary mechanism and secondary descriptors

Recommended tie-break order:

1. If a complete, well-evidenced non-gold answer exists, record evaluation
   ambiguity first.
2. If the implementation and score decomposition support a mechanism directly,
   prefer it over a code that merely describes the shape of the ranking.
3. If one mechanism can explain only one gold while the other gold has an
   independent cause, retain compound coding.
4. Rank, missingness, and cutoff proximity are outcomes and must not stand alone
   as a causal primary.
5. Choose the single most specific, best-evidenced primary; keep other
   independent mechanisms or downstream results as secondaries.

Every secondary descriptor must record all of:

- definition;
- include when;
- exclude when;
- affected unit;
- decision-log source.

### Step 9: Write the joint review and the decision log

A reviewable joint review contains at least:

- the facts both reviewers agree on;
- body-text evidence for the key distractors;
- gold evidence and comparison evidence;
- the confirmed implementation facts;
- the primary and the closest competitor;
- the tie-break rationale;
- the retained secondary mechanisms;
- if a factorial diagnostic was run: the complete baseline / single-factor /
  combination evidence table, the single-factor effect, the combination effect,
  and the attribution boundary;
- if no factorial diagnostic was run: an explicit `not_run` status and reason;
- confidence;
- the taxonomy defect flag;
- the uncertainty that remains unresolved.

When a case produces a consequential decision, `joint_review_notes` and the
decision log must hold the same set of factorial conditions and results. Wording
may be compressed to fit a field, but no single factor, no combination condition
that affects the conclusion, no rank of any required evidence passage, and no
complete-top-k-recovery verdict may be omitted. Until that synchronization is
complete, the case must not move from `in_review` to validated.

## 4. Concrete lessons from the reviewed cases

> **Where the full investigations live.** The subsections below record only the
> distilled, reusable lessons. The complete investigation of each case, including
> the full distractor worksheet, per-token decomposition, every factorial cell,
> the evidence layering, and a runnable reproduction script with built-in
> assertions, is kept as one dossier per analytical unit in
> `manual_review_v1/analysis/per_case_analysis/`. See that folder's `README.md`
> for the required sections and the `<method>_<question_type>_<example_id>.md`
> naming rule. Every newly reviewed case must get its own dossier there; this
> playbook must not be used as the storage location for case-level experimental
> detail.

### 4.1 Am Rong / Ava DuVernay: do not write a Dense semantic neighborhood as an internal fact

The top passages are generic person and birth-related biographies, while the two
explicitly named gold people sit adjacently at ranks 26-27. The defensible
conclusion is that the ranking is consistent with broad person/birth semantics
being overweighted; it cannot be claimed that the embedding was observed to
attend specifically to `born`.

Reusable lessons:

- read the actual biographies and confirm whether a stable semantic
  neighborhood forms;
- distinguish "both entities suppressed together" from "crowding on one entity";
- record a short name-dominated query as an alternative, not as an unverified
  main cause.

### 4.2 Edward Albee / J. M. Barrie: check entity-name failure by real tokens

The implementation indexes body text only and uses lowercase whitespace
tokenization. The query's `j.`, `m.`, and `barrie?` cannot match `james`,
`matthew`, and `barrie,` in the gold text, while `J. Edward Snyder` recombines
`j.` and `edward` across two query entities.

Reusable lessons:

- do not assume the title entered the index;
- name abbreviations, punctuation, and expanded forms must be compared token by
  token;
- an orderless matcher may combine tokens across entities;
- related-document crowding may be only a downstream result of a name-form
  mismatch.

The same unit's two corpus settings disagree about which required passage ranks
higher; 4.21 measures why.

### 4.3 Kanye West / Graduation: first decide whether it is a genuine answer

The `Graduation` text satisfies the Kanye West album, Roc-A-Fella, and Dwele
conditions simultaneously, and it is also an original distractor in the
per-question setting. It is therefore not an ordinary topical distractor
introduced by pooling, but a complete plausible non-gold answer.

Reusable lessons:

- check the strongest distractor against every constraint in the question;
- a complete alternative answer takes precedence over a crowding or
  relation-failure explanation;
- check the per-question result to avoid attributing a pre-existing dataset
  ambiguity to the pooled corpus;
- a gold-title miss does not necessarily equal a practical answer-retrieval
  failure.

### 4.4 Bharatpur: only score decomposition revealed the main implementation problem

Ranks 1-10 are not merely separate matches on India, Ireland, commander, or
siege. The actual decomposition shows that `of` occurs four times in the query,
`the` twice, and `commander-in-chief` twice, and that the current `rank-bm25`
implementation accumulates each occurrence. Large shares of the distractor
scores come from repeated function words. At the same time, punctuation and
word-form differences prevent the gold passages from matching key cues.

Reusable lessons:

- apparent facet fragmentation may be only a downstream ranking pattern;
- check the stop-word policy and the actual scoring behavior of repeated query
  terms;
- use score reconstruction to separate "looks possible" from "verified";
- the wrong officeholder and the 1805 siege, which survive corrected
  preprocessing, should be retained as method-level secondary mechanisms.

### 4.5 Blue / Innocent Records: a substitute passage may replace only one hop of the gold chain

The rank-2 `RGB color model` text supplies the primary-color evidence the
question needs and can therefore replace the annotated Blue passage; but it does
not supply the other hop that Innocent Records is needed for. This does not
constitute a complete top-k alternative chain, and it does not mean retrieval
succeeded.

BM25 score reconstruction also shows that the query's repeated `color` is
accumulated per occurrence while the `colour` in the Blue text cannot match, and
that surface-form differences such as `act`/`act)`, `sales`/`sales.`, and
`achieved`/`achieving` further weaken the gold passage.

Reusable lessons:

- separate "complete non-gold answer", "complete alternative evidence chain",
  and "single-hop substitute";
- an evidence-bearing substitute must not be described loosely as a distractor;
- after finding one replaceable hop, still state explicitly whether the other
  hop is missing;
- use actual score reconstruction for BM25 repeated query terms and
  spelling/punctuation/morphology mismatches; do not decide the main cause by
  intuition.

### 4.6 Tennessee Volunteers: when the query does not specify a version or year, first check whether the gold is substitutable

The question does not say 1984. The 1983, 1985, and statistical-leaders passages
can all supply the Tennessee Volunteers to SEC bridge, so the low rank of the
annotated 1984 passage does not mean that bridge is missing; what the top 5
genuinely lacks is the other hop leading from SEC to Birmingham.

The per-question result already forms a multi-year neighborhood for the same
team. Pooling only inserts one stadium passage at rank 10 and pushes SEC from
rank 10 to rank 11; it does not create the main competitive structure.

Reusable lessons:

- when the query does not specify a year or version, do not treat the annotated
  year or title as an implicit hard constraint;
- before judging gold missingness, check whether other passages supply the same
  bridge;
- a comparative explanation must first be checked against the query itself; do
  not claim that BM25 exploited a year token that does not appear in the query;
- verified mean pooling explains only how the vector is produced; it cannot
  prove that a visible token raised the score, nor that a long passage was
  "diluted" by its other content. Such explanations require attribution or
  controlled text ablation;
- per-question provenance must be checked, so that a slight pooling shift is not
  mistaken for the source of a competitive neighborhood.

### 4.7 Frank Thomas / Big Hurt: a score increase is not outcome determinacy

The question describes Frank Thomas as "the player with seven consecutive .300
seasons" but does not write his name in the query. The player passage resolves
that description to Frank Thomas; the game passage only states that
`Frank Thomas' Big Hurt` is a pinball machine named after Frank Thomas. The
verified Dense implementation scores each passage independently and cannot carry
the entity name resolved in the first passage into the second.

On the same 4,937-passage pooled corpus, the current local model reproduces the
original ranks 10/50 and scores exactly. Complete single-factor re-ranking gives:

| Diagnostic query change | Player gold rank | Game gold rank | Complete top-5 recovery |
|---|---:|---:|---|
| original query | 10 | 50 | no |
| add only the oracle name `Frank Thomas` | 1 | 2 | yes |
| change only `arcade game` to `pinball machine` | 6 | 12 | no |
| add only `type of` | 10 | 53 | no |

`description_only_bridge_entity` therefore has outcome-determinative evidence;
`cross_passage_conjunction_unresolved` records the architectural boundary that
makes an unnamed bridge difficult; `possible_type_mismatch` is a real but
non-determinative wording/evaluation secondary. That the game passage is short
is an observed fact, but it enters the model input in full, and neither
attribution nor text ablation shows that shortness caused a penalty, so
`short_answer_passage_underweighted` must not be used.

Reusable lessons:

- reproduce the original complete ranking exactly before running
  counterfactuals;
- do not substitute "the gold's cosine rose" for "the complete ranking outcome
  changed";
- run single-factor and combination diagnostics over multiple candidate causes,
  and separate independent effects from interaction;
- both required hops must enter the target top-k simultaneously to count as
  complete recovery;
- oracle entity insertion diagnoses an unnamed-anchor failure but is not a
  production fix;
- passage length may only be recorded as an observation; without a length
  ablation it must not be written as a weighting mechanism.

### 4.8 Serri / John Fogerty: a multi-factor rewrite must not pose as a single-factor explanation

Pooled Dense gold ranks are 8/12 and per-question 4/5. The body texts show
different-entity Fogerty passages on the John side, and several non-candidate
people explicitly described as actors on the Serri side. Name disambiguation,
answer-property wording, and their combination must be verified separately and
cannot all be called name collision.

| Condition | John rank | Serri rank | Both top 5 |
|---|---:|---:|---|
| baseline | 8 | 12 | no |
| only `actor` to `actress` | 10 | 2 | no |
| only `actor or actress` | 12 | 10 | no |
| only `John Cameron Fogerty` | 7 | 13 | no |
| names only | 6 | 1 | no |
| inclusive property + full name | 8 | 10 | no |
| profession-aware multi-factor rewrite | 3 | 1 | yes |

Reusable lessons:

- names-only has less context yet improves the result, so
  `low_context_name_query` must not be adopted merely because the query is
  short;
- a single factor recovering one candidate is not the same as complete
  comparison-retrieval recovery;
- when a multi-factor rewrite succeeds but key cells were not run, only a
  compound interaction may be recorded; the result must not be credited to
  profession, gender wording, full name, or syntax;
- the per-question/pooled difference establishes provenance, but corpus setting
  is not a causal category;
- the complete table must enter both `joint_review_notes` and the consequential
  decision in content-equivalent form.

### 4.9 A Summer in the Cage / American Hardcore: a full factorial separates the main cause from residual competition

The formal BM25 indexes paragraph text only, not the displayed title. On the
complete 4,937-passage baseline the two gold ranks/scores are 430/15.585870 and
4067/9.241837, and the formal top 50 is reproduced with zero title/score error.
Per-token decomposition shows that the entire scores of Treehouse and Libocedrus
come from generic question scaffold, while the two golds lose their title/type
word matches because the whitespace tokenizer preserves quotation marks, colons,
and question marks. This phenomenon must not be named title fragmentation on the
basis of the displayed title or partial word hits alone.

Define P as two-sided boundary-punctuation normalization, S as removal of the
eight exactly specified function/scaffold tokens, and T as prepending the title
to the paragraph. The complete 2x2x2 diagnostic on the same candidate set:

| Condition | A Summer rank/score | American Hardcore rank/score | Both top 5 |
|---|---:|---:|---|
| baseline | 430 / 15.585870 | 4067 / 9.241837 | no |
| T | 111 / 17.877157 | 4074 / 9.236677 | no |
| S | 30 / 6.055856 | 4193 / 0.000000 | no |
| S+T | 11 / 8.014693 | 4193 / 0.000000 | no |
| P | 6 / 29.111138 | 30 / 23.670245 | no |
| P+T | 1 / 33.808407 | 15 / 25.957566 | no |
| P+S | 2 / 16.306188 | 14 / 11.471025 | no |
| P+S+T | 1 / 20.598225 | 6 / 13.790434 | no |

P is the strongest single factor, but the complete combination still reaches only
1/6. The actual text shows that the rank-1 All Ages is a documentary about Boston
hardcore and mentions the director of American Hardcore; it supplies no evidence
about A Summer in the Cage and cannot answer the comparison, yet it constitutes
genuine same-topic passage competition. The counterfactual rank 6 being close to
the cutoff is not an observed cutoff mechanism.

Reusable lessons:

- before judging a title-related mechanism, verify whether the title actually
  participates in indexing;
- non-repeated grammar/interrogative scaffold can also lift scores materially,
  and should be recorded separately from repeated-token amplification;
- a full factorial design should preserve the baseline, all cells, single-factor
  effects, interaction effects, and the boundary of untested mechanisms;
- when neither the strongest single factor nor the best combination achieves
  complete recovery, the primary may be the verified preprocessing distortion,
  but it must not be claimed to exhaust the failure;
- residual same-topic competitors must be verified from passage body text and
  retained as secondaries;
- per-question 3/8 versus pooled 430/4067 may be used for provenance judgment,
  but pooling is not a causal category.

### 4.10 Flaming Feather / Montezuma Castle: a quoted phrase does not point to its own source

The question designates its target only by the verbatim epithet
`"dwelling place of the dead"`. That phrase appears literally in just one clause
of the Flaming Feather passage, an article about the production of a 1952
Western; the answer passage, Montezuma Castle, does not contain the phrase at
all and only says "built over the course of three centuries". After exact
reconstruction of the 4,937-passage pooled Dense run (zero-error ordering of the
formal top 50, max abs error 2.384e-07), the two gold complete ranks/scores are
465/0.112206 and 13/0.317347.

Define A as removing the two quotation marks, B as supplying the referent name
`at Montezuma Castle`, C as supplying the source film name
`in the film Flaming Feather`; T as prepending the title into the index and
re-encoding; and D/D2/E as removal probes. Results on the same complete candidate
set:

| Condition | Flaming Feather rank/score | Montezuma rank/score | Both top 5 |
|---|---:|---:|---|
| baseline | 465 / 0.112206 | 13 / 0.317347 | no |
| A | 479 / 0.111678 | 12 / 0.318517 | no |
| B | 453 / 0.114506 | 1 / 0.647072 | no |
| C | 1 / 0.642457 | 99 / 0.197916 | no |
| A+B | 452 / 0.117326 | 1 / 0.651049 | no |
| A+C | 1 / 0.666199 | 128 / 0.184604 | no |
| B+C | 1 / 0.553056 | 2 / 0.505606 | yes |
| A+B+C | 1 / 0.572109 | 2 / 0.499141 | yes |
| T | 526 / 0.098571 | 16 / 0.298440 | no |
| D (query = the quoted phrase) | 106 / 0.219506 | 88 / 0.228047 | no |
| D2 (same, without quotation marks) | 180 / 0.181538 | 67 / 0.230495 | no |
| E (phrase replaced by `dwellings`) | 1180 / 0.049846 | 5 / 0.366752 | no |

Reusable lessons:

- a code whose name contains "quoted" must be tested with an explicit condition
  that checks whether the quotation marks themselves do any work; here A barely
  differs from the baseline, showing that the mechanism is the phrase's semantic
  content, not the punctuation;
- judging whether a code's name is merely misleading and judging whether its
  evidence holds are two different things: when the evidence holds, the primary
  may be retained while `taxonomy_defect_flag=true` records the naming conflict
  and the rename is deferred to the vocabulary audit;
- when a query designates its target through a verbatim quotation, first use a
  probe that reduces the query to that quotation and check whether Dense can
  recover its source; here the source still ranks only 106/4937 while the top
  five are all conceptual-neighborhood passages;
- when single-factor oracle anchors each rescue only one hop and only supplying
  both restores top 5, read that as the architectural boundary of independent
  passage scoring (`cross_passage_conjunction_unresolved`) rather than
  automatically writing it up as a compound with an independent mechanism on
  each side; this holds especially when both sides trace to a single query cue;
- use one removal probe, replacing the decisive cue with a plain noun, to
  separate two competitor families: those that disappear with the cue belong to
  the primary mechanism, and those that remain at the top form an independent
  question-frame family;
- the comparison retriever's success must be explained by its actual
  implementation. Here BM25's rank 1 is not an exact-phrase match, since that
  implementation has no phrase matching; it comes from the single rare
  punctuation-attached token `"dwelling` contributing 7.815653. Writing it as
  phrase matching would misstate both the comparison and the Dense conclusion.

### 4.11 Neil Blair / Prince Andrew: the query may hide a unique cue that the tokenizer destroys

For the question
`What was position of the man who served Prince Andrew from 1990-2001?` the
answer passage is only 17 tokens long: `Captain Robert Neil Blair CVO RN was
Private Secretary and Treasurer to The Duke of York, 1990–2001.` After exact
reconstruction of the 4,937-passage pooled BM25 run (zero-error ordering and
scores for the formal top 50, max abs error = 0), the two gold complete
ranks/scores are 2074/9.070003 and 14/17.955882.

Per-token decomposition shows that the answer passage's entire 9.070003 comes
from the three function words `was`, `of`, and `the`, with **no content token
matching at all**. Four separate layers account for this and must be recorded
separately: the person's name does not appear in the query; the passage
designates by "The Duke of York" the same entity the query writes as "Prince
Andrew", so neither `prince` at idf 5.08 nor `andrew` at idf 5.30 can match; the
passage says "was Private Secretary and Treasurer" rather than `position` or
`served`; and the one genuinely shared discriminating cue, the date span, is
destroyed by the tokenizer, because the query form is `1990-2001?` with a
hyphen-minus plus question mark while the passage form is `1990–2001.` with
U+2013 plus a period. Both `1990-2001?` and `1990-2001` are **absent from the
corpus vocabulary**, so the contribution is exactly 0.

Define P as two-sided boundary-punctuation normalization, E as en/em dash to
hyphen, S as removal of the exact set {what, was, of, the, who, from}, and T as
prepending the title into the index; N as supplying the described person's oracle
name `Neil Blair`, and A as supplying the designation the answer passage actually
uses, `Duke of York`. All 16 P x E x S x T cells and all 4 N x A cells were run
on the same complete candidate set:

| Condition | Neil Blair rank/score | Prince Andrew rank/score | Both top 5 |
|---|---:|---:|---|
| baseline | 2074 / 9.070003 | 14 / 17.955882 | no |
| T | 2168 / 8.974816 | 11 / 19.028574 | no |
| S | 4537 / 0.000000 | 18 / 8.020928 | no |
| E | 2074 / 9.069582 | 14 / 17.955421 | no |
| P | 2130 / 8.912919 | 1 / 25.775418 | no |
| P+S | 4539 / 0.000000 | 1 / 15.901130 | no |
| P+E | 7 / 21.673599 | 1 / 25.773671 | no |
| P+E+T | 9 / 21.444087 | 1 / 27.796855 | no |
| **P+E+S** | **5 / 12.762256** | **1 / 15.901130** | **yes** |
| P+E+S+T | 6 / 12.627217 | 1 / 17.911879 | no |
| N | 1 / 32.297984 | 15 / 17.955882 | no |
| A | 46 / 20.157917 | 2 / 30.042440 | no |
| N+A | 1 / 43.385898 | 3 / 30.042440 | yes |
| D (query = the normalized date span only) | 1 / 12.762256 | 4487 / 0.000000 | no |
| D0 (query = the raw date token only) | 4487 / 0.000000 | 4486 / 0.000000 | no |
| R2 (date span removed) | 1891 / 9.070003 | 12 / 17.955882 | no |

Not run: N x T and A x T (T is inert-to-negative in every cell that was run),
stemming/lemmatization, phrase n-grams, and any production analyzer
configuration.

Reusable lessons:

- **The query may contain a lexical cue that uniquely identifies the gold within
  the whole corpus, yet the tokenizer turns it into a corpus-absent token.**
  Before concluding that "the lexical retriever has no anchor to match", use a
  removal probe that reduces the query to that cue alone: here probe D shows that
  the normalized `1990-2001` occurs in only 1 of 4,937 passages, sends the answer
  passage to rank 1, and leaves every other passage at 0.000000, while probe D0
  shows the raw token scores 0 across the entire corpus. Such probes are
  **non-oracle** evidence and are stronger than any oracle anchor.
- **One surface mismatch may span two independent dimensions at once and must be
  split into two factors.** Here the date differs both in boundary punctuation
  and in the U+2013 character: P alone moves the answer hop from 2074 to 2130,
  which is worse; E alone is entirely inert; only P+E aligns it and reaches 7.
  Running only one of them would wrongly establish that "punctuation is not the
  cause".
- **When `description_only_bridge_entity` is proposed as primary, it must be
  tested with the single-factor oracle-name condition.** Here condition N lifts
  only the answer hop to 1 while the other hop drifts from 14 to 15, the same
  shape as D-020's condition B and the opposite of D-017, where N alone gave 1/2.
  **A satisfied inclusion rule** is not the same as **winning the primary
  tie-break**; in that situation retain it as a secondary plus closest
  competitor, do not keep it as primary merely because the name fits, and do not
  reach over and edit the registry's exclude rule, since boundary rules belong to
  the vocabulary audit.
- **Distinguish "one entity with two names" from "two entities with one name".**
  The former is `entity_alias_reference_mismatch` (Prince Andrew / The Duke of
  York); the latter is `proper_name_homonym_collision` (the fictional character
  "Prince Andrew Alcott" inside Armie Hammer). Their repair conditions and
  evidence requirements differ and must not be conflated.
- **The direction of stop-word removal depends on passage length.** Here S alone
  drives the answer passage to 0.000000, because scaffold was its only match; but
  adding S on top of P+E is the necessary step that completes recovery, because
  it withdraws about 8.9 points from the 17-token answer passage and about 10.5
  points from long competitors. The same factor has opposite signs on different
  baselines, so a complete factorial is required and single-factor results alone
  are not enough.
- **When per-question also fails, pooling can be excluded as the source
  directly.** Here per-question BM25 places the two golds 9th and 10th out of
  ten, showing that the mechanism is fully present in a ten-passage index; corpus
  setting is still only provenance, not a causal category.
- When the recovery condition lands on the cutoff edge, state the fragility
  explicitly: P+E+S puts the answer hop at exactly rank 5, and adding T pushes it
  back to 6, so the primary is "the strongest verified mechanism", not "a
  complete account of the strict cutoff outcome".

### 4.12 Shadows in Flight / Ender's Game: when every factor helps one hop and harms the other

For the question
`How many novels are there in the series of novels of which Shadows in Flight is the tenth novel ?`
the bridge passage supplies the series name and the answer passage supplies the
count. The query names the bridge work but never names the series. After exact
reconstruction of the 4,937-passage pooled BM25 run (zero-error ordering and
scores for the formal top 50, max abs error 0.000000), the answer hop ranks
8/42.931612 and the bridge hop 15/39.521244.

Per-token decomposition shows the answer hop matches **none** of the query's
discriminating tokens, `shadows` at idf 6.999727, `flight` at 5.149023, and
`tenth` at 5.301069; its rank rests entirely on generic book vocabulary and
unfiltered function words, with scaffold supplying 52 percent of its score and
85.3 percent of that scaffold coming from the repeated `in`, `the`, and `of`.
The bridge hop misses `novels`, because its text uses the singular `novel`, and
`series`, because its text carries only `series.` and `series"`.

Define P as boundary-punctuation stripping, M as crude two-sided suffix
stemming, S as removal of {are, how, in, is, of, the, which}, T as prepending
the title, Rc as collapsing the repeated content token `novels`, Rf as
collapsing the repeated `in`/`the`/`of`, X as competitor removal, Q and K as
reduced-query and reachability probes, and N1/N2 as the oracle series and work
names. All 16 P x M x S x T cells and all 4 Rc x Rf cells were run:

| Condition | Answer hop rank/score | Bridge hop rank/score | Both top 5 |
|---|---:|---:|---|
| baseline | 8 / 42.931612 | 15 / 39.521244 | no |
| P | 7 / 43.781416 | 14 / 41.628907 | no |
| M | 16 / 43.066332 | 5 / 48.514878 | no |
| S | 7 / 20.434442 | 5 / 22.101731 | no |
| T | 10 / 42.964314 | 4 / 45.172571 | no |
| PST | 7 / 21.900318 | 1 / 29.552461 | no |
| PMST | 10 / 21.749567 | 1 / 39.451069 | no |
| Rc | 12 / 36.367857 | 6 / 39.521244 | no |
| Rf | 7 / 33.336556 | 11 / 32.156664 | no |
| X1 (drop the near-title competitor) | 8 / 42.941939 | 14 / 39.817754 | no |
| X3 (drop the 3 pooling-introduced rivals) | 5 / 43.148830 | 12 / 39.541961 | no |
| Q1 (query = the work name) | 3887 / 1.869956 | 1 / 15.295021 | no |
| Q5 (query = `novels`) | 5 / 6.563755 | 4187 / 0.000000 | no |
| K1 (query = the series name) | 1 / 11.672885 | 4273 / 0.000000 | no |
| N1 (oracle series name) | 1 / 54.604497 | 20 / 39.521244 | no |
| N2 (oracle work name) | 11 / 44.801568 | 4 / 54.816265 | no |
| N1+N2 | 5 / 56.474453 | 6 / 54.816265 | no |
| N1+N2+S | 3 / 32.107327 | 2 / 33.950399 | yes |

Reusable lessons:

- **"No single factor rescues both hops" is not evidence that the two hops have
  independent mechanisms; look for positive evidence.** Three kinds are available
  here. First, lexical: the two golds' matched query-token sets are nearly
  disjoint, {novels, series, of, which} against {shadows, flight, tenth}, sharing
  only {the, in, is, novel}. Second, sign: six separate factors, M, T, Rc, Rf, N1,
  and N2, move the two hops in opposite directions. Third, reachability: probe Q1
  puts the bridge hop at rank 1 from its own name and probe K1 puts the answer hop
  at rank 1 from the series name, while the series name appears nowhere in the
  query and only inside the bridge passage. Only after all three does the
  antagonism support a conclusion.
- **A removal probe is the cheapest way to falsify a named-distractor claim.**
  The original note called one passage "a strong title-token distractor" and
  explicitly flagged uncertainty about whether it was decisive. Dropping that
  passage from the index moved the result from 8 and 15 only to 8 and 14. One
  probe both answered the reviewer's own open question and disposed of the
  provisional primary. Run it before building any theory around a named
  competitor.
- **A repeated generic content word can be simultaneously the gold's largest
  score component and its worst enemy.** Here `novels` occurs twice in the query,
  supplies 13.127511 of the answer hop's score, its single largest component, and
  supplies 15.559850, 14.541960, and 13.585525 to three purely generic
  competitors, while the bridge hop gets nothing from it because its text is
  singular. Collapsing the repetition therefore improves one hop and worsens the
  other. Report repeated-token effects per hop, never as a single case-level
  direction.
- **Check whether the query's own descriptive frame is itself generic.** The
  phrase "the series of novels of which X is the tenth novel" is instantiated by a
  whole family of passages; reducing the query to `tenth novel` returns five
  non-gold books and no gold. When the frame that is supposed to identify the
  target is shared corpus-wide, the identification burden falls entirely on the
  one discriminating name, and that name may sit in the other passage.
- **When even both oracle anchors together fail, say so and lower confidence
  accordingly.** N1+N2 reaches only 5 and 6; recovery needs N1+N2+S. In D-020 the
  two-anchor condition alone sufficed. A primary chosen in this situation is the
  best-supported structural account, not a demonstrated sufficient cause.
- **Corpus setting is provenance, but provenance can still flip the metric, and
  that must be stated rather than smoothed over.** Unlike the D-021 unit, here
  per-question BM25 places the answer hop at rank 2 and is not a strict Any@5
  failure, and removing only the three pooling-introduced rivals restores rank 5.
  Record that pooling determined whether the cutoff was crossed while the
  mechanism is already fully present in the ten-passage index, and do not promote
  corpus setting to a causal category.
- **A high idf token can contribute exactly nothing.** A space before the final
  question mark made `?` a standalone token with the highest idf in the query,
  8.098947, occurring in 1 of 4,937 passages and in none of the golds or
  competitors. Rank the query tokens by contribution, not by idf.
- **Verify that a per-token decomposition reconciles with the scorer before
  quoting any contribution.** A decomposition that iterates unique query tokens
  understates every repeated one; under `rank-bm25==0.2.2` the answer hop's
  reported total was short by 16.158812 and the scaffold share was wrong. Assert
  that the parts sum to `get_scores` output, and treat a query containing repeated
  tokens as a distinct shape that tooling must be validated against.
- **Corpus titles may be escaped.** Two competitor titles are stored as
  `&quot;J&quot; Is for Judgment` and `&quot;Q&quot; Is for Quarry`. A removal
  probe whose drop list uses real quotation marks silently removes nothing and
  reports a null result that looks like evidence. Assert that every title in a
  drop list exists in the corpus title set.

### 4.13 1920 film series: a controlled text ablation is what turns "dilution" from speculation into evidence

A dense unit had one required passage that stated every constraint of the
question verbatim, including both named actors and the named director, and it
still ranked 32 of 4,937 while passages naming none of those entities filled the
top six. The tempting explanation, that the passage's other content diluted its
embedding, is exactly the claim §2.3 and §4.1 forbid asserting from a ranking.

The way to earn it is a three-part index-side experiment, and all three parts are
required.

1. **Ablation.** Replace that one passage's text with a verbatim subset of its
   own sentences, the ones carrying the question's constraints, adding no new
   text. Re-encode only that passage and re-rank the same unchanged candidate
   set. Here it moved from 32 to 1.
2. **Dose-response.** Run intermediate reductions. Here dropping only the final
   sentence gave 29 and keeping the first four sentences gave 13, a monotone
   curve rather than a single lucky cell.
3. **A length-matched control.** Replace the same passage with a similar-length
   subset of its *non*-relevant sentences. Here 43 model tokens of plot text sent
   it to 50. Without this cell the whole result is consistent with "shorter
   passages score higher" and proves nothing about content.

Also verify the passage sits inside the encoder's sequence limit first, or the
mechanism is truncation and must be measured as truncation instead.

Even with all three parts, the licensed statement stays at the passage level:
removing those sentences raises that passage's similarity to that query. It is
still not a token-level attribution, and because it requires knowing which
passage is required, it is a third kind of intervention alongside non-oracle
conditions and oracle rewrites: a gold-targeted index-side ablation, and not a
deployable fix. Record it as its own class in the condition table.

Two further lessons from the same unit. First, when a descriptor's name contains
a word like "title", test both readings, not one: the indexing reading died under
the title-prepending condition, and the semantic reading died under a reduced
query containing the bare name alone, which ranked both golds first and second.
Second, before adopting a "crowding" descriptor, run the reduced query that
contains only the question's referent cue. If that cue alone reproduces most of
the observed neighborhood, the crowding is produced by the primary mechanism and
is not a separate contributing condition.

### 4.14 General Mills / Robert Smith: enumerate the family above each gold before believing a two-mechanism note

A reviewer note described two competitor families, generic multinational-company
profiles and unrelated people named Smith, and coded the unit as a compound with one
mechanism per gold. The note's own closing sentence flagged the uncertainty.
Enumerating what actually sits above each gold settled it in one pass: all seven
passages above the bridge hop belong to the generic-company family and not one is a
Smith homonym; the two homonyms rank 9 and 11, that is, **below** the gold at 8. Two
removal probes then closed it. Dropping the two homonyms left the bridge hop at rank
8 unchanged; dropping all four name-sharing rivals still gave 12 and 7; dropping the
ten purely generic company profiles while **leaving every name-sharing rival in
place** gave 5 and 2 and was the only condition outside the oracle set that recovered
both hops. One query cue produced one family that suppressed both sides, so there was
no compound.

Reusable lessons:

- **A note that names two families is a hypothesis about which family sits where.
  Enumerate the passages above each required gold and attribute their scores before
  accepting it.** A family can be conspicuous in the top 20 and still rank entirely
  below the gold it is supposed to be crowding out.
- **Build the removal probe as a contrast, not as a single deletion.** Dropping
  family A while keeping family B, and the reverse, is what isolates the
  outcome-determinative family. A single "drop everything above the gold" probe only
  gives the displacement upper bound.
- **An oracle-name condition can deliver its points to the wrong passage, and then
  its failure means nothing.** Here the answer passage tokenizes
  `General Mills, Inc.,` into `general` and `mills,`, while the *other* gold writes
  `founded General Mills in 1856.` and carries the bare `mills`. Appending the answer
  passage's own name therefore gave 9.426700 points to the other gold and exactly
  nothing to the passage it was meant to reach, so the single-factor oracle-name test
  read 9 and 1, which looks like "the anchor is insufficient". One boundary-punctuation
  normalization took the same condition to 2 and 1, and the query-only version of the
  effect is starker: reducing the query to the bare name left the answer passage at
  rank 51, and normalizing took it to 4. **Before interpreting that test, assert that
  the injected anchor is matchable by the passage it names.** This is a precondition
  on a test the project has now run six times; record it, and do not silently reinterpret
  the test's earlier verdicts.
- **A corpus-absent query token can be exactly inert rather than distorting.** The
  final token here was `city?`, absent from the corpus vocabulary and therefore worth
  exactly 0 everywhere. Deleting it reproduced the baseline bit for bit in every digit,
  and normalizing it to `city` still matched neither gold while matching 412 non-golds,
  so normalizing would only have helped competitors. Contrast §4.11, where the
  tokenizer-destroyed token was a corpus-unique cue that sent the gold to rank 1. **The
  cheap discriminator is a one-token removal probe that must come back bit-identical;
  run it before coding any preprocessing mechanism.** Here it, plus a query-side-only
  punctuation condition that left the gold unmoved, plus a mismatch ladder reporting no
  alignable form for any unmatched token, together excluded the whole
  preprocessing-distortion family that D-012, D-014, D-016, D-019 and D-021 had used.
- **The required passage may be the weakest match for the very description meant to
  identify it.** Exactly 12 of 4,937 passages satisfied all three description tokens;
  reducing the query to those tokens put positions 1 to 11 entirely inside that
  satisfying set with the answer passage **last** at 11, because it says "multinational
  manufacturer and marketer" rather than "multinational company" and carries tf 1 where
  the leaders carry tf 3. A description can fail not only by being generic but by
  fitting the target worse than it fits the field.
- **Corpus setting can decide the metric through idf scale rather than through added
  competitors, and the two must not be conflated.** In D-022 and D-023 the pooled and
  per-question `any@5` disagreement reduced to exactly three pooling-introduced rivals,
  and removing them restored the cutoff precisely. Here only two pooling-introduced
  passages sat above the affected gold and removing exactly those two reached rank 6,
  not 5. The driver was that in a ten-document index where six documents are company
  profiles, `idf(multinational)` is 0.421076 against 5.480131 pooled and `idf(smith)`
  is 0.762140 against 5.222190, so the descriptive facet carries almost no weight and
  the name tokens dominate. **When the pooling-removal probe does not restore the
  cutoff, check idf and avgdl before concluding anything.** Corpus setting is still
  only provenance.
- **Report a repeated-family effect per token, not per family.** Removing any one of
  the three description tokens helped the bridge hop and harmed the answer hop, except
  `company`, the least discriminating of the three, whose removal helped both. Ten of
  the nineteen single-factor conditions carried opposite signs across the hops, but
  stating "removing description tokens helps one hop and harms the other" without the
  exception would have been false.

### 4.15 Catuvellauni / Togodumnus: the question's own identifying clue can hurt both required passages

For the question
`This Celtic ruler who was born in AD 43 ruled southeastern Britain prior to conquest by which empire?`
the bridge passage supplies the ruler's identity and his tribe, the answer passage
supplies that tribe's region and its pre-conquest status, and the query names
neither entity. After exact re-encoding of the 4,937-passage pooled Dense run, with
0 of 50 stored titles misordered and a maximum absolute score error of 2.682e-07,
the answer hop ranks 8 / 0.449564 and the bridge hop 115 / 0.222228, so the stored
`not_in_top50` means rank 115 of 4,937.

A Dense unit has no per-token decomposition, so the substitute is a clause-level
removal series over the query plus one reduced query per facet. Sixty-six
conditions were run; these are the load-bearing ones:

| Condition | Answer hop rank/score | Bridge hop rank/score | Both top 5 |
|---|---:|---:|---|
| baseline | 8 / 0.449564 | 115 / 0.222228 | no |
| R2 (delete `Celtic`) | 8 / 0.382436 | 30 / 0.300654 | no |
| R4 (delete the date clause) | 4 / 0.476682 | 138 / 0.196126 | no |
| R9 (delete the whole referent clause) | 5 / 0.449328 | 70 / 0.227445 | no |
| T (titles indexed) | 11 / 0.430058 | 110 / 0.224717 | no |
| Q1 (query = `Celtic ruler`) | 13 / 0.392818 | 31 / 0.338248 | no |
| Q6 (query = the answer facet) | 5 / 0.379224 | 53 / 0.236968 | no |
| Q10 (query = `ruler`) | 547 / 0.083697 | 1 / 0.277850 | no |
| K1 (query = the bridge name) | 2158 / 0.045367 | 1 / 0.703075 | no |
| K2 (query = the answer name) | 1 / 0.532805 | 28 / 0.281346 | no |
| K4 vs K4b (died vs born, same reduced description) | 39 / 0.325903 vs 33 / 0.344949 | 3 / 0.438969 vs 5 / 0.446765 | no |
| Z5 (name-free ceiling, written from the gold's own sentence) | 4 / 0.519406 | 14 / 0.356395 | no |
| N1 (oracle bridge name) | 10 / 0.405082 | 2 / 0.526568 | no |
| N4 (oracle answer name) | 1 / 0.640362 | 66 / 0.255184 | no |
| N6 (both oracle names) | 1 / 0.581589 | 2 / 0.547945 | yes |
| X1 (drop the 3 Scottish rivals) | 5 / 0.449564 | 112 / 0.222228 | no |
| X2 (drop the 4 context rivals) | 4 / 0.449564 | 111 / 0.222228 | no |
| X4 (drop the 3 pooling-introduced rivals) | 5 / 0.449564 | 112 / 0.222228 | no |
| X7 (drop all 107 pooling-introduced rivals above the bridge hop) | 5 / 0.449564 | 8 / 0.222228 | no |
| L1 (bridge keeps its query-relevant sentence) | 8 / 0.449564 | 39 / 0.307062 | no |
| L1c (control: bridge keeps only the other sentence) | 8 / 0.449564 | 18 / 0.367169 | no |

Reusable lessons:

- **On a bi-encoder, the clause-level removal series is what replaces score
  decomposition, and it can show that the identifying clue is net negative.**
  Deleting the entire referent clause here improved *both* required passages, 8 to
  5 and 115 to 70. A description that fails to identify its target is the expected
  finding; a description that also costs the other hop is not, and it is what
  finally separated the architectural reading from "the bridge entity is merely
  unnamed". Delete each clause once and report both hops for every deletion.
- **Two competitor families usually mean two query facets; attribute each family
  with its own reduced query before adopting or rejecting a crowding descriptor.**
  One cue here, `Celtic ruler`, returns 9 of the 10 period-mismatched Scottish
  nobility passages in its top 20 and 0 of the 4 Roman-Britain context passages;
  the answer facet alone returns 3 of those 4 and 0 of the 10. The §4.13 test then
  *splits* the neighborhood instead of rejecting all of it: the family the referent
  cue produces belongs to the primary mechanism, and the family that survives
  deletion of that cue earns its own secondary descriptor. A single "the referent
  cue reproduces the neighborhood" check would have thrown away half the finding.
- **Search the name-free ceiling before calling a failure architectural.** The
  strongest honest counterfactual is not the oracle name but the best question you
  can write without any name, including one built from the required passage's own
  sentence with the name removed. Here that ceiling is 4 and 14, approached
  monotonically at 25, 18 and 15, and it never recovers both hops, while injecting
  both names does at 1 and 2. That is a much stronger statement than "no single
  factor worked", and it is non-oracle in the part that matters.
- **A pooling-removal probe that lands exactly on the per-question rank is the
  cleanest provenance statement available; and on a bi-encoder the idf-scale
  alternative is impossible by construction.** A cosine score contains no corpus
  statistic, so a Dense per-question ranking is exactly the restriction of the
  pooled ranking to that item's own paragraphs — verify it by reconstructing those
  paragraphs and asserting the official order title by title, then say why the
  §4.14 idf check does not apply instead of running it. Here dropping exactly the
  three pooling-introduced rivals returned the answer hop to rank 5, its
  per-question rank, and dropping all 107 above the other gold returned that one to
  rank 8, also its per-question rank and still below the cutoff.
- **The dilution gate is falsifiable, and this is what falsifying it looks like.**
  Keeping the required passage's query-relevant sentence improved it from 115 to 39,
  but keeping only the *other* sentence improved it further, to 18. When the
  non-relevant control beats the relevant ablation, the effect is brevity, the
  include rule's third condition fails in its strongest direction, and no
  length-matched cell can rescue the claim. Report the control row anyway; it is the
  evidence.
- **A verified factual error in the question must be measured, not assumed
  decisive.** The question says the ruler was born in AD 43 while the passage records
  `(d. AD 43)`. Correcting it moved the bridge hop only from 115 to 102, and the born
  and died forms of the same reduced description gave 5 and 3. The error is real,
  belongs in the record, and is not the mechanism.
- **When each of two families alone suffices to push a gold below the cutoff, there
  is no outcome-determinative family.** Dropping either the three Scottish passages
  or the four context passages put the answer hop inside the top five, at 5 and 4.
  That is the additive case, and it is the opposite of §4.14, where exactly one
  family of ten was decisive and the other was inert. Say which of the two shapes
  you have; "crowding" alone does not distinguish them.

### 4.16 2008 Summer Olympics / Summer Olympic Games: a malformed question is a hypothesis, not a finding

- **When the provisional label blames the question's wording, repair the wording as a
  complete factorial and measure it.** This question was genuinely malformed in the
  source data: a duplicated preposition, a double space, an unrepaired relative
  clause, a disagreeing main-clause auxiliary and no final question mark. Repairing
  every one of those defects, across all eight cells of the design, moved the two
  required passages from 6 and 13 to 5 and 12. Supplying the entity's name, which the
  question never contains, moved them to 1 and 2 in each of seven surface forms. A
  visible defect in the query is a hypothesis about the failure, and it costs eight
  cheap query rewrites to find out whether it is the failure.
- **A descriptor whose name is a diagnosis of the question needs both of its readings
  tested, and the second reading is usually the harder one.** The surface reading is
  the grammar; the semantic reading here was that the head noun `the game` is too
  vague to designate anything. The second reading was real and measurable, reaching 2
  and 7 when the head noun was replaced by a category phrase containing no name, and
  it was still not enough. Report the measured size of a real-but-insufficient
  contribution rather than dropping it silently.
- **Test the "this crowding is the primary mechanism's own output" claim in both
  directions.** §4.13 established the forward test: reduce the query to the referent
  cue and see whether it reproduces the observed neighborhood. The reverse test is
  just as cheap and is a genuinely independent check: delete that cue from the full
  query and see whether the neighborhood survives. Here the referent cue alone
  returned 10 of 10 of its top ten inside the baseline top twelve, deleting it left 3
  of 10, and the answer facet alone returned 0 of 10. Two directions that agree
  exclude a crowding descriptor far more firmly than one.
- **Run the length-matched control of a dilution claim at several lengths.** §4.13
  requires a length-matched control so that "shorter scores higher" cannot masquerade
  as "content matters". One control point can be read either way. Here the four
  controls on one gold, at 14, 24, 30 and 68 words against a 34-word ablation, ranked
  24, 16, 101 and 23: the nearest length match was the worst of them and rank was not
  monotone in length at all. A curve of controls falsifies the length explanation;
  a point does not.
- **On a bi-encoder, replacing one row of the document matrix is exactly equivalent to
  re-encoding the corpus with that passage changed - but prove it with a null control
  before using it.** Each passage is embedded independently, so an ablation costs one
  encode instead of the whole corpus, which is the difference between a single
  ablation and a dozen of them. Re-encode the unchanged passage first and check that
  the baseline comes back in every digit; only then read the ablation rows.
- **An anchor that lifts both required passages is the signature that separates a
  description-only failure from an unresolved cross-passage conjunction.** In §4.12,
  §4.14 and §4.15 each name lifted one hop and pushed the other down, and the
  proportion of single factors carrying opposite signs was about half. Here every name
  probe raised both hops, each bare name ranking its own passage 1 and the other 2,
  and only 4 of 19 single factors carried opposite signs. Same question type, same
  backend, opposite structure: count the signs and run both reachability probes before
  choosing between the two codes.
- **The pooled and per-question settings can disagree on `full@5`, not only on
  `any@5`.** The four earlier units where the settings disagreed all had `full@5` 0
  in both. Here both required passages sit at 2 and 3 of the question's own ten
  paragraphs, so the entire failure lives in the pooled setting, and dropping exactly
  the ten pooling-introduced passages above the lower gold returns the ranking to
  those two ranks. This is still provenance and not a mechanism, but the record must
  say which metric moved.

### 4.17 Edward Albee / J. M. Barrie on Dense: a comparison question needs the reduced-query battery, not the oracle-name one

This is the same `example_id` as §4.2 under the other retriever, and it is a reminder
that the unit key includes the retriever: §4.2's tokenization mechanism has no analogue
here and was not carried across.

- **On a comparison question, oracle-name injection is a degenerate factor, because the
  question already names both required passages.** Appending a gold's own title is then
  just token duplication. Here all six oracle conditions failed inside a range of three
  ranks, appending one name gave 7 / 11, appending both gave 8 / 9, and even injecting
  both lifespans verbatim gave 9 / 10. The single-factor oracle-name test that decides
  `description_only_bridge_entity` in §4.7, §4.13 and §4.16 simply cannot be run in that
  form, and reading its failure as "no anchor is sufficient" would be wrong. **Replace
  the augmented-query battery with a reduced-query one**: delete one side of the
  comparison and ask whether the remaining candidate is reachable on its own.
- **Do not assume per-side reachability holds; it can fail on the side the query names
  most effectively.** §4.15 used "each side ranks 1 from its own bare name" as positive
  evidence. Here one side did exactly that, ranking 1 under all five non-oracle
  single-sided queries tried, while the other never reached the top five under any of its
  own five, at 6, 7, 8, 7 and 7. A biography lost to six documents *about its own subject*
  even when the query was nothing but that subject's name. The only query that did reach
  the cutoff on that side, at 5, was an oracle one built from the required passage's own
  formal name form, and it pushed the other side to 3221, so it recovered nothing either.
  When a side fails its own bare name, look at the satellite documents and at that
  passage's content composition, not at the query.
- **Query splitting is the obvious deployable repair for a comparison question, so
  measure it before writing that no repair exists.** Three splittings were tried, the
  full frame with one side deleted, a natural single-sided rephrasing, and the bare
  names. Every one of them recovered one side at rank 1 and left the other outside the
  top five, so the union of the two single-sided top-five lists never contained both
  required passages. That measurement is what licenses the sentence "no deployable
  non-oracle repair exists"; without it the sentence is a guess.
- **Compute the cutoff gap as a score percentage before adopting a near-miss
  descriptor.** Ranks 8 and 9 against a cutoff of 5 look adjacent. The two passages were
  19.351 and 19.701 percent below the rank-5 score, with a gap of 0.067081 separating
  rank 7 from rank 8 — a real cliff between the cutoff region and the golds. The
  acceptances in this project sit between 1.156 and 4.503 percent and the exclusions at
  24.619 and 52.794 percent, so rank distance and score distance disagreed by a factor
  of four here. Rank distance is the misleading one.
- **A length-matched control must also preserve the entity name.** §4.13 and §4.16 built
  toward a curve of length-matched controls; this case adds the other axis. The first
  four controls here deleted the subject's name along with the non-relevant content, and
  produced ranks between 14 and 630 with no relation to length at all — uninterpretable,
  because two things changed. The decisive pair holds both length and name fixed and
  varies only which non-relevant span survives: removing the works list, 40 words, gave
  rank 2, while removing the awards sentence and keeping the works list, 41 words, gave
  rank 8. Ask of every control: besides length, what else did I change?
- **One competitor family can suppress a required passage it shares nothing with, and
  that is what distinguishes one-sided crowding from a compound failure.** The
  lower-ranked candidate here had no name link, no topical link and no competitor family
  of its own; only four non-gold passages in the whole corpus even mentioned it, none in
  the top 50. It failed because the *other* candidate's neighborhood filled the top five
  that both candidates must share. A cumulative removal ladder made this quantitative:
  dropping that family one passage at a time gave 8 / 7, 7 / 6, 6 / 5, 5 / 4, 4 / 3 and
  3 / 2, so the pair entered the cutoff once four were gone, while dropping the one
  unrelated competitor gave 8 / 7 and nothing else. Also record the boundary: under every
  removal the golds' own scores were unchanged, so the claim is that the competitors
  occupied the positions, never that they depressed the golds' similarity.
- **A one-sided competitor family can be the item's own annotated distractors rather than
  a pooling artifact.** Six of this item's eight HotpotQA distractors were built around
  one of the two candidates and held per-question ranks 1 to 6 ahead of the golds at 7
  and 8, so pooled and per-question agreed on both `any@5` and `full@5` and pooling was
  excluded outright. Before attributing a crowding family to the pooled corpus, check
  whether the annotator put it there.

### 4.18 Ron Joyce / Tim Hortons on BM25: split the preprocessing factor by side, and never assume the title field is inert

- **Split every preprocessing factor into its query-side and document-side halves before
  reporting it.** The combined boundary-punctuation factor moved the two required passages
  from 16 and 8 to 7 and 3 here, which reads like "the question needed cleaning". Measured
  separately, the query side reproduced the baseline **bit for bit** and the document side
  reproduced the combined condition bit for bit, because the only query token it changed
  was the trailing `found?`, which occurs in 0 corpus passages against 75 for `found`.
  Reporting only the combined factor would have named a repair that does nothing; the only
  thing that helped was re-tokenizing the corpus. Two extra cells buy that distinction.
- **Indexing the title is not permanently inert. Seven consecutive units measured it inert
  or negative; the eighth was decisive.** Here the bridge gold's title is exactly the name
  the question uses, while its body writes `Ronald Vaughan "Ron" Joyce`, so the query's
  `ron` scores 0.000000 against the indexed text. Prefixing titles moved that passage from
  16 / 21.492350 to 2 / 32.480848, the second occurrence of the surname raising its
  contribution from 11.846012 to 14.876898 and the title supplying a matchable `ron` worth
  8.029012, and the factor appears in **every** non-oracle condition that recovers both
  hops. Whenever a required passage's title is the query's own name anchor, run the
  condition. The rule against assuming the title entered the index still stands; this is
  its mirror image.
- **Price each tokenizer artifact with a single-token gold-targeted repair against a null
  control, and check whether repairing all of them is even sufficient.** Rebuilding both
  gold texts unchanged reproduced the baseline exactly, which is what makes the rest
  readable: one pair of quotation marks was worth 8.247890 points and ten rank positions,
  one semicolon 5.481747 points and six, one derivational mismatch 6.960967 points and
  eight. Repairing **both** punctuation artifacts at once still left the far hop at 7, so
  punctuation was necessary and not sufficient — a conclusion no combined condition could
  have produced. These are third-class interventions and never deployable repairs.
- **A BM25 per-question ranking is not the restriction of the pooled ranking, which is the
  opposite of the Dense property in §4.15.** Cosine carries no collection statistics, so
  the Dense restriction holds; BM25 idf and avgdl both depend on the collection, so it
  fails. Scoring the item's own ten paragraphs with pooled statistics put the golds at 10
  and 7, while the per-question index put them at 3 and 7 — the same ten documents, only
  the statistics changed. That single condition isolates the idf-scale path §4.14
  identified, which §4.14 could not separate from the document set, and it is the cheapest
  way to tell the three corpus-setting paths apart: new competitors, idf scale, and an
  annotator-constructed family. To discuss corpus setting at all, rebuild with
  per-question statistics; do not restrict pooled scores.
- **If one non-oracle condition recovers both hops while supplying no intermediate fact,
  the cross-passage-conjunction reading is falsified even when all its positive evidence
  holds.** All three legs held here: the two hops matched **completely** disjoint query
  tokens, 6 of 18 single factors carried opposite signs, and the missing intermediate fact
  was a name absent from the query and present only inside the other gold, in exactly 2
  corpus passages which are the two golds. Yet punctuation normalization plus title
  indexing placed both inside the cutoff at 2 / 34.444959 and 4 / 32.279538 while carrying
  nothing between passages. Look for a non-oracle route before adopting that name; §4.12,
  §4.14 and §4.15 could not be challenged this way only because none existed there.
- **A passing oracle-name test does not win the primary if a non-oracle condition
  contradicts it.** The un-named entity here is the chain the question describes only as
  the quick service restaurant chain a named person helped found, and five oracle-name
  forms all recovered both hops, with the anchor-matchability precondition verified. It
  still lost, because index-side punctuation normalization alone moved that same un-named
  hop from 8 / 27.226538 to 3 / 32.295791: the descriptive referent was sufficient once one
  tokenizer artifact was repaired, so the missing name was never the binding constraint.
  Oracle evidence ranks below non-oracle evidence even when the oracle test is the one with
  a written contract.
- **Stemming can be negative, and the reason is worth stating.** The question contained
  both `restaurant` and `restaurants`. Stemming merged them into one **repeated** token,
  which `rank-bm25` accumulates per occurrence, doubling the generic category facet for the
  fifteen competitors and pushing both golds from 16 and 8 to 19 and 10. It never entered
  any recovering condition. Report the mechanism, not just that the factor did not help.

### 4.19 Matilda Lutz / Rings on Dense: measure whether the question's one name anchor is usable at all

- **When a question carries exactly one proper name, measure that name's retrieval power
  before interpreting anything else.** Reduce the query to the name alone and ask where the
  passage that contains it ranks. Here the corpus contains the queried director's name in
  exactly one passage, a required one, and that query ranked it 2202 of 4937; the bare
  surname ranked it 4243. Everything else about this case follows from that one number:
  with the only discriminative cue contributing nothing, what remains is the question's
  generic framing, and in a pooled corpus of film pages that framing has hundreds of better
  matches than either required passage.
- **The probe needs two controls or it proves nothing.** A length control, because a
  four-word query might simply be too short: here the four-word descriptive query `Italian
  model and actress` ranked its passage 14, so brevity was not the explanation. And a
  position control, because a name at the start of its own passage may behave completely
  differently from one buried inside it: the two subject-position names ranked their own
  passages 1 and 1, while five further mid-passage names from the same required passage
  ranked it between 533 and 2914. Run both before writing anything about the name.
- **Cross the name probe with a content ablation to see how much of the effect belongs to
  the passage rather than to the name.** Reducing that passage from 88 words to its 14-word
  query-relevant core moved the same bare-name query from 2202 to 120, and reducing it to
  its non-relevant content pushed it to 3911. That separates the two readings partially,
  and the residue is informative: 120 of 4937 is still unreachable, so content dilution
  cannot carry the explanation alone.
- **Give every family-scoped removal probe a complement control.** Dropping the 84
  framing-family passages above the deeper required passage moved the pair from 43 and 94
  to 4 and 10; dropping only the 8 passages that family did not cover moved it to 40 and
  86. Without the second cell the first is just an assertion that the family you chose to
  name is the one that matters. The control costs one extra probe.
- **Deleting a cue can improve the side that cue was meant to help.** Removing the whole
  director clause moved the un-named bridge passage from 43 to 5, inside the cutoff, and
  removing the descriptive referent instead moved the answer passage from 94 to 47. Each
  required passage was better served by a query that omitted the other one's cue, so the
  full question was optimal for neither. Eight of thirteen single factors carried opposite
  signs here.
- **A crowding descriptor can win the primary against a descriptor whose oracle test
  passes, and the argument has a shape worth reusing.** The description-only reading passed
  its single-factor oracle-name test in five forms with the anchor-matchability
  precondition verified in its strongest form, and still lost: its entire support was
  oracle, a non-oracle condition put the un-named passage inside the cutoff on its own, and
  on the other side the query did carry that passage's name. What won was the only
  intervention of any kind that moved both required passages together, a family-scoped
  removal with a control, against a measured ceiling of 12 and 28 for every query rewrite
  and 18 and 16 for every gold-passage repair.

### 4.20 Suicide / Ghost Rider on BM25: price the question's one name token before anything else

- **When a lexical run fails and the question carries exactly one proper name, check first
  whether that name is in the corpus vocabulary at all.** Here the question wrote the band as
  `Suicide's`. Under `text.lower().split()` that is a token occurring in 0 of 4,937 passages,
  so it contributed exactly 0.000000 to every passage, while the corpus form `suicide` occurs
  in 12 passages at an idf of 5.976452 and stands in the indexed body of both required
  passages. Everything else about the case follows from that one fact: with the only
  discriminative cue scoring nothing, the two required passages were left competing on generic
  music-catalogue vocabulary against 59 song and album profiles that match it better.
- **Prove the dead token dead on the whole ranking, not just on the golds.** Delete it from
  the query and compare the complete ordering. Here deleting `suicide's`, and separately the
  question's final token `character?`, reproduced all 4,937 positions bit for bit, 0 order
  mismatches and a maximum absolute score difference of 0.000000. That is a stronger statement
  than a table of unchanged gold ranks, it takes one extra line of code, and it forecloses the
  objection that the token was doing something small somewhere else.
- **The normalization ladder has a possessive blind spot; do not trust `no corresponding
  form`.** Boundary-punctuation stripping cannot reach a word-internal apostrophe and a crude
  suffix stemmer turns `suicide's` into `suicide'`, so an automated P, E, Q, U, M ladder
  reports that the query token aligns with nothing in either required passage, when in fact
  its corpus form is sitting in both of them. Whenever a query token ends in `'s` and the
  ladder reports no alignment, check the bare stem by hand.
- **One missing normalization can produce a false negative and a false positive at the same
  time, and that pairing is the strongest form this primary takes.** The same unhandled clitic
  that reduced the only name to a zero-scoring token also made `brand's`, the head noun of the
  interrogative frame `what brand's comic character`, the highest-idf token in the whole query
  at 7.587919, because it occurs in exactly 2 corpus passages. It gave 7.815653 points, 36.190
  percent of the rank-1 passage's score, to an unrelated song page through the phrase `Russell
  Brand's Got Issues`, and 0.000000 to both required passages. Look for the matching false
  positive whenever you find a false negative of this kind.
- **An oracle condition can pass degenerately: decompose the injected string before reading
  the verdict.** The single-factor oracle-name test appeared to pass here, appending the
  answer-side gold title recovering both required passages. But of its three appended tokens
  one was out of vocabulary and one had term frequency 0 in both passages, so appending the
  single token `Suicide` reproduced both gold scores to 0.000000 and a purely non-oracle
  possessive repair reproduced them to 3.553e-15. The condition supplied nothing the question
  did not already contain, and reading it as evidence of a missing name anchor would have
  inverted the mechanism. This is the companion to the earlier precondition that the injected
  anchor must be matchable by the passage it names: check both what the injection reaches and
  what it actually adds.
- **Run the drop-everything-above cell early, because a removal probe can be insufficient in
  principle.** Dropping every one of the 64 non-gold passages above the deeper required
  passage still left it at 8 and the other at 2. When a required passage's absolute score is
  low enough, deleting its competitors just lets the next ones rise. That single cell settled
  the crowding reading before any family had to be classified, and it costs one probe. Note
  that this is the opposite shape from cases where a family-scoped removal is the only
  intervention that works; both shapes exist and only measurement distinguishes them.
- **A preprocessing factor's effect can live entirely on the query side.** Splitting the
  possessive normalization by side gave both required passages inside the cutoff from the
  query half alone, 1 and 4, while the document half alone was slightly worse than the
  baseline, 70 and 66. An earlier case in this project measured the exact opposite for
  boundary punctuation, where the query half was bit-identical to the baseline and the
  document half carried the whole effect. Split every preprocessing factor by side as a matter
  of routine; the rule is to measure, not to expect one side.
- **Show that the repair is not written for the question.** A rule that strips `'s` is
  suspiciously well aimed at a question containing `Suicide's`. Replacing the tokenizer
  wholesale with a general alphanumeric analyzer, `re.findall` over `[a-z0-9]+` applied blind
  to both sides with no possessive-specific rule, gave 1 and 4 as well. That is the cell that
  turns a case-specific counterfactual into a statement about the pipeline. Say explicitly
  what it does not show: the effect on the rest of the run's questions was not measured.

### 4.21 Edward Albee / J. M. Barrie across settings: for BM25 a corpus setting is a scoring function, and the two settings can disagree about which gold is better

- **Two required passages can swap order between `pooled` and `per_question`, and the
  three-cell control that proves why costs almost nothing.** This unit stores
  `Edward Albee` 6 and `J. M. Barrie` 640 under `pooled`, and 10 and 6 under
  `per_question`. Restricting the pooled scores to the item's own ten paragraphs (C1)
  keeps the pooled order, 6 and 10, so the swap is not the smaller candidate set.
  Rebuilding on the ten paragraphs but substituting the pooled `idf` (C2) already puts
  the two golds back in that order, 5 and 10, and also restoring the pooled `avgdl` (C3)
  reproduces C1 to the last digit. Run C1 whenever the two settings disagree; run C2 and C3 only if C1
  fails to reproduce, since together they partition the effect between the two
  collection statistics.
- **In a ten-document index, document frequency destroys exactly the tokens the case is
  about.** The Albee gold's entire pooled score of 19.520331 comes from `albee`
  7.842862, `playwright` 6.379566, and `edward` 5.297903. In the per-question index
  `albee` occurs in five of ten paragraphs, which is precisely where the classic idf
  returns `log(5.5 / 5.5) = 0`, so the unit's strongest cue is worth nothing; the other
  two are negative and are replaced by the shared `epsilon` floor 0.3989. This is not
  bad luck. HotpotQA supplies distractors about the queried entities, so the
  per-question index is by construction the one place where the question's own entity
  tokens are least discriminative. Check the df of the discriminative tokens inside the
  small index before reading any per-question rank.
- **A better per-question rank can be pure function-word noise, so do not report it as
  reachability.** The Barrie gold matches none of `j.`, `m.`, or `barrie?` in either
  setting, for the name-form reason in 4.2. Its whole score is `a` and `or`, 4.908864
  pooled and 1.454420 per-question, and it overtakes the Albee gold only because `or`
  occurs in just two of the ten paragraphs and keeps a high weight. The top-ranked
  paragraph of that index, `Three Tall Women`, takes 1.7743 of its 2.9310 points from
  `which`, and `lived`, `longer`, and `life,` have df 0 across all ten. Decompose one or
  two per-question scores before believing the ordering means anything.
- **Check the direction of the statistic that did not cause it, because that is what makes
  the attribution exclusive.** Length normalization moves against the conclusion here:
  `avgdl` falls from 90.885 to 61.200, so the 121-token Barrie gold's factor worsens from
  1.2485 to 1.7328 while the 64-token Albee gold's improves from 0.7781 to 1.0343, and
  Barrie overtakes it anyway. Naming the statistic that opposed the outcome is stronger
  than naming only the one that produced it.
- **The Dense contrast is a real asymmetry between the backends and is worth stating in
  any joint review.** Cosine over `all-MiniLM-L6-v2` contains no collection statistic, so
  for Dense the per-question ranking genuinely is the pooled ranking restricted to the
  item's paragraphs, which this project has now verified twice by reconstruction. Under
  BM25 the same words in the same documents are scored differently. `pooled` and
  `per_question` BM25 ranks are therefore not on a common scale, and a passage that
  "moved" between them may not have moved at all.

### 4.22 Harold Godwinson's burial county on Dense: separate what the question is missing from what the passage is about, and price each required fact with a single-fact control

- **When every intervention is one-sided, say so with a Pareto front rather than a list of
  failures.** This unit's two required passages are `Edith Walks`, a documentary-film page whose
  subordinate clause states that the king is buried at Waltham Abbey, and `Waltham Abbey Church`,
  which places that town in Essex; they rank 18 / 0.342168 and 21 / 0.339314 against a rank-5
  score of 0.488627. Forty non-oracle query rewrites were run and none recovers both. Reporting
  that as "no non-oracle condition works" understates it. The informative statement is the front:
  the best result for one required passage is 10 / 0.371487 with the other at 25 / 0.338254, and
  the best for the other is 3 / 0.545094 with the first at 27 / 0.347204. Two corners and nothing
  in between is a structural claim; a list of failed conditions is not.
- **Delete exactly the fact the question needs, keep every other word verbatim, and read the
  price.** Against two null controls that re-encode each passage's own text into its own row and
  reproduce the baseline, deleting the clause `from Waltham Abbey where he is buried` from the
  first passage moves it from 18 / 0.342168 to 49 / 0.291785, while deleting `, Essex,` from the
  second moves it only from 21 / 0.339314 to 23 / 0.336277. One required fact is worth 31 rank
  positions and the other is worth 2 positions and 0.003037 points. This control is cheaper than
  an ablation curve, it changes one thing, and it answers a question no ablation answers: whether
  a passage's rank depends at all on its stating the answer. Run it before building any curve.
- **A missing intermediate fact can be missing as a category rather than as a name.** Adding the
  single generic word `abbey` to the question moves the answer hop from 21 / 0.339314 to
  4 / 0.504249, inside the cutoff, and leaves the other required passage at 18 / 0.357596;
  `church` gives 5 / 0.447542. No gold identifier and no answer string is injected, so the
  condition is non-oracle, yet it presupposes something stated only in the other required
  passage. Classify it as non-oracle, record it as evidence for the cross-passage reading, and
  say explicitly that it is not a deployable repair, because the pipeline has no way to know
  which type word to add.
- **On a bi-encoder, dropping every non-gold passage above a required one proves nothing.**
  Cosine carries no collection statistic, so that removal leaves every score bit-identical and
  the required passages become 1 and 2 by construction; here that cell reads 1 / 0.342168 and
  2 / 0.339314, the same two scores as the baseline. The cell in 4.20 that falsified a crowding
  reading on BM25 works only because removing documents there changes `idf` and `avgdl` and lets
  other passages rise. The Dense analogue that does carry information is the family-scoped probe
  with a complement control: here dropping the 8 name-linked passages gives 10 and 13, dropping
  their 11-passage complement gives 9 and 10, and 17 of the 19 must go before both enter the
  cutoff, so neither family is outcome-determinative.
- **The dilution gate's literal control and its name-preserving control can disagree, and the
  disagreement is diagnostic rather than a defect in the case.** 4.14 added the requirement that
  a length-matched control preserve the entity name. Here the question's only content is that
  name, so a name-preserving control necessarily keeps query-relevant material: the literal
  control retaining only the non-relevant sentence gives 2908 / -0.012338 and would pass the
  gate, while the 18-word and 14-word name-preserving controls give 1 / 0.649612 and
  1 / 0.725954, exactly the rank the 16-word, 13-word and 11-word ablations reach. Take the
  conservative reading, withhold the descriptor, and record which form was used; what the
  disagreement tells you is that the passage's rank tracks its query-relevant fraction rather
  than its sentence composition.
- **A provisional name can be unusable even when the mechanism it points at is real.** The
  provisional primary here asserted that the burial relation was underweighted. On a bi-encoder
  that is a token-level weighting claim and cannot be measured without attribution, so it must
  go; but do not delete it by citing the earlier case that deleted the same name, because there
  the relation tokens were measured completely inert and here they are not. Deleting `buried`
  from the question worsens both required passages, to 21 / 0.333201 and 47 / 0.293346, the
  burial clause is worth 31 rank positions inside its own passage, and the string `is buried`
  occurs in exactly 1 of 4,937 passages, that passage. Emphasising the relation still fails,
  tripling the word giving 21 / 0.326115 and 24 / 0.320425 and six paraphrases never recovering
  both. Write the deletion as "the name is unmeasurable" and keep the measurements, rather than
  as "the relation does nothing".

### 4.23 Thomas H. Ince / Joseph McGrath on BM25: a query token that scores nothing for the required passage and a great deal for its satellites

This is the project's first comparison unit on a lexical retriever and the first case in which a
one-sided preprocessing condition looked like a repair and turned out to be a broken match. Three
practices generalise.

- **Price a name token with a pair of reduced queries that differ by one token and agree on the
  score.** A required passage whose title and the question both read `Thomas H. Ince` while its
  indexed body reads `Thomas Harper Ince` ranks 6 / 16.787469 under a query consisting of that
  name, and 2 / 16.787469 under the same name with the middle initial removed. **The two scores are
  bit-identical**, so all four rank positions come from what the initial gives the competitors, not
  from what it gives the passage. Confirm on the whole ranking rather than on the gold ranks:
  deleting that token from the full question changes 4896 of 4937 order positions with a maximum
  absolute score difference of 8.333161 while both required passages' scores do not move at all.
  This is cheaper than any ablation curve and it changes exactly one thing. The corpus scan that
  explains it is equally cheap: the string occurs in 8 non-gold passages and 0 times in the
  required passage's own body, while the other candidate's surname occurs in exactly 1 of 4,937
  passages, itself.
- **After splitting a preprocessing factor into its query side and its document side, run the cell
  with both sides applied.** Query-side normalization of that initial gives 2 / 26.870093 and
  8 / 19.741610; document-side normalization gives 2 / 26.870094 and 8 / 19.741610; each recovers
  both required passages once the query scaffold is removed, at 2 / 17.888493 and 3 / 16.787469.
  Normalizing both sides so the token realigns returns the baseline at 6 / 26.870094 and
  11 / 19.741610, and with scaffold removal gives 6 / 17.888493 and 7 / 16.787469, bit-identical to
  scaffold removal alone. **Both single sides are positive and the pair is inert**, because
  one-sided normalization destroys a match that otherwise holds; the effect is identical to deleting
  the token. On a one-sided table a repair and a broken match look the same. Note also that the sign
  of such a factor is not additive, which is a third shape after "the effect is wholly document
  side" and "the effect is wholly query side".
- **A lexical removal probe needs a size-matched null control and a statistics-matched control, not
  only a complement.** Dropping documents changes `idf` and `avgdl` as well as the candidate set, so
  the family probe's gain is mixed: here the required passage's score rises from 19.741610 to
  22.167723 when its seven satellites go. Two cheap controls separate the two effects. Dropping the
  same number of highly ranked passages that carry none of the query's name tokens gives
  6 / 26.861098 and 11 / 19.734995; dropping the same number that do carry the shared tokens but all
  rank below the required evidence gives 6 / 26.905808 and 11 / 19.829852, worth 0.088242 points and
  0 rank positions. A counter-example shows why this is not optional: dropping all 31 non-gold
  passages carrying the other candidate's forename lifts that candidate's biography from 6 to 4, and
  **none of those 31 outranks it** — the whole effect is document frequency falling from 32 to 1.
  The statement that gold scores are bit-identical under every removal is a bi-encoder fact and must
  not be carried to a lexical backend.

Two further results are worth reusing. First, a **dead query token whose repair is also worth
nothing**: the question's only statement of the compared property occurs in 0 corpus passages,
contributes exactly 0.000000, and deleting it leaves the 4,937-passage order 0 of 4937 changed; and
normalizing it to the form that does occur, in 7 passages, changes neither required passage, because
neither contains that word. A dead token is not automatically a missed repair. Second, on a
comparison unit **query splitting must be measured before it is dismissed or recommended**: three
splittings, at three budgets each, never return both required passages, because the harder side sits
outside the top five of a query consisting only of its own side, whose top five is five of its own
satellites.

### 4.24 Rose McGowan / Planet Terror on BM25: a surface repair is worth what its deployable form is worth, not what its gold-targeted form is worth

This unit's two required passages fail for the same reason on opposite sides of the index, and the
whole tie-break turns on the gap between repairing one passage and repairing the corpus. Three
practices generalise.

- **Every gold-targeted surface repair needs its corpus-wide twin, and the gap between them is the
  finding.** The answer passage's indexed body reads `Rose McGowan,` while the question reads the
  bare name, so the query's highest-idf content token scores exactly 0.000000 against the one
  passage that satisfies that half of the question. Stripping that single comma inside that passage
  and changing nothing else moves it from 115 / 26.074919 to 5 / 32.133137 and flips `any@5`, worth
  6.058218 points and 110 rank positions. Applying the **identical** repair to every corpus passage
  carrying the same mismatch gives 11 / 31.534653, and a query-aware normalization that touches a
  document token only when its normalized form is a query token gives 14 / 31.630834. The 9 rank
  positions between the first cell and the last are not noise: they are the fourteen other passages
  naming the same person receiving the same repair. Report only the gold-targeted cell and a reader
  will price the comma at 110 positions of deployable gain. This is distinct from the rule that
  gold-targeted interventions are not deployable; the point here is that **how much the deployable
  version is worth has to be measured separately**, and it usually is not the same number.
- **Run the family-scoped removal probe on two baselines: the raw one and the one where the
  preprocessing defect is repaired. They can disagree.** At baseline the name family loses to its
  own complement, dropping the 18 same-name passages above the answer passage giving
  15 / 28.805372 and 73 / 26.630444 against 10 / 29.270483 and 30 / 26.124391 for the other 95,
  with a statistics-matched control at 90 / 26.622223 and a size-matched null control at
  115 / 26.068632. Under a fully normalized pipeline the same family is decisive: dropping the 14
  non-gold passages that name the person, a set definable from the query alone, gives 1 / 25.266887
  and 3 / 15.335047 against a null control's 1 / 25.981076 and 12 / 12.825312, and the cumulative
  ladder crosses the cutoff at the eighth removal. Read only the first state and a real crowding
  mechanism disappears; read only the second and it becomes the primary. It also raises a contract
  question worth registering rather than answering locally: at which baseline is a crowding entry's
  inclusion rule supposed to be evaluated?
- **Price a dead query token twice: once by deleting it across the whole ranking, once by the score
  of the single-token query that repairs it.** The question's only distinctive name is written
  `McGraw's` and occurs in 0 of 4,937 passages; deleting it leaves the 4,937-passage order 0 of 4937
  changed with a maximum absolute score difference of 0.000000, and the same holds for `daughter?`.
  That establishes the token is dead. What it is *worth* is a separate measurement, and the cheapest
  confirmation is that the repair's increment equals the single-token query's own score to the last
  digit: normalizing the clitic moves the passage from 26 / 28.798100 to 2 / 37.789878, an increment
  of 8.991778, and a query consisting only of `mcgraw` gives that passage 2 / 8.991778; the question
  mark is worth 3.520270 against the single-token query `daughter` at 48 / 3.520270; and the two
  repairs are additive at 1 / 41.310149. Two independent routes to the same figure make the pricing
  hard to argue with, and they cost one cell each.

Three further results are worth reusing. First, a preprocessing factor's two sides can repair
**different** required passages and damage each other's, which is a third non-additive shape after
"the effect is wholly document side" and "both sides positive, the pair inert": query-side
punctuation normalization gives 5 / 32.318370 and 134 / 26.074919, document-side gives
38 / 28.345032 and 12 / 31.262470, and both together give 13 / 31.744210 and 14 / 31.262470, a
compromise rather than a sum. Second, **the two scaffold descriptors can be told apart by one pair
of cells** instead of by inspection: deleting only the repeated occurrences of the single repeated
function word is worth 8 rank positions on one required passage and minus 3 on the other, while
deleting the four non-repeated scaffold tokens is worth 9 and 38, so the repeated occurrences are
not the material half. Third, a **single-fact control can show that a required passage's rank is
almost independent of whether it states the fact the question needs**: deleting only the sentence
that links the bridge entity to the answer film, leaving the rest verbatim, moves that passage from
26 / 28.798100 to 34 / 28.265136, eight rank positions, while deleting only the actress's name from
the other required passage moves it 886 positions.

### 4.25 Hlin / Norse mythology on BM25: run the wording factorial on two preprocessing baselines, and run the drop-everything cell on two baselines as well

This unit's provisional primary named a defect of the question, and the question really does have
one: two interrogative words, an auxiliary that disagrees with its verb, and a double space. The
defect is measurable and it is not the mechanism. Three practices generalise.

- **A wording-repair factorial has to be run at baseline preprocessing and again with the
  preprocessing defect repaired, and the grammatically correct repair may be the worst cell.** Pit
  19k already requires the factorial rather than the single fully-repaired cell. That is not
  enough. Here the A x B x C factorial, where A restores subject-verb agreement, B deletes the
  redundant interrogative frame and C collapses the double space, leaves one required passage at
  exactly 7 / 33.382868 in all eight baseline cells and at exactly 1 / 43.328448 in all eight cells
  under two-sided boundary normalization. Sixteen identical readings is a far stronger statement
  than eight, and only the second set rules out the possibility that the preprocessing defect was
  masking a wording effect. On the other required passage the cell that fixes the grammar is the
  worst of the eight, 545 / 12.232081 against a baseline of 72 / 17.155303, because the corpus
  writes the inflected form in 60 passages and the bare form in 9, and the inflected form is that
  passage's only content match with the question. **Before writing any grammar-repair condition,
  look up the document frequency of both forms.** A third guard: the natural fluent rewrite changed
  four things at once here, one of them creating a new zero-frequency token, so it cannot be
  compared with the baseline at all - which is pit 10 arriving through the front door of a
  condition that looks like a single repair.
- **The drop-everything-above-the-gold cell inherits the two-baseline rule.** Pit 19u says to run
  that cell early because it can rule out every crowding descriptor at once, and 19af says a
  family probe's verdict depends on which baseline it runs against. Those combine: at baseline,
  dropping every one of the 70 non-gold passages above the answer passage still leaves it at
  14 / 17.293278, which on the D-030 reading rules out crowding as a primary. After the
  preprocessing repair only 16 passages sit above it, and dropping those gives 1 / 52.744000 and
  2 / 23.271751. Same cell, opposite conclusion. Run it on both, report both, and say which one
  the tie-break rests on.
- **Choose between the repeated-function-word descriptor and the query-scaffold descriptor with
  two deletion cells, not by inspection.** Delete only the second occurrence of each repeated
  scaffold token; separately, delete only the non-repeated scaffold tokens. Here the two halves
  removed the *identical* number of points from the required passage, because the two tokens
  involved shared an idf, so the entire difference was what happened to the competitors: 35 rank
  positions for the repeated half against minus 5 for the non-repeated one. The score share alone
  said nothing - the rank-9 competitor, a passage with no content relation to the question at all,
  took 100.0 percent of its score from scaffold and split that almost evenly between the two
  halves. The previous unit ran the same experiment and it came out the other way, so the two are
  a matched pair rather than a rule.

### 4.26 Philadelphia crime family / Salvatore Testa on Dense: on a bi-encoder an index-side removal probe is arithmetic, not an experiment

This is the project's first unit whose question contains no proper name at all. The organization
is identified only as `an Italian American Criminal Organization` and the answer entity only as
the hitman it hired; the two required passages rank 7 / 0.438223 and 12 / 0.406772 against a
rank-5 score of 0.476272.

- **On a bi-encoder, every index-side removal probe is an arithmetic identity, not only the
  drop-everything cell.** Cosine carries no collection statistic, so removing documents changes
  no score and a removed set's outcome is fully determined by how many of the removed passages
  ranked above the gold. Nine cells were checked against `rank_after = rank_before - |removed and
  ranked above it|` and all nine agree exactly with every score bit-identical; two *different*
  random 7-passage subsets of the same pool give the same answer-hop rank of 5. 4.22 records that
  the drop-everything cell is an identity and offers the family probe with a complement control as
  the discriminating alternative - **that alternative is an identity too**, because the family and
  its complement differ only in size. The consequence is not subtle: on this backend a crowding
  descriptor cannot be given primary-level evidence at all, and the cumulative removal ladder that
  the near-miss descriptor has weighed as counter-evidence since 4.12 is unavailable in principle.
  On BM25 none of this holds, because removing documents there moves `idf` and `avgdl`.
- **What does carry information on Dense is the query-side cue test, because it changes the
  scores.** Compare each state's top ten against the baseline top ten and against the family read
  from text. Here the referring description alone gives 9 of 10 and 6 of the 7 person biographies,
  deleting that description gives 0 and 0, deleting only its demonym half gives 2 and 1, and the
  answer frame alone gives 0 and 0. Both directions agree, so the competing family is produced by
  the question's own referring expression and is downstream of the primary rather than beside it.
- **Run a full factorial on the question's referring expression, not on its grammar.** 4.16 and
  4.25 ran wording factorials on malformed questions and found them inert. This question is
  well formed; what is underdetermined is which words name the required entity. A 2x2x2x2 over
  keeping `Italian`, keeping `American`, writing `Mafia crime family` instead of `Criminal
  Organization`, and inserting `gangster` locates two defects binding on *different* required
  passages: the head-noun change alone gives 3 / 13, the demonym deletion alone gives 15 / 5, and
  the two together give 1 / 0.585624 and 4 / 0.510640. Mean single-factor rank deltas are -1.12
  and +6.00 for the demonym's first half, -0.12 and +1.25 for its second, -7.88 and +0.75 for the
  head noun and -2.38 and -2.75 for the role word, so three of four factors carry opposite signs
  and **the half that actually discriminates the question's constraint is very nearly inert.** The
  demonym's sign on one required passage reverses with the head noun, 7 / 12 to 20 / 10 under one
  and 3 / 13 to 1 / 7 under the other, so a single baseline reports that factor backwards.
- **Slice the refutation path of 4.18 by whether a condition leaves the referring expression
  intact.** Read literally, seven non-oracle conditions here recover both required passages, which
  by that rule would refuse the description-only reading. The discriminating partition is that of
  the 35 conditions keeping `Italian American Criminal Organization` verbatim, the only ones
  recovering both are oracle injections and **not one is non-oracle**, while all seven non-oracle
  recoveries replace that expression and none keeps the demonym `Italian`; the
  constraint-preserving variant that changes only the head noun gives 3 / 13 and fails. In 4.18
  the refuting condition was index-side and left the query untouched, which is what showed the
  description as given to be sufficient. Also report the margin: two of these conditions differ
  only in the order of two role words and land on 1 / 6 and 1 / 5.
- **A length-matched control has to be decontaminated word by word, not sentence by sentence.**
  4.17 added that the control must keep the entity name. Here two controls that satisfy the
  sentence-level wording still improve the rank - an alias list at 6 / 0.466902 and a role clause
  at 7 / 0.445466 - and each is disqualified only after a single query-relevant word is removed
  from it, giving 11 / 0.407230 and 23 / 0.350442. Before trusting a control, read it word by word
  and ask which of those words the query also contains. Related construction limit: when the
  query-relevant material is embedded inside a sentence, an appositive list or a relative clause,
  a sentence-level verbatim subset cannot be built at all and only word-level subsets are
  available; record that rather than pretending the literal rule was met.
- **A description can be present verbatim in the required passage, be near-unique in the corpus,
  and still not identify it.** The bridge passage's indexed body contains `is an Italian American
  criminal organization` word for word and exactly 2 of 4,937 passages contain that string. As a
  query on its own it ranks that passage 1 / 0.541525; inside the full question it ranks
  7 / 0.438223. The same description is a net liability for the other required passage, whose rank
  improves by seven positions when its demonym half is deleted. Two single-fact controls make the
  point from the other side: deleting the whole answer clause from the answer passage *improves*
  it, 12 / 0.406772 to 6 / 0.463775, and the passage's own statement of the bridge relation is
  worth 0 rank positions. Price the description before interpreting anything about the neighbours.

### 4.27 Ade Edmondson / Bad News on BM25: split a punctuation factor by character, and do not read a positive title-indexing cell as a title anchor

Two lessons, both of them about reading a positive result too quickly.

**A thorough normalization can be worse than a one-character one.** Pits 19p, 19v and 19ac
require a preprocessing factor to be measured on the query side, on the document side and on
both. That is still not enough when the query and the gold write *the same punctuation-bearing
surface form*, because then the punctuation is part of a high-idf anchor rather than noise.
Here the query's quoted title tokenized to `"the`, `young` and `ones"?`; the last occurred in 0
of 4,937 passages and contributed exactly 0.000000, while the corpus form `ones"` occurred in 5
passages at an idf of 6.798853, the highest available to the question. Stripping only the
trailing question mark moved the required passage from 6 / 19.630966 to 2 / 25.786297, worth
6.155330248 points and 4 rank positions and exactly the score a query of the single token
`ones"` gives it, the two agreeing to 8.882e-16. **Stripping the quotes as well was negative**,
11 / 20.256894 on the query side, because boundary stripping dissolves the anchor: df(`ones"`)
falls from 5 to 0 while df(`ones`) rises from 10 to 24, and df(`"the`) falls from 494 to 0
while df(`the`) rises from 4715 to 4726. The three deployable repairs therefore order as
minimal 2 / 25.786297, full boundary stripping 3 / 27.760767, generic analyzer 3 / 27.442933.
Report each character separately, or a negative component hides inside a positive combined
factor and the write-up recommends the wrong fix.

**A materially positive `T` is not evidence that the title is the anchor.** Pit 19q says not to
assume the title-indexing condition is inert; this unit is the second materially positive one
after D-028, moving the required passage from 6 / 19.630966 to 5 / 19.745864 and flipping
`any@5`, and the mechanism is completely different. **No query token appears in either gold
title.** avgdl moves from 90.884950 to 94.023496, the required passage gains 0.114897 and the
passage that had defined the cutoff gains 0.038857, and they exchange places on a margin of
0.020780. That is a length-normalization side effect. Check
`unindexed_title_name_anchor`'s second inclusion condition before adopting it: here the
indexing reading is positive and the entry still fails at the first step.

**A third, smaller one about the record.** `derived/case_results/` is keyed by producer, so
three diagnostic scripts all writing the default `"diagnostic"` key overwrite one another and
`make_repro.py` sees only the last. Give each script its own `source=`.

### 4.28 Pitof / Catwoman on Dense: when the passage's own padding is the mechanism, and what that does to an unusable name anchor

This unit's question carries exactly one proper name, `Pitof`, and that name occurs in 1 of the
4,937 indexed bodies - the very passage the question needs. The two required passages rank
263 / 0.244736 and 39 / 0.320936 against a rank-5 score of 0.396391, and both settings of the
corpus agree, so nothing here is a pooling artefact.

- **On a bi-encoder, ask which of the two terms of a rank you can actually move.** A rank is the
  passage's own score plus the count of passages scoring above it. Every index-side removal probe
  is an arithmetic identity (4.26), so the second term is not experimentally reachable; the only
  intervention that moves the first is a controlled text ablation. That asymmetry is not a
  weakness of the case, it is a fact about the backend, and it should be stated before the
  candidates are weighed rather than discovered while weighing them. Here 22 removal cells all
  match `rank_after = rank_before - |removed and ranked above it|` with every gold score
  bit-identical, and the ablation moves the answer hop's score by 0.225015.
- **The two-sided ablation ceiling is a cell, not a foregone conclusion.** From 4.9 onward the
  dilution gate has passed and still lost the primary, always on the same ground: reduce both
  required passages to their cores and one of them is still outside the cutoff, 1 / 0.585251 and
  7 / 0.460718 at 4.26. Run the cell. Here it gives 3 / 0.469751 and 1 / 0.549310, against
  863 / 0.144759 and 871 / 0.143892 for the same two rows at matched length, and the two
  asymmetric cells confirm the sides are independent. Report the level dependence too: the less
  aggressive pairing gives 12 / 0.378848 and 3 / 0.450154, so the ceiling is a function of how far
  the ablation is taken.
- **Add a directional control to the length-matched one.** 4.11 requires the control to keep the
  entity name and 4.26 requires it to be stripped word by word; both ask whether the control
  fails to improve. A second, cheaper direction asks whether the ablation makes the *removed*
  material harder to find: `Halle Berry` goes from 141 / 0.249922 to 426 / 0.183656 and
  `Jennifer Hale` from 31 / 0.307791 to 420 / 0.177707 under the very ablations that lift the
  query-relevant probes. A brevity effect cannot produce a sign that depends on what the probe
  matches.
- **Before naming an unusable name anchor as its own mechanism, run the same query against the
  ablated passage.** 4.19 established the probe: reduce the query to the name and see where its
  bearer lands. Here that gives 1283 / 0.076500 for a corpus-unique name, 835 places worse than an
  unrelated four-word descriptive control at 448 / 0.230280. Three more cells close the
  attribution rather than leaving it open: the same query gives 1 / 0.391955 against an 8-word
  verbatim subset of that same body and 894 / 0.095909 against a 12-word length-matched control.
  The anchor is not unusable in itself; it is unusable *in that body*. Two names written in both
  required passages give the same reading from a second angle, `Halle Berry` reaching the 42-word
  passage at 9 / 0.354602 and the 60-word one at 141 / 0.249922.
- **A positive title-indexing cell can be decomposed in three cells instead of argued about.**
  4.27 warns that a materially positive `T` need not mean the title carries a name anchor. The
  cheap decomposition is to prepend, to the required rows only, the bare name, then the
  parenthetical alone, then the whole title: 260 / 0.247282 and 26 / 0.333190, then 91 / 0.292896
  and 8 / 0.388039, then 146 / 0.273863 and 8 / 0.387651. The name is close to inert and putting
  it back is negative, so the deployable cell's gain, 125 / 0.273863 and 5 / 0.387651, comes from
  the disambiguator's type words, which are the question's own facets.
- **A crowding family can be real, well evidenced in both directions, and still not be the
  constraint.** The frame here reproduces 6 of the baseline top ten on its own and the referring
  cue 1 of ten, and 8 of ten survive deleting the referring cue, so the family is the frame's.
  Then delete the frame: both required passages get *worse*, 545 / 0.203382 and 937 / 0.150986.
  A cue that produces the competitors can still be the cue the required passages depend on, so
  the two-direction test licenses a composition claim and not a determinacy claim.
- **Report the null control of 4.10 as a residual, not as equality.** Substituting one matrix row
  reproduces the baseline rank and its six printed digits, but the batch encode behind the
  document matrix and the single-element encode behind a substituted row are not bit-identical:
  the largest absolute difference over all 4,937 rows is 5.960e-08 here. Saying "bit for bit"
  when the measurement is 5.960e-08 costs nothing today and misleads the first reader who checks.

### 4.29 Cocoa Krispies / Kellogg's on Dense: when a question carries two coordinated referring expressions, measure each one alone before reading anything else

A bridge question sometimes identifies its unnamed bridge entity twice over, with two
coordinated descriptions rather than one. On a bi-encoder the query is a single vector, so
two descriptions do not add: they can pull that vector apart, and the retrieval outcome can
be worse than either description alone would have produced.

The measurement is cheap and it should come before any factor design, because it decides
which descriptors are even in play:

1. Run each referring expression **alone** and record both required passages.
2. Run the full question with **each expression deleted in turn**, keeping everything else
   word for word.
3. Compare against the full question.

The signature to look for is a clean antagonism: each expression alone places its own
required passage inside or near the cutoff and drives the other one far out, deleting either
one from the question restores its partner's side and destroys the other, and the annotated
question sits between the two, reaching neither. When that pattern holds, three things
follow that are otherwise easy to get wrong.

**Per-side reachability is not in doubt, so a descriptor that says the passage cannot be
reached is the wrong name.** The same probes that show the antagonism also show each side is
reachable from wording drawn from the question itself, which is the leg D-025 established
for `cross_passage_conjunction_unresolved` and the ground on which
`description_only_bridge_entity` should be refused here.

**Both refusal routes for the conjunction descriptor have to be run, not just the one that
looks likely.** The D-026 route asks whether a single anchor lifts both sides; the D-028
route of pit 19s asks whether any non-oracle condition double-recovers. Two earlier landings
refused this name on one route each, so a case where neither fires is a positive result and
not an absence of evidence. Run several anchors, not one: a single anchor that lifts both
sides settles it, and four one-sided anchors are a much weaker statement than five.

**A crowding descriptor needs the forward probe before the read.** The competitor family
above the answer hop can look like a frame family on read text - businesses with locations,
brands with owners - while the frame alone reproduces almost none of it. Run the frame as a
query and count the overlap with the baseline top ten before writing that the frame produced
the family; if the referring cue reproduces it and the frame does not, the third exclusion of
`question_frame_semantic_crowding` fires and the family belongs to the referent, not the
framing.

Two further habits this case reinforces. First, when a dilution gate is measured on both
required passages, **report which side it passes on and read the ceiling on that side
alone**: a two-sided ablation whose second half is unlicensed by the gate is not the gate's
evidence, even when it double-recovers. Second, **price the answer clause itself with a
single-fact control**. Deleting the clause that literally answers the question may move the
passage's rank by nothing at all, which is a stronger and more surprising statement than any
ablation curve, and it tells you immediately that the passage's position is not about the
answer.

### 4.30 BraveStarr / Celebrity Home Entertainment on BM25: a crowding family that only a rule containing the gold can name

When a crowding descriptor's family is determinative, run one more cell before letting it
take the primary: **state the family as a rule that uses nothing but the question, apply it
without exempting the golds, and see what is left in the index.** On the unit that produced
this note the rule "drop every passage whose text names the queried distributor" selected six
passages and one of them was a required gold, so the deployable form of the removal destroys
the evidence it was supposed to expose. What distinguishes a gold from its own name family is
usually written in the *other* gold, which is the cross-passage conjunction restated rather
than an independent condition. This is pit 19ae's question asked about a removal instead of a
repair: 19ae asks what a gold-targeted *repair* is worth once deployed, and this asks whether
a gold-targeted *removal* has a deployable form at all. The cell costs one run.

Two reporting habits go with it. First, when no non-oracle condition recovers both required
passages, report the Pareto frontier's corners **and whether the scores at those corners
moved**: "no condition double-recovers" is much weaker than "at three of the four corners the
passage's score is bit for bit its baseline, so nothing anywhere added a point to it and every
rank gain was a competitor falling below it". Second, when a gold-targeted condition does
double-recover while every deployable one falls short, report it in the boundary section
rather than smoothing it over, and say which slice of the governing pit it turns on.

Three smaller things this case fixed that generalize. A positive title-indexing cell has now
been produced by three different mechanisms - an anchor that exists only in the title, a
length-normalization side effect, and plain term-frequency amplification of an anchor the body
already carried - so check the **body's** term frequencies before reading such a cell as a
title anchor, not just whether the title holds the query's words. A preprocessing factor whose
two one-sided cells are both strongly negative and whose two-sided cell is inert is the same
structure as the case where both one-sided cells are positive, with the sign flipped; the
lesson is that the relation between one side and both sides does not extrapolate, in either
direction. And when a compound punctuation factor is split by character, the deployable
version of the winning component may cost nothing at all in rank, which is now the second such
unit: "the general repair is worse than the minimal one" and "the minimal one does not survive
deployment" are two different findings and both have to be measured.

## 5. Common mistakes

- Reading only the title and not the passage text.
- Assuming the title necessarily entered the index.
- Assuming the tokenizer removes commas, question marks, or dashes.
- Assuming BM25 will match a synonym.
- Asserting from a related Dense topic that the model internally attended to some
  token.
- Calling every passage ranked above the gold an "irrelevant distractor".
- Not checking whether a passage already constitutes a complete non-gold answer.
- Not distinguishing a complete alternative chain from an evidence-bearing
  passage that replaces only one gold hop.
- Mistaking pooled-corpus competition for an original per-question distractor.
- Writing `not_in_top50` as "the passage is not in the corpus".
- Treating a cutoff miss, rank pattern, or retriever identity as a causal label.
- Claiming that the comparison retriever exploited an exact year/version token
  without checking the query.
- Asserting from the mean-pooling implementation fact alone that some token
  raised the score or that extra text diluted the passage embedding.
- Looking only at one gold's rank being near the cutoff, without comparing the
  relevant score gaps and substitutable passages.
- Weighing a crowding reading against a content reading on a bi-encoder without
  first noting that only one of the two can be experimentally moved there.
- Accepting the standing conclusion that a dilution gate cannot win a primary,
  instead of running the two-sided ablation ceiling cell for this unit.
- Reporting a two-sided ablation ceiling without also reporting how far the
  ablation had to be taken to reach it.
- Treating a length-matched control as the only control available, when asking
  whether the ablation demotes a probe matching the removed material is cheaper
  and points a second way.
- Naming an unusable name anchor as a mechanism of its own before running the
  same reduced query against that passage's ablated and control bodies.
- Writing that a single-row substitution reproduces the baseline "bit for bit"
  when what was checked is the rank and six printed digits.
- Forcing one broad mechanism to explain two gold passages that have different
  failure causes.
- Letting a generator replay a recorded measurement without recording which
  retriever produced it. A comparison-retriever condition re-emitted against this
  unit's own retriever is syntactically fine, runnable, and wrong in every figure;
  unlike the conditions a generator cannot rebuild, it is not named as skipped,
  because nothing knows there is anything to say. Record the backend beside the
  call, and refuse to replay a call whose backend is unknown rather than assuming
  the unit's own.
- Reading a shorter cross-case result as a finding when it is a gap in what was
  dumped. Units validated before the dump convention hold only the standard probe
  battery, so any question asked across cases returns systematically less for
  them. Enumerate the units that could not answer, by name, instead of letting
  them drop out of the output.
- Creating a secondary descriptor without recording its definition and
  boundaries.
- Generalizing the problems of one minimal BM25 baseline into an inherent
  limitation of all BM25.
- Looking only at the gold's score rising after a modification, without
  re-ranking on the complete candidate set.
- Silently attributing the success of a multi-factor rewrite to one of its
  factors.
- Treating an oracle diagnostic that contains the gold bridge answer as a
  deployable query rewrite.
- Assuming that quotation marks or the title participated in scoring because the
  code name contains "quoted" or "title".
- Concluding that the two sides have mutually independent mechanisms just because
  no single factor rescues both hops.
- Describing the comparison retriever's success loosely as an exact-phrase match
  without checking whether it supports phrases.
- Concluding that a lexical retriever "has no anchor to match" without checking
  whether the query already contained a unique cue that the tokenizer destroyed.
- Normalizing only punctuation or only Unicode characters and then concluding
  that surface form is not the cause.
- Assuming a descriptor wins the primary tie-break because its inclusion rule is
  satisfied.
- Treating "two designations of one entity" and "two entities sharing one name"
  as the same mechanism.
- Reporting single-factor effects only, without checking whether the same factor
  has opposite signs on different baselines.
- Concluding that two hops have independent mechanisms from the absence of a
  single fix, without lexical, sign, or reachability evidence.
- Quoting a per-token contribution without checking that the decomposition sums
  to the scorer's own output, which silently understates repeated query tokens.
- Building a theory around a named distractor without first running the one
  removal probe that drops it.
- Filtering or removing passages by title without asserting that the titles
  resolve against the corpus, when the corpus stores HTML-escaped titles.
- Ranking query tokens by idf instead of by measured contribution.
- Smoothing over a case where the corpus setting decided whether the cutoff was
  crossed, instead of stating it explicitly as provenance that narrows
  attribution.
- Running a text ablation without a length-matched control, so a content claim
  and a length artifact remain indistinguishable.
- Filing a gold-targeted index-side ablation as a non-oracle condition, when it
  is a third class that injects no answer content but still requires knowing
  which passage is required.
- Testing only one reading of a descriptor whose name names a field, such as
  "title", instead of testing both the indexing reading and the semantic reading.
- Adopting a crowding descriptor without first checking whether the question's
  own referent cue, queried alone, already reproduces the observed neighborhood.
- Treating the passage that outranks the gold as a distractor without checking
  whether it supplies one of the required hops itself.
- Reading a harness self-check line such as "no non-oracle condition recovers
  both hops" as a finding about the case, when it can only report on the factors
  that harness happens to implement.
- Accepting a note's claim that two competitor families each suppress one gold
  without enumerating which family actually ranks above each gold; a conspicuous
  family can sit entirely below the gold it is said to crowd out.
- Running one "drop everything above the gold" removal probe instead of the
  family-versus-family contrast that is what isolates the outcome-determinative
  competitors.
- Interpreting a failed single-factor oracle-name condition without first asserting
  that the injected anchor is matchable by the passage it names; under a punctuation-
  preserving tokenizer the anchor can score for a different passage entirely.
- Coding a preprocessing mechanism around a tokenizer-mangled query token without
  the one-token removal probe that shows whether the baseline changes at all; a
  corpus-absent token can be exactly inert, and normalizing it can help only the
  competitors.
- Treating a pooled-versus-per-question metric split as the "extra rivals" pattern
  without checking whether removing exactly those rivals restores the cutoff; the
  split can instead come from the idf and avgdl scale of the smaller index.
- Relying on a prose rule to enforce a mechanically checkable formatting constraint.
  The prohibition on emphasis inside a `rank / score` cell was recorded in three
  documents and was still violated twice, because it has to be obeyed at the moment of
  writing. State such constraints positively — result numbers are plain text, emphasis
  belongs only on the Condition name and the Both-top-5 verdict — and back them with a
  script that runs as part of landing rather than with another sentence.
- Treating a factual error in the question as the mechanism the moment it is spotted.
  Measure it: correcting a birth date that the gold records as a death date moved the
  affected gold only from 115 to 102, and the two forms of the same reduced description
  gave 5 and 3.
- Reading a content-ablation result without its control, or dismissing the control's
  direction. If the non-relevant control improves the rank *more* than the
  query-relevant ablation, the effect is passage length and the dilution claim is dead;
  no additional length-matched cell can revive it.
- Adopting a descriptor whose definition presupposes explicitly named target entities
  on a question that names none. The fit is superficial and adopting it silently widens
  the definition, which the validation pass forbids.
- Concluding that one competitor family crowded a gold out when each of two families
  alone suffices to do it. Removing either family independently placed the gold inside
  the cutoff here, which is the additive shape and not the single-decisive-family shape
  of §4.14.
- Inferring that pooling harmed a gold because most passages above it were
  pooling-introduced. Removing all 107 of them left that gold at rank 8, exactly its
  per-question rank. Only the removal probe, not the count, licenses a provenance claim.
- Reporting the oracle-anchor result as the whole counterfactual story. Also write the
  best question that injects no name at all, including one built from the required
  passage's own wording minus the name; its ceiling is what bounds the non-oracle
  direction.
- Treating a malformed or ungrammatical question as self-evidently the cause without
  running the repair and measuring it.
- Running only the "complete repair" cell of a wording factorial, so that a small
  positive and a small negative factor cancel and the design is read as inert.
- Running the crowding-origin test in one direction only, when the reverse deletion
  costs one more query and is an independent check.
- Supporting a dilution claim with a single length-matched control, when control rank
  need not be monotone in passage length.
- Substituting one row of a Dense document matrix without first re-encoding an
  unchanged passage as a null control.
- Assuming a pooled-versus-per-question disagreement can only affect `any@5`.
- Running the augmented-query oracle-name battery on a comparison question, where both
  required passages are already named and appending a name is only token duplication.
- Assuming each named candidate is reachable from its own bare name without measuring it;
  a biography can lose to six documents about its own subject.
- Writing "no deployable repair exists" for a comparison question without measuring query
  splitting, which is the obvious one.
- Judging cutoff proximity by rank distance rather than by the score gap as a percentage
  of the rank-5 score; the two can disagree by a factor of four.
- Building a length-matched control that also deletes the passage's entity name, so that
  two things change and the control becomes unreadable.
- Attributing a crowding family to the pooled corpus without checking whether the item's
  own annotated distractors already contain it.

- Reporting a combined preprocessing factor without splitting it by side, so a repair that
  only works on the corpus is written as if cleaning the question would do.
- Assuming the title-indexing condition is inert because earlier cases measured it so,
  instead of running it when a required passage's title is the query's own name anchor.
- Reading a multi-artifact punctuation repair as sufficient without running the combined
  gold-targeted condition that shows it is not.
- Restricting pooled scores to an item's own paragraphs and calling the result the
  per-question ranking; under BM25 the collection statistics change too.
- Adopting the cross-passage-conjunction reading on its three positive legs alone, without
  first checking whether any non-oracle condition recovers both hops while carrying no
  intermediate fact.
- Treating stemming as a strictly helpful normalization, when merging a singular and plural
  query token creates a repeated token that amplifies the competing family.
- Assuming a proper name is the strongest anchor in a dense query without measuring it; a
  name that is nearly unique in the corpus can still be unreachable for a bi-encoder.
- Running the bare-name probe without a length control and a subject-position control, so
  an unreachable name and a too-short query cannot be told apart.
- Reporting a family-scoped removal probe with no complement control, which leaves the
  choice of family unfalsifiable.
- Reading a cue deletion that helps the other required passage as noise, instead of
  recording it as an antagonistic single-factor effect.
- Assuming lower case or a missing accent is a surface-form defect on a tokenizer that
  lower-cases and strips accents, where both are bit-identical no-ops.
- Extending a name-position finding measured on one passage into a claim about how the
  encoder treats names in general.
- Reading a possessive query token as if it were the bare name, on a tokenizer that splits on
  whitespace only, where the two are different tokens and the possessive form may occur in no
  corpus passage at all.
- Trusting an automated normalization ladder's `no corresponding form` verdict on a token
  ending in `'s`, where a word-internal apostrophe is out of reach of boundary stripping and a
  crude stemmer produces a form that still matches nothing.
- Reading a passing oracle-name condition as evidence of a missing anchor without decomposing
  the injected string, when its whole effect on the required passages may come from a token the
  question already contains in another surface form.
- Classifying competitor families before running the cell that drops every passage above the
  required one, which can show that no removal of any composition would have been sufficient.
- Reporting a preprocessing factor as a single number without splitting it into its query-side
  and document-side halves, when either side alone can carry the entire effect.
- Presenting a normalization counterfactual as a pipeline fix without also running a generic
  analyzer that contains no rule written for this question.
- Comparing a BM25 unit's `pooled` and `per_question` ranks as if a passage had moved, when
  the two indexes assign different weights to the same tokens and are not on a common scale.
- Reading a required passage's better `per_question` rank as evidence that it is reachable in
  the smaller index, without decomposing the score, where the whole ranking can be produced by
  function words after document frequency has zeroed the question's own entity tokens.
- Attributing a between-setting difference to `idf` without checking `avgdl`, or the reverse,
  when substituting each statistic separately partitions the effect in two extra cells.
- Reporting a set of one-sided interventions as a list of failures instead of as a Pareto
  front, which hides whether the two required passages are separately reachable.
- Running an ablation curve on a required passage before running the single-fact control that
  deletes only the fact the question needs, which is one cell and answers a sharper question.
- Reading the "drop every passage above the gold" cell as evidence on a Dense unit, where the
  scores are unchanged by construction and the resulting ranks follow arithmetically.
- Treating a length-matched control as name-preserving when the question's only content is that
  name, so the control necessarily retains query-relevant material and the gate cannot be read.
- Calling a query addition oracle or non-oracle by whether it contains a gold title, without
  asking whether it presupposes a fact stated only in the other required passage.
- Deleting a provisional code by citing an earlier case that deleted the same name, without
  re-measuring, since the same name can be wrong for opposite reasons in two units.
- Splitting a preprocessing factor into its query side and its document side and stopping there,
  when a one-sided gain can be a destroyed match rather than a repair and only the both-sides cell
  tells the two apart.
- Reading a lexical index-side removal probe as purely positional, when dropping documents also
  changes `idf` and `avgdl` and the required passage's own score moves.
- Running a family-scoped removal probe with a complement control but without a size-matched null
  control and a statistics-matched control drawn from below the required evidence.
- Copying the bi-encoder fact that gold scores are unchanged under every removal onto a lexical
  backend, where they are not.
- Assuming that a query token with 0 corpus occurrences is a missed repair, without measuring what
  normalizing it actually does to the required passages.
- Concluding that a title supplies the discriminative anchor because indexing titles helps, without
  also running the query reduced to that title, which can rank the passage outside the cutoff when
  the title string occurs verbatim in other passages.

- Pricing a surface mismatch from a gold-targeted repair alone, without running the same repair
  corpus-wide, when the deployable form usually returns a different and much smaller number because
  the competitors carry the same mismatch.
- Running a family-scoped removal probe on the raw baseline only, when repairing the preprocessing
  defect first can reverse the verdict in either direction.
- Concluding that a query token is dead and stopping there, without measuring what its repair is
  worth, which is a separate quantity and is confirmed most cheaply by the single-token query's own
  score.
- Assuming that once a preprocessing factor has been split into query side and document side, the
  two sides act on the same required passage; they can repair different ones and damage each
  other's.
- Choosing between the repeated-function-word descriptor and the query-scaffold descriptor by
  inspecting the query, rather than by deleting the repeated occurrences and the non-repeated
  scaffold tokens in two separate cells.
- Treating `not_in_top50` in a stored window as evidence that the answer entity is absent from the
  corpus, and then coining a descriptor that says so.
- Writing a figure into several landed files and only then running the script that verifies it,
  so that one transcription error has to be corrected in several places at once - and one of those
  places is an append-only log, which may already be beyond editing. Finish and run the
  reproduction script first, freeze every figure it establishes into one table, and transcribe
  each shared file from that table rather than from memory or from output printed earlier in the
  session.
- Running a wording-repair factorial on the raw baseline only, when repairing the preprocessing
  defect first can turn eight indistinguishable cells into evidence, or hide a wording effect
  behind a much larger surface-form effect.
- Writing a grammar-repair condition without first checking the document frequency of both
  inflected forms, when the corpus may overwhelmingly carry the ungrammatical one and the repair
  then destroys the required passage's only content match.
- Comparing a fluent rewrite of the question against the baseline when the rewrite also changed
  the punctuation, the token count and the interrogative frame, so that four factors move at once
  and one of them may silently create a zero-frequency token.
- Running the drop-everything-above-the-gold cell on one baseline and concluding from it that no
  crowding descriptor can be the primary, when the same cell reverses after the adopted primary's
  repair.
- Treating a competitor family as name-driven because its members carry the queried name, without
  deleting that name from the question to see whether the neighbourhood survives; a category word
  the question also contains may be what actually produces it.
- Adopting a near-miss descriptor because the score gap falls inside the accepted band, without
  re-checking the no-substitute condition, which can fail even when the gap is small and the
  removal ladder is favourable.

- Reading a Dense family-scoped removal probe as evidence, when on a bi-encoder its outcome is
  fully determined by how many of the removed passages ranked above the gold; a complement control
  does not fix this, because it differs from the family only in size.
- Treating a length-matched control as valid because it retains only non-query-relevant sentences,
  without checking it word by word for a query-relevant term that the sentence-level rule let
  through.
- Concluding that the description-only reading fails because some non-oracle condition recovers
  both required passages, without separating the conditions that leave the question's referring
  expression intact from the ones that replace it.
- Calling a query rewrite a repair when it drops one of the question's stated constraints; it is
  non-oracle evidence about which description works, not a deployable fix.
- Running a wording factorial on a question's grammar when what is underdetermined is which words
  name the required entity, and so measuring the wrong four factors.
- Reporting a double recovery as a yes-or-no outcome, when the margin can be one rank position and
  two conditions differing only in word order land on either side of the cutoff.
- Asserting a figure in the reproduction script without also printing it. The script's own
  assertions pass, and the cross-file audit — whose only source of truth for standalone
  decimals is that script's output — reports every one of those figures as never measured.
  One landing asserted 151 checks and had 194 figures come back unaccounted for. Record each
  verified value as it is checked and print them all at the end.
- Naming a non-gold passage's rank and score in a landed file without recording its position
  during the diagnostic phase. The audit checks rank/score pairs against the unit's results
  record only, and that record holds the golds; a passage that is not a gold appears in no
  condition row and can therefore never reconcile. Decide which passages the write-up will
  name while reading the distractor texts, and record their positions then.
- Writing down a difference, a percentage or a share obtained by subtracting two figures that
  have already been rounded for printing. The quantity looks measured — its two inputs were —
  but it was never computed from the unrounded values, and the last digit is where it shows.
  One landing did this twice and got the last digit wrong both times, at a cost of two rounds
  of rework. Compute every derived quantity with an expression in the reproduction script and
  print it from there.
- Correcting a figure in a file and leaving the superseded value in a comment. A cross-file
  audit scans every decimal in the file and does not distinguish code from prose, so the dead
  number is reported as unaccounted for exactly as a live one would be.
- Letting two diagnostic scripts for the same unit write their results under the same producer
  key. Each write is individually legal and the record silently keeps only the last one; no
  check fires, because nothing is inconsistent — there is simply less evidence than was
  measured. Key each producer by its own script name, and treat a shrinking condition count as
  a symptom rather than a coincidence.
- Accepting a text-formatting helper's silent no-op. A wrapper that reflows only the lines
  carrying a given indent will return unindented input unchanged and raise nothing; the write
  then succeeds, the format checker passes because it does not look at line width, and the
  defect is visible only in the diff. A tool that can do nothing at all should say so.
- Anchoring an edit on a block of text that two entries share. Entries created together by one
  decision are often byte-identical for several lines, so an anchor that reads as specific
  matches twice. Anchor on the entry's unique name instead, and run the whole replacement plan
  against disk before writing any of it.

- Treating a tool's output as unverifiable because the artifact it produces is
  indistinguishable from a hand-written one. A condition table copied correctly by hand is
  byte-identical to a generated one, so a format checker, a count reconciler and a figure
  audit all pass whether or not the generator was used — which means skipping it is free and
  silent, and the review learns nothing until someone measures the duplicated typing after
  the fact. Split the rule in two: mechanise the half that compares the artifact against its
  machine-readable source, and make the report state, tool by tool, which ones were used and
  why the rest were not. "Not used" is a fine answer; not saying is not.
- Abandoning a template because one step of it is in the wrong order. The mismatch is usually
  real — a generator that reads the current state of the working tree gives mid-run numbers if
  it runs before the state it reads has been written — but the response of reverting to
  hand-written scripts also discards everything else the template supplied, and the
  replacement is then rebuilt from nothing under time pressure. Reorder the template and say
  so in it.
- Recording a measurement's result without recording the call that produced it. The result
  alone can generate an expectation table and nothing else, so every condition is typed a
  second time into the reproduction script, and that second pass is where the transcription
  errors are: in one landing all five failing assertions were typos introduced there and none
  was a wrongly written call. Record the query, the flags and the substitutions beside the
  figures. State the cost in writing, too — replaying a recorded call cannot show that making
  that call was the right experiment, and the retyping used to be an incidental second look at
  exactly that.
- Deriving a rule's scope from prose that was written for a different purpose. A pit list
  whose entries cross-reference each other will contain sentences like "this is specific to
  the dense backend" that describe the thing being cited, not the entry containing them, so a
  phrase rule reads the scope backwards. Before automating an attribution, count how many
  entries state it at all: if most do not, the tool's confident answers on the few that do are
  worth less than its silence on the rest. Index which cases have cited each entry instead —
  that is a fact about the record — and leave applicability to the reviewer.
- Anchoring an idempotent insert on a greedy multi-line pattern that ends where the insert
  goes. The first run succeeds; the second run's anchor swallows the text the first run
  added, so `old` is no longer the same string and the block lands twice. Anchor an insert on
  a single stable line — the heading that follows it — so the matched text is byte-identical
  on every run.

## 6. Repeatable single-case checklist

### Workspace hygiene

- [ ] All temporary scripts, payloads, and intermediates are under the current
  workspace's `tmp/<task_name>/`.
- [ ] No project temporary data was written to another disk, system temp, a user
  profile, a home directory, or a Codex cache.
- [ ] Before cleanup, the task temporary directory's absolute path was confirmed
  to lie under the workspace `tmp/`.
- [ ] After the formal files passed cross-validation, only the temporary
  directory created by this task was deleted.

### Evidence

- [ ] The complete question has been read.
- [ ] Both complete gold passages have been read.
- [ ] Gold ranks, cutoff, and stored-window missingness have been recorded.
- [ ] At least the top-5 distractor texts have been read.
- [ ] The key passage texts ranked above the gold have been read.
- [ ] The matched and missing constraints of each key distractor have been listed.
- [ ] Comparison-retriever evidence has been checked.
- [ ] Pooled/per-question provenance has been checked.
- [ ] Whether the query explicitly requires the annotated gold's year/version has
  been checked.
- [ ] A complete alternative answer/chain, a single-hop substitute, and a genuine
  distractor have been distinguished.
- [ ] The score gap of each key gold has been compared individually, rather than
  marking a cutoff near miss in general terms.

### Implementation

- [ ] Indexed fields have been confirmed.
- [ ] Query/document preprocessing has been confirmed.
- [ ] Tokenizer, punctuation, and stop-word policy have been confirmed.
- [ ] Stemming, lemmatization, and Unicode policy have been confirmed.
- [ ] Method version, parameters, and scoring function have been confirmed.
- [ ] Whether title, token order, phrase, and entity boundary participate in
  scoring has been confirmed.
- [ ] Repeated query tokens have been checked.
- [ ] Where necessary, the total score has been reproduced and a per-token
  decomposition completed.
- [ ] If counterfactuals were used, the original complete ranking was reproduced
  first and re-ranking was done on the same complete candidate set.

### Interpretation

- [ ] The implementation, method, corpus, and evaluation levels have been
  distinguished.
- [ ] Whether a complete plausible non-gold answer exists has been checked.
- [ ] Whether an evidence-bearing passage replaces only one gold hop has been
  checked, and the remaining missing hop has been stated.
- [ ] The best-evidenced and most specific primary mechanism has been chosen.
- [ ] The closest competitor and the tie-break rationale have been recorded.
- [ ] Secondary mechanisms that the primary cannot explain have been retained.
- [ ] Include/exclude rules have been defined for all secondary descriptors.
- [ ] Confidence, taxonomy defect, and unresolved boundaries have been recorded.
- [ ] Causal wording does not exceed the observable evidence.
- [ ] Dense token-level or "content dilution" explanations without
  attribution/ablation have been marked as speculation.
- [ ] The comparative explanation has been checked against the actual query
  tokens/semantics.
- [ ] Gold-only score increase, single-hop improvement, and complete top-k
  outcome recovery have been distinguished.
- [ ] Oracle rewrites have been marked explicitly as diagnostics and are not
  presented as production fixes.

### Archiving

- [ ] A dossier for this unit exists in
  `manual_review_v1/analysis/per_case_analysis/`, named
  `<method>_<question_type>_<example_id>.md`, containing every required section
  from that folder's `README.md`.
- [ ] The dossier's reproduction script was actually executed and its assertions
  passed before the dossier was written.
- [ ] The dossier index table in that `README.md` was updated with this unit.
- [ ] The consequential decision and `joint_review_notes` still hold the complete
  factorial evidence; the dossier supplements them and does not replace them.

## 7. Recommended record format

```text
Observed retrieval behavior:
Gold evidence status:

Top distractor evidence:
- Rank / score / title:
- Actual text evidence:
- Matched cues:
- Missing decisive constraint:

Verified implementation facts:
- Indexed fields:
- Tokenizer or embedding model:
- Normalization:
- Scoring behavior:
- Corpus setting:

Reconstructed mechanism:
Comparison-retriever evidence:
Evaluation or corpus ambiguity:

Factorial diagnostic status: run | not_run
Factorial setting / baseline reconstruction:
| Condition | Single or combination | Exact change | Required evidence ranks / scores | Complete top-k recovery | Interpretation |
|---|---|---|---|---|---|
| baseline | baseline | none | ... | yes/no | reconstruction status |
| A | single | ... | ... | yes/no | ... |
| B | single | ... | ... | yes/no | ... |
| A+B | combination | ... | ... | yes/no | ... |
Single-factor effect:
Combination / interaction effect:
Attribution boundary:

Primary mechanism:
Secondary descriptors:
Closest competitor:
Tie-break result:
Confidence:
Taxonomy defect flag:
Remaining uncertainty:
```

## 8. Related project materials

- `manual_review_v1/analysis/per_case_analysis/` — one full investigation dossier
  per analytical unit, with the complete experimental record and a runnable
  reproduction script; see its `README.md` for the format and naming rule
- `references/failure_annotation_guideline.md`
- `references/bm25_implementation_reference.md`
- `references/dense_implementation_reference.md`
- `manual_review_v1/analysis/case_memos_v2.csv`
- `manual_review_v1/analysis/open_code_decision_log.md`
- `manual_review_v1/analysis/secondary_descriptor_registry.md`
- `manual_review_v1/analysis/single_note_validation_queue.md`

This method should be updated continuously as new implementations, retriever
types, and boundary cases appear. Every method-level conclusion must be bound to
a specific run, code version, and corpus setting, and must not be silently
generalized from one case to all retrieval systems.
