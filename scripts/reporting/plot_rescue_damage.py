"""
plot_rescue_damage.py   ->  place at  scripts/reporting/plot_rescue_damage.py

Render the frozen rescue/damage summary as two slide-ready figures.

Inputs:  results/rerank_rescue_damage.csv        aggregate summary, frozen
                                                17 columns / 21 rows
                                                (scripts/reporting/rescue_damage.py)
         results/rerank_rescue_damage_cases.csv  per-example cases, frozen
                                                12 columns / 2500 rows
                                                (scripts/reporting/rerank_rescue_damage_cases.py)
Output:  results/figures/rerank_rescue_damage.html
         A self-contained page (inline SVG, no third-party runtime, no network)
         holding three 1280x720 figure cards plus the table views behind them:
           Figure 1 - waterfall of the pooled Full@5 decomposition, beside a
                      symmetric-scale rescue/damage comparison at every cutoff.
           Figure 2 - rescue/damage as a SHARE of each question-type group,
                      pooled vs per_question at k=5 (spec S7: groups of 500 /
                      404 / 96 are never compared by raw counts).
           Figure 3 - one mark per question, placed by the rank of its
                      worst-ranked gold paragraph before and after reranking, so
                      the four transition classes become four quadrants.
                      Questions whose gold never entered a stage's stored list
                      have no observable rank and are reported as a count, never
                      placed at a made-up one.

AI-USAGE BOUNDARY:
  This is presentation plumbing. It defines no metric, computes no rescue or
  damage classification, and makes no failure-category judgment: every number
  drawn is read verbatim from the two accepted CSVs, so a slide can never drift
  from the artifacts. The derived quantities are display conveniences the specs
  already define: dense_hits / n and rerank_hits / n (aggregate S9.5), and the
  bottleneck (worst-ranked) gold rank of aggregate S8, which the cases file
  supplies per gold.

  OWNERSHIP: captions here stay neutral and mechanically descriptive. They name
  the criterion, the setting, the cutoff, the accepted counts and rates, the
  transition class of a mark, and whether a rank is observable in a stage's
  stored list. The failure-analysis reading -- why a question was rescued or
  damaged, whether a movement is large or small, what the pattern implies --
  belongs to the analysis owner (aggregate spec S10, cases spec S1 / S6) and is
  written in the slide or report layer, never generated here. No derived
  statistic beyond the two rates above is published on a card.

  Both inputs are re-validated against their frozen contracts before anything is
  rendered and before the destination is touched: the aggregate S9.1 columns,
  S9.2 lexemes and domains, S9.3 21-row key set, S9.4 row order, the S9.5
  row-local identities, the S9.2/S7 group partition (`overall` is the exact
  total of `bridge` + `comparison`), and the S7/S2 group size all seven
  combinations share (the 21 rows are seven decompositions of one question set,
  so one `question_type` carries one `n` file-wide); and the cases S5.1
  physical row shape, S5.2 lexemes and example-bound fields, S5.3 gold-rank
  objects (canonical compact serialization, ranks within the stored depth,
  pairwise-distinct non-null ranks, and one object per
  `(stage, setting, example_id)` across the example's `k`
  rows), S5.4 key matrix and row order, S5.5 identities, plus the S5.6 agreement
  with the accepted summary for **all five** `(setting, k)` slices, not only the
  one Figure 3 plots.

  Every physical rule is matched on the raw cell: an integer, a rate, and a `k`
  are matched as text before any conversion can normalise a second spelling into
  legality, a lexeme is never trimmed, and a rank is never accepted past the
  depth the stored list can observe nor repeated across two distinct golds. Two
  figures on one page therefore cannot tell two different stories, rendering the
  same file at two cutoffs cannot produce two readings of one stored list, and a
  partially valid artifact cannot be rendered. Chart-form and color decisions are
  design choices, recorded in the module constants below.

Usage:
    python scripts/reporting/plot_rescue_damage.py
    python scripts/reporting/plot_rescue_damage.py --no-cases
    python scripts/reporting/plot_rescue_damage.py \
        --summary results/rerank_rescue_damage.csv \
        --cases results/rerank_rescue_damage_cases.csv \
        --cases-setting pooled --cases-k 5 \
        --out results/figures/rerank_rescue_damage.html
"""

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.results_schema import STORE_DEPTH_BY_SETTING, TITLE_SEPARATOR

DEFAULT_SUMMARY = os.path.join("results", "rerank_rescue_damage.csv")
DEFAULT_CASES = os.path.join("results", "rerank_rescue_damage_cases.csv")
DEFAULT_OUT = os.path.join("results", "figures", "rerank_rescue_damage.html")

# ── Design parameters ────────────────────────────────────────────────────────
# Two data series (rescue / damage) plus one de-emphasis neutral for the level
# bars of the waterfall. Rescue/damage is a polarity, so it takes the diverging
# blue<->red pair rather than two arbitrary categorical hues.
#
# Validated with the palette validator (adjacent and all-pairs, both modes):
#   light  #2a78d6 / #e34948 / #52514e  - CVD dE 10.4, normal-vision 21.8, all >= 3:1
#   dark   #3987e5 / #e34948 / #898781  - CVD dE  8.7, normal-vision 17.0, all >= 3:1
# The neutral trips the chroma floor by construction: it is the de-emphasis gray
# of the emphasis form, not a categorical slot.
#
# Data marks are drawn at full opacity for the same reason. Figure 3 places one
# mark per question, so marks overlap; a translucent mark would show that stacking
# but drops an isolated mark below the 3:1 mark-contrast floor (light-mode damage
# reaches only 1.83:1 at 0.45 alpha and 3.00:1 at 0.80). Overlap is therefore
# stated in the caption and quantified in the cell table instead of encoded in
# alpha or in a bubble area.
CARD_W, CARD_H = 1280, 720

INK = "var(--text-primary)"
INK2 = "var(--text-secondary)"
MUTED = "var(--text-muted)"
GRID = "var(--grid)"
AXIS = "var(--axis)"
RESCUE = "var(--rescue)"
DAMAGE = "var(--damage)"
LEVEL = "var(--level)"

MINUS = "−"  # true minus, not a hyphen


# ── The frozen summary contract ──────────────────────────────────────────────
# Schema constants restated from the accepted aggregate spec, not logic: S9.1
# columns and order, S9.2 vocabularies and physical lexemes, S9.3 the 7 valid
# (criterion, setting, k) combinations and the 21-row key set, S9.4 the physical
# row order. They are declared here rather than imported from
# scripts/reporting/rescue_damage.py so this renderer stays a stdlib-only reader
# of the finished artifact and cannot reach the counting code that produced it.
SUMMARY_COLUMNS = [
    "criterion", "setting", "k", "question_type", "n",
    "dense_hits", "rerank_hits",
    "stable_miss", "rescues", "damages", "stable_hit",
    "rescue_rate", "damage_rate", "net_count", "net_rate",
    "rescue_given_dense_miss", "damage_given_dense_hit",
]

VALID_SUMMARY_COMBOS = [
    ("full_evidence_recall", "pooled", 2),
    ("full_evidence_recall", "pooled", 5),
    ("full_evidence_recall", "pooled", 10),
    ("full_evidence_recall", "per_question", 2),
    ("full_evidence_recall", "per_question", 5),
    ("any_evidence_recall", "pooled", 5),
    ("any_evidence_recall", "per_question", 5),
]

CRITERIA = ("full_evidence_recall", "any_evidence_recall")
SETTINGS = ("pooled", "per_question")
QUESTION_TYPE_GROUPS = ("overall", "bridge", "comparison")
K_LEXEMES = ("2", "5", "10")

# The exact 21 keys in the exact S9.4 physical order.
SUMMARY_ROW_ORDER = [(criterion, setting, k, question_type)
                     for criterion, setting, k in VALID_SUMMARY_COMBOS
                     for question_type in QUESTION_TYPE_GROUPS]

COUNT_COLUMNS = ["n", "dense_hits", "rerank_hits",
                 "stable_miss", "rescues", "damages", "stable_hit"]

# S9.2 makes `overall` "the whole-group total row", and S7 fixes the three groups
# as overall (N = 500), bridge (404) and comparison (96): bridge and comparison
# partition overall, so every additive column of the `overall` row is the exact
# total of the two part rows. The rate columns are deliberately absent -- a rate
# is not additive, and each row's rates are already reconciled against its own
# counts by S9.5.
PARTITION_COLUMNS = COUNT_COLUMNS + ["net_count"]
RATE_DOMAINS = {"rescue_rate": (0.0, 1.0), "damage_rate": (0.0, 1.0),
                "net_rate": (-1.0, 1.0)}

_PLAIN_INT = re.compile(r"^(0|[1-9][0-9]*)$")
_SIGNED_INT = re.compile(r"^(0|-?[1-9][0-9]*)$")

