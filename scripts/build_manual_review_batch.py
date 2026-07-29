"""
build_manual_review_batch.py  (the manual-failure-review batch extractor)

Reads the accepted formal run as a **read-only source** and writes the v1
calibration/open-coding review workspace beside it:

    results/runs/2026-07-17_a/          (read-only source; never written)
        details.jsonl                   canonical case content + gold_ranks
        gold_rank_patterns.csv          the machine ten-class rank_pattern
            |
            v
    results/annotations/manual_review_v1/
        assignment.csv                  compact record of the 30-unit split
        xin_cases.json                  Xin's 17 cases
        jiajun_cases.json               Jiajun's 17 cases
        failure_review.html             the one shared file-picker review page

Authoritative design:
    docs/specs/2026-07-27-manual-failure-review-course-protocol.md
        section 2.1   read-only source run
        section 2.2   unit identity, strict Any@5, review_cutoff = 5
        section 3.1.1 the one frozen selection algorithm
        section 3.2   overlap and workload
        section 3.3   the complete assignment predicate
        section 3.4   the frozen selection oracle
        section 4     reviewer case files
        section 4.1   exact rank_pattern source binding
        section 4.2   exact per-case review_cutoff storage
        section 9     minimal validation and acceptance

Design principles this extractor keeps (protocol section 2):

  - **Python computes structure; it never proposes a cause.** Every value it
    writes is either copied from the accepted run or derived from the frozen
    sampling rule. No human field is pre-filled: a generated case carries no
    `label` field at all, so there is nowhere for a machine-authored failure
    cause to appear.
  - **The machine `rank_pattern` and the human failure label are different
    layers.** `rank_pattern` is copied byte for byte from its own
    `(example_id, retriever)` source row and travels as read-only context.
  - **The source run is read-only.** Generation refuses any output path inside
    the run directory, and the run's own `failures_review.html` is left
    untouched — the new page is a separate artifact derived from it.
  - **Validation repeats the generator's work rather than trusting it.** The
    four frozen contracts (assignment predicate, selection oracle,
    `rank_pattern` source binding, per-case `review_cutoff`) are re-checked from
    the built artifacts.

Every frozen quantity lives in one `BatchSpec`, and each function that enforces a
contract is given that spec rather than reading a module constant. That is what
makes the contracts checkable: the acceptance tests drive the same validators
with a different population and a different quota table, so a validator that had
quietly hardcoded the v1 numbers — and would therefore pass vacuously — fails.

The details.jsonl / config.json loaders and the identifier and path guards are
reused verbatim from `scripts.build_failure_report`, so the input contract is
identical to the accepted failure-review pipeline. This script imports that
module without modifying it, and recomputes no metric: strict Any@5 eligibility
is read off the evaluator's already-stored `gold_ranks`.

Usage:
    python scripts/build_manual_review_batch.py
    python scripts/build_manual_review_batch.py --out-dir /tmp/manual_review_v1
    python scripts/build_manual_review_batch.py --run 2026-07-17_a --check-only
"""

import argparse
import copy
import csv
import json
import os
import random
import sys
from typing import Dict, Mapping, NamedTuple, Sequence, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import build_failure_report as bfr
# The two closed section-4 shapes and the frozen reviewer set are imported, not
# restated: the extractor and the shipped page must enforce one contract, and a
# second definition here is exactly how they would drift apart.
from scripts.manual_review_page import (
    CASE_FIELDS,
    REVIEWER_FILE_FIELDS,
    REVIEWER_IDS,
    render_page,
)
from src.rank_pattern import CANONICAL_RANK_PATTERNS

# --------------------------------------------------------------------------- #
# Frozen batch identity (protocol sections 2.1 / 2.2 / 4)
# --------------------------------------------------------------------------- #

BATCH_ID = "manual_review_v1"
SOURCE_RUN_ID = "2026-07-17_a"

# The strict Any@5 criterion cutoff. Stored explicitly at the file level, in
# every case, and in every exported notes row (sections 2.2 / 4.2 / 6). This is
# NOT the accepted export cutoff `k` of the upstream annotation pipeline: an
# upstream export cutoff and the failure-selection cutoff are different
# concepts, and v1 has no research need to join on upstream `k`.
REVIEW_CUTOFF = 5

DEFAULT_OUTPUT_DIR = os.path.join("results", "annotations", BATCH_ID)

ASSIGNMENT_NAME = "assignment.csv"
PAGE_NAME = "failure_review.html"
RANK_PATTERN_SOURCE_NAME = "gold_rank_patterns.csv"


def reviewer_file_name(reviewer_id):
    """The delivery file name for one reviewer (section 4)."""
    return f"{reviewer_id}_cases.json"


# --------------------------------------------------------------------------- #
# Frozen sampling rule (protocol section 3.1.1)
# --------------------------------------------------------------------------- #

# The seed and the draw operation are both frozen: "seeded with 6120" alone does
# not specify a sample, because drawing with `sample` and shuffling then slicing
# are both ordinary readings of that phrase and they select disjoint sets on this
# population. A fresh generator per stratum is part of the rule, not an
# implementation detail — strata never share a stream.
SELECTION_SEED = 6120

# (retriever, question_type, quota) in the frozen stratum order. This order is
# both the stratum-processing order and the canonical output order of
# assignment.csv and of the `cases` arrays.
STRATA = (
    ("bm25", "bridge", 12),
    ("bm25", "comparison", 3),
    ("dense", "bridge", 12),
    ("dense", "comparison", 3),
)

# Exactly one unit per stratum is double-reviewed (section 3.2).
OVERLAP_PER_STRATUM = 1

