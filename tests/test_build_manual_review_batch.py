"""
test_build_manual_review_batch.py

Acceptance tests for the manual_review_v1 batch extractor
(scripts/build_manual_review_batch.py), covering the validation list in section
9 of docs/specs/2026-07-27-manual-failure-review-course-protocol.md.

Four contracts are non-negotiable, and each is exercised through **both halves**
of its named paired controls: the legal control must be accepted and every named
rejection must be rejected. Each rejection differs from its legal control in
exactly one property, so a validator that accepts both halves of a pair has not
implemented that contract.

    AS-OK-1 / AS-NO-1..4     the complete assignment predicate (section 3.3),
                             including the four reviewer-private retriever counts
    SS-OK-1..2 / SS-NO-1..4  the frozen selection algorithm and oracle
                             (sections 3.1.1 / 3.4)
    RP-OK-1 / RP-NO-1..6     the exact rank_pattern source binding (section 4.1)
    RC-OK-1 / RC-NO-1..3     the exact per-case review_cutoff storage (section 4.2)

Most tests run the real validators over a **synthetic** source run with its own
population, quota table, and workload split, so a check that had quietly
hardcoded the v1 numbers cannot pass vacuously here. They need no model, no
network, and no HotpotQA download.

A separate group is gated on the presence of the real
`results/runs/2026-07-17_a/` and asserts the frozen 30-key oracle, the frozen
eligible population, repeat-generation stability, and that the read-only source
run is byte-for-byte unchanged after generation.
"""

import copy
import csv
import hashlib
import io
import json
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from scripts import build_manual_review_batch as mrb
from scripts import manual_review_page as page
from src.rank_pattern import CANONICAL_RANK_PATTERNS

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FORMAL_RUN_DIR = os.path.join(REPO_ROOT, "results", "runs", mrb.SOURCE_RUN_ID)

requires_formal_run = pytest.mark.skipif(
    not os.path.isdir(FORMAL_RUN_DIR),
    reason=f"the read-only source run results/runs/{mrb.SOURCE_RUN_ID}/ is absent",
)


# --------------------------------------------------------------------------- #
# A synthetic source run with its own frozen numbers
# --------------------------------------------------------------------------- #

SYNTH_RUN_ID = "2026-01-02_a"
RETRIEVERS = ("bm25", "dense")

# Deliberately different from v1 in every dimension: population, quotas, batch
# size, and the workload split.
SYNTH_ELIGIBLE = {
    ("bm25", "bridge"): 20,
    ("bm25", "comparison"): 8,
    ("dense", "bridge"): 18,
    ("dense", "comparison"): 6,
}
SYNTH_STRATA = (
    ("bm25", "bridge", 5),
    ("bm25", "comparison", 2),
    ("dense", "bridge", 5),
    ("dense", "comparison", 2),
)
# 14 units, 4 overlap, 10 private -> 5 private per reviewer. The private pools
# are odd (5 per retriever), like v1's 13, so the asymmetric split is reachable
# and the AS-NO-2 quota swap is actually detectable.
SYNTH_PRIVATE_QUOTAS = {
    "xin": {"bm25": 3, "dense": 2},
    "jiajun": {"bm25": 2, "dense": 3},
}


def _synth_example_id(index):
    """A source-run-shaped 24-hex-character example id."""
    return f"{index:024x}"


def _top_k(gold_positions, depth=50):
    """A 50-long ranked list; gold titles are placed at the given 1-based ranks."""
    results = []
    for rank in range(1, depth + 1):
        title = gold_positions.get(rank, f"Distractor {rank}")
        results.append(
            {
                "rank": rank,
                "title": title,
                "score": round(1.0 - rank / 100.0, 6),
                "text": f"Passage text for {title} at rank {rank}.",
            }
        )
    return results


def _retriever_record(gold_titles, ranks, depth=50):
    """One `retrievers.<name>` sub-record with the metrics the loader requires."""
    placed = {rank: title for title, rank in zip(gold_titles, ranks) if rank is not None}
    gold_ranks = {title: rank for title, rank in zip(gold_titles, ranks)}
    metrics = {
        f"any_evidence_recall@{k}": any(r is not None and r <= k for r in ranks)
        for k in (2, 5, 10)
    }
    return {"top_k": _top_k(placed, depth), "gold_ranks": gold_ranks, "metrics": metrics}


def _ranks_for(eligible, index):
    """Gold ranks that are a strict Any@5 failure, or a hit, deterministically."""
    if eligible:
        # Both golds below the cutoff: one deep in 11-50, one absent entirely.
        return [11 + (index % 30), None]
    # One gold inside the top 5, so the unit is not a strict Any@5 failure.
    return [1 + (index % 5), 12]


PATTERN_COLUMNS = ("run_id", "example_id", "retriever", "rank_pattern")


