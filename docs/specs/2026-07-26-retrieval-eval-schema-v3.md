# Retrieval Eval Schema v3

**Owner:** Xin · **Drafted:** agent, under owner direction, from the 2026-07-26 M1 manifest-contract design
independent review · **Date:** 2026-07-26 · **Status:** Frozen — passed independent contract review 2026-07-26
(`docs/Local/Reviews/2026-07-26_stage5_m1_eval_schema_v3_contract_corrective_independent_rereview.md`)
**Applies to:** every evaluation bundle under `evals/<eval_id>/` that declares
`eval_schema_version = retrieval_eval_schema_v3`
**Layer:** automatic evaluation only. Aggregates are computed from an accepted per-example artifact, never
recomputed directly from raw rankings.

This document is the tracked v3 amendment authorized for spec authoring by
`docs/Local/Reviews/2026-07-26_stage5_m1_manifest_contract_design_independent_review.md` (verdict: **PASS FOR SPEC
AUTHORING**). It records the exact reviewed M1 contract. It does **not** implement the validator, serializer,
evaluator core, tests, or any formal eval artifact, and it does not begin Stage 6. The amendment passed its fresh
independent contract review on 2026-07-26
(`docs/Local/Reviews/2026-07-26_stage5_m1_eval_schema_v3_contract_corrective_independent_rereview.md`); that
implementation remains gated on separately authorized Stage 5 work.

Metric meaning, edge cases, and the canonical v2 metric identifiers remain frozen in
`docs/specs/2026-07-17-retrieval-metrics-v2.md` (version `retrieval_metrics_v2`). This eval-schema spec references
those identifiers verbatim and never redefines, adds, or removes a metric, formula, edge case, or golden value. The
raw input contract remains `docs/specs/2026-07-20-raw-retrieval-rankings-schema.md`.

## Why a new eval-schema version

`retrieval_eval_schema_v2` is a full-bundle-only contract: every accepted v2 manifest has no mode field, a non-empty
`aggregation_groups`, and both `per_example.csv` and `aggregate.csv` in `artifact_sha256`. The canonical plan Phase 4
(Stage 5) must emit `per_example.csv` plus a manifest and must not write aggregate output, so no v2 manifest can
represent the Phase-4 result. Because the physical manifest/bundle contract changes, this is a new eval-schema
version, per the v2 freeze rule that "file-shape/serialization changes require a new eval-schema version."

`retrieval_eval_schema_v2` is preserved unchanged and continues to mean exactly the original full-bundle-only
contract. v3 is additive: it introduces an explicit manifest-mode discriminator, a closed per-example-only bundle,
and a full mode that retains the v2 aggregate/subgroup artifact shapes and metric columns under the v3
manifest/version rules, and it fixes the Stage 5 → Stage 6 lifecycle under refuse-overwrite.

## What v3 inherits unchanged from v2

v3 changes only the manifest-level contract, the per-example-only bundle shape, the embedded eval-schema-version
value, and the Stage 5 → Stage 6 lifecycle. Everything else is inherited byte-for-byte from
`docs/specs/2026-07-20-retrieval-eval-schema-v2.md`:

- the `per_example.csv` metadata columns, the eleven canonical per-example metric columns (metric spec §5.1), their
  order, types, nullability, and key uniqueness;
- the `aggregate.csv` and `aggregate_by_<dimension>.csv` tidy-long shapes, aggregate identifiers (metric spec §5.2),
  and key uniqueness (full mode only);
- the serialization and null policy (integer `0`/`1`; finite floats in `[0, 1]`; the single canonical serialized
  null is an empty CSV cell loaded as `NaN`; literal `"NaN"`/`"None"`/`"null"` rejected);
- the byte-level CSV and manifest serialization and checksum rules (UTF-8 without BOM; comma delimiter; header
  required; LF terminator; the fixed CSV dialect; integer/float/null text rules; canonical
  `json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':'))` manifest bytes
  followed by one LF; SHA-256 over the exact serialized bytes of each named file);