# Owner decision (DR-009 round 3): S9.2 closes the physical lexeme of a rate the
# same way it closes an integer column, so the raw text of every numeric cell is
# matched before any conversion. `Decimal()` and `float()` both normalise a
# PEP 515 underscore (`0.2_32`) and a fullwidth digit (`０.232`) into a legal
# value, exactly as `int()` normalised `k="02"`, so a second physical spelling of
# a frozen rate would otherwise be accepted silently. Only `net_rate` may carry a
# sign; a leading `+`, an exponent, and a bare `.5` are second spellings too.
_PLAIN_DECIMAL = re.compile(r"^(0|[1-9][0-9]*)(\.[0-9]+)?$")
_SIGNED_DECIMAL = re.compile(r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$")

_ATOL = 1e-9


def _cell(row, column, key, path):
    """A missing or split field means a ragged row, not a readable value."""
    value = row.get(column)
    if value is None:
        raise SystemExit(
            "error: %s: row %r has no %s field (ragged row)" % (path, key, column))
    return value


def _plain_int(cell, column, key, path):
    """S9.2: an integer column is a plain integer, matched on the raw text.

    Only `net_count` may be negative. A padded, signed, float, exponent, or
    boolean spelling refuses rather than being coerced by int().
    """
    pattern = _SIGNED_INT if column == "net_count" else _PLAIN_INT
    if not pattern.match(cell):
        raise SystemExit(
            "error: %s: row %r has %s=%r, which is not the plain integer S9.2 "
            "requires" % (path, key, column, cell))
    return int(cell)


def _domain_float(cell, column, key, path, lo, hi):
    """S9.2: a rate column is a finite decimal inside its closed domain.

    The domain is enforced on the exact decimal before float(), so a
    precision-adjacent spelling such as `1.0000000000000001` cannot be rounded
    into range -- the same rule the input contract applies to the shared schema.

    Surrounding whitespace refuses instead of being trimmed. `Decimal()` accepts
    a padded string, so trimming here would quietly admit a second physical
    spelling of every rate -- and, for a conditional rate, would make a
    whitespace cell indistinguishable from the empty field S9.2 reserves for a
    zero denominator.

    The physical lexeme is matched last, after the value-level complaints, so a
    cell that is not a number at all, is non-finite, or is out of domain still
    reports that more specific diagnosis. The lexeme guard closes exactly what
    those checks normalise: a spelling `Decimal()` accepts and silently rewrites
    into a legal in-domain value.
    """
    if cell != cell.strip():
        raise SystemExit(
            "error: %s: row %r has %s=%r, which is padded with whitespace; S9.2 "
            "fixes the physical lexeme of a rate" % (path, key, column, cell))
    try:
        exact = Decimal(cell)
    except InvalidOperation:
        raise SystemExit(
            "error: %s: row %r has %s=%r, which is not a decimal number"
            % (path, key, column, cell))
    if not exact.is_finite():
        raise SystemExit(
            "error: %s: row %r has a non-finite %s=%r" % (path, key, column, cell))
    if not Decimal(repr(lo)) <= exact <= Decimal(repr(hi)):
        raise SystemExit(
            "error: %s: row %r has %s=%r outside its S9.2 domain [%g, %g]"
            % (path, key, column, cell, lo, hi))
    pattern = _SIGNED_DECIMAL if column == "net_rate" else _PLAIN_DECIMAL
    if not pattern.match(cell):
        raise SystemExit(
            "error: %s: row %r has %s=%r, which is not the plain decimal S9.2 "
            "requires" % (path, key, column, cell))
    value = float(cell)
    if not math.isfinite(value) or not lo <= value <= hi:
        raise SystemExit(
            "error: %s: row %r has %s=%r outside its S9.2 domain [%g, %g]"
            % (path, key, column, cell, lo, hi))
    return value


# ── Reading the frozen artifact ──────────────────────────────────────────────
def load_summary(path):
    """Read the frozen summary and enforce its complete S9 contract.

    Figures 1-2 read this table, so the whole artifact is validated here rather
    than only the rows a figure happens to request: S9.1 columns and order, S9.2
    vocabularies / lexemes / domains, S9.3 the exact 21-key set with no
    duplicate, S9.4 the physical row order, the S9.5 row-local identities, the
    S9.2/S7 group partition across the three rows of one combination, and the
    S7/S2 group size shared by all seven combinations. Every refusal happens
    before a figure is built and therefore before the destination is touched, so
    `--no-cases` is covered by the same boundary.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SUMMARY_COLUMNS:
            raise SystemExit(
                "error: %s does not carry the 17 summary columns in order (S9.1): %r"
                % (path, reader.fieldnames))
        rows = list(reader)
    if not rows:
        raise SystemExit("error: %s has no data rows" % path)

    table, order = {}, []
    for index, row in enumerate(rows, start=1):
        if None in row:
            raise SystemExit(
                "error: %s row %d has more fields than the 17 columns of S9.1"
                % (path, index))
        key = _summary_key(row, index, path)
        if key in table:
            raise SystemExit("error: duplicate summary key %r in %s" % (key, path))
        order.append(key)
        table[key] = _summary_values(row, key, path)

    expected = set(SUMMARY_ROW_ORDER)
    missing = [key for key in SUMMARY_ROW_ORDER if key not in table]
    unexpected = [key for key in order if key not in expected]
    if missing or unexpected:
        raise SystemExit(
            "error: %s is not the exact 21-row key set of S9.3: missing %r, "
            "unexpected %r" % (path, missing, unexpected))
    for index, (actual, wanted) in enumerate(zip(order, SUMMARY_ROW_ORDER), start=1):
        if actual != wanted:
            raise SystemExit(
                "error: %s row %d breaks the S9.4 row order: expected %r, found %r"
                % (path, index, wanted, actual))
    _check_group_partition(table, path)
    _check_group_sizes(table, path)
    return table, rows


def _check_group_sizes(table, path):
    """S7 / S2: one `question_type` has one group size across all seven combos.

    S7 reports "every valid combination" for the same three groups, and S2 binds
    both settings and both methods to the identical example-id set, so the 21
    rows are seven decompositions of one question set rather than seven
    independent tables: `n` for a given `question_type` is one constant for the
    whole file. S5 skips an invalid combination outright; it never recomputes a
    valid one over a subset.

    `_check_group_partition` binds the three rows of one combination to each
    other and stops there. A combination silently counted over fewer questions
    keeps every row-local S9.5 identity and every additive partition intact, yet
    Figure 1 states the pooled N in one caption while printing that
    combination's net as a share of a different denominator, and Figure 2's
    caption names the three group sizes three lines above a table that lists
    others. Binding the combinations to each other is what makes the docstring's
    "two figures on one page cannot tell two different stories" true of the
    denominator as well as of the counts.
    """
    for question_type in QUESTION_TYPE_GROUPS:
        first_combo, first_n = None, None
        for criterion, setting, k in VALID_SUMMARY_COMBOS:
            n = table[(criterion, setting, k, question_type)]["n"]
            if first_combo is None:
                first_combo, first_n = (criterion, setting, k), n
            elif n != first_n:
                raise SystemExit(
                    "error: %s: the %s group holds n=%d in (%s, %s, k=%d) but "
                    "n=%d in (%s, %s, k=%d); S7 reports every valid combination "
                    "over the same questions, so one question_type has one "
                    "group size across the whole file"
                    % (path, question_type, first_n, first_combo[0],
                       first_combo[1], first_combo[2], n, criterion, setting, k))


def _check_group_partition(table, path):
    """S9.2 / S7: `overall` is the exact total of `bridge` + `comparison`.

    Checked across the three `question_type` rows of one `(criterion, setting,
    k)`, which no row-local identity can see. Figure 1 reads `overall` while
    Figure 2 draws all three groups side by side on one card, so a group total
    that is not the sum of its parts is precisely the contradiction the two
    figures must not be able to state -- three bars that cannot all be true.
    """
    for criterion, setting, k in VALID_SUMMARY_COMBOS:
        whole = table[(criterion, setting, k, "overall")]
        bridge = table[(criterion, setting, k, "bridge")]
        comparison = table[(criterion, setting, k, "comparison")]
        for column in PARTITION_COLUMNS:
            total = bridge[column] + comparison[column]
            if whole[column] != total:
                raise SystemExit(
                    "error: %s: the overall row of (%s, %s, k=%d) is not the "
                    "total of its bridge and comparison rows: %s is %d overall, "
                    "but %d + %d = %d in the groups"
                    % (path, criterion, setting, k, column, whole[column],
                       bridge[column], comparison[column], total))


def _summary_key(row, index, path):
    """S9.2 vocabularies and the S9.3 row key, checked on the raw cells."""
    criterion = _cell(row, "criterion", index, path)
    setting = _cell(row, "setting", index, path)
    k = _cell(row, "k", index, path)
    question_type = _cell(row, "question_type", index, path)
    for column, value, vocabulary in (("criterion", criterion, CRITERIA),
                                      ("setting", setting, SETTINGS),
                                      ("k", k, K_LEXEMES),
                                      ("question_type", question_type,
                                       QUESTION_TYPE_GROUPS)):
        if value not in vocabulary:
            raise SystemExit(
                "error: %s row %d has %s=%r, which is outside the S9.2 vocabulary %r"
                % (path, index, column, value, list(vocabulary)))
    return (criterion, setting, int(k), question_type)


def _summary_values(row, key, path):
    """Every cell of one summary row, with the S9.2 types and S9.5 identities."""
    values = {column: _plain_int(_cell(row, column, key, path), column, key, path)
              for column in COUNT_COLUMNS}
    values["net_count"] = _plain_int(
        _cell(row, "net_count", key, path), "net_count", key, path)
    for column, (lo, hi) in RATE_DOMAINS.items():
        values[column] = _domain_float(
            _cell(row, column, key, path), column, key, path, lo, hi)

    # The row's own counts are reconciled first, so a conditional-rate complaint
    # below can never be the downstream symptom of a broken count identity.
    _check_summary_identities(values, key, path)

    # S9.2: a conditional rate is a blank cell exactly on a zero denominator,
    # never a fabricated 0 and never a populated null-like token. "Blank" is the
    # physical empty field, so the raw cell is compared with "" and is never
    # trimmed first: a cell holding a space or a tab is populated, and a
    # populated cell on a zero denominator refuses like any other fabricated
    # value.
    for column, numerator, denominator in (
            ("rescue_given_dense_miss", values["rescues"],
             values["n"] - values["dense_hits"]),
            ("damage_given_dense_hit", values["damages"], values["dense_hits"])):
        cell = _cell(row, column, key, path)
        if denominator == 0:
            if cell != "":
                raise SystemExit(
                    "error: %s: row %r has %s=%r but a zero denominator; S9.2 "
                    "requires a blank cell, which is the empty field and not "
                    "whitespace" % (path, key, column, cell))
            values[column] = None
            continue
        if cell == "":
            raise SystemExit(
                "error: %s: row %r has a blank %s but a denominator of %d"
                % (path, key, column, denominator))
        values[column] = _domain_float(cell, column, key, path, 0.0, 1.0)
        if not math.isclose(values[column], numerator / denominator,
                            rel_tol=0.0, abs_tol=_ATOL):
            raise SystemExit(
                "error: %s: row %r has %s=%r, but its own counts give %r"
                % (path, key, column, values[column], numerator / denominator))

    return values


def _check_summary_identities(values, key, path):
    """The S9.5 identities, so two cards can never state inconsistent numbers."""
    n = values["n"]
    if n <= 0:
        raise SystemExit(
            "error: %s: row %r has n=%d; a reported group holds at least one "
            "question" % (path, key, n))
    for column, expected in (
            ("n", values["stable_miss"] + values["rescues"]
             + values["damages"] + values["stable_hit"]),
            ("dense_hits", values["damages"] + values["stable_hit"]),
            ("rerank_hits", values["rescues"] + values["stable_hit"]),
            ("net_count", values["rescues"] - values["damages"])):
        if values[column] != expected:
            raise SystemExit(
                "error: %s: row %r breaks the S9.5 identity for %s: %d in the "
                "file, %d from its own counts"
                % (path, key, column, values[column], expected))
    for column, numerator in (("rescue_rate", values["rescues"]),
                              ("damage_rate", values["damages"]),
                              ("net_rate", values["net_count"])):
        expected = numerator / n
        if not math.isclose(values[column], expected, rel_tol=0.0, abs_tol=_ATOL):
            raise SystemExit(
                "error: %s: row %r has %s=%r, but its own counts give %r"
                % (path, key, column, values[column], expected))


def pick(table, criterion, setting, k, question_type):
    key = (criterion, setting, k, question_type)
    if key not in table:
        raise SystemExit("error: summary is missing the required row %r" % (key,))
    return table[key]


# ── Reading the per-example cases artifact ───────────────────────────────────
# Contract: docs/specs/2026-08-12-rerank-rescue-damage-cases.md (S5.1 columns,
# S5.3 gold-rank objects, S5.4 row key, S5.5 identities, S5.6 aggregate
# consistency). The plot re-checks them because a figure must not be able to
# disagree with the accepted summary it sits next to.
CASE_COLUMNS = [
    "setting", "example_id", "question_type", "level", "question", "gold_titles",
    "k", "dense_full_at_k", "rerank_full_at_k",
    "dense_gold_ranks", "rerank_gold_ranks", "transition",
]

# Aggregate S2 / cases S5.2: these four are properties of the example, so they
# are identical in all five (setting, k) rows that share an example_id.
EXAMPLE_BOUND_COLUMNS = ("question_type", "level", "question", "gold_titles")

# S5.3: "the ranks are the whole ranked list's ranks and are not cut off at `k`.
# `k` is applied by the reader." The two objects are therefore a property of
# (stage, setting, example_id) -- read from the one `retrieved_titles` cell that
# stage holds for that example -- so the setting's `k` rows all carry the same
# object. Unlike EXAMPLE_BOUND_COLUMNS these are bound per setting, not per
# example: pooled and per_question hold genuinely different stored lists, so one
# example_id legitimately carries different ranks in the two settings.
RANK_BOUND_COLUMNS = ("dense_gold_ranks", "rerank_gold_ranks")

# S5.4 fixes the whole key matrix, not only the rows a figure happens to plot:
# each of the accepted run's 500 examples appears once per valid (setting, k),
# so the artifact is exactly 500 x (3 + 2) = 2500 rows, ordered by
# (setting, example_id, k) with pooled before per_question. This renderer reads
# the frozen artifact, so it enforces that whole matrix before selecting a slice.
CASE_KS_BY_SETTING = {"pooled": (2, 5, 10), "per_question": (2, 5)}
CASE_SETTING_ORDER = ("pooled", "per_question")
EXPECTED_CASE_ROWS = 2500

VALID_CASE_COMBOS = {(setting, k)
                     for setting, ks in CASE_KS_BY_SETTING.items()
                     for k in ks}

TRANSITIONS = {(0, 0): "stable_miss", (0, 1): "rescue",
               (1, 0): "damage", (1, 1): "stable_hit"}


def _full_at_k(ranks, k):
    """Spec S5.3: the cutoff is applied by the reader, not stored in the ranks."""
    return int(all(rank is not None and rank <= k for rank in ranks.values()))


def bottleneck(ranks):
    """Spec S8 of the aggregate contract: the worst-ranked gold, or None.

    The worst gold is the one that decides Full@k. It is observable only when
    every gold appears in that stage's stored list; otherwise it stays None and
    is never inferred as a concrete rank beyond the stored depth.
    """
    values = list(ranks.values())
    if not values or any(value is None for value in values):
        return None
    return max(values)


def _ranks(cell, golds, where, depth):
    """S5.3: every value is null or a rank observable in the stored list.

    `depth` is that setting's stored retrieval depth (`STORE_DEPTH_BY_SETTING`:
    pooled 50, per_question 10). A rank above it cannot have been read from the
    stored list, so it is a fabricated beyond-depth position rather than an
    observation, and null is the only representation the contract allows for a
    gold that never entered the list. Enforcing the ceiling here keeps such a
    value from reaching `bottleneck()` and being drawn as a concrete coordinate.

    The non-null ranks of one object must also be pairwise distinct. S5.3 maps
    each gold to its *first* position in one stored list, and two distinct titles
    occupy distinct positions, so their first occurrences differ: a shared rank
    is not an observation the stored list can produce. Nulls are exempt -- any
    number of golds may be absent from the list.

    Finally the object is compared with its canonical S5.3 serialization
    (compact `,` / `:` separators, gold order preserved, `ensure_ascii=False`).
    `json.loads` normalises `", "` / `": "` padding away exactly as `int()`
    normalised `k="02"`, so the frozen physical spelling is matched on the raw
    cell rather than recovered from the parsed value.
    """
    try:
        ranks = json.loads(cell)
    except ValueError:
        raise SystemExit("error: %s is not valid JSON: %r" % (where, cell))
    if not isinstance(ranks, dict):
        raise SystemExit("error: %s is not a JSON object: %r" % (where, cell))
    if list(ranks.keys()) != golds:
        raise SystemExit(
            "error: %s keys %r are not the row's gold titles %r in order"
            % (where, list(ranks.keys()), golds))
    holder = {}
    for title, rank in ranks.items():
        if rank is None:
            continue
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            raise SystemExit(
                "error: %s has a non-rank value for %r: %r" % (where, title, rank))
        if rank > depth:
            raise SystemExit(
                "error: %s has rank %d for %r, beyond the stored top-%d list; "
                "S5.3 records an absent gold as null, never as a concrete rank "
                "past the storage depth" % (where, rank, title, depth))
        if rank in holder:
            raise SystemExit(
                "error: %s gives %r and %r the same rank %d; S5.3 maps each gold "
                "to its first position in one stored list, so two distinct "
                "titles cannot share one position"
                % (where, holder[rank], title, rank))
        holder[rank] = title
    canonical = json.dumps(ranks, separators=(",", ":"), ensure_ascii=False)
    if canonical != cell:
        raise SystemExit(
            "error: %s is not the compact S5.3 serialization: the cell is %r "
            "where the frozen spelling is %r" % (where, cell, canonical))
    return ranks


def _validate_case_matrix(keys, path):
    """S5.4: the exact 2500-key matrix in the exact physical row order.

    Checked over the whole file, not the requested slice: a renderer that claims
    to re-validate the frozen cases artifact must not accept an incomplete one
    just because the slice it happens to plot is intact.
    """
    if len(keys) != EXPECTED_CASE_ROWS:
        raise SystemExit(
            "error: %s holds %d rows; the frozen cases artifact is exactly %d "
            "(S5.4)" % (path, len(keys), EXPECTED_CASE_ROWS))

    ids = {setting: set() for setting in CASE_SETTING_ORDER}
    for setting, example_id, _ in keys:
        ids[setting].add(example_id)
    if ids["pooled"] != ids["per_question"]:
        raise SystemExit(
            "error: %s does not cover the same example ids in both settings "
            "(S5.4): pooled only %r, per_question only %r"
            % (path, sorted(ids["pooled"] - ids["per_question"])[:3],
               sorted(ids["per_question"] - ids["pooled"])[:3]))

    expected = [(setting, example_id, k)
                for setting in CASE_SETTING_ORDER
                for example_id in sorted(ids[setting])
                for k in CASE_KS_BY_SETTING[setting]]
    if set(keys) != set(expected):
        raise SystemExit(
            "error: %s is not the complete (setting, example_id, k) matrix of "
            "S5.4: missing %r, unexpected %r"
            % (path, sorted(set(expected) - set(keys))[:3],
               sorted(set(keys) - set(expected))[:3]))
    for index, (actual, wanted) in enumerate(zip(keys, expected), start=1):
        if actual != wanted:
            raise SystemExit(
                "error: %s row %d breaks the S5.4 row order: expected %r, found %r"
                % (path, index, wanted, actual))


def load_cases(path):
    """Read and re-validate the per-example cases artifact."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CASE_COLUMNS:
            raise SystemExit(
                "error: %s does not carry the 12 case columns in order: %r"
                % (path, reader.fieldnames))
        raw = list(reader)
    if not raw:
        raise SystemExit("error: %s has no data rows" % path)

    cases = []
    seen = set()
    keys = []
    metadata = {}
    ranks_by_example = {}
    for index, row in enumerate(raw, start=1):
        # S5.1 freezes 12 columns, so a data row that is not 12 fields wide is
        # not the frozen artifact. csv.DictReader buckets a 13th field under the
        # None key and pads a short row with None, so both directions are caught
        # before any cell is read: a later key-matrix check cannot recover the
        # physical shape that was silently discarded here.
        if None in row:
            raise SystemExit(
                "error: %s row %d has more fields than the 12 columns of S5.1"
                % (path, index))
        for column in CASE_COLUMNS:
            if row.get(column) is None:
                raise SystemExit(
                    "error: %s row %d has no %s field (ragged row)"
                    % (path, index, column))

        setting = row["setting"]
        # S5.2: `k` is written as a plain integer from the closed set, so the
        # raw lexeme is matched before int() can normalise `02`, `+2`, `2.0`, or
        # a padded spelling into a legal-looking key.
        if row["k"] not in K_LEXEMES:
            raise SystemExit(
                "error: %s row %d has k=%r, which is not one of the plain "
                "integers S5.2 requires: %r"
                % (path, index, row["k"], list(K_LEXEMES)))
        k = int(row["k"])
        if (setting, k) not in VALID_CASE_COMBOS:
            raise SystemExit(
                "error: %s holds the invalid combination (%s, k=%d)"
                % (path, setting, k))

        key = (setting, row["example_id"], k)
        if key in seen:
            raise SystemExit("error: duplicate case key %r in %s" % (key, path))
        seen.add(key)
        keys.append(key)

        dense = row["dense_full_at_k"]
        rerank = row["rerank_full_at_k"]
        if dense not in ("0", "1") or rerank not in ("0", "1"):
            raise SystemExit(
                "error: case %r has non-binary hit cells (%r, %r)"
                % (key, dense, rerank))
        dense, rerank = int(dense), int(rerank)

        golds = row["gold_titles"].split(TITLE_SEPARATOR)
        if not golds or any(title == "" for title in golds):
            raise SystemExit("error: case %r has an empty gold title" % (key,))
        depth = STORE_DEPTH_BY_SETTING[setting]
        dense_ranks = _ranks(row["dense_gold_ranks"], golds,
                             "dense_gold_ranks of %r" % (key,), depth)
        rerank_ranks = _ranks(row["rerank_gold_ranks"], golds,
                              "rerank_gold_ranks of %r" % (key,), depth)

        # Aggregate spec S2 binds question_type / level / question / gold_titles
        # to the example, not to a method, setting, or cutoff, and cases S5.2
        # copies them verbatim from that joined input. All five rows of one
        # example_id therefore carry identical values, and drift means one
        # logical question has two identities -- which cutoff Figure 3 plots
        # would decide which one the page shows.
        identity = tuple(row[column] for column in EXAMPLE_BOUND_COLUMNS)
        first_key, first_identity = metadata.setdefault(
            row["example_id"], (key, identity))
        if identity != first_identity:
            column, mine, theirs = next(
                triple for triple
                in zip(EXAMPLE_BOUND_COLUMNS, identity, first_identity)
                if triple[1] != triple[2])
            raise SystemExit(
                "error: %s: example %r has %s=%r at %r but %r at %r; S5.2 copies "
                "the example-bound fields verbatim, so every row of one example "
                "carries the same value"
                % (path, row["example_id"], column, mine, key, theirs, first_key))

        if _full_at_k(dense_ranks, k) != dense or _full_at_k(rerank_ranks, k) != rerank:
            raise SystemExit(
                "error: case %r stores ranks that imply a different Full@%d than "
                "its hit cells" % (key, k))
        if TRANSITIONS[(dense, rerank)] != row["transition"]:
            raise SystemExit(
                "error: case %r has transition %r but hit cells (%d, %d)"
                % (key, row["transition"], dense, rerank))

        # The row's own identities are reconciled first, so this cross-row
        # complaint can never be the downstream symptom of a broken row. S5.3
        # keeps the ranks uncut by `k`, so all `k` rows of one (setting,
        # example_id) read the same stored list and must carry the same object.
        # The comparison is on the raw cell, which pins the S5.3 serialization
        # for every row of the example as well: without it one example can hold
        # two contradictory readings of one stored list, and rendering the same
        # file at two cutoffs states two different worst-gold ranks.
        for column in RANK_BOUND_COLUMNS:
            first_ranks_key, first_cell = ranks_by_example.setdefault(
                (setting, row["example_id"], column), (key, row[column]))
            if row[column] != first_cell:
                raise SystemExit(
                    "error: %s: example %r has %s=%s at %r but %s at %r; S5.3 "
                    "ranks are the whole stored list's ranks and are not cut off "
                    "at k, so every k row of one (setting, example) carries the "
                    "same object"
                    % (path, row["example_id"], column, row[column], key,
                       first_cell, first_ranks_key))

        cases.append({
            "setting": setting,
            "k": k,
            "example_id": row["example_id"],
            "question_type": row["question_type"],
            "level": row["level"],
            "question": row["question"],
            "transition": row["transition"],
            "dense_bottleneck": bottleneck(dense_ranks),
            "rerank_bottleneck": bottleneck(rerank_ranks),
        })
    _validate_case_matrix(keys, path)
    return cases


