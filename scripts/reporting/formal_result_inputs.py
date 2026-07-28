"""
formal_result_inputs.py  ->  scripts/reporting/formal_result_inputs.py

Shared, mechanical input contract for the BM25/dense/rerank *reporting* tools
(`disagreement_cases.py`, `bm25_failure_shortlist.py`, `rescue_damage.py`). It
closes the join those tools perform so they can never silently combine
unrelated records that merely share an `example_id`, and it closes the physical
value domains so a malformed cell can never reach an `int()` conversion.

Contract (frozen for these tools, see
`docs/specs/2026-07-27-bm25-dense-reporting-contracts.md`):

  - each input file exposes exactly ``RESULT_COLUMNS`` in order;
  - each input file is uniformly its expected method (`bm25`/`dense`/`rerank`);
  - the `setting` column is exactly ``{pooled, per_question}`` — both present,
    no other value, and together with the column it decides whether a metric
    cell must be empty or must be populated;
  - ``(setting, example_id)`` is unique within every file;
  - required textual metadata (`example_id`, `question`, `gold_titles`) is a
    non-null, non-empty string in every row, `retrieved_titles` is a string
    (empty = the approved empty retrieved list), and the closed upstream
    vocabularies ``question_type in {bridge, comparison}`` /
    ``level in {easy, medium, hard}`` hold
    (`docs/specs/2026-07-15-results-csv-schema.md`);
  - across the joined methods, each `setting` covers the identical example-id
    set (cross-method parity — required by the one-to-one per-setting join);
  - `question_type`, `level`, `question`, and `gold_titles` are properties of
    the example, so every row for a given `example_id` (across methods and
    settings) must carry identical values for those four fields — compared
    *including* missing values, so a one-sided null is drift, not a match;
  - a metric cell actually consumed as a binary criterion must be a plain
    integer 0/1: `bool`, float ``0.0``/``1.0``, numeric strings, and empty
    cells are refused even when numerically equal to 0/1;
  - a public `setting` argument is checked against the closed vocabulary before
    any row is selected, so an unsupported value can never pass vacuously by
    filtering the frame down to zero rows.

PHYSICAL PARSING (`read_formal_result_csv`) — column-aware and non-lossy.

The file is first read as **raw text**: every field keeps its exact physical
lexeme, with pandas' numeric parsing and its global NA-token inference both
switched off. Validation then runs on those lexemes, *before* any conversion,
so nothing can be normalized into legality:

  - binary hit columns admit exactly the owner-frozen lexeme set
    ``APPROVED_BINARY_LEXEMES`` (``0``, ``1``, ``0.0``, ``1.0``) or an empty
    cell — subject to the placement rule below, which decides which of the two
    a given slot must be. The float spellings exist only because the pooled
    ``@10`` columns of the current formal BM25/dense artifacts serialized as
    float once the per-question rows were left blank; they are a closed
    compatibility list, not a numeric range. Every other spelling — a
    precision-adjacent fraction such as ``0.00000000000000000001`` or
    ``0.99999999999999999999``, an ordinary fraction such as ``0.5``,
    scientific notation, a sign, a padding zero or space, a boolean, or a
    null-like word — is refused as text. This matters because a float parser
    rounds the first two of those to 0 and 1 and destroys the evidence that the
    cell was ever malformed;
  - the `[0,1]` float metric columns admit a finite decimal lexeme whose exact
    written value lies within the inclusive ``[0, 1]`` domain the shared schema
    declares. Lexical finiteness is not the semantic domain: ``-0.1``, ``1.1``,
    ``2``, and the overflow spelling ``1e9999`` are all finite decimals and all
    refuse. The check runs on the exact decimal, before conversion, because
    ``float()`` launders the two boundary-adjacent cases —
    ``1.0000000000000001`` rounds down to exactly ``1.0`` and ``-1e-400``
    underflows to ``-0.0`` — into apparently legal values. The converted float
    is then re-checked as finite and in range as a defensive backstop;
    ``NaN``, ``inf``, and null-like words are refused;
  - textual columns are never NA-inferred, so the legitimate strings ``None``,
    ``NA``, ``null``, and ``NaN`` survive as themselves, and *placement* —
    whether a metric cell is present at all — is decided per column *and per
    row*, as a two-sided contract rather than a nullability permission
    (`metric_cell_placement`). Each ``(metric column, setting)`` slot is
    exactly one of two states: the three recall ``@10`` columns on a
    ``per_question`` row are ``REQUIRED_EMPTY`` — the schema does not merely
    tolerate a blank there, it declares the metric uncomputed — and every other
    metric slot is ``REQUIRED_POPULATED``. So an empty pooled recall cell, an
    empty per-question ``@2``/``@5`` cell, and an empty reciprocal-rank cell
    refuse as a truncated file, *and* a populated per-question ``@10`` recall
    cell refuses as an unauthorized extension of the frozen K policy — both
    before conversion and before any write. Without the second half the three
    tools would not share one input language: rescue would refuse a populated
    ``@10`` while the two general tools published a report from the same file.
    An empty ``retrieved_titles`` cell stays legal: it is text, the approved
    serialization of an empty retrieved list, not a metric.

There is deliberately **no** public helper that normalizes an in-memory frame's
binary columns: such a helper erases the float provenance the contract refuses,
so a caller building a frame by hand must construct the nullable-integer
columns from integer/missing values directly.

TYPED-FRAME VALIDATION (`validate_typed_metric_frame`) — the second layer.

The lexeme rules above can only run on a file. A caller may also hand a tool an
already-created DataFrame — `extract_disagreements`, `build_shortlist`, and
`build_paired_frame` all accept one — and for such a frame the physical
spellings no longer exist. The two layers are therefore deliberately distinct,
and neither pretends to be the other:

  - the **raw CSV layer** decides exact physical binary spellings, exact
    `Decimal` range comparisons, and raw required-empty / required-populated
    placement, all before conversion;
  - the **typed frame layer** decides every invariant that survives parsing:
    all three per-question recall `@10` slots are missing, all other 19
    `(metric column, setting)` slots are populated, every populated binary cell
    is a genuine integer `0`/`1` (a `bool`, float-laundered, string,
    object/numeric-string, or otherwise non-integer column refuses on its
    physical dtype), and every partial-recall and reciprocal-rank cell is
    numeric, finite, and inside the inclusive `[0,1]` domain.

The typed layer performs **no normalization and no coercion**. It cannot
reconstruct a lost spelling — a frame whose binary column is float dtype is
refused, not repaired — and it never clips, rounds, or fills a value; it only
refuses. Running it from `validate_structure` (after the `setting` vocabulary is
known, so placement is decidable) is what stops a public in-memory entry point
from publishing a bundle the file entry points refuse, and is what keeps the
three tools sharing exactly one input language on both kinds of input.

AI-USAGE BOUNDARY: this module is pure plumbing. It defines no metric and makes
no failure-category judgment; metric definitions stay hand-written in
`src/evaluator.py`. It only validates structure and refuses malformed bundles.
"""

