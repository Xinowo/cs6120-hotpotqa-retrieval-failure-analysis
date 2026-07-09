# When Multi-Hop Retrieval Fails: Retrieval Failure Analysis on HotpotQA

A controlled comparison of BM25 (lexical) and dense (embedding-based) retrieval on HotpotQA, evaluated by whether each method recovers the full set of gold supporting evidence needed for multi-hop question answering -- not just "any" relevant passage.

Status: **Week 1 (data loader + BM25 + Any Evidence Recall@k)**. Dense retrieval, Full/Partial Evidence Recall, MRR, and failure analysis are upcoming weeks.

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
    data_loader.py      # loads HotpotQA, builds per-question paragraph corpus + gold titles
    retrievers.py        # BM25Retriever (Xin's dense_retriever.py will live here too)
    evaluator.py          # Any Evidence Recall@k (Week 1); more metrics coming Week 2
  scripts/
    run_week1_debug.py   # end-to-end debug run: 10 examples -> BM25 -> metrics -> CSV
  tests/
    test_data_loader.py  # offline tests, no network needed
    test_evaluator.py    # offline tests, no network needed
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

- **Any Evidence Recall@k / Evidence Hit@k**: whether at least one mapped gold evidence paragraph appears in the top-k retrieved passages. A basic hit metric -- insufficient on its own for multi-hop QA, since it says nothing about whether *all* required evidence was found.
- **Retrieval corpus**: per HotpotQA question, the corpus is that question's own provided `context` paragraphs (~10, mixing gold evidence and distractors) -- not all of Wikipedia.
- **Gold evidence titles**: derived from HotpotQA's `supporting_facts`, matched by paragraph title.

## Team

- **Jiajun**: data loader, BM25 baseline, evaluator, experiment runner, README, demo.py support, packaging.
- **Xin**: dense retrieval, dense failure analysis.
- **Shared**: failure taxonomy, qualitative examples, report, slides.
