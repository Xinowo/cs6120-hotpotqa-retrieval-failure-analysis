"""Regression tests for scripts/reporting/formal_result_inputs.py.

Covers the physical parsing contract shared by the three Week 3 reporting
tools at the level that decides acceptance: the *raw CSV lexeme*, before any
numeric conversion.

Four properties are asserted throughout.

1. Binary hit cells are validated as text against the owner-frozen lexeme set
   (Xin, 2026-07-27: exactly `0`, `1`, `0.0`, `1.0`, or an empty cell where the
   schema permits a blank). A float parser rounds `0.00000000000000000001` to 0
   and `0.99999999999999999999` to 1, so a conversion-first loader cannot see
   that those cells were malformed; every such spelling must therefore refuse
   on the text.
2. Float metric cells are validated against the schema's **semantic** `[0,1]`
   domain, on the exact written decimal, not merely against decimal finiteness.
   The same laundering hazard applies: `float("1.0000000000000001")` is exactly
   `1.0` and `float("-1e-400")` is `-0.0`, so both would pass a
   conversion-first range check. The converted float is re-checked as finite and
   in range as a defensive backstop.
3. Parsing is column- and row-aware. Textual columns are never NA-inferred, so
   the legitimate strings `None` / `NA` / `null` / `NaN` survive as themselves,
   while in a metric column only a physically empty cell is missing and those
   same populated words refuse.
4. Placement is a two-sided contract, not a nullability permission. Every one of
   the 22 `(metric column, setting)` slots is either required-empty or
   required-populated, and both halves are enforced on the raw text. The three
   `@10` recall columns of a `per_question` row are the required-empty slots —
   the schema does not compute those metrics, so a populated value there is an
   unauthorized extension of the frozen K policy and refuses even when it is an
   approved `0`/`1`/`0.0`/`1.0` lexeme or an in-range decimal. The other 19
   slots are required-populated, so a blank pooled recall cell, a blank
   per-question `@2`/`@5` cell, and a blank in either reciprocal-rank column all
   refuse as a truncated file. An empty `retrieved_titles` cell is text and stays
   legal.

5. There are two enforcement layers, and they are not interchangeable. The four
   properties above are decided on the raw CSV text, which exists only while a
   file is read. `validate_typed_metric_frame` is the second layer: it re-checks
   every invariant that survives parsing on an **already-created** DataFrame —
   all three per-question `@10` slots missing, all other 19 slots populated,
   every populated binary cell a genuine integer `0`/`1` (on the column's dtype
   as well as its values), every populated partial/reciprocal-rank cell numeric,
   finite, and inside `[0,1]` — and it does so with no normalization and no
   coercion. It deliberately claims nothing about spelling, because a parsed
   frame no longer distinguishes `0` from `0.00000000000000000001`; only the raw
   layer can, and only on a file.

Every rejection has a legal twin differing only in the targeted property — and
because placement is two-sided, the legal twin of a required-empty slot is the
blank, not a populated value.
"""

import csv
import re

import numpy as np
import pandas as pd
import pytest

from scripts.reporting import formal_result_inputs as fri
from src.results_schema import RESULT_COLUMNS

GOLD = "Gold A | Gold B"
RETRIEVED = "Gold A | Gold B | X"
CONSUMED = "full_evidence_recall@5"

# The shared schema's metric columns, written out independently of the module
# under test so the matrices below have their own oracle.
SCHEMA_BINARY_COLUMNS = [
    "any_evidence_recall@2", "any_evidence_recall@5", "any_evidence_recall@10",
    "full_evidence_recall@2", "full_evidence_recall@5", "full_evidence_recall@10",
]
SCHEMA_FLOAT_COLUMNS = [
    "partial_evidence_recall@2", "partial_evidence_recall@5",
    "partial_evidence_recall@10",
    "reciprocal_rank_at_10", "reciprocal_rank_at_50",
]
SCHEMA_METRIC_COLUMNS = SCHEMA_BINARY_COLUMNS + SCHEMA_FLOAT_COLUMNS
SETTINGS = ("pooled", "per_question")

# The complete (metric column, setting) matrix, partitioned into its two
# placement states. `REQUIRED_EMPTY_SLOTS` are the cells the schema declares
# uncomputed: they must be physically empty, so a populated value there is a
# violation rather than a legal alternative. Every other slot is the inverse —
# it must carry a value, so a blank there is a truncated file.
PLACEMENT_MATRIX = [(column, setting)
                    for column in SCHEMA_METRIC_COLUMNS for setting in SETTINGS]
REQUIRED_EMPTY_SLOTS = frozenset({
    ("any_evidence_recall@10", "per_question"),
    ("full_evidence_recall@10", "per_question"),
    ("partial_evidence_recall@10", "per_question"),
})
REQUIRED_POPULATED_SLOTS = [slot for slot in PLACEMENT_MATRIX
                            if slot not in REQUIRED_EMPTY_SLOTS]

# A populated legal twin for each metric family. Legal only in a
# required-populated slot: in the three required-empty slots the same tokens are
# exactly what must refuse.
LEGAL_TOKEN = {column: "1" for column in SCHEMA_BINARY_COLUMNS}
LEGAL_TOKEN.update({column: "0.5" for column in SCHEMA_FLOAT_COLUMNS})

# Every populated spelling that must refuse in a required-empty slot: all four
# owner-approved binary lexemes for the two binary `@10` columns, and
# representative in-range values (boundaries, interior, scientific notation) for
# the `[0,1]` partial column. Each is legal in its own family elsewhere, so the
# only thing being tested is placement.
APPROVED_BINARY_SPELLINGS = ["0", "1", "0.0", "1.0"]
IN_RANGE_PARTIAL_SPELLINGS = ["0", "1", "0.0", "1.0", "0.5", "0.25", "1e-3",
                              "0.999999999999999999999"]
REQUIRED_EMPTY_REJECTED_TOKENS = {
    "any_evidence_recall@10": APPROVED_BINARY_SPELLINGS,
    "full_evidence_recall@10": APPROVED_BINARY_SPELLINGS,
    "partial_evidence_recall@10": IN_RANGE_PARTIAL_SPELLINGS,
}

# Finite decimals whose exact value falls outside the schema's `[0,1]` domain.
# Well-formed numbers, every one of them: lexical finiteness is not the domain.
OUT_OF_DOMAIN_DECIMALS = [
    # negatives
    "-0.1", "-1", "-0.5", "-2", "-1.0",
    # greater than one
    "1.1", "2", "10", "1.5", "100.0",
    # boundary-adjacent, and laundered into range by float()
    "1.0000000000000001", "1.000000000000000000001", "-1e-400",
    # boundary-adjacent, out of range after conversion too
    "-0.000000000000000000001", "1.0000000000001",
    # overflow spellings
    "1e9999", "1E9999", "1e400", "-1e9999",
    # out-of-range scientific notation
    "1e1", "2e0", "-1e0",
]