# The eligible strict Any@5 population this batch was frozen against (section
# 3.1). Recomputed on every run and compared: a different population means the
# source run changed, which invalidates the frozen oracle rather than producing
# a new batch.
ELIGIBLE_POPULATION = {
    ("bm25", "bridge"): 51,
    ("bm25", "comparison"): 12,
    ("dense", "bridge"): 16,
    ("dense", "comparison"): 3,
}

# Non-overlap units per reviewer per retriever (section 3.2). These four counts
# are part of the assignment predicate, not commentary on it: without them a
# split that gives Xin all 13 private BM25 units and Jiajun all 13 private Dense
# units satisfies every set-cardinality and strata check while violating the
# agreed workload.
PRIVATE_QUOTAS = {
    "xin": {"bm25": 7, "dense": 6},
    "jiajun": {"bm25": 6, "dense": 7},
}


# --------------------------------------------------------------------------- #
# Frozen selection oracle (protocol section 3.4)
# --------------------------------------------------------------------------- #

# The exact keys the section 3.1.1 algorithm produces on the accepted source
# run, in canonical output order. A frozen batch that only a program can name is
# not frozen, so the expected keys are asserted rather than assumed: a future
# Python or library change that altered the draw fails this comparison instead
# of silently producing a different batch.
FROZEN_SELECTED_KEYS = (
    # bm25 / bridge
    ("5a79b7f6554299029c4b5f6f", "bm25"),
    ("5a7c9f325542990527d554e6", "bm25"),
    ("5a7d61775542991319bc93b9", "bm25"),
    ("5a83880e554299123d8c214e", "bm25"),
    ("5a83a532554299334474606f", "bm25"),
    ("5abcc96c5542996583600492", "bm25"),
    ("5ac1a3665542994ab5c67daf", "bm25"),
    ("5adc8977554299438c868de2", "bm25"),
    ("5ade42b55542992fa25da717", "bm25"),
    ("5adf58f15542993a75d264d2", "bm25"),
    ("5ae057fd55429945ae959328", "bm25"),
    ("5ae60426554299546bf83019", "bm25"),
    # bm25 / comparison
    ("5a78b209554299148911f93e", "bm25"),
    ("5ab72a025542992aa3b8c7b8", "bm25"),
    ("5ab8f57b5542991b5579f097", "bm25"),
    # dense / bridge
    ("5a7d19d85542995ed0d165e8", "dense"),
    ("5a81ebee554299676cceb16d", "dense"),
    ("5a83aaeb5542996488c2e483", "dense"),
    ("5a85cead5542991dd0999ea9", "dense"),
    ("5ab48c325542996a3a969f93", "dense"),
    ("5ab978855542996be2020512", "dense"),
    ("5add67915542992200553af8", "dense"),
    ("5ade69e455429975fa854ec5", "dense"),
    ("5ae048a255429924de1b708e", "dense"),
    ("5ae0a59a55429945ae9593e2", "dense"),
    ("5ae1801955429901ffe4aec4", "dense"),
    ("5ae1f596554299234fd04372", "dense"),
    # dense / comparison (the entire eligible stratum)
    ("5a76387d554299109176e6ba", "dense"),
    ("5a78b209554299148911f93e", "dense"),
    ("5a8d93ad554299653c1aa13d", "dense"),
)

# The four overlap units, in the same stratum order.
#
# `5a78b209554299148911f93e` appears twice above and once below: once under BM25
# and once under Dense. Those are two distinct review units, because a unit key
# includes the retriever. The 30 keys are therefore 30 distinct
# (example_id, retriever) pairs but only 29 distinct example_id values, so every
# cardinality check must be applied to the unit key and never to example_id.
FROZEN_OVERLAP_KEYS = (
    ("5a7d61775542991319bc93b9", "bm25"),
    ("5a78b209554299148911f93e", "bm25"),
    ("5a83aaeb5542996488c2e483", "dense"),
    ("5a76387d554299109176e6ba", "dense"),
)


# --------------------------------------------------------------------------- #
# Output shapes (protocol sections 4 / 4.2)
# --------------------------------------------------------------------------- #

ASSIGNMENT_COLUMNS = (
    "run_id",
    "example_id",
    "retriever",
    "question_type",
    "assigned_reviewer",
    "is_overlap",
)

# `CASE_FIELDS`, `REVIEWER_FILE_FIELDS`, and `REVIEWER_IDS` are imported above
# from `scripts.manual_review_page`, which owns the one definition of each. Both
# key sets are closed and are checked for EQUALITY, not for the presence of the
# frozen fields: a case contains only the material needed for review, carries no
# `label` field (so no machine-authored failure cause can travel in it) and no
# `notes` field (section 4 freezes that the file contains no notes from either
# reviewer). `CASE_FIELDS` also fixes the serialization order, so an overlap unit
# is byte-identical in both reviewer files.

# One retrieved result, through rank 50.
RESULT_FIELDS = ("rank", "title", "score", "text")


class BatchError(ValueError):
    """A frozen contract was violated. Always a rejection, never a fallback."""


# --------------------------------------------------------------------------- #
# The frozen quantities, in one place
# --------------------------------------------------------------------------- #

