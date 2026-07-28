"""Regression tests for scripts/reporting/rescue_damage.py.

Covers the frozen rescue/damage contract
(docs/specs/2026-07-26-reranker-rescue-damage.md): the §2 input contract
(cardinality, closed question-type partition, closed metadata value domains,
strict plain-integer consumed cells, null-aware metadata identity) and the §9
output contract (exact types/ranges/row order plus the safe writer). Every
rejection is paired with a legal control that differs only in the targeted
property, and refusals are shown not to create or overwrite the destination.

The physical-parsing section covers the `[0,1]` float domain and the
blank-placement rule on cells the counting never consumes, since a truncated or
impossible input bundle must not be able to produce a formal summary.
"""

import csv
import math

import numpy as np
import pandas as pd
import pytest

from scripts.reporting import rescue_damage
from scripts.reporting.formal_result_inputs import BINARY_METRIC_COLUMNS
from src.results_schema import RESULT_COLUMNS

BRIDGE_N = 404
COMPARISON_N = 96
PER_SETTING = 500

CONSUMED = "full_evidence_recall@5"


# ─────────────────────────── formal-bundle fixtures ──────────────────────────

def _meta(i):
    return {
        "example_id": f"ex{i:04d}",
        "question_type": "bridge" if i < BRIDGE_N else "comparison",
        "level": "hard",
        "question": f"Question {i}?",
        "gold_titles": "Gold A | Gold B",
    }


def _row(method, setting, i):
    row = {column: np.nan for column in RESULT_COLUMNS}
    row["method"] = method
    row["setting"] = setting
    row.update(_meta(i))
    row["retrieved_titles"] = "Gold A | Cand B | Cand C"
    # Deterministic 0/1 patterns that differ between dense and rerank so every
    # transition cell (stable_miss/rescue/damage/stable_hit) is exercised.
    full_hit = (1 if i % 2 == 0 else 0) if method == "dense" else (1 if i % 3 == 0 else 0)
    any_hit = (1 if i % 5 != 0 else 0) if method == "dense" else (1 if i % 4 != 0 else 0)
    for k in (2, 5, 10):
        row[f"full_evidence_recall@{k}"] = full_hit
        row[f"any_evidence_recall@{k}"] = any_hit
        row[f"partial_evidence_recall@{k}"] = 0.5
    row["reciprocal_rank_at_10"] = 0.5
    row["reciprocal_rank_at_50"] = 0.5
    if setting == "per_question":
        row["any_evidence_recall@10"] = np.nan
        row["full_evidence_recall@10"] = np.nan
        row["partial_evidence_recall@10"] = np.nan
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


def _file(method, ids):
    rows = [
        _row(method, setting, i)
        for setting in ("pooled", "per_question")
        for i in ids
    ]
    return _formal_frame(rows)


def _bundle(ids=None):
    ids = list(range(PER_SETTING)) if ids is None else list(ids)
    return _file("dense", ids), _file("rerank", ids)


def _set_qtype(df, eid, value):
    df.loc[df.example_id == eid, "question_type"] = value


def _valid_summary():
    dense, rerank = _bundle()
    paired = rescue_damage.build_paired_frame(dense, rerank)
    return rescue_damage.summarize_rescue_damage(paired), dense, rerank


def _write_bundle(tmp_path, dense, rerank):
    dense_path = tmp_path / "dense_results.csv"
    rerank_path = tmp_path / "rerank_results.csv"
    dense.to_csv(dense_path, index=False)
    rerank.to_csv(rerank_path, index=False)
    return str(dense_path), str(rerank_path)


# ─────────────────────────── happy path (legal control) ──────────────────────

def test_formal_shaped_bundle_produces_21_rows_deterministically(tmp_path):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    out_path = tmp_path / "rerank_rescue_damage.csv"

    rescue_damage.main(dense_path, rerank_path, str(out_path))
    first = out_path.read_bytes()
    rescue_damage.main(dense_path, rerank_path, str(out_path))
    second = out_path.read_bytes()

    written = pd.read_csv(out_path)
    assert list(written.columns) == rescue_damage.OUTPUT_COLUMNS
    assert len(written) == 21
    assert first == second  # deterministic bytes
    assert not first.startswith(b"\xef\xbb\xbf")  # no UTF-8 BOM
    overall = written[written.question_type == "overall"]
    assert (overall.n == 500).all()


# ──────────────────────── §2 cardinality / group partition ───────────────────