def select_cases(cases, setting, k):
    chosen = [case for case in cases
              if case["setting"] == setting and case["k"] == k]
    if not chosen:
        raise SystemExit(
            "error: the cases file has no rows for (%s, k=%d)" % (setting, k))
    return chosen


def cross_check_all_cases(cases, table):
    """Spec S5.6 over the whole file, not the slice Figure 3 happens to plot.

    S5.6 binds every `(setting, k)` and every `question_type` group, so a file
    that aggregates back for one combination and not the other four is not the
    frozen artifact -- and whether it is accepted must not depend on which cutoff
    the operator renders. The 15 Full Evidence rows this needs are already in the
    validated 21-row table, and the walk happens before slice selection and
    before the destination is touched. This is the S5.4 principle of
    `_validate_case_matrix` applied to the aggregate agreement.
    """
    for setting in CASE_SETTING_ORDER:
        for k in CASE_KS_BY_SETTING[setting]:
            cross_check_cases(select_cases(cases, setting, k), table, setting, k)


def cross_check_cases(chosen, table, setting, k):
    """Spec S5.6: counting one slice must reproduce the accepted summary."""
    for question_type in ("overall", "bridge", "comparison"):
        group = [case for case in chosen
                 if question_type == "overall"
                 or case["question_type"] == question_type]
        expected = pick(table, "full_evidence_recall", setting, k, question_type)
        counts = Counter(case["transition"] for case in group)
        actual = {
            "n": len(group),
            "rescues": counts["rescue"],
            "damages": counts["damage"],
            "stable_hit": counts["stable_hit"],
            "stable_miss": counts["stable_miss"],
            "dense_hits": counts["damage"] + counts["stable_hit"],
            "rerank_hits": counts["rescue"] + counts["stable_hit"],
        }
        for field, value in actual.items():
            if value != expected[field]:
                raise SystemExit(
                    "error: the cases file disagrees with the accepted summary at "
                    "(%s, k=%d, %s): %s is %d in the cases and %d in the summary"
                    % (setting, k, question_type, field, value, expected[field]))


