"""
run_rerank_experiment.py  (the formal reranker runner)

The third retrieval stage after BM25 (run_bm25_experiment.py) and dense
(run_dense_experiment.py): re-scores the dense pooled top-50 shortlist with a
cross-encoder and writes `results/rerank_results.csv` in the SAME finalized
long-format schema (docs/specs/2026-07-15-results-csv-schema.md) as the other
two methods, one row per (method, setting, example), so all three files concat
by `example_id`.

Two corpus settings share ONE output CSV (--setting selects which one runs):

POOLED (--setting pooled, the default) reranks the dense top-50 shortlist --
sharpening a shortlist is meaningful only when there is a shortlist to sharpen:

    results/dense_top50_pooled.csv   (example_id, rank, title, score)
        -> group candidate titles per example, ordered by dense rank
        -> join (example_id, title) back to the pooled corpus for paragraph
           TEXT (the top-50 export stores no text, by design)
        -> CrossEncoderReranker.rerank  (reuses the cross-encoder reranker
           class; this runner never re-implements scoring/sorting)
        -> reranked titles -> evidence Recall@k + reciprocal rank (evaluator.py)

PER_QUESTION (--setting per_question) reranks each question's OWN provided
candidate set (example.paragraphs, ~10 gold+distractor paragraphs). It reads no
top-50 export and builds no pooled corpus: the cross-encoder scores ALL of a
question's candidates in one call, then the top 10 are stored. Per the K policy
the per_question rows fill @2/@5 and leave @10 empty, and (because the final
list has at most ~10 titles) RR@10 and RR@50 are equal per row. These 500
per_question rows are byte-preserving merge-appended onto the already-accepted
500 pooled rows in the SAME CSV: the existing pooled bytes are copied verbatim
(never re-serialized) and the reranked per_question rows are appended after them
via a same-directory temp file, a full 1000-row re-validation, an exact
byte-prefix check, and an atomic os.replace -- so an accepted pooled result can
never be recomputed, reordered, or corrupted by a failed per_question run.

For the pooled path, two inputs must describe the SAME evaluation set, enforced
before any model is
built: the pooled corpus is rebuilt here from `load_examples(--split, --n)`, and
the top-50 CSV's example-ID set must equal the loaded example-ID set exactly
(both a missing and an unexpected ID raise), each example must carry exactly the
pooled storage depth of candidates, and every candidate title must resolve to a
paragraph in the corpus. Passing an --n/--split that does not match the run
which produced the CSV is therefore caught loudly, never silently dropped.

Like the dense/BM25 runners, this one only *calls* evaluator.py
(evaluate_example / aggregate_results); it re-implements no recall metric --
that logic is a hand-written core component and stays in evaluator.py. The
per-example bare ``mrr`` key is replaced with the explicit reciprocal-rank
column names the schema fixes (RR@10 / RR@50, no bare ``mrr``).

AI-usage boundary: pure plumbing (CSV join -> reuse reranker -> call evaluator
-> write rows), no metric definition and no failure-taxonomy judgement, so this
is agent-allowed per the project's AI boundary.

Usage:
    # pooled (default): writes/overwrites the 500 pooled rows
    python scripts/run_rerank_experiment.py --n 500
    python scripts/run_rerank_experiment.py --n 500 \
        --top50-in results/dense_top50_pooled.csv --out results/rerank_results.csv

    # per_question: appends 500 per_question rows onto the existing pooled CSV
    python scripts/run_rerank_experiment.py --setting per_question --n 500 \
        --out results/rerank_results.csv

The first real run downloads cross-encoder/ms-marco-MiniLM-L-6-v2 and HotpotQA,
so it needs network access once; both are cached locally afterward.
"""

import argparse
import hashlib
import os
import sys

# Allow running directly from the project root without installing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from src.cross_encoder_reranker import CrossEncoderReranker
from src.data_loader import Paragraph, build_pooled_corpus, load_examples
from src.evaluator import aggregate_results, evaluate_example
from src.results_schema import (
    METRIC_KS_BY_SETTING,
    RESULT_COLUMNS,
    STORE_DEPTH_BY_SETTING,
    TITLE_SEPARATOR,
    validate_setting,
)
from src.top50_export import TOP50_COLUMNS

METHOD = "rerank"

