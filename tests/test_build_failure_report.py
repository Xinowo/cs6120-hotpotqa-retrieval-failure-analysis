"""
test_build_failure_report.py

Offline unit tests for the failure-review HTML generator's Python layer:
path/schema validation, failure-unit reshaping (missed_ks / export_k /
gold_display / worst_gold_rank), HTML-safe embedding, and end-to-end file
generation. No browser, network, model, or HotpotQA data is touched; the
DOM/localStorage/CSV round-trip behavior is covered by the mandatory browser
acceptance in the design doc (section 9.2), not here.

These tests assert only the PLUMBING contract -- the generator moves the
evaluator's precomputed fields into display structures and never recomputes a
metric.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import shutil
import subprocess

import pytest

from scripts import build_failure_report as bfr


# --------------------------------------------------------------------------- #
# Builders for synthetic (valid) run data
# --------------------------------------------------------------------------- #

def make_top_k(n, prefix="p"):
    """A filler top_k list of length n with consecutive ranks 1..n."""
    return [
        {"rank": i + 1, "title": f"{prefix}{i + 1}", "score": 1.0 / (i + 1),
         "text": f"paragraph text {i + 1}"}
        for i in range(n)
    ]


def make_sub(gold_ranks, any2, any5, any10, top_k=None, top_k_len=10):
    """One retriever sub-record. metrics are set INDEPENDENTLY of gold_ranks on
    purpose, so tests can prove gold_display is derived from gold_ranks and not
    reverse-engineered from the global any-evidence metric."""
    return {
        "top_k": top_k if top_k is not None else make_top_k(top_k_len),
        "gold_ranks": gold_ranks,
        "metrics": {
            "any_evidence_recall@2": any2,
            "any_evidence_recall@5": any5,
            "any_evidence_recall@10": any10,
        },
    }


def make_record(example_id, gold_titles, retrievers, question_type="comparison"):
    return {
        "example_id": example_id,
        "question": "Question?",
        "question_type": question_type,
        "gold_titles": list(gold_titles),
        "retrievers": retrievers,
    }


def make_config(run_id="2026-07-17_a", retrievers=("dense", "bm25"),
                top_k_max=10, git_commit="135765bb", **extra):
    config = {
        "run_id": run_id,
        "n": 2,
        "split": "validation",
        "corpus_setting": "pooled",
        "corpus_size": 4937,
        "top_k_max": top_k_max,
        "retrievers": {name: f"model-{name}" for name in retrievers},
        "timestamp": "2026-07-17T20:16:18",
        "script": "scripts/run_failure_review.py",
        "git_commit": git_commit,
    }
    config.update(extra)
    return config


def write_run(tmp_path, records, config, run_id=None):
    """Write a run directory (config.json + details.jsonl) and return runs_root."""
    run_id = run_id or config["run_id"]
    runs_root = tmp_path / "runs"
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "config.json").write_text(
        json.dumps(config, ensure_ascii=False), encoding="utf-8"
    )
    with open(run_dir / "details.jsonl", "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return str(runs_root)


def extract_payload(html):
    """Extract and JSON-parse the embedded report-data payload, proving it is
    standard JSON and that the closing </script> was not swallowed."""
    marker = 'type="application/json">'
    start = html.index(marker) + len(marker)
    end = html.index("</script>", start)
    return json.loads(html[start:end]), html[start:end]


# --------------------------------------------------------------------------- #
# Failure-unit filtering, missed_ks, export_k
# --------------------------------------------------------------------------- #

def two_record_fixture():
    # Record A: dense passes everything; bm25 misses only @2.
    rec_a = make_record(
        "aaa11111",
        ["Gold Alpha", "Gold Beta"],
        {
            "dense": make_sub({"Gold Alpha": 1, "Gold Beta": 3}, True, True, True),
            "bm25": make_sub({"Gold Alpha": 4, "Gold Beta": None}, False, True, True),
        },
    )
    # Record B: dense misses at every k; bm25 passes everything.
    rec_b = make_record(
        "bbb22222",
        ["Gold Gamma", "Gold Delta"],
        {
            "dense": make_sub({"Gold Gamma": None, "Gold Delta": None}, False, False, False),
            "bm25": make_sub({"Gold Gamma": 1, "Gold Delta": 2}, True, True, True),
        },
    )
    return [rec_a, rec_b], make_config()


def test_default_filter_keeps_only_failing_units():
    records, config = two_record_fixture()
    units = bfr.build_failure_units(records, config)
    keys = {(u["example_id"], u["card_retriever"]) for u in units}
    assert keys == {("aaa11111", "bm25"), ("bbb22222", "dense")}


def test_missed_ks_and_export_k():
    records, config = two_record_fixture()
    units = {u["card_retriever"]: u for u in bfr.build_failure_units(records, config)}
    assert units["bm25"]["missed_ks"] == [2]
    assert units["bm25"]["export_k"] == 2
    assert units["dense"]["missed_ks"] == [2, 5, 10]
    assert units["dense"]["export_k"] == 2


def test_retriever_narrowing():
    records, config = two_record_fixture()
    units = bfr.build_failure_units(records, config, retriever="dense")
    assert [(u["example_id"], u["card_retriever"]) for u in units] == [("bbb22222", "dense")]


def test_retriever_narrowing_unknown_retriever_raises():
    records, config = two_record_fixture()
    with pytest.raises(ValueError, match="not in run"):
        bfr.build_failure_units(records, config, retriever="rerank")


def test_k_narrowing_uses_membership_in_missed_ks():
    records, config = two_record_fixture()
    # k=10 keeps only units that miss at 10 (dense B).
    units10 = bfr.build_failure_units(records, config, k=10)
    assert [(u["example_id"], u["card_retriever"]) for u in units10] == [("bbb22222", "dense")]
    # k=2 keeps both (both miss at 2).
    units2 = bfr.build_failure_units(records, config, k=2)
    assert {(u["example_id"], u["card_retriever"]) for u in units2} == {
        ("aaa11111", "bm25"), ("bbb22222", "dense")
    }


def test_export_k_is_min_missed_even_when_generated_with_k10():
    records, config = two_record_fixture()
    units = bfr.build_failure_units(records, config, k=10)
    # Generated under --k 10 but export_k is still the smallest missed k.
    assert units[0]["export_k"] == 2


def test_retriever_and_k_intersection():
    records, config = two_record_fixture()
    units = bfr.build_failure_units(records, config, retriever="bm25", k=10)
    assert units == []  # bm25 unit only misses @2, so k=10 excludes it


# --------------------------------------------------------------------------- #
# gold_display: per-gold derivation, independent of the global metric
# --------------------------------------------------------------------------- #

def test_build_gold_display_per_gold():
    display = bfr.build_gold_display(
        ["Gold A", "Gold B"], {"Gold A": 1, "Gold B": 6}
    )
    assert display["Gold A"]["hits"] == {"2": True, "5": True, "10": True}
    assert display["Gold B"]["rank"] == 6
    assert display["Gold B"]["hits"] == {"2": False, "5": False, "10": True}


def test_build_gold_display_null_rank():
    display = bfr.build_gold_display(["Gold A"], {"Gold A": None})
    assert display["Gold A"]["rank"] is None
    assert display["Gold A"]["hits"] == {"2": False, "5": False, "10": False}


def test_gold_display_not_reverse_engineered_from_global_metric():
    # dense's global any_evidence_recall is all True (gold Alpha at rank 1), yet
    # gold Beta at rank 6 must still read as miss@2/@5, hit@10. The unit is
    # created because bm25 fails; we inspect dense's gold_display inside it.
    record = make_record(
        "cccc3333",
        ["Gold Alpha", "Gold Beta"],
        {
            "dense": make_sub({"Gold Alpha": 1, "Gold Beta": 6}, True, True, True),
            "bm25": make_sub({"Gold Alpha": None, "Gold Beta": None}, False, False, False),
        },
    )
    units = bfr.build_failure_units([record], make_config())
    assert len(units) == 1
    dense_display = units[0]["retrievers"]["dense"]["gold_display"]
    assert dense_display["Gold Alpha"]["hits"] == {"2": True, "5": True, "10": True}
    assert dense_display["Gold Beta"]["hits"] == {"2": False, "5": False, "10": True}


# --------------------------------------------------------------------------- #
# worst_gold_rank + finite sort sentinel + deterministic ordering
# --------------------------------------------------------------------------- #

def test_worst_gold_rank_all_ranked():
    record = make_record(
        "dddd4444",
        ["G1", "G2"],
        {
            "dense": make_sub({"G1": 3, "G2": 7}, False, False, False),
            "bm25": make_sub({"G1": 1, "G2": 2}, True, True, True),
        },
    )
    unit = bfr.build_failure_units([record], make_config())[0]
    assert unit["worst_gold_rank"] == 7
    assert unit["worst_gold_rank_sort"] == 7


def test_worst_gold_rank_null_uses_finite_sentinel():
    record = make_record(
        "eeee5555",
        ["G1", "G2"],
        {
            "dense": make_sub({"G1": 3, "G2": None}, False, False, False),
            "bm25": make_sub({"G1": 1, "G2": 2}, True, True, True),
        },
    )
    config = make_config(top_k_max=50)
    unit = bfr.build_failure_units([record], config)[0]
    assert unit["worst_gold_rank"] is None
    assert unit["worst_gold_rank_sort"] == 51  # top_k_max + 1, finite
    # payload serializes as standard JSON (null, not NaN/Infinity)
    payload = bfr.build_payload(config, [record])
    text = json.dumps(payload, allow_nan=False)
    assert '"worst_gold_rank": null' in text


def test_default_sort_worst_first_then_tie_breakers():
    # Two records: one dense-fail with worst rank 4, one with both retrievers
    # failing and gold unranked (sentinel sort). Sentinel (top_k_max+1) sorts
    # first; then tie-break by example_id, then card_retriever.
    rec_low = make_record(
        "aaaa0000",
        ["G1", "G2"],
        {
            "dense": make_sub({"G1": 2, "G2": 4}, False, False, False),
            "bm25": make_sub({"G1": 1, "G2": 2}, True, True, True),
        },
    )
    rec_null = make_record(
        "zzzz9999",
        ["G1", "G2"],
        {
            "dense": make_sub({"G1": None, "G2": None}, False, False, False),
            "bm25": make_sub({"G1": None, "G2": None}, False, False, False),
        },
    )
    units = bfr.build_failure_units([rec_low, rec_null], make_config())
    order = [(u["example_id"], u["card_retriever"]) for u in units]
    # rec_null's two cards (sentinel sort=11) come first, ordered bm25 < dense,
    # then rec_low dense (sort=4).
    assert order == [
        ("zzzz9999", "bm25"),
        ("zzzz9999", "dense"),
        ("aaaa0000", "dense"),
    ]


# --------------------------------------------------------------------------- #
# Schema validation errors
# --------------------------------------------------------------------------- #

def test_retriever_set_missing_retriever_raises(tmp_path):
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": 3}, False, True, True)},  # missing bm25
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="retriever set.*missing.*bm25"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_retriever_set_extra_retriever_raises(tmp_path):
    record = make_record(
        "aaaa1111", ["G1"],
        {
            "dense": make_sub({"G1": 3}, False, True, True),
            "bm25": make_sub({"G1": 3}, False, True, True),
            "rerank": make_sub({"G1": 3}, False, True, True),  # extra
        },
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="extra.*rerank"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_gold_rank_over_top_k_max_raises(tmp_path):
    record = make_record(
        "aaaa1111", ["G1"],
        {
            "dense": make_sub({"G1": 11}, False, True, True),  # > top_k_max 10
            "bm25": make_sub({"G1": 3}, False, True, True),
        },
    )
    runs_root = write_run(tmp_path, [record], make_config(top_k_max=10))
    with pytest.raises(ValueError, match="out of range"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_top_k_rank_skip_raises(tmp_path):
    bad_top_k = [
        {"rank": 1, "title": "a", "score": 1.0, "text": "x"},
        {"rank": 3, "title": "b", "score": 0.5, "text": "y"},  # skips 2
    ]
    record = make_record(
        "aaaa1111", ["G1"],
        {
            "dense": make_sub({"G1": 1}, False, True, True, top_k=bad_top_k),
            "bm25": make_sub({"G1": 3}, False, True, True),
        },
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="consecutive from 1"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_top_k_rank_over_limit_raises(tmp_path):
    record = make_record(
        "aaaa1111", ["G1"],
        {
            "dense": make_sub({"G1": 1}, False, True, True, top_k=make_top_k(11)),
            "bm25": make_sub({"G1": 3}, False, True, True),
        },
    )
    runs_root = write_run(tmp_path, [record], make_config(top_k_max=10))
    with pytest.raises(ValueError, match="exceeds top_k_max"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_missing_metric_raises(tmp_path):
    sub = make_sub({"G1": 3}, False, True, True)
    del sub["metrics"]["any_evidence_recall@5"]
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": sub, "bm25": make_sub({"G1": 3}, False, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="any_evidence_recall@5"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_non_finite_score_rejected(tmp_path):
    # json.dumps with the default allow_nan=True writes a bare NaN token that
    # json.loads happily reads back; the finite check must reject it.
    record = make_record(
        "aaaa1111", ["G1"],
        {
            "dense": make_sub({"G1": 1}, False, True, True,
                              top_k=[{"rank": 1, "title": "a",
                                      "score": float("nan"), "text": "x"}]),
            "bm25": make_sub({"G1": 3}, False, True, True),
        },
    )
    runs_root = tmp_path / "runs"
    run_dir = runs_root / "2026-07-17_a"
    run_dir.mkdir(parents=True)
    (run_dir / "config.json").write_text(json.dumps(make_config()), encoding="utf-8")
    with open(run_dir / "details.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")  # default allow_nan=True -> "NaN"
    with pytest.raises(ValueError, match="finite"):
        bfr.generate_report("2026-07-17_a", runs_root=str(runs_root),
                            out=str(tmp_path / "out.html"))


def test_html_safe_json_rejects_infinity():
    with pytest.raises(ValueError):
        bfr.html_safe_json({"x": float("inf")})


def test_leading_dash_example_id_rejected(tmp_path):
    record = make_record(
        "-badid", ["G1"],
        {
            "dense": make_sub({"G1": 3}, False, True, True),
            "bm25": make_sub({"G1": 3}, False, True, True),
        },
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="not a valid identifier"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_colon_example_id_rejected(tmp_path):
    record = make_record(
        "bad:id", ["G1"],
        {
            "dense": make_sub({"G1": 3}, False, True, True),
            "bm25": make_sub({"G1": 3}, False, True, True),
        },
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="not a valid identifier"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_colon_retriever_name_rejected(tmp_path):
    config = make_config(retrievers=("de:nse", "bm25"))
    record = make_record(
        "aaaa1111", ["G1"],
        {
            "de:nse": make_sub({"G1": 3}, False, True, True),
            "bm25": make_sub({"G1": 3}, False, True, True),
        },
    )
    runs_root = write_run(tmp_path, [record], config)
    with pytest.raises(ValueError, match="not a valid identifier"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


# --------------------------------------------------------------------------- #
# CLI argument / path handling
# --------------------------------------------------------------------------- #

def test_k_argparse_rejects_non_domain_value():
    with pytest.raises(SystemExit):
        bfr.parse_args(["--run", "2026-07-17_a", "--k", "3"])


@pytest.mark.parametrize("bad", ["/abs/path", "..", "a/b", "a\\b"])
def test_run_id_arg_rejects_unsafe(bad):
    with pytest.raises(ValueError):
        bfr.validate_run_id_arg(bad)


def test_missing_run_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="run directory not found"):
        bfr.generate_report("2026-07-17_a", runs_root=str(tmp_path / "runs"),
                            out=str(tmp_path / "out.html"))


def test_missing_config_raises(tmp_path):
    runs_root = tmp_path / "runs"
    run_dir = runs_root / "2026-07-17_a"
    run_dir.mkdir(parents=True)
    (run_dir / "details.jsonl").write_text("", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="config.json not found"):
        bfr.generate_report("2026-07-17_a", runs_root=str(runs_root),
                            out=str(tmp_path / "out.html"))


def test_bad_jsonl_line_reports_line_number(tmp_path):
    runs_root = tmp_path / "runs"
    run_dir = runs_root / "2026-07-17_a"
    run_dir.mkdir(parents=True)
    (run_dir / "config.json").write_text(json.dumps(make_config()), encoding="utf-8")
    good = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": 3}, False, True, True),
         "bm25": make_sub({"G1": 3}, False, True, True)},
    )
    with open(run_dir / "details.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(good) + "\n")
        f.write("{not valid json\n")
    with pytest.raises(ValueError, match="line 2: invalid JSON"):
        bfr.generate_report("2026-07-17_a", runs_root=str(runs_root),
                            out=str(tmp_path / "out.html"))


def test_run_id_mismatch_raises(tmp_path):
    config = make_config(run_id="2026-01-01_z")
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": 3}, False, True, True),
         "bm25": make_sub({"G1": 3}, False, True, True)},
    )
    runs_root = write_run(tmp_path, [record], config, run_id="2026-07-17_a")
    with pytest.raises(ValueError, match="run_id mismatch"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


# --------------------------------------------------------------------------- #
# End-to-end rendering
# --------------------------------------------------------------------------- #

def test_empty_details_yields_no_failure_units(tmp_path):
    runs_root = write_run(tmp_path, [], make_config())
    out = tmp_path / "out.html"
    bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=str(out))
    html = out.read_text(encoding="utf-8")
    payload, _ = extract_payload(html)
    assert payload["failure_units"] == []
    # the empty-state message string is present in the template
    assert "No failures under the current report filter." in html


def test_git_commit_null_allowed(tmp_path):
    config = make_config(git_commit=None)
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": None}, False, False, False),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], config)
    out = tmp_path / "out.html"
    bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=str(out))
    payload, _ = extract_payload(out.read_text(encoding="utf-8"))
    assert payload["config"]["git_commit"] is None


def test_payload_preserves_full_config_including_script(tmp_path):
    config = make_config()
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": None}, False, False, False),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], config)
    out = tmp_path / "out.html"
    bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=str(out))
    payload, _ = extract_payload(out.read_text(encoding="utf-8"))
    assert payload["config"]["script"] == "scripts/run_failure_review.py"
    assert payload["config"]["corpus_setting"] == "pooled"
    assert payload["config"]["timestamp"] == "2026-07-17T20:16:18"


def test_html_safe_escaping_no_raw_script_close(tmp_path):
    danger = "</script><b>x</b> & < > done"
    top_k = [{"rank": 1, "title": "T", "score": 1.0, "text": danger}]
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": None}, False, False, False, top_k=top_k),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    out = tmp_path / "out.html"
    bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=str(out))
    html = out.read_text(encoding="utf-8")
    payload, payload_text = extract_payload(html)
    # No raw </script> or < inside the embedded payload.
    assert "</script>" not in payload_text
    assert "<" not in payload_text
    # The dangerous text survived round-trip through the standard JSON parser.
    assert payload["failure_units"][0]["retrievers"]["dense"]["top_k"][0]["text"] == danger


def test_default_output_path(tmp_path):
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": None}, False, False, False),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    out_path = bfr.generate_report("2026-07-17_a", runs_root=runs_root)
    assert out_path == os.path.join(runs_root, "2026-07-17_a", "failures_review.html")
    assert os.path.isfile(out_path)


def test_out_override_creates_parent(tmp_path):
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": None}, False, False, False),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    out = tmp_path / "nested" / "dir" / "review.html"
    out_path = bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=str(out))
    assert out_path == str(out)
    assert out.is_file()


def test_out_overwriting_input_rejected(tmp_path):
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": None}, False, False, False),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    details = os.path.join(runs_root, "2026-07-17_a", "details.jsonl")
    with pytest.raises(ValueError, match="overwrite an input file"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=details)


def test_render_report_requires_single_placeholder():
    # Sanity: the template carries exactly one placeholder.
    assert bfr.HTML_TEMPLATE.count(bfr.DATA_PLACEHOLDER) == 1


# --------------------------------------------------------------------------- #
# Hardening regressions with legal controls (identifier fullmatch, metric
# monotonicity, case-insensitive output-alias protection)
# --------------------------------------------------------------------------- #

# Full-string identifier validation: a trailing LF must not slip through.

@pytest.mark.parametrize("good", ["abc", "2026-07-17_a", "dense", "a.b_c-1", "5a8b57f2"])
def test_is_valid_identifier_accepts_legal(good):
    assert bfr.is_valid_identifier(good) is True


@pytest.mark.parametrize(
    "bad",
    ["abc\n", "\nabc", "a\nb", "abc\r", "-abc", "a:b", "", "a b", "abc ", 7, None],
)
def test_is_valid_identifier_rejects_illegal(bad):
    assert bfr.is_valid_identifier(bad) is False


def test_trailing_newline_example_id_rejected(tmp_path):
    record = make_record(
        "aaaa1111\n", ["G1"],
        {"dense": make_sub({"G1": 3}, False, True, True),
         "bm25": make_sub({"G1": 3}, False, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="not a valid identifier"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


def test_trailing_newline_run_id_rejected(tmp_path):
    config = make_config(run_id="2026-07-17_a\n")
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="not a valid identifier"):
        bfr.load_config(str(path), "2026-07-17_a\n")


def test_trailing_newline_retriever_name_rejected(tmp_path):
    config = make_config(retrievers=("dense\n", "bm25"))
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="not a valid identifier"):
        bfr.load_config(str(path), "2026-07-17_a")


# Monotonicity of the precomputed Any@2/@5/@10 booleans.

@pytest.mark.parametrize("seq", [(False, True, False), (True, False, False),
                                 (True, False, True), (True, True, False)])
def test_non_monotone_any_recall_rejected(tmp_path, seq):
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": 3}, *seq),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    with pytest.raises(ValueError, match="not monotone"):
        bfr.generate_report("2026-07-17_a", runs_root=runs_root,
                            out=str(tmp_path / "out.html"))


@pytest.mark.parametrize("seq,expected_missed",
                         [((False, False, False), [2, 5, 10]),
                          ((False, False, True), [2, 5]),
                          ((False, True, True), [2])])
def test_monotone_any_recall_legal_control(tmp_path, seq, expected_missed):
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": 3}, *seq),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    out = tmp_path / "out.html"
    bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=str(out))
    payload, _ = extract_payload(out.read_text(encoding="utf-8"))
    dense_units = [u for u in payload["failure_units"] if u["card_retriever"] == "dense"]
    assert len(dense_units) == 1
    assert dense_units[0]["missed_ks"] == expected_missed


# Case-insensitive / alias --out protection for both input files.

def _case_insensitive_fs():
    return os.path.normcase("A") == os.path.normcase("a")


@pytest.mark.parametrize("alias_name", ["DETAILS.JSONL", "CONFIG.JSON",
                                        "Details.Jsonl", "Config.Json"])
def test_out_case_insensitive_input_alias_rejected(tmp_path, alias_name):
    record = make_record(
        "aaaa1111", ["G1"],
        {"dense": make_sub({"G1": None}, False, False, False),
         "bm25": make_sub({"G1": 1}, True, True, True)},
    )
    runs_root = write_run(tmp_path, [record], make_config())
    run_dir = os.path.join(runs_root, "2026-07-17_a")
    alias = os.path.join(run_dir, alias_name)
    if _case_insensitive_fs():
        with pytest.raises(ValueError, match="overwrite an input file"):
            bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=alias)
        # Legal control: a genuinely different name is accepted on the same FS.
        legal = os.path.join(run_dir, "failures_review.html")
        assert bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=legal)
    else:
        # On a case-sensitive FS an uppercase alias names a distinct legal file.
        out_path = bfr.generate_report("2026-07-17_a", runs_root=runs_root, out=alias)
        assert os.path.isfile(out_path)


# --------------------------------------------------------------------------- #
# Corrective regressions with legal controls for the embedded browser guards:
# the CJK import/export guard, persisted-annotation load validation, the
# clear-last-annotation persistence path, and the null-prototype string sets.
#
# These guards live in the embedded browser <script>. The tests execute the
# ACTUAL guard source, extracted verbatim from HTML_TEMPLATE, under Node (a real
# JS engine) -- so they are direct JS regressions, not Python re-implementations
# of the guards. When no Node runtime is present they skip; the `test_source_*`
# assertions below always run as a floor, and the design's mandatory manual
# browser acceptance (section 9.2) remains the DOM-level check. No browser/
# network/model is used.
# --------------------------------------------------------------------------- #

_NODE = shutil.which("node")
requires_node = pytest.mark.skipif(
    _NODE is None,
    reason="node runtime unavailable; guards still covered by source-level checks + browser QA",
)

_JS_ASSERT = (
    'function assert(c, m){ if (!c) { console.error("ASSERT FAIL: " + m); '
    "process.exit(1); } }\n"
)


def _balanced_from(text, start):
    """Index just past the brace/paren matching the one at `text[start]`,
    skipping string literals and // and /* */ comments."""
    depth = 0
    i = start
    n = len(text)
    in_str = None
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if c in "\"'":
            in_str = c
            i += 1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced from %d" % start)