# ── Formatting ───────────────────────────────────────────────────────────────
def pct(value, digits=1):
    return "%.*f%%" % (digits, value * 100.0)


def pct_opt(value, digits=1):
    """A zero-denominator conditional rate stays blank; it is never shown as 0%."""
    return "n/a" if value is None else pct(value, digits)


def pp(value, digits=1):
    return "%+.*f pp" % (digits, value * 100.0)


def signed(count):
    return ("+%d" % count) if count >= 0 else (MINUS + "%d" % abs(count))


# ── SVG primitives ───────────────────────────────────────────────────────────
def bar_path(x, y, w, h, round_side, r=4.0):
    """A bar with a 4px rounded data-end and a square baseline end."""
    r = max(0.0, min(r, w / 2.0, h))
    if round_side == "top":
        return (
            "M{x:.1f},{b:.1f} L{x:.1f},{ty:.1f} Q{x:.1f},{y:.1f} {xr:.1f},{y:.1f} "
            "L{xw_r:.1f},{y:.1f} Q{xw:.1f},{y:.1f} {xw:.1f},{ty:.1f} "
            "L{xw:.1f},{b:.1f} Z"
        ).format(x=x, y=y, b=y + h, ty=y + r, xr=x + r, xw=x + w, xw_r=x + w - r)
    return (
        "M{x:.1f},{y:.1f} L{xw:.1f},{y:.1f} L{xw:.1f},{by_r:.1f} "
        "Q{xw:.1f},{b:.1f} {xw_r:.1f},{b:.1f} L{xr:.1f},{b:.1f} "
        "Q{x:.1f},{b:.1f} {x:.1f},{by_r:.1f} Z"
    ).format(x=x, y=y, b=y + h, by_r=y + h - r, xr=x + r, xw=x + w, xw_r=x + w - r)