# The reranker writes both corpus settings into one CSV, but each is produced by
# a separate run. Storage depth and the filled metric cutoffs for each setting
# come straight from the shared schema so this method matches dense/BM25 exactly.
#
# POOLED reranks the dense top-50 shortlist (that shortlist exists only for the
# pooled corpus); it stores 50 titles and fills @2/@5/@10.
SETTING = "pooled"
POOLED_STORE_TOP_K = STORE_DEPTH_BY_SETTING[SETTING]
POOLED_METRIC_KS = list(METRIC_KS_BY_SETTING[SETTING])

# PER_QUESTION reranks each question's own ~10 provided paragraphs; it stores up
# to 10 titles, fills @2/@5, and leaves @10 empty (a ~10-paragraph corpus makes
# @10 trivially satisfied, exactly the dense/BM25 per_question policy).
PER_QUESTION_SETTING = "per_question"
PER_QUESTION_STORE_TOP_K = STORE_DEPTH_BY_SETTING[PER_QUESTION_SETTING]
PER_QUESTION_METRIC_KS = list(METRIC_KS_BY_SETTING[PER_QUESTION_SETTING])

# The three @10 recall columns are the ones the per_question K policy leaves
# uncomputed; used by the per_question and merge validators.
AT10_RECALL_COLUMNS = [
    "any_evidence_recall@10",
    "full_evidence_recall@10",
    "partial_evidence_recall@10",
]

TITLE_SEP = TITLE_SEPARATOR

# Fixed column order shared by BM25, dense, and this reranker.
COLUMNS = RESULT_COLUMNS


def title_depth(retrieved_titles):
    """Count the titles stored in a ``retrieved_titles`` cell.

    An empty/NaN cell (a question with zero candidates) is depth 0, not 1 --
    ``"".split(TITLE_SEP)`` would otherwise return ``[""]``. MediaWiki titles
    cannot contain the ``" | "`` separator, so a plain split is exact.
    """
    if retrieved_titles is None:
        return 0
    if isinstance(retrieved_titles, float) and pd.isna(retrieved_titles):
        return 0
    text = str(retrieved_titles)
    if text == "":
        return 0
    return len(text.split(TITLE_SEP))


def read_top50(top50_path):
    """Read the dense top-50 export, validating its exact
    (example_id, rank, title, score) schema before use.

    example_id is forced to str so it joins against HotpotExample.example_id
    (a str) even if a batch of ids happened to look numeric.
    """
    if not os.path.exists(top50_path):
        raise FileNotFoundError(
            f"Reranker input not found: {top50_path!r}. Produce it first with "
            f"run_dense_experiment.py --setting both --top50-out {top50_path}."
        )
    df = pd.read_csv(top50_path, dtype={"example_id": str})
    if list(df.columns) != TOP50_COLUMNS:
        raise ValueError(
            f"{top50_path!r} has columns {list(df.columns)}, expected the "
            f"top-50 export schema {TOP50_COLUMNS}."
        )
    return df


def candidate_titles_by_example(top50_df):
    """Group the top-50 export into {example_id: [title, ...]} ordered by
    ascending dense rank.

    Ranks within each example must be contiguous 1..N (the export writes one
    row per (example, rank) with no gaps); a gap would mean the candidate list
    was truncated or corrupted, so we fail loudly rather than rerank a partial
    shortlist. The candidate order feeds the reranker only as tie-break input --
    the cross-encoder re-scores everything -- but we still honour the dense
    ranking so ties resolve reproducibly.
    """
    grouped = {}
    for example_id, sub in top50_df.groupby("example_id", sort=False):
        sub = sub.sort_values("rank")
        ranks = sub["rank"].tolist()
        expected = list(range(1, len(sub) + 1))
        if ranks != expected:
            raise ValueError(
                f"example {example_id!r}: top-50 ranks are not contiguous "
                f"1..{len(sub)} (got {ranks}); the candidate shortlist is "
                f"truncated or corrupted."
            )
        grouped[example_id] = sub["title"].tolist()
    return grouped


