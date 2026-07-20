# Retrieval Eval Schema v2

**Author:** Xin · **Date:** 2026-07-20 · **Status:** Proposed contract — pending BM25-collaborator
alignment before the Stage 2 implementation freeze
**Applies to:** every evaluation bundle under `evals/<eval_id>/`
**Layer:** automatic evaluation only. Aggregates are computed from an accepted per-example artifact, never
recomputed directly from raw rankings.

This document is the Stage 1 contract for the evaluation side of the metrics/schema v2 refactor. It fixes the
physical file layout, column order, types, nullability, keys, and serialization of per-example and aggregate
eval outputs and their manifest.

Metric meaning, edge cases, and the canonical v2 metric identifiers are frozen in
`docs/specs/2026-07-17-retrieval-metrics-v2.md` (version `retrieval_metrics_v2`, Xin-verified 2026-07-17).
This eval-schema spec references those identifiers verbatim and never redefines a metric. The raw input
contract is `docs/specs/2026-07-20-raw-retrieval-rankings-schema.md`.

## Version identifiers

Every eval bundle records three independent versions (from the metric spec §6):

| Version key | Value |
|---|---|
| `metric_definition_version` | `retrieval_metrics_v2` |
| `evaluation_protocol_version` | `hotpotqa_retrieval_protocol_v2` |
| `eval_schema_version` | `retrieval_eval_schema_v2` |

A formula/edge-case change bumps the metric-definition version; a setting/cutoff/required-depth change bumps
the evaluation-protocol version; a file-shape/serialization change bumps the eval-schema version. An evaluator
rejects any unsupported version rather than silently substituting another contract.

## Directory layout

```text
evals/
└── <eval_id>/
    ├── manifest.json
    ├── per_example.csv
    ├── aggregate.csv
    └── aggregate_by_question_type.csv    # generated only when requested
```

`aggregate_by_<dimension>.csv` is the general subgroup pattern; `question_type` is the primary dimension and
`level` uses `aggregate_by_level.csv` with the identical tidy-long shape. The default `aggregate.csv` groups
only by `method + setting`.

## `eval_id` grammar and collision policy

One eval bundle corresponds to exactly one raw retrieval run, so the ID embeds that run directly:

```text
eval_<retrieval_run_id>_metrics_v2_e<NN>
```

- `e<NN>` is a two-digit sequence, so one raw retrieval run can produce multiple eval versions (e.g. a metric
  re-run) without collision. The refuse-overwrite policy matches `retrieval_run_id`.
- Cross-method or cross-setting comparison tables are not eval bundles. They live under `analysis_outputs/` and
  read from multiple single-run eval bundles; a bundle never mixes more than one raw run.

Example:

```text
eval_dense_pooled_n500_d50_20260720_r01_metrics_v2_e01
```

## Serialization and null policy

- Indicators serialize as integer `0` or `1`.
- Evidence Recall and Reciprocal Rank serialize as finite floats in `[0, 1]`.
- The single canonical serialized null is an **empty CSV cell** (zero-length), loaded as `NaN`. Literal
  strings `"NaN"`, `"None"`, and `"null"` are never metric values and are rejected.
- The only permitted per-example nulls are the three deliberately uncomputed `per_question` @10 hit/recall
  fields (metric spec §3). Every pooled metric and every reciprocal-rank metric is required. Any other missing
  value is a schema/evaluation error.

## `per_example.csv`

One row per evaluated `(eval_id, retrieval_run_id, example_id)`. Fixed column order — metadata first, then the
eleven canonical per-example metric columns from the metric spec §5.1.

Metadata columns:

| # | Column | Type | Nullable | Notes |
|---|---|---|---|---|
| 1 | `eval_id` | str | no | matches the directory and manifest |
| 2 | `eval_schema_version` | str | no | `retrieval_eval_schema_v2` |
| 3 | `metric_definition_version` | str | no | `retrieval_metrics_v2` |
| 4 | `evaluation_protocol_version` | str | no | `hotpotqa_retrieval_protocol_v2` |
| 5 | `retrieval_run_id` | str | no | source raw run |
| 6 | `method` | str | no | `bm25` \| `dense` \| `rerank` |
| 7 | `setting` | str | no | `pooled` \| `per_question` |
| 8 | `example_id` | str | no | HotpotQA `_id` |
| 9 | `question_type` | str | no | `bridge` \| `comparison` |
| 10 | `level` | str | no | `easy` \| `medium` \| `hard` |
| 11 | `gold_title_count` | int | no | `|G_q|`, always ≥ 1 (empty gold is rejected upstream) |
| 12 | `retrieved_depth` | int | no | saved rank depth actually available for this example |

Metric columns (exact identifiers, in this order):

```text
any_evidence_hit_indicator_at_2      # int 0/1
any_evidence_hit_indicator_at_5      # int 0/1
any_evidence_hit_indicator_at_10     # int 0/1; empty for per_question
full_evidence_hit_indicator_at_2     # int 0/1
full_evidence_hit_indicator_at_5     # int 0/1
full_evidence_hit_indicator_at_10    # int 0/1; empty for per_question
evidence_recall_at_2                 # float [0,1]
evidence_recall_at_5                 # float [0,1]
evidence_recall_at_10                # float [0,1]; empty for per_question
reciprocal_rank_at_10                # float [0,1]; required
reciprocal_rank_at_50                # float [0,1]; required
```

- Key uniqueness: `(eval_id, retrieval_run_id, example_id)`.
- This eleven-name list is the complete active per-example metric vocabulary. Legacy-only aliases
  (`any_evidence_recall@k`, `full_evidence_recall@k`, `partial_evidence_recall@k`) are not accepted columns;
  they exist only inside the versioned read-only migration adapter.
- The three `_at_10` hit/recall fields are the only columns that may be empty, and only when
  `setting = per_question`. `reciprocal_rank_at_10` and `reciprocal_rank_at_50` are always required.
- Validators check ranges/types/nullability only; they never recompute or redefine a metric.

## `aggregate.csv`

Tidy-long format: one row per `(group, metric_name)`. Default group is `method + setting`.

| # | Column | Type | Nullable | Notes |
|---|---|---|---|---|
| 1 | `eval_id` | str | no | matches the manifest |
| 2 | `eval_schema_version` | str | no | `retrieval_eval_schema_v2` |
| 3 | `metric_definition_version` | str | no | `retrieval_metrics_v2` |
| 4 | `evaluation_protocol_version` | str | no | `hotpotqa_retrieval_protocol_v2` |
| 5 | `method` | str | no | `bm25` \| `dense` \| `rerank` |
| 6 | `setting` | str | no | `pooled` \| `per_question` |
| 7 | `n_questions` | int | no | questions in the group |
| 8 | `metric_name` | str | no | one canonical aggregate identifier (below) |
| 9 | `value` | float | yes | macro average; empty only when `n_valid = 0` |
| 10 | `n_valid` | int | no | valid-example count for this specific metric |

Canonical aggregate `metric_name` vocabulary (metric spec §5.2):

```text
any_evidence_hit_rate_at_2      any_evidence_hit_rate_at_5      any_evidence_hit_rate_at_10
full_evidence_hit_rate_at_2     full_evidence_hit_rate_at_5     full_evidence_hit_rate_at_10
macro_evidence_recall_at_2      macro_evidence_recall_at_5      macro_evidence_recall_at_10
mean_reciprocal_rank_at_10      mean_reciprocal_rank_at_50
```

Rules:

- Key uniqueness: `(eval_id, method, setting, metric_name)`.
- Each metric carries its own `n_valid`; `n_questions` alone is not an acceptable denominator description.
- Aggregation is macro averaging: skip `NaN`, divide by `n_valid`, and emit an empty `value` only when
  `n_valid = 0`. No micro-averaged evidence-recall metric exists.
