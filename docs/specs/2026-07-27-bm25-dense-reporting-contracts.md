---
status: active
last_updated: 2026-07-28
---

# BM25-vs-Dense Reporting Tools — Frozen/Narrowed Contract

- Date: 2026-07-27
- Applies to: `scripts/reporting/disagreement_cases.py`,
  `scripts/reporting/bm25_failure_shortlist.py`
- Shared input plumbing: `scripts/reporting/formal_result_inputs.py`
- Upstream schema: `docs/specs/2026-07-15-results-csv-schema.md`
- Boundary authorities: `docs/specs/2026-07-12-failure-review-pipeline-design.md`
  (evidence-rich causal review), `docs/specs/2026-07-27-manual-failure-review-course-protocol.md`
  (notes-first, no prefilled causal labels)
- Design record: DR-004
- Revision: 2026-07-27 (round-3 corrective pass) — recorded Xin's owner decision
  on binary CSV serialization as the frozen physical lexeme rule (§1.1), made
  the missing-value policy column-aware (§1.2), and updated §1/§5 accordingly.
  No metric, criterion, output schema, or result number changed.
- Revision: 2026-07-27 (round-4 corrective pass) — clarified two secondary
  wordings of §1.2 that could be read more broadly than the shared schema
  allows: a `[0,1]` float metric lexeme must be **in range**, not merely a
  finite decimal (§1.2, §5), and an empty metric cell is legal **only** in the
  three per-question `@10` recall slots the schema leaves uncomputed (§1.1,
  §1.2, §5). Both readings are narrowings of the reader's accepted set toward
  the upstream schema; the owner decision on binary lexemes is unchanged and is
  not broadened. No metric, criterion, output schema, or result number changed.
- Revision: 2026-07-27 (round-5 corrective pass) — closed the **inverse** of
  that clarification. "Uncomputed" in the shared schema means the cell **is**
  empty, not that it *may* be: the three per-question `@10` recall slots are
  **required-empty**, so a populated value there refuses even when it is an
  owner-approved binary lexeme or an in-range decimal, and every other metric
  slot is **required-populated**. §1.2 now states the placement rule as a
  two-state contract over all 22 `(metric column, setting)` slots and §5 lists
  the inverse refusal. This is again a narrowing toward the upstream schema and
  toward the rescue authority, which already required it; the owner-approved
  binary lexeme set is unchanged and is **not** broadened. No metric, criterion,
  output schema, or result number changed.
- Revision: 2026-07-28 (round-6 corrective pass) — named the **second
  enforcement layer** the previous revisions left implicit. The rules of §1.1
  and §1.2 can only be decided on a file; a caller may also hand either tool an
  already-created DataFrame, and §1/§5 always required those callers to be held
  to the same contract. §1 now states the two layers explicitly and adds
  `validate_typed_metric_frame` as the typed-frame gate, and §5 lists the
  direct-frame refusals. This adds no new accepted value anywhere: it states
  where each already-frozen invariant is enforced when the lexemes no longer
  exist, and it explicitly does **not** claim that a typed frame can recover a
  lost spelling. Also corrected a stale cross-reference in §4 (the notes-first
  boundary is course-protocol §2, not §3). No metric, criterion, output schema,
  or result number changed.

## 0. Why this document exists

The reranker rescue/damage tool has a frozen spec
(`docs/specs/2026-07-26-reranker-rescue-damage.md`). The two BM25-vs-dense
reporting tools previously had only plan-level scope and no standalone
input/output/refusal contract, so an independent review could not decide
whether their join, criterion, and output vocabulary were compliant. This
document **narrows and freezes** their contract. It defines only mechanical
reporting behavior; it defines no metric (metric logic stays hand-written in
`src/evaluator.py`) and asserts no failure cause.

## 1. Shared input contract (both tools)

Both tools read the shared long-format result CSVs (`RESULT_COLUMNS` in
`src/results_schema.py`). `scripts/reporting/formal_result_inputs.py` enforces,
**before any cell is read or converted**:

- **Physical read** (`read_formal_result_csv`): the file is read as raw text —
  pandas' numeric parsing and its global NA-token inference are both switched
  off — and every cell is validated **as its literal lexeme before any
  conversion** (§1.1). Only then are binary hit columns converted to nullable
  integers and the `[0,1]` metric columns to floats; textual columns keep the
  exact strings the file contains. A deliberately empty binary cell (the schema
  leaves per-question `@10` uncomputed) stays missing and is never silently
  read as `0`; an empty cell anywhere the schema does not reserve one refuses,
  and so does a populated cell in one of the three slots the schema requires to
  be empty (§1.2). There is deliberately **no** public helper that normalizes an
  in-memory frame's binary columns: such a helper erases exactly the float
  provenance this contract refuses, so a caller building a frame by hand must
  construct the nullable-integer columns from integer/missing values directly.
- **Per file** (`validate_structure`): exact `RESULT_COLUMNS` in order; the file
  is uniformly its expected method (`bm25` / `dense` / `rerank`); the `setting`
  column is exactly `{pooled, per_question}` (both present, nothing else);
  `(setting, example_id)` is unique within each setting.
- **Per typed frame** (`validate_typed_metric_frame`, §1.3): every invariant of
  §1.2 that survives parsing, re-checked on the already-created DataFrame across
  all 22 `(metric column, setting)` slots, and run from `validate_structure`
  once the `setting` vocabulary above makes placement decidable. This is the
  layer that binds a caller who never touches a file.
- **Metadata value domains** (`validate_metadata_domains`): `example_id`,
  `question`, and `gold_titles` are a non-null string in every row, and the
  closed upstream vocabularies of the shared schema hold —
  `question_type ∈ {bridge, comparison}` and `level ∈ {easy, medium, hard}`.
  An upstream-invalid value such as `question_type=other` is refused even when
  it is consistent across both inputs.
- **Across the joined methods** (`validate_cross_method_identity`): for each
  setting, every method covers the identical `example_id` set (cross-method
  parity, required by the per-setting one-to-one join); and each `example_id`
  carries identical `question_type` / `level` / `question` / `gold_titles`
  across every `(method, setting)` row (no metadata drift). Missing values
  participate in that comparison, so a value present on one side and absent on
  the other is drift, not a match.
- **Consumed cell** (`validate_consumed_binary`): the single selected metric
  column `{criterion}@{k}` in the selected setting is present and is a **plain
  integer** `0`/`1` for every retriever consumed, including the optional rerank
  frame. A `bool`, a float-dtype column, a numeric string, and an empty cell are
  refused even though they compare equal to `0`/`1` — equality semantics are
  exactly what would otherwise let a malformed cell reach `int()`. The selection
  must also be non-empty, so no check can be satisfied vacuously.

  This is the check on the **in-memory value**, and it composes with §1.1 rather
  than contradicting it. A physical `0.0` lexeme is admitted by §1.1 and
  converted to the genuine integer `0`, so it satisfies this check; a frame
  whose binary column is still float dtype does not, and refuses here. Because
  no public helper normalizes such a frame, float provenance cannot be erased
  before this predicate runs.

This is deliberately narrower than the rescue/damage §2 contract: it does **not**
freeze a 1000/500 cardinality or a 404/96 question-type split, because these
tools are general reporting over whatever formal bundle is supplied. It does
close the join and the value domains.

### 1.1 Physical lexeme rule (owner decision, Xin, 2026-07-27)

The shared schema types a binary recall cell as `int` with values `1|0|empty`,
but the required `results/bm25_results.csv` and `results/dense_results.csv`
physically serialize their **pooled `@10`** cells as `0.0`/`1.0`: leaving the
per-question `@10` rows blank made pandas write that whole column as float.
`results/rerank_results.csv` writes plain `0`/`1`. Xin resolved the resulting
conflict on 2026-07-27 by choosing the **narrow compatibility rule** over a
strict rewrite, so no formal input is regenerated and no accepted result number
moves.

A binary hit cell is therefore accepted if and only if its physical lexeme is
exactly one of:

```text
0    1    0.0    1.0    <empty>     (empty only where the schema permits a blank)
```

