"""
rerank_rescue_damage_cases.py  ->  scripts/reporting/rerank_rescue_damage_cases.py

Per-example reranker rescue / damage cases.

Spec:    docs/specs/2026-08-12-rerank-rescue-damage-cases.md
Inputs:  results/dense_results.csv (stage 1), results/rerank_results.csv (stage 2)
Output:  results/rerank_rescue_damage_cases.csv  (12 columns, one row per
         (setting, example_id, k) under the Full Evidence criterion)

The accepted aggregate `results/rerank_rescue_damage.csv` says how many
questions the reranker rescued and broke. This says *which* ones, and what the
gold paragraphs' observed ranks were on either side of the transition, so a
failure reading no longer has to be reassembled by hand from the two result
files.

It is a downstream artifact and deliberately a narrow one:

  - it reuses the upstream §2 input contract verbatim — the same reader, the
    same per-file and cross-file checks, and the same one-to-one join — through
    `rescue_damage.load_and_validate_inputs()` / `build_paired_frame()`. A second
    loader would be a second input language;
  - it reuses the hand-written rank and hit semantics in `src/evaluator.py`
    (`gold_ranks`, `full_evidence_recall_at_k`) rather than restating them;
  - it changes nothing in `results/rerank_rescue_damage.csv` or its frozen
    contract (docs/specs/2026-07-26-reranker-rescue-damage.md), and it must
    aggregate back to that file's Full Evidence rows exactly.

Two independent paths decide each hit, and both must agree before anything is
written: the value recomputed from the stored ranked list, and the
`full_evidence_recall@k` value saved in the input. The persisted file is then
validated a third time, from its own bytes, where the serialized ranks must
imply the binary column they sit beside. A disagreement means the stored ranked
list and the stored metric describe different runs; it is a fail-fast, never a
silent preference for one of the two.

AI-USAGE BOUNDARY: this module is plumbing. It defines no metric and makes no
failure-category judgment. The metric definitions stay hand-written in
`src/evaluator.py`; the four-cell transition table is the accepted aggregate
spec's, restated per example; the reading of any individual case is written
separately by the analysis owner.

Usage:
    python scripts/reporting/rerank_rescue_damage_cases.py
    python scripts/reporting/rerank_rescue_damage_cases.py \
        --dense results/dense_results.csv \
        --rerank results/rerank_results.csv \
        --out results/rerank_rescue_damage_cases.csv
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd

from src.evaluator import full_evidence_recall_at_k, gold_ranks
from src.results_schema import TITLE_SEPARATOR
from scripts.reporting.formal_result_inputs import is_binary_cell, validate_setting
from scripts.reporting.rescue_damage import build_paired_frame, load_and_validate_inputs


# ── Frozen output contract (spec §5) — schema constants, not logic ───────────

OUTPUT_COLUMNS = [
    "setting", "example_id", "question_type", "level", "question", "gold_titles",
    "k",
    "dense_full_at_k", "rerank_full_at_k",
    "dense_gold_ranks", "rerank_gold_ranks",
    "transition",
]

# Full Evidence only. The Any diagnostic is deliberately absent: the aggregate
# spec §4 forbids merging or confusing Any and Full rescue/damage events, and a
# row carrying both criteria invites exactly that.
CRITERION = "full_evidence_recall"

# The valid cutoffs per setting (spec §3 = aggregate spec §5, Full rows).
# per_question @10 is not computed by the schema's K policy, so it is refused
# rather than read from the blank cell the contract requires there.
VALID_KS_BY_SETTING = {
    "pooled": (2, 5, 10),
    "per_question": (2, 5),
}

# 500 examples × (3 pooled cutoffs + 2 per-question cutoffs). The upstream §2
# contract freezes the 500, so this is a derived constant, not a new rule.
EXPECTED_ROWS = 2500

STAGES = ("dense", "rerank")

# The four-cell transition table (spec §4).
TRANSITIONS = {
    (0, 0): "stable_miss",
    (0, 1): "rescue",
    (1, 0): "damage",
    (1, 1): "stable_hit",
}
TRANSITION_CLASSES = ("stable_miss", "rescue", "damage", "stable_hit")

# Deterministic sort keys (spec §5.4).
_SETTING_ORDER = {"pooled": 0, "per_question": 1}

_TEXT_COLUMNS = ["example_id", "question_type", "level", "question", "gold_titles"]
_BINARY_COLUMNS = ["dense_full_at_k", "rerank_full_at_k"]
_RANK_COLUMNS = {"dense": "dense_gold_ranks", "rerank": "rerank_gold_ranks"}


# ─────────────────────────── §3  valid combinations ──────────────────────────

def valid_ks(setting):
    """The cutoffs this artifact computes for `setting` (spec §3)."""
    validate_setting(setting)
    return VALID_KS_BY_SETTING[setting]


def full_column(setting, k):
    """The input column a `(setting, k)` row is read from, or a refusal.

    The refusal is the point: `per_question` at `k = 10` is not a cutoff of this
    artifact, the schema leaves that cell physically blank, and a tool that
    silently read it would publish a fabricated outcome for 500 examples.
    """
    if k not in valid_ks(setting):
        raise ValueError(
            f"Unsupported (setting, k) combination ({setting!r}, {k!r}); this "
            f"artifact computes exactly {sorted(valid_ks(setting))} for "
            f"{setting!r} (spec §3). per_question @10 is not computed by the "
            f"schema's K policy and its cell is required to be blank, so it is "
            f"refused rather than read."
        )
    return f"{CRITERION}@{k}"


def combination_rows(setting, example_ids):
    """Every `(setting, example_id, k)` key of one setting, in spec §5.4 order."""
    return [
        (setting, example_id, k)
        for example_id in sorted(example_ids)
        for k in sorted(valid_ks(setting))
    ]


# ──────────────────────────── §2  title extraction ───────────────────────────

def split_gold_titles(cell, source):
    """The row's gold titles, in stored order, under the exact-title convention.

    A duplicate title is refused rather than collapsed: it cannot survive as a
    JSON object key, so collapsing it would silently drop a gold requirement
    from the record. An empty component is refused for the same reason — it is a
    malformed cell, not a title.
    """
    if not isinstance(cell, str) or cell == "":
        raise ValueError(
            f"{source}: gold_titles must be a non-empty string, got {cell!r}."
        )
    titles = cell.split(TITLE_SEPARATOR)
    empty = [position for position, title in enumerate(titles) if title == ""]
    if empty:
        raise ValueError(
            f"{source}: gold_titles {cell!r} has an empty title at position(s) "
            f"{empty}; the separator {TITLE_SEPARATOR!r} must join non-empty "
            f"titles."
        )
    if len(set(titles)) != len(titles):
        duplicates = sorted({t for t in titles if titles.count(t) > 1})
        raise ValueError(
            f"{source}: gold_titles {cell!r} repeats {duplicates}; a duplicate "
            f"gold title cannot survive as a JSON object key, so it is refused "
            f"rather than silently collapsed."
        )
    return titles


def split_retrieved_titles(cell, source):
    """The stage's stored ranked list. An empty cell is the approved empty list."""
    if not isinstance(cell, str):
        raise ValueError(
            f"{source}: retrieved_titles must be a string (an empty one is the "
            f"approved empty retrieved list), got {cell!r}."
        )
    return cell.split(TITLE_SEPARATOR) if cell else []