class BatchSpec(NamedTuple):
    """Everything a batch freezes, passed explicitly to each contract check.

    Threading this rather than reading module constants is deliberate: the
    acceptance tests run the same validators over a different population and
    quota table, so a check that had hardcoded the v1 numbers cannot pass
    vacuously.
    """

    batch_id: str
    run_id: str
    review_cutoff: int
    seed: int
    strata: Tuple[Tuple[str, str, int], ...]
    overlap_per_stratum: int
    eligible_population: Mapping[Tuple[str, str], int]
    private_quotas: Mapping[str, Mapping[str, int]]
    selected_keys: Tuple[Tuple[str, str], ...]
    overlap_keys: Tuple[Tuple[str, str], ...]

    @property
    def retriever_order(self):
        """Retrievers in frozen stratum order, deduplicated."""
        return tuple(dict.fromkeys(retriever for retriever, _, _ in self.strata))

    @property
    def reviewer_order(self):
        """Reviewer ids in a fixed order, for deterministic row ordering."""
        return tuple(sorted(self.private_quotas))

    @property
    def batch_size(self):
        return sum(quota for _, _, quota in self.strata)

    @property
    def overlap_size(self):
        return self.overlap_per_stratum * len(self.strata)

    def cases_for(self, reviewer_id):
        """How many cases one reviewer sees: the overlap units plus their own."""
        return self.overlap_size + sum(self.private_quotas[reviewer_id].values())


V1_SPEC = BatchSpec(
    batch_id=BATCH_ID,
    run_id=SOURCE_RUN_ID,
    review_cutoff=REVIEW_CUTOFF,
    seed=SELECTION_SEED,
    strata=STRATA,
    overlap_per_stratum=OVERLAP_PER_STRATUM,
    eligible_population=ELIGIBLE_POPULATION,
    private_quotas=PRIVATE_QUOTAS,
    selected_keys=FROZEN_SELECTED_KEYS,
    overlap_keys=FROZEN_OVERLAP_KEYS,
)

BATCH_SIZE = V1_SPEC.batch_size            # 30 unique units
OVERLAP_SIZE = V1_SPEC.overlap_size        # 4 double-reviewed
CASES_PER_REVIEWER = V1_SPEC.cases_for("xin")   # 17


# --------------------------------------------------------------------------- #
# Read-only source: strict Any@5 eligibility
# --------------------------------------------------------------------------- #

def is_strict_any5_failure(gold_titles, gold_ranks, cutoff=REVIEW_CUTOFF):
    """True when neither gold title appears in the first `cutoff` results.

    This reads the evaluator's already-precomputed `gold_ranks` (exact string
    equality, first occurrence wins, None when unobserved) and recomputes no
    metric. A rank of None means the gold was absent from the stored 50, which
    is also a miss at 5.
    """
    return all(
        gold_ranks[title] is None or gold_ranks[title] > cutoff
        for title in gold_titles
    )


def eligible_strata(records, cutoff=REVIEW_CUTOFF):
    """Partition the strict Any@5 eligible units by (retriever, question_type).

    Returns {(retriever, question_type): [example_id, ...]} with each stratum's
    ids sorted in ascending Unicode code-point order — Python's default string
    comparison, with no locale, case folding, or normalization (section 3.1.1
    step 2).
    """
    strata: Dict[Tuple[str, str], list] = {}
    for record in records:
        gold_titles = record["gold_titles"]
        for retriever, sub in record["retrievers"].items():
            if not is_strict_any5_failure(gold_titles, sub["gold_ranks"], cutoff):
                continue
            strata.setdefault((retriever, record["question_type"]), []).append(
                record["example_id"]
            )
    return {key: sorted(ids) for key, ids in strata.items()}


def verify_eligible_population(strata, spec):
    """Reject a source population that differs from the frozen section 3.1 table.

    The frozen oracle is only meaningful for the population it was drawn from,
    so a changed population is a rejection rather than a new batch.
    """
    actual = {key: len(ids) for key, ids in strata.items()}
    expected = dict(spec.eligible_population)
    if actual != expected:
        raise BatchError(
            "strict Any@5 eligible population does not match the frozen table: "
            f"expected {dict(sorted(expected.items()))}, "
            f"got {dict(sorted(actual.items()))}"
        )


# --------------------------------------------------------------------------- #
# The one frozen selection algorithm (protocol section 3.1.1)
# --------------------------------------------------------------------------- #

def draw_stratum(sorted_ids, quota, seed=SELECTION_SEED):
    """Draw one stratum's quota with the frozen operation.

    A **fresh** ``random.Random(seed)`` per stratum, then
    ``rng.sample(sorted_ids, quota)``, then the drawn ids sorted ascending
    (steps 3-5). No other pseudorandom generator, sampling operation, shared
    generator stream, or stratum order may be substituted: on this population,
    shuffling and slicing selects a disjoint set.
    """
    if quota > len(sorted_ids):
        raise BatchError(
            f"quota {quota} exceeds the stratum's {len(sorted_ids)} eligible units"
        )
    rng = random.Random(seed)
    return sorted(rng.sample(sorted_ids, quota))


def select_batch(strata, spec):
    """Assemble the batch by concatenating the strata in the frozen order.

    Returns [(retriever, question_type, [example_id, ...]), ...]. Because each
    stratum resets the generator, the processing order does not affect which
    units are drawn; the order is frozen so that the output ordering is
    reproducible.
    """
    selected = []
    for retriever, question_type, quota in spec.strata:
        key = (retriever, question_type)
        if key not in strata:
            raise BatchError(f"no eligible units in stratum {key}")
        selected.append(
            (retriever, question_type, draw_stratum(strata[key], quota, seed=spec.seed))
        )
    return selected


def select_overlap(selected, spec):
    """Draw the double-reviewed units from the already selected batch.

    The same procedure is repeated independently inside each stratum of the
    selected batch: sort that stratum's selected ids, create a **fresh**
    generator, and draw exactly `overlap_per_stratum`.

    The draw reads only `selected`. It never sees the full eligible population,
    so it cannot return a unit that was not assigned, and it never reuses the
    generator state left by selection. Reading the full eligible stratum instead
    is a different procedure and is not permitted, even where it happens to
    coincide.
    """
    overlap = []
    for retriever, _question_type, drawn in selected:
        rng = random.Random(spec.seed)
        for example_id in sorted(rng.sample(sorted(drawn), spec.overlap_per_stratum)):
            overlap.append((example_id, retriever))
    return tuple(overlap)