"Where the schema permits a blank" resolves to exactly one place, and the reader
enforces it as such (§1.2): `any_evidence_recall@10`, `full_evidence_recall@10`,
and `partial_evidence_recall@10` on a `per_question` row. A blank pooled recall
cell, a blank per-question `@2`/`@5` cell, and a blank reciprocal-rank cell are
**not** permitted and refuse. In those three slots the schema does not permit a
blank so much as **require** one, so `<empty>` is not an alternative to the four
populated lexemes there — it is the only accepted cell, and each of `0`, `1`,
`0.0`, `1.0` refuses on placement (§1.2). Conversely, in every other metric slot
`<empty>` is not accepted at all. This clause narrows nothing the owner decided:
the four approved spellings remain exactly as frozen, and it only names where
the shared schema already places a value and where it already places none.

This is an **exhaustive, closed list of spellings, decided on the raw text** —
not a numeric range and not a tolerance. Every other spelling refuses, in
particular:

| Refused class | Examples |
|---|---|
| precision-adjacent fractions | `0.00000000000000000001`, `0.99999999999999999999` |
| ordinary fractions | `0.5`, `0.50`, `0.999999` |
| scientific notation | `1e0`, `1E0`, `0e0`, `1e-20` |
| signs | `+1`, `+0`, `-0`, `-1` |
| padding zeros / alternative decimals | `01`, `001`, `1.00`, `0.00`, `1.`, `.0` |
| whitespace padding | `" 1"`, `"1 "`, `"\t1"`, `"  "` |
| booleans and other numbers | `True`, `False`, `true`, `2` |
| null-like words | `NaN`, `nan`, `NA`, `N/A`, `null`, `None`, `<NA>`, `-` |

Validating the lexeme rather than the converted value is the whole point of the
rule. A nullable-integer cast rounds `0.00000000000000000001` to `0` and
`0.99999999999999999999` to `1`; after that conversion every plain-integer check
passes and the evidence that the cell was ever malformed is gone.

The accepted float spellings are a **legacy-artifact compatibility list only**.
The canonical write form for new artifacts remains plain `0`/`1`; if the runners
are ever changed to serialize the pooled `@10` columns as integers, `0.0`/`1.0`
should be retired from this list by a further owner decision.

### 1.2 Column-aware missing-value policy

Missing-ness is decided per column **and per row**, never by a global token set:

- **textual columns** (`method`, `setting`, `example_id`, `question_type`,
  `level`, `question`, `gold_titles`, `retrieved_titles`) are never NA-inferred.
  The legitimate strings `None`, `NA`, `null`, `NaN`, `<NA>`, and `-` survive as
  themselves and are accepted wherever the column has no closed vocabulary;
- **metric columns** treat **only a physically empty cell** as missing, and only
  where the schema reserves one. The same null-like words are *refused* there,
  so a populated cell can never be misread as the deliberate blank the schema
  reserves for an uncomputed metric;
- **whether a metric cell must be empty or must be populated is decided by the
  column and the row's `setting`, and it is a two-state contract with no third,
  "either" state.** The shared schema's storage/metric policy declares the
  metric uncomputed in exactly three slots; "uncomputed" means the cell **is**
  empty, not that a blank is merely tolerated there. Each of the 22
  `(metric column, setting)` slots is therefore exactly one of:

  | Setting | Required-empty (3 slots) | Required-populated (19 slots) |
  |---|---|---|
  | `per_question` | `any_evidence_recall@10`, `full_evidence_recall@10`, `partial_evidence_recall@10` | recall `@2`/`@5`, partial `@2`/`@5`, `reciprocal_rank_at_10`, `reciprocal_rank_at_50` |
  | `pooled` | none | every recall/partial `@2`/`@5`/`@10` and both reciprocal ranks |

  Both halves are enforced **before conversion and before any write**, on the
  raw lexeme, by the shared reader, for the BM25, dense, and optional rerank
  inputs alike:

  - an empty cell in a **required-populated** slot — a blank pooled recall, a
    blank per-question `@2`/`@5`, or a blank in either reciprocal-rank column —
    is refused, because it marks a truncated or partially generated file rather
    than a deliberate omission. A truncated file that passed here would
    otherwise produce an apparently complete report;
  - a populated cell in a **required-empty** slot is refused for the mirror-image
    reason: the frozen K policy declares that metric absent, so a value there is
    an unauthorized metric extension, not a legal alternative spelling. This
    holds for an owner-approved `0`/`1`/`0.0`/`1.0` lexeme and for an in-range
    `[0,1]` decimal exactly as it does for a null-like token — legality of the
    *spelling* never implies legality of the *placement*. Reading the rule as a
    one-sided permission to be blank is what would let two of the three tools
    publish a report from a bundle the rescue tool refuses, so this clause is
    what keeps all three sharing one input language;
