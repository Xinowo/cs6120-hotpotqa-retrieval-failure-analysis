# Raw Retrieval Rankings Schema (v1)

**Author:** Xin · **Date:** 2026-07-20 · **Status:** Proposed contract — pending BM25-collaborator
alignment before the Stage 2 implementation freeze
**Applies to:** every raw retrieval/reranker run bundle under `results/retrieval_runs/<retrieval_run_id>/`
**Layer:** raw retrieval output only. This layer never stores gold, metrics, or failure labels.

This document is the Stage 1 contract for the raw side of the metrics/schema v2 refactor. It fixes the physical
file layout, column order, types, nullability, keys, and serialization of raw retrieval rankings and their run
manifests. The metric meaning and per-example/aggregate metric identifiers live in the separate frozen contract
`docs/specs/2026-07-17-retrieval-metrics-v2.md`; the eval file shapes live in
`docs/specs/2026-07-20-retrieval-eval-schema-v2.md`.

The legacy mixed `RESULT_COLUMNS` contract (`docs/specs/2026-07-15-results-csv-schema.md`) is a read-only
migration input, not the starting point for this schema. This raw schema must not reuse `RESULT_COLUMNS`.

## Version identifiers

One bundle-level version covers both `manifest.json` and `rankings.csv` in a run bundle; the two files never
carry divergent schema versions.

| Version key | Value | Meaning |
|---|---|---|
| raw bundle schema | `retrieval_raw_schema_v1` | field set of `manifest.json` plus the column set, order, types, and keys of `rankings.csv` |
| transitional title-only | `legacy_raw_schema_v0` | migration-only, score-free ranked titles; never a formal v1 artifact |

The manifest records this under `raw_schema_version`, and validators read it to select the rankings-column
contract. A column/layout/field change produces a new bundle-schema version. A score-free migration input uses
`legacy_raw_schema_v0` and must never masquerade as `retrieval_raw_schema_v1`.

## Directory layout

```text
results/
└── retrieval_runs/
    └── <retrieval_run_id>/
        ├── manifest.json
        └── rankings.csv
```

- `results/` and `evals/` are top-level sibling directories, so the filesystem itself enforces the
  raw/evaluation boundary.
- One run bundle represents exactly one fixed `method + setting + retrieval_depth`. A CLI invocation with
  `--setting both` creates two independent bundles and reports both run IDs; pooled and per-question raw
  outputs are never combined into one CSV.
- Debug and smoke-test outputs go to an ignored scratch directory, never a formal run bundle.
- Report-ready tables/figures belong under `analysis_outputs/`, not under raw `results/`.
- Failure-review HTML/details artifacts belong under `failure_review/runs/` (Stage 7 target), not `results/`.

## `retrieval_run_id` grammar and collision policy

```text
<method>_<setting>_n<N>_d<depth>_<YYYYMMDD>_r<NN>
```

- `method`: `bm25` | `dense` | `rerank`.
- `setting`: `pooled` | `per_question`.
- `n<N>`: number of loaded questions (`n_loaded`), e.g. `n500`.
- `d<depth>`: `retrieval_depth` recorded in the manifest, e.g. `d50`. For `pooled` this is the fixed pooled
  depth. For `per_question` the writer saves each example's complete mini-corpus, so `retrieval_depth` is the
  maximum per-example saved depth; the verifiable per-example truth is the manifest `per_example_corpus_size`
  map (see "Per-question completeness").
- `<YYYYMMDD>`: run date, UTC, compact with no separators.
- `r<NN>`: two-digit sequence starting at `01`, incremented for a same-day rerun of the same configuration.

Examples:

```text
dense_pooled_n500_d50_20260720_r01
bm25_pooled_n500_d50_20260720_r01
dense_per_question_n500_d10_20260720_r01
```

Collision policy: if the target `results/retrieval_runs/<retrieval_run_id>/` directory already exists, the
writer refuses and errors; it never overwrites. Full fingerprints/checksums live in the manifest, not the ID.

## `rankings.csv`

Long format, one row per `(example_id, rank)`. Fixed column order:

| # | Column | Type | Values / format | Nullable | Notes |
|---|---|---|---|---|---|
| 1 | `retrieval_run_id` | str | matches the containing directory and manifest exactly | no | join/concatenation safety |
| 2 | `method` | str | `bm25` \| `dense` \| `rerank` | no | matches the manifest |
| 3 | `setting` | str | `pooled` \| `per_question` | no | matches the manifest |
| 4 | `example_id` | str | HotpotQA `_id` | no | stable cross-artifact join key |
| 5 | `rank` | int | 1-based | no | continuous per example, no gaps or duplicates |
| 6 | `title` | str | retrieved passage title | no | current retrieval/evaluation unit; the raw layer never decides gold |
| 7 | `score` | float | finite native retriever score | no (v1) | produced by the same retrieval call; never fabricated or back-derived from rank |

Constraints:

- `rank` starts at `1` and increases by exactly `1` within each `example_id`.
- `(retrieval_run_id, example_id, rank)` is unique.
- Every `score` is a finite float. A missing score makes the file `legacy_raw_schema_v0`, not raw v1.
- For a `pooled` run, every example has exactly `retrieval_depth` rows. A pooled saved list shorter than
  `retrieval_depth` is valid only when the pooled corpus itself is smaller (`corpus_size < retrieval_depth`),
  which the manifest establishes.
- For a `per_question` run, every example saves its complete mini-corpus:
  `saved_depth(example) == per_example_corpus_size(example)`. An example whose ranking was capped below its
  full mini-corpus (`saved_depth < per_example_corpus_size`) is an invalid raw artifact, because the corpus was
  not exhausted and deep metrics such as RR@50 would be miscomputed on a truncated list.