def write_pattern_csv(path, rows, columns=PATTERN_COLUMNS):
    with io.open(str(path), "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[column] for column in columns])


def build_synthetic_run(tmp_path, eligible=SYNTH_ELIGIBLE, extra_hits=3):
    """Write a synthetic run directory satisfying the accepted input contract.

    Every example carries both retrievers, and a unit is made eligible or not per
    retriever, so the same example can be a strict Any@5 failure under BM25 and a
    hit under Dense — as the real run behaves. Neighbouring rank-pattern rows get
    *different* valid labels, which is what makes the RP-NO-1 swap control and
    the RP-NO-6 example_id-only-join control meaningful.
    """
    run_dir = tmp_path / SYNTH_RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)

    records = []
    index = 0
    for question_type in ("bridge", "comparison"):
        needed = {r: eligible[(r, question_type)] for r in RETRIEVERS}
        for row in range(max(needed.values()) + extra_hits):
            index += 1
            example_id = _synth_example_id(index)
            gold_titles = sorted([f"Gold A {example_id}", f"Gold B {example_id}"])
            records.append(
                {
                    "example_id": example_id,
                    "question": f"Synthetic question {index}?",
                    "question_type": question_type,
                    "gold_titles": gold_titles,
                    "retrievers": {
                        retriever: _retriever_record(
                            gold_titles, _ranks_for(row < needed[retriever], index)
                        )
                        for retriever in RETRIEVERS
                    },
                }
            )

    # The formal pooled run's stored top-50 union contains every selected gold
    # passage, even when that passage is absent for the unit being reviewed. Give
    # this offline fixture the same property by carrying each example's two gold
    # passages in the next example's non-gold rank-50 slots. This changes no
    # unit's own gold ranks or eligibility.
    for position, record in enumerate(records):
        carrier = records[(position + 1) % len(records)]
        for title, retriever in zip(record["gold_titles"], RETRIEVERS):
            carrier_item = carrier["retrievers"][retriever]["top_k"][49]
            carrier_item["title"] = title
            carrier_item["text"] = f"Ground-truth passage text for {title}."

    with io.open(str(run_dir / "details.jsonl"), "w", encoding="utf-8", newline="") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    config = {
        "run_id": SYNTH_RUN_ID,
        "n": len(records),
        "split": "validation",
        "corpus_setting": "pooled",
        "corpus_size": 1234,
        "top_k_max": 50,
        "retrievers": {"bm25": "rank_bm25.BM25Okapi", "dense": "fake-encoder"},
        "timestamp": "2026-01-02T00:00:00",
        "script": "tests/test_build_manual_review_batch.py",
        "git_commit": None,
    }
    with io.open(str(run_dir / "config.json"), "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(config, ensure_ascii=False, indent=2) + "\n")

    pattern_rows = []
    for position, record in enumerate(records):
        for offset, retriever in enumerate(sorted(record["retrievers"])):
            pattern_rows.append(
                {
                    "run_id": SYNTH_RUN_ID,
                    "example_id": record["example_id"],
                    "retriever": retriever,
                    "rank_pattern": CANONICAL_RANK_PATTERNS[
                        (position * len(RETRIEVERS) + offset)
                        % len(CANONICAL_RANK_PATTERNS)
                    ],
                }
            )
    write_pattern_csv(run_dir / mrb.RANK_PATTERN_SOURCE_NAME, pattern_rows)
    return str(run_dir)


def _synth_spec(run_dir):
    """A BatchSpec for the synthetic run, with its oracle taken from one draw.

    The oracle has to come from an actual run of the frozen algorithm, exactly as
    the v1 oracle in the protocol did; the point of the SS controls below is that
    a *different* procedure then fails to reproduce it.
    """
    provisional = mrb.BatchSpec(
        batch_id="synthetic_review_v1",
        run_id=SYNTH_RUN_ID,
        review_cutoff=5,
        seed=mrb.SELECTION_SEED,
        strata=SYNTH_STRATA,
        overlap_per_stratum=1,
        eligible_population=SYNTH_ELIGIBLE,
        private_quotas=SYNTH_PRIVATE_QUOTAS,
        selected_keys=(),
        overlap_keys=(),
    )
    strata = mrb.eligible_strata(_load_records(run_dir), provisional.review_cutoff)
    selected = mrb.select_batch(strata, provisional)
    return provisional._replace(
        selected_keys=mrb.selected_keys(selected),
        overlap_keys=mrb.select_overlap(selected, provisional),
    )


def _load_records(run_dir):
    config = mrb.bfr.load_config(os.path.join(run_dir, "config.json"), SYNTH_RUN_ID)
    return mrb.bfr.load_details(os.path.join(run_dir, "details.jsonl"), config)


@pytest.fixture
def synthetic_run(tmp_path):
    return build_synthetic_run(tmp_path)


@pytest.fixture
def spec(synthetic_run):
    return _synth_spec(synthetic_run)


@pytest.fixture
def batch(synthetic_run, spec):
    return mrb.build_batch(synthetic_run, spec)


def _per_reviewer(reviewer_files):
    return {
        reviewer: [(c["example_id"], c["retriever"]) for c in payload["cases"]]
        for reviewer, payload in reviewer_files.items()
    }


def _all_cases(reviewer_files):
    """One case object per unique unit across both reviewer files."""
    unique = {}
    for payload in reviewer_files.values():
        for case in payload["cases"]:
            unique[(case["example_id"], case["retriever"])] = case
    return list(unique.values())


# ─────────────────────────── the synthetic run itself ────────────────────────

def test_the_synthetic_run_reproduces_its_declared_eligible_population(
    synthetic_run, spec
):
    """A fixture that silently drifted would make every control below vacuous."""
    strata = mrb.eligible_strata(_load_records(synthetic_run), spec.review_cutoff)
    assert {key: len(ids) for key, ids in strata.items()} == dict(SYNTH_ELIGIBLE)
    mrb.verify_eligible_population(strata, spec)


def test_the_synthetic_spec_differs_from_the_v1_spec():
    """Otherwise these tests would only prove the v1 numbers agree with themselves."""
    assert SYNTH_STRATA != mrb.STRATA
    assert dict(SYNTH_ELIGIBLE) != dict(mrb.ELIGIBLE_POPULATION)
    assert SYNTH_PRIVATE_QUOTAS != mrb.PRIVATE_QUOTAS


def test_strict_any5_eligibility_reads_the_stored_gold_ranks():
    """Neither gold within the cutoff; an absent gold is also a miss."""
    titles = ["A", "B"]
    assert mrb.is_strict_any5_failure(titles, {"A": None, "B": None})
    assert mrb.is_strict_any5_failure(titles, {"A": 6, "B": 40})
    assert mrb.is_strict_any5_failure(titles, {"A": None, "B": 6})
    assert not mrb.is_strict_any5_failure(titles, {"A": 5, "B": None})
    assert not mrb.is_strict_any5_failure(titles, {"A": 1, "B": 2})
    assert not mrb.is_strict_any5_failure(titles, {"A": None, "B": 3})


def test_an_eligible_population_that_drifts_is_rejected(spec):
    drifted = {key: ["x"] * (count + 1) for key, count in SYNTH_ELIGIBLE.items()}
    with pytest.raises(mrb.BatchError, match="eligible population"):
        mrb.verify_eligible_population(drifted, spec)


def test_a_run_directory_the_batch_is_not_frozen_against_is_rejected(synthetic_run, spec):
    with pytest.raises(mrb.BatchError, match="frozen against run"):
        mrb.build_batch(synthetic_run, spec._replace(run_id="1999-01-01_z"))


# ───────────────── SS: the frozen selection algorithm and oracle ─────────────

def test_ss_ok_1_repeat_generation_is_identical(synthetic_run, spec):
    """SS-OK-1: run the algorithm twice; keys, overlap keys, and order match."""
    strata = mrb.eligible_strata(_load_records(synthetic_run), spec.review_cutoff)
    first, second = mrb.select_batch(strata, spec), mrb.select_batch(strata, spec)
    assert mrb.selected_keys(first) == mrb.selected_keys(second)
    assert mrb.select_overlap(first, spec) == mrb.select_overlap(second, spec)
    assert mrb.selected_keys(first) == spec.selected_keys


def test_ss_ok_2_a_generated_batch_matches_the_frozen_oracle(batch, spec):
    """SS-OK-2: comparing a generated batch against the frozen lists succeeds."""
    mrb.verify_selection_oracle(batch.keys, batch.overlap_keys, spec)


def test_ss_no_1_shuffle_then_slice_is_a_different_draw(spec):
    """SS-NO-1: `shuffle` then take the first `quota` selects other units.

    Named in the protocol because it is an ordinary reading of "seeded with
    6120" that picks a different sample — here, a disjoint one.
    """
    ids = sorted(f"id-{n:03d}" for n in range(51))
    frozen = mrb.draw_stratum(ids, 12, seed=spec.seed)

    shuffled = list(ids)
    random.Random(spec.seed).shuffle(shuffled)
    sliced = sorted(shuffled[:12])

    assert frozen != sliced
    assert not (set(frozen) & set(sliced)), "on this population the two draws are disjoint"

    oracle = spec._replace(
        selected_keys=tuple((i, "bm25") for i in frozen), overlap_keys=()
    )
    mrb.verify_selection_oracle(oracle.selected_keys, (), oracle)
    with pytest.raises(mrb.BatchError, match="do not reproduce the frozen oracle"):
        mrb.verify_selection_oracle(tuple((i, "bm25") for i in sliced), (), oracle)


def test_ss_no_2_one_shared_generator_across_strata_is_a_different_draw(
    synthetic_run, spec
):
    """SS-NO-2: strata must reset the generator; one shared stream differs."""
    strata = mrb.eligible_strata(_load_records(synthetic_run), spec.review_cutoff)

    shared_rng = random.Random(spec.seed)
    shared = []
    for retriever, question_type, quota in spec.strata:
        drawn = sorted(shared_rng.sample(strata[(retriever, question_type)], quota))
        shared.extend((example_id, retriever) for example_id in drawn)

    assert tuple(shared) != spec.selected_keys
    with pytest.raises(mrb.BatchError, match="do not reproduce the frozen oracle"):
        mrb.verify_selection_oracle(tuple(shared), spec.overlap_keys, spec)


def test_ss_no_3_another_stratum_order_is_rejected(batch, spec):
    """SS-NO-3: the output order is frozen, not only the membership."""
    reordered = tuple(reversed(batch.keys))
    assert set(reordered) == set(batch.keys)
    with pytest.raises(mrb.BatchError, match="do not reproduce the frozen oracle"):
        mrb.verify_selection_oracle(reordered, batch.overlap_keys, spec)


def test_ss_no_4_the_overlap_draw_only_sees_the_selected_batch(synthetic_run, spec):
    """SS-NO-4, part 1: the draw is a pure function of the selected batch.

    The protocol records SS-NO-4 as a procedural requirement verified by reading
    the generator, because on the real run the non-conforming reading happens to
    produce the same four keys. The structural half of that requirement is
    executable: `select_overlap` is handed only the selected batch, so no change
    to the eligible population can move the draw, and its result therefore can
    never be a unit that was not assigned.
    """
    strata = mrb.eligible_strata(_load_records(synthetic_run), spec.review_cutoff)
    selected = mrb.select_batch(strata, spec)
    conforming = mrb.select_overlap(selected, spec)
    assert set(conforming) <= set(mrb.selected_keys(selected))

    # The draw's only input is the selected batch, so the same selection yields
    # the same overlap no matter what the eligible population was.
    hand_made = [(retriever, qt, list(drawn)) for retriever, qt, drawn in selected]
    assert mrb.select_overlap(hand_made, spec) == conforming

    # Every drawn unit comes from its own stratum's selected list.
    for (example_id, retriever), (stratum_retriever, _qt, drawn) in zip(
        conforming, selected
    ):
        assert retriever == stratum_retriever
        assert example_id in drawn


def test_ss_no_4_a_full_population_overlap_draw_is_rejected_where_it_differs(spec):
    """SS-NO-4, part 2: where the two readings differ, the oracle rejects the wrong one.

    On the real run's four strata the non-conforming reading coincides with the
    frozen one, so the divergence is demonstrated on a stratum where it does not.
    ``(population 10, quota 4)`` is such a case: drawing one unit from the whole
    sorted population and drawing one from the sorted selected batch pick
    different units, and the oracle comparison rejects the second.
    """
    ids = sorted(f"id-{n:03d}" for n in range(10))
    selected = [("bm25", "bridge", mrb.draw_stratum(ids, 4, seed=spec.seed))]
    oracle = spec._replace(
        strata=(("bm25", "bridge", 4),),
        selected_keys=mrb.selected_keys(selected),
    )
    conforming = mrb.select_overlap(selected, oracle)
    non_conforming = (
        (random.Random(oracle.seed).sample(ids, 1)[0], "bm25"),
    )

    assert non_conforming != conforming, "this population must expose the divergence"
    frozen = oracle._replace(overlap_keys=conforming)
    mrb.verify_selection_oracle(frozen.selected_keys, conforming, frozen)
    with pytest.raises(mrb.BatchError, match="overlap unit keys do not reproduce"):
        mrb.verify_selection_oracle(frozen.selected_keys, non_conforming, frozen)


def test_a_frozen_oracle_with_a_duplicate_key_is_rejected(spec):
    doubled = spec.selected_keys + (spec.selected_keys[0],)
    with pytest.raises(mrb.BatchError, match="duplicate unit key"):
        mrb.verify_selection_oracle(doubled, spec.overlap_keys,
                                    spec._replace(selected_keys=doubled))


def test_a_frozen_overlap_outside_the_selected_batch_is_rejected(spec):
    stray = (("ffffffffffffffffffffffff", "bm25"),)
    broken = spec._replace(overlap_keys=stray)
    with pytest.raises(mrb.BatchError, match="not in the selected batch"):
        mrb.verify_selection_oracle(spec.selected_keys, stray, broken)


def test_a_quota_larger_than_its_stratum_is_rejected():
    with pytest.raises(mrb.BatchError, match="exceeds the stratum"):
        mrb.draw_stratum(["a", "b"], 3)


# ─────────────────── AS: the complete assignment predicate ───────────────────

def test_as_ok_1_the_frozen_split_is_accepted(batch, spec):
    """AS-OK-1: the frozen private quotas with valid union and overlap strata."""
    mrb.validate_assignment(
        _per_reviewer(batch.reviewer_files), batch.overlap_keys, batch.keys, spec
    )


def test_as_no_1_all_of_one_retriever_to_one_reviewer_is_rejected(batch, spec):
    """AS-NO-1: differs from AS-OK-1 in exactly one property — the private split.

    Every file size, the union, the intersection, and both strata tables stay
    exactly correct, so a predicate missing the private-count clauses accepts it.
    """
    overlap = list(batch.overlap_keys)
    private = [key for key in batch.keys if key not in set(overlap)]
    illegal = {
        "xin": overlap + [k for k in private if k[1] == "bm25"],
        "jiajun": overlap + [k for k in private if k[1] == "dense"],
    }

    # Confirm the illegal split really is adjacent on every other clause.
    legal = _per_reviewer(batch.reviewer_files)
    assert {r: len(v) for r, v in illegal.items()} == {r: len(v) for r, v in legal.items()}
    assert set(illegal["xin"]) | set(illegal["jiajun"]) == set(batch.keys)
    assert set(illegal["xin"]) & set(illegal["jiajun"]) == set(overlap)

    with pytest.raises(mrb.BatchError, match="private"):
        mrb.validate_assignment(illegal, batch.overlap_keys, batch.keys, spec)


def test_as_no_2_swapped_reviewer_quotas_are_rejected(batch, spec):
    """AS-NO-2: the two reviewers' private quotas exchanged."""
    legal = _per_reviewer(batch.reviewer_files)
    swapped = {"xin": legal["jiajun"], "jiajun": legal["xin"]}
    with pytest.raises(mrb.BatchError, match="private"):
        mrb.validate_assignment(swapped, batch.overlap_keys, batch.keys, spec)


def test_as_no_3_moving_one_private_unit_unbalances_the_files(batch, spec):
    """AS-NO-3: one private unit moved, so the two file sizes differ by two."""
    per_reviewer = {r: list(v) for r, v in _per_reviewer(batch.reviewer_files).items()}
    overlap = set(batch.overlap_keys)
    moved = next(key for key in per_reviewer["xin"] if key not in overlap)
    per_reviewer["xin"].remove(moved)
    per_reviewer["jiajun"].append(moved)
    with pytest.raises(mrb.BatchError, match="units, expected"):
        mrb.validate_assignment(per_reviewer, batch.overlap_keys, batch.keys, spec)


def test_as_no_4_an_extra_unit_in_both_files_is_rejected(batch, spec):
    """AS-NO-4: one more unit placed in both files, so the overlap is one too many."""
    per_reviewer = {r: list(v) for r, v in _per_reviewer(batch.reviewer_files).items()}
    overlap = set(batch.overlap_keys)
    extra = next(key for key in per_reviewer["xin"] if key not in overlap)
    per_reviewer["jiajun"].append(extra)
    with pytest.raises(mrb.BatchError):
        mrb.validate_assignment(per_reviewer, batch.overlap_keys, batch.keys, spec)


def test_a_duplicate_unit_inside_one_file_is_rejected(batch, spec):
    per_reviewer = {r: list(v) for r, v in _per_reviewer(batch.reviewer_files).items()}
    per_reviewer["xin"].append(per_reviewer["xin"][0])
    with pytest.raises(mrb.BatchError, match="more than once"):
        mrb.validate_assignment(per_reviewer, batch.overlap_keys, batch.keys, spec)


def test_an_unexpected_reviewer_set_is_rejected(batch, spec):
    per_reviewer = _per_reviewer(batch.reviewer_files)
    per_reviewer = {"xin": per_reviewer["xin"], "someone_else": per_reviewer["jiajun"]}
    with pytest.raises(mrb.BatchError, match="expected reviewers"):
        mrb.validate_assignment(per_reviewer, batch.overlap_keys, batch.keys, spec)


def test_the_private_split_is_deterministic_and_meets_the_quota_table(batch, spec):
    """The dealing rule reaches the frozen counts and repeats exactly."""
    overlap = set(batch.overlap_keys)
    private = [key for key in batch.keys if key not in overlap]
    first = mrb.split_private_units(private, spec)
    assert first == mrb.split_private_units(private, spec)
    for reviewer, quotas in spec.private_quotas.items():
        for retriever, expected in quotas.items():
            assert sum(1 for key in first[reviewer] if key[1] == retriever) == expected


def test_the_private_split_mixes_question_types_for_each_reviewer(batch, spec):
    """Dealing alternately, not slicing, so neither reviewer gets one type only."""
    stratum_of = mrb._stratum_index(batch.keys, spec)
    overlap = set(batch.overlap_keys)
    private = [key for key in batch.keys if key not in overlap]
    assignment = mrb.split_private_units(private, spec)
    for keys in assignment.values():
        types = {stratum_of[key][1] for key in keys}
        assert types == {"bridge", "comparison"}


def test_a_private_split_that_cannot_meet_the_quota_table_is_rejected(spec):
    """An unreachable quota table fails loudly instead of dealing silently."""
    private = [(f"{n:024x}", "bm25") for n in range(5)]
    impossible = spec._replace(
        strata=(("bm25", "bridge", 5),),
        private_quotas={"xin": {"bm25": 4}, "jiajun": {"bm25": 1}},
    )
    with pytest.raises(mrb.BatchError, match="frozen quota"):
        mrb.split_private_units(private, impossible)


# ─────────────────── RP: the exact rank_pattern source binding ───────────────

def test_rp_ok_1_each_case_carries_its_own_source_row(batch):
    """RP-OK-1: every rank_pattern copied from its own (example_id, retriever) row."""
    mrb.validate_rank_pattern_binding(_all_cases(batch.reviewer_files), batch.patterns)


def test_rp_no_1_two_units_with_swapped_valid_labels_are_rejected(batch):
    """RP-NO-1: two distinct valid labels exchanged — passes a vocabulary check."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    pair = next(
        (left, right)
        for i, left in enumerate(cases)
        for right in cases[i + 1:]
        if left["rank_pattern"] != right["rank_pattern"]
    )
    left, right = pair
    left["rank_pattern"], right["rank_pattern"] = (
        right["rank_pattern"], left["rank_pattern"]
    )
    # Both swapped values remain legal vocabulary members, so a vocabulary-only
    # check accepts this; the source binding must not.
    assert left["rank_pattern"] in CANONICAL_RANK_PATTERNS
    assert right["rank_pattern"] in CANONICAL_RANK_PATTERNS
    with pytest.raises(mrb.BatchError, match="does not equal its own"):
        mrb.validate_rank_pattern_binding(cases, batch.patterns)


def test_rp_no_2_a_different_valid_vocabulary_member_is_rejected(batch):
    """RP-NO-2: one case's label replaced by another legal label."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    cases[0]["rank_pattern"] = next(
        label for label in CANONICAL_RANK_PATTERNS if label != cases[0]["rank_pattern"]
    )
    with pytest.raises(mrb.BatchError, match="does not equal its own"):
        mrb.validate_rank_pattern_binding(cases, batch.patterns)


