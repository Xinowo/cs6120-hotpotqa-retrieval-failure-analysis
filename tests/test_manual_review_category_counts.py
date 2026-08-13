"""Tests for the calibration category counts.

The contract under test is section 8 of
`docs/specs/2026-07-27-manual-failure-review-course-protocol.md`: the counts come
only from the 30 rows of `final_labels.csv`, the denominator is always 30, and
the named-category counts plus `unresolved` equal 30.

Each rejection below differs from the legal control in exactly one property, so a
validator that accepts both halves of a pair has not implemented the contract.
The committed workspace is exercised separately, and skipped when absent.
"""

import io
import os
import sys

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.reporting import manual_review_category_counts as mcc


HEADER = ",".join(mcc.LABEL_COLUMNS)

# A synthetic legal control: 30 unique units, 15 bm25 and 15 dense, using the
# real vocabulary. The distribution is deliberately not the committed one, so a
# test that passed by hard-coding the shipped numbers would fail here.
def _synthetic_rows():
    rows = []
    plan = [
        ("bm25_minimal_preprocessing_score_distortion", 8, 0),
        ("description_only_bridge_entity", 0, 6),
        ("cross_passage_conjunction_unresolved", 4, 4),
        ("near_neighbour_crowding_and_sense_drift", 2, 3),
        ("dense_peripheral_passage_content_dilution", 0, 1),
        ("evaluation_side_gold_chain_ambiguity", 1, 0),
        ("unresolved", 0, 1),
    ]
    counter = 0
    for label, bm25, dense in plan:
        for retriever, many in (("bm25", bm25), ("dense", dense)):
            for _ in range(many):
                example_id = "%024x" % counter
                counter += 1
                resolution = "unresolved" if label == "unresolved" else "single_review"
                rows.append([mcc.RUN_ID, example_id, retriever, label, resolution])
    assert len(rows) == 30
    return rows


def _write(path, rows, header=HEADER):
    body = [header] + [",".join(row) for row in rows]
    with io.open(str(path), "wb") as handle:
        handle.write(("\r\n".join(body) + "\r\n").encode("utf-8"))
    return str(path)


@pytest.fixture
def labels(tmp_path):
    return _write(tmp_path / "final_labels.csv", _synthetic_rows())


# --------------------------------------------------------------------------- #
# Legal control
# --------------------------------------------------------------------------- #

def test_the_legal_control_is_accepted_and_counts_to_thirty(labels):
    table = mcc.derive_counts(mcc.load_labels(labels))
    assert len(table) == len(mcc.LABEL_ORDER) + 1
    total = table[-1]
    assert total[1] == mcc.TOTAL_ROW_LABEL
    assert (total[2], total[3], total[4]) == (30, 15, 15)
    named = sum(row[2] for row in table[:-1] if row[1] != "unresolved")
    unresolved = [row for row in table if row[1] == "unresolved"][0][2]
    assert named + unresolved == 30
    assert all(row[5] == 30 for row in table)


def test_the_output_row_order_is_the_taxonomy_order(labels):
    table = mcc.derive_counts(mcc.load_labels(labels))
    assert [row[1] for row in table] == mcc.LABEL_ORDER + [mcc.TOTAL_ROW_LABEL]


def test_the_output_is_crlf_and_deterministic(labels, tmp_path):
    out = tmp_path / "category_counts.csv"
    assert mcc.main(["--labels", labels, "--out", str(out)]) == 0
    first = out.read_bytes()
    assert first.count(b"\r\n") == first.count(b"\n"), "the directory is -text"
    assert not first.startswith(b"\xef\xbb\xbf")
    assert first.startswith(",".join(mcc.OUTPUT_COLUMNS).encode("utf-8"))
    assert mcc.main(["--labels", labels, "--out", str(out)]) == 0
    assert out.read_bytes() == first
    assert mcc.main(["--labels", labels, "--out", str(out), "--check"]) == 0


def test_check_reports_a_corrupted_output_without_rewriting_it(labels, tmp_path):
    out = tmp_path / "category_counts.csv"
    assert mcc.main(["--labels", labels, "--out", str(out)]) == 0
    out.write_bytes(b"SENTINEL")
    assert mcc.main(["--labels", labels, "--out", str(out), "--check"]) == 1
    assert out.read_bytes() == b"SENTINEL"


