---
status: draft
last_updated: 2026-07-31
---

# Notes-First Grounded Failure-Taxonomy Workflow

## 1. Status and purpose

This is a temporary working specification for deriving a retrieval-failure
taxonomy from completed case notes. It records the desired analysis sequence;
it does not assign the work, replace the DR-003 canonical protocol, or claim
that the taxonomy has already been produced.

The methodological pattern is adapted from the grounded-theory annotation
process in *AgentRx: Diagnosing AI Agent Failures from Execution Trajectories*.
That work begins without a predefined failure-label set, writes concrete codes
and memos grounded in individual traces, compares new observations with earlier
ones, progressively groups related open codes into higher-level categories,
refines category definitions, freezes the taxonomy after saturation, and then
uses closed coding to label or relabel cases under the frozen taxonomy.

For the current retrieval study, the corresponding high-level sequence is:

```text
free-form evidence-based notes
  -> open codes and analytic memos
  -> constant comparison across cases
  -> candidate category clustering
  -> category-boundary refinement
  -> taxonomy convergence and freeze
  -> final unit-level labeling under the frozen taxonomy
```

## 2. Core design principles

### 2.1 Evidence precedes categories

No fixed causal taxonomy is imposed while the case notes are being written.
Each note records what is visible in the case before abstracting it into a
failure mechanism.

The notes should remain free-form because different failures expose different
types of evidence. Free-form does not mean unsupported: a useful note connects
its possible explanation to concrete ranks, retrieved passages, distractors,
missing gold evidence, comparison-retriever behavior, and uncertainty.

### 2.2 Open coding precedes closed coding

During open coding, short descriptive codes may be attached to observations,
but they are provisional and revisable. A new observation may reuse an existing
open code when the same mechanism is present, introduce a new code when no
existing code fits, or expose that an earlier code is too broad or too narrow.

Closed coding begins only after the taxonomy has converged and been frozen.
Only then is every unit assigned one final analytical label from the frozen
taxonomy, with `unresolved` available when the evidence does not support a
defensible category.

### 2.3 Constant comparison drives convergence

Every proposed code or category is compared against earlier cases. The purpose
is not merely to collect recurring phrases, but to test whether apparently
similar failures share the same causal mechanism and whether apparently
different failures require distinct categories.

Comparison should actively look for:

- positive examples that clearly fit a category;
- near-neighbor examples that appear similar but should be excluded;
- cases that exhibit more than one plausible mechanism;
- cases where the evaluation contract or question ambiguity is more important
  than a retriever defect;
- cases where the two retrieval methods fail for different reasons;
- counterexamples that force a category to be split, merged, renamed, or
  narrowed.

### 2.4 Machine structure remains separate from human causes

The machine-generated `rank_pattern`, gold ranks, and retrieval cutoff describe
observable retrieval structure. They may organize comparisons, but they are not
failure causes and must not become taxonomy categories by themselves.

For example, `both_not_in_top50` states where gold evidence appeared; it does
not explain whether the cause was lexical mismatch, entity ambiguity,
near-neighbor crowding, bridge under-specification, or another mechanism.

### 2.5 Raw notes remain primary evidence

The original notes remain intact as the evidence base from which the taxonomy
was derived. Later coding decisions may add analytic memos, corrected
interpretations, and final labels, but they should not silently rewrite the raw
observations that motivated those decisions.

## 3. Desired workflow

### Phase 0 — Establish the analysis corpus

1. Freeze the set of review units and their identities.
2. Preserve each unit's question, gold passages, target-retriever results,
   comparison-retriever results, gold ranks, and read-only machine pattern.
3. Keep independently written notes distinct where the same unit has more than
   one note.
4. Confirm that all intended units have substantive notes before taxonomy
   formation begins.

For `manual_review_v1`, the analysis corpus is 30 unique units represented by
34 review actions: four units have two independent notes and the remaining 26
have one note each.

### Phase 1 — Read notes without imposing a label set

Read the full notes corpus before fixing any category vocabulary. For each unit,
extract a compact analytic memo that preserves the note's evidence and
uncertainty.

A working memo may contain:

```text
unit identity:
observed retrieval behavior:
gold-evidence status:
retrieved distractor or competing evidence:
comparison-retriever contrast:
provisional mechanism description:
alternative explanation or uncertainty:
```

The memo is a bridge from a detailed note to open coding. It is not yet a final
label.

### Phase 2 — Create provisional open codes

Assign a short, concrete open code to each distinct mechanism visible in the
memos. The wording should stay close to the evidence rather than jump directly
to an abstract universal category.

Examples of the desired level of abstraction include descriptions such as:

- exact query terms promote topically related distractors;
- one comparison entity crowds out the other;
- a named entity is buried among homonyms or near-neighbor entities;
- the bridge entity is described indirectly and has weak surface overlap;
- both gold passages are found but narrowly miss the cutoff;
- the question or gold chain admits a plausible non-gold answer.

These are illustrations of open-code granularity, not a predefined taxonomy.
They must not be copied into final categories without comparison against the
full notes corpus.

### Phase 3 — Apply constant comparison

Process the memos iteratively. For every new open code:

1. compare it with codes already assigned;
2. reuse an existing code only when its definition and evidence requirements
   genuinely match;
3. create a new code when the observed mechanism is materially different;
4. record why a close existing code was rejected;
5. revisit earlier cases when a new distinction exposes an over-broad code.

Maintain an append-only decision memo for consequential merges, splits,
renames, and boundary changes. The memo should preserve the reason for each
change and the cases that motivated it.

