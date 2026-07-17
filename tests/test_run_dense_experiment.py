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
from src.results_schema import RESULT_COLUMNS


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

    assert list(df.columns) == RESULT_COLUMNS
    assert "mrr" not in df.columns
    assert df.columns[-2:].tolist() == [
        "reciprocal_rank_at_10",
        "reciprocal_rank_at_50",
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


def test_reciprocal_rank_horizons_distinguish_rank_11_to_50():
    ex = make_example("deep_hit", "cat", {"Gold"})
    titles = [f"Distractor {i}" for i in range(19)] + ["Gold"]

    row, metrics = runner.make_row(ex, titles, "pooled", store_top_k=50)

    assert row["reciprocal_rank_at_10"] == 0.0
    assert row["reciprocal_rank_at_50"] == 1 / 20
    assert metrics["reciprocal_rank_at_10"] == 0.0
    assert metrics["reciprocal_rank_at_50"] == 1 / 20


def make_pooled_corpus():
    """The shared pooled corpus for the offline pooled tests: four distinct
    single-word paragraphs (the same vocab the fake encoder ranks on), standing
    in for build_pooled_corpus's output so no model/data is needed."""
    return [
        Paragraph(title="Cats", text="cat"),
        Paragraph(title="Dogs", text="dog"),
        Paragraph(title="Fishes", text="fish"),
        Paragraph(title="Birds", text="bird"),
    ]


def test_pooled_fills_all_three_cutoffs():
    # The pooled K policy fills @2/@5/@10 (unlike per_question, which leaves
    # @10 empty). "cat" ranks "Cats" first, so the gold hits at every cutoff.
    ex = make_example("id1", "cat", {"Cats"})
    rows, _, _ = runner.run_pooled([ex], make_pooled_corpus(), encoder=fake_encode)
    row = rows[0]

    assert row["setting"] == "pooled"
    assert row["any_evidence_recall@2"] == 1
    assert row["any_evidence_recall@5"] == 1
    assert row["any_evidence_recall@10"] == 1  # computed, not left empty


def test_pooled_one_row_per_example_over_shared_index():
    # Every question is scored against the SAME shared corpus in one batch.
    examples = [
        make_example("q_cat", "cat", {"Cats"}),
        make_example("q_fish", "fish", {"Fishes"}),
    ]
    rows, per_example_metrics, _batches = runner.run_pooled(
        examples, make_pooled_corpus(), encoder=fake_encode
    )

    assert [r["example_id"] for r in rows] == ["q_cat", "q_fish"]
    assert len(per_example_metrics) == len(examples)
    # q_cat hits its gold at rank 1; q_fish hits its gold at rank 1 too.
    assert rows[0]["any_evidence_recall@2"] == 1
    assert rows[1]["any_evidence_recall@2"] == 1


def test_main_rejects_non_protocol_per_question_depth(monkeypatch):
    # Formal per_question output is locked to 10, so --k=3 is rejected early.
    def _boom(*a, **k):
        raise AssertionError("load_examples must not be called when --k is invalid")

    monkeypatch.setattr(runner, "load_examples", _boom)
    with pytest.raises(ValueError):
        runner.main(n=1, split="validation", setting="per_question", k=3, out_path="unused.csv")


def test_main_rejects_non_protocol_pooled_depth(monkeypatch):
    # Formal pooled output is locked to 50, so --k=10 is rejected early.
    def _boom(*a, **k):
        raise AssertionError("load_examples must not be called when --k is invalid")

    monkeypatch.setattr(runner, "load_examples", _boom)
    with pytest.raises(ValueError):
        runner.main(n=1, split="validation", setting="pooled", k=10, out_path="unused.csv")


def test_main_both_writes_both_settings_to_one_file(monkeypatch, tmp_path):
    examples = [make_example("q1", "cat", {"Cats"})]
    monkeypatch.setattr(runner, "load_examples", lambda **_kwargs: examples)
    monkeypatch.setattr(runner, "_warm_encoder", lambda _examples: fake_encode)
    monkeypatch.setattr(
        runner,
        "build_pooled_corpus",
        lambda _examples: (make_pooled_corpus(), []),
    )
    out = tmp_path / "dense_results.csv"

    runner.main(n=1, split="validation", setting="both", k=None, out_path=str(out))

    result = pd.read_csv(out)
    assert result["setting"].tolist() == ["pooled", "per_question"]
    assert result.columns.tolist() == RESULT_COLUMNS


def test_main_top50_out_writes_export_consistent_with_results(monkeypatch, tmp_path):
    """--top50-out writes the score-bearing export from the SAME pooled
    retrieval, so its schema, contiguous ranks, and per-question title order all
    match dense_results.csv's pooled rows."""
    from src.top50_export import TOP50_COLUMNS

    examples = [
        make_example("q_cat", "cat", {"Cats"}),
        make_example("q_fish", "fish", {"Fishes"}),
    ]
    monkeypatch.setattr(runner, "load_examples", lambda **_kwargs: examples)
    monkeypatch.setattr(runner, "_warm_encoder", lambda _examples: fake_encode)
    monkeypatch.setattr(
        runner, "build_pooled_corpus", lambda _examples: (make_pooled_corpus(), [])
    )
    out = tmp_path / "dense_results.csv"
    top50 = tmp_path / "dense_top50_pooled.csv"

    runner.main(
        n=2, split="validation", setting="both",
        k=None, out_path=str(out), top50_out=str(top50),
    )

    export = pd.read_csv(top50)
    assert export.columns.tolist() == TOP50_COLUMNS

    results = pd.read_csv(out)
    pooled = results[results.setting == "pooled"].set_index("example_id")
    for eid in ["q_cat", "q_fish"]:
        ex_rows = export[export.example_id == eid]
        # ranks are 1-based and contiguous within each example.
        assert ex_rows["rank"].tolist() == list(range(1, len(ex_rows) + 1))
        # export title order is identical to the results CSV's pooled row.
        assert ex_rows["title"].tolist() == pooled.loc[eid, "retrieved_titles"].split(" | ")


def test_main_top50_out_retrieves_pooled_index_exactly_once(monkeypatch, tmp_path):
    """The export must be built from the SAME pooled retrieval as the results
    CSV, never a second pass. Spy on the pooled retriever's retrieve_many and
    assert it fires exactly once even when --top50-out is set (a regression
    here would mean the export re-queried the index, risking tie-break drift)."""
    from src.dense_retriever import DenseRetriever

    calls = {"n": 0}
    original = DenseRetriever.retrieve_many

    def counting_retrieve_many(self, *args, **kwargs):
        calls["n"] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(DenseRetriever, "retrieve_many", counting_retrieve_many)

    examples = [
        make_example("q_cat", "cat", {"Cats"}),
        make_example("q_fish", "fish", {"Fishes"}),
    ]
    monkeypatch.setattr(runner, "load_examples", lambda **_kwargs: examples)
    monkeypatch.setattr(runner, "_warm_encoder", lambda _examples: fake_encode)
    monkeypatch.setattr(
        runner, "build_pooled_corpus", lambda _examples: (make_pooled_corpus(), [])
    )
    out = tmp_path / "dense_results.csv"
    top50 = tmp_path / "dense_top50_pooled.csv"

    runner.main(
        n=2, split="validation", setting="both",
        k=None, out_path=str(out), top50_out=str(top50),
    )

    # One batched pass over the shared pooled index, reused for both artifacts;
    # per_question uses retrieve_titles, so it does not add a retrieve_many call.
    assert calls["n"] == 1


def test_main_top50_out_requires_pooled(monkeypatch):
    # --top50-out is meaningless without pooled; reject before loading data.
    def _boom(*a, **k):
        raise AssertionError("load_examples must not run when --top50-out lacks pooled")

    monkeypatch.setattr(runner, "load_examples", _boom)
    with pytest.raises(ValueError):
        runner.main(
            n=1, split="validation", setting="per_question",
            k=None, out_path="unused.csv", top50_out="unused_top50.csv",
        )
