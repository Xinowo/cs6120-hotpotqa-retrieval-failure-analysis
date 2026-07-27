"""
rank_pattern.py

Deterministic gold-rank pattern partition for the pooled top-50 setting.

This is the machine-structural layer of the failure analysis: it answers
"*where* did the gold evidence titles appear in the ranking?", never "*why*
did the retriever fail?". It is a mutually exclusive and collectively
exhaustive partition of gold-title rank positions -- not a causal failure
taxonomy and not a metric.

Authoritative design:
    docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md

Boundaries this module respects (spec section 1.1 / 11):
  - It reuses -- never redefines -- the evaluator's gold-rank semantics
    (exact string equality, first occurrence wins, None when unobserved;
    see src/evaluator.py gold_ranks()). The preferred input is the evaluator's
    already-precomputed details.jsonl `gold_ranks`.
  - It computes NO metric and emits NO recall/coverage/MRR value. Metric
    definitions stay in src/evaluator.py under their canonical names.

Pooled v1 fixes the observation horizon at exactly 50, so the band function
takes no depth argument; a different depth is a different schema version
(spec section 15), not a runtime parameter.

Bands (spec section 3.2):
    1-5       -> top5
    6-10      -> rank6_10
    11-50     -> rank11_50
    missing   -> not_in_top50   (absent from the stored 50, not from the corpus)
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Optional, Tuple

# Frozen identifiers for pooled v1 (spec section 15). These are persisted in the
# CSV columns and test fixtures; changing any of them is a new schema version.
RANK_PATTERN_SCHEMA = "gold_rank_partition_v1"
RANK_PATTERN_SCOPE = "pooled_top50"
STORED_DEPTH = 50  # pooled v1: fixed observation horizon (exact, not "up to 50")
BAND_CUTOFF_PRIMARY = 5
BAND_CUTOFF_SECONDARY = 10
GOLD_COUNT_V1 = 2  # pooled v1 classifies exactly two unique gold titles

# The four rank bands, in the order used for the count tuple / CSV columns.
BANDS = (
    "top5",
    "rank6_10",
    "rank11_50",
    "not_in_top50",
)

# Canonical count-tuple -> label map for the two-gold partition (spec section
# 8.2). The tuple is (n_top5, n_rank6_10, n_rank11_50, n_not_in_top50) and every
# valid two-gold input sums to 2, giving exactly C(5, 2) = 10 unordered classes.
TWO_GOLD_PATTERN_MAP = {
    (2, 0, 0, 0): "both_in_top5",
    (1, 1, 0, 0): "one_top5_one_6_10",
    (1, 0, 1, 0): "one_top5_one_11_50",
    (1, 0, 0, 1): "one_top5_one_not_in_top50",
    (0, 2, 0, 0): "both_in_6_10",
    (0, 1, 1, 0): "one_6_10_one_11_50",
    (0, 1, 0, 1): "one_6_10_one_not_in_top50",
    (0, 0, 2, 0): "both_in_11_50",
    (0, 0, 1, 1): "one_11_50_one_not_in_top50",
    (0, 0, 0, 2): "both_not_in_top50",
}

# The 10 canonical labels in count-tuple order. Kept as a stable, ordered tuple
# so the exhaustiveness test and any downstream display have a single source.
CANONICAL_RANK_PATTERNS = tuple(TWO_GOLD_PATTERN_MAP.values())

# Human-readable display labels (spec section 13). Machine labels above stay
# snake_case and stable; a UI may show these instead.
RANK_PATTERN_DISPLAY = {
    "both_in_top5": "Both golds in top 5",
    "one_top5_one_6_10": "One gold in top 5; one at ranks 6-10",
    "one_top5_one_11_50": "One gold in top 5; one at ranks 11-50",
    "one_top5_one_not_in_top50": "One gold in top 5; one absent from top 50",
    "both_in_6_10": "Both golds at ranks 6-10",
    "one_6_10_one_11_50": "One gold at ranks 6-10; one at ranks 11-50",
    "one_6_10_one_not_in_top50": "One gold at ranks 6-10; one absent from top 50",
    "both_in_11_50": "Both golds at ranks 11-50",
    "one_11_50_one_not_in_top50": "One gold at ranks 11-50; one absent from top 50",
    "both_not_in_top50": "Both golds absent from top 50",
}


def rank_to_band(rank: Optional[int]) -> str:
    """Map one gold rank to its structural band (spec section 6).

    Pooled v1 fixes the horizon at 50, so there is no depth argument. `None`
    means the gold was not observed in the stored top-50 -- band
    ``not_in_top50`` -- which means "absent from the stored 50", never "absent
    from the corpus" (spec section 3.2).

    Rejections (fail loudly rather than coerce):
      - ``bool`` (``True``/``False``) raises TypeError BEFORE the int check --
        ``bool`` subclasses ``int``, so ``True`` would otherwise read as rank 1;
      - any non-int, non-None value raises TypeError;
      - a rank < 1 or > 50 raises ValueError.
    """
    if rank is None:
        return "not_in_top50"

    # bool is a subclass of int; reject it before the int check so True is not
    # silently read as rank 1.
    if isinstance(rank, bool):
        raise TypeError("Rank must be an int or None, not bool.")

    if not isinstance(rank, int):
        raise TypeError("Rank must be an int or None.")

    if rank < 1:
        raise ValueError("Rank must be >= 1.")

    if rank > STORED_DEPTH:
        raise ValueError(
            f"Observed rank {rank} exceeds the pooled stored depth {STORED_DEPTH}."
        )

    if rank <= BAND_CUTOFF_PRIMARY:
        return "top5"

    if rank <= BAND_CUTOFF_SECONDARY:
        return "rank6_10"

    return "rank11_50"


def band_count_tuple(
    gold_ranks: Iterable[Optional[int]],
) -> Tuple[int, int, int, int]:
    """Count how many of exactly two gold ranks fall in each band.

    Returns ``(n_top5, n_rank6_10, n_rank11_50, n_not_in_top50)``, which always
    sums to 2 for a valid two-gold input. Raises ValueError on a gold count
    other than 2 (spec section 5.3 / 7.1); each rank is validated by
    :func:`rank_to_band`, so a bool or out-of-range rank fails loudly here too.
    """
    ranks = list(gold_ranks)

    if len(ranks) != GOLD_COUNT_V1:
        raise ValueError(
            f"Pooled v1 classifies exactly {GOLD_COUNT_V1} unique gold ranks, "
            f"got {len(ranks)}."
        )

    counts = Counter(rank_to_band(rank) for rank in ranks)
    return (
        counts["top5"],
        counts["rank6_10"],
        counts["rank11_50"],
        counts["not_in_top50"],
    )


def pattern_from_counts(counts: Tuple[int, int, int, int]) -> str:
    """Map a band-count tuple to its canonical label (spec section 8.2).

    Every count tuple produced from a valid two-gold input is in the frozen
    map, so a miss is an unreachable internal inconsistency, not a user error.
    """
    try:
        return TWO_GOLD_PATTERN_MAP[counts]
    except KeyError as exc:  # pragma: no cover - unreachable for valid input
        raise AssertionError(
            f"Unreachable two-gold band-count pattern: {counts}"
        ) from exc


def classify_two_gold_rank_pattern(
    gold_ranks: Iterable[Optional[int]],
) -> str:
    """Classify an unordered pair of gold ranks into one of 10 labels.

    The result is invariant to the order of the two ranks (the band counts are
    order-free). Fails loudly on any gold count other than 2, on a bool rank,
    and on a rank outside ``[1, 50]`` (spec section 5.3 / 7).
    """
    return pattern_from_counts(band_count_tuple(gold_ranks))


# --------------------------------------------------------------------------- #
# Secondary path: derive gold ranks from raw retrieved titles (tests only).
#
# The primary path consumes details.jsonl `gold_ranks` directly and needs none
# of this. This exists only so tests can synthesize inputs, and it must
# reproduce evaluator.gold_ranks exactly: exact string equality, earliest
# occurrence wins, None when unobserved (spec section 9; src/evaluator.py).
# --------------------------------------------------------------------------- #

def first_title_ranks(
    retrieved_titles: Iterable[str],
) -> dict:
    """1-based rank of the first occurrence of each retrieved title.

    Exact string equality; the earliest (smallest-rank) occurrence wins if a
    title repeats. This mirrors evaluator.gold_ranks and introduces no title
    normalization.
    """
    first_ranks: dict = {}
    for rank, title in enumerate(retrieved_titles, start=1):
        if title not in first_ranks:
            first_ranks[title] = rank
    return first_ranks


def get_gold_ranks(
    gold_titles: Iterable[str],
    retrieved_titles: Iterable[str],
) -> List[Optional[int]]:
    """Gold ranks for the secondary raw-title path (spec section 9).

    Deduplicates gold titles (repeated supporting facts under one title collapse
    to a single gold), requires exactly two unique gold titles, and requires
    exactly ``STORED_DEPTH`` retrieved titles so a ``None`` rank provably means
    "absent from the stored 50", not "the list happened to be short" (spec
    section 14.6). Returns one rank-or-None per unique gold title, in first-seen
    order.
    """
    unique_gold_titles = list(dict.fromkeys(gold_titles))

    if not unique_gold_titles:
        raise ValueError("Gold title set must not be empty.")
    if len(unique_gold_titles) != GOLD_COUNT_V1:
        raise ValueError(
            f"Pooled v1 expects exactly {GOLD_COUNT_V1} unique gold titles, "
            f"got {len(unique_gold_titles)}."
        )

    retrieved = list(retrieved_titles)
    if len(retrieved) != STORED_DEPTH:
        raise ValueError(
            f"Pooled v1 observation horizon must be exactly {STORED_DEPTH} "
            f"retrieved titles, got {len(retrieved)}."
        )

    rank_lookup = first_title_ranks(retrieved)
    return [rank_lookup.get(gold_title) for gold_title in unique_gold_titles]