### Phase 4 — Cluster open codes into candidate categories

Periodically group related open codes into higher-level candidate categories.
A candidate category is acceptable only when it explains a coherent mechanism,
not merely a shared retriever, rank pattern, question type, or keyword.

For each candidate, write:

```text
category name:
definition:
required observable evidence:
inclusion rules:
exclusion rules:
closest competing category:
tie-break rule:
positive examples:
counterexamples:
known ambiguity or limitation:
```

At this stage categories may still be merged, split, renamed, or removed.

### Phase 5 — Stress-test category boundaries

Test every candidate category against the full notes corpus rather than only
the cases that originally motivated it.

The boundary review should ask:

- Does the category cover all of its intended examples?
- Does it wrongly absorb a near-neighbor mechanism?
- Is the definition based on causal evidence or only rank structure?
- Can two categories be distinguished using information actually visible in
  the notes?
- Does a category force uncertain or ambiguous cases into an unsupported
  explanation?
- Would an independent reader apply the definition consistently?
- Is a proposed distinction analytically useful for the research question?

If the answer reveals an unstable boundary, revise the definitions and recheck
all affected cases.

### Phase 6 — Converge and freeze `taxonomy_v1`

Because the current corpus is bounded, convergence is defined operationally
rather than claimed as universal theoretical saturation. `taxonomy_v1` may be
frozen when all of the following are true:

1. all 30 unique units have been examined during taxonomy formation;
2. a complete comparison pass introduces no materially new failure mechanism;
3. every category has a definition, evidence requirements, inclusion and
   exclusion rules, a closest-overlap rule, examples, and limitations;
4. every unit can be mapped to one category or defensibly marked `unresolved`;
5. no category is merely a restatement of `rank_pattern`, retriever identity,
   question type, or cutoff status;
6. overlap cases retain both original notes and any differences in
   interpretation have been explicitly considered;
7. unresolved boundary decisions are recorded rather than hidden by forced
   agreement.

Freezing `taxonomy_v1` means its definitions become the closed-coding contract
for the current analysis. Later substantive changes require a new taxonomy
version rather than silent edits.

### Phase 7 — Recode every unit under the frozen taxonomy

After `taxonomy_v1` is frozen, revisit all 30 unique units. Assign exactly one
final analytical label to each unit using the frozen category definitions.

The recoding pass must:

- use the full original note evidence, not only the provisional open code;
- preserve both notes for overlap units;
- avoid counting an overlap unit twice;
- use `unresolved` instead of forcing an unsupported category;
- record whether the final label came from a single-note unit, agreement on an
  overlap unit, resolution after differing interpretations, or an unresolved
  case;
- document any case that exposes a possible taxonomy defect.

If recoding repeatedly requires exceptions or cannot apply the frozen
definitions, reopen the taxonomy as a new version rather than modifying labels
ad hoc.

### Phase 8 — Produce final analytical artifacts

The desired outputs are:

1. the preserved raw notes exports;
2. an open-code and decision memo linking evidence to category development;
3. the frozen `taxonomy_v1` definition document;
4. `results/annotations/manual_review_v1/final_labels.csv` with one row per
   unique unit;
5. a category-count summary whose denominator is 30 and whose category counts,
   including `unresolved`, sum to 30;
6. a qualitative analysis that cites representative notes and counterexamples.

These counts describe the bounded calibration/open-coding sample. They are not
population-level prevalence estimates.

## 4. Separation of artifacts

The workflow keeps four conceptual layers separate:

| Layer | Purpose | May change during convergence? |
|---|---|---:|
| Raw notes | Case-level observations and uncertainty | Preserved; corrections are explicit |
| Open codes and memos | Provisional mechanism descriptions and comparison history | Yes |
| `taxonomy_v1` | Frozen category definitions and decision rules | No after freeze; revise by version |
| Final labels | One closed-code result per unique unit | Only through an explicit recoding pass |

This separation prevents a provisional phrase in a note from silently becoming
a final category and prevents later taxonomy decisions from erasing the
evidence that produced them.

## 5. Anti-patterns

The following are outside the desired workflow:

- defining a fixed category list before reading the full notes corpus;
- treating the suggested note template as a category schema;
- copying machine `rank_pattern` values into causal labels;
- clustering only by retriever, question type, or gold-rank configuration;
- assigning final labels while category definitions are still changing;
- rewriting raw notes to make them appear consistent with the final taxonomy;
- forcing every unit into a category to avoid `unresolved`;
- reporting counts from 34 review actions as though they were 34 unique units;
- describing category frequencies in this bounded sample as prevalence in the
  full failure population.

## 6. Relationship to DR-003

This workflow elaborates the existing DR-003 notes-first rule:

- free-form evidence-bearing notes come before causal categories;
- no system pre-fills a human failure label;
- a taxonomy is derived from completed notes rather than assumed in advance;
- raw reviewer labels and final analytical labels are distinct;
- final category counts use one row per unique unit.

If this temporary document conflicts with the canonical DR-003 course protocol,
the canonical protocol controls. This document becomes authoritative only if it
is explicitly adopted through the design-record process.

## References

- Barke, S., Goyal, A., Khare, A., Singh, A., Nath, S., and Bansal, C.
  [*AgentRx: Diagnosing AI Agent Failures from Execution Trajectories*](https://arxiv.org/abs/2602.02475),
  Section 2.1, 2026.
- `docs/specs/2026-07-27-manual-failure-review-course-protocol.md`