def test_rp_no_3_a_missing_source_row_is_rejected(batch):
    """RP-NO-3: a selected case whose source row is absent from the join."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    patterns = dict(batch.patterns)
    key = (cases[0]["example_id"], cases[0]["retriever"])
    del patterns[key]
    with pytest.raises(mrb.BatchError, match="does not exist"):
        mrb.validate_rank_pattern_binding(cases, patterns)
    with pytest.raises(mrb.BatchError, match="never a blank or inferred label"):
        mrb.bind_rank_pattern(key, patterns)


def test_rp_no_4_a_duplicated_case_key_is_rejected(batch):
    """RP-NO-4: one case key present twice."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    cases.append(copy.deepcopy(cases[0]))
    with pytest.raises(mrb.BatchError, match="more than once"):
        mrb.validate_rank_pattern_binding(cases, batch.patterns)


def test_rp_no_5_an_extra_key_not_in_the_source_is_rejected(batch):
    """RP-NO-5: an extra case whose key does not exist in the source file."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    ghost = copy.deepcopy(cases[0])
    ghost["example_id"] = _synth_example_id(999999)
    cases.append(ghost)
    with pytest.raises(mrb.BatchError, match="does not exist"):
        mrb.validate_rank_pattern_binding(cases, batch.patterns)


def test_rp_no_6_matching_on_example_id_alone_is_rejected(batch):
    """RP-NO-6: an example_id-only join attaches BM25 structure to a Dense unit.

    Every synthetic example has a row under both retrievers with different
    labels, mirroring the one real example_id that was selected twice.
    """
    patterns = batch.patterns
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    target = next(
        case for case in cases
        if (case["example_id"], "bm25") in patterns
        and (case["example_id"], "dense") in patterns
        and patterns[(case["example_id"], "bm25")] != patterns[(case["example_id"], "dense")]
    )
    other = "dense" if target["retriever"] == "bm25" else "bm25"
    target["rank_pattern"] = patterns[(target["example_id"], other)]
    with pytest.raises(mrb.BatchError, match="does not equal its own"):
        mrb.validate_rank_pattern_binding(cases, patterns)


def test_a_duplicate_join_key_in_the_source_file_is_rejected(tmp_path):
    path = tmp_path / "patterns.csv"
    write_pattern_csv(path, [
        {"run_id": SYNTH_RUN_ID, "example_id": "a1", "retriever": "bm25",
         "rank_pattern": "both_not_in_top50"},
        {"run_id": SYNTH_RUN_ID, "example_id": "a1", "retriever": "bm25",
         "rank_pattern": "both_in_11_50"},
    ])
    with pytest.raises(mrb.BatchError, match="duplicate join key"):
        mrb.load_rank_pattern_source(str(path), run_id=SYNTH_RUN_ID)


def test_a_source_row_for_another_run_is_rejected(tmp_path):
    path = tmp_path / "patterns.csv"
    write_pattern_csv(path, [
        {"run_id": "1999-01-01_z", "example_id": "a1", "retriever": "bm25",
         "rank_pattern": "both_not_in_top50"},
    ])
    with pytest.raises(mrb.BatchError, match="run_id"):
        mrb.load_rank_pattern_source(str(path), run_id=SYNTH_RUN_ID)


def test_a_source_label_outside_the_accepted_vocabulary_is_rejected(tmp_path):
    path = tmp_path / "patterns.csv"
    write_pattern_csv(path, [
        {"run_id": SYNTH_RUN_ID, "example_id": "a1", "retriever": "bm25",
         "rank_pattern": "invented_pattern"},
    ])
    with pytest.raises(mrb.BatchError, match="not one of the accepted ten labels"):
        mrb.load_rank_pattern_source(str(path), run_id=SYNTH_RUN_ID)


def test_a_source_file_missing_a_required_column_is_rejected(tmp_path):
    path = tmp_path / "patterns.csv"
    write_pattern_csv(
        path,
        [{"run_id": SYNTH_RUN_ID, "example_id": "a1", "retriever": "bm25"}],
        columns=("run_id", "example_id", "retriever"),
    )
    with pytest.raises(mrb.BatchError, match="missing required column"):
        mrb.load_rank_pattern_source(str(path), run_id=SYNTH_RUN_ID)


# ────────────────── RC: the exact per-case review_cutoff storage ─────────────

def test_rc_ok_1_every_case_carries_the_integer_cutoff(batch, spec):
    """RC-OK-1: accepted."""
    mrb.validate_review_cutoff(_all_cases(batch.reviewer_files), spec)
    for payload in batch.reviewer_files.values():
        assert payload["review_cutoff"] == spec.review_cutoff
        assert not isinstance(payload["review_cutoff"], bool)


def test_rc_no_1_a_case_missing_the_field_is_rejected(batch, spec):
    """RC-NO-1: one case is missing review_cutoff."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    del cases[0]["review_cutoff"]
    with pytest.raises(mrb.BatchError, match="missing the review_cutoff field"):
        mrb.validate_review_cutoff(cases, spec)


