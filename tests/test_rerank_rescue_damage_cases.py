"""Regression tests for scripts/reporting/rerank_rescue_damage_cases.py.

The per-example cases file is a downstream artifact
(docs/specs/2026-08-12-rerank-rescue-damage-cases.md), so the properties under
test are fidelity and refusal rather than any new metric:

  - all four transition classes are emitted, and each row's class is the frozen
    four-cell function of its two binary outcomes;
  - exactly the five valid `(setting, k)` combinations appear, and
    `per_question` at k = 10 — the cutoff the schema's K policy leaves blank —
    is refused rather than read;
  - the frozen 12-column schema, the 2500-row key set, key uniqueness, and the
    deterministic `(setting, example_id, k)` order;
  - gold ranks are 1-based, take a repeated title's first occurrence, hold every
    gold title of the row, and record an unretrieved gold as `null` instead of
    inferring a rank beyond the stored depth;
  - a row whose stored ranked list implies a different Full@k than the metric
    saved in the input refuses, because the two would describe different runs;
  - the serialized rank map is checked as bytes, not only as a mapping: a
    whitespace-bearing, re-spelled, or ASCII-escaped cell carrying the same
    ranks is refused, since §5.3 freezes the physical serialization;
  - the *public writer* refuses a non-compliant frame rather than normalizing
    it — an extra column, a reordered column list, and a wrong row order are all
    rejected at the write boundary, where a silent repair would answer a
    required refusal with a compliant-looking artifact;
  - a refusal never creates and never overwrites the destination;
  - regeneration is byte-for-byte deterministic;
  - counting the emitted transitions reproduces the Full Evidence rows of the
    accepted `results/rerank_rescue_damage.csv` exactly, for `overall`,
    `bridge`, and `comparison` alike.

Every rejection is paired with a legal control that differs only in the targeted
property, so a validator that stopped discriminating could not pass quietly.
"""

import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from scripts.reporting import rerank_rescue_damage_cases as cases_module
from scripts.reporting.formal_result_inputs import BINARY_METRIC_COLUMNS
from src.results_schema import RESULT_COLUMNS, TITLE_SEPARATOR

SCRIPT = "scripts/reporting/rerank_rescue_damage_cases.py"

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FORMAL_CASES = os.path.join(REPO_ROOT, "results", "rerank_rescue_damage_cases.csv")
FORMAL_SUMMARY = os.path.join(REPO_ROOT, "results", "rerank_rescue_damage.csv")

BRIDGE_N = 404
PER_SETTING = 500
GOLD_A, GOLD_B = "Gold A", "Gold B"
GOLD_CELL = TITLE_SEPARATOR.join([GOLD_A, GOLD_B])

# The worst (bottleneck) gold rank each stage gets, by `example index % 6`.
# `None` means the second gold is absent from the stored list entirely. The six
# patterns are chosen so that every transition class occurs at k = 5, and so
# that k = 2 and k = 10 disagree with it — a fixture where all three cutoffs
# told the same story could not detect a cutoff being read from the wrong column.
#
#   i%6:        0        1        2        3        4        5
#   dense:      2       10        2       10     None        5
#   rerank:     5        2       10     None        5     None
#   @5:    st_hit   rescue   damage  st_miss   rescue   damage
WORST_RANKS = {
    "dense": [2, 10, 2, 10, None, 5],
    "rerank": [5, 2, 10, None, 5, None],
}
STORE_DEPTH = {"pooled": 50, "per_question": 10}


# ─────────────────────────── formal-bundle fixtures ──────────────────────────

def _worst(method, i):
    return WORST_RANKS[method][i % len(WORST_RANKS[method])]


def _retrieved(method, setting, i):
    """A stored ranked list whose gold ranks are exactly the fixture's design.

    The first gold sits at rank 1 in every row and the second at the row's
    bottleneck rank, so `full_evidence_recall@k` is `worst <= k` by construction
    and the saved metric below cannot drift from the list it describes.
    """
    depth = STORE_DEPTH[setting]
    titles = [f"Cand {method}{i}-{j}" for j in range(depth)]
    titles[0] = GOLD_A
    worst = _worst(method, i)
    if worst is not None:
        titles[worst - 1] = GOLD_B
    return TITLE_SEPARATOR.join(titles)


def _meta(i):
    return {
        "example_id": f"ex{i:04d}",
        "question_type": "bridge" if i < BRIDGE_N else "comparison",
        "level": "hard",
        # `NA` and `None` are legitimate question strings, and the file must
        # round-trip them as text rather than as missing values.
        "question": {0: "NA", 1: "None"}.get(i, f"Question {i}?"),
        "gold_titles": GOLD_CELL,
    }


def _row(method, setting, i):
    row = {column: np.nan for column in RESULT_COLUMNS}
    row["method"] = method
    row["setting"] = setting
    row.update(_meta(i))
    row["retrieved_titles"] = _retrieved(method, setting, i)
    worst = _worst(method, i)
    for k in (2, 5, 10):
        full_hit = int(worst is not None and worst <= k)
        row[f"full_evidence_recall@{k}"] = full_hit
        row[f"any_evidence_recall@{k}"] = 1  # the first gold is always at rank 1
        row[f"partial_evidence_recall@{k}"] = 1.0 if full_hit else 0.5
    row["reciprocal_rank_at_10"] = 1.0
    row["reciprocal_rank_at_50"] = 1.0
    if setting == "per_question":
        row["any_evidence_recall@10"] = np.nan
        row["full_evidence_recall@10"] = np.nan
        row["partial_evidence_recall@10"] = np.nan
    return row


def _formal_frame(rows):
    """Assemble rows into the exact physical shape `read_formal_result_csv` returns."""
    df = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    for column in BINARY_METRIC_COLUMNS:
        df[column] = pd.array(
            [
                pd.NA if (isinstance(row[column], float) and np.isnan(row[column]))
                else int(row[column])
                for row in rows
            ],
            dtype="Int64",
        )
    return df


def _file(method):
    return _formal_frame([
        _row(method, setting, i)
        for setting in ("pooled", "per_question")
        for i in range(PER_SETTING)
    ])


@pytest.fixture(scope="module")
def bundle():
    return _file("dense"), _file("rerank")


@pytest.fixture(scope="module")
def valid_cases(bundle):
    dense, rerank = bundle
    paired = cases_module.build_paired_frame(dense, rerank)
    return cases_module.build_cases(paired)


def _write_bundle(tmp_path, dense, rerank):
    dense_path = tmp_path / "dense_results.csv"
    rerank_path = tmp_path / "rerank_results.csv"
    dense.to_csv(dense_path, index=False)
    rerank.to_csv(rerank_path, index=False)
    return str(dense_path), str(rerank_path)


def _keys(frame):
    return list(zip(frame.setting, frame.example_id, [int(k) for k in frame.k]))


# ─────────────────────────── happy path (legal control) ──────────────────────

def test_formal_bundle_produces_the_frozen_schema(tmp_path, bundle):
    dense, rerank = bundle
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    out_path = tmp_path / "rerank_rescue_damage_cases.csv"

    cases_module.main(dense_path, rerank_path, str(out_path))

    written = cases_module.read_cases_csv(str(out_path))
    assert list(written.columns) == cases_module.OUTPUT_COLUMNS
    assert len(written.columns) == 12
    assert len(written) == cases_module.EXPECTED_ROWS == 2500
    assert not out_path.read_bytes().startswith(b"\xef\xbb\xbf")  # no UTF-8 BOM
    # The written file satisfies the whole contract on its own bytes.
    cases_module.validate_cases(written, str(out_path))


def test_keys_are_unique_and_deterministically_ordered(valid_cases):
    keys = _keys(valid_cases)
    assert len(set(keys)) == len(keys) == 2500

    expected = [
        (setting, f"ex{i:04d}", k)
        for setting in ("pooled", "per_question")
        for i in range(PER_SETTING)
        for k in sorted(cases_module.VALID_KS_BY_SETTING[setting])
    ]
    assert keys == expected


def test_exactly_the_five_valid_setting_k_combinations_appear(valid_cases):
    combinations = sorted({(s, k) for s, _, k in _keys(valid_cases)})
    assert combinations == [
        ("per_question", 2), ("per_question", 5),
        ("pooled", 2), ("pooled", 5), ("pooled", 10),
    ]
    assert ("per_question", 10) not in combinations
    for setting, k in combinations:
        subset = valid_cases[(valid_cases.setting == setting) & (valid_cases.k == k)]
        assert len(subset) == PER_SETTING


def test_metadata_is_copied_verbatim_including_na_like_questions(valid_cases):
    pooled = valid_cases[valid_cases.setting == "pooled"].set_index("example_id")
    assert pooled.loc["ex0000", "question"].tolist() == ["NA", "NA", "NA"]
    assert pooled.loc["ex0001", "question"].tolist() == ["None", "None", "None"]
    assert set(valid_cases.question_type) == {"bridge", "comparison"}
    assert (valid_cases.gold_titles == GOLD_CELL).all()


# ────────────────────────── §4 transition classification ─────────────────────

def test_all_four_transition_classes_are_emitted(valid_cases):
    assert set(valid_cases.transition) == set(cases_module.TRANSITION_CLASSES)
    at_five = valid_cases[(valid_cases.setting == "pooled") & (valid_cases.k == 5)]
    assert set(at_five.transition) == set(cases_module.TRANSITION_CLASSES)


def test_every_row_class_is_the_frozen_four_cell_function(valid_cases):
    expected = {
        (0, 0): "stable_miss", (0, 1): "rescue",
        (1, 0): "damage", (1, 1): "stable_hit",
    }
    for row in valid_cases.itertuples(index=False):
        key = (int(row.dense_full_at_k), int(row.rerank_full_at_k))
        assert row.transition == expected[key]


def test_classify_covers_the_table_and_refuses_anything_else():
    assert cases_module.classify(0, 0) == "stable_miss"
    assert cases_module.classify(0, 1) == "rescue"
    assert cases_module.classify(1, 0) == "damage"
    assert cases_module.classify(1, 1) == "stable_hit"
    with pytest.raises(ValueError, match="Illegal hit pair"):
        cases_module.classify(1, 2)


# ──────────────────────── §3 valid combinations / refusals ───────────────────

def test_per_question_k10_is_refused_not_read():
    """The schema leaves that cell blank; reading it would fabricate 500 rows."""
    assert cases_module.valid_ks("per_question") == (2, 5)
    assert cases_module.valid_ks("pooled") == (2, 5, 10)
    assert cases_module.full_column("per_question", 5) == "full_evidence_recall@5"
    assert cases_module.full_column("pooled", 10) == "full_evidence_recall@10"
    with pytest.raises(ValueError, match="Unsupported \\(setting, k\\) combination"):
        cases_module.full_column("per_question", 10)


@pytest.mark.parametrize("k", [0, 1, 3, 7, 50])
def test_a_cutoff_outside_the_frozen_set_is_refused(k):
    with pytest.raises(ValueError, match="Unsupported \\(setting, k\\) combination"):
        cases_module.full_column("pooled", k)


@pytest.mark.parametrize("setting", ["Pooled", "per-question", "", None])
def test_an_unsupported_setting_is_refused(setting):
    with pytest.raises(ValueError, match="Unsupported setting"):
        cases_module.valid_ks(setting)


# ──────────────────────────── §5.3 gold-rank semantics ───────────────────────

def test_ranks_are_one_based_and_keyed_in_stored_gold_order():
    mapping = cases_module.ordered_gold_ranks(
        ["Other", GOLD_B, "Filler", GOLD_A], [GOLD_A, GOLD_B]
    )
    assert mapping == {GOLD_A: 4, GOLD_B: 2}
    assert list(mapping) == [GOLD_A, GOLD_B]  # stored gold order, not rank order


def test_a_repeated_gold_takes_its_first_occurrence():
    mapping = cases_module.ordered_gold_ranks(
        [GOLD_A, "Filler", GOLD_A, GOLD_B], [GOLD_A, GOLD_B]
    )
    assert mapping == {GOLD_A: 1, GOLD_B: 4}


def test_an_unretrieved_gold_is_null_and_never_inferred():
    mapping = cases_module.ordered_gold_ranks([GOLD_A, "Filler"], [GOLD_A, GOLD_B])
    assert mapping == {GOLD_A: 1, GOLD_B: None}
    encoded = cases_module.encode_gold_ranks(mapping)
    assert encoded == '{"Gold A":1,"Gold B":null}'
    # Not 0, not depth+1, not a fabricated concrete rank.
    assert ":0" not in encoded and ":3" not in encoded


def test_an_empty_retrieved_list_yields_only_nulls():
    """An empty cell is the approved empty list, not a missing value."""
    assert cases_module.split_retrieved_titles("", "src") == []
    mapping = cases_module.ordered_gold_ranks([], [GOLD_A, GOLD_B])
    assert mapping == {GOLD_A: None, GOLD_B: None}
    assert cases_module.full_at_k_from_ranks(mapping, 10) == 0


def test_the_rank_map_holds_every_gold_title(valid_cases):
    for cell in valid_cases.dense_gold_ranks.tolist()[:50]:
        assert list(json.loads(cell)) == [GOLD_A, GOLD_B]


def test_encoding_is_compact_stable_and_round_trippable():
    mapping = {"Zeta": 3, "Alpha": None}
    encoded = cases_module.encode_gold_ranks(mapping)
    assert encoded == '{"Zeta":3,"Alpha":null}'  # compact, and never re-sorted
    assert cases_module.decode_gold_ranks(encoded, "src") == mapping


def test_non_ascii_titles_survive_the_json_and_csv_round_trip(tmp_path):
    mapping = {"Bœuf — Ω": 2, "第二篇": None}
    encoded = cases_module.encode_gold_ranks(mapping)
    assert "Bœuf — Ω" in encoded  # written as itself, not \\u-escaped
    path = tmp_path / "roundtrip.csv"
    pd.DataFrame([{"cell": encoded}]).to_csv(path, index=False)
    read_back = pd.read_csv(path, dtype=str, keep_default_na=False).cell.iloc[0]
    assert cases_module.decode_gold_ranks(read_back, str(path)) == mapping


