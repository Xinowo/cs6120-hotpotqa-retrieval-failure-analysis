"""Regression tests for scripts/reporting/plot_rescue_damage.py.

The figure generator is presentation plumbing, so the property under test is
fidelity, not aesthetics: every number that reaches a slide must come from
`results/rerank_rescue_damage.csv` and
`results/rerank_rescue_damage_cases.csv` verbatim, and an input that cannot
support the figures must refuse instead of rendering a plausible-looking card.

Covered for the aggregate summary (Figures 1-2):
  - the drawn labels equal the CSV cells (counts, rates, net, conditional rates);
  - a blank zero-denominator conditional rate (spec S9.2) is never fabricated
    into `0.0%`;
  - the complete frozen contract is enforced before output: the S9.1 17-column
    order, the S9.2 vocabularies / integer and rate lexemes / closed domains, the
    S9.3 21-key set with no duplicate / extra / missing key, the S9.4 physical
    row order, and the S9.5 identities;
  - the S9.2 / S7 group partition holds across the three rows of a combination:
    an `overall` row that is not the exact total of its `bridge` and
    `comparison` rows refuses, both where the cases file cannot incidentally
    catch it and under `--no-cases`, where nothing else stands in the way;
  - the S7 / S2 group size is one constant per `question_type` across all seven
    `(criterion, setting, k)` combinations: a combination recounted over 400 of
    the 500 questions -- every row-local identity and the whole partition still
    intact -- refuses under `--no-cases`, and refuses for an
    `any_evidence_recall` combination even with the cases file supplied, which
    the Full-Evidence-only `cross_check_all_cases` walk cannot stand in for;
  - every one of those refusals happens through the public CLI without creating
    or overwriting the destination, each paired with the accepted-shape control
    that proves the refusal is the invariant and not a broken fixture;
  - rendering is deterministic, and the table view carries every input row so
    nothing is gated behind a chart.

Covered for the per-example cases (Figure 3), against
docs/specs/2026-08-12-rerank-rescue-damage-cases.md:
  - the worst-ranked gold (S8 of the aggregate spec) drives the plotted
    position, and an unobservable rank is counted, never placed;
  - Figure 3 emits exactly one data mark per observable case -- never a bubble
    that collapses cases sharing a rank pair -- and the mark count plus the
    not-plotted count is the whole selected slice;
  - reordered columns, an invalid `(setting, k)`, a duplicate key, a rank object
    that disagrees with its hit cell, a transition that disagrees with its hit
    cells, and a non-rank value all refuse;
  - S5.4 is enforced over the whole file before a slice is selected: a missing
    key, an extra otherwise-valid key, a wrong total, and a reordered row all
    refuse even when the plotted slice itself is intact;
  - S5.3 is enforced as a whole object, not value by value: two distinct golds
    sharing one rank refuse (including where only two of three collide), nulls
    stay exempt, the compact serialization is matched on the raw cell, and one
    rank object is bound to a `(setting, example)` across its `k` rows -- while
    the same example legitimately carries different ranks in the two settings;
  - S5.6: case counts that disagree with the accepted summary refuse for *every*
    `(setting, k)` slice, not only the one Figure 3 plots, so the page cannot
    show two contradictory figures and cannot depend on the rendered cutoff;
  - `--no-cases` renders Figures 1-2 alone, and a missing cases file refuses
    without creating the destination.

Covered for the ownership boundary (aggregate spec S10, cases spec S1 / S6):
  - the generated page carries neutral, mechanically descriptive captions and
    none of the research conclusions or undeclared derived statistics that
    belong to the analysis owner's slide/report layer;
  - the not-plotted wording is neutral and correct for a dense-only null, a
    rerank-only null, and a both-stages null.
"""

import csv
import json
import re
import subprocess
import sys
from collections import Counter
from html import unescape

import pytest

from scripts.reporting import plot_rescue_damage as prd

SCRIPT = "scripts/reporting/plot_rescue_damage.py"

SENTINEL = "<!-- sentinel: this file must survive every refusal -->\n"

COLUMNS = [
    "criterion", "setting", "k", "question_type", "n",
    "dense_hits", "rerank_hits",
    "stable_miss", "rescues", "damages", "stable_hit",
    "rescue_rate", "damage_rate", "net_count", "net_rate",
    "rescue_given_dense_miss", "damage_given_dense_hit",
]

VALID_KEYS = [
    ("full_evidence_recall", "pooled", 2),
    ("full_evidence_recall", "pooled", 5),
    ("full_evidence_recall", "pooled", 10),
    ("full_evidence_recall", "per_question", 2),
    ("full_evidence_recall", "per_question", 5),
    ("any_evidence_recall", "pooled", 5),
    ("any_evidence_recall", "per_question", 5),
]

GROUP_N = {"overall": 500, "bridge": 404, "comparison": 96}


def _row(criterion, setting, k, question_type, dense_hits, rescues, damages):
    """One internally consistent summary row over its S7 group size."""
    return _resized_row(criterion, setting, k, question_type,
                        GROUP_N[question_type], dense_hits, rescues, damages)


def _resized_row(criterion, setting, k, question_type, n,
                 dense_hits, rescues, damages):
    """The same row (spec S9.5 identities) over an explicitly given group size.

    `n` is a parameter here because `GROUP_N` holds one constant per
    `question_type`, so `_row` can only ever write the S7 size. A probe for the
    group size *shared across the seven combinations* has to produce a row the
    ordinary fixture cannot: every identity intact, over a different `n`.
    """
    stable_hit = dense_hits - damages
    rerank_hits = rescues + stable_hit
    dense_miss = n - dense_hits
    return {
        "criterion": criterion,
        "setting": setting,
        "k": str(k),
        "question_type": question_type,
        "n": str(n),
        "dense_hits": str(dense_hits),
        "rerank_hits": str(rerank_hits),
        "stable_miss": str(dense_miss - rescues),
        "rescues": str(rescues),
        "damages": str(damages),
        "stable_hit": str(stable_hit),
        "rescue_rate": repr(rescues / n),
        "damage_rate": repr(damages / n),
        "net_count": str(rescues - damages),
        "net_rate": repr((rescues - damages) / n),
        "rescue_given_dense_miss": repr(rescues / dense_miss) if dense_miss else "",
        "damage_given_dense_hit": repr(damages / dense_hits) if dense_hits else "",
    }


CASE_COLUMNS = [
    "setting", "example_id", "question_type", "level", "question", "gold_titles",
    "k", "dense_full_at_k", "rerank_full_at_k",
    "dense_gold_ranks", "rerank_gold_ranks", "transition",
]

CASE_KS = {"pooled": (2, 5, 10), "per_question": (2, 5)}
CASE_SETTINGS = ("pooled", "per_question")

GOLD_A, GOLD_B = "Gold A", "Gold B"


# ── The fixture world ───────────────────────────────────────────────────────
# The two frozen artifacts are not independent tables, so the fixture is not
# built as two independent tables either. Three cross-row invariants tie them
# together, and a per-(setting, k) fixture cannot satisfy all three at once:
#
#   - cases S5.3: the gold ranks are the whole stored list's ranks and are *not*
#     cut off at `k`, so one rank object belongs to a (stage, setting, example)
#     and every `k` row of that example repeats it;
#   - cases S5.6: each of the five (setting, k) slices must aggregate back to the
#     summary's Full Evidence rows;
#   - aggregate S9.2 / S7: `overall` is the exact total of `bridge` +
#     `comparison`.
#
# The fixture is therefore built the way the real artifact is: one rank pair per
# (setting, example), with the cutoff applied by the reader, and the summary
# *derived* from the resulting transitions. Every one of the three invariants
# then holds by construction rather than by arithmetic that has to be maintained
# by hand.
#
# `Gold A` sits at rank 1 in both stages of every example, so the worst-ranked
# gold -- the S8 bottleneck Figure 3 plots -- is always `Gold B`, and no two
# distinct golds ever share a rank (S5.3 records each gold's *first* position).
# `None` means the gold never entered that stage's stored list.
POOLED_RANK_PAIRS = [
    (2, 2),        # hit in both stages at every cutoff
    (7, 2),        # rescued at k=2 and k=5, stable hit at k=10
    (2, 7),        # damaged at k=2 and k=5, stable hit at k=10
    (20, 30),      # missed in both stages at every cutoff
    (3, 12),       # stable miss at k=2, damaged at k=5 and k=10
    (12, 3),       # stable miss at k=2, rescued at k=5 and k=10
    (None, 4),     # dense gold never stored: stable miss at k=2, else rescued
    (4, None),     # rerank gold never stored: stable miss at k=2, else damaged
    (None, None),  # neither stage stored the gold: stable miss everywhere
    (11, 2),       # rescued at every cutoff
]

# per_question stores only a top-10 list (STORE_DEPTH_BY_SETTING), so no rank
# here exceeds 10. The cycle length differs from the pooled one, so the same
# example carries genuinely different ranks in the two settings and the two
# settings never produce identical counts.
PER_QUESTION_RANK_PAIRS = [
    (2, 2), (7, 2), (2, 7), (9, 10), (3, 8), (8, 3),
    (None, 4), (4, None), (None, None), (10, 2), (6, 2),
]

RANK_PAIRS = {"pooled": POOLED_RANK_PAIRS,
              "per_question": PER_QUESTION_RANK_PAIRS}

EXAMPLE_IDS = ["ex%03d" % index for index in range(GROUP_N["overall"])]
EXAMPLE_INDEX = {example_id: index
                 for index, example_id in enumerate(EXAMPLE_IDS)}
EXAMPLE_TYPE = dict(zip(EXAMPLE_IDS,
                        ["bridge"] * GROUP_N["bridge"]
                        + ["comparison"] * GROUP_N["comparison"]))

