"""
manual_review_category_counts.py  ->  scripts/reporting/manual_review_category_counts.py

Calibration / open-coding category counts for the manual review batch.

Spec:    docs/specs/2026-07-27-manual-failure-review-course-protocol.md section 8
Labels:  docs/taxonomy_candidate_v0_1.md section 11 (the closed label vocabulary)
Input:   results/annotations/manual_review_v1/final_labels.csv  (30 rows)
Output:  results/annotations/manual_review_v1/category_counts.csv  (7 rows + TOTAL)

Section 8 of the protocol says the counts for this batch are computed **only**
from the 30 rows of `final_labels.csv`, that the denominator is always 30, and
that the named-category counts plus the `unresolved` count must equal 30. This
script is that computation, so the numbers quoted in the report are derived from
the shipped label file rather than copied from a document that might drift away
from it.

It validates before it counts, and refuses rather than guesses:

  - the header is exactly the protocol's five columns, in order;
  - exactly 30 rows, each a unique `(example_id, retriever)` unit;
  - `run_id` is `2026-07-17_a` on every row, `retriever` is `bm25` or `dense`;
  - `resolution` is one of the protocol's four values;
  - every `final_label` is one of the seven values in the candidate taxonomy's
    closed vocabulary. An unknown label is a rejection, not a new row: it would
    mean the label file and the taxonomy document had come apart, which is the
    one failure this script exists to catch;
  - the counts sum to 30 after counting, checked against the row count.

`--check` re-derives everything and byte-compares it with the file on disk
without writing, so a reader can confirm the committed counts instead of
trusting them.

Byte note: `results/annotations/** -text` in the root `.gitattributes` exempts
this directory from end-of-line conversion, so whatever this script writes is
what Git stores and checks out. It therefore writes CRLF explicitly, matching
`final_labels.csv` beside it, instead of inheriting the platform default.

AI-USAGE BOUNDARY: this module is plumbing. It defines no category, judges no
unit and decides no label. The category definitions, their boundaries and the
30 labels are human-authored research content; this only tallies the shipped
file and refuses inputs that contradict the protocol.

Usage:
    python scripts/reporting/manual_review_category_counts.py
    python scripts/reporting/manual_review_category_counts.py --check
    python scripts/reporting/manual_review_category_counts.py \
        --labels results/annotations/manual_review_v1/final_labels.csv \
        --out results/annotations/manual_review_v1/category_counts.csv
"""

import argparse
import csv
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

BATCH_DIR = os.path.join("results", "annotations", "manual_review_v1")
DEFAULT_LABELS = os.path.join(BATCH_DIR, "final_labels.csv")
DEFAULT_OUT = os.path.join(BATCH_DIR, "category_counts.csv")

# Frozen input contract (protocol section 8). Not logic, schema.
LABEL_COLUMNS = ["run_id", "example_id", "retriever", "final_label", "resolution"]
RUN_ID = "2026-07-17_a"
RETRIEVERS = ("bm25", "dense")
RESOLUTIONS = ("single_review", "overlap_agreed", "overlap_resolved", "unresolved")
UNIT_TOTAL = 30

# The closed label vocabulary, in the candidate taxonomy's own K1..K6 order with
# `unresolved` last. The order is the output row order, so the counts file reads
# in the same sequence as the document that defines the categories.
LABEL_ORDER = [
    "bm25_minimal_preprocessing_score_distortion",
    "description_only_bridge_entity",
    "cross_passage_conjunction_unresolved",
    "near_neighbour_crowding_and_sense_drift",
    "dense_peripheral_passage_content_dilution",
    "evaluation_side_gold_chain_ambiguity",
    "unresolved",
]

# Output contract.
OUTPUT_COLUMNS = [
    "taxonomy_version", "category", "count", "bm25_count", "dense_count",
    "denominator", "sample_scope",
]
TAXONOMY_VERSION = "candidate_v0_1"
SAMPLE_SCOPE = "manual_review_v1_calibration_batch"
TOTAL_ROW_LABEL = "TOTAL"


class CountsError(Exception):
    """A validation failure. Raised instead of writing a file."""


def _resolve(path):
    return path if os.path.isabs(path) else os.path.join(PROJECT_ROOT, path)