import decimal
import math

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_integer_dtype, is_numeric_dtype

from src.results_schema import (
    BASE_COLUMNS,
    RECIPROCAL_RANK_COLUMNS,
    RESULT_COLUMNS,
)

SETTINGS = ("pooled", "per_question")

# Closed upstream vocabularies (docs/specs/2026-07-15-results-csv-schema.md).
QUESTION_TYPES = ("bridge", "comparison")
LEVELS = ("easy", "medium", "hard")

# The example-level metadata that must be identical across every
# (method, setting) row of the same example_id.
META_COLUMNS = ["question_type", "level", "question", "gold_titles"]

# Metadata that must be a non-null, non-empty string but has no closed
# vocabulary.
_TEXT_METADATA_COLUMNS = ["example_id", "question", "gold_titles"]
# Text whose empty value is meaningful: an empty `retrieved_titles` cell is the
# approved serialization of an empty retrieved list, not a missing value.
_OPTIONAL_TEXT_COLUMNS = ["retrieved_titles"]
_CLOSED_METADATA_VOCABULARIES = {
    "question_type": QUESTION_TYPES,
    "level": LEVELS,
}

# The binary hit columns of the shared schema. `partial_evidence_recall@k` is a
# [0,1] float and is deliberately absent: it is not a binary hit column.
BINARY_METRIC_COLUMNS = [
    f"{metric}@{k}"
    for metric in ("any_evidence_recall", "full_evidence_recall")
    for k in (2, 5, 10)
]

# The non-binary numeric columns: `[0,1]` partial recall plus the per-example
# reciprocal ranks.
FLOAT_METRIC_COLUMNS = [
    f"partial_evidence_recall@{k}" for k in (2, 5, 10)
] + list(RECIPROCAL_RANK_COLUMNS)

# Every metric column of the shared schema, binary and float alike.
METRIC_COLUMNS = BINARY_METRIC_COLUMNS + FLOAT_METRIC_COLUMNS

# The inclusive semantic domain the shared schema declares for a float metric
# column (`docs/specs/2026-07-15-results-csv-schema.md`: partial recall and
# reciprocal rank are `[0,1]`). Held as `Decimal` so the raw lexeme is compared
# exactly, before any binary-floating-point rounding can occur.
FLOAT_METRIC_MIN = decimal.Decimal(0)
FLOAT_METRIC_MAX = decimal.Decimal(1)

# The only metric cells the shared schema leaves uncomputed: the three recall
# `@10` columns of a `per_question` row (storage/metric policy table — a
# ~10-paragraph per-question corpus makes `@10` trivial). The schema does not
# say those cells *may* be blank, it says the metric is not computed and the
# cell *is* empty, so a populated value there is an unauthorized extension of
# the frozen K policy. Pooled recall, per-question `@2`/`@5`, and both
# reciprocal-rank columns are conversely always populated, so a blank there is a
# truncated or partially generated file, not a deliberate uncomputed value.
REQUIRED_EMPTY_METRIC_COLUMNS = (
    "any_evidence_recall@10",
    "full_evidence_recall@10",
    "partial_evidence_recall@10",
)
REQUIRED_EMPTY_SETTING = "per_question"

