"""
demo.py   ->  place at  demo.py  (repository root)

Offline walkthrough of the project's accepted retrieval results.
Spec: docs/specs/2026-08-14-offline-demo.md
Inputs:  results/main_results_v1.csv          (headline comparison, §4.1)
         results/disagreement_cases.csv       (one BM25-vs-dense case, §4.2)
         results/rerank_rescue_damage_cases.csv (one rescue, one damage, §4.3)
Output:  formatted text on stdout; no file is written

This is a presentation layer over artifacts that were already produced and
accepted. It computes no metric, defines no failure category, and re-runs no
retrieval: every figure it prints is read from a CSV cell, so it cannot
disagree with the results it displays. There is no live mode, and no network or
model-download path exists here (spec §2).

The script fails closed. A missing file, a missing column, or a selection rule
that matches no row exits non-zero before anything is printed, because a
silently omitted section would read as a result (spec §5).

Usage:
    python demo.py
    python demo.py --results-dir results
"""

import argparse
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RESULTS_DIR = os.path.join(HERE, "results")

MAIN_RESULTS_FILE = "main_results_v1.csv"
DISAGREEMENT_FILE = "disagreement_cases.csv"
RESCUE_DAMAGE_FILE = "rerank_rescue_damage_cases.csv"

# The cells each section reads (spec §3). Columns beyond these may exist; the
# demo never consumes them.
MAIN_RESULTS_COLUMNS = [
    "Method",
    "Any Evidence Hit Rate@2", "Any Evidence Hit Rate@5", "Any Evidence Hit Rate@10",
    "Full Evidence Hit Rate@2", "Full Evidence Hit Rate@5", "Full Evidence Hit Rate@10",
    "Evidence Recall@5", "MRR@10", "MRR@50",
]
DISAGREEMENT_COLUMNS = [
    "example_id", "question", "gold_titles", "k", "bm25_hit", "dense_hit",
    "direction", "bm25_retrieved_titles", "dense_retrieved_titles",
]
RESCUE_DAMAGE_COLUMNS = [
    "setting", "example_id", "question", "gold_titles", "k",
    "dense_gold_ranks", "rerank_gold_ranks", "transition",
]

TITLE_SEPARATOR = " | "
GOLD_MARKER = "[gold]"
NOT_RETRIEVED = "not retrieved"

SECTION_1_HEADING = "1. Headline comparison: BM25, dense, and dense + reranking"
SECTION_2_HEADING = "2. One question BM25 misses and dense finds"
SECTION_3_HEADING = "3. What the reranker rescues, and what it damages"

# The criterion §4.1 points the reader at, named exactly as the CSV spells it.
PRIMARY_CRITERION_COLUMN = "Full Evidence Hit Rate@5"


class DemoError(Exception):
    """An input the demo cannot honestly display. Always fatal (spec §5)."""


# ───────────────────────────── input handling ────────────────────────────────

def read_input(path, required_columns):
    """Read one accepted result CSV, or fail with a message naming it.

    Cells are read as text so the demo prints them exactly as the file spells
    them: `1.000` stays `1.000` rather than becoming `1.0`.
    """
    if not os.path.isfile(path):
        raise DemoError(
            f"{path}: input file not found. demo.py displays checked-in "
            f"results and cannot regenerate them; run the pipeline in "
            f"README.md 'Running the formal experiments' first."
        )
    try:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as error:                       # malformed CSV bytes
        raise DemoError(f"{path}: could not be read as CSV ({error}).")

    missing = [c for c in required_columns if c not in frame.columns]
    if missing:
        raise DemoError(
            f"{path}: expected column(s) {missing} are absent; found "
            f"{list(frame.columns)}."
        )
    if frame.empty:
        raise DemoError(f"{path}: file holds a header but no data rows.")
    return frame


