---
status: active
last_updated: 2026-08-04
---

# BM25 Implementation Reference for Failure Review

## Scope

This document records the BM25 implementation contract used by source run
`2026-07-17_a` and the `manual_review_v1` failure-review corpus. It supports
mechanism-level interpretation of BM25 failures. Revalidate these facts before
applying them to a different run or implementation version.

The implementation lives in the sibling repository
`main-cs6120-hotpotqa-retrieval-failure-analysis`.

## Verified implementation contract

### Document construction and indexed fields

`src/data_loader.py::_build_paragraphs` stores each HotpotQA title separately
from a paragraph `text` formed by joining the associated sentences.

`src/retrievers.py::BM25Retriever.__init__` builds the corpus with:

```python
tokenized_corpus = [_tokenize(p.text) for p in paragraphs]
```

Only paragraph `text` contributes to BM25 scores. The title is returned as
metadata and used for gold-title evaluation and pooled-corpus deduplication, but
it is not part of the indexed document.

### Tokenization and normalization

Both documents and queries use:

```python
def _tokenize(text: str) -> List[str]:
    return text.lower().split()
```

The pipeline therefore performs lowercase conversion and whitespace splitting
only. It does not perform:

- punctuation removal or normalization;
- stop-word removal;
- stemming or lemmatization;
- Unicode normalization;
- phrase matching;
- entity recognition or entity-boundary preservation; or
- initial expansion, such as mapping `J.` to `James`.

Punctuation remains attached to tokens. For example, `barrie?`, `barrie,`,
and `barrie.` are three distinct tokens.

### BM25 scoring and ranking

The retriever passes the tokenized corpus to `rank_bm25.BM25Okapi`, scores the
tokenized query with `get_scores`, and sorts documents by descending score.
The current environment uses `rank-bm25==0.2.2`; the repository requirement is
`rank-bm25>=0.2.2`. No explicit BM25 parameters are passed, so the library
defaults apply:

- `k1=1.5`;
- `b=0.75`; and
- `epsilon=0.25`.

BM25 scores query tokens without positions, phrase structure, or entity
membership. Tokens originating in different entity names or query facets can
therefore contribute jointly to an unrelated document.

`rank-bm25==0.2.2` iterates directly over the tokenized query list in
`BM25Okapi.get_scores` and adds a score contribution for each occurrence. It
does not deduplicate repeated query tokens. A term appearing four times in a
query therefore contributes four times to every document containing that
term. With the reviewed tokenizer, this also applies to unfiltered function
words such as `of` and `the`.

### Corpus settings

`scripts/run_bm25_experiment.py` evaluates two settings:

- `pooled`: one index over the shared pooled paragraph corpus; and
- `per_question`: a separate index over each question's supplied paragraphs.

Failure review must record which setting produced the reviewed result. The
`manual_review_v1` pooled-corpus evidence must not be interpreted as if it
came from the smaller per-question index.

**Changing the setting changes the scoring function, not just the candidate
set.** `BM25Okapi` derives `idf` from the corpus size and document frequency and
normalizes document length by `avgdl`, and both are recomputed per index. A
`per_question` index therefore assigns different weights to the same query
tokens over the same documents. Two consequences follow:

- restricting the pooled scores to an item's own paragraphs is **not** the
  per-question ranking, and the two can disagree in order; and
- `pooled` and `per_question` ranks for the same unit are not on a common scale
  and must not be compared as if a passage "moved".

With `epsilon=0.25`, any term whose classic idf is negative is replaced by
`0.25 * average_idf`. In a ten-document index this fires easily: a term occurring
in more than about half the documents is floored, and several distinct terms then
carry the identical floored weight. A term occurring in exactly half the
documents receives `log(5.5 / 5.5) = 0` and contributes nothing at all. See the
corpus-setting subsection of the `5a78b209554299148911f93e|bm25` worked case for
a measured instance.

This contrast is specific to lexical retrieval. Cosine similarity over
`all-MiniLM-L6-v2` contains no collection statistic, so for the Dense backend the
per-question ranking really is the pooled ranking restricted to the item's
paragraphs; see `references/dense_implementation_reference.md`.

## Failure-review implications

When reviewing a BM25 unit from this implementation:

1. Compare query tokens with the complete gold passage text, not merely the
   displayed gold title.
2. Do not assume a title contributes to retrieval just because it is used to
   identify a gold hit.
3. Check punctuation-bearing forms exactly. A question mark, comma, period, or
   parenthesis can prevent an otherwise obvious word match.
4. Check abbreviations and initials. The implementation cannot connect initials
   to expanded names without literal token overlap.
