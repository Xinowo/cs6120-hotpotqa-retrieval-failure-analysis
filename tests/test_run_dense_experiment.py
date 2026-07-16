"""
test_run_dense_experiment.py

Offline tests for the dense runner (scripts/run_dense_experiment.py).
They exercise the schema-shaping logic -- column set/order, the K policy
(per_question fills @2/@5, leaves @10 empty), the 1/0 boolean encoding, and
the pooled guard -- WITHOUT downloading a model or HotpotQA: a tiny fake
encoder and hand-built HotpotExamples make retrieval deterministic, matching
the style of test_dense_retriever.py.

The runner only calls evaluator.py for the actual recall values, so these
tests check the plumbing (row shape / encoding), not the metric definition.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import numpy as np
import pandas as pd
import pytest

from src.data_loader import HotpotExample, Paragraph

import run_dense_experiment as runner


VOCAB = ["cat", "dog", "fish", "bird"]


def fake_encode(texts):
    """Deterministic bag-of-words encoder over VOCAB (same idea as the
    DenseRetriever tests) so top-k ordering is predictable and offline."""
    vecs = []
    for t in texts:
        tokens = t.lower().split()
        vecs.append([float(tokens.count(w)) for w in VOCAB])
    return np.array(vecs, dtype=np.float32)


def make_example(example_id, question, gold_titles, question_type="bridge", level="hard"):
    """A HotpotExample whose per-question corpus is four single-word
    paragraphs; the fake encoder ranks the paragraph matching `question`
    first, so we control exactly which gold titles land in the top-k."""
    paragraphs = [
        Paragraph(title="Cats", text="cat"),
        Paragraph(title="Dogs", text="dog"),
        Paragraph(title="Fishes", text="fish"),
        Paragraph(title="Birds", text="bird"),
    ]
    return HotpotExample(
        example_id=example_id,
        question=question,
        answer="",
        question_type=question_type,
        level=level,
        paragraphs=paragraphs,
        gold_titles=set(gold_titles),
    )


def test_columns_match_schema_order():
    ex = make_example("id1", "cat", {"Cats"})
    rows, _ = runner.run_per_question([ex], encoder=fake_encode)
    df = pd.DataFrame(rows, columns=runner.COLUMNS)

    assert list(df.columns) == [
        "method",
        "setting",
        "example_id",
        "question_type",
        "level",
        "question",
        "gold_titles",
        "retrieved_titles",
        "any_evidence_recall@2",
        "any_evidence_recall@5",
        "any_evidence_recall@10",
    ]


def test_per_question_fills_at2_at5_leaves_at10_empty():
    # "cat" ranks "Cats" first -> gold in top-1 -> hit at @2 and @5.
    ex = make_example("id1", "cat", {"Cats"})
    rows, _ = runner.run_per_question([ex], encoder=fake_encode)
    row = rows[0]

    assert row["method"] == "dense"
    assert row["setting"] == "per_question"
    assert row["any_evidence_recall@2"] == 1
    assert row["any_evidence_recall@5"] == 1
    # @10 is left uncomputed for per_question (K policy) -> None -> empty cell.
    assert row["any_evidence_recall@10"] is None


def test_booleans_are_ints_not_python_bools():
    # A miss: gold "Birds" is ranked last by "cat", so @2 must be 0, not False.
    ex = make_example("id_miss", "cat", {"Birds"})
    rows, _ = runner.run_per_question([ex], encoder=fake_encode)
    row = rows[0]

    assert row["any_evidence_recall@2"] == 0
    # Guard the schema's explicit choice: ints, never Python bools (which would
    # serialize as True/False strings and read back as truthy objects).
    assert type(row["any_evidence_recall@2"]) is int
    assert not isinstance(row["any_evidence_recall@2"], bool)


def test_csv_roundtrip_reads_back_int_and_nan(tmp_path):
    examples = [
        make_example("hit", "cat", {"Cats"}),
        make_example("miss", "cat", {"Birds"}),
    ]
    rows, _ = runner.run_per_question(examples, encoder=fake_encode)
    out = tmp_path / "dense_results.csv"
    pd.DataFrame(rows, columns=runner.COLUMNS).to_csv(out, index=False)

    back = pd.read_csv(out)
    # Filled columns read back as an integer dtype (mean() -> recall directly).
    assert back["any_evidence_recall@2"].tolist() == [1, 0]
    assert pd.api.types.is_integer_dtype(back["any_evidence_recall@2"])
    # The all-empty @10 column reads back as NaN, which mean() skips.
    assert back["any_evidence_recall@10"].isna().all()


def test_retrieved_and_gold_titles_use_pipe_separator():
    ex = make_example("id1", "cat", {"Cats", "Dogs"})
    rows, _ = runner.run_per_question([ex], encoder=fake_encode)
    row = rows[0]

    assert row["gold_titles"] == "Cats | Dogs"  # sorted, pipe-joined
    assert " | " in row["retrieved_titles"]
    # All four paragraphs are retrieved when k >= 4.
    assert len(row["retrieved_titles"].split(" | ")) == 4


def test_store_top_k_limits_retrieved_titles():
    ex = make_example("id1", "cat", {"Cats"})
    rows, _ = runner.run_per_question([ex], encoder=fake_encode, store_top_k=2)
    assert len(rows[0]["retrieved_titles"].split(" | ")) == 2


def test_pooled_setting_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        runner.main(n=1, split="validation", setting="pooled", k=10, out_path="unused.csv")


def test_main_rejects_k_smaller_than_max_metric_cutoff(monkeypatch):
    # per_question evaluates up to @5, so --k=3 must be rejected before any load.
    def _boom(*a, **k):
        raise AssertionError("load_examples must not be called when --k is invalid")

    monkeypatch.setattr(runner, "load_examples", _boom)
    with pytest.raises(ValueError):
        runner.main(n=1, split="validation", setting="per_question", k=3, out_path="unused.csv")
