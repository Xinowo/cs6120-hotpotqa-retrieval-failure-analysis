"""Build a human-review worksheet for HotpotQA gold-title matching.

This is inspection plumbing only.  It does not define, modify, or recompute
Recall/MRR metrics.  It cross-checks raw HotpotQA fields, processed gold-title
sets, saved ranked-title positions, and the formal result CSVs, then renders a
small deterministic sample for manual approval.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import process_example  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 12-case gold-title matching audit worksheet."
    )
    parser.add_argument("--validation-arrow", type=Path, required=True)
    parser.add_argument(
        "--details",
        type=Path,
        default=Path("results/runs/2026-07-17_a/details.jsonl"),
    )
    parser.add_argument(
        "--dense-results",
        type=Path,
        default=Path("results/dense_results.csv"),
    )
    parser.add_argument(
        "--bm25-results",
        type=Path,
        default=Path("results/bm25_results.csv"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "docs/Local/check_consistency/"
            "2026-07-20_gold_matching_spot_check.md"
        ),
    )
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument(
        "--human-review-pass",
        action="store_true",
        help="Render every manual checklist item and the final decision as PASS.",
    )
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--review-date", default="")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_pooled_results(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["setting"] == "pooled"]
    return {row["example_id"]: row for row in rows}


def split_titles(value: str) -> list[str]:
    if not value:
        return []
    return value.split(" | ")


def collision_titles(raw_rows: Iterable[dict[str, Any]]) -> set[str]:
    seen: dict[str, str] = {}
    collisions: set[str] = set()
    for raw in raw_rows:
        titles = raw["context"]["title"]
        sentence_groups = raw["context"]["sentences"]
        for title, sentences in zip(titles, sentence_groups):
            text = " ".join(sentence.strip() for sentence in sentences)
            if title not in seen:
                seen[title] = text
            elif seen[title] != text:
                collisions.add(title)
    return collisions


def first_saved_rank(record: dict[str, Any], gold_title: str) -> int | None:
    for item in record["top_k"]:
        if item["title"] == gold_title:
            return item["rank"]
    return None


def supporting_rows(raw: dict[str, Any]) -> list[dict[str, Any]]:
    context_titles = raw["context"]["title"]
    sentence_groups = raw["context"]["sentences"]
    output = []
    for title, sent_id in zip(
        raw["supporting_facts"]["title"],
        raw["supporting_facts"]["sent_id"],
    ):
        matching_indices = [
            index for index, context_title in enumerate(context_titles)
            if context_title == title
        ]
        sentence = None
        valid = False
        for index in matching_indices:
            sentences = sentence_groups[index]
            if 0 <= sent_id < len(sentences):
                sentence = sentences[sent_id]
                valid = True
                break
        output.append(
            {
                "title": title,
                "sent_id": sent_id,
                "sentence": sentence,
                "valid": valid,
            }
        )
    return output


def mechanical_checks(
    raw: dict[str, Any],
    detail: dict[str, Any],
    dense_csv: dict[str, str],
    bm25_csv: dict[str, str],
) -> list[tuple[str, bool]]:
    processed = process_example(raw)
    raw_gold = set(raw["supporting_facts"]["title"])
    detail_gold = set(detail["gold_titles"])
    support = supporting_rows(raw)

    checks: list[tuple[str, bool]] = [
        ("Raw ID equals details ID", processed.example_id == detail["example_id"]),
        ("Raw question equals details question", processed.question == detail["question"]),
        ("Raw supporting-title set equals processed gold_titles", raw_gold == processed.gold_titles),
        ("Processed gold_titles equals details gold_titles", processed.gold_titles == detail_gold),
        ("Every supporting title/sent_id resolves in context", all(row["valid"] for row in support)),
    ]

    for retriever_name in ("dense", "bm25"):
        retriever = detail["retrievers"][retriever_name]
        expected_ranks = {
            gold: first_saved_rank(retriever, gold) for gold in detail_gold
        }
        contiguous = [item["rank"] for item in retriever["top_k"]] == list(
            range(1, len(retriever["top_k"]) + 1)
        )
        checks.append(
            (
                f"{retriever_name} saved gold_ranks equal exact positions in saved top-50",
                retriever["gold_ranks"] == expected_ranks,
            )
        )
        checks.append(
            (
                f"{retriever_name} saved top_k rank indices are contiguous from 1",
                contiguous,
            )
        )

    checks.extend(
        [
            (
                "Dense details top-50 equals formal pooled CSV",
                [item["title"] for item in detail["retrievers"]["dense"]["top_k"]]
                == split_titles(dense_csv["retrieved_titles"]),
            ),
            (
                "BM25 details top-50 equals formal pooled CSV",
                [item["title"] for item in detail["retrievers"]["bm25"]["top_k"]]
                == split_titles(bm25_csv["retrieved_titles"]),
            ),
            (
                "Details gold_titles equal both formal pooled CSVs",
                detail_gold == set(split_titles(dense_csv["gold_titles"]))
                == set(split_titles(bm25_csv["gold_titles"])),
            ),
        ]
    )
    return checks


def balanced_take(
    candidates: list[dict[str, Any]],
    count: int,
    used: set[str],
) -> list[dict[str, Any]]:
    available = [c for c in candidates if c["example_id"] not in used]
    picked: list[dict[str, Any]] = []
    target_per_type = max(1, count // 2)
    for question_type in ("bridge", "comparison"):
        typed = [c for c in available if c["question_type"] == question_type]
        picked.extend(typed[:target_per_type])
    for candidate in available:
        if len(picked) >= count:
            break
        if candidate not in picked:
            picked.append(candidate)
    picked = picked[:count]
    used.update(candidate["example_id"] for candidate in picked)
    return picked


def select_cases(
    details: list[dict[str, Any]],
    raw_by_id: dict[str, dict[str, Any]],
    collisions: set[str],
) -> list[tuple[str, str, dict[str, Any]]]:
    used: set[str] = set()

    def edge_tags(detail: dict[str, Any]) -> list[str]:
        raw = raw_by_id[detail["example_id"]]
        raw_support_titles = raw["supporting_facts"]["title"]
        raw_context_titles = raw["context"]["title"]
        tags = []
        if len(raw_support_titles) != len(set(raw_support_titles)):
            tags.append("duplicate supporting title")
        if set(detail["gold_titles"]) & collisions:
            tags.append("gold title has pooled text collision")
        if len(raw_context_titles) != len(set(raw_context_titles)):
            tags.append("duplicate context title")
        return tags

    edge_candidates = [detail for detail in details if edge_tags(detail)]
    edge_picks: list[dict[str, Any]] = []
    for wanted_tag in (
        "duplicate supporting title",
        "gold title has pooled text collision",
        "duplicate context title",
    ):
        for detail in edge_candidates:
            if detail["example_id"] in used or detail in edge_picks:
                continue
            if wanted_tag in edge_tags(detail):
                edge_picks.append(detail)
                used.add(detail["example_id"])
                break
        if len(edge_picks) == 2:
            break
    if len(edge_picks) < 2:
        for detail in edge_candidates:
            if len(edge_picks) == 2:
                break
            if detail["example_id"] in used or detail in edge_picks:
                continue
            edge_picks.append(detail)
            used.add(detail["example_id"])

    dense_wins = [
        detail for detail in details
        if detail["retrievers"]["dense"]["metrics"]["full_evidence_recall@5"]
        and not detail["retrievers"]["bm25"]["metrics"]["full_evidence_recall@5"]
    ]
    bm25_wins = [
        detail for detail in details
        if detail["retrievers"]["bm25"]["metrics"]["full_evidence_recall@5"]
        and not detail["retrievers"]["dense"]["metrics"]["full_evidence_recall@5"]
    ]
    disagreement_picks = []
    for pool in (dense_wins, bm25_wins):
        pick = balanced_take(pool, 1, used)
        disagreement_picks.extend(pick)
    if len(disagreement_picks) < 2:
        all_disagreements = [
            detail for detail in details
            if detail["retrievers"]["dense"]["metrics"]["full_evidence_recall@5"]
            != detail["retrievers"]["bm25"]["metrics"]["full_evidence_recall@5"]
        ]
        disagreement_picks.extend(
            balanced_take(all_disagreements, 2 - len(disagreement_picks), used)
        )

    dense_no_hit = [
        detail for detail in details
        if not detail["retrievers"]["dense"]["metrics"]["any_evidence_recall@5"]
    ]
    dense_partial = [
        detail for detail in details
        if detail["retrievers"]["dense"]["metrics"]["any_evidence_recall@5"]
        and not detail["retrievers"]["dense"]["metrics"]["full_evidence_recall@5"]
    ]
    failure_picks = balanced_take(dense_no_hit, 2, used)
    failure_picks.extend(balanced_take(dense_partial, 4 - len(failure_picks), used))
    if len(failure_picks) < 4:
        all_failures = [
            detail for detail in details
            if not detail["retrievers"]["dense"]["metrics"]["full_evidence_recall@5"]
        ]
        failure_picks.extend(balanced_take(all_failures, 4 - len(failure_picks), used))

    successes = [
        detail for detail in details
        if detail["retrievers"]["dense"]["metrics"]["full_evidence_recall@5"]
    ]
    success_picks = balanced_take(successes, 4, used)

    selected: list[tuple[str, str, dict[str, Any]]] = []
    for detail in success_picks:
        selected.append(("Dense success", "Dense Full@5 = 1", detail))
    for detail in failure_picks:
        dense_metrics = detail["retrievers"]["dense"]["metrics"]
        mode = "no gold in top-5" if not dense_metrics["any_evidence_recall@5"] else "partial gold in top-5"
        selected.append(("Dense Full@5 failure", mode, detail))
    for detail in disagreement_picks:
        dense_full = detail["retrievers"]["dense"]["metrics"]["full_evidence_recall@5"]
        direction = "Dense=1, BM25=0" if dense_full else "Dense=0, BM25=1"
        selected.append(("Dense/BM25 disagreement", direction, detail))
    for detail in edge_picks:
        selected.append(("Title edge case", "; ".join(edge_tags(detail)), detail))

    if len(selected) != 12:
        raise RuntimeError(f"Expected 12 distinct cases, selected {len(selected)}")
    if len({detail["example_id"] for _, _, detail in selected}) != 12:
        raise RuntimeError("Candidate selection produced duplicate example IDs")
    return selected


def md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_rank_table(record: dict[str, Any], gold_titles: set[str]) -> list[str]:
    lines = ["| Rank | Title | Gold? |", "|---:|---|:---:|"]
    for item in record["top_k"][:10]:
        lines.append(
            f"| {item['rank']} | {md_escape(item['title'])} | "
            f"{'yes' if item['title'] in gold_titles else ''} |"
        )
    return lines


def render_document(
    selected: list[tuple[str, str, dict[str, Any]]],
    raw_by_id: dict[str, dict[str, Any]],
    dense_results: dict[str, dict[str, str]],
    bm25_results: dict[str, dict[str, str]],
    collisions: set[str],
    args: argparse.Namespace,
) -> tuple[str, bool]:
    audit_rows = []
    all_machine_pass = True
    for category, reason, detail in selected:
        example_id = detail["example_id"]
        checks = mechanical_checks(
            raw_by_id[example_id],
            detail,
            dense_results[example_id],
            bm25_results[example_id],
        )
        passed = all(result for _, result in checks)
        all_machine_pass = all_machine_pass and passed
        audit_rows.append((category, reason, detail, checks, passed))

    if args.human_review_pass and not all_machine_pass:
        raise ValueError("Cannot approve human review while mechanical checks fail")

    review_mark = "x" if args.human_review_pass else " "
    final_review = "**PASS**" if args.human_review_pass else "☐ PASS / ☐ FAIL"
    review_notes = (
        "Reviewed; no mismatch found in the supporting evidence, deduplicated "
        "gold titles, or saved ranks."
        if args.human_review_pass
        else "_................................................................................_"
    )

    lines = [
        "# Gold Evidence Matching Spot Check — Human Review Worksheet",
        "",
        "> **Purpose:** verify that real HotpotQA supporting-fact titles are mapped to",
        "> paragraph-level gold titles correctly, and that saved ranks/results preserve",
        "> those exact titles. This worksheet does not define or recompute Recall/MRR.",
        "> The final correctness judgment and all checked boxes belong to Xin/team.",
        "",
        "## Sources and machine-check result",
        "",
        f"- Raw validation Arrow: `{md_escape(args.validation_arrow)}` (first {args.n} examples)",
        f"- Failure-review details: `{md_escape(args.details)}`",
        f"- Formal results: `{md_escape(args.dense_results)}`, `{md_escape(args.bm25_results)}`",
        f"- Pooled differing-text collision titles found mechanically: **{len(collisions)}**",
        f"- Selected examples: **12 distinct IDs**",
        f"- Mechanical cross-file checks: **{'PASS' if all_machine_pass else 'FAIL'}**",
        "",
        "Mechanical PASS means the saved fields agree with each other. It does **not**",
        "replace the human decision that the raw supporting title/sentence is the right",
        "paragraph-level gold evidence for the question.",
        "",
        "## Review summary",
        "",
        "| # | Category | Selection reason | Example ID | Type | Machine | Xin final review |",
        "|---:|---|---|---|---|:---:|:---:|",
    ]
    for index, (category, reason, detail, _, passed) in enumerate(audit_rows, start=1):
        lines.append(
            f"| {index:02d} | {md_escape(category)} | {md_escape(reason)} | "
            f"`{detail['example_id']}` | {detail['question_type']} | "
            f"{'PASS' if passed else 'FAIL'} | {final_review} |"
        )

    lines.extend(
        [
            "",
            "## Human completion rule",
            "",
            "For every case, check the five boxes after inspecting the evidence. If any",
            "case fails, record the exact mismatch and do not approve the Week 2 checkpoint",
            "until the effect on saved results is understood.",
            "",
        ]
    )

    for index, (category, reason, detail, checks, passed) in enumerate(audit_rows, start=1):
        example_id = detail["example_id"]
        raw = raw_by_id[example_id]
        processed = process_example(raw)
        gold_titles = set(detail["gold_titles"])
        context_titles = raw["context"]["title"]
        supporting = supporting_rows(raw)

        lines.extend(
            [
                f"## {index:02d}. {md_escape(category)} — `{example_id}`",
                "",
                f"**Selection reason:** {md_escape(reason)}  ",
                f"**Question type:** {detail['question_type']}  ",
                f"**Question:** {md_escape(detail['question'])}",
                "",
                "### Xin checklist",
                "",
                f"- [{review_mark}] Raw supporting title and sentence genuinely identify supporting evidence for this question.",
                f"- [{review_mark}] Paragraph-level `gold_titles` is the correct set after title deduplication.",
                f"- [{review_mark}] Dense saved `gold_ranks` agrees with the gold-rank evidence table and saved top-50 (top-10 shown below where applicable).",
                f"- [{review_mark}] BM25 saved `gold_ranks` agrees with the gold-rank evidence table and saved top-50 (top-10 shown below where applicable).",
                f"- [{review_mark}] Final decision for this example: **PASS**. If not, write the mismatch below.",
                "",
                "**Xin notes:**  ",
                review_notes,
                "",
                "### Raw and processed evidence",
                "",
                f"- Raw supporting titles in source order: `{md_escape(raw['supporting_facts']['title'])}`",
                f"- Raw supporting sentence IDs: `{md_escape(raw['supporting_facts']['sent_id'])}`",
                f"- Processed `gold_titles`: `{md_escape(sorted(processed.gold_titles))}`",
                f"- Context titles ({len(context_titles)}): {md_escape(' | '.join(context_titles))}",
                "",
                "| Raw title | sent_id | Referenced supporting sentence | Resolved? |",
                "|---|---:|---|:---:|",
            ]
        )
        for row in supporting:
            lines.append(
                f"| {md_escape(row['title'])} | {row['sent_id']} | "
                f"{md_escape(row['sentence'] if row['sentence'] is not None else '[missing]')} | "
                f"{'yes' if row['valid'] else 'NO'} |"
            )

        dense_record = detail["retrievers"]["dense"]
        bm25_record = detail["retrievers"]["bm25"]
        lines.extend(
            [
                "",
                "### Gold-rank evidence in the saved top-50",
                "",
                "`null` / `not present` means the exact gold title is absent from the saved top-50.",
                "",
                "| Gold title | Dense saved rank | Dense observed position | BM25 saved rank | BM25 observed position |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for gold_title in sorted(gold_titles):
            dense_saved = dense_record["gold_ranks"][gold_title]
            dense_observed = first_saved_rank(dense_record, gold_title)
            bm25_saved = bm25_record["gold_ranks"][gold_title]
            bm25_observed = first_saved_rank(bm25_record, gold_title)
            lines.append(
                f"| {md_escape(gold_title)} | {dense_saved if dense_saved is not None else 'null'} | "
                f"{dense_observed if dense_observed is not None else 'not present'} | "
                f"{bm25_saved if bm25_saved is not None else 'null'} | "
                f"{bm25_observed if bm25_observed is not None else 'not present'} |"
            )

        lines.extend(
            [
                "",
                "### Dense pooled top-10",
                "",
                *render_rank_table(detail["retrievers"]["dense"], gold_titles),
                "",
                f"Saved Dense `gold_ranks`: `{md_escape(detail['retrievers']['dense']['gold_ranks'])}`",
                "",
                "### BM25 pooled top-10",
                "",
                *render_rank_table(detail["retrievers"]["bm25"], gold_titles),
                "",
                f"Saved BM25 `gold_ranks`: `{md_escape(detail['retrievers']['bm25']['gold_ranks'])}`",
                "",
                "### Mechanical consistency checks",
                "",
                "| Check | Result |",
                "|---|:---:|",
            ]
        )
        for name, result in checks:
            lines.append(f"| {md_escape(name)} | {'PASS' if result else 'FAIL'} |")
        lines.extend(["", f"**Mechanical result for this case: {'PASS' if passed else 'FAIL'}**", "", "---", ""])

    lines.extend(
        [
            "## Final team sign-off",
            "",
            f"- [{review_mark}] All 12 examples were manually reviewed.",
            f"- [{review_mark}] Any FAIL cases were documented and resolved or scoped.",
            f"- [{review_mark}] Gold evidence matching spot-check final decision: **PASS**.",
            "",
            f"Reviewer: {args.reviewer or '____________________'}  ",
            f"Date: {args.review_date or '____________________'}",
            "",
        ]
    )
    return "\n".join(lines), all_machine_pass


def main() -> int:
    args = parse_args()
    from datasets import Dataset

    raw_dataset = Dataset.from_file(str(args.validation_arrow))
    raw_rows = [raw_dataset[index] for index in range(min(args.n, len(raw_dataset)))]
    raw_by_id = {
        raw.get("id", raw.get("_id", "")): raw
        for raw in raw_rows
    }
    details = read_jsonl(args.details)
    dense_results = read_pooled_results(args.dense_results)
    bm25_results = read_pooled_results(args.bm25_results)

    if len(details) != args.n:
        raise ValueError(f"Expected {args.n} details rows, found {len(details)}")
    detail_ids = {detail["example_id"] for detail in details}
    if not detail_ids <= raw_by_id.keys():
        missing = sorted(detail_ids - raw_by_id.keys())[:5]
        raise ValueError(f"Details IDs missing from raw data: {missing}")
    if not detail_ids <= dense_results.keys() or not detail_ids <= bm25_results.keys():
        raise ValueError("Formal pooled result CSVs do not cover all details IDs")

    collisions = collision_titles(raw_rows)
    selected = select_cases(details, raw_by_id, collisions)
    document, all_machine_pass = render_document(
        selected,
        raw_by_id,
        dense_results,
        bm25_results,
        collisions,
        args,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(document, encoding="utf-8")

    print(f"Wrote {args.out}")
    print(f"Selected {len(selected)} distinct examples")
    for index, (category, reason, detail) in enumerate(selected, start=1):
        print(f"{index:02d} {category}: {detail['example_id']} ({reason})")
    print(f"Mechanical checks: {'PASS' if all_machine_pass else 'FAIL'}")
    return 0 if all_machine_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