# The two placement states of a `(metric column, setting)` slot. There is no
# third, "either" state: that reading is exactly what let a populated
# per-question `@10` cell through the two general tools while rescue refused it.
REQUIRED_EMPTY = "required-empty"
REQUIRED_POPULATED = "required-populated"

# Owner-frozen physical lexemes for a binary hit cell (Xin, 2026-07-27; recorded
# in the three canonical authorities). This is an exhaustive, closed list of
# spellings, not a numeric tolerance: membership is decided on the raw text.
APPROVED_BINARY_LEXEMES = ("0", "1", "0.0", "1.0")
_BINARY_LEXEME_VALUES = {"0": 0, "1": 1, "0.0": 0, "1.0": 1}

# The one lexeme that means "deliberately uncomputed", and the only accepted
# cell in a `REQUIRED_EMPTY` slot. A consumed cell still refuses it
# (`validate_consumed_binary`).
EMPTY_LEXEME = ""


def is_binary_cell(value):
    """True only for a plain integer 0 or 1.

    `bool`, float ``0.0``/``1.0``, numeric strings, and missing values are all
    rejected, even when they compare equal to 0/1 — equality semantics are
    exactly what let a malformed physical cell reach `int()`.
    """
    if isinstance(value, (bool, np.bool_)):
        return False
    if not isinstance(value, (int, np.integer)):
        return False
    return int(value) in (0, 1)


def is_float_metric_cell(value):
    """True only for a real, finite number inside the inclusive `[0,1]` domain.

    The typed-frame counterpart of `_is_in_domain_decimal_lexeme`. On a frame
    the exact written decimal no longer exists, so the value itself is the
    subject: a `bool`, a string, any other non-numeric scalar, a `NaN`, an
    infinity, a negative, and anything greater than one are all refused.
    Nothing is clipped or rounded — an out-of-domain value is a defect to report,
    not a value to repair.
    """
    if isinstance(value, (bool, np.bool_)):
        return False
    if not isinstance(value, (int, float, np.integer, np.floating)):
        return False
    number = float(value)
    return math.isfinite(number) and 0.0 <= number <= 1.0


def _is_missing_scalar(value):
    """True when a typed metric cell holds no value (`NaN`, `pd.NA`, `None`).

    Presence, not legality: which cells *may* be missing is decided by
    `metric_cell_placement`, exactly as it is on the raw text.
    """
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return False


def _decimal_lexeme(token):
    """The exact `Decimal` an exactly-written finite decimal token spells.

    Returns `None` for anything else. Padding whitespace and digit underscores
    are refused rather than stripped, and `Decimal`'s own `NaN` / `Infinity`
    spellings are refused by the finiteness check, so a null-like word can never
    become a float metric. The value is exact: unlike `float(token)` it neither
    rounds a boundary-adjacent decimal nor overflows a large exponent.
    """
    if token != token.strip() or "_" in token:
        return None
    try:
        value = decimal.Decimal(token)
    except (decimal.DecimalException, ValueError):
        return None
    return value if value.is_finite() else None


def _is_finite_decimal_lexeme(token):
    """True only for an exactly-written finite decimal number, any magnitude."""
    return _decimal_lexeme(token) is not None


def _is_in_domain_decimal_lexeme(token):
    """True only for a finite decimal token whose exact value is within [0,1].

    This is the *semantic* domain check, deliberately separate from lexical
    finiteness: `-0.1`, `1.1`, `2`, and `1e9999` are all perfectly well-formed
    finite decimals and none of them is a legal recall or reciprocal rank.
    Comparing the exact `Decimal` is what makes the two boundary-adjacent
    spellings visible — `float("1.0000000000000001")` is exactly `1.0` and
    `float("-1e-400")` is `-0.0`, so a conversion-first check would accept both.
    """
    value = _decimal_lexeme(token)
    if value is None:
        return False
    try:
        return FLOAT_METRIC_MIN <= value <= FLOAT_METRIC_MAX
    except decimal.DecimalException:  # pragma: no cover - defensive
        return False


def _read_raw_lexemes(path):
    """Read the file as exact physical text.

    `na_filter=False` disables pandas' global null-token inference and
    `dtype=str` disables numeric parsing, so every field arrives as the literal
    characters the file contains. Nothing here interprets a value; that is the
    point — interpretation before validation is what let a fractional cell be
    rounded into an apparently legal integer.
    """
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{path}: is not a readable formal result CSV ({exc}).") from exc


def _column_lexemes(raw, column, source):
    """The column's raw physical text, refusing a non-string (ragged) cell."""
    tokens = raw[column].tolist()
    for position, token in enumerate(tokens):
        if not isinstance(token, str):
            raise ValueError(
                f"{source}: {column} row {position} is not a physical text "
                f"field ({token!r}); the row is ragged or malformed."
            )
    return tokens