def selected_keys(selected):
    """The batch's unit keys in canonical output order."""
    return tuple(
        (example_id, retriever)
        for retriever, _question_type, drawn in selected
        for example_id in drawn
    )


def verify_selection_oracle(keys, overlap_keys, spec):
    """Compare a generated batch against the frozen section 3.4 oracle.

    Order is compared as well as membership: a difference in either is a
    rejection, not a new batch.
    """
    if len(set(spec.selected_keys)) != len(spec.selected_keys):
        raise BatchError("the frozen oracle contains a duplicate unit key")
    if tuple(keys) != tuple(spec.selected_keys):
        raise BatchError(
            "selected unit keys do not reproduce the frozen oracle: expected "
            f"{len(spec.selected_keys)} keys in canonical order, got {len(tuple(keys))} "
            "keys or a different order"
        )
    if tuple(overlap_keys) != tuple(spec.overlap_keys):
        raise BatchError(
            "overlap unit keys do not reproduce the frozen oracle: expected "
            f"{list(spec.overlap_keys)}, got {list(overlap_keys)}"
        )
    if not set(spec.overlap_keys) <= set(spec.selected_keys):
        raise BatchError(
            "the frozen overlap set contains a unit that is not in the selected batch"
        )


# --------------------------------------------------------------------------- #
# Exact rank_pattern source binding (protocol section 4.1)
# --------------------------------------------------------------------------- #

def load_rank_pattern_source(path, run_id):
    """Read the rank-pattern source into {(example_id, retriever): rank_pattern}.

    Membership in the accepted ten-label vocabulary is not sufficient to bind a
    label to a case, so this returns the exact source value keyed by the exact
    join key `(example_id, retriever)` within the fixed run. A duplicate key
    would make the join ambiguous and is rejected here rather than resolved.
    """
    patterns = {}
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for column in ("run_id", "example_id", "retriever", "rank_pattern"):
            if column not in (reader.fieldnames or ()):
                raise BatchError(
                    f"{RANK_PATTERN_SOURCE_NAME}: missing required column {column!r}"
                )
        for line_no, row in enumerate(reader, start=2):
            if row["run_id"] != run_id:
                raise BatchError(
                    f"{RANK_PATTERN_SOURCE_NAME} line {line_no}: run_id "
                    f"{row['run_id']!r} != {run_id!r}"
                )
            key = (row["example_id"], row["retriever"])
            if key in patterns:
                raise BatchError(
                    f"{RANK_PATTERN_SOURCE_NAME} line {line_no}: duplicate join "
                    f"key {key}; the join must be unique"
                )
            pattern = row["rank_pattern"]
            if pattern not in CANONICAL_RANK_PATTERNS:
                raise BatchError(
                    f"{RANK_PATTERN_SOURCE_NAME} line {line_no}: rank_pattern "
                    f"{pattern!r} is not one of the accepted ten labels"
                )
            patterns[key] = pattern
    if not patterns:
        raise BatchError(f"{RANK_PATTERN_SOURCE_NAME}: no rows for run {run_id!r}")
    return patterns


def bind_rank_pattern(key, patterns):
    """The exact source value for one unit key.

    A key absent from the source file is a rejection, never a blank or inferred
    label.
    """
    if key not in patterns:
        raise BatchError(
            f"{key} has no row in {RANK_PATTERN_SOURCE_NAME}; a missing source "
            "row is a rejection, never a blank or inferred label"
        )
    return patterns[key]


def validate_rank_pattern_binding(cases, patterns):
    """Re-check the section 4.1 binding from the built cases.

    This repeats the join independently instead of trusting the generator. It
    matches on the full `(example_id, retriever)` key: 29 of the 30 selected
    example_id values are unique but one appears under both retrievers, so an
    example_id-only join can attach BM25 structure to a Dense unit.
    """
    seen = set()
    for case in cases:
        key = (case["example_id"], case["retriever"])
        if key in seen:
            raise BatchError(f"case key {key} appears more than once")
        seen.add(key)
        if key not in patterns:
            raise BatchError(
                f"case key {key} does not exist in {RANK_PATTERN_SOURCE_NAME}"
            )
        expected = patterns[key]
        actual = case["rank_pattern"]
        if actual != expected:
            raise BatchError(
                f"case {key}: rank_pattern {actual!r} does not equal its own "
                f"source row value {expected!r} byte for byte"
            )


# --------------------------------------------------------------------------- #
# Exact per-case review_cutoff storage (protocol section 4.2)
# --------------------------------------------------------------------------- #

def validate_review_cutoff(cases, spec):
    """Every case carries its own `review_cutoff` as the JSON integer `5`.

    A boolean, string, float, missing field, or any other integer is a
    rejection. `bool` is checked before `int` because it subclasses `int`, so
    `True` would otherwise read as the integer 1.
    """
    cutoff = spec.review_cutoff
    for case in cases:
        key = (case.get("example_id"), case.get("retriever"))
        if "review_cutoff" not in case:
            raise BatchError(f"case {key} is missing the review_cutoff field")
        value = case["review_cutoff"]
        if isinstance(value, bool) or not isinstance(value, int):
            raise BatchError(
                f"case {key}: review_cutoff must be the integer {cutoff}, got "
                f"{value!r} ({type(value).__name__})"
            )
        if value != cutoff:
            raise BatchError(
                f"case {key}: review_cutoff must be {cutoff}, got {value!r}"
            )