def hbar_path(x, y, w, h, round_side, r=4.0):
    """A horizontal bar; the rounded end is 'left' or 'right'."""
    r = max(0.0, min(r, h / 2.0, w))
    if round_side == "right":
        return (
            "M{x:.1f},{y:.1f} L{xw_r:.1f},{y:.1f} Q{xw:.1f},{y:.1f} {xw:.1f},{yr:.1f} "
            "L{xw:.1f},{yh_r:.1f} Q{xw:.1f},{yh:.1f} {xw_r:.1f},{yh:.1f} "
            "L{x:.1f},{yh:.1f} Z"
        ).format(x=x, y=y, yr=y + r, yh=y + h, yh_r=y + h - r, xw=x + w, xw_r=x + w - r)
    return (
        "M{xw:.1f},{y:.1f} L{xr:.1f},{y:.1f} Q{x:.1f},{y:.1f} {x:.1f},{yr:.1f} "
        "L{x:.1f},{yh_r:.1f} Q{x:.1f},{yh:.1f} {xr:.1f},{yh:.1f} "
        "L{xw:.1f},{yh:.1f} Z"
    ).format(x=x, y=y, yr=y + r, yh=y + h, yh_r=y + h - r, xr=x + r, xw=x + w)


def text(x, y, body, *, size=14, fill=INK2, anchor="start", weight=400, extra=""):
    return (
        '<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
        'text-anchor="{anchor}" font-weight="{weight}"{extra}>{body}</text>'
    ).format(
        x=x, y=y, size=size, fill=fill, anchor=anchor, weight=weight,
        extra=extra, body=escape(body),
    )


def line(x1, y1, x2, y2, stroke=GRID, width=1.0, extra=""):
    return (
        '<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        'stroke="{stroke}" stroke-width="{w}"{extra} />'
    ).format(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, w=width, extra=extra)


def mark(path, fill, tip):
    """A data mark: hover target carries its own tooltip text."""
    return '<path d="{d}" fill="{fill}" class="mark" data-tip="{tip}" />'.format(
        d=path, fill=fill, tip=escape(tip)
    )


def legend(x, y, items):
    """Identity never rests on color alone: every chart with 2+ series has this."""
    out = []
    cursor = x
    for color, label in items:
        out.append(
            '<rect x="{x:.1f}" y="{y:.1f}" width="12" height="12" rx="3" '
            'fill="{c}" />'.format(x=cursor, y=y - 10, c=color)
        )
        out.append(text(cursor + 20, y, label, size=14, fill=INK2))
        cursor += 20 + 7.4 * len(label) + 32
    return "".join(out)


# ── Figure 1: the pooled Full@5 decomposition + every cutoff ─────────────────
def figure_one(table):
    p2 = pick(table, "full_evidence_recall", "pooled", 2, "overall")
    p5 = pick(table, "full_evidence_recall", "pooled", 5, "overall")
    p10 = pick(table, "full_evidence_recall", "pooled", 10, "overall")

    svg = ['<svg viewBox="0 0 %d %d" role="img" aria-label="%s">' % (
        CARD_W, CARD_H,
        escape(
            "Waterfall: pooled Full Evidence Recall@5 rises from %d to %d hits via "
            "%d rescues and %d damages; beside it, rescues versus damages at k=2, 5 and 10."
            % (p5["dense_hits"], p5["rerank_hits"], p5["rescues"], p5["damages"])
        ),
    )]

    svg.append(text(
        56, 74,
        "Reranking rescued %d questions and broke %d" % (p5["rescues"], p5["damages"]),
        size=32, fill=INK, weight=600,
    ))
    svg.append(text(
        56, 106,
        "Pooled setting, Full Evidence Recall@5 — a hit means both gold paragraphs "
        "land in the top 5. N = %d questions." % p5["n"],
        size=16, fill=INK2,
    ))
    svg.append(legend(56, 146, [
        (RESCUE, "Rescues (dense miss → rerank hit)"),
        (DAMAGE, "Damages (dense hit → rerank miss)"),
        (LEVEL, "Questions hit"),
    ]))

    # ── Panel A: waterfall ──
    ax0, ax1 = 100.0, 412.0
    base_y, top_y = 588.0, 214.0
    y_max = 400.0
    scale = (base_y - top_y) / y_max

    def ay(value):
        return base_y - value * scale

    svg.append(text(56, 192, "Where the +%s comes from" % pp(p5["net_rate"]).lstrip("+"),
                    size=18, fill=INK, weight=600))

    for tick in (0, 100, 200, 300, 400):
        svg.append(line(ax0, ay(tick), ax1, ay(tick)))
        svg.append(text(ax0 - 10, ay(tick) + 5, "%d" % tick, size=12, fill=MUTED,
                        anchor="end", extra=' font-variant-numeric="tabular-nums"'))
    svg.append(line(ax0, base_y, ax1, base_y, stroke=AXIS))

    band = (ax1 - ax0) / 4.0
    centers = [ax0 + band * (i + 0.5) for i in range(4)]
    bw = 24.0
    start, end = float(p5["dense_hits"]), float(p5["rerank_hits"])
    peak = start + p5["rescues"]

    steps = [
        (centers[0], ay(start), base_y - ay(start), LEVEL, "top", "Dense",
         "%d of %d dense hits (%s)" % (p5["dense_hits"], p5["n"], pct(p5["dense_hits"] / p5["n"]))),
        (centers[1], ay(peak), ay(start) - ay(peak), RESCUE, "top", "Rescues",
         "%d rescues — %s of all questions, and %s of the %d the dense stage missed"
         % (p5["rescues"], pct(p5["rescue_rate"]), pct_opt(p5["rescue_given_dense_miss"]),
            p5["n"] - p5["dense_hits"])),
        (centers[2], ay(peak), ay(end) - ay(peak), DAMAGE, "bottom", "Damages",
         "%d damages — %s of all questions, and %s of the %d the dense stage already had"
         % (p5["damages"], pct(p5["damage_rate"]), pct_opt(p5["damage_given_dense_hit"]),
            p5["dense_hits"])),
        (centers[3], ay(end), base_y - ay(end), LEVEL, "top", "Rerank",
         "%d of %d rerank hits (%s)" % (p5["rerank_hits"], p5["n"], pct(p5["rerank_hits"] / p5["n"]))),
    ]

    # Connectors first, so the marks sit on top of them.
    for (cx_a, _, _, _, _, _, _), (cx_b, _, _, _, _, _, _), level in (
        (steps[0], steps[1], ay(start)),
        (steps[1], steps[2], ay(peak)),
        (steps[2], steps[3], ay(end)),
    ):
        svg.append(line(cx_a + bw / 2.0 + 2, level, cx_b - bw / 2.0 - 2, level, stroke=AXIS))

    for cx, y, h, color, side, label, tip in steps:
        svg.append(mark(bar_path(cx - bw / 2.0, y, bw, h, side), color, tip))
        svg.append(text(cx, base_y + 22, label, size=13, fill=INK2, anchor="middle"))

    svg.append(text(centers[0], ay(start) - 30, pct(p5["dense_hits"] / p5["n"]),
                    size=13, fill=MUTED, anchor="middle"))
    svg.append(text(centers[0], ay(start) - 12, "%d" % p5["dense_hits"],
                    size=17, fill=INK, anchor="middle", weight=600))
    svg.append(text(centers[1], ay(peak) - 12, signed(p5["rescues"]),
                    size=17, fill=INK, anchor="middle", weight=600))
    svg.append(text(centers[2], ay(end) + 20, signed(-p5["damages"]),
                    size=17, fill=INK, anchor="middle", weight=600))
    svg.append(text(centers[3], ay(end) - 30, pct(p5["rerank_hits"] / p5["n"]),
                    size=13, fill=MUTED, anchor="middle"))
    svg.append(text(centers[3], ay(end) - 12, "%d" % p5["rerank_hits"],
                    size=17, fill=INK, anchor="middle", weight=600))

    # ── Panel B: symmetric rescue/damage arms at every cutoff ──
    svg.append(text(470, 192, "Same story at every cutoff (pooled, Full)",
                    size=18, fill=INK, weight=600))

    cx = 897.0
    half = 280.0
    b_max = 120.0
    bscale = half / b_max
    rows = [(2, p2), (5, p5), (10, p10)]
    row_y = [316.0, 424.0, 532.0]
    rh = 24.0
    b_top, b_bottom = 250.0, 588.0

    svg.append(line(cx, b_top, cx, b_bottom, stroke=AXIS))
    for tick in (50, 100):
        for sign in (-1, 1):
            tx = cx + sign * tick * bscale
            svg.append(line(tx, b_top, tx, b_bottom))
    for sign, ticks in ((-1, (100, 50)), (1, (50, 100))):
        for tick in ticks:
            svg.append(text(cx + sign * tick * bscale, 610, "%d" % tick, size=12,
                            fill=MUTED, anchor="middle",
                            extra=' font-variant-numeric="tabular-nums"'))
    svg.append(text(cx, 610, "0", size=12, fill=MUTED, anchor="middle"))
    svg.append(text(cx - 12, 636, "← damages", size=13, fill=MUTED, anchor="end"))
    svg.append(text(cx + 12, 636, "rescues →", size=13, fill=MUTED))

    for (k, row), ry in zip(rows, row_y):
        top = ry - rh / 2.0
        rw = row["rescues"] * bscale
        dw = row["damages"] * bscale
        svg.append(mark(
            hbar_path(cx + 2, top, rw, rh, "right"), RESCUE,
            "Full@%d — %d rescues (%s of all; %s of the %d dense missed)"
            % (k, row["rescues"], pct(row["rescue_rate"]),
               pct_opt(row["rescue_given_dense_miss"]), row["n"] - row["dense_hits"]),
        ))
        svg.append(mark(
            hbar_path(cx - 2 - dw, top, dw, rh, "left"), DAMAGE,
            "Full@%d — %d damages (%s of all; %s of the %d dense already had)"
            % (k, row["damages"], pct(row["damage_rate"]),
               pct_opt(row["damage_given_dense_hit"]), row["dense_hits"]),
        ))
        svg.append(text(cx + 2 + rw + 10, ry + 6, "%d" % row["rescues"],
                        size=17, fill=INK, weight=600))
        svg.append(text(cx - 2 - dw - 10, ry + 6, "%d" % row["damages"],
                        size=17, fill=INK, anchor="end"))
        svg.append(text(470, ry - 2, "Full@%d" % k, size=17, fill=INK, weight=600))
        svg.append(text(470, ry + 18, "net %s  (%s)" % (signed(row["net_count"]),
                                                        pp(row["net_rate"])),
                        size=13, fill=MUTED))

    svg.append(line(56, 660, 1224, 660, stroke=GRID))
    svg.append(text(
        56, 684,
        "rescue = dense miss → rerank hit   ·   damage = dense hit → rerank miss"
        "   ·   net = rescues − damages = (rerank hits − dense hits)",
        size=13, fill=MUTED,
    ))
    svg.append(text(56, 704, "Source: results/rerank_rescue_damage.csv", size=13, fill=MUTED))
    svg.append("</svg>")
    return "".join(svg)


