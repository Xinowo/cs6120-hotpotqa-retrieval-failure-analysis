"""Regression tests for scripts/reporting/disagreement_cases.py.

Covers the frozen contract in
docs/specs/2026-07-27-bm25-dense-reporting-contracts.md: the closed join
(unique keys, cross-method id parity, null-aware metadata identity, closed
metadata value domains), the binary-only criterion, the closed `setting`
vocabulary on the direct public argument as well as the CLI, strict
plain-integer consumed cells for BM25/dense/optional rerank before any `int()`
conversion, and deterministic / exact-schema empty output. Every rejection has
a legal control differing only in the targeted property, and refusals neither
create nor overwrite the destination.

The physical-input sections also cover cells this tool never reads: an
out-of-domain float metric, a blank outside the three per-question `@10` recall
slots, and a populated value *inside* them are all refused before any write,
because a general reporting tool must not turn a truncated, impossible, or
K-policy-violating formal bundle into a normal-looking report. The last of those
is the inverse half of the placement rule: the schema does not compute
per-question `@10`, so a value there is an unauthorized metric extension even
when it is spelled with an owner-approved lexeme.
"""

import csv
import math
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from scripts.reporting import disagreement_cases as dc
from scripts.reporting.formal_result_inputs import (
    BINARY_METRIC_COLUMNS,
    load_result_csv,
)
from src.results_schema import RESULT_COLUMNS

GOLD = "Gold A | Gold B"
# (example_id, question_type)
META = [("ex0", "bridge"), ("ex1", "bridge"), ("ex2", "comparison"),
        ("ex3", "bridge"), ("ex4", "comparison"), ("ex5", "bridge")]
DEFAULT_RETRIEVED = "Gold A | Gold B | X | Y | Z"

CONSUMED = "full_evidence_recall@5"
SCRIPT = "scripts/reporting/disagreement_cases.py"


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


# bm25 vs dense full@5 hits (index-aligned with META).
BM25_HITS = [0, 1, 1, 0, 0, 1]
DENSE_HITS = [1, 0, 1, 0, 1, 0]
RERANK_HITS = [1, 1, 0, 0, 1, 0]


def _bm25():
    return _frame("bm25", BM25_HITS)


def _dense():
    return _frame("dense", DENSE_HITS)


def _rerank():
    return _frame("rerank", RERANK_HITS)


# ─────────────────────────────── happy path ──────────────────────────────────

def test_default_full5_pooled_disagreements_and_deterministic_order():
    df = dc.extract_disagreements(_bm25(), _dense(), "full_evidence_recall", 5, "pooled")
    assert list(df.columns) == dc.OUTPUT_COLUMNS
    assert len(df) == 4
    assert int((df.direction == "dense_only").sum()) == 2
    assert int((df.direction == "bm25_only").sum()) == 2
    # deterministic: direction (dense_only<bm25_only), then question_type, then id
    assert df.example_id.tolist() == ["ex0", "ex4", "ex1", "ex5"]


def test_any5_legal_control_runs():
    df = dc.extract_disagreements(_bm25(), _dense(), "any_evidence_recall", 5, "pooled")
    assert len(df) == 4  # any@5 mirrors full@5 in this fixture


def test_empty_result_has_columns_and_no_rows():
    agree = [1, 1, 1, 1, 1, 1]
    df = dc.extract_disagreements(
        _frame("bm25", agree), _frame("dense", agree),
        "full_evidence_recall", 5, "pooled",
    )
    assert list(df.columns) == dc.OUTPUT_COLUMNS
    assert len(df) == 0


# ─────────────────────────── binary-only criterion ───────────────────────────

def test_partial_criterion_removed_from_cli():
    assert "partial_evidence_recall" not in dc.SUPPORTED_CRITERIA


def test_partial_criterion_rejected():
    with pytest.raises(ValueError, match="Unsupported criterion"):
        dc.extract_disagreements(
            _bm25(), _dense(), "partial_evidence_recall", 5, "pooled"
        )


# ──────────────────────── closed public `setting` domain ─────────────────────

@pytest.mark.parametrize("setting", ["bogus", "", None, "Pooled", "POOLED",
                                     "per-question", " pooled", 0])
def test_reject_unsupported_direct_setting(setting):
    """An unsupported setting must refuse, never filter down to zero rows."""
    with pytest.raises(ValueError, match="Unsupported setting"):
        dc.extract_disagreements(
            _bm25(), _dense(), "full_evidence_recall", 5, setting
        )


@pytest.mark.parametrize("setting", ["pooled", "per_question"])
def test_accept_supported_direct_setting(setting):
    df = dc.extract_disagreements(
        _bm25(), _dense(), "full_evidence_recall", 5, setting
    )
    assert list(df.columns) == dc.OUTPUT_COLUMNS
    assert len(df) == 4
    assert set(df.setting.unique()) == {setting}


@pytest.mark.parametrize("setting", ["pooled", "per_question"])
def test_supported_setting_with_zero_cases_keeps_exact_schema(setting):
    """A genuinely empty result stays valid output for a supported setting."""
    agree = [1, 1, 1, 1, 1, 1]
    df = dc.extract_disagreements(
        _frame("bm25", agree), _frame("dense", agree),
        "full_evidence_recall", 5, setting,
    )
    assert list(df.columns) == dc.OUTPUT_COLUMNS
    assert len(df) == 0


def test_reject_unsupported_setting_before_touching_destination(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "disagreement_cases.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)

    with pytest.raises(ValueError, match="Unsupported setting"):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "bogus", str(out_path))
    assert not out_path.exists()


def test_cli_rejects_unsupported_setting(tmp_path):
    out_path = tmp_path / "disagreement_cases.csv"
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
    out_path = tmp_path / "disagreement_cases.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)

    completed = subprocess.run(
        [sys.executable, SCRIPT,
         "--bm25", str(bm25_path), "--dense", str(dense_path),
         "--setting", "per_question", "--k", "2", "--out", str(out_path)],
        capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert list(pd.read_csv(out_path).columns) == dc.OUTPUT_COLUMNS


# ─────────────────────────────── closed join ─────────────────────────────────

def test_reject_duplicate_key_within_setting():
    bm25 = _bm25()
    dup = bm25[(bm25.setting == "pooled") & (bm25.example_id == "ex0")]
    bm25 = pd.concat([bm25, dup], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate example_id"):
        dc.extract_disagreements(bm25, _dense(), "full_evidence_recall", 5, "pooled")


def test_reject_cross_method_id_drift():
    dense = _dense()
    dense = dense[dense.example_id != "ex5"]  # dense missing an id bm25 has
    with pytest.raises(ValueError, match="example_id sets differ across methods"):
        dc.extract_disagreements(_bm25(), dense, "full_evidence_recall", 5, "pooled")


def test_reject_cross_method_metadata_drift():
    dense = _dense()
    dense.loc[dense.example_id == "ex0", "question_type"] = "comparison"
    with pytest.raises(ValueError, match="metadata drift"):
        dc.extract_disagreements(_bm25(), dense, "full_evidence_recall", 5, "pooled")


@pytest.mark.parametrize("method", ["bm25", "dense"])
def test_reject_one_sided_null_metadata(method):
    """A question present on one side and missing on the other must refuse, and
    must never be emitted as a null question."""
    frames = {"bm25": _bm25(), "dense": _dense()}
    frames[method].loc[frames[method].example_id == "ex0", "question"] = np.nan
    with pytest.raises(ValueError, match="question must be a non-null string"):
        dc.extract_disagreements(
            frames["bm25"], frames["dense"], "full_evidence_recall", 5, "pooled"
        )


def test_reject_two_sided_null_metadata():
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame.loc[frame.example_id == "ex0", "question"] = np.nan
    with pytest.raises(ValueError, match="question must be a non-null string"):
        dc.extract_disagreements(bm25, dense, "full_evidence_recall", 5, "pooled")


def test_accept_non_null_metadata_on_both_sides():
    df = dc.extract_disagreements(_bm25(), _dense(), "full_evidence_recall", 5, "pooled")
    assert df.question.notna().all()
    assert all(isinstance(value, str) for value in df.question.tolist())


# ──────────────────── closed upstream metadata vocabularies ──────────────────

def test_reject_unknown_question_type_consistent_across_methods():
    """Consistent drift is still an upstream-invalid value, not a legal bundle."""
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame.loc[frame.example_id == "ex0", "question_type"] = "other"
    with pytest.raises(ValueError, match="question_type.*must be exactly"):
        dc.extract_disagreements(bm25, dense, "full_evidence_recall", 5, "pooled")


def test_reject_unknown_level_consistent_across_methods():
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame.loc[frame.example_id == "ex0", "level"] = "trivial"
    with pytest.raises(ValueError, match="level.*must be exactly"):
        dc.extract_disagreements(bm25, dense, "full_evidence_recall", 5, "pooled")


@pytest.mark.parametrize("question_type", ["bridge", "comparison"])
@pytest.mark.parametrize("level", ["easy", "medium", "hard"])
def test_accept_every_schema_vocabulary_value(question_type, level):
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame["question_type"] = question_type
        frame["level"] = level
    df = dc.extract_disagreements(bm25, dense, "full_evidence_recall", 5, "pooled")
    assert len(df) == 4


# ───────────────────── strict consumed-cell value domain ─────────────────────

@pytest.mark.parametrize("method", ["bm25", "dense"])
def test_reject_bool_consumed_cell(method):
    frames = {"bm25": _bm25(), "dense": _dense()}
    frames[method][CONSUMED] = frames[method][CONSUMED].astype(bool)
    with pytest.raises(ValueError, match="non-0/1"):
        dc.extract_disagreements(
            frames["bm25"], frames["dense"], "full_evidence_recall", 5, "pooled"
        )


@pytest.mark.parametrize("method", ["bm25", "dense"])
def test_reject_float_binary_consumed_cell(method):
    """Physical float 0.0/1.0 is refused even though it equals 0/1."""
    frames = {"bm25": _bm25(), "dense": _dense()}
    frames[method][CONSUMED] = frames[method][CONSUMED].astype(float)
    with pytest.raises(ValueError, match="non-0/1"):
        dc.extract_disagreements(
            frames["bm25"], frames["dense"], "full_evidence_recall", 5, "pooled"
        )


@pytest.mark.parametrize("method", ["bm25", "dense"])
def test_reject_numeric_string_consumed_cell(method):
    frames = {"bm25": _bm25(), "dense": _dense()}
    frames[method][CONSUMED] = frames[method][CONSUMED].astype(str)
    with pytest.raises(ValueError, match="non-0/1"):
        dc.extract_disagreements(
            frames["bm25"], frames["dense"], "full_evidence_recall", 5, "pooled"
        )


@pytest.mark.parametrize("method", ["bm25", "dense"])
def test_reject_null_consumed_cell(method):
    frames = {"bm25": _bm25(), "dense": _dense()}
    frame = frames[method]
    frame.loc[(frame.setting == "pooled") & (frame.example_id == "ex0"),
              CONSUMED] = pd.NA
    with pytest.raises(ValueError, match="non-0/1"):
        dc.extract_disagreements(
            frames["bm25"], frames["dense"], "full_evidence_recall", 5, "pooled"
        )


def test_reject_non_binary_consumed_cell():
    dense = _dense()
    dense[CONSUMED] = dense[CONSUMED].astype(float)
    dense.loc[(dense.setting == "pooled") & (dense.example_id == "ex0"),
              CONSUMED] = 0.5
    with pytest.raises(ValueError, match="non-0/1"):
        dc.extract_disagreements(_bm25(), dense, "full_evidence_recall", 5, "pooled")


def test_accept_plain_integer_consumed_cells():
    """Legal control for the strict binary predicate."""
    df = dc.extract_disagreements(_bm25(), _dense(), "full_evidence_recall", 5, "pooled")
    assert set(df.bm25_hit.unique()) <= {0, 1}
    assert set(df.dense_hit.unique()) <= {0, 1}


# ─────────────────────────── optional rerank path ────────────────────────────

def test_rerank_legal_control_appends_hit_column():
    df = dc.extract_disagreements(
        _bm25(), _dense(), "full_evidence_recall", 5, "pooled", rerank=_rerank()
    )
    assert "rerank_hit" in df.columns
    assert set(df.rerank_hit.unique()) <= {0, 1}


def test_rerank_non_binary_cell_rejected_before_conversion():
    rerank = _rerank()
    rerank[CONSUMED] = rerank[CONSUMED].astype(float)
    rerank.loc[(rerank.setting == "pooled") & (rerank.example_id == "ex0"),
               CONSUMED] = 0.5
    with pytest.raises(ValueError, match="non-0/1"):
        dc.extract_disagreements(
            _bm25(), _dense(), "full_evidence_recall", 5, "pooled", rerank=rerank
        )


@pytest.mark.parametrize("corruption", ["bool", "float", "string", "null"])
def test_rerank_consumed_cell_value_domain(corruption):
    """The optional rerank frame is held to the same strict cell domain."""
    rerank = _rerank()
    if corruption == "bool":
        rerank[CONSUMED] = rerank[CONSUMED].astype(bool)
    elif corruption == "float":
        rerank[CONSUMED] = rerank[CONSUMED].astype(float)
    elif corruption == "string":
        rerank[CONSUMED] = rerank[CONSUMED].astype(str)
    else:
        rerank.loc[(rerank.setting == "pooled") & (rerank.example_id == "ex0"),
                   CONSUMED] = pd.NA
    with pytest.raises(ValueError, match="non-0/1"):
        dc.extract_disagreements(
            _bm25(), _dense(), "full_evidence_recall", 5, "pooled", rerank=rerank
        )


def test_rerank_metadata_domain_enforced():
    rerank = _rerank()
    rerank.loc[rerank.example_id == "ex0", "level"] = "trivial"
    with pytest.raises(ValueError, match="level.*must be exactly"):
        dc.extract_disagreements(
            _bm25(), _dense(), "full_evidence_recall", 5, "pooled", rerank=rerank
        )


def test_rerank_missing_id_rejected():
    rerank = _rerank()
    rerank = rerank[rerank.example_id != "ex0"]
    with pytest.raises(ValueError, match="example_id sets differ across methods"):
        dc.extract_disagreements(
            _bm25(), _dense(), "full_evidence_recall", 5, "pooled", rerank=rerank
        )


def test_rerank_unsupported_setting_rejected():
    with pytest.raises(ValueError, match="Unsupported setting"):
        dc.extract_disagreements(
            _bm25(), _dense(), "full_evidence_recall", 5, "bogus", rerank=_rerank()
        )


# ──────────────── no-create / no-overwrite on refusal (main) ─────────────────

def test_main_refusal_does_not_create_output(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "disagreement_cases.csv"
    _bm25().to_csv(bm25_path, index=False)
    dense = _dense()
    dense.loc[dense.example_id == "ex0", "question_type"] = "comparison"  # drift
    dense.to_csv(dense_path, index=False)

    with pytest.raises(ValueError):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(out_path))
    assert not out_path.exists()


def test_main_refusal_does_not_overwrite_existing_output(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "disagreement_cases.csv"
    _bm25().to_csv(bm25_path, index=False)
    dense = _dense()
    dense.loc[dense.example_id == "ex0", "question_type"] = "comparison"  # drift
    dense.to_csv(dense_path, index=False)
    out_path.write_bytes(b"SENTINEL")

    with pytest.raises(ValueError):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(out_path))
    assert out_path.read_bytes() == b"SENTINEL"


def test_main_legal_control_writes_output(tmp_path):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    out_path = tmp_path / "disagreement_cases.csv"
    _bm25().to_csv(bm25_path, index=False)
    _dense().to_csv(dense_path, index=False)

    dc.main(str(bm25_path), str(dense_path), None,
            "full_evidence_recall", 5, "pooled", str(out_path))
    assert list(pd.read_csv(out_path).columns) == dc.OUTPUT_COLUMNS


# ─────────── physical parsing: lexemes, null-like text, title cells ──────────
# The frozen lexeme rule and column-aware NA policy (contract sections 1.1
# and 1.2), exercised end-to-end through `main`.

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


def _bundle_files(tmp_path, bm25=None, dense=None):
    bm25_path = tmp_path / "bm25.csv"
    dense_path = tmp_path / "dense.csv"
    (bm25 if bm25 is not None else _bm25()).to_csv(bm25_path, index=False)
    (dense if dense is not None else _dense()).to_csv(dense_path, index=False)
    return bm25_path, dense_path


@pytest.mark.parametrize("lexeme", ["0.00000000000000000001",
                                    "0.99999999999999999999", "0.5", "True",
                                    "1e0", "+1", " 1", "01", "1.00", "NaN"])
def test_main_refuses_an_unapproved_binary_lexeme(tmp_path, lexeme):
    bm25_path, dense_path = _bundle_files(tmp_path)
    out_path = tmp_path / "disagreement_cases.csv"
    _corrupt_lexeme(dense_path, CONSUMED, lexeme)
    out_path.write_bytes(b"SENTINEL")

    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(out_path))
    assert out_path.read_bytes() == b"SENTINEL"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(missing))
    assert not missing.exists()


@pytest.mark.parametrize("lexeme", ["0", "1", "0.0", "1.0"])
def test_main_accepts_every_approved_binary_lexeme(tmp_path, lexeme):
    """Legal twin: the same corruption site, spelled an approved way."""
    bm25_path, dense_path = _bundle_files(tmp_path)
    out_path = tmp_path / "disagreement_cases.csv"
    _corrupt_lexeme(dense_path, CONSUMED, lexeme)

    dc.main(str(bm25_path), str(dense_path), None,
            "full_evidence_recall", 5, "pooled", str(out_path))
    assert list(pd.read_csv(out_path).columns) == dc.OUTPUT_COLUMNS


@pytest.mark.parametrize("lexeme", ["0.00000000000000000001", "0.5", "NaN"])
def test_rerank_file_is_held_to_the_same_lexeme_rule(tmp_path, lexeme):
    bm25_path, dense_path = _bundle_files(tmp_path)
    rerank_path = tmp_path / "rerank.csv"
    _rerank().to_csv(rerank_path, index=False)
    _corrupt_lexeme(rerank_path, CONSUMED, lexeme)
    out_path = tmp_path / "disagreement_cases.csv"

    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        dc.main(str(bm25_path), str(dense_path), str(rerank_path),
                "full_evidence_recall", 5, "pooled", str(out_path))
    assert not out_path.exists()


def test_rerank_file_legal_twin(tmp_path):
    bm25_path, dense_path = _bundle_files(tmp_path)
    rerank_path = tmp_path / "rerank.csv"
    _rerank().to_csv(rerank_path, index=False)
    _corrupt_lexeme(rerank_path, CONSUMED, "1.0")
    out_path = tmp_path / "disagreement_cases.csv"

    dc.main(str(bm25_path), str(dense_path), str(rerank_path),
            "full_evidence_recall", 5, "pooled", str(out_path))
    assert "rerank_hit" in pd.read_csv(out_path).columns


@pytest.mark.parametrize("literal", ["None", "NA", "null", "NaN", "nan", "<NA>"])
def test_null_like_question_text_survives_into_the_output(tmp_path, literal):
    """A legitimate `None`/`NA`/`null`/`NaN` question is text, not a missing value."""
    bm25, dense = _bm25(), _dense()
    for frame in (bm25, dense):
        frame.loc[frame.example_id == "ex0", "question"] = literal
    bm25_path, dense_path = _bundle_files(tmp_path, bm25, dense)
    out_path = tmp_path / "disagreement_cases.csv"

    dc.main(str(bm25_path), str(dense_path), None,
            "full_evidence_recall", 5, "pooled", str(out_path))

    written = pd.read_csv(out_path, keep_default_na=False, na_filter=False)
    assert written.loc[written.example_id == "ex0", "question"].tolist() == [literal]


@pytest.mark.parametrize("literal", ["NaN", "NA", "null", "None"])
def test_null_like_metric_token_is_refused_not_read_as_blank(tmp_path, literal):
    """The same word that is legal in `question` is illegal in a metric cell."""
    bm25_path, dense_path = _bundle_files(tmp_path)
    _corrupt_lexeme(dense_path, "full_evidence_recall@10", literal)
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled",
                str(tmp_path / "disagreement_cases.csv"))


def test_blank_per_question_at10_is_the_legal_twin(tmp_path):
    """A blank in the one slot the schema leaves uncomputed stays legal."""
    bm25_path, dense_path = _bundle_files(tmp_path)
    _corrupt_lexeme(dense_path, "full_evidence_recall@10", "",
                    setting="per_question")
    out_path = tmp_path / "disagreement_cases.csv"
    dc.main(str(bm25_path), str(dense_path), None,
            "full_evidence_recall", 5, "pooled", str(out_path))
    assert list(pd.read_csv(out_path).columns) == dc.OUTPUT_COLUMNS


# ─────── malformed *unconsumed* metric cells still refuse, without writing ────
# The selected criterion is `full_evidence_recall@5`, so none of the cells below
# is read by the tool. A general reporting tool must still refuse the bundle:
# otherwise a truncated or impossible formal file produces a normal-looking
# report. Each probe proves both no-create and no-overwrite.

# (column, lexeme, setting, expected message) — every cell here is unconsumed.
_MALFORMED_UNCONSUMED = [
    ("partial_evidence_recall@5", "1.1", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@5", "-0.1", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@5", "1e9999", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@2", "1.0000000000000001", "per_question",
     r"outside the inclusive \[0, 1\] domain"),
    ("reciprocal_rank_at_10", "2", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("reciprocal_rank_at_50", "-1e-400", "per_question",
     r"outside the inclusive \[0, 1\] domain"),
    ("any_evidence_recall@2", "", "pooled", "empty cell where the schema permits none"),
    ("full_evidence_recall@10", "", "pooled", "empty cell where the schema permits none"),
    ("partial_evidence_recall@5", "", "pooled", "empty cell where the schema permits none"),
    ("full_evidence_recall@2", "", "per_question", "empty cell where the schema permits none"),
    ("reciprocal_rank_at_10", "", "pooled", "empty cell where the schema permits none"),
    ("reciprocal_rank_at_50", "", "per_question", "empty cell where the schema permits none"),
]


@pytest.mark.parametrize("column,lexeme,setting,message", _MALFORMED_UNCONSUMED)
def test_main_refuses_a_malformed_unconsumed_metric_without_writing(
        tmp_path, column, lexeme, setting, message):
    bm25_path, dense_path = _bundle_files(tmp_path)
    _corrupt_lexeme(dense_path, column, lexeme, setting=setting)

    existing = tmp_path / "disagreement_cases.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match=message):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(existing))
    assert existing.read_bytes() == b"SENTINEL"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match=message):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(missing))
    assert not missing.exists()


@pytest.mark.parametrize("column,lexeme", [
    ("partial_evidence_recall@5", "1.0"),
    ("partial_evidence_recall@5", "0.0"),
    ("partial_evidence_recall@2", "0.999999999999999999999"),
    ("reciprocal_rank_at_10", "1"),
    ("reciprocal_rank_at_50", "1e-3"),
])
def test_main_accepts_an_in_domain_unconsumed_metric(tmp_path, column, lexeme):
    """Legal twins: the same unconsumed cells, spelled inside `[0,1]`."""
    bm25_path, dense_path = _bundle_files(tmp_path)
    _corrupt_lexeme(dense_path, column, lexeme)
    out_path = tmp_path / "disagreement_cases.csv"

    dc.main(str(bm25_path), str(dense_path), None,
            "full_evidence_recall", 5, "pooled", str(out_path))
    assert list(pd.read_csv(out_path).columns) == dc.OUTPUT_COLUMNS


@pytest.mark.parametrize("column", ["any_evidence_recall@10",
                                    "full_evidence_recall@10",
                                    "partial_evidence_recall@10"])
def test_rerank_file_blank_placement_is_enforced_too(tmp_path, column):
    """The optional rerank frame is held to the same blank-placement rule."""
    bm25_path, dense_path = _bundle_files(tmp_path)
    rerank_path = tmp_path / "rerank.csv"
    _rerank().to_csv(rerank_path, index=False)
    _corrupt_lexeme(rerank_path, column, "", setting="pooled")
    out_path = tmp_path / "disagreement_cases.csv"

    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        dc.main(str(bm25_path), str(dense_path), str(rerank_path),
                "full_evidence_recall", 5, "pooled", str(out_path))
    assert not out_path.exists()

    # Legal twin: the same blank, in the per_question row the schema permits.
    _rerank().to_csv(rerank_path, index=False)
    _corrupt_lexeme(rerank_path, column, "", setting="per_question")
    dc.main(str(bm25_path), str(dense_path), str(rerank_path),
            "full_evidence_recall", 5, "pooled", str(out_path))
    assert "rerank_hit" in pd.read_csv(out_path).columns


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
    bm25_path, dense_path = _bundle_files(tmp_path)
    _corrupt_lexeme(bm25_path if target == "bm25" else dense_path,
                    column, token, setting="per_question")

    existing = tmp_path / "disagreement_cases.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match=_REQUIRED_EMPTY_MESSAGE):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(existing))
    assert existing.read_bytes() == b"SENTINEL"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match=_REQUIRED_EMPTY_MESSAGE):
        dc.main(str(bm25_path), str(dense_path), None,
                "full_evidence_recall", 5, "pooled", str(missing))
    assert not missing.exists()


@pytest.mark.parametrize("column,token", _REQUIRED_EMPTY_MUTATIONS)
def test_rerank_file_required_empty_placement_is_enforced_too(
        tmp_path, column, token):
    """The optional rerank frame shares the same input language, both ways."""
    bm25_path, dense_path = _bundle_files(tmp_path)
    rerank_path = tmp_path / "rerank.csv"
    _rerank().to_csv(rerank_path, index=False)
    _corrupt_lexeme(rerank_path, column, token, setting="per_question")

    existing = tmp_path / "disagreement_cases.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match=_REQUIRED_EMPTY_MESSAGE):
        dc.main(str(bm25_path), str(dense_path), str(rerank_path),
                "full_evidence_recall", 5, "pooled", str(existing))
    assert existing.read_bytes() == b"SENTINEL"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match=_REQUIRED_EMPTY_MESSAGE):
        dc.main(str(bm25_path), str(dense_path), str(rerank_path),
                "full_evidence_recall", 5, "pooled", str(missing))
    assert not missing.exists()


@pytest.mark.parametrize("target", ["bm25", "dense", "rerank"])
@pytest.mark.parametrize("column,token", _REQUIRED_EMPTY_MUTATIONS)
def test_the_same_token_in_the_pooled_row_is_the_legal_twin(
        tmp_path, target, column, token):
    """Placement, not spelling: the identical token passes in the pooled row."""
    bm25_path, dense_path = _bundle_files(tmp_path)
    rerank_path = tmp_path / "rerank.csv"
    _rerank().to_csv(rerank_path, index=False)
    _corrupt_lexeme({"bm25": bm25_path, "dense": dense_path,
                     "rerank": rerank_path}[target],
                    column, token, setting="pooled")
    out_path = tmp_path / "disagreement_cases.csv"

    dc.main(str(bm25_path), str(dense_path), str(rerank_path),
            "full_evidence_recall", 5, "pooled", str(out_path))
    assert list(pd.read_csv(out_path).columns) == \
        dc.OUTPUT_COLUMNS + dc.RERANK_COLUMNS


def test_empty_retrieved_list_is_emitted_as_empty_not_nan(tmp_path):
    bm25 = _frame("bm25", BM25_HITS, retrieved_by_id={"ex0": ""})
    bm25_path, dense_path = _bundle_files(tmp_path, bm25)
    out_path = tmp_path / "disagreement_cases.csv"

    dc.main(str(bm25_path), str(dense_path), None,
            "full_evidence_recall", 5, "pooled", str(out_path))

    text = out_path.read_text(encoding="utf-8")
    assert ",nan," not in text and ",NaN," not in text
    written = pd.read_csv(out_path, keep_default_na=False, na_filter=False)
    ex0 = written[written.example_id == "ex0"]
    assert ex0.bm25_retrieved_titles.tolist() == [""]


def test_populated_retrieved_list_is_the_legal_twin(tmp_path):
    bm25_path, dense_path = _bundle_files(tmp_path)
    out_path = tmp_path / "disagreement_cases.csv"
    dc.main(str(bm25_path), str(dense_path), None,
            "full_evidence_recall", 5, "pooled", str(out_path))
    written = pd.read_csv(out_path)
    assert (written.bm25_retrieved_titles == DEFAULT_RETRIEVED).all()


@pytest.mark.parametrize("value", [np.nan, None, pd.NA])
def test_missing_retrieved_titles_in_a_direct_frame_refuses(value):
    bm25 = _bm25()
    bm25["retrieved_titles"] = bm25["retrieved_titles"].astype(object)
    bm25.loc[bm25.example_id == "ex0", "retrieved_titles"] = value
    with pytest.raises(ValueError, match="retrieved_titles must be a string"):
        dc.extract_disagreements(bm25, _dense(), "full_evidence_recall", 5, "pooled")


# ══════ the direct typed-frame entry point, including unconsumed columns ══════
# Everything above this line reaches the contract through a file, or through the
# one column the tool consumes. `extract_disagreements` is also a public
# function that accepts already-created DataFrames, and a caller using it can
# supply a bundle whose *unconsumed* metric cells are malformed. The selected
# criterion throughout this section is `full_evidence_recall@5`, so none of the
# cells mutated below is ever read — which is exactly why trusting them was the
# defect: a whole-frame contract is the only thing that can see them.
#
# No file is written or read in this section, and no fixture is loaded through
# the CSV reader, so nothing here can be satisfied by the raw lexeme layer.

_METRIC_COLUMNS = [
    "any_evidence_recall@2", "any_evidence_recall@5", "any_evidence_recall@10",
    "full_evidence_recall@2", "full_evidence_recall@5", "full_evidence_recall@10",
    "partial_evidence_recall@2", "partial_evidence_recall@5",
    "partial_evidence_recall@10",
    "reciprocal_rank_at_10", "reciprocal_rank_at_50",
]
_BINARY_COLUMNS = [c for c in _METRIC_COLUMNS if "partial" not in c
                   and "reciprocal" not in c]
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

# An unconsumed column of each family, so "the tool never reads this" is
# structural rather than incidental.
_UNCONSUMED_BINARY = "any_evidence_recall@2"
_UNCONSUMED_FLOATS = ["partial_evidence_recall@5", "reciprocal_rank_at_10",
                      "reciprocal_rank_at_50"]

_MISSING_BINARY_MESSAGE = "non-0/1"
_MISSING_FLOAT_MESSAGE = "missing cell where the schema requires a populated value"
_POPULATED_EMPTY_MESSAGE = "populated cell where the schema requires an empty one"
_OUT_OF_DOMAIN_MESSAGE = r"outside the inclusive \[0, 1\] domain"


def _missing_message(column):
    return _MISSING_BINARY_MESSAGE if column in _BINARY_COLUMNS \
        else _MISSING_FLOAT_MESSAGE


def _bundle(target=None, mutate=None):
    """The three legal frames, with at most one of them mutated in memory."""
    frames = {"bm25": _bm25(), "dense": _dense(), "rerank": _rerank()}
    if mutate is not None:
        frames[target] = mutate(frames[target])
    return frames


def _run(frames, with_rerank, setting="pooled"):
    return dc.extract_disagreements(
        frames["bm25"], frames["dense"], "full_evidence_recall", 5, setting,
        rerank=frames["rerank"] if with_rerank else None,
    )


def _put(column, setting, value):
    """Overwrite one `(column, setting)` slot of a frame, in place, no coercion."""
    def mutate(frame):
        frame.loc[frame["setting"] == setting, column] = value
        return frame
    return mutate


def _retype(column, transform):
    def mutate(frame):
        frame[column] = transform(frame[column])
        return frame
    return mutate


# `rerank` is only reachable when the optional argument is supplied.
_TARGETS = [("bm25", False), ("dense", False), ("rerank", True)]


# ───── every required-populated slot refuses a missing cell, all 3 frames ─────

@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("column,setting", _REQUIRED_POPULATED_SLOTS)
def test_direct_frame_refuses_a_missing_required_populated_slot(
        target, with_rerank, column, setting):
    """The complete 19-slot required-populated half, on a direct frame.

    the demonstrated blanked `reciprocal_rank_at_50` bypass is one cell of this
    matrix; the tool reads none of these columns.
    """
    frames = _bundle(target, _put(column, setting, None))
    with pytest.raises(ValueError, match=_missing_message(column)):
        _run(frames, with_rerank)


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("column,setting", _REQUIRED_POPULATED_SLOTS)
def test_direct_frame_accepts_the_populated_twin_of_that_slot(
        target, with_rerank, column, setting):
    """Legal twin for every rejection above: the same slot, legally populated."""
    value = 1 if column in _BINARY_COLUMNS else 0.75
    df = _run(_bundle(target, _put(column, setting, value)), with_rerank)
    assert list(df.columns) == dc.OUTPUT_COLUMNS + (
        dc.RERANK_COLUMNS if with_rerank else []
    )


# ───── every required-empty slot refuses a populated cell, all 3 frames ───────

_REQUIRED_EMPTY_VALUES = {
    "any_evidence_recall@10": [0, 1],
    "full_evidence_recall@10": [0, 1],
    "partial_evidence_recall@10": [0.0, 1.0, 0.5],
}


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize(
    "column,value",
    [(column, value) for column, values in sorted(_REQUIRED_EMPTY_VALUES.items())
     for value in values],
)
def test_direct_frame_refuses_a_populated_required_empty_slot(
        target, with_rerank, column, value):
    """the first demonstrated bypass, over all three slots and all three frames.

    Each value is legal in the same column's pooled row, so only placement is
    under test — and the rescue tool already refused exactly this, which is why
    accepting it here meant the three tools did not share one input language.
    """
    frames = _bundle(target, _put(column, "per_question", value))
    with pytest.raises(ValueError, match=_POPULATED_EMPTY_MESSAGE):
        _run(frames, with_rerank)


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("column", sorted(_REQUIRED_EMPTY_VALUES))
def test_the_same_value_in_the_pooled_row_is_the_direct_legal_twin(
        target, with_rerank, column):
    """Placement, not value: the identical cell passes one setting over."""
    value = 1 if column in _BINARY_COLUMNS else 0.5
    df = _run(_bundle(target, _put(column, "pooled", value)), with_rerank)
    assert len(df) == 4


# ─────── unconsumed binary columns: genuine integers, dtype and value ─────────

@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("cast", ["boolean", "float64", "str", "object"])
def test_direct_frame_refuses_a_laundered_unconsumed_binary_column(
        target, with_rerank, cast):
    """A bool / float / string / object binary column the tool never reads."""
    transform = (lambda s: s.astype(object)) if cast == "object" else (
        lambda s: s.astype(cast)
    )
    frames = _bundle(target, _retype(_UNCONSUMED_BINARY, transform))
    with pytest.raises(ValueError, match=_MISSING_BINARY_MESSAGE):
        _run(frames, with_rerank)


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("value", [2, -1, 10])
def test_direct_frame_refuses_a_non_binary_integer_in_an_unconsumed_column(
        target, with_rerank, value):
    frames = _bundle(target, _put(_UNCONSUMED_BINARY, "pooled", value))
    with pytest.raises(ValueError, match=_MISSING_BINARY_MESSAGE):
        _run(frames, with_rerank)


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("value", [0, 1])
def test_direct_frame_accepts_a_genuine_integer_in_an_unconsumed_column(
        target, with_rerank, value):
    df = _run(_bundle(target, _put(_UNCONSUMED_BINARY, "pooled", value)), with_rerank)
    assert len(df) == 4


# ────────── unconsumed float columns: numeric, finite, inside [0,1] ───────────

@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("column", _UNCONSUMED_FLOATS)
@pytest.mark.parametrize("value", [-0.1, 1.1, 2.0, float("inf"), float("-inf")])
def test_direct_frame_refuses_an_out_of_domain_unconsumed_float(
        target, with_rerank, column, value):
    """the third demonstrated bypass, generalized: negatives, >1, and both
    infinities, in every float family, for every frame."""
    frames = _bundle(target, _put(column, "pooled", value))
    with pytest.raises(ValueError, match=_OUT_OF_DOMAIN_MESSAGE):
        _run(frames, with_rerank)


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("column", _UNCONSUMED_FLOATS)
@pytest.mark.parametrize("value", [0.0, 1.0, 0.5, 1e-9])
def test_direct_frame_accepts_an_in_domain_unconsumed_float(
        target, with_rerank, column, value):
    """Legal twins, including both inclusive boundaries."""
    df = _run(_bundle(target, _put(column, "pooled", value)), with_rerank)
    assert len(df) == 4


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("column", _UNCONSUMED_FLOATS)
def test_direct_frame_refuses_a_nan_in_an_unconsumed_float(
        target, with_rerank, column):
    """On a typed frame `NaN` is the absent marker, so it refuses on placement."""
    frames = _bundle(target, _put(column, "pooled", np.nan))
    with pytest.raises(ValueError, match=_MISSING_FLOAT_MESSAGE):
        _run(frames, with_rerank)


@pytest.mark.parametrize("target,with_rerank", _TARGETS)
@pytest.mark.parametrize("cast", ["str", "object"])
def test_direct_frame_refuses_a_non_numeric_unconsumed_float_column(
        target, with_rerank, cast):
    transform = (lambda s: s.astype(object)) if cast == "object" else (
        lambda s: s.astype(str)
    )
    frames = _bundle(target, _retype("reciprocal_rank_at_50", transform))
    with pytest.raises(ValueError, match="is not numeric"):
        _run(frames, with_rerank)


# ─────────── the same defects refuse in the per_question setting too ──────────

@pytest.mark.parametrize("target,with_rerank", _TARGETS)
def test_direct_frame_contract_holds_for_the_other_supported_setting(
        target, with_rerank):
    """Selecting `per_question` does not narrow the frame contract to it."""
    frames = _bundle(target, _put("reciprocal_rank_at_50", "pooled", 1.1))
    with pytest.raises(ValueError, match=_OUT_OF_DOMAIN_MESSAGE):
        _run(frames, with_rerank, setting="per_question")

    legal = _run(_bundle(), with_rerank, setting="per_question")
    assert len(legal) == 4


# ─────────── the accepted formal bundle still produces its 220 rows ───────────

def test_the_real_loaded_frames_are_still_accepted_directly():
    """The review's legal control: untouched real inputs, direct public API."""
    bm25 = load_result_csv("results/bm25_results.csv", "bm25")
    dense = load_result_csv("results/dense_results.csv", "dense")
    df = dc.extract_disagreements(bm25, dense, "full_evidence_recall", 5, "pooled")
    assert len(df) == 220
    assert int((df.direction == "dense_only").sum()) == 160
    assert int((df.direction == "bm25_only").sum()) == 60


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
        dc.extract_disagreements(bm25, dense, "full_evidence_recall", 5, "pooled")
