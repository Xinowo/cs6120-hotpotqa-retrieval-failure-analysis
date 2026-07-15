# CS6120 Final Project Idea Reference Document

## Diagnosing Multi-Hop Retrieval Failures in RAG on HotpotQA

Prepared as a reusable project-description document for future planning conversations.

Scope synchronization note, updated 2026-07-07:

This is an early idea reference. The final project scope has been narrowed to **BM25 vs dense retrieval, evidence coverage metrics, and failure analysis**. Reranking is now an optional extension only. *(Superseded on 2026-07-12: reranking is back in the core scope; see the 2026-07-12 note below.)* Full answer generation, query decomposition, hybrid retrieval, full Wikipedia retrieval, and chunking experiments are out of scope unless the core project is already complete.

Scope synchronization note, updated 2026-07-10:

Three further decisions are recorded in the Scope document:

1. **Corpus settings.** The primary experimental setting is now a **pooled corpus** built by merging all evaluation questions' context paragraphs (deduplicated by title). The original per-question distractor setting is kept only as a contrast condition, because with ~10 candidate paragraphs Recall@10 is trivially 100% and k = 5 is near ceiling.
2. **Optional extension priority.** The preferred optional extension is now **contrastive fine-tuning of the dense retriever** on HotpotQA train-split pairs, evaluated per failure category (which failures fine-tuning repairs, which persist). The reranker is demoted to a secondary optional extension; at most one extension is chosen at the Week 2 decision point. *(Superseded on 2026-07-12: the reranker is core, not an extension; fine-tuning is the sole optional extension.)* Per the course AI policy, fine-tuning code must be hand-written by team members.
3. **Taxonomy operationalization.** The failure categories must be assigned by explicit rule-based decision rules (including a disambiguation rule between first-hop-only and missing-bridge-entity failures), validated against manually labeled examples.

Sections below were updated on 2026-07-12 to reflect the current scope (reranking as the third core method); if anything still conflicts, the Scope document wins.

Scope synchronization note, updated 2026-07-12:

The submitted proposal (docs/Plans/proposal.md) commits to reranking in both its title and proposed solution. Reranking is therefore **restored to the core scope** as the third core method (off-the-shelf cross-encoder, e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`, no training; dense top-50 candidates in the pooled setting, all candidates in the per-question setting), with rescue/damage analysis as a core deliverable scheduled for Week 3. This supersedes the 2026-07-10 note's demotion of the reranker. Fine-tuning of the dense retriever remains the sole optional extension and must not compete with the reranker for time.

Consistency note: the **Scope document is the source of truth**. This Idea document provides background and reusable framing, while the Weekly Todo document is the execution plan. Metric naming, evidence matching, and failure taxonomy should follow the Scope document.

---

## 1. One-Sentence Summary

This project studies why retrieval systems fail in multi-hop question answering by comparing BM25 lexical retrieval, dense retrieval, and dense retrieval with cross-encoder reranking on HotpotQA, then diagnosing failures through evidence coverage metrics and a structured failure taxonomy.

---

## 2. Recommended Project Title

**Primary title (as submitted in the proposal):**

**When Multi-Hop Retrieval Fails: A Failure Analysis of BM25, Dense Retrieval, and Reranking on HotpotQA**

Alternative titles:

- Diagnosing Multi-Hop Retrieval Failures in RAG: A Controlled Study on HotpotQA
- Understanding Evidence Coverage Failures in Multi-Hop Retrieval-Augmented QA
- Retrieval Failure Analysis for Multi-Hop Question Answering

---

## 3. Motivation

Retrieval-Augmented Generation (RAG) systems often fail not because the language model cannot generate an answer, but because the retriever fails to recover all evidence required for the answer. This is especially important in multi-hop question answering, where a system may need to retrieve multiple supporting documents, connect a bridge entity, or compare facts across two entities.

The goal of this project is not simply to build a RAG system or maximize benchmark accuracy. The goal is to understand the behavior of different retrieval strategies and explain when they succeed or fail. This aligns with a broader interest in model behavior analysis, representation analysis, and systematic failure analysis.

---

## 4. Core Research Questions

1. When do BM25 and dense retrieval succeed or fail in retrieving HotpotQA supporting evidence?
2. Do retrievers fail differently on bridge questions versus comparison questions?
3. How often do systems retrieve only partial evidence, such as the first supporting document but not the second?
4. When does dense retrieval succeed where BM25 fails, and when does BM25 succeed where dense retrieval fails?
5. Which failure modes are caused by lexical mismatch, semantic drift, distractor entities, or comparison coverage gaps?
6. When does a reranker rescue missing evidence, and when does it damage retrieval by pushing gold evidence out of the top-k results?

---

## 5. Fit with CS6120 Final Project Expectations

This topic fits the CS6120 final project format because it has a clear NLP problem, a standard dataset, multiple methods, measurable results, and a scientific discussion centered on evidence retrieval failures. It can be framed as a combination of RAG evaluation and multi-hop question answering.

| Course requirement / expectation | How this project satisfies it |
|---|---|
| Problem and motivation | Multi-hop RAG systems can fail because retrieval misses necessary evidence, even when the answer generator is strong. |
| Prior work | RAG, BM25, dense passage retrieval, reranking, HotpotQA, multi-hop QA, evidence retrieval. |
| Methods | BM25 retriever, dense retriever, and dense retrieval with cross-encoder reranking (all three core, per the proposal). |
| Dataset | HotpotQA provides questions, answers, contexts, question types, difficulty levels, and gold supporting facts. |
| Results | Any Evidence Recall@k / Evidence Hit@k, MRR, Full Evidence Recall@k, and Partial Evidence Recall@k, grouped by question type, plus reranker rescue/damage rates. |
| Discussion | Failure taxonomy, qualitative examples, strengths and limitations of each retrieval method. |
| Code | Can be organized into data loader, retriever classes, evaluator, failure analyzer, and demo.py. |

---

## 6. Dataset: HotpotQA

HotpotQA is a Wikipedia-based multi-hop question answering dataset. Each example typically includes a natural language question, a short answer, multiple context documents or paragraphs, question type metadata, difficulty metadata, and gold supporting facts. The supporting facts make it suitable for retrieval evaluation because the project can directly measure whether the retriever recovered the required evidence.

| HotpotQA field | Meaning for this project |
|---|---|
| question | The user query to be passed to retrievers. |
| answer | The gold answer, useful context for manual inspection but not part of the core retrieval evaluation. |
| context | Candidate Wikipedia paragraphs or documents used as the retrieval corpus. |
| supporting_facts | Gold title + sentence-index annotations. Because this project retrieves paragraph-level passages, these annotations are mapped to gold evidence paragraphs by title. |
| type | Usually bridge or comparison; useful for controlled analysis. |
| level | Difficulty level; useful for subgroup analysis. |

Main HotpotQA question types:

- **Bridge questions:** require finding an intermediate entity before reaching the answer. These are useful for analyzing first-hop-only failures and missing bridge entities.
- **Comparison questions:** require retrieving facts about two entities and comparing them. These are useful for analyzing evidence coverage failures where only one side of the comparison is retrieved.

Evidence matching convention:

Because the project retrieves paragraph-level passages, HotpotQA `supporting_facts` title + sentence-index annotations should be mapped to gold evidence paragraphs. A retrieved passage counts as a gold evidence hit when its title matches a gold supporting-fact title, with optional verification that the paragraph contains the supporting sentence when sentence indices are available.

---

## 7. Recommended Scope

| Component | Recommended scope |
|---|---|
| Dataset size | Start with 10 examples for debugging, 100 for pipeline testing, 500 for the first real experiment, and 1000 only if runtime is acceptable. |
| Task focus | Evidence retrieval, not full answer generation. |
| Retrieval units | Paragraph-level passages from the provided HotpotQA contexts. |
| Methods | Core: BM25, dense retrieval, and dense retrieval with cross-encoder reranking, including reranker rescue/damage analysis. Optional: contrastive fine-tuning of the dense retriever. |
| Analysis | Quantitative metrics plus qualitative failure cases. |
| Deliverable emphasis | Scientific report with failure taxonomy, bridge-vs-comparison slices, and concrete test examples. |

---

## 8. Methodology

The project can be implemented as a retrieval-focused RAG diagnostic pipeline:

1. Load a subset of HotpotQA and construct a retrieval corpus from the provided context documents or paragraphs.
2. Normalize text minimally and preserve entity names, titles, and supporting fact structure.
3. Build a BM25 lexical retrieval baseline.
4. Build a dense retrieval baseline using a sentence embedding model.
5. Evaluate whether mapped gold evidence paragraphs appear in the retrieved top-k results.
6. Group results by question type and evidence coverage pattern.
7. Perform failure analysis using rule-based diagnosis plus manual inspection of representative examples.
8. Apply an off-the-shelf cross-encoder reranker to the top-N dense retrieval results (N = 50 pooled, all candidates per-question) and compare before/after ranking changes (rescue/damage analysis).

---

## 9. Proposed Metrics

| Metric | What it measures | Why it matters |
|---|---|---|
| Any Evidence Recall@k / Evidence Hit@k | Whether at least one mapped gold evidence paragraph appears in the top-k results. If abbreviated as Recall@k in tables, the report should explicitly define it this way. | Basic evidence hit metric, but insufficient for multi-hop QA by itself. |
| Full Evidence Recall@k | Whether all required mapped gold evidence paragraphs are retrieved within top-k. | Crucial for multi-hop QA because partial retrieval may still fail. |
| Partial Evidence Recall@k | Whether some, but not all, required mapped gold evidence paragraphs are retrieved within top-k. | Captures first-hop-only and incomplete comparison failures. |
| MRR | How highly the first mapped gold evidence paragraph is ranked. | Measures ranking quality, not just presence. |
| Reranker rescue rate | Cases where gold evidence is outside top-k before reranking but inside top-k after reranking. | Shows when reranking helps. |
| Reranker damage rate | Cases where gold evidence is inside top-k before reranking but pushed out after reranking. | Shows when reranking hurts evidence coverage. |
| Failure type distribution | How often each failure category occurs. | Turns raw errors into interpretable findings. |

---

## 10. Failure Taxonomy

| Failure mode | Description | Typical signal |
|---|---|---|
| First-hop-only failure | The retriever finds the document/entity explicitly mentioned in the question but misses the second supporting document. | Partial Evidence Recall@k but not Full Evidence Recall@k. |
| Missing bridge entity | The retrieved first-hop evidence contains or implies a bridge entity, but the system does not retrieve evidence about that bridge entity. | Bridge questions fail despite one relevant passage being retrieved. |
| Comparison coverage failure | A comparison question requires evidence for two entities, but retrieval covers only one. | One supporting entity appears, the other is missing. |
| Lexical mismatch | BM25 fails because the question and evidence use different surface forms. | Dense retrieval succeeds where BM25 fails. |
| Dense semantic drift | Dense retrieval retrieves semantically related but answer-irrelevant passages. | Dense top results look topically relevant but do not support the answer. |
| Distractor entity failure | The retriever retrieves a page or passage with a similar name or topic but not the gold evidence. | High lexical/entity overlap with wrong passage. |
| Reranker rescue | Reranking improves evidence ranking and moves gold evidence into top-k. | Gold evidence appears after reranking but not before. |
| Reranker damage | Reranking over-prioritizes local relevance and pushes necessary evidence out of top-k. | Gold evidence appears before reranking but disappears after reranking. |

---

## 11. Experiment Plan

Core experiment plan:

- Run BM25, dense retrieval, and dense + reranking on the same HotpotQA subset.
- Compute Any Evidence Recall@k / Evidence Hit@k, MRR, Full Evidence Recall@k, and Partial Evidence Recall@k for k = 2, 5, and 10.
- Compare results overall and by HotpotQA question type: bridge vs comparison.
- Identify examples where methods disagree, such as BM25 succeeds but dense fails, dense succeeds but BM25 fails, both partially succeed, or both fail.
- Analyze reranker rescue and damage cases.
- Manually inspect representative cases and assign failure types using the taxonomy.

Optional extension plan, decided at the Week 4 decision point (after the 7/28 final presentation), only if the core project is stable:

- Contrastively fine-tune the dense retriever on HotpotQA train-split pairs and evaluate per failure category.

Current project dates:

- Scope sync date: 2026-07-12.
- Final presentation (slides due): 2026-07-28.
- Full submission deadline: 2026-08-14.

---

## 12. Expected Findings / Hypotheses

- BM25 may perform well when exact entity names or titles appear in the question and supporting documents.
- Dense retrieval may perform better when the question paraphrases the evidence or uses semantically related wording.
- Dense retrieval may also suffer from semantic drift by retrieving passages that are topically related but not actually evidential.
- Reranking may improve local relevance but can hurt multi-hop evidence coverage if it favors one strong passage over a complete set of supporting passages.
- Comparison questions may be especially vulnerable to partial retrieval, because retrieving evidence for only one entity is insufficient.
- Bridge questions may reveal first-hop-only failures where the system retrieves the explicit entity but fails to retrieve the bridge target.

---

## 13. Recommended demo.py Design

The demo should not merely output a final answer. It should demonstrate the project's diagnostic goal: retrieve evidence using multiple methods, compare results against gold supporting facts when available, and produce a simple failure diagnosis.

| Demo mode | Behavior |
|---|---|
| Predefined mode | Runs selected HotpotQA examples that illustrate typical outcomes: BM25 success, dense success, BM25 succeeds but dense fails, dense succeeds but BM25 fails, first-hop-only failure, comparison coverage failure, reranker rescue, and reranker damage. |
| Interactive mode | Accepts a user-provided question. If the question matches a demo subset example, show gold evidence and metrics; otherwise, show retrieved passages without gold evaluation. |

Example command-line interface:

```bash
python demo.py --mode predefined
python demo.py --mode predefined --example_id 2 --top_k 5
python demo.py --mode interactive --retriever compare --top_k 5
```

Recommended demo output sections:

- Question
- Gold answer and gold supporting facts, if available
- Top-k retrieved passages from BM25, dense retrieval, and dense + reranking
- Per-example metrics such as Any Evidence Recall@k and Full Evidence Recall@k
- Failure diagnosis using the taxonomy

---

## 14. Suggested Code Structure

```text
project/
  demo.py
  src/
    data_loader.py
    retrievers.py
    evaluator.py
    failure_analyzer.py
    utils.py
  tests/
    test_data_loader.py
    test_retrievers.py
    test_evaluator.py
  data/
    demo_examples.json
    processed_corpus.pkl
    bm25_index.pkl
    dense_embeddings.npy
```

Suggested classes:

- `HotpotQADataLoader`: loads and preprocesses HotpotQA examples and corpus passages.
- `BM25Retriever`: implements lexical retrieval.
- `DenseRetriever`: implements embedding-based retrieval.
- `RerankerRetriever`: reranks dense top-N candidates with an off-the-shelf cross-encoder and computes rescue/damage cases.
- `RetrievalEvaluator`: computes Any Evidence Recall@k / Evidence Hit@k, MRR, Full Evidence Recall@k, and Partial Evidence Recall@k.
- `FailureAnalyzer`: assigns rule-based diagnostic labels to retrieval outcomes.

---

## 15. Possible Team Division

| Role | Responsibilities |
|---|---|
| Xin | Dense retrieval, dense retrieval experiments, dense failure analysis, semantic drift examples, bridge-vs-comparison analysis, and report discussion. |
| Teammate | HotpotQA data loader, BM25 baseline, evaluator, experiment runner, code packaging, README, and demo support. |
| Shared | Final failure taxonomy, qualitative example selection, presentation slides, final report editing, code explanation test, and AI usage declaration. |

---

## 16. Short Pitch for Teammates or Instructor

We propose to study retrieval failure modes in multi-hop question answering using HotpotQA. Instead of focusing only on end-to-end answer accuracy, we compare BM25, dense retrieval, and dense retrieval with cross-encoder reranking to understand when each method succeeds or fails to retrieve the required supporting evidence. Because HotpotQA provides gold supporting facts, we can evaluate retrieval without manually labeling evidence. Our main contribution will be a diagnostic analysis of multi-hop retrieval failures, including first-hop-only failures, missing bridge entities, distractor entity failures, lexical mismatch, semantic drift, comparison coverage failures, and reranker rescue/damage cases. If time allows, we will additionally fine-tune the dense retriever on HotpotQA training pairs and analyze which failure categories fine-tuning repairs. The final report will combine quantitative metrics with qualitative test-set examples to explain the inductive biases and limitations of different retrieval strategies.

---

## 17. Risks and Scope Control

| Risk | Mitigation |
|---|---|
| The project becomes a generic baseline comparison. | Emphasize failure taxonomy, controlled analysis, and example-level diagnosis. |
| Full answer generation becomes too time-consuming. | Keep answer generation out of scope and focus on evidence retrieval. |
| Reranker or dense retrieval is slow. | Use a manageable subset, cache embeddings/results, and if needed reduce the pooled reranking candidate depth (e.g. N = 20); the reranker itself is core and cannot be cut. |
| Failure analysis becomes too subjective. | Use rule-based diagnostic categories first, then manually inspect representative examples. |
| Too many experiments. | Prioritize BM25, dense retrieval, evidence coverage metrics, and question-type analysis. |

---

## 18. Why This Topic Still Has Value

The topic remains valuable because modern RAG systems still struggle with multi-hop retrieval and evidence coverage. The research value is not in showing that BM25 or dense retrieval can be run on HotpotQA; the value is in diagnosing why different retrieval strategies fail under different reasoning patterns. This is especially relevant when AI tools can help with implementation: the expected contribution should shift from coding a basic pipeline to designing a clear evaluation, analyzing errors, and producing scientific findings.

In future work, the same diagnostic framework could be transferred to scientific papers, interpretability literature, enterprise knowledge bases, industrial part search, or agentic RAG systems.

---

## 19. Keywords

RAG; retrieval-augmented generation; HotpotQA; multi-hop question answering; BM25; dense retrieval; reranking; evidence retrieval; failure analysis; model behavior analysis; representation analysis; semantic drift; evidence coverage; retrieval diagnostics.
