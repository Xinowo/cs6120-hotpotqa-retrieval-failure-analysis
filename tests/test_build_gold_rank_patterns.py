"""
test_build_gold_rank_patterns.py

Offline output-contract tests for the pooled gold_rank_patterns.csv generator
(scripts/reporting/build_gold_rank_patterns.py), covering spec section 16.9 and
the acceptance criteria (section 17):

  - exact frozen columns in order, one row per (example_id, retriever), rows
    sorted by (example_id, retriever), no empty cells, constant schema/scope/
    depth, UTF-8 without BOM;
  - identical input yields byte-identical output;
  - generation refuses a non-pooled run, a top_k_max != 50 run, a gold count
    other than 2, a stored depth other than 50, and an --out that would clobber
    a run artifact.

A gated integration test regenerates the formal run's 1000-row artifact when the
local run directory is present, and proves the on-disk artifact is byte-for-byte
reproducible.

Synthetic run data conforms to the same details.jsonl / config.json contract the
accepted failure-review pipeline validates (scripts.build_failure_report), so
these tests never touch a model, network, or HotpotQA data.
"""

import csv
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from scripts.reporting import build_gold_rank_patterns as grp
from src.rank_pattern import (
    CANONICAL_RANK_PATTERNS,
    RANK_PATTERN_SCHEMA,
    RANK_PATTERN_SCOPE,
    STORED_DEPTH,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FORMAL_RUN_DIR = os.path.join(REPO_ROOT, "results", "runs", "2026-07-17_a")


# --------------------------------------------------------------------------- #
# Builders for synthetic (valid) pooled run data
# --------------------------------------------------------------------------- #

def make_top_k(n=STORED_DEPTH, placements=None):
    """A top_k list of length n with consecutive ranks 1..n; `placements` maps a
    1-based rank -> gold title to seat at that position."""
    placements = placements or {}
    top_k = []
    for i in range(n):
        rank = i + 1
        title = placements.get(rank, f"p{rank}")
        top_k.append(
            {"rank": rank, "title": title, "score": 1.0 / rank, "text": f"text {rank}"}
        )
    return top_k


def make_sub(gold_ranks, top_k_len=STORED_DEPTH):
    """One retriever sub-record whose top_k seats each ranked gold, and whose
    any-evidence metrics are consistent and monotone (as load_details requires)."""
    placements = {rank: title for title, rank in gold_ranks.items() if rank is not None}
    top_k = make_top_k(top_k_len, placements)

    def any_at(k):
        return any(r is not None and r <= k for r in gold_ranks.values())

    return {
        "top_k": top_k,
        "gold_ranks": dict(gold_ranks),
        "metrics": {f"any_evidence_recall@{k}": any_at(k) for k in (2, 5, 10)},
    }


def make_record(example_id, gold_titles, ranks_by_retriever,
                question_type="bridge", top_k_len=STORED_DEPTH):
    return {
        "example_id": example_id,
        "question": "Question?",
        "question_type": question_type,
        "gold_titles": list(gold_titles),
        "retrievers": {
            name: make_sub(ranks, top_k_len)
            for name, ranks in ranks_by_retriever.items()
        },
    }


def make_config(run_id="testrun_a", retrievers=("dense", "bm25"),
                corpus_setting="pooled", top_k_max=STORED_DEPTH, **extra):
    config = {
        "run_id": run_id,
        "n": 2,
        "split": "validation",
        "corpus_setting": corpus_setting,
        "corpus_size": 4937,
        "top_k_max": top_k_max,
        "retrievers": {name: f"model-{name}" for name in retrievers},
        "timestamp": "2026-07-17T20:16:18",
        "script": "scripts/reporting/build_gold_rank_patterns.py",
        "git_commit": "deadbeef",
    }
    config.update(extra)
    return config


def write_run(tmp_path, records, config):
    run_id = config["run_id"]
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


def two_record_fixture():
    """Two examples x two retrievers = four units spanning several patterns."""
    rec_a = make_record(
        "aaa111",
        ["Gold Alpha", "Gold Beta"],
        {
            "dense": {"Gold Alpha": 2, "Gold Beta": 8},     # one_top5_one_6_10
            "bm25": {"Gold Alpha": 2, "Gold Beta": None},   # one_top5_one_not_in_top50
        },
    )
    rec_b = make_record(
        "bbb222",
        ["Gold Gamma", "Gold Delta"],
        {
            "dense": {"Gold Gamma": 1, "Gold Delta": 5},    # both_in_top5
            "bm25": {"Gold Gamma": None, "Gold Delta": None},  # both_not_in_top50
        },
        question_type="comparison",
    )
    return [rec_a, rec_b]


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def generate(tmp_path, records=None, config=None, out=None):
    records = two_record_fixture() if records is None else records
    config = make_config() if config is None else config
    runs_root = write_run(tmp_path, records, config)
    return grp.generate_gold_rank_patterns(
        run_id=config["run_id"], runs_root=runs_root, out=out
    )


# --------------------------------------------------------------------------- #
# Schema / ordering / cells
# --------------------------------------------------------------------------- #

def test_columns_exact_order(tmp_path):
    rows = read_csv(generate(tmp_path))
    assert rows[0] == grp.CSV_COLUMNS


def test_one_row_per_unit_sorted_by_key(tmp_path):
    rows = read_csv(generate(tmp_path))
    header, data = rows[0], rows[1:]
    ix = {name: header.index(name) for name in ("example_id", "retriever")}
    keys = [(r[ix["example_id"]], r[ix["retriever"]]) for r in data]
    # 2 examples x 2 retrievers = 4 units, one row each, keys unique and sorted.
    assert len(keys) == 4
    assert len(set(keys)) == 4
    assert keys == sorted(keys)
    assert keys == [
        ("aaa111", "bm25"), ("aaa111", "dense"),
        ("bbb222", "bm25"), ("bbb222", "dense"),
    ]


def test_no_empty_cells(tmp_path):
    rows = read_csv(generate(tmp_path))
    for row in rows[1:]:
        assert len(row) == len(grp.CSV_COLUMNS)
        assert all(cell != "" for cell in row)


def test_constant_provenance_columns(tmp_path):
    rows = read_csv(generate(tmp_path))
    header, data = rows[0], rows[1:]
    ix = {name: header.index(name) for name in
          ("rank_pattern_schema", "rank_pattern_scope", "stored_depth",
           "gold_count", "run_id")}
    for row in data:
        assert row[ix["rank_pattern_schema"]] == RANK_PATTERN_SCHEMA
        assert row[ix["rank_pattern_scope"]] == RANK_PATTERN_SCOPE
        assert row[ix["stored_depth"]] == str(STORED_DEPTH)
        assert row[ix["gold_count"]] == "2"
        assert row[ix["run_id"]] == "testrun_a"


def test_band_counts_sum_to_gold_count_and_pattern_valid(tmp_path):
    rows = read_csv(generate(tmp_path))
    header, data = rows[0], rows[1:]
    ix = {name: header.index(name) for name in
          ("n_top5", "n_rank6_10", "n_rank11_50", "n_not_in_top50",
           "rank_pattern")}
    for row in data:
        counts = [int(row[ix[c]]) for c in
                  ("n_top5", "n_rank6_10", "n_rank11_50", "n_not_in_top50")]
        assert sum(counts) == 2
        assert row[ix["rank_pattern"]] in CANONICAL_RANK_PATTERNS


def test_known_pattern_values(tmp_path):
    rows = read_csv(generate(tmp_path))
    header, data = rows[0], rows[1:]
    ix = {name: header.index(name) for name in
          ("example_id", "retriever", "rank_pattern", "n_top5", "n_rank6_10",
           "n_not_in_top50")}
    by_key = {(r[ix["example_id"]], r[ix["retriever"]]): r for r in data}

    dense_a = by_key[("aaa111", "dense")]
    assert dense_a[ix["rank_pattern"]] == "one_top5_one_6_10"
    assert dense_a[ix["n_top5"]] == "1"
    assert dense_a[ix["n_rank6_10"]] == "1"

    bm25_a = by_key[("aaa111", "bm25")]
    assert bm25_a[ix["rank_pattern"]] == "one_top5_one_not_in_top50"
    assert bm25_a[ix["n_top5"]] == "1"
    assert bm25_a[ix["n_not_in_top50"]] == "1"

    assert by_key[("bbb222", "dense")][ix["rank_pattern"]] == "both_in_top5"
    assert by_key[("bbb222", "bm25")][ix["rank_pattern"]] == "both_not_in_top50"


# --------------------------------------------------------------------------- #
# Determinism / encoding
# --------------------------------------------------------------------------- #

def test_byte_identical_on_identical_input(tmp_path):
    out1 = generate(tmp_path, out=str(tmp_path / "a.csv"))
    out2 = generate(tmp_path / "second", out=str(tmp_path / "b.csv"))
    with open(out1, "rb") as f:
        b1 = f.read()
    with open(out2, "rb") as f:
        b2 = f.read()
    assert b1 == b2


def test_utf8_without_bom_and_lf_terminated(tmp_path):
    out = generate(tmp_path, out=str(tmp_path / "p.csv"))
    with open(out, "rb") as f:
        raw = f.read()
    assert not raw.startswith(b"\xef\xbb\xbf")          # no UTF-8 BOM
    assert raw.startswith(b"run_id,")                    # header first
    assert b"\r\n" not in raw                             # LF-only line endings
    assert raw.endswith(b"\n")


# --------------------------------------------------------------------------- #
# Refusals (fail loudly)
# --------------------------------------------------------------------------- #

def test_refuses_non_pooled_run(tmp_path):
    config = make_config(corpus_setting="per_question")
    with pytest.raises(ValueError, match="pooled-only"):
        generate(tmp_path, config=config)


def test_refuses_wrong_top_k_max(tmp_path):
    config = make_config(top_k_max=10)
    with pytest.raises(ValueError, match="top_k_max"):
        generate(tmp_path, config=config)


def test_validate_pooled_run_rejects_bool_top_k_max():
    # bool subclasses int; a True top_k_max must not slip through as "1"/"50".
    with pytest.raises(ValueError):
        grp.validate_pooled_run(make_config(top_k_max=True))


def test_refuses_gold_count_other_than_two(tmp_path):
    record = make_record(
        "ccc333",
        ["G1", "G2", "G3"],
        {
            "dense": {"G1": 1, "G2": 2, "G3": 3},
            "bm25": {"G1": 1, "G2": 2, "G3": 3},
        },
    )
    with pytest.raises(ValueError):
        generate(tmp_path, records=[record])


def test_refuses_stored_depth_other_than_fifty(tmp_path):
    # A unit that stored only 49 results must fail loudly, not silently emit
    # not_in_top50 for a gold that a full 50-deep list might have contained.
    record = make_record(
        "ddd444",
        ["G1", "G2"],
        {"dense": {"G1": 1, "G2": 2}, "bm25": {"G1": 1, "G2": 2}},
        top_k_len=49,
    )
    with pytest.raises(ValueError, match="stored depth"):
        generate(tmp_path, records=[record])


def test_refuses_out_alias_of_input(tmp_path):
    config = make_config()
    runs_root = write_run(tmp_path, two_record_fixture(), config)
    details_path = os.path.join(runs_root, config["run_id"], "details.jsonl")
    with pytest.raises(ValueError, match="overwrite"):
        grp.generate_gold_rank_patterns(
            run_id=config["run_id"], runs_root=runs_root, out=details_path
        )


# --------------------------------------------------------------------------- #
# Frozen vocabulary + exact key-set enforcement (round-1 review F-1 / F-2)
#
# Each invalid run is paired below with a legal control, and every rejection is
# additionally proven to neither create nor overwrite an output file.
# --------------------------------------------------------------------------- #

def _run_unknown_retriever():
    config = make_config(retrievers=("dense", "rerank"))
    record = make_record(
        "aaa111", ["Gold A", "Gold B"],
        {"dense": {"Gold A": 1, "Gold B": 5},
         "rerank": {"Gold A": 1, "Gold B": 5}},
    )
    return config, [record], "unsupported retriever"


def _run_unknown_question_type():
    record = make_record(
        "aaa111", ["Gold A", "Gold B"],
        {"dense": {"Gold A": 1, "Gold B": 5}, "bm25": {"Gold A": 1, "Gold B": 5}},
        question_type="other",
    )
    return make_config(), [record], "question_type"


def _run_empty_question_type():
    record = make_record(
        "aaa111", ["Gold A", "Gold B"],
        {"dense": {"Gold A": 1, "Gold B": 5}, "bm25": {"Gold A": 1, "Gold B": 5}},
        question_type="",
    )
    return make_config(), [record], "question_type"


def _run_extra_gold_key():
    record = make_record(
        "aaa111", ["Gold A", "Gold B"],
        {"dense": {"Gold A": 1, "Gold B": 6, "Gold C": 11},
         "bm25": {"Gold A": 1, "Gold B": 6, "Gold C": 11}},
    )
    return make_config(), [record], "gold_ranks keys"


# name -> (factory, expected-error substring)
INVALID_RUNS = {
    "unknown_retriever": _run_unknown_retriever,
    "unknown_question_type": _run_unknown_question_type,
    "empty_question_type": _run_empty_question_type,
    "extra_gold_key": _run_extra_gold_key,
}


@pytest.mark.parametrize("kind", sorted(INVALID_RUNS))
def test_rejects_invalid_vocabulary_or_keys(tmp_path, kind):
    config, records, match = INVALID_RUNS[kind]()
    with pytest.raises(ValueError, match=match):
        generate(tmp_path, records=records, config=config)


@pytest.mark.parametrize("kind", sorted(INVALID_RUNS))
def test_rejection_does_not_create_output(tmp_path, kind):
    config, records, _ = INVALID_RUNS[kind]()
    runs_root = write_run(tmp_path, records, config)
    out_path = os.path.join(runs_root, config["run_id"], "gold_rank_patterns.csv")
    assert not os.path.exists(out_path)
    with pytest.raises(ValueError):
        grp.generate_gold_rank_patterns(run_id=config["run_id"], runs_root=runs_root)
    # A rejected run must not leave a partial/new output behind.
    assert not os.path.exists(out_path)


@pytest.mark.parametrize("kind", sorted(INVALID_RUNS))
def test_rejection_does_not_overwrite_existing_output(tmp_path, kind):
    config, records, _ = INVALID_RUNS[kind]()
    runs_root = write_run(tmp_path, records, config)
    out_path = os.path.join(runs_root, config["run_id"], "gold_rank_patterns.csv")
    sentinel = b"PRE-EXISTING-DO-NOT-CLOBBER\n"
    with open(out_path, "wb") as f:
        f.write(sentinel)
    with pytest.raises(ValueError):
        grp.generate_gold_rank_patterns(run_id=config["run_id"], runs_root=runs_root)
    with open(out_path, "rb") as f:
        assert f.read() == sentinel  # untouched by the rejected run


def test_missing_gold_ranks_key_is_rejected(tmp_path):
    # A declared gold title absent from gold_ranks is rejected (by the reused
    # loader); retained as the missing-key half of the F-2 key-set contract.
    record = make_record(
        "aaa111", ["Gold A", "Gold B"],
        {"dense": {"Gold A": 1}, "bm25": {"Gold A": 1}},
    )
    with pytest.raises(ValueError):
        generate(tmp_path, records=[record])


def test_accepts_both_allowed_retrievers(tmp_path):
    # Legal control for F-1: dense + bm25 both pass and appear in the output.
    rows = read_csv(generate(tmp_path))
    ix = grp.CSV_COLUMNS.index("retriever")
    assert {row[ix] for row in rows[1:]} == {"bm25", "dense"}


def test_accepts_both_allowed_question_types(tmp_path):
    # Legal control for F-1: bridge + comparison both pass, no empty cell.
    rows = read_csv(generate(tmp_path))
    ix = grp.CSV_COLUMNS.index("question_type")
    values = {row[ix] for row in rows[1:]}
    assert values == {"bridge", "comparison"}
    assert "" not in values


def test_accepts_exact_gold_ranks_keys(tmp_path):
    # Legal control for F-2: gold_ranks keys exactly equal to gold_titles pass.
    record = make_record(
        "aaa111", ["Gold A", "Gold B"],
        {"dense": {"Gold A": 1, "Gold B": 6}, "bm25": {"Gold A": 1, "Gold B": 6}},
    )
    rows = read_csv(generate(tmp_path, records=[record]))
    assert len(rows) == 1 + 2  # header + 2 units, nothing rejected


# --------------------------------------------------------------------------- #
# CLI end-to-end
# --------------------------------------------------------------------------- #

def test_cli_writes_default_artifact(tmp_path):
    config = make_config()
    runs_root = write_run(tmp_path, two_record_fixture(), config)
    script = os.path.join(REPO_ROOT, "scripts", "reporting",
                          "build_gold_rank_patterns.py")
    proc = subprocess.run(
        [sys.executable, script, "--run", config["run_id"],
         "--runs-root", runs_root],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    out_path = os.path.join(runs_root, config["run_id"], "gold_rank_patterns.csv")
    assert os.path.isfile(out_path)
    rows = read_csv(out_path)
    assert rows[0] == grp.CSV_COLUMNS
    assert len(rows) == 1 + 4  # header + 4 units


# --------------------------------------------------------------------------- #
# Formal-run integration (gated on the local, gitignored run directory)
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(
    not os.path.isfile(os.path.join(FORMAL_RUN_DIR, "details.jsonl")),
    reason="formal run directory results/runs/2026-07-17_a is not present",
)
def test_formal_run_has_1000_rows_and_is_reproducible(tmp_path):
    fresh = grp.generate_gold_rank_patterns(
        run_id="2026-07-17_a",
        runs_root=os.path.join(REPO_ROOT, "results", "runs"),
        out=str(tmp_path / "regen.csv"),
    )
    rows = read_csv(fresh)
    header, data = rows[0], rows[1:]
    assert header == grp.CSV_COLUMNS
    # 500 examples x 2 retrievers = 1000 units, one row each.
    assert len(data) == 1000
    ix = {name: header.index(name) for name in ("example_id", "retriever",
                                                "rank_pattern", "run_id")}
    keys = [(r[ix["example_id"]], r[ix["retriever"]]) for r in data]
    assert len(set(keys)) == 1000
    assert keys == sorted(keys)
    assert all(r[ix["run_id"]] == "2026-07-17_a" for r in data)
    assert all(r[ix["rank_pattern"]] in CANONICAL_RANK_PATTERNS for r in data)

    on_disk = os.path.join(FORMAL_RUN_DIR, "gold_rank_patterns.csv")
    if os.path.isfile(on_disk):
        with open(fresh, "rb") as f:
            fresh_bytes = f.read()
        with open(on_disk, "rb") as f:
            disk_bytes = f.read()
        assert fresh_bytes == disk_bytes  # committed artifact is reproducible
