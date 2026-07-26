# Reranker Rescue / Damage Analysis — Spec

- Date: 2026-07-26
- Status: Criteria agreed by Xin and Jiajun (2026-07-26); counting implementation pending (owner: Jiajun)
- Revision: 2026-07-26 — froze the formal output contract (§9: exact `OUTPUT_COLUMNS`, vocabularies,
  21-row key set, types, blank-cell / full-precision rules, deterministic order) and completed the
  input-bundle fail-fast contract (§2: method-uniformity, setting vocabulary/cardinality, cross-method
  and cross-setting ID identity, consumed-cell 0/1). Owner freeze choices: `criterion` uses the base
  metric names `full_evidence_recall` / `any_evidence_recall`; cross-setting ID equality is required;
  row order is `criterion → setting → k → question_type`.
- Revision: 2026-07-26 (round-2 corrective pass) — corrected the column-count wording (the frozen
  §9.1 schema is **17** columns, not 18; two "18-column" references fixed); bound cross-setting
  identity to metadata (each `example_id`'s `question_type` / `level` / `question` / `gold_titles`
  must be identical across both settings and both methods); added explicit reject/accept controls for
  same-id cross-setting metadata drift, populated per_question `@10` cells, and wrong physical row
  order. No agreed criterion changed.
- Applies to (inputs): `results/dense_results.csv` (first stage), `results/rerank_results.csv` (second stage)
- Produces (output): `results/rerank_rescue_damage.csv`
- Related: `docs/specs/2026-07-15-results-csv-schema.md` (the shared long-format result schema both inputs follow)

## 1. Purpose

Aggregate recall gains (for example, pooled Full Evidence Recall@5 rising from dense 0.502 to
rerank 0.654) show that reranking helps *on average* but not *where* it helps or what it costs. A
rescue/damage analysis decomposes that scalar change into per-question transitions between the
first-stage dense retriever and the second-stage cross-encoder reranker.

This document records the evaluation criteria the team agreed on. It defines the counting rule but
contains **no result numbers** and no research interpretation. The counting logic is a hand-written
evaluation component (see §10, Ownership); it is not machine-generated.

## 2. Inputs and input contract

Both formal result files follow the shared long-format schema (`RESULT_COLUMNS` in
`src/results_schema.py`): one row per `(method, setting, example_id)`.

