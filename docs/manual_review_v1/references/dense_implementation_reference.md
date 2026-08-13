---
status: active
last_updated: 2026-08-04
---

# Dense Implementation Reference for Failure Review

## Scope

This document records the Dense retrieval implementation contract used by
source run `2026-07-17_a` and the `manual_review_v1` failure-review corpus. It
supports mechanism-level interpretation of Dense failures and comparison-panel
evidence. Revalidate these facts before applying them to another run,
dependency environment, model revision, or retriever implementation.

The implementation lives in the sibling repository
`main-cs6120-hotpotqa-retrieval-failure-analysis`.

## Verified implementation contract

### Retriever architecture

The main Dense experiment uses a symmetric bi-encoder:

- model: `sentence-transformers/all-MiniLM-L6-v2`;
- one shared `SentenceTransformer` instance for queries and passages;
- no query or passage prompt or prefix;
- one independent embedding per passage;
- one independent embedding per query; and
- no query-passage cross-attention during the main Dense retrieval stage.

Batch encoding and matrix multiplication only parallelize independent scoring.
They do not introduce passage-to-passage attention or cross-passage reasoning.

### Document construction and indexed fields

`src/data_loader.py::_build_paragraphs` strips each sentence and joins the
sentences belonging to a HotpotQA title with one space. It stores the title
separately from the resulting paragraph `text`.

`src/dense_retriever.py::DenseRetriever` encodes:

```python
[p.text for p in paragraphs]
```

It does not encode `p.title` or `p.title + p.text`. The title is metadata used
for result identification, pooled-corpus deduplication, cache validation, and
gold-title matching. A displayed title must not be treated as evidence that
its tokens contributed to Dense similarity.

The query input is the unchanged `example.question`. The passage input is the
space-joined paragraph text. Neither input receives a role-specific prefix
such as `query:`, `passage:`, or `Represent this sentence:`.

### Embedding and scoring

The project calls:

```python
model.encode(
    texts,
    convert_to_numpy=True,
    show_progress_bar=False,
)
```

The returned arrays are converted to NumPy `float32`. The project then applies
explicit row-wise L2 normalization to both passage and query embeddings. The
model snapshot also contains a Normalize module, but the project-level
normalization guarantees that vectors entering retrieval are unit length even
if model behavior changes.

Scoring is:

```python
scores = normalized_doc_embeddings @ normalized_query_vector
```

The dot product of two unit vectors is numerically equal to cosine similarity.
The main Dense retrieval therefore does not use Euclidean distance.

Results are sorted by descending score with Python's stable sort. Exact score
ties retain original corpus order. There is no score threshold or additional
filter before `top_k` truncation.

### Sequence length and pooling

The currently inspected local model snapshot has:

- maximum sequence length: 256 tokens;
- overlength behavior: tokenizer truncation with `longest_first`;
- embedding dimension: 384;
- pooling: attention-mask-aware mean pooling; and
- CLS and max pooling: disabled.

The project does not override `model.max_seq_length`. When a relevant clue may
occur late in a long passage, failure review should check whether it falls
beyond the effective 256-token input window. Do not claim truncation as a cause
without measuring the actual tokenized passage.

### Tokenizer normalization

The model's tokenizer is a WordPiece tokenizer that **lower-cases and strips accents**.
Verified on 2026-08-04 against the loaded model: `F. Javier gutierrez` and
`F. Javier Gutiérrez` both tokenize to `f`, `.`, `javier`, `gutierrez`.

Two consequences for failure review, both established in D-029 and recorded here so no
later case re-derives them:

1. **Capitalization and accent differences between a query and a passage are identity
   operations on this backend, not surface-form defects.** A wording factorial that varies
   only case or accents will reproduce its baseline bit for bit; D-029's eight-cell A x B x C
   design collapsed to two distinct results for exactly this reason. Do not spend a factor on
   them, and do not adopt `surface_form_tokenization_mismatch` on a Dense unit for a case or
   accent difference.
2. **A dataset typo in a name is therefore not, by itself, a Dense mechanism.** It may still
   matter for the BM25 unit of the same `example_id`, where the tokenizer is
   `text.lower().split()` with no normalization at all, so the two backends must be argued
   separately.

This is a statement about token identity only. It says nothing about whether a name that
does tokenize correctly is retrievable; D-029 measured a name that is present in exactly one
corpus passage and still ranked that passage 2202 of 4937 when the query was reduced to the
name itself.

### No reranker in the main Dense results

The formal Dense experiment does not call a reranker. It has no cross-encoder,
threshold, or cross-passage reasoning step.

The repository contains a separate reranking experiment using
`cross-encoder/ms-marco-MiniLM-L-6-v2`. It independently scores each
`(query, candidate.text)` pair from Dense pooled top 50 and writes
`rerank_results.csv`. It still excludes titles and does not jointly reason over
multiple candidates. Reranker behavior must not be attributed to
`dense_results.csv`.

### Corpus settings

The retrieval algorithm is the same in both corpus settings, but the retrieval
environments are not equivalent.