5. Check whether tokens from different entities or query facets recombine in a
   distractor because token order and entity boundaries are not represented.
6. Treat clusters of related retrieved documents as possible downstream
   consequences when a more specific tokenization or name-form mismatch is
   directly supported.
7. Do not generalize these implementation-specific findings to every BM25
   system; different analyzers, indexed fields, n-grams, or entity-aware
   preprocessing can behave differently.
8. Do not claim exact per-token causal contribution without decomposing the
   BM25 score. Ranks and token overlap support a mechanism, but they do not by
   themselves quantify each token's contribution.
9. Check repeated query tokens. Under `rank-bm25==0.2.2`, every occurrence is
   accumulated, so repeated function or content words may materially amplify a
   distractor.
10. Before reading the `per_question` ranks at all, check the document frequency
    of the query's discriminative tokens inside that ten-document index. A term
    can be worth nothing there while being the unit's strongest pooled signal,
    and the resulting ranking can then be driven entirely by function words.

## Worked case: `5a78b209554299148911f93e|bm25`

Question:

```text
Which playwright lived a longer life, Edward Albee or J. M. Barrie?
```

Relevant whitespace tokens are:

| Source | Entity-bearing tokens |
|---|---|
| Query | `edward`, `albee`, `j.`, `m.`, `barrie?` |
| Edward Albee gold text | `edward`, `albee` |
| J. M. Barrie gold text | `james`, `matthew`, `barrie,` |
| `J. Edward Snyder` result | `j.`, `edward` |
| `Peter Pan (1953 film)` result | `j.`, `m.`, `barrie.` |

The J. M. Barrie title is not indexed. Its gold text expands the initials and
uses `barrie,`, so none of the three query name tokens `j.`, `m.`, and
`barrie?` matches the corresponding gold-text name form. By contrast,
`J. Edward Snyder` combines `j.` from one queried name with `edward` from
the other.

For this case, the most specific provisional mechanism is
`entity_name_tokenization_mismatch`. Use
`cross_entity_token_recombination` and `related_name_document_crowding` as
secondary descriptors. `one_sided_entity_crowding` describes the resulting
ranking pattern but is less specific than the implementation-supported
name-form mismatch.

### Corpus setting: the two golds swap order, and only the statistics moved

The stored results place `Edward Albee` above `J. M. Barrie` under `pooled` and
below it under `per_question`. Both settings were reproduced bit for bit from the
read-only pooled corpus, using the ten paragraphs named in the stored
`per_question` `retrieved_titles` field.

| Condition | idf / avgdl source | Candidates | `Edward Albee` | `J. M. Barrie` |
|---|---|---:|---:|---:|
| `pooled` (stored) | pooled 4,937 | 4,937 | 6 / 19.520331 | 640 / 4.908864 |
| **C1** pooled scores restricted to the item's 10 paragraphs | pooled 4,937 | 10 | **6** / 19.520331 | **10** / 4.908864 |
| `per_question` (stored) | 10-document index | 10 | **10** / 0.781630 | **6** / 1.454420 |
| **C2** the 10 documents, pooled idf substituted, per-question `avgdl` | mixed | 10 | 5 / 16.580502 | 10 / 4.217603 |
| **C3** the 10 documents, pooled idf and pooled `avgdl` | pooled 4,937 | 10 | 6 / 19.520331 | 10 / 4.908864 |

C1 keeps the pooled order, so the swap is not caused by the smaller candidate
set. C3 reproduces C1 to the last digit, so the swap is fully accounted for by
the collection statistics. C2 shows that `idf` carries essentially all of it: the
two golds are already back in their pooled order at 5 and 10, and `avgdl` only
adjusts magnitudes and two adjacent non-gold pairs.

Query tokens under `text.lower().split()`, with document frequency and idf in
each index. `pooled` has `average_idf` 7.6693 and floor 1.9173; the
ten-document index has `average_idf` 1.5954 and floor 0.3989.

| Query token | df pooled | idf pooled | df / 10 | idf per-question |
|---|---:|---:|---:|---:|
| `albee` | 5 | 6.7989 | 5 | **0.0000** (exactly half the index) |
| `playwright` | 19 | 5.5303 | 7 | 0.3989 (floored) |
| `edward` | 49 | 4.5927 | 9 | 0.3989 (floored) |
| `or` | 648 | 1.8893 | 2 | 1.2238 |
| `which` | 920 | 1.4735 | 2 | 1.2238 |
| `a` | 4,071 | 1.9173 (floored) | 8 | 0.3989 (floored) |
| `lived` | 25 | 5.2609 | 0 | 0 |
| `longer` | 18 | 5.5832 | 0 | 0 |
| `life,` | 19 | 5.5303 | 0 | 0 |
| `j.` | 59 | 4.4066 | 0 | 0 |
| `m.` | 32 | 5.0169 | 0 | 0 |
| `barrie?` | 0 | 0 | 0 | 0 |