def _stmt_end(text, start):
    """Index just past the first top-level ';' at or after `start`."""
    depth = 0
    i = start
    n = len(text)
    in_str = None
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if c in "\"'":
            in_str = c
            i += 1
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == ";" and depth == 0:
            return i + 1
        i += 1
    raise ValueError("no terminating ; from %d" % start)


def _js_func(name):
    """Extract `function <name>(...) { ... }` verbatim from the template."""
    t = bfr.HTML_TEMPLATE
    idx = t.index("function " + name)
    brace = t.index("{", idx)
    return t[idx:_balanced_from(t, brace)]


def _js_var(name):
    """Extract the `var <name> = ...;` statement verbatim from the template."""
    t = bfr.HTML_TEMPLATE
    idx = t.index("var " + name + " ")
    return t[idx:_stmt_end(t, idx)]


def _js_regex(name):
    """The right-hand-side regex literal of a `var <name> = /.../;` line."""
    return _js_var(name).split("=", 1)[1].strip().rstrip(";").strip()


def _run_node(js_source):
    proc = subprocess.run(
        [_NODE, "-e", _JS_ASSERT + js_source],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, (
        "node harness failed:\nSTDOUT:\n%s\nSTDERR:\n%s" % (proc.stdout, proc.stderr)
    )
    return proc


# ---- CJK guard covers the named CJK blocks; legal controls pass ----------- #

_CJK_BODY = """
function det(cp){ return CJK_RE.test(String.fromCodePoint(cp)); }
// Must be detected as CJK (import AND export share this one guard): Bopomofo,
// CJK strokes, enclosed CJK, ideographic description, Han (BMP + supplementary),
// Hiragana, Katakana, Hangul, fullwidth, Kangxi radicals, CJK radicals supp,
// CJK compatibility, CJK compatibility forms, and the Japanese shared
// Common/Inherited kana marks (U+30FC prolonged, U+3099/U+309A combining,
// U+309B/U+309C spacing, U+30FB middle dot) plus their halfwidth forms.
var POS = [0x3105, 0x31C0, 0x3220, 0x2FF0, 0x4E2D, 0x20000, 0x3042, 0x30AB,
           0xD55C, 0xFF01, 0x2F00, 0x2E80, 0x3300, 0xFE30,
           0x30FC, 0x3099, 0x309A, 0x309B, 0x309C, 0x30FB, 0xFF70, 0xFF9E];
// Legal controls that must PASS (not a CJK char): ASCII letters/digits,
// accented Latin, and emoji -- so the guard is a CJK ban, not an ASCII-only ban.
var NEG = [0x41, 0x7A, 0x30, 0xE9, 0xF1, 0xFC, 0x1F600, 0x2705, 0x2713];
POS.forEach(function(cp){ assert(det(cp), "CJK must be detected: U+" + cp.toString(16)); });
NEG.forEach(function(cp){ assert(!det(cp), "legal char must pass: U+" + cp.toString(16)); });
assert(CJK_RE.test("hello " + String.fromCodePoint(0x3105) + " world"),
       "embedded bopomofo detected inside a sentence");
assert(!CJK_RE.test("Note: cafe " + String.fromCodePoint(0xE9)),
       "accented-latin sentence passes");
console.log("CJK-GUARD OK");
"""


@requires_node
def test_js_cjk_guard_covers_named_blocks_and_passes_legal_controls():
    _run_node(_js_var("CJK_RE") + _CJK_BODY)


def test_source_cjk_guard_extended_blocks_present():
    src = _js_regex("CJK_RE")
    for token in [
        "Script=Han", "Script=Hiragana", "Script=Katakana", "Script=Hangul",
        "Script=Bopomofo",
        "\\u2E80-\\u2EFF", "\\u2F00-\\u2FDF", "\\u2FF0-\\u2FFF",
        "\\u3000-\\u303F", "\\u31C0-\\u31EF", "\\u3200-\\u32FF",
        "\\u3300-\\u33FF", "\\uFE30-\\uFE4F", "\\uFF00-\\uFFEF",
    ]:
        assert token in src, "CJK_RE missing block %r" % token


# ---- persisted-entry semantics / provenance / key-grammar validation ------ #

def _load_validation_decls():
    return (
        _js_var("IDENTIFIER_RE") + "\n"
        + _js_var("ISO_RE") + "\n"
        + _js_func("isValidIso") + "\n"  # validAnnotationEntry delegates to it
        + "var VALID_KS = [2, 5, 10];\n"  # fixed cutoff domain (bfr.VALID_KS)
        + 'var STORAGE_KEY = "fr::run_x";\n'
        + "var banner = [];\n"
        + "function showBanner(m){ banner.push(m); }\n"
        + "var RAW = null;\n"
        + "var storage = { getItem: function(k){ "
        + "return (k === STORAGE_KEY) ? RAW : null; } };\n"
        + _js_func("isAnnotated") + "\n"
        + _js_func("validAnnotationKey") + "\n"
        + _js_func("validAnnotationEntry") + "\n"
        + _js_func("loadAnnotations") + "\n"
    )


_LOAD_VALIDATION_BODY = """
function goodEntry(over){
  var e = { k: 2, label: "lexical mismatch", notes: "",
            annotator: "amy", annotated_at: "2026-07-26T10:00:00Z" };
  if (over) { for (var kk in over) e[kk] = over[kk]; }
  return e;
}
function load(map){ banner = []; RAW = JSON.stringify({ schema: 1, annotations: map }); return loadAnnotations(); }
function isolated(res){ return Object.keys(res).length === 0 && banner.length > 0; }
function accepted(res, key){ return !!res[key] && banner.length === 0; }

// legal control: a fully valid, well-provenanced entry loads with no warning
assert(accepted(load({ "aaa1::dense": goodEntry() }), "aaa1::dense"), "valid entry loads");

// provenance / semantics violations must isolate the WHOLE blob
assert(isolated(load({ "aaa1::dense": goodEntry({ annotator: "" }) })), "empty annotator isolates");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotator: "   " }) })), "blank annotator isolates");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "" }) })), "empty timestamp isolates");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "not-a-date" }) })), "non-ISO timestamp isolates");
assert(isolated(load({ "aaa1::dense": goodEntry({ k: 2.5 }) })), "fractional k isolates");
assert(isolated(load({ "aaa1::dense": goodEntry({ k: 999 }) })), "out-of-domain k isolates");
assert(isolated(load({ "aaa1::dense": goodEntry({ label: "", notes: "   " }) })), "unannotated entry isolates");

// composite-key grammar violations isolate
assert(isolated(load({ "aaa1:dense": goodEntry() })), "single-colon key isolates");
assert(isolated(load({ "aaa1::dense::x": goodEntry() })), "three-part key isolates");
assert(isolated(load({ "-bad::dense": goodEntry() })), "leading-dash example_id key isolates");
assert(isolated(load({ "aaa1::de nse": goodEntry() })), "space in retriever key isolates");

// round-1 corrupt-storage shapes remain isolated
assert(isolated(load({ "aaa1::dense": { k: 2, label: 7, notes: "",
       annotator: "amy", annotated_at: "2026-07-26T10:00:00Z" } })), "numeric label isolates");
banner = []; RAW = JSON.stringify({ schema: 1, annotations: [1, 2] });
assert(isolated(loadAnnotations()), "array-shaped annotations isolates");
banner = []; RAW = JSON.stringify({ schema: 2, annotations: {} });
assert(isolated(loadAnnotations()), "wrong schema isolates");
banner = []; RAW = "{ not valid json";
assert(isolated(loadAnnotations()), "unparseable blob isolates");

// legal controls that must NOT be treated as corruption
banner = []; RAW = JSON.stringify({ schema: 1, annotations: {} });
var em = loadAnnotations();
assert(Object.keys(em).length === 0 && banner.length === 0, "empty map loads clean");
banner = []; RAW = null;
var ab = loadAnnotations();
assert(Object.keys(ab).length === 0 && banner.length === 0, "absent storage loads clean");
// CJK / formula content is editable DRAFT state, not storage corruption -> loads
var draft = load({ "aaa1::dense": goodEntry({ label: "=danger",
                   notes: "see " + String.fromCodePoint(0x4E2D) }) });
assert(accepted(draft, "aaa1::dense"),
       "CJK/formula content loads as draft (blocked only at export/import)");

// impossible ISO calendar dates are rejected at load; real leap day / offset load
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "2025-02-29T10:00:00Z" }) })), "load isolates 2025-02-29");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-02-30T10:00:00Z" }) })), "load isolates feb-30");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-04-31T10:00:00Z" }) })), "load isolates apr-31");
assert(accepted(load({ "aaa1::dense": goodEntry({ annotated_at: "2024-02-29T10:00:00Z" }) }), "aaa1::dense"), "load accepts real leap day");
assert(accepted(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00+05:30" }) }), "aaa1::dense"), "load accepts offset");

// impossible timezone offsets are rejected at load; legal Z / no-offset / +05:30 / +0530 load
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00+05:60" }) })), "load isolates +05:60");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00-05:60" }) })), "load isolates -05:60");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00+99:00" }) })), "load isolates +99:00");
assert(isolated(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00+99:99" }) })), "load isolates +99:99");
assert(accepted(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00Z" }) }), "aaa1::dense"), "load accepts Z");
assert(accepted(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00" }) }), "aaa1::dense"), "load accepts no offset");
assert(accepted(load({ "aaa1::dense": goodEntry({ annotated_at: "2026-07-26T10:00:00+0530" }) }), "aaa1::dense"), "load accepts +0530");
console.log("LOAD-VALIDATION OK");
"""


@requires_node
def test_js_persisted_entry_semantics_and_provenance():
    _run_node(_load_validation_decls() + _LOAD_VALIDATION_BODY)


def test_source_persisted_entry_load_validation():
    entry = _js_func("validAnnotationEntry")
    assert "VALID_KS.indexOf(e.k)" in entry
    assert "Math.floor(e.k) !== e.k" in entry
    assert "isAnnotated(e)" in entry
    assert "e.annotator.trim()" in entry
    assert "isValidIso(e.annotated_at)" in entry
    key = _js_func("validAnnotationKey")
    assert 'split("::")' in key
    assert "IDENTIFIER_RE.test(parts[0])" in key
    assert "IDENTIFIER_RE.test(parts[1])" in key
    load = _js_func("loadAnnotations")
    assert "validAnnotationKey(keys[i])" in load
    # export defense: provenance re-checked at the write boundary
    assert "badProv" in bfr.HTML_TEMPLATE
    assert "missing/invalid provenance" in bfr.HTML_TEMPLATE


# ---- clearing the last annotation cannot silently fail persistence -------- #

def _persist_decls():
    storage_rhs = _js_var("storage").split("=", 1)[1]  # " (function () {...})();"
    return (
        'var STORAGE_KEY = "fr::run_x";\n'
        + "var banner = [];\n"
        + "function showBanner(m){ banner.push(m); }\n"
        + "var window = { localStorage: null };\n"
        + "var annotations = {};\n"
        + _js_func("degradedWarn") + "\n"
        + "function makeStorage(){ return " + storage_rhs + " }\n"
        + "var storage;\n"
        + _js_func("persist") + "\n"
    )


_PERSIST_BODY = """
function makeBackend(opts){
  opts = opts || {};
  var store = {};
  return {
    getItem: function(k){ return (k in store) ? store[k] : null; },
    setItem: function(k, v){ if (opts.failSet) throw new Error("quota"); store[k] = v; },
    removeItem: function(k){
      if (opts.failRemoveAll) throw new Error("remove blocked");
      if (opts.failRemoveKey && k === opts.failRemoveKey) throw new Error("remove blocked");
      delete store[k];
    },
    _store: store
  };
}

// scenario 1 (THE FIX): remove of the last entry throws -> must warn + degrade,
// newest in-memory map (empty) stands, stale blob cannot silently persist quietly.
var be1 = makeBackend({ failRemoveKey: STORAGE_KEY });
window.localStorage = be1;
be1._store[STORAGE_KEY] = "stale-old-blob";
storage = makeStorage();
assert(!storage.degraded(), "probe on a random key must succeed here");
banner = []; annotations = {};
persist();
assert(banner.length > 0, "clearing last entry with a failing remove MUST warn");
assert(storage.degraded(), "adapter degrades after remove failure");
assert(storage.getItem(STORAGE_KEY) === null, "newest in-memory map is the cleared state");

// scenario 2 (legal control): remove succeeds -> no warning, run key deleted
var be2 = makeBackend({});
window.localStorage = be2;
be2._store[STORAGE_KEY] = "old";
storage = makeStorage();
banner = []; annotations = {};
persist();
assert(banner.length === 0, "successful remove must not warn");
assert(!(STORAGE_KEY in be2._store), "successful remove deletes the run key");

// scenario 3 (legal control): non-empty persist writes a blob, no warning
var be3 = makeBackend({});
window.localStorage = be3;
storage = makeStorage();
banner = [];
annotations = { "a::dense": { k: 2, label: "x", notes: "",
                annotator: "amy", annotated_at: "2026-07-26T10:00:00Z" } };
persist();
assert(banner.length === 0, "healthy setItem must not warn");
assert(be3._store[STORAGE_KEY] && be3._store[STORAGE_KEY].indexOf("schema") !== -1,
       "blob persisted on a non-empty map");

// scenario 4: probe CLEANUP failure degrades + warns, never claims clean persistence
var be4 = makeBackend({ failRemoveAll: true });
window.localStorage = be4;
storage = makeStorage();
assert(storage.degraded(), "probe cleanup failure must degrade");
banner = [];
if (storage.degraded()) { degradedWarn(); }
assert(banner.length > 0, "probe cleanup failure warns");
assert(storage.setItem("k", "v") === false,
       "degraded setItem returns false (no clean-persistence claim)");
console.log("PERSIST-CLEAR OK");
"""


@requires_node
def test_js_clear_last_annotation_persistence_failure_warns():
    _run_node(_persist_decls() + _PERSIST_BODY)


def test_source_remove_reports_status_and_persist_warns():
    tpl = bfr.HTML_TEMPLATE
    assert "backend.removeItem(k); return true;" in tpl  # remove now reports success
    persist = _js_func("persist")
    assert "var removed = storage.removeItem(STORAGE_KEY);" in persist
    assert "if (!removed || storage.degraded()) { degradedWarn(); }" in persist


# ---- null-prototype string sets keep a legal "__proto__" value ------------ #

def _datalist_decls():
    return (
        "var options = [];\n"
        + 'var datalistEl = { textContent: "", '
        + "appendChild: function(o){ options.push(o.value); } };\n"
        + "var document = { createElement: function(tag){ return { value: undefined }; } };\n"
        + _js_func("isAnnotated") + "\n"
        + "var annotations = {\n"
        + '  "a1::dense": { k: 2, label: "__proto__", notes: "", annotator: "amy", annotated_at: "t" },\n'
        + '  "a2::dense": { k: 2, label: "lexical gap", notes: "", annotator: "amy", annotated_at: "t" },\n'
        + '  "a3::dense": { k: 2, label: "toString", notes: "", annotator: "amy", annotated_at: "t" }\n'
        + "};\n"
        + 'var cardRefs = [ { key: "a1::dense" }, { key: "a2::dense" }, { key: "a3::dense" } ];\n'
        + _js_func("rebuildDatalist") + "\n"
    )


_DATALIST_BODY = """
rebuildDatalist();
options.sort();
assert(options.indexOf("__proto__") !== -1, "legal __proto__ label must reach the datalist");
assert(options.indexOf("toString") !== -1, "legal toString label must reach the datalist");
assert(options.indexOf("lexical gap") !== -1, "ordinary label present");
assert(options.length === 3, "exactly 3 distinct labels; got " + options.length + " [" + options.join(", ") + "]");
console.log("DATALIST-SET OK");
"""


@requires_node
def test_js_datalist_keeps_special_key_labels():
    _run_node(_datalist_decls() + _DATALIST_BODY)


def test_source_null_prototype_string_sets():
    # rebuildDatalist / populateFilters / goldSet must use null-prototype maps.
    assert bfr.HTML_TEMPLATE.count("Object.create(null)") >= 3
    assert "Object.create(null)" in _js_func("rebuildDatalist")


# ---- one strict ISO-8601 validator: real calendar dates only --------------- #

_ISO_BODY = """
var CASES = [
  // valid, currently-supported forms (must stay valid)
  ["2024-02-29T10:00:00Z", true], ["2000-02-29T00:00:00Z", true],
  ["2026-07-26T10:00:00+05:30", true], ["2026-07-26T10:00:00+0530", true],
  ["2026-07-26T10:00:00-05:30", true], ["2026-07-26T10:00:00-0530", true],
  ["2026-07-26T10:00:00.123Z", true], ["2026-07-26T10:00:00", true],
  ["2026-12-31T23:59:59Z", true],
  // impossible calendar/clock components (Date.parse used to normalize these)
  ["2025-02-29T10:00:00Z", false], ["2026-02-30T10:00:00Z", false],
  ["2026-04-31T10:00:00Z", false], ["2026-06-31T10:00:00Z", false],
  ["2026-13-01T10:00:00Z", false], ["2026-00-10T10:00:00Z", false],
  ["2026-07-00T10:00:00Z", false], ["2026-07-32T10:00:00Z", false],
  ["2026-07-26T24:00:00Z", false], ["2026-07-26T10:60:00Z", false],
  ["2026-07-26T10:00:60Z", false], ["1900-02-29T00:00:00Z", false],
  // impossible timezone offsets: syntactically matched, semantically invalid
  ["2026-07-26T10:00:00+05:60", false], ["2026-07-26T10:00:00-05:60", false],
  ["2026-07-26T10:00:00+99:00", false], ["2026-07-26T10:00:00+99:99", false],
  ["2026-07-26T10:00:00+0560", false], ["2026-07-26T10:00:00+9900", false],
  ["not-a-date", false], ["", false], ["2026-07-26 10:00:00Z", false]
];
CASES.forEach(function(c){
  assert(isValidIso(c[0]) === c[1], "isValidIso(" + c[0] + ") expected " + c[1] + " got " + isValidIso(c[0]));
});
console.log("ISO-VALIDATOR OK");
"""


@requires_node
def test_js_iso_validator_rejects_impossible_calendar_dates():
    js = _js_var("ISO_RE") + "\n" + _js_func("isValidIso") + "\n" + _ISO_BODY
    _run_node(js)


# ---- import path: shared CJK marks and impossible dates rejected ----------- #

def _import_guard_decls():
    return (
        _js_var("IDENTIFIER_RE") + "\n"
        + _js_var("CJK_RE") + "\n"
        + _js_var("ISO_RE") + "\n"
        + _js_func("isValidIso") + "\n"
        + "var VALID_KS = [2, 5, 10];\n"
        + 'var RUN_ID = "run_x";\n'
        + 'var units = { "aaa1::dense": { export_k: 2 } };\n'
        + _js_func("firstNonSpaceIsFormula") + "\n"
        + _js_func("validateImportRow") + "\n"
    )


_IMPORT_BODY = """
function base(over){
  var r = { runId: "run_x", exId: "aaa1", retr: "dense", kRaw: "2",
            label: "lexical", notes: "", annotator: "amy",
            annotatedAt: "2026-07-26T10:00:00Z" };
  if (over) { for (var k in over) r[k] = over[k]; }
  return r;
}
function imp(r){
  return validateImportRow(r.runId, r.exId, r.retr, r.kRaw, r.label, r.notes,
                           r.annotator, r.annotatedAt, units, 2);
}

// legal control: a clean ASCII row imports
assert(imp(base()) === null, "valid ASCII row imports");

// Japanese shared marks (+ ordinary kana) rejected in label / notes / annotator
[0x30FC, 0x3099, 0x309A, 0x309B, 0x309C, 0x30FB, 0x30A2, 0x3042].forEach(function(cp){
  var m = String.fromCodePoint(cp);
  var e1 = imp(base({ label: "x" + m }));
  assert(e1 && e1.indexOf("CJK") !== -1, "import rejects mark in label U+" + cp.toString(16) + " got " + e1);
  var e2 = imp(base({ notes: "x" + m }));
  assert(e2 && e2.indexOf("CJK") !== -1, "import rejects mark in notes U+" + cp.toString(16));
  var e3 = imp(base({ annotator: "a" + m }));
  assert(e3 && e3.indexOf("CJK") !== -1, "import rejects mark in annotator U+" + cp.toString(16));
});

// impossible dates rejected; real leap day + offset accepted
assert(imp(base({ annotatedAt: "2025-02-29T10:00:00Z" })) !== null, "import rejects 2025-02-29");
assert(imp(base({ annotatedAt: "2026-02-30T10:00:00Z" })) !== null, "import rejects feb-30");
assert(imp(base({ annotatedAt: "2026-04-31T10:00:00Z" })) !== null, "import rejects apr-31");
assert(imp(base({ annotatedAt: "2024-02-29T10:00:00Z" })) === null, "import accepts leap day");
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00+05:30" })) === null, "import accepts offset");

// impossible timezone offsets rejected at import; legal Z / no-offset / +05:30 / +0530 import
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00+05:60" })) !== null, "import rejects +05:60");
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00-05:60" })) !== null, "import rejects -05:60");
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00+99:00" })) !== null, "import rejects +99:00");
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00+99:99" })) !== null, "import rejects +99:99");
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00Z" })) === null, "import accepts Z");
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00" })) === null, "import accepts no offset");
assert(imp(base({ annotatedAt: "2026-07-26T10:00:00+0530" })) === null, "import accepts +0530");

// non-CJK legal controls: accented Latin + emoji
assert(imp(base({ label: "caf" + String.fromCodePoint(0xE9) })) === null, "accented latin label imports");
assert(imp(base({ notes: "ok " + String.fromCodePoint(0x1F600) })) === null, "emoji notes imports");
console.log("IMPORT-GUARD OK");
"""


@requires_node
def test_js_import_guard_rejects_cjk_marks_and_impossible_dates():
    _run_node(_import_guard_decls() + _IMPORT_BODY)


# ---- export path: shared CJK marks and impossible dates blocked ------------ #

def _export_guard_decls():
    return (
        _js_var("IDENTIFIER_RE") + "\n"
        + _js_var("CJK_RE") + "\n"
        + _js_var("ISO_RE") + "\n"
        + _js_func("isValidIso") + "\n"
        + 'var RUN_ID = "run_x";\n'
        + 'var CSV_COLUMNS = ["run_id", "example_id", "retriever", "k", "label", "notes", "annotator", "annotated_at"];\n'
        + 'var statusMsg = "";\n'
        + "function setStatus(m){ statusMsg = m || \"\"; }\n"
        + "var downloads = 0;\n"
        # exportCsv success path needs Blob/URL/document/setTimeout stubs
        + "function Blob(parts, opts){ this.parts = parts; }\n"
        + 'var URL = { createObjectURL: function(){ return "blob:x"; }, revokeObjectURL: function(){} };\n'
        + "var document = { createElement: function(){ return { href: \"\", download: \"\", "
        + "click: function(){ downloads++; } }; }, body: { appendChild: function(){}, removeChild: function(){} } };\n"
        + "function setTimeout(fn){ }\n"
        # csvField contains a regex literal with quotes/brackets the extractor cannot
        # slice, so it is re-implemented here verbatim (plumbing, not the guard under test).
        + "function csvField(value){ var s = (value == null) ? \"\" : String(value); "
        + "return /[\",\\r\\n]/.test(s) ? '\"' + s.replace(/\"/g, '\"\"') + '\"' : s; }\n"
        + 'var cardRefs = [ { unit: { export_k: 2, example_id: "aaa1", card_retriever: "dense" }, key: "aaa1::dense" } ];\n'
        + "var annotations = {};\n"
        + _js_func("isAnnotated") + "\n"
        + _js_func("firstNonSpaceIsFormula") + "\n"
        + _js_func("exportCsv") + "\n"
    )


_EXPORT_BODY = """
function setAnn(over){
  annotations["aaa1::dense"] = { k: 2, label: "lexical", notes: "",
    annotator: "amy", annotated_at: "2026-07-26T10:00:00Z" };
  if (over) { for (var k in over) annotations["aaa1::dense"][k] = over[k]; }
}
function run(){ downloads = 0; statusMsg = ""; exportCsv(); }

// legal control: a clean annotation exports (one download, "Exported")
setAnn(); run();
assert(downloads === 1 && statusMsg.indexOf("Exported") !== -1, "clean annotation exports; got " + statusMsg);

// Japanese shared marks block the export
[0x30FC, 0x3099, 0x309A, 0x309B, 0x309C, 0x30FB].forEach(function(cp){
  setAnn({ label: "x" + String.fromCodePoint(cp) }); run();
  assert(downloads === 0 && statusMsg.indexOf("Export blocked") !== -1 && statusMsg.indexOf("CJK") !== -1,
         "export blocks CJK mark U+" + cp.toString(16) + " got " + statusMsg);
});

// impossible date blocked at the write boundary; real leap day exports
setAnn({ annotated_at: "2025-02-29T10:00:00Z" }); run();
assert(downloads === 0 && statusMsg.indexOf("Export blocked") !== -1, "export blocks impossible date; got " + statusMsg);
setAnn({ annotated_at: "2024-02-29T10:00:00Z" }); run();
assert(downloads === 1, "export allows real leap day; got " + statusMsg);

// impossible timezone offsets blocked at the write boundary; legal offsets export
["2026-07-26T10:00:00+05:60", "2026-07-26T10:00:00-05:60",
 "2026-07-26T10:00:00+99:00", "2026-07-26T10:00:00+99:99"].forEach(function(ts){
  setAnn({ annotated_at: ts }); run();
  assert(downloads === 0 && statusMsg.indexOf("Export blocked") !== -1,
         "export blocks impossible offset " + ts + "; got " + statusMsg);
});
["2026-07-26T10:00:00Z", "2026-07-26T10:00:00",
 "2026-07-26T10:00:00+05:30", "2026-07-26T10:00:00+0530"].forEach(function(ts){
  setAnn({ annotated_at: ts }); run();
  assert(downloads === 1, "export allows legal offset " + ts + "; got " + statusMsg);
});

// non-CJK legal controls export fine
setAnn({ label: "caf" + String.fromCodePoint(0xE9), notes: "ok " + String.fromCodePoint(0x1F600) }); run();
assert(downloads === 1, "accented latin + emoji export fine; got " + statusMsg);
console.log("EXPORT-GUARD OK");
"""


@requires_node
def test_js_export_guard_rejects_cjk_marks_and_impossible_dates():
    _run_node(_export_guard_decls() + _EXPORT_BODY)


def test_source_cjk_guard_covers_japanese_shared_marks():
    # Full Hiragana + Katakana blocks (U+3040-30FF) include the shared
    # Common/Inherited kana marks that Script=Hiragana/Katakana omit.
    assert "\\u3040-\\u30FF" in _js_regex("CJK_RE")


def test_source_single_strict_iso_validator():
    tpl = bfr.HTML_TEMPLATE
    iso = _js_func("isValidIso")
    assert "ISO_RE.exec(value)" in iso
    assert "mdays" in iso and "% 400" in iso  # real calendar + leap-year math
    assert "m[7]" in iso  # optional offset hour/minute captured + range-checked
    # the lenient shape-plus-Date.parse pattern is gone from every consumer
    assert tpl.count("isNaN(Date.parse") == 0
    # one validator shared by persisted load, import, and export
    assert "isValidIso(e.annotated_at)" in _js_func("validAnnotationEntry")
    assert "isValidIso(annotatedAt)" in _js_func("validateImportRow")
    assert "isValidIso(String(a.annotated_at" in tpl