def _offenders(tokens, predicate, limit=3):
    """The first `limit` ``"row N: <lexeme>"`` strings failing `predicate`."""
    bad = []
    for position, token in enumerate(tokens):
        if not predicate(token):
            bad.append(f"row {position}: {token!r}")
            if len(bad) >= limit:
                break
    return bad


def metric_cell_placement(column, setting):
    """Whether a metric cell of `column` must be empty or populated in `setting`.

    This is the whole placement contract, in one predicate, so the three tools
    cannot drift into different input languages. The schema reserves an
    uncomputed metric for exactly one situation — a per-question `@10` recall —
    and *reserves* means both directions: that cell must be empty, and every
    other metric cell must be populated. Reading it as a mere permission to be
    blank leaves the inverse open, so a rerun that accidentally computes an
    `@10` value the frozen K policy declares absent looks like a valid bundle.
    """
    if column in REQUIRED_EMPTY_METRIC_COLUMNS and setting == REQUIRED_EMPTY_SETTING:
        return REQUIRED_EMPTY
    return REQUIRED_POPULATED


def _placement_offenders(column, tokens, settings, state, limit=3):
    """Cells of `column` whose physical presence contradicts `state`.

    With `state=REQUIRED_POPULATED` this collects empty cells in slots the
    schema always populates; with `state=REQUIRED_EMPTY` it collects populated
    cells in the three slots the schema leaves uncomputed. Both halves run on
    the raw lexeme, before conversion and before any destination is touched.

    `settings` is the row-aligned `setting` lexeme list, or `None` when the file
    carries no `setting` column at all. In that case placement is not decidable,
    so it is left to `validate_structure`, which reports the wrong column set in
    full and refuses the file before any tool can consume it.
    """
    if settings is None:
        return []
    bad = []
    for position, token in enumerate(tokens):
        if metric_cell_placement(column, settings[position]) != state:
            continue
        empty = token == EMPTY_LEXEME
        if empty == (state == REQUIRED_EMPTY):
            continue
        where = f"row {position} (setting {settings[position]!r})"
        # An offending blank has no lexeme worth quoting; an offending populated
        # cell does, and naming it is what makes the defect diagnosable.
        bad.append(where if empty else f"{where}: {token!r}")
        if len(bad) >= limit:
            break
    return bad


def _validate_metric_spelling(column, tokens, source):
    """Refuse any metric lexeme outside its column family's legal spellings.

    An empty cell is passed over here and decided by `_validate_metric_placement`
    instead, so the two questions stay separate: *is this a legal spelling* and
    *should this cell exist at all*.
    """
    if column in BINARY_METRIC_COLUMNS:
        bad = _offenders(
            tokens,
            lambda token: token == EMPTY_LEXEME or token in _BINARY_LEXEME_VALUES,
        )
        if bad:
            raise ValueError(
                f"{source}: {column} has cell(s) that are not an approved "
                f"binary lexeme, e.g. {bad}. The frozen physical rule admits "
                f"exactly {list(APPROVED_BINARY_LEXEMES)} or an empty cell "
                f"where the schema requires a blank, decided on the raw text "
                f"before any numeric conversion, so a fraction, scientific "
                f"notation, a sign, a padding zero or space, a boolean, or a "
                f"null-like word is refused even when a float parser would "
                f"round it to 0 or 1."
            )
        return

    bad = _offenders(
        tokens,
        lambda token: token == EMPTY_LEXEME or _is_finite_decimal_lexeme(token),
    )
    if bad:
        raise ValueError(
            f"{source}: {column} has cell(s) that are not a finite decimal "
            f"or a permitted empty cell, e.g. {bad}. A null-like word such "
            f"as NaN/NA/null/None, an infinity, and a padded or underscored "
            f"number are all refused."
        )
    bad = _offenders(
        tokens,
        lambda token: token == EMPTY_LEXEME or _is_in_domain_decimal_lexeme(token),
    )
    if bad:
        raise ValueError(
            f"{source}: {column} has cell(s) outside the inclusive "
            f"[{FLOAT_METRIC_MIN}, {FLOAT_METRIC_MAX}] domain the schema "
            f"declares for this metric, e.g. {bad}. The exact written "
            f"decimal is compared before any conversion, so a negative, a "
            f"value greater than one, an overflow spelling such as 1e9999, "
            f"and a boundary-adjacent decimal that float() would round into "
            f"range are all refused."
        )


