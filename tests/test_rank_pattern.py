"""
test_rank_pattern.py

Offline unit tests for the gold-rank pattern partition (src/rank_pattern.py),
covering the spec's required test matrix (section 16):

  - band boundaries and invalid ranks (bool rejected before the int check);
  - the complete two-gold mapping, order-invariance, exhaustiveness, and the
    gold-count guard;
  - the secondary raw-title path (dedup, count/horizon guards, first-occurrence);
  - a metric-consistency oracle that cross-checks each pattern against
    src/evaluator.py's canonical Any/Full/Partial evidence recall -- as an
    oracle only, never an emitted field.

No metric is recomputed inside the partition; the classifier reuses the
evaluator's gold-rank semantics.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from src import evaluator
from src.rank_pattern import (
    CANONICAL_RANK_PATTERNS,
    GOLD_COUNT_V1,
    STORED_DEPTH,
    TWO_GOLD_PATTERN_MAP,
    band_count_tuple,
    classify_two_gold_rank_pattern,
    first_title_ranks,
    get_gold_ranks,
    pattern_from_counts,
    rank_to_band,
)

# One representative rank per band (spec section 16.5).
BAND_REPRESENTATIVES = {
    "top5": 1,
    "rank6_10": 6,
    "rank11_50": 11,
    "not_in_top50": None,
}

# Canonical example rank pairs per pattern (spec section 7.2 / 16.3), all with
# DISTINCT positions so two gold titles never collide at one rank. Used by the
# metric-consistency oracle, which must place both golds in a real ranking.
PATTERN_EXAMPLE_RANKS = {
    "both_in_top5": [1, 5],
    "one_top5_one_6_10": [2, 8],
    "one_top5_one_11_50": [2, 14],
    "one_top5_one_not_in_top50": [2, None],
    "both_in_6_10": [6, 10],
    "one_6_10_one_11_50": [8, 14],
    "one_6_10_one_not_in_top50": [8, None],
    "both_in_11_50": [11, 50],
    "one_11_50_one_not_in_top50": [14, None],
    "both_not_in_top50": [None, None],
}


# --------------------------------------------------------------------------- #
# 16.1 Boundary tests for rank_to_band
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    ("rank", "expected"),
    [
        (1, "top5"),
        (5, "top5"),
        (6, "rank6_10"),
        (10, "rank6_10"),
        (11, "rank11_50"),
        (50, "rank11_50"),
        (None, "not_in_top50"),
    ],
)
def test_rank_to_band_boundaries(rank, expected):
    assert rank_to_band(rank) == expected


# --------------------------------------------------------------------------- #
# 16.2 Invalid-rank tests
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("rank", [0, -1, 51, 100])
def test_rank_to_band_rejects_invalid_rank(rank):
    with pytest.raises(ValueError):
        rank_to_band(rank)


@pytest.mark.parametrize("rank", [True, False])
def test_rank_to_band_rejects_bool(rank):
    # bool subclasses int, so it must be rejected BEFORE the int check (a naive
    # int() path would read True as rank 1).
    with pytest.raises(TypeError):
        rank_to_band(rank)


@pytest.mark.parametrize("rank", [1.0, "1", 5.5, [1]])
def test_rank_to_band_rejects_non_int(rank):
    with pytest.raises(TypeError):
        rank_to_band(rank)


# --------------------------------------------------------------------------- #
# 16.3 Complete two-gold mapping tests
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    ("ranks", "expected"),
    [
        ([1, 5], "both_in_top5"),
        ([2, 8], "one_top5_one_6_10"),
        ([2, 14], "one_top5_one_11_50"),
        ([2, None], "one_top5_one_not_in_top50"),
        ([6, 10], "both_in_6_10"),
        ([8, 14], "one_6_10_one_11_50"),
        ([8, None], "one_6_10_one_not_in_top50"),
        ([11, 50], "both_in_11_50"),
        ([14, None], "one_11_50_one_not_in_top50"),
        ([None, None], "both_not_in_top50"),
    ],
)
def test_two_gold_partition(ranks, expected):
    assert classify_two_gold_rank_pattern(ranks) == expected


def test_two_gold_partition_rejects_bool_rank():
    with pytest.raises(TypeError):
        classify_two_gold_rank_pattern([True, 5])


# --------------------------------------------------------------------------- #
# 16.4 Order-invariance tests
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "ranks",
    [
        [2, 8],
        [2, 14],
        [2, None],
        [8, 14],
        [8, None],
        [14, None],
    ],
)
def test_two_gold_pattern_is_order_invariant(ranks):
    assert classify_two_gold_rank_pattern(ranks) == classify_two_gold_rank_pattern(
        list(reversed(ranks))
    )


# --------------------------------------------------------------------------- #
# 16.5 Exhaustiveness test
# --------------------------------------------------------------------------- #

def _all_unordered_band_pairs():
    """All 10 unordered pairs of the four band representatives."""
    bands = list(BAND_REPRESENTATIVES)
    pairs = []
    for i in range(len(bands)):
        for j in range(i, len(bands)):
            pairs.append(
                [BAND_REPRESENTATIVES[bands[i]], BAND_REPRESENTATIVES[bands[j]]]
            )
    return pairs


def test_partition_is_collectively_exhaustive_and_mutually_exclusive():
    pairs = _all_unordered_band_pairs()
    assert len(pairs) == 10

    labels = [classify_two_gold_rank_pattern(pair) for pair in pairs]
    # Every unordered band pair maps to a distinct canonical label (mutual
    # exclusivity), and the 10 labels exactly cover the canonical set
    # (collective exhaustiveness).
    assert len(set(labels)) == 10
    assert set(labels) == set(CANONICAL_RANK_PATTERNS)
    assert set(CANONICAL_RANK_PATTERNS) == set(TWO_GOLD_PATTERN_MAP.values())
    assert len(CANONICAL_RANK_PATTERNS) == 10


def test_pattern_from_counts_rejects_unreachable_tuple():
    # A count tuple that does not sum to 2 can never come from a valid two-gold
    # input; it is an internal inconsistency, surfaced as AssertionError.
    with pytest.raises(AssertionError):
        pattern_from_counts((3, 0, 0, 0))


# --------------------------------------------------------------------------- #
# 16.6 Gold-count guard
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("ranks", [[1], [1, 2, 3], [], [1, 2, 3, 4]])
def test_v1_rejects_non_two_gold_counts(ranks):
    with pytest.raises(ValueError):
        classify_two_gold_rank_pattern(ranks)


def test_band_count_tuple_sums_to_gold_count():
    for pair in _all_unordered_band_pairs():
        counts = band_count_tuple(pair)
        assert sum(counts) == GOLD_COUNT_V1


# --------------------------------------------------------------------------- #
# 16.7 Uniqueness / horizon (secondary raw-title path)
# --------------------------------------------------------------------------- #

def _retrieved_of_depth(depth, titles_at=None):
    """A retrieved list of length `depth` with fillers, optional gold placement.

    titles_at maps a 1-based rank -> title to place there.
    """
    retrieved = [f"filler_{i}" for i in range(1, depth + 1)]
    for rank, title in (titles_at or {}).items():
        retrieved[rank - 1] = title
    return retrieved


def test_secondary_path_reproduces_evaluator_ranks():
    retrieved = _retrieved_of_depth(50, {3: "Gold A", 20: "Gold B"})
    assert get_gold_ranks(["Gold A", "Gold B"], retrieved) == [3, 20]


def test_secondary_path_none_when_absent():
    retrieved = _retrieved_of_depth(50, {3: "Gold A"})
    assert get_gold_ranks(["Gold A", "Gold B"], retrieved) == [3, None]


def test_secondary_path_rejects_empty_gold_set():
    with pytest.raises(ValueError):
        get_gold_ranks([], _retrieved_of_depth(50))


@pytest.mark.parametrize("gold_titles", [["A"], ["A", "B", "C"]])
def test_secondary_path_rejects_non_two_gold(gold_titles):
    with pytest.raises(ValueError):
        get_gold_ranks(gold_titles, _retrieved_of_depth(50))


@pytest.mark.parametrize("depth", [10, 49, 51, 0])
def test_secondary_path_rejects_wrong_horizon(depth):
    with pytest.raises(ValueError):
        get_gold_ranks(["Gold A", "Gold B"], _retrieved_of_depth(depth))


def test_secondary_path_duplicate_retrieved_uses_first_occurrence():
    # Ranks: 1.A 2.A 3.X ... 4.B ...; A's first occurrence (rank 1) wins.
    retrieved = _retrieved_of_depth(50, {1: "A", 2: "A", 3: "X", 4: "B"})
    assert get_gold_ranks(["A", "B"], retrieved) == [1, 4]
    assert first_title_ranks(retrieved)["A"] == 1


def test_secondary_path_dedup_repeated_supporting_facts():
    # Repeated supporting facts under one title (["A",0],["A",2],["B",1]) collapse
    # to two unique gold titles, not three.
    retrieved = _retrieved_of_depth(50, {2: "A", 5: "B"})
    ranks = get_gold_ranks(["A", "A", "B"], retrieved)
    assert ranks == [2, 5]
    assert classify_two_gold_rank_pattern(ranks) == "both_in_top5"


# --------------------------------------------------------------------------- #
# 16.8 Metric-consistency oracle (test only; nothing emitted)
# --------------------------------------------------------------------------- #

def test_pattern_is_consistent_with_evaluator_metrics():
    """For each representative pattern, the band counts agree with the
    evaluator's canonical Any/Full/Partial Evidence Recall at 5 and 10.

    This is an independent oracle: it reads src/evaluator.py's real metric
    functions and confirms the partition never contradicts them. It recomputes
    nothing inside the partition and asserts no new metric name.
    """
    gold_titles = {"Gold A", "Gold B"}
    # All 10 patterns are covered, each via a distinct-position example.
    assert set(PATTERN_EXAMPLE_RANKS) == set(CANONICAL_RANK_PATTERNS)
    for expected_pattern, pair in PATTERN_EXAMPLE_RANKS.items():
        assert classify_two_gold_rank_pattern(pair) == expected_pattern
        rank_a, rank_b = pair
        placement = {}
        if rank_a is not None:
            placement[rank_a] = "Gold A"
        if rank_b is not None:
            placement[rank_b] = "Gold B"
        retrieved = _retrieved_of_depth(STORED_DEPTH, placement)

        # Sanity: the secondary path reproduces exactly evaluator.gold_ranks.
        eval_ranks = evaluator.gold_ranks(retrieved, gold_titles)
        assert sorted(eval_ranks.values(), key=lambda r: (r is None, r)) == sorted(
            pair, key=lambda r: (r is None, r)
        )

        counts = band_count_tuple(pair)
        n_top5, n_rank6_10, n_rank11_50, _ = counts
        n_within_5 = n_top5
        n_within_10 = n_top5 + n_rank6_10

        for k, n_within in ((5, n_within_5), (10, n_within_10)):
            any_hit = evaluator.any_evidence_recall_at_k(retrieved, gold_titles, k)
            full_hit = evaluator.full_evidence_recall_at_k(retrieved, gold_titles, k)
            partial = evaluator.partial_evidence_recall_at_k(retrieved, gold_titles, k)
            assert any_hit == (n_within >= 1)
            assert full_hit == (n_within == GOLD_COUNT_V1)
            assert partial == pytest.approx(n_within / GOLD_COUNT_V1)

        # The spec's headline identity: both_in_top5 <=> full_evidence_recall@5.
        pattern = pattern_from_counts(counts)
        assert (pattern == "both_in_top5") == (
            evaluator.full_evidence_recall_at_k(retrieved, gold_titles, 5)
        )