def build_candidate_paragraphs(titles, text_by_title, example_id):
    """Join each candidate title back to the pooled corpus to recover its
    paragraph TEXT (the top-50 export stores titles + scores only). Returns a
    list of Paragraph, in the given title order.

    A title absent from the pooled corpus means the top-50 CSV and the rebuilt
    corpus describe different evaluation sets (wrong --n/--split), which would
    corrupt every downstream rank and metric -- so we raise instead of dropping
    the candidate.
    """
    paragraphs = []
    for title in titles:
        if title not in text_by_title:
            raise ValueError(
                f"Candidate title {title!r} (example {example_id!r}) is not in "
                f"the pooled corpus. The top-50 CSV must come from the SAME "
                f"--n/--split used to build this pooled corpus."
            )
        paragraphs.append(Paragraph(title=title, text=text_by_title[title]))
    return paragraphs


def evaluate_for_results(retrieved_titles, gold_titles, k_values):
    """Shape existing evaluator output for the formal result schema.

    The evaluator owns all metric computation. This runner calls it on the two
    documented horizons and replaces its context-dependent bare ``mrr`` key
    with explicit per-example reciprocal-rank column names (matching how the
    dense and failure-review runners each shape the same evaluator output).
    """
    metrics = evaluate_example(retrieved_titles, gold_titles, k_values=k_values)
    metrics.pop("mrr")
    metrics["reciprocal_rank_at_10"] = evaluate_example(
        retrieved_titles[:10], gold_titles, k_values=[]
    )["mrr"]
    metrics["reciprocal_rank_at_50"] = evaluate_example(
        retrieved_titles[:50], gold_titles, k_values=[]
    )["mrr"]
    return metrics


def make_row(
    example,
    retrieved_titles,
    setting=SETTING,
    metric_ks=POOLED_METRIC_KS,
    store_top_k=POOLED_STORE_TOP_K,
):
    """Build one schema-shaped CSV row (a dict) for one example, plus the
    per-example metric dict (for aggregation).

    `retrieved_titles` is the RERANKED title list; only its first `store_top_k`
    entries go into the CSV. Recall is computed only at this `setting`'s K-policy
    cutoffs (`metric_ks`): pooled fills @2/@5/@10, per_question fills @2/@5. Any
    recall column outside `metric_ks` (per_question's three @10 columns) is left
    as None, which pandas writes as an empty cell and reads back as NaN -- so the
    per_question @10 metrics are deliberately uncomputed, never faked as 0.
    Booleans are encoded 1/0. Shape is identical for both settings and matches
    the dense runner's rows -- only `method`, `setting`, and the filled cutoffs
    differ. Reciprocal rank is always filled at both horizons; for per_question
    the final list has at most ~10 titles, so RR@10 == RR@50 per row.
    """
    metrics = evaluate_for_results(
        retrieved_titles, example.gold_titles, metric_ks
    )

    row = {
        "method": METHOD,
        "setting": setting,
        "example_id": example.example_id,
        "question_type": example.question_type,
        "level": example.level,
        "question": example.question,
        "gold_titles": TITLE_SEP.join(sorted(example.gold_titles)),
        "retrieved_titles": TITLE_SEP.join(retrieved_titles[:store_top_k]),
    }
    for key in COLUMNS[len(row):]:
        value = metrics.get(key)
        # int(bool) -> 1/0 per schema; a recall cutoff outside metric_ks is
        # absent from `metrics`, so metrics.get(...) is None -> empty cell (NaN).
        row[key] = int(value) if isinstance(value, bool) else value

    return row, metrics


def run_rerank_pooled(
    examples,
    titles_by_example,
    text_by_title,
    reranker,
    store_top_k=POOLED_STORE_TOP_K,
):
    """Rerank each example's dense top-50 shortlist and shape schema rows.

    For every example (in the given order, matching dense_results.csv's pooled
    rows): pull its candidate titles, join them to pooled-corpus text, rerank
    with the injected `CrossEncoderReranker`, and build the result row. Returns
    (rows, per_example_metrics).

    `titles_by_example` must cover every example (validated by the caller);
    `store_top_k` reranked titles are stored (50 for the pooled protocol).
    """
    rows = []
    per_example_metrics = []
    for ex in examples:
        candidates = build_candidate_paragraphs(
            titles_by_example[ex.example_id], text_by_title, ex.example_id
        )
        reranked_titles = reranker.rerank_titles(
            ex.question, candidates, top_k=store_top_k
        )
        # Output invariant: the formal pooled protocol stores exactly
        # store_top_k titles per row. With exactly store_top_k validated input
        # candidates and the reranker's one-score-per-candidate contract, the
        # reranked list is store_top_k long; this postcondition guarantees the
        # runner can never serialize a short row even if an injected reranker
        # misbehaves.
        if len(reranked_titles) != store_top_k:
            raise ValueError(
                f"example {ex.example_id!r}: reranked output has "
                f"{len(reranked_titles)} titles, expected exactly {store_top_k}."
            )
        row, metrics = make_row(ex, reranked_titles, store_top_k=store_top_k)
        rows.append(row)
        per_example_metrics.append(metrics)
    return rows, per_example_metrics


