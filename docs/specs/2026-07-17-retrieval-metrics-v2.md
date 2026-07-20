# Retrieval Metrics v2 Definition

- **Metric-definition version:** `retrieval_metrics_v2`
- **Decision status:** Metric semantics confirmed by Xin on 2026-07-17
- **Golden-example status:** Verified by Xin on 2026-07-17
- **Applies to:** evaluation artifacts derived from raw Dense, BM25, and reranker rankings
- **Canonical naming policy:** V2 machine identifiers are the only identifiers emitted by active evaluators,
  aggregate writers, experiment outputs, and downstream consumers

This specification freezes metric meaning and the canonical v2 metric identifiers independently of the raw/eval
storage refactor. Implementations and validators must follow this document; changing a formula or edge-case policy
requires an explicit new metric-definition version rather than a silent edit under `retrieval_metrics_v2`.

Legacy-only identifiers are accepted only by an explicitly versioned, read-only migration adapter. They may appear in
historical documentation, migration mappings, parity audits, and temporary migration inputs, but active v2 writers and
consumers must never emit or accept them directly. After v2 cutover, legacy-named experiment artifacts must leave the
active repository tree; Git history and documentation preserve the audit trail.

This document does not by itself define the complete physical eval-file contract. Exact file names, column order,
types, nullability, keys, and serialization rules belong to the separately versioned eval-schema specification.

## 1. Evidence unit and ranking semantics

For question `q`:

- `G_q` is the non-empty set of unique mapped gold evidence titles.
- `T_q = [t_1, ..., t_L]` is the retrieved-title sequence in rank order, with one-based rank positions.
- `R_{q,k}` is the set of titles appearing in the first `min(k, L)` positions of `T_q`.
- `c_{q,k} = |G_q ∩ R_{q,k}|` is the number of distinct gold titles retrieved by cutoff `k`.

Matching is title-based after the upstream gold-title mapping step. Duplicate retrieved titles still occupy ranking
positions, but the same gold title contributes at most one hit. Reciprocal rank uses the first occurrence of a gold
title. A list shorter than `k` may be evaluated using all available positions only when the manifest proves that the
ranking is complete because the corpus was exhausted. A ranking truncated below a requested cutoff or RR horizon is
insufficient input and must be rejected rather than padded or interpreted as retrieval failure.

An empty `G_q` is a data-validation error. It must fail before metric calculation and must not be interpreted as a
successful example or silently included in an aggregate denominator.

## 2. Per-example definitions

### 2.1 Any Evidence Hit Indicator@k

```text
any_evidence_hit_indicator_at_k(q) = 1(c_{q,k} > 0)
```

### 2.2 Full Evidence Hit Indicator@k

```text
full_evidence_hit_indicator_at_k(q) = 1(c_{q,k} = |G_q|)
```

Because empty gold sets are rejected, this definition never relies on vacuous truth.

### 2.3 Evidence Recall@k

```text
evidence_recall_at_k(q) = c_{q,k} / |G_q|
```

This is a coverage fraction in `[0, 1]`. It includes zero, incomplete, and full-coverage examples; it is not a binary
"some but not all" indicator.

### 2.4 Reciprocal Rank@h

For horizon `h` in `{10, 50}`, let `r_{q,h}` be the smallest rank `j <= h` whose title belongs to `G_q`.

```text
reciprocal_rank_at_h(q) = 1 / r_{q,h}, if such a rank exists
reciprocal_rank_at_h(q) = 0, otherwise
```

RR@10 examines only ranks 1–10. RR@50 examines only ranks 1–50. The per-example values are called RR@10 and RR@50;
only their macro averages across questions are called MRR@10 and MRR@50.

## 3. Setting and cutoff policy

| Setting | Hit/recall metrics | Reciprocal-rank metrics |
|---|---|---|
| `pooled` | compute @2, @5, and @10 | compute RR@10 and RR@50 |
| `per_question` | compute @2 and @5; keep all @10 hit/recall fields deliberately `NaN` | compute RR@10 and RR@50 |

