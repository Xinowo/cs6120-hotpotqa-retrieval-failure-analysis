"""
build_gold_rank_patterns.py

Generate the standalone, pooled-only gold-rank pattern CSV for one run:

    results/runs/<run_id>/
        details.jsonl   one line per question (evaluator-precomputed gold_ranks)
        config.json     run parameters + corpus_setting + top_k_max
            |
            v
    results/runs/<run_id>/gold_rank_patterns.csv

Authoritative design:
    docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md  (section 10)
Input run-directory contract:
    docs/specs/2026-07-12-failure-review-pipeline-design.md  (section 5.1)

Design principle (same as the failure-review generator): Python classifies from
the evaluator's already-precomputed gold_ranks; this script recomputes no metric
and reuses the frozen exact-string / first-occurrence / None-when-unobserved
gold-rank semantics. It writes ONE new artifact and touches nothing else -- not
evaluator.py, not RESULT_COLUMNS, not the formal result CSVs, not the accepted
failures_review.html / build_failure_report.py.

The config/details loaders and identifier/path guards are reused verbatim from
scripts.build_failure_report so the input contract is identical to the accepted
failure-review pipeline (spec section 5.1 cites that validation as the gold_ranks
authority). This script only ADDS the pooled/top-50 scope guards and the
partition classification; it imports build_failure_report without modifying it.

Usage:
    python scripts/reporting/build_gold_rank_patterns.py --run 2026-07-17_a
    python scripts/reporting/build_gold_rank_patterns.py --run 2026-07-17_a --out /tmp/patterns.csv
"""

import argparse
import csv
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from scripts import build_failure_report as bfr
from src.rank_pattern import (
    RANK_PATTERN_SCHEMA,
    RANK_PATTERN_SCOPE,
    STORED_DEPTH,
    band_count_tuple,
    pattern_from_counts,
)

DEFAULT_OUTPUT_NAME = "gold_rank_patterns.csv"

# Frozen output columns, in order (spec section 10.2). Every field is always
# populated: no nulls, no empty cells. Absence of a gold is encoded as band
# membership (n_not_in_top50), never as a blank cell.
CSV_COLUMNS = [
    "run_id",
    "example_id",
    "retriever",
    "question_type",
    "gold_count",
    "n_top5",
    "n_rank6_10",
    "n_rank11_50",
    "n_not_in_top50",
    "rank_pattern",
    "rank_pattern_schema",
    "rank_pattern_scope",
    "stored_depth",
]

# Frozen output vocabularies (spec section 10.2): the `retriever` and
# `question_type` columns may hold ONLY these values. The reused failure-report
# loader is deliberately more permissive (any identifier-shaped retriever name,
# any string question_type), so the generator must enforce these itself before
# writing -- otherwise it could emit a file that violates the frozen schema
# (e.g. a `rerank` retriever, an `other`/empty question_type) even though the
# current formal run happens to contain only legal values.
VALID_RETRIEVERS = ("bm25", "dense")
VALID_QUESTION_TYPES = ("bridge", "comparison")


def validate_pooled_run(config):
    """Refuse any run that is not pooled top-50 (spec section 10.1 / 3.1).

    `rank_pattern` and its fixed 4 bands are defined only for the pooled setting
    with exactly 50 stored results. A non-pooled setting, or a different stored
    depth, is a different schema version -- fail loudly rather than emit a CSV
    whose `not_in_top50` band would silently mean something else.
    """
    setting = config.get("corpus_setting")
    if setting != "pooled":
        raise ValueError(
            f"gold_rank_patterns is pooled-only; corpus_setting={setting!r} "
            f"(expected 'pooled')."
        )
    top_k_max = config.get("top_k_max")
    if isinstance(top_k_max, bool) or top_k_max != STORED_DEPTH:
        raise ValueError(
            f"gold_rank_patterns requires top_k_max == {STORED_DEPTH}; "
            f"got {top_k_max!r}."
        )