def _validate_metric_placement(column, tokens, settings, source):
    """Refuse any metric cell that is present where the schema requires absence,
    or absent where the schema requires presence.

    Both halves of the same invariant, applied to every input file the three
    tools read, so a bundle one tool refuses can never be published by another.
    """
    misplaced = _placement_offenders(column, tokens, settings, REQUIRED_POPULATED)
    if misplaced:
        raise ValueError(
            f"{source}: {column} has an empty cell where the schema permits "
            f"none, e.g. {misplaced}. A metric cell is physically empty only "
            f"in {list(REQUIRED_EMPTY_METRIC_COLUMNS)} on a "
            f"{REQUIRED_EMPTY_SETTING!r} row (the deliberately uncomputed @10 "
            f"recall of the storage policy); pooled recall, per-question "
            f"@2/@5, and both reciprocal-rank columns are always populated, "
            f"so a blank there is a truncated or partially generated file. "
            f"An empty retrieved_titles cell remains legal: it is text, the "
            f"approved empty retrieved list, not a metric."
        )

    misplaced = _placement_offenders(column, tokens, settings, REQUIRED_EMPTY)
    if misplaced:
        raise ValueError(
            f"{source}: {column} has a populated cell where the schema "
            f"requires an empty one, e.g. {misplaced}. The storage/metric "
            f"policy does not compute "
            f"{list(REQUIRED_EMPTY_METRIC_COLUMNS)} on a "
            f"{REQUIRED_EMPTY_SETTING!r} row, so those cells must be "
            f"physically empty; an approved lexeme such as 0/1/0.0/1.0 or an "
            f"in-range decimal is refused there too, because a value the "
            f"frozen K policy declares absent is an unauthorized metric "
            f"extension rather than a legal spelling."
        )


def validate_physical_lexemes(raw, source):
    """Validate the raw physical lexemes of a formal result CSV.

    Runs on text, before any numeric conversion, so a cell that a parser would
    round or normalize into legality is still visible as what it physically is.
    Validation is column- *and* row-aware in two independent ways: a metric's
    legal spellings are bounded by the frozen binary lexeme set or by the
    schema's `[0,1]` domain rather than by decimal finiteness, and its legal
    *placement* — required empty or required populated — is decided by the
    column together with the row's `setting`. Spelling is checked first so a
    physically impossible token is reported as what it is; placement then
    closes both halves of the uncomputed-`@10` rule. Only columns actually
    present are checked; a wrong column set is reported later, in full, by
    `validate_structure`.
    """
    settings = (
        _column_lexemes(raw, "setting", source)
        if "setting" in raw.columns else None
    )

    for column in METRIC_COLUMNS:
        if column not in raw.columns:
            continue
        tokens = _column_lexemes(raw, column, source)
        _validate_metric_spelling(column, tokens, source)
        _validate_metric_placement(column, tokens, settings, source)

    # Textual columns are never NA-inferred, so nothing here reinterprets a
    # legitimate `None`/`NA`/`null`/`NaN` string; this only rejects a ragged row.
    for column in BASE_COLUMNS:
        if column not in raw.columns:
            continue
        _column_lexemes(raw, column, source)


def _float_metric_value(token, column, position, source):
    """Convert one validated float-metric lexeme, re-checking the result.

    `validate_physical_lexemes` has already refused every lexeme outside the
    schema's `[0,1]` domain, so this is a defensive backstop rather than the
    primary gate. It guarantees that no conversion artifact — an exponent that
    overflows to infinity, a decimal that rounds across the boundary — can put a
    non-finite or out-of-range float into the frame the tools consume.
    """
    if token == EMPTY_LEXEME:
        return np.nan
    try:
        value = float(token)
    except (ValueError, OverflowError) as exc:  # pragma: no cover - defensive
        raise ValueError(
            f"{source}: {column} row {position} lexeme {token!r} is not "
            f"convertible to a float ({exc})."
        ) from exc
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:  # pragma: no cover
        raise ValueError(
            f"{source}: {column} row {position} lexeme {token!r} converted to "
            f"{value!r}, which is not a finite value inside the inclusive "
            f"[0, 1] domain; the converted float must stay in the domain the "
            f"validated lexeme promised."
        )
    return value


def _typed_frame(raw, source):
    """Convert validated lexemes to the physical frame the tools consume.

    Binary columns become nullable integers (an empty cell stays missing and is
    never silently read as 0), the `[0,1]` metric columns become floats whose
    converted values are re-checked as finite and in range, and textual columns
    keep the exact strings that were read.
    """
    df = raw.copy()
    for column in BINARY_METRIC_COLUMNS:
        if column not in df.columns:
            continue
        df[column] = pd.array(
            [
                pd.NA if token == EMPTY_LEXEME else _BINARY_LEXEME_VALUES[token]
                for token in raw[column].tolist()
            ],
            dtype="Int64",
        )
    for column in FLOAT_METRIC_COLUMNS:
        if column not in df.columns:
            continue
        df[column] = pd.Series(
            [
                _float_metric_value(token, column, position, source)
                for position, token in enumerate(raw[column].tolist())
            ],
            index=raw.index,
            dtype="float64",
        )
    return df


def read_formal_result_csv(path):
    """Read one formal result CSV under the schema's physical value domains.

    The file is read as raw text, validated lexically, and only then converted:
    a physically fractional, boolean, null-like, out-of-domain, or otherwise
    unapproved metric cell — and a misplaced one, blank where the schema
    requires a value or populated where it requires none — is refused here,
    before any frame the tools can consume exists, and therefore before any
    destination can be created or overwritten.
    """
    raw = _read_raw_lexemes(path)
    validate_physical_lexemes(raw, path)
    return _typed_frame(raw, path)