def run_rerank_per_question(
    examples,
    reranker,
    metric_ks=PER_QUESTION_METRIC_KS,
    store_top_k=PER_QUESTION_STORE_TOP_K,
):
    """Rerank each question's OWN provided candidate set and shape schema rows.

    Unlike the pooled path there is no top-50 shortlist and no shared corpus:
    each example's candidates ARE its `example.paragraphs` (~10 gold+distractor
    paragraphs), so no join is needed and `build_pooled_corpus` is not called.
    The whole candidate set is passed to the reranker, which scores every
    candidate in one call before truncating to `store_top_k` -- the scorer
    therefore always sees ALL of a question's candidates; nothing is dropped
    before scoring.

    Output invariant (defense in depth): the per_question protocol stores every
    reranked candidate up to `store_top_k`, so a row must carry exactly
    ``min(len(candidates), store_top_k)`` titles. That is deliberately NOT a
    blanket ``<= store_top_k``: a question with 8 candidates must keep all 8, not
    silently drop to 7; a question with 12 must score all 12 and keep 10; an
    (allowed) empty candidate set expects depth 0. This catches an injected
    reranker that returns the wrong count before any short/oversized row is
    serialized. Returns (rows, per_example_metrics).
    """
    rows = []
    per_example_metrics = []
    for ex in examples:
        candidates = ex.paragraphs
        reranked_titles = reranker.rerank_titles(
            ex.question, candidates, top_k=store_top_k
        )
        expected_depth = min(len(candidates), store_top_k)
        if len(reranked_titles) != expected_depth:
            raise ValueError(
                f"example {ex.example_id!r}: per_question reranked output has "
                f"{len(reranked_titles)} titles, expected exactly "
                f"{expected_depth} (min of {len(candidates)} candidate(s) and "
                f"the per_question store depth {store_top_k})."
            )
        row, metrics = make_row(
            ex,
            reranked_titles,
            setting=PER_QUESTION_SETTING,
            metric_ks=metric_ks,
            store_top_k=store_top_k,
        )
        rows.append(row)
        per_example_metrics.append(metrics)
    return rows, per_example_metrics


def validate_candidate_coverage(examples, titles_by_example):
    """The top-50 CSV's example-ID set must equal the loaded example-ID set
    EXACTLY -- neither side may carry an ID the other lacks.

    A loaded example missing from the CSV means the CSV came from a different
    (smaller) run; an example in the CSV that is not loaded means the CSV came
    from a larger run than requested. Either way the two artifacts describe
    different evaluation sets, so downstream ID/metric comparisons would be
    invalid. Both directions are reported (with a few offending IDs each) and
    the check runs before any model is built or any example is reranked.
    """
    loaded_ids = {ex.example_id for ex in examples}
    csv_ids = set(titles_by_example)
    missing = sorted(loaded_ids - csv_ids)
    unexpected = sorted(csv_ids - loaded_ids)
    if missing or unexpected:
        raise ValueError(
            f"top-50 CSV and loaded examples must describe the SAME evaluation "
            f"set. {len(missing)} loaded example(s) missing from the CSV "
            f"(first few: {missing[:5]}); {len(unexpected)} CSV example(s) not "
            f"in the loaded set (first few: {unexpected[:5]}). Use the same "
            f"--n/--split that produced the CSV."
        )