# ─────────────────────────── §5.3  the gold-rank map ─────────────────────────

def ordered_gold_ranks(retrieved_titles, gold_title_list):
    """`{gold title: 1-based first rank or None}`, keyed in stored gold order.

    The rank semantics are `src.evaluator.gold_ranks` — this only fixes the key
    order, which a set cannot carry, so that serialization is byte-stable.
    """
    ranks = gold_ranks(retrieved_titles, set(gold_title_list))
    return {title: ranks[title] for title in gold_title_list}


def encode_gold_ranks(mapping):
    """Serialize a rank map compactly and stably (spec §5.3).

    Insertion order is preserved (no sorting), separators carry no whitespace,
    and non-ASCII titles are written as themselves, so a rerun on the same
    inputs produces the same bytes.
    """
    return json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))


def decode_gold_ranks(cell, source):
    """Parse a serialized rank map back into `{title: int or None}`.

    Used by the validators, which is why it refuses rather than repairs: a rank
    that is not a positive integer, a non-object payload, and a non-string key
    are all defects the writer must never be able to publish.

    The *spelling* is checked too, not only the meaning. §5.3 freezes the
    physical serialization, so a cell must be byte-identical to
    `encode_gold_ranks()` of the mapping it decodes to. Semantic JSON
    equivalence is weaker than that contract: a whitespace-bearing or
    ASCII-escaped cell carries the same mapping, and accepting it would let the
    writer publish a spelling a rerun does not reproduce.
    """
    try:
        mapping = json.loads(cell)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{source}: gold-rank cell {cell!r} is not valid JSON ({exc})."
        ) from exc
    if not isinstance(mapping, dict):
        raise ValueError(
            f"{source}: gold-rank cell {cell!r} must be a JSON object mapping "
            f"each gold title to a rank or null, got {type(mapping).__name__}."
        )
    for title, rank in mapping.items():
        if not isinstance(title, str) or title == "":
            raise ValueError(
                f"{source}: gold-rank cell {cell!r} has a non-title key {title!r}."
            )
        if rank is None:
            continue
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            raise ValueError(
                f"{source}: gold-rank cell {cell!r} maps {title!r} to {rank!r}; "
                f"a rank is null (not retrieved) or a 1-based positive integer. "
                f"An absent gold is never inferred as 0, as storage_depth + 1, "
                f"or as any concrete rank beyond the stored retrieval depth."
            )

    canonical = encode_gold_ranks(mapping)
    if cell != canonical:
        raise ValueError(
            f"{source}: gold-rank cell {cell!r} carries a legal mapping but not "
            f"the frozen serialization of it; the canonical spelling is "
            f"{canonical!r} (§5.3: compact ','/':' separators, no whitespace, "
            f"no re-sorting, ensure_ascii=False). An equivalent spelling is "
            f"refused rather than published unchanged, because the contract is "
            f"on the persisted bytes and a rerun reproduces only this one."
        )
    return mapping


