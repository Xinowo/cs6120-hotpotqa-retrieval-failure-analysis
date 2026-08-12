---
status: active
last_updated: 2026-08-12
---

# Per-Example Reranker Rescue / Damage Cases — Spec

- Date: 2026-08-12
- Status: downstream analysis artifact; the accepted aggregate contract is unchanged
- Applies to (inputs): `results/dense_results.csv` (first stage), `results/rerank_results.csv` (second stage)
- Produces (output): `results/rerank_rescue_damage_cases.csv`
- Upstream authority: `docs/specs/2026-07-26-reranker-rescue-damage.md` (the accepted aggregate
  contract and the §2 input contract this artifact reuses verbatim)
- Related: `docs/specs/2026-07-15-results-csv-schema.md` (the shared long-format result schema both
  inputs follow), `docs/specs/2026-07-27-bm25-dense-reporting-contracts.md` (the shared physical
  input domains)

## 1. Purpose

`results/rerank_rescue_damage.csv` answers *how many* questions the reranker rescued and broke. It
cannot answer *which* ones, so every reading of a rescue or a damage currently has to be
reconstructed by hand from the two result files.

This artifact is that reconstruction, done once and deterministically: one row per
`(setting, example_id, k)` under the **Full Evidence** criterion, carrying both stages' hit outcome,
both stages' observed gold ranks, and the transition class. It is a **downstream** artifact. It
adds no metric, changes no accepted number, and must not alter
`results/rerank_rescue_damage.csv` or its frozen §9 contract.

The interpretation of a particular case — *why* a question was rescued or damaged — is written
separately by the analysis owner and is not part of this spec.

## 2. Inputs and input contract

The inputs and their contract are exactly those of the aggregate spec
(`docs/specs/2026-07-26-reranker-rescue-damage.md` §2), reused without narrowing or widening: the
same reader (`scripts/reporting/formal_result_inputs.py`), the same per-file structural contract,
the same cross-file / cross-setting identity contract, and the same one-to-one join on
`(setting, example_id)`. A generator for this artifact **must** reuse
`scripts/reporting/rescue_damage.py`'s `load_and_validate_inputs()` and `build_paired_frame()`
rather than introduce a second, weaker loader; two loaders would be two input languages.

Beyond the reused contract, this artifact reads two fields the aggregate never consumes, so it
closes them here:

- `gold_titles` is split on the shared exact-title separator (`TITLE_SEPARATOR` in
  `src/results_schema.py`). Every component must be a non-empty title and the list must contain **no
  duplicate title**: a duplicate cannot survive as a JSON object key, and silently collapsing it
  would drop a gold requirement from the record;
- `retrieved_titles` is split the same way. An empty cell is the approved empty retrieved list and
  yields no ranks at all — it is never treated as a missing value.

## 3. Criterion, settings, and cutoffs

The criterion is `full_evidence_recall` only. The Any diagnostic is deliberately absent: the
aggregate spec §4 forbids merging or confusing Any and Full rescue/damage events, and a per-example
file carrying both criteria in one row invites exactly that.

The valid `(setting, k)` combinations are the Full Evidence rows of the aggregate spec §5:

| setting | k |
|---|---|
| `pooled` | 2, 5, 10 |
| `per_question` | 2, 5 |

`per_question` at `k = 10` is **not** a cutoff of this artifact. The metric is not computed there
(schema K policy), the cell is required to be physically blank, and a generator must refuse the
combination rather than read the blank cell.

## 4. Transition classes

For each row, the dense and rerank Full@k outcomes place the example in exactly one class:

| dense | rerank | `transition` |
|---:|---:|---|
| 0 | 0 | `stable_miss` |
| 0 | 1 | `rescue` |
| 1 | 0 | `damage` |
| 1 | 1 | `stable_hit` |

All four classes are emitted, not only the two changed ones: the unchanged cells are what make the
file aggregate back to the accepted summary, and a file holding only changes cannot be checked
against it.

## 5. Formal output contract

### 5.1 Columns (exact set and order)

```text
setting, example_id, question_type, level, question, gold_titles, k,
dense_full_at_k, rerank_full_at_k, dense_gold_ranks, rerank_gold_ranks, transition
```

These 12 columns, in this order, are the complete schema. A missing, extra, or reordered column is
non-compliant.

### 5.2 Value vocabularies and types

- `setting` ∈ {`pooled`, `per_question`}; `k` ∈ {`2`, `5`, `10`}, written as a plain integer, and
  restricted per setting by §3.
- `example_id`, `question_type`, `level`, `question`, and `gold_titles` are copied verbatim from the
  joined inputs, where they are already bound to be identical across all four `(method, setting)`
  rows of the example. This artifact never rewrites, re-cases, or re-splits them.
- `dense_full_at_k` and `rerank_full_at_k` are the plain integers `0` or `1`.
- `transition` ∈ {`stable_miss`, `rescue`, `damage`, `stable_hit`} and is exactly the §4 cell of
  `(dense_full_at_k, rerank_full_at_k)`.