def validate_candidate_depths(titles_by_example, expected_depth=POOLED_STORE_TOP_K):
    """Every example must carry EXACTLY `expected_depth` candidates (the pooled
    storage depth, 50).

    This is deliberately separate from the contiguity check in
    `candidate_titles_by_example`: contiguity proves the ranks are 1..N with no
    gaps, but N could be 49 or 51 and still be contiguous. Depth proves N is
    exactly 50 -- a truncated (short) or oversized export is an invalid formal
    input that must fail before it is reranked and serialized, not be silently
    reranked at the wrong depth. Runs before any model is built.
    """
    wrong = {
        example_id: len(titles)
        for example_id, titles in titles_by_example.items()
        if len(titles) != expected_depth
    }
    if wrong:
        sample = list(wrong.items())[:5]
        raise ValueError(
            f"{len(wrong)} example(s) do not have exactly {expected_depth} "
            f"candidates in the top-50 CSV (example_id -> observed depth, first "
            f"few: {sample}); the pooled reranker input must store exactly "
            f"{expected_depth} candidates per example."
        )


def validate_existing_pooled_csv(out_path, examples):
    """Before a per_question run touches the output CSV, prove the file already
    holds EXACTLY the accepted pooled result for this evaluation set.

    The per_question rows are appended onto these pooled rows, so an unexpected
    pooled file (wrong method/setting, wrong row count, stale IDs, a truncated
    row, already-merged per_question rows, or a non-schema layout) would corrupt
    the merge. All of that is rejected up front, before any model is built.
    Returns (pooled_df, pooled_id_set).
    """
    if not os.path.exists(out_path):
        raise FileNotFoundError(
            f"per_question merge target {out_path!r} does not exist. Produce the "
            f"pooled reranker results first (run this script with the default "
            f"--setting pooled)."
        )
    df = pd.read_csv(out_path, dtype={"example_id": str})

    if list(df.columns) != RESULT_COLUMNS:
        raise ValueError(
            f"{out_path!r} does not match RESULT_COLUMNS (got {list(df.columns)}); "
            f"refusing to append per_question rows to a non-schema file."
        )

    methods = set(df["method"])
    if methods != {METHOD}:
        raise ValueError(
            f"{out_path!r} must contain only method={METHOD!r} rows, found {methods}."
        )
    settings = set(df["setting"])
    if settings != {SETTING}:
        raise ValueError(
            f"{out_path!r} must contain only the accepted {SETTING!r} rows before "
            f"a per_question merge, found settings {settings} (already-merged "
            f"per_question rows, or the wrong file)."
        )

    if len(df) != len(examples):
        raise ValueError(
            f"{out_path!r} has {len(df)} pooled row(s) but {len(examples)} "
            f"examples were loaded; the pooled results and this run must cover "
            f"the same evaluation set (use the same --n/--split)."
        )
    if df["example_id"].duplicated().any():
        dups = sorted(df.loc[df["example_id"].duplicated(), "example_id"].unique())
        raise ValueError(
            f"{out_path!r} has duplicate pooled example_id(s) (first few: "
            f"{dups[:5]}); the accepted pooled result has one row per example."
        )

    pooled_ids = set(df["example_id"])
    loaded_ids = {ex.example_id for ex in examples}
    if pooled_ids != loaded_ids:
        missing = sorted(loaded_ids - pooled_ids)
        extra = sorted(pooled_ids - loaded_ids)
        raise ValueError(
            f"{out_path!r} pooled example_id set does not match the loaded set: "
            f"{len(missing)} loaded missing from CSV (first few: {missing[:5]}); "
            f"{len(extra)} in CSV but not loaded (first few: {extra[:5]}). Use the "
            f"same --n/--split that produced the pooled results."
        )

    depths = df["retrieved_titles"].map(title_depth)
    wrong = df.loc[depths != POOLED_STORE_TOP_K, "example_id"].tolist()
    if wrong:
        raise ValueError(
            f"{len(wrong)} pooled row(s) in {out_path!r} do not store exactly "
            f"{POOLED_STORE_TOP_K} titles (first few example_id: {wrong[:5]}); the "
            f"accepted pooled result stores the full top-{POOLED_STORE_TOP_K}."
        )

    return df, pooled_ids


