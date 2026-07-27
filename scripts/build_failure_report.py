"""
build_failure_report.py  (the failure-review HTML generator)

Reads a failure-review run directory produced by
`scripts/run_failure_review.py` and renders a self-contained, single-file
`failures_review.html` for manual failure annotation.

    results/runs/<run_id>/
        details.jsonl   one line per question (top_k / gold_ranks / metrics)
        config.json     run parameters + corpus_setting + git_commit
        metrics.json    aggregate metrics (not read here)
            |
            v
    results/runs/<run_id>/failures_review.html

Design principle (spec section 3): **Python computes, the HTML only displays.**
Every evaluation quantity (recall@k, gold hit ranks) is already computed by
`src/evaluator.py` and stored in details.jsonl. This generator only *validates*
and *reshapes* those fields into display structures (`missed_ks`, `export_k`,
`gold_display`, `worst_gold_rank`); it re-computes no metric. The JavaScript
embedded in the page only renders, filters, highlights, annotates, and
imports/exports CSV -- it contains no metric or taxonomy logic.

Authoritative design:
    docs/specs/2026-07-12-failure-review-pipeline-design.md  (sections 5-6)
    docs/Local/analysis/build_failure_report_design.md        (full contract)

Usage:
    python scripts/build_failure_report.py --run 2026-07-17_a
    python scripts/build_failure_report.py --run 2026-07-17_a --retriever dense --k 2
    python scripts/build_failure_report.py --run 2026-07-17_a --out /tmp/review.html
"""

import argparse
import json
import math
import os
import re
import sys

# The fixed metric cutoff domain for this pipeline's runner. Both the CLI --k
# and the in-browser k dropdown are restricted to these; a record missing any
# of these three metrics is an error, never silently recomputed.
VALID_KS = (2, 5, 10)

# Machine-generated identifier columns (run_id / example_id / retriever) are
# written into a CSV that may be opened in Excel/Sheets and used as a
# localStorage key component. This whitelist blocks both spreadsheet formula
# injection (the first character can never be = + - @) and the "::" storage-key
# delimiter (no ':' allowed). See design section 7.4.
#
# NOTE: matched with re.fullmatch via is_valid_identifier(). The pattern carries
# no anchors on purpose -- an anchored `...$` would match immediately before a
# trailing newline in re.match(), letting `"abc\n"` slip through; fullmatch on
# an unanchored pattern requires the WHOLE string to match, so any newline
# (or other out-of-class character) is rejected.
IDENTIFIER_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._-]*")


def is_valid_identifier(value):
    """True only if `value` is a string matching IDENTIFIER_RE in full (no
    trailing newline or any other out-of-whitelist character)."""
    return isinstance(value, str) and IDENTIFIER_RE.fullmatch(value) is not None

# The single placeholder the HTML template carries; replaced exactly once with
# the HTML-safe-serialized payload.
DATA_PLACEHOLDER = "/*DATA*/"


# --------------------------------------------------------------------------- #
# Path / argument safety
# --------------------------------------------------------------------------- #

def validate_run_id_arg(run_id):
    """`--run` names a directory under runs-root, not an arbitrary path.

    Reject empty values, absolute paths, `.`/`..`, and anything containing a
    path separator so a crafted run id cannot escape the runs root. The
    stricter IDENTIFIER_RE syntax is enforced later against config.run_id
    (which must equal this value)."""
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("run id must be a non-empty string")
    if os.path.isabs(run_id):
        raise ValueError(f"run id must be a directory name, not an absolute path: {run_id!r}")
    if run_id in (".", ".."):
        raise ValueError(f"invalid run id: {run_id!r}")
    if "/" in run_id or "\\" in run_id or os.sep in run_id:
        raise ValueError(f"run id must not contain path separators: {run_id!r}")


# --------------------------------------------------------------------------- #
# config.json / details.jsonl loading + validation (schema checks, not metrics)
# --------------------------------------------------------------------------- #

def load_config(config_path, run_id):
    """Read and validate config.json. The full object is preserved for the
    page header; only the fields the generator relies on are validated."""
    with open(config_path, encoding="utf-8") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"config.json: invalid JSON: {e}")

    if not isinstance(config, dict):
        raise ValueError("config.json: top-level value must be a JSON object")

    cfg_run = config.get("run_id")
    if cfg_run != run_id:
        raise ValueError(
            f"config.json: run_id mismatch (expected {run_id!r}, got {cfg_run!r})"
        )
    if not is_valid_identifier(cfg_run):
        raise ValueError(f"config.json: run_id {cfg_run!r} is not a valid identifier")

    retrievers = config.get("retrievers")
    if not isinstance(retrievers, dict) or not retrievers:
        raise ValueError("config.json: retrievers must be a non-empty object")
    for name in retrievers:
        if not is_valid_identifier(name):
            raise ValueError(
                f"config.json: retriever name {name!r} is not a valid identifier"
            )

    top_k_max = config.get("top_k_max")
    if not isinstance(top_k_max, int) or isinstance(top_k_max, bool) or top_k_max < 10:
        raise ValueError(
            f"config.json: top_k_max must be an integer >= 10, got {top_k_max!r}"
        )

    return config


def _require_finite(value, path, fail):
    """Recursively reject NaN / +-Infinity anywhere in a record so the payload
    is always standard JSON (serialized with allow_nan=False downstream)."""
    if isinstance(value, bool):
        return
    if isinstance(value, float) and not math.isfinite(value):
        fail(f"{path} is not a finite number ({value})")
    elif isinstance(value, dict):
        for k, v in value.items():
            _require_finite(v, f"{path}.{k}", fail)
    elif isinstance(value, list):
        for idx, v in enumerate(value):
            _require_finite(v, f"{path}[{idx}]", fail)