# ── Figure 2: who pays the cost ──────────────────────────────────────────────
def figure_two(table):
    groups = ["overall", "bridge", "comparison"]
    settings = [
        ("pooled", "Pooled corpus (dense top-50 shortlist reranked)"),
        ("per_question", "Per-question corpus (the question's own ~10 paragraphs)"),
    ]
    any_pooled = pick(table, "any_evidence_recall", "pooled", 5, "overall")
    any_pq = pick(table, "any_evidence_recall", "per_question", 5, "overall")
    pooled5 = pick(table, "full_evidence_recall", "pooled", 5, "overall")
    pq5 = pick(table, "full_evidence_recall", "per_question", 5, "overall")

    svg = ['<svg viewBox="0 0 %d %d" role="img" aria-label="%s">' % (
        CARD_W, CARD_H,
        escape(
            "Rescue and damage rates at k=5 by question type, pooled versus "
            "per-question setting. Overall, the pooled setting rescues %s and "
            "damages %s of its questions; the per-question setting rescues %s and "
            "damages %s."
            % (pct(pooled5["rescue_rate"]), pct(pooled5["damage_rate"]),
               pct(pq5["rescue_rate"]), pct(pq5["damage_rate"]))
        ),
    )]

    svg.append(text(56, 74, "Rescue and damage rates by question type and setting",
                    size=32, fill=INK, weight=600))
    svg.append(text(
        56, 106,
        "Full Evidence Recall@5 — rescues and damages as a share of each "
        "question-type group.",
        size=16, fill=INK2,
    ))
    svg.append(text(
        56, 130,
        "Overall n = %d, bridge n = %d, comparison n = %d, so groups are compared "
        "by rate and never by raw count."
        % (pick(table, "full_evidence_recall", "pooled", 5, "overall")["n"],
           pick(table, "full_evidence_recall", "pooled", 5, "bridge")["n"],
           pick(table, "full_evidence_recall", "pooled", 5, "comparison")["n"]),
        size=16, fill=INK2,
    ))
    svg.append(legend(56, 172, [
        (RESCUE, "Rescue rate"),
        (DAMAGE, "Damage rate"),
    ]))

    row_y = [318.0, 408.0, 498.0]
    rh = 24.0
    half = 250.0
    r_max = 0.25
    scale = half / r_max
    panels = [(160.0, 660.0), (724.0, 1224.0)]
    p_top, p_bottom = 274.0, 542.0

    for group, ry in zip(groups, row_y):
        svg.append(text(56, ry - 2, group.capitalize(), size=17, fill=INK, weight=600))
        svg.append(text(56, ry + 18, "n = %d"
                        % pick(table, "full_evidence_recall", "pooled", 5, group)["n"],
                        size=13, fill=MUTED))

    for (setting, label), (px0, px1) in zip(settings, panels):
        cx = (px0 + px1) / 2.0
        svg.append(text(px0, 226, label, size=17, fill=INK, weight=600))
        svg.append(line(cx, p_top, cx, p_bottom, stroke=AXIS))
        for tick in (10, 20):
            for sign in (-1, 1):
                tx = cx + sign * (tick / 100.0) * scale
                svg.append(line(tx, p_top, tx, p_bottom))
        for sign, ticks in ((-1, (20, 10)), (1, (10, 20))):
            for tick in ticks:
                svg.append(text(cx + sign * (tick / 100.0) * scale, 564, "%d%%" % tick,
                                size=12, fill=MUTED, anchor="middle"))
        svg.append(text(cx, 564, "0", size=12, fill=MUTED, anchor="middle"))
        svg.append(text(cx - 12, 590, "← damaged", size=13, fill=MUTED, anchor="end"))
        svg.append(text(cx + 12, 590, "rescued →", size=13, fill=MUTED))

        for group, ry in zip(groups, row_y):
            row = pick(table, "full_evidence_recall", setting, 5, group)
            top = ry - rh / 2.0
            rw = row["rescue_rate"] * scale
            dw = row["damage_rate"] * scale
            svg.append(mark(
                hbar_path(cx + 2, top, rw, rh, "right"), RESCUE,
                "%s / %s — %d rescues, %s of the group's %d questions"
                % (setting, group, row["rescues"], pct(row["rescue_rate"]), row["n"]),
            ))
            svg.append(mark(
                hbar_path(cx - 2 - dw, top, dw, rh, "left"), DAMAGE,
                "%s / %s — %d damages, %s of the group's %d questions"
                % (setting, group, row["damages"], pct(row["damage_rate"]), row["n"]),
            ))
            svg.append(text(cx + 2 + rw + 10, ry + 6, pct(row["rescue_rate"]),
                            size=16, fill=INK, weight=600))
            svg.append(text(cx - 2 - dw - 10, ry + 6, pct(row["damage_rate"]),
                            size=16, fill=INK, anchor="end"))
            svg.append(text(cx + 2 + rw + 10, ry + 24, "net %s" % pp(row["net_rate"]),
                            size=12, fill=MUTED))

    svg.append(line(56, 620, 1224, 620, stroke=GRID))
    svg.append(text(
        56, 646,
        "Diagnostic, Any Evidence Recall@5 (at least one gold paragraph): pooled "
        "%d rescues / %d damages, per-question %d / %d. Any and Full are never added."
        % (any_pooled["rescues"], any_pooled["damages"], any_pq["rescues"], any_pq["damages"]),
        size=14, fill=INK2,
    ))
    svg.append(text(
        56, 672,
        "Conditional view at k=5: of the questions the dense stage missed, reranking "
        "recovered %s pooled vs %s per-question; of those it already had, reranking "
        "broke %s vs %s."
        % (pct_opt(pooled5["rescue_given_dense_miss"]), pct_opt(pq5["rescue_given_dense_miss"]),
           pct_opt(pooled5["damage_given_dense_hit"]), pct_opt(pq5["damage_given_dense_hit"])),
        size=14, fill=INK2,
    ))
    svg.append(text(56, 704, "Source: results/rerank_rescue_damage.csv", size=13, fill=MUTED))
    svg.append("</svg>")
    return "".join(svg)


# ── Figure 3: what moved, in rank space ──────────────────────────────────────
def wrap(body, width):
    """Greedy wrap; SVG has no flow text, so lines are measured here."""
    lines = []
    current = ""
    for word in body.split():
        candidate = word if current == "" else current + " " + word
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def case_counts(chosen, setting):
    """Every number Figure 3 states: counts read from the cases file.

    Nothing here is a derived statistic about the *size* of a movement (no
    range, median, or near-cutoff tally). Those readings belong to the analysis
    owner, so the card publishes only class counts, the observable/not-observable
    split, and which stage's stored list lacks a gold (aggregate S8, cases S5.3).
    """
    observable, unobservable = [], []
    for case in chosen:
        seen = (case["dense_bottleneck"] is not None
                and case["rerank_bottleneck"] is not None)
        (observable if seen else unobservable).append(case)
    return {
        "depth": STORE_DEPTH_BY_SETTING[setting],
        "n": len(chosen),
        "counts": Counter(case["transition"] for case in chosen),
        "observable": observable,
        "unobservable": len(unobservable),
        "dense_only_null": sum(1 for case in unobservable
                               if case["dense_bottleneck"] is None
                               and case["rerank_bottleneck"] is not None),
        "rerank_only_null": sum(1 for case in unobservable
                                if case["rerank_bottleneck"] is None
                                and case["dense_bottleneck"] is not None),
        "both_null": sum(1 for case in unobservable
                         if case["dense_bottleneck"] is None
                         and case["rerank_bottleneck"] is None),
    }


