"""
data_loader.py

Loads HotpotQA examples and turns them into the shapes the rest of the
pipeline needs:

  - a paragraph-level retrieval corpus (one entry per title+sentences block)
  - the set of gold evidence paragraph titles for each question, derived
    from `supporting_facts`

Scope note: per the project plan, the retrieval corpus for each question
is built ONLY from that question's own `context` field (the ~10 paragraphs
HotpotQA already provides, 2 gold + ~8 distractors). We are not retrieving
against all of Wikipedia.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional


@dataclass
class Paragraph:
    """One retrieval unit: a single Wikipedia paragraph belonging to a
    specific HotpotQA question's context."""
    title: str
    text: str


@dataclass
class HotpotExample:
    """A single processed HotpotQA question, ready for retrieval + eval."""
    example_id: str
    question: str
    answer: str
    question_type: str      # "bridge" or "comparison"
    level: str               # "easy" / "medium" / "hard"
    paragraphs: List[Paragraph]         # the per-question retrieval corpus
    gold_titles: Set[str] = field(default_factory=set)  # gold evidence titles


def load_raw_hotpotqa(split: str = "validation", n: Optional[int] = None):
    """
    Loads raw HotpotQA examples via Hugging Face `datasets`.

    split: "train" or "validation" (HotpotQA test set has no public labels,
           so validation is the standard dev/eval split to use here).
    n: if set, only load the first n examples (useful for the Week 1
       10-example debug subset).

    `trust_remote_code` compatibility: HotpotQA used to ship as a Hub loading
    script, so older `datasets` (< 3.0) REQUIRE `trust_remote_code=True` to run
    it. Newer `datasets` (3.x / 4.x) serve it as Parquet, execute no remote
    code, and treat `trust_remote_code` as removed -- passing it prints a
    deprecation warning (4.x) or would raise. So we try the modern no-arg call
    first and only fall back to the legacy arg when the failure is specifically
    about trust_remote_code; any other error (bad split, no network) propagates
    unchanged. This keeps one code path working across the pinned version range.
    """
    from datasets import load_dataset

    try:
        ds = load_dataset("hotpot_qa", "distractor", split=split)
    except (ValueError, TypeError) as err:
        if "trust_remote_code" not in str(err):
            raise  # a real error (unknown split, etc.), not the compat shim
        ds = load_dataset(
            "hotpot_qa", "distractor", split=split, trust_remote_code=True
        )
    if n is not None:
        ds = ds.select(range(min(n, len(ds))))
    return ds


def _build_paragraphs(context) -> List[Paragraph]:
    """
    Converts HotpotQA's `context` field into a list of Paragraph objects.

    `context` arrives as a dict with parallel lists:
        context["title"]     -> list[str]
        context["sentences"] -> list[list[str]]
    One Paragraph is created per title, joining its sentences into one
    passage of text.
    """
    titles = context["title"]
    sentence_groups = context["sentences"]

    paragraphs = []
    for title, sentences in zip(titles, sentence_groups):
        text = " ".join(s.strip() for s in sentences)
        paragraphs.append(Paragraph(title=title, text=text))
    return paragraphs


def _extract_gold_titles(supporting_facts) -> Set[str]:
    """
    Converts HotpotQA's `supporting_facts` field into a set of gold
    evidence paragraph titles.

    `supporting_facts` arrives as a dict with parallel lists:
        supporting_facts["title"]   -> list[str]
        supporting_facts["sent_id"] -> list[int]

    We only need the titles: a retrieved paragraph counts as a gold hit
    if its title appears here, regardless of which sentence index.
    """
    return set(supporting_facts["title"])


def process_example(raw_example) -> HotpotExample:
    """Converts one raw HotpotQA example (dict-like) into a HotpotExample."""
    paragraphs = _build_paragraphs(raw_example["context"])
    gold_titles = _extract_gold_titles(raw_example["supporting_facts"])

    return HotpotExample(
        example_id=raw_example.get("id", raw_example.get("_id", "")),
        question=raw_example["question"],
        answer=raw_example["answer"],
        question_type=raw_example.get("type", "unknown"),
        level=raw_example.get("level", "unknown"),
        paragraphs=paragraphs,
        gold_titles=gold_titles,
    )


def load_examples(split: str = "validation", n: Optional[int] = None) -> List[HotpotExample]:
    """
    Top-level convenience function: loads raw HotpotQA examples and
    processes them into HotpotExample objects in one call.

    Example:
        examples = load_examples(split="validation", n=10)
    """
    raw = load_raw_hotpotqa(split=split, n=n)
    return [process_example(ex) for ex in raw]