Under the frozen v2 evaluation protocol, the `per_question` @10 fields remain deliberately uncomputed. They must not
be reinterpreted or filled as Evidence Recall@10, Any Evidence Hit Indicator@10, or Full Evidence Hit Indicator@10.
This is a v2 protocol decision rather than a consequence of retaining legacy field names. Legacy values are used only
to verify migration parity where the corresponding metric was previously computed.

## 4. Aggregation and missing values

Every formal aggregate is a macro average: compute the per-example value first, then give each valid question equal
weight.

For metric `m` in aggregation group `S`:

```text
V_m = {q in S | m(q) is not NaN}
n_valid(m) = |V_m|
aggregate(m) = sum(m(q) for q in V_m) / n_valid(m), when n_valid(m) > 0
aggregate(m) = NaN, when n_valid(m) = 0
```

Each aggregate metric records its own `n_valid`; `n_questions` alone is not an acceptable denominator description.
NaNs are skipped, not converted to zero. No micro-averaged evidence-recall metric is part of
`retrieval_metrics_v2`.

The only permitted per-example NaNs are the three deliberately uncomputed `per_question` @10 hit/recall values from
Section 3. All pooled metrics and all reciprocal-rank metrics are required. Any other missing metric is a schema or
evaluation error and must not be silently absorbed by the aggregation rule. The eval-schema specification must define
one unambiguous serialized null representation; literal strings such as `"NaN"`, `"None"`, and `"null"` are not metric
values.

## 5. Canonical v2 identifiers and report labels

V2 identifiers are the active canonical schema. The metavariables `k` and `h` in formulas and prose are never literal
serialized suffixes. Physical v2 fields expand them to the exact numeric cutoffs listed below.

### 5.1 Exact per-example identifiers

```text
any_evidence_hit_indicator_at_2
any_evidence_hit_indicator_at_5
any_evidence_hit_indicator_at_10
full_evidence_hit_indicator_at_2
full_evidence_hit_indicator_at_5
full_evidence_hit_indicator_at_10
evidence_recall_at_2
evidence_recall_at_5
evidence_recall_at_10
reciprocal_rank_at_10
reciprocal_rank_at_50
```

### 5.2 Exact aggregate identifiers

```text
any_evidence_hit_rate_at_2
any_evidence_hit_rate_at_5
any_evidence_hit_rate_at_10
full_evidence_hit_rate_at_2
full_evidence_hit_rate_at_5
full_evidence_hit_rate_at_10
macro_evidence_recall_at_2
macro_evidence_recall_at_5
macro_evidence_recall_at_10
mean_reciprocal_rank_at_10
mean_reciprocal_rank_at_50
```

### 5.3 Central report-label mapping

| V2 per-example family | V2 aggregate family | Aggregate report label |
|---|---|---|
| `any_evidence_hit_indicator_at_k` | `any_evidence_hit_rate_at_k` | Any Evidence Hit Rate@k |
| `full_evidence_hit_indicator_at_k` | `full_evidence_hit_rate_at_k` | Full Evidence Hit Rate@k |
| `evidence_recall_at_k` | `macro_evidence_recall_at_k` | Macro Evidence Recall@k |
| `reciprocal_rank_at_h` | `mean_reciprocal_rank_at_h` | MRR@h |

Report labels are presentation-only and must come from one centralized mapping. They are never storage identifiers.

### 5.4 Migration-only aliases

| Legacy-only identifier template | Canonical v2 identifier template |
|---|---|
| `any_evidence_recall@k` | `any_evidence_hit_indicator_at_k` |
| `full_evidence_recall@k` | `full_evidence_hit_indicator_at_k` |
| `partial_evidence_recall@k` | `evidence_recall_at_k` |

`reciprocal_rank_at_10` and `reciprocal_rank_at_50` are unchanged and remain canonical. A bare legacy `mrr` field
cannot be migrated without an explicit source horizon and must otherwise be rejected. New experiment writers MUST NOT
emit legacy-only aliases. Active consumers MUST NOT accept them except through the versioned migration adapter.

`Incomplete Evidence Indicator/Rate@k` is not a formal field in the frozen v2 result schema. Failure analysis may
derive it as:

```text
incomplete_evidence_indicator_at_k(q) = 1(0 < c_{q,k} < |G_q|)
Incomplete Evidence Rate@k = macro mean of that indicator
```