@pytest.mark.parametrize("bad", ["5", True, False, 5.0, None, [5], {"k": 5}])
def test_rc_no_2_a_non_integer_cutoff_is_rejected(batch, spec, bad):
    """RC-NO-2: a string, boolean, float, or other non-integer is a rejection."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    cases[0]["review_cutoff"] = bad
    with pytest.raises(mrb.BatchError, match="review_cutoff must be"):
        mrb.validate_review_cutoff(cases, spec)


@pytest.mark.parametrize("bad", [10, 2, 0, -5])
def test_rc_no_3_a_different_integer_cutoff_is_rejected(batch, spec, bad):
    """RC-NO-3: an integer other than 5."""
    cases = copy.deepcopy(_all_cases(batch.reviewer_files))
    cases[0]["review_cutoff"] = bad
    with pytest.raises(mrb.BatchError, match="review_cutoff must be 5"):
        mrb.validate_review_cutoff(cases, spec)


def test_a_drifted_file_level_cutoff_is_rejected(batch, spec):
    files = copy.deepcopy(batch.reviewer_files)
    files["xin"]["review_cutoff"] = 10
    with pytest.raises(mrb.BatchError, match="file-level review_cutoff"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


# ───────────────────────── reviewer files and overlap ────────────────────────

def test_each_reviewer_file_is_one_closed_object_with_the_frozen_fields(batch, spec):
    for reviewer, payload in batch.reviewer_files.items():
        assert tuple(payload) == mrb.REVIEWER_FILE_FIELDS
        assert payload["reviewer_id"] == reviewer
        assert payload["batch_id"] == spec.batch_id
        assert payload["run_id"] == spec.run_id
        assert len(payload["cases"]) == spec.cases_for(reviewer)


def test_every_case_carries_exactly_the_frozen_fields_and_no_label(batch):
    for case in _all_cases(batch.reviewer_files):
        assert tuple(case) == mrb.CASE_FIELDS
        assert "label" not in case
        assert len(case["retrieved_results"]) == 50
        assert len(case["comparison"]["retrieved_results"]) == 50
        assert case["comparison"]["retriever"] != case["retriever"]
        assert [p["title"] for p in case["gold_passages"]] == case["gold_titles"]
        assert all(p["text"] for p in case["gold_passages"])
        for result in case["retrieved_results"]:
            assert tuple(result) == mrb.RESULT_FIELDS


def test_gold_passages_and_comparison_are_bound_to_the_read_only_source(
    batch, synthetic_run
):
    records = _load_records(synthetic_run)
    passage_texts = mrb.build_passage_text_index(records)
    mrb.validate_review_context_binding(
        batch.reviewer_files, records, batch.patterns, passage_texts
    )


@pytest.mark.parametrize("field", ["gold_passages", "comparison"])
def test_tampered_review_context_is_rejected(batch, synthetic_run, field):
    records = _load_records(synthetic_run)
    passage_texts = mrb.build_passage_text_index(records)
    files = copy.deepcopy(batch.reviewer_files)
    case = files["xin"]["cases"][0]
    if field == "gold_passages":
        case[field][0]["text"] += " tampered"
        expected = "displayed gold passages"
    else:
        case[field]["retrieved_results"][0]["title"] = "Wrong comparison title"
        expected = "displayed comparison"
    with pytest.raises(mrb.BatchError, match=expected):
        mrb.validate_review_context_binding(
            files, records, batch.patterns, passage_texts
        )


def test_a_reviewer_file_holds_no_case_assigned_only_to_the_other_reviewer(batch):
    per_reviewer = _per_reviewer(batch.reviewer_files)
    overlap = set(batch.overlap_keys)
    assert not (
        (set(per_reviewer["xin"]) - overlap) & (set(per_reviewer["jiajun"]) - overlap)
    )


def test_overlap_cases_are_byte_identical_across_the_two_files(batch):
    mrb.validate_overlap_content_identical(batch.reviewer_files, batch.overlap_keys)
    by_key = {}
    overlap = set(batch.overlap_keys)
    for payload in batch.reviewer_files.values():
        for case in payload["cases"]:
            key = (case["example_id"], case["retriever"])
            if key in overlap:
                by_key.setdefault(key, []).append(
                    json.dumps(case, ensure_ascii=False, indent=2)
                )
    assert len(by_key) == len(overlap)
    for blobs in by_key.values():
        assert len(blobs) == 2 and blobs[0] == blobs[1]


def test_an_overlap_case_that_differs_between_files_is_rejected(batch):
    files = copy.deepcopy(batch.reviewer_files)
    target = next(case for case in files["xin"]["cases"] if case["is_overlap"])
    target["question"] += " (edited)"
    with pytest.raises(mrb.BatchError, match="differs between the two reviewer files"):
        mrb.validate_overlap_content_identical(files, batch.overlap_keys)


def test_the_cases_arrays_follow_the_canonical_batch_order(batch):
    """Overlap-first is the page's display order; the file keeps canonical order."""
    canonical = {key: index for index, key in enumerate(batch.keys)}
    for payload in batch.reviewer_files.values():
        positions = [
            canonical[(case["example_id"], case["retriever"])]
            for case in payload["cases"]
        ]
        assert positions == sorted(positions)