# --------------------------------------------------------------------------- #
# Case construction (protocol section 4)
# --------------------------------------------------------------------------- #

def build_case(record, retriever, rank_pattern, is_overlap, spec):
    """Build one `cases` item, carrying only the material needed for review.

    Field order is fixed by CASE_FIELDS so that an overlap unit serializes
    byte-identically in both reviewer files.
    """
    sub = record["retrievers"][retriever]
    case = {
        "example_id": record["example_id"],
        "retriever": retriever,
        "question_type": record["question_type"],
        "question": record["question"],
        "gold_titles": list(record["gold_titles"]),
        "gold_ranks": {
            title: sub["gold_ranks"][title] for title in record["gold_titles"]
        },
        "retrieved_results": [
            {field: item[field] for field in RESULT_FIELDS} for item in sub["top_k"]
        ],
        "rank_pattern": rank_pattern,
        "review_cutoff": spec.review_cutoff,
        "is_overlap": is_overlap,
    }
    if tuple(case) != CASE_FIELDS:
        raise BatchError(
            f"case field order drifted from the frozen list: {tuple(case)}"
        )
    return case


def build_cases(records, keys, overlap_keys, patterns, spec):
    """Build every unique case in canonical order, keyed for reuse per reviewer."""
    by_example = {record["example_id"]: record for record in records}
    overlap = set(overlap_keys)
    cases = {}
    for key in keys:
        example_id, retriever = key
        record = by_example.get(example_id)
        if record is None:
            raise BatchError(
                f"selected example_id {example_id!r} is not in the source run"
            )
        if retriever not in record["retrievers"]:
            raise BatchError(
                f"selected unit {key} has no {retriever!r} record in the source run"
            )
        cases[key] = build_case(
            record, retriever, bind_rank_pattern(key, patterns), key in overlap, spec
        )
    return cases


# --------------------------------------------------------------------------- #
# Workload split (protocol sections 3.2 / 3.3)
# --------------------------------------------------------------------------- #

def split_private_units(private_keys, spec):
    """Deal the non-overlap units to the reviewers, deterministically.

    The protocol freezes the four per-reviewer per-retriever counts but not the
    procedure that reaches them, so this is an implementation choice made
    deterministic on purpose: within each retriever's private pool, in canonical
    batch order, units are dealt alternately starting with the reviewer holding
    the larger quota for that retriever. Each v1 pool has an odd size (13), so
    the reviewer who deals first takes the extra unit and the frozen 7/6 and 6/7
    counts fall out of the quota table rather than out of a hardcoded name. The
    result is verified against that table before it is used.

    Alternating rather than slicing also keeps each reviewer's private set mixed
    across bridge and comparison units, so neither reviewer calibrates on a
    single question type.
    """
    assignment = {reviewer: [] for reviewer in spec.private_quotas}
    for retriever in spec.retriever_order:
        pool = [key for key in private_keys if key[1] == retriever]
        order = sorted(
            spec.private_quotas,
            key=lambda reviewer: (
                -spec.private_quotas[reviewer].get(retriever, 0),
                reviewer,
            ),
        )
        for index, key in enumerate(pool):
            assignment[order[index % len(order)]].append(key)

    for reviewer, quotas in spec.private_quotas.items():
        for retriever, expected in quotas.items():
            actual = sum(1 for key in assignment[reviewer] if key[1] == retriever)
            if actual != expected:
                raise BatchError(
                    f"private split gives {reviewer} {actual} {retriever} units, "
                    f"but the frozen quota is {expected}"
                )
    return assignment


def reviewer_keys(assignment, overlap_keys, keys):
    """Each reviewer's unit keys — the shared overlap units plus their private ones.

    Emitted in the canonical batch order of section 3.1.1, which is the output
    order of both `assignment.csv` and the `cases` arrays. The overlap-first
    presentation the calibration step needs is the review page's ordering
    (section 5), applied at display time; putting it in the file instead would
    replace the canonical order the protocol freezes.
    """
    canonical = {key: index for index, key in enumerate(keys)}
    overlap = set(overlap_keys)
    return {
        reviewer: sorted(overlap | set(private), key=canonical.__getitem__)
        for reviewer, private in assignment.items()
    }


def _stratum_index(keys, spec):
    """Map each unit key to the frozen stratum that drew it.

    Recovered from the canonical output order and the frozen quotas rather than
    from the generator's own partition, so the predicate stays independent of
    the code it checks.
    """
    stratum_of = {}
    index = 0
    for retriever, question_type, quota in spec.strata:
        for key in keys[index:index + quota]:
            stratum_of[key] = (retriever, question_type)
        index += quota
    if index != len(keys):
        raise BatchError(
            f"the frozen quotas cover {index} units but the batch has {len(keys)}"
        )
    return stratum_of


def _count_by_stratum(unit_keys, keys, spec):
    """Count units per (retriever, question_type)."""
    stratum_of = _stratum_index(keys, spec)
    counts: Dict[Tuple[str, str], int] = {}
    for key in unit_keys:
        stratum = stratum_of.get(key)
        if stratum is None:
            raise BatchError(f"unit {key} is not part of the selected batch")
        counts[stratum] = counts.get(stratum, 0) + 1
    return counts