#### Per-question

- Each question receives its own HotpotQA context paragraphs.
- A new small Dense index is constructed for each question.
- No extra deduplication is performed.
- The formal run stores top 10 and reports metrics at 2 and 5.

#### Pooled

- All reviewed examples share one pooled index.
- Paragraphs are deduplicated by title.
- The first text observed for a title is retained.
- Later same-title/different-text entries are recorded as collisions but do not
  replace the retained passage.
- Corpus order follows first appearance.
- Queries are scored in batches against the shared index.
- The formal run stores top 50 and reports metrics at 2, 5, and 10.

Pooling can introduce many semantically related competitors. A pooled failure
must not be interpreted as if it came from the original small per-question
context. Conversely, a suspected pooling artifact should be checked against
the per-question ranking rather than inferred from corpus size alone.

## Failure-review implications

When reviewing a Dense unit from this implementation:

1. Read the complete retrieved paragraph text; do not explain similarity from
   the displayed title because title tokens are not embedded.
2. Treat each score as standalone query-to-passage cosine similarity. Do not
   attribute cross-passage reasoning, candidate interaction, or reranker
   behavior to the main Dense ranking.
3. Describe coherent high-ranked semantic neighborhoods as observed output
   behavior. Do not claim token-level attention or an internal feature weight
   without an appropriate probing or attribution experiment.
4. Check whether exact entity names appear in paragraph text. Title-only entity
   information is unavailable to the retriever. Presence is not reachability: reduce the
   query to the name and measure where the passage containing it actually ranks, with a
   short descriptive query as a length control and a subject-position name as a position
   control.
5. Check long passages for 256-token truncation only when the relevant clue's
   position makes this plausible, and verify the tokenized position before
   assigning the mechanism.
6. Use per-question results to determine whether a strong pooled competitor was
   part of the item's original context or introduced through pooling.
7. Distinguish a complete plausible non-gold answer from a merely related
   semantic neighbor by checking every explicit query constraint against the
   passage text.
8. Use score margins to describe cutoff sensitivity, not to infer an internal
   causal feature.
9. Do not compare Dense and BM25 score magnitudes; their scores have different
   meanings and scales.
10. Revalidate model, dependency, revision, and sequence-length facts for a new
    run before reusing implementation-specific conclusions.

## Worked interpretation: `5a76387d554299109176e6ba|dense`

Dense ranks `Am Rong` and `Ava DuVernay` at 26 and 27 while higher passages
form a broad person and birth-related neighborhood. The implementation confirms
that this is a text-only, independently scored cosine ranking without a
reranker. It supports describing the output as consistent with broad
person/birth semantics outranking the exact entities.

It does not establish that the model internally "attended to `born`" or reveal
the contribution of an individual token. The primary open code
`two_named_entities_underprioritized` therefore remains appropriate, with
`generic_person_semantic_neighborhood` as an output-level secondary descriptor.

## Worked interpretation: `5a83aaeb5542996488c2e483|dense`

`Graduation` ranks first as an independently embedded paragraph. Its actual
text satisfies the Kanye West album, Roc-A-Fella, and Dwele constraints, and
the per-question ranking also places it first. The implementation establishes
that no reranker or cross-passage component constructed this alternative;
the single passage itself is a complete plausible non-gold answer.

This evidence preserves `plausible_non_gold_answer` as the primary code.
Same-artist semantic proximity can explain other Kanye works in the ranking but
does not turn the complete `Graduation` answer into an ordinary distractor.

## Version and reproducibility boundary

The repository declares only:

```text
sentence-transformers>=2.7.0
```

It does not lock `transformers`, `torch`, or the Hugging Face model revision.
The currently inspected environment contains:

- `sentence-transformers==5.1.2`;
- `transformers==4.57.6`;
- `torch==2.8.0`;
- `tokenizers==0.22.2`;
- `numpy==2.0.2`; and
- `datasets==4.5.0`.

The currently cached model revision is
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, but the loading code does not pass
`revision=` and the historical result files contain no environment or model
manifest. The current revision, dependency versions, and CPU device therefore
cannot be asserted as the exact environment that generated the historical
Dense CSV files.

The implementation contract visible in repository code is stable enough for
the interpretations above, but strict run reproduction requires an explicit
future environment and model manifest.

## Provenance

Implementation locations in
`main-cs6120-hotpotqa-retrieval-failure-analysis`:

- `src/dense_retriever.py::DenseRetriever`;
- `src/dense_retriever.py::_build_default_encoder`;
- `src/dense_retriever.py::_l2_normalize`;
- `src/data_loader.py::_build_paragraphs`;
- `src/data_loader.py::build_pooled_corpus`;
- `scripts/run_dense_experiment.py`;
- `src/cross_encoder_reranker.py`; and
- `requirements.txt`.

The supplied implementation audit reports 41 passing offline tests and no code
changes. If indexed fields, model name, prompt behavior, sequence length,
normalization, similarity, reranking, corpus construction, dependency version,
or model revision changes, associate the change with a new run ID before
reusing these conclusions.