@pytest.mark.parametrize("payload", [
    "[1, 2]", "null", '"text"', "{", '{"Gold A": 0}', '{"Gold A": -1}',
    '{"Gold A": 1.5}', '{"Gold A": true}',
])
def test_a_malformed_rank_payload_refuses(payload):
    with pytest.raises(ValueError):
        cases_module.decode_gold_ranks(payload, "src")


def test_the_legal_rank_payload_control_is_accepted():
    assert cases_module.decode_gold_ranks('{"Gold A":1,"Gold B":null}', "src") == {
        GOLD_A: 1, GOLD_B: None
    }


@pytest.mark.parametrize("cell", [
    '{"Gold A": 1,"Gold B":null}',     # whitespace after a colon
    '{"Gold A":1, "Gold B":null}',     # whitespace after a comma
    ' {"Gold A":1,"Gold B":null}',     # leading whitespace
    '{"Gold B":null,"Gold A":1}\n',    # trailing newline
    '{"Bo\\u0153uf":1}',               # a non-ASCII title written as an escape
    '{"Gold A":1,"Gold A":2}',         # a repeated key, silently last-wins in JSON
])
def test_a_non_canonical_gold_rank_spelling_is_refused(cell):
    """§5.3 freezes the physical serialization, not merely the mapping.

    Each cell here decodes to a legal mapping, so a validator that only checked
    meaning would pass it and the writer would persist bytes a rerun does not
    reproduce. The repeated-key cell is the sharpest of them: JSON keeps the last
    value, so the *mapping* looks fine while a gold requirement has vanished.
    """
    with pytest.raises(ValueError, match="not the frozen serialization"):
        cases_module.decode_gold_ranks(cell, "src")


def test_the_canonical_spelling_of_each_refused_cell_is_accepted():
    """The legal controls: the same mappings, spelled the one frozen way."""
    for mapping in ({GOLD_A: 1, GOLD_B: None}, {GOLD_B: None, GOLD_A: 1},
                    {"Boœuf": 1}, {GOLD_A: 2}):
        encoded = cases_module.encode_gold_ranks(mapping)
        assert cases_module.decode_gold_ranks(encoded, "src") == mapping


@pytest.mark.parametrize("k,expected", [(1, 0), (2, 0), (5, 1), (10, 1)])
def test_full_at_k_is_implied_by_the_ranks(k, expected):
    assert cases_module.full_at_k_from_ranks({GOLD_A: 1, GOLD_B: 5}, k) == expected


def test_full_at_k_is_zero_when_any_gold_is_null():
    assert cases_module.full_at_k_from_ranks({GOLD_A: 1, GOLD_B: None}, 50) == 0


# ─────────────────────── §2 title extraction refusals ────────────────────────

def test_a_duplicate_gold_title_is_refused_not_collapsed():
    with pytest.raises(ValueError, match="cannot survive as a JSON object key"):
        cases_module.split_gold_titles("Gold A | Gold A", "src")
    # Legal control: the same cell with two distinct titles.
    assert cases_module.split_gold_titles(GOLD_CELL, "src") == [GOLD_A, GOLD_B]


def test_an_empty_gold_component_is_refused():
    with pytest.raises(ValueError, match="empty title"):
        cases_module.split_gold_titles("Gold A |  | Gold B", "src")


@pytest.mark.parametrize("cell", ["", None, 3, np.nan])
def test_a_missing_gold_titles_cell_is_refused(cell):
    with pytest.raises(ValueError, match="gold_titles must be a non-empty string"):
        cases_module.split_gold_titles(cell, "src")


@pytest.mark.parametrize("cell", [None, 3, np.nan])
def test_a_non_string_retrieved_titles_cell_is_refused(cell):
    with pytest.raises(ValueError, match="retrieved_titles must be a string"):
        cases_module.split_retrieved_titles(cell, "src")


# ─────────────── §5.5 the ranks and the saved metric must agree ──────────────

def _corrupt_saved_metric(frame, example_id, setting, column, value):
    """Change one saved metric cell without touching the list that implies it."""
    corrupted = frame.copy()
    mask = (corrupted.example_id == example_id) & (corrupted.setting == setting)
    corrupted.loc[mask, column] = pd.array([value], dtype="Int64")
    return corrupted


def test_a_saved_metric_that_contradicts_the_stored_ranks_refuses(bundle):
    dense, rerank = bundle
    # ex0000's dense bottleneck is rank 2, so Full@5 is genuinely 1; claim 0.
    corrupted = _corrupt_saved_metric(
        dense, "ex0000", "pooled", "full_evidence_recall@5", 0
    )
    paired = cases_module.build_paired_frame(corrupted, rerank)
    with pytest.raises(ValueError, match="describe different runs"):
        cases_module.build_cases(paired)