def validate_record(record, line_no, retriever_keys, top_k_max, seen_ids):
    """Validate one details.jsonl record against the schema. Raises ValueError
    with a line-numbered message on any violation. These are structural /
    consistency checks; no metric is recomputed."""

    def fail(msg):
        raise ValueError(f"details.jsonl line {line_no}: {msg}")

    if not isinstance(record, dict):
        fail("record is not a JSON object")

    example_id = record.get("example_id")
    if not isinstance(example_id, str) or not example_id:
        fail("example_id must be a non-empty string")
    if not is_valid_identifier(example_id):
        fail(f"example_id {example_id!r} is not a valid identifier")
    if example_id in seen_ids:
        fail(f"duplicate example_id {example_id!r}")

    if not isinstance(record.get("question"), str):
        fail("question must be a string")
    if not isinstance(record.get("question_type"), str):
        fail("question_type must be a string")

    gold_titles = record.get("gold_titles")
    if (
        not isinstance(gold_titles, list)
        or not gold_titles
        or not all(isinstance(t, str) and t for t in gold_titles)
    ):
        fail("gold_titles must be a non-empty list of non-empty strings")

    retrievers = record.get("retrievers")
    if not isinstance(retrievers, dict) or not retrievers:
        fail("retrievers must be a non-empty object")

    record_keys = set(retrievers)
    if record_keys != retriever_keys:
        missing = sorted(retriever_keys - record_keys)
        extra = sorted(record_keys - retriever_keys)
        fail(
            f"retriever set {sorted(record_keys)} != config.retrievers "
            f"{sorted(retriever_keys)} (missing={missing}, extra={extra})"
        )

    for name, sub in retrievers.items():
        base = f"retrievers.{name}"
        if not isinstance(sub, dict):
            fail(f"{base} must be an object")

        top_k = sub.get("top_k")
        gold_ranks = sub.get("gold_ranks")
        metrics = sub.get("metrics")
        if not isinstance(top_k, list):
            fail(f"{base}.top_k must be a list")
        if not isinstance(gold_ranks, dict):
            fail(f"{base}.gold_ranks must be an object")
        if not isinstance(metrics, dict):
            fail(f"{base}.metrics must be an object")

        for idx, item in enumerate(top_k):
            item_path = f"{base}.top_k[{idx}]"
            if not isinstance(item, dict):
                fail(f"{item_path} must be an object")
            rank = item.get("rank")
            if not isinstance(rank, int) or isinstance(rank, bool):
                fail(f"{item_path}.rank must be an integer")
            if rank != idx + 1:
                fail(
                    f"{base}.top_k ranks must be consecutive from 1 "
                    f"(expected {idx + 1}, got {rank})"
                )
            if rank > top_k_max:
                fail(f"{item_path}.rank {rank} exceeds top_k_max {top_k_max}")
            if not isinstance(item.get("title"), str):
                fail(f"{item_path}.title must be a string")
            score = item.get("score")
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                fail(f"{item_path}.score must be a number")
            if not isinstance(item.get("text"), str):
                fail(f"{item_path}.text must be a string")

        for title in gold_titles:
            if title not in gold_ranks:
                fail(f"{base}.gold_ranks is missing gold title {title!r}")
            gr = gold_ranks[title]
            if gr is None:
                continue
            if not isinstance(gr, int) or isinstance(gr, bool):
                fail(f"{base}.gold_ranks[{title!r}] must be null or an integer")
            if gr < 1 or gr > top_k_max:
                fail(
                    f"{base}.gold_ranks[{title!r}] {gr} is out of range "
                    f"[1, {top_k_max}]"
                )

        for k in VALID_KS:
            key = f"any_evidence_recall@{k}"
            if key not in metrics:
                fail(f"missing {base}.metrics.{key}")
            if not isinstance(metrics[key], bool):
                fail(f"{base}.metrics.{key} must be a boolean")

        # Any Evidence Recall is monotone non-decreasing in k (a larger cutoff
        # can only add hits), so the three booleans must be non-decreasing and
        # `missed_ks` a prefix of VALID_KS. A non-monotone sequence (e.g.
        # False, True, False) is a structural inconsistency in the precomputed
        # metrics -- reject it rather than silently emit an illegal failure
        # shape like [2, 10]. This checks the stored booleans only; it does not
        # recompute any metric from ranks or titles.
        recalls = [metrics[f"any_evidence_recall@{k}"] for k in VALID_KS]
        for i in range(len(recalls) - 1):
            if recalls[i] and not recalls[i + 1]:
                fail(
                    f"{base}.metrics: any_evidence_recall is not monotone in k "
                    f"(@{VALID_KS[i]}={recalls[i]} but @{VALID_KS[i + 1]}="
                    f"{recalls[i + 1]}); it must be non-decreasing"
                )

    _require_finite(record, "record", fail)


