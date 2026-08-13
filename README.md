# When Multi-Hop Retrieval Fails: Retrieval Failure Analysis on HotpotQA

A controlled comparison of BM25 (lexical) and dense (embedding-based) retrieval on HotpotQA, evaluated by whether each method recovers the full set of gold supporting evidence needed for multi-hop question answering -- not just "any" relevant passage.

Status: **Week 1 (data loader + BM25 + dense retrieval + Any Evidence Recall@k)**. Full/Partial Evidence Recall, MRR, and failure analysis are upcoming weeks.

## Setup

```bash
# from the project root
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Requires Python 3.10+. `datasets` will download HotpotQA from Hugging Face on first run (~600MB), so the first run needs an internet connection; afterward it's cached locally.

## Project structure

```text
hotpotqa-retrieval/
  requirements.txt
  README.md
  src/
    data_loader.py         # loads HotpotQA, builds per-question paragraph corpus + gold titles
    retrievers.py          # BM25Retriever (lexical baseline)
    dense_retriever.py     # DenseRetriever (embedding-based; all-MiniLM-L6-v2)
    evaluator.py           # Any Evidence Recall@k (Week 1); more metrics coming Week 2
  scripts/
    run_week1_debug.py         # end-to-end debug run: 10 examples -> BM25 -> metrics -> CSV
    run_week1_dense_debug.py   # end-to-end debug run: 10 examples -> dense + BM25 side by side -> metrics -> CSV
  tests/
    test_data_loader.py    # offline tests, no network needed
    test_evaluator.py      # offline tests, no network needed
    test_dense_retriever.py # offline tests (injected fake encoder), no network needed
  results/                # output CSVs land here (gitignored except .gitkeep)
  data/                   # cached/processed data artifacts, if any (gitignored)
```

## Running the Week 1 debug script

```bash
python scripts/run_week1_debug.py --n 10
```

This will:
1. Load 10 HotpotQA validation examples.
2. Build each question's paragraph-level retrieval corpus from its own `context`.
3. Run BM25 retrieval per question.
4. Compute Any Evidence Recall@2/5/10.
5. Print per-example results and save them to `results/week1_debug_results.csv`.

## Running the dense debug script

```bash
python scripts/run_week1_dense_debug.py --n 10
```

Same loop as above, but runs **dense retrieval and BM25 side by side** on the same examples so their top-k passages can be compared. It computes Any Evidence Recall@2/5/10 for both and saves per-example results (including both methods' top-k titles) to `results/week1_dense_debug_results.csv`.

The first run downloads the embedding model (`sentence-transformers/all-MiniLM-L6-v2`, ~90MB), so it needs network access once; afterward it's cached locally.

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

```bash
pytest tests/
```

or, without pytest installed:

```bash
python tests/test_data_loader.py
python tests/test_evaluator.py
```

## Key terminology

- **BM25 vs dense retrieval**: BM25 ranks paragraphs by lexical keyword overlap with the question; dense retrieval ranks by cosine similarity between sentence-embedding vectors (`all-MiniLM-L6-v2`) of the question and each paragraph. Both are built per question over that question's own ~10 context paragraphs, so the comparison is controlled.
- **Any Evidence Recall@k / Evidence Hit@k**: whether at least one mapped gold evidence paragraph appears in the top-k retrieved passages. A basic hit metric -- insufficient on its own for multi-hop QA, since it says nothing about whether *all* required evidence was found.
- **Retrieval corpus**: per HotpotQA question, the corpus is that question's own provided `context` paragraphs (~10, mixing gold evidence and distractors) -- not all of Wikipedia.
- **Gold evidence titles**: derived from HotpotQA's `supporting_facts`, matched by paragraph title.

## Team

- **Jiajun**: data loader, BM25 baseline, evaluator, experiment runner, README, demo.py support, packaging.
- **Xin**: dense retrieval, dense failure analysis.
- **Shared**: failure taxonomy, qualitative examples, report, slides.
