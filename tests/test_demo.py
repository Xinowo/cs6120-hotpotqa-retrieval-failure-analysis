"""Regression tests for demo.py.

The demo is a presentation layer over accepted result artifacts
(docs/specs/2026-08-14-offline-demo.md), so what these tests guard is its
honesty about those artifacts, not the formatting of its output. They cover
exactly the five obligations in spec §6:

  - the default invocation exits 0 and prints all three sections, since a
    silently omitted section would read as a result;
  - every figure in the headline table is a cell of `results/main_results_v1.csv`
    and every cell of that file is printed -- checked in both directions, and
    once more against a perturbed copy, so a hard-coded number that no longer
    matches the file cannot pass;
  - the gold marking in the disagreement section agrees with that row's own
    `bm25_hit` / `dense_hit` cells, because the marking is display formatting
    and must not imply a hit the accepted results do not record;
  - a missing input file exits non-zero naming that file and prints no partial
    walkthrough, for each of the three inputs;
  - selection is deterministic: two invocations show the same three examples.

Everything here is offline. No test downloads a model or touches a network.
"""

import re
import shutil
import subprocess
import sys

import pandas as pd
import pytest

SCRIPT = "demo.py"
RESULTS_DIR = "results"
MAIN_RESULTS = "results/main_results_v1.csv"
DISAGREEMENT_CASES = "results/disagreement_cases.csv"
RESCUE_DAMAGE_CASES = "results/rerank_rescue_damage_cases.csv"

INPUT_FILES = ["main_results_v1.csv", "disagreement_cases.csv",
               "rerank_rescue_damage_cases.csv"]

SECTION_HEADINGS = [
    "1. Headline comparison: BM25, dense, and dense + reranking",
    "2. One question BM25 misses and dense finds",
    "3. What the reranker rescues, and what it damages",
]

DECIMAL = re.compile(r"\d+\.\d+")
EXAMPLE_ID = re.compile(r"(?:Example|example) ([0-9a-f]+) \(pooled corpus")


def run_demo(results_dir=None):
    """Run the demo as a user would, from the repository root."""
    command = [sys.executable, SCRIPT]
    if results_dir is not None:
        command += ["--results-dir", str(results_dir)]
    return subprocess.run(command, capture_output=True, text=True)


def section(stdout, index):
    """The text of one output section, heading excluded."""
    start = stdout.index(SECTION_HEADINGS[index])
    if index + 1 < len(SECTION_HEADINGS):
        end = stdout.index(SECTION_HEADINGS[index + 1])
    else:
        end = len(stdout)
    return stdout[start + len(SECTION_HEADINGS[index]):end]


def copy_inputs(destination, omit=None):
    """A results directory holding the three inputs, minus an omitted one."""
    destination.mkdir(parents=True, exist_ok=True)
    for name in INPUT_FILES:
        if name != omit:
            shutil.copy(f"{RESULTS_DIR}/{name}", destination / name)
    return destination


@pytest.fixture(scope="module")
def completed():
    result = run_demo()
    assert result.returncode == 0, result.stderr
    return result


# ─────────────────── §6.1  all three sections, exit code 0 ───────────────────

def test_the_default_invocation_prints_all_three_sections(completed):
    for heading in SECTION_HEADINGS:
        assert heading in completed.stdout
    assert completed.stderr == ""


# ─────────────────── §6.2  every headline figure is a CSV cell ───────────────

def test_the_headline_table_prints_exactly_the_cells_of_the_results_file(completed):
    frame = pd.read_csv(MAIN_RESULTS, dtype=str)
    printed = section(completed.stdout, 0)
    cells = {value for column in frame.columns for value in frame[column]}

    # Neither direction alone is enough: printing only some rows would pass a
    # subset check, and a hard-coded extra figure would pass a superset check.
    assert set(DECIMAL.findall(printed)) == {c for c in cells if DECIMAL.fullmatch(c)}
    for method in frame["Method"]:
        assert method in printed
    for _, row in frame.iterrows():
        for column in frame.columns:
            assert row[column] in printed


