# When Multi-Hop Retrieval Fails: Retrieval Failure Analysis on HotpotQA

A controlled comparison of BM25 (lexical), dense (embedding-based), and cross-encoder reranked retrieval on HotpotQA, evaluated by whether each method recovers the **full** set of gold supporting evidence needed for multi-hop question answering -- not just "any" relevant passage.

Status -- **research and result artifacts are complete**: all three retrieval stages ran over the first 500 HotpotQA validation examples in both corpus settings, with Any/Full/Partial Evidence Recall and MRR reported, and the reranker rescue/damage analysis plus the v1 manual failure review (30 hand-labelled units, candidate taxonomy v0.1) are landed.

What the submission consists of, and where each item lives, is listed in [docs/submission_inventory.md](docs/submission_inventory.md).

The AI Usage Declaration and the per-member contribution statements are sections of the report; [docs/AI_Usage_Declaration.md](docs/AI_Usage_Declaration.md) is this repository's working copy of that disclosure.

## Setup

```bash
# from the project root
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Requires Python 3.10+. `datasets` will download HotpotQA from Hugging Face on first run (~600MB), and the dense retriever downloads `all-MiniLM-L6-v2` (~90MB), so the first run needs an internet connection; afterward both are cached locally.

## Demo

```bash
python demo.py
```

One command, needing neither a network connection nor a GPU: `demo.py` prints the project's finding from the result CSVs already in the checkout. Three sections -- the headline BM25 / dense / dense + rerank table, one question BM25 misses and dense finds with the top 5 titles each retrieved, and one question the reranker rescues alongside one it damages.

It is a presentation layer, so every number it prints is read from a cell of an accepted result file rather than recomputed: it defines no metric and runs no retrieval. Its contract is [docs/specs/2026-08-14-offline-demo.md](docs/specs/2026-08-14-offline-demo.md).

## Project structure

```text
cs6120-hotpotqa-retrieval-failure-analysis/
  demo.py                     # offline walkthrough of the accepted results (see Demo above)
  src/
    data_loader.py            # loads HotpotQA, builds per-question and pooled corpora + gold titles
    retrievers.py             # BM25Retriever (lexical baseline)
    dense_retriever.py        # DenseRetriever (embedding-based; all-MiniLM-L6-v2)
    cross_encoder_reranker.py # CrossEncoderReranker (ms-marco-MiniLM-L-6-v2)
    embedding_cache.py        # on-disk embedding cache for repeated dense runs
    evaluator.py              # ALL metric definitions: Any/Full/Partial Evidence Recall@k, reciprocal rank
    results_schema.py         # the shared long-format result CSV contract
    rank_pattern.py           # gold-rank pattern classification
    top50_export.py           # pooled dense top-50 shortlist export (the reranker's input)
  scripts/
    run_bm25_experiment.py    # formal BM25 run     -> results/bm25_results.csv
    run_dense_experiment.py   # formal dense run    -> results/dense_results.csv
    run_rerank_experiment.py  # formal rerank run   -> results/rerank_results.csv
    run_failure_review.py     # per-run failure-review record -> results/runs/<run_id>/
    build_failure_report.py   # run directory       -> failures_review.html
    build_manual_review_batch.py  # the v1 manual review workspace
    manual_review_page.py     # the shared static review page
    smoke_test_reranker.py    # hand-run online check that the real cross-encoder loads
    run_week1_debug.py        # early 10-example BM25 debug run
    run_week1_dense_debug.py  # early 10-example dense-vs-BM25 debug run
    reporting/                # post-run tables, shortlists, and figures -- see its own README
  tests/                      # offline test suite; no network needed
  docs/
    specs/                    # the frozen contracts every runner and tool cites
    manual_review_v1/         # the imported manual failure-review record
    taxonomy_candidate_v0_1.md
    AI_Usage_Declaration.md
  results/                    # formal result CSVs, annotations, and figures
  data/                       # cached/processed data artifacts, if any (gitignored)
```

## Running the formal experiments

Each runner writes one long-format CSV sharing the column set in [src/results_schema.py](src/results_schema.py), one row per `(method, setting, example)`, so the three files concatenate by `example_id`.

From a clean checkout, four commands produce all three method files in both corpus settings:

```bash
# BM25 and dense each write both settings in one run
python scripts/run_bm25_experiment.py --n 500
python scripts/run_dense_experiment.py --n 500 --top50-out results/dense_top50_pooled.csv

