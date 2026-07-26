"""
smoke_test_reranker.py

A hand-run sanity check that the REAL cross-encoder model
(cross-encoder/ms-marco-MiniLM-L-6-v2) loads and scores query/passage
relevance in the right direction. This is the online counterpart of the
offline test_cross_encoder_reranker.py: those tests inject a fake scorer and
never touch the model; this script builds CrossEncoderReranker with no injected
scorer, so it exercises the lazily-loaded real model end to end.

What it checks (not a metric, just a direction): for a handful of queries, each
paired with one clearly relevant passage and a couple of clearly off-topic
distractors, the reranker must rank the relevant passage first AND score it
strictly above every distractor. The candidate lists are deliberately given
with the relevant passage NOT first, so a passing run also proves the reranker
actually reorders by model score.

Usage:
    python scripts/smoke_test_reranker.py

Note: the first run downloads the cross-encoder model (~90MB), so it needs
network access once; it is cached locally afterward. Exits non-zero if any
case comes out in the wrong order, so a failing model/direction is loud.
"""

import argparse
import sys
import os

# Allow running this script directly from the project root without
# installing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import Paragraph
from src.cross_encoder_reranker import CrossEncoderReranker, DEFAULT_MODEL_NAME


# Each case: a query, the title of the passage that should win, and a candidate
# shortlist (relevant passage placed NOT first, so a correct rerank must move
# it up). Passages are self-contained; the check is topical relevance, not
# HotpotQA gold correctness.
CASES = [
    {
        "query": "Where is the Eiffel Tower located?",
        "expected_title": "Eiffel Tower",
        "candidates": [
            Paragraph(
                title="Blue whale",
                text="The blue whale is a marine mammal and the largest animal "
                "known to have ever existed.",
            ),
            Paragraph(
                title="Eiffel Tower",
                text="The Eiffel Tower is a wrought-iron lattice tower on the "
                "Champ de Mars in Paris, France.",
            ),
            Paragraph(
                title="Photosynthesis",
                text="Photosynthesis is the process by which green plants convert "
                "sunlight into chemical energy stored in sugars.",
            ),
        ],
    },
    {
        "query": "Who wrote the play Romeo and Juliet?",
        "expected_title": "Romeo and Juliet",
        "candidates": [
            Paragraph(
                title="Mitochondrion",
                text="The mitochondrion is a double-membrane-bound organelle "
                "found in most eukaryotic cells.",
            ),
            Paragraph(
                title="Mount Everest",
                text="Mount Everest is Earth's highest mountain above sea level, "
                "located in the Himalayas.",
            ),
            Paragraph(
                title="Romeo and Juliet",
                text="Romeo and Juliet is a tragedy written by William "
                "Shakespeare early in his career.",
            ),
        ],
    },
    {
        "query": "What is the capital of the country where the Colosseum is located?",
        "expected_title": "Rome",
        "candidates": [
            Paragraph(
                title="Great Barrier Reef",
                text="The Great Barrier Reef is the world's largest coral reef "
                "system, off the coast of Queensland, Australia.",
            ),
            Paragraph(
                title="Rome",
                text="Rome is the capital city of Italy; the Colosseum is an "
                "ancient amphitheatre in the centre of Rome.",
            ),
            Paragraph(
                title="Basketball",
                text="Basketball is a team sport in which two teams shoot a ball "
                "through a hoop to score points.",
            ),
        ],
    },
]


def main(model_name: str) -> int:
    print(f"Loading cross-encoder '{model_name}' (first run downloads ~90MB)...")
    reranker = CrossEncoderReranker(model_name=model_name)

    all_passed = True
    for case in CASES:
        query = case["query"]
        expected = case["expected_title"]
        candidates = case["candidates"]

        ranked = reranker.rerank(query, candidates, top_k=len(candidates))
        scores_by_title = {p.title: score for p, score in ranked}

        top_title = ranked[0][0].title
        relevant_score = scores_by_title[expected]
        distractor_scores = [
            score for title, score in scores_by_title.items() if title != expected
        ]
        # PASS = relevant passage ranks first AND outscores every distractor.
        case_passed = top_title == expected and all(
            relevant_score > d for d in distractor_scores
        )
        all_passed = all_passed and case_passed

        print(f"\nQuery: {query}")
        print(f"  incoming order: {[p.title for p in candidates]}")
        print("  reranked:")
        for rank, (paragraph, score) in enumerate(ranked, start=1):
            marker = " <- expected relevant" if paragraph.title == expected else ""
            print(f"    {rank}. {paragraph.title:<22} score={score:+.3f}{marker}")
        print(f"  => {'PASS' if case_passed else 'FAIL'} "
              f"(top='{top_title}', expected='{expected}')")

    print("\n" + ("=" * 48))
    if all_passed:
        print("SMOKE TEST PASSED: relevant passages outscore distractors.")
        return 0
    print("SMOKE TEST FAILED: at least one case ranked in the wrong order.")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cross-encoder reranker smoke test: real model ranks "
        "relevant passages above off-topic distractors."
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=DEFAULT_MODEL_NAME,
        help="Cross-encoder model to load (default: the project reranker model)",
    )
    args = parser.parse_args()

    sys.exit(main(model_name=args.model_name))