def validate_per_question_frame(pq_df, examples, pooled_ids):
    """Validate the freshly built per_question DataFrame BEFORE it is written.

    Enforces the per_question output contract row-for-row: one rerank row per
    loaded example, the same example-ID set as the accepted pooled rows, each
    row storing exactly ``min(candidate count, 10)`` titles, the three @10
    recall columns left empty (NaN, never faked as 0), and RR@10 == RR@50 per
    row (the final list has at most ~10 titles, so both horizons coincide).
    """
    if len(pq_df) != len(examples):
        raise ValueError(
            f"per_question frame has {len(pq_df)} row(s), expected "
            f"{len(examples)} (one per loaded example)."
        )
    methods = set(pq_df["method"])
    if methods != {METHOD}:
        raise ValueError(f"per_question rows must all be method={METHOD!r}, got {methods}.")
    settings = set(pq_df["setting"])
    if settings != {PER_QUESTION_SETTING}:
        raise ValueError(
            f"per_question rows must all be setting={PER_QUESTION_SETTING!r}, got {settings}."
        )
    if pq_df["example_id"].duplicated().any():
        dups = sorted(pq_df.loc[pq_df["example_id"].duplicated(), "example_id"].unique())
        raise ValueError(f"per_question frame has duplicate example_id(s): {dups[:5]}.")

    pq_ids = set(pq_df["example_id"])
    if pq_ids != pooled_ids:
        missing = sorted(pooled_ids - pq_ids)
        extra = sorted(pq_ids - pooled_ids)
        raise ValueError(
            f"per_question example_id set must equal the pooled set: "
            f"{len(missing)} pooled missing (first few: {missing[:5]}); "
            f"{len(extra)} extra (first few: {extra[:5]})."
        )

    candidate_counts = {ex.example_id: len(ex.paragraphs) for ex in examples}
    for _, row in pq_df.iterrows():
        expected = min(candidate_counts[row["example_id"]], PER_QUESTION_STORE_TOP_K)
        observed = title_depth(row["retrieved_titles"])
        if observed != expected:
            raise ValueError(
                f"example {row['example_id']!r}: per_question row stores "
                f"{observed} title(s), expected exactly {expected} "
                f"(min of the candidate count and store depth "
                f"{PER_QUESTION_STORE_TOP_K})."
            )

    for column in AT10_RECALL_COLUMNS:
        if not pq_df[column].isna().all():
            raise ValueError(
                f"per_question rows must leave {column!r} empty (the K policy does "
                f"not compute @10 for per_question); found non-empty values."
            )

    if not (pq_df["reciprocal_rank_at_10"] == pq_df["reciprocal_rank_at_50"]).all():
        raise ValueError(
            "per_question RR@10 and RR@50 must be equal per row (the final list "
            "has at most ~10 titles, so both horizons see the same ranking)."
        )


def validate_merged_bundle(merged, examples):
    """Re-validate the full 1000-row file after the append, read back from disk.

    This is the final gate before the atomic replace: it re-proves the schema,
    the pooled+per_question split, unique (setting, example_id) keys, the
    per-setting example-ID parity, storage depths for both settings, the
    per_question @10-empty / pooled @10-filled policy, and per_question
    RR-horizon equality -- all recomputed from the serialized bytes, not trusted
    from the in-memory frames.
    """
    n = len(examples)
    if list(merged.columns) != RESULT_COLUMNS:
        raise ValueError(
            f"merged file does not match RESULT_COLUMNS (got {list(merged.columns)})."
        )
    if set(merged["method"]) != {METHOD}:
        raise ValueError(f"merged file must be all method={METHOD!r}.")
    if len(merged) != 2 * n:
        raise ValueError(
            f"merged file has {len(merged)} rows, expected {2 * n} "
            f"({n} pooled + {n} per_question)."
        )
    counts = merged["setting"].value_counts().to_dict()
    if counts != {SETTING: n, PER_QUESTION_SETTING: n}:
        raise ValueError(
            f"merged file setting counts {counts} != "
            f"{{{SETTING!r}: {n}, {PER_QUESTION_SETTING!r}: {n}}}."
        )
    if merged.duplicated(subset=["setting", "example_id"]).any():
        raise ValueError(
            "merged file has duplicate (setting, example_id) key(s); the append "
            "must not overlap the pooled rows."
        )

    loaded_ids = {ex.example_id for ex in examples}
    pooled = merged[merged["setting"] == SETTING]
    perq = merged[merged["setting"] == PER_QUESTION_SETTING]
    if set(pooled["example_id"]) != loaded_ids:
        raise ValueError("merged pooled example_id set changed from the loaded set.")
    if set(perq["example_id"]) != loaded_ids:
        raise ValueError("merged per_question example_id set does not match the loaded set.")

    pooled_wrong = pooled.loc[
        pooled["retrieved_titles"].map(title_depth) != POOLED_STORE_TOP_K,
        "example_id",
    ].tolist()
    if pooled_wrong:
        raise ValueError(
            f"merged pooled row(s) no longer store {POOLED_STORE_TOP_K} titles "
            f"(first few: {pooled_wrong[:5]})."
        )
    candidate_counts = {ex.example_id: len(ex.paragraphs) for ex in examples}
    for _, row in perq.iterrows():
        expected = min(candidate_counts[row["example_id"]], PER_QUESTION_STORE_TOP_K)
        if title_depth(row["retrieved_titles"]) != expected:
            raise ValueError(
                f"merged per_question row {row['example_id']!r} stores the wrong "
                f"depth (expected {expected})."
            )

    for column in AT10_RECALL_COLUMNS:
        if not perq[column].isna().all():
            raise ValueError(f"merged per_question {column!r} must be empty (NaN).")
        if pooled[column].isna().any():
            raise ValueError(f"merged pooled {column!r} must be filled (no NaN).")

    if not (perq["reciprocal_rank_at_10"] == perq["reciprocal_rank_at_50"]).all():
        raise ValueError("merged per_question RR@10 and RR@50 must be equal per row.")