The raw layer must never contain any of:

```text
question_type      level              gold_titles / gold_ranks
question text (repeated per row)      any/full/evidence-recall metrics
reciprocal rank / MRR                 failure labels
report-facing display names
```

### `question` policy

Rankings store only `example_id`. The manifest records the dataset identifier and fingerprint, and evaluation
reloads the same dataset snapshot by ID. If external dataset reproducibility is required, save a separate
`queries.jsonl` keyed by `example_id`; question text is never repeated on every candidate row.

## `manifest.json`

`manifest.json` is a single JSON object. Every field below has a fixed JSON type; conditional fields state the
`setting`/`method` under which they are required.

| Field | JSON type | Required | Nullable | Constraints |
|---|---|---|---|---|
| `raw_schema_version` | string | yes | no | `retrieval_raw_schema_v1` (or `legacy_raw_schema_v0`) |
| `retrieval_run_id` | string | yes | no | matches the directory and every rankings row |
| `created_at` | string | yes | no | ISO-8601 UTC |
| `method` | string | yes | no | `bm25` \| `dense` \| `rerank`; matches rankings |
| `setting` | string | yes | no | `pooled` \| `per_question`; matches rankings |
| `split` | string | yes | no | e.g. `validation` |
| `n_requested` | integer | yes | no | ≥ 1 |
| `n_loaded` | integer | yes | no | ≥ 1; equals the distinct `example_id` count |
| `retrieval_depth` | integer | yes | no | pooled fixed depth; per_question max per-example saved depth |
| `score_type` | string | yes | no | `cosine_similarity` \| `bm25_okapi` \| `cross_encoder_logit` |
| `score_direction` | string | yes | no | `higher_is_better` |
| `model_or_retriever_config` | object | yes | no | model id / tokenizer / retriever configuration |
| `dataset_identifier` | string | yes | no | dataset name/version |
| `dataset_fingerprint` | string | yes | no | fingerprint of the loaded dataset snapshot |
| `example_ids_fingerprint` | string | yes | no | fingerprint of the ordered evaluated `example_id` set |
| `corpus_fingerprint` | string | yes | no | fingerprint of the corpus used for retrieval |
| `corpus_size` | integer | pooled only | no | size of the shared pooled corpus; omitted for `per_question` |
| `per_example_corpus_size` | object (string → integer) | per_question only | no | `example_id` → mini-corpus size; omitted for `pooled` |
| `deduplication_policy` | string | yes | no | how duplicate/colliding titles are handled |
| `tie_break_policy` | string | yes | no | deterministic tie-break rule for equal scores |
| `git_commit` | string | yes | no | code commit that produced the run |
| `command` | string | yes | no | exact command line |
| `rankings_sha256` | string | yes | no | SHA-256 of `rankings.csv` |
| `parent_retrieval_run_id` | string | rerank only | no | the raw run whose candidates were reranked |
| `parent_rankings_sha256` | string | rerank only | no | checksum of the parent `rankings.csv` |
| `parent_candidate_depth` | integer | rerank only | no | number of parent candidates consumed per example |

Serialization and checksum rules:

```text
CSV:            UTF-8, comma-delimited, header row required, LF (\n) newlines, standard CSV quoting
rankings order: ascending manifest example_id order, then ascending rank within each example
manifest.json:  UTF-8 object, keys sorted, one trailing newline
rankings_sha256: SHA-256 over the exact serialized bytes of rankings.csv
```

Score semantics recorded via `score_type` / `score_direction`:

- Dense: dot product of L2-normalized embeddings (equivalent to cosine similarity); higher is better.
- BM25: native BM25Okapi score; higher is better.
- Reranker: native Cross-Encoder output; the manifest states whether it is a logit or another score type.
- Values from different `score_type` systems must not be compared directly across methods.

### Per-question completeness

For a `per_question` run every example saves its complete mini-corpus, so
`saved_depth(example) == per_example_corpus_size(example)` and the list is never truncated below the full
corpus. Because the full mini-corpus is present, RR@10 and RR@50 are both computable; they coincide only when a
mini-corpus contains no gold beyond rank 10. If any example was capped below its full mini-corpus, the run is
invalid raw output: RR@50 (and any metric whose horizon exceeds that example's `saved_depth`) must be rejected
rather than computed on a truncated list. The evaluator verifies completeness per example against
`per_example_corpus_size`.

## Reranker specifics

- A `rerank` run consumes the Dense pooled raw run and records `parent_retrieval_run_id`,
  `parent_rankings_sha256`, and `parent_candidate_depth` as first-class manifest fields, not inside
  `model_or_retriever_config`.
- Reranking never introduces candidates outside the parent top-50 (verified downstream in Stage 7).

## Migration safety (read-only inputs)

- Never infer raw rankings from legacy metric columns; never fabricate or back-derive missing scores.
- A transitional score-free artifact uses `legacy_raw_schema_v0` and is never presented as
  `retrieval_raw_schema_v1`.
- Formal raw v1 artifacts are produced by the new writer from genuine retrieval outputs. Any temporary
  legacy-shaped comparison view is written only to ignored migration scratch and deleted after the audit.

## Alignment status

This is a proposed contract. Per the refactor policy (HANDOFF §6, plan working-branch policy), the raw column
set, run-ID grammar, directory layout, and manifest fields must be confirmed with the BM25 collaborator before
the Stage 2 schema constants/validators freeze them. Until then, only offline schema work proceeds.