- `example_id`, `question`, and `gold_titles` must additionally be **non-empty**;
- `retrieved_titles` must be a string, and an **empty cell is the approved
  serialization of an empty retrieved list**. It is text, not a metric, so the
  blank-placement rule above does not apply to it. It stays empty end to end: it
  is never converted to a missing scalar and never stringified back into a title,
  so a fabricated title such as `"nan"` cannot reach a generated artifact;
- the `[0,1]` float metric columns (`partial_evidence_recall@{2,5,10}`,
  `reciprocal_rank_at_10`, `reciprocal_rank_at_50`) accept an **in-range finite
  decimal** lexeme — the exact written decimal must satisfy `0 <= value <= 1` —
  or an empty cell in one of the three slots above. Lexical finiteness is not
  the semantic domain: `-0.1`, `1.1`, `2`, and the overflow spelling `1e9999`
  are all well-formed finite decimals and all refuse. The comparison is made on
  the exact decimal **before any conversion**, which is what makes the two
  boundary-adjacent spellings visible — `float("1.0000000000000001")` is exactly
  `1.0` and `float("-1e-400")` is `-0.0`, so a conversion-first check would
  admit both. After conversion the resulting float is re-checked as finite and
  in range as a defensive backstop. `NaN`, `inf`, `Infinity`, null-like words,
  and padded or underscored numbers all refuse as before.

### 1.3 The two enforcement layers

§1.1 and §1.2 are decided on **raw text**, which exists only while a file is
being read. Both tools also expose public functions — `extract_disagreements`
and `build_shortlist` — that accept an **already-created DataFrame**, and the
rescue tool exposes `build_paired_frame` and `oracle_check` on the same terms.
For such a frame the lexemes are gone, so the contract is enforced in two
distinct layers. Neither layer is a substitute for the other, and neither
pretends to be:

| Layer | Function | Subject | Decides |
|---|---|---|---|
| raw CSV | `read_formal_result_csv` | the exact physical lexeme | the frozen binary spellings of §1.1; the exact `Decimal` `[0,1]` comparison; raw required-empty / required-populated placement |
| typed frame | `validate_typed_metric_frame` | the parsed scalar and the column's dtype | all three per-question recall `@10` slots missing; all other 19 slots populated; every populated binary cell a genuine integer `0`/`1`; every populated partial-recall and reciprocal-rank cell numeric, finite, and inside `[0,1]` |

Binding rules:

- the typed layer **never normalizes or coerces**. It does not clip, round, fill,
  or re-type anything; it only refuses. A binary column that has been cast to
  `float`, `bool`, `str`, or `object` is refused on its dtype, because the cast
  already destroyed the integer provenance and no non-coercing validator can
  return it;
- the typed layer **makes no claim about spelling**. It cannot tell
  `0.00000000000000000001` from `0`, because after parsing there is nothing left
  to tell them apart. Only §1.1 can, and only on a file. Presenting the typed
  layer as a replacement for the reader would be a false provenance claim;
- every **file** path runs both layers: `read_formal_result_csv` first, then
  `validate_structure` (which carries the typed layer). Every **in-memory** path
  runs the typed layer. So for every invariant that is observable on a typed
  frame, the two kinds of input are accepted and refused identically; the raw
  layer adds only the invariants a typed frame physically cannot express;
- a narrow single-column predicate such as `validate_consumed_binary` is a
  component, never the whole gate. No public function may validate only the
  cell it consumes while trusting the unconsumed metric columns.

## 2. Supported criteria (both tools)

`--criterion` is restricted to the two **binary** hit metrics:

```text
full_evidence_recall, any_evidence_recall
```