Score decomposition of the two golds. Every non-listed query token contributes
0.000000 in both settings.

| Gold | Setting | Contributions | Total |
|---|---|---|---:|
| `Edward Albee` (64 tokens) | `pooled` | `albee` 7.842862, `playwright` 6.379566, `edward` 5.297903 | 19.520331 |
| `Edward Albee` | `per_question` | `playwright` 0.390815, `edward` 0.390815, `albee` **0.000000** | 0.781630 |
| `J. M. Barrie` (121 tokens) | `pooled` | `a` 3.264753, `or` 1.644111 | 4.908864 |
| `J. M. Barrie` | `per_question` | `or` 0.850018, `a` 0.604403 | 1.454420 |

Reading:

- The whole of the Albee gold's pooled score comes from three tokens that the
  ten-document index destroys. `albee` occurs in five of those ten paragraphs,
  which is exactly the point where the classic idf formula returns zero, so the
  unit's single strongest pooled cue becomes worth nothing. `playwright` and
  `edward` are both floored to the same 0.3989.
- The Barrie gold never matched its own name in either setting, for the
  name-form reason recorded above. Its entire score in both settings comes from
  the function words `a` and `or`. It "wins" the per-question comparison because
  `or` happens to occur in only two of the ten paragraphs and so keeps a
  comparatively high weight.
- Length normalization pushes the other way and is therefore not the cause:
  `avgdl` falls from 90.885 to 61.200, so the 121-token Barrie gold's
  normalization factor worsens from 1.2485 to 1.7328 while the 64-token Albee
  gold's improves from 0.7781 to 1.0343. Barrie still overtakes it.
- Consequently the per-question rank 6 must not be read as the Barrie biography
  being more retrievable in the smaller index. That ranking is produced by
  function words: the top-scoring paragraph, `Three Tall Women`, earns 1.7743 of
  its 2.9310 points from `which`, and `lived`, `longer`, and `life,` have
  document frequency 0 across all ten paragraphs.

The df collapse is not an accident of this item. HotpotQA supplies distractors
about the queried entities, so the per-question index is by construction the one
place where the question's own entity tokens are least discriminative.

Reproduction: build `BM25Okapi` over `text.lower().split()` of
`references/pooled_corpus_validation_500_title_text.jsonl` for `pooled`, and over
the ten paragraphs named in the stored `per_question` `retrieved_titles` for
`per_question`; score the verbatim question. C2 and C3 are the same
ten-paragraph model with `BM25Okapi.idf`, and then also `BM25Okapi.avgdl`,
overwritten from the pooled model. Both stored settings reproduce exactly, and
C3 reproduces C1 exactly. This reconstruction sits outside the 66-condition
battery of the sibling Dense unit `5a78b209554299148911f93e|dense`; that
dossier's provenance table and `not_run` list now point here.

## Worked case: `5a7d61775542991319bc93b9|bm25`

The query contains `of` four times, `commander-in-chief` twice, and `the`
twice. Exact score decomposition over the 4,937-paragraph pooled corpus
reproduces the exported scores and shows that repeated function words account
for large shares of several distractor scores. For example,
`Commander-in-Chief, India` receives 17.31 points from `of` and 8.65 from
`the`; `Siege of Bharatpur (1805)` receives 23.07 of its 41.85 points from
those two terms.

Punctuation and surface-form mismatches simultaneously suppress the golds:
`bharatpur,` does not match `bharatpur`, `commander-in-chief` does not match
`commander-in-chief,`, and `storming` does not match `stormed`. The displayed
event titles do not repair these mismatches because titles are not indexed.
The resulting primary candidate is `minimal_preprocessing_score_distortion`,
with event confusion and description-only bridge retrieval retained as
secondary difficulties rather than treated as effects of preprocessing alone.

## Provenance

Implementation locations in
`main-cs6120-hotpotqa-retrieval-failure-analysis`:

- `src/data_loader.py::_build_paragraphs`;
- `src/retrievers.py::_tokenize`;
- `src/retrievers.py::BM25Retriever`;
- `scripts/run_bm25_experiment.py::run_pooled_setting`;
- `scripts/run_bm25_experiment.py::run_per_question_setting`; and
- `requirements.txt`.

If any indexed field, tokenizer, preprocessing rule, BM25 parameter, corpus
construction rule, or dependency version changes, update this reference and
associate the change with a new run ID before reusing its conclusions.