# Xin — Week 1 Completion Log

**Project:** When Multi-Hop Retrieval Fails: A Failure Analysis of BM25, Dense Retrieval, and Reranking on HotpotQA
**Owner:** Xin
**Scope:** Week 1 (7/7–7/13) — Dense retrieval prototype
**Status:** ✅ Complete

---

## 1. Goal for the week

Per the [weekly plan](../Plans/CS6120_Final_Project_Weekly_Todo_Plan.md), Xin's Week 1 job was to stand up the dense-retrieval side of the pipeline as a mirror of Jiajun's already-delivered BM25 side, and confirm it produces sensible top-k results on a small debug subset.

Full path to make work end-to-end:

```
HotpotQA example -> per-question paragraph corpus -> dense retriever -> top-k -> Any Evidence Recall@k
```

---

## 2. Starting point (what Jiajun had already delivered)

- `src/data_loader.py` — loads HotpotQA (`distractor` config), builds per-question `Paragraph(title, text)` list + gold evidence titles from `supporting_facts`.
- `src/retrievers.py` — `BM25Retriever` with `retrieve()` / `retrieve_titles()`, built **per question**.
- `src/evaluator.py` — Any Evidence Recall@k.
- `scripts/run_week1_debug.py` — BM25 end-to-end debug run.
- `tests/` — offline tests for data loader and evaluator.

Key interfaces reused as-is: `Paragraph`, `HotpotExample`, `load_examples()`, `evaluate_example()`, `aggregate_results()`.

---

## 3. What was built

### 3.1 `src/dense_retriever.py` — `DenseRetriever`

Embedding-based retriever, the semantic counterpart to BM25.

- **Interface parity:** exposes the exact same API as `BM25Retriever`
  (`__init__(paragraphs)`, `retrieve(query, top_k)`, `retrieve_titles(query, top_k)`),
  so it is a drop-in swap in any script and the two methods compare fairly.
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (per plan).
- **Corpus:** per-question, over that question's own ~10 context paragraphs
  (2 gold + ~8 distractors) — not all of Wikipedia. Matches BM25's setting.
- **Similarity:** cosine similarity, computed as a dot product of L2-normalized
  embeddings. Zero-norm rows are guarded to avoid divide-by-zero.
- **Testability:** an `encoder` callable can be injected. When `None`, the real
  SentenceTransformer model is built lazily on first use — so offline tests never
  download the model.

### 3.2 `tests/test_dense_retriever.py` — 3 offline unit tests (TDD)

Written **test-first** (red → green). A tiny deterministic bag-of-words fake
encoder is injected so cosine similarities are predictable and no model download
is needed.

- `test_retrieve_titles_ranks_most_similar_first` — most-similar paragraph ranked #1.
- `test_top_k_limits_number_of_results` — top_k truncation.
- `test_retrieve_returns_paragraph_score_tuples_descending` — returns `(Paragraph, float)` pairs sorted highest-first.

### 3.3 `scripts/run_week1_dense_debug.py` — dense + BM25 side-by-side debug run

Mirrors Jiajun's `run_week1_debug.py` but runs **both** retrievers on the same
examples so their top-k passages can be eyeballed together. Warms the embedding
model once and reuses the encoder across questions. Outputs per-example rows
(both methods' top-k titles + Any Evidence Recall@k) to
`results/week1_dense_debug_results.csv`.

### 3.4 Supporting changes

- `requirements.txt` — added `sentence-transformers>=2.7.0`.
- `README.md` — updated status line, project structure, added a "Running the dense
  debug script" section, and a BM25-vs-dense terminology bullet.

---

## 4. Verification

### 4.1 Environment

Created an isolated `venv/` (gitignored) and installed `requirements.txt`
(pulls in torch + sentence-transformers + datasets).

### 4.2 Tests

```
python -m pytest tests/ -q
9 passed
```

### 4.3 End-to-end run on 10 validation examples

```
python scripts/run_week1_dense_debug.py --n 10
```

Aggregate Any Evidence Recall@k on the 10-example debug subset:

| Method | Any Evidence Recall@2 | @5 | @10 |
|---|---:|---:|---:|
| BM25  | 0.700 | 1.000 | 1.000 |
| Dense | 1.000 | 1.000 | 1.000 |

### 4.4 Manual inspection (Week 1 checkpoint)

Dense top-k looks reasonable and, on this subset, already outperforms BM25 at k=2.
Concrete cases worth keeping for the Week 3 failure analysis:

- **Comparison — "Were Scott Derrickson and Ed Wood of the same nationality?"**
  BM25 top-1 is `Doctor Strange (2016 film)` (pulled in by lexical overlap with
  the director's filmography) and misses gold in top-2. Dense ranks `Ed Wood (film)`
  and `Ed Wood` at the top → gold hit @2. → clean **lexical-mismatch** example
  favoring dense.
- **Bridge — "…woman who portrayed Corliss Archer in the film Kiss and Tell?"**
  Dense ranks `Kiss and Tell (1945 film)` #1 (gold hit @2); BM25 misses gold @2.
- A third example: both methods hit — not every case separates them.

---

## 5. Week 1 checkpoint questions — all "yes"

- Can we load 10 HotpotQA examples? ✅
- Can we retrieve top-k with BM25? ✅ (Jiajun)
- Can we retrieve top-k with dense retrieval? ✅
- Can we compute basic Any Evidence Recall@k? ✅
- Can we inspect results manually? ✅

---

## 6. Files touched

| File | Type | Note |
|---|---|---|
| `src/dense_retriever.py` | new | DenseRetriever module |
| `tests/test_dense_retriever.py` | new | 3 offline unit tests |
| `scripts/run_week1_dense_debug.py` | new | dense + BM25 debug run |
| `results/week1_dense_debug_results.csv` | new (generated) | 10-example output |
| `requirements.txt` | modified | added sentence-transformers |
| `README.md` | modified | status / structure / run docs / terminology |

**Git status:** committed in `dabf607` ("Add dense retriever (all-MiniLM-L6-v2) for Week 1.") — this covers `src/dense_retriever.py`, `tests/test_dense_retriever.py`, `scripts/run_week1_dense_debug.py`, `results/week1_dense_debug_results.csv`, `requirements.txt`, `README.md`, plus a `.gitignore` update. A follow-up commit `665a03a` removed the accidentally-tracked `src/__pycache__/` byte-compiled files from git.

---

## 7. AI Usage This Week

Tool: **Claude Code** (autonomous coding agent), used in agent sessions during 7/7–7/13.

| Component | AI involvement | Policy category |
|---|---|---|
| `src/dense_retriever.py` | Generated by Claude Code (framework + implementation of the retriever class: encoding, cosine similarity, top-k ranking, lazy model loading, encoder injection) | Retriever plumbing around an off-the-shelf model — agent-allowed supporting infrastructure |
| `tests/test_dense_retriever.py` | Generated by Claude Code (test scaffolding + fake-encoder design) | Unit tests for utilities — agent-allowed |
| `scripts/run_week1_dense_debug.py` | Generated by Claude Code (debug/eval harness mirroring the BM25 script) | Evaluation harness — agent-allowed |
| `requirements.txt`, `README.md` updates | Generated by Claude Code | Scaffolding — agent-allowed |

Scope of generation: Claude Code produced the framework and implementations above; design constraints (interface parity with `BM25Retriever`, per-question corpus setting, model choice per the plan) came from the project plan and Xin's direction. All generated code was reviewed by Xin and falls on the agent-allowed side of the AI Usage Boundary (docs/Plans/CS6120_Final_Project_Weekly_Todo_Plan.md) — no core metric logic or failure-analysis rules were involved this week.

Explanation Test note: since these components are agent-generated, Xin must be able to explain `dense_retriever.py` (normalization, cosine-as-dot-product, the zero-norm guard, encoder injection) on demand before submission.

### 7.1 Docs-only agent session (7/13) — failure review pipeline design + plan sync

Tool: **Claude Code**. No code was written; all changes are design/plan documents.

| Work item | AI involvement | Policy category |
|---|---|---|
| `docs/specs/2026-07-12-failure-review-pipeline-design.md` | Agent reviewed the design and drafted 4 additions decided with Xin: annotations.csv import/restore in the HTML page, `git_commit` + `corpus_setting` in `config.json`, `annotator`/`annotated_at` columns in annotations.csv, matching §9 acceptance items | Design doc for plumbing (runner output layout, HTML review tooling) — agent-allowed; contains no metric logic or failure rules |
| `docs/Plans/Xin_Implementation_Plan.md` | Agent applied the F1 → F1a/F1b/F1c task split (per the design doc), updated F3/F5 dependencies and the task-pool pointer | Plan bookkeeping — agent-allowed |
| `docs/Plans/CS6120_Final_Project_Weekly_Todo_Plan.md` | Agent added Xin's failure-review-pipeline task line (marked personal tooling), the annotations.csv shared-contract note on the ~20-example validation task, two entries in the Week 3 expected-output tree, and a to-be-discussed marker beside Jiajun's "Export failure cases to CSV" (his task content unchanged) | Plan bookkeeping — agent-allowed |

The design decisions themselves (corpus-setting distinction, CSV-as-contract, holding the Jiajun-task change for discussion) came from review discussion between Xin and the agent; the agent drafted the wording, Xin reviewed the edits.

---

## 8. Handoff to Week 2 (Xin)

Per the plan, Week 2 turns the prototype into a real experiment:

- Add **embedding caching** — the current per-question re-embedding is fine for 10
  examples but becomes the bottleneck at 100/500. This is the main Week 2 dense task.
- Run dense on 100 examples, then 500 if runtime is acceptable.
- Save dense results to `results/dense_results.csv`.
- Start recording initial dense success/failure patterns.