def load_labels(labels_path):
    """Read and validate `final_labels.csv`, returning its 30 rows as dicts."""
    path = _resolve(labels_path)
    if not os.path.isfile(path):
        raise CountsError("the label file does not exist: %s" % labels_path)
    with io.open(path, "rb") as handle:
        raw = handle.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CountsError("the label file carries a UTF-8 BOM")
    reader = csv.reader(io.StringIO(raw.decode("utf-8")))
    table = [row for row in reader if row]
    if not table:
        raise CountsError("the label file is empty")
    header, data = table[0], table[1:]
    if header != LABEL_COLUMNS:
        raise CountsError(
            "the label header must be exactly %s, found %s"
            % (",".join(LABEL_COLUMNS), ",".join(header))
        )
    if len(data) != UNIT_TOTAL:
        raise CountsError(
            "the protocol requires exactly %d unit rows, found %d"
            % (UNIT_TOTAL, len(data))
        )

    rows = []
    seen = set()
    for line, values in enumerate(data, start=2):
        if len(values) != len(LABEL_COLUMNS):
            raise CountsError("line %d has %d fields, expected %d"
                             % (line, len(values), len(LABEL_COLUMNS)))
        row = dict(zip(LABEL_COLUMNS, values))
        if row["run_id"] != RUN_ID:
            raise CountsError("line %d has run_id %r, expected %r"
                             % (line, row["run_id"], RUN_ID))
        if row["retriever"] not in RETRIEVERS:
            raise CountsError("line %d has retriever %r, expected one of %s"
                             % (line, row["retriever"], ", ".join(RETRIEVERS)))
        if row["resolution"] not in RESOLUTIONS:
            raise CountsError("line %d has resolution %r, expected one of %s"
                             % (line, row["resolution"], ", ".join(RESOLUTIONS)))
        if row["final_label"] not in LABEL_ORDER:
            raise CountsError(
                "line %d carries final_label %r, which is not in the candidate "
                "taxonomy's closed vocabulary. Either the label file or "
                "docs/taxonomy_candidate_v0_1.md section 11 is wrong; this "
                "script will not invent a category for it"
                % (line, row["final_label"])
            )
        unit = row["example_id"] + "|" + row["retriever"]
        if unit in seen:
            raise CountsError("line %d repeats the unit %s; the protocol "
                              "requires 30 unique units" % (line, unit))
        seen.add(unit)
        rows.append(row)
    return rows


def derive_counts(rows):
    """Tally the rows into the output table, TOTAL row included."""
    counts = dict((label, [0, 0, 0]) for label in LABEL_ORDER)
    for row in rows:
        tally = counts[row["final_label"]]
        tally[0] += 1
        tally[1 if row["retriever"] == "bm25" else 2] += 1

    table = []
    for label in LABEL_ORDER:
        total, bm25, dense = counts[label]
        table.append([TAXONOMY_VERSION, label, total, bm25, dense,
                      UNIT_TOTAL, SAMPLE_SCOPE])

    named = sum(r[2] for r in table if r[1] != "unresolved")
    unresolved = counts["unresolved"][0]
    if named + unresolved != UNIT_TOTAL:
        raise CountsError(
            "named-category counts %d plus unresolved %d must equal %d"
            % (named, unresolved, UNIT_TOTAL)
        )
    grand = sum(r[2] for r in table)
    bm25_total = sum(r[3] for r in table)
    dense_total = sum(r[4] for r in table)
    if grand != len(rows):
        raise CountsError("the tally is %d but %d rows were read"
                          % (grand, len(rows)))
    table.append([TAXONOMY_VERSION, TOTAL_ROW_LABEL, grand, bm25_total,
                  dense_total, UNIT_TOTAL, SAMPLE_SCOPE])
    return table


def serialize(table):
    """Render the table as the exact bytes the output file must hold."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(OUTPUT_COLUMNS)
    for row in table:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compute the calibration category counts from final_labels.csv."
    )
    parser.add_argument("--labels", default=DEFAULT_LABELS)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true",
                        help="re-derive and byte-compare without writing")
    args = parser.parse_args(argv)

    if os.path.basename(args.out) == os.path.basename(DEFAULT_LABELS):
        raise CountsError("refusing to write over the label file itself")

    rows = load_labels(args.labels)
    payload = serialize(derive_counts(rows))
    out_path = _resolve(args.out)

    if args.check:
        if not os.path.isfile(out_path):
            print("MISSING  %s has not been generated" % args.out)
            return 1
        with io.open(out_path, "rb") as handle:
            on_disk = handle.read()
        if on_disk != payload:
            print("MISMATCH %s differs from the derivation (%d bytes on disk, "
                  "%d derived)" % (args.out, len(on_disk), len(payload)))
            return 1
        print("OK       %s matches the derivation, %d bytes"
              % (args.out, len(payload)))
        print("OK       30 unit rows, denominator %d, counts sum to 30" % UNIT_TOTAL)
        return 0

    directory = os.path.dirname(out_path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    with io.open(out_path, "wb") as handle:
        handle.write(payload)
    print("WROTE    %s, %d bytes" % (args.out, len(payload)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CountsError as error:
        sys.stderr.write("error: %s\n" % error)
        sys.exit(2)