def test_check_reports_a_missing_output(labels, tmp_path):
    out = tmp_path / "absent.csv"
    assert mcc.main(["--labels", labels, "--out", str(out), "--check"]) == 1
    assert not out.exists()


# --------------------------------------------------------------------------- #
# Rejections, one changed property each
# --------------------------------------------------------------------------- #

def test_a_label_outside_the_closed_vocabulary_is_rejected(tmp_path):
    rows = _synthetic_rows()
    rows[0][3] = "some_new_category"
    path = _write(tmp_path / "final_labels.csv", rows)
    with pytest.raises(mcc.CountsError, match="closed vocabulary"):
        mcc.load_labels(path)


def test_a_twenty_nine_row_file_is_rejected(tmp_path):
    path = _write(tmp_path / "final_labels.csv", _synthetic_rows()[:-1])
    with pytest.raises(mcc.CountsError, match="exactly 30 unit rows"):
        mcc.load_labels(path)


def test_a_repeated_unit_is_rejected(tmp_path):
    rows = _synthetic_rows()
    rows[1][1], rows[1][2] = rows[0][1], rows[0][2]
    path = _write(tmp_path / "final_labels.csv", rows)
    with pytest.raises(mcc.CountsError, match="repeats the unit"):
        mcc.load_labels(path)


def test_a_sixth_column_is_rejected(tmp_path):
    rows = [row + ["extra"] for row in _synthetic_rows()]
    path = _write(tmp_path / "final_labels.csv", rows, HEADER + ",bridge_link")
    with pytest.raises(mcc.CountsError, match="header must be exactly"):
        mcc.load_labels(path)


def test_a_foreign_run_id_is_rejected(tmp_path):
    rows = _synthetic_rows()
    rows[3][0] = "2026-07-17_b"
    path = _write(tmp_path / "final_labels.csv", rows)
    with pytest.raises(mcc.CountsError, match="run_id"):
        mcc.load_labels(path)


def test_a_foreign_resolution_is_rejected(tmp_path):
    rows = _synthetic_rows()
    rows[4][4] = "overlap"
    path = _write(tmp_path / "final_labels.csv", rows)
    with pytest.raises(mcc.CountsError, match="resolution"):
        mcc.load_labels(path)


def test_a_foreign_retriever_is_rejected(tmp_path):
    rows = _synthetic_rows()
    rows[5][2] = "rerank"
    path = _write(tmp_path / "final_labels.csv", rows)
    with pytest.raises(mcc.CountsError, match="retriever"):
        mcc.load_labels(path)


def test_writing_over_the_label_file_is_refused(labels):
    with pytest.raises(mcc.CountsError, match="over the label file"):
        mcc.main(["--labels", labels, "--out", labels])


# --------------------------------------------------------------------------- #
# The committed workspace
# --------------------------------------------------------------------------- #

COMMITTED_LABELS = os.path.join(REPO_ROOT, mcc.DEFAULT_LABELS)


@pytest.mark.skipif(not os.path.isfile(COMMITTED_LABELS),
                    reason="final_labels.csv has not been shipped yet")
def test_the_committed_labels_produce_the_reported_counts():
    """The numbers the report quotes, recomputed from the shipped label file."""
    table = mcc.derive_counts(mcc.load_labels(mcc.DEFAULT_LABELS))
    counts = dict((row[1], (row[2], row[3], row[4])) for row in table)
    assert counts["bm25_minimal_preprocessing_score_distortion"] == (10, 10, 0)
    assert counts["description_only_bridge_entity"] == (4, 0, 4)
    assert counts["cross_passage_conjunction_unresolved"] == (6, 3, 3)
    assert counts["near_neighbour_crowding_and_sense_drift"] == (5, 1, 4)
    assert counts["dense_peripheral_passage_content_dilution"] == (1, 0, 1)
    assert counts["evaluation_side_gold_chain_ambiguity"] == (2, 1, 1)
    assert counts["unresolved"] == (2, 0, 2)
    assert counts[mcc.TOTAL_ROW_LABEL] == (30, 15, 15)


@pytest.mark.skipif(not os.path.isfile(COMMITTED_LABELS),
                    reason="final_labels.csv has not been shipped yet")
def test_the_committed_counts_file_matches_its_derivation():
    if not os.path.isfile(os.path.join(REPO_ROOT, mcc.DEFAULT_OUT)):
        pytest.skip("category_counts.csv has not been generated yet")
    assert mcc.main(["--check"]) == 0