# One mark per question, so overlapping marks stay separate elements. Unchanged
# classes are drawn first purely so the two changed classes are not hidden under
# them; the order is otherwise fully determined by the row key.
MARK_DRAW_ORDER = {"stable_hit": 0, "stable_miss": 1, "damage": 2, "rescue": 3}


def figure_three(chosen, table, setting, k):
    stats = case_counts(chosen, setting)
    counts = stats["counts"]
    depth = stats["depth"]
    observable = stats["observable"]

    svg = ['<svg viewBox="0 0 %d %d" role="img" aria-label="%s">' % (
        CARD_W, CARD_H,
        escape(
            "Scatter of the rank of each question's worst-ranked gold paragraph "
            "before and after reranking, one mark per question: %d rescued, %d "
            "damaged, %d hit in both stages, %d missed in both. %d of the %d "
            "questions have no observable rank in at least one stage and carry no "
            "mark."
            % (counts["rescue"], counts["damage"], counts["stable_hit"],
               counts["stable_miss"], stats["unobservable"], stats["n"])
        ),
    )]

    svg.append(text(56, 74, "Worst-ranked gold paragraph before and after reranking",
                    size=30, fill=INK, weight=600))
    svg.append(text(
        56, 106,
        "%s setting, Full Evidence Recall@%d. One mark per question; marks overlap "
        "where questions share a rank pair."
        % (setting.replace("_", "-").capitalize(), k),
        size=16, fill=INK2,
    ))
    svg.append(text(
        56, 130,
        "Position is the rank of the question's worst-ranked gold paragraph — the "
        "one that decides Full@%d. On the diagonal the rank is unchanged." % k,
        size=16, fill=INK2,
    ))
    svg.append(legend(56, 172, [
        (RESCUE, "Rescued"),
        (DAMAGE, "Damaged"),
        (LEVEL, "Stable hit"),
    ]))
    svg.append('<circle cx="654" cy="167.5" r="5.5" fill="none" stroke="%s" '
               'stroke-width="2" />' % LEVEL)
    svg.append(text(668, 172, "Stable miss", size=14, fill=INK2))

    # ── Panel A: the rank-space scatter ──
    x0, x1 = 148.0, 548.0
    y0, y1 = 210.0, 610.0
    ranks = [c["dense_bottleneck"] for c in observable]
    ranks += [c["rerank_bottleneck"] for c in observable]
    lo, hi = 1.4, max(ranks + [depth]) * 1.12
    span = math.log(hi) - math.log(lo)

    def frac(value):
        return (math.log(value) - math.log(lo)) / span

    def px(value):
        return x0 + frac(value) * (x1 - x0)

    def py(value):
        return y1 - frac(value) * (y1 - y0)

    # The cutoff sits between k and k+1, so a rank of exactly k reads as a hit.
    cut = math.sqrt(k * (k + 1))
    cut_x, cut_y = px(cut), py(cut)

    svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
               'opacity="0.07" />' % (cut_x, cut_y, x1 - cut_x, y1 - cut_y, RESCUE))
    svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
               'opacity="0.07" />' % (x0, y0, cut_x - x0, cut_y - y0, DAMAGE))

    for tick in (2, 3, 5, 10, 20, 50):
        if not lo < tick <= hi:
            continue
        svg.append(line(px(tick), y0, px(tick), y1))
        svg.append(line(x0, py(tick), x1, py(tick)))
        svg.append(text(px(tick), y1 + 20, "%d" % tick, size=12, fill=MUTED,
                        anchor="middle"))
        svg.append(text(x0 - 10, py(tick) + 4, "%d" % tick, size=12, fill=MUTED,
                        anchor="end"))

    svg.append(line(x0, y1, x1, y1, stroke=AXIS))
    svg.append(line(x0, y0, x0, y1, stroke=AXIS))
    svg.append(line(x0, y1, x1, y0, stroke=AXIS))
    svg.append(line(cut_x, y0, cut_x, y1, stroke=AXIS))
    svg.append(line(x0, cut_y, x1, cut_y, stroke=AXIS))

    # Quadrant labels name the transition class of the region only. They carry no
    # count, because a question with an unobservable rank in either stage has no
    # mark, so a quadrant is not the class total.
    svg.append(text(x1, y1 - 10, "rescued", size=13, fill=INK2, anchor="end"))
    svg.append(text(x0 + 8, y0 + 16, "damaged", size=13, fill=INK2))
    svg.append(text(x1 - 4, y0 + 16, "stable miss", size=13, fill=MUTED,
                    anchor="end"))
    svg.append(text(x0 + 8, y1 - 10, "stable hit", size=13, fill=MUTED))
    svg.append(text(cut_x, y0 - 8, "top-%d cutoff" % k, size=12, fill=MUTED,
                    anchor="middle"))
    svg.append(text((x0 + x1) / 2.0, y1 + 44,
                    "worst gold rank — dense stage (log scale)",
                    size=13, fill=MUTED, anchor="middle"))
    svg.append(text(112, (y0 + y1) / 2.0,
                    "worst gold rank — after reranking",
                    size=13, fill=MUTED, anchor="middle",
                    extra=' transform="rotate(-90 112 %.1f)"' % ((y0 + y1) / 2.0)))

    # One data mark per observable question, never an aggregated bubble: the
    # cardinality of this layer is exactly the number of questions with an
    # observable worst-gold rank in both stages. Radius and opacity are constant,
    # so a mark encodes nothing but its own (before, after) rank pair and every
    # mark keeps the validated palette contrast. Questions sharing a pair overlap;
    # the caption says so and the cell table below carries the exact counts.
    for case in sorted(observable,
                       key=lambda item: (MARK_DRAW_ORDER[item["transition"]],
                                         item["dense_bottleneck"],
                                         item["rerank_bottleneck"],
                                         item["example_id"])):
        transition = case["transition"]
        dense_rank = case["dense_bottleneck"]
        rerank_rank = case["rerank_bottleneck"]
        fill = {"rescue": RESCUE, "damage": DAMAGE,
                "stable_hit": LEVEL, "stable_miss": "none"}[transition]
        stroke = LEVEL if transition == "stable_miss" else "none"
        svg.append(
            '<circle class="mark" cx="%.1f" cy="%.1f" r="4.0" fill="%s" '
            'stroke="%s" stroke-width="2" data-tip="%s" />'
            % (px(dense_rank), py(rerank_rank), fill, stroke,
               escape("%s — %s: worst gold at rank %d before, %d after"
                      % (transition.replace("_", " "), case["example_id"],
                         dense_rank, rerank_rank))))

    # ── Right column: the counted classes ──
    rx = 620.0
    blocks = [
        (RESCUE, "%d rescued" % counts["rescue"], "Dense miss → rerank hit."),
        (DAMAGE, "%d damaged" % counts["damage"], "Dense hit → rerank miss."),
        (LEVEL, "%d stable hit" % counts["stable_hit"],
         "Full@%d met in both stages." % k),
        (LEVEL, "%d stable miss" % counts["stable_miss"],
         "Full@%d met in neither stage." % k),
        (MUTED, "%d not plotted" % stats["unobservable"],
         "No observable worst-gold rank in at least one stage: %d dense only, "
         "%d rerank only, %d both. Ranks are read from each stage's stored "
         "top-%d list."
         % (stats["dense_only_null"], stats["rerank_only_null"],
            stats["both_null"], depth)),
    ]

    block_y = 248.0
    for color, heading, body in blocks:
        svg.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s" />'
                   % (rx + 6, block_y - 7, color))
        svg.append(text(rx + 24, block_y, heading, size=19, fill=INK, weight=600))
        for index, chunk in enumerate(wrap(body, 62)):
            svg.append(text(rx + 24, block_y + 24 + index * 20, chunk,
                            size=15, fill=INK2))
        block_y += 78.0

    svg.append(line(56, 660, 1224, 660, stroke=GRID))
    svg.append(text(
        56, 684,
        "%d of %d questions have an observable worst-gold rank in both stages; a rank "
        "is recorded only when every gold appears in that stage's stored list, never "
        "inferred beyond it." % (len(observable), stats["n"]),
        size=13, fill=MUTED,
    ))
    svg.append(text(56, 704, "Source: results/rerank_rescue_damage_cases.csv",
                    size=13, fill=MUTED))
    svg.append("</svg>")
    return "".join(svg)