def full_at_k_from_ranks(mapping, k):
    """Full@k implied by a rank map: every gold retrieved at a rank ≤ k.

    The same identity `src.evaluator.full_evidence_recall_at_k` applies to the
    ranks it derives itself; here it is applied to the ranks the file actually
    carries, which is what makes the round-trip check independent of the frame
    the writer held in memory.
    """
    if not mapping:
        raise ValueError("a gold-rank map must hold at least one gold title.")
    return int(all(rank is not None and rank <= k for rank in mapping.values()))


def classify(dense_hit, rerank_hit):
    """The §4 transition cell of a paired outcome."""
    key = (int(dense_hit), int(rerank_hit))
    if key not in TRANSITIONS:
        raise ValueError(f"Illegal hit pair {key}; both values must be 0 or 1.")
    return TRANSITIONS[key]


# ───────────────────────────── build the case rows ───────────────────────────

def _consumed_hit(value, column, stage, source):
    """One stage's saved metric cell, refused unless it is a plain integer 0/1."""
    if not is_binary_cell(value):
        raise ValueError(
            f"{source}: {stage} cell {column} is {value!r}; a consumed binary "
            f"criterion must be the plain integer 0 or 1 (a bool, a float, a "
            f"numeric string, and an empty cell are refused even when they "
            f"compare equal to 0/1)."
        )
    return int(value)


def build_cases(paired):
    """One row per `(setting, example_id, k)` from the joined stages.

    `paired` is `rescue_damage.build_paired_frame()`'s output, so the whole
    upstream §2 contract has already been enforced on both inputs and on the
    join. What is added here is per-row and specific to this artifact: the gold
    and retrieved lists are split under the exact-title convention, the gold
    ranks are extracted from each stage's stored ranked list, and each stage's
    Full@k is recomputed from that list and required to equal the value saved in
    the input file before it may be written.
    """
    rows = []
    for _, row in paired.iterrows():
        setting = row["setting"]
        validate_setting(setting)
        source = f"{setting}/{row['example_id']}"

        gold = split_gold_titles(row["gold_titles"], source)
        gold_set = set(gold)
        retrieved = {
            stage: split_retrieved_titles(row[f"retrieved_titles_{stage}"], source)
            for stage in STAGES
        }
        ranks = {
            stage: ordered_gold_ranks(retrieved[stage], gold) for stage in STAGES
        }

        for k in valid_ks(setting):
            column = full_column(setting, k)
            hits = {}
            for stage in STAGES:
                saved = _consumed_hit(
                    row[f"{column}_{stage}"], column, stage, source
                )
                recomputed = int(
                    full_evidence_recall_at_k(retrieved[stage], gold_set, k)
                )
                if recomputed != saved:
                    raise ValueError(
                        f"{source}: {stage} {column} is {saved} in the input "
                        f"file but the stored retrieved_titles imply "
                        f"{recomputed} (gold ranks {ranks[stage]!r}). The "
                        f"ranked list and the metric describe different runs; "
                        f"neither is preferred silently."
                    )
                hits[stage] = saved

            rows.append({
                "setting": setting,
                "example_id": row["example_id"],
                "question_type": row["question_type"],
                "level": row["level"],
                "question": row["question"],
                "gold_titles": row["gold_titles"],
                "k": k,
                "dense_full_at_k": hits["dense"],
                "rerank_full_at_k": hits["rerank"],
                "dense_gold_ranks": encode_gold_ranks(ranks["dense"]),
                "rerank_gold_ranks": encode_gold_ranks(ranks["rerank"]),
                "transition": classify(hits["dense"], hits["rerank"]),
            })

    return sort_cases(pd.DataFrame(rows, columns=OUTPUT_COLUMNS))