- the `k_policy` object shape and values (frozen under `hotpotqa_retrieval_protocol_v2`);
- the layer-separation invariants (`indicator`/`reciprocal_rank` at the per-example layer; `rate`/
  `mean_reciprocal_rank` at the aggregate layer; no legacy-only identifier in any active column; no raw-only column
  in an eval file and no eval column in a raw file).

The only change to the per-example and aggregate rows is that the `eval_schema_version` metadata cell now records
`retrieval_eval_schema_v3` instead of `retrieval_eval_schema_v2`. No metric column, value, type, null policy, key,
or serialization byte rule changes.

## Version identifiers and version strategy

Every v3 eval bundle records three independent versions:

| Version key | Value |
|---|---|
| `metric_definition_version` | `retrieval_metrics_v2` |
| `evaluation_protocol_version` | `hotpotqa_retrieval_protocol_v2` |
| `eval_schema_version` | `retrieval_eval_schema_v3` |

- `metric_definition_version` stays `retrieval_metrics_v2`: the metric formulas and identifiers are unchanged.
- `evaluation_protocol_version` stays `hotpotqa_retrieval_protocol_v2`: settings, cutoffs, and required depths are
  unchanged.
- `eval_schema_version` becomes `retrieval_eval_schema_v3` because the physical manifest/bundle contract changes.
- The validator must dispatch on the exact declared `eval_schema_version`. It must never accept a v3 shape while it
  is labelled `retrieval_eval_schema_v2`, and never accept a v2 shape while it is labelled `retrieval_eval_schema_v3`.
  An evaluator rejects any unsupported version rather than silently substituting another contract.

Metric-spec §6 carries a compatibility/status contract for the physical carriers of `retrieval_metrics_v2`:
`retrieval_eval_schema_v2` and `retrieval_eval_schema_v3` are both frozen, supported carriers. A conforming evaluator
dispatches on the exact declared `eval_schema_version`, accepts either supported carrier, and rejects any other value
fail-closed. That contract adds no formula, edge case, or identifier; the metric formulas and canonical identifiers
remain unchanged.

## `eval_id` grammar and collision policy

The existing eval-ID grammar is unchanged:

```text
eval_<retrieval_run_id>_metrics_v2_e<NN>
```

The literal `metrics_v2` segment identifies the metric definition, not the physical eval-schema version, so it stays
`metrics_v2` for v3 bundles. `e<NN>` is a two-digit ASCII sequence (`[0-9][0-9]`; no Arabic-Indic, fullwidth, or
other Unicode decimal digits) starting at `e01`; `e00` is invalid. The `e<NN>` sequence denotes a distinct immutable
evaluation bundle, not a pipeline stage. The refuse-overwrite collision policy matches `retrieval_run_id` and the
frozen v2 policy. Cross-method or cross-setting comparison tables are not eval bundles; they live under
`analysis_outputs/` and read from multiple single-run eval bundles.

## Manifest-mode discriminator

Every v3 manifest carries the required, non-null field:

```json
"manifest_mode": "per_example_only" | "full"
```

- The field is explicit. Mode is **not** inferred from file presence or from `aggregation_groups`.
- Missing, null, non-string, unknown, or contradictory values are rejected.
- The mode-specific `aggregation_groups` arrays and artifact/file sets below remain independent cross-checks: a
  manifest that declares one mode but carries another mode's arrays or files is rejected.

## Closed manifest fields

Both v3 modes have exactly these common fields and no others:

```text
eval_schema_version
metric_definition_version
evaluation_protocol_version
manifest_mode
eval_id
created_at
source_retrieval_run_id
source_rankings_sha256
dataset_identifier
dataset_fingerprint
gold_mapping_version_or_fingerprint
k_policy
aggregation_groups
evaluator_git_commit
command
artifact_sha256
```

`per_example_only` has exactly the common field set.

`full` has the common field set plus exactly:

```text
source_per_example_eval_id
source_per_example_sha256
```

Both source fields are required, non-null, and forbidden in `per_example_only`. `source_per_example_sha256` is the
SHA-256 of the exact Stage 5 `per_example.csv` bytes actually consumed by Stage 6.

Field constraints. Every common field keeps its v2 constraint (see
`docs/specs/2026-07-20-retrieval-eval-schema-v2.md`), with the version values and the added discriminator as below:

| Field | JSON type | Required | Nullable | Constraints |
|---|---|---|---|---|
| `eval_schema_version` | string | yes | no | `retrieval_eval_schema_v3` |
| `metric_definition_version` | string | yes | no | `retrieval_metrics_v2` |
| `evaluation_protocol_version` | string | yes | no | `hotpotqa_retrieval_protocol_v2` |
| `manifest_mode` | string | yes | no | exactly `per_example_only` or `full` |
| `eval_id` | string | yes | no | matches the directory and every eval row |
| `created_at` | string | yes | no | UTC `YYYY-MM-DDTHH:MM:SSZ`; no fractional seconds |
| `source_retrieval_run_id` | string | yes | no | the single raw run consumed |
| `source_rankings_sha256` | string | yes | no | 64 lowercase hex; that raw run's `rankings.csv` checksum |
| `dataset_identifier` | string | yes | no | dataset name/version |
| `dataset_fingerprint` | string | yes | no | `sha256:<64 lowercase hex>` matching the accepted raw run's dataset snapshot |
| `gold_mapping_version_or_fingerprint` | string | yes | no | gold-title mapping version or fingerprint |
| `k_policy` | object | yes | no | the frozen v2 shape/values, unchanged |
| `aggregation_groups` | array of strings | yes | no | exact per-mode array/order defined below |
| `evaluator_git_commit` | string | yes | no | code commit that produced the eval |
| `command` | string | yes | no | exact command line |
| `artifact_sha256` | object (string → string) | yes | no | exact per-mode filename set → 64 lowercase hex SHA-256 |
| `source_per_example_eval_id` | string | full only | no | the exact consumed Stage 5 per-example-only `eval_id`; forbidden in `per_example_only` |
| `source_per_example_sha256` | string | full only | no | 64 lowercase hex SHA-256 of the exact consumed Stage 5 `per_example.csv` bytes; forbidden in `per_example_only` |

All present fields are non-null. All unconstrained provenance strings must be non-empty. The manifest permits no
additional top-level fields; duplicate JSON object keys are invalid. `manifest.json` is excluded from its own
`artifact_sha256` map because including its own checksum would be self-referential.

## Per-mode `aggregation_groups`, artifacts, and directory shape

For `per_example_only`:

- `aggregation_groups` is exactly `[]`;
- `artifact_sha256` has exactly one key, `per_example.csv`;
- the bundle directory has exactly `manifest.json` and `per_example.csv`;
- every aggregate or subgroup file/key is forbidden.

For `full`:

- `aggregation_groups` is exactly one of the four current ordered v2 arrays beginning with `"method+setting"`:

  ```text
  ["method+setting"]
  ["method+setting", "question_type"]
  ["method+setting", "level"]
  ["method+setting", "question_type", "level"]
  ```

- `artifact_sha256` always contains exactly `per_example.csv` and `aggregate.csv`, plus the subgroup filename if and
  only if its dimension appears in `aggregation_groups` (`aggregate_by_question_type.csv` iff `question_type`;
  `aggregate_by_level.csv` iff `level`);
- the directory contains exactly `manifest.json` plus the declared artifact filenames; any undeclared extra file is
  rejected.

Every declared digest is 64 lowercase hexadecimal characters and is checked against the exact serialized bytes of
its named file.

## Stage 5 → Stage 6 lifecycle under refuse-overwrite

1. Stage 5 creates an immutable v3 `per_example_only` bundle at a new legal `e<NN>`; it never writes aggregate files.
2. Stage 6 accepts only an existing, fully validated v3 `per_example_only` bundle as its source. A v2 full bundle, a
   v3 full bundle, an invalid bundle, or an undeclared standalone CSV is not a legal source.
3. For the same raw retrieval run, Stage 6 selects the smallest unoccupied legal sequence strictly greater than the
   source sequence. If none exists through `e99`, it fails. It never wraps, reuses, deletes, extends, or overwrites a
   directory.
4. The new full manifest records the source in `source_per_example_eval_id` and `source_per_example_sha256`. The
   latter must equal both the source manifest's `artifact_sha256["per_example.csv"]` and the SHA-256 recomputed from
   the source file bytes.