def cell_view(chosen):
    """The exact aggregation behind Figure 3, so nothing is chart-only."""
    rows = Counter()
    for case in chosen:
        rows[(case["dense_bottleneck"], case["rerank_bottleneck"],
              case["transition"])] += 1
    out = ["<table><thead><tr><th>dense worst-gold rank</th>"
           "<th>rerank worst-gold rank</th><th>transition</th>"
           "<th>questions</th></tr></thead><tbody>"]
    for (dense_rank, rerank_rank, transition), count in sorted(
            rows.items(),
            key=lambda item: (item[0][0] is None, item[0][0] or 0,
                              item[0][1] is None, item[0][1] or 0)):
        out.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td></tr>"
            % ("not in stored list" if dense_rank is None else dense_rank,
               "not in stored list" if rerank_rank is None else rerank_rank,
               escape(transition), count))
    out.append("</tbody></table>")
    return "".join(out)


# ── The table view (nothing is gated behind a chart) ─────────────────────────
def table_view(raw_rows):
    header = list(raw_rows[0].keys())
    out = ["<table><thead><tr>"]
    for column in header:
        out.append("<th>%s</th>" % escape(column))
    out.append("</tr></thead><tbody>")
    for row in raw_rows:
        out.append("<tr>")
        for column in header:
            cell = row[column]
            if column in ("rescue_rate", "damage_rate", "net_rate",
                          "rescue_given_dense_miss", "damage_given_dense_hit"):
                cell = "" if (cell or "").strip() == "" else "%.4f" % float(cell)
            out.append("<td>%s</td>" % escape(cell or ""))
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Reranker rescue / damage — presentation figures</title>
<style>
  :root {{
    --page: #f9f9f7;
    --surface-1: #fcfcfb;
    --text-primary: #0b0b0b;
    --text-secondary: #52514e;
    --text-muted: #898781;
    --grid: #e1e0d9;
    --axis: #c3c2b7;
    --rescue: #2a78d6;
    --damage: #e34948;
    --level: #52514e;
    --ring: rgba(11, 11, 11, 0.10);
  }}
  html[data-theme="dark"] {{
    --page: #0d0d0d;
    --surface-1: #1a1a19;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted: #898781;
    --grid: #2c2c2a;
    --axis: #383835;
    --rescue: #3987e5;
    --damage: #e34948;
    --level: #898781;
    --ring: rgba(255, 255, 255, 0.10);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 32px;
    background: var(--page); color: var(--text-primary);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  }}
  header {{
    max-width: 1280px; margin: 0 auto 24px; display: flex;
    align-items: baseline; gap: 16px; flex-wrap: wrap;
  }}
  h1 {{ font-size: 18px; font-weight: 600; margin: 0; }}
  header p {{ margin: 0; font-size: 14px; color: var(--text-secondary); }}
  button {{
    font: inherit; font-size: 13px; padding: 6px 12px; border-radius: 8px;
    border: 1px solid var(--ring); background: var(--surface-1);
    color: var(--text-primary); cursor: pointer;
  }}
  figure {{
    max-width: 1280px; margin: 0 auto 32px; padding: 0;
    background: var(--surface-1); border: 1px solid var(--ring);
    border-radius: 12px; overflow: hidden;
  }}
  figure svg {{ display: block; width: 100%; height: auto; }}
  figcaption {{
    font-size: 13px; color: var(--text-muted);
    padding: 12px 20px; border-top: 1px solid var(--grid);
  }}
  .mark {{ transition: opacity 120ms ease; }}
  .mark:hover {{ opacity: 0.82; }}
  details {{
    max-width: 1280px; margin: 0 auto 32px; background: var(--surface-1);
    border: 1px solid var(--ring); border-radius: 12px; padding: 16px 20px;
  }}
  summary {{ font-size: 14px; font-weight: 600; cursor: pointer; }}
  table {{
    border-collapse: collapse; margin-top: 16px; font-size: 12px;
    font-variant-numeric: tabular-nums; width: 100%;
  }}
  th, td {{
    text-align: right; padding: 5px 8px; border-bottom: 1px solid var(--grid);
    white-space: nowrap;
  }}
  th:nth-child(-n+4), td:nth-child(-n+4) {{ text-align: left; }}
  th {{ color: var(--text-secondary); font-weight: 600; }}
  #tip {{
    position: fixed; pointer-events: none; opacity: 0; transition: opacity 90ms;
    max-width: 320px; padding: 8px 10px; border-radius: 8px; font-size: 13px;
    line-height: 1.45; background: var(--surface-1); color: var(--text-primary);
    border: 1px solid var(--ring); box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
    z-index: 10;
  }}
  @media print {{
    body {{ padding: 0; background: #fff; }}
    figure {{ border: none; margin: 0; page-break-after: always; }}
    details {{ display: none; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Reranker rescue / damage — presentation figures</h1>
  <p>Generated from <code>{summary_path}</code>. Screenshot a card at 2&times; for slides.</p>
  <button id="theme">Toggle dark mode</button>
</header>

<figure>
{fig1}
<figcaption>Figure 1 &mdash; the headline slide. Waterfall: how the pooled Full@5 hit
count moves from the dense stage to the reranked stage. Right: rescues and damages
on one symmetric count scale at every cutoff.</figcaption>
</figure>

<figure>
{fig2}
<figcaption>Figure 2 &mdash; backup slide. Rescue and damage as a share of each
question-type group, pooled versus per-question setting. The two settings are a
contrast, never an additive total.</figcaption>
</figure>

{fig3_block}
<details>
<summary>Table view &mdash; all 21 rows of results/rerank_rescue_damage.csv</summary>
{table}
</details>

<div id="tip" role="status"></div>
<script>
  var tip = document.getElementById('tip');
  document.addEventListener('mousemove', function (event) {{
    var target = event.target.closest ? event.target.closest('.mark') : null;
    if (!target) {{ tip.style.opacity = 0; return; }}
    tip.textContent = target.getAttribute('data-tip');
    tip.style.opacity = 1;
    var box = tip.getBoundingClientRect();
    var x = Math.min(event.clientX + 14, window.innerWidth - box.width - 12);
    var y = Math.max(event.clientY - box.height - 14, 12);
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
  }});
  document.getElementById('theme').addEventListener('click', function () {{
    var root = document.documentElement;
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  }});
</script>
</body>
</html>
"""


FIG3_BLOCK = """<figure>
{fig3}
<figcaption>Figure 3 &mdash; the case-level view. One mark per question, placed by the
rank of its worst-ranked gold paragraph before and after reranking; the quadrants are
the four transition classes. Marks overlap where questions share a rank pair; the
cell table below carries the exact per-pair counts.</figcaption>
</figure>

<details>
<summary>Cell view &mdash; the (before, after) rank pairs behind Figure 3</summary>
{cells}
</details>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Render the rescue/damage results as slide-ready figures."
    )
    parser.add_argument("--summary", default=DEFAULT_SUMMARY,
                        help="frozen rescue/damage summary CSV (default: %(default)s)")
    parser.add_argument("--cases", default=DEFAULT_CASES,
                        help="per-example cases CSV for Figure 3 (default: %(default)s)")
    parser.add_argument("--no-cases", action="store_true",
                        help="render only Figures 1-2 and skip the case-level figure")
    parser.add_argument("--cases-setting", default="pooled",
                        choices=("pooled", "per_question"),
                        help="setting Figure 3 plots (default: %(default)s)")
    parser.add_argument("--cases-k", type=int, default=5, choices=(2, 5, 10),
                        help="cutoff Figure 3 plots (default: %(default)s)")
    parser.add_argument("--out", default=DEFAULT_OUT,
                        help="output HTML path (default: %(default)s)")
    args = parser.parse_args()

    summary_path = args.summary if os.path.isabs(args.summary) else os.path.join(
        PROJECT_ROOT, args.summary)
    cases_path = args.cases if os.path.isabs(args.cases) else os.path.join(
        PROJECT_ROOT, args.cases)
    out_path = args.out if os.path.isabs(args.out) else os.path.join(
        PROJECT_ROOT, args.out)

    if not os.path.exists(summary_path):
        raise SystemExit("error: summary not found: %s" % summary_path)

    table, raw_rows = load_summary(summary_path)

    fig3_block = ""
    if not args.no_cases:
        if not os.path.exists(cases_path):
            raise SystemExit(
                "error: cases file not found: %s (pass --no-cases to render only "
                "Figures 1-2)" % cases_path)
        if (args.cases_setting, args.cases_k) not in VALID_CASE_COMBOS:
            raise SystemExit(
                "error: (%s, k=%d) is not a cutoff of the cases contract"
                % (args.cases_setting, args.cases_k))
        cases = load_cases(cases_path)
        cross_check_all_cases(cases, table)
        chosen = select_cases(cases, args.cases_setting, args.cases_k)
        fig3_block = FIG3_BLOCK.format(
            fig3=figure_three(chosen, table, args.cases_setting, args.cases_k),
            cells=cell_view(chosen),
        )

    page = PAGE.format(
        summary_path=escape(args.summary.replace(os.sep, "/")),
        fig1=figure_one(table),
        fig2=figure_two(table),
        fig3_block=fig3_block,
        table=table_view(raw_rows),
    )

    # Every input is validated and the complete page is built above, so nothing
    # below can refuse. The write is still staged through a temporary file in the
    # destination directory and atomically replaced, so an interrupted or failing
    # write leaves the previous artifact intact rather than truncated.
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    staged = out_path + ".tmp"
    try:
        with open(staged, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(page)
        os.replace(staged, out_path)
    except BaseException:
        if os.path.exists(staged):
            os.remove(staged)
        raise
    print("wrote %s" % out_path)


if __name__ == "__main__":
    main()
