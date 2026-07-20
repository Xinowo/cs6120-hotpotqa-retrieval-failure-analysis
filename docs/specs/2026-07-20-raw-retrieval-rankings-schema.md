# Raw Retrieval Rankings Schema (v1)

**Author:** Xin · **Date:** 2026-07-20 · **Status:** Frozen for Stage 2 implementation
**Applies to:** every raw retrieval/reranker run bundle under `results/retrieval_runs/<retrieval_run_id>/`
**Layer:** raw retrieval output only. This layer never stores gold, metrics, or failure labels.

The remaining BM25-interface decisions were closed by owner-delegated review on 2026-07-20; separate collaborator
sign-off is not required. The decision record is
`docs/Local/Plans/2026-07-20_bm25_interface_alignment_checklist.md`.

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
- For a `pooled` run, every example has exactly `min(retrieval_depth, corpus_size)` rows. The v2 protocol requests
  `retrieval_depth = 50`; therefore a formal corpus with at least 50 entries has exactly 50 ranks per example.
- For a `per_question` run, every example saves its complete mini-corpus:
  `saved_depth(example) == per_example_corpus_size(example)`. An example whose ranking was capped below its
  full mini-corpus (`saved_depth < per_example_corpus_size`) is an invalid raw artifact, because the corpus was
  not exhausted and deep metrics such as RR@50 would be miscomputed on a truncated list. The writer requests
  `top_k = per_example_corpus_size(example)`; there is no per-question storage cap, including when a mini-corpus
  contains more than 50 entries.

The raw layer must never contain any of:

```text
question_type      level              gold_titles / gold_ranks
question text (repeated per row)      any/full/evidence-recall metrics
reciprocal rank / MRR                 failure labels
report-facing display names
```

### `question` policy

Rankings store only `example_id`. The manifest records the dataset identifier and fingerprint, and evaluation
reloads the same dataset snapshot by ID. `retrieval_raw_schema_v1` permits exactly the two files in the directory
layout above; `queries.jsonl` is not part of a v1 run bundle. If a future portability requirement needs stored query
text, it must use a separately versioned schema that defines that file and its checksum. Question text is never
repeated on every candidate row.

## `manifest.json`

`manifest.json` is a single JSON object. Every field below has a fixed JSON type; conditional fields state the
`setting`/`method` under which they are required.

| Field | JSON type | Required | Nullable | Constraints |
|---|---|---|---|---|
| `raw_schema_version` | string | yes | no | `retrieval_raw_schema_v1` (or `legacy_raw_schema_v0`) |
| `retrieval_run_id` | string | yes | no | matches the directory and every rankings row |
| `created_at` | string | yes | no | UTC `YYYY-MM-DDTHH:MM:SSZ`; no fractional seconds |
| `method` | string | yes | no | `bm25` \| `dense` \| `rerank`; matches rankings |
| `setting` | string | yes | no | `pooled` \| `per_question`; matches rankings |
| `split` | string | yes | no | e.g. `validation` |
| `n_requested` | integer | yes | no | ≥ 1 |
| `n_loaded` | integer | yes | no | ≥ 1; equals the distinct `example_id` count |
| `retrieval_depth` | integer | yes | no | pooled fixed depth; per_question max per-example saved depth |
| `score_type` | string | yes | no | method-matched: Dense=`cosine_similarity`, BM25=`bm25_okapi`, Rerank=`cross_encoder_logit` |
| `score_direction` | string | yes | no | `higher_is_better` |
| `model_or_retriever_config` | object | yes | no | exact closed shape defined below |
| `dataset_identifier` | string | yes | no | dataset name/version |
| `dataset_fingerprint` | string | yes | no | `sha256:<64 lowercase hex>` of the canonical loaded dataset snapshot |
| `example_ids_fingerprint` | string | yes | no | `sha256:<64 lowercase hex>` of the ordered evaluated `example_id` list |
| `corpus_fingerprint` | string | yes | no | `sha256:<64 lowercase hex>` of the setting-specific ordered retrieval corpus |
| `corpus_size` | integer | pooled only | no | positive size of the shared pooled corpus; omitted for `per_question` |
| `per_example_corpus_size` | object (string → integer) | per_question only | no | exact ranked `example_id` set → positive mini-corpus size; omitted for `pooled` |
| `deduplication_policy` | string | yes | no | one setting/method-matched closed identifier defined below |
| `tie_break_policy` | string | yes | no | one method-matched closed identifier defined below |
| `git_commit` | string | yes | no | code commit that produced the run |
| `command` | string | yes | no | exact command line |
| `rankings_sha256` | string | yes | no | 64 lowercase hexadecimal characters; SHA-256 of `rankings.csv` |
| `parent_retrieval_run_id` | string | rerank only | no | the raw run whose candidates were reranked |
| `parent_rankings_sha256` | string | rerank only | no | 64 lowercase hexadecimal characters; checksum of the parent `rankings.csv` |
| `parent_candidate_depth` | integer | rerank only | no | ≥ 1; fixed number of parent candidates consumed per example |