def load_result_csv(path, expected_method):
    """Read one formal result CSV and enforce the per-file structural contract."""
    df = read_formal_result_csv(path)
    validate_structure(df, path, expected_method)
    return df


def validate_setting(setting):
    """A public `setting` argument must be in the closed vocabulary.

    Checked before any row is selected: filtering by an unsupported value would
    otherwise yield an empty frame that passes every downstream cell check
    vacuously and looks like a genuine zero-case result.
    """
    if not isinstance(setting, str) or setting not in SETTINGS:
        raise ValueError(
            f"Unsupported setting {setting!r}; supported settings are exactly "
            f"{list(SETTINGS)} (exact, case-sensitive)."
        )


def validate_metadata_domains(df, source):
    """Required metadata must be non-null text within its closed vocabulary."""
    for column in _TEXT_METADATA_COLUMNS:
        invalid = [
            v for v in df[column].tolist()
            if not isinstance(v, str) or v == ""
        ]
        if invalid:
            raise ValueError(
                f"{source}: {column} must be a non-null string in every row "
                f"(schema); found {len(invalid)} null/non-string/empty "
                f"value(s), e.g. {invalid[:3]}."
            )

    # An empty cell here is the approved empty retrieved list and stays empty;
    # a missing or non-string value is refused so no consumer can stringify it
    # into fabricated title text.
    for column in _OPTIONAL_TEXT_COLUMNS:
        invalid = [v for v in df[column].tolist() if not isinstance(v, str)]
        if invalid:
            raise ValueError(
                f"{source}: {column} must be a string in every row (schema); an "
                f"empty cell is the approved empty list, but a missing or "
                f"non-string value is refused; found {len(invalid)} such "
                f"value(s), e.g. {invalid[:3]}."
            )

    for column, allowed in _CLOSED_METADATA_VOCABULARIES.items():
        invalid = [
            v for v in df[column].tolist()
            if not isinstance(v, str) or v not in allowed
        ]
        if invalid:
            raise ValueError(
                f"{source}: {column} must be exactly a non-null string in "
                f"{list(allowed)} (schema); found {len(invalid)} invalid "
                f"value(s), e.g. {invalid[:3]}."
            )


# ───────────────── typed-frame metric contract (second layer) ────────────────
# Everything below runs on an already-created DataFrame, where the physical
# lexemes are gone. It therefore claims nothing about spelling — that is the raw
# reader's job and cannot be reconstructed — and instead closes every invariant
# that *does* survive parsing, so a caller who builds or mutates a frame in
# memory cannot publish a bundle the file entry points refuse.


def _typed_settings(df, source):
    """The row-aligned `setting` values, refusing anything placement can't use."""
    if "setting" not in df.columns:
        raise ValueError(
            f"{source}: a formal result frame must carry a 'setting' column; "
            f"without it a metric cell's required placement is not decidable."
        )
    settings = df["setting"].tolist()
    unknown = sorted({repr(value) for value in settings if value not in SETTINGS})
    if unknown:
        raise ValueError(
            f"{source}: cannot decide metric placement because the frame "
            f"carries setting value(s) outside {list(SETTINGS)}, e.g. "
            f"{unknown[:3]}."
        )
    return settings


def _validate_typed_metric_dtype(column, series, source):
    """Refuse a metric column whose physical dtype cannot hold contract values.

    This is the typed-frame analogue of the lexeme rule, and it is the check
    that makes laundering visible: a binary column cast to float, string, or
    object has already destroyed the integer provenance the contract requires,
    and no non-coercing validator can give it back.
    """
    dtype = series.dtype
    if column in BINARY_METRIC_COLUMNS:
        if is_bool_dtype(dtype) or not is_integer_dtype(dtype):
            raise ValueError(
                f"{source}: binary metric column {column} has empty or non-0/1 "
                f"values: the column's physical type is {dtype}, but the "
                f"typed-frame contract requires genuine integer cells, so a "
                f"bool, float, string, or object column is refused even when "
                f"every value compares equal to 0/1. Nothing is coerced: a "
                f"float-laundered binary column cannot be normalized back into "
                f"the provenance the cast destroyed."
            )
        return
    if is_bool_dtype(dtype) or not is_numeric_dtype(dtype):
        raise ValueError(
            f"{source}: float metric column {column} is not numeric: the "
            f"column's physical type is {dtype}, but partial recall and "
            f"reciprocal rank must be real numbers inside the inclusive "
            f"[{FLOAT_METRIC_MIN}, {FLOAT_METRIC_MAX}] domain, so a bool, "
            f"string, or object column is refused even when its cells print as "
            f"numbers."
        )