def load_details(details_path, config):
    """Read details.jsonl line by line, validating each non-empty line. Blank
    lines are skipped. Returns the list of validated records."""
    retriever_keys = set(config["retrievers"])
    top_k_max = config["top_k_max"]
    seen_ids = set()
    records = []
    with open(details_path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(f"details.jsonl line {line_no}: invalid JSON: {e}")
            validate_record(record, line_no, retriever_keys, top_k_max, seen_ids)
            seen_ids.add(record["example_id"])
            records.append(record)
    return records


# --------------------------------------------------------------------------- #
# Failure-unit model (reshaping, not metric computation)
# --------------------------------------------------------------------------- #

def compute_missed_ks(metrics):
    """The cutoffs at which this retriever failed the any-evidence check.

    A retriever "misses" at k when any_evidence_recall@k is False. Because that
    metric is monotonic non-decreasing in k, missed_ks is always a prefix
    ([2], [2,5], or [2,5,10]); export_k = min(missed_ks) follows the upstream
    spec's "smallest missed k" rule verbatim."""
    return [k for k in VALID_KS if metrics[f"any_evidence_recall@{k}"] is False]


def build_gold_display(gold_titles, gold_ranks):
    """Per-gold cutoff status derived from THAT gold's own rank -- never from
    the global any-evidence metric (design section 5.3).

    hit@k  <=>  rank is not None and rank <= k

    This is a display regrouping of the evaluator's precomputed gold_ranks, not
    a recomputed metric."""
    display = {}
    for title in gold_titles:
        rank = gold_ranks[title]
        display[title] = {
            "rank": rank,
            "hits": {str(k): (rank is not None and rank <= k) for k in VALID_KS},
        }
    return display


def augment_retrievers(record):
    """Return a copy of the record's retrievers map with a `gold_display` block
    added to each retriever, so every side-by-side column can render per-gold
    status without the JS reaching back into the global metric."""
    augmented = {}
    gold_titles = record["gold_titles"]
    for name, sub in record["retrievers"].items():
        new_sub = dict(sub)
        new_sub["gold_display"] = build_gold_display(gold_titles, sub["gold_ranks"])
        augmented[name] = new_sub
    return augmented


def worst_gold_rank(card_retriever_sub, gold_titles, top_k_max):
    """Worst (largest) gold rank for the card's retriever, plus a finite sort
    key. If any gold is unranked (null), the worst rank is null and the sort
    key is top_k_max + 1 -- a sentinel guaranteed (by the gold-rank upper-bound
    validation) not to collide with any real rank. No math.inf / NaN ever
    enters the payload (design section 3.5)."""
    ranks = [card_retriever_sub["gold_ranks"][t] for t in gold_titles]
    if any(r is None for r in ranks):
        return None, top_k_max + 1
    worst = max(ranks)
    return worst, worst


def build_failure_units(records, config, retriever=None, k=None):
    """Build the sorted list of failure-unit payloads.

    One unit per (example_id, retriever) whose missed_ks is non-empty. Optional
    `retriever` / `k` narrow generation (intersection when both are given);
    `k` filters by `k in missed_ks`, not by export_k. Each unit still carries
    every retriever's data for side-by-side comparison; card_retriever only
    decides which retriever the annotation belongs to."""
    retriever_keys = set(config["retrievers"])
    if retriever is not None and retriever not in retriever_keys:
        raise ValueError(
            f"retriever {retriever!r} not in run; available: {sorted(retriever_keys)}"
        )
    if k is not None and k not in VALID_KS:
        raise ValueError(f"k must be one of {list(VALID_KS)}, got {k!r}")

    top_k_max = config["top_k_max"]
    units = []
    for record in records:
        augmented = augment_retrievers(record)
        for name in sorted(record["retrievers"]):
            if retriever is not None and name != retriever:
                continue
            metrics = record["retrievers"][name]["metrics"]
            missed = compute_missed_ks(metrics)
            if not missed:
                continue
            if k is not None and k not in missed:
                continue
            worst, worst_sort = worst_gold_rank(
                record["retrievers"][name], record["gold_titles"], top_k_max
            )
            units.append(
                {
                    "example_id": record["example_id"],
                    "question": record["question"],
                    "question_type": record["question_type"],
                    "gold_titles": list(record["gold_titles"]),
                    "card_retriever": name,
                    "missed_ks": list(missed),
                    "export_k": min(missed),
                    "worst_gold_rank": worst,
                    "worst_gold_rank_sort": worst_sort,
                    "retrievers": augmented,
                }
            )

    # Default order: most severe first (worst gold rank descending), then
    # deterministic tie-breakers.
    units.sort(
        key=lambda u: (-u["worst_gold_rank_sort"], u["example_id"], u["card_retriever"])
    )
    return units


def build_payload(config, records, retriever=None, k=None):
    """Assemble the {config, report_filter, failure_units} payload embedded in
    the HTML."""
    units = build_failure_units(records, config, retriever=retriever, k=k)
    return {
        "config": config,
        "report_filter": {
            "retriever": retriever,
            "k": k,
            "valid_ks": list(VALID_KS),
        },
        "failure_units": units,
    }


# --------------------------------------------------------------------------- #
# HTML-safe serialization + rendering
# --------------------------------------------------------------------------- #

def html_safe_json(obj):
    """Serialize to JSON that is safe to embed inside a <script> element.

    `allow_nan=False` guarantees standard JSON (no NaN/Infinity tokens).
    Escaping `<`, `>`, `&`, U+2028 and U+2029 guarantees the embedded payload
    can never contain a raw `</script>` or a line separator the HTML/JS parser
    would misread (design section 4.2)."""
    text = json.dumps(obj, ensure_ascii=False, allow_nan=False)
    return (
        text.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_report(payload):
    """Substitute the HTML-safe payload into the single template placeholder."""
    safe_json = html_safe_json(payload)
    occurrences = HTML_TEMPLATE.count(DATA_PLACEHOLDER)
    if occurrences != 1:
        raise ValueError(
            f"HTML template must contain exactly one {DATA_PLACEHOLDER} "
            f"placeholder, found {occurrences}"
        )
    return HTML_TEMPLATE.replace(DATA_PLACEHOLDER, safe_json, 1)


# --------------------------------------------------------------------------- #
# Top-level generation
# --------------------------------------------------------------------------- #

def _is_input_alias(out_path, input_paths):
    """True if `out_path` refers to (any alias of) one of the input files.

    Comparing os.path.abspath() strings is not enough: on a case-insensitive
    filesystem (Windows, default macOS) `.../DETAILS.JSONL` and
    `.../details.jsonl` name the SAME file, so a case-only --out alias could
    silently overwrite an already-read input. We therefore compare
    case-normalized real paths (resolving symlinks and case), and, when the
    target already exists, additionally use os.path.samefile() to catch
    hardlinks and 8.3 short-name aliases that string comparison would miss."""
    out_real = os.path.normcase(os.path.realpath(out_path))
    out_exists = os.path.exists(out_path)
    for input_path in input_paths:
        if out_real == os.path.normcase(os.path.realpath(input_path)):
            return True
        if out_exists and os.path.exists(input_path):
            try:
                if os.path.samefile(out_path, input_path):
                    return True
            except OSError:
                pass
    return False


def generate_report(run_id, retriever=None, k=None, runs_root="results/runs", out=None):
    """Full pipeline: validate paths, load + validate config/details, build the
    payload, render, and write the HTML. Returns the output path."""
    validate_run_id_arg(run_id)

    run_dir = os.path.join(runs_root, run_id)
    config_path = os.path.join(run_dir, "config.json")
    details_path = os.path.join(run_dir, "details.jsonl")

    if not os.path.isdir(run_dir):
        raise FileNotFoundError(f"run directory not found: {run_dir}")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"config.json not found: {config_path}")
    if not os.path.isfile(details_path):
        raise FileNotFoundError(f"details.jsonl not found: {details_path}")

    config = load_config(config_path, run_id)
    records = load_details(details_path, config)

    if retriever is not None and retriever not in config["retrievers"]:
        raise ValueError(
            f"retriever {retriever!r} not in run; available: "
            f"{sorted(config['retrievers'])}"
        )

    payload = build_payload(config, records, retriever=retriever, k=k)
    html = render_report(payload)

    out_path = out if out is not None else os.path.join(run_dir, "failures_review.html")
    if os.path.isdir(out_path):
        raise ValueError(f"--out is an existing directory: {out_path}")
    if _is_input_alias(out_path, (details_path, config_path)):
        raise ValueError(f"--out would overwrite an input file: {out_path}")

    parent = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Render a self-contained failures_review.html from a "
        "failure-review run directory (details.jsonl + config.json)."
    )
    parser.add_argument(
        "--run",
        dest="run_id",
        required=True,
        help="Run directory name under --runs-root (e.g. 2026-07-17_a)",
    )
    parser.add_argument(
        "--retriever",
        default=None,
        help="Only generate cards for this retriever (default: all retrievers)",
    )
    parser.add_argument(
        "--k",
        type=int,
        choices=list(VALID_KS),
        default=None,
        help="Only cards that miss at this cutoff (k in missed_ks); "
        "default: no narrowing",
    )
    parser.add_argument(
        "--runs-root",
        default="results/runs",
        help="Root directory that run directories live under",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: <runs-root>/<run_id>/failures_review.html)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    out_path = generate_report(
        run_id=args.run_id,
        retriever=args.retriever,
        k=args.k,
        runs_root=args.runs_root,
        out=args.out,
    )
    print(f"Wrote failure report to {out_path}")
    return out_path