Conditional fields are omitted when their condition is false; they are never serialized as JSON `null`.
`per_example_corpus_size` has exactly `n_loaded` keys, its key set equals the distinct `example_id` set in
`rankings.csv`, and every value is an integer ≥ 1. All unconstrained provenance strings in the table must be
non-empty strings. A `retrieval_raw_schema_v1` manifest has no additional top-level fields and duplicate JSON
object keys are invalid. The migration adapter owns the separate complete shape for `legacy_raw_schema_v0`.

### Fingerprints and corpus policies

Fingerprint input uses canonical JSON bytes with no trailing newline:

```text
json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
           separators=(',', ':')).encode('utf-8')
```

The stored value is `sha256:` followed by the SHA-256 lowercase hexadecimal digest of those exact bytes.

- `dataset_fingerprint` hashes the JSON array of the complete loaded raw dataset records, in selected dataset
  order, before conversion to `HotpotExample`.
- `example_ids_fingerprint` hashes the JSON array of `example_id` strings in that same selected dataset order.
- For `pooled`, `corpus_fingerprint` hashes the post-deduplication JSON array of
  `{"title": <string>, "text": <string>}` objects in corpus input order.
- For `per_question`, `corpus_fingerprint` hashes the selected-order JSON array of
  `{"example_id": <string>, "paragraphs": [{"title": <string>, "text": <string>}, ...]}` objects, with each
  paragraph array in source context order.

Formal Dense and BM25 comparisons require equal `setting`, `dataset_identifier`, `dataset_fingerprint`,
`example_ids_fingerprint`, and `corpus_fingerprint`. The corpus fingerprint must match across methods within one
setting. It is not expected to match between `pooled` and `per_question`, whose corpora differ by design.

Closed policy identifiers:

| Condition | `deduplication_policy` | Behavior |
|---|---|---|
| Dense/BM25, `pooled` | `exact_title_keep_first_dataset_order` | remove later exact-title duplicates; the first loaded dataset/context occurrence supplies text and corpus position, including different-text title collisions |
| Dense/BM25, `per_question` | `none_preserve_source_order` | retain every source context row in its original order |
| Rerank | `none_parent_candidate_set_unchanged` | preserve the parent candidate set; do not add, remove, or deduplicate candidates |

| Condition | `tie_break_policy` | Behavior |
|---|---|---|
| Dense/BM25 | `score_desc_then_corpus_order_asc` | descending native score, then ascending input corpus position through stable sorting |
| Rerank | `score_desc_then_parent_rank_asc` | descending native score, then ascending parent rank through stable sorting |

The policy identifier plus the corpus fingerprint records pooled title-collision handling without adding collision
titles or text to `rankings.csv`.

### `model_or_retriever_config` shape

The object has exactly these three top-level keys:

```json
{
  "implementation": "non-empty implementation/library name",
  "identifier": "non-empty model or retriever identifier",
  "parameters": {}
}
```

- `implementation` and `identifier` are non-empty strings.
- `parameters` is an object with string keys. Its values use the recursive `JSONValue` grammar:
  `null | boolean | finite number | string | array<JSONValue> | object<string, JSONValue>`.
- No other top-level keys are allowed. Method-specific tokenizer, BM25, encoder, or Cross-Encoder settings live
  under `parameters`; the manifest validator validates the closed outer shape and recursively valid JSON values,
  while method-specific provenance tests validate the required parameter names.

For `method = bm25`, the complete object has exactly this shape and no extra key:

```json
{
  "implementation": "rank_bm25",
  "identifier": "BM25Okapi",
  "parameters": {
    "b": 0.75,
    "epsilon": 0.25,
    "k1": 1.5,
    "lowercase": true,
    "package_version": "0.2.2",
    "stopword_policy": "none",
    "tokenizer": "python_str_split"
  }
}
```

`b`, `epsilon`, and `k1` are finite JSON numbers containing the actual run values; `package_version` is the
non-empty installed distribution version. `lowercase` is a boolean. `tokenizer` and `stopword_policy` are the
exact strings shown for the current implementation, which tokenizes with `text.lower().split()` and performs no
stopword removal. A future BM25 tokenizer or parameter-key change requires a raw-schema contract amendment.
Corpus construction is not duplicated under `parameters`; it is covered by `setting`, `deduplication_policy`,
`corpus_size` / `per_example_corpus_size`, and `corpus_fingerprint`.