def test_a_figure_that_disagrees_with_the_results_file_cannot_be_printed(tmp_path):
    """The numbers are read, not remembered: perturb the file and the output moves."""
    results_dir = copy_inputs(tmp_path / "perturbed")
    frame = pd.read_csv(MAIN_RESULTS, dtype=str)
    original = frame.loc[0, "Full Evidence Hit Rate@5"]
    perturbed = "0.001"
    assert perturbed not in set(frame.stack())
    frame.loc[0, "Full Evidence Hit Rate@5"] = perturbed
    frame.to_csv(results_dir / "main_results_v1.csv", index=False)

    result = run_demo(results_dir)
    assert result.returncode == 0, result.stderr
    printed = section(result.stdout, 0)
    assert perturbed in printed
    assert original not in printed


# ────────────── §6.3  gold marking agrees with the row's hit cells ───────────

def selected_disagreement_row():
    frame = pd.read_csv(DISAGREEMENT_CASES, dtype=str)
    selected = frame[frame["direction"] == "dense_only"]
    return selected.sort_values("example_id", kind="mergesort").iloc[0]


def marked_titles(printed, label, k):
    """The shown titles of one retriever, paired with whether they are marked."""
    body = printed.split(f"{label}, top {k} of the")[1]
    shown = []
    for line in body.splitlines():
        match = re.match(r"\s*(\d+)\. (.*)$", line)
        if match is None:
            if shown:
                break
            continue
        title = match.group(2)
        is_marked = title.endswith(" [gold]")
        shown.append((title[: -len(" [gold]")] if is_marked else title, is_marked))
    return shown


@pytest.mark.parametrize("label, hit_column, titles_column", [
    ("BM25", "bm25_hit", "bm25_retrieved_titles"),
    ("Dense", "dense_hit", "dense_retrieved_titles"),
])
def test_gold_marking_agrees_with_the_selected_rows_hit_cells(
        completed, label, hit_column, titles_column):
    row = selected_disagreement_row()
    k = int(row["k"])
    gold_titles = set(row["gold_titles"].split(" | "))
    printed = section(completed.stdout, 1)

    shown = marked_titles(printed, label, k)
    assert [title for title, _ in shown] == row[titles_column].split(" | ")[:k]

    marked = {title for title, is_marked in shown if is_marked}
    unmarked = {title for title, is_marked in shown if not is_marked}
    assert marked <= gold_titles
    assert not (unmarked & gold_titles)

    # The row's criterion is full evidence, so a hit cell of 1 is the statement
    # that *every* gold title is inside the cutoff. A marked title on its own
    # does not imply a hit: one of two gold titles inside the cutoff is a marked
    # title on a row whose hit cell is 0, and 131 of the 320 retriever-units
    # among the file's dense_only rows are exactly that.
    assert (marked == gold_titles) == (int(row[hit_column]) == 1)


# ──────────── §6.4  a missing input fails closed, naming the file ────────────

@pytest.mark.parametrize("omitted", INPUT_FILES)
def test_a_missing_input_file_fails_before_printing_anything(tmp_path, omitted):
    results_dir = copy_inputs(tmp_path / "incomplete", omit=omitted)
    result = run_demo(results_dir)

    assert result.returncode != 0
    assert omitted in result.stderr
    assert result.stdout == ""
    for heading in SECTION_HEADINGS:
        assert heading not in result.stdout


# ───────────────────────── §6.5  selection is deterministic ──────────────────

def test_two_invocations_select_the_same_three_examples(completed):
    second = run_demo()
    assert second.returncode == 0, second.stderr

    first_ids = EXAMPLE_ID.findall(completed.stdout)
    second_ids = EXAMPLE_ID.findall(second.stdout)
    assert len(first_ids) == 3
    assert first_ids == second_ids
    assert first_ids[0] == selected_disagreement_row()["example_id"]
