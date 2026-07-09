"""
test_data_loader.py

Tests the parsing logic in data_loader.py using a small synthetic
HotpotQA-shaped example -- no network / dataset download needed, so this
runs fast and works offline.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import process_example, Paragraph


def make_fake_raw_example():
    """Builds a small dict that mimics the shape of a real HotpotQA example."""
    return {
        "id": "fake_001",
        "question": "Where was the founder of Company X born?",
        "answer": "Springfield",
        "type": "bridge",
        "level": "medium",
        "context": {
            "title": ["Company X", "Jane Doe", "Unrelated Topic"],
            "sentences": [
                ["Company X was founded in 1990.", "It makes widgets."],
                ["Jane Doe founded Company X.", "She was born in Springfield."],
                ["This is about something else entirely."],
            ],
        },
        "supporting_facts": {
            "title": ["Company X", "Jane Doe"],
            "sent_id": [0, 1],
        },
    }


def test_process_example_builds_correct_paragraphs():
    raw = make_fake_raw_example()
    example = process_example(raw)

    assert example.example_id == "fake_001"
    assert example.question_type == "bridge"
    assert len(example.paragraphs) == 3

    titles = [p.title for p in example.paragraphs]
    assert titles == ["Company X", "Jane Doe", "Unrelated Topic"]

    # Sentences should be joined into one text block per paragraph
    jane_doe_paragraph = example.paragraphs[1]
    assert "Jane Doe founded Company X." in jane_doe_paragraph.text
    assert "She was born in Springfield." in jane_doe_paragraph.text


def test_process_example_extracts_gold_titles():
    raw = make_fake_raw_example()
    example = process_example(raw)

    assert example.gold_titles == {"Company X", "Jane Doe"}
    # The distractor paragraph should NOT be in the gold set
    assert "Unrelated Topic" not in example.gold_titles


if __name__ == "__main__":
    test_process_example_builds_correct_paragraphs()
    test_process_example_extracts_gold_titles()
    print("All data_loader tests passed.")
