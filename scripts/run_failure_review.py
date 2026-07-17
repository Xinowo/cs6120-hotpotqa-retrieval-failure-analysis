"""
run_failure_review.py  (the failure-review runner)

Produces the structured, per-run record that the failure-review pipeline
(docs/specs/2026-07-12-failure-review-pipeline-design.md) is built on. Unlike
`run_dense_experiment.py` -- which writes the finalized wide-table
`results/dense_results.csv` (one True/False row per example, for the formal
results) -- this runner writes a self-contained *run directory* rich enough
for manual failure debugging:

    results/runs/<run_id>/
        details.jsonl    one line per question: full top_k (rank/title/score/
                         text), gold_ranks, and per-retriever metrics
        metrics.json     each retriever's overall Any Evidence Recall@k
        config.json      run parameters + corpus_setting + git_commit

Design principle (spec section 3): **Python computes, the HTML only displays.**
Every evaluation quantity written here (recall@k, gold hit ranks) comes from
`src/evaluator.py`; this runner only *calls* those functions and moves their
output into JSON. It re-implements no metric -- that logic is a hand-written
core component and stays in evaluator.py.

Both corpus settings are wired: **per_question** builds one small
~10-paragraph corpus per question (each re-embedded), while **pooled** builds
ONE shared index over every question's paragraphs merged and deduplicated
(data_loader.build_pooled_corpus) and scores all questions against it in a
single batch -- so a gold can be outranked by OTHER questions' paragraphs, the
drift/distractor signal per_question can't expose. Only the `dense` retriever
is wired in for now; the `retrievers` object in details.jsonl is a dict
precisely so BM25 / rerank can be added later without a schema change.

Usage:
    python scripts/run_failure_review.py --n 10 --setting per_question
    python scripts/run_failure_review.py --n 500 --setting pooled
    python scripts/run_failure_review.py --n 100 --run-id 2026-07-16_a

The first real run downloads all-MiniLM-L6-v2 (~90MB) and HotpotQA, so it
needs network access once; both are cached locally afterward.
"""

import argparse
import json
import os
import string
import subprocess
import sys
from datetime import datetime

