---
status: draft
last_updated: 2026-07-27
---

# Rank-Pattern Partition Specification for HotpotQA Gold Evidence

**Document type:** implementation specification
**Purpose:** define a mutually exclusive and collectively exhaustive partition of gold-evidence rank patterns for HotpotQA pooled top-50 retrieval results
**Primary audience:** coding agents and project contributors implementing retrieval diagnostics, CSV exports, and tests
**Project:** CS6120 — *When Multi-Hop Retrieval Fails: A Failure Analysis of BM25 and Dense Retrieval on HotpotQA*
**Status:** proposed implementation spec — round-2 corrected; pending a fresh independent review before implementation
**Last updated:** 2026-07-26

---

## 1. Objective

Implement an automatic, non-causal classification of where a question's gold-evidence titles appear in a retriever's ranked output.

The classification must:

1. depend only on observed gold-title ranks;
2. not assume which gold title is the first hop or second hop;
3. be mutually exclusive;
4. be collectively exhaustive over the supported input domain;
5. distinguish evidence inside the primary band cutoff (rank ≤ 5) from evidence ranked below it;
6. distinguish deeply ranked evidence from evidence absent from the stored retrieval list;
7. remain separate from human failure-cause labels such as:
   - `first-hop only`
   - `missing bridge entity`
   - `comparison coverage failure`
   - `lexical mismatch`
   - `dense semantic drift`
   - `distractor entity failure`

This specification defines a **rank-pattern partition**, not a causal failure taxonomy.

### 1.1 Relationship to existing frozen contracts (read first)

This spec is **additive and diagnostic**. It introduces one new, standalone,
pooled-only CSV artifact (Section 10) and changes nothing that already exists.
In particular:

- `src/evaluator.py` is **unchanged**. This spec reuses its `gold_ranks`
  semantics; it does not redefine, recompute, or extend any metric.
- `src/results_schema.py` `RESULT_COLUMNS` and the formal result CSVs
  (`results/*_results.csv`) are **unchanged**. No column is added, renamed, or
  removed there.
- The accepted any-based failure page (`scripts/build_failure_report.py` →
  `failures_review.html`) is **unchanged**. See Section 12.
- The planned coverage table and `hop_roles.csv`
  (`docs/Local/analysis/hop_role_review_design.md`, Section 14) are separate
  artifacts with separate keys and owners. `rank_pattern` is **additive** to
  them and does not replace `coverage_pattern`, `role_pattern`, or any human
  annotation. See Section 10.3.

---

## 2. Motivation

HotpotQA provides gold supporting-fact titles, but it does not explicitly label:

```text
first_hop_title
second_hop_title
bridge_entity
```

Therefore, rank information alone can determine only facts such as:

```text
one gold title is within top 5
the other gold title is ranked 11–50
```

Rank information alone cannot justify a causal statement such as:

```text
the retriever found the first hop but missed the second hop
```

The automatic system must therefore use neutral structural labels.

---

## 3. Scope

### 3.1 Supported corpus setting

Pooled-v1 targets **only** the pooled retrieval setting in which exactly 50
ranked results are stored per `(question, retriever)`. This matches the accepted
formal run contract (`src/results_schema.py` `STORE_DEPTH_BY_SETTING["pooled"]
== 50`; the formal pooled run `results/runs/2026-07-17_a` has
`corpus_setting == "pooled"` and `top_k_max == 50`).

The observation horizon is fixed:

```text
stored_depth = 50   (exact, not "up to 50")
```

The per-question setting (top-10) is **out of scope for v1** and, if ever
supported, requires a separate schema version with its own absence label (see
Section 14.5 and Section 15).

### 3.2 Band cutoffs

The partition uses two rank boundaries to cut the stored horizon into bands:

```text
band_cutoff_primary   = 5
band_cutoff_secondary = 10
stored_depth          = 50
```

> **Naming caution.** `band_cutoff_primary = 5` is only the *band boundary* of
> this structural partition. It is **not** the pooled failure taxonomy's
> "primary analysis cutoff," which
> `docs/Local/analysis/hop_role_review_design.md` Section 14.5 records as
> **@5 provisionally, not a frozen project fact**. This spec does not settle
> that owner decision. A band boundary at 5 is compatible with any later
> taxonomy-cutoff choice; the two are independent.

These produce four rank bands:

| Band | Rank condition | Meaning |
|---|---:|---|
| `top5` | `1 <= rank <= 5` | evidence is inside the primary band cutoff |
| `rank6_10` | `6 <= rank <= 10` | evidence is below the primary band cutoff but inside top 10 |
| `rank11_50` | `11 <= rank <= 50` | evidence is present in the stored list but ranked deeply |
| `not_in_top50` | no observed rank in `1..50` | evidence is absent from the stored top-50 list |

The phrase `not_in_top50` must not be interpreted as:

```text
absent from the corpus
```

It means only:

```text
absent from the stored top-50 retrieval results
```

