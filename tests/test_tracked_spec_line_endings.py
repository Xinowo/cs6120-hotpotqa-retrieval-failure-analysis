"""Executable guard for the end-of-line policy on the tracked specifications.

The repository is checked out with `core.autocrlf=true`, so every tracked text
file that no `.gitattributes` rule exempts materializes as CRLF in a fresh clone
even though its committed bytes are LF. For `docs/specs/` that is not cosmetic:
the accepted byte identity of the manual-review course protocol is a SHA-256
over its LF bytes, and a CRLF checkout silently produces a different digest.
The root `.gitattributes` closes that with `docs/specs/** text eol=lf`.

Nothing else in the suite would notice if that rule were deleted or weakened.
The doc-reference scan beside this module asserts what the protocol *says* and
deliberately reads it end-of-line agnostically, so it is green under CRLF by
design; no other test digests a specification. This module is therefore the
regression guard for the rule itself, and it is built so that it fails on
exactly the platforms where the defect is real: on a CRLF checkout the bytes
change and both checks below fire, while on an LF-native checkout — where
removing the rule causes no harm — they stay green. Because a silent removal
should not be invisible even there, the rule's presence is asserted directly too.

The accepted digest is pinned deliberately. It is the byte identity the course
protocol was accepted under, so a change to it is an owner decision: an
intentional edit to the protocol must update `ACCEPTED_PROTOCOL_DIGEST` through
the same review that approves the edit, and this test is meant to be the thing
that stops an unreviewed one. The failure message says so, because a bare digest
mismatch reads like a broken test rather than a changed authority.

Two of the checks need a Git index and two do not, and the split matters outside
a checkout. The submission archive is `git archive` output — the tracked files
and no `.git` — and running the suite from it is supported, so the two checks
that enumerate the tracked set skip themselves there rather than erroring. They
skip rather than fail because "which paths does Git own" is not a question an
archive can answer, not because the invariant stopped mattering. The digest of
the accepted protocol and the presence of the attribute rule are both read
straight off disk, so those two still run and still hold in an unpacked archive.

The two helpers are checked against a legal control and against single-defect
mutations, so a guard that had stopped discriminating could not pass quietly.
The set being guarded is checked the same way: the discovery is exercised
against a throwaway repository holding the two shapes the real `docs/specs/`
does not currently contain — a nested tracked specification and an untracked
top-level draft — because a guard is only as good as the set it enumerates.
"""

import hashlib
import io
import os
import subprocess

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SPEC_DIRECTORY = "docs/specs"
ATTRIBUTES_FILE = ".gitattributes"

# The accepted byte identity of the manual-review course protocol. See the
# module docstring before changing either value.
ACCEPTED_PROTOCOL = "docs/specs/2026-07-27-manual-failure-review-course-protocol.md"
ACCEPTED_PROTOCOL_SIZE = 40102
ACCEPTED_PROTOCOL_DIGEST = \
    "5BB4E045C363BA2C239EF3091824D348EBA66E6571BBA2EF01042AF3D22FBDD2"


def _is_own_repository_root(root):
    """Whether `root` is itself the root of the Git repository that owns it.

    Kept separate from the `git ls-files` failure below, because the two mean
    opposite things. The submission archive is `git archive` output: the tracked
    files and no `.git` at all. Unpacking it and running the suite is a supported
    way to read this project, so "these files are not in an index" is an expected
    state, in which a guard over *tracked* bytes has nothing to enumerate and must
    step aside. Any `git ls-files` failure below still means an index exists but
    could not be read, which is a broken environment and remains an error.

    The question is asked as "is this tree its own repository" rather than "is
    there a repository anywhere above" on purpose. Git searches upwards, so an
    archive unpacked *inside* some unrelated checkout -- a scratch directory under
    another project, say -- answers yes to the weaker question while every path
    here belongs to a different index, and the guard would then enumerate an empty
    set and report it as a missing specification directory. Comparing the reported
    top level against this tree is what distinguishes the two.
    """
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        capture_output=True,
    )
    if completed.returncode != 0:
        return False
    toplevel = completed.stdout.decode("utf-8", "replace").strip()
    if not toplevel:
        return False
    return os.path.realpath(toplevel) == os.path.realpath(str(root))