5. The source and full manifests must agree exactly on the source raw run ID/checksum, dataset
   identifier/fingerprint, gold mapping version/fingerprint, metric-definition version, evaluation-protocol version,
   eval-schema version, and `k_policy`.
6. Because the new full bundle has a new `eval_id`, Stage 6 deterministically re-emits `per_example.csv` with **only**
   the row-level `eval_id` replaced by the new full-bundle ID. The header, row order, row count, and every other cell
   must be identical to the accepted source. The re-emitted file gets its own checksum in the full manifest; it is
   not falsely claimed to be byte-identical to the source.
7. Aggregation consumes only the accepted Stage 5 per-example data. It never re-reads raw rankings to recompute
   per-example metrics.
8. The source bundle remains byte-unchanged. Full-bundle publication uses a temporary sibling directory, validates
   the complete candidate bundle, and publishes atomically to the absent final directory; an existence race fails
   closed.

The explicit `source_per_example_eval_id` and `source_per_example_sha256` fields — not the `e<NN>` number — carry the
Stage 5 → Stage 6 relationship.

## Resolved design point M1-D1 — a new full eval ID makes byte-for-byte copying impossible

`per_example.csv` includes `eval_id` in every row, and the existing invariant requires those row IDs to match the
containing manifest and directory. A Stage 6 full bundle must have a new ID under refuse-overwrite. Therefore it
cannot both use a new ID and preserve the Stage 5 file byte-for-byte.

This contract resolves the contradiction by allowing exactly one deterministic row transformation: replace the
row-level `eval_id` with the new full-bundle ID and prove every other cell and the physical ordering unchanged. The
full manifest separately records the exact consumed Stage 5 `eval_id` and file checksum. No open owner decision
remains on this point.

## Contract inventory the later validator must enforce

The following are normative rules for the eventual validator/serializer. This spec states them; it does not
implement them. Each rule is paired with the adversarial control the later implementation and its independent review
must exercise (review §5, §7).

| Rule | Required implementation point | Required adversarial control |
|---|---|---|
| v2 remains the original full-only contract | version dispatcher | a legal v2 full accepts; a v2 manifest carrying a mode field or a v3-only shape rejects |
| v3 requires an explicit mode | v3 manifest validator | both legal modes accept; missing/null/non-string/unknown/contradictory mode rejects |
| mode-specific closed field sets | manifest validator | source fields required only for `full`; a missing or extra source-field twin rejects |
| mode-specific group arrays | artifact-key helper + manifest validator | `[]` only for `per_example_only`; only the four listed arrays for `full` |
| exact artifact and directory sets | bundle validator | a missing, extra, or mode-contradictory file/key rejects |
| checksums bind every declared file | checksum validator | a one-byte mutation rejects; an untouched control accepts |
| the Stage 6 source is a v3 per-example-only bundle | Stage 6 input validator | a per-example source accepts; a full/v2/invalid source rejects |
| raw/dataset/gold/version provenance agrees | source/full cross-validator | a one-field mismatch rejects against an otherwise legal control |
| a new full eval ID never overwrites | allocator/publisher | an occupied target, `e99` exhaustion, and an existence race reject; the next free ID accepts |
| only the eval ID changes in copied rows | Stage 6 transformation validator | the exact normalized twin accepts; any other cell, row-order, or row-count change rejects |
| aggregation never recomputes from raw | dependency-boundary tests | an accepted source-only control; a raw-dependent per-example recompute path is prohibited |

The full required post-amendment test matrix (review §7) is an obligation of the later implementation/review pass,
not of this contract-authoring pass.

## Freeze status

This v3 spec is **frozen**. It is the exact M1 contract that passed its independent contract re-review on 2026-07-26
(`docs/Local/Reviews/2026-07-26_stage5_m1_eval_schema_v3_contract_corrective_independent_rereview.md`). This freeze
approves the contract content only: no validator, serializer, evaluator core, test, or formal eval artifact is
implemented or authorized by this document, and Stage 6 is not begun — those remain separately authorized Stage 5
work. Now that it is frozen, any incompatible physical or semantic change requires a new explicit amendment or a new
eval-schema version rather than an implementation-time choice.
