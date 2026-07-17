"""Shared storage contract for formal retrieval result CSVs.

This module contains schema/plumbing constants only. Metric definitions and
their core computation remain in :mod:`src.evaluator` per the project AI-use
boundary.
"""

TITLE_SEPARATOR = " | "

METRIC_KS = (2, 5, 10)
METRIC_KS_BY_SETTING = {
    "per_question": (2, 5),
    "pooled": METRIC_KS,
}

# A small per-question corpus returns all available paragraphs (normally
# about ten); pooled formal results store the first 50 when that many exist.
STORE_DEPTH_BY_SETTING = {
    "per_question": 10,
    "pooled": 50,
}

BASE_COLUMNS = [
    "method",
    "setting",
    "example_id",
    "question_type",
    "level",
    "question",
    "gold_titles",
    "retrieved_titles",
]

RECALL_COLUMNS = [
    f"{metric_name}@{k}"
    for metric_name in (
        "any_evidence_recall",
        "full_evidence_recall",
        "partial_evidence_recall",
    )
    for k in METRIC_KS
]

# These are per-example reciprocal ranks. Their dataset means are reported as
# MRR@10 and MRR@50; a bare `mrr` column is deliberately not part of the CSV:
#
#   MRR@10 = df["reciprocal_rank_at_10"].mean()
#   MRR@50 = df["reciprocal_rank_at_50"].mean()
#
# Compute each mean within the intended method/setting analysis group.
RECIPROCAL_RANK_COLUMNS = [
    "reciprocal_rank_at_10",
    "reciprocal_rank_at_50",
]

RESULT_COLUMNS = BASE_COLUMNS + RECALL_COLUMNS + RECIPROCAL_RANK_COLUMNS


def validate_setting(setting: str) -> None:
    """Reject unknown corpus settings before a runner loads data or models."""
    if setting not in STORE_DEPTH_BY_SETTING:
        raise ValueError(f"Unknown setting: {setting!r}")
