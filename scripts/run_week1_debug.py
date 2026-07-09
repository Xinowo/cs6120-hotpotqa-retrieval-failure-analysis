"""
run_week1_debug.py

Week 1 goal: run the full path end-to-end on a small debug subset and see
real retrieval outputs.

    HotpotQA example -> paragraph corpus -> BM25 -> top-k results -> Any Evidence Recall@k

Usage:
    python scripts/run_week1_debug.py
    python scripts/run_week1_debug.py --n 10 --split validation
"""

import argparse
import sys
import os

# Allow running this script directly (python scripts/run_week1_debug.py)
# from the project root without installing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.data_loader import load_examples
from src.retrievers import BM25Retriever
from src.evaluator import evaluate_example, aggregate_results


def main(n: int, split: str, top_k_max: int, out_path: str):
    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    k_values = [2, 5, 10]
    rows = []
    per_example_metrics = []

    for ex in examples:
        retriever = BM25Retriever(ex.paragraphs)
        retrieved_titles = retriever.retrieve_titles(ex.question, top_k=top_k_max)

        metrics = evaluate_example(retrieved_titles, ex.gold_titles, k_values=k_values)
        per_example_metrics.append(metrics)

        row = {
            "example_id": ex.example_id,
            "question": ex.question,
            "question_type": ex.question_type,
            "gold_titles": " | ".join(sorted(ex.gold_titles)),
            "bm25_top_k_titles": " | ".join(retrieved_titles),
        }
        row.update(metrics)
        rows.append(row)

        # Print a quick human-readable inspection line per example
        hit5 = metrics["any_evidence_recall@5"]
        print(f"[{ex.example_id}] type={ex.question_type} any_evidence_recall@5={hit5}")

    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    print(f"\nSaved per-example results to {out_path}")

    overall = aggregate_results(per_example_metrics)
    print("\nOverall BM25 Any Evidence Recall@k (this debug subset):")
    for metric, value in overall.items():
        print(f"  {metric}: {value:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 1 debug run: data loader + BM25 + Any Evidence Recall@k")
    parser.add_argument("--n", type=int, default=10, help="Number of examples to load")
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split to use")
    parser.add_argument("--top_k_max", type=int, default=10, help="Max top-k to retrieve (should cover the largest k you evaluate)")
    parser.add_argument("--out", type=str, default="results/week1_debug_results.csv", help="Output CSV path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    main(n=args.n, split=args.split, top_k_max=args.top_k_max, out_path=args.out)
