"""
data_loader.py

Loads HotpotQA examples and turns them into the shapes the rest of the
pipeline needs:

  - a paragraph-level retrieval corpus (one entry per title+sentences block)
  - the set of gold evidence paragraph titles for each question, derived
    from `supporting_facts`

Corpus settings (Week 2):
  - per_question: each question's own ~10 provided paragraphs (Week 1 setting)
  - pooled: all evaluated questions' paragraphs merged into one shared corpus,
    deduplicated by title. This is now the PRIMARY setting; per_question is
    the contrast setting (see build_pooled_corpus below).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple


@dataclass
class Paragraph:
    """One retrieval unit: a single Wikipedia paragraph."""
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
    paragraphs: List[Paragraph]         # this question's own ~10 paragraphs
    gold_titles: Set[str] = field(default_factory=set)  # gold evidence titles


def load_raw_hotpotqa(split: str = "validation", n: Optional[int] = None):
    """
    Loads raw HotpotQA examples via Hugging Face `datasets`.

    split: "train" or "validation" (HotpotQA test set has no public labels,
           so validation is the standard dev/eval split to use here).
    n: if set, only load the first n examples.

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


def build_pooled_corpus(examples: List[HotpotExample]) -> Tuple[List[Paragraph], List[str]]:
    """
    Merges every example's per-question paragraphs into one shared corpus
    (Week 2's PRIMARY corpus setting), deduplicated by title.

    Dedup rule (per project plan): if the same title appears across multiple
    questions with slightly different paragraph text, keep the FIRST
    occurrence encountered and log the title as a collision. This is safe
    for evaluation because gold matching is by title, not exact text.

    Returns:
        (pooled_paragraphs, collision_titles)
        - pooled_paragraphs: deduplicated list of Paragraph, insertion order
        - collision_titles: titles where a later occurrence's text differed
          from the first (for logging/inspection, not used in scoring)
    """
    seen: Dict[str, Paragraph] = {}
    collision_titles: List[str] = []

    for example in examples:
        for paragraph in example.paragraphs:
            if paragraph.title not in seen:
                seen[paragraph.title] = paragraph
            elif seen[paragraph.title].text != paragraph.text:
                collision_titles.append(paragraph.title)

    return list(seen.values()), collision_titles