def atomic_merge_append(out_path, pq_df, examples):
    """Append the per_question rows onto the existing pooled CSV WITHOUT
    re-serializing the accepted pooled rows.

    The pooled bytes are copied verbatim; only the per_question rows are newly
    serialized (header-less, with the pooled file's own line terminator) and
    concatenated after them in a same-directory temp file. The temp file is then
    fully re-validated (`validate_merged_bundle`) and proven to keep the pooled
    bytes as an exact prefix before an atomic ``os.replace`` swaps it in. Any
    failure removes the temp file and leaves the original ``out_path`` untouched,
    so a broken run can never leave a half-written or reordered formal result.
    Returns the recorded baseline pooled SHA-256 (upper hex).
    """
    with open(out_path, "rb") as handle:
        baseline_bytes = handle.read()
    baseline_sha = hashlib.sha256(baseline_bytes).hexdigest().upper()

    if not baseline_bytes.endswith(b"\n"):
        raise ValueError(
            f"{out_path!r} does not end with a newline; refusing to append "
            f"per_question rows onto an unterminated final pooled row."
        )
    newline = "\r\n" if baseline_bytes.endswith(b"\r\n") else "\n"

    # Only the per_question rows are (re)serialized; the pooled bytes are never
    # round-tripped through pandas. header=False so there is exactly one header.
    per_question_text = pq_df.to_csv(index=False, header=False, lineterminator=newline)
    per_question_bytes = per_question_text.encode("utf-8")

    tmp_path = out_path + ".merge.tmp"
    try:
        with open(tmp_path, "wb") as handle:
            handle.write(baseline_bytes)
            handle.write(per_question_bytes)

        # Re-read the serialized bytes and re-validate the whole 1000-row bundle.
        merged = pd.read_csv(tmp_path, dtype={"example_id": str})
        validate_merged_bundle(merged, examples)

        # The pooled bytes must survive verbatim as a prefix of the merged file.
        with open(tmp_path, "rb") as handle:
            merged_bytes = handle.read()
        if not merged_bytes.startswith(baseline_bytes):
            raise ValueError(
                "merged temp file does not preserve the pooled bytes as an exact "
                "prefix; refusing to replace the formal result."
            )

        os.replace(tmp_path, out_path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

    return baseline_sha


def _run_pooled(examples, top50_in, out_path, reranker):
    """Pooled path (unchanged behavior): read the dense top-50 shortlist, join
    it to the pooled corpus for text, rerank, and (over)write the pooled rows."""
    pooled_paragraphs, collision_titles = build_pooled_corpus(examples)
    print(
        f"Pooled corpus: {len(pooled_paragraphs)} paragraphs "
        f"({len(collision_titles)} title collisions).\n"
    )
    text_by_title = {p.title: p.text for p in pooled_paragraphs}

    print(f"Reading dense candidate shortlist from {top50_in}...")
    titles_by_example = candidate_titles_by_example(read_top50(top50_in))
    validate_candidate_coverage(examples, titles_by_example)
    validate_candidate_depths(titles_by_example)

    if reranker is None:
        print("Building cross-encoder (first run downloads ms-marco-MiniLM-L-6-v2)...")
        reranker = CrossEncoderReranker()

    rows, per_example_metrics = run_rerank_pooled(
        examples, titles_by_example, text_by_title, reranker,
        store_top_k=POOLED_STORE_TOP_K,
    )

    df = pd.DataFrame(rows, columns=COLUMNS)
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}\n")

    print(f"Overall RERANK retrieval metrics ({SETTING}, n={len(examples)}):")
    for metric, value in aggregate_results(per_example_metrics).items():
        print(f"  {metric}: {value:.3f}")