def _tracked_specifications(root, directory=SPEC_DIRECTORY):
    """Every Git-tracked Markdown file under `directory`, repository-relative.

    Discovered rather than listed: the rule is written on the directory, so a
    specification added later is protected by it and must be checked by this
    guard without anyone remembering to extend a list here.

    Discovery asks Git, not the filesystem, because both words in "tracked
    specification" are load-bearing and a directory glob proves neither.

    *Recursive.* The rule is `docs/specs/** text eol=lf`, which covers
    subdirectories; `git ls-files` is recursive, so a specification filed under
    `docs/specs/<area>/` is checked here exactly as the rule already converts
    it. A non-recursive `docs/specs/*.md` pattern would silently skip it and
    report a green guard over a CRLF specification.

    *Tracked.* The invariant is about bytes Git owns: the attribute rule
    converts nothing that is not in the index, and no recorded digest describes
    an untracked file. A filesystem pattern also sees local authoring drafts,
    which would make this guard reject a file that is outside the contract it
    enforces. `git ls-files` reads the index, which is precisely what makes a
    path tracked rather than untracked.
    """
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--full-name", "-z", "--", directory],
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"could not ask git for the tracked files under {directory}/ in "
            f"{root}: git ls-files exited {completed.returncode}. This guard is "
            f"about tracked bytes, so it needs the index to know what to check; "
            f"stderr was "
            f"{completed.stderr.decode('utf-8', 'replace').strip()!r}"
        )
    entries = completed.stdout.decode("utf-8").split("\0")
    return sorted(path for path in entries if path.endswith(".md"))


INDEX_AVAILABLE = _is_own_repository_root(REPO_ROOT)

NO_INDEX_REASON = (
    "this tree is not its own Git repository, so there is no tracked set to "
    "enumerate; that is the expected state inside an unpacked source archive, "
    "not a broken checkout. The two checks that read bytes straight off disk "
    "still run, so the accepted digest and the attribute rule stay guarded."
)

TRACKED_SPECIFICATIONS = (
    _tracked_specifications(REPO_ROOT) if INDEX_AVAILABLE else []
)


def _read_bytes(relative_path):
    with io.open(os.path.join(REPO_ROOT, relative_path), "rb") as fh:
        return fh.read()


def _line_ending_violations(relative_path, data):
    """Report a CRLF checkout in terms of the rule that should have prevented it."""
    carriage_returns = data.count(b"\r")
    if not carriage_returns:
        return []
    return [
        f"{relative_path} has {carriage_returns} CR byte(s); the tracked "
        f"specifications must check out LF-only. This is what a checkout "
        f"without the '{SPEC_DIRECTORY}/** text eol=lf' rule in "
        f"{ATTRIBUTES_FILE} looks like under core.autocrlf=true, and it "
        f"invalidates every digest recorded over these bytes."
    ]


def _identity_violations(relative_path, data, expected_size, expected_digest):
    """Report a digest change as a changed authority, not as an opaque mismatch."""
    actual_digest = hashlib.sha256(data).hexdigest().upper()
    if actual_digest == expected_digest and len(data) == expected_size:
        return []
    return [
        f"{relative_path} no longer has its accepted byte identity: expected "
        f"{expected_size} bytes / {expected_digest}, found {len(data)} bytes / "
        f"{actual_digest}. If the line endings are LF the content itself "
        f"changed, and an intentional change must update "
        f"ACCEPTED_PROTOCOL_DIGEST in this module through the review that "
        f"approves it."
    ]


# ───────────────────────── the rule holds on real bytes ──────────────────────

@pytest.mark.skipif(not INDEX_AVAILABLE, reason=NO_INDEX_REASON)
def test_the_specification_directory_is_not_empty():
    """A guard over an empty discovery would pass vacuously forever."""
    assert len(TRACKED_SPECIFICATIONS) >= 6, \
        f"expected the tracked specifications under {SPEC_DIRECTORY}/, " \
        f"found {TRACKED_SPECIFICATIONS}"
    assert ACCEPTED_PROTOCOL in TRACKED_SPECIFICATIONS


@pytest.mark.skipif(not INDEX_AVAILABLE, reason=NO_INDEX_REASON)
@pytest.mark.parametrize("specification", TRACKED_SPECIFICATIONS)
def test_every_tracked_specification_checks_out_lf_only(specification):
    """The whole directory is the unit of the rule, so check the whole directory."""
    violations = _line_ending_violations(specification, _read_bytes(specification))
    assert not violations, violations[0]