# the reranker writes one setting per run: pooled first, then per_question
python scripts/run_rerank_experiment.py --n 500 --setting pooled
python scripts/run_rerank_experiment.py --n 500 --setting per_question
```

The two **corpus settings** are:

- **pooled** -- one shared index over every question's paragraphs, merged and deduplicated. The realistic setting; stores the top 50 and fills @2/@5/@10.
- **per_question** -- each question retrieves over its own ~10 provided paragraphs. The contrast setting; stores up to 10 and fills @2/@5 only, because Recall@10 is trivially 1.0 over a ~10-paragraph corpus.

Which settings one command produces differs by runner, which is why there are four commands and not three:

- `run_bm25_experiment.py` always runs both settings and has no `--setting` flag.
- `run_dense_experiment.py` defaults to `--setting both`.
- `run_rerank_experiment.py` runs **one** setting per invocation. `--setting pooled` (its default) writes the pooled rows; a second invocation with `--setting per_question` appends the per_question rows onto that same CSV, copying the accepted pooled bytes verbatim rather than recomputing them. Pooled must therefore run first.

The reranker re-scores the pooled dense top-50 shortlist, so `run_dense_experiment.py` must run before it -- and the dense command needs the explicit `--top50-out` above, because that flag defaults to `None`. Without it the dense run writes `results/dense_results.csv` but no score-bearing shortlist, and the reranker's default `--top50-in results/dense_top50_pooled.csv` has nothing to read. Passing it builds the shortlist from the same pooled retrieval as the results CSV, so the two artifacts cannot disagree. `results/dense_top50_pooled.csv` is committed, so a fresh clone can rerun the reranker alone without repeating the dense run.

## Headline results

Pooled setting, 500 validation examples (`results/main_results_v1.csv`, generated by `scripts/reporting/summarize_results.py --main-table`):

| Method | Any Hit@5 | Full Hit@2 | Full Hit@5 | Full Hit@10 | Evidence Recall@5 | MRR@10 |
|---|---|---|---|---|---|---|
| BM25 | 0.874 | 0.140 | 0.302 | 0.500 | 0.588 | 0.751 |
| Dense | 0.962 | 0.244 | 0.502 | 0.664 | 0.732 | 0.869 |
| Dense + Rerank | 0.994 | 0.436 | 0.654 | 0.804 | 0.824 | 0.948 |

The gap between the "Any" and "Full" columns is the project's central observation. At k=5, dense retrieval finds *some* gold evidence for 96.2% of questions but the *complete* evidence chain for only 50.2%; reranking narrows that gap without closing it (99.4% vs 65.4%). A retriever that looks strong under the usual single-passage hit metric can still be missing half the evidence multi-hop QA needs.

## Reporting and analysis

Everything downstream of the result CSVs -- summary tables, BM25-vs-dense disagreement cases, the failure shortlist, the reranker rescue/damage analysis, and the slide figures -- lives in [scripts/reporting/](scripts/reporting/) and is indexed by [scripts/reporting/README.md](scripts/reporting/README.md).

Metric definitions are **not** in that directory. They live in [src/evaluator.py](src/evaluator.py) and are hand-written; the reporting tools only aggregate values that already exist.

## Failure review and manual annotation

`run_failure_review.py` writes a self-contained run directory rich enough to inspect a failure by hand (full paragraph text, precomputed gold ranks), and `build_failure_report.py` renders it as a single-file HTML page for annotation. Run directories are large and are not committed; `config.json` records the git commit, so any run is reproducible.

The v1 manual review labelled 30 `(example_id, retriever)` units against a candidate taxonomy. Its record, scope, and limits are documented in [docs/manual_review_v1/README.md](docs/manual_review_v1/README.md); the label vocabulary is [docs/taxonomy_candidate_v0_1.md](docs/taxonomy_candidate_v0_1.md), and the counts are re-derived from the shipped label file by `scripts/reporting/manual_review_category_counts.py` rather than copied by hand.

## Inspecting the original per-question corpus

The formal 500-example experiments use the first 500 rows of the HotpotQA
`validation` split, in dataset order; they are not a random sample. The project
loader exposes each question's original `context` as `example.paragraphs`, where
every paragraph has a `title` and the full paragraph `text` reconstructed from
that context's sentence list.

Look up an example by `example_id` (preferred because it is stable and unique),
then print all of its original candidate paragraphs:

```python
from src.data_loader import load_examples

examples = load_examples(split='validation', n=500)

target_id = '5a8b57f25542995d1e6f1371'
example = next(ex for ex in examples if ex.example_id == target_id)

print('Example ID:', example.example_id)
print('Question:', example.question)
print('Gold titles:', sorted(example.gold_titles))
print('Corpus size:', len(example.paragraphs))

for index, paragraph in enumerate(example.paragraphs, start=1):
    print(f'\n===== Corpus {index} =====')
    print('Title:', paragraph.title)
    print('Text:', paragraph.text)
```

If only the exact question text is known, replace the lookup with:

```python
target_question = 'Were Scott Derrickson and Ed Wood of the same nationality?'
example = next(ex for ex in examples if ex.question == target_question)
```

Use `len(example.paragraphs)` rather than assuming every question has exactly
10 candidates: the distractor configuration usually supplies 10, but some
examples contain fewer. On the first run, `load_examples` downloads HotpotQA;
later calls reuse the Hugging Face cache, so callers should not hard-code a
machine-specific cache path.

To inspect the untouched HotpotQA fields (including sentence boundaries and
supporting-fact sentence indices), use the raw loader instead:

```python
from src.data_loader import load_raw_hotpotqa