# In-domain spellings that must keep working, including the approved in-range
# scientific notation. `-0.0` is exactly zero, so it is inside `[0,1]`.
IN_DOMAIN_DECIMALS = [
    "0", "1", "0.0", "1.0", "0.5", "0.25", "0.000001",
    "1e-3", "1E-3", "1e0", "0e0", "1.0e0", "1e-400",
    "0.999999999999999999999", "0.000000000000000000001", "-0.0",
]

# Spellings that a numeric parser would happily turn into 0 or 1, or that are
# otherwise outside the frozen lexeme set. None of them may be accepted.
UNAPPROVED_BINARY_LEXEMES = [
    # precision-adjacent fractions: a numeric cast rounds these to a clean 0/1
    "0.00000000000000000001", "0.99999999999999999999",
    "0.000000000000000000001", "0.999999999999999999999",
    # ordinary and near fractions
    "0.5", "0.50", "0.1", "0.9", "0.000001", "0.999999",
    # scientific notation
    "1e0", "1E0", "0e0", "1e-20", "1.0e0", "1e+0",
    # signs
    "+1", "+0", "-0", "-1", "+1.0", "-0.0",
    # padding zeros and alternative decimal spellings
    "01", "001", "1.00", "0.00", "00.0", "1.", "0.", ".0", ".1",
    # whitespace
    " 1", "1 ", " 1 ", "\t1", "1\t", "  ",
    # booleans and numeric strings that are not the frozen lexemes
    "True", "False", "true", "false", "TRUE", "yes", "Y", "2", "10",
    # null-like words in a metric column
    "NaN", "nan", "NA", "N/A", "null", "NULL", "None", "<NA>", "-",
]

# Null-like words that must survive untouched in a textual column.
NULL_LIKE_TEXT = ["None", "NA", "N/A", "null", "NULL", "NaN", "nan", "<NA>", "-"]


# ────────────────────────────── raw CSV fixtures ─────────────────────────────

def _tokens(method, setting, eid, question_type="bridge", **overrides):
    """One row as its exact physical lexemes, keyed by column."""
    row = {
        "method": method,
        "setting": setting,
        "example_id": eid,
        "question_type": question_type,
        "level": "hard",
        "question": f"Question {eid}?",
        "gold_titles": GOLD,
        "retrieved_titles": RETRIEVED,
    }
    for k in (2, 5, 10):
        row[f"any_evidence_recall@{k}"] = "1"
        row[f"full_evidence_recall@{k}"] = "1"
        row[f"partial_evidence_recall@{k}"] = "1.0"
    row["reciprocal_rank_at_10"] = "0.5"
    row["reciprocal_rank_at_50"] = "0.5"
    if setting == "per_question":
        # The schema leaves per-question @10 deliberately uncomputed.
        for metric in ("any_evidence_recall", "full_evidence_recall",
                       "partial_evidence_recall"):
            row[f"{metric}@10"] = ""
    row.update(overrides)
    return row


def _rows(method):
    return [
        _tokens(method, setting, eid, question_type=qtype)
        for setting in ("pooled", "per_question")
        for eid, qtype in (("ex0", "bridge"), ("ex1", "comparison"))
    ]