def select_first(frame, mask, path, description):
    """First row matching `mask` after sorting by example_id (spec §4.2/§4.3)."""
    selected = frame[mask]
    if selected.empty:
        raise DemoError(f"{path}: no row matches {description}.")
    return selected.sort_values("example_id", kind="mergesort").iloc[0]


def split_titles(cell):
    """Split a ` | `-separated title list (spec §3)."""
    return [title for title in cell.split(TITLE_SEPARATOR) if title]


def parse_rank_map(cell, path, column, example_id):
    """Parse a `{title: rank-or-null}` JSON object (spec §3)."""
    try:
        ranks = json.loads(cell)
    except ValueError as error:
        raise DemoError(
            f"{path}: {column} of example {example_id} is not valid JSON ({error})."
        )
    if not isinstance(ranks, dict):
        raise DemoError(
            f"{path}: {column} of example {example_id} must be a JSON object "
            f"mapping a gold title to its rank, got {type(ranks).__name__}."
        )
    return ranks


def rank_label(ranks, title, path, column, example_id):
    """Render one gold title's stored rank; `null` is not a number (spec §4.3)."""
    if title not in ranks:
        raise DemoError(
            f"{path}: {column} of example {example_id} has no entry for gold "
            f"title {title!r}."
        )
    rank = ranks[title]
    if rank is None:
        return NOT_RETRIEVED
    return f"rank {rank}"


# ──────────────────────────────── rendering ──────────────────────────────────

def format_table(frame, columns):
    """Aligned text table; cells verbatim from the file (spec §4.1)."""
    widths = [
        max([len(column)] + [len(value) for value in frame[column]])
        for column in columns
    ]
    def render(cells):
        first = cells[0].ljust(widths[0])
        rest = [cell.rjust(width) for cell, width in zip(cells[1:], widths[1:])]
        return "  ".join([first] + rest)

    lines = [render(columns), render(["-" * width for width in widths])]
    lines.extend(render([row[column] for column in columns])
                 for _, row in frame.iterrows())
    return lines


def mark_gold(titles, gold_titles):
    """Pair each shown title with whether it is one of this row's gold titles.

    Display formatting only: the demo marks titles, it does not decide hits.
    Whatever it marks must agree with the row's own hit cells (spec §4.2, §6.3).
    """
    gold = set(gold_titles)
    return [(title, title in gold) for title in titles]


def print_heading(heading):
    print()
    print(heading)
    print("=" * len(heading))
    print()


def print_headline_comparison(main_results):
    print_heading(SECTION_1_HEADING)
    for line in format_table(main_results, MAIN_RESULTS_COLUMNS):
        print(line)
    print()
    print(
        f"The project's primary criterion is the {PRIMARY_CRITERION_COLUMN} "
        f"column: it asks whether"
    )
    print(
        "every gold paragraph a multi-hop question needs was retrieved, not "
        "merely whether one"
    )
    print(
        "of them was. Separating \"recovered some evidence\" from \"recovered "
        "all the evidence"
    )
    print("needed to answer\" is what this project is about.")


def print_disagreement(row, path):
    print_heading(SECTION_2_HEADING)
    k = int(row["k"])
    gold_titles = split_titles(row["gold_titles"])

    print(f"Example {row['example_id']} (pooled corpus, full evidence, k = {k})")
    print()
    print(f"  Question:    {row['question']}")
    print(f"  Gold titles: {TITLE_SEPARATOR.join(gold_titles)}")

    for label, column in (("BM25", "bm25_retrieved_titles"),
                          ("Dense", "dense_retrieved_titles")):
        titles = split_titles(row[column])
        if len(titles) < k:
            raise DemoError(
                f"{path}: {column} of example {row['example_id']} holds "
                f"{len(titles)} titles, fewer than the k = {k} the row was "
                f"scored at."
            )
        print()
        print(f"  {label}, top {k} of the {len(titles)} titles stored in this row:")
        for rank, (title, is_gold) in enumerate(mark_gold(titles[:k], gold_titles), 1):
            marker = f" {GOLD_MARKER}" if is_gold else ""
            print(f"    {rank}. {title}{marker}")

    print()
    print(
        f"  Full evidence hit at k = {k}: BM25 {row['bm25_hit']}, "
        f"dense {row['dense_hit']}."
    )