def test_reject_two_id_bundle_cardinality():
    dense, _ = _bundle(ids=[0, BRIDGE_N])  # one bridge + one comparison id
    with pytest.raises(ValueError, match="exactly 1000 rows"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


@pytest.mark.parametrize("n", [499, 501])
def test_reject_off_by_one_total_cardinality(n):
    dense, _ = _bundle(ids=range(n))
    with pytest.raises(ValueError, match="1000 rows"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_unknown_question_type():
    dense, _ = _bundle()
    _set_qtype(dense, "ex0000", "other")
    with pytest.raises(ValueError, match="question_type.*must be exactly"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_null_question_type():
    dense, _ = _bundle()
    _set_qtype(dense, "ex0000", np.nan)
    with pytest.raises(ValueError, match="question_type.*must be exactly"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_403_97_split():
    dense, _ = _bundle()
    _set_qtype(dense, "ex0403", "comparison")  # last bridge id -> comparison
    with pytest.raises(ValueError, match="bridge=403, comparison=97"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_accept_formal_404_96_split():
    dense, _ = _bundle()
    # Legal control: the untouched bundle passes the full per-file contract.
    rescue_damage._validate_one_file(dense, "dense", "dense")


# ──────────────────────── §2 closed metadata value domains ───────────────────

def test_reject_unknown_level():
    dense, _ = _bundle()
    dense.loc[dense.example_id == "ex0000", "level"] = "trivial"
    with pytest.raises(ValueError, match="level.*must be exactly"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_null_level():
    dense, _ = _bundle()
    dense.loc[dense.example_id == "ex0000", "level"] = np.nan
    with pytest.raises(ValueError, match="level.*must be exactly"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_accept_every_schema_level():
    """Legal control: all three schema levels are accepted."""
    for level in ("easy", "medium", "hard"):
        dense, _ = _bundle()
        dense["level"] = level
        rescue_damage._validate_one_file(dense, "dense", "dense")


@pytest.mark.parametrize("column", ["question", "gold_titles", "example_id"])
def test_reject_null_required_text_metadata(column):
    dense, _ = _bundle()
    dense.loc[dense.example_id == "ex0000", column] = np.nan
    with pytest.raises(ValueError, match=f"{column} must be a non-null string"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_non_string_question_metadata():
    dense, _ = _bundle()
    dense["question"] = dense["question"].astype(object)
    dense.loc[dense.example_id == "ex0000", "question"] = 12345
    with pytest.raises(ValueError, match="question must be a non-null string"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


# ────────────────────── §2 strict consumed-cell value domain ─────────────────

def test_accept_plain_integer_consumed_cells():
    """Legal control for the strict binary predicate."""
    dense, _ = _bundle()
    rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_bool_consumed_cell():
    dense, _ = _bundle()
    dense[CONSUMED] = dense[CONSUMED].astype(bool)
    with pytest.raises(ValueError, match="non-0/1"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_float_binary_consumed_cell():
    """Physical float 0.0/1.0 is refused even though it equals 0/1."""
    dense, _ = _bundle()
    dense[CONSUMED] = dense[CONSUMED].astype(float)
    with pytest.raises(ValueError, match="non-0/1"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_numeric_string_consumed_cell():
    dense, _ = _bundle()
    dense[CONSUMED] = dense[CONSUMED].astype(str)
    with pytest.raises(ValueError, match="non-0/1"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_null_consumed_cell():
    dense, _ = _bundle()
    dense.loc[
        (dense.setting == "pooled") & (dense.example_id == "ex0000"), CONSUMED
    ] = pd.NA
    with pytest.raises(ValueError, match="non-0/1"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_fractional_consumed_cell():
    dense, _ = _bundle()
    dense[CONSUMED] = dense[CONSUMED].astype(float)
    mask = (dense.setting == "pooled") & (dense.example_id == "ex0000")
    dense.loc[mask, CONSUMED] = 0.5
    with pytest.raises(ValueError, match="non-0/1"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_reject_populated_per_question_at10():
    dense, _ = _bundle()
    mask = (dense.setting == "per_question") & (dense.example_id == "ex0000")
    dense.loc[mask, "full_evidence_recall@10"] = 1
    with pytest.raises(ValueError, match="per_question.*must be blank"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


# ───────────────── §2 physical read domain (file-level controls) ─────────────

def test_loader_accepts_float_serialized_integer_cells(tmp_path):
    """The accepted formal files serialize `@10` as `0.0`/`1.0` (blanks force a
    float column upstream). Those are exact integers and must be accepted, then
    normalized to the nullable-integer physical type."""
    dense, rerank = _bundle()
    # Emulate the upstream serialization: the blank per_question cells make the
    # `@10` columns float, so their pooled values reach the CSV as `0.0`/`1.0`.
    at10 = ["any_evidence_recall@10", "full_evidence_recall@10"]
    dense_path, rerank_path = _write_bundle(
        tmp_path,
        dense.astype({column: float for column in at10}),
        rerank.astype({column: float for column in at10}),
    )
    assert ",1.0," in open(dense_path, encoding="utf-8").read()

    loaded, _ = rescue_damage.load_and_validate_inputs(dense_path, rerank_path)
    assert str(loaded["full_evidence_recall@10"].dtype) == "Int64"


def test_loader_rejects_physically_fractional_cell(tmp_path):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    text = open(dense_path, encoding="utf-8").read().replace(
        "Question 0?", "Question 0?", 1
    )
    lines = text.splitlines()
    header = lines[0].split(",")
    index = header.index(CONSUMED)
    cells = lines[1].split(",")
    cells[index] = "0.5"
    lines[1] = ",".join(cells)
    open(dense_path, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)


def test_loader_rejects_physical_boolean_cell(tmp_path):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    lines = open(dense_path, encoding="utf-8").read().splitlines()
    header = lines[0].split(",")
    index = header.index(CONSUMED)
    for position in (1, 2):
        cells = lines[position].split(",")
        cells[index] = "True" if cells[index] == "1" else "False"
        lines[position] = ",".join(cells)
    open(dense_path, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)


def test_main_refusal_does_not_create_or_overwrite_output(tmp_path):
    dense, rerank = _bundle()
    _set_qtype(dense, "ex0000", "other")  # closed-vocabulary violation
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError):
        rescue_damage.main(dense_path, rerank_path, str(missing))
    assert not missing.exists()

    existing = tmp_path / "existing.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError):
        rescue_damage.main(dense_path, rerank_path, str(existing))
    assert existing.read_bytes() == b"SENTINEL"


# ───────────────────── §2 null-aware cross-method identity ───────────────────

def test_reject_cross_setting_metadata_drift():
    dense, rerank = _bundle()
    # same id labelled bridge under pooled but comparison under per_question
    mask = (dense.setting == "per_question") & (dense.example_id == "ex0000")
    dense.loc[mask, "question_type"] = "comparison"
    rerank.loc[
        (rerank.setting == "per_question") & (rerank.example_id == "ex0000"),
        "question_type",
    ] = "comparison"
    with pytest.raises(ValueError, match="metadata drift"):
        rescue_damage._validate_cross(dense, rerank)


def test_reject_one_sided_null_metadata_in_identity_check():
    """A value present on one side and missing on the other is drift, not a
    match: the identity comparison must not drop missing values."""
    dense, rerank = _bundle()
    dense.loc[dense.example_id == "ex0000", "question"] = np.nan
    with pytest.raises(ValueError, match="metadata drift"):
        rescue_damage._validate_cross(dense, rerank)


def test_accept_identical_metadata_in_identity_check():
    dense, rerank = _bundle()
    rescue_damage._validate_cross(dense, rerank)


def test_two_sided_null_metadata_is_refused_by_the_file_contract():
    """Nulling both sides keeps identity intact, so the required-metadata
    domain check is what must refuse it."""
    dense, rerank = _bundle()
    for frame in (dense, rerank):
        frame.loc[frame.example_id == "ex0000", "question"] = np.nan
    rescue_damage._validate_cross(dense, rerank)  # identical on both sides
    with pytest.raises(ValueError, match="question must be a non-null string"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def _consistent_row(question_type, stable_miss, rescues, damages, stable_hit,
                    criterion="full_evidence_recall", setting="pooled", k=5):
    """A per-row internally consistent summary row (all §9.5 identities hold)."""
    n = stable_miss + rescues + damages + stable_hit
    dense_hits = damages + stable_hit
    rerank_hits = rescues + stable_hit
    net_count = rescues - damages
    return dict(
        criterion=criterion, setting=setting, k=k, question_type=question_type,
        n=n, dense_hits=dense_hits, rerank_hits=rerank_hits,
        stable_miss=stable_miss, rescues=rescues, damages=damages,
        stable_hit=stable_hit,
        rescue_rate=rescues / n, damage_rate=damages / n,
        net_count=net_count, net_rate=net_count / n,
        rescue_given_dense_miss=(np.nan if n == dense_hits
                                 else rescues / (n - dense_hits)),
        damage_given_dense_hit=(np.nan if dense_hits == 0
                                else damages / dense_hits),
    )


def test_partition_consistency_enforced_on_output():
    # Each row is internally consistent, but bridge (n=60) + comparison (n=30)
    # do not sum to overall (n=100): only the partition check should fire.
    rows = [
        _consistent_row("overall", 30, 20, 10, 40),
        _consistent_row("bridge", 18, 12, 6, 24),
        _consistent_row("comparison", 9, 6, 3, 12),
    ]
    frame = pd.DataFrame(rows, columns=rescue_damage.OUTPUT_COLUMNS)
    with pytest.raises(ValueError, match="partition broken"):
        rescue_damage.validate_summary_consistency(frame)


# ───────────────────────── §9.2 output type / range ──────────────────────────

def _summary_frame(**overrides):
    base = dict(
        criterion="full_evidence_recall", setting="pooled", k=5,
        question_type="overall", n=500, dense_hits=250, rerank_hits=300,
        stable_miss=200, rescues=100, damages=50, stable_hit=150,
        rescue_rate=0.2, damage_rate=0.1, net_count=50, net_rate=0.1,
        rescue_given_dense_miss=0.4, damage_given_dense_hit=0.2,
    )
    base.update(overrides)
    return pd.DataFrame([base], columns=rescue_damage.OUTPUT_COLUMNS)


def test_types_accept_valid_row_and_negative_net_count():
    rescue_damage.validate_output_types_and_ranges(_summary_frame())
    # net_count may legitimately be negative; net_rate stays in [-1, 1].
    rescue_damage.validate_output_types_and_ranges(
        _summary_frame(rescues=10, damages=60, net_count=-50, net_rate=-0.1)
    )


def test_types_reject_fractional_integer_cell():
    frame = _summary_frame()
    frame["stable_miss"] = frame["stable_miss"].astype(float)
    frame.loc[0, "stable_miss"] = 0.5
    with pytest.raises(ValueError, match="non-integer value"):
        rescue_damage.validate_output_types_and_ranges(frame)


def test_types_reject_bool_integer_cell():
    frame = _summary_frame()
    frame["stable_hit"] = frame["stable_hit"].astype(object)
    frame.loc[0, "stable_hit"] = True
    with pytest.raises(ValueError, match="non-integer value"):
        rescue_damage.validate_output_types_and_ranges(frame)


def test_types_reject_numeric_string_integer_cell():
    frame = _summary_frame()
    frame["n"] = frame["n"].astype(object)
    frame.loc[0, "n"] = "500"
    with pytest.raises(ValueError, match="non-integer value"):
        rescue_damage.validate_output_types_and_ranges(frame)


def test_types_reject_negative_count():
    with pytest.raises(ValueError, match="is negative"):
        rescue_damage.validate_output_types_and_ranges(
            _summary_frame(rescues=-1)
        )


def test_types_reject_infinite_rate():
    with pytest.raises(ValueError, match="finite float"):
        rescue_damage.validate_output_types_and_ranges(
            _summary_frame(net_rate=float("inf"))
        )


def test_types_reject_nan_required_rate():
    with pytest.raises(ValueError, match="finite float"):
        rescue_damage.validate_output_types_and_ranges(
            _summary_frame(rescue_rate=float("nan"))
        )


def test_types_reject_out_of_range_rate():
    with pytest.raises(ValueError, match="out of range"):
        rescue_damage.validate_output_types_and_ranges(
            _summary_frame(rescue_rate=1.5)
        )


def test_conditional_rate_must_be_blank_on_zero_denominator():
    # n == dense_hits -> rescue_given_dense_miss denominator is zero.
    frame = _summary_frame(dense_hits=500, rerank_hits=500,
                           stable_miss=0, rescues=0, damages=0, stable_hit=500,
                           rescue_rate=0.0, damage_rate=0.0, net_count=0,
                           net_rate=0.0, damage_given_dense_hit=0.0,
                           rescue_given_dense_miss=0.5)
    with pytest.raises(ValueError, match="must be a blank cell"):
        rescue_damage.validate_output_types_and_ranges(frame)


def test_conditional_rate_blank_accepted_on_zero_denominator():
    frame = _summary_frame(dense_hits=500, rerank_hits=500,
                           stable_miss=0, rescues=0, damages=0, stable_hit=500,
                           rescue_rate=0.0, damage_rate=0.0, net_count=0,
                           net_rate=0.0, damage_given_dense_hit=0.0,
                           rescue_given_dense_miss=np.nan)
    rescue_damage.validate_output_types_and_ranges(frame)


def test_conditional_rate_nan_rejected_when_denominator_nonzero():
    with pytest.raises(ValueError, match="finite float"):
        rescue_damage.validate_output_types_and_ranges(
            _summary_frame(rescue_given_dense_miss=np.nan)
        )


# ───────────────────────── §9.4 row order & §9.5 oracle ──────────────────────

def test_row_order_validator_rejects_shuffle():
    summary, _, _ = _valid_summary()
    shuffled = summary.iloc[::-1].reset_index(drop=True)
    with pytest.raises(ValueError, match="Row order does not match"):
        rescue_damage.validate_row_order(shuffled)


def test_oracle_rejects_rounded_net_rate():
    summary, dense, rerank = _valid_summary()
    rounded = summary.copy()
    rounded["net_rate"] = rounded["net_rate"].round(3)
    with pytest.raises(ValueError, match="Oracle mismatch"):
        rescue_damage.oracle_check(rounded, dense, rerank)


# ─────────────────── §9 safe writer (no-create / no-overwrite) ───────────────

def test_writer_refuses_and_does_not_create_destination(tmp_path):
    summary, _, _ = _valid_summary()
    corrupt = summary.copy()
    idx = corrupt.index[0]
    corrupt.loc[idx, "rescues"] = -1  # invalid but schema-shaped
    out_path = tmp_path / "rerank_rescue_damage.csv"
    with pytest.raises(ValueError):
        rescue_damage.write_rescue_damage_csv(corrupt, str(out_path))
    assert not out_path.exists()
    assert not (tmp_path / "rerank_rescue_damage.csv.tmp").exists()


def test_writer_refuses_and_does_not_overwrite_existing(tmp_path):
    summary, _, _ = _valid_summary()
    corrupt = summary.copy()
    corrupt["stable_miss"] = corrupt["stable_miss"].astype(float)
    corrupt.loc[corrupt.index[0], "stable_miss"] = 0.5
    out_path = tmp_path / "rerank_rescue_damage.csv"
    out_path.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError):
        rescue_damage.write_rescue_damage_csv(corrupt, str(out_path))
    assert out_path.read_bytes() == b"SENTINEL"


def test_writer_emits_exact_schema_and_row_order(tmp_path):
    summary, _, _ = _valid_summary()
    out_path = tmp_path / "rerank_rescue_damage.csv"
    rescue_damage.write_rescue_damage_csv(summary, str(out_path))
    written = pd.read_csv(out_path)
    assert list(written.columns) == rescue_damage.OUTPUT_COLUMNS
    rescue_damage.validate_row_order(written)
    assert len(written) == 21


# ─────────── physical parsing: lexemes, null-like text, blank @10 ────────────
# The frozen lexeme rule and column-aware NA policy, exercised against the
# §2 input contract.

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


@pytest.mark.parametrize("lexeme", ["0.00000000000000000001",
                                    "0.99999999999999999999", "0.5", "0.50",
                                    "1e0", "1E0", "+1", "-0", "01", "1.00",
                                    " 1", "1 ", "True", "false", "NaN", "null",
                                    "None", "NA", "<NA>", "2"])
def test_reject_unapproved_binary_lexeme_in_a_consumed_cell(tmp_path, lexeme):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, CONSUMED, lexeme)
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)


@pytest.mark.parametrize("lexeme", ["0", "1", "0.0", "1.0"])
def test_accept_every_approved_binary_lexeme(tmp_path, lexeme):
    """Legal twin: the same cell, spelled an approved way, still counts 21 rows."""
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, CONSUMED, lexeme)

    loaded, _ = rescue_damage.load_and_validate_inputs(dense_path, rerank_path)
    assert str(loaded[CONSUMED].dtype) == "Int64"
    cell = loaded.loc[loaded.setting == "pooled", CONSUMED].iloc[0]
    assert cell == int(float(lexeme)) and not isinstance(cell, float)


@pytest.mark.parametrize("lexeme", ["0.00000000000000000001", "0.5", "NaN"])
def test_main_refuses_an_unapproved_lexeme_without_touching_output(tmp_path, lexeme):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, CONSUMED, lexeme)

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        rescue_damage.main(dense_path, rerank_path, str(missing))
    assert not missing.exists()

    existing = tmp_path / "existing.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        rescue_damage.main(dense_path, rerank_path, str(existing))
    assert existing.read_bytes() == b"SENTINEL"


@pytest.mark.parametrize("lexeme", ["0.00000000000000000001", "0.5", "True"])
def test_non_consumed_pooled_at10_is_also_lexically_validated(tmp_path, lexeme):
    """Read-time validation covers every binary column, not only consumed ones."""
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, "any_evidence_recall@2", lexeme, setting="per_question")
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)


@pytest.mark.parametrize("literal", ["NaN", "nan", "NA", "null", "None", "<NA>"])
def test_populated_null_like_per_question_at10_refuses(tmp_path, literal):
    """§2 requires a physically blank per-question @10 cell; a literal null-like
    word is populated, and must not be misread as that blank."""
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, "full_evidence_recall@10", literal,
                    setting="per_question")
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)


def test_truly_blank_per_question_at10_is_the_legal_twin(tmp_path):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, "full_evidence_recall@10", "", setting="per_question")
    loaded, _ = rescue_damage.load_and_validate_inputs(dense_path, rerank_path)
    assert loaded.loc[loaded.setting == "per_question",
                      "full_evidence_recall@10"].isna().all()


@pytest.mark.parametrize("literal", ["NaN", "NA", "null", "None"])
def test_null_like_partial_at10_refuses(tmp_path, literal):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, "partial_evidence_recall@10", literal,
                    setting="per_question")
    with pytest.raises(ValueError, match="not a finite decimal"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)


_AT10_RECALL_COLUMNS = ["any_evidence_recall@10", "full_evidence_recall@10",
                        "partial_evidence_recall@10"]


@pytest.mark.parametrize("column", _AT10_RECALL_COLUMNS)
def test_per_question_at10_blank_is_legal_and_a_populated_token_refuses(
        tmp_path, column):
    """§2's blank requirement, paired per column: blank accepted, value refused.

    §2 does not merely tolerate a blank in this slot, it requires one, so the
    populated twin must refuse rather than be counted. The refusal now comes
    from the shared reader's placement invariant, which runs on the raw text of
    every input file before conversion — the same invariant the two general
    reporting tools enforce, so all three tools accept exactly one input
    language. Rescue's own `must be blank` check keeps its direct-frame coverage
    in `test_reject_populated_per_question_at10`, and is exercised below on the
    in-memory frame it defends.
    """
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, column, "", setting="per_question")
    loaded, _ = rescue_damage.load_and_validate_inputs(dense_path, rerank_path)
    assert loaded.loc[loaded.setting == "per_question", column].isna().all()

    populated = "1" if "partial" not in column else "0.5"
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, column, populated, setting="per_question")
    with pytest.raises(ValueError,
                       match="populated cell where the schema requires an empty one"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)

    # Defence in depth: rescue still refuses the same defect on a frame that
    # never passed through the shared reader.
    dense, _ = _bundle()
    mask = (dense.setting == "per_question") & (dense.example_id == "ex0000")
    dense.loc[mask, column] = 1 if "partial" not in column else 0.5
    with pytest.raises(ValueError, match="per_question.*must be blank"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


@pytest.mark.parametrize("target", ["dense", "rerank"])
@pytest.mark.parametrize("column,token", [
    ("any_evidence_recall@10", "1"),
    ("full_evidence_recall@10", "0.0"),
    ("partial_evidence_recall@10", "0.5"),
])
def test_main_refuses_a_populated_required_empty_cell_without_writing(
        tmp_path, target, column, token):
    """A K-policy violation in either input never reaches the output file."""
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path if target == "dense" else rerank_path,
                    column, token, setting="per_question")
    message = "populated cell where the schema requires an empty one"

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match=message):
        rescue_damage.main(dense_path, rerank_path, str(missing))
    assert not missing.exists()

    existing = tmp_path / "existing.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match=message):
        rescue_damage.main(dense_path, rerank_path, str(existing))
    assert existing.read_bytes() == b"SENTINEL"


@pytest.mark.parametrize("target", ["dense", "rerank"])
@pytest.mark.parametrize("column,token", [
    ("any_evidence_recall@10", "1"),
    ("full_evidence_recall@10", "0.0"),
    ("partial_evidence_recall@10", "0.5"),
])
def test_the_same_token_in_the_pooled_row_is_the_legal_twin(
        tmp_path, target, column, token):
    """Placement, not spelling: the identical token passes in the pooled row."""
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path if target == "dense" else rerank_path,
                    column, token, setting="pooled")
    out_path = tmp_path / "rerank_rescue_damage.csv"

    rescue_damage.main(dense_path, rerank_path, str(out_path))
    assert len(pd.read_csv(out_path)) == 21


@pytest.mark.parametrize("column", _AT10_RECALL_COLUMNS)
def test_pooled_at10_blank_refuses_at_read_time(tmp_path, column):
    """The same blank one setting over is a truncated file, not an omission."""
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, column, "", setting="pooled")
    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        rescue_damage.load_and_validate_inputs(dense_path, rerank_path)


# (column, lexeme, setting, expected message) — none of these cells is consumed
# by the rescue/damage counting, which reads only the seven valid binary
# `{criterion}@{k}` combinations.
_MALFORMED_UNCONSUMED = [
    ("partial_evidence_recall@5", "1.1", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@5", "-0.1", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@2", "1e9999", "per_question",
     r"outside the inclusive \[0, 1\] domain"),
    ("reciprocal_rank_at_10", "2", "pooled", r"outside the inclusive \[0, 1\] domain"),
    ("reciprocal_rank_at_50", "1.0000000000000001", "pooled",
     r"outside the inclusive \[0, 1\] domain"),
    ("reciprocal_rank_at_50", "-1e-400", "per_question",
     r"outside the inclusive \[0, 1\] domain"),
    ("partial_evidence_recall@5", "", "pooled", "empty cell where the schema permits none"),
    ("partial_evidence_recall@2", "", "per_question", "empty cell where the schema permits none"),
    ("reciprocal_rank_at_10", "", "pooled", "empty cell where the schema permits none"),
    ("reciprocal_rank_at_50", "", "per_question", "empty cell where the schema permits none"),
]


@pytest.mark.parametrize("column,lexeme,setting,message", _MALFORMED_UNCONSUMED)
def test_main_refuses_a_malformed_unconsumed_metric_without_writing(
        tmp_path, column, lexeme, setting, message):
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, column, lexeme, setting=setting)

    missing = tmp_path / "absent.csv"
    with pytest.raises(ValueError, match=message):
        rescue_damage.main(dense_path, rerank_path, str(missing))
    assert not missing.exists()

    existing = tmp_path / "existing.csv"
    existing.write_bytes(b"SENTINEL")
    with pytest.raises(ValueError, match=message):
        rescue_damage.main(dense_path, rerank_path, str(existing))
    assert existing.read_bytes() == b"SENTINEL"


@pytest.mark.parametrize("column,lexeme", [
    ("partial_evidence_recall@5", "1.0"),
    ("partial_evidence_recall@5", "0.0"),
    ("partial_evidence_recall@2", "0.999999999999999999999"),
    ("reciprocal_rank_at_10", "1"),
    ("reciprocal_rank_at_50", "1e-3"),
])
def test_main_accepts_an_in_domain_unconsumed_metric(tmp_path, column, lexeme):
    """Legal twins: the same unconsumed cells, spelled inside `[0,1]`."""
    dense, rerank = _bundle()
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    _corrupt_lexeme(dense_path, column, lexeme)
    out_path = tmp_path / "rerank_rescue_damage.csv"

    rescue_damage.main(dense_path, rerank_path, str(out_path))
    assert len(pd.read_csv(out_path)) == 21