def _write(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=RESULT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return str(path)


def _write_text(path, text):
    """Write exact bytes: `Path.write_text` has no `newline` before Python 3.10."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return str(path)


def _file(tmp_path, method="dense", name=None, edit=None):
    """A structurally valid single-method file; `edit` mutates the raw rows."""
    rows = _rows(method)
    if edit is not None:
        edit(rows)
    return _write(tmp_path / (name or f"{method}_results.csv"), rows)


def _set(column, value, where=lambda row: True):
    def edit(rows):
        changed = 0
        for row in rows:
            if where(row):
                row[column] = value
                changed += 1
        assert changed, f"fixture edit matched no row for {column}"
    return edit


_POOLED = lambda row: row["setting"] == "pooled"
_PER_QUESTION = lambda row: row["setting"] == "per_question"


def _in(setting):
    """Row selector for one `setting`, for the matrices below."""
    return lambda row: row["setting"] == setting


# ───────────────────── the frozen lexeme set itself ──────────────────────────

def test_approved_binary_lexemes_are_the_owner_frozen_set():
    """The compatibility list is closed and enumerated, not a numeric range."""
    assert fri.APPROVED_BINARY_LEXEMES == ("0", "1", "0.0", "1.0")


def test_no_public_in_memory_binary_coercion_helper():
    """A helper that normalizes float columns would erase the provenance the
    contract refuses, so none may be exposed."""
    assert not hasattr(fri, "coerce_binary_metric_dtypes")


# ──────────── binary lexemes are validated before any conversion ────────────

@pytest.mark.parametrize("lexeme", UNAPPROVED_BINARY_LEXEMES)
def test_reject_unapproved_binary_lexeme(tmp_path, lexeme):
    path = _file(tmp_path, edit=_set(CONSUMED, lexeme, _POOLED))
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("lexeme", ["0", "1", "0.0", "1.0"])
def test_accept_approved_binary_lexeme(tmp_path, lexeme):
    """Legal twin: the same file, differing only in the binary spelling."""
    path = _file(tmp_path, edit=_set(CONSUMED, lexeme, _POOLED))
    df = fri.read_formal_result_csv(path)
    cells = df.loc[df.setting == "pooled", CONSUMED]
    assert str(cells.dtype) == "Int64"
    assert set(cells.tolist()) == {int(float(lexeme))}
    # The accepted float spellings still land as genuine integers, so the
    # consumed-cell predicate keeps seeing plain integers.
    assert all(fri.is_binary_cell(value) for value in cells.tolist())


@pytest.mark.parametrize("lexeme", ["0.00000000000000000001",
                                    "0.99999999999999999999"])
def test_precision_adjacent_fraction_is_not_rounded_into_legality(tmp_path, lexeme):
    """The two fractions closest to a legal value, with the hazard they exploit.

    A conversion-first loader reads these through pandas' nullable-integer
    cast, which rounds them to a clean 0/1 and destroys the evidence that the
    cell was ever fractional. Validating the lexeme is what makes them visible.
    """
    path = _file(tmp_path, edit=_set(CONSUMED, lexeme, _POOLED))

    laundered = pd.read_csv(path, dtype={CONSUMED: "Int64"})
    assert set(laundered.loc[laundered.setting == "pooled", CONSUMED]) <= {0, 1}

    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("column", fri.BINARY_METRIC_COLUMNS)
def test_every_binary_column_is_lexically_validated(tmp_path, column):
    """Validation covers all binary columns at read time, not only consumed ones."""
    path = _file(tmp_path, edit=_set(column, "0.5", _POOLED))
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        fri.read_formal_result_csv(path)


def test_blank_binary_cell_stays_missing_and_is_never_read_as_zero(tmp_path):
    """In the one binary slot the schema leaves uncomputed, a blank is missing."""
    path = _file(tmp_path, edit=_set("any_evidence_recall@10", "", _PER_QUESTION))
    df = fri.read_formal_result_csv(path)
    cells = df.loc[df.setting == "per_question", "any_evidence_recall@10"]
    assert str(cells.dtype) == "Int64"
    assert cells.isna().all()


def test_blank_consumed_cell_refuses_at_read_time(tmp_path):
    """Blanking a consumed pooled cell is refused before a frame even exists."""
    path = _file(tmp_path, edit=_set(CONSUMED, "", _POOLED))
    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        fri.read_formal_result_csv(path)


def test_permitted_blank_still_refuses_when_it_is_consumed(tmp_path):
    """The legal per-question `@10` blank is legal to *read*, never to *consume*.

    This is the pairing the rescue contract relies on: the cell may be blank in
    the file, but any tool that selects it as its binary criterion must refuse
    rather than read the blank as a miss.
    """
    path = _file(tmp_path, edit=_set("full_evidence_recall@10", "", _PER_QUESTION))
    df = fri.read_formal_result_csv(path)
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_consumed_binary(
            df, "full_evidence_recall@10", "per_question", path
        )


def test_populated_consumed_cell_is_the_legal_twin(tmp_path):
    path = _file(tmp_path, edit=_set(CONSUMED, "0", _POOLED))
    df = fri.read_formal_result_csv(path)
    fri.validate_consumed_binary(df, CONSUMED, "pooled", path)


@pytest.mark.parametrize("dtype", ["float", "bool", "str"])
def test_direct_frame_binary_dtype_still_refuses(tmp_path, dtype):
    """A frame built in memory cannot dodge the physical type contract now that
    no public normalization helper exists."""
    df = fri.read_formal_result_csv(_file(tmp_path))
    df[CONSUMED] = df[CONSUMED].astype(dtype)
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_consumed_binary(df, CONSUMED, "pooled", "direct")


def test_direct_integer_frame_is_the_legal_twin(tmp_path):
    df = fri.read_formal_result_csv(_file(tmp_path))
    fri.validate_consumed_binary(df, CONSUMED, "pooled", "direct")


# ────────────── column-aware NA policy — text side is preserved ─────────────

@pytest.mark.parametrize("column", ["question", "gold_titles", "example_id",
                                    "retrieved_titles"])
@pytest.mark.parametrize("literal", NULL_LIKE_TEXT)
def test_null_like_text_survives_as_a_string(tmp_path, column, literal):
    """`None`/`NA`/`null`/`NaN` are legal strings, not missing values."""
    path = _file(tmp_path, edit=_set(column, literal))
    df = fri.read_formal_result_csv(path)
    values = df[column].tolist()
    assert all(isinstance(value, str) for value in values), values
    assert set(values) == {literal}


@pytest.mark.parametrize("literal", NULL_LIKE_TEXT)
def test_quoted_null_like_text_survives_identically(tmp_path, literal):
    """The quoted and unquoted spellings must parse to the same string."""
    unquoted = _file(tmp_path, name="unquoted.csv", edit=_set("question", literal))
    raw = open(unquoted, encoding="utf-8").read()
    quoted = _write_text(tmp_path / "quoted.csv",
                         raw.replace(f",{literal},", f',"{literal}",'))

    assert fri.read_formal_result_csv(quoted).question.tolist() == \
        fri.read_formal_result_csv(unquoted).question.tolist() == [literal] * 4


def test_null_like_question_passes_the_metadata_domain(tmp_path):
    """Legal twin at the validation layer, not only at the parse layer."""
    path = _file(tmp_path, edit=_set("question", "NaN"))
    df = fri.read_formal_result_csv(path)
    fri.validate_structure(df, path, "dense")


@pytest.mark.parametrize("column", ["example_id", "question", "gold_titles"])
def test_reject_empty_required_text_cell(tmp_path, column):
    path = _file(tmp_path, edit=_set(column, "", _POOLED))
    df = fri.read_formal_result_csv(path)
    with pytest.raises(ValueError, match=f"{column} must be a non-null string"):
        fri.validate_metadata_domains(df, path)


@pytest.mark.parametrize("column", ["example_id", "question", "gold_titles"])
def test_accept_populated_required_text_cell(tmp_path, column):
    path = _file(tmp_path, edit=_set(column, "populated"))
    df = fri.read_formal_result_csv(path)
    fri.validate_metadata_domains(df, path)


# ───────── column-aware NA policy — metric side refuses null-like words ──────

@pytest.mark.parametrize("literal", ["NaN", "nan", "NA", "null", "None", "<NA>"])
def test_reject_populated_null_like_binary_metric_cell(tmp_path, literal):
    """A populated null-like token must not be misread as a legal blank."""
    path = _file(tmp_path, edit=_set("full_evidence_recall@10", literal, _PER_QUESTION))
    with pytest.raises(ValueError, match="not an approved binary lexeme"):
        fri.read_formal_result_csv(path)


def test_truly_blank_metric_cell_is_the_legal_twin(tmp_path):
    path = _file(tmp_path, edit=_set("full_evidence_recall@10", "", _PER_QUESTION))
    df = fri.read_formal_result_csv(path)
    assert df.loc[df.setting == "per_question", "full_evidence_recall@10"].isna().all()


@pytest.mark.parametrize("literal", ["NaN", "nan", "inf", "-inf", "Infinity",
                                     "null", "None", "NA", " 0.5", "0.5 ", "0_5"])
def test_reject_non_finite_float_metric_cell(tmp_path, literal):
    path = _file(tmp_path, edit=_set("partial_evidence_recall@5", literal, _POOLED))
    with pytest.raises(ValueError, match="not a finite decimal"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("literal", ["0", "1", "0.5", "0.0", "1.0", "1e-3", "0.25"])
def test_accept_finite_float_metric_cell(tmp_path, literal):
    path = _file(tmp_path, edit=_set("partial_evidence_recall@5", literal, _POOLED))
    df = fri.read_formal_result_csv(path)
    cells = df.loc[df.setting == "pooled", "partial_evidence_recall@5"]
    assert str(cells.dtype) == "float64"
    assert set(cells.tolist()) == {float(literal)}


# ───────── float metrics: the semantic [0,1] domain, not just finiteness ──────
# The shared schema types partial recall and reciprocal rank as `[0,1]`. Every
# lexeme below is a well-formed finite decimal, so only a *domain* check refuses
# it — and the check has to run on the exact written decimal, because `float()`
# rounds two of these into the legal range.

def test_float_metric_columns_are_the_schema_float_families():
    """Independent oracle for the families the domain rule must cover."""
    assert list(fri.FLOAT_METRIC_COLUMNS) == SCHEMA_FLOAT_COLUMNS
    assert list(fri.BINARY_METRIC_COLUMNS) == SCHEMA_BINARY_COLUMNS
    assert list(fri.METRIC_COLUMNS) == SCHEMA_METRIC_COLUMNS


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
@pytest.mark.parametrize("lexeme", OUT_OF_DOMAIN_DECIMALS)
def test_reject_out_of_domain_float_metric_per_family(tmp_path, column, lexeme):
    """Every float metric family refuses every out-of-domain decimal."""
    path = _file(tmp_path, edit=_set(column, lexeme, _POOLED))
    with pytest.raises(ValueError, match=r"outside the inclusive \[0, 1\] domain"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
@pytest.mark.parametrize("setting", SETTINGS)
def test_reject_out_of_domain_float_metric_in_either_setting(tmp_path, column, setting):
    path = _file(tmp_path, edit=_set(column, "1.1", _in(setting)))
    with pytest.raises(ValueError, match=r"outside the inclusive \[0, 1\] domain"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
@pytest.mark.parametrize("lexeme", IN_DOMAIN_DECIMALS)
def test_accept_in_domain_float_metric_per_family(tmp_path, column, lexeme):
    """Legal twins: the same cell, spelled with an in-domain decimal."""
    path = _file(tmp_path, edit=_set(column, lexeme, _POOLED))
    df = fri.read_formal_result_csv(path)
    cells = df.loc[df.setting == "pooled", column]
    assert str(cells.dtype) == "float64"
    assert set(cells.tolist()) == {float(lexeme)}


@pytest.mark.parametrize("lexeme", ["1.0000000000000001",
                                    "1.000000000000000000001", "-1e-400"])
def test_boundary_adjacent_decimal_is_not_rounded_into_the_domain(tmp_path, lexeme):
    """The out-of-domain spellings closest to a legal value, with their hazard.

    `float()` maps each of these *into* `[0,1]` — `1.0000000000000001` becomes
    exactly `1.0`, `-1e-400` underflows to `-0.0` — so a conversion-first range
    check would accept them and lose the evidence that the cell was impossible.
    Comparing the exact decimal is what keeps them visible.
    """
    assert 0.0 <= float(lexeme) <= 1.0  # the hazard itself

    path = _file(tmp_path, edit=_set("partial_evidence_recall@5", lexeme, _POOLED))
    laundered = pd.read_csv(path)["partial_evidence_recall@5"].dropna()
    assert laundered.between(0.0, 1.0).all()

    with pytest.raises(ValueError, match=r"outside the inclusive \[0, 1\] domain"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("lexeme", ["1e9999", "-1e9999", "1e400"])
def test_overflow_spelling_never_becomes_an_infinity(tmp_path, lexeme):
    """An exponent that would overflow the float type refuses before conversion."""
    path = _file(tmp_path, edit=_set("reciprocal_rank_at_10", lexeme, _POOLED))
    with pytest.raises(ValueError, match=r"outside the inclusive \[0, 1\] domain"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("token", ["1e9999", "-1e9999", "1.1", "-0.1", "2"])
def test_conversion_backstop_refuses_an_out_of_range_converted_float(token):
    """Defence in depth: the converted float is re-checked, not trusted.

    The lexical domain check already refuses each of these, so this exercises the
    backstop directly — the guarantee that no conversion artifact (an infinity, a
    value that crossed the boundary) can enter the frame the tools consume.
    """
    with pytest.raises(ValueError, match="not a finite value inside the inclusive"):
        fri._float_metric_value(token, "partial_evidence_recall@5", 0, "direct")


@pytest.mark.parametrize("token", ["0", "1", "0.5", "1e-3", "-0.0", "1e-400"])
def test_conversion_backstop_passes_an_in_range_converted_float(token):
    value = fri._float_metric_value(token, "partial_evidence_recall@5", 0, "direct")
    assert np.isfinite(value) and 0.0 <= value <= 1.0


def test_conversion_backstop_maps_a_permitted_blank_to_missing():
    value = fri._float_metric_value(
        "", "partial_evidence_recall@10", 0, "direct"
    )
    assert np.isnan(value)


def test_every_accepted_float_metric_is_finite_and_in_range(tmp_path):
    df = fri.read_formal_result_csv(_file(tmp_path))
    for column in fri.FLOAT_METRIC_COLUMNS:
        values = df[column].dropna()
        assert np.isfinite(values).all(), column
        assert values.between(0.0, 1.0).all(), column


# ────── metric placement: three required-empty slots, 19 required-populated ───
# The schema's storage/metric policy leaves only the per-question `@10` recall
# uncomputed, and "uncomputed" is two-sided: those three cells must be empty,
# and every other metric cell of a compliant artifact must carry a value. A
# blank in the second group marks a truncated or partially generated file; a
# value in the first group marks an unauthorized metric extension.

def test_placement_matrix_is_exhaustive_and_two_sided():
    """Independent oracle for both halves of the placement contract."""
    assert set(fri.REQUIRED_EMPTY_METRIC_COLUMNS) == {
        "any_evidence_recall@10", "full_evidence_recall@10",
        "partial_evidence_recall@10",
    }
    assert fri.REQUIRED_EMPTY_SETTING == "per_question"
    assert len(PLACEMENT_MATRIX) == 22
    assert len(REQUIRED_EMPTY_SLOTS) == 3
    assert len(REQUIRED_POPULATED_SLOTS) == 19
    # Every slot has exactly one of the two states; there is no "either" state.
    for column, setting in PLACEMENT_MATRIX:
        expected = (fri.REQUIRED_EMPTY if (column, setting) in REQUIRED_EMPTY_SLOTS
                    else fri.REQUIRED_POPULATED)
        assert fri.metric_cell_placement(column, setting) == expected
    assert fri.REQUIRED_EMPTY != fri.REQUIRED_POPULATED


@pytest.mark.parametrize("column,setting", REQUIRED_POPULATED_SLOTS)
def test_reject_empty_metric_cell_in_a_required_populated_slot(
        tmp_path, column, setting):
    """The full forbidden-blank half of the (metric column x setting) matrix."""
    path = _file(tmp_path, edit=_set(column, "", _in(setting)))
    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        fri.read_formal_result_csv(path)


@pytest.mark.parametrize("column,setting", REQUIRED_POPULATED_SLOTS)
def test_populated_metric_cell_is_the_legal_twin_of_a_required_populated_slot(
        tmp_path, column, setting):
    """Each forbidden blank paired with the same cell, legally populated.

    This control belongs to the 19 required-populated slots *only*. Applying it
    to the three required-empty slots would assert the opposite of the schema:
    there, the populated value is the violation and the blank is the twin.
    """
    path = _file(tmp_path, edit=_set(column, LEGAL_TOKEN[column], _in(setting)))
    df = fri.read_formal_result_csv(path)
    cells = df.loc[df.setting == setting, column]
    assert cells.notna().all()
    assert set(cells.tolist()) == {
        1 if column in SCHEMA_BINARY_COLUMNS else 0.5
    }


@pytest.mark.parametrize("column,setting", sorted(REQUIRED_EMPTY_SLOTS))
def test_accept_empty_metric_cell_in_a_required_empty_slot(tmp_path, column, setting):
    """The legal twin of the required-empty half is the physically blank cell."""
    path = _file(tmp_path, edit=_set(column, "", _in(setting)))
    df = fri.read_formal_result_csv(path)
    assert df.loc[df.setting == setting, column].isna().all()


@pytest.mark.parametrize(
    "column,setting,token",
    [(column, setting, token)
     for column, setting in sorted(REQUIRED_EMPTY_SLOTS)
     for token in REQUIRED_EMPTY_REJECTED_TOKENS[column]],
)
def test_reject_populated_metric_cell_in_a_required_empty_slot(
        tmp_path, column, setting, token):
    """The inverse half: a value the schema declares absent must refuse.

    Every token here is a spelling the same column accepts in a *pooled* row —
    all four owner-approved binary lexemes, or an in-range `[0,1]` decimal — so
    nothing about the lexeme rule or the float domain is being restated. What
    refuses is the placement: the frozen K policy does not compute per-question
    `@10`, so publishing a value there would present an unauthorized metric
    extension as a valid formal bundle.
    """
    path = _file(tmp_path, edit=_set(column, token, _in(setting)))
    with pytest.raises(ValueError,
                       match="populated cell where the schema requires an empty one"):
        fri.read_formal_result_csv(path)
    with pytest.raises(ValueError,
                       match="populated cell where the schema requires an empty one"):
        fri.load_result_csv(path, "dense")


@pytest.mark.parametrize("column,setting", sorted(REQUIRED_EMPTY_SLOTS))
def test_the_same_token_is_legal_in_the_pooled_row_of_a_required_empty_column(
        tmp_path, column, setting):
    """Placement, not spelling: the identical token passes in the pooled row.

    Pairs directly with the rejection above and isolates the variable — the same
    column, the same lexeme, only the row's `setting` differs.
    """
    token = LEGAL_TOKEN[column]
    df = fri.read_formal_result_csv(
        _file(tmp_path, edit=_set(column, token, _POOLED))
    )
    assert df.loc[df.setting == "pooled", column].notna().all()
    assert df.loc[df.setting == setting, column].isna().all()


@pytest.mark.parametrize("column", ["any_evidence_recall@10",
                                    "full_evidence_recall@10",
                                    "partial_evidence_recall@10"])
def test_at10_placement_inverts_between_the_two_settings(tmp_path, column):
    """The same column, both mutations: the row's `setting` inverts the rule.

    Pooled requires a value and refuses the blank; per-question requires the
    blank and refuses the value.
    """
    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        fri.read_formal_result_csv(_file(tmp_path, name="pooled_blank.csv",
                                         edit=_set(column, "", _POOLED)))

    with pytest.raises(ValueError,
                       match="populated cell where the schema requires an empty one"):
        fri.read_formal_result_csv(
            _file(tmp_path, name="per_question_populated.csv",
                  edit=_set(column, LEGAL_TOKEN[column], _PER_QUESTION))
        )

    legal = _file(tmp_path, name="per_question.csv",
                  edit=_set(column, "", _PER_QUESTION))
    df = fri.read_formal_result_csv(legal)
    assert df.loc[df.setting == "per_question", column].isna().all()
    assert df.loc[df.setting == "pooled", column].notna().all()


def test_a_wholly_blank_metric_column_refuses(tmp_path):
    """A truncated generation that leaves an entire column empty is refused."""
    path = _file(tmp_path, edit=_set("reciprocal_rank_at_50", ""))
    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        fri.read_formal_result_csv(path)


def test_empty_retrieved_titles_is_not_governed_by_the_blank_rule(tmp_path):
    """The blank-placement rule is about metrics; `retrieved_titles` is text."""
    path = _file(tmp_path, edit=_set("retrieved_titles", ""))
    df = fri.read_formal_result_csv(path)
    assert df.retrieved_titles.tolist() == [""] * 4
    fri.validate_metadata_domains(df, path)


def test_blank_float_metric_cell_is_missing(tmp_path):
    """In the one float slot the schema leaves uncomputed, a blank is missing."""
    path = _file(tmp_path, edit=_set("partial_evidence_recall@10", "", _PER_QUESTION))
    df = fri.read_formal_result_csv(path)
    cells = df.loc[df.setting == "per_question", "partial_evidence_recall@10"]
    assert str(cells.dtype) == "float64"
    assert cells.isna().all()


# ─────────────────────── retrieved_titles string domain ──────────────────────

def test_empty_retrieved_titles_is_preserved_as_empty(tmp_path):
    """An empty retrieved list stays an empty string, never NaN."""
    path = _file(tmp_path, edit=_set("retrieved_titles", "", _POOLED))
    df = fri.read_formal_result_csv(path)
    values = df.loc[df.setting == "pooled", "retrieved_titles"].tolist()
    assert values == ["", ""]
    fri.validate_metadata_domains(df, path)


def test_normal_retrieved_titles_is_the_legal_twin(tmp_path):
    df = fri.read_formal_result_csv(_file(tmp_path))
    assert set(df.retrieved_titles.tolist()) == {RETRIEVED}
    fri.validate_metadata_domains(df, "dense")


@pytest.mark.parametrize("value", [np.nan, None, pd.NA, 3, 4.5])
def test_reject_non_string_retrieved_titles_in_a_direct_frame(tmp_path, value):
    df = fri.read_formal_result_csv(_file(tmp_path))
    df["retrieved_titles"] = df["retrieved_titles"].astype(object)
    df.loc[df.index[0], "retrieved_titles"] = value
    with pytest.raises(ValueError, match="retrieved_titles must be a string"):
        fri.validate_metadata_domains(df, "direct")


def test_accept_string_retrieved_titles_in_a_direct_frame(tmp_path):
    df = fri.read_formal_result_csv(_file(tmp_path))
    df.loc[df.index[0], "retrieved_titles"] = ""
    fri.validate_metadata_domains(df, "direct")


# ───────────────────────── malformed physical files ──────────────────────────

def test_ragged_row_blanks_its_tail_and_is_then_refused(tmp_path):
    """A truncated row must never smuggle a non-string cell into the frame.

    pandas pads a short row with empty fields rather than with NaN, so no
    consumer can stringify a missing scalar into content — the raw lexemes stay
    strings. The padding also blanks the row's metric tail, which is precisely
    the truncated-file case the blank-placement rule exists to catch, so the
    file is now refused at read time rather than later, at the empty
    required-text cell. (That text refusal keeps its own coverage in
    `test_reject_empty_required_text_cell`.)
    """
    raw = open(_file(tmp_path), encoding="utf-8").read().splitlines()
    raw[1] = ",".join(raw[1].split(",")[:5])  # truncate before `question`
    path = _write_text(tmp_path / "ragged.csv", "\n".join(raw) + "\n")

    lexemes = fri._read_raw_lexemes(path)
    for column in RESULT_COLUMNS:
        assert all(isinstance(value, str) for value in lexemes[column].tolist())
    assert lexemes.loc[0, "question"] == ""

    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        fri.read_formal_result_csv(path)
    with pytest.raises(ValueError, match="empty cell where the schema permits none"):
        fri.load_result_csv(path, "dense")


def test_wrong_columns_are_still_reported_by_validate_structure(tmp_path):
    """Lexical validation must not mask the structural column error."""
    raw = open(_file(tmp_path), encoding="utf-8").read().splitlines()
    keep = len(RESULT_COLUMNS) - 2
    path = _write_text(
        tmp_path / "short.csv",
        "\n".join(",".join(line.split(",")[:keep]) for line in raw) + "\n",
    )
    with pytest.raises(ValueError, match="columns do not match RESULT_COLUMNS"):
        fri.load_result_csv(path, "dense")


def test_missing_file_refuses(tmp_path):
    with pytest.raises((ValueError, OSError)):
        fri.read_formal_result_csv(str(tmp_path / "absent.csv"))


# ───────────── end-to-end: the accepted file keeps its exact values ──────────

def test_accepted_file_round_trips_every_physical_value(tmp_path):
    """Nothing in the accepted path rewrites a value the file actually holds."""
    path = _file(tmp_path, edit=_set("full_evidence_recall@10", "0.0", _POOLED))
    df = fri.read_formal_result_csv(path)

    raw = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)
    for column in fri.BINARY_METRIC_COLUMNS:
        for token, value in zip(raw[column], df[column]):
            if token == "":
                assert pd.isna(value)
            else:
                assert value == int(float(token)) and isinstance(value, (int, np.integer))
    for column in ("question", "gold_titles", "retrieved_titles", "example_id"):
        assert raw[column].tolist() == df[column].tolist()


# ═════════════════ the typed-frame layer (validate_typed_metric_frame) ════════
# Everything above enters through a file, so every matrix above is decided on a
# raw lexeme. A caller may instead hand a tool an already-created DataFrame, and
# for that frame the lexemes no longer exist. The section below is the second
# layer: every invariant that *survives* parsing, asserted on frames that never
# touched a file, with no coercion anywhere.
#
# The two layers are deliberately not interchangeable. This one claims nothing
# about spelling — after parsing there is no way to tell `0` from
# `0.00000000000000000001` — and the raw layer keeps its exclusive authority
# over that. What this layer must close is the complete 22-slot placement
# matrix, the genuine-integer binary domain, and the finite `[0,1]` float domain
# on cells the caller never consumes.

# The three families of missing marker a typed frame can actually carry.
MISSING_MARKERS = [pd.NA, np.nan, None]

# Populated values that must refuse in a required-empty slot. Every one of them
# is legal in the same column's pooled row, so only placement is under test.
REQUIRED_EMPTY_REJECTED_TYPED = {
    "any_evidence_recall@10": [0, 1, np.int64(0), np.int64(1)],
    "full_evidence_recall@10": [0, 1, np.int64(0), np.int64(1)],
    "partial_evidence_recall@10": [0.0, 1.0, 0.5, 1e-9, np.float64(0.25)],
}

# Float values outside the schema's inclusive [0,1] domain, as parsed scalars.
# `NaN` is deliberately absent: on a typed frame a NaN *is* the missing marker,
# so it is judged by placement, not by the domain (see the dedicated test).
OUT_OF_DOMAIN_TYPED = [
    -0.1, -1.0, -1e-9, -0.0000001, 1.1, 2.0, 10.0, 1.0000000001,
    float("inf"), float("-inf"), np.float64(1.5), np.float64(-0.5),
]

# Legal boundary and interior values, so the domain is inclusive, not exclusive.
IN_DOMAIN_TYPED = [0.0, 1.0, 0.5, 1e-9, 0.9999999999, -0.0, np.float64(0.25)]

# Populated binary cells that are genuine integers but not 0 or 1.
NON_BINARY_INTEGERS = [2, -1, 10, np.int64(2), np.int64(-1)]

# The two binary columns whose per-question cells are legitimately missing, so a
# plain (non-nullable) numpy cast cannot be applied to them at all.
_BINARY_COLUMNS_WITH_A_MISSING_SLOT = ("any_evidence_recall@10",
                                       "full_evidence_recall@10")


def _typed_row(method, setting, eid, qtype):
    """One already-parsed row: scalars, never lexemes."""
    row = {
        "method": method,
        "setting": setting,
        "example_id": eid,
        "question_type": qtype,
        "level": "hard",
        "question": f"Question {eid}?",
        "gold_titles": GOLD,
        "retrieved_titles": RETRIEVED,
    }
    for k in (2, 5, 10):
        row[f"any_evidence_recall@{k}"] = 1
        row[f"full_evidence_recall@{k}"] = 0
        row[f"partial_evidence_recall@{k}"] = 0.5
    row["reciprocal_rank_at_10"] = 0.5
    row["reciprocal_rank_at_50"] = 0.25
    if setting == "per_question":
        for column in ("any_evidence_recall@10", "full_evidence_recall@10",
                       "partial_evidence_recall@10"):
            row[column] = None
    return row


def _typed_frame(method="dense"):
    """A compliant typed frame built directly, with no file and no reader.

    The physical shape is written out here rather than obtained from
    `read_formal_result_csv`, so these probes have their own oracle and cannot
    inherit a defect from the layer they are meant to be independent of.
    """
    rows = [
        _typed_row(method, setting, eid, qtype)
        for setting in SETTINGS
        for eid, qtype in (("ex0", "bridge"), ("ex1", "comparison"))
    ]
    df = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    for column in SCHEMA_BINARY_COLUMNS:
        df[column] = pd.array(
            [pd.NA if row[column] is None else int(row[column]) for row in rows],
            dtype="Int64",
        )
    for column in SCHEMA_FLOAT_COLUMNS:
        df[column] = pd.Series(
            [np.nan if row[column] is None else float(row[column]) for row in rows],
            dtype="float64",
        )
    return df


def _put(column, setting, value, method="dense"):
    """The canonical typed frame with one `(column, setting)` slot overwritten."""
    df = _typed_frame(method)
    df.loc[df["setting"] == setting, column] = value
    return df


def _retype(column, transform, method="dense"):
    """The canonical typed frame with one whole metric column re-typed."""
    df = _typed_frame(method)
    df[column] = transform(df[column])
    return df


def _missing_message(column):
    """The refusal a required-populated slot must produce, per metric family."""
    if column in SCHEMA_BINARY_COLUMNS:
        return "empty or non-0/1 values"
    return "missing cell where the schema requires a populated value"


_POPULATED_IN_REQUIRED_EMPTY = "populated cell where the schema requires an empty one"


# ───────────── the canonical typed frame is the legal control ────────────────

@pytest.mark.parametrize("method", ["bm25", "dense", "rerank"])
def test_untouched_typed_frame_is_accepted(method):
    """The legal twin of every mutation below, for all three retrievers."""
    df = _typed_frame(method)
    fri.validate_typed_metric_frame(df, "direct")
    fri.validate_structure(df, "direct", method)


def test_typed_frame_fixture_has_the_physical_shape_the_reader_produces():
    """The hand-built frame must match the reader's, or it proves nothing."""
    direct = _typed_frame()
    for column in SCHEMA_BINARY_COLUMNS:
        assert str(direct[column].dtype) == "Int64", column
    for column in SCHEMA_FLOAT_COLUMNS:
        assert str(direct[column].dtype) == "float64", column
    for column, setting in REQUIRED_EMPTY_SLOTS:
        assert direct.loc[direct.setting == setting, column].isna().all()
    for column, setting in REQUIRED_POPULATED_SLOTS:
        assert direct.loc[direct.setting == setting, column].notna().all()


def test_typed_layer_covers_every_metric_column_of_the_schema():
    """Independent oracle: no metric column may be outside the typed contract."""
    assert sorted(fri.METRIC_COLUMNS) == sorted(SCHEMA_METRIC_COLUMNS)
    assert len(SCHEMA_METRIC_COLUMNS) * len(SETTINGS) == 22


@pytest.mark.parametrize("column", SCHEMA_METRIC_COLUMNS)
def test_typed_layer_refuses_a_frame_missing_a_metric_column(column):
    """A subset of the metric columns cannot satisfy the whole contract."""
    df = _typed_frame().drop(columns=[column])
    with pytest.raises(ValueError, match=f"metric column {re.escape(column)} is absent"):
        fri.validate_typed_metric_frame(df, "direct")


def test_typed_layer_refuses_a_frame_without_a_setting_column():
    """Placement is not decidable without the row's setting, so nothing is
    assumed about it."""
    df = _typed_frame().drop(columns=["setting"])
    with pytest.raises(ValueError, match="must carry a 'setting' column"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("value", ["Pooled", "bogus", "", None, 0])
def test_typed_layer_refuses_an_unknown_setting_value(value):
    df = _typed_frame()
    df.loc[df.index[0], "setting"] = value
    with pytest.raises(ValueError, match="cannot decide metric placement"):
        fri.validate_typed_metric_frame(df, "direct")


# ──────── placement: 19 required-populated slots reject a missing cell ────────

@pytest.mark.parametrize("column,setting", REQUIRED_POPULATED_SLOTS)
@pytest.mark.parametrize("marker", MISSING_MARKERS)
def test_typed_frame_rejects_a_missing_cell_in_a_required_populated_slot(
        column, setting, marker):
    """The complete required-populated half, for every missing marker.

    This is the direct-frame counterpart of the raw forbidden-blank matrix, and
    it is the half that the demonstrated blanked reciprocal-rank bypass defeated:
    the tool never reads `reciprocal_rank_at_50`, so only a whole-frame check
    can see it.
    """
    df = _put(column, setting, marker)
    with pytest.raises(ValueError, match=_missing_message(column)):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column,setting", REQUIRED_POPULATED_SLOTS)
def test_typed_frame_accepts_the_populated_twin_of_that_slot(column, setting):
    """Each rejection above paired with the same slot, legally populated."""
    value = 1 if column in SCHEMA_BINARY_COLUMNS else 0.75
    fri.validate_typed_metric_frame(_put(column, setting, value), "direct")


@pytest.mark.parametrize("column,setting", REQUIRED_POPULATED_SLOTS)
def test_a_missing_required_populated_slot_also_refuses_through_validate_structure(
        column, setting):
    """The public structural gate carries the typed contract, not just the
    standalone validator."""
    df = _put(column, setting, pd.NA if column in SCHEMA_BINARY_COLUMNS else np.nan)
    with pytest.raises(ValueError, match=_missing_message(column)):
        fri.validate_structure(df, "direct", "dense")


# ───────── placement: the 3 required-empty slots reject any value ─────────────

@pytest.mark.parametrize(
    "column,setting,value",
    [(column, setting, value)
     for column, setting in sorted(REQUIRED_EMPTY_SLOTS)
     for value in REQUIRED_EMPTY_REJECTED_TYPED[column]],
)
def test_typed_frame_rejects_a_populated_required_empty_slot(column, setting, value):
    """the first demonstrated bypass, generalized over all three slots.

    Every value here is one the same column accepts in its pooled row — a
    genuine integer `0`/`1`, or an in-range `[0,1]` float — so nothing about the
    binary domain or the float domain is being restated. What refuses is the
    placement: the frozen K policy does not compute per-question `@10`.
    """
    df = _put(column, setting, value)
    with pytest.raises(ValueError, match=_POPULATED_IN_REQUIRED_EMPTY):
        fri.validate_typed_metric_frame(df, "direct")
    with pytest.raises(ValueError, match=_POPULATED_IN_REQUIRED_EMPTY):
        fri.validate_structure(_put(column, setting, value), "direct", "dense")


@pytest.mark.parametrize("column,setting", sorted(REQUIRED_EMPTY_SLOTS))
@pytest.mark.parametrize("marker", MISSING_MARKERS)
def test_typed_frame_accepts_the_missing_twin_of_a_required_empty_slot(
        column, setting, marker):
    """The legal twin of the required-empty half is the absent cell."""
    fri.validate_typed_metric_frame(_put(column, setting, marker), "direct")


@pytest.mark.parametrize("column", sorted({c for c, _ in REQUIRED_EMPTY_SLOTS}))
def test_typed_placement_inverts_between_the_two_settings(column):
    """The same column, the same value: only the row's setting inverts the rule."""
    value = 1 if column in SCHEMA_BINARY_COLUMNS else 0.5
    marker = pd.NA if column in SCHEMA_BINARY_COLUMNS else np.nan

    fri.validate_typed_metric_frame(_put(column, "pooled", value), "direct")
    with pytest.raises(ValueError, match=_POPULATED_IN_REQUIRED_EMPTY):
        fri.validate_typed_metric_frame(_put(column, "per_question", value), "direct")
    with pytest.raises(ValueError, match=_missing_message(column)):
        fri.validate_typed_metric_frame(_put(column, "pooled", marker), "direct")
    fri.validate_typed_metric_frame(_put(column, "per_question", marker), "direct")


# ─────────── binary columns: genuine integers, on dtype and on value ──────────

@pytest.mark.parametrize("column", SCHEMA_BINARY_COLUMNS)
def test_typed_binary_column_rejects_a_nullable_boolean_dtype(column):
    df = _retype(column, lambda s: s.astype("boolean"))
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize(
    "column",
    [c for c in SCHEMA_BINARY_COLUMNS if c not in _BINARY_COLUMNS_WITH_A_MISSING_SLOT],
)
def test_typed_binary_column_rejects_a_numpy_bool_dtype(column):
    df = _retype(column, lambda s: s.astype(bool))
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column", SCHEMA_BINARY_COLUMNS)
def test_typed_binary_column_rejects_a_float_laundered_dtype(column):
    """`0.0`/`1.0` compare equal to `0`/`1`, and the cast is exactly what the
    contract refuses: the integer provenance is gone and cannot be restored."""
    df = _retype(column, lambda s: s.astype("float64"))
    assert df.loc[df.setting == "pooled", column].isin([0.0, 1.0]).all()
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column", SCHEMA_BINARY_COLUMNS)
def test_typed_binary_column_rejects_a_numeric_string_dtype(column):
    df = _retype(column, lambda s: s.astype(str))
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column", SCHEMA_BINARY_COLUMNS)
def test_typed_binary_column_rejects_an_object_dtype(column):
    """Even holding genuine integers: an object column has no integer type, so
    a numeric string could be hiding in it and nothing here will coerce."""
    df = _retype(column, lambda s: s.astype(object))
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column", SCHEMA_BINARY_COLUMNS)
@pytest.mark.parametrize("value", NON_BINARY_INTEGERS)
def test_typed_binary_column_rejects_a_non_0_1_integer(column, value):
    """Integer dtype is necessary, not sufficient: the value must be 0 or 1."""
    df = _put(column, "pooled", value)
    assert str(df[column].dtype) == "Int64"
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column", SCHEMA_BINARY_COLUMNS)
@pytest.mark.parametrize("value", [0, 1, np.int64(0), np.int64(1)])
def test_typed_binary_column_accepts_a_genuine_integer(column, value):
    """Legal twin for every binary rejection above."""
    fri.validate_typed_metric_frame(_put(column, "pooled", value), "direct")


@pytest.mark.parametrize("column", SCHEMA_BINARY_COLUMNS)
def test_typed_binary_dtype_refusal_also_fires_through_validate_structure(column):
    df = _retype(column, lambda s: s.astype("float64"))
    with pytest.raises(ValueError, match="non-0/1"):
        fri.validate_structure(df, "direct", "dense")


# ──────── float columns: numeric, finite, inside the inclusive [0,1] ──────────

@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
@pytest.mark.parametrize("value", OUT_OF_DOMAIN_TYPED)
def test_typed_float_column_rejects_an_out_of_domain_value(column, value):
    """the third demonstrated bypass, generalized over every float family."""
    df = _put(column, "pooled", value)
    with pytest.raises(ValueError, match=r"outside the inclusive \[0, 1\] domain"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
@pytest.mark.parametrize("value", IN_DOMAIN_TYPED)
def test_typed_float_column_accepts_an_in_domain_value(column, value):
    """Legal twins, including both inclusive boundaries and the interior."""
    fri.validate_typed_metric_frame(_put(column, "pooled", value), "direct")


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
def test_typed_float_column_rejects_an_out_of_domain_value_in_either_setting(column):
    for setting in SETTINGS:
        if (column, setting) in REQUIRED_EMPTY_SLOTS:
            # There a populated value refuses on placement, which is its own
            # matrix; the domain rule is exercised in the populated slot.
            continue
        with pytest.raises(ValueError, match=r"outside the inclusive \[0, 1\] domain"):
            fri.validate_typed_metric_frame(_put(column, setting, 1.1), "direct")


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
def test_typed_float_nan_in_a_required_populated_slot_is_a_placement_defect(column):
    """A `NaN` is how a typed frame spells "absent", so it is judged by
    placement rather than by the domain — and it still refuses."""
    with pytest.raises(ValueError,
                       match="missing cell where the schema requires a populated value"):
        fri.validate_typed_metric_frame(_put(column, "pooled", np.nan), "direct")


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
@pytest.mark.parametrize("transform", ["string", "object", "boolean"])
def test_typed_float_column_rejects_a_non_numeric_dtype(column, transform):
    caster = {"string": str, "object": object, "boolean": "boolean"}[transform]
    if transform == "boolean":
        df = _retype(column, lambda s: (s > 0.4).astype("boolean"))
    else:
        df = _retype(column, lambda s: s.astype(caster))
    with pytest.raises(ValueError, match="is not numeric"):
        fri.validate_typed_metric_frame(df, "direct")


@pytest.mark.parametrize("column", SCHEMA_FLOAT_COLUMNS)
def test_typed_float_integer_dtype_is_accepted_when_every_value_is_in_domain(column):
    """`is_numeric_dtype`, not `is_float_dtype`: an all-`1` integer column is
    still a legal `[0,1]` metric, and nothing re-types it.

    `partial_evidence_recall@10` is the one exception, and for the right reason:
    a non-nullable integer column physically cannot hold the required-empty
    per-question cell, so the same cast refuses on placement rather than on the
    domain.
    """
    df = _retype(column, lambda s: (s.fillna(1.0) * 0 + 1).astype("int64"))
    if (column, "per_question") in REQUIRED_EMPTY_SLOTS:
        with pytest.raises(ValueError, match=_POPULATED_IN_REQUIRED_EMPTY):
            fri.validate_typed_metric_frame(df, "direct")
        return
    fri.validate_typed_metric_frame(df, "direct")


# ───────────────── the typed layer never coerces or repairs ───────────────────

def test_typed_validation_does_not_mutate_the_frame():
    """A validator that silently normalized would hide the defect it reports."""
    df = _typed_frame()
    before = df.copy(deep=True)
    fri.validate_typed_metric_frame(df, "direct")
    pd.testing.assert_frame_equal(df, before)
    for column in SCHEMA_BINARY_COLUMNS + SCHEMA_FLOAT_COLUMNS:
        assert str(df[column].dtype) == str(before[column].dtype)


def test_typed_validation_leaves_a_rejected_frame_untouched():
    df = _retype("full_evidence_recall@5", lambda s: s.astype("float64"))
    before = df.copy(deep=True)
    with pytest.raises(ValueError):
        fri.validate_typed_metric_frame(df, "direct")
    pd.testing.assert_frame_equal(df, before)


def test_float_metric_cell_predicate_is_exact():
    """The typed float predicate has its own unit oracle."""
    for value in [0, 1, 0.0, 1.0, 0.5, -0.0, 1e-12, np.float64(0.5), np.int64(1)]:
        assert fri.is_float_metric_cell(value), value
    for value in [-0.1, 1.1, float("nan"), float("inf"), float("-inf"),
                  True, False, np.bool_(True), "0.5", None, pd.NA]:
        assert not fri.is_float_metric_cell(value), value


# ───────── the real formal inputs stay accepted by the new typed layer ────────

@pytest.mark.parametrize("path,method", [
    ("results/bm25_results.csv", "bm25"),
    ("results/dense_results.csv", "dense"),
    ("results/rerank_results.csv", "rerank"),
])
def test_the_real_formal_inputs_pass_the_typed_contract_untouched(path, method):
    """The guard must not change what the accepted formal bundle means."""
    df = fri.load_result_csv(path, method)
    fri.validate_typed_metric_frame(df, path)
    assert len(df) == 1000
    for column in SCHEMA_BINARY_COLUMNS:
        assert str(df[column].dtype) == "Int64", column
    for column, setting in REQUIRED_EMPTY_SLOTS:
        assert df.loc[df.setting == setting, column].isna().all()
    for column, setting in REQUIRED_POPULATED_SLOTS:
        assert df.loc[df.setting == setting, column].notna().all()
