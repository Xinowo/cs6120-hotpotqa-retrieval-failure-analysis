"""
test_data_loader.py

Tests the parsing logic in data_loader.py using a small synthetic
HotpotQA-shaped example -- no network / dataset download needed, so this
runs fast and works offline.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datasets
import pytest

from src.data_loader import process_example, load_raw_hotpotqa, Paragraph


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


# ---------------------------------------------------------------------------
# trust_remote_code compatibility shim (load_raw_hotpotqa)
#
# These patch `datasets.load_dataset` so no network / real download happens.
# load_raw_hotpotqa does `from datasets import load_dataset` at call time, so
# it resolves the patched attribute off the datasets module each call.
# ---------------------------------------------------------------------------


class _FakeDS:
    """Minimal stand-in for a datasets.Dataset: just len + select, enough for
    load_raw_hotpotqa's n-slicing."""

    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def select(self, indices):
        return _FakeDS([self.rows[i] for i in indices])


def _install_fake_load_dataset(monkeypatch, behavior):
    """Replace datasets.load_dataset with a spy that records each call's kwargs
    and delegates the return/raise decision to `behavior(kwargs)`."""
    calls = []

    def fake_load_dataset(*args, **kwargs):
        calls.append(kwargs)
        return behavior(kwargs)

    monkeypatch.setattr(datasets, "load_dataset", fake_load_dataset)
    return calls


def test_modern_datasets_path_passes_no_trust_remote_code(monkeypatch):
    # Newer datasets: the plain call succeeds; the shim must NOT pass the arg.
    rows = [{"i": i} for i in range(5)]
    calls = _install_fake_load_dataset(monkeypatch, lambda kwargs: _FakeDS(rows))

    ds = load_raw_hotpotqa(split="validation")

    assert len(ds) == 5
    assert len(calls) == 1
    assert "trust_remote_code" not in calls[0]


def test_legacy_datasets_path_retries_with_trust_remote_code(monkeypatch):
    # Older datasets: the plain call raises asking for trust_remote_code; the
    # shim must retry WITH trust_remote_code=True and succeed.
    rows = [{"i": i} for i in range(3)]

    def behavior(kwargs):
        if "trust_remote_code" not in kwargs:
            raise ValueError(
                "Loading this dataset requires you to pass trust_remote_code=True"
            )
        return _FakeDS(rows)

    calls = _install_fake_load_dataset(monkeypatch, behavior)

    ds = load_raw_hotpotqa(split="validation")

    assert len(ds) == 3
    assert len(calls) == 2
    assert "trust_remote_code" not in calls[0]
    assert calls[1]["trust_remote_code"] is True


def test_unrelated_error_is_not_retried(monkeypatch):
    # A real error (e.g. bad split) must propagate immediately, not trigger the
    # trust_remote_code retry.
    def behavior(kwargs):
        raise ValueError("Unknown split 'nope'.")

    calls = _install_fake_load_dataset(monkeypatch, behavior)

    with pytest.raises(ValueError, match="Unknown split"):
        load_raw_hotpotqa(split="nope")

    assert len(calls) == 1  # no retry


def test_n_slicing_selects_first_n(monkeypatch):
    rows = [{"i": i} for i in range(10)]
    _install_fake_load_dataset(monkeypatch, lambda kwargs: _FakeDS(rows))

    ds = load_raw_hotpotqa(split="validation", n=4)

    assert [r["i"] for r in ds.rows] == [0, 1, 2, 3]


if __name__ == "__main__":
    test_process_example_builds_correct_paragraphs()
    test_process_example_extracts_gold_titles()
    print("All data_loader tests passed.")