# Allow running directly from the project root without installing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import build_pooled_corpus, load_examples
from src.dense_retriever import DEFAULT_MODEL_NAME, DenseRetriever
from src.evaluator import aggregate_results, evaluate_example, gold_ranks

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Only the dense retriever is wired in for now (Xin's half). The key here is
# the name that appears under `retrievers.<name>` in details.jsonl.
RETRIEVER_NAME = "dense"

# How many ranked results to store per question. gold_ranks treats absence
# from this list as "not retrieved" (rank null), so this is the top_k_max
# horizon. Defaults differ by setting: a per-question corpus is only ~10
# paragraphs, so 10 captures it all; the pooled corpus is thousands of
# paragraphs, so 50 is the storage/candidate depth (also the reranker's
# candidate-set size). A gold ranked beyond the horizon still reads as null.
DEFAULT_TOP_K_MAX = 10
POOLED_TOP_K_MAX = 50
TOP_K_MAX_BY_SETTING = {"per_question": DEFAULT_TOP_K_MAX, "pooled": POOLED_TOP_K_MAX}

# The metric cutoffs written into every details record. These are fixed at
# {2, 5, 10} (not narrowed by setting) because the review HTML's filter rule
# is "misses at any k in {2, 5, 10}" -- the filter needs all three present.
METRIC_KS = [2, 5, 10]


def build_retriever_record(ranked, gold_titles, metric_ks=METRIC_KS):
    """Build one retriever's sub-record for a single question.

    `ranked` is the retriever's top results as (Paragraph, score) tuples,
    highest score first (exactly what DenseRetriever.retrieve returns).
    `gold_titles` is that question's gold evidence title set.

    Returns the dict stored under `retrievers.<name>` in details.jsonl:
    a `top_k` list (rank/title/score/text), the `gold_ranks` map, and the
    `metrics` dict. gold_ranks and metrics are computed by evaluator.py from
    the ranked titles; this function only reshapes the retriever output and
    forwards those calls -- it computes no metric itself.
    """
    top_k = [
        {
            "rank": i + 1,
            "title": paragraph.title,
            "score": float(score),
            "text": paragraph.text,
        }
        for i, (paragraph, score) in enumerate(ranked)
    ]
    retrieved_titles = [paragraph.title for paragraph, _ in ranked]

    return {
        "top_k": top_k,
        # gold_ranks is Xin's hand-written evaluator function; passed the full
        # ranked-title list, it returns each gold's 1-based rank or None.
        "gold_ranks": gold_ranks(retrieved_titles, gold_titles),
        "metrics": evaluate_example(retrieved_titles, gold_titles, k_values=metric_ks),
    }


def build_details_record(example, retriever_records):
    """Assemble one details.jsonl line for a question.

    `retriever_records` maps retriever name -> the dict from
    build_retriever_record. gold_titles is stored sorted for a stable,
    diff-friendly ordering.
    """
    return {
        "example_id": example.example_id,
        "question": example.question,
        "question_type": example.question_type,
        "gold_titles": sorted(example.gold_titles),
        "retrievers": retriever_records,
    }


def run_dense_per_question(examples, encoder=None, top_k_max=DEFAULT_TOP_K_MAX):
    """Per-question dense path: one DenseRetriever per example over that
    question's own ~10 paragraphs. Returns
    (details_records, per_example_metrics), where per_example_metrics is the
    list of metric dicts for the dense retriever (for aggregation).

    `encoder` is injected so all questions reuse one loaded model and so tests
    can pass a fake encoder and stay offline; with encoder=None each
    DenseRetriever lazily builds the real model on first use.
    """
    details_records = []
    per_example_metrics = []
    for ex in examples:
        retriever = DenseRetriever(ex.paragraphs, encoder=encoder)
        ranked = retriever.retrieve(ex.question, top_k=top_k_max)
        record = build_retriever_record(ranked, ex.gold_titles)
        details_records.append(build_details_record(ex, {RETRIEVER_NAME: record}))
        per_example_metrics.append(record["metrics"])
    return details_records, per_example_metrics


def run_dense_pooled(examples, pooled_paragraphs, encoder=None, top_k_max=POOLED_TOP_K_MAX):
    """Pooled dense path: ONE shared DenseRetriever over the whole
    deduplicated pooled corpus, with every question scored against it in a
    single batch (retrieve_many). Because the index holds every question's
    paragraphs, a gold can be outranked by OTHER questions' paragraphs -- the
    drift/distractor signal per_question can't show. Returns
    (details_records, per_example_metrics), same shape as run_dense_per_question.

    `pooled_paragraphs` is the shared corpus from build_pooled_corpus; `encoder`
    is injected so the one model load is reused and tests stay offline. Record
    and metric shaping is identical to the per_question path -- only the corpus
    and the batched retrieval differ.
    """
    retriever = DenseRetriever(pooled_paragraphs, encoder=encoder)
    batches = retriever.retrieve_many([ex.question for ex in examples], top_k=top_k_max)

    details_records = []
    per_example_metrics = []
    for ex, ranked in zip(examples, batches):
        record = build_retriever_record(ranked, ex.gold_titles)
        details_records.append(build_details_record(ex, {RETRIEVER_NAME: record}))
        per_example_metrics.append(record["metrics"])
    return details_records, per_example_metrics


def _warm_encoder(examples):
    """Build one DenseRetriever up front just to load the model once, then
    reuse its encoder across all questions. Returns None for an empty example
    set (nothing to warm)."""
    if not examples:
        return None
    warm = DenseRetriever(examples[0].paragraphs)
    return warm._encoder


def next_run_id(runs_dir, date_str):
    """Return the smallest unused run_id for `date_str` under `runs_dir`:
    `<date_str>_a`, then `_b`, ... skipping any that already exist so a rerun
    never overwrites an earlier run's directory (runs are immutable history).
    Raises if all 26 letters for the day are taken."""
    existing = set()
    if os.path.isdir(runs_dir):
        existing = {name for name in os.listdir(runs_dir) if name.startswith(date_str + "_")}
    for letter in string.ascii_lowercase:
        run_id = f"{date_str}_{letter}"
        if run_id not in existing:
            return run_id
    raise RuntimeError(f"All 26 run-id letters for {date_str} are used in {runs_dir}.")


def get_git_commit():
    """Return the current HEAD commit hash, or None if unavailable (e.g. git
    missing or not a repo) -- so results stay traceable to a code version
    without the runner ever failing on a non-git environment."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
    except (OSError, ValueError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def write_details_jsonl(path, details_records):
    """Write one JSON object per line. ensure_ascii=False keeps any non-ASCII
    paragraph text readable rather than \\uXXXX-escaped."""
    with open(path, "w", encoding="utf-8") as f:
        for record in details_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_json(path, obj):
    """Write a pretty-printed JSON file (config.json / metrics.json)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_run(run_dir, details_records, metrics_by_retriever, config):
    """Create the run directory and write its three files. Returns run_dir."""
    os.makedirs(run_dir, exist_ok=True)
    write_details_jsonl(os.path.join(run_dir, "details.jsonl"), details_records)
    write_json(os.path.join(run_dir, "metrics.json"), metrics_by_retriever)
    write_json(os.path.join(run_dir, "config.json"), config)
    return run_dir


def build_config(run_id, n, split, setting, top_k_max, timestamp, git_commit,
                 corpus_size=None):
    """Assemble config.json: run parameters plus the traceability fields the
    spec requires -- corpus_setting (per_question vs pooled failures are
    different in nature) and git_commit (which code version produced this).
    corpus_size records the shared pooled corpus's paragraph count (null for
    per_question, where each question has its own ~10-paragraph corpus)."""
    return {
        "run_id": run_id,
        "n": n,
        "split": split,
        "corpus_setting": setting,
        "corpus_size": corpus_size,
        "top_k_max": top_k_max,
        "retrievers": {RETRIEVER_NAME: DEFAULT_MODEL_NAME},
        "timestamp": timestamp,
        "script": "scripts/run_failure_review.py",
        "git_commit": git_commit,
    }


def main(n, split, setting, top_k_max, run_id, runs_root):
    if setting not in TOP_K_MAX_BY_SETTING:
        raise ValueError(f"Unknown setting: {setting!r}")

    # Default storage horizon depends on the setting (10 per_question, 50
    # pooled); an explicit --k overrides it.
    if top_k_max is None:
        top_k_max = TOP_K_MAX_BY_SETTING[setting]

    max_metric_k = max(METRIC_KS)
    if top_k_max < max_metric_k:
        raise ValueError(
            f"--k={top_k_max} is too small: metrics go up to @{max_metric_k}, "
            f"so at least {max_metric_k} results must be stored per question."
        )

    if run_id is None:
        run_id = next_run_id(runs_root, datetime.now().strftime("%Y-%m-%d"))
    run_dir = os.path.join(runs_root, run_id)

    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    print("Building dense encoder (first run downloads all-MiniLM-L6-v2)...")
    encoder = _warm_encoder(examples)

    corpus_size = None
    if setting == "per_question":
        details_records, per_example_metrics = run_dense_per_question(
            examples, encoder=encoder, top_k_max=top_k_max
        )
    else:  # pooled: one shared index over every question's paragraphs
        pooled_paragraphs, collision_titles = build_pooled_corpus(examples)
        corpus_size = len(pooled_paragraphs)
        print(
            f"Pooled corpus: {corpus_size} paragraphs "
            f"({len(collision_titles)} title collisions).\n"
        )
        details_records, per_example_metrics = run_dense_pooled(
            examples, pooled_paragraphs, encoder=encoder, top_k_max=top_k_max
        )

    metrics_by_retriever = {RETRIEVER_NAME: aggregate_results(per_example_metrics)}
    config = build_config(
        run_id=run_id,
        n=len(examples),
        split=split,
        setting=setting,
        top_k_max=top_k_max,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        git_commit=get_git_commit(),
        corpus_size=corpus_size,
    )

    write_run(run_dir, details_records, metrics_by_retriever, config)
    print(f"Wrote run '{run_id}' to {run_dir}")
    print(f"  details.jsonl : {len(details_records)} lines")
    print(f"  metrics.json  : {RETRIEVER_NAME}")
    print(f"  config.json   : corpus_setting={setting}, git_commit={config['git_commit']}\n")

    print(f"Overall {RETRIEVER_NAME.upper()} retrieval metrics "
          f"({setting}, n={len(examples)}):")
    for metric, value in metrics_by_retriever[RETRIEVER_NAME].items():
        print(f"  {metric}: {value:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Failure-review runner: HotpotQA -> dense retrieval -> "
        "structured per-run directory (details.jsonl / metrics.json / config.json)."
    )
    parser.add_argument("--n", type=int, default=100, help="Number of examples to load")
    parser.add_argument(
        "--setting",
        type=str,
        default="per_question",
        choices=["per_question", "pooled"],
        help="Corpus setting: per_question (small per-question corpus) or "
        "pooled (one shared deduplicated corpus over all questions)",
    )
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split")
    parser.add_argument(
        "--k",
        type=int,
        default=None,
        dest="top_k_max",
        help="How many ranked results to store per question (top_k_max horizon "
        "for gold_ranks; must cover the largest metric cutoff). Default depends "
        "on --setting: 10 for per_question, 50 for pooled.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run id (default: <today>_<smallest unused letter>)",
    )
    parser.add_argument(
        "--runs-root",
        type=str,
        default="results/runs",
        help="Root directory that run directories are created under",
    )
    args = parser.parse_args()

    main(
        n=args.n,
        split=args.split,
        setting=args.setting,
        top_k_max=args.top_k_max,
        run_id=args.run_id,
        runs_root=args.runs_root,
    )
