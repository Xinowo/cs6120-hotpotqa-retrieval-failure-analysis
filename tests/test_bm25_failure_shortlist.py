"""Regression tests for scripts/reporting/bm25_failure_shortlist.py.

Covers the frozen contract in
docs/specs/2026-07-27-bm25-dense-reporting-contracts.md: the closed join and
strict input value domains, the binary-only criterion, the closed `setting`
vocabulary on the direct public argument as well as the CLI, the neutral
observable-signal boundary (no causal labels), and the §4 definition of
`bm25_gold_found` as the number of DISTINCT gold titles found anywhere in
BM25's stored list. Signal counts are asserted against small hand-built
bundles, and every rejection has a legal control differing only in the targeted
property.

The physical-input section also covers cells this tool never reads: an
out-of-domain float metric, a blank outside the three per-question `@10` recall
slots, and a populated value *inside* them are all refused before any write, so
a truncated, impossible, or K-policy-violating formal bundle cannot yield a
normal-looking shortlist. The last of those is the inverse half of the placement
rule: the schema does not compute per-question `@10`, so a value there is an
unauthorized metric extension even when it is spelled with an owner-approved
lexeme.
"""

import csv
import math
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from scripts.reporting import bm25_failure_shortlist as sl
from scripts.reporting.formal_result_inputs import (
    BINARY_METRIC_COLUMNS,
    load_result_csv,
)
from src.results_schema import RESULT_COLUMNS

GOLD = "Gold A | Gold B"
META = [("ex0", "bridge"), ("ex1", "bridge"), ("ex2", "comparison"),
        ("ex3", "bridge"), ("ex4", "comparison"), ("ex5", "bridge")]
DEFAULT_RETRIEVED = "Gold A | Gold B | X | Y | Z"

CONSUMED = "full_evidence_recall@5"
SCRIPT = "scripts/reporting/bm25_failure_shortlist.py"

# Retired causal names that must never reappear in this neutral tool.
_CAUSAL_NAMES = {"lexical_mismatch", "distractor_entity", "category_candidate"}


def _row(method, setting, eid, qtype, hit, retrieved):
    row = {column: np.nan for column in RESULT_COLUMNS}
    row.update(
        method=method, setting=setting, example_id=eid, question_type=qtype,
        level="hard", question=f"Q {eid}", gold_titles=GOLD,
        retrieved_titles=retrieved,
    )
    for k in (2, 5, 10):
        row[f"any_evidence_recall@{k}"] = hit
        row[f"full_evidence_recall@{k}"] = hit
        row[f"partial_evidence_recall@{k}"] = float(hit)
    row["reciprocal_rank_at_10"] = 0.5
    row["reciprocal_rank_at_50"] = 0.5
    if setting == "per_question":
        # The storage/metric policy does not compute per-question `@10`, and
        # "uncomputed" is required-empty, not merely permitted-empty. A fixture
        # that populated these cells would be a malformed formal bundle, so it
        # could not serve as the legal control for anything else.
        for metric in ("any_evidence_recall", "full_evidence_recall",
                       "partial_evidence_recall"):
            row[f"{metric}@10"] = np.nan
    return row


def _binary_or_missing(column, value):
    """A fixture's binary cell: a plain integer, or missing. Never a float.

    Built from the source row dicts rather than from an assembled frame, so the
    fixture cannot launder a float `0.0`/`1.0` into the nullable-integer type
    the contract reserves for genuine integers.
    """
    if value is None or value is pd.NA:
        return pd.NA
    if isinstance(value, float) and math.isnan(value):
        return pd.NA
    if isinstance(value, (int, np.integer)) and not isinstance(value, bool):
        return int(value)
    raise AssertionError(
        f"fixture {column} must hold an int or a missing value, got {value!r}"
    )


def _formal_frame(rows):
    """Assemble rows into the exact physical shape `read_formal_result_csv` returns."""
    df = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    for column in BINARY_METRIC_COLUMNS:
        df[column] = pd.array(
            [_binary_or_missing(column, row[column]) for row in rows], dtype="Int64"
        )
    return df


def _frame(method, hits, meta=META, retrieved_by_id=None):
    retrieved_by_id = retrieved_by_id or {}
    rows = []
    for setting in ("pooled", "per_question"):
        for (eid, qtype), hit in zip(meta, hits):
            rows.append(
                _row(method, setting, eid, qtype, hit,
                     retrieved_by_id.get(eid, DEFAULT_RETRIEVED))
            )
    return _formal_frame(rows)


BM25_HITS = [0, 1, 1, 0, 0, 1]
DENSE_HITS = [1, 0, 1, 0, 1, 0]

# BM25 retrieved titles chosen so that only ex0 has no gold in its top-2.
BM25_RETRIEVED = {
    "ex0": "X | Y | Gold A | P | Q",       # no gold in top-2 -> signal B
    "ex3": "Gold A | X | Y | Z | W",       # gold in top-2 -> no signal B
    "ex4": "Gold A | X | Y | Z | W",       # gold in top-2 -> no signal B
}


def _bm25():
    return _frame("bm25", BM25_HITS, retrieved_by_id=BM25_RETRIEVED)


def _dense():
    return _frame("dense", DENSE_HITS)


def _shortlist(bm25=None, dense=None, criterion="full_evidence_recall", k=5,
               setting="pooled", per_signal=15):
    return sl.build_shortlist(
        _bm25() if bm25 is None else bm25,
        _dense() if dense is None else dense,
        criterion, k, setting, per_signal,
    )


# ─────────────────────────────── happy path ──────────────────────────────────

def test_signal_counts_and_neutral_vocabulary():
    df, n_a, n_b = _shortlist()
    # signal A: bm25 miss & dense hit -> {ex0, ex4}
    assert n_a == 2
    # signal B: bm25 miss & no gold in bm25 top-2 -> {ex0}
    assert n_b == 1
    assert len(df) == 3
    assert set(df.observed_signal.unique()) == {
        sl.SIGNAL_DENSE_HIT_BM25_MISS, sl.SIGNAL_BM25_NO_GOLD_IN_TOP2
    }


def test_output_schema_has_provenance_columns():
    df, _, _ = _shortlist()
    assert list(df.columns) == sl.OUTPUT_COLUMNS
    for column in ("observed_signal", "setting", "criterion", "k"):
        assert column in df.columns
    assert set(df.criterion.unique()) == {"full_evidence_recall"}
    assert set(df.k.unique()) == {5}


def test_no_causal_labels_anywhere():
    """Neither the column names nor any value may be a causal category."""
    df, _, _ = _shortlist()
    assert _CAUSAL_NAMES.isdisjoint(df.columns)
    assert _CAUSAL_NAMES.isdisjoint(set(df.observed_signal.unique()))
    # the module exposes no causal names at all
    assert _CAUSAL_NAMES.isdisjoint(set(sl.OUTPUT_COLUMNS))


def test_per_signal_truncation():
    df, n_a, n_b = _shortlist(per_signal=1)
    assert n_a == 2 and n_b == 1
    assert int((df.observed_signal == sl.SIGNAL_DENSE_HIT_BM25_MISS).sum()) == 1
    assert int((df.observed_signal == sl.SIGNAL_BM25_NO_GOLD_IN_TOP2).sum()) == 1


def test_deterministic_order_within_signal_group():
    df, _, _ = _shortlist()
    a = df[df.observed_signal == sl.SIGNAL_DENSE_HIT_BM25_MISS]
    # ranked by (bm25_gold_found, question_type, example_id): ex0(bridge) < ex4(comparison)
    assert a.example_id.tolist() == ["ex0", "ex4"]


# ───────────── bm25_gold_found counts DISTINCT gold titles found ─────────────

# Two BM25 misses that dense hits, so both carry signal A only.
DISTINCT_META = [("exA", "comparison"), ("exB", "bridge")]
DISTINCT_BM25_HITS = [0, 0]
DISTINCT_DENSE_HITS = [1, 1]


def _distinct_bundle(retrieved_by_id):
    bm25 = _frame("bm25", DISTINCT_BM25_HITS, meta=DISTINCT_META,
                  retrieved_by_id=retrieved_by_id)
    dense = _frame("dense", DISTINCT_DENSE_HITS, meta=DISTINCT_META)
    return bm25, dense


def _found_by_id(df):
    return dict(zip(df.example_id, df.bm25_gold_found))


def test_repeated_gold_title_counts_once():
    bm25, dense = _distinct_bundle({
        "exA": "Gold A | Gold A | Gold A | X | Y",   # one gold, three times
        "exB": "Gold A | Gold B | X | Y | Z",        # two distinct golds
    })
    df, _, _ = sl.build_shortlist(bm25, dense, "full_evidence_recall", 5,
                                  "pooled", 15)
    found = _found_by_id(df)
    assert found["exA"] == 1  # NOT 3
    assert found["exB"] == 2
    assert set(df.n_gold.unique()) == {2}


def test_duplicate_non_gold_titles_do_not_change_the_count():
    bm25, dense = _distinct_bundle({
        "exA": "X | X | X | Gold A | Y",
        "exB": "Y | Y | Gold A | Gold B | Z",
    })
    df, _, _ = sl.build_shortlist(bm25, dense, "full_evidence_recall", 5,
                                  "pooled", 15)
    found = _found_by_id(df)
    assert found["exA"] == 1
    assert found["exB"] == 2


def test_no_gold_and_empty_stored_list_controls():
    bm25, dense = _distinct_bundle({
        "exA": "X | Y | Z",   # no gold anywhere
        "exB": "",            # empty stored list
    })
    df, _, _ = sl.build_shortlist(bm25, dense, "full_evidence_recall", 5,
                                  "pooled", 15)
    found = _found_by_id(df[df.observed_signal == sl.SIGNAL_DENSE_HIT_BM25_MISS])
    assert found["exA"] == 0
    assert found["exB"] == 0


def test_gold_found_never_exceeds_n_gold():
    bm25, dense = _distinct_bundle({
        "exA": "Gold A | Gold A | Gold B | Gold B | Gold A",
        "exB": "Gold B | Gold B | X | Y | Z",
    })
    df, _, _ = sl.build_shortlist(bm25, dense, "full_evidence_recall", 5,
                                  "pooled", 15)
    assert len(df) > 0
    assert ((df.bm25_gold_found >= 0) & (df.bm25_gold_found <= df.n_gold)).all()
    found = _found_by_id(df)
    assert found["exA"] == 2 and found["exB"] == 1


def test_distinct_count_drives_ranking_and_truncation():
    """Occurrence counting would rank exB first and survive truncation; the
    distinct count must keep exA (fewest gold titles actually found)."""
    bm25, dense = _distinct_bundle({
        "exA": "Gold A | Gold A | Gold A | X | Y",   # distinct 1, occurrences 3
        "exB": "Gold A | Gold B | X | Y | Z",        # distinct 2, occurrences 2
    })
    full, _, _ = sl.build_shortlist(bm25, dense, "full_evidence_recall", 5,
                                    "pooled", 15)
    signal_a = full[full.observed_signal == sl.SIGNAL_DENSE_HIT_BM25_MISS]
    assert signal_a.example_id.tolist() == ["exA", "exB"]

    truncated, _, _ = sl.build_shortlist(bm25, dense, "full_evidence_recall", 5,
                                         "pooled", 1)
    kept = truncated[truncated.observed_signal == sl.SIGNAL_DENSE_HIT_BM25_MISS]
    assert kept.example_id.tolist() == ["exA"]


def test_formal_bundle_gold_found_within_bounds():
    df, _, _ = _shortlist()
    assert ((df.bm25_gold_found >= 0) & (df.bm25_gold_found <= df.n_gold)).all()


# ─────────────────────────── binary-only criterion ───────────────────────────

def test_partial_criterion_removed_and_rejected():
    assert "partial_evidence_recall" not in sl.SUPPORTED_CRITERIA
    with pytest.raises(ValueError, match="Unsupported criterion"):
        _shortlist(criterion="partial_evidence_recall")


def test_any_criterion_legal_control():
    df, _, _ = _shortlist(criterion="any_evidence_recall")
    assert set(df.criterion.unique()) == {"any_evidence_recall"}


# ──────────────────────── closed public `setting` domain ─────────────────────

@pytest.mark.parametrize("setting", ["bogus", "", None, "Pooled", "POOLED",
                                     "per-question", " pooled", 0])
def test_reject_unsupported_direct_setting(setting):
    with pytest.raises(ValueError, match="Unsupported setting"):
        _shortlist(setting=setting)


@pytest.mark.parametrize("setting", ["pooled", "per_question"])
def test_accept_supported_direct_setting(setting):
    df, n_a, n_b = _shortlist(setting=setting)
    assert list(df.columns) == sl.OUTPUT_COLUMNS
    assert set(df.setting.unique()) == {setting}
    assert (n_a, n_b) == (2, 1)


@pytest.mark.parametrize("setting", ["pooled", "per_question"])
def test_supported_setting_with_zero_candidates_keeps_exact_schema(setting):
    """No BM25 miss at all is a genuine zero-case result, not an error."""
    all_hit = [1, 1, 1, 1, 1, 1]
    df, n_a, n_b = sl.build_shortlist(
        _frame("bm25", all_hit), _frame("dense", all_hit),
        "full_evidence_recall", 5, setting, 15,
    )
    assert list(df.columns) == sl.OUTPUT_COLUMNS
    assert len(df) == 0 and n_a == 0 and n_b == 0


def test_reject_unsupported_setting_before_touching_destination(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)

    with pytest.raises(ValueError, match="Unsupported setting"):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "bogus", 15, str(out_path))
    assert not out_path.exists()


def test_cli_rejects_unsupported_setting(tmp_path):
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    completed = subprocess.run(
        [sys.executable, SCRIPT, "--setting", "bogus", "--out", str(out_path)],
        capture_output=True, text=True,
    )
    assert completed.returncode == 2
    assert "invalid choice" in completed.stderr
    assert not out_path.exists()


def test_cli_accepts_supported_setting(tmp_path):
    """Legal CLI twin: same invocation shape with a supported setting."""
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)

    completed = subprocess.run(
        [sys.executable, SCRIPT,
         "--bm25", str(bm25_path), "--dense", str(dense_path),
         "--setting", "per_question", "--k", "2", "--out", str(out_path)],
        capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert list(pd.read_csv(out_path).columns) == sl.OUTPUT_COLUMNS


# ─────────────────────────────── closed join ─────────────────────────────────

def test_reject_cross_method_id_drift():
    dense = _dense()
    dense = dense[dense.example_id != "ex5"]
    with pytest.raises(ValueError, match="example_id sets differ across methods"):
        _shortlist(dense=dense)


def test_reject_duplicate_key_within_setting():
    bm25 = _bm25()
    dup = bm25[(bm25.setting == "pooled") & (bm25.example_id == "ex0")]
    bm25 = pd.concat([bm25, dup], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate example_id"):
        _shortlist(bm25=bm25)


def test_reject_cross_method_metadata_drift():
    dense = _dense()
    dense.loc[dense.example_id == "ex0", "gold_titles"] = "Gold A | Gold C"
    with pytest.raises(ValueError, match="metadata drift"):
        _shortlist(dense=dense)


@pytest.mark.parametrize("method", ["bm25", "dense"])
def test_reject_one_sided_null_metadata(method):
    frames = {"bm25": _bm25(), "dense": _dense()}
    frames[method].loc[frames[method].example_id == "ex0", "gold_titles"] = np.nan
    with pytest.raises(ValueError, match="gold_titles must be a non-null string"):
        _shortlist(bm25=frames["bm25"], dense=frames["dense"])


def test_reject_two_sided_null_metadata():
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame.loc[frame.example_id == "ex0", "gold_titles"] = np.nan
    with pytest.raises(ValueError, match="gold_titles must be a non-null string"):
        _shortlist(bm25=bm25, dense=dense)


# ──────────────────── closed upstream metadata vocabularies ──────────────────

def test_reject_unknown_question_type_consistent_across_methods():
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame.loc[frame.example_id == "ex0", "question_type"] = "other"
    with pytest.raises(ValueError, match="question_type.*must be exactly"):
        _shortlist(bm25=bm25, dense=dense)


def test_reject_unknown_level_consistent_across_methods():
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame.loc[frame.example_id == "ex0", "level"] = "trivial"
    with pytest.raises(ValueError, match="level.*must be exactly"):
        _shortlist(bm25=bm25, dense=dense)


@pytest.mark.parametrize("level", ["easy", "medium", "hard"])
def test_accept_every_schema_level(level):
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame["level"] = level
    df, _, _ = _shortlist(bm25=bm25, dense=dense)
    assert set(df.level.unique()) == {level}


# ───────────────────── strict consumed-cell value domain ─────────────────────

@pytest.mark.parametrize("method", ["bm25", "dense"])
@pytest.mark.parametrize("corruption", ["bool", "float", "string", "null"])
def test_reject_non_plain_integer_consumed_cell(method, corruption):
    frames = {"bm25": _bm25(), "dense": _dense()}
    frame = frames[method]
    if corruption == "bool":
        frame[CONSUMED] = frame[CONSUMED].astype(bool)
    elif corruption == "float":
        frame[CONSUMED] = frame[CONSUMED].astype(float)
    elif corruption == "string":
        frame[CONSUMED] = frame[CONSUMED].astype(str)
    else:
        frame.loc[(frame.setting == "pooled") & (frame.example_id == "ex0"),
                  CONSUMED] = pd.NA
    with pytest.raises(ValueError, match="non-0/1"):
        _shortlist(bm25=frames["bm25"], dense=frames["dense"])


def test_reject_fractional_consumed_cell():
    bm25 = _bm25()
    bm25[CONSUMED] = bm25[CONSUMED].astype(float)
    bm25.loc[(bm25.setting == "pooled") & (bm25.example_id == "ex0"),
             CONSUMED] = 0.5
    with pytest.raises(ValueError, match="non-0/1"):
        _shortlist(bm25=bm25)


def test_accept_plain_integer_consumed_cells():
    """Legal control for the strict binary predicate."""
    df, _, _ = _shortlist()
    assert set(df.bm25_hit.unique()) <= {0, 1}
    assert set(df.dense_hit.unique()) <= {0, 1}


# ──────────────── no-create / no-overwrite on refusal (main) ─────────────────

def test_main_refusal_does_not_create_output(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    dense = _dense()
    dense = dense[dense.example_id != "ex5"]  # cross-method id drift
    dense.to_csv(dense_path, index=False)

    with pytest.raises(ValueError):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert not out_path.exists()


def test_main_refusal_does_not_overwrite_existing_output(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    dense = _dense()
    dense = dense[dense.example_id != "ex5"]
    dense.to_csv(dense_path, index=False)
    out_path.write_bytes(b"SENTINEL")

    with pytest.raises(ValueError):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert out_path.read_bytes() == b"SENTINEL"


def test_main_legal_control_writes_output(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)

    sl.main(str(bm25_path), str(dense_path),
            "full_evidence_recall", 5, "pooled", 15, str(out_path))
    written = pd.read_csv(out_path)
    assert list(written.columns) == sl.OUTPUT_COLUMNS
    assert len(written) == 3


# ───────── stored title lists: empty stays empty, NaN is never a title ───────
# A missing cell must never be stringified: `str(NaN)` would fabricate the
# title "nan" and put it in a published artifact (contract section 1.2).

def test_titles_of_an_empty_cell_is_an_empty_list():
    assert sl._titles("") == []
    assert sl._titles("", 5) == []


def test_titles_of_a_normal_cell_is_the_legal_twin():
    assert sl._titles("A | B | C") == ["A", "B", "C"]
    assert sl._titles("A | B | C", 2) == ["A", "B"]


@pytest.mark.parametrize("cell", [np.nan, None, pd.NA, 3, 4.5])
def test_titles_refuses_a_non_string_cell_instead_of_stringifying_it(cell):
    with pytest.raises(ValueError, match="must be a string"):
        sl._titles(cell)


def test_empty_retrieved_list_emits_an_empty_top5_never_the_string_nan():
    bm25 = _frame("bm25", BM25_HITS, retrieved_by_id=dict(BM25_RETRIEVED, ex0=""))
    df, _, _ = sl.build_shortlist(bm25, _dense(), "full_evidence_recall", 5,
                                  "pooled", 15)
    ex0 = df[df.example_id == "ex0"]
    assert len(ex0) > 0
    assert set(ex0.bm25_top5) == {""}
    assert set(ex0.bm25_gold_found) == {0}
    emitted = {str(value) for value in df.values.ravel()}
    assert "nan" not in emitted and "NaN" not in emitted


def test_populated_retrieved_list_is_the_legal_twin():
    df, _, _ = _shortlist()
    ex0 = df[df.example_id == "ex0"]
    assert set(ex0.bm25_top5) == {BM25_RETRIEVED["ex0"]}


@pytest.mark.parametrize("value", [np.nan, None, pd.NA])
def test_missing_retrieved_titles_in_a_direct_frame_refuses(value):
    bm25 = _bm25()
    bm25["retrieved_titles"] = bm25["retrieved_titles"].astype(object)
    bm25.loc[bm25.example_id == "ex0", "retrieved_titles"] = value
    with pytest.raises(ValueError, match="retrieved_titles must be a string"):
        sl.build_shortlist(bm25, _dense(), "full_evidence_recall", 5, "pooled", 15)


def test_empty_retrieved_list_round_trips_through_main(tmp_path):
    """The published artifact must carry an empty cell, not a fabricated title."""
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _frame("bm25", BM25_HITS,
           retrieved_by_id=dict(BM25_RETRIEVED, ex0="")).to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)

    sl.main(str(bm25_path), str(dense_path),
            "full_evidence_recall", 5, "pooled", 15, str(out_path))

    text = out_path.read_text(encoding="utf-8")
    assert ",nan," not in text and ",NaN," not in text
    written = pd.read_csv(out_path, keep_default_na=False, na_filter=False)
    assert set(written[written.example_id == "ex0"].bm25_top5) == {""}


# ───────── physical binary lexemes reach this tool through the loader ────────

@pytest.mark.parametrize("lexeme", ["0.00000000000000000001",
                                    "0.99999999999999999999", "0.5", "True",
                                    "1e0", " 1", "01", "NaN"])
def test_main_refuses_an_unapproved_binary_lexeme_without_touching_output(
        tmp_path, lexeme):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)
    _corrupt_lexeme(bm25_path, CONSUMED, lexeme)
    out_path.write_bytes(b"SENTINEL")

    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert out_path.read_bytes() == b"SENTINEL"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(missing))
    assert not missing.exists()


@pytest.mark.parametrize("lexeme", ["0", "1", "0.0", "1.0"])
def test_main_accepts_every_approved_binary_lexeme(tmp_path, lexeme):
    """Legal twin: the same corruption site, spelled an approved way."""
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)
    _corrupt_lexeme(bm25_path, CONSUMED, lexeme)

    sl.main(str(bm25_path), str(dense_path),
            "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert list(pd.read_csv(out_path).columns) == sl.OUTPUT_COLUMNS


# ─────── malformed *unconsumed* metric cells still refuse, without writing ────
# This tool reads `full_evidence_recall@5` only, so none of the cells below is
# consumed. A truncated or impossible formal bundle must still be refused before
# the shortlist is written; each probe proves no-create and no-overwrite.

# (column, lexeme, setting, expected message) — every cell here is unconsumed.
_MALFORMED_UNCONSUMED = [
    ("partial_evidence_recall@5", "1.1", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@5", "-0.1", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@10", "1e9999", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("reciprocal_rank_at_10", "2", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("reciprocal_rank_at_50", "1.0000000000000001", "per_question",
     r"outside the inclusive \[0, 1\] domain"),
    ("any_evidence_recall@2", "", "pooled", "empty cell where the schema permits none"),
    ("full_evidence_recall@10", "", "pooled", "empty cell where the schema permits none"),
    ("partial_evidence_recall@5", "", "per_question", "empty cell where the schema permits none"),
    ("reciprocal_rank_at_10", "", "per_question", "empty cell where the schema permits none"),
    ("reciprocal_rank_at_50", "", "pooled", "empty cell where the schema permits none"),
]


@pytest.mark.parametrize("column,lexeme,setting,message", _MALFORMED_UNCONSUMED)
def test_main_refuses_a_malformed_unconsumed_metric_without_writing(
        tmp_path, column, lexeme, setting, message):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)
    _corrupt_lexeme(dense_path, column, lexeme, setting=setting)

    existing = tmp_path / "bm25_failure_shortlist.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match=message):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(existing))
    assert existing.read_bytes() == b"SENTINEL"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match=message):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(missing))
    assert not missing.exists()


@pytest.mark.parametrize("column,lexeme", [
    ("partial_evidence_recall@5", "1.0"),
    ("partial_evidence_recall@10", "0.0"),
    ("reciprocal_rank_at_10", "1"),
    ("reciprocal_rank_at_50", "1e-3"),
    ("reciprocal_rank_at_50", "0.000000000000000000001"),
])
def test_main_accepts_an_in_domain_unconsumed_metric(tmp_path, column, lexeme):
    """Legal twins: the same unconsumed cells, spelled inside `[0,1]`."""
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)
    _corrupt_lexeme(dense_path, column, lexeme)

    sl.main(str(bm25_path), str(dense_path),
            "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert list(pd.read_csv(out_path).columns) == sl.OUTPUT_COLUMNS


@pytest.mark.parametrize("column", ["any_evidence_recall@10",
                                    "full_evidence_recall@10",
                                    "partial_evidence_recall@10"])
def test_blank_at10_legality_follows_the_row_setting(tmp_path, column):
    """The same blank refuses in a pooled row and is legal in a per_question row."""
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _dense().to_csv(dense_path, index=False)

    _bm25().to_csv(bm25_path, index=False)
    _corrupt_lexeme(bm25_path, column, "", setting="pooled")
    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert not out_path.exists()

    _bm25().to_csv(bm25_path, index=False)
    _corrupt_lexeme(bm25_path, column, "", setting="per_question")
    sl.main(str(bm25_path), str(dense_path),
            "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert list(pd.read_csv(out_path).columns) == sl.OUTPUT_COLUMNS


# ──── a value in a required-empty slot refuses too, without writing ──────────
# The inverse of the blank-placement rule. The schema does not compute
# per-question `@10`, so a populated cell there is an unauthorized metric
# extension — and this tool never reads it, which is exactly why the loader has
# to refuse it. Every token below is a spelling the same column accepts in a
# pooled row, so only the placement is under test.

# (column, token) — legal spellings, illegal placement.
_REQUIRED_EMPTY_MUTATIONS = [
    ("any_evidence_recall@10", "0"),
    ("any_evidence_recall@10", "1"),
    ("full_evidence_recall@10", "0.0"),
    ("full_evidence_recall@10", "1.0"),
    ("partial_evidence_recall@10", "0.5"),
    ("partial_evidence_recall@10", "1"),
]
_REQUIRED_EMPTY_MESSAGE = "populated cell where the schema requires an empty one"


@pytest.mark.parametrize("target", ["bm25", "dense"])
@pytest.mark.parametrize("column,token", _REQUIRED_EMPTY_MUTATIONS)
def test_main_refuses_a_populated_required_empty_cell_without_writing(
        tmp_path, target, column, token):
    """Both required inputs are held to the required-empty half of the rule."""
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)
    _corrupt_lexeme(bm25_path if target == "bm25" else dense_path,
                    column, token, setting="per_question")

    existing = tmp_path / "bm25_failure_shortlist.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match=_REQUIRED_EMPTY_MESSAGE):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(existing))
    assert existing.read_bytes() == b"SENTINEL"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match=_REQUIRED_EMPTY_MESSAGE):
        sl.main(str(bm25_path), str(dense_path),
                "full_evidence_recall", 5, "pooled", 15, str(missing))
    assert not missing.exists()


@pytest.mark.parametrize("target", ["bm25", "dense"])
@pytest.mark.parametrize("column,token", _REQUIRED_EMPTY_MUTATIONS)
def test_the_same_token_in_the_pooled_row_is_the_legal_twin(
        tmp_path, target, column, token):
    """Placement, not spelling: the identical token passes in the pooled row."""
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "bm25_failure_shortlist.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)
    _corrupt_lexeme(bm25_path if target == "bm25" else dense_path,
                    column, token, setting="pooled")

    sl.main(str(bm25_path), str(dense_path),
            "full_evidence_recall", 5, "pooled", 15, str(out_path))
    assert list(pd.read_csv(out_path).columns) == sl.OUTPUT_COLUMNS


def _corrupt_lexeme(path, column, lexeme, setting="pooled"):
    """Rewrite the first `setting` row's physical `column` token."""
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    header, index = rows[0], rows[0].index(column)
    setting_index = header.index("setting")
    for row in rows[1:]:
        if row[setting_index] == setting:
            row[index] = lexeme
            break
    else:
        raise AssertionError(f"no {setting} row to corrupt")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(rows)


# ══════ the direct typed-frame entry point, including unconsumed columns ══════
# Every matrix above reaches the contract through a file, or through the single
# column the tool consumes. `build_shortlist` is also a public function that
# takes already-created DataFrames, and such a caller can supply a bundle whose
# *unconsumed* metric cells are malformed. The criterion here stays
# `full_evidence_recall@5`, so nothing mutated below is ever read — which is
# precisely why trusting those cells was the defect.
#
# No file is written or read in this section, so nothing here can be satisfied
# by the raw lexeme layer.

_METRIC_COLUMNS = [
    "any_evidence_recall@2", "any_evidence_recall@5", "any_evidence_recall@10",
    "full_evidence_recall@2", "full_evidence_recall@5", "full_evidence_recall@10",
    "partial_evidence_recall@2", "partial_evidence_recall@5",
    "partial_evidence_recall@10",
    "reciprocal_rank_at_10", "reciprocal_rank_at_50",
]
_BINARY_COLUMNS = [c for c in _METRIC_COLUMNS
                   if "partial" not in c and "reciprocal" not in c]
_FLOAT_COLUMNS = [c for c in _METRIC_COLUMNS if c not in _BINARY_COLUMNS]
_SETTINGS = ("pooled", "per_question")

_REQUIRED_EMPTY_SLOTS = frozenset({
    ("any_evidence_recall@10", "per_question"),
    ("full_evidence_recall@10", "per_question"),
    ("partial_evidence_recall@10", "per_question"),
})
_REQUIRED_POPULATED_SLOTS = [
    (column, setting) for column in _METRIC_COLUMNS for setting in _SETTINGS
    if (column, setting) not in _REQUIRED_EMPTY_SLOTS
]

_UNCONSUMED_BINARY = "any_evidence_recall@2"
_UNCONSUMED_FLOATS = ["partial_evidence_recall@5", "reciprocal_rank_at_10",
                      "reciprocal_rank_at_50"]

_MISSING_BINARY_MESSAGE = "non-0/1"
_MISSING_FLOAT_MESSAGE = "missing cell where the schema requires a populated value"
_OUT_OF_DOMAIN_MESSAGE = r"outside the inclusive \[0, 1\] domain"


def _missing_message(column):
    return _MISSING_BINARY_MESSAGE if column in _BINARY_COLUMNS \
        else _MISSING_FLOAT_MESSAGE


def _direct(target, mutate, setting="pooled"):
    """Run the public builder on two legal frames with one mutated in memory."""
    frames = {"bm25": _bm25(), "dense": _dense()}
    frames[target] = mutate(frames[target])
    return sl.build_shortlist(frames["bm25"], frames["dense"],
                              "full_evidence_recall", 5, setting, 15)


def _put(column, setting, value):
    def mutate(frame):
        frame.loc[frame["setting"] == setting, column] = value
        return frame
    return mutate


def _retype(column, transform):
    def mutate(frame):
        frame[column] = transform(frame[column])
        return frame
    return mutate


_TARGETS = ["bm25", "dense"]


# ───── every required-populated slot refuses a missing cell, both frames ──────

@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("column,setting", _REQUIRED_POPULATED_SLOTS)
def test_direct_frame_refuses_a_missing_required_populated_slot(
        target, column, setting):
    """The complete 19-slot required-populated half, on a direct frame."""
    with pytest.raises(ValueError, match=_missing_message(column)):
        _direct(target, _put(column, setting, None))


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("column,setting", _REQUIRED_POPULATED_SLOTS)
def test_direct_frame_accepts_the_populated_twin_of_that_slot(
        target, column, setting):
    """Legal twin for every rejection above."""
    value = 1 if column in _BINARY_COLUMNS else 0.75
    df, _, _ = _direct(target, _put(column, setting, value))
    assert list(df.columns) == sl.OUTPUT_COLUMNS


# ───── every required-empty slot refuses a populated cell, both frames ────────

_REQUIRED_EMPTY_VALUES = {
    "any_evidence_recall@10": [0, 1],
    "full_evidence_recall@10": [0, 1],
    "partial_evidence_recall@10": [0.0, 1.0, 0.5],
}
_POPULATED_EMPTY_MESSAGE = _REQUIRED_EMPTY_MESSAGE


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize(
    "column,value",
    [(column, value) for column, values in sorted(_REQUIRED_EMPTY_VALUES.items())
     for value in values],
)
def test_direct_frame_refuses_a_populated_required_empty_slot(
        target, column, value):
    """the first demonstrated bypass, over all three slots and both frames."""
    with pytest.raises(ValueError, match=_POPULATED_EMPTY_MESSAGE):
        _direct(target, _put(column, "per_question", value))


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("column", sorted(_REQUIRED_EMPTY_VALUES))
def test_the_same_value_in_the_pooled_row_is_the_direct_legal_twin(target, column):
    """Placement, not value: the identical cell passes one setting over."""
    value = 1 if column in _BINARY_COLUMNS else 0.5
    df, n_a, n_b = _direct(target, _put(column, "pooled", value))
    assert (n_a, n_b) == (2, 1) and len(df) == 3


# ─────── unconsumed binary columns: genuine integers, dtype and value ─────────

@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("cast", ["boolean", "float64", "str", "object"])
def test_direct_frame_refuses_a_laundered_unconsumed_binary_column(target, cast):
    transform = (lambda s: s.astype(object)) if cast == "object" else (
        lambda s: s.astype(cast)
    )
    with pytest.raises(ValueError, match=_MISSING_BINARY_MESSAGE):
        _direct(target, _retype(_UNCONSUMED_BINARY, transform))


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("value", [2, -1, 10])
def test_direct_frame_refuses_a_non_binary_integer_in_an_unconsumed_column(
        target, value):
    with pytest.raises(ValueError, match=_MISSING_BINARY_MESSAGE):
        _direct(target, _put(_UNCONSUMED_BINARY, "pooled", value))


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("value", [0, 1])
def test_direct_frame_accepts_a_genuine_integer_in_an_unconsumed_column(
        target, value):
    df, _, _ = _direct(target, _put(_UNCONSUMED_BINARY, "pooled", value))
    assert list(df.columns) == sl.OUTPUT_COLUMNS


# ────────── unconsumed float columns: numeric, finite, inside [0,1] ───────────

@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("column", _UNCONSUMED_FLOATS)
@pytest.mark.parametrize("value", [-0.1, 1.1, 2.0, float("inf"), float("-inf")])
def test_direct_frame_refuses_an_out_of_domain_unconsumed_float(
        target, column, value):
    """the third demonstrated bypass, generalized across families and frames."""
    with pytest.raises(ValueError, match=_OUT_OF_DOMAIN_MESSAGE):
        _direct(target, _put(column, "pooled", value))


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("column", _UNCONSUMED_FLOATS)
@pytest.mark.parametrize("value", [0.0, 1.0, 0.5, 1e-9])
def test_direct_frame_accepts_an_in_domain_unconsumed_float(target, column, value):
    """Legal twins, including both inclusive boundaries."""
    df, _, _ = _direct(target, _put(column, "pooled", value))
    assert list(df.columns) == sl.OUTPUT_COLUMNS


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("column", _UNCONSUMED_FLOATS)
def test_direct_frame_refuses_a_nan_in_an_unconsumed_float(target, column):
    """On a typed frame `NaN` is the absent marker, so it refuses on placement."""
    with pytest.raises(ValueError, match=_MISSING_FLOAT_MESSAGE):
        _direct(target, _put(column, "pooled", np.nan))


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("cast", ["str", "object"])
def test_direct_frame_refuses_a_non_numeric_unconsumed_float_column(target, cast):
    transform = (lambda s: s.astype(object)) if cast == "object" else (
        lambda s: s.astype(str)
    )
    with pytest.raises(ValueError, match="is not numeric"):
        _direct(target, _retype("reciprocal_rank_at_50", transform))


@pytest.mark.parametrize("target", _TARGETS)
def test_direct_frame_contract_holds_for_the_other_supported_setting(target):
    """Selecting `per_question` does not narrow the frame contract to it."""
    with pytest.raises(ValueError, match=_OUT_OF_DOMAIN_MESSAGE):
        _direct(target, _put("reciprocal_rank_at_50", "pooled", 1.1),
                setting="per_question")
    df, n_a, n_b = sl.build_shortlist(_bm25(), _dense(), "full_evidence_recall",
                                      5, "per_question", 15)
    assert (n_a, n_b) == (2, 1) and len(df) == 3


# ──────────── the accepted formal bundle still produces its 30 rows ───────────

def test_the_real_loaded_frames_are_still_accepted_directly():
    """The review's legal control: untouched real inputs, direct public API."""
    bm25 = load_result_csv("results/bm25_results.csv", "bm25")
    dense = load_result_csv("results/dense_results.csv", "dense")
    df, n_a, n_b = sl.build_shortlist(bm25, dense, "full_evidence_recall", 5,
                                      "pooled", 15)
    assert len(df) == 30
    assert int((df.observed_signal == sl.SIGNAL_DENSE_HIT_BM25_MISS).sum()) == 15
    assert int((df.observed_signal == sl.SIGNAL_BM25_NO_GOLD_IN_TOP2).sum()) == 15
    assert n_a >= 15 and n_b >= 15


@pytest.mark.parametrize("column,setting,value,message", [
    ("full_evidence_recall@10", "per_question", 1, _POPULATED_EMPTY_MESSAGE),
    ("reciprocal_rank_at_50", "per_question", np.nan, _MISSING_FLOAT_MESSAGE),
    ("partial_evidence_recall@5", "pooled", 1.1, _OUT_OF_DOMAIN_MESSAGE),
])
def test_the_three_demonstrated_bypasses_refuse_on_the_real_frames(
        column, setting, value, message):
    """The three mutations that previously slipped through, on the real frames."""
    bm25 = load_result_csv("results/bm25_results.csv", "bm25")
    dense = load_result_csv("results/dense_results.csv", "dense")
    dense.loc[dense["setting"] == setting, column] = value
    with pytest.raises(ValueError, match=message):
        sl.build_shortlist(bm25, dense, "full_evidence_recall", 5, "pooled", 15)