def sort_cases(cases):
    """Spec §5.4 order: pooled before per_question, then example_id, then k."""
    ordered = cases.assign(_s=cases.setting.map(_SETTING_ORDER)).sort_values(
        ["_s", "example_id", "k"], kind="mergesort"
    )
    return ordered.drop(columns=["_s"]).reset_index(drop=True)


# ─────────────────────────────── §5  output checks ───────────────────────────

def _is_plain_int(value):
    """True only for a genuine integer scalar (excludes bool, float, string)."""
    return isinstance(value, (int, np.integer)) and not isinstance(value, bool)


def validate_cases_schema(cases, source="cases"):
    """§5.1/§5.4: exact columns, the exact key set, and the exact row order."""
    if list(cases.columns) != OUTPUT_COLUMNS:
        raise ValueError(
            f"{source}: output columns must be exactly OUTPUT_COLUMNS in order; "
            f"got {list(cases.columns)}."
        )

    keys = list(zip(cases.setting, cases.example_id, cases.k))
    if len(set(keys)) != len(keys):
        duplicates = sorted({key for key in keys if keys.count(key) > 1})[:3]
        raise ValueError(
            f"{source}: (setting, example_id, k) must be unique; duplicate "
            f"key(s) e.g. {duplicates}."
        )

    for setting, _, k in keys:
        full_column(setting, k)  # refuses per_question @10 and any other combo

    expected = []
    for setting in ("pooled", "per_question"):
        ids = {eid for s, eid, _ in keys if s == setting}
        expected.extend(combination_rows(setting, ids))
    if keys != expected:
        raise ValueError(
            f"{source}: rows are not the complete key set in the §5.4 order. "
            f"Expected {len(expected)} row(s) starting {expected[:2]}, got "
            f"{len(keys)} starting {keys[:2]}."
        )

    if len(cases) != EXPECTED_ROWS:
        raise ValueError(
            f"{source}: expected exactly {EXPECTED_ROWS} rows (500 examples × "
            f"3 pooled + 2 per-question cutoffs, §5.4), got {len(cases)}."
        )


def validate_cases_values(cases, source="cases"):
    """§5.2/§5.3/§5.5: types, vocabularies, and the two per-row identities."""
    for column in _TEXT_COLUMNS:
        invalid = [v for v in cases[column].tolist()
                   if not isinstance(v, str) or v == ""]
        if invalid:
            raise ValueError(
                f"{source}: {column} must be a non-empty string in every row; "
                f"found {len(invalid)} invalid value(s), e.g. {invalid[:3]}."
            )

    for column in ["k"] + _BINARY_COLUMNS:
        invalid = [v for v in cases[column].tolist() if not _is_plain_int(v)]
        if invalid:
            raise ValueError(
                f"{source}: {column} must be a plain integer in every row (a "
                f"bool, a float, and a numeric string are refused even when "
                f"they compare equal); found {len(invalid)} non-integer "
                f"value(s), e.g. {invalid[:3]}."
            )

    for column in _BINARY_COLUMNS:
        invalid = [v for v in cases[column].tolist() if not is_binary_cell(v)]
        if invalid:
            raise ValueError(
                f"{source}: {column} must be the plain integer 0 or 1; found "
                f"{len(invalid)} invalid value(s), e.g. {invalid[:3]}."
            )

    for row in cases.itertuples(index=False):
        tag = f"{source} ({row.setting}, {row.example_id}, k={row.k})"
        gold = split_gold_titles(row.gold_titles, tag)
        hits = {"dense": int(row.dense_full_at_k), "rerank": int(row.rerank_full_at_k)}

        for stage in STAGES:
            mapping = decode_gold_ranks(getattr(row, _RANK_COLUMNS[stage]), tag)
            if list(mapping) != gold:
                raise ValueError(
                    f"{tag}: {_RANK_COLUMNS[stage]} keys {list(mapping)} are not "
                    f"the row's gold titles {gold} in stored order; the object "
                    f"holds every gold title, never a filtered subset."
                )
            implied = full_at_k_from_ranks(mapping, int(row.k))
            if implied != hits[stage]:
                raise ValueError(
                    f"{tag}: {_RANK_COLUMNS[stage]} implies Full@{row.k} = "
                    f"{implied} but the row records {hits[stage]} (§5.5)."
                )

        if row.transition not in TRANSITION_CLASSES:
            raise ValueError(
                f"{tag}: transition {row.transition!r} is outside "
                f"{list(TRANSITION_CLASSES)}."
            )
        expected = classify(hits["dense"], hits["rerank"])
        if row.transition != expected:
            raise ValueError(
                f"{tag}: transition {row.transition!r} contradicts "
                f"(dense={hits['dense']}, rerank={hits['rerank']}), which is "
                f"{expected!r} (§4)."
            )