def print_rank_transition(label, row, path):
    k = int(row["k"])
    gold_titles = split_titles(row["gold_titles"])
    dense_ranks = parse_rank_map(
        row["dense_gold_ranks"], path, "dense_gold_ranks", row["example_id"])
    rerank_ranks = parse_rank_map(
        row["rerank_gold_ranks"], path, "rerank_gold_ranks", row["example_id"])

    print(f"  {label}: example {row['example_id']} (pooled corpus, k = {k})")
    print()
    print(f"    Question: {row['question']}")
    print()
    for title in gold_titles:
        before = rank_label(
            dense_ranks, title, path, "dense_gold_ranks", row["example_id"])
        after = rank_label(
            rerank_ranks, title, path, "rerank_gold_ranks", row["example_id"])
        print(f"    {title}")
        print(f"      dense {before}  ->  reranked {after}")


def print_rescue_and_damage(rescue_row, damage_row, path):
    print_heading(SECTION_3_HEADING)
    print_rank_transition("Rescue", rescue_row, path)
    print()
    print_rank_transition("Damage", damage_row, path)
    print()
    print(
        "The reranker moves questions in both directions. Reporting only the "
        "rescues would"
    )
    print("misrepresent the result, so one of each is shown.")


# ───────────────────────────────── driver ────────────────────────────────────

def run(results_dir):
    """Read every input and select every row first, then print (spec §5)."""
    main_path = os.path.join(results_dir, MAIN_RESULTS_FILE)
    disagreement_path = os.path.join(results_dir, DISAGREEMENT_FILE)
    rescue_damage_path = os.path.join(results_dir, RESCUE_DAMAGE_FILE)

    main_results = read_input(main_path, MAIN_RESULTS_COLUMNS)
    disagreement = read_input(disagreement_path, DISAGREEMENT_COLUMNS)
    rescue_damage = read_input(rescue_damage_path, RESCUE_DAMAGE_COLUMNS)

    # The disagreement file is already restricted to pooled / full evidence /
    # k = 5, so direction is the only selection this section makes (§4.2).
    disagreement_row = select_first(
        disagreement, disagreement["direction"] == "dense_only",
        disagreement_path, 'direction == "dense_only"',
    )
    pooled_at_5 = (rescue_damage["setting"] == "pooled") & (rescue_damage["k"] == "5")
    rescue_row = select_first(
        rescue_damage, pooled_at_5 & (rescue_damage["transition"] == "rescue"),
        rescue_damage_path, 'setting == "pooled", k == 5, transition == "rescue"',
    )
    damage_row = select_first(
        rescue_damage, pooled_at_5 & (rescue_damage["transition"] == "damage"),
        rescue_damage_path, 'setting == "pooled", k == 5, transition == "damage"',
    )

    print_headline_comparison(main_results)
    print_disagreement(disagreement_row, disagreement_path)
    print_rescue_and_damage(rescue_row, damage_row, rescue_damage_path)
    print()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Print the project's finding from the accepted result CSVs already "
            "checked into this repository. It reads results/main_results_v1.csv, "
            "results/disagreement_cases.csv, and "
            "results/rerank_rescue_damage_cases.csv, and performs no retrieval: "
            "no network connection, no model download, and no GPU are needed, "
            "and no file is written."
        ),
    )
    parser.add_argument(
        "--results-dir", default=DEFAULT_RESULTS_DIR,
        help="directory holding the three accepted result CSVs "
             "(default: the results/ directory of this checkout)",
    )
    args = parser.parse_args(argv)
    try:
        run(args.results_dir)
    except DemoError as error:
        print(f"demo.py: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