def validate_assignment(per_reviewer, overlap_keys, keys, spec):
    """The complete section 3.3 predicate, including the four private counts.

    The private-count clauses are part of the predicate. Without them it accepts
    an assignment section 3.2 forbids: all 13 private BM25 units to Xin and all
    13 private Dense units to Jiajun, while both file sizes, the union, the
    intersection, and both strata tables stay exactly correct.
    """
    if set(per_reviewer) != set(spec.private_quotas):
        raise BatchError(
            f"expected reviewers {sorted(spec.private_quotas)}, "
            f"got {sorted(per_reviewer)}"
        )

    sets = {}
    for reviewer, unit_keys in per_reviewer.items():
        unique = set(unit_keys)
        if len(unique) != len(unit_keys):
            raise BatchError(f"{reviewer}: a unit appears more than once in one file")
        sets[reviewer] = unique

    for reviewer, unit_keys in sets.items():
        expected = spec.cases_for(reviewer)
        if len(unit_keys) != expected:
            raise BatchError(
                f"{reviewer} has {len(unit_keys)} units, expected {expected}"
            )

    union = set().union(*sets.values())
    intersection = set.intersection(*sets.values())

    if union != set(keys):
        raise BatchError("the union of the reviewer files is not the selected batch")
    if len(union) != len(set(keys)):
        raise BatchError(
            f"the union has {len(union)} units, expected {len(set(keys))}"
        )
    if intersection != set(overlap_keys):
        raise BatchError(
            "the intersection of the reviewer files is not the overlap set"
        )

    # The four private-count clauses.
    for reviewer, quotas in spec.private_quotas.items():
        private = sets[reviewer] - intersection
        for retriever, expected in quotas.items():
            actual = sum(1 for key in private if key[1] == retriever)
            if actual != expected:
                raise BatchError(
                    f"{reviewer} has {actual} private {retriever} units, "
                    f"expected {expected}"
                )

    # Every non-overlap unit appears in exactly one file.
    for key in union - intersection:
        holders = [reviewer for reviewer, unit_keys in sets.items() if key in unit_keys]
        if len(holders) != 1:
            raise BatchError(
                f"non-overlap unit {key} appears in {len(holders)} files, expected 1"
            )

    # The union carries the exact section 3.1 quotas and the intersection the
    # exact section 3.2 quotas.
    quotas_by_stratum = {
        (retriever, question_type): quota
        for retriever, question_type, quota in spec.strata
    }
    union_strata = _count_by_stratum(union, keys, spec)
    if union_strata != quotas_by_stratum:
        raise BatchError(
            f"union strata {union_strata} do not match the frozen quotas "
            f"{quotas_by_stratum}"
        )
    overlap_strata = _count_by_stratum(intersection, keys, spec)
    expected_overlap = {
        stratum: spec.overlap_per_stratum for stratum in quotas_by_stratum
    }
    if overlap_strata != expected_overlap:
        raise BatchError(
            f"overlap strata {overlap_strata} do not match {expected_overlap}"
        )


# --------------------------------------------------------------------------- #
# Artifact assembly
# --------------------------------------------------------------------------- #

def build_reviewer_file(reviewer_id, unit_keys, cases, spec):
    """One closed reviewer object (section 4).

    It contains no notes from either reviewer and no case assigned only to the
    other reviewer.

    Each case is deep-copied in. An overlap unit therefore becomes two
    independent objects rather than one object referenced twice: the two files
    must be *equal*, and proving that is the job of
    `validate_overlap_content_identical`. Sharing one object would make that
    check pass by construction and would also let a later in-place edit to one
    reviewer's cases silently rewrite the other's.
    """
    payload = {
        "batch_id": spec.batch_id,
        "reviewer_id": reviewer_id,
        "run_id": spec.run_id,
        "review_cutoff": spec.review_cutoff,
        "cases": [copy.deepcopy(cases[key]) for key in unit_keys],
    }
    if tuple(payload) != REVIEWER_FILE_FIELDS:
        raise BatchError(f"reviewer file field order drifted: {tuple(payload)}")
    return payload


def build_assignment_rows(keys, overlap_keys, per_reviewer, cases, spec):
    """The compact record of the split (section 4).

    An overlap unit has two rows, one for each reviewer; a non-overlap unit has
    one. Rows follow the canonical batch order, and an overlap unit's two rows
    follow the fixed reviewer order.
    """
    holders: Dict[Tuple[str, str], list] = {}
    for reviewer in spec.reviewer_order:
        for key in per_reviewer[reviewer]:
            holders.setdefault(key, []).append(reviewer)

    overlap = set(overlap_keys)
    rows = []
    for key in keys:
        case = cases[key]
        for reviewer in holders.get(key, ()):
            rows.append(
                {
                    "run_id": spec.run_id,
                    "example_id": case["example_id"],
                    "retriever": case["retriever"],
                    "question_type": case["question_type"],
                    "assigned_reviewer": reviewer,
                    "is_overlap": "true" if key in overlap else "false",
                }
            )
    expected_rows = len(keys) + len(overlap)
    if len(rows) != expected_rows:
        raise BatchError(
            f"assignment.csv would have {len(rows)} rows, expected {expected_rows}"
        )
    return rows


def validate_overlap_content_identical(reviewer_files, overlap_keys):
    """Overlap case objects must be identical across the two reviewer files.

    Only the top-level `reviewer_id` may differ, so the comparison is made on
    the serialized case bytes.
    """
    overlap = set(overlap_keys)
    serialized = {}
    for payload in reviewer_files.values():
        for case in payload["cases"]:
            key = (case["example_id"], case["retriever"])
            if key not in overlap:
                continue
            blob = json.dumps(case, ensure_ascii=False, sort_keys=False)
            if key in serialized and serialized[key] != blob:
                raise BatchError(
                    f"overlap case {key} differs between the two reviewer files"
                )
            serialized[key] = blob
    if set(serialized) != overlap:
        raise BatchError(
            f"expected {len(overlap)} overlap cases in both files, "
            f"found {len(serialized)}"
        )