def test_a_truncated_retrieved_list_that_contradicts_the_metric_refuses(bundle):
    """The mirror case: the metric is kept and the ranked list is shortened."""
    dense, rerank = bundle
    corrupted = dense.copy()
    mask = (corrupted.example_id == "ex0000") & (corrupted.setting == "pooled")
    corrupted.loc[mask, "retrieved_titles"] = TITLE_SEPARATOR.join(
        [GOLD_A] + [f"Cand {j}" for j in range(49)]  # second gold now absent
    )
    paired = cases_module.build_paired_frame(corrupted, rerank)
    with pytest.raises(ValueError, match="describe different runs"):
        cases_module.build_cases(paired)


def test_the_agreeing_control_bundle_builds(bundle):
    dense, rerank = bundle
    paired = cases_module.build_paired_frame(dense, rerank)
    assert len(cases_module.build_cases(paired)) == 2500


# ─────────────────────────── §5 output-contract refusals ─────────────────────

def test_a_reordered_column_is_refused(valid_cases):
    swapped = valid_cases[
        ["example_id", "setting"] + cases_module.OUTPUT_COLUMNS[2:]
    ]
    with pytest.raises(ValueError, match="must be exactly OUTPUT_COLUMNS"):
        cases_module.validate_cases(swapped)