- For a `per_question` group, the three `*_at_10` hit/recall aggregates have `n_valid = 0` and empty `value`.
- Report labels (`Any Evidence Hit Rate@k`, `Full Evidence Hit Rate@k`, `Macro Evidence Recall@k`, `MRR@h`)
  are presentation-only and come from the single central mapping in the metric spec §5.3. They are never
  storage identifiers and never appear in `metric_name`.
- `Incomplete Evidence Rate@k` is not a formal field; it is derived only in team-approved failure analysis.

## `aggregate_by_<dimension>.csv`

Identical tidy-long shape as `aggregate.csv` plus one grouping column (`question_type` or `level`) inserted
after `setting`. Key uniqueness extends to `(eval_id, method, setting, <dimension>, metric_name)`. Metric
definitions and identifiers are unchanged across dimensions.

## `manifest.json`

`manifest.json` is a single JSON object with fixed field types.

| Field | JSON type | Required | Nullable | Constraints |
|---|---|---|---|---|
| `eval_schema_version` | string | yes | no | `retrieval_eval_schema_v2` |
| `metric_definition_version` | string | yes | no | `retrieval_metrics_v2` |
| `evaluation_protocol_version` | string | yes | no | `hotpotqa_retrieval_protocol_v2` |
| `eval_id` | string | yes | no | matches the directory and every eval row |
| `created_at` | string | yes | no | ISO-8601 UTC |
| `source_retrieval_run_id` | string | yes | no | the single raw run consumed |
| `source_rankings_sha256` | string | yes | no | that raw run's `rankings.csv` checksum |
| `dataset_identifier` | string | yes | no | dataset name/version |
| `dataset_fingerprint` | string | yes | no | fingerprint of the gold dataset snapshot |
| `gold_mapping_version_or_fingerprint` | string | yes | no | gold-title mapping version or fingerprint |
| `k_policy` | object | yes | no | cutoffs/horizons per setting (hit/recall @2,@5,@10; RR@10,@50) |
| `aggregation_groups` | array of strings | yes | no | groups materialized, e.g. `["method+setting", "question_type"]` |
| `evaluator_git_commit` | string | yes | no | code commit that produced the eval |
| `command` | string | yes | no | exact command line |
| `artifact_sha256` | object (string → string) | yes | no | file name → SHA-256; keys include only files actually generated |

`artifact_sha256` example:

```json
"artifact_sha256": {
  "per_example.csv": "...",
  "aggregate.csv": "...",
  "aggregate_by_question_type.csv": "..."
}
```

Serialization and checksum rules:

```text
CSV:              UTF-8, comma-delimited, header row required, LF (\n) newlines, standard CSV quoting
per_example order: source raw-run example order
aggregate order:   group-key order, then the canonical metric order listed above
manifest.json:     UTF-8 object, keys sorted, one trailing newline
artifact_sha256:   SHA-256 over the exact serialized bytes of each named file
```

Provenance rules:

- The eval references the exact source raw `source_rankings_sha256`, so an aggregate is fully traceable to one
  raw retrieval run, a dataset/gold snapshot, and the three frozen versions.
- Aggregation reads only the accepted per-example artifact (`artifact_sha256["per_example.csv"]`), never the raw
  rankings, to recompute question-level metrics.

## Layer-separation invariants

- Per-example identifiers use `indicator` / `reciprocal_rank`; aggregate identifiers use `rate` /
  `mean_reciprocal_rank`. `MRR` is a presentation label only (metric spec §5.3), never a stored identifier. No
  field named like `mrr` or `mrr_for_example` may appear at the per-example layer.
- No eval file contains raw-only columns (`rank`, `title`, `score`), and no raw file contains any eval column.
- Validators reject a legacy-only identifier appearing in any active eval column.

## Alignment status

This is a proposed contract. Per the refactor policy (HANDOFF §6, plan working-branch policy), the eval column
sets, `eval_id` grammar, tidy-long aggregate shape, subgroup file layout, and manifest fields must be confirmed
with the BM25 collaborator before the Stage 2 schema constants/validators freeze them. Until then, only offline
schema work proceeds.