def build_rows(config, records):
    """Classify every (example_id, retriever) unit into one CSV row.

    One row per retriever present in each record; the key is
    ``(example_id, retriever)`` and `rank_pattern` is k-independent, so k is not
    part of the key. Rows are returned sorted by ``(example_id, retriever)`` as
    exact strings, so identical input yields byte-identical output.
    """
    run_id = config["run_id"]
    # Enforce the frozen retriever vocabulary once from the run's declared
    # retrievers (spec section 10.2). load_details guarantees each record's
    # retriever set equals config.retrievers, so this covers every emitted row.
    unknown_retrievers = sorted(
        name for name in config["retrievers"] if name not in VALID_RETRIEVERS
    )
    if unknown_retrievers:
        raise ValueError(
            f"unsupported retriever(s) {unknown_retrievers}; pooled v1 emits "
            f"only {list(VALID_RETRIEVERS)}."
        )

    rows = []
    for record in records:
        example_id = record["example_id"]
        question_type = record["question_type"]
        # Enforce the frozen question_type vocabulary before any output write
        # (spec section 10.2). This rejects unknown values like "other" and the
        # empty string, the latter of which would otherwise emit a forbidden
        # empty CSV cell.
        if question_type not in VALID_QUESTION_TYPES:
            raise ValueError(
                f"{example_id}: unsupported question_type {question_type!r}; "
                f"pooled v1 emits only {list(VALID_QUESTION_TYPES)}."
            )
        # Deduplicate gold titles before classification (spec section 4.1 /
        # 14.1). In the formal pooled path they are already deduplicated
        # upstream; this keeps the guarantee explicit and local.
        unique_titles = list(dict.fromkeys(record["gold_titles"]))
        for name in record["retrievers"]:
            sub = record["retrievers"][name]
            # The observation horizon must be exactly the pooled stored depth so
            # a None gold rank provably means "absent from the stored 50", not
            # "the stored list was short" (spec section 14.6).
            stored = len(sub["top_k"])
            if stored != STORED_DEPTH:
                raise ValueError(
                    f"{example_id}/{name}: stored depth {stored} != "
                    f"{STORED_DEPTH}; pooled v1 requires exactly {STORED_DEPTH} "
                    f"stored results per unit."
                )
            gold_ranks = sub["gold_ranks"]
            # The evaluator's gold_ranks keys are exactly the example's gold
            # titles (spec section 5.1). The reused loader rejects a MISSING
            # declared title but tolerates EXTRA keys; require exact set equality
            # here so a malformed unit cannot cross the boundary with silently
            # discarded ranks (spec section 5.1 / 17).
            gold_key_set = set(gold_ranks)
            title_set = set(unique_titles)
            if gold_key_set != title_set:
                missing = sorted(title_set - gold_key_set)
                extra = sorted(gold_key_set - title_set)
                raise ValueError(
                    f"{example_id}/{name}: gold_ranks keys must equal the gold "
                    f"titles (missing={missing}, extra={extra})."
                )
            # Consume the evaluator's precomputed ranks directly (spec section
            # 5.1). band_count_tuple fails loudly on a gold count other than 2
            # or any bad rank, so a malformed unit never yields a coerced label.
            ranks = [gold_ranks[title] for title in unique_titles]
            counts = band_count_tuple(ranks)
            pattern = pattern_from_counts(counts)
            rows.append(
                {
                    "run_id": run_id,
                    "example_id": example_id,
                    "retriever": name,
                    "question_type": question_type,
                    "gold_count": len(unique_titles),
                    "n_top5": counts[0],
                    "n_rank6_10": counts[1],
                    "n_rank11_50": counts[2],
                    "n_not_in_top50": counts[3],
                    "rank_pattern": pattern,
                    "rank_pattern_schema": RANK_PATTERN_SCHEMA,
                    "rank_pattern_scope": RANK_PATTERN_SCOPE,
                    "stored_depth": STORED_DEPTH,
                }
            )

    rows.sort(key=lambda row: (row["example_id"], row["retriever"]))
    return rows


def write_csv(rows, out_path):
    """Write rows as UTF-8 (no BOM), LF-terminated, deterministic CSV.

    `newline=""` plus an explicit LF line terminator makes the bytes identical
    across platforms; standard minimal quoting applies. The header is the frozen
    column order; every row is emitted in that same order.
    """
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(CSV_COLUMNS)
        for row in rows:
            writer.writerow([row[column] for column in CSV_COLUMNS])


def _protected_sibling_paths(run_dir):
    """The run's own artifacts this generator must never overwrite."""
    return tuple(
        os.path.join(run_dir, name)
        for name in ("config.json", "details.jsonl", "metrics.json",
                     "failures_review.html")
    )


def generate_gold_rank_patterns(run_id, runs_root="results/runs", out=None):
    """Full pipeline: validate scope, load run, classify, write CSV.

    Returns the output path. Refuses a non-pooled / non-top-50 run and refuses
    to overwrite any of the run's existing artifacts.
    """
    bfr.validate_run_id_arg(run_id)

    run_dir = os.path.join(runs_root, run_id)
    config_path = os.path.join(run_dir, "config.json")
    details_path = os.path.join(run_dir, "details.jsonl")

    if not os.path.isdir(run_dir):
        raise FileNotFoundError(f"run directory not found: {run_dir}")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"config.json not found: {config_path}")
    if not os.path.isfile(details_path):
        raise FileNotFoundError(f"details.jsonl not found: {details_path}")

    config = bfr.load_config(config_path, run_id)
    validate_pooled_run(config)
    records = bfr.load_details(details_path, config)

    rows = build_rows(config, records)

    out_path = out if out is not None else os.path.join(run_dir, DEFAULT_OUTPUT_NAME)
    if os.path.isdir(out_path):
        raise ValueError(f"--out is an existing directory: {out_path}")
    if bfr._is_input_alias(out_path, _protected_sibling_paths(run_dir)):
        raise ValueError(
            f"--out would overwrite a run artifact: {out_path}"
        )

    parent = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(parent, exist_ok=True)
    write_csv(rows, out_path)
    return out_path


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate the pooled top-50 gold_rank_patterns.csv for a run "
        "directory (details.jsonl + config.json)."
    )
    parser.add_argument(
        "--run",
        dest="run_id",
        required=True,
        help="Run directory name under --runs-root (e.g. 2026-07-17_a)",
    )
    parser.add_argument(
        "--runs-root",
        default="results/runs",
        help="Root directory that run directories live under",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output CSV path "
        "(default: <runs-root>/<run_id>/gold_rank_patterns.csv)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out_path = generate_gold_rank_patterns(
        run_id=args.run_id,
        runs_root=args.runs_root,
        out=args.out,
    )
    print(f"Wrote gold-rank patterns to {out_path}")
    return out_path


if __name__ == "__main__":
    main()