# any_evidence_recall has no case-level counterpart, so its two combinations are
# written from the two part groups and the `overall` row is their exact total.
ANY_PART_COUNTS = {
    ("pooled", "bridge"): (240, 60, 20),
    ("pooled", "comparison"): (52, 13, 5),
    ("per_question", "bridge"): (260, 44, 16),
    ("per_question", "comparison"): (58, 11, 4),
}


def _rank_pair(setting, example_id):
    """The one (dense, rerank) worst-gold rank pair of this (setting, example)."""
    pairs = RANK_PAIRS[setting]
    return pairs[EXAMPLE_INDEX[example_id] % len(pairs)]


def _ranks_json(second, first=1):
    return json.dumps({GOLD_A: first, GOLD_B: second},
                      separators=(",", ":"), ensure_ascii=False)


def _case_row(setting, example_id, question_type, k, dense_second, rerank_second):
    """One internally consistent case row for an explicit worst-gold rank pair.

    The cutoff is applied here exactly as S5.3 says the reader applies it, so the
    hit cells and the transition are *derived* from the stored ranks and can
    never quietly disagree with them.
    """
    dense_hit = int(dense_second is not None and dense_second <= k)
    rerank_hit = int(rerank_second is not None and rerank_second <= k)
    return {
        "setting": setting,
        "example_id": example_id,
        "question_type": question_type,
        "level": "hard",
        "question": "Which one came first?",
        "gold_titles": "%s | %s" % (GOLD_A, GOLD_B),
        "k": str(k),
        "dense_full_at_k": str(dense_hit),
        "rerank_full_at_k": str(rerank_hit),
        "dense_gold_ranks": _ranks_json(dense_second),
        "rerank_gold_ranks": _ranks_json(rerank_second),
        "transition": prd.TRANSITIONS[(dense_hit, rerank_hit)],
    }


def _case_rows():
    """The complete 2500-row cases matrix, already in the S5.4 physical order."""
    rows = []
    for setting in CASE_SETTINGS:
        for example_id in EXAMPLE_IDS:
            dense_second, rerank_second = _rank_pair(setting, example_id)
            for k in CASE_KS[setting]:
                rows.append(_case_row(setting, example_id,
                                      EXAMPLE_TYPE[example_id], k,
                                      dense_second, rerank_second))
    return rows


def _full_evidence_counts():
    """(dense_hits, rescues, damages) per (setting, k, group), from the cases."""
    tally = {}
    for row in _case_rows():
        for group in ("overall", row["question_type"]):
            key = (row["setting"], int(row["k"]), group)
            tally.setdefault(key, Counter())[row["transition"]] += 1
    return {key: (counts["damage"] + counts["stable_hit"],
                  counts["rescue"], counts["damage"])
            for key, counts in tally.items()}


FULL_EVIDENCE_COUNTS = _full_evidence_counts()


def _any_counts(setting, question_type):
    if question_type != "overall":
        return ANY_PART_COUNTS[(setting, question_type)]
    return tuple(part + whole
                 for part, whole in zip(ANY_PART_COUNTS[(setting, "bridge")],
                                        ANY_PART_COUNTS[(setting, "comparison")]))


def _combination_counts(criterion, setting, k, question_type):
    """The (dense_hits, rescues, damages) one summary row is written from."""
    if criterion == "full_evidence_recall":
        return FULL_EVIDENCE_COUNTS[(setting, k, question_type)]
    return _any_counts(setting, question_type)


def _summary_rows():
    """The 21-row summary the fixture cases really aggregate to.

    Because the Full Evidence counts are counted off the same rank pairs the
    cases file is written from, `overall` is the exact total of `bridge` +
    `comparison` (S9.2 / S7) and every one of the five (setting, k) slices
    reproduces its rows (S5.6) -- both by construction, for all seven
    combinations rather than for the one slice a figure happens to plot.
    """
    rows = []
    for criterion, setting, k in VALID_KEYS:
        for question_type in ("overall", "bridge", "comparison"):
            rows.append(_row(criterion, setting, k, question_type,
                             *_combination_counts(criterion, setting, k,
                                                  question_type)))
    return rows


def _write(path, rows, columns=COLUMNS):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def _write_raw(path, header, rows):
    """Write an arbitrary physical header/row shape, including a broken one."""
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for row in rows:
            writer.writerow([row.get(column, "") for column in header])
    return str(path)


def _write_cases(path, rows, columns=None):
    return _write(path, rows, columns or CASE_COLUMNS)


def _write_physical_cases(path, physical_rows):
    """Write the frozen 12-column header over rows of arbitrary physical width.

    `csv.DictWriter` cannot emit a ragged data row, so the S5.1 row-shape probes
    hand the writer plain lists.
    """
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(CASE_COLUMNS)
        writer.writerows(physical_rows)
    return str(path)


def _physical(rows):
    return [[row[column] for column in CASE_COLUMNS] for row in rows]


# ── Public-CLI harness: every refusal must preserve an existing destination ──
def _sentinel(tmp_path, name="out.html"):
    out = tmp_path / name
    out.write_text(SENTINEL, encoding="utf-8")
    return out


def _run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args],
                          capture_output=True, text=True)


def _assert_no_staging_residue(out):
    """The atomic writer leaves no half-written `.tmp` beside the destination."""
    residue = sorted(path.name for path in out.parent.glob("*.tmp"))
    assert residue == [], residue


def _assert_refused(result, out, expect=None):
    """The CLI refused, said why, and left the existing artifact untouched."""
    assert result.returncode != 0, result.stdout
    message = result.stderr + result.stdout
    if expect is not None:
        assert expect in message, message
    assert out.read_text(encoding="utf-8") == SENTINEL
    _assert_no_staging_residue(out)


def _assert_accepted(result, out):
    """The paired legal control really does render over the same sentinel."""
    assert result.returncode == 0, result.stderr
    assert out.read_text(encoding="utf-8") != SENTINEL
    _assert_no_staging_residue(out)


def _fixture_pair(tmp_path):
    summary_rows = _summary_rows()
    case_rows = _case_rows()
    summary = _write(tmp_path / "summary.csv", summary_rows)
    cases = _write_cases(tmp_path / "cases.csv", case_rows)
    return summary, cases, summary_rows, case_rows


# ── Rewriting an example's ranks the way S5.3 binds them ────────────────────
def _example_rows(case_rows, setting, example_id):
    """Every `k` row of one (setting, example), which share one rank object."""
    return [row for row in case_rows
            if row["setting"] == setting and row["example_id"] == example_id]


def _retarget_example(case_rows, setting, example_id,
                      dense_second=..., rerank_second=...):
    """Move one (setting, example)'s worst-gold ranks across all its `k` rows.

    S5.3 binds one rank object to the example, so a rank probe is written into
    every `k` row of that example; the hit cells and transition of each row are
    then re-derived from the new ranks, exactly as the reader derives them. The
    result is a file whose every per-row identity still holds, so only the
    property under test has moved.
    """
    current = _rank_pair(setting, example_id)
    dense = current[0] if dense_second is ... else dense_second
    rerank = current[1] if rerank_second is ... else rerank_second
    for row in _example_rows(case_rows, setting, example_id):
        row.update(_case_row(setting, example_id, row["question_type"],
                             int(row["k"]), dense, rerank))
    return case_rows


def _set_rank_cells(case_rows, setting, example_id, column, cell):
    """Write one raw rank cell into every `k` row of a (setting, example).

    Used where the probe is about the *spelling* or the *pairwise* content of the
    object rather than about the ranks it implies, so the hit cells are left
    alone and stay true.
    """
    for row in _example_rows(case_rows, setting, example_id):
        row[column] = cell
    return case_rows


def _is_always_missing(setting, example_id):
    """Both golds sit outside every cutoff of the setting, in both stages."""
    dense, rerank = _rank_pair(setting, example_id)
    ceiling = max(CASE_KS[setting])
    return (dense is not None and rerank is not None
            and dense > ceiling and rerank > ceiling)


def _always_missing_example(setting):
    """An example that misses in both stages at *every* cutoff of the setting.

    Rewriting such an example's ranks -- as long as they stay outside every
    cutoff -- moves no hit cell, no transition and therefore no S5.6 count in any
    slice, so a rank probe over it changes exactly one property of the file.
    """
    for example_id in EXAMPLE_IDS:
        if _is_always_missing(setting, example_id):
            return example_id
    raise AssertionError(
        "no all-cutoff stable miss in %r: %r" % (setting, RANK_PAIRS[setting]))


def _always_missing_in_both():
    """The same, in both settings at once.

    `gold_titles` is bound to the example across *both* settings (S5.2), so a
    probe that rewrites it has to leave every slice of both settings intact.
    """
    for example_id in EXAMPLE_IDS:
        if all(_is_always_missing(setting, example_id)
               for setting in CASE_SETTINGS):
            return example_id
    raise AssertionError("no all-cutoff stable miss in both settings")


def _example_with_pair(setting, pair):
    """The first example whose (setting) worst-gold rank pair is exactly `pair`."""
    for example_id in EXAMPLE_IDS:
        if _rank_pair(setting, example_id) == pair:
            return example_id
    raise AssertionError("no example carries %r in %r" % (pair, setting))


def _render(tmp_path, rows):
    summary = _write(tmp_path / "summary.csv", rows)
    table, raw = prd.load_summary(summary)
    return prd.figure_one(table) + prd.figure_two(table) + prd.table_view(raw)


