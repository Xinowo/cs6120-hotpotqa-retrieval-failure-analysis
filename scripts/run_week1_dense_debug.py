"""
run_week1_dense_debug.py

Xin's Week 1 end-to-end debug run for DENSE retrieval, mirroring Jiajun's
run_week1_debug.py (BM25). It runs dense retrieval AND BM25 on the same
small subset so their top-k passages can be eyeballed side by side:

    HotpotQA example -> paragraph corpus -> {dense, BM25} -> top-k -> Any Evidence Recall@k

The two retrievers share an identical interface, so this is just BM25's
debug loop with a DenseRetriever added alongside.

Usage:
    python scripts/run_week1_dense_debug.py
    python scripts/run_week1_dense_debug.py --n 10 --split validation

Note: the first run downloads the embedding model
(sentence-transformers/all-MiniLM-L6-v2, ~90MB) and HotpotQA, so it needs
network access once; both are cached locally afterward.
"""

import argparse
import sys
import os

# Allow running this script directly from the project root without
# installing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.data_loader import load_examples
from src.retrievers import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.evaluator import evaluate_example, aggregate_results


def main(n: int, split: str, top_k_max: int, out_path: str):
    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    print("Building dense encoder (first run downloads all-MiniLM-L6-v2)...")
    # Build one DenseRetriever up front just to warm the model, then reuse
    # its encoder across questions so we don't reload the model each time.
    # (Per-question corpora are still re-embedded, per Week 1 scope.)
    shared_encoder = None
    if examples:
        warm = DenseRetriever(examples[0].paragraphs)
        shared_encoder = warm._encoder

    k_values = [2, 5, 10]
    rows = []
    dense_metrics_all = []
    bm25_metrics_all = []

    for ex in examples:
        bm25 = BM25Retriever(ex.paragraphs)
        dense = DenseRetriever(ex.paragraphs, encoder=shared_encoder)

        bm25_titles = bm25.retrieve_titles(ex.question, top_k=top_k_max)
        dense_titles = dense.retrieve_titles(ex.question, top_k=top_k_max)

        bm25_metrics = evaluate_example(bm25_titles, ex.gold_titles, k_values=k_values)
        dense_metrics = evaluate_example(dense_titles, ex.gold_titles, k_values=k_values)
        bm25_metrics_all.append(bm25_metrics)
        dense_metrics_all.append(dense_metrics)

        row = {
            "example_id": ex.example_id,
            "question": ex.question,
            "question_type": ex.question_type,
            "gold_titles": " | ".join(sorted(ex.gold_titles)),
            "bm25_top_k_titles": " | ".join(bm25_titles),
            "dense_top_k_titles": " | ".join(dense_titles),
        }
        row.update({f"bm25_{m}": v for m, v in bm25_metrics.items()})
        row.update({f"dense_{m}": v for m, v in dense_metrics.items()})
        rows.append(row)

        # Human-readable inspection line per example.
        print(
            f"[{ex.example_id}] type={ex.question_type} "
            f"bm25_any@5={bm25_metrics['any_evidence_recall@5']} "
            f"dense_any@5={dense_metrics['any_evidence_recall@5']}"
        )

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nSaved per-example results to {out_path}")

    print("\nOverall BM25 Any Evidence Recall@k (this debug subset):")
    for metric, value in aggregate_results(bm25_metrics_all).items():
        print(f"  {metric}: {value:.3f}")

    print("\nOverall DENSE Any Evidence Recall@k (this debug subset):")
    for metric, value in aggregate_results(dense_metrics_all).items():
        print(f"  {metric}: {value:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Week 1 dense debug run: data loader + dense (and BM25) + Any Evidence Recall@k"
    )
    parser.add_argument("--n", type=int, default=10, help="Number of examples to load")
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split to use")
    parser.add_argument("--top_k_max", type=int, default=10, help="Max top-k to retrieve (should cover the largest k you evaluate)")
    parser.add_argument("--out", type=str, default="results/week1_dense_debug_results.csv", help="Output CSV path")
    args = parser.parse_args()

    main(n=args.n, split=args.split, top_k_max=args.top_k_max, out_path=args.out)
