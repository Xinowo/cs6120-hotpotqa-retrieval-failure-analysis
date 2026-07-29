"""
test_manual_review_page.py

Round-trip acceptance tests for the one shared review page
(scripts/manual_review_page.py), covering the browser-behavior items in section
9 of docs/specs/2026-07-27-manual-failure-review-course-protocol.md:

  - the picker loads each reviewer file and shows the four overlap cases first,
    17 in total;
  - every card's `rank_pattern` is read-only machine context beside a separate
    human label input that is empty by default;
  - saving notes with an empty human label succeeds, and no code path copies
    `rank_pattern` into `label`;
  - browser state is separated by batch and reviewer;
  - each exported CSV has the section 6 header, identity, and 17-row cardinality;
  - cross-reviewer import is rejected;
  - the union of the two exports covers 30 unique units with four duplicated
    overlap units.

These are executed rather than asserted about. The page keeps its contract logic
in one DOM-free `review-contract` script, and each test extracts **those exact
bytes from the generated page** and runs them under Node, so what is checked is
the JavaScript that ships — not a Python re-implementation of it. Tests that need
Node skip cleanly where it is unavailable; the structural properties that can be
checked without it are asserted in `tests/test_build_manual_review_batch.py`.
"""

import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from scripts import build_manual_review_batch as mrb
from scripts import manual_review_page as page

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FORMAL_RUN_DIR = os.path.join(REPO_ROOT, "results", "runs", mrb.SOURCE_RUN_ID)

NODE = shutil.which("node")
requires_node = pytest.mark.skipif(
    NODE is None,
    reason="node is not on PATH, so the page's own JavaScript cannot be executed",
)
requires_formal_run = pytest.mark.skipif(
    not os.path.isdir(FORMAL_RUN_DIR),
    reason=f"the read-only source run results/runs/{mrb.SOURCE_RUN_ID}/ is absent",
)

CONTRACT_SCRIPT_RE = re.compile(
    r'<script id="review-contract">(.*?)</script>', re.DOTALL
)


def contract_source():
    """The page's DOM-free contract script, exactly as it ships."""
    match = CONTRACT_SCRIPT_RE.search(page.render_page())
    assert match, "the page must expose its contract logic in one review-contract script"
    body = match.group(1)
    for browser_only in ("document.", "window.", "localStorage", "FileReader", "Blob("):
        assert browser_only not in body, (
            f"the contract script must stay DOM-free, found {browser_only!r}"
        )
    return body


@pytest.fixture(scope="module")
def contract_js():
    return contract_source()