`partial_evidence_recall` is intentionally **not** supported. Partial is a
`[0,1]` float, not a binary hit; admitting it would either be rejected by the
binary validator or require a separately owner-approved non-binary contract.
`--k` is an integer.

`setting` is restricted to the exact, case-sensitive vocabulary:

```text
pooled, per_question
```

This is enforced on the **direct public argument** of `extract_disagreements`
and `build_shortlist`, not only by the CLI `choices=` list, and it is checked
**before** any row is selected. Filtering by an unsupported value would
otherwise leave an empty frame on which every cell check passes vacuously,
making a caller or configuration error indistinguishable from a genuine
zero-case result. Unsupported, null, empty, and case-variant values (`Pooled`,
`POOLED`) all refuse. A *supported* setting with genuinely zero cases remains
valid output: an exact-schema, zero-row frame (§3, §4).

## 3. `disagreement_cases.py`

Extracts questions where BM25 and dense disagree on the selected binary hit.

**Output columns (exact, in order):**

```text
example_id, setting, question_type, level, question, gold_titles,
criterion, k, bm25_hit, dense_hit, direction,
bm25_retrieved_titles, dense_retrieved_titles
```

When `--with-rerank` is set, exactly two columns are appended:
`rerank_hit, rerank_retrieved_titles`. The rerank cell is validated `0`/`1`
before `int()` conversion, so a non-binary rerank value can never be silently
coerced.

- `direction ∈ {dense_only, bm25_only}`: `dense_only` = dense hit, BM25 miss;
  `bm25_only` = BM25 hit, dense miss. Agreements are omitted.
- **Deterministic order:** `direction` (`dense_only` before `bm25_only`), then
  `question_type`, then `example_id`.
- **Empty result:** an all-agreement bundle yields a 0-row file with the exact
  header. This is valid output, not an error.

## 4. `bm25_failure_shortlist.py`

Surfaces BM25 failure candidates as a **neutral, mechanical** shortlist. It
assigns no causal category. Under the accepted failure-review boundary
(2026-07-12 §1) a cause such as lexical mismatch requires reading gold and
retrieved paragraph text side by side; under the notes-first course-protocol
boundary (`docs/specs/2026-07-27-manual-failure-review-course-protocol.md` §2,
"Stable boundaries") no system or agent pre-fills a causal label. This tool
therefore emits only observables.

**Output columns (exact, in order):**

```text
example_id, observed_signal, setting, criterion, k,
question_type, level, question, gold_titles,
bm25_top5, dense_top5,
bm25_hit, dense_hit, bm25_gold_found, n_gold
```

`setting` / `criterion` / `k` are provenance columns so each row is
self-describing.

**`observed_signal` vocabulary (closed, neutral, no causal names):**

| Signal | Purely mechanical meaning |
|---|---|
| `dense_hit_bm25_miss` | Under the selected `criterion@k`, BM25 misses (`hit=0`) and dense hits (`hit=1`). |
| `bm25_no_gold_in_top2` | BM25 misses (`hit=0`) and no gold title appears in BM25's own stored top-2 titles. |

A case may carry either or both signals (emitted as separate rows). Neither
signal names or implies a cause; causal categories `lexical_mismatch` /
`distractor_entity` (and any `category_candidate` column) are retired and must
not reappear until a post-notes taxonomy and evidence contract are
owner-approved.

- `bm25_gold_found` = the number of **distinct gold titles** found anywhere in
  BM25's stored list — the size of the intersection between the gold titles and
  the stored retrieved titles, never the number of retrieved *occurrences*
  (mechanical context, not a verdict). `n_gold` = number of gold titles. The
  invariant `0 <= bm25_gold_found <= n_gold` therefore always holds and is
  asserted while each row is built; counting occurrences would break it when a
  title repeats in storage, and would also perturb the ranking key below.
- **Ranking within each signal group:** `(bm25_gold_found, question_type,
  example_id)` ascending; `--per-signal` keeps the top N of each group.
- **Empty result:** a bundle with no BM25 miss yields a 0-row file with the
  exact header. This is valid output, not an error.