def _key_set_error(mapping, expected):
    """Describe how `mapping`'s key set differs from `expected`, or return None.

    Key SET equality, not key-order equality. Order is enforced separately, where
    it actually matters: `build_reviewer_file` and `build_case` assert the
    serialization order, because that is what makes an overlap case byte-identical
    in both files. A validator that also rejected key order would be wrong for a
    file that arrived by ordinary exchange, since JSON object member order carries
    no meaning.
    """
    allowed = set(expected)
    missing = [field for field in expected if field not in mapping]
    unexpected = [key for key in mapping if key not in allowed]
    if missing:
        return "is missing " + ", ".join(missing)
    if unexpected:
        return (
            "carries unexpected field(s) "
            + ", ".join(unexpected)
            + "; the shape is closed"
        )
    return None


def validate_closed_shapes(reviewer_files):
    """Each reviewer file and each case is a closed object (section 4).

    The key set must EQUAL the frozen field set. Checking only that the frozen
    fields are present is a strictly weaker contract: it accepts a reviewer file
    carrying extra top-level material, and it accepts a case carrying a `notes`
    field, which directly contradicts section 4's statement that the file
    contains no notes from either reviewer.
    """
    for reviewer, payload in reviewer_files.items():
        if not isinstance(payload, dict):
            raise BatchError(f"{reviewer}: the reviewer file must be one JSON object")
        problem = _key_set_error(payload, REVIEWER_FILE_FIELDS)
        if problem is not None:
            raise BatchError(f"{reviewer}: the reviewer file {problem}")
        for case in payload["cases"]:
            if not isinstance(case, dict):
                raise BatchError(f"{reviewer}: a case is not an object")
            key = (case.get("example_id"), case.get("retriever"))
            # Named before the general shape check so the human-label defect —
            # the one place a machine-authored failure cause could appear — keeps
            # its own diagnostic.
            if "label" in case:
                raise BatchError(
                    f"case {key} carries a `label` field; the human failure label "
                    "is authored in the review page, never pre-filled here"
                )
            problem = _key_set_error(case, CASE_FIELDS)
            if problem is not None:
                raise BatchError(f"case {key} {problem}")


def validate_batch(reviewer_files, keys, overlap_keys, patterns, spec):
    """Run every artifact-level check section 9 names.

    Called on the built objects, so it validates what would actually be written.
    """
    validate_closed_shapes(reviewer_files)
    if set(reviewer_files) != set(REVIEWER_IDS):
        raise BatchError(
            f"expected the frozen reviewer set {', '.join(REVIEWER_IDS)}, "
            f"got {', '.join(sorted(reviewer_files))}"
        )
    per_reviewer = {
        reviewer: [
            (case["example_id"], case["retriever"]) for case in payload["cases"]
        ]
        for reviewer, payload in reviewer_files.items()
    }
    validate_assignment(per_reviewer, overlap_keys, keys, spec)
    validate_overlap_content_identical(reviewer_files, overlap_keys)

    overlap = set(overlap_keys)
    for reviewer, payload in reviewer_files.items():
        if payload["batch_id"] != spec.batch_id:
            raise BatchError(f"{reviewer}: batch_id must be {spec.batch_id!r}")
        if payload["run_id"] != spec.run_id:
            raise BatchError(f"{reviewer}: run_id must be {spec.run_id!r}")
        # Two independent conditions: the identity must be one of the frozen two
        # reviewers, and it must be the reviewer whose file this is. A
        # syntactically valid third identity such as `alice` fails the first even
        # when the file is otherwise perfectly formed.
        if payload["reviewer_id"] not in REVIEWER_IDS:
            raise BatchError(
                f"{reviewer}: reviewer_id must be one of "
                f"{', '.join(REVIEWER_IDS)}, got {payload['reviewer_id']!r}"
            )
        if payload["reviewer_id"] != reviewer:
            raise BatchError(f"{reviewer}: reviewer_id is {payload['reviewer_id']!r}")
        file_cutoff = payload["review_cutoff"]
        if isinstance(file_cutoff, bool) or file_cutoff != spec.review_cutoff:
            raise BatchError(
                f"{reviewer}: file-level review_cutoff must be {spec.review_cutoff}"
            )
        validate_review_cutoff(payload["cases"], spec)
        validate_rank_pattern_binding(payload["cases"], patterns)
        for case in payload["cases"]:
            key = (case["example_id"], case["retriever"])
            if not isinstance(case["is_overlap"], bool):
                raise BatchError(f"case {key}: is_overlap must be a boolean")
            if case["is_overlap"] != (key in overlap):
                raise BatchError(
                    f"case {key}: is_overlap is {case['is_overlap']} but the unit "
                    f"{'is' if key in overlap else 'is not'} an overlap unit"
                )
            # The `label` field and every other foreign field were already
            # rejected by validate_closed_shapes above.


# --------------------------------------------------------------------------- #
# Writing (protocol sections 2.1 / 9)
# --------------------------------------------------------------------------- #

def _protected_run_paths(run_dir):
    """The read-only source run's own artifacts."""
    return tuple(
        os.path.join(run_dir, name)
        for name in ("config.json", "details.jsonl", "metrics.json",
                     RANK_PATTERN_SOURCE_NAME, "failures_review.html")
    )


def _is_inside(candidate, container):
    """True when `candidate` resolves to `container` or somewhere beneath it.

    Compares case-normalized real paths so a symlink, a case-only alias, or a
    `..` segment cannot smuggle an output path into the read-only run.
    """
    candidate_real = os.path.normcase(os.path.realpath(candidate))
    container_real = os.path.normcase(os.path.realpath(container))
    if candidate_real == container_real:
        return True
    return candidate_real.startswith(container_real + os.sep)


