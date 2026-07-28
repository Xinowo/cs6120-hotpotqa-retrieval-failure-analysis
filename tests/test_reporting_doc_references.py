"""Provenance scan for the Week 3 reporting artifacts.

A citation in a registered implementation file is a promise that the cited
document exists and says what the citing file claims. That promise is not
checked by any behavioral test — a tool with a dead authority reference behaves
exactly like a tool with a live one — so it can rot silently while every other
suite stays green. This module makes it executable.

Three properties are asserted over the DR-004 reporting sources:

1. every repository-relative path they cite resolves to a real file;
2. none of them cites the local, untracked review workspace or a review-local
   finding identifier, which would be a dangling reference for anyone who has
   only the repository;
3. the shortlist tool cites the *current* notes-first boundary — the course
   protocol's "Stable boundaries" section — rather than a predecessor path or a
   section number that has since been reused for something else.

The scan is deliberately scoped to the DR-004 sources. Historical completion
logs and handoff notes legitimately record paths that existed at the time, and
rewriting those would destroy the record they exist to keep.
"""

import io
import os
import re

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# The DR-004 sources: the three reporting tools, their shared input contract,
# their regression suites, and the two specifications that govern them.
SCANNED_FILES = [
    "scripts/reporting/formal_result_inputs.py",
    "scripts/reporting/disagreement_cases.py",
    "scripts/reporting/bm25_failure_shortlist.py",
    "scripts/reporting/rescue_damage.py",
    "tests/test_formal_result_inputs.py",
    "tests/test_disagreement_cases.py",
    "tests/test_bm25_failure_shortlist.py",
    "tests/test_rescue_damage.py",
    "docs/specs/2026-07-27-bm25-dense-reporting-contracts.md",
    "docs/specs/2026-07-26-reranker-rescue-damage.md",
]
# This module is deliberately not in that list: it has to spell the retired path
# and the forbidden patterns literally in order to look for them, so scanning
# itself would report its own subject matter as a violation.

# A repository-relative path as these files spell one.
_PATH_PATTERN = re.compile(
    r"\b(?:docs|src|scripts|tests)/[A-Za-z0-9_./@-]*"
    r"\.(?:md|py|csv|json|html)\b"
)

# Identifiers that only exist inside the local, untracked review workspace.
_REVIEW_LOCAL_PATTERNS = [
    (re.compile(r"\bR\d+-F\d+\b"), "review-local finding identifier"),
    (re.compile(r"\.claude/"), "path into the untracked local design-record workspace"),
]

CURRENT_COURSE_PROTOCOL = "docs/specs/2026-07-27-manual-failure-review-course-protocol.md"
RETIRED_MANUAL_PROTOCOL = "docs/specs/2026-07-27-manual-failure-review-protocol.md"


def _read(relative_path):
    with io.open(os.path.join(REPO_ROOT, relative_path),
                 encoding="utf-8", newline="") as fh:
        return fh.read()


def _cited_paths(text):
    """Every repository-relative document/code path the text names, deduplicated."""
    return sorted({match.group(0) for match in _PATH_PATTERN.finditer(text)})


# ─────────────────────── every cited path must resolve ───────────────────────

@pytest.mark.parametrize("source", SCANNED_FILES)
def test_every_cited_repository_path_exists(source):
    """The scan that would have caught the dead protocol citation."""
    missing = [
        path for path in _cited_paths(_read(source))
        if not os.path.exists(os.path.join(REPO_ROOT, path))
    ]
    assert not missing, f"{source} cites path(s) that do not exist: {missing}"


def test_the_scan_actually_finds_paths_to_check():
    """A scan that matched nothing would pass vacuously forever."""
    found = {source: _cited_paths(_read(source)) for source in SCANNED_FILES}
    assert all(found.values()), \
        f"no path cited in: {[s for s, p in found.items() if not p]}"
    assert sum(len(paths) for paths in found.values()) >= 20


def test_the_retired_manual_protocol_path_is_gone_from_the_repository():
    """Its replacement exists; the predecessor path must not be cited again."""
    assert os.path.exists(os.path.join(REPO_ROOT, CURRENT_COURSE_PROTOCOL))
    assert not os.path.exists(os.path.join(REPO_ROOT, RETIRED_MANUAL_PROTOCOL))
    for source in SCANNED_FILES:
        assert RETIRED_MANUAL_PROTOCOL not in _read(source), source


# ─────────────── no dangling reference into the local workspace ──────────────

@pytest.mark.parametrize("source", SCANNED_FILES)
def test_no_reference_to_a_review_local_identifier(source):
    """A tracked file must be readable by someone who has only the repository."""
    text = _read(source)
    for pattern, description in _REVIEW_LOCAL_PATTERNS:
        hits = sorted(set(pattern.findall(text)))
        assert not hits, f"{source} contains a {description}: {hits}"


# ───────────── the shortlist boundary citation names the live section ─────────

def test_shortlist_cites_the_current_course_protocol_boundary_section():
    """The neutral-signal boundary must point at the section that states it."""
    docstring = _read("scripts/reporting/bm25_failure_shortlist.py").split('"""')[1]
    assert CURRENT_COURSE_PROTOCOL in docstring
    assert re.search(
        re.escape(CURRENT_COURSE_PROTOCOL) + r"\s+§2", docstring
    ), "the notes-first boundary is §2 of the course protocol"


def test_the_cited_course_protocol_section_still_states_that_boundary():
    """Cite-and-verify: §2 must actually contain the no-prefilled-label rule.

    A path that resolves and a section number that exists are not enough — the
    citation is only sound if the named section still says what the tool claims
    it says, so the rule text itself is asserted here.
    """
    protocol = _read(CURRENT_COURSE_PROTOCOL)
    section_2 = protocol.split("\n## 2. Stable boundaries\n")[1].split("\n## ")[0]
    assert "no system or agent pre-fills a causal label" in section_2


def test_the_accepted_failure_review_boundary_citation_is_still_live():
    """The second, already-accepted authority beside it must also resolve."""
    docstring = _read("scripts/reporting/bm25_failure_shortlist.py").split('"""')[1]
    cited = "docs/specs/2026-07-12-failure-review-pipeline-design.md"
    assert cited in docstring
    assert os.path.exists(os.path.join(REPO_ROOT, cited))