# ── Fidelity ────────────────────────────────────────────────────────────────
def test_drawn_labels_come_from_the_csv(tmp_path):
    rows = _summary_rows()
    page = _render(tmp_path, rows)

    by_key = {(r["criterion"], r["setting"], r["k"], r["question_type"]): r
              for r in rows}

    # Figure 1: the pooled Full waterfall and the per-cutoff arms.
    for k in ("2", "5", "10"):
        row = by_key[("full_evidence_recall", "pooled", k, "overall")]
        assert ">%s<" % row["rescues"] in page
        assert ">%s<" % row["damages"] in page
        assert "net +%s" % row["net_count"] in page
    pooled5 = by_key[("full_evidence_recall", "pooled", "5", "overall")]
    assert ">%s<" % pooled5["dense_hits"] in page
    assert ">%s<" % pooled5["rerank_hits"] in page
    assert prd.pct(int(pooled5["dense_hits"]) / int(pooled5["n"])) in page

    # Figure 2: rates for every question-type group in both settings.
    for setting in ("pooled", "per_question"):
        for question_type in ("overall", "bridge", "comparison"):
            row = by_key[("full_evidence_recall", setting, "5", question_type)]
            assert prd.pct(float(row["rescue_rate"])) in page
            assert prd.pct(float(row["damage_rate"])) in page


def test_headline_counts_are_not_recomputed(tmp_path):
    """The title reads the CSV's own rescue/damage counts, not a derived guess."""
    rows = _summary_rows()
    pooled5 = next(r for r in rows if (r["criterion"], r["setting"], r["k"],
                                      r["question_type"])
                   == ("full_evidence_recall", "pooled", "5", "overall"))
    page = _render(tmp_path, rows)
    assert "Reranking rescued %s questions and broke %s" % (
        pooled5["rescues"], pooled5["damages"]) in page


def test_blank_conditional_rate_is_not_fabricated(tmp_path):
    """A zero denominator stays 'n/a'; it never becomes a 0.0% claim."""
    page = _render(tmp_path, _zero_denominator_rows("damage_given_dense_hit"))
    assert "n/a" in page
    assert prd.pct_opt(None) == "n/a"


# ── Refusals ────────────────────────────────────────────────────────────────
def test_missing_summary_key_refuses(tmp_path):
    """S9.3: the 21-key set is checked as a whole, not row by row on demand."""
    rows = [r for r in _summary_rows()
            if not (r["criterion"] == "any_evidence_recall"
                    and r["setting"] == "per_question")]
    summary = _write(tmp_path / "summary.csv", rows)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_summary(summary)
    assert "21-row key set" in str(excinfo.value)


def test_pick_refuses_an_absent_row():
    """`pick()` stays a hard guard even though load_summary pre-validates."""
    with pytest.raises(SystemExit) as excinfo:
        prd.pick({}, "full_evidence_recall", "pooled", 5, "overall")
    assert "missing the required row" in str(excinfo.value)


def test_duplicate_row_refuses(tmp_path):
    rows = _summary_rows()
    rows.append(dict(rows[0]))
    summary = _write(tmp_path / "summary.csv", rows)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_summary(summary)
    assert "duplicate summary key" in str(excinfo.value)


def test_empty_summary_refuses(tmp_path):
    summary = _write(tmp_path / "summary.csv", [])
    with pytest.raises(SystemExit):
        prd.load_summary(summary)