def test_the_accepted_course_protocol_still_has_its_accepted_byte_identity():
    """The digest the protocol was accepted under, asserted over raw bytes."""
    data = _read_bytes(ACCEPTED_PROTOCOL)
    violations = _identity_violations(
        ACCEPTED_PROTOCOL, data, ACCEPTED_PROTOCOL_SIZE, ACCEPTED_PROTOCOL_DIGEST
    )
    assert not violations, violations[0]


def test_the_attribute_rule_that_makes_this_hold_is_still_present():
    """The only check here that also catches a removal on an LF-native checkout.

    On such a checkout the bytes above are LF whether or not the rule exists, so
    deleting it would be invisible to them while reintroducing the defect for
    everyone on a CRLF platform.
    """
    attributes = _read_bytes(ATTRIBUTES_FILE).decode("utf-8")
    rules = [
        line.split("#", 1)[0].split()
        for line in attributes.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    covering = [
        fields for fields in rules
        if fields and fields[0] == f"{SPEC_DIRECTORY}/**"
    ]
    assert len(covering) == 1, \
        f"{ATTRIBUTES_FILE} must carry exactly one rule for " \
        f"{SPEC_DIRECTORY}/**; found {covering}"
    assert covering[0][1:] == ["text", "eol=lf"], \
        f"the {SPEC_DIRECTORY}/** rule must be 'text eol=lf' so that LF is " \
        f"normalized on the way into the index and restored on checkout; " \
        f"found {covering[0][1:]}. '-text' would instead let a CRLF working " \
        f"copy write CRLF into the index and break the accepted digest."


# ──────────────── the guard still discriminates: control and drift ───────────
#
# These exercise the two helpers against a fixed control document rather than
# against the repository, deliberately. If a checkout ever does deliver CRLF the
# three assertions above are the ones that should fail, and they should fail
# alone: keeping the self-tests independent of the checkout means a real defect
# is reported as "the protocol's bytes are wrong" rather than as a dozen
# simultaneous failures that no longer say which layer broke. The control digest
# is a literal constant, not recomputed from the same bytes it checks, so the
# comparison being asserted is a real one.

CONTROL_DOCUMENT = b"# Control specification\n\nOne line, LF terminated.\n"
CONTROL_SIZE = 50
CONTROL_DIGEST = \
    "33A29F3C277A3B0264F2163C6040C83B67D20C0BA1E3C6B35B0E95DD17A20CB2"


def test_the_guard_accepts_a_legal_control():
    """An LF-only document at its recorded identity must produce no violation."""
    assert _line_ending_violations("control.md", CONTROL_DOCUMENT) == []
    assert _identity_violations(
        "control.md", CONTROL_DOCUMENT, CONTROL_SIZE, CONTROL_DIGEST
    ) == []


def test_the_guard_rejects_a_crlf_reserialization():
    """The defect the rule exists to prevent: same content, CRLF line endings.

    This is exactly what a checkout without the rule produces, and it must fail
    both checks — the line endings are wrong and the recorded digest no longer
    describes the file. The diagnostic has to name the rule, because whoever
    sees this failure is most likely looking at a checkout, not at an edit.
    """
    crlf = CONTROL_DOCUMENT.replace(b"\n", b"\r\n")

    line_endings = _line_ending_violations("control.md", crlf)
    assert len(line_endings) == 1
    assert "3 CR byte(s)" in line_endings[0]
    assert f"{SPEC_DIRECTORY}/** text eol=lf" in line_endings[0]
    assert ATTRIBUTES_FILE in line_endings[0]

    identity = _identity_violations(
        "control.md", crlf, CONTROL_SIZE, CONTROL_DIGEST
    )
    assert len(identity) == 1
    assert CONTROL_DIGEST in identity[0]


def test_the_guard_rejects_a_digest_drift_that_is_still_lf_only():
    """The two checks are independent, not one check reported twice.

    Content drift with correct line endings must be caught by the identity check
    alone — otherwise the digest assertion would be doing nothing beyond
    counting CR bytes, and an edited specification would pass.
    """
    drifted = CONTROL_DOCUMENT + b"one appended line\n"

    assert _line_ending_violations("control.md", drifted) == []

    identity = _identity_violations(
        "control.md", drifted, CONTROL_SIZE, CONTROL_DIGEST
    )
    assert len(identity) == 1
    assert "no longer has its accepted byte identity" in identity[0]
    assert "ACCEPTED_PROTOCOL_DIGEST" in identity[0]


def test_the_guard_rejects_a_single_flipped_byte():
    """Same length, LF-only, one byte different: only the digest can catch it."""
    flipped = CONTROL_DOCUMENT.replace(b"One line", b"Two line")
    assert len(flipped) == CONTROL_SIZE
    assert _line_ending_violations("control.md", flipped) == []
    assert len(_identity_violations(
        "control.md", flipped, CONTROL_SIZE, CONTROL_DIGEST
    )) == 1


def test_the_guard_rejects_a_size_only_disagreement():
    """A recorded size that disagrees with the bytes is also a stale record.

    Size and digest are asserted together, so a guard that compared only the
    digest could keep passing beside a size that had stopped being true.
    """
    identity = _identity_violations(
        "control.md", CONTROL_DOCUMENT, CONTROL_SIZE + 1, CONTROL_DIGEST
    )
    assert len(identity) == 1
    assert str(CONTROL_SIZE + 1) in identity[0]


# ────────────── the guard enumerates the set it claims to enumerate ──────────
#
# The three assertions over real bytes are only worth their diagnostics if the
# parameter list is the tracked, recursive set the attribute rule covers. The
# real `docs/specs/` cannot demonstrate either property: it happens to be flat
# and happens to have no untracked draft in it right now, so a discovery that
# was neither recursive nor tracked-only would look identical to one that was.
# These two exercise the discovery against a throwaway repository built to hold
# exactly the two shapes that tell them apart — one regression and one legal
# control, each turning a single property on and nothing else.


@pytest.fixture
def repository_with_both_shapes(tmp_path):
    """A scratch repository: a nested *tracked* spec and an untracked draft.

    `git add` without a commit is deliberate and sufficient. The index is what
    makes a path tracked — it is exactly what `git ls-files` reports and what
    `git status` calls a file untracked for lacking — so staging establishes the
    property under test without needing a committer identity, signing key, or
    hook environment inside a temporary directory.
    """
    root = tmp_path / "r"
    specs = root / SPEC_DIRECTORY
    (specs / "nested").mkdir(parents=True)

    for path, data in (
        (specs / "top.md", b"# top-level specification\n"),
        (specs / "nested" / "child.md", b"# nested specification\r\n"),
        (specs / "local_draft.md", b"# an untracked authoring draft\r\n"),
    ):
        with io.open(str(path), "wb") as fh:
            fh.write(data)

    for arguments in (
        ["init", "--quiet"],
        # Everything except the draft, which stays untracked on purpose.
        ["add", "--", f"{SPEC_DIRECTORY}/top.md", f"{SPEC_DIRECTORY}/nested/child.md"],
    ):
        completed = subprocess.run(
            ["git", "-C", str(root)] + arguments, capture_output=True
        )
        assert completed.returncode == 0, \
            f"scratch git {arguments[0]} failed: " \
            f"{completed.stderr.decode('utf-8', 'replace')}"
    return root


def test_a_nested_tracked_specification_is_discovered_and_checked(
    repository_with_both_shapes
):
    """The regression for the recursive half of `docs/specs/**`.

    A specification one directory down is converted by the rule, so a CRLF copy
    of it is the same defect as a CRLF copy of the canonical. It must reach the
    parameter list, and the line-ending check must then report it — a discovery
    that found it but a helper that ignored it would be no better.
    """
    relative = f"{SPEC_DIRECTORY}/nested/child.md"
    assert relative in _tracked_specifications(repository_with_both_shapes)

    nested = repository_with_both_shapes / SPEC_DIRECTORY / "nested" / "child.md"
    with io.open(str(nested), "rb") as fh:
        violations = _line_ending_violations(relative, fh.read())
    assert len(violations) == 1
    assert "1 CR byte(s)" in violations[0]


def test_an_untracked_top_level_draft_does_not_enter_the_invariant(
    repository_with_both_shapes
):
    """The legal control for the tracked half, in the same repository.

    A CRLF file that Git does not own is outside this contract entirely: no
    attribute rule converts it and no recorded digest describes it. It must not
    appear, and its presence must not disturb the tracked set — which stays
    exactly the two staged specifications, so this is a control rather than a
    second copy of the assertion above.
    """
    discovered = _tracked_specifications(repository_with_both_shapes)
    assert discovered == [
        f"{SPEC_DIRECTORY}/nested/child.md",
        f"{SPEC_DIRECTORY}/top.md",
    ]

    draft = repository_with_both_shapes / SPEC_DIRECTORY / "local_draft.md"
    assert draft.exists(), "the control is only meaningful if the draft is there"