- `results/dense_results.csv` — first stage (dense retrieval).
- `results/rerank_results.csv` — second stage (in pooled, the dense top-50 shortlist reranked; in
  per_question, each question's own candidate set reranked).

Join key: `(setting, example_id)`. The join **must be one-to-one**. Before any counting, verify
**every** item below and **fail-fast** on any violation (never silently inner-join and continue).

**Per-file structural contract (this formal run):**

- both files expose exactly `RESULT_COLUMNS`, in that order;
- every row of `results/dense_results.csv` has `method == "dense"`, and every row of
  `results/rerank_results.csv` has `method == "rerank"` (the shared schema also permits `bm25`, so
  the method label must be checked, not assumed);
- the `setting` column contains exactly the vocabulary `{pooled, per_question}` — both present, no
  other value;
- each file has exactly 1000 rows = 500 `pooled` + 500 `per_question`;
- within each setting, `(setting, example_id)` is unique, i.e. exactly 500 unique example IDs per
  setting per file.

**Cross-file / cross-setting identity contract:**

- for each setting, the dense and rerank files cover the **identical** 500 example-id set
  (cross-method parity, also required by the one-to-one join);
- the `pooled` and `per_question` settings use the **identical** 500 example-id set (cross-setting
  parity — a required contract invariant of this accepted run);
- `question_type`, `level`, `question`, and `gold_titles` are properties of the example, not of the
  method or setting, so for each `example_id` **all four rows** — `(dense, pooled)`,
  `(dense, per_question)`, `(rerank, pooled)`, `(rerank, per_question)` — must carry identical values
  for those four fields. This binds them across **both** methods **and** both settings, not only
  within a joined `(setting, example_id)` key; same-id cross-setting metadata drift (e.g. an
  `example_id` labeled `bridge` under pooled but `comparison` under per_question) is a fail-fast.

**Consumed metric-cell contract:**

- per_question `@10` recall columns are intentionally empty (K policy: a ~10-paragraph corpus makes
  @10 trivial) and are **never** consumed; pooled has all three cutoffs, per_question only `@2`/`@5`;
- every metric cell actually consumed as a binary criterion (Full or Any at a valid setting/k) must
  be exactly `0` or `1`; an empty or non-0/1 value in a consumed cell triggers fail-fast, never a
  silent row drop.

**Required reject / accept controls (input):**

- reject a `results/dense_results.csv` whose `method` is uniformly `bm25` (or mixed); accept uniform
  `dense` (and uniform `rerank` for the rerank file);
- reject a missing/extra `setting` value or wrong per-setting cardinality; accept exactly 500 + 500;
- reject cross-method ID drift (dense vs rerank IDs differ within a setting) **and** cross-setting ID
  drift (pooled ID set ≠ per_question ID set); accept the identical 500 IDs across both methods and
  both settings;
- reject same-`example_id` metadata drift in any of `question_type`, `level`, `question`,
  `gold_titles` across the four `(method, setting)` rows (in particular cross-setting drift, e.g. one
  field differing between an ID's pooled and per_question rows); accept the bundle where all four rows
  per `example_id` agree on those fields;
- reject a populated per_question `@10` recall cell (any of the three `@10` recall columns non-empty
  in a per_question row); accept blank per_question `@10` cells;
- reject a consumed cell that is empty or not `0`/`1`; accept `0`/`1`.

## 3. Concept: per-question paired comparison (dense → rerank)

For one question, compare the hit outcome before (dense) and after (rerank) under a chosen **binary
hit criterion**:

```
              rerank hit?
              no            yes
dense  no  |  stable_miss   RESCUE
hit?   yes |  DAMAGE        stable_hit
```

- **Rescue**: dense miss → rerank hit (reranking fixed the question).
- **Damage**: dense hit → rerank miss (reranking broke the question).
- The other two cells (`stable_hit`, `stable_miss`) are unchanged by reranking.
- Net effect = `#rescue − #damage`; the aggregate rate change equals `(rescue − damage) / N`.

## 4. Hit criterion: Full primary, Any diagnostic only

- **Primary:** `full_evidence_recall@k` — all gold titles for the question are within the top-k. This
  is the criterion most faithful to multi-hop evidence completeness.
- **Diagnostic:** `any_evidence_recall@5`, produced for **both** settings, to observe the
  "at least one hop found" movement. Do **not** add, merge, or treat Any and Full rescue/damage as
  the same events.
- **No** rescue/damage threshold is placed on `partial_evidence_recall@k`. Partial is retained only
  as an auxiliary delta; the classification is always driven by the binary Full column (or the
  clearly-labeled Any diagnostic column).

For each `criterion × setting × k`, every question falls into exactly one cell:

| dense hit | rerank hit | class |
|---:|---:|---|
| 0 | 0 | `stable_miss` |
| 0 | 1 | `rescue` |
| 1 | 0 | `damage` |
| 1 | 1 | `stable_hit` |

## 5. Cutoffs

Valid combinations are fixed as follows; invalid combinations must be skipped (never pad with 0,
never admit an empty cell into a denominator):

| setting | @2 | @5 | @10 |
|---|---|---|---|
| `pooled` | appendix | **primary** | appendix |
| `per_question` | appendix | **contrast primary** | not computed (schema K policy) |

The Any diagnostic is produced at `@5` only (both settings), not at other cutoffs, to avoid
confusion with the Full primary analysis.

## 6. Settings

- `pooled` is the main experiment and the source of the main table.
- `per_question` provides the same-criteria contrast, but only at the valid `@2` / `@5`.
- The two settings are summarized separately; counts are **never merged across settings**. Their
  candidate corpora and difficulty differ, so they serve only as a contrast, not an additive total.

## 7. Grouping

Every valid combination is reported for three groups:

- `overall` (N = 500);
- `bridge` (N = 404);
- `comparison` (N = 96).

Each row must retain its group `n` and report **both count and rate**, so 404-question and
96-question groups are never compared by raw counts. This version does not split by `level` (to
avoid many small groups); if a research question later requires it, add it as an explicit extension,
never as a silent change to this spec.

## 8. Boundary cases

- **Single gold title:** Full and Any then coincide numerically, but they remain two separate metric
  tables and must not be cross-added. (The current formal 500 questions each have 2 gold titles, so
  this boundary does not arise in this run.)
- **Partial 0.5 → 1.0:** a clear `rescue` under Full (Full goes 0 → 1); the reverse 1.0 → 0.5 is a
  `damage`.
- **Partial 0 → 0.5 with Full still 0:** not a rescue; may be recorded in a per-question auxiliary
  field as `stable_miss` + `partial_gain`.
- **Dense and rerank both miss, but rank improved:** not counted as a rescue. Prefer
  `partial_delta = rerank_partial − dense_partial` to record soft improvement/regression. If partial
  is unchanged but the gold's out-of-cutoff ordering improved, this may be noted per-question as
  `dense_bottleneck_gold_rank` / `rerank_bottleneck_gold_rank`, but it is **not** in the main summary
  table and is **not** called a rescue. Each stage's bottleneck rank is defined as the **maximum
  1-based rank over that question's gold titles** — the worst-ranked gold, the one that determines
  whether Full@k is met. It is computed only from gold ranks observable in that stage's stored
  `retrieved_titles`: it has a value only when **all** gold titles appear in the stored list; if any
  gold is absent it must be left empty — never inferred as 0, `storage_depth + 1`, infinity, or any
  concrete rank beyond the pooled top-50 / per_question storage depth.
- **Null or illegal values:** every cell to be compared must be 0/1. Outside per_question `@10`, any
  empty cell or any non-0/1 value must trigger fail-fast, never a silent row drop.

## 9. Formal output contract

The formal summary is written to `results/rerank_rescue_damage.csv` with an **exact, frozen**
physical schema: no extra columns, no reordering, no additional rows. "At least these columns" is
explicitly **not** the rule — the schema below is complete and closed.

### 9.1 Columns (exact set and order)

```text
criterion, setting, k, question_type, n,
dense_hits, rerank_hits,
stable_miss, rescues, damages, stable_hit,
rescue_rate, damage_rate, net_count, net_rate,
rescue_given_dense_miss, damage_given_dense_hit
```

These 17 columns, in this order, are the complete schema. A missing, extra, or reordered column is
non-compliant.

### 9.2 Value vocabularies and types

- `criterion` ∈ {`full_evidence_recall`, `any_evidence_recall`} — the base metric name only; the
  cutoff is carried solely by `k`. A row `(criterion, setting, k)` is computed from the input column
  `{criterion}@{k}` of that setting (e.g. `criterion=full_evidence_recall, setting=pooled, k=5`
  reads `full_evidence_recall@5`). Tokens such as `full`, `Full`, or `full_evidence_recall@5` are
  non-compliant.
- `setting` ∈ {`pooled`, `per_question`}.
- `k` ∈ {`2`, `5`, `10`}, written as a plain integer.
- `question_type` ∈ {`overall`, `bridge`, `comparison`} (`overall` is the whole-group total row).
- Integer columns — `n`, `dense_hits`, `rerank_hits`, `stable_miss`, `rescues`, `damages`,
  `stable_hit`, `net_count` — are serialized as plain integers. Counts are ≥ 0; only `net_count`
  may be negative.
- Rate columns — `rescue_rate`, `damage_rate`, `net_rate`, `rescue_given_dense_miss`,
  `damage_given_dense_hit` — are floats. `rescue_rate`, `damage_rate`, `rescue_given_dense_miss`,
  `damage_given_dense_hit` ∈ [0, 1]; `net_rate` ∈ [−1, 1]. They are serialized at **full precision**
  (no rounding) — the same invariant the oracle relies on (§9.5), so a formal `net_rate` must never
  be rounded before serialization.
- A conditional rate with a **zero denominator** (`rescue_given_dense_miss` when `n == dense_hits`;
  `damage_given_dense_hit` when `dense_hits == 0`) is serialized as a **blank CSV cell** (empty
  field) — never `0`, never the literal `NaN`, never a fabricated value. Its raw counts stay
  populated.

### 9.3 Row key and the exact 21-row set

The unique row key is `(criterion, setting, k, question_type)`. The file contains **exactly** 21
rows: the 7 valid `(criterion, setting, k)` combinations, each once per `question_type`. No
duplicate, missing, or extra combination is permitted.

The 7 valid `(criterion, setting, k)` combinations:

| criterion | setting | k |
|---|---|---|
| `full_evidence_recall` | `pooled` | 2 |
| `full_evidence_recall` | `pooled` | 5 |
| `full_evidence_recall` | `pooled` | 10 |
| `full_evidence_recall` | `per_question` | 2 |
| `full_evidence_recall` | `per_question` | 5 |
| `any_evidence_recall` | `pooled` | 5 |
| `any_evidence_recall` | `per_question` | 5 |

Each combination appears once for each `question_type` ∈ {`overall`, `bridge`, `comparison`} →
7 × 3 = **21 rows**. Invalid combinations (Any at @2/@10, Full per_question @10, any other) must be
**absent**, never zero-filled.

### 9.4 Deterministic row order

Rows are sorted by `(criterion, setting, k, question_type)` with these fixed orders:

- `criterion`: `full_evidence_recall` before `any_evidence_recall`;
- `setting`: `pooled` before `per_question`;
- `k`: ascending;
- `question_type`: `overall`, then `bridge`, then `comparison`.

### 9.5 Definitions, identities, and independent oracle

```text
dense_hit_rate  = dense_hits / n
rerank_hit_rate = rerank_hits / n
rescue_rate     = rescues / n
damage_rate     = damages / n
net_count       = rescues - damages
net_rate        = net_count / n
                = (rerank_hits - dense_hits) / n
                = rerank_hit_rate - dense_hit_rate

rescue_given_dense_miss = rescues / (n - dense_hits)
damage_given_dense_hit  = damages / dense_hits
```

The two conditional rates have different denominators, are diagnostic only, and **must not be
subtracted from each other**. On a zero denominator, output a blank cell and keep the raw count
(§9.2); do not fabricate 0%.

Every summary group must pass these consistency checks:

```text
n           = stable_miss + rescues + damages + stable_hit
dense_hits  = damages + stable_hit
rerank_hits = rescues + stable_hit
net_count   = rescues - damages
net_rate    = rerank_hit_rate - dense_hit_rate
```

**Independent aggregate oracle.** For each `(criterion, setting, k, question_type)`, `net_rate` must
also equal the rerank-mean minus dense-mean that `scripts/reporting/summarize_results.py` computes
for the same inputs, the input column `{criterion}@{k}`, and the same grouping. Recheck `overall`
with `--group-by method setting`; recheck `bridge` / `comparison` with
`--group-by method setting question_type`. This check must re-average the two accepted input files
directly — it must **not** be derived from the rescue/damage counts, or it is not an independent
regression check.

The oracle must use **full-precision means**: call `summarize()` for the unformatted DataFrame, or
read the general-summary `--out` CSV (which writes with `float_format=None`, i.e. unrounded). Do not
parse the three-decimal display Markdown, and do not back-infer integer counts from rounded rates.
Compare integer identities exactly; compare the floating `net_rate` against the aggregate mean
difference with `math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-9)`, to avoid false failures
from floating-point representation or display rounding.

### 9.6 Required reject / accept controls (output)

- reject an unknown `criterion` token (e.g. `full`, `full_evidence_recall@5`); accept exactly
  {`full_evidence_recall`, `any_evidence_recall`};
- reject a duplicate, missing, or extra `(criterion, setting, k, question_type)` key; accept exactly
  the 21-row matrix;
- reject any invalid combination present (Any @2/@10, Full per_question @10, …); accept only the 7
  valid combinations;
- reject a fabricated (non-blank) zero-denominator conditional rate; accept a blank cell;
- reject a rounded `net_rate` that breaks the full-precision oracle invariant; accept
  round-trippable full precision;
- reject a reordered, extra, or missing column; accept exactly the 17-column order of §9.1;
- reject rows serialized in any order other than §9.4; accept the exact §9.4 row order.

## 10. Ownership and boundary

- **Counting logic (hand-written, owner: Jiajun):** join the two inputs, classify each question per
  the criteria above, and emit the summary table. This is an evaluation-judgment rule and lives on
  the team's hand-written evaluator boundary (`src/evaluator.py` or a shared analysis script). It is
  not machine-generated.
- **Inputs:** the two aligned, independently-accepted result CSVs are already produced; they share
  the schema and example-id set required by §2.
- **Interpretation:** the failure-analysis reading (why particular questions are rescued or damaged)
  is written separately by the analysis owner; it is not part of this counting spec.
