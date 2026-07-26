"""
test_run_rerank_experiment.py

Offline tests for the reranker runner (scripts/run_rerank_experiment.py).
They exercise the NEW plumbing this runner adds -- reading the dense top-50
export, grouping candidates by example with contiguous ranks, enforcing the
exact pooled input depth and exact evaluation-set IDs, joining each
(example_id, title) back to the pooled corpus for text, feeding that shortlist
through the reranker, and shaping the result into the frozen RESULT_COLUMNS
schema -- WITHOUT downloading the cross-encoder model or HotpotQA.

The reranker's own scoring/sorting lives in the cross-encoder reranker class and
is tested in test_cross_encoder_reranker.py; here we inject a tiny deterministic
word-overlap scorer (the same one those tests use) so a real rerank happens
offline, and we check the runner's join/schema/depth/coverage/rank-continuity
plumbing around it.

Each malformed-input guard is tested against a legal control that differs only
in the property under test (a paired legal/adversarial matrix), so a regression
that loosens a guard is caught.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import pandas as pd
import pytest

from src.cross_encoder_reranker import CrossEncoderReranker
from src.data_loader import HotpotExample, Paragraph
from src.results_schema import RESULT_COLUMNS, STORE_DEPTH_BY_SETTING
from src.top50_export import TOP50_COLUMNS

import run_rerank_experiment as runner

POOLED_DEPTH = STORE_DEPTH_BY_SETTING["pooled"]  # 50


def fake_score(pairs):
    """Deterministic relevance scorer: count how many query words appear in the
    passage (with multiplicity). Same fake used in test_cross_encoder_reranker,
    so a passage sharing more query terms reranks higher -- fully offline."""
    scores = []
    for query, text in pairs:
        query_words = set(query.lower().split())
        passage_tokens = text.lower().split()
        scores.append(float(sum(1 for tok in passage_tokens if tok in query_words)))
    return scores


def make_reranker():
    return CrossEncoderReranker(scorer=fake_score)


# A small shared pooled corpus (title -> text) for the shaping/ordering unit
# tests. "Cats" is the most relevant passage for the query "cat"; "CatDog"
# shares one term; the rest share none. These tests pass store_top_k=4 to match
# this 4-candidate shortlist (the formal pooled depth of 50 is exercised by the
# deep fixtures below and the main() end-to-end test).
POOLED = [
    Paragraph(title="Dogs", text="dog dog dog"),
    Paragraph(title="Cats", text="cat cat cat"),
    Paragraph(title="CatDog", text="cat dog"),
    Paragraph(title="Birds", text="bird bird"),
]
TEXT_BY_TITLE = {p.title: p.text for p in POOLED}


# A full-depth (exactly 50) pooled corpus for depth/coverage/main tests: "Gold"
# (text "gold") is the single passage relevant to query "gold"; the other 49 are
# distinct distractors sharing no query word.
DEEP_CORPUS = [Paragraph(title="Gold", text="gold")] + [
    Paragraph(title=f"D{i}", text=f"d{i}") for i in range(POOLED_DEPTH - 1)
]
DEEP_TEXT = {p.title: p.text for p in DEEP_CORPUS}


def deep_top50_rows(example_id, depth=POOLED_DEPTH):
    """`depth` top-50 triples for `example_id`, ranks 1..depth, with "Gold"
    placed LAST so a correct rerank must promote it to rank 1. Distractor titles
    are drawn from DEEP_CORPUS so every candidate joins to real corpus text."""
    titles = [f"D{i}" for i in range(depth - 1)] + ["Gold"]
    return [(example_id, rank, title) for rank, title in enumerate(titles, start=1)]


def make_example(example_id, question, gold_titles, question_type="bridge", level="hard"):
    """A HotpotExample; per-question paragraphs are irrelevant in the pooled
    reranker path (candidates come from the top-50 CSV), so they are left
    empty."""
    return HotpotExample(
        example_id=example_id,
        question=question,
        answer="",
        question_type=question_type,
        level=level,
        paragraphs=[],
        gold_titles=set(gold_titles),
    )


def make_top50_df(rows):
    """Build a top-50-export-shaped DataFrame from (example_id, rank, title)
    triples; score is filler (the reranker recomputes it)."""
    return pd.DataFrame(
        [
            {"example_id": eid, "rank": rank, "title": title, "score": 1.0 / rank}
            for eid, rank, title in rows
        ],
        columns=TOP50_COLUMNS,
    )


# Candidates for "q_cat" deliberately NOT in relevance order, so a correct
# rerank must reorder them (Dogs first in dense order, Cats must be promoted).
QCAT_TOP50 = [
    ("q_cat", 1, "Dogs"),
    ("q_cat", 2, "Cats"),
    ("q_cat", 3, "CatDog"),
    ("q_cat", 4, "Birds"),
]


# --------------------------------------------------------------------------- #
# read_top50 schema guard
# --------------------------------------------------------------------------- #

def test_read_top50_rejects_wrong_schema(tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame([{"example_id": "x", "rank": 1, "title": "T"}]).to_csv(bad, index=False)
    with pytest.raises(ValueError):
        runner.read_top50(str(bad))


def test_read_top50_accepts_exact_schema(tmp_path):
    # Legal control for the schema guard: exact TOP50_COLUMNS is accepted.
    good = tmp_path / "good.csv"
    make_top50_df(QCAT_TOP50).to_csv(good, index=False)
    df = runner.read_top50(str(good))
    assert list(df.columns) == TOP50_COLUMNS


def test_read_top50_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        runner.read_top50(str(tmp_path / "does_not_exist.csv"))


# --------------------------------------------------------------------------- #
# rank continuity (distinct from depth)
# --------------------------------------------------------------------------- #

def test_candidate_titles_ordered_by_rank():
    # Rows shuffled; grouping must return them in ascending-rank order.
    df = make_top50_df([("q_cat", 3, "CatDog"), ("q_cat", 1, "Dogs"),
                        ("q_cat", 4, "Birds"), ("q_cat", 2, "Cats")])
    grouped = runner.candidate_titles_by_example(df)
    assert grouped["q_cat"] == ["Dogs", "Cats", "CatDog", "Birds"]


def test_candidate_titles_non_contiguous_ranks_raise():
    # A gap in the ranks (1,2,4) means the shortlist is truncated/corrupted.
    # Kept independent from the depth matrix so continuity and cardinality
    # remain distinct guards.
    df = make_top50_df([("q_cat", 1, "Dogs"), ("q_cat", 2, "Cats"), ("q_cat", 4, "Birds")])
    with pytest.raises(ValueError):
        runner.candidate_titles_by_example(df)


# --------------------------------------------------------------------------- #
# exact pooled input depth (49 / 50 / 51 matrix)
# --------------------------------------------------------------------------- #

def _titles(n):
    return [f"T{i}" for i in range(n)]


def test_validate_candidate_depths_accepts_exactly_50():
    # Legal control: exactly the pooled storage depth is accepted.
    runner.validate_candidate_depths({"q": _titles(POOLED_DEPTH)})


def test_validate_candidate_depths_rejects_49():
    with pytest.raises(ValueError):
        runner.validate_candidate_depths({"q": _titles(POOLED_DEPTH - 1)})


def test_validate_candidate_depths_rejects_51():
    with pytest.raises(ValueError):
        runner.validate_candidate_depths({"q": _titles(POOLED_DEPTH + 1)})


def test_main_rejects_short_input_depth_before_reranking(monkeypatch, tmp_path):
    # A contiguous but 49-deep CSV (ranks 1..49) passes continuity yet must be
    # rejected on depth, before any reranking.
    examples = [make_example("q", "gold", {"Gold"})]
    top50_path = tmp_path / "dense_top50_pooled.csv"
    make_top50_df(deep_top50_rows("q", depth=POOLED_DEPTH - 1)).to_csv(top50_path, index=False)

    monkeypatch.setattr(runner, "load_examples", lambda **_kwargs: examples)
    monkeypatch.setattr(runner, "build_pooled_corpus", lambda _ex: (list(DEEP_CORPUS), []))

    def _boom(*a, **k):
        raise AssertionError("reranker must not run when depth validation fails")

    with pytest.raises(ValueError):
        runner.main(
            n=1, split="validation",
            top50_in=str(top50_path), out_path=str(tmp_path / "unused.csv"),
            reranker=type("R", (), {"rerank_titles": _boom})(),
        )


# --------------------------------------------------------------------------- #
# join to pooled corpus text
# --------------------------------------------------------------------------- #

def test_build_candidate_paragraphs_joins_text():
    paras = runner.build_candidate_paragraphs(["Cats", "CatDog"], TEXT_BY_TITLE, "q_cat")
    assert [p.title for p in paras] == ["Cats", "CatDog"]
    # Text is pulled from the pooled corpus, not the (empty) top-50 export.
    assert paras[0].text == "cat cat cat"
    assert paras[1].text == "cat dog"


def test_build_candidate_paragraphs_missing_title_raises():
    with pytest.raises(ValueError):
        runner.build_candidate_paragraphs(["Ghost"], TEXT_BY_TITLE, "q_cat")


# --------------------------------------------------------------------------- #
# symmetric evaluation-set coverage (missing / exact / extra matrix)
# --------------------------------------------------------------------------- #

def test_validate_candidate_coverage_accepts_exact_set():
    # Legal control: identical ID sets are accepted.
    examples = [make_example("q_cat", "cat", {"Cats"})]
    runner.validate_candidate_coverage(examples, {"q_cat": ["Dogs", "Cats"]})


def test_validate_candidate_coverage_raises_on_missing_example():
    examples = [make_example("q_cat", "cat", {"Cats"}),
                make_example("q_uncovered", "dog", {"Dogs"})]
    grouped = {"q_cat": ["Dogs", "Cats"]}
    with pytest.raises(ValueError):
        runner.validate_candidate_coverage(examples, grouped)


def test_validate_candidate_coverage_raises_on_extra_csv_example():
    # An ID present in the CSV but not in the loaded set means the CSV came from
    # a larger run; the one-directional check used to miss this.
    examples = [make_example("q_cat", "cat", {"Cats"})]
    grouped = {"q_cat": ["Dogs", "Cats"], "q_extra": ["Dogs", "Cats"]}
    with pytest.raises(ValueError):
        runner.validate_candidate_coverage(examples, grouped)


def test_main_rejects_extra_csv_example_before_reranking(monkeypatch, tmp_path):
    # main() must reject an extra CSV example before building/using the reranker.
    examples = [make_example("q", "gold", {"Gold"})]
    top50_path = tmp_path / "dense_top50_pooled.csv"
    rows = deep_top50_rows("q") + deep_top50_rows("q_extra")
    make_top50_df(rows).to_csv(top50_path, index=False)

    monkeypatch.setattr(runner, "load_examples", lambda **_kwargs: examples)
    monkeypatch.setattr(runner, "build_pooled_corpus", lambda _ex: (list(DEEP_CORPUS), []))

    def _boom(*a, **k):
        raise AssertionError("reranker must not run when coverage validation fails")

    with pytest.raises(ValueError):
        runner.main(
            n=1, split="validation",
            top50_in=str(top50_path), out_path=str(tmp_path / "unused.csv"),
            reranker=type("R", (), {"rerank_titles": _boom})(),
        )


def test_main_raises_when_csv_misses_an_example(monkeypatch, tmp_path):
    examples = [make_example("q", "gold", {"Gold"}),
                make_example("q_missing", "gold", {"Gold"})]
    top50_path = tmp_path / "dense_top50_pooled.csv"
    make_top50_df(deep_top50_rows("q")).to_csv(top50_path, index=False)

    monkeypatch.setattr(runner, "load_examples", lambda **_kwargs: examples)
    monkeypatch.setattr(runner, "build_pooled_corpus", lambda _ex: (list(DEEP_CORPUS), []))

    def _boom(*a, **k):
        raise AssertionError("reranker must not run when coverage validation fails")

    with pytest.raises(ValueError):
        runner.main(
            n=2, split="validation",
            top50_in=str(top50_path), out_path=str(tmp_path / "unused.csv"),
            reranker=type("R", (), {"rerank_titles": _boom})(),
        )


# --------------------------------------------------------------------------- #
# reranking + schema shaping (4-candidate shortlist, store_top_k=4)
# --------------------------------------------------------------------------- #

def test_run_rerank_pooled_reorders_and_shapes_rows():
    ex = make_example("q_cat", "cat", {"Cats"})
    grouped = runner.candidate_titles_by_example(make_top50_df(QCAT_TOP50))

    rows, metrics = runner.run_rerank_pooled(
        [ex], grouped, TEXT_BY_TITLE, make_reranker(), store_top_k=4
    )
    row = rows[0]

    assert row["method"] == "rerank"
    assert row["setting"] == "pooled"
    # Dense order started with "Dogs"; rerank promotes "Cats" (3 shared terms)
    # then "CatDog" (1), leaving the two zero-score passages in incoming order.
    assert row["retrieved_titles"].split(" | ") == ["Cats", "CatDog", "Dogs", "Birds"]
    # Gold "Cats" is now at rank 1 -> hit at every pooled cutoff.
    assert row["any_evidence_recall@2"] == 1
    assert row["full_evidence_recall@10"] == 1
    assert row["reciprocal_rank_at_10"] == 1.0
    assert len(metrics) == 1


def test_columns_match_schema_order():
    ex = make_example("q_cat", "cat", {"Cats"})
    grouped = runner.candidate_titles_by_example(make_top50_df(QCAT_TOP50))
    rows, _ = runner.run_rerank_pooled(
        [ex], grouped, TEXT_BY_TITLE, make_reranker(), store_top_k=4
    )
    df = pd.DataFrame(rows, columns=runner.COLUMNS)

    assert list(df.columns) == RESULT_COLUMNS
    assert "mrr" not in df.columns
    assert df.columns[-2:].tolist() == ["reciprocal_rank_at_10", "reciprocal_rank_at_50"]


def test_pooled_fills_all_three_cutoffs():
    # Pooled K policy fills @2/@5/@10 (unlike per_question, which leaves @10
    # empty). None of the three recall columns should be left uncomputed.
    ex = make_example("q_cat", "cat", {"Cats"})
    grouped = runner.candidate_titles_by_example(make_top50_df(QCAT_TOP50))
    rows, _ = runner.run_rerank_pooled(
        [ex], grouped, TEXT_BY_TITLE, make_reranker(), store_top_k=4
    )
    row = rows[0]
    for k in (2, 5, 10):
        assert row[f"any_evidence_recall@{k}"] is not None


def test_booleans_are_ints_not_python_bools():
    # A miss: gold "Birds" ends last after rerank, so @2 must be 0, not False.
    ex = make_example("q_cat", "cat", {"Birds"})
    grouped = runner.candidate_titles_by_example(make_top50_df(QCAT_TOP50))
    rows, _ = runner.run_rerank_pooled(
        [ex], grouped, TEXT_BY_TITLE, make_reranker(), store_top_k=4
    )
    row = rows[0]

    assert row["any_evidence_recall@2"] == 0
    assert type(row["any_evidence_recall@2"]) is int
    assert not isinstance(row["any_evidence_recall@2"], bool)


def test_make_row_store_depth_caps_at_50():
    ex = make_example("deep", "cat", {"Cats"})
    reranked = [f"T{i}" for i in range(60)]
    row, _ = runner.make_row(ex, reranked)
    assert len(row["retrieved_titles"].split(" | ")) == 50


def test_make_row_reciprocal_rank_horizons_distinguish_rank_11_to_50():
    ex = make_example("deep_hit", "cat", {"Gold"})
    reranked = [f"Distractor {i}" for i in range(19)] + ["Gold"]
    row, metrics = runner.make_row(ex, reranked)

    assert row["reciprocal_rank_at_10"] == 0.0
    assert row["reciprocal_rank_at_50"] == 1 / 20
    assert metrics["reciprocal_rank_at_10"] == 0.0


def test_candidate_order_feeds_reranker_in_rank_order():
    """The reranker should be handed candidates in ascending dense-rank order
    (its tie-break input). Spy on the scorer to capture the pair order."""
    seen = {"texts": None}

    def spy_score(pairs):
        seen["texts"] = [text for _q, text in pairs]
        return fake_score(pairs)

    ex = make_example("q_cat", "cat", {"Cats"})
    grouped = runner.candidate_titles_by_example(make_top50_df(QCAT_TOP50))
    runner.run_rerank_pooled(
        [ex], grouped, TEXT_BY_TITLE, CrossEncoderReranker(scorer=spy_score), store_top_k=4
    )

    # Dense rank order Dogs(1), Cats(2), CatDog(3), Birds(4) -> their texts.
    assert seen["texts"] == ["dog dog dog", "cat cat cat", "cat dog", "bird bird"]


# --------------------------------------------------------------------------- #
# runner output-depth postcondition (defense in depth)
# --------------------------------------------------------------------------- #

def test_run_rerank_pooled_rejects_short_reranked_output():
    """Even if an injected reranker returns fewer titles than store_top_k, the
    runner must refuse to build a row rather than serialize a short result."""
    ex = make_example("q_cat", "cat", {"Cats"})
    grouped = runner.candidate_titles_by_example(make_top50_df(QCAT_TOP50))

    class ShortReranker:
        def rerank_titles(self, query, candidates, top_k):
            return [candidates[0].title]  # only ONE title, not top_k

    with pytest.raises(ValueError):
        runner.run_rerank_pooled(
            [ex], grouped, TEXT_BY_TITLE, ShortReranker(), store_top_k=4
        )


# --------------------------------------------------------------------------- #
# end-to-end main() at the real pooled depth of 50
# --------------------------------------------------------------------------- #

def test_main_writes_pooled_rerank_csv(monkeypatch, tmp_path):
    examples = [
        make_example("q1", "gold", {"Gold"}),
        make_example("q2", "gold", {"Gold"}),
    ]
    top50 = make_top50_df(deep_top50_rows("q1") + deep_top50_rows("q2"))
    top50_path = tmp_path / "dense_top50_pooled.csv"
    top50.to_csv(top50_path, index=False)

    monkeypatch.setattr(runner, "load_examples", lambda **_kwargs: examples)
    monkeypatch.setattr(runner, "build_pooled_corpus", lambda _ex: (list(DEEP_CORPUS), []))
    out = tmp_path / "rerank_results.csv"

    runner.main(
        n=2, split="validation",
        top50_in=str(top50_path), out_path=str(out),
        reranker=make_reranker(),
    )

    result = pd.read_csv(out)
    assert result.columns.tolist() == RESULT_COLUMNS
    assert result["method"].tolist() == ["rerank", "rerank"]
    assert result["setting"].tolist() == ["pooled", "pooled"]
    # Rows follow the examples' order, one per example.
    assert result["example_id"].tolist() == ["q1", "q2"]
    # Every pooled row stores exactly the pooled depth of titles.
    depths = result["retrieved_titles"].apply(lambda s: len(s.split(" | ")))
    assert depths.tolist() == [POOLED_DEPTH, POOLED_DEPTH]
    # Pooled @10 is computed (integer dtype), not left empty/NaN.
    assert pd.api.types.is_integer_dtype(result["any_evidence_recall@10"])
    # Both golds get promoted to rank 1 by the reranker.
    assert result["reciprocal_rank_at_10"].tolist() == [1.0, 1.0]