def validate_output_dir(out_dir, run_dir):
    """Refuse an output directory that would write inside the read-only run."""
    if _is_inside(out_dir, run_dir):
        raise BatchError(
            f"refusing to write inside the read-only source run: {out_dir} is "
            f"within {run_dir}"
        )
    for protected in _protected_run_paths(run_dir):
        candidate = os.path.join(out_dir, os.path.basename(protected))
        if bfr._is_input_alias(candidate, (protected,)):
            raise BatchError(
                f"refusing to overwrite a source-run artifact: {protected}"
            )


def write_json(path, payload):
    """Write pretty-printed JSON with LF line endings and a trailing newline."""
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def write_assignment_csv(path, rows, columns=ASSIGNMENT_COLUMNS):
    """Write the assignment record as UTF-8 (no BOM), LF-terminated CSV."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[column] for column in columns])


def write_page(path, text):
    """Write the shared review page with LF line endings."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


# --------------------------------------------------------------------------- #
# Top-level generation
# --------------------------------------------------------------------------- #

class Batch(NamedTuple):
    """Everything one generation produced, before anything is written."""

    reviewer_files: Dict[str, dict]
    assignment_rows: Sequence[dict]
    keys: Tuple[Tuple[str, str], ...]
    overlap_keys: Tuple[Tuple[str, str], ...]
    patterns: Mapping[Tuple[str, str], str]


def build_batch(run_dir, spec=V1_SPEC):
    """Load the read-only source and build every artifact object.

    Writes nothing, so this is also the `--check-only` path.
    """
    config_path = os.path.join(run_dir, "config.json")
    details_path = os.path.join(run_dir, "details.jsonl")
    patterns_path = os.path.join(run_dir, RANK_PATTERN_SOURCE_NAME)

    for path in (config_path, details_path, patterns_path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"source run file not found: {path}")

    run_id = os.path.basename(os.path.normpath(run_dir))
    if run_id != spec.run_id:
        raise BatchError(
            f"this batch is frozen against run {spec.run_id!r}, not {run_id!r}"
        )

    config = bfr.load_config(config_path, run_id)
    records = bfr.load_details(details_path, config)
    patterns = load_rank_pattern_source(patterns_path, run_id=run_id)

    strata = eligible_strata(records, spec.review_cutoff)
    verify_eligible_population(strata, spec)

    selected = select_batch(strata, spec)
    keys = selected_keys(selected)
    overlap_keys = select_overlap(selected, spec)
    verify_selection_oracle(keys, overlap_keys, spec)

    cases = build_cases(records, keys, overlap_keys, patterns, spec)

    private_keys = [key for key in keys if key not in set(overlap_keys)]
    assignment = split_private_units(private_keys, spec)
    per_reviewer = reviewer_keys(assignment, overlap_keys, keys)

    reviewer_files = {
        reviewer: build_reviewer_file(reviewer, unit_keys, cases, spec)
        for reviewer, unit_keys in per_reviewer.items()
    }
    validate_batch(reviewer_files, keys, overlap_keys, patterns, spec)

    rows = build_assignment_rows(keys, overlap_keys, per_reviewer, cases, spec)
    return Batch(reviewer_files, rows, keys, overlap_keys, patterns)


def generate_batch(run_id=None, runs_root=os.path.join("results", "runs"),
                   out_dir=None, check_only=False, spec=V1_SPEC):
    """Full pipeline: load the read-only run, build, validate, write.

    Returns the list of written paths (empty for `check_only`).
    """
    run_id = spec.run_id if run_id is None else run_id
    bfr.validate_run_id_arg(run_id)
    run_dir = os.path.join(runs_root, run_id)
    if not os.path.isdir(run_dir):
        raise FileNotFoundError(f"run directory not found: {run_dir}")

    batch = build_batch(run_dir, spec)
    if check_only:
        return []

    out_dir = DEFAULT_OUTPUT_DIR if out_dir is None else out_dir
    validate_output_dir(out_dir, run_dir)
    os.makedirs(out_dir, exist_ok=True)

    written = []
    assignment_path = os.path.join(out_dir, ASSIGNMENT_NAME)
    write_assignment_csv(assignment_path, batch.assignment_rows)
    written.append(assignment_path)

    for reviewer, payload in sorted(batch.reviewer_files.items()):
        path = os.path.join(out_dir, reviewer_file_name(reviewer))
        write_json(path, payload)
        written.append(path)

    page_path = os.path.join(out_dir, PAGE_NAME)
    write_page(page_path, render_page())
    written.append(page_path)
    return written


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Build the manual_review_v1 calibration/open-coding batch "
        "from the read-only formal run: assignment.csv, both reviewer case JSON "
        "files, and the one shared file-picker review page."
    )
    parser.add_argument(
        "--run",
        dest="run_id",
        default=SOURCE_RUN_ID,
        help=f"Read-only source run directory name (default: {SOURCE_RUN_ID})",
    )
    parser.add_argument(
        "--runs-root",
        default=os.path.join("results", "runs"),
        help="Root directory that run directories live under",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Build and validate the batch without writing anything",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    written = generate_batch(
        run_id=args.run_id,
        runs_root=args.runs_root,
        out_dir=args.out_dir,
        check_only=args.check_only,
    )
    if args.check_only:
        print(
            f"Validated the {BATCH_ID} batch against the frozen contracts; "
            "wrote nothing."
        )
    else:
        for path in written:
            print(f"Wrote {path}")
    return written


if __name__ == "__main__":
    try:
        main()
    except (BatchError, ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