def validate_cases(cases, source="cases"):
    """The complete output contract for an in-memory frame."""
    validate_cases_schema(cases, source)
    validate_cases_values(cases, source)


def read_cases_csv(path):
    """Read a persisted cases file back into the frame the validators expect.

    The file is read as raw text — no numeric parsing, no NA-token inference —
    so `question` / `gold_titles` values such as `NA` or `None` survive as the
    strings they are, and the integer columns are converted only after their
    physical lexemes have been checked. That is what makes the round-trip guard
    a statement about the persisted bytes rather than about pandas' parsing.
    """
    raw = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False)
    if list(raw.columns) != OUTPUT_COLUMNS:
        raise ValueError(
            f"{path}: output columns must be exactly OUTPUT_COLUMNS in order; "
            f"got {list(raw.columns)}."
        )
    frame = raw.copy()
    for column, legal in (("k", ("2", "5", "10")),
                          ("dense_full_at_k", ("0", "1")),
                          ("rerank_full_at_k", ("0", "1"))):
        tokens = raw[column].tolist()
        bad = [f"row {position}: {token!r}"
               for position, token in enumerate(tokens) if token not in legal]
        if bad:
            raise ValueError(
                f"{path}: {column} must be written as one of {list(legal)}; "
                f"e.g. {bad[:3]}. The lexeme is checked before conversion, so a "
                f"float or padded spelling cannot be rounded into legality."
            )
        frame[column] = [int(token) for token in tokens]
    return frame


# ────────────────────────────────── writer ───────────────────────────────────

def write_cases_csv(cases, out_path):
    """Serialize the frozen schema, validating before and after persistence.

    The frame is validated *as handed over* — its physical column list and its
    physical row order included — then written to a temporary file, re-read from
    its own bytes and validated again, and only then atomically moved onto the
    destination. A refusal at any step therefore never creates and never
    overwrites `out_path`.

    Nothing is projected, reordered, or sorted before that first check, and that
    is the point rather than an omission. §5.1/§5.4 say an extra or reordered
    column and any row order other than §5.4's is non-compliant, and §5.5 says
    the writer never coerces. A writer that quietly repaired those would answer
    a required refusal with a compliant-looking artifact. Deterministic ordering
    belongs to construction (`build_cases()` -> `sort_cases()`), where it is
    derived from the inputs, not to the write boundary, where it would be
    laundering a caller's malformed frame. The only normalization left here is
    dropping a non-default row index, which is not part of the output contract.
    """
    validate_cases(cases, out_path)
    ordered = cases.reset_index(drop=True)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    tmp_path = out_path + ".tmp"
    ordered.to_csv(tmp_path, index=False)
    try:
        written = read_cases_csv(tmp_path)
        validate_cases(written, tmp_path)
        if not written.equals(ordered):
            raise ValueError(
                f"{tmp_path}: the persisted rows differ from the validated "
                f"frame; serialization is not round-trippable."
            )
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    os.replace(tmp_path, out_path)


def main(dense_path, rerank_path, out_path):
    dense, rerank = load_and_validate_inputs(dense_path, rerank_path)
    print(
        f"Inputs pass the upstream input contract: {len(dense)} dense + "
        f"{len(rerank)} rerank rows."
    )

    paired = build_paired_frame(dense, rerank)
    cases = build_cases(paired)
    validate_cases(cases, out_path)
    counts = cases.transition.value_counts()
    print(
        "Cases: " + ", ".join(
            f"{name}={int(counts.get(name, 0))}" for name in TRANSITION_CLASSES
        ) + f" (total {len(cases)})"
    )

    write_cases_csv(cases, out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Per-example reranker rescue/damage cases (spec 2026-08-12)."
    )
    p.add_argument("--dense", default="results/dense_results.csv")
    p.add_argument("--rerank", default="results/rerank_results.csv")
    p.add_argument("--out", default="results/rerank_rescue_damage_cases.csv")
    args = p.parse_args()
    main(args.dense, args.rerank, args.out)