raw_examples = load_raw_hotpotqa(split='validation', n=500)
raw_example = next(row for row in raw_examples if row['id'] == target_id)

print(raw_example['context']['title'])
print(raw_example['context']['sentences'])
print(raw_example['supporting_facts'])
```

## Running tests

The whole suite is offline: no network, model download, or freshly generated
experiment output is required. Several accepted-data regression controls do read
the three formal result CSVs included in the checkout:
`results/bm25_results.csv`, `results/dense_results.csv`, and
`results/rerank_results.csv`.

```bash
venv/Scripts/python.exe -m pytest tests/    # Windows
python -m pytest tests/                     # elsewhere
```

A fresh clone reports `2470 passed, 78 skipped`. The 78 skips are expected and
self-declared: they belong to controls that read a complete failure-review run
directory, and run directories are too large to commit (see *Failure review and
manual annotation* above), so those tests skip themselves when the directory is
absent rather than fail.

Two environment notes, both Windows-only. Use the project virtual environment
explicitly; a system-wide Anaconda install can shadow imports and produce
failures unrelated to the code. And if the console code page is not UTF-8 --
cp936 on a Chinese Windows, for example -- set `PYTHONUTF8=1` before running.
One test deliberately feeds a full-width digit through a subprocess, and Python
decodes a child process's output with the ANSI code page, which cannot represent
that character; changing `chcp` alone does not help.

```bash
set PYTHONUTF8=1        # cmd
$env:PYTHONUTF8 = "1"   # PowerShell
export PYTHONUTF8=1     # bash
```

## Key terminology

- **BM25 vs dense vs rerank**: BM25 ranks paragraphs by lexical keyword overlap with the question; dense retrieval ranks by cosine similarity between sentence-embedding vectors (`all-MiniLM-L6-v2`) of the question and each paragraph; the reranker re-scores the dense top-50 with a cross-encoder (`ms-marco-MiniLM-L-6-v2`) that reads the question and paragraph jointly.
- **Any Evidence Recall@k** (reported as *Any Evidence Hit Rate*): whether at least one gold evidence paragraph appears in the top-k. A basic hit metric -- insufficient on its own for multi-hop QA, since it says nothing about whether *all* required evidence was found.
- **Full Evidence Recall@k** (reported as *Full Evidence Hit Rate*): whether **every** gold evidence paragraph appears in the top-k. This is the metric the project is actually about.
- **Partial Evidence Recall@k** (reported as *Evidence Recall@k*): the fraction of gold evidence paragraphs recovered in the top-k. Not a binary hit, which is why the binary-only reporting tools reject it.
- **MRR@k**: the dataset mean of the per-example reciprocal rank of the first gold paragraph. Stored per example as `reciprocal_rank_at_10` / `reciprocal_rank_at_50`; a bare `mrr` column deliberately does not exist in the CSVs.
- **Corpus settings**: *pooled* (one shared index over all questions' paragraphs) and *per_question* (each question's own ~10 context paragraphs, mixing gold evidence and distractors).
- **Gold evidence titles**: derived from HotpotQA's `supporting_facts`, matched by paragraph title.
- **Rescue / damage**: a question the reranker moved from a Full Evidence miss to a hit is a *rescue*; the reverse is *damage*. Reported per cutoff and per question type.

## Documentation map

- [docs/specs/](docs/specs/) -- the frozen contracts. A runner or reporting tool that a spec governs names that spec by repository path in its own docstring, so the authority behind a tool is readable from the tool. Four hand-run tools are governed by no spec and cite none: `run_week1_debug.py` and `run_week1_dense_debug.py`, the early debug runs; `smoke_test_reranker.py`, the hand-run online check; and `build_gold_matching_audit.py`, which renders a worksheet for a human to read and approve.
- [scripts/reporting/README.md](scripts/reporting/README.md) -- the reporting and audit tools.
- [docs/manual_review_v1/README.md](docs/manual_review_v1/README.md) -- the manual failure-review record and its scope limits.
- [docs/AI_Usage_Declaration.md](docs/AI_Usage_Declaration.md) -- which components are hand-written and which are agent-generated.
- [docs/submission_inventory.md](docs/submission_inventory.md) -- what the final submission consists of, where each item lives, and what is deliberately excluded from the archive.

## Team

- **Jiajun**: data loader, BM25 baseline, evaluator, experiment runner, README, demo.py support, packaging.
- **Xin**: dense retrieval, reranking, failure analysis, reporting tools.
- **Shared**: failure taxonomy, qualitative examples, report, slides.