@pytest.mark.parametrize("literal", ["None", "NA", "null", "NaN", "nan", "<NA>"])
def test_null_like_question_text_is_accepted_as_text(tmp_path, literal):
    """The same word that refuses in a metric cell is a legal question string."""
    dense, rerank = _bundle()
    for frame in (dense, rerank):
        frame.loc[frame.example_id == "ex0000", "question"] = literal
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)

    loaded, _ = rescue_damage.load_and_validate_inputs(dense_path, rerank_path)
    values = loaded.loc[loaded.example_id == "ex0000", "question"].tolist()
    assert values == [literal, literal]
    assert all(isinstance(value, str) for value in values)


def test_null_like_question_still_produces_the_21_row_summary(tmp_path):
    dense, rerank = _bundle()
    for frame in (dense, rerank):
        frame.loc[frame.example_id == "ex0000", "question"] = "NaN"
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    out_path = tmp_path / "rerank_rescue_damage.csv"

    rescue_damage.main(dense_path, rerank_path, str(out_path))
    assert len(pd.read_csv(out_path)) == 21


@pytest.mark.parametrize("value", [np.nan, None, pd.NA])
def test_missing_retrieved_titles_in_a_direct_frame_refuses(value):
    """Checked on the frame: serializing a missing cell to CSV would write a
    blank, which is the *legal* empty-list spelling, so the direct frame is
    where a genuinely missing title list has to be caught."""
    dense, _ = _bundle()
    dense["retrieved_titles"] = dense["retrieved_titles"].astype(object)
    dense.loc[dense.example_id == "ex0000", "retrieved_titles"] = value
    with pytest.raises(ValueError, match="retrieved_titles must be a string"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_string_retrieved_titles_in_a_direct_frame_is_the_legal_twin():
    dense, _ = _bundle()
    dense.loc[dense.example_id == "ex0000", "retrieved_titles"] = ""
    rescue_damage._validate_one_file(dense, "dense", "dense")


def test_empty_retrieved_titles_is_accepted_as_an_empty_list(tmp_path):
    dense, rerank = _bundle()
    dense.loc[dense.example_id == "ex0000", "retrieved_titles"] = ""
    dense_path, rerank_path = _write_bundle(tmp_path, dense, rerank)
    loaded, _ = rescue_damage.load_and_validate_inputs(dense_path, rerank_path)
    values = loaded.loc[loaded.example_id == "ex0000", "retrieved_titles"].tolist()
    assert values == ["", ""]


# ════════ rescue's own public direct-frame entry points share the gate ════════
# `build_paired_frame` and `oracle_check` are public functions that accept
# already-created result frames, so they apply the same shared typed metric
# contract rather than trusting a caller who never went through the reader. The
# rescue counting reads only the seven valid `{criterion}@{k}` combinations, so
# every cell mutated below is unconsumed by it.

_TYPED_PROBES = [
    # (label, column, setting, value, expected message)
    ("required-empty any@10 populated", "any_evidence_recall@10", "per_question",
     1, "populated cell where the schema requires an empty one"),
    ("required-empty partial@10 populated", "partial_evidence_recall@10",
     "per_question", 0.5, "populated cell where the schema requires an empty one"),
    ("required-populated pooled recall blank", "any_evidence_recall@10", "pooled",
     pd.NA, "non-0/1"),
    ("required-populated per-question recall blank", "any_evidence_recall@2",
     "per_question", pd.NA, "non-0/1"),
    ("required-populated partial blank", "partial_evidence_recall@5", "pooled",
     np.nan, "missing cell where the schema requires a populated value"),
    ("required-populated reciprocal rank blank", "reciprocal_rank_at_50",
     "per_question", np.nan,
     "missing cell where the schema requires a populated value"),
    ("float above one", "partial_evidence_recall@2", "pooled", 1.1,
     r"outside the inclusive \[0, 1\] domain"),
    ("float below zero", "reciprocal_rank_at_10", "pooled", -0.1,
     r"outside the inclusive \[0, 1\] domain"),
    ("float infinity", "reciprocal_rank_at_50", "pooled", float("inf"),
     r"outside the inclusive \[0, 1\] domain"),
    ("non-0/1 integer", "any_evidence_recall@2", "pooled", 2, "non-0/1"),
]


def _mutated_bundle(target, column, setting, value):
    dense, rerank = _bundle()
    frame = dense if target == "dense" else rerank
    frame.loc[frame["setting"] == setting, column] = value
    return dense, rerank


@pytest.mark.parametrize("target", ["dense", "rerank"])
@pytest.mark.parametrize("label,column,setting,value,message", _TYPED_PROBES)
def test_build_paired_frame_refuses_a_malformed_direct_frame(
        target, label, column, setting, value, message):
    dense, rerank = _mutated_bundle(target, column, setting, value)
    with pytest.raises(ValueError, match=message):
        rescue_damage.build_paired_frame(dense, rerank)


@pytest.mark.parametrize("target", ["dense", "rerank"])
@pytest.mark.parametrize("label,column,setting,value,message", _TYPED_PROBES)
def test_oracle_check_refuses_a_malformed_direct_frame(
        target, label, column, setting, value, message):
    summary, _, _ = _valid_summary()
    dense, rerank = _mutated_bundle(target, column, setting, value)
    with pytest.raises(ValueError, match=message):
        rescue_damage.oracle_check(summary, dense, rerank)


@pytest.mark.parametrize("target", ["dense", "rerank"])
@pytest.mark.parametrize("cast", ["boolean", "float64", "str", "object"])
def test_build_paired_frame_refuses_a_laundered_unconsumed_binary_column(
        target, cast):
    """`any_evidence_recall@2` is genuinely unconsumed here: VALID_COMBINATIONS
    reads the `any` criterion only at k=5, so nothing in the counting would ever
    notice this column had been cast away from a genuine integer."""
    dense, rerank = _bundle()
    frame = dense if target == "dense" else rerank
    column = "any_evidence_recall@2"
    assert not any(criterion == "any_evidence_recall" and k == 2
                   for criterion, _, k in rescue_damage.VALID_COMBINATIONS)
    frame[column] = (frame[column].astype(object) if cast == "object"
                     else frame[column].astype(cast))
    with pytest.raises(ValueError, match="non-0/1"):
        rescue_damage.build_paired_frame(dense, rerank)


def test_build_paired_frame_and_oracle_accept_the_legal_bundle():
    """Legal twin for every rejection above: the untouched formal-shaped bundle."""
    dense, rerank = _bundle()
    paired = rescue_damage.build_paired_frame(dense, rerank)
    assert len(paired) == len(dense)
    summary = rescue_damage.summarize_rescue_damage(paired)
    rescue_damage.oracle_check(summary, dense, rerank)


@pytest.mark.parametrize("column", _AT10_RECALL_COLUMNS)
def test_rescue_keeps_its_own_must_be_blank_message_for_the_at10_slots(column):
    """Defence in depth is retained, not replaced: rescue's §2 check still runs
    first and still names the K-policy violation in its own words."""
    dense, _ = _bundle()
    mask = (dense.setting == "per_question") & (dense.example_id == "ex0000")
    dense.loc[mask, column] = 1 if "partial" not in column else 0.5
    with pytest.raises(ValueError, match="per_question.*must be blank"):
        rescue_damage._validate_one_file(dense, "dense", "dense")


@pytest.mark.parametrize("label,column,setting,value,message", _TYPED_PROBES)
def test_validate_one_file_also_carries_the_shared_typed_contract(
        label, column, setting, value, message):
    """The other 19 slots and both value domains now refuse on a direct frame
    too, which rescue's own §2 check never covered.

    Where rescue's older, narrower check already owned the defect — a populated
    per-question `@10` cell — it still reports it in its own words, because the
    shared contract is appended after it rather than in front of it.
    """
    dense, _ = _bundle()
    dense.loc[dense["setting"] == setting, column] = value
    expected = ("per_question.*must be blank"
                if (column in _AT10_RECALL_COLUMNS and setting == "per_question"
                    and not pd.isna(value))
                else message)
    with pytest.raises(ValueError, match=expected):
        rescue_damage._validate_one_file(dense, "dense", "dense")


def test_the_real_formal_bundle_still_passes_rescue_direct_paths():
    """The guard must not change what the accepted formal bundle means."""
    dense, rerank = rescue_damage.load_and_validate_inputs(
        "results/dense_results.csv", "results/rerank_results.csv"
    )
    summary = rescue_damage.summarize_rescue_damage(
        rescue_damage.build_paired_frame(dense, rerank)
    )
    rescue_damage.validate_output_schema(summary)
    rescue_damage.oracle_check(summary, dense, rerank)
    assert len(summary) == 21