def test_refusal_does_not_create_the_destination(tmp_path):
    rows = [r for r in _summary_rows() if r["question_type"] != "comparison"]
    summary = _write(tmp_path / "summary.csv", rows)
    out = tmp_path / "figures" / "out.html"
    result = subprocess.run(
        [sys.executable, SCRIPT, "--summary", summary, "--out", str(out), "--no-cases"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert not out.exists()


def test_missing_summary_refuses(tmp_path):
    out = tmp_path / "out.html"
    result = subprocess.run(
        [sys.executable, SCRIPT, "--no-cases",
         "--summary", str(tmp_path / "absent.csv"), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "summary not found" in (result.stderr + result.stdout)
    assert not out.exists()


# ── The complete frozen summary contract (S9.1-S9.5), through the CLI ───────
def _accepted_summary_control(tmp_path):
    """The legal twin every summary probe is paired with."""
    summary = _write(tmp_path / "control.csv", _summary_rows())
    out = _sentinel(tmp_path, "control.html")
    _assert_accepted(_run("--summary", summary, "--out", str(out), "--no-cases"), out)


def _summary_probe(tmp_path, name, header, rows, expect):
    """One changed property, an existing destination, and the legal control."""
    summary = _write_raw(tmp_path / ("%s.csv" % name), header, rows)
    out = _sentinel(tmp_path, "%s.html" % name)
    _assert_refused(_run("--summary", summary, "--out", str(out), "--no-cases"),
                    out, expect)
    _accepted_summary_control(tmp_path)


def test_accepted_summary_shape_renders_over_an_existing_page(tmp_path):
    """The control alone: a compliant summary really does replace the target."""
    _accepted_summary_control(tmp_path)


def test_reordered_summary_columns_refuse(tmp_path):
    """S9.1: the 17 columns are an exact order, not an unordered set."""
    header = COLUMNS[:]
    header[0], header[1] = header[1], header[0]
    _summary_probe(tmp_path, "reordered_columns", header, _summary_rows(),
                   "17 summary columns in order")


def test_extra_summary_column_refuses(tmp_path):
    _summary_probe(tmp_path, "extra_column", COLUMNS + ["note"], _summary_rows(),
                   "17 summary columns in order")


def test_missing_summary_column_refuses(tmp_path):
    _summary_probe(tmp_path, "missing_column", COLUMNS[:-1], _summary_rows(),
                   "17 summary columns in order")


def test_extra_summary_key_refuses(tmp_path):
    """An illegal `setting` is outside the S9.2 vocabulary, key-unique or not."""
    rows = _summary_rows()
    extra = dict(rows[0])
    extra["setting"] = "illegal_setting"
    _summary_probe(tmp_path, "extra_key", COLUMNS, rows + [extra],
                   "outside the S9.2 vocabulary")


def test_invalid_summary_combination_refuses(tmp_path):
    """S9.3: Any at k=2 is not one of the 7 valid combinations."""
    rows = _summary_rows()
    extra = dict(next(r for r in rows if r["criterion"] == "any_evidence_recall"))
    extra["k"] = "2"
    _summary_probe(tmp_path, "invalid_combo", COLUMNS, rows + [extra],
                   "21-row key set")


def test_missing_unrendered_summary_key_refuses(tmp_path):
    """A valid key no figure draws is still part of the frozen 21-row set."""
    rows = [r for r in _summary_rows()
            if (r["criterion"], r["setting"], r["k"], r["question_type"])
            != ("any_evidence_recall", "pooled", "5", "bridge")]
    assert len(rows) == 20
    _summary_probe(tmp_path, "missing_key", COLUMNS, rows, "21-row key set")


def test_duplicate_summary_key_refuses_through_the_cli(tmp_path):
    rows = _summary_rows()
    _summary_probe(tmp_path, "duplicate_key", COLUMNS, rows + [dict(rows[0])],
                   "duplicate summary key")


def test_wrong_summary_row_order_refuses(tmp_path):
    """S9.4: the physical row order is frozen, so a swap refuses."""
    rows = _summary_rows()
    rows[0], rows[1] = rows[1], rows[0]
    _summary_probe(tmp_path, "row_order", COLUMNS, rows, "S9.4 row order")


@pytest.mark.parametrize("column,cell,label", [
    ("n", "500.0", "float"),
    ("dense_hits", " 200", "padded"),
    ("rescues", "+80", "signed"),
    ("stable_hit", "0120", "leading_zero"),
    ("net_count", "1e2", "exponent"),
])
def test_illegal_integer_spelling_refuses(tmp_path, column, cell, label):
    """S9.2: an integer column is a plain integer, checked on the raw text."""
    rows = _summary_rows()
    rows[0][column] = cell
    _summary_probe(tmp_path, "int_%s" % label, COLUMNS, rows,
                   "not the plain integer S9.2 requires")


@pytest.mark.parametrize("column,cell,label,expect", [
    ("rescue_rate", "NaN", "nan", "non-finite"),
    ("damage_rate", "", "blank", "not a decimal number"),
    ("net_rate", "seven", "word", "not a decimal number"),
    ("rescue_rate", "1.0000000000000001", "precision_adjacent", "S9.2 domain"),
    ("damage_rate", "1e9999", "overflow", "S9.2 domain"),
    ("net_rate", "-1.5", "below_domain", "S9.2 domain"),
])
def test_illegal_rate_spelling_refuses(tmp_path, column, cell, label, expect):
    """S9.2: a rate is a finite decimal inside its closed domain."""
    rows = _summary_rows()
    rows[0][column] = cell
    _summary_probe(tmp_path, "rate_%s" % label, COLUMNS, rows, expect)


@pytest.mark.parametrize("column", ["n", "dense_hits", "rerank_hits", "net_count"])
def test_broken_summary_identity_refuses(tmp_path, column):
    """S9.5: a row whose own counts disagree can only produce a false card."""
    rows = _summary_rows()
    rows[0][column] = str(int(rows[0][column]) + 1)
    _summary_probe(tmp_path, "identity_%s" % column, COLUMNS, rows,
                   "S9.5 identity")


@pytest.mark.parametrize("column,cell,label", [
    ("rescue_rate", "0.2_32", "pep515_underscore"),
    ("rescue_rate", "０.232", "fullwidth_digit"),
    ("damage_rate", "1e-1", "exponent"),
    ("net_rate", "+0.05", "signed_plus"),
])
def test_non_canonical_rate_lexeme_refuses(tmp_path, column, cell, label):
    """S9.2 closes the physical lexeme of a rate (owner decision, DR-009 r3).

    `Decimal()` and `float()` read every spelling here as a legal, in-domain
    value -- exactly as `int()` read `k="02"` -- so each would otherwise be a
    second physical spelling of a frozen rate, silently accepted. The raw text is
    matched instead, and the paired control is the ordinary summary whose rates
    are written in the plain decimal S9.2 requires.
    """
    rows = _summary_rows()
    rows[0][column] = cell
    _summary_probe(tmp_path, "rate_lexeme_%s" % label, COLUMNS, rows,
                   "not the plain decimal S9.2 requires")


# ── S9.2 / S7: `overall` is the exact total of `bridge` + `comparison` ───────
# A row-local identity cannot see this: every one of the three rows below stays
# internally consistent, and only their relationship to each other breaks.
ALTERED_COMPARISON = (44, 9, 4)  # dense_hits, rescues, damages


def _partition_probe_rows(criterion, setting, k, repair):
    """Move one combination's `comparison` row, optionally repairing `overall`.

    Without the repair the `overall` row is no longer the total of its two
    groups; with it, the combination is a different but wholly legal table. Both
    variants satisfy every S9.5 identity in every row, so the partition is the
    single property under test.
    """
    rows = _summary_rows()
    index = {(row["criterion"], row["setting"], row["k"], row["question_type"]):
             position for position, row in enumerate(rows)}
    bridge = rows[index[(criterion, setting, str(k), "bridge")]]
    original = rows[index[(criterion, setting, str(k), "comparison")]]
    assert tuple(int(original[column]) for column
                 in ("dense_hits", "rescues", "damages")) != ALTERED_COMPARISON
    rows[index[(criterion, setting, str(k), "comparison")]] = _row(
        criterion, setting, k, "comparison", *ALTERED_COMPARISON)
    if repair:
        rows[index[(criterion, setting, str(k), "overall")]] = _row(
            criterion, setting, k, "overall",
            *(int(bridge[column]) + part for column, part
              in zip(("dense_hits", "rescues", "damages"), ALTERED_COMPARISON)))
    return rows


def test_a_broken_group_partition_refuses_on_an_unplotted_combination(tmp_path):
    """The break sits where no case-level check can incidentally catch it.

    `any_evidence_recall` / pooled / 5 is a valid combination that the cases
    file's S5.6 Full Evidence rows never touch, so `cross_check_cases` cannot
    stand in for the partition rule, and the corrected-partition control is a
    legal table with the cases file still supplied.
    """
    _, cases, _, _ = _fixture_pair(tmp_path)
    summary = _write(tmp_path / "broken_partition.csv",
                     _partition_probe_rows("any_evidence_recall", "pooled", 5,
                                           repair=False))
    out = _sentinel(tmp_path, "broken_partition.html")
    _assert_refused(
        _run("--summary", summary, "--cases", cases, "--out", str(out)),
        out, "is not the total of its bridge and comparison rows")

    control = _write(tmp_path / "repaired_partition.csv",
                     _partition_probe_rows("any_evidence_recall", "pooled", 5,
                                           repair=True))
    _assert_accepted(
        _run("--summary", control, "--cases", cases, "--out", str(out)), out)


def test_a_broken_group_partition_refuses_under_no_cases(tmp_path):
    """The plotted combination, with no cases file present at all.

    `--no-cases` renders Figures 1-2 alone, so nothing but `load_summary` stands
    between a summary whose groups do not partition and one card stating an
    `overall` rescue count beside a `bridge` and a `comparison` count that do not
    add up to it.
    """
    _summary_probe(tmp_path, "partition_no_cases", COLUMNS,
                   _partition_probe_rows("full_evidence_recall", "pooled", 5,
                                         repair=False),
                   "is not the total of its bridge and comparison rows")

    control = _write(tmp_path / "partition_repaired.csv",
                     _partition_probe_rows("full_evidence_recall", "pooled", 5,
                                           repair=True))
    out = _sentinel(tmp_path, "partition_repaired.html")
    _assert_accepted(
        _run("--summary", control, "--out", str(out), "--no-cases"), out)


# ── S7 / S2: one `question_type` has one `n` across all seven combinations ──
# The partition above binds the three rows of one combination to each other; it
# cannot see one combination disagreeing with another about how many questions
# there are. `_row` reads `n` from `GROUP_N`, so the ordinary fixture cannot
# express that defect at all -- these probes therefore build the three rows of
# one combination explicitly, over a group size 100 questions smaller, and leave
# the other six combinations exactly as they were. Every row-local S9.5 identity
# still holds, and so does the S9.2 / S7 partition (400 = 304 + 96): only the
# relationship between the combinations breaks.
SHRUNK_N = {"overall": 400, "bridge": 304, "comparison": 96}


def _shrunken_combination_rows(criterion, setting, k):
    """The 21 rows with one combination recounted over `SHRUNK_N`."""
    rows = _summary_rows()
    index = {(row["criterion"], row["setting"], row["k"], row["question_type"]):
             position for position, row in enumerate(rows)}
    for question_type in ("overall", "bridge", "comparison"):
        position = index[(criterion, setting, str(k), question_type)]
        assert rows[position]["n"] == str(GROUP_N[question_type])
        rows[position] = _resized_row(
            criterion, setting, k, question_type, SHRUNK_N[question_type],
            *_combination_counts(criterion, setting, k, question_type))
    return rows


def test_a_shrunken_group_size_refuses_under_no_cases(tmp_path):
    """A Full Evidence combination recounted over 400 of the 500 questions.

    `--no-cases` renders Figures 1-2 alone, so nothing but `load_summary` stands
    between this file and a card whose Panel A caption states `N = 500
    questions` while Panel B prints the same combination's net as a share of
    400 -- a percentage that moved because the denominator did.
    """
    _summary_probe(tmp_path, "shrunken_full_no_cases", COLUMNS,
                   _shrunken_combination_rows("full_evidence_recall", "pooled", 2),
                   "so one question_type has one group size")


def test_a_shrunken_any_evidence_group_size_refuses_with_the_cases_file(tmp_path):
    """The same defect where the cases walk cannot stand in for the rule.

    `cross_check_all_cases` pins the five Full Evidence combinations to the case
    rows, but `any_evidence_recall` has no case-level counterpart at all, so its
    two combinations are unpinned even in the default invocation with the cases
    file supplied. The paired control is the accepted fixture pair, which really
    does render over the same sentinel.
    """
    _, cases, _, _ = _fixture_pair(tmp_path)
    summary = _write(tmp_path / "shrunken_any.csv",
                     _shrunken_combination_rows("any_evidence_recall", "pooled", 5))
    out = _sentinel(tmp_path, "shrunken_any.html")
    _assert_refused(
        _run("--summary", summary, "--cases", cases, "--out", str(out)),
        out, "so one question_type has one group size")

    control = _write(tmp_path / "accepted_group_sizes.csv", _summary_rows())
    _assert_accepted(
        _run("--summary", control, "--cases", cases, "--out", str(out)), out)


@pytest.mark.parametrize("column", ["rescue_rate", "damage_rate", "net_rate"])
def test_rate_disagreeing_with_its_counts_refuses(tmp_path, column):
    rows = _summary_rows()
    rows[0][column] = repr(float(rows[0][column]) / 2.0)
    _summary_probe(tmp_path, "rate_drift_%s" % column, COLUMNS, rows,
                   "its own counts give")


def test_fabricated_zero_denominator_rate_refuses(tmp_path):
    """S9.2: a populated conditional rate on a zero denominator refuses."""
    rows = _zero_denominator_rows("damage_given_dense_hit")
    rows[0]["damage_given_dense_hit"] = "0.0"
    _summary_probe(tmp_path, "fabricated_rate", COLUMNS, rows,
                   "requires a blank cell")


def test_blank_rate_with_a_real_denominator_refuses(tmp_path):
    """The mirror case: a blank cell where the denominator is not zero."""
    rows = _summary_rows()
    rows[0]["damage_given_dense_hit"] = ""
    _summary_probe(tmp_path, "blank_rate", COLUMNS, rows,
                   "blank damage_given_dense_hit")


# ── S9.2: "blank" is the physical empty field, never whitespace ──────────────
# The zero-denominator rule is a serialization rule, so the raw cell is compared
# with "" and is never trimmed. A cell holding a space or a tab is populated,
# and a populated cell on a zero denominator is exactly the fabricated value
# S9.2 forbids.
CONDITIONAL_COLUMNS = ["rescue_given_dense_miss", "damage_given_dense_hit"]

WHITESPACE_CELLS = [(" ", "space"), ("\t", "tab"), ("  ", "two_spaces")]


# The rescues / damages each group keeps while its conditional denominator is
# driven to zero. `overall` is the exact total of the two parts, so the block
# still satisfies the S9.2 / S7 partition.
ZERO_DENOMINATOR_RESCUES = {"bridge": 50, "comparison": 10, "overall": 60}
ZERO_DENOMINATOR_DAMAGES = {"bridge": 40, "comparison": 8, "overall": 48}


def _zero_denominator_rows(column):
    """A valid 21-row summary whose first combination has a zero denominator.

    The whole `(criterion, setting, k)` block moves together: S9.2 makes
    `overall` the total of `bridge` + `comparison`, so a zero denominator written
    into the `overall` row alone would be a broken partition rather than the
    blank-cell case under test. Only the denominator moves -- every S9.5
    identity, the partition, and every other rate still hold, so the blank cell
    is the single property under test.
    """
    rows = _summary_rows()
    criterion, setting, k = VALID_KEYS[0]
    for index, question_type in enumerate(("overall", "bridge", "comparison")):
        if column == "damage_given_dense_hit":
            # No group has a dense hit, so none has a damage denominator.
            counts = (0, ZERO_DENOMINATOR_RESCUES[question_type], 0)
        else:
            # Every group is a complete dense hit, so nothing was left to rescue.
            counts = (GROUP_N[question_type], 0,
                      ZERO_DENOMINATOR_DAMAGES[question_type])
        rows[index] = _row(criterion, setting, k, question_type, *counts)
    assert rows[0][column] == ""
    return rows


@pytest.mark.parametrize("column", CONDITIONAL_COLUMNS)
def test_exactly_empty_zero_denominator_rate_is_accepted(tmp_path, column):
    """The legal control: the empty field renders and shows 'n/a', never 0.0%."""
    summary = _write_raw(tmp_path / ("empty_%s.csv" % column), COLUMNS,
                         _zero_denominator_rows(column))
    out = _sentinel(tmp_path, "empty_%s.html" % column)
    _assert_accepted(_run("--summary", summary, "--out", str(out), "--no-cases"),
                     out)
    assert "n/a" in out.read_text(encoding="utf-8")


@pytest.mark.parametrize("column", CONDITIONAL_COLUMNS)
@pytest.mark.parametrize("cell,label", WHITESPACE_CELLS)
def test_whitespace_zero_denominator_rate_refuses(tmp_path, column, cell, label):
    """Whitespace is a populated cell, so it refuses like a fabricated value."""
    rows = _zero_denominator_rows(column)
    control = [dict(row) for row in rows]
    rows[0][column] = cell

    name = "ws_%s_%s" % (column, label)
    summary = _write_raw(tmp_path / ("%s.csv" % name), COLUMNS, rows)
    out = _sentinel(tmp_path, "%s.html" % name)
    _assert_refused(_run("--summary", summary, "--out", str(out), "--no-cases"),
                    out, "requires a blank cell")

    # The legal twin differs only by the exact empty field and replaces the
    # same sentinel, so the refusal is the invariant and not a broken fixture.
    twin = _write_raw(tmp_path / ("%s_control.csv" % name), COLUMNS, control)
    _assert_accepted(_run("--summary", twin, "--out", str(out), "--no-cases"), out)


@pytest.mark.parametrize("column", CONDITIONAL_COLUMNS + ["rescue_rate",
                                                         "damage_rate",
                                                         "net_rate"])
def test_whitespace_padded_rate_refuses(tmp_path, column):
    """A padded rate is a second physical spelling, not a value to be trimmed."""
    rows = _summary_rows()
    rows[0][column] = " " + rows[0][column]
    _summary_probe(tmp_path, "padded_%s" % column, COLUMNS, rows,
                   "padded with whitespace")


def test_whitespace_conditional_rate_with_a_real_denominator_refuses(tmp_path):
    """The mirror of the zero-denominator case: whitespace is never a blank."""
    rows = _summary_rows()
    rows[0]["damage_given_dense_hit"] = " "
    _summary_probe(tmp_path, "ws_real_denominator", COLUMNS, rows,
                   "padded with whitespace")


def test_populated_conditional_rate_is_still_accepted(tmp_path):
    """The retained positive control: a real conditional rate keeps rendering."""
    rows = _summary_rows()
    assert rows[0]["damage_given_dense_hit"] not in ("", " ")
    summary = _write_raw(tmp_path / "populated_rate.csv", COLUMNS, rows)
    out = _sentinel(tmp_path, "populated_rate.html")
    _assert_accepted(_run("--summary", summary, "--out", str(out), "--no-cases"),
                     out)
    assert prd.pct(float(rows[0]["damage_given_dense_hit"])) in out.read_text(
        encoding="utf-8")


# ── Output shape ────────────────────────────────────────────────────────────
def test_table_view_carries_every_input_row(tmp_path):
    rows = _summary_rows()
    summary = _write(tmp_path / "summary.csv", rows)
    _, raw = prd.load_summary(summary)
    view = prd.table_view(raw)
    body = view.split("<tbody>")[1]
    assert body.count("<tr>") == len(rows)
    assert view.count("<th>") == len(COLUMNS)


def test_render_is_deterministic(tmp_path):
    rows = _summary_rows()
    summary = _write(tmp_path / "summary.csv", rows)
    first = tmp_path / "a.html"
    second = tmp_path / "b.html"
    for out in (first, second):
        result = subprocess.run(
            [sys.executable, SCRIPT, "--summary", summary, "--out", str(out),
             "--no-cases"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
    assert first.read_bytes() == second.read_bytes()


def test_page_is_self_contained(tmp_path):
    rows = _summary_rows()
    out = tmp_path / "out.html"
    summary = _write(tmp_path / "summary.csv", rows)
    result = subprocess.run(
        [sys.executable, SCRIPT, "--summary", summary, "--out", str(out),
         "--no-cases"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    page = out.read_text(encoding="utf-8")
    assert "<script src" not in page
    assert "http://" not in page and "https://" not in page
    # Identity never rests on color alone: both series appear in a legend.
    assert "Rescues (dense miss" in page and "Damages (dense hit" in page


# ── Figure 3: the per-example cases ─────────────────────────────────────────
def _pick_summary(summary_rows, setting, k, question_type):
    return next(row for row in summary_rows
                if (row["criterion"], row["setting"], row["k"], row["question_type"])
                == ("full_evidence_recall", setting, k, question_type))


def test_bottleneck_is_the_worst_gold():
    assert prd.bottleneck({"a": 3, "b": 7}) == 7
    assert prd.bottleneck({"a": 1, "b": 1}) == 1
    # An unobservable gold is never inferred as a concrete rank.
    assert prd.bottleneck({"a": 3, "b": None}) is None


def test_figure_three_states_the_counted_classes(tmp_path):
    summary, cases, summary_rows, case_rows = _fixture_pair(tmp_path)
    table, _ = prd.load_summary(summary)
    chosen = prd.select_cases(prd.load_cases(cases), "pooled", 5)
    prd.cross_check_cases(chosen, table, "pooled", 5)
    svg = prd.figure_three(chosen, table, "pooled", 5)

    expected = _pick_summary(summary_rows, "pooled", "5", "overall")
    assert "%s rescued" % expected["rescues"] in svg
    assert "%s damaged" % expected["damages"] in svg

    # "Not plotted" is a null in *either* stage: the worst-ranked gold is
    # unobservable as soon as one stage never stored one of the golds.
    unobservable = sum(1 for row in case_rows
                       if row["setting"] == "pooled" and row["k"] == "5"
                       and ("null" in row["dense_gold_ranks"]
                            or "null" in row["rerank_gold_ranks"]))
    assert unobservable > 0
    assert "%d not plotted" % unobservable in svg


def _observable(chosen):
    return [case for case in chosen
            if case["dense_bottleneck"] is not None
            and case["rerank_bottleneck"] is not None]


def _unobservable(chosen):
    return [case for case in chosen
            if case["dense_bottleneck"] is None
            or case["rerank_bottleneck"] is None]


def test_one_data_mark_per_observable_case(tmp_path):
    """The gate's cardinality rule: one mark per observable case, never a bubble.

    A bubble layer would satisfy `marks <= observable` by collapsing every case
    that shares a rank pair, so the fixture is asserted to contain such a
    collision before the count is compared.
    """
    summary, cases, _, _ = _fixture_pair(tmp_path)
    table, _ = prd.load_summary(summary)
    chosen = prd.select_cases(prd.load_cases(cases), "pooled", 5)
    svg = prd.figure_three(chosen, table, "pooled", 5)

    observable = _observable(chosen)
    coordinates = [(case["dense_bottleneck"], case["rerank_bottleneck"])
                   for case in observable]
    assert len(set(coordinates)) < len(coordinates), (
        "the fixture must contain cases sharing one coordinate")

    marks = svg.count('<circle class="mark"')
    assert marks == len(observable)
    assert marks + (len(chosen) - len(observable)) == len(chosen)


def test_unobservable_cases_are_counted_but_not_plotted(tmp_path):
    summary, cases, _, _ = _fixture_pair(tmp_path)
    table, _ = prd.load_summary(summary)
    chosen = prd.select_cases(prd.load_cases(cases), "pooled", 5)
    svg = prd.figure_three(chosen, table, "pooled", 5)

    unobservable = _unobservable(chosen)
    assert len(unobservable) > 0
    assert "%d not plotted" % len(unobservable) in svg
    # No mark may sit at a fabricated coordinate for an unobservable rank.
    assert svg.count('<circle class="mark"') == len(chosen) - len(unobservable)

    # The unobservable rows stay visible in the cell table instead.
    assert "not in stored list" in prd.cell_view(chosen)
    assert sum(1 for case in chosen if case["dense_bottleneck"] is None) > 0


def test_marks_carry_a_constant_radius(tmp_path):
    """A per-case mark must not re-encode multiplicity as an area."""
    summary, cases, _, _ = _fixture_pair(tmp_path)
    table, _ = prd.load_summary(summary)
    chosen = prd.select_cases(prd.load_cases(cases), "pooled", 5)
    svg = prd.figure_three(chosen, table, "pooled", 5)

    radii = set(re.findall(r'<circle class="mark"[^>]*? r="([0-9.]+)"', svg))
    assert len(radii) == 1, radii


# ── The ownership boundary: neutral description, not research interpretation ──
# Aggregate spec S10 and cases spec S1/S6 reserve the failure-analysis reading
# for the analysis owner. These phrases were published by the generator in the
# round-1 artifact; they belong to Xin's slide/report layer, not to a renderer.
INTERPRETIVE_PHRASES = [
    "riskier",
    "near-miss",
    "near-misses",
    "almost never",
    "mostly promotes",
    "never a collapse",
    "cannot find new evidence",
    "cannot be reached",
    "unreachable",
    "Largest bubble",
    "median",
    "was the problem",
    "still missing evidence",
    "Lower is better",
]


def test_the_page_states_no_owner_level_interpretation(tmp_path):
    summary, cases, _, _ = _fixture_pair(tmp_path)
    out = tmp_path / "out.html"
    result = _run("--summary", summary, "--cases", cases, "--out", str(out))
    assert result.returncode == 0, result.stderr
    page = out.read_text(encoding="utf-8")
    # Checked on the raw page and on the rejoined prose, so a banned phrase
    # cannot hide across a wrapped-caption boundary.
    prose = _svg_prose(page)
    found = [phrase for phrase in INTERPRETIVE_PHRASES
             if phrase in page or phrase in prose]
    assert found == [], found


def test_the_page_states_the_neutral_data_description(tmp_path):
    """The approved side of the boundary: classes, counts, and observability."""
    summary, cases, summary_rows, _ = _fixture_pair(tmp_path)
    out = tmp_path / "out.html"
    result = _run("--summary", summary, "--cases", cases, "--out", str(out))
    assert result.returncode == 0, result.stderr
    prose = _svg_prose(out.read_text(encoding="utf-8"))
    expected = _pick_summary(summary_rows, "pooled", "5", "overall")
    for phrase in ("%s rescued" % expected["rescues"],
                   "%s damaged" % expected["damages"],
                   "%s stable hit" % expected["stable_hit"],
                   "%s stable miss" % expected["stable_miss"],
                   "not plotted",
                   "One mark per question",
                   "No observable worst-gold rank in at least one stage"):
        assert phrase in prose, phrase


def _svg_prose(svg):
    """The drawn prose, rejoined: SVG has no flow text, so a caption is wrapped
    across several <text> elements and a phrase can straddle two of them."""
    bodies = re.findall(r"<text\b[^>]*>(.*?)</text>", svg)
    return unescape(" ".join(bodies))


def _null_ranks(row, stage):
    """Null one stage's second gold rank, keeping the row's own identities."""
    row["%s_gold_ranks" % stage] = _ranks_json(None)
    row["%s_full_at_k" % stage] = "0"
    row["transition"] = prd.TRANSITIONS[(int(row["dense_full_at_k"]),
                                         int(row["rerank_full_at_k"]))]
    return row


@pytest.mark.parametrize("stages,label", [
    (("dense",), "dense_only"),
    (("rerank",), "rerank_only"),
    (("dense", "rerank"), "both"),
])
def test_neutral_wording_for_each_null_control(tmp_path, stages, label):
    """S5.3 nulls are described by stage, with no owner-level reading attached."""
    summary, _, summary_rows, case_rows = _fixture_pair(tmp_path)
    table, _ = prd.load_summary(summary)

    # A stable_miss is legal with a null in either stage or in both, and nulling
    # a rank inside that class never moves a S5.6 count. S5.3 binds the rank
    # object to the example, so the null is written into every `k` row of it; the
    # example already misses in both stages at every cutoff, so no hit cell,
    # transition or slice count moves either.
    target = _always_missing_example("pooled")
    for row in _example_rows(case_rows, "pooled", target):
        for stage in stages:
            _null_ranks(row, stage)
    cases = _write_cases(tmp_path / ("null_%s.csv" % label), case_rows)

    chosen = prd.select_cases(prd.load_cases(cases), "pooled", 5)
    prd.cross_check_cases(chosen, table, "pooled", 5)
    svg = prd.figure_three(chosen, table, "pooled", 5)

    counts = prd.case_counts(chosen, "pooled")
    assert counts["unobservable"] == (counts["dense_only_null"]
                                     + counts["rerank_only_null"]
                                     + counts["both_null"])
    assert counts["dense_only_null" if stages == ("dense",) else
                  "rerank_only_null" if stages == ("rerank",) else
                  "both_null"] > 0
    assert ("No observable worst-gold rank in at least one stage: %d dense only, "
            "%d rerank only, %d both."
            % (counts["dense_only_null"], counts["rerank_only_null"],
               counts["both_null"])) in _svg_prose(svg)
    assert svg.count('<circle class="mark"') == len(_observable(chosen))
    assert [phrase for phrase in INTERPRETIVE_PHRASES if phrase in svg] == []


def test_cases_disagreeing_with_the_summary_refuse(tmp_path):
    summary, _, _, case_rows = _fixture_pair(tmp_path)
    table, _ = prd.load_summary(summary)

    # Turn one example that pooled@5 counts as a rescue into an example missed by
    # both stages. The move is written across all three of its `k` rows, as S5.3
    # binds it, so every per-row identity and the rank binding still hold and
    # only the aggregate counts leave the summary.
    target = next(row for row in case_rows
                  if (row["setting"], row["k"], row["transition"])
                  == ("pooled", "5", "rescue"))["example_id"]
    _retarget_example(case_rows, "pooled", target,
                      dense_second=30, rerank_second=40)
    cases = _write_cases(tmp_path / "drifted.csv", case_rows)
    chosen = prd.select_cases(prd.load_cases(cases), "pooled", 5)
    with pytest.raises(SystemExit) as excinfo:
        prd.cross_check_cases(chosen, table, "pooled", 5)
    assert "disagrees with the accepted summary" in str(excinfo.value)


def test_reordered_case_columns_refuse(tmp_path):
    _, _, _, case_rows = _fixture_pair(tmp_path)
    swapped = CASE_COLUMNS[:]
    swapped[0], swapped[1] = swapped[1], swapped[0]
    cases = _write_cases(tmp_path / "swapped.csv", case_rows, swapped)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_cases(cases)
    assert "12 case columns in order" in str(excinfo.value)


def test_invalid_case_combination_refuses(tmp_path):
    _, _, _, case_rows = _fixture_pair(tmp_path)
    case_rows.append(_case_row("per_question", "ex999", "bridge", 10, 2, 2))
    cases = _write_cases(tmp_path / "invalid.csv", case_rows)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_cases(cases)
    assert "invalid combination" in str(excinfo.value)


def test_duplicate_case_key_refuses(tmp_path):
    _, _, _, case_rows = _fixture_pair(tmp_path)
    case_rows.append(dict(case_rows[0]))
    cases = _write_cases(tmp_path / "duplicate.csv", case_rows)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_cases(cases)
    assert "duplicate case key" in str(excinfo.value)


def test_ranks_disagreeing_with_the_hit_cell_refuse(tmp_path):
    _, _, _, case_rows = _fixture_pair(tmp_path)
    target = next(row for row in case_rows if row["transition"] == "rescue")
    target["rerank_gold_ranks"] = _ranks_json(int(target["k"]) + 6)
    cases = _write_cases(tmp_path / "ranks.csv", case_rows)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_cases(cases)
    assert "imply a different Full@" in str(excinfo.value)


def test_transition_disagreeing_with_the_hit_cells_refuses(tmp_path):
    _, _, _, case_rows = _fixture_pair(tmp_path)
    target = next(row for row in case_rows if row["transition"] == "rescue")
    target["transition"] = "damage"
    cases = _write_cases(tmp_path / "transition.csv", case_rows)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_cases(cases)
    assert "has transition" in str(excinfo.value)


@pytest.mark.parametrize("bad,label", [("0", "zero"), ("true", "bool"),
                                       ("-3", "negative"), ("1.5", "fraction")])
def test_non_rank_values_refuse(tmp_path, bad, label):
    _, _, _, case_rows = _fixture_pair(tmp_path)
    case_rows[0]["dense_gold_ranks"] = '{"Gold A":1,"Gold B":%s}' % bad
    cases = _write_cases(tmp_path / ("rank_%s.csv" % label), case_rows)
    with pytest.raises(SystemExit):
        prd.load_cases(cases)


def test_gold_rank_keys_must_be_the_rows_gold_titles(tmp_path):
    _, _, _, case_rows = _fixture_pair(tmp_path)
    case_rows[0]["dense_gold_ranks"] = '{"Gold A":1,"Other":2}'
    cases = _write_cases(tmp_path / "keys.csv", case_rows)
    with pytest.raises(SystemExit) as excinfo:
        prd.load_cases(cases)
    assert "not the row" in str(excinfo.value)


# ── The complete frozen cases matrix (S5.4), through the CLI ────────────────
# Every probe here leaves the plotted pooled@5 slice intact and changes only a
# non-selected part of the file, so it fails exactly when validation is
# slice-local rather than whole-file.
def _cases_probe(tmp_path, name, case_rows, expect, control_rows=None):
    summary = _write(tmp_path / ("summary_%s.csv" % name), _summary_rows())
    cases = _write_cases(tmp_path / ("%s.csv" % name), case_rows)
    out = _sentinel(tmp_path, "%s.html" % name)
    _assert_refused(
        _run("--summary", summary, "--cases", cases, "--out", str(out)),
        out, expect)
    if control_rows is not None:
        # The legal twin differs from the probe in exactly the property under
        # test and replaces the same sentinel target.
        control = _write_cases(tmp_path / ("%s_control.csv" % name), control_rows)
        _assert_accepted(
            _run("--summary", summary, "--cases", control, "--out", str(out)), out)


def test_accepted_cases_shape_renders_over_an_existing_page(tmp_path):
    """The legal control for every S5.4 probe below."""
    summary, cases, _, _ = _fixture_pair(tmp_path)
    out = _sentinel(tmp_path, "control.html")
    _assert_accepted(
        _run("--summary", summary, "--cases", cases, "--out", str(out)), out)


def test_a_missing_non_selected_cases_key_refuses(tmp_path):
    """The round-1 counterexample: 2,499 valid rows, pooled@5 slice intact."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    victim = next(row for row in case_rows
                  if (row["setting"], row["k"]) == ("pooled", "2"))
    case_rows.remove(victim)
    assert len(case_rows) == 2499
    _cases_probe(tmp_path, "missing_case_key", case_rows, "exactly 2500")


def test_an_extra_otherwise_valid_cases_key_refuses(tmp_path):
    """A brand-new example id at one cutoff is a valid row and an invalid file."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    case_rows.append(_case_row("pooled", "ex999", "bridge", 2, 2, 2))
    _cases_probe(tmp_path, "extra_case_key", case_rows, "exactly 2500")


def test_a_wrong_cases_total_refuses(tmp_path):
    """Dropping one example's whole five-row block keeps every other invariant."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    victim = case_rows[0]["example_id"]
    case_rows = [row for row in case_rows if row["example_id"] != victim]
    assert len(case_rows) == 2495
    _cases_probe(tmp_path, "wrong_case_total", case_rows, "exactly 2500")


def test_reordered_cases_rows_refuse(tmp_path):
    """S5.4 freezes the physical order, so swapping two rows refuses."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    first = next(index for index, row in enumerate(case_rows)
                 if row["setting"] == "per_question")
    case_rows[first], case_rows[first + 1] = case_rows[first + 1], case_rows[first]
    _cases_probe(tmp_path, "reordered_case_rows", case_rows, "S5.4 row order")


def test_settings_covering_different_example_ids_refuse(tmp_path):
    """S5.4: both settings cover the same example set, checked as a whole."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    for row in case_rows:
        if (row["setting"], row["k"]) == ("per_question", "2"):
            row["example_id"] = "zz_" + row["example_id"]
            break
    case_rows.sort(key=lambda row: (row["setting"] != "pooled",
                                    row["example_id"], int(row["k"])))
    _cases_probe(tmp_path, "case_id_drift", case_rows, "same example ids")


# ── S5.1 / S5.2: physical row shape and the exact `k` lexeme ────────────────
# Each probe leaves the plotted pooled@5 slice intact and changes only a
# non-selected row, so it fails exactly when the physical contract is recovered
# from the normalized key matrix instead of being checked on the raw file.
def _non_selected(case_rows, setting="pooled", k="2"):
    return next(row for row in case_rows
                if (row["setting"], row["k"]) == (setting, k))


def _physical_cases_probe(tmp_path, name, physical_rows, expect, control_rows):
    summary = _write(tmp_path / ("summary_%s.csv" % name), _summary_rows())
    cases = _write_physical_cases(tmp_path / ("%s.csv" % name), physical_rows)
    out = _sentinel(tmp_path, "%s.html" % name)
    _assert_refused(
        _run("--summary", summary, "--cases", cases, "--out", str(out)),
        out, expect)
    control = _write_physical_cases(tmp_path / ("%s_control.csv" % name),
                                    _physical(control_rows))
    _assert_accepted(
        _run("--summary", summary, "--cases", control, "--out", str(out)), out)


def test_a_thirteenth_cases_field_refuses(tmp_path):
    """S5.1 freezes 12 columns, so a 13-field data row is not the artifact."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    physical = _physical(case_rows)
    victim = case_rows.index(_non_selected(case_rows))
    physical[victim] = physical[victim] + ["surplus"]
    _physical_cases_probe(tmp_path, "cases_long_row", physical,
                          "more fields than the 12 columns", case_rows)


def test_a_short_cases_data_row_refuses(tmp_path):
    """The other direction: a row missing its last field is equally ragged."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    physical = _physical(case_rows)
    victim = case_rows.index(_non_selected(case_rows))
    physical[victim] = physical[victim][:-1]
    _physical_cases_probe(tmp_path, "cases_short_row", physical,
                          "has no transition field", case_rows)


@pytest.mark.parametrize("cell,label", [
    ("02", "leading_zero"),
    ("+2", "signed"),
    ("2.0", "float"),
    (" 2", "padded_left"),
    ("2 ", "padded_right"),
])
def test_non_canonical_case_k_lexeme_refuses(tmp_path, cell, label):
    """S5.2: `k` is a plain integer, matched before int() can normalize it.

    Every spelling here converts to the legal cutoff 2, so the key matrix,
    identities, and S5.6 counts all stay intact: only the physical lexeme is
    wrong, and the accepted twin spells the same row `2`.
    """
    _, _, _, case_rows = _fixture_pair(tmp_path)
    control = [dict(row) for row in case_rows]
    _non_selected(case_rows)["k"] = cell
    _cases_probe(tmp_path, "case_k_%s" % label, case_rows,
                 "not one of the plain integers", control_rows=control)


# ── S5.3: a rank is observable in the stored list, or it is null ────────────
# S5.3 binds one rank object to a (stage, setting, example), so each probe here
# rewrites every `k` row of its example rather than a single row: a one-row edit
# would be caught by the cross-row binding first and would never reach the rule
# under test. Each probe uses an example that already misses in both stages at
# every cutoff, so no hit cell, transition or S5.6 count moves in any slice.
@pytest.mark.parametrize("setting", ["pooled", "per_question"])
def test_a_rank_beyond_the_stored_depth_refuses(tmp_path, setting):
    """A rank past the storage depth cannot have been read from that list.

    The example stays a stable miss at every cutoff either way, so hit cells,
    transitions and every S5.6 count are unchanged; the legal twin carries the
    exact stored depth, which is observable and must still be accepted.
    """
    _, _, _, case_rows = _fixture_pair(tmp_path)
    depth = prd.STORE_DEPTH_BY_SETTING[setting]
    example_id = _always_missing_example(setting)
    control = [dict(row) for row in case_rows]
    _set_rank_cells(control, setting, example_id, "dense_gold_ranks",
                    _ranks_json(depth))
    _set_rank_cells(case_rows, setting, example_id, "dense_gold_ranks",
                    _ranks_json(depth + 1))
    _cases_probe(tmp_path, "depth_%s" % setting, case_rows,
                 "beyond the stored top-%d list" % depth, control_rows=control)


@pytest.mark.parametrize("setting", ["pooled", "per_question"])
def test_an_absent_gold_is_accepted_as_null(tmp_path, setting):
    """Null stays the only legal representation of a gold past the depth."""
    summary, _, _, case_rows = _fixture_pair(tmp_path)
    _set_rank_cells(case_rows, setting, _always_missing_example(setting),
                    "dense_gold_ranks", _ranks_json(None))
    cases = _write_cases(tmp_path / ("null_ok_%s.csv" % setting), case_rows)
    out = _sentinel(tmp_path, "null_ok_%s.html" % setting)
    _assert_accepted(
        _run("--summary", summary, "--cases", cases, "--out", str(out)), out)


# ── S5.3: two distinct golds cannot share one position ──────────────────────
def test_two_golds_at_the_same_rank_refuse(tmp_path):
    """S5.3 maps each gold to its *first* rank in one stored list.

    Two distinct titles occupy distinct positions in a list, so their first
    occurrences differ: a repeated rank is not an observation the stored list can
    produce, and `bottleneck()` would take `max()` over the fabricated set and
    plot the result. Both golds sit outside every cutoff, so `full_at_k`, the
    transition and every S5.6 count are unchanged in all three `k` rows -- the
    repeated rank is the single property under test. The control is the same two
    golds at distinct ranks, a spec-legal permutation.
    """
    _, _, _, case_rows = _fixture_pair(tmp_path)
    example_id = _always_missing_example("pooled")
    control = [dict(row) for row in case_rows]
    _set_rank_cells(control, "pooled", example_id, "dense_gold_ranks",
                    _ranks_json(20, first=30))
    _set_rank_cells(case_rows, "pooled", example_id, "dense_gold_ranks",
                    _ranks_json(20, first=20))
    _cases_probe(tmp_path, "shared_rank", case_rows, "the same rank 20",
                 control_rows=control)


def test_two_golds_both_absent_are_accepted(tmp_path):
    """Nulls are exempt: any number of golds may be missing from the list."""
    summary, _, _, case_rows = _fixture_pair(tmp_path)
    _set_rank_cells(case_rows, "pooled", _always_missing_example("pooled"),
                    "dense_gold_ranks", _ranks_json(None, first=None))
    cases = _write_cases(tmp_path / "both_null.csv", case_rows)
    out = _sentinel(tmp_path, "both_null.html")
    _assert_accepted(
        _run("--summary", summary, "--cases", cases, "--out", str(out)), out)


GOLD_C = "Gold C"

# Ranks outside every cutoff of each setting, so a third gold changes no hit
# cell: the pooled list stores 50 and its widest cutoff is 10, the per_question
# list stores 10 and its widest cutoff is 5.
THREE_GOLD_DISTINCT = {"pooled": (20, 30, 40), "per_question": (7, 8, 9)}
THREE_GOLD_COLLIDING = {"pooled": (20, 30, 30), "per_question": (7, 8, 8)}


def _make_three_gold(case_rows, example_id, ranks_by_setting):
    """Give one example a third gold, consistently across all five of its rows.

    `gold_titles` is example-bound (S5.2), so it moves in both settings at once,
    while each setting keeps its own rank object because the two settings hold
    genuinely different stored lists.
    """
    titles = prd.TITLE_SEPARATOR.join((GOLD_A, GOLD_B, GOLD_C))
    for row in case_rows:
        if row["example_id"] != example_id:
            continue
        row["gold_titles"] = titles
        cell = json.dumps(
            dict(zip((GOLD_A, GOLD_B, GOLD_C), ranks_by_setting[row["setting"]])),
            separators=(",", ":"), ensure_ascii=False)
        row["dense_gold_ranks"] = cell
        row["rerank_gold_ranks"] = cell
    return case_rows


def test_three_golds_with_only_two_colliding_refuse(tmp_path):
    """The rule is pairwise, not "the object holds one rank".

    Two of three golds share a position while the third is distinct, so a check
    that only compared the extremes, or the first pair, would pass. The example
    misses at every cutoff of both settings, so the extra gold moves no count.
    """
    _, _, _, case_rows = _fixture_pair(tmp_path)
    example_id = _always_missing_in_both()
    control = _make_three_gold([dict(row) for row in case_rows], example_id,
                               THREE_GOLD_DISTINCT)
    _make_three_gold(case_rows, example_id, THREE_GOLD_COLLIDING)
    _cases_probe(tmp_path, "three_gold_collision", case_rows, "the same rank 30",
                 control_rows=control)


def test_a_non_canonical_rank_serialization_refuses(tmp_path):
    """S5.3 freezes the compact spelling, so a rerun is byte-identical.

    `json.loads` normalises `", "` / `": "` padding away exactly as `int()`
    normalised `k="02"`, so the parsed object is identical and no rendered number
    moves: the physical fidelity of the frozen artifact is the whole property.
    The padded spelling goes into every `k` row of the example, so the cross-row
    rank binding cannot fire first and stand in for the serialization rule.
    """
    _, _, _, case_rows = _fixture_pair(tmp_path)
    example_id = _always_missing_example("pooled")
    compact = _ranks_json(30, first=20)
    padded = json.dumps(json.loads(compact), ensure_ascii=False)
    assert json.loads(padded) == json.loads(compact) and padded != compact

    control = [dict(row) for row in case_rows]
    _set_rank_cells(control, "pooled", example_id, "dense_gold_ranks", compact)
    _set_rank_cells(case_rows, "pooled", example_id, "dense_gold_ranks", padded)
    _cases_probe(tmp_path, "rank_serialization", case_rows,
                 "not the compact S5.3 serialization", control_rows=control)


# ── S5.3: one rank object per (stage, setting, example), across its k rows ───
@pytest.mark.parametrize("column", ["dense_gold_ranks", "rerank_gold_ranks"])
def test_rank_drift_across_the_k_rows_of_one_example_refuses(tmp_path, column):
    """The ranks are the whole list's ranks; `k` is applied by the reader.

    Only the `k=10` row moves, and it moves to another out-of-cutoff rank, so
    `full_at_10` stays 0, the transition stays `stable_miss`, no slice count
    changes, and no other cell moves. What does change is the reading: the file
    would place that gold at one position when rendered at `k=5` and at another
    when rendered at `k=10` -- two observations of one stored list.
    """
    _, _, _, case_rows = _fixture_pair(tmp_path)
    example_id = _always_missing_example("pooled")
    drifted_cell = _ranks_json(40)

    control = [dict(row) for row in case_rows]
    _set_rank_cells(control, "pooled", example_id, column, drifted_cell)
    next(row for row in _example_rows(case_rows, "pooled", example_id)
         if row["k"] == "10")[column] = drifted_cell

    _cases_probe(tmp_path, "rank_drift_%s" % column, case_rows,
                 "every k row of one (setting, example) carries the same object",
                 control_rows=control)


def test_one_example_may_carry_different_ranks_in_each_setting(tmp_path):
    """The binding is per (setting, example), never per example.

    Pooled and per_question hold genuinely different stored lists, so one
    example_id legitimately carries different ranks in the two settings; a
    binding scoped to the example alone would refuse the accepted artifact.
    """
    summary, cases, _, case_rows = _fixture_pair(tmp_path)
    example_id = next(
        (candidate for candidate in EXAMPLE_IDS
         if _rank_pair("pooled", candidate) != _rank_pair("per_question", candidate)),
        None)
    assert example_id is not None, "the fixture must differ across settings"
    per_setting = [{row["dense_gold_ranks"] for row
                    in _example_rows(case_rows, setting, example_id)}
                   for setting in CASE_SETTINGS]
    assert all(len(cells) == 1 for cells in per_setting)
    assert per_setting[0] != per_setting[1]

    out = _sentinel(tmp_path, "cross_setting_ranks.html")
    _assert_accepted(
        _run("--summary", summary, "--cases", cases, "--out", str(out)), out)


# ── S5.6: every (setting, k) slice, not the one Figure 3 plots ──────────────
# Each drift moves one example's rerank rank just far enough to change its
# transition at exactly one cutoff of one setting. The rank object stays
# identical across the example's `k` rows, every per-row S5.5 identity holds, the
# key matrix is intact, and the pooled@5 counts Figure 3 draws never move.
NON_PLOTTED_SLICE_DRIFTS = [
    ("pooled", 2, (7, 2), 3, "pooled_k2"),
    ("per_question", 2, (7, 2), 3, "per_question_k2"),
    ("per_question", 5, (8, 3), 6, "per_question_k5"),
]


@pytest.mark.parametrize("setting,k,pair,rerank_second,label",
                         NON_PLOTTED_SLICE_DRIFTS)
def test_summary_drift_in_a_non_plotted_slice_refuses(
        tmp_path, setting, k, pair, rerank_second, label):
    """A slice-local check would accept this file at one cutoff and refuse the
    *identical* file at another, so whether it is the frozen artifact would
    depend on which cutoff the operator happens to render."""
    _, _, _, case_rows = _fixture_pair(tmp_path)
    control = [dict(row) for row in case_rows]
    _retarget_example(case_rows, setting, _example_with_pair(setting, pair),
                      rerank_second=rerank_second)

    # The counts of the plotted slice really are intact, so the probe is not
    # caught incidentally by the combination Figure 3 happens to draw.
    def plotted_counts(rows):
        return Counter(row["transition"] for row in rows
                       if (row["setting"], row["k"]) == ("pooled", "5"))

    assert plotted_counts(case_rows) == plotted_counts(control)

    _cases_probe(tmp_path, "slice_%s" % label, case_rows,
                 "disagrees with the accepted summary at (%s, k=%d" % (setting, k),
                 control_rows=control)


# ── S5.2 / aggregate S2: the example-bound fields across all five rows ──────
def _drift(row, column):
    """Change exactly one example-bound field, keeping every other rule true."""
    if column == "question_type":
        row[column] = "comparison" if row[column] == "bridge" else "bridge"
    elif column == "level":
        row[column] = "easy"
    elif column == "question":
        row[column] = "Which one came second?"
    else:
        # The rank objects are keyed by the row's gold titles, so they are
        # rewritten too: otherwise the S5.3 key check would fire first and the
        # cross-row binding would never be reached.
        row["gold_titles"] = "%s | %s" % (GOLD_A, "Gold C")
        for stage in ("dense", "rerank"):
            ranks = json.loads(row["%s_gold_ranks" % stage])
            row["%s_gold_ranks" % stage] = json.dumps(
                {GOLD_A: ranks[GOLD_A], "Gold C": ranks[GOLD_B]},
                separators=(",", ":"), ensure_ascii=False)
    return row


@pytest.mark.parametrize("column", ["question_type", "level", "question",
                                    "gold_titles"])
@pytest.mark.parametrize("setting,k,label", [
    ("pooled", "10", "across_k"),
    ("per_question", "2", "across_setting"),
])
def test_same_example_metadata_drift_refuses(tmp_path, column, setting, k, label):
    """One example_id cannot carry two identities across its five rows.

    The drifted row is never the plotted slice and every key, rank, hit cell,
    transition and S5.6 count is unchanged, so the file is rejected purely for
    the contradiction between rows of one example.
    """
    _, _, _, case_rows = _fixture_pair(tmp_path)
    control = [dict(row) for row in case_rows]
    example_id = case_rows[0]["example_id"]
    victim = next(row for row in case_rows
                  if (row["setting"], row["k"], row["example_id"])
                  == (setting, k, example_id))
    _drift(victim, column)
    _cases_probe(tmp_path, "meta_%s_%s" % (label, column), case_rows,
                 "carries the same value", control_rows=control)


def test_absent_requested_combination_refuses(tmp_path):
    _, cases, _, _ = _fixture_pair(tmp_path)
    loaded = prd.load_cases(cases)
    with pytest.raises(SystemExit) as excinfo:
        prd.select_cases(loaded, "per_question", 10)
    assert "no rows for" in str(excinfo.value)


# ── CLI wiring for the third figure ─────────────────────────────────────────
def test_cli_renders_three_figures(tmp_path):
    summary, cases, _, _ = _fixture_pair(tmp_path)
    out = tmp_path / "out.html"
    result = subprocess.run(
        [sys.executable, SCRIPT, "--summary", summary, "--cases", cases,
         "--out", str(out)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    page = out.read_text(encoding="utf-8")
    assert page.count("<figure>") == 3
    assert "Cell view" in page


def test_no_cases_renders_only_two_figures(tmp_path):
    summary, _, _, _ = _fixture_pair(tmp_path)
    out = tmp_path / "out.html"
    result = subprocess.run(
        [sys.executable, SCRIPT, "--summary", summary, "--out", str(out),
         "--no-cases"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    page = out.read_text(encoding="utf-8")
    assert page.count("<figure>") == 2
    assert "Cell view" not in page


def test_missing_cases_file_refuses(tmp_path):
    summary, _, _, _ = _fixture_pair(tmp_path)
    out = tmp_path / "out.html"
    result = subprocess.run(
        [sys.executable, SCRIPT, "--summary", summary,
         "--cases", str(tmp_path / "absent.csv"), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "cases file not found" in (result.stderr + result.stdout)
    assert not out.exists()


def test_three_figure_render_is_deterministic(tmp_path):
    summary, cases, _, _ = _fixture_pair(tmp_path)
    first, second = tmp_path / "a.html", tmp_path / "b.html"
    for out in (first, second):
        result = subprocess.run(
            [sys.executable, SCRIPT, "--summary", summary, "--cases", cases,
             "--out", str(out)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
    assert first.read_bytes() == second.read_bytes()
