# Project Specifications

This directory contains the versioned contracts and design documents for the
HotpotQA retrieval-failure-analysis pipeline. Use it to determine which file
owns a metric definition, artifact format, or review workflow before changing
an implementation.

## Specification index

| Document | What it owns | Current role |
|---|---|---|
| [Retrieval Metrics v2 Definition](2026-07-17-retrieval-metrics-v2.md) | Metric semantics, canonical identifiers, cutoff policy, aggregation rules, and golden examples | Frozen metric contract for active evaluation |
| [Raw Retrieval Rankings Schema (v1)](2026-07-20-raw-retrieval-rankings-schema.md) | `results/retrieval_runs/<retrieval_run_id>/`, `rankings.csv`, raw manifests, provenance, and validation rules | Frozen raw-output contract for Stage 2 implementation |
| [Retrieval Eval Schema v2](2026-07-20-retrieval-eval-schema-v2.md) | `evals/<eval_id>/`, per-example and aggregate files, eval manifests, serialization, and layer boundaries | Frozen full-bundle-only evaluation-output contract |
| [Retrieval Eval Schema v3](2026-07-26-retrieval-eval-schema-v3.md) | Adds an explicit `manifest_mode` (`per_example_only` \| `full`), the per-example-only bundle, and the Stage 5 → Stage 6 refuse-overwrite lifecycle; inherits every v2 metric column and serialization rule | Frozen evaluation-output contract (passed independent contract review 2026-07-26) |
| [Results CSV Schema](2026-07-15-results-csv-schema.md) | Legacy mixed result files such as `results/dense_results.csv` | Read-only migration and parity reference; not the target v2 schema |
| [Failure Review Pipeline — Design Doc](2026-07-12-failure-review-pipeline-design.md) | Human review, annotations, report UI, and failure-analysis handoff | Design reference; data layer implemented and report UI pending |

## Active contract model

The active pipeline separates raw retrieval from automatic evaluation:

```text
retriever / reranker
        |
        v
results/retrieval_runs/<retrieval_run_id>/
  governed by: retrieval_raw_schema_v1
        |
        v
shared evaluator
  governed by: retrieval_metrics_v2
        |
        v
evals/<eval_id>/
  governed by: retrieval_eval_schema_v2 (frozen full-bundle carrier) /
              retrieval_eval_schema_v3 (frozen; adds per-example-only + full)
        |
        +--> analysis_outputs/          cross-run tables and figures
        +--> failure_review/runs/       review and annotation artifacts
```

The three active version identifiers are independent:

- `retrieval_metrics_v2` changes when formulas, names, or edge-case semantics
  change.
- `hotpotqa_retrieval_protocol_v2` changes when settings, cutoffs, or required
  retrieval depths change.
- `retrieval_eval_schema_v2` / `retrieval_eval_schema_v3` change when evaluation
  file shapes or serialization rules change. Both are frozen, supported carriers:
  v2 is the full-bundle-only carrier, and v3 (passed independent contract review
  2026-07-26) additively introduces an explicit `manifest_mode` and a
  per-example-only bundle while inheriting every v2 metric column and
  serialization rule. A validator dispatches on the exact declared
  `eval_schema_version` and rejects any unsupported value fail-closed.

The raw bundle has its own physical schema version,
`retrieval_raw_schema_v1`.

## Which document takes precedence?

When documents overlap, use the owner of the relevant concern:

1. For metric meaning, canonical metric names, missing values, and aggregation,
   follow the Retrieval Metrics v2 definition.
2. For raw rankings, scores, run IDs, raw manifests, and retrieval provenance,
   follow the Raw Retrieval Rankings Schema.
3. For per-example or aggregate evaluation files, eval IDs, eval manifests,
   and serialization, follow the Retrieval Eval Schema v2, and the Retrieval
   Eval Schema v3 amendment for the `manifest_mode` discriminator, the
   per-example-only bundle, and the Stage 5 → Stage 6 lifecycle.
4. Use the Results CSV Schema only to read or audit legacy artifacts during
   migration. Active v2 writers must not emit its legacy-only names or reuse
   its mixed raw-and-metric layout.
5. Use the Failure Review Pipeline design for the human-review workflow. Where
   its earlier storage plan overlaps the v2 raw/eval architecture, the frozen
   v2 contracts govern the active machine-readable artifacts.

Executable code and tests must implement these contracts; they should not
silently redefine them.

## Change policy

- Treat a document marked **Frozen** as a versioned contract. Make an explicit
  amendment or introduce a new version for incompatible changes.
- Keep raw retrieval data, automatic evaluation data, analysis outputs, and
  human annotations in their designated layers.
- Do not fabricate missing raw scores or derive raw rankings from legacy
  metric columns during migration.
- Add new specifications as date-prefixed Markdown files and update the index
  above when their status or authority changes.
- Record rationale and migration impact alongside every schema, protocol, or
  metric-version change.