def _typed_placement_offenders(column, values, settings, state, limit=3):
    """Typed cells of `column` whose presence contradicts `state`.

    Mirrors `_placement_offenders` exactly, one layer later: there the subject
    is the physical lexeme, here it is the parsed scalar. Both halves of the
    two-state rule are collected the same way, so the two layers cannot drift
    into different placement contracts.
    """
    bad = []
    for position, value in enumerate(values):
        if metric_cell_placement(column, settings[position]) != state:
            continue
        missing = _is_missing_scalar(value)
        if missing == (state == REQUIRED_EMPTY):
            continue
        where = f"row {position} (setting {settings[position]!r})"
        # An offending absence has no value worth quoting; an offending present
        # cell does, and naming it is what makes the defect diagnosable.
        bad.append(where if missing else f"{where}: {value!r}")
        if len(bad) >= limit:
            break
    return bad


def _validate_typed_metric_placement(column, values, settings, source):
    """Refuse a typed metric cell that is present where the schema requires
    absence, or absent where the schema requires presence."""
    misplaced = _typed_placement_offenders(
        column, values, settings, REQUIRED_POPULATED
    )
    if misplaced:
        if column in BINARY_METRIC_COLUMNS:
            raise ValueError(
                f"{source}: binary metric column {column} has empty or non-0/1 "
                f"values: the cell is missing in a slot the schema requires to "
                f"be populated, e.g. {misplaced}. On a typed frame a metric "
                f"value is absent only in "
                f"{list(REQUIRED_EMPTY_METRIC_COLUMNS)} on a "
                f"{REQUIRED_EMPTY_SETTING!r} row; a missing pooled recall or a "
                f"missing per-question @2/@5 cell is a truncated or partially "
                f"built bundle, not a deliberately uncomputed metric."
            )
        raise ValueError(
            f"{source}: float metric column {column} has a missing cell where "
            f"the schema requires a populated value, e.g. {misplaced}. Pooled "
            f"partial recall, per-question partial @2/@5, and both "
            f"reciprocal-rank columns are always populated, so a missing value "
            f"there is a truncated or partially built bundle."
        )

    misplaced = _typed_placement_offenders(column, values, settings, REQUIRED_EMPTY)
    if misplaced:
        raise ValueError(
            f"{source}: {column} has a populated cell where the schema "
            f"requires an empty one, e.g. {misplaced}. The storage/metric "
            f"policy does not compute "
            f"{list(REQUIRED_EMPTY_METRIC_COLUMNS)} on a "
            f"{REQUIRED_EMPTY_SETTING!r} row, so those typed cells must be "
            f"missing; a genuine integer 0/1 and an in-range [0, 1] float are "
            f"refused there exactly as a malformed value is, because a value "
            f"the frozen K policy declares absent is an unauthorized metric "
            f"extension rather than a legal cell."
        )


def _validate_typed_metric_values(column, values, settings, source):
    """Refuse a populated typed metric cell outside its family's value domain.

    Only present cells are examined: an absent one has already been judged by
    the placement rule, which is the sole authority on whether it may be absent.
    """
    if column in BINARY_METRIC_COLUMNS:
        invalid = [
            f"row {position}: {value!r}"
            for position, value in enumerate(values)
            if not _is_missing_scalar(value) and not is_binary_cell(value)
        ]
        if invalid:
            raise ValueError(
                f"{source}: binary metric column {column} has empty or non-0/1 "
                f"values, e.g. {invalid[:3]}. A populated binary cell must be "
                f"the genuine integer 0 or 1; a bool, a float, a numeric "
                f"string, and any other integer are refused even when they "
                f"compare equal to 0/1."
            )
        return

    invalid = [
        f"row {position}: {value!r}"
        for position, value in enumerate(values)
        if not _is_missing_scalar(value) and not is_float_metric_cell(value)
    ]
    if invalid:
        raise ValueError(
            f"{source}: {column} has cell(s) outside the inclusive "
            f"[{FLOAT_METRIC_MIN}, {FLOAT_METRIC_MAX}] domain the schema "
            f"declares for this metric, e.g. {invalid[:3]}. On a typed frame "
            f"the parsed value is the subject, so a negative, a value greater "
            f"than one, an infinity, and a non-numeric scalar all refuse; "
            f"nothing is clipped, rounded, or filled."
        )


def validate_typed_metric_frame(df, source):
    """The complete metric contract of an **already-typed** result frame.

    The second of the two validation layers, and the one a caller who never
    touches a file still has to satisfy. It enforces, without any normalization
    or coercion, every invariant that survives parsing:

      - the three per-question recall `@10` slots are missing and the other 19
        `(metric column, setting)` slots are populated (`metric_cell_placement`,
        the same predicate the raw reader uses);
      - every populated binary cell is a genuine integer `0` or `1`, on the
        column's physical dtype as well as on the value, so a `bool`,
        float-laundered, string, or object binary column refuses;
      - every populated partial-recall and reciprocal-rank cell is numeric,
        finite, and inside the inclusive `[0,1]` domain.

    It deliberately does **not** re-derive the physical spelling rules of §1.1:
    a typed frame no longer holds the lexemes, and pretending otherwise would
    claim provenance the frame cannot carry. `read_formal_result_csv` remains
    the only authority on those, and the two layers compose — every file path
    runs both.
    """
    settings = _typed_settings(df, source)
    for column in METRIC_COLUMNS:
        if column not in df.columns:
            raise ValueError(
                f"{source}: metric column {column} is absent; the typed metric "
                f"contract covers all {len(METRIC_COLUMNS)} metric columns of "
                f"the shared schema and cannot be satisfied by a subset."
            )
        series = df[column]
        _validate_typed_metric_dtype(column, series, source)
        values = series.tolist()
        _validate_typed_metric_placement(column, values, settings, source)
        _validate_typed_metric_values(column, values, settings, source)


