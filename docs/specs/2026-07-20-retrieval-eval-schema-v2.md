# Retrieval Eval Schema v2

**Author:** Xin · **Date:** 2026-07-20 · **Status:** Frozen for Stage 2 implementation
**Applies to:** every evaluation bundle under `evals/<eval_id>/`
**Layer:** automatic evaluation only. Aggregates are computed from an accepted per-example artifact, never
recomputed directly from raw rankings.

The remaining BM25-interface decisions were closed by owner-delegated review on 2026-07-20; separate collaborator
sign-off is not required. The decision record is
`docs/Local/Plans/2026-07-20_bm25_interface_alignment_checklist.md`.

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
    ├── aggregate_by_question_type.csv    # generated only when requested
    └── aggregate_by_level.csv            # generated only when requested
```

The only v2 subgroup dimensions are `question_type` and `level`, materialized as
`aggregate_by_question_type.csv` and `aggregate_by_level.csv`. The default `aggregate.csv` groups only by
`method + setting`. Adding another subgroup dimension changes the physical contract and requires a new
eval-schema version.

## `eval_id` grammar and collision policy

One eval bundle corresponds to exactly one raw retrieval run, so the ID embeds that run directly:

```text
eval_<retrieval_run_id>_metrics_v2_e<NN>
```

- `e<NN>` is a two-digit ASCII sequence (`[0-9][0-9]`; no Arabic-Indic, fullwidth, or other Unicode decimal
  digits) starting at `e01`, so one raw retrieval run can produce multiple eval versions (e.g. a metric re-run)
  without collision. `e00` is invalid. This uses the same canonical sequence policy as the `retrieval_run_id`
  rerun sequence (`r<NN>`), and the refuse-overwrite collision policy likewise matches `retrieval_run_id`.
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
| 12 | `retrieved_depth` | int | no | number of source raw ranking rows for this example; always ≥ 1 |

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
definitions and identifiers are unchanged across dimensions. No other `aggregate_by_*.csv` filename is valid
under `retrieval_eval_schema_v2`.

## `manifest.json`

`manifest.json` is a single JSON object with fixed field types.

| Field | JSON type | Required | Nullable | Constraints |
|---|---|---|---|---|
| `eval_schema_version` | string | yes | no | `retrieval_eval_schema_v2` |
| `metric_definition_version` | string | yes | no | `retrieval_metrics_v2` |
| `evaluation_protocol_version` | string | yes | no | `hotpotqa_retrieval_protocol_v2` |
| `eval_id` | string | yes | no | matches the directory and every eval row |
| `created_at` | string | yes | no | UTC `YYYY-MM-DDTHH:MM:SSZ`; no fractional seconds |
| `source_retrieval_run_id` | string | yes | no | the single raw run consumed |
| `source_rankings_sha256` | string | yes | no | 64 lowercase hexadecimal characters; that raw run's `rankings.csv` checksum |
| `dataset_identifier` | string | yes | no | dataset name/version |
| `dataset_fingerprint` | string | yes | no | `sha256:<64 lowercase hex>` matching the accepted raw run's loaded dataset snapshot |
| `gold_mapping_version_or_fingerprint` | string | yes | no | gold-title mapping version or fingerprint |
| `k_policy` | object | yes | no | exact closed shape and values defined below |
| `aggregation_groups` | array of strings | yes | no | exact generated grouping set and order defined below |
| `evaluator_git_commit` | string | yes | no | code commit that produced the eval |
| `command` | string | yes | no | exact command line |
| `artifact_sha256` | object (string → string) | yes | no | exact generated filename set → 64-character lowercase hexadecimal SHA-256 |

All manifest fields are non-null. All unconstrained provenance strings in the table must be non-empty strings.
The manifest permits no additional top-level fields under `retrieval_eval_schema_v2`; duplicate JSON object keys
are invalid.

### `k_policy` shape

The value is exactly:

```json
{
  "insufficient_depth_policy": "reject_unless_corpus_exhausted",
  "per_question": {
    "computed_hit_recall_cutoffs": [2, 5],
    "reciprocal_rank_horizons": [10, 50],
    "uncomputed_hit_recall_cutoffs": [10]
  },
  "pooled": {
    "computed_hit_recall_cutoffs": [2, 5, 10],
    "reciprocal_rank_horizons": [10, 50],
    "uncomputed_hit_recall_cutoffs": []
  }
}
```

No key, value, or array order may differ under `hotpotqa_retrieval_protocol_v2`.

### `aggregation_groups` and artifact-key shape

`aggregation_groups` always starts with `"method+setting"`, followed by zero or more subgroup names in this
fixed order: `"question_type"`, then `"level"`. Values are unique; no other value is valid. Thus the complete
set of valid arrays is:

```text
["method+setting"]
["method+setting", "question_type"]
["method+setting", "level"]
["method+setting", "question_type", "level"]
```

`artifact_sha256` contains `per_example.csv` and `aggregate.csv` exactly once. It contains
`aggregate_by_question_type.csv` if and only if `question_type` is listed, and `aggregate_by_level.csv` if and
only if `level` is listed. No other key is allowed. `manifest.json` is deliberately excluded because including
its own checksum would be self-referential.

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
CSV bytes:          UTF-8 without BOM; comma delimiter; header required; LF (\n) record terminator
CSV dialect:        quotechar='"', doublequote=true, escapechar absent, QUOTE_MINIMAL
integer text:       base-10 ASCII, no leading '+' and no leading zero except the value 0
float text:         Python format(value, '.17g'), lowercase exponent, with negative zero normalized to 0
null text:          zero bytes between delimiters (an empty cell)
per_example order:  the source rankings.csv example order, then one row per example
default aggregate:  the single method + setting group, then canonical metric order listed above
question_type order: bridge, comparison; within each value, canonical metric order
level order:         easy, medium, hard; within each value, canonical metric order
manifest bytes:     json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True,
                    separators=(',', ':')) encoded as UTF-8 without BOM, followed by one LF
artifact_sha256:    SHA-256 over the exact serialized bytes of each named file
```