def test_a_case_carrying_a_label_field_is_rejected(batch, spec):
    files = copy.deepcopy(batch.reviewer_files)
    files["xin"]["cases"][0]["label"] = "distractor dominance"
    with pytest.raises(mrb.BatchError, match="carries a `label` field"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


# ───────────── the closed section-4 shapes and the frozen reviewer set ───────
#
# Section 4 defines the reviewer JSON as one closed object, defines each case as
# containing only the frozen material, and says the file contains no notes from
# either reviewer. "Closed" is key-set EQUALITY: a validator that only checks
# that the frozen fields are PRESENT accepts the legal control below *and* every
# rejection below it, so it has not implemented the contract at all.
#
# Each rejection is the accepted payload with exactly one property changed, so
# neither half of a pair can pass for an unrelated reason.


def test_the_closed_shape_legal_control_is_accepted(batch, spec):
    """The exact generated top-level and case shapes validate as they stand."""
    mrb.validate_closed_shapes(batch.reviewer_files)
    mrb.validate_batch(
        batch.reviewer_files, batch.keys, batch.overlap_keys, batch.patterns, spec
    )
    for reviewer, payload in batch.reviewer_files.items():
        assert set(payload) == set(mrb.REVIEWER_FILE_FIELDS)
        assert payload["reviewer_id"] == reviewer
        assert reviewer in mrb.REVIEWER_IDS
        for case in payload["cases"]:
            assert set(case) == set(mrb.CASE_FIELDS)
            assert "notes" not in case


@pytest.mark.parametrize(
    "field, value",
    [
        # A reviewer's notes at the file level: section 4 says the delivered file
        # carries none.
        ("notes", {"unit": "a note that does not belong in a generated file"}),
        ("provenance", "hand-edited"),
    ],
)
def test_one_extra_top_level_field_is_rejected(batch, spec, field, value):
    files = copy.deepcopy(batch.reviewer_files)
    files["xin"][field] = value
    with pytest.raises(mrb.BatchError, match="carries unexpected field"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


@pytest.mark.parametrize("field", mrb.REVIEWER_FILE_FIELDS)
def test_a_missing_top_level_field_is_rejected(batch, spec, field):
    """Closed in both directions: a truncated object is not the frozen shape."""
    files = copy.deepcopy(batch.reviewer_files)
    del files["xin"][field]
    with pytest.raises(mrb.BatchError, match="is missing " + field):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


def test_a_case_carrying_a_foreign_notes_field_is_rejected(batch, spec):
    """The one mutation that most directly disproves the no-notes contract."""
    files = copy.deepcopy(batch.reviewer_files)
    files["xin"]["cases"][0]["notes"] = "another reviewer note"
    with pytest.raises(mrb.BatchError, match="carries unexpected field"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


@pytest.mark.parametrize(
    "field, value",
    [
        ("failure_reason", "lexical mismatch"),
        ("annotated_at", "2026-07-28T12:00:00Z"),
        ("unexpected_field", 1),
    ],
)
def test_another_arbitrary_extra_case_field_is_rejected(batch, spec, field, value):
    files = copy.deepcopy(batch.reviewer_files)
    files["jiajun"]["cases"][2][field] = value
    with pytest.raises(mrb.BatchError, match="carries unexpected field"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


@pytest.mark.parametrize("field", mrb.CASE_FIELDS)
def test_a_case_missing_one_frozen_field_is_rejected(batch, spec, field):
    files = copy.deepcopy(batch.reviewer_files)
    del files["xin"]["cases"][0][field]
    with pytest.raises(mrb.BatchError, match="is missing " + field):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


@pytest.mark.parametrize("foreign", ["alice", "reviewer3", "xin2"])
def test_a_syntactically_valid_foreign_reviewer_id_is_rejected(batch, spec, foreign):
    """A valid identifier is still not one of the two reviewers this batch has."""
    assert foreign not in mrb.REVIEWER_IDS
    files = copy.deepcopy(batch.reviewer_files)
    files["xin"]["reviewer_id"] = foreign
    with pytest.raises(mrb.BatchError, match="reviewer_id must be one of"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


def test_a_third_reviewer_file_is_rejected(batch, spec):
    """The frozen set is exactly two people, so a third file is a rejection."""
    files = copy.deepcopy(batch.reviewer_files)
    files["alice"] = copy.deepcopy(files["xin"])
    files["alice"]["reviewer_id"] = "alice"
    with pytest.raises(mrb.BatchError, match="frozen reviewer set"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


def test_a_reviewer_file_delivered_under_a_foreign_key_is_rejected(batch, spec):
    files = copy.deepcopy(batch.reviewer_files)
    files["alice"] = files.pop("xin")
    with pytest.raises(mrb.BatchError, match="frozen reviewer set"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


def test_the_extractor_and_the_page_share_one_definition_of_each_shape():
    """Not equal tuples — the same objects, so the two cannot drift apart."""
    assert mrb.CASE_FIELDS is page.CASE_FIELDS
    assert mrb.REVIEWER_FILE_FIELDS is page.REVIEWER_FILE_FIELDS
    assert mrb.REVIEWER_IDS is page.REVIEWER_IDS
    assert mrb.REVIEWER_IDS == ("jiajun", "xin")
    assert tuple(sorted(mrb.PRIVATE_QUOTAS)) == mrb.REVIEWER_IDS
    assert "label" not in mrb.CASE_FIELDS and "notes" not in mrb.CASE_FIELDS


def test_a_mislabelled_is_overlap_flag_is_rejected(batch, spec):
    files = copy.deepcopy(batch.reviewer_files)
    marker = next(case for case in files["xin"]["cases"] if case["is_overlap"])
    key = (marker["example_id"], marker["retriever"])
    for payload in files.values():
        for case in payload["cases"]:
            if (case["example_id"], case["retriever"]) == key:
                case["is_overlap"] = False
    with pytest.raises(mrb.BatchError, match="is_overlap"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


def test_a_non_boolean_is_overlap_flag_is_rejected(batch, spec):
    """A string "false" is not the boolean the case contract requires."""
    files = copy.deepcopy(batch.reviewer_files)
    private = next(case for case in files["xin"]["cases"] if not case["is_overlap"])
    private["is_overlap"] = "false"
    with pytest.raises(mrb.BatchError, match="is_overlap must be a boolean"):
        mrb.validate_batch(files, batch.keys, batch.overlap_keys, batch.patterns, spec)


# ──────────────────────────── assignment.csv shape ───────────────────────────

def test_assignment_csv_has_one_row_per_reviewer_per_unit(batch, spec, tmp_path):
    path = tmp_path / "assignment.csv"
    mrb.write_assignment_csv(str(path), batch.assignment_rows)
    with io.open(str(path), "rb") as fh:
        raw = fh.read()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" not in raw

    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    assert tuple(rows[0]) == mrb.ASSIGNMENT_COLUMNS
    overlap = set(batch.overlap_keys)
    assert len(rows) == len(batch.keys) + len(overlap)

    per_unit = {}
    for row in rows:
        per_unit.setdefault((row["example_id"], row["retriever"]), []).append(row)
    assert len(per_unit) == len(batch.keys)
    for key, unit_rows in per_unit.items():
        expected = 2 if key in overlap else 1
        assert len(unit_rows) == expected, key
        for row in unit_rows:
            assert row["is_overlap"] == ("true" if expected == 2 else "false")
            assert row["run_id"] == spec.run_id
        if expected == 2:
            assert sorted(r["assigned_reviewer"] for r in unit_rows) == list(
                spec.reviewer_order
            )


def test_assignment_rows_follow_the_canonical_batch_order(batch):
    canonical = {key: index for index, key in enumerate(batch.keys)}
    positions = [
        canonical[(row["example_id"], row["retriever"])] for row in batch.assignment_rows
    ]
    assert positions == sorted(positions)


# ───────────────────────── writing and the read-only run ─────────────────────

def test_generation_refuses_to_write_inside_the_source_run(synthetic_run):
    with pytest.raises(mrb.BatchError, match="read-only source run"):
        mrb.validate_output_dir(synthetic_run, synthetic_run)
    with pytest.raises(mrb.BatchError, match="read-only source run"):
        mrb.validate_output_dir(os.path.join(synthetic_run, "nested"), synthetic_run)


def test_a_dotdot_path_back_into_the_source_run_is_refused(synthetic_run):
    sneaky = os.path.join(synthetic_run, "..", os.path.basename(synthetic_run), "out")
    with pytest.raises(mrb.BatchError, match="read-only source run"):
        mrb.validate_output_dir(sneaky, synthetic_run)


def test_generation_refuses_a_case_only_alias_of_the_source_run(synthetic_run):
    """A case-only alias names the same directory on Windows and default macOS."""
    aliased = os.path.join(
        os.path.dirname(synthetic_run), os.path.basename(synthetic_run).upper()
    )
    if not os.path.isdir(aliased):
        pytest.skip("this filesystem distinguishes the case-only alias")
    with pytest.raises(mrb.BatchError, match="read-only source run"):
        mrb.validate_output_dir(aliased, synthetic_run)


def test_a_sibling_output_directory_is_accepted(synthetic_run, tmp_path):
    mrb.validate_output_dir(str(tmp_path / "annotations" / "batch"), synthetic_run)


def _digest_tree(directory):
    digests = {}
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            with io.open(path, "rb") as fh:
                digests[name] = hashlib.sha256(fh.read()).hexdigest()
    return digests


def test_generation_leaves_the_source_run_byte_for_byte_unchanged(
    synthetic_run, spec, tmp_path
):
    before = _digest_tree(synthetic_run)
    out_dir = tmp_path / "out" / "batch"
    written = mrb.generate_batch(
        runs_root=os.path.dirname(synthetic_run), out_dir=str(out_dir), spec=spec
    )
    assert _digest_tree(synthetic_run) == before
    assert sorted(os.path.basename(p) for p in written) == sorted(
        [mrb.ASSIGNMENT_NAME, mrb.PAGE_NAME, "jiajun_cases.json", "xin_cases.json"]
    )
    for path in written:
        assert os.path.dirname(os.path.abspath(path)) == os.path.abspath(str(out_dir))


def test_identical_input_produces_byte_identical_output(synthetic_run, spec, tmp_path):
    for name in ("a", "b"):
        mrb.generate_batch(
            runs_root=os.path.dirname(synthetic_run),
            out_dir=str(tmp_path / name),
            spec=spec,
        )
    assert _digest_tree(str(tmp_path / "a")) == _digest_tree(str(tmp_path / "b"))


def test_check_only_writes_nothing(synthetic_run, spec, tmp_path):
    out_dir = tmp_path / "unwritten"
    assert mrb.generate_batch(
        runs_root=os.path.dirname(synthetic_run),
        out_dir=str(out_dir),
        check_only=True,
        spec=spec,
    ) == []
    assert not out_dir.exists()


def test_written_json_is_utf8_lf_with_a_trailing_newline(batch, tmp_path):
    path = tmp_path / "xin_cases.json"
    mrb.write_json(str(path), batch.reviewer_files["xin"])
    with io.open(str(path), "rb") as fh:
        raw = fh.read()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert b"\r\n" not in raw
    assert raw.endswith(b"\n")
    assert json.loads(raw.decode("utf-8"))["reviewer_id"] == "xin"


def test_a_missing_source_file_is_a_hard_failure(synthetic_run, spec):
    os.remove(os.path.join(synthetic_run, mrb.RANK_PATTERN_SOURCE_NAME))
    with pytest.raises(FileNotFoundError, match=mrb.RANK_PATTERN_SOURCE_NAME):
        mrb.build_batch(synthetic_run, spec)


# ───────────────────────────── the shared page ───────────────────────────────

def test_the_page_states_the_same_contract_as_the_extractor():
    page.verify_page_contract()
    assert page.BATCH_ID == mrb.BATCH_ID
    assert page.SOURCE_RUN_ID == mrb.SOURCE_RUN_ID
    assert page.REVIEW_CUTOFF == mrb.REVIEW_CUTOFF
    assert page.CASES_PER_REVIEWER == mrb.CASES_PER_REVIEWER == 17
    assert page.OVERLAP_COUNT == mrb.OVERLAP_SIZE == 4
    assert page.CASE_FIELDS == mrb.CASE_FIELDS
    assert page.REVIEWER_FILE_FIELDS == mrb.REVIEWER_FILE_FIELDS
    assert page.REVIEWER_IDS == mrb.REVIEWER_IDS


@pytest.mark.parametrize(
    "original, drifted",
    [
        ("var REVIEW_CUTOFF = 5;", "var REVIEW_CUTOFF = 10;"),
        # The closed shapes and the reviewer set are literals in the shipped page
        # too, so a page that quietly widened either one is rejected here rather
        # than discovered by a reviewer opening a non-conforming file.
        ('"comparison", "review_cutoff", "is_overlap"];',
         '"comparison", "review_cutoff", "is_overlap", "label"];'),
        ('var REVIEWER_IDS = ["jiajun", "xin"];',
         'var REVIEWER_IDS = ["jiajun", "xin", "alice"];'),
        ('var REVIEWER_FILE_FIELDS = ["batch_id", "reviewer_id", "run_id", "review_cutoff", "cases"];',
         'var REVIEWER_FILE_FIELDS = ["batch_id", "reviewer_id", "run_id", "review_cutoff", "cases", "notes"];'),
    ],
)
def test_a_page_with_a_drifted_contract_literal_is_rejected(original, drifted):
    text = page.render_page()
    assert original in text, original
    broken = text.replace(original, drifted)
    assert broken != text
    with pytest.raises(ValueError, match="contract literal"):
        page.verify_page_contract(broken)


def test_the_page_carries_no_case_data_and_no_payload_placeholder():
    """Data arrives through the file picker, so the page ships empty."""
    text = page.render_page()
    assert "/*DATA*/" not in text
    assert "retrieved_results" in text            # it renders the field...
    assert mrb.FROZEN_SELECTED_KEYS[0][0] not in text   # ...but embeds no case


def test_the_page_offers_a_file_picker_and_reaches_no_network():
    text = page.render_page()
    assert 'type="file"' in text and 'id="file-cases"' in text
    for forbidden in ("fetch(", "XMLHttpRequest", "http://", "https://",
                      "WebSocket", "navigator.sendBeacon"):
        assert forbidden not in text, forbidden


def test_the_page_separates_draft_state_by_batch_and_reviewer():
    text = page.render_page()
    assert 'return STORAGE_PREFIX + "::" + batchId + "::" + reviewerId;' in text
    assert "C.storageKey(payload.batch_id, payload.reviewer_id)" in text


def test_the_page_never_copies_the_machine_pattern_into_the_human_label():
    """No code path may assign rank_pattern into a label field."""
    text = page.render_page()
    for snippet in ("labelInput.value = caseObj.rank_pattern",
                    "label = caseObj.rank_pattern",
                    "label: caseObj.rank_pattern",
                    "label = c.rank_pattern",
                    "labelInput.value = c.rank_pattern",
                    ".label = rank_pattern"):
        assert snippet not in text, snippet
    # The label input's only sources are the reviewer's own draft and "".
    assert (
        'labelInput.value = (draft && typeof draft.label === "string") '
        '? draft.label : "";'
    ) in text
    # The machine pattern is rendered read-only: text content, never a value.
    assert "value.textContent = caseObj.retriever + \" = \" + caseObj.rank_pattern" in text
    assert "Machine rank pattern (10-class)" in text
    assert "Human failure label (optional)" in text


def test_the_page_shows_the_note_template_as_prose_not_as_a_default_value():
    text = page.render_page()
    for line in ("Observed:", "Missing gold:", "Retrieved evidence or distractor:",
                 "Possible reason:", "Alternative or uncertainty:"):
        assert line in text
    assert "notesInput.value = (draft" in text


# ───────────── the real read-only run: frozen oracle and population ──────────

@requires_formal_run
def test_the_formal_run_reproduces_the_frozen_eligible_population():
    config = mrb.bfr.load_config(
        os.path.join(FORMAL_RUN_DIR, "config.json"), mrb.SOURCE_RUN_ID
    )
    records = mrb.bfr.load_details(os.path.join(FORMAL_RUN_DIR, "details.jsonl"), config)
    strata = mrb.eligible_strata(records, mrb.REVIEW_CUTOFF)
    assert {key: len(ids) for key, ids in strata.items()} == {
        ("bm25", "bridge"): 51,
        ("bm25", "comparison"): 12,
        ("dense", "bridge"): 16,
        ("dense", "comparison"): 3,
    }
    mrb.verify_eligible_population(strata, mrb.V1_SPEC)


@requires_formal_run
def test_the_formal_run_reproduces_the_frozen_selection_oracle():
    built = mrb.build_batch(FORMAL_RUN_DIR)
    assert built.keys == mrb.FROZEN_SELECTED_KEYS
    assert built.overlap_keys == mrb.FROZEN_OVERLAP_KEYS
    assert len(set(built.keys)) == mrb.BATCH_SIZE == 30
    # 30 distinct unit keys but only 29 distinct example ids: one example was
    # selected under both retrievers, so cardinality is a property of the key.
    assert len({example_id for example_id, _ in built.keys}) == 29
    assert len(set(built.overlap_keys)) == mrb.OVERLAP_SIZE == 4


@requires_formal_run
def test_repeat_generation_on_the_formal_run_is_identical():
    first, second = mrb.build_batch(FORMAL_RUN_DIR), mrb.build_batch(FORMAL_RUN_DIR)
    assert first.keys == second.keys
    assert first.overlap_keys == second.overlap_keys
    assert first.reviewer_files == second.reviewer_files
    assert first.assignment_rows == second.assignment_rows


@requires_formal_run
def test_on_the_formal_run_the_two_overlap_readings_coincide_as_disclosed():
    """The protocol discloses this coincidence; it is recorded, not relied upon.

    Drawing one unit from the full eligible stratum yields the same four keys as
    drawing from the selected batch, and each lies inside the selected batch.
    That is why SS-NO-4 is a procedural requirement here rather than a
    key-comparison control, and why matching keys must not be read as evidence
    that either procedure is acceptable.
    """
    config = mrb.bfr.load_config(
        os.path.join(FORMAL_RUN_DIR, "config.json"), mrb.SOURCE_RUN_ID
    )
    records = mrb.bfr.load_details(os.path.join(FORMAL_RUN_DIR, "details.jsonl"), config)
    strata = mrb.eligible_strata(records, mrb.REVIEW_CUTOFF)
    selected = mrb.select_batch(strata, mrb.V1_SPEC)

    non_conforming = tuple(
        (random.Random(mrb.SELECTION_SEED).sample(
            sorted(strata[(retriever, question_type)]), 1)[0], retriever)
        for retriever, question_type, _quota in mrb.V1_SPEC.strata
    )
    assert non_conforming == mrb.FROZEN_OVERLAP_KEYS
    assert set(non_conforming) <= set(mrb.FROZEN_SELECTED_KEYS)


@requires_formal_run
def test_the_formal_batch_satisfies_every_frozen_contract():
    built = mrb.build_batch(FORMAL_RUN_DIR)
    mrb.validate_batch(
        built.reviewer_files, built.keys, built.overlap_keys, built.patterns, mrb.V1_SPEC
    )
    assert sorted(built.reviewer_files) == ["jiajun", "xin"]
    for payload in built.reviewer_files.values():
        assert len(payload["cases"]) == 17
        assert sum(case["is_overlap"] for case in payload["cases"]) == 4
        for case in payload["cases"]:
            assert len(case["retrieved_results"]) == 50
            assert case["review_cutoff"] == 5
    for reviewer, quotas in mrb.PRIVATE_QUOTAS.items():
        private = {
            (c["example_id"], c["retriever"])
            for c in built.reviewer_files[reviewer]["cases"]
        } - set(built.overlap_keys)
        for retriever, expected in quotas.items():
            assert sum(1 for key in private if key[1] == retriever) == expected


@requires_formal_run
def test_the_formal_batch_binds_every_rank_pattern_to_its_own_source_row():
    built = mrb.build_batch(FORMAL_RUN_DIR)
    assert len(built.patterns) == 1000
    source = {}
    with io.open(os.path.join(FORMAL_RUN_DIR, mrb.RANK_PATTERN_SOURCE_NAME),
                 encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            source[(row["example_id"], row["retriever"])] = row["rank_pattern"]
    assert len(source) == 1000
    for case in _all_cases(built.reviewer_files):
        key = (case["example_id"], case["retriever"])
        assert case["rank_pattern"] == source[key]


@requires_formal_run
def test_generating_the_formal_batch_leaves_the_source_run_unchanged(tmp_path):
    before = _digest_tree(FORMAL_RUN_DIR)
    mrb.generate_batch(out_dir=str(tmp_path / "mrv1"))
    assert _digest_tree(FORMAL_RUN_DIR) == before


@requires_formal_run
def test_the_checked_in_batch_artifacts_are_reproducible(tmp_path):
    """The workspace in the repository must regenerate from the read-only run.

    Human `<reviewer_id>_notes.csv` exports live in the same committed
    directory as the four generator-owned artifacts (section 6 of the
    protocol). The generator does not author those files, so reproducibility
    is scoped to its own outputs rather than the whole directory listing.
    """
    committed = os.path.join(REPO_ROOT, "results", "annotations", mrb.BATCH_ID)
    if not os.path.isdir(committed):
        pytest.skip("the manual_review_v1 workspace has not been generated yet")
    out_dir = tmp_path / "regenerated"
    written = mrb.generate_batch(out_dir=str(out_dir))
    owned_names = {os.path.basename(path) for path in written}
    committed_digests = _digest_tree(committed)
    assert owned_names <= set(committed_digests)
    assert _digest_tree(str(out_dir)) == {
        name: digest for name, digest in committed_digests.items() if name in owned_names
    }


def test_generator_owned_digest_scope_ignores_coexisting_notes_but_catches_drift(
    synthetic_run, spec, tmp_path
):
    """R20-O1 legal control: a coexisting human notes file must not fail
    reproducibility, but drift in a generator-owned file still must.
    """
    out_dir = tmp_path / "workspace"
    written = mrb.generate_batch(
        runs_root=os.path.dirname(synthetic_run), out_dir=str(out_dir), spec=spec
    )
    owned_names = {os.path.basename(path) for path in written}

    def _owned_digests(directory):
        return {
            name: digest
            for name, digest in _digest_tree(str(directory)).items()
            if name in owned_names
        }

    regenerated = tmp_path / "regenerated"
    mrb.generate_batch(
        runs_root=os.path.dirname(synthetic_run), out_dir=str(regenerated), spec=spec
    )

    (out_dir / "xin_notes.csv").write_text(
        "batch_id,run_id,example_id,retriever,review_cutoff,label,notes,annotator,annotated_at\n",
        encoding="utf-8",
    )
    assert _owned_digests(out_dir) == _owned_digests(regenerated)

    drifted_path = out_dir / mrb.ASSIGNMENT_NAME
    drifted_path.write_bytes(drifted_path.read_bytes() + b"# tampered\n")
    assert _owned_digests(out_dir) != _owned_digests(regenerated)


# ─────────────────────────────── the CLI ─────────────────────────────────────

def test_the_cli_refuses_a_run_the_v1_batch_is_not_frozen_against(synthetic_run):
    """Invoked as a subprocess, so the module's `__main__` guard runs too."""
    result = subprocess.run(
        [sys.executable, os.path.join("scripts", "build_manual_review_batch.py"),
         "--run", SYNTH_RUN_ID,
         "--runs-root", os.path.dirname(synthetic_run),
         "--check-only"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "error:" in result.stderr
    assert "frozen against run" in result.stderr


@requires_formal_run
def test_the_cli_validates_the_formal_run_without_writing():
    result = subprocess.run(
        [sys.executable, os.path.join("scripts", "build_manual_review_batch.py"),
         "--check-only"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "wrote nothing" in result.stdout