def validate_structure(df, source, expected_method):
    """Per-file structural contract. Fail-fast on any violation.

    Also the shared gate for the typed-frame metric contract: every public
    entry point that accepts an already-created result frame runs this, so no
    caller can validate only the cell it consumes and trust the rest.
    """
    if list(df.columns) != RESULT_COLUMNS:
        raise ValueError(f"{source}: columns do not match RESULT_COLUMNS exactly.")

    validate_metadata_domains(df, source)

    methods = set(df["method"].unique())
    if methods != {expected_method}:
        raise ValueError(
            f"{source}: expected method uniformly {expected_method!r}, "
            f"got {sorted(methods)}."
        )

    settings = set(df["setting"].unique())
    if settings != set(SETTINGS):
        raise ValueError(
            f"{source}: setting vocabulary must be exactly {set(SETTINGS)}, "
            f"got {settings}."
        )

    # Unique (setting, example_id): each setting must not repeat an example id.
    for setting in SETTINGS:
        sub = df[df["setting"] == setting]
        if len(sub) != sub["example_id"].nunique():
            raise ValueError(
                f"{source}: duplicate example_id within setting {setting!r} "
                f"({len(sub)} rows, {sub['example_id'].nunique()} unique)."
            )

    # The complete typed metric contract, run last because it needs the closed
    # `setting` vocabulary above to decide each cell's required placement. Every
    # metric column is covered, not only the one a caller happens to consume.
    validate_typed_metric_frame(df, source)


def validate_cross_method_identity(frames):
    """Cross-method identity contract for structurally valid frames.

    ``frames`` maps method name -> DataFrame (already ``validate_structure``-d).
    For each setting, every method must cover the identical example-id set, and
    every ``example_id`` must carry identical metadata across all
    ``(method, setting)`` rows. Missing values participate in that comparison,
    so a value present on one side and absent on the other is drift.
    """
    methods = sorted(frames)
    for setting in SETTINGS:
        id_sets = {
            m: set(frames[m][frames[m]["setting"] == setting]["example_id"])
            for m in methods
        }
        reference = id_sets[methods[0]]
        for m in methods[1:]:
            if id_sets[m] != reference:
                raise ValueError(
                    f"example_id sets differ across methods in setting "
                    f"{setting!r} ({methods[0]} vs {m}); the join would not be "
                    f"one-to-one."
                )

    combined = pd.concat(list(frames.values()), ignore_index=True)
    nunique = combined.groupby("example_id", dropna=False)[META_COLUMNS].nunique(
        dropna=False
    )
    drift = nunique[(nunique > 1).any(axis=1)]
    if not drift.empty:
        raise ValueError(
            f"Same-example_id metadata drift across (method, setting) rows for "
            f"{len(drift)} id(s), e.g. {list(drift.index[:3])}."
        )


def validate_consumed_binary(df, col, setting, source):
    """The metric cell each tool consumes must be a plain integer 0/1.

    Enforced before any `int()` conversion, and on the physical type as well as
    the value: a boolean, a float ``0.0``/``1.0``, a numeric string, or an empty
    cell is refused even though it compares equal to 0/1.

    This is deliberately a **narrow, single-column** predicate — it is named for
    the cell a tool selects, and it also refuses a legally blank per-question
    `@10` cell that a caller tries to *consume*, which the whole-frame contract
    must not do. It is never a substitute for `validate_typed_metric_frame`: no
    builder relies on it alone, because trusting the unconsumed columns is
    exactly how a malformed bundle used to reach a published report.
    """
    validate_setting(setting)
    if col not in df.columns:
        raise ValueError(f"{source}: unknown metric column {col!r}.")

    cells = df.loc[df["setting"] == setting, col]
    if cells.empty:
        raise ValueError(
            f"{source}: consumed cell {col} in setting {setting!r} selects no "
            f"rows; an empty selection cannot vacuously satisfy the 0/1 contract."
        )
    if is_bool_dtype(cells) or not is_integer_dtype(cells):
        raise ValueError(
            f"{source}: consumed cell {col} in setting {setting!r} has empty or "
            f"non-0/1 values: the column's physical type is {cells.dtype}, but "
            f"the contract requires plain integer cells (bool, float, and "
            f"string cells are refused even when equal to 0/1)."
        )
    invalid = [v for v in cells.tolist() if not is_binary_cell(v)]
    if invalid:
        raise ValueError(
            f"{source}: consumed cell {col} in setting {setting!r} has empty or "
            f"non-0/1 values, e.g. {invalid[:3]}."
        )