### 5.3 The gold-rank columns

`dense_gold_ranks` and `rerank_gold_ranks` are JSON objects mapping **each** gold title of the
example to its **1-based first** rank in that stage's stored `retrieved_titles`:

```json
{"Gold A":2,"Gold B":null}
```

- the rank semantics are the hand-written ones in `src/evaluator.py` (`gold_ranks()`): rank 1 is the
  top of the ranked list, and a title occurring more than once takes its first occurrence;
- a gold title **absent** from the stored retrieved list has the value `null`. It is never inferred
  as `0`, as `storage_depth + 1`, as infinity, or as any concrete rank beyond the stored retrieval
  depth (pooled top-50 / per-question storage depth) — the file records what is observable, and
  nothing else. This is the same rule the aggregate spec §8 states for the bottleneck rank;
- the object holds **every** gold title of the example, never a filtered subset, and its keys appear
  in the order they appear in the row's `gold_titles` cell. Serialization is compact and stable
  (`,` / `:` separators, no sorting, no whitespace, `ensure_ascii=False`), so a rerun on the same
  inputs is byte-identical;
- the ranks are the whole ranked list's ranks and are **not** cut off at `k`. `k` is applied by the
  reader: `full_at_k` holds exactly when every value is a non-null rank ≤ `k`, which is the identity
  §5.5 requires the file to satisfy.

### 5.4 Row key, cardinality, and deterministic order

The unique row key is `(setting, example_id, k)`. Each valid combination of §3 appears exactly once
per example, so the file holds `500 × (3 + 2) = 2500` rows for the accepted 500-example run. A
duplicate, missing, or extra key is non-compliant, and an invalid combination must be **absent**,
never emitted with a fabricated value.

Rows are sorted by `(setting, example_id, k)` with these fixed orders:

- `setting`: `pooled` before `per_question`;
- `example_id`: ascending lexicographic;
- `k`: ascending.

### 5.5 Identities and the safe writer

Two identities must hold for **every** row, and are checked before the destination is touched:

```text
full_at_k              = all(rank is not None and rank <= k for rank in gold_ranks)
transition             = TRANSITION[(dense_full_at_k, rerank_full_at_k)]
```

The first is checked in both directions and against the inputs: the value written to
`dense_full_at_k` / `rerank_full_at_k` must equal the `full_evidence_recall@k` value **saved in the
input file** for that stage, and it must equal the value the serialized ranks imply. A disagreement
means the stored ranked list and the stored metric describe different runs, and it is a fail-fast —
never a silent preference for one of the two.

The writer never coerces or truncates. It validates the complete, ordered frame, writes to a
temporary file, re-reads the persisted bytes and validates them again, and only then atomically
replaces the destination. A refusal at any step therefore never creates and never overwrites
`results/rerank_rescue_damage_cases.csv`.

### 5.6 Aggregate consistency with the accepted summary

Counting the `transition` column of this file must reproduce the Full Evidence rows of
`results/rerank_rescue_damage.csv` exactly — for each `(setting, k)` and each `question_type` group
(`overall`, `bridge`, `comparison`), the four class counts, `n`, `dense_hits`, and `rerank_hits`.

This is a one-directional check. The aggregate is the accepted artifact; if the two disagree, this
downstream file is wrong.

### 5.7 Required reject / accept controls (output)

- reject a missing, extra, or reordered column; accept exactly the 12-column order of §5.1;
- reject a `per_question` row at `k = 10`, and any other combination outside §3; accept exactly the
  five valid combinations;
- reject a duplicate `(setting, example_id, k)` key, a wrong row count, and any row order other than
  §5.4; accept the exact 2500-row key set in the §5.4 order;
- reject a `dense_full_at_k` / `rerank_full_at_k` cell that is not the plain integer `0` or `1`;
  accept `0` and `1`;
- reject a gold-rank object whose key set is not exactly the row's gold titles, whose value is
  neither `null` nor a positive integer, or whose implied `full_at_k` differs from the binary
  column; accept the object of §5.3;
- reject a row whose stored ranks imply a Full@k different from the saved input metric; accept the
  agreeing row;
- reject a `transition` outside the four-class vocabulary or inconsistent with the two binary
  columns; accept the §4 cell;
- reject on a failed validation **without** creating or overwriting the destination; accept an
  atomic replacement only after the persisted bytes have themselves been validated.

## 6. Ownership and boundary

- **Metric definitions** stay hand-written in `src/evaluator.py`. This artifact reuses
  `gold_ranks()` and `full_evidence_recall_at_k()`; it defines no metric of its own.
- **The counting rule** (the four-cell transition table) is the accepted aggregate spec's, restated
  here per example. This file changes none of it.
- **The generator** (`scripts/reporting/rerank_rescue_damage_cases.py`) is plumbing: it joins,
  extracts observable ranks, classifies by the frozen table, validates, and serializes.
- **Interpretation** of individual cases is written separately by the analysis owner.