def test_a_duplicate_key_is_refused(valid_cases):
    duplicated = pd.concat([valid_cases, valid_cases.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="must be unique"):
        cases_module.validate_cases_schema(duplicated)


def test_a_missing_row_is_refused(valid_cases):
    with pytest.raises(ValueError, match="rows are not the complete key set"):
        cases_module.validate_cases_schema(valid_cases.iloc[1:].reset_index(drop=True))


def test_a_shuffled_row_order_is_refused(valid_cases):
    shuffled = valid_cases.iloc[[1, 0] + list(range(2, 2500))].reset_index(drop=True)
    with pytest.raises(ValueError, match="§5.4 order"):
        cases_module.validate_cases_schema(shuffled)
    # Legal control: the same rows in the frozen order pass.
    cases_module.validate_cases_schema(valid_cases)


def test_a_per_question_k10_row_is_refused(valid_cases):
    smuggled = valid_cases.copy()
    smuggled.loc[smuggled.index[-1], "k"] = 10  # last row is per_question @5
    with pytest.raises(ValueError, match="Unsupported \\(setting, k\\) combination"):
        cases_module.validate_cases_schema(smuggled)


@pytest.mark.parametrize("value", [True, "1", 1.0, None])
def test_a_non_integer_binary_cell_is_refused(valid_cases, value):
    broken = valid_cases.copy()
    broken["dense_full_at_k"] = broken["dense_full_at_k"].astype(object)
    broken.loc[broken.index[0], "dense_full_at_k"] = value
    with pytest.raises(ValueError, match="dense_full_at_k"):
        cases_module.validate_cases_values(broken)


def test_a_transition_contradicting_its_binaries_is_refused(valid_cases):
    broken = valid_cases.copy()
    row = broken.index[(broken.transition == "rescue").tolist().index(True)]
    broken.loc[row, "transition"] = "stable_hit"
    with pytest.raises(ValueError, match="contradicts"):
        cases_module.validate_cases_values(broken)


def test_a_transition_outside_the_vocabulary_is_refused(valid_cases):
    broken = valid_cases.copy()
    broken.loc[broken.index[0], "transition"] = "improved"
    with pytest.raises(ValueError, match="is outside"):
        cases_module.validate_cases_values(broken)


def test_rank_keys_that_are_not_the_rows_gold_titles_are_refused(valid_cases):
    broken = valid_cases.copy()
    broken.loc[broken.index[0], "dense_gold_ranks"] = '{"Gold A":1}'
    with pytest.raises(ValueError, match="are not the row's gold titles"):
        cases_module.validate_cases_values(broken)


def test_ranks_that_imply_a_different_full_at_k_are_refused(valid_cases):
    broken = valid_cases.copy()
    broken.loc[broken.index[0], "dense_gold_ranks"] = '{"Gold A":1,"Gold B":null}'
    with pytest.raises(ValueError, match="implies Full@"):
        cases_module.validate_cases_values(broken)


# ────────────────────────────── writer behavior ──────────────────────────────
#
# These exercise the *public* writer rather than the validators it calls. The
# distinction is the whole point: a writer that projects, reorders, or sorts
# before validating answers a required refusal with a compliant-looking
# artifact, and every direct `validate_cases*()` assertion above would still
# pass while it did so.

def _tmp_leftovers(root):
    return sorted(str(path.relative_to(root)) for path in root.rglob("*.tmp"))


def _assert_writer_refuses(frame, tmp_path, label, match):
    """`write_cases_csv(frame)` must refuse, against both kinds of destination.

    "Never creates" and "never overwrites" are two different promises, so the
    same frame is offered an absent path and a path holding a sentinel, and
    neither may end up touched. No `.tmp` file may survive either attempt.
    """
    root = tmp_path / label
    absent = root / "nested" / "cases.csv"
    with pytest.raises(ValueError, match=match):
        cases_module.write_cases_csv(frame, str(absent))
    assert not absent.exists()
    assert not absent.parent.exists()  # validation precedes the makedirs
    assert _tmp_leftovers(tmp_path) == []

    existing = root / "cases.csv"
    existing.parent.mkdir(parents=True, exist_ok=True)
    sentinel = b"previous accepted artifact\n"
    existing.write_bytes(sentinel)
    with pytest.raises(ValueError, match=match):
        cases_module.write_cases_csv(frame, str(existing))
    assert existing.read_bytes() == sentinel
    assert _tmp_leftovers(tmp_path) == []


def _assert_writer_accepts(frame, tmp_path, label):
    """The legal control: the twin differing only in the targeted property writes.

    It is written to two destinations and the bytes compared, so "accepted" also
    means reproducible rather than merely produced once, and the persisted file
    is re-validated from its own bytes.
    """
    root = tmp_path / label
    first, second = root / "a.csv", root / "b.csv"
    cases_module.write_cases_csv(frame, str(first))
    cases_module.write_cases_csv(frame, str(second))
    assert first.read_bytes() == second.read_bytes()

    written = cases_module.read_cases_csv(str(first))
    cases_module.validate_cases(written, str(first))
    assert written.equals(frame.reset_index(drop=True))
    return first.read_bytes()


def test_the_writer_refuses_an_extra_column(tmp_path, valid_cases):
    """§5.1 calls an extra column non-compliant, so it is not projected away."""
    extra = valid_cases.copy()
    extra["unexpected"] = "must-refuse"
    _assert_writer_refuses(extra, tmp_path, "extra", "must be exactly OUTPUT_COLUMNS")
    # Legal control: the exact 12-column twin.
    _assert_writer_accepts(valid_cases, tmp_path, "extra-control")


def test_the_writer_refuses_reordered_columns(tmp_path, valid_cases):
    swapped = valid_cases[["example_id", "setting"] + cases_module.OUTPUT_COLUMNS[2:]]
    _assert_writer_refuses(
        swapped, tmp_path, "reordered", "must be exactly OUTPUT_COLUMNS"
    )
    # Legal control: the same values in the §5.1 order.
    _assert_writer_accepts(
        swapped[cases_module.OUTPUT_COLUMNS], tmp_path, "reordered-control"
    )


def test_the_writer_refuses_a_shuffled_row_order(tmp_path, valid_cases):
    """A wrong row order is a refusal, not something the writer sorts into shape.

    Without this the writer's output for a shuffled frame was byte-identical to
    the compliant artifact, so the caller could not tell a repair from a pass.
    """
    order = [1, 0] + list(range(2, cases_module.EXPECTED_ROWS))
    shuffled = valid_cases.iloc[order].reset_index(drop=True)
    _assert_writer_refuses(shuffled, tmp_path, "shuffled", "§5.4 order")
    # Legal control: the same rows, in the §5.4 order.
    _assert_writer_accepts(
        cases_module.sort_cases(shuffled), tmp_path, "shuffled-control"
    )


def test_the_writer_still_accepts_a_non_default_row_index(tmp_path, valid_cases):
    """The one normalization left in the writer, kept deliberately.

    A pandas index is not part of the §5.1 schema and is not serialized, so
    dropping it coerces nothing the contract speaks about; the rows are already
    required to be in the §5.4 order before it happens.
    """
    reindexed = valid_cases.set_index(
        pd.Index(range(1000, 1000 + len(valid_cases)))
    )
    _assert_writer_accepts(reindexed, tmp_path, "reindexed")


@pytest.mark.parametrize("column", ["dense_gold_ranks", "rerank_gold_ranks"])
def test_the_writer_refuses_whitespace_bearing_gold_rank_json(
    tmp_path, valid_cases, column
):
    """A cell that means the right thing but is spelled loosely (§5.3)."""
    canonical = valid_cases[column].iloc[0]
    spaced = json.dumps(json.loads(canonical), ensure_ascii=False)  # ', ' / ': '
    assert spaced != canonical
    assert json.loads(spaced) == json.loads(canonical)  # differs only in whitespace

    broken = valid_cases.copy()
    broken.loc[broken.index[0], column] = spaced
    _assert_writer_refuses(
        broken, tmp_path, f"spaced-{column}", "not the frozen serialization"
    )

    # Legal control: the identical frame with that one cell spelled compactly.
    restored = broken.copy()
    restored.loc[restored.index[0], column] = canonical
    _assert_writer_accepts(restored, tmp_path, f"spaced-{column}-control")


NON_ASCII_GOLD = ["Bœuf à la Ω", "第二篇 — Σ"]


def _restate_gold_titles(frame, index, titles):
    """Row `index` restated with different gold titles, every identity intact.

    Only the titles change: each stage's rank map keeps its values and its key
    order, so the row still satisfies §5.5's key-set and Full@k identities and
    the only property left under test is how the map is spelled.
    """
    restated = frame.copy()
    restated.loc[index, "gold_titles"] = TITLE_SEPARATOR.join(titles)
    for column in ("dense_gold_ranks", "rerank_gold_ranks"):
        ranks = json.loads(restated.loc[index, column])
        assert len(ranks) == len(titles)
        restated.loc[index, column] = cases_module.encode_gold_ranks(
            dict(zip(titles, ranks.values()))
        )
    return restated


def test_the_writer_refuses_ascii_escaped_gold_rank_json(tmp_path, valid_cases):
    """The second non-canonical spelling: same mapping, escapes instead of text."""
    frame = _restate_gold_titles(valid_cases, valid_cases.index[0], NON_ASCII_GOLD)

    # Legal control first, so the escaped variant below is the only difference:
    # the compact ensure_ascii=False twin writes the titles as themselves and
    # regenerates byte-for-byte.
    control = _assert_writer_accepts(frame, tmp_path, "escaped-control")
    assert NON_ASCII_GOLD[0] in control.decode("utf-8")
    assert b"\\u" not in control

    escaped = frame.copy()
    ranks = json.loads(escaped.loc[escaped.index[0], "dense_gold_ranks"])
    escaped.loc[escaped.index[0], "dense_gold_ranks"] = json.dumps(
        ranks, ensure_ascii=True, separators=(",", ":")
    )
    assert "\\u" in escaped.loc[escaped.index[0], "dense_gold_ranks"]
    _assert_writer_refuses(
        escaped, tmp_path, "escaped", "not the frozen serialization"
    )


def test_refusal_does_not_create_the_destination(tmp_path, valid_cases):
    out_path = tmp_path / "nested" / "cases.csv"
    with pytest.raises(ValueError):
        cases_module.write_cases_csv(
            valid_cases.iloc[1:].reset_index(drop=True), str(out_path)
        )
    assert not out_path.exists()
    assert not (tmp_path / "nested" / "cases.csv.tmp").exists()


def test_refusal_does_not_overwrite_an_existing_destination(tmp_path, valid_cases):
    out_path = tmp_path / "cases.csv"
    sentinel = b"previous accepted artifact\n"
    out_path.write_bytes(sentinel)
    broken = valid_cases.copy()
    broken.loc[broken.index[0], "transition"] = "improved"
    with pytest.raises(ValueError):
        cases_module.write_cases_csv(broken, str(out_path))
    assert out_path.read_bytes() == sentinel
    assert not (tmp_path / "cases.csv.tmp").exists()


def test_a_failing_run_leaves_the_destination_alone(tmp_path, bundle):
    """End to end, through the CLI: a bad bundle must not touch the artifact."""
    dense, rerank = bundle
    corrupted = _corrupt_saved_metric(
        dense, "ex0000", "pooled", "full_evidence_recall@5", 0
    )
    dense_path, rerank_path = _write_bundle(tmp_path, corrupted, rerank)
    out_path = tmp_path / "cases.csv"
    sentinel = b"previous accepted artifact\n"
    out_path.write_bytes(sentinel)

    result = subprocess.run(
        [sys.executable, SCRIPT,
         "--dense", dense_path, "--rerank", rerank_path, "--out", str(out_path)],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert result.returncode != 0
    assert out_path.read_bytes() == sentinel


def test_regeneration_is_byte_for_byte_deterministic(tmp_path, bundle):
    dense, rerank = bundle
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    first = tmp_path / "a.csv"
    second = tmp_path / "b.csv"
    for out in (first, second):
        result = subprocess.run(
            [sys.executable, SCRIPT,
             "--dense", dense_path, "--rerank", rerank_path, "--out", str(out)],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
    assert first.read_bytes() == second.read_bytes()


def test_the_persisted_file_reads_back_identically(tmp_path, bundle, valid_cases):
    dense, rerank = bundle
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    out_path = tmp_path / "cases.csv"
    cases_module.main(dense_path, rerank_path, str(out_path))
    written = cases_module.read_cases_csv(str(out_path))
    assert written.equals(valid_cases)


@pytest.mark.parametrize("lexeme", ["1.0", " 1", "true", "", "01"])
def test_a_non_integer_lexeme_in_the_persisted_file_is_refused(tmp_path, valid_cases, lexeme):
    path = tmp_path / "cases.csv"
    raw = valid_cases.astype({"k": str, "dense_full_at_k": str, "rerank_full_at_k": str})
    raw.loc[raw.index[0], "dense_full_at_k"] = lexeme
    raw.to_csv(path, index=False)
    with pytest.raises(ValueError, match="dense_full_at_k must be written as"):
        cases_module.read_cases_csv(str(path))


# ──────────────── §5.6 consistency with the accepted aggregate ───────────────

def _aggregate(cases, setting, k, question_type):
    group = cases[(cases.setting == setting) & (cases.k == k)]
    if question_type != "overall":
        group = group[group.question_type == question_type]
    counts = group.transition.value_counts()
    return {
        "n": len(group),
        "stable_miss": int(counts.get("stable_miss", 0)),
        "rescues": int(counts.get("rescue", 0)),
        "damages": int(counts.get("damage", 0)),
        "stable_hit": int(counts.get("stable_hit", 0)),
        "dense_hits": int(group.dense_full_at_k.sum()),
        "rerank_hits": int(group.rerank_full_at_k.sum()),
    }


def test_the_formal_cases_file_aggregates_to_the_accepted_summary():
    """The one-directional check: the accepted aggregate is the authority."""
    assert os.path.exists(FORMAL_CASES), FORMAL_CASES
    assert os.path.exists(FORMAL_SUMMARY), FORMAL_SUMMARY
    cases = cases_module.read_cases_csv(FORMAL_CASES)
    cases_module.validate_cases(cases, FORMAL_CASES)
    summary = pd.read_csv(FORMAL_SUMMARY)
    full = summary[summary.criterion == "full_evidence_recall"]
    assert len(full) == 15  # 5 valid (setting, k) x 3 question-type groups

    for row in full.itertuples(index=False):
        actual = _aggregate(cases, row.setting, int(row.k), row.question_type)
        expected = {name: int(getattr(row, name)) for name in actual}
        assert actual == expected, (row.setting, row.k, row.question_type)


def test_the_bridge_and_comparison_groups_partition_the_formal_overall_row():
    """Group counts are only comparable if the subgroups partition the whole."""
    cases = cases_module.read_cases_csv(FORMAL_CASES)
    for setting, ks in cases_module.VALID_KS_BY_SETTING.items():
        for k in ks:
            overall = _aggregate(cases, setting, k, "overall")
            bridge = _aggregate(cases, setting, k, "bridge")
            comparison = _aggregate(cases, setting, k, "comparison")
            for name, value in overall.items():
                assert value == bridge[name] + comparison[name], (setting, k, name)


def test_every_repository_path_the_generator_cites_resolves():
    """A citation is a promise; a dead one behaves exactly like a live one.

    Scoped to this artifact's own sources, mirroring the DR-004 provenance scan
    in tests/test_reporting_doc_references.py without widening that module's
    deliberately fixed subject.
    """
    import re

    pattern = re.compile(
        r"\b(?:docs|src|scripts|tests|results)/[A-Za-z0-9_./@-]*"
        r"\.(?:md|py|csv|json|html)\b"
    )
    for source in (SCRIPT, "docs/specs/2026-08-12-rerank-rescue-damage-cases.md"):
        with open(os.path.join(REPO_ROOT, source), encoding="utf-8") as handle:
            text = handle.read()
        cited = sorted({match.group(0) for match in pattern.finditer(text)})
        assert cited, source
        missing = [p for p in cited if not os.path.exists(os.path.join(REPO_ROOT, p))]
        assert not missing, f"{source} cites path(s) that do not exist: {missing}"

    with open(os.path.join(REPO_ROOT, SCRIPT), encoding="utf-8") as handle:
        docstring = handle.read().split('"""')[1]
    assert "docs/specs/2026-08-12-rerank-rescue-damage-cases.md" in docstring
    assert "docs/specs/2026-07-26-reranker-rescue-damage.md" in docstring


def test_the_fixture_bundle_aggregates_the_same_way(valid_cases):
    """The same identity on a synthetic bundle, so the check is not data-bound."""
    for setting, ks in cases_module.VALID_KS_BY_SETTING.items():
        for k in ks:
            actual = _aggregate(valid_cases, setting, k, "overall")
            assert actual["n"] == PER_SETTING
            assert actual["stable_miss"] + actual["rescues"] + actual["damages"] \
                + actual["stable_hit"] == PER_SETTING
            assert actual["dense_hits"] == actual["damages"] + actual["stable_hit"]
            assert actual["rerank_hits"] == actual["rescues"] + actual["stable_hit"]