- **Empty stored title list:** a row whose `retrieved_titles` is the approved
  empty cell (§1.2) contributes an empty title list, so its `bm25_top5` /
  `dense_top5` cell is written empty and its `bm25_gold_found` is `0`. The list
  is never stringified from a missing scalar, so a fabricated title such as
  `"nan"` can never appear in the shortlist.

## 5. Refusal contract (both tools)

Fail-fast (never silently inner-join or coerce) on:

- wrong columns; a non-uniform or wrong method; a missing/extra `setting` value
  in the data; a duplicate `(setting, example_id)`;
- a binary hit cell whose **physical lexeme** is outside the frozen set of §1.1,
  refused on the text before any conversion — including a precision-adjacent
  fraction that a numeric cast would round to a clean `0`/`1`;
- a `[0,1]` float metric cell that is not a finite decimal lexeme, and a finite
  decimal lexeme whose exact value falls **outside the inclusive `[0,1]` domain**
  — a negative, a value greater than one, an overflow spelling such as `1e9999`,
  and a boundary-adjacent decimal that `float()` would round into range;
- an **empty metric cell outside the three per-question `@10` recall slots** of
  §1.2 — a blank pooled recall, a blank per-question `@2`/`@5`, or a blank
  reciprocal rank — refused before conversion and before any write, whether or
  not the selected criterion consumes that column;
- a **populated metric cell inside those three slots** — the inverse half of the
  same rule — refused on the same terms: an approved `0`/`1`/`0.0`/`1.0` lexeme
  and an in-range `[0,1]` decimal refuse there exactly as a malformed token
  does, because the frozen K policy declares the metric absent. The refusal
  applies to the BM25, dense, and optional rerank inputs of both tools, so no
  general reporting run can publish from a bundle the rescue tool refuses;
- a **populated null-like token** (`NaN`, `NA`, `null`, `None`, …) in any metric
  column, which must not be mistaken for the schema's deliberate blank;
- a null, non-string, or empty `example_id` / `question` / `gold_titles`; a
  missing or non-string `retrieved_titles` (an *empty* one is legal, §1.2); a
  `question_type` or `level` outside the shared schema's closed vocabulary;
- cross-method `example_id` mismatch in any setting; cross-method metadata
  drift, including a one-sided missing value;
- a consumed cell that is empty or not a plain integer `0`/`1` — for BM25,
  dense, **and** the optional rerank frame — including a `bool`, a float-dtype
  column, or a numeric string;
- an unsupported `criterion`, or an unsupported `setting` argument (§2).

The same refusals apply when the tool is called on an **already-created
DataFrame** rather than a file, for every invariant a typed frame can still
express (§1.3). Specifically, `extract_disagreements` and `build_shortlist`
refuse a direct BM25, dense, or optional rerank frame that carries:

- a **present value in any of the three required-empty** per-question `@10`
  recall slots — including a genuine integer `0`/`1` and an in-range `[0,1]`
  float, because placement is not spelling;
- a **missing value in any of the other 19** metric slots, including a `NaN` in
  a partial-recall or reciprocal-rank column and a `pd.NA` in a binary column;
- a binary column that is not a genuine integer column — `bool`, float-laundered
  `0.0`/`1.0`, string, or `object` dtype — or a populated binary cell that is
  not exactly `0` or `1`;
- a partial-recall or reciprocal-rank cell that is non-numeric, negative,
  greater than one, or non-finite (`NaN` in a required-populated slot,
  `±inf` anywhere).

None of these is repaired: the frame is refused as supplied. What the typed
layer cannot refuse is a *spelling* defect, which no longer exists once the
frame is parsed; that stays the sole responsibility of `read_formal_result_csv`
on the file path.

Because all validation precedes any type conversion and any write, a refusal
never creates or overwrites the destination.

## 6. Formal outputs and provenance

Default formal outputs are `results/disagreement_cases.csv`
(`full_evidence_recall@5`, pooled) and `results/bm25_failure_shortlist.csv`
(`full_evidence_recall@5`, pooled, 15 per signal). Both are mandated,
persisted artifacts of this contract, not optional by-products. Reruns on the
same input bundle are byte-stable. Input/output SHA-256 fingerprints and the
generator provenance are recorded in the DR-004 registry and in the appended
maintainer responses of the DR-004 review artifacts.