CSV string values are passed through unchanged; the fixed dialect quotes fields containing a comma, quote, CR, or
LF and doubles an embedded quote. The per-example source order is mechanically available from the raw contract,
whose rows are ordered by ascending `example_id` and then rank. These rules apply before checksum calculation.

Provenance rules:

- The eval references the exact source raw `source_rankings_sha256`, so an aggregate is fully traceable to one
  raw retrieval run, a dataset/gold snapshot, and the three frozen versions.
- Aggregation reads only the accepted per-example artifact (`artifact_sha256["per_example.csv"]`), never the raw
  rankings, to recompute question-level metrics.
- The eval `dataset_identifier` and `dataset_fingerprint` must equal the source raw manifest values. Cross-method
  comparisons additionally require equal `setting`, `dataset_identifier`, `dataset_fingerprint`,
  `example_ids_fingerprint`, and `corpus_fingerprint` in the referenced raw manifests. Corpus fingerprints match
  across methods within a setting; pooled and per-question fingerprints are not compared to each other.

## Layer-separation invariants

- Per-example identifiers use `indicator` / `reciprocal_rank`; aggregate identifiers use `rate` /
  `mean_reciprocal_rank`. `MRR` is a presentation label only (metric spec §5.3), never a stored identifier. No
  field named like `mrr` or `mrr_for_example` may appear at the per-example layer.
- Dense, BM25, and Rerank use one evaluator implementation and one eval contract. The metric calculation has no
  method-specific branch: `method` and raw `score_type` are provenance, while ranked titles plus the frozen gold
  mapping determine metric values.
- No eval file contains raw-only columns (`rank`, `title`, `score`), and no raw file contains any eval column.
- Validators reject a legacy-only identifier appearing in any active eval column.

## Freeze status

The eval column sets, `eval_id` grammar, tidy-long aggregate shape, subgroup file layout, manifest fields, shared
evaluator rule, and comparison provenance gates are frozen for Stage 2 implementation. Any incompatible physical
or semantic change requires an explicit schema/protocol amendment rather than an implementation-time choice.