(consistent with `docs/specs/2026-07-15-results-csv-schema.md`, "Interpretation
of truncation").

---

## 4. Terminology

### 4.1 Gold title

A unique Wikipedia title derived from HotpotQA `supporting_facts`.

Example:

```python
gold_titles = {
    "Something There",
    "Paige O'Hara",
}
```

Duplicate sentence-level supporting facts under the same title must be
deduplicated before rank-pattern classification. This mirrors how the runner
already stores `gold_titles` (a deduplicated, sorted set) in `details.jsonl`.

### 4.2 Gold rank (evaluator semantics — exact string, first occurrence)

For a gold title, the gold rank is the earliest 1-based rank at which that
**exact** title string appears in the retrieved ranking, or `None` if it does
not appear in the stored top-50.

This is exactly the contract of `src/evaluator.py` `gold_ranks()`
(`src/evaluator.py:39-58`):

- membership is exact Python string equality — **there is no title
  normalization function in the evaluator, and this spec must not invent one**;
- the first (smallest-rank) occurrence wins if a title repeats;
- a gold absent from the stored list maps to `None`, never omitted.

If duplicate retrieved titles appear, only the first occurrence determines the
gold rank:

```text
retrieved titles:
1. A
2. A
3. X
4. B
```

Then:

```text
rank(A) = 1
rank(B) = 4
```

### 4.3 Rank pattern

A normalized label describing the **unordered** combination of rank bands
occupied by the gold titles.

For the two-gold case:

```text
top5 + rank11_50
```

becomes:

```text
one_top5_one_11_50
```

---

## 5. Input Contract

The classifier accepts one `(question, retriever)` unit at a time.

### 5.1 Primary input — precomputed gold ranks (preferred)

The preferred and default input consumes the gold ranks **already computed by
the evaluator** and stored per retriever in `details.jsonl` under
`retrievers.<name>.gold_ranks`:

```python
{
    "example_id": str,
    "retriever": str,
    "question_type": str,          # copied through; not used for classification
    "gold_ranks": dict[str, int | None],   # exact gold title -> rank or None
}
```

`gold_ranks` is a dict keyed by the example's exact gold-title strings. By
construction (`evaluator.gold_ranks` and the `details.jsonl` validation in
`scripts/build_failure_report.py:230-242`) it always has exactly the example's
gold titles as keys, each value is an `int` in `[1, 50]` or `None`, and the key
set is already unique. The classifier therefore does not re-derive ranks in this
path; it only maps them to bands.

### 5.2 Secondary input — raw retrieved titles (testing / offline only)

A raw-title input is accepted only for offline testing and must reproduce
`evaluator.gold_ranks` exactly (exact string equality, earliest occurrence,
`None` when unobserved — Section 4.2, Section 9):

```python
{
    "example_id": str,
    "retriever": str,
    "gold_titles": list[str],
    "retrieved_titles": list[str],   # exactly 50 for pooled v1
}
```

The classifier must not introduce a second, inconsistent matching path. Exact
title equality is the frozen current evaluator contract; a future
normalization policy would be a separate, owner-approved evaluator/schema change
(and a schema-version bump — Section 15).

### 5.3 Required validation

The implementation must reject:

- an empty gold-title set / empty `gold_ranks`;
- a gold count other than 2 (pooled v1 classifies exactly two unique gold
  titles; see Section 7.1 and Section 14.3–14.4);
- a `bool` rank value (`True`/`False`), before any `int` check — `bool` is a
  subclass of `int` in Python, so `True` would otherwise be read as rank 1;
- a non-positive observed rank;
- an observed rank greater than 50 (the fixed pooled horizon);
- for the raw-title path, a `retrieved_titles` length other than 50 (the
  observation horizon must be exactly the pooled stored depth so a `None` gold
  provably means "absent from the stored 50," not "list happened to be short" —
  see Section 14.6).

There is **no dict-level "inconsistent duplicate key" validation**: a Python
`dict` (and a parsed JSON object) has already collapsed duplicate keys before
the classifier sees it, so such a check is not executable at this layer. Uniqueness
is instead guaranteed upstream (`gold_ranks` keys equal the example's gold
titles) and re-asserted here as "exactly 2 distinct gold titles."

Recommended error behavior:

```python
raise ValueError(...)   # contract violations
raise TypeError(...)    # wrong rank type, including bool
```

---

## 6. Core Rank-Band Function

Pooled-v1 fixes the horizon at exactly 50, so the band function takes no depth
parameter; a different depth is a different schema version (Section 15), not a
runtime argument.

Required behavior:

```python
rank_to_band(1)     == "top5"
rank_to_band(5)     == "top5"
rank_to_band(6)     == "rank6_10"
rank_to_band(10)    == "rank6_10"
rank_to_band(11)    == "rank11_50"
rank_to_band(50)    == "rank11_50"
rank_to_band(None)  == "not_in_top50"
rank_to_band(0)     -> ValueError
rank_to_band(-1)    -> ValueError
rank_to_band(51)    -> ValueError
rank_to_band(True)  -> TypeError
rank_to_band(False) -> TypeError
```

Reference pseudocode (single normative behavior; see Section 8 for the full
reference implementation):

```python
def rank_to_band(rank):
    if rank is None:
        return "not_in_top50"
    if isinstance(rank, bool):
        raise TypeError("Rank must be an int or None, not bool.")
    if not isinstance(rank, int):
        raise TypeError("Rank must be an int or None.")
    if rank < 1:
        raise ValueError("Rank must be >= 1.")
    if rank > 50:
        raise ValueError(f"Observed rank {rank} exceeds the pooled stored depth 50.")
    if rank <= 5:
        return "top5"
    if rank <= 10:
        return "rank6_10"
    return "rank11_50"
```

---

## 7. Two-Gold Partition

### 7.1 Assumption

This section applies when, and only when:

```text
number of unique gold titles = 2
```

Pooled v1 classifies exactly two unique gold titles. Every formal example
currently has exactly two gold titles (both bridge and comparison — verified in
`results/runs/2026-07-17_a/details.jsonl`), so this is the whole formal domain.
A count other than 2 must fail loudly (Section 5.3); it must not be coerced into
a two-gold label. Generalization to other counts is **non-normative** (Section
18).

The gold titles are treated as an unordered pair for structural classification.

Let:

```text
A = top5
B = rank6_10
C = rank11_50
D = not_in_top50
```

Because order does not matter, the number of possible multisets of size 2 drawn
from 4 bands is:

```text
C(4 + 2 - 1, 2) = C(5, 2) = 10
```

Therefore, the complete partition contains exactly 10 classes.

### 7.2 Complete class table

The last three columns are **descriptive** of the coverage each pattern implies
(matching the evaluator's any/full/partial states); they are not output columns
and introduce no new metric name. "full" = both golds within the cutoff, "zero"
= neither, "partial" = exactly one.

| Canonical label | Band pattern | Example gold ranks | Coverage @5 | Coverage @10 | Coverage @50 |
|---|---|---|---|---|---|
| `both_in_top5` | A + A | `[2, 4]` | full | full | full |
| `one_top5_one_6_10` | A + B | `[2, 8]` | partial | full | full |
| `one_top5_one_11_50` | A + C | `[2, 14]` | partial | partial | full |
| `one_top5_one_not_in_top50` | A + D | `[2, None]` | partial | partial | partial |
| `both_in_6_10` | B + B | `[6, 9]` | zero | full | full |
| `one_6_10_one_11_50` | B + C | `[8, 14]` | zero | partial | full |
| `one_6_10_one_not_in_top50` | B + D | `[8, None]` | zero | partial | partial |
| `both_in_11_50` | C + C | `[14, 30]` | zero | zero | full |
| `one_11_50_one_not_in_top50` | C + D | `[14, None]` | zero | zero | partial |
| `both_not_in_top50` | D + D | `[None, None]` | zero | zero | zero |

### 7.3 Formal partition properties

The implementation must guarantee:

#### Mutual exclusivity

For every valid two-gold input, exactly one canonical label is returned.

Formally:

```text
For every valid example x,
sum(1[label_i matches x]) = 1
```

#### Collective exhaustiveness

Every unordered pair of bands from:

```text
{top5, rank6_10, rank11_50, not_in_top50}
```

must map to one of the 10 labels.

No valid two-gold input may return:

```text
unknown
other
unclassified
```

unless the input itself violates the contract (in which case the classifier
raises, per Section 5.3).

---

## 8. Canonicalization Algorithm

### 8.1 Recommended approach

Do not implement the 10 classes using a long sequence of fragile conditional
statements.

Instead:

1. compute each gold title's rank (Section 5 / Section 9);
2. map each rank to a band;
3. count the number of gold titles in each band;
4. map the count tuple to one canonical label.

Count tuple:

```python
(
    n_top5,
    n_rank6_10,
    n_rank11_50,
    n_not_in_top50,
)
```

For two gold titles, all valid tuples sum to 2.

### 8.2 Canonical mapping table

```python
TWO_GOLD_PATTERN_MAP = {
    (2, 0, 0, 0): "both_in_top5",
    (1, 1, 0, 0): "one_top5_one_6_10",
    (1, 0, 1, 0): "one_top5_one_11_50",
    (1, 0, 0, 1): "one_top5_one_not_in_top50",
    (0, 2, 0, 0): "both_in_6_10",
    (0, 1, 1, 0): "one_6_10_one_11_50",
    (0, 1, 0, 1): "one_6_10_one_not_in_top50",
    (0, 0, 2, 0): "both_in_11_50",
    (0, 0, 1, 1): "one_11_50_one_not_in_top50",
    (0, 0, 0, 2): "both_not_in_top50",
}
```

### 8.3 Reference implementation

```python
from collections import Counter
from typing import Iterable, Optional


BANDS = (
    "top5",
    "rank6_10",
    "rank11_50",
    "not_in_top50",
)

STORED_DEPTH = 50  # pooled v1: fixed observation horizon


TWO_GOLD_PATTERN_MAP = {
    (2, 0, 0, 0): "both_in_top5",
    (1, 1, 0, 0): "one_top5_one_6_10",
    (1, 0, 1, 0): "one_top5_one_11_50",
    (1, 0, 0, 1): "one_top5_one_not_in_top50",
    (0, 2, 0, 0): "both_in_6_10",
    (0, 1, 1, 0): "one_6_10_one_11_50",
    (0, 1, 0, 1): "one_6_10_one_not_in_top50",
    (0, 0, 2, 0): "both_in_11_50",
    (0, 0, 1, 1): "one_11_50_one_not_in_top50",
    (0, 0, 0, 2): "both_not_in_top50",
}


def rank_to_band(rank: Optional[int]) -> str:
    if rank is None:
        return "not_in_top50"

    # bool is a subclass of int; reject it before the int check so True is not
    # silently read as rank 1.
    if isinstance(rank, bool):
        raise TypeError("Rank must be an int or None, not bool.")

    if not isinstance(rank, int):
        raise TypeError("Rank must be an int or None.")

    if rank < 1:
        raise ValueError("Rank must be >= 1.")

    if rank > STORED_DEPTH:
        raise ValueError(
            f"Observed rank {rank} exceeds the pooled stored depth {STORED_DEPTH}."
        )

    if rank <= 5:
        return "top5"

    if rank <= 10:
        return "rank6_10"

    return "rank11_50"


def classify_two_gold_rank_pattern(
    gold_ranks: Iterable[Optional[int]],
) -> str:
    ranks = list(gold_ranks)

    if len(ranks) != 2:
        raise ValueError(
            f"Pooled v1 classifies exactly 2 unique gold ranks, got {len(ranks)}."
        )

    bands = [rank_to_band(rank) for rank in ranks]
    counts = Counter(bands)

    key = (
        counts["top5"],
        counts["rank6_10"],
        counts["rank11_50"],
        counts["not_in_top50"],
    )

    try:
        return TWO_GOLD_PATTERN_MAP[key]
    except KeyError as exc:
        raise AssertionError(
            f"Unreachable two-gold band-count pattern: {key}"
        ) from exc
```

---

## 9. Deriving Gold Ranks from Retrieved Titles (secondary path)

The primary path consumes `details.jsonl` `gold_ranks` directly (Section 5.1)
and needs none of this. This section defines the secondary raw-title path
(Section 5.2), which exists only so tests can synthesize inputs. It must
reproduce `evaluator.gold_ranks` exactly.

Reference implementation:

```python
from typing import Iterable

STORED_DEPTH = 50


def first_title_ranks(
    retrieved_titles: Iterable[str],
) -> dict[str, int]:
    first_ranks: dict[str, int] = {}
    for rank, title in enumerate(retrieved_titles, start=1):
        if title not in first_ranks:      # exact string equality; first wins
            first_ranks[title] = rank
    return first_ranks


def get_gold_ranks(
    gold_titles: Iterable[str],
    retrieved_titles: Iterable[str],
) -> list[int | None]:
    unique_gold_titles = list(dict.fromkeys(gold_titles))

    if not unique_gold_titles:
        raise ValueError("Gold title set must not be empty.")
    if len(unique_gold_titles) != 2:
        raise ValueError(
            f"Pooled v1 expects exactly 2 unique gold titles, "
            f"got {len(unique_gold_titles)}."
        )

    retrieved = list(retrieved_titles)
    if len(retrieved) != STORED_DEPTH:
        raise ValueError(
            f"Pooled v1 observation horizon must be exactly {STORED_DEPTH} "
            f"retrieved titles, got {len(retrieved)}."
        )

    rank_lookup = first_title_ranks(retrieved)
    return [rank_lookup.get(gold_title) for gold_title in unique_gold_titles]
```

Important:

```text
Duplicate retrieved titles occupy ranking positions but only the first
occurrence counts as the gold title's rank.
```

This reproduces the project's frozen RR/MRR and gold-rank behavior
(`src/evaluator.py:39-58`). It does not reinterpret title matching.

---

## 10. Frozen Output Contract

The classifier produces **one new, standalone, pooled-only diagnostic CSV**.
It does not modify any existing artifact.

### 10.1 Artifact, key, and cardinality

- **Path:** `results/runs/<run_id>/gold_rank_patterns.csv`
  (derived purely from that run's `details.jsonl`; it lives beside
  `details.jsonl`/`config.json`/`metrics.json`/`failures_review.html` and must
  never overwrite any of them).
- **Scope:** pooled runs only (`config.corpus_setting == "pooled"` and
  `config.top_k_max == 50`). Refuse to generate for any other setting/depth.
- **Key:** `(example_id, retriever)` — one row per retriever unit. `rank_pattern`
  is k-independent, so `k` is **not** part of the key.
- **Cardinality:** exactly one row per `(example_id, retriever)` present in the
  run's `details.jsonl`. For the formal pooled run `2026-07-17_a`: 500 examples
  × 2 retrievers = **1000 rows**.

### 10.2 Columns (fixed order), types, vocabulary, nulls

```text
run_id, example_id, retriever, question_type, gold_count,
n_top5, n_rank6_10, n_rank11_50, n_not_in_top50,
rank_pattern, rank_pattern_schema, rank_pattern_scope, stored_depth
```

| # | Column | Type | Values / format |
|---|---|---|---|
| 1 | `run_id` | str | source run id; equals `config.run_id` |
| 2 | `example_id` | str | HotpotQA `_id`; copied from `details.jsonl` |
| 3 | `retriever` | str | `bm25` \| `dense` |
| 4 | `question_type` | str | `bridge` \| `comparison`; copied from `details.jsonl` |
| 5 | `gold_count` | int | always `2` in v1 |
| 6 | `n_top5` | int | `0`–`2` |
| 7 | `n_rank6_10` | int | `0`–`2` |
| 8 | `n_rank11_50` | int | `0`–`2` |
| 9 | `n_not_in_top50` | int | `0`–`2` |
| 10 | `rank_pattern` | str | exactly one of the 10 labels in Section 7.2 |
| 11 | `rank_pattern_schema` | str | constant `gold_rank_partition_v1` |
| 12 | `rank_pattern_scope` | str | constant `pooled_top50` |
| 13 | `stored_depth` | int | constant `50` |

- **No nulls / no empty cells.** Every field is always populated. A
  not-retrieved gold contributes to `n_not_in_top50`; it never becomes an empty
  cell. Absence is encoded as band membership, never as null.
- `n_top5 + n_rank6_10 + n_rank11_50 + n_not_in_top50 == gold_count == 2`.
- **No metric columns.** This artifact contains no recall/coverage/MRR values.
  Metrics remain owned by `src/evaluator.py` and stored only in
  `results/*_results.csv` and `details.jsonl`. They are joinable to this file by
  `(example_id, retriever)` when needed. This spec introduces no metric name.

### 10.3 Provenance and deterministic order

- **Provenance:** the `run_id` column plus the three constant schema columns
  (`rank_pattern_schema`, `rank_pattern_scope`, `stored_depth`). Run-level
  metadata (`git_commit`, `split`, `corpus_setting`, `top_k_max`, `timestamp`)
  is **not** duplicated per row; it is obtained from
  `results/runs/<run_id>/config.json`, matching the project convention that run
  metadata lives in sidecar config, not in every result row
  (`docs/specs/2026-07-15-results-csv-schema.md`).
- **Deterministic row order:** rows are sorted by `(example_id, retriever)`
  ascending, both as exact strings. Identical input produces byte-identical
  output. Standard CSV quoting applies; UTF-8 without BOM.

### 10.4 Coexistence with the coverage table, role pattern, and human labels

`rank_pattern` is **additive**. It does not replace and must not be merged into:

- the planned machine coverage table keyed by `(example_id, retriever, k)` with
  `coverage_pattern ∈ {full_coverage, one_gold_only, zero_gold}` and, for
  resolved bridges only, `role_pattern ∈ {first_hop_only, second_hop_only}`
  (`hop_role_review_design.md` Section 9 / 14.4);
- `hop_roles.csv` (human, key `example_id`);
- `annotations.csv` (human causal labels, key `(run_id, example_id, retriever)`).

Key differences to preserve:

- `rank_pattern` is **k-independent** (fixed 4 bands); `coverage_pattern` is
  **per-k**.
- `rank_pattern` needs only gold ranks; `role_pattern` additionally needs a
  resolved human hop-role assignment.
- Neither `rank_pattern` nor `coverage_pattern` is a causal label. Do not
  overwrite a structural rank pattern with a human failure cause, and do not
  store a failure cause in this file.

Example of keeping the structural and human views side by side (conceptual, not
this file's schema):

```json
{
  "rank_pattern": "one_top5_one_not_in_top50",
  "human_failure_label": "missing bridge entity",
  "human_notes": "..."
}
```

---

## 11. Metrics Are Out of Scope (do not compute or emit)

The rank-pattern classifier **computes no metric**. It emits no
recall/coverage/MRR column (Section 10.2). Metric definitions and computation
remain a hand-written core component in `src/evaluator.py` per the project
AI-use boundary; the canonical stored names are exactly:

```text
any_evidence_recall@k
full_evidence_recall@k
partial_evidence_recall@k
reciprocal_rank_at_10
reciprocal_rank_at_50
```

(`src/results_schema.py`, `docs/specs/2026-07-15-results-csv-schema.md`). Do not
introduce alternative names such as `gold_coverage_at_*`, `full_evidence_at_*`,
`evidence_recall_at_k`, or `any_evidence_at_k` — they duplicate existing
semantics under non-canonical names.

**Incomplete Evidence Indicator / Rate is explicitly out of scope.** Its
implementation is a separate owner go/no-go (`hop_role_review_design.md`; the
personal plan reserves it), so it must not appear in this artifact or its
implementation.

### 11.1 Optional test oracle (not an output)

Tests **may** cross-check that a pattern is consistent with the evaluator's
precomputed metrics, using the exact canonical names above and values read from
`details.jsonl` (never recomputed inside diagnostic plumbing). For a two-gold
unit this is a pure consequence of the band counts, e.g.:

```text
both golds' ranks <= 5      <=>  full_evidence_recall@5  is True
exactly one gold rank <= 5  <=>  partial_evidence_recall@5 == 0.5
neither gold rank <= 5      <=>  any_evidence_recall@5   is False
```

This is an independent oracle for testing only; it is not a set of new output
fields, and it recomputes nothing.

---

## 12. Relationship to Failure-Review Cards

### 12.1 The rank pattern is defined for every two-gold unit

`rank_pattern` is computed for **all** `(example_id, retriever)` units in the
pooled run, independent of any failure filter and for both bridge and comparison
questions.

### 12.2 The accepted any-based failure page is unchanged

The accepted `scripts/build_failure_report.py` and its `failures_review.html`
output are **any-based by design and are not modified by this spec**. They
conform to their original design and are not an implementation defect
(`hop_role_review_design.md` Section 14.7). This spec adds no assertion to that
generator and changes none of its behavior.

### 12.3 A Full-recall page is a separate, owner-gated revision (out of scope)

A Full Evidence Recall failure view is a separate future revision. Its delivery
mechanism (e.g. a `--criterion {any,full}` flag, a distinctly named
`failures_review_full.html`, and a byte-stability test proving the any-path
output is unchanged) is an **owner decision** (`hop_role_review_design.md`
Section 14.7, marked `[OWNER]`) and is **out of scope for this task** unless and
until that mechanism is separately approved.

For reference only (not implemented here): among units that fail Full Evidence
Recall@5, the pattern `both_in_top5` cannot occur, because `both_in_top5` is
exactly `full_evidence_recall@5 == True`. If a Full@5 view is later built under
an approved mechanism, that identity may serve as a check — but this spec neither
builds nor modifies any report generator.

---

## 13. Human-Readable Display Labels

Canonical machine labels remain stable and snake_case. A UI may display
friendlier text:

| Canonical label | Recommended UI text |
|---|---|
| `both_in_top5` | Both golds in top 5 |
| `one_top5_one_6_10` | One gold in top 5; one at ranks 6–10 |
| `one_top5_one_11_50` | One gold in top 5; one at ranks 11–50 |
| `one_top5_one_not_in_top50` | One gold in top 5; one absent from top 50 |
| `both_in_6_10` | Both golds at ranks 6–10 |
| `one_6_10_one_11_50` | One gold at ranks 6–10; one at ranks 11–50 |
| `one_6_10_one_not_in_top50` | One gold at ranks 6–10; one absent from top 50 |
| `both_in_11_50` | Both golds at ranks 11–50 |
| `one_11_50_one_not_in_top50` | One gold at ranks 11–50; one absent from top 50 |
| `both_not_in_top50` | Both golds absent from top 50 |

Avoid display strings such as:

```text
one gold only @5
one gold only @10
```

Those phrases are ambiguous because they do not specify the location of the
other gold title.

---

## 14. Edge Cases

### 14.1 Duplicate gold supporting facts under one title

Input:

```python
supporting_facts = [
    ["A", 0],
    ["A", 2],
    ["B", 1],
]
```

Unique gold titles:

```python
["A", "B"]
```

The classifier must treat this as a two-gold case. (In the primary path this is
already handled upstream: `details.jsonl` stores deduplicated `gold_titles`.)

### 14.2 Duplicate retrieved title

Input ranks:

```text
1. A
2. A
3. X
4. B
```

Gold ranks:

```text
A = 1
B = 4
```

Pattern:

```text
both_in_top5
```

### 14.3 One unique gold title

Pooled v1 **fails loudly** on a gold count other than 2 (Section 5.3); it must
not force such an example into the two-gold partition. A one-gold partition is
**not part of v1** and, if ever needed, is a separate versioned schema. (A
minimal future shape would be `gold_in_top5 / gold_in_6_10 / gold_in_11_50 /
gold_not_in_top50`, but it is non-normative here.)

### 14.4 More than two unique gold titles

Pooled v1 **fails loudly** (Section 5.3). Do not invent two-gold labels and do
not silently apply the generalized count-vector representation (Section 18) as a
v1 output.

### 14.5 Per-question setting with only top 10 stored

Out of scope for v1 (Section 3.1). Do not reuse `not_in_top50` for a top-10
horizon. Such a setting requires a separate schema version with its own absence
label (e.g. `not_in_top10`) and its own bands. Do not combine pooled top-50 and
per-question top-10 patterns into one unversioned column.

### 14.6 Observation horizon must be exactly 50

Pooled v1 requires exactly 50 stored results per retriever unit (Section 3.1,
Section 5.3). A unit whose stored ranked-title count is not 50 is a contract
violation and must **fail loudly**, not silently receive `not_in_top50`. This
removes the ambiguity between "observed only a short list" and "observed the full
50 with this gold absent": `not_in_top50` provably means the latter. (If a
future setting legitimately stores a different depth, add an explicit
`observed_depth` and version the absence label by that depth.)

---

## 15. Versioning

Frozen identifiers for pooled v1:

```text
rank_pattern_schema   = "gold_rank_partition_v1"
rank_pattern_scope    = "pooled_top50"
band_cutoff_primary   = 5
band_cutoff_secondary = 10
stored_depth          = 50
```

Persist these in:

- the frozen CSV columns (Section 10.2), which already carry
  `rank_pattern_schema`, `rank_pattern_scope`, and `stored_depth`;
- test fixtures and their expected outputs;
- this documentation.

Run-level provenance (`git_commit`, `split`, etc.) is read from the source run's
`config.json`, not duplicated per row (Section 10.3).

### 15.1 Data-schema version vs report-analysis configuration

The **data-schema version** changes only when the partition's data contract
changes — the band boundaries or the title-matching semantics. It does **not**
change merely because a downstream report chooses a different analysis cutoff
while the four bands stay identical. Keep the schema version (a data contract)
separate from a report's analysis-cutoff choice (a configuration).

Examples requiring a **new schema version**:

- changing a band cutoff from 5 to 10;
- changing the stored depth from 50 (e.g. to 100), or supporting per-question
  top-10;
- adding a 51–100 band;
- merging the 6–10 and 11–50 bands;
- changing title-matching from the current exact-string equality.

Examples **not** requiring a new schema version:

- a report or slide analyzing the same four bands at a different cutoff;
- resolving the still-provisional pooled *taxonomy* primary cutoff (that choice
  is independent of this partition — Section 3.2).

---

## 16. Required Unit Tests

### 16.1 Boundary tests for `rank_to_band`

```python
@pytest.mark.parametrize(
    ("rank", "expected"),
    [
        (1, "top5"),
        (5, "top5"),
        (6, "rank6_10"),
        (10, "rank6_10"),
        (11, "rank11_50"),
        (50, "rank11_50"),
        (None, "not_in_top50"),
    ],
)
def test_rank_to_band_boundaries(rank, expected):
    assert rank_to_band(rank) == expected
```

### 16.2 Invalid-rank tests

```python
@pytest.mark.parametrize("rank", [0, -1, 51])
def test_rank_to_band_rejects_invalid_rank(rank):
    with pytest.raises(ValueError):
        rank_to_band(rank)


@pytest.mark.parametrize("rank", [True, False])
def test_rank_to_band_rejects_bool(rank):
    with pytest.raises(TypeError):
        rank_to_band(rank)
```

### 16.3 Complete two-gold mapping tests

```python
@pytest.mark.parametrize(
    ("ranks", "expected"),
    [
        ([1, 5], "both_in_top5"),
        ([2, 8], "one_top5_one_6_10"),
        ([2, 14], "one_top5_one_11_50"),
        ([2, None], "one_top5_one_not_in_top50"),
        ([6, 10], "both_in_6_10"),
        ([8, 14], "one_6_10_one_11_50"),
        ([8, None], "one_6_10_one_not_in_top50"),
        ([11, 50], "both_in_11_50"),
        ([14, None], "one_11_50_one_not_in_top50"),
        ([None, None], "both_not_in_top50"),
    ],
)
def test_two_gold_partition(ranks, expected):
    assert classify_two_gold_rank_pattern(ranks) == expected
```

### 16.4 Order-invariance tests

```python
@pytest.mark.parametrize(
    "ranks",
    [
        [2, 8],
        [2, 14],
        [2, None],
        [8, 14],
        [8, None],
        [14, None],
    ],
)
def test_two_gold_pattern_is_order_invariant(ranks):
    assert classify_two_gold_rank_pattern(ranks) == \
           classify_two_gold_rank_pattern(list(reversed(ranks)))
```

### 16.5 Exhaustiveness test

Generate all unordered pairs of the four representative band values:

```python
representatives = {
    "top5": 1,
    "rank6_10": 6,
    "rank11_50": 11,
    "not_in_top50": None,
}
```

Confirm that:

```text
number of generated unordered pairs = 10
number of distinct returned labels = 10
returned label set equals the canonical 10-label set
```

### 16.6 Gold-count guard

```python
@pytest.mark.parametrize("ranks", [[1], [1, 2, 3], []])
def test_v1_rejects_non_two_gold_counts(ranks):
    with pytest.raises(ValueError):
        classify_two_gold_rank_pattern(ranks)
```

### 16.7 Uniqueness / horizon (secondary path)

- Confirm the secondary path rejects an empty gold set, a gold count other than
  2, and a `retrieved_titles` length other than 50.
- Confirm duplicate retrieved titles use the first rank only.
- Confirm repeated supporting facts under one title collapse to a single gold
  title (`gold_count == 2`), not three.

### 16.8 Metric-consistency oracle (test only)

For every pattern, cross-check consistency against the evaluator's canonical
metric names read from a synthetic `details.jsonl`-shaped record — as an oracle,
not an emitted field (Section 11.1):

```text
any_evidence_recall@{5,10}
full_evidence_recall@{5,10}
partial_evidence_recall@{5,10}
```

### 16.9 Output-contract tests

- Given a small synthetic pooled run directory, the generated
  `gold_rank_patterns.csv` has exactly the Section 10.2 columns in order, one
  row per `(example_id, retriever)`, rows sorted by `(example_id, retriever)`,
  no empty cells, and constant `rank_pattern_schema` / `rank_pattern_scope` /
  `stored_depth`.
- Identical input yields byte-identical output.
- Generation refuses a non-pooled run or a `top_k_max != 50` run.

---

## 17. Acceptance Criteria

The implementation is complete only when all of the following are true:

- [ ] Empty gold sets fail validation.
- [ ] Gold titles are deduplicated before classification.
- [ ] A gold count other than 2 fails loudly (v1 classifies exactly two golds).
- [ ] `bool` ranks (`True`/`False`) are rejected with `TypeError` before the
      `int` check.
- [ ] Duplicate retrieved titles use the first occurrence as rank (secondary
      path), reproducing `evaluator.gold_ranks`.
- [ ] The secondary path requires exactly 50 retrieved titles; a different
      length fails loudly.
- [ ] Rank bands match the exact boundary rules (Section 3.2 / Section 6).
- [ ] Every valid two-gold input maps to exactly one of 10 labels.
- [ ] All 10 labels are reachable.
- [ ] Label assignment is invariant to gold-title ordering.
- [ ] `not_in_top50` is documented and used only as "absent from the stored
      top-50," never "absent from the corpus."
- [ ] The classifier emits **no** metric column and introduces no new metric
      name; Incomplete Evidence Indicator/Rate is not implemented.
- [ ] Automatic rank patterns are stored separately from human causal labels and
      do not replace `coverage_pattern` or `role_pattern`.
- [ ] The frozen output CSV (`results/runs/<run_id>/gold_rank_patterns.csv`)
      matches Section 10: path, columns/order, `(example_id, retriever)` key,
      1000 rows for `2026-07-17_a`, no nulls, deterministic byte-identical row
      order, constant schema/scope/depth columns.
- [ ] Generation refuses any non-pooled or non-`top_k_max==50` run.
- [ ] `src/evaluator.py`, `src/results_schema.py` `RESULT_COLUMNS`, accepted
      result CSVs, and the accepted any-based `failures_review.html` /
      `scripts/build_failure_report.py` are unchanged.
- [ ] The classifier reuses the evaluator's exact-string, first-occurrence,
      `None`-when-unobserved gold-rank semantics (preferably by consuming
      precomputed `details.jsonl` `gold_ranks`).
- [ ] Unit tests cover every partition class and every guard above.

---

## 18. Generalization Beyond Two Gold Titles (non-normative)

This section is **non-normative** and is **not** part of pooled v1. Its output
vocabulary and tests are not frozen; do not emit it from the v1 artifact. It is
recorded only to show the intended future direction if a dataset ever contains
gold counts other than 2.

For arbitrary `n >= 1` unique gold titles, the robust representation is the count
vector:

```python
(
    n_top5,
    n_rank6_10,
    n_rank11_50,
    n_not_in_top50,
)
```

subject to:

```text
n_top5
+ n_rank6_10
+ n_rank11_50
+ n_not_in_top50
= total unique gold titles
```

Example with three gold titles:

```json
{
  "gold_count": 3,
  "n_top5": 1,
  "n_rank6_10": 1,
  "n_rank11_50": 0,
  "n_not_in_top50": 1,
  "rank_pattern_key": "1|1|0|1"
}
```

Recommended generalized machine label (future):

```text
gold_rank_counts_1_1_0_1
```

For the common two-gold case, retain the named 10-class partition. If this
generalization is ever adopted, it is a new schema version with its own frozen
output and tests.

---

## 19. Non-Goals

This classifier must not automatically decide:

- which gold title is first hop;
- which gold title is second hop;
- which title represents the bridge entity;
- whether the failure is lexical mismatch;
- whether dense retrieval semantically drifted;
- whether a distractor entity caused the miss;
- whether the retrieved evidence is sufficient for answer generation.

Those require textual inspection, additional heuristics, or human annotation.

---

## 20. Recommended Integration Pattern

```text
pooled run details.jsonl (evaluator gold_ranks: exact-string, first-occurrence)
      |
      v
gold-rank extraction  (Section 5.1 primary path; Section 9 for tests only)
      |
      v
rank-pattern partition  --->  results/runs/<run_id>/gold_rank_patterns.csv
      |
      :  (downstream, OUT OF SCOPE for this spec)
      v
failure report card  /  coverage table  /  human causal annotation
```

The nodes below the dashed boundary (failure card, coverage table, human causal
annotation) are separate, owner-owned artifacts. This spec produces only the
`gold_rank_patterns.csv` node and touches nothing else.

If a downstream card ever displays this partition, useful fields would include:

```text
Question
Question type
Gold titles and ranks            (from details.jsonl)
Automatic rank pattern           (from gold_rank_patterns.csv)
Coverage / role pattern          (from the separate coverage table)
Human label / notes              (from annotations.csv)
```

but building that card is not part of this spec.

---

## 21. Summary for the Coding Agent

Implement a deterministic structural classifier over gold-title ranks for the
pooled top-50 setting only.

Bands:

```text
1–5       -> top5
6–10      -> rank6_10
11–50     -> rank11_50
missing   -> not_in_top50   (absent from the stored 50, not from the corpus)
```

For exactly two unique gold titles, classify the unordered pair into exactly one
of 10 canonical patterns. Fail loudly on any other gold count, on `bool` ranks,
on ranks outside `[1, 50]`, and on a non-pooled / non-50 run.

Consume the evaluator's precomputed `details.jsonl` `gold_ranks` (exact-string,
first-occurrence, `None`-when-unobserved). Compute no metric, emit no metric
column, and introduce no new metric name.

Write exactly one new artifact,
`results/runs/<run_id>/gold_rank_patterns.csv`, with the frozen Section 10
schema. Change nothing else — not `evaluator.py`, not `RESULT_COLUMNS`, not the
accepted result CSVs, not the accepted any-based failure page.

Store:

```text
automatic rank pattern
```

separately from:

```text
human failure label     (annotations.csv)
coverage / role pattern (separate coverage table)
```

The automatic partition answers:

> Where did the gold evidence appear in the ranking?

The human taxonomy answers:

> Why did the retriever fail?