def run_contract(contract_js, body, payload=None, tmp_path=None):
    """Execute `body` with the page's contract in scope; return its JSON result.

    The script must end by assigning to `result`. Any input is provided as the
    parsed JSON global `INPUT`.
    """
    script = (
        contract_js
        + "\n;(function () {\n"
        + "var INPUT = " + json.dumps(payload if payload is not None else None) + ";\n"
        + "var result;\n"
        + body
        + "\nprocess.stdout.write(JSON.stringify(result));\n"
        + "})();\n"
    )
    path = os.path.join(str(tmp_path), "contract_probe.js")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(script)
    completed = subprocess.run(
        [NODE, path], capture_output=True, text=True, encoding="utf-8"
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


# --------------------------------------------------------------------------- #
# Reviewer files to drive the page with
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def formal_reviewer_files():
    if not os.path.isdir(FORMAL_RUN_DIR):
        pytest.skip("the read-only source run is absent")
    return mrb.build_batch(FORMAL_RUN_DIR).reviewer_files


# ───────────────────────── the contract script itself ────────────────────────

@requires_node
def test_the_contract_script_loads_and_states_the_frozen_values(contract_js, tmp_path):
    values = run_contract(
        contract_js,
        "result = {"
        "  batch: MANUAL_REVIEW_CONTRACT.BATCH_ID,"
        "  run: MANUAL_REVIEW_CONTRACT.RUN_ID,"
        "  cutoff: MANUAL_REVIEW_CONTRACT.REVIEW_CUTOFF,"
        "  cases: MANUAL_REVIEW_CONTRACT.CASES_PER_REVIEWER,"
        "  overlap: MANUAL_REVIEW_CONTRACT.OVERLAP_COUNT,"
        "  columns: MANUAL_REVIEW_CONTRACT.NOTES_COLUMNS,"
        "  fields: MANUAL_REVIEW_CONTRACT.CASE_FIELDS,"
        "  file_fields: MANUAL_REVIEW_CONTRACT.REVIEWER_FILE_FIELDS,"
        "  reviewers: MANUAL_REVIEW_CONTRACT.REVIEWER_IDS"
        "};",
        tmp_path=tmp_path,
    )
    assert values["batch"] == mrb.BATCH_ID
    assert values["run"] == mrb.SOURCE_RUN_ID
    assert values["cutoff"] == mrb.REVIEW_CUTOFF == 5
    assert values["cases"] == mrb.CASES_PER_REVIEWER == 17
    assert values["overlap"] == mrb.OVERLAP_SIZE == 4
    assert tuple(values["columns"]) == page.NOTES_COLUMNS
    assert tuple(values["fields"]) == mrb.CASE_FIELDS
    # The two closed shapes and the frozen reviewer set the page actually ships,
    # read out of the shipped bytes rather than asserted about the Python side.
    assert tuple(values["file_fields"]) == mrb.REVIEWER_FILE_FIELDS
    assert tuple(values["reviewers"]) == mrb.REVIEWER_IDS == ("jiajun", "xin")
    # The page's case contract carries neither human field.
    assert "label" not in values["fields"]
    assert "notes" not in values["fields"]


@requires_node
def test_draft_state_keys_are_separated_by_batch_and_reviewer(contract_js, tmp_path):
    """Xin's and Jiajun's browser state cannot collide (section 5, item 5)."""
    keys = run_contract(
        contract_js,
        "var K = MANUAL_REVIEW_CONTRACT.storageKey;"
        "result = {"
        "  xin: K('manual_review_v1', 'xin'),"
        "  jiajun: K('manual_review_v1', 'jiajun'),"
        "  other_batch: K('manual_review_v2', 'xin')"
        "};",
        tmp_path=tmp_path,
    )
    assert keys["xin"] != keys["jiajun"]
    assert keys["xin"] != keys["other_batch"]
    for reviewer in ("xin", "jiajun"):
        assert "manual_review_v1" in keys[reviewer]
        assert reviewer in keys[reviewer]


# ─────────────────── loading: 17 cases, the four overlap first ───────────────

@requires_node
@requires_formal_run
@pytest.mark.parametrize("reviewer", ["xin", "jiajun"])
def test_the_page_accepts_each_reviewer_file_and_shows_17_cases(
    contract_js, formal_reviewer_files, reviewer, tmp_path
):
    result = run_contract(
        contract_js,
        "var C = MANUAL_REVIEW_CONTRACT;"
        "var error = C.validateReviewerFile(INPUT);"
        "var ordered = error ? [] : C.orderCasesForReview(INPUT.cases);"
        "result = {"
        "  error: error,"
        "  total: ordered.length,"
        "  overlap_flags: ordered.map(function (c) { return c.is_overlap; }),"
        "  labels_present: ordered.some(function (c) {"
        "     return Object.prototype.hasOwnProperty.call(c, 'label'); })"
        "};",
        payload=formal_reviewer_files[reviewer],
        tmp_path=tmp_path,
    )
    assert result["error"] is None
    assert result["total"] == 17
    # The four overlap cases come first, then the 13 private ones.
    assert result["overlap_flags"] == [True] * 4 + [False] * 13
    assert result["labels_present"] is False


@requires_node
@requires_formal_run
def test_the_display_order_is_overlap_first_while_the_file_stays_canonical(
    contract_js, formal_reviewer_files, tmp_path
):
    """The reviewer file keeps the canonical batch order; the page reorders it."""
    payload = formal_reviewer_files["xin"]
    assert [case["is_overlap"] for case in payload["cases"]] != [True] * 4 + [False] * 13

    result = run_contract(
        contract_js,
        "var C = MANUAL_REVIEW_CONTRACT;"
        "var ordered = C.orderCasesForReview(INPUT.cases);"
        "result = {"
        "  keys: ordered.map(C.unitKey),"
        "  original: INPUT.cases.map(C.unitKey)"
        "};",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert sorted(result["keys"]) == sorted(result["original"])
    # Stable within each group: the overlap units keep their canonical relative
    # order, and so do the private ones.
    canonical = result["original"]
    overlap = [k for k in canonical if k in result["keys"][:4]]
    assert result["keys"][:4] == overlap
    assert result["keys"][4:] == [k for k in canonical if k not in overlap]


@requires_node
@requires_formal_run
@pytest.mark.parametrize(
    "mutation, expected",
    [
        ({"batch_id": "other_batch"}, "batch_id must be"),
        ({"run_id": "1999-01-01_z"}, "run_id must be"),
        ({"review_cutoff": 10}, "file-level review_cutoff"),
        ({"review_cutoff": "5"}, "file-level review_cutoff"),
        ({"reviewer_id": ""}, "reviewer_id must be"),
        ({"cases": []}, "expected 17 cases"),
    ],
)
def test_the_page_rejects_a_reviewer_file_that_breaks_the_contract(
    contract_js, formal_reviewer_files, mutation, expected, tmp_path
):
    payload = dict(formal_reviewer_files["xin"])
    payload.update(mutation)
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None and expected in result


@requires_node
@requires_formal_run
@pytest.mark.parametrize("bad", [10, "5", True, 5.5, None])
def test_the_page_independently_rejects_a_bad_per_case_cutoff(
    contract_js, formal_reviewer_files, bad, tmp_path
):
    """RC-NO-1..3 again, enforced by the page rather than by the extractor.

    The reviewer opens a file that arrived by ordinary file exchange, so the page
    repeats the per-case check instead of trusting the bytes.
    """
    payload = json.loads(json.dumps(formal_reviewer_files["xin"]))
    payload["cases"][3]["review_cutoff"] = bad
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None and "review_cutoff as the integer 5" in result


@requires_node
@requires_formal_run
def test_the_page_rejects_a_case_that_carries_a_human_label(
    contract_js, formal_reviewer_files, tmp_path
):
    payload = json.loads(json.dumps(formal_reviewer_files["xin"]))
    payload["cases"][0]["label"] = "distractor dominance"
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None and "carries a label field" in result


# ────────── the closed section-4 shapes and the frozen reviewer set ───────────
#
# The same paired controls the extractor's suite applies to `validate_batch`, run
# here against the bytes the page actually ships. Each rejection is a deep copy of
# the valid generated Xin payload with exactly one property changed, so a
# validator that accepts both halves of a pair has not implemented the closed
# shape. A validator that only checks that the frozen fields are PRESENT accepts
# the legal control below and every rejection under it.


def _mutable(payload):
    """A deep copy of a generated reviewer payload, safe to mutate."""
    return json.loads(json.dumps(payload))


@requires_node
@requires_formal_run
@pytest.mark.parametrize("reviewer", ["xin", "jiajun"])
def test_the_page_accepts_the_exact_generated_shapes(
    contract_js, formal_reviewer_files, reviewer, tmp_path
):
    """The legal half of every pair below: the shipped shapes validate as they are."""
    result = run_contract(
        contract_js,
        "var C = MANUAL_REVIEW_CONTRACT;"
        "result = {"
        "  error: C.validateReviewerFile(INPUT),"
        "  file_shape: C.keySetError(INPUT, C.REVIEWER_FILE_FIELDS),"
        "  case_shapes: INPUT.cases.map(function (c) {"
        "     return C.keySetError(c, C.CASE_FIELDS); }),"
        "  reviewer_known: C.REVIEWER_IDS.indexOf(INPUT.reviewer_id) >= 0"
        "};",
        payload=formal_reviewer_files[reviewer],
        tmp_path=tmp_path,
    )
    assert result["error"] is None
    assert result["file_shape"] is None
    assert result["case_shapes"] == [None] * 17
    assert result["reviewer_known"] is True


@requires_node
@requires_formal_run
@pytest.mark.parametrize(
    "field, value",
    [
        ("notes", {"unit": "a note that does not belong in a delivered file"}),
        ("provenance", "hand-edited"),
    ],
)
def test_the_page_rejects_one_extra_top_level_field(
    contract_js, formal_reviewer_files, field, value, tmp_path
):
    payload = _mutable(formal_reviewer_files["xin"])
    payload[field] = value
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None
    assert "carries unexpected field(s) " + field in result


@requires_node
@requires_formal_run
@pytest.mark.parametrize("field", page.REVIEWER_FILE_FIELDS)
def test_the_page_rejects_a_reviewer_file_missing_a_top_level_field(
    contract_js, formal_reviewer_files, field, tmp_path
):
    """Closed in both directions: a truncated object is not the frozen shape."""
    payload = _mutable(formal_reviewer_files["xin"])
    del payload[field]
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None and "is missing " + field in result


@requires_node
@requires_formal_run
def test_the_page_rejects_a_case_carrying_a_foreign_notes_field(
    contract_js, formal_reviewer_files, tmp_path
):
    """The one mutation that most directly disproves the no-notes contract.

    Section 4 says the delivered file contains no notes from either reviewer, so a
    case arriving with someone's note in it is rejected whole rather than loaded
    and silently displayed.
    """
    payload = _mutable(formal_reviewer_files["xin"])
    payload["cases"][0]["notes"] = "another reviewer note"
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None
    assert "case 1 carries unexpected field(s) notes" in result


@requires_node
@requires_formal_run
@pytest.mark.parametrize(
    "field, value",
    [
        ("failure_reason", "lexical mismatch"),
        ("annotated_at", "2026-07-28T12:00:00Z"),
        ("unexpected_field", 1),
    ],
)
def test_the_page_rejects_another_arbitrary_extra_case_field(
    contract_js, formal_reviewer_files, field, value, tmp_path
):
    payload = _mutable(formal_reviewer_files["xin"])
    payload["cases"][2][field] = value
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None
    assert "case 3 carries unexpected field(s) " + field in result


@requires_node
@requires_formal_run
@pytest.mark.parametrize("field", page.CASE_FIELDS)
def test_the_page_rejects_a_case_missing_one_frozen_field(
    contract_js, formal_reviewer_files, field, tmp_path
):
    payload = _mutable(formal_reviewer_files["xin"])
    del payload["cases"][0][field]
    result = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT);",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result is not None and "is missing " + field in result


@requires_node
@requires_formal_run
@pytest.mark.parametrize("foreign", ["alice", "reviewer3", "xin2"])
def test_the_page_rejects_a_syntactically_valid_foreign_reviewer_id(
    contract_js, formal_reviewer_files, foreign, tmp_path
):
    """`alice` is a valid identifier and still not a reviewer of this batch.

    Accepting one would let this page create isolated draft storage and export a
    notes CSV under an identity outside the frozen assignment, so the identity is
    checked against the frozen two-person set and not merely against syntax.
    """
    assert foreign not in page.REVIEWER_IDS
    payload = _mutable(formal_reviewer_files["xin"])
    payload["reviewer_id"] = foreign
    result = run_contract(
        contract_js,
        "var C = MANUAL_REVIEW_CONTRACT;"
        "result = {"
        "  error: C.validateReviewerFile(INPUT),"
        "  storage_key: C.storageKey(INPUT.batch_id, INPUT.reviewer_id),"
        "  export_name: C.notesFileName(INPUT.reviewer_id)"
        "};",
        payload=payload,
        tmp_path=tmp_path,
    )
    assert result["error"] is not None
    assert "reviewer_id must be one of jiajun, xin" in result["error"]
    # The identity a rejected file would have driven, shown to make the
    # consequence concrete: the page never reaches either of these, because the
    # UI only stores and exports after validateReviewerFile returns null.
    assert foreign in result["storage_key"] and foreign in result["export_name"]


# ─────────────────────────── the notes export (section 6) ────────────────────

def _parse_notes_csv(text):
    assert text.endswith("\r\n")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    return rows[0], rows[1:]


@requires_node
@requires_formal_run
@pytest.mark.parametrize("reviewer", ["xin", "jiajun"])
def test_an_export_with_no_notes_at_all_still_has_17_rows(
    contract_js, formal_reviewer_files, reviewer, tmp_path
):
    """Saving with an empty human label — and an empty note — succeeds.

    One row per displayed unit, always: an empty note simply means that unit is
    not complete yet, and `label` may stay empty through open coding.
    """
    text = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.buildNotesCsv("
        "  INPUT, {}, '2026-07-28T12:00:00.000Z');",
        payload=formal_reviewer_files[reviewer],
        tmp_path=tmp_path,
    )
    header, rows = _parse_notes_csv(text)
    assert tuple(header) == page.NOTES_COLUMNS
    assert len(rows) == 17
    for row in rows:
        record = dict(zip(header, row))
        assert record["batch_id"] == mrb.BATCH_ID
        assert record["run_id"] == mrb.SOURCE_RUN_ID
        assert record["review_cutoff"] == "5"
        assert record["annotator"] == reviewer
        assert record["label"] == ""
        assert record["notes"] == ""
        assert record["annotated_at"] == "2026-07-28T12:00:00.000Z"


@requires_node
@requires_formal_run
def test_an_export_carries_notes_with_an_empty_label_and_never_the_machine_pattern(
    contract_js, formal_reviewer_files, tmp_path
):
    payload = formal_reviewer_files["xin"]
    first = payload["cases"][0]
    drafts = {
        f'{first["example_id"]}::{first["retriever"]}': {
            "label": "",
            "notes": "Observed: both golds absent from the top 5, one absent entirely.",
            "annotated_at": "2026-07-28T11:30:00Z",
        }
    }
    text = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.buildNotesCsv("
        "  INPUT.payload, INPUT.drafts, '2026-07-28T12:00:00.000Z');",
        payload={"payload": payload, "drafts": drafts},
        tmp_path=tmp_path,
    )
    header, rows = _parse_notes_csv(text)
    records = [dict(zip(header, row)) for row in rows]
    written = next(
        r for r in records
        if (r["example_id"], r["retriever"]) == (first["example_id"], first["retriever"])
    )
    assert written["notes"].startswith("Observed:")
    assert written["label"] == ""
    assert written["annotated_at"] == "2026-07-28T11:30:00Z"

    # No exported label ever equals a machine rank pattern for its own unit.
    patterns = {
        (case["example_id"], case["retriever"]): case["rank_pattern"]
        for case in payload["cases"]
    }
    for record in records:
        assert record["label"] == "" or record["label"] != patterns[
            (record["example_id"], record["retriever"])
        ]


@requires_node
@requires_formal_run
def test_an_export_quotes_a_multiline_note_without_losing_a_row(
    contract_js, formal_reviewer_files, tmp_path
):
    """The note template is multi-line, so the CSV must survive embedded newlines."""
    payload = formal_reviewer_files["jiajun"]
    case = payload["cases"][2]
    note = (
        "Observed: gold ranked 31.\r\n"
        'Missing gold: "Second hop", comma, and quote " included.\n'
        "Possible reason: lexical drift."
    )
    text = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.buildNotesCsv("
        "  INPUT.payload, INPUT.drafts, '2026-07-28T12:00:00.000Z');",
        payload={
            "payload": payload,
            "drafts": {
                f'{case["example_id"]}::{case["retriever"]}': {
                    "label": "lexical drift",
                    "notes": note,
                    "annotated_at": "2026-07-28T11:00:00Z",
                }
            },
        },
        tmp_path=tmp_path,
    )
    header, rows = _parse_notes_csv(text)
    assert len(rows) == 17
    record = next(
        dict(zip(header, row)) for row in rows
        if (row[header.index("example_id")], row[header.index("retriever")])
        == (case["example_id"], case["retriever"])
    )
    assert record["notes"] == note
    assert record["label"] == "lexical drift"


@requires_node
@requires_formal_run
def test_the_union_of_both_exports_covers_30_units_with_four_duplicated(
    contract_js, formal_reviewer_files, tmp_path
):
    """Double review adds review actions, not unique units (section 9)."""
    all_rows = []
    for reviewer in ("xin", "jiajun"):
        text = run_contract(
            contract_js,
            "result = MANUAL_REVIEW_CONTRACT.buildNotesCsv("
            "  INPUT, {}, '2026-07-28T12:00:00.000Z');",
            payload=formal_reviewer_files[reviewer],
            tmp_path=tmp_path,
        )
        header, rows = _parse_notes_csv(text)
        records = [dict(zip(header, row)) for row in rows]
        assert {r["annotator"] for r in records} == {reviewer}
        all_rows.extend(records)

    assert len(all_rows) == 34
    keys = [(r["example_id"], r["retriever"]) for r in all_rows]
    assert len(set(keys)) == 30
    duplicated = {key for key in keys if keys.count(key) == 2}
    assert len(duplicated) == 4
    assert duplicated == set(mrb.FROZEN_OVERLAP_KEYS)


@requires_node
@requires_formal_run
def test_an_export_never_contains_the_other_reviewers_rows(
    contract_js, formal_reviewer_files, tmp_path
):
    xin_private = {
        (c["example_id"], c["retriever"])
        for c in formal_reviewer_files["xin"]["cases"] if not c["is_overlap"]
    }
    text = run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.buildNotesCsv("
        "  INPUT, {}, '2026-07-28T12:00:00.000Z');",
        payload=formal_reviewer_files["jiajun"],
        tmp_path=tmp_path,
    )
    header, rows = _parse_notes_csv(text)
    keys = {(row[header.index("example_id")], row[header.index("retriever")])
            for row in rows}
    assert not (keys & xin_private)


# ───────────────── notes import: own file accepted, others rejected ──────────

def _export(contract_js, payload, drafts, tmp_path, exported_at="2026-07-28T12:00:00.000Z"):
    return run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.buildNotesCsv("
        f"  INPUT.payload, INPUT.drafts, {exported_at!r});",
        payload={"payload": payload, "drafts": drafts},
        tmp_path=tmp_path,
    )


def _import(contract_js, payload, csv_text, tmp_path):
    return run_contract(
        contract_js,
        "result = MANUAL_REVIEW_CONTRACT.validateNotesImport(INPUT.payload, INPUT.csv);",
        payload={"payload": payload, "csv": csv_text},
        tmp_path=tmp_path,
    )


@requires_node
@requires_formal_run
@pytest.mark.parametrize("reviewer", ["xin", "jiajun"])
def test_a_reviewer_can_re_import_their_own_export_unchanged(
    contract_js, formal_reviewer_files, reviewer, tmp_path
):
    """The full round trip: export, re-import, and the notes come back verbatim."""
    payload = formal_reviewer_files[reviewer]
    case = payload["cases"][1]
    key = f'{case["example_id"]}::{case["retriever"]}'
    drafts = {
        key: {
            "label": "",
            "notes": 'Observed: distractor "X, Y" outranks the gold.\nUncertain.',
            "annotated_at": "2026-07-28T10:15:30Z",
        }
    }
    text = _export(contract_js, payload, drafts, tmp_path)
    result = _import(contract_js, payload, text, tmp_path)
    assert result["ok"] is True, result.get("error")
    assert len(result["drafts"]) == 17
    assert result["drafts"][key]["notes"] == drafts[key]["notes"]
    assert result["drafts"][key]["label"] == ""
    assert result["drafts"][key]["annotated_at"] == "2026-07-28T10:15:30Z"


@requires_node
@requires_formal_run
def test_importing_the_other_reviewers_export_is_rejected(
    contract_js, formal_reviewer_files, tmp_path
):
    """Cross-reviewer import is rejected (section 5, item 9; section 9)."""
    jiajun_export = _export(contract_js, formal_reviewer_files["jiajun"], {}, tmp_path)
    result = _import(contract_js, formal_reviewer_files["xin"], jiajun_export, tmp_path)
    assert result["ok"] is False
    assert "not the active reviewer" in result["error"]
    assert "jiajun" in result["error"]


@requires_node
@requires_formal_run
def test_importing_a_file_from_another_batch_is_rejected(
    contract_js, formal_reviewer_files, tmp_path
):
    payload = formal_reviewer_files["xin"]
    text = _export(contract_js, payload, {}, tmp_path)
    tampered = text.replace(mrb.BATCH_ID, "manual_review_v2")
    result = _import(contract_js, payload, tampered, tmp_path)
    assert result["ok"] is False
    assert "does not match this reviewer file" in result["error"]


@requires_node
@requires_formal_run
@pytest.mark.parametrize(
    "column, replacement, expected",
    [
        ("run_id", "1999-01-01_z", "does not match this reviewer file"),
        ("review_cutoff", "10", "review_cutoff must be 5"),
        ("annotated_at", "2026-02-30T00:00:00Z", "not a valid ISO 8601"),
        ("annotated_at", "not-a-timestamp", "not a valid ISO 8601"),
    ],
)
def test_an_import_row_that_breaks_the_contract_is_rejected(
    contract_js, formal_reviewer_files, column, replacement, expected, tmp_path
):
    payload = formal_reviewer_files["xin"]
    text = _export(contract_js, payload, {}, tmp_path)
    header, rows = _parse_notes_csv(text)
    index = list(header).index(column)
    rows[2][index] = replacement
    rebuilt = "\r\n".join(
        [",".join(header)] + [",".join(_quote(f) for f in row) for row in rows]
    ) + "\r\n"
    result = _import(contract_js, payload, rebuilt, tmp_path)
    assert result["ok"] is False
    assert expected in result["error"], result["error"]


def _quote(field):
    if any(ch in field for ch in ',"\r\n'):
        return '"' + field.replace('"', '""') + '"'
    return field


@requires_node
@requires_formal_run
def test_an_import_missing_a_row_is_rejected(
    contract_js, formal_reviewer_files, tmp_path
):
    payload = formal_reviewer_files["xin"]
    text = _export(contract_js, payload, {}, tmp_path)
    header, rows = _parse_notes_csv(text)
    rows.pop()
    rebuilt = "\r\n".join(
        [",".join(header)] + [",".join(_quote(f) for f in row) for row in rows]
    ) + "\r\n"
    result = _import(contract_js, payload, rebuilt, tmp_path)
    assert result["ok"] is False
    assert "expected 17 data rows" in result["error"]


@requires_node
@requires_formal_run
def test_an_import_with_a_duplicated_unit_is_rejected(
    contract_js, formal_reviewer_files, tmp_path
):
    payload = formal_reviewer_files["xin"]
    text = _export(contract_js, payload, {}, tmp_path)
    header, rows = _parse_notes_csv(text)
    rows[1] = list(rows[0])
    rebuilt = "\r\n".join(
        [",".join(header)] + [",".join(_quote(f) for f in row) for row in rows]
    ) + "\r\n"
    result = _import(contract_js, payload, rebuilt, tmp_path)
    assert result["ok"] is False
    assert "duplicate row" in result["error"]


@requires_node
@requires_formal_run
def test_an_import_naming_a_unit_outside_this_reviewers_cases_is_rejected(
    contract_js, formal_reviewer_files, tmp_path
):
    payload = formal_reviewer_files["xin"]
    text = _export(contract_js, payload, {}, tmp_path)
    header, rows = _parse_notes_csv(text)
    rows[5][list(header).index("example_id")] = "ffffffffffffffffffffffff"
    rebuilt = "\r\n".join(
        [",".join(header)] + [",".join(_quote(f) for f in row) for row in rows]
    ) + "\r\n"
    result = _import(contract_js, payload, rebuilt, tmp_path)
    assert result["ok"] is False
    assert "is not one of your cases" in result["error"]


@requires_node
@requires_formal_run
@pytest.mark.parametrize(
    "header_line",
    [
        "batch_id,run_id,example_id,retriever,review_cutoff,label,notes,annotator",
        "run_id,batch_id,example_id,retriever,review_cutoff,label,notes,annotator,annotated_at",
        "batch_id,run_id,example_id,retriever,k,label,notes,annotator,annotated_at",
    ],
)
def test_an_import_with_the_wrong_header_is_rejected(
    contract_js, formal_reviewer_files, header_line, tmp_path
):
    payload = formal_reviewer_files["xin"]
    text = _export(contract_js, payload, {}, tmp_path)
    body = text.split("\r\n", 1)[1]
    result = _import(contract_js, payload, header_line + "\r\n" + body, tmp_path)
    assert result["ok"] is False


@requires_node
def test_the_shared_iso_validator_rejects_impossible_dates(contract_js, tmp_path):
    """One validator for export and import, so a false timestamp cannot pass."""
    cases = {
        "2026-07-28T12:00:00Z": True,
        "2026-07-28T12:00:00.123Z": True,
        "2024-02-29T00:00:00Z": True,
        "2026-07-28T08:00:00-04:00": True,
        "2026-07-28T08:00:00-0400": True,
        "2026-07-28T12:00:00": True,
        "2026-02-30T00:00:00Z": False,
        "2025-02-29T00:00:00Z": False,
        "2026-04-31T00:00:00Z": False,
        "2026-13-01T00:00:00Z": False,
        "2026-07-28T24:00:00Z": False,
        "2026-07-28T12:00:00+05:60": False,
        "2026-07-28T12:00:00+99:00": False,
        "": False,
        "yesterday": False,
    }
    result = run_contract(
        contract_js,
        "var f = MANUAL_REVIEW_CONTRACT.isValidIso;"
        "result = {};"
        "INPUT.forEach(function (v) { result[v] = f(v); });",
        payload=list(cases),
        tmp_path=tmp_path,
    )
    assert result == {value: expected for value, expected in cases.items()}


@requires_node
def test_the_notes_file_name_is_per_reviewer(contract_js, tmp_path):
    names = run_contract(
        contract_js,
        "var f = MANUAL_REVIEW_CONTRACT.notesFileName;"
        "result = { xin: f('xin'), jiajun: f('jiajun') };",
        tmp_path=tmp_path,
    )
    assert names == {"xin": "xin_notes.csv", "jiajun": "jiajun_notes.csv"}


# ───────────────── the generated page on disk is the tested page ─────────────

@requires_formal_run
def test_the_written_page_contains_the_contract_that_was_tested(tmp_path):
    """The bytes exercised above are the bytes the extractor writes."""
    out_dir = tmp_path / "mrv1"
    mrb.generate_batch(out_dir=str(out_dir))
    with io.open(str(out_dir / mrb.PAGE_NAME), encoding="utf-8", newline="") as fh:
        written = fh.read()
    assert written == page.render_page()
    assert CONTRACT_SCRIPT_RE.search(written).group(1) == contract_source()
    page.verify_page_contract(written)


@requires_node
@requires_formal_run
def test_the_delivered_page_file_enforces_the_closed_shapes(
    formal_reviewer_files, tmp_path
):
    """The closed-shape probes, run against the page file the reviewers receive.

    Every other page test extracts the contract from `render_page()`. This one
    reads `results/annotations/manual_review_v1/failure_review.html` off disk and
    executes *those* bytes, so a workspace left stale after a contract change
    fails here instead of shipping a permissive page to the other reviewer.
    """
    delivered = os.path.join(
        REPO_ROOT, "results", "annotations", mrb.BATCH_ID, mrb.PAGE_NAME
    )
    if not os.path.isfile(delivered):
        pytest.skip("the manual_review_v1 workspace has not been generated yet")
    with io.open(delivered, encoding="utf-8", newline="") as fh:
        shipped = fh.read()
    page.verify_page_contract(shipped)
    shipped_contract = CONTRACT_SCRIPT_RE.search(shipped).group(1)

    valid = formal_reviewer_files["xin"]
    probes = {"legal control": _mutable(valid)}

    extra_top = _mutable(valid)
    extra_top["provenance"] = "hand-edited"
    probes["extra top-level field"] = extra_top

    case_notes = _mutable(valid)
    case_notes["cases"][0]["notes"] = "another reviewer note"
    probes["case notes field"] = case_notes

    case_extra = _mutable(valid)
    case_extra["cases"][2]["failure_reason"] = "lexical mismatch"
    probes["arbitrary extra case field"] = case_extra

    foreign = _mutable(valid)
    foreign["reviewer_id"] = "alice"
    probes["foreign reviewer_id"] = foreign

    results = run_contract(
        shipped_contract,
        "result = {};"
        "Object.keys(INPUT).forEach(function (name) {"
        "  result[name] = MANUAL_REVIEW_CONTRACT.validateReviewerFile(INPUT[name]);"
        "});",
        payload=probes,
        tmp_path=tmp_path,
    )
    assert results["legal control"] is None
    assert "carries unexpected field(s) provenance" in results["extra top-level field"]
    assert "carries unexpected field(s) notes" in results["case notes field"]
    assert "carries unexpected field(s) failure_reason" in results["arbitrary extra case field"]
    assert "reviewer_id must be one of jiajun, xin" in results["foreign reviewer_id"]