Serialization and checksum rules:

```text
CSV bytes:       UTF-8 without BOM; comma delimiter; header required; LF (\n) record terminator
CSV dialect:     quotechar='"', doublequote=true, escapechar absent, QUOTE_MINIMAL
integer text:    base-10 ASCII, no leading '+' and no leading zero except the value 0
float text:      Python format(value, '.17g'), lowercase exponent, with negative zero normalized to 0
rankings order:  ascending example_id by Unicode code point, then ascending integer rank
manifest bytes:  json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True,
                 separators=(',', ':')) encoded as UTF-8 without BOM, followed by one LF
rankings_sha256: SHA-256 over the exact serialized bytes of rankings.csv
```

CSV string values are passed through unchanged; the fixed dialect quotes fields containing a comma, quote, CR, or
LF and doubles an embedded quote. These rules apply before checksum calculation. A v1 bundle contains exactly
`manifest.json` and `rankings.csv`; the manifest is deliberately not checksummed by itself because that would be
self-referential.

Score semantics recorded via `score_type` / `score_direction`:

- Dense: dot product of L2-normalized embeddings (equivalent to cosine similarity); higher is better.
- BM25: native BM25Okapi score; higher is better.
- Reranker: native Cross-Encoder logit recorded as `cross_encoder_logit`. Supporting another output type requires
  an explicit contract amendment before a v1 writer may emit it.
- Values from different `score_type` systems must not be compared directly across methods.

### Per-question completeness

For a `per_question` run every example saves its complete mini-corpus, so
`saved_depth(example) == per_example_corpus_size(example)` and the list is never truncated below the full
corpus. The bundle-level depth must also satisfy
`retrieval_depth == max(per_example_corpus_size.values()) == max(saved_depth(example))`. Because the full
mini-corpus is present, RR@10 and RR@50 are both computable; they coincide only when a mini-corpus contains no gold
beyond rank 10. If any example was capped below its full mini-corpus, the run is invalid raw output: RR@50 (and any
metric whose horizon exceeds that example's `saved_depth`) must be rejected rather than computed on a truncated
list. The evaluator verifies completeness per example against `per_example_corpus_size`. Extra or missing map
keys, non-positive sizes, any saved-depth mismatch, or a bundle-level `retrieval_depth` unequal to the maximum map
value invalidates the bundle.

## Writer and parity requirements

- The method-agnostic writer consumes already-produced `(Paragraph, score)` batches from the retrieval call that
  determines the ranking. Export never invokes retrieval a second time.
- Before bundle acceptance, validate the exact schema, expected row counts/depth, rank continuity, key uniqueness,
  finite scores, deterministic row order, manifest agreement, and `rankings_sha256`.
- Formal BM25 migration requires zero per-rank title mismatches. For pooled n=500, failure-review `details.jsonl`,
  the legacy pooled `bm25_results.csv`, and the new-writer output must agree at every saved rank. Per-question raw
  v1 reruns must agree with every title rank present in the legacy file. Any mismatch blocks promotion and is
  investigated rather than normalized away.

## Reranker specifics

- A `rerank` run consumes the Dense pooled raw run and records `parent_retrieval_run_id`,
  `parent_rankings_sha256`, and `parent_candidate_depth` as first-class manifest fields, not inside
  `model_or_retriever_config`.
- In v1, `method = rerank` requires `setting = pooled`, a Dense pooled parent, and
  `parent_candidate_depth == retrieval_depth` for every example. Non-rerank manifests omit all three parent fields.
- Reranking never introduces candidates outside the parent top-50 (verified downstream in Stage 7).

## Migration safety (read-only inputs)

- Never infer raw rankings from legacy metric columns; never fabricate or back-derive missing scores.
- A transitional score-free artifact uses `legacy_raw_schema_v0` and is never presented as
  `retrieval_raw_schema_v1`.
- Formal raw v1 artifacts are produced by the new writer from genuine retrieval outputs. Any temporary
  legacy-shaped comparison view is written only to ignored migration scratch and deleted after the audit.

## Freeze status

The raw column set, run-ID grammar, directory layout, manifest fields, BM25 configuration, corpus policies, and
writer/parity rules are frozen for Stage 2 implementation. Any incompatible physical or semantic change requires
an explicit schema/protocol amendment rather than an implementation-time choice.