For non-empty gold sets the per-example indicator equals Any Evidence Hit Indicator@k minus Full Evidence Hit
Indicator@k. Its aggregate equals Any Evidence Hit Rate@k minus Full Evidence Hit Rate@k only when both rates use the
same aggregation group and identical valid-example set; validators must enforce that condition.

## 6. Manifest requirement

Every v2 eval manifest must store:

```json
{
  "metric_definition_version": "retrieval_metrics_v2",
  "evaluation_protocol_version": "hotpotqa_retrieval_protocol_v2",
  "eval_schema_version": "retrieval_eval_schema_v2"
}
```

The three versions are independent: formula or edge-case changes require a new metric-definition version; setting,
cutoff, or required-depth changes require a new evaluation-protocol version; file-shape or serialization changes
require a new eval-schema version. An evaluator must reject any unsupported version rather than silently substituting
another contract.

## 7. Verified golden examples

These are Xin-verified expected values and must be encoded in automated tests before v2 cutover.

### 7.1 Duplicate results occupy ranks but do not duplicate hits

```text
G = {A, B}
retrieved = [A, A, X, B, Y]
```

| Metric | Expected value |
|---|---:|
| Any Evidence Hit Indicator@2 | 1 |
| Full Evidence Hit Indicator@2 | 0 |
| Evidence Recall@2 | 0.5 |
| Any Evidence Hit Indicator@5 | 1 |
| Full Evidence Hit Indicator@5 | 1 |
| Evidence Recall@5 | 1.0 |
| RR@10 | 1.0 |
| RR@50 | 1.0 |

### 7.2 First gold after the requested recall cutoff

```text
G = {A, B}
retrieved = [X, Y, B, A]
first gold B is at rank 3; second gold A is at rank 4; both are within top-5
```

| Metric | Expected value |
|---|---:|
| Any Evidence Hit Indicator@2 | 0 |
| Full Evidence Hit Indicator@2 | 0 |
| Evidence Recall@2 | 0.0 |
| Any Evidence Hit Indicator@5 | 1 |
| Full Evidence Hit Indicator@5 | 1 |
| Evidence Recall@5 | 1.0 |
| RR@10 | 1/3 |
| RR@50 | 1/3 |

### 7.3 RR horizons are independent

```text
setting = pooled
G = {A}
retrieved ranks 1–10 contain no gold; rank 11 is A
```

| Metric | Expected value |
|---|---:|
| Any Evidence Hit Indicator@10 | 0 |
| Full Evidence Hit Indicator@10 | 0 |
| Evidence Recall@10 | 0.0 |
| RR@10 | 0.0 |
| RR@50 | 1/11 |

If no gold occurs in the first 50 positions, both RR@10 and RR@50 are `0.0`.

### 7.4 Empty gold is invalid

```text
G = {}
retrieved = [A, B]
expected = data-validation error before any metric value is emitted
```

### 7.5 Per-question @10 hit/recall values remain uncomputed

```text
setting = per_question
G = {A, B}
retrieved = [A, X, B]
```

| Metric | Expected value |
|---|---:|
| Any Evidence Hit Indicator@10 | NaN |
| Full Evidence Hit Indicator@10 | NaN |
| Evidence Recall@10 | NaN |
| RR@10 | 1.0 |
| RR@50 | 1.0 |

The @10 NaNs express a deliberate setting policy, not retrieval failure. Reciprocal-rank metrics remain computed.

### 7.6 NaN-aware macro aggregation

For one metric with per-example values `[1.0, 0.5, NaN]`:

```text
n_questions = 3
n_valid = 2
aggregate = 0.75
```

For values `[NaN, NaN]`:

```text
n_questions = 2
n_valid = 0
aggregate = NaN
```

### 7.7 Five-question coverage example

For hit counts `[2/2, 2/2, 1/2, 1/2, 0/2]`:

| Aggregate | Expected value |
|---|---:|
| Any Evidence Hit Rate@k | 0.8 |
| Full Evidence Hit Rate@k | 0.4 |
| Evidence Recall@k | 0.6 |
| Derived Incomplete Evidence Rate@k | 0.4 |

The incomplete rate is verified as a derived failure-analysis value, not emitted as a formal v2 result-schema field.