def _run_per_question(examples, out_path, reranker):
    """Per-question path: rerank each question's own candidates and byte-append
    them onto the already-accepted pooled rows. Reads no top-50 export and never
    rebuilds/rewrites the pooled corpus or the pooled rows."""
    # Validate the existing accepted pooled CSV BEFORE building any model, so a
    # wrong/stale target fails cheaply.
    print(f"Validating existing pooled results in {out_path} before merge...")
    _pooled_df, pooled_ids = validate_existing_pooled_csv(out_path, examples)

    if reranker is None:
        print("Building cross-encoder (first run downloads ms-marco-MiniLM-L-6-v2)...")
        reranker = CrossEncoderReranker()

    rows, per_example_metrics = run_rerank_per_question(examples, reranker)
    pq_df = pd.DataFrame(rows, columns=COLUMNS)
    validate_per_question_frame(pq_df, examples, pooled_ids)

    baseline_sha = atomic_merge_append(out_path, pq_df, examples)
    print(
        f"Appended {len(pq_df)} per_question rows to {out_path} "
        f"(pooled prefix preserved; pooled baseline SHA-256 {baseline_sha}).\n"
    )

    print(f"Overall RERANK retrieval metrics ({PER_QUESTION_SETTING}, n={len(examples)}):")
    for metric, value in aggregate_results(per_example_metrics).items():
        print(f"  {metric}: {value:.3f}")


def main(n, split, top50_in, out_path, setting=SETTING, reranker=None):
    print(f"Loading {n} HotpotQA examples from split='{split}'...")
    examples = load_examples(split=split, n=n)
    print(f"Loaded {len(examples)} examples.\n")

    if setting == PER_QUESTION_SETTING:
        _run_per_question(examples, out_path, reranker)
    elif setting == SETTING:
        _run_pooled(examples, top50_in, out_path, reranker)
    else:
        # validate_setting rejects anything outside the schema vocabulary; a
        # known-but-unsupported setting (there is none today) would fall through.
        validate_setting(setting)
        raise ValueError(
            f"The reranker runner supports only {SETTING!r} and "
            f"{PER_QUESTION_SETTING!r}; got {setting!r}."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reranker runner: rerank the dense pooled top-50 (pooled) or "
        "each question's own candidates (per_question) -> Any/Full/Partial "
        "Evidence Recall@k, written in the long-format results schema."
    )
    parser.add_argument("--n", type=int, default=500, help="Number of examples to load")
    parser.add_argument(
        "--setting",
        type=str,
        default=SETTING,
        choices=[SETTING, PER_QUESTION_SETTING],
        help="Corpus setting: pooled (default; reranks the dense top-50 shortlist "
        "and writes the pooled rows) or per_question (reranks each question's own "
        "candidates and appends them onto the existing pooled rows).",
    )
    parser.add_argument("--split", type=str, default="validation", help="HotpotQA split")
    parser.add_argument(
        "--top50-in",
        type=str,
        default="results/dense_top50_pooled.csv",
        dest="top50_in",
        help="Dense pooled top-50 export (example_id,rank,title,score) used as "
        "the reranker's candidate shortlist. Pooled setting only; ignored for "
        "per_question.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="results/rerank_results.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    main(
        n=args.n,
        split=args.split,
        top50_in=args.top50_in,
        out_path=args.out,
        setting=args.setting,
    )