# --------------------------------------------------------------------------- #
# Self-contained HTML template. Exactly one /*DATA*/ placeholder (inside the
# report-data <script>). All display/filtering/annotation/CSV logic is here;
# no metric or taxonomy computation lives in JS.
# --------------------------------------------------------------------------- #

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Failure Review</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    margin: 0; line-height: 1.4; color: #1a1a1a; background: #f5f5f5;
  }
  header, .toolbar { position: sticky; z-index: 10; background: #fff;
    border-bottom: 1px solid #ddd; padding: 8px 14px; }
  header { top: 0; }
  .toolbar { top: 0; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
  header h1 { font-size: 16px; margin: 0 0 4px; }
  .meta { font-size: 12px; color: #444; }
  .meta code { background: #eee; padding: 1px 4px; border-radius: 3px; }
  .retrievers-meta { font-size: 12px; color: #444; margin-top: 3px; }
  .annotator-row { margin-top: 6px; font-size: 13px; }
  .annotator-row input { font-size: 13px; padding: 2px 6px; }
  .toolbar label { font-size: 13px; }
  .toolbar select, .toolbar button { font-size: 13px; padding: 3px 6px; }
  .counts { margin-left: auto; font-size: 13px; font-weight: 600; }
  #banner { background: #ffe8e0; color: #7a2500; border: 1px solid #e0a58f;
    padding: 8px 14px; font-size: 13px; display: none; white-space: pre-wrap; }
  #banner.show { display: block; }
  #status { padding: 6px 14px; font-size: 13px; color: #333; white-space: pre-wrap; }
  main { padding: 14px; display: flex; flex-direction: column; gap: 14px; }
  .card { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 12px; }
  .card-head { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: baseline; }
  .card-for { font-weight: 700; }
  .missed { color: #b00020; font-weight: 600; font-size: 13px; }
  .qtype { font-size: 12px; color: #555; }
  .eid { font-size: 12px; color: #888; }
  .question { margin: 8px 0; font-size: 15px; }
  .gold-summary { font-size: 13px; margin: 6px 0; }
  .gold-summary .hit { color: #0a7d29; }
  .gold-summary .miss { color: #b00020; }
  .cols { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; }
  .col { flex: 1 1 320px; min-width: 280px; border: 1px solid #e2e2e2;
    border-radius: 5px; padding: 8px; background: #fafafa; }
  .col h3 { font-size: 13px; margin: 0 0 4px; }
  .col .flags { font-size: 12px; margin-bottom: 6px; }
  .flag { display: inline-block; margin-right: 8px; }
  .flag .ok { color: #0a7d29; } .flag .no { color: #b00020; }
  .row { border-top: 1px solid #eee; padding: 4px 0; font-size: 13px; }
  .row.gold { background: #fff6d6; }
  .row .rank { color: #666; }
  .row .score { color: #888; font-size: 12px; }
  .row .title { font-weight: 600; }
  .row .text { display: none; margin-top: 3px; font-size: 12px; color: #333;
    white-space: pre-wrap; }
  .row .text.show { display: block; }
  .row .toggle { cursor: pointer; color: #0645ad; font-size: 12px; }
  .ann { margin-top: 10px; display: flex; flex-direction: column; gap: 6px; }
  .ann input, .ann textarea { font-size: 13px; padding: 4px 6px; width: 100%; }
  .ann textarea { min-height: 52px; resize: vertical; }
  .ann label { font-size: 12px; font-weight: 600; }
  .empty-msg { font-size: 15px; color: #555; padding: 20px; text-align: center; }
</style>
</head>
<body>
<div id="banner"></div>
<header>
  <h1>Failure Review</h1>
  <div class="meta" id="run-meta"></div>
  <div class="retrievers-meta" id="retrievers-meta"></div>
  <div class="annotator-row">
    <label>Annotator: <input type="text" id="annotator" autocomplete="off"></label>
  </div>
</header>
<div class="toolbar">
  <label>retriever
    <select id="f-retriever"><option value="">All</option></select>
  </label>
  <label>k
    <select id="f-k">
      <option value="">All</option>
      <option value="2">2</option>
      <option value="5">5</option>
      <option value="10">10</option>
    </select>
  </label>
  <label>type
    <select id="f-type"><option value="">All</option></select>
  </label>
  <label><input type="checkbox" id="f-unann"> only unannotated</label>
  <label>sort
    <select id="f-sort">
      <option value="worst">worst gold rank</option>
      <option value="eid">example_id</option>
    </select>
  </label>
  <button id="btn-import" type="button">Import CSV</button>
  <input type="file" id="file-import" accept=".csv,text/csv" style="display:none">
  <button id="btn-export" type="button">Export CSV</button>
  <span class="counts" id="counts"></span>
</div>
<div id="status"></div>
<main id="cards"></main>
<datalist id="fr-labels"></datalist>

<script id="report-data" type="application/json">/*DATA*/</script>
<script>
(function () {
  "use strict";

  var REPORT = JSON.parse(document.getElementById("report-data").textContent);
  var CONFIG = REPORT.config || {};
  var RUN_ID = CONFIG.run_id;
  var UNITS = REPORT.failure_units || [];
  var VALID_KS = (REPORT.report_filter && REPORT.report_filter.valid_ks) || [2, 5, 10];
  var STORAGE_KEY = "fr::" + RUN_ID;
  var CSV_COLUMNS = ["run_id", "example_id", "retriever", "k",
                     "label", "notes", "annotator", "annotated_at"];
  var IDENTIFIER_RE = /^[A-Za-z0-9_][A-Za-z0-9._-]*$/;
  // CJK / East-Asian guard for the English-only annotation columns. Unicode
  // script properties (u flag) cover the scripted domain -- Han (incl.
  // supplementary-plane Han such as U+20000), Hiragana, Katakana, Hangul, and
  // Bopomofo (U+3105 etc.). The explicit ranges add the CJK-affiliated blocks
  // that Unicode assigns to script=Common/Inherited and the script properties
  // therefore do NOT catch: CJK radicals supplement / Kangxi radicals,
  // ideographic-description characters (U+2FF0), CJK symbols & punctuation, the
  // whole Hiragana + Katakana blocks U+3040-30FF -- which include the shared
  // Common/Inherited kana marks U+30FC (prolonged sound), U+3099/U+309A
  // (combining voiced/semi-voiced), U+309B/U+309C (spacing voiced/semi-voiced),
  // and U+30FB (katakana middle dot) that Script=Hiragana/Katakana omit -- CJK
  // strokes (U+31C0), enclosed CJK letters & months (U+3220), CJK compatibility,
  // CJK compatibility forms, and halfwidth/fullwidth forms (incl. the halfwidth
  // kana marks U+FF9E/U+FF9F and prolonged mark U+FF70). Latin (incl. accented)
  // and emoji are intentionally NOT in this class, so the guard is a CJK ban, not
  // an ASCII-only ban. One definition is reused on import and export.
  var CJK_RE = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}\p{Script=Bopomofo}\u2E80-\u2EFF\u2F00-\u2FDF\u2FF0-\u2FFF\u3000-\u303F\u3040-\u30FF\u31C0-\u31EF\u3200-\u32FF\u3300-\u33FF\uFE30-\uFE4F\uFF00-\uFFEF]/u;
  // One strict ISO-8601 validator shared by persisted load, CSV import, and CSV
  // export. ISO_RE fixes the supported syntactic forms (date + T + time, optional
  // fractional seconds, optional Z / +-HH:MM / +-HHMM offset) and captures the
  // components -- INCLUDING the optional offset hour/minute -- so isValidIso()
  // can range-check the real calendar+clock AND the offset, rejecting an
  // IMPOSSIBLE date or offset instead of letting it pass on syntax alone. JS
  // Date.parse used to turn 2025-02-29 into March 1, 2026-02-30 into March 2, and
  // 2026-04-31 into May 1, and never rejected impossible offsets like +05:60 or
  // +99:00. Real leap days (2024-02-29), offsets (+05:30 / +0530), Z, no offset,
  // and fractional seconds stay valid; no supported form is narrowed. Reused so a
  // false provenance timestamp cannot enter or leave the tracked CSV.
  var ISO_RE = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):?(\d{2}))?$/;

  function isValidIso(value) {
    if (typeof value !== "string") return false;
    var m = ISO_RE.exec(value);
    if (!m) return false;
    var year = +m[1], month = +m[2], day = +m[3];
    var hour = +m[4], minute = +m[5], second = +m[6];
    if (month < 1 || month > 12) return false;
    if (hour > 23 || minute > 59 || second > 59) return false;
    // Optional timezone offset (m[7]/m[8] are undefined for Z or no offset):
    // range-check the captured offset HH:MM exactly like the wall clock so an
    // impossible offset such as +05:60 or +99:00 is rejected instead of being
    // accepted on syntax alone -- nothing else validates the offset now that
    // Date.parse is gone. Legal +05:30 / +0530 stay valid.
    if (m[7] !== undefined && (+m[7] > 23 || +m[8] > 59)) return false;
    var mdays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    var leap = (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
    if (month === 2 && leap) mdays[1] = 29;
    return day >= 1 && day <= mdays[month - 1];
  }

  // -- element handles --
  var bannerEl = document.getElementById("banner");
  var statusEl = document.getElementById("status");
  var cardsEl = document.getElementById("cards");
  var datalistEl = document.getElementById("fr-labels");
  var annotatorEl = document.getElementById("annotator");
  var fRetriever = document.getElementById("f-retriever");
  var fK = document.getElementById("f-k");
  var fType = document.getElementById("f-type");
  var fUnann = document.getElementById("f-unann");
  var fSort = document.getElementById("f-sort");
  var btnImport = document.getElementById("btn-import");
  var btnExport = document.getElementById("btn-export");
  var fileImport = document.getElementById("file-import");
  var countsEl = document.getElementById("counts");

  function setStatus(msg) { statusEl.textContent = msg || ""; }
  function showBanner(msg) { bannerEl.textContent = msg; bannerEl.classList.add("show"); }

  function unitKey(u) { return u.example_id + "::" + u.card_retriever; }

  function isAnnotated(a) {
    if (!a) return false;
    var l = (a.label || "").trim();
    var n = (a.notes || "").trim();
    return l !== "" || n !== "";
  }

  // ---------------------------------------------------------------------- //
  // localStorage adapter with in-memory fallback (design section 6.4).
  // ---------------------------------------------------------------------- //
  var storage = (function () {
    var backend = null, degraded = false, mem = {};
    try {
      // A collision-resistant one-shot probe key, so capability probing never
      // reads, overwrites, or deletes a pre-existing unrelated key.
      var probe = "__fr_probe__" + Math.random().toString(36).slice(2)
        + "_" + Date.now();
      window.localStorage.setItem(probe, "1");
      window.localStorage.removeItem(probe);
      backend = window.localStorage;
    } catch (e) { backend = null; degraded = true; }
    return {
      degraded: function () { return degraded; },
      _fail: function () { degraded = true; backend = null; },
      getItem: function (k) {
        if (backend) { try { return backend.getItem(k); } catch (e) { this._fail(); } }
        return (k in mem) ? mem[k] : null;
      },
      setItem: function (k, v) {
        mem[k] = v;
        if (backend) { try { backend.setItem(k, v); return true; } catch (e) { this._fail(); return false; } }
        return false;
      },
      removeItem: function (k) {
        delete mem[k];
        // Report success/failure like setItem so persist() can warn if the
        // newest state could not be made persistent (design 6.4 / 10.2#7).
        if (backend) { try { backend.removeItem(k); return true; } catch (e) { this._fail(); return false; } }
        return false;
      }
    };
  })();

  function degradedWarn() {
    showBanner("Storage is unavailable, so annotations live only in memory: "
      + "refreshing or closing this tab will lose them. Export the CSV to save your work.");
  }
  if (storage.degraded()) { degradedWarn(); }

  // ---------------------------------------------------------------------- //
  // Annotation state: single aggregate map, persisted as one blob under one
  // key with one setItem (design section 6.1).
  // ---------------------------------------------------------------------- //
  var annotations = loadAnnotations();

  function validAnnotationKey(key) {
    // The persisted map key is the composite "<example_id>::<retriever>"
    // (design 6.1). Both halves must satisfy the identifier grammar (7.4);
    // because that grammar forbids ':', a well-formed key splits on "::" into
    // exactly two identifier parts. Anything else is a corrupt/legacy key.
    if (typeof key !== "string") return false;
    var parts = key.split("::");
    return parts.length === 2
      && IDENTIFIER_RE.test(parts[0]) && IDENTIFIER_RE.test(parts[1]);
  }

  function validAnnotationEntry(e) {
    // Type floor: an object (not an array) carrying the five persisted fields.
    if (!e || typeof e !== "object" || Array.isArray(e)) return false;
    if (typeof e.label !== "string" || typeof e.notes !== "string"
        || typeof e.annotator !== "string" || typeof e.annotated_at !== "string"
        || typeof e.k !== "number") return false;
    // Persisted k is export_k: an INTEGER in the fixed cutoff domain. A
    // fractional (2.5) or out-of-domain (999) k is a schema-incompatible blob,
    // not editable draft content -> isolate. (This checks a stored schema value;
    // it recomputes no metric.)
    if (!isFinite(e.k) || Math.floor(e.k) !== e.k || VALID_KS.indexOf(e.k) === -1)
      return false;
    // A persisted entry is always an annotated row (design 6.3: clearing both
    // label and notes deletes the entry), so an empty-content entry is corrupt.
    if (!isAnnotated(e)) return false;
    // Provenance the persistence/export contract requires (6.2 / 8.2): a
    // non-empty annotator and a valid ISO-8601 calendar timestamp (via the one
    // shared isValidIso, so an impossible date cannot load). CJK/formula content
    // is NOT checked here -- that is loadable editable draft state, an
    // export/import content guard, not storage corruption.
    if (e.annotator.trim() === "") return false;
    if (!isValidIso(e.annotated_at)) return false;
    return true;
  }

  function loadAnnotations() {
    var raw = storage.getItem(STORAGE_KEY);
    if (raw == null) return {};
    var isolate = function () {
      showBanner("Stored annotations for this run were unreadable or malformed and "
        + "have been ignored. Starting from an empty set; export to re-save.");
      return {};
    };
    try {
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)
          || parsed.schema !== 1
          || !parsed.annotations || typeof parsed.annotations !== "object"
          || Array.isArray(parsed.annotations)) {
        return isolate();
      }
      // Validate every key's grammar AND every entry's full semantics before
      // trusting the blob: composite-key syntax, integer k in the cutoff domain,
      // annotation predicate, non-empty annotator, and a parseable ISO time. A
      // single invalid key or entry isolates the WHOLE blob rather than emitting
      // an invalid tracked CSV or crashing later in isAnnotated()/rendering.
      var map = parsed.annotations;
      var keys = Object.keys(map);
      for (var i = 0; i < keys.length; i++) {
        if (!validAnnotationKey(keys[i]) || !validAnnotationEntry(map[keys[i]]))
          return isolate();
      }
      return map;
    } catch (e) {
      return isolate();
    }
  }

  function persist() {
    var keys = Object.keys(annotations);
    if (keys.length === 0) {
      // Clearing the last entry removes the run key. If the backend remove
      // fails (or storage already degraded), the newest in-memory map (now
      // empty) still stands, but persistence is NOT clean -- warn before
      // returning so a stale blob cannot silently reappear after a refresh.
      var removed = storage.removeItem(STORAGE_KEY);
      if (!removed || storage.degraded()) { degradedWarn(); }
      return;
    }
    var blob = JSON.stringify({ schema: 1, annotations: annotations });
    var ok = storage.setItem(STORAGE_KEY, blob);
    if (!ok || storage.degraded()) { degradedWarn(); }
  }

  // ---------------------------------------------------------------------- //
  // Rendering
  // ---------------------------------------------------------------------- //
  var cardRefs = [];  // { unit, el, key, labelInput, notesInput }

  function renderMeta() {
    var meta = document.getElementById("run-meta");
    meta.textContent = "";
    var parts = [
      ["run_id", CONFIG.run_id],
      ["corpus_setting", CONFIG.corpus_setting],
      ["n", CONFIG.n],
      ["split", CONFIG.split],
      ["timestamp", CONFIG.timestamp],
      ["script", CONFIG.script],
      ["git_commit", (CONFIG.git_commit == null ? "unknown" : CONFIG.git_commit)]
    ];
    parts.forEach(function (p, i) {
      if (p[1] === undefined || p[1] === null) {
        if (p[0] !== "git_commit") return;
      }
      if (i > 0 && meta.childNodes.length) meta.appendChild(document.createTextNode("  ·  "));
      var label = document.createTextNode(p[0] + ": ");
      var code = document.createElement("code");
      code.textContent = String(p[1]);
      meta.appendChild(label);
      meta.appendChild(code);
    });

    var rm = document.getElementById("retrievers-meta");
    rm.textContent = "";
    var retr = CONFIG.retrievers || {};
    var names = Object.keys(retr);
    rm.appendChild(document.createTextNode("retrievers: "));
    names.forEach(function (name, i) {
      if (i > 0) rm.appendChild(document.createTextNode("  |  "));
      var strong = document.createElement("strong");
      strong.textContent = name;
      rm.appendChild(strong);
      rm.appendChild(document.createTextNode(":" + String(retr[name])));
    });
  }

  function populateFilters() {
    // retriever options come from the card_retrievers actually present.
    // Null-prototype string sets: a legal free-text/identifier token such as
    // "__proto__" must be a normal key, not the object's prototype slot, and no
    // inherited name (toString, ...) may test truthy as spurious membership.
    var retrSet = Object.create(null), typeSet = Object.create(null);
    UNITS.forEach(function (u) {
      retrSet[u.card_retriever] = true;
      typeSet[u.question_type] = true;
    });
    Object.keys(retrSet).sort().forEach(function (r) {
      var o = document.createElement("option"); o.value = r; o.textContent = r;
      fRetriever.appendChild(o);
    });
    Object.keys(typeSet).sort().forEach(function (t) {
      var o = document.createElement("option"); o.value = t; o.textContent = t;
      fType.appendChild(o);
    });
  }

  function flagsLine(sub) {
    var wrap = document.createElement("div");
    wrap.className = "flags";
    VALID_KS.forEach(function (k) {
      var span = document.createElement("span");
      span.className = "flag";
      var hit = sub.metrics["any_evidence_recall@" + k] === true;
      span.appendChild(document.createTextNode("@" + k + " "));
      var mark = document.createElement("span");
      mark.className = hit ? "ok" : "no";
      mark.textContent = hit ? "✓" : "✗";
      span.appendChild(mark);
      wrap.appendChild(span);
    });
    return wrap;
  }

  function goldStatusText(disp, topKMax) {
    // Per-gold cutoff status read only from gold_display (design section 5.3).
    var out = [];
    if (disp.rank === null) {
      out.push("not in top-" + topKMax);
    } else {
      out.push("rank " + disp.rank);
    }
    var misses = [], hits = [];
    VALID_KS.forEach(function (k) {
      if (disp.hits[String(k)]) hits.push("@" + k); else misses.push("@" + k);
    });
    var frag = document.createElement("span");
    frag.appendChild(document.createTextNode(out.join("") ));
    if (misses.length) {
      frag.appendChild(document.createTextNode(" · "));
      var m = document.createElement("span"); m.className = "miss";
      m.textContent = "miss" + misses.join("/");
      frag.appendChild(m);
    }
    if (hits.length) {
      frag.appendChild(document.createTextNode(" · "));
      var h = document.createElement("span"); h.className = "hit";
      h.textContent = "hit" + hits.join("/");
      frag.appendChild(h);
    }
    return frag;
  }

  function renderColumn(name, sub, goldTitles, topKMax) {
    var col = document.createElement("div");
    col.className = "col";
    var h = document.createElement("h3");
    h.textContent = name;
    col.appendChild(h);
    col.appendChild(flagsLine(sub));

    var goldSet = Object.create(null);  // null-proto: a gold title may be "__proto__"
    goldTitles.forEach(function (t) { goldSet[t] = true; });

    sub.top_k.forEach(function (item) {
      var row = document.createElement("div");
      row.className = "row" + (goldSet[item.title] ? " gold" : "");
      var head = document.createElement("div");
      var rank = document.createElement("span");
      rank.className = "rank"; rank.textContent = "#" + item.rank + " ";
      var title = document.createElement("span");
      title.className = "title"; title.textContent = item.title;
      var score = document.createElement("span");
      score.className = "score"; score.textContent = "  (" + item.score.toFixed(4) + ")";
      head.appendChild(rank); head.appendChild(title); head.appendChild(score);
      if (item.text) {
        var toggle = document.createElement("span");
        toggle.className = "toggle"; toggle.textContent = "  [text]";
        var textDiv = document.createElement("div");
        textDiv.className = "text"; textDiv.textContent = item.text;
        toggle.addEventListener("click", function () { textDiv.classList.toggle("show"); });
        head.appendChild(toggle);
        row.appendChild(head);
        row.appendChild(textDiv);
      } else {
        row.appendChild(head);
      }
      col.appendChild(row);
    });
    return col;
  }

  function renderCard(unit) {
    var card = document.createElement("div");
    card.className = "card";
    card.setAttribute("data-key", unitKey(unit));
    var topKMax = CONFIG.top_k_max;

    var head = document.createElement("div");
    head.className = "card-head";
    var cardFor = document.createElement("span");
    cardFor.className = "card-for";
    cardFor.textContent = "card for: " + unit.card_retriever;
    var missed = document.createElement("span");
    missed.className = "missed";
    missed.textContent = "misses " + unit.missed_ks.map(function (k) { return "@" + k; }).join(", ");
    var qtype = document.createElement("span");
    qtype.className = "qtype"; qtype.textContent = unit.question_type;
    var eid = document.createElement("span");
    eid.className = "eid"; eid.textContent = unit.example_id;
    head.appendChild(cardFor); head.appendChild(missed);
    head.appendChild(qtype); head.appendChild(eid);
    card.appendChild(head);

    var q = document.createElement("div");
    q.className = "question"; q.textContent = unit.question;
    card.appendChild(q);

    // gold summary for the card's retriever, per-gold from gold_display.
    var cardSub = unit.retrievers[unit.card_retriever];
    var gs = document.createElement("div");
    gs.className = "gold-summary";
    gs.appendChild(document.createTextNode("gold: "));
    unit.gold_titles.forEach(function (t, i) {
      if (i > 0) gs.appendChild(document.createTextNode("; "));
      var name = document.createElement("span");
      name.textContent = t + " — ";
      gs.appendChild(name);
      gs.appendChild(goldStatusText(cardSub.gold_display[t], topKMax));
    });
    card.appendChild(gs);

    // side-by-side columns for every retriever present.
    var cols = document.createElement("div");
    cols.className = "cols";
    Object.keys(unit.retrievers).sort().forEach(function (name) {
      cols.appendChild(renderColumn(name, unit.retrievers[name], unit.gold_titles, topKMax));
    });
    card.appendChild(cols);

    // annotation inputs.
    var ann = document.createElement("div");
    ann.className = "ann";
    var labWrap = document.createElement("label");
    labWrap.textContent = "label";
    var labelInput = document.createElement("input");
    labelInput.type = "text"; labelInput.setAttribute("list", "fr-labels");
    labelInput.autocomplete = "off";
    var noteWrap = document.createElement("label");
    noteWrap.textContent = "notes";
    var notesInput = document.createElement("textarea");

    var key = unitKey(unit);
    var existing = annotations[key];
    if (existing) {
      labelInput.value = existing.label || "";
      notesInput.value = existing.notes || "";
    }

    function onEdit() { handleEdit(unit, labelInput, notesInput); }
    labelInput.addEventListener("input", onEdit);
    notesInput.addEventListener("input", onEdit);

    ann.appendChild(labWrap); ann.appendChild(labelInput);
    ann.appendChild(noteWrap); ann.appendChild(notesInput);
    card.appendChild(ann);

    cardRefs.push({ unit: unit, el: card, key: key,
                    labelInput: labelInput, notesInput: notesInput });
    return card;
  }

  function handleEdit(unit, labelInput, notesInput) {
    var key = unitKey(unit);
    var labelVal = labelInput.value;
    var notesVal = notesInput.value;
    var willAnnotate = (labelVal.trim() !== "" || notesVal.trim() !== "");
    var existing = annotations[key];

    if (!willAnnotate) {
      // Cleared: drop only this entry, then rewrite the whole blob.
      if (existing) { delete annotations[key]; persist(); }
      afterStateChange();
      return;
    }

    var annotator = annotatorEl.value.trim();
    if (annotator === "") {
      setStatus("Enter an annotator name (top of page) before annotating "
        + unit.example_id + " / " + unit.card_retriever + ".");
      return;  // forbid create/modify without an annotator; state unchanged.
    }
    setStatus("");

    var now = new Date().toISOString();
    if (!existing) {
      annotations[key] = {
        k: unit.export_k, label: labelVal, notes: notesVal,
        annotator: annotator, annotated_at: now
      };
    } else {
      var changed = (existing.label !== labelVal) || (existing.notes !== notesVal);
      existing.label = labelVal;
      existing.notes = notesVal;
      existing.k = unit.export_k;
      if (changed) { existing.annotator = annotator; existing.annotated_at = now; }
    }
    persist();
    afterStateChange();
  }

  function afterStateChange() {
    rebuildDatalist();
    updateCounts();
    applyFilter();
  }

  // ---------------------------------------------------------------------- //
  // Datalist of previously used labels (design section 5.6).
  // ---------------------------------------------------------------------- //
  function rebuildDatalist() {
    // Suggestions come only from annotated cards IN THE CURRENT REPORT, not the
    // whole shared-run blob -- a narrowed report must not leak labels for
    // out-of-scope (example_id, retriever) keys that share the run's storage.
    var seen = Object.create(null);  // null-proto: keep a legal "__proto__" label
    cardRefs.forEach(function (ref) {
      var a = annotations[ref.key];
      if (isAnnotated(a) && a.label && a.label.trim() !== "") seen[a.label] = true;
    });
    var labels = Object.keys(seen).sort();
    datalistEl.textContent = "";
    labels.forEach(function (lab) {
      var opt = document.createElement("option");
      opt.value = lab;
      datalistEl.appendChild(opt);
    });
  }

  // ---------------------------------------------------------------------- //
  // Filtering, sorting, counts (design section 5.4).
  // ---------------------------------------------------------------------- //
  function applyFilter() {
    var r = fRetriever.value, k = fK.value, t = fType.value, unann = fUnann.checked;
    cardRefs.forEach(function (ref) {
      var u = ref.unit;
      var show = true;
      if (r && u.card_retriever !== r) show = false;
      if (show && k && u.missed_ks.indexOf(parseInt(k, 10)) === -1) show = false;
      if (show && t && u.question_type !== t) show = false;
      if (show && unann && isAnnotated(annotations[ref.key])) show = false;
      ref.el.style.display = show ? "" : "none";
    });
  }

  function applySort() {
    var mode = fSort.value;
    var order = cardRefs.slice();
    if (mode === "eid") {
      order.sort(function (a, b) {
        if (a.unit.example_id < b.unit.example_id) return -1;
        if (a.unit.example_id > b.unit.example_id) return 1;
        if (a.unit.card_retriever < b.unit.card_retriever) return -1;
        if (a.unit.card_retriever > b.unit.card_retriever) return 1;
        return 0;
      });
    } else {
      order.sort(function (a, b) {
        if (b.unit.worst_gold_rank_sort !== a.unit.worst_gold_rank_sort)
          return b.unit.worst_gold_rank_sort - a.unit.worst_gold_rank_sort;
        if (a.unit.example_id < b.unit.example_id) return -1;
        if (a.unit.example_id > b.unit.example_id) return 1;
        if (a.unit.card_retriever < b.unit.card_retriever) return -1;
        if (a.unit.card_retriever > b.unit.card_retriever) return 1;
        return 0;
      });
    }
    order.forEach(function (ref) { cardsEl.appendChild(ref.el); });
  }

  function updateCounts() {
    var total = cardRefs.length;
    var done = 0;
    cardRefs.forEach(function (ref) {
      if (isAnnotated(annotations[ref.key])) done += 1;
    });
    countsEl.textContent = "annotated " + done + " / total " + total;
  }

  // ---------------------------------------------------------------------- //
  // CSV export (design section 7).
  // ---------------------------------------------------------------------- //
  function csvField(value) {
    var s = (value == null) ? "" : String(value);
    if (/[",\r\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
    return s;
  }

  function firstNonSpaceIsFormula(s) {
    var t = String(s == null ? "" : s).replace(/^\s+/, "");
    return t.length > 0 && "=+-@".indexOf(t.charAt(0)) !== -1;
  }

  function exportCsv() {
    var rows = [];
    var badCjk = [], badFormula = [], badId = [], badK = [], badProv = [];
    cardRefs.forEach(function (ref) {
      var u = ref.unit;
      var a = annotations[ref.key];
      if (!isAnnotated(a)) return;

      if (a.k !== u.export_k) badK.push(ref.key);
      // Defensive provenance guard: the strengthened loader already isolates
      // any storage blob with empty/invalid provenance, but re-check at the
      // write boundary (same strict isValidIso) so a storage-derived row can
      // never emit a false or impossible-date timestamp into the tracked CSV.
      if (String(a.annotator || "").trim() === ""
          || !isValidIso(String(a.annotated_at || ""))) {
        badProv.push(u.example_id + "/" + u.card_retriever);
      }
      [["run_id", RUN_ID], ["example_id", u.example_id], ["retriever", u.card_retriever]]
        .forEach(function (p) { if (!IDENTIFIER_RE.test(p[1])) badId.push(u.example_id + " (" + p[0] + ")"); });
      [["label", a.label], ["notes", a.notes], ["annotator", a.annotator]].forEach(function (p) {
        if (CJK_RE.test(String(p[1] || ""))) badCjk.push(u.example_id + "/" + u.card_retriever + "/" + p[0]);
        if (firstNonSpaceIsFormula(p[1])) badFormula.push(u.example_id + "/" + u.card_retriever + "/" + p[0]);
      });

      rows.push([RUN_ID, u.example_id, u.card_retriever, u.export_k,
                 a.label, a.notes, a.annotator, a.annotated_at]);
    });

    var errs = [];
    if (badK.length) errs.push("k mismatch vs export_k: " + badK.join(", "));
    if (badProv.length) errs.push("missing/invalid provenance (annotator/annotated_at): " + badProv.join(", "));
    if (badId.length) errs.push("invalid identifier: " + badId.join(", "));
    if (badCjk.length) errs.push("CJK / non-English in: " + badCjk.join(", "));
    if (badFormula.length) errs.push("formula-injection start (= + - @) in: " + badFormula.join(", "));
    if (errs.length) {
      setStatus("Export blocked. Fix these before exporting:\n- " + errs.join("\n- "));
      return;
    }
    if (rows.length === 0) { setStatus("Nothing to export: no annotated failures."); return; }

    var lines = [CSV_COLUMNS.join(",")];
    rows.forEach(function (r) { lines.push(r.map(csvField).join(",")); });
    var text = lines.join("\r\n") + "\r\n";  // CRLF is RFC-4180 friendly; no BOM.

    var blob = new Blob([text], { type: "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = "annotations.csv";
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 0);
    setStatus("Exported " + rows.length + " annotation(s).");
  }

  // ---------------------------------------------------------------------- //
  // CSV import (design section 8): quote-aware parse, strict-scope validate,
  // transactional single-setItem merge.
  // ---------------------------------------------------------------------- //
  function parseCsv(text) {
    if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);  // optional BOM
    var rows = [], row = [], field = "", i = 0, inQuotes = false, n = text.length;
    while (i < n) {
      var c = text.charAt(i);
      if (inQuotes) {
        if (c === '"') {
          if (text.charAt(i + 1) === '"') { field += '"'; i += 2; continue; }
          inQuotes = false; i += 1; continue;
        }
        field += c; i += 1; continue;
      }
      if (c === '"') { inQuotes = true; i += 1; continue; }
      if (c === ",") { row.push(field); field = ""; i += 1; continue; }
      if (c === "\r") {
        if (text.charAt(i + 1) === "\n") i += 1;
        row.push(field); field = ""; rows.push(row); row = []; i += 1; continue;
      }
      if (c === "\n") { row.push(field); field = ""; rows.push(row); row = []; i += 1; continue; }
      field += c; i += 1;
    }
    if (inQuotes) throw new Error("unterminated quoted field");
    row.push(field); rows.push(row);
    // Drop a single trailing empty row caused by a final newline.
    if (rows.length && rows[rows.length - 1].length === 1 && rows[rows.length - 1][0] === "") {
      rows.pop();
    }
    return rows;
  }

  function unitByKeyMap() {
    var m = {};
    UNITS.forEach(function (u) { m[unitKey(u)] = u; });
    return m;
  }

  function handleImportText(text) {
    var rows;
    try { rows = parseCsv(text); }
    catch (e) { setStatus("Import failed: " + e.message); return; }
    if (rows.length === 0) { setStatus("Import failed: file is empty."); return; }

    var header = rows[0];
    var headerErrs = validateHeader(header);
    if (headerErrs) { setStatus("Import failed: " + headerErrs); return; }
    var colIndex = {};
    header.forEach(function (name, idx) { colIndex[name] = idx; });

    var units = unitByKeyMap();
    var parsed = [], errs = [], seenKeys = {};
    for (var r = 1; r < rows.length; r++) {
      var row = rows[r];
      var lineNo = r + 1;
      if (row.length !== CSV_COLUMNS.length) {
        errs.push("line " + lineNo + ": expected " + CSV_COLUMNS.length
          + " fields, got " + row.length);
        continue;
      }
      var get = function (name) { return row[colIndex[name]]; };
      var runId = get("run_id"), exId = get("example_id"), retr = get("retriever");
      var kRaw = get("k"), label = get("label"), notes = get("notes");
      var annotator = get("annotator"), annotatedAt = get("annotated_at");

      var rowErr = validateImportRow(runId, exId, retr, kRaw, label, notes,
                                     annotator, annotatedAt, units, lineNo);
      if (rowErr) { errs.push(rowErr); continue; }

      var key = exId + "::" + retr;
      if (seenKeys[key]) { errs.push("line " + lineNo + ": duplicate key " + key); continue; }
      seenKeys[key] = true;

      parsed.push({
        key: key,
        value: { k: parseInt(kRaw, 10), label: label, notes: notes,
                 annotator: annotator, annotated_at: annotatedAt }
      });
    }

    if (errs.length) {
      setStatus("Import rejected (no changes made):\n- " + errs.join("\n- "));
      return;
    }

    var newCount = 0, overrideCount = 0;
    parsed.forEach(function (p) {
      if (Object.prototype.hasOwnProperty.call(annotations, p.key)) overrideCount += 1;
      else newCount += 1;
    });

    var msg = "Import " + parsed.length + " annotation(s): " + newCount + " new, "
      + overrideCount + " override existing. Imported values overwrite existing "
      + "annotations with the same key. Continue?";
    if (!window.confirm(msg)) { setStatus("Import cancelled."); return; }

    // Merge in memory, then a single atomic write via persist().
    parsed.forEach(function (p) { annotations[p.key] = p.value; });
    persist();

    // Reflect imported values into any visible inputs.
    var byKey = {};
    cardRefs.forEach(function (ref) { byKey[ref.key] = ref; });
    parsed.forEach(function (p) {
      var ref = byKey[p.key];
      if (ref) { ref.labelInput.value = p.value.label; ref.notesInput.value = p.value.notes; }
    });

    rebuildDatalist();
    updateCounts();
    applyFilter();
    setStatus("Imported " + parsed.length + " annotation(s) ("
      + newCount + " new, " + overrideCount + " overwritten).");
  }

  function validateHeader(header) {
    var seen = {};
    for (var i = 0; i < header.length; i++) {
      var name = header[i];
      if (seen[name]) return "duplicate column " + name;
      seen[name] = true;
    }
    var want = CSV_COLUMNS.slice().sort().join(",");
    var got = header.slice().sort().join(",");
    if (want !== got) {
      return "columns must be exactly [" + CSV_COLUMNS.join(", ")
        + "] (order may vary), got [" + header.join(", ") + "]";
    }
    return null;
  }

  function validateImportRow(runId, exId, retr, kRaw, label, notes,
                             annotator, annotatedAt, units, lineNo) {
    if (runId !== RUN_ID)
      return "line " + lineNo + ": run_id " + runId + " != report run_id " + RUN_ID;
    if (!IDENTIFIER_RE.test(runId) || !IDENTIFIER_RE.test(exId) || !IDENTIFIER_RE.test(retr))
      return "line " + lineNo + ": run_id/example_id/retriever must match identifier syntax";
    var key = exId + "::" + retr;
    var unit = units[key];
    if (!unit)
      return "line " + lineNo + ": (" + exId + ", " + retr + ") is not in this report";
    if (!/^\d+$/.test(kRaw))
      return "line " + lineNo + ": k must be an integer";
    var k = parseInt(kRaw, 10);
    if (VALID_KS.indexOf(k) === -1)
      return "line " + lineNo + ": k " + k + " not in {2,5,10}";
    if (k !== unit.export_k)
      return "line " + lineNo + ": k " + k + " != export_k " + unit.export_k;

    var fields = [["label", label], ["notes", notes], ["annotator", annotator]];
    for (var i = 0; i < fields.length; i++) {
      if (CJK_RE.test(String(fields[i][1] || "")))
        return "line " + lineNo + ": CJK/non-English in " + fields[i][0];
      if (firstNonSpaceIsFormula(fields[i][1]))
        return "line " + lineNo + ": formula-injection start (= + - @) in " + fields[i][0];
    }

    var annotated = (String(label || "").trim() !== "" || String(notes || "").trim() !== "");
    if (!annotated)
      return "line " + lineNo + ": row has neither label nor notes (not annotated)";
    if (String(annotator || "").trim() === "")
      return "line " + lineNo + ": missing annotator (provenance required)";
    if (String(annotatedAt || "").trim() === "")
      return "line " + lineNo + ": missing annotated_at (provenance required)";
    if (!isValidIso(annotatedAt))
      return "line " + lineNo + ": annotated_at is not a valid ISO 8601 calendar date";
    return null;
  }

  // ---------------------------------------------------------------------- //
  // Wiring
  // ---------------------------------------------------------------------- //
  function renderEmpty() {
    var msg = document.createElement("div");
    msg.className = "empty-msg";
    msg.textContent = "No failures under the current report filter.";
    cardsEl.appendChild(msg);
    btnImport.disabled = true;
    btnExport.disabled = true;
    setStatus("This report contains no failure units, so import/export are disabled.");
  }

  function init() {
    renderMeta();
    if (UNITS.length === 0) {
      updateCounts();
      renderEmpty();
      return;
    }
    populateFilters();
    UNITS.forEach(function (u) { cardsEl.appendChild(renderCard(u)); });
    applySort();
    rebuildDatalist();
    updateCounts();
    applyFilter();

    fRetriever.addEventListener("change", applyFilter);
    fK.addEventListener("change", applyFilter);
    fType.addEventListener("change", applyFilter);
    fUnann.addEventListener("change", applyFilter);
    fSort.addEventListener("change", function () { applySort(); applyFilter(); });
    btnExport.addEventListener("click", exportCsv);
    btnImport.addEventListener("click", function () { fileImport.click(); });
    fileImport.addEventListener("change", function (e) {
      var file = e.target.files && e.target.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function () {
        try { handleImportText(String(reader.result)); }
        finally { fileImport.value = ""; }
      };
      reader.readAsText(file, "utf-8");
    });
  }

  init();
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
