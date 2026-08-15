---
status: active
last_updated: 2026-08-14
---

# Submission Inventory

The complete list of what is submitted for the CS6120 final project, where each
item actually lives, and what must be checked before upload. It is an index, not
a claim of completeness: items that do not exist yet are listed as missing rather
than omitted.

- Course: CS6120, final project, due 2026-08-14
- Team: Xin Wang, Jiajun (two members)
- Repository baseline for this inventory: `9bff6cd` on `main`, in sync with
  `origin/main`
- Governing schedule: `docs/Plans/CS6120_Final_Project_Weekly_Todo_Plan.md`,
  "Week 5 Exit Criteria" and "Final Submission Checklist"

## 1. Submission shape

Three things leave this project:

| # | What | Where it goes | Who |
|---|---|---|---|
| 1 | The final report, as a rendered file | Canvas upload | Jiajun uploads after both approve |
| 2 | The repository, as a link inside the report | the report's own text | — |
| 3 | A frozen archive of the repository at the submitted commit | Canvas upload alongside the report | Jiajun |

Item 3 is a snapshot, not a bag of leftovers. Everything a reader needs is
already tracked in Git, so the archive's job is to freeze the exact bytes the
report's link pointed at — a link can be edited after the deadline, an uploaded
archive cannot. Build it with `git archive`, which by construction contains
exactly the tracked files and nothing else:

```bash
git archive --format=zip --prefix=hotpotqa-retrieval/ -o cs6120_final_submission.zip <commit>
```

Do not assemble the archive by copying the working directory. See §6 for what
that would leak. Measured at `9bff6cd`: the archive holds **112 files and 4.0 MB**,
and none of the §6 exclusions appear in it.

## 2. Report

| Item | Path | State |
|---|---|---|
| Final report | `docs/Local/CS6120NLP_Final_Report_draft.pdf` | **draft**, local-only, password-protected, last written 2026-08-14 |

`docs/Local/` is excluded by `.gitignore`, deliberately: the report is a Canvas
deliverable, not a repository artifact, and this directory also holds personal
working notes that must not be published. The report is therefore **not** part of
the archive in §1 unless the owners decide otherwise.

Owner actions still required:

- Replace the draft with the final rendered file and record its final name here.
- Confirm the repository link inside the report resolves and names the same
  commit the archive was cut from.

## 3. Code

All tracked. 112 files total; the breakdown below covers all of them.

### 3.1 Entry points at the repository root

| Path | What it is |
|---|---|
| `README.md` | setup, demo, the three formal experiment commands, project structure, document map |
| `requirements.txt` | the runtime dependencies. Tested on Python 3.9.7 and 3.11.5; the earlier "3.10+" claim here was wrong, since the project virtual environment is 3.9.7. |
| `demo.py` | the offline walkthrough, spec `docs/specs/2026-08-14-offline-demo.md` |
| `LICENSE` | — |
| `.gitignore`, `.gitattributes` | exclusion rules and the LF locks on checksum-bearing artifacts |

### 3.2 Library — `src/` (10 files)

`__init__.py`, `data_loader.py`, `retrievers.py`, `dense_retriever.py`,
`embedding_cache.py`, `cross_encoder_reranker.py`, `evaluator.py`,
`results_schema.py`, `rank_pattern.py`, `top50_export.py`.

`evaluator.py` holds the hand-written metric definitions; the AI Usage
Declaration §4 records that boundary function by function.

### 3.3 Runners and reporting tools — `scripts/` (22 files)

- Experiment runners: `run_bm25_experiment.py`, `run_dense_experiment.py`,
  `run_rerank_experiment.py`, `run_failure_review.py`
- Review builders: `build_failure_report.py`, `build_manual_review_batch.py`,
  `manual_review_page.py`
- Debug and smoke tools, governed by no spec and citing none:
  `run_week1_debug.py`, `run_week1_dense_debug.py`, `smoke_test_reranker.py`
- `scripts/reporting/` (11 files): `README.md`, `__init__.py`,
  `summarize_results.py`, `disagreement_cases.py`, `rescue_damage.py`,
  `rerank_rescue_damage_cases.py`, `plot_rescue_damage.py`,
  `bm25_failure_shortlist.py`, `build_gold_rank_patterns.py`,
  `formal_result_inputs.py`, `manual_review_category_counts.py`,
  `build_gold_matching_audit.py`

### 3.4 Tests — `tests/` (26 files)

Run with `python -m pytest tests/` from the repository root.

Recorded result at `9bff6cd`, in the project virtual environment:

```text
PYTHONUTF8=1  ->  2548 passed  (242s)
default locale (cp936 on this machine)  ->  2547 passed, 1 failed
```

The single failure is environment-dependent and is listed as an open item in §8.
Anyone reproducing this should record which of the two lines they got.

## 4. Results

All tracked under `results/`. The authoritative artifacts, by role:

| File | Role |
|---|---|
| `main_results_v1.csv` | the three-row headline table: BM25, Dense, Dense + Rerank |
| `bm25_results.csv`, `dense_results.csv`, `rerank_results.csv` | the per-stage formal runs, 500 examples per setting |
| `dense_top50_pooled.csv` | the top-50 export the reranker and the failure review consume |
| `rerank_rescue_damage.csv` | the aggregate rescue/damage summary |
| `rerank_rescue_damage_cases.csv` | the per-example rescue/damage transitions |
| `disagreement_cases.csv` | BM25-versus-dense disagreements at k = 5 |
| `bm25_failure_shortlist.csv` | the BM25 failure shortlist |
| `week1_debug_results.csv`, `week1_dense_debug_results.csv` | the Week 1 ten-example debug outputs |
| `figures/rerank_rescue_damage.html` | the rescue/damage presentation figure |
| `annotations/manual_review_v1/final_labels.csv` | the 30 hand-assigned failure labels |
| `annotations/manual_review_v1/category_counts.csv` | their counts, denominator 30 |
| `annotations/manual_review_v1/case_memos_v2.csv` | the reviewers' written review records |
| `annotations/manual_review_v1/assignment.csv` | the reviewer assignment table |
| `annotations/manual_review_v1/failure_review.html` | the review page both reviewers used |

Manual-review write-ups live under `docs/`:
`docs/manual_review_v1_failure_analysis.md`,
`docs/manual_review_v1_open_coding_memo.md`,
`docs/taxonomy_candidate_v0_1.md`, and the record under
`docs/manual_review_v1/`.

Every number in the report must be traceable to one of these files. The
regenerating tool for the headline table is
`scripts/reporting/summarize_results.py --main-table`; for the rescue/damage
summary, `scripts/reporting/rescue_damage.py`; for the label counts,
`scripts/reporting/manual_review_category_counts.py --check`.

## 5. Demo, declaration, and contribution statement

| Item | Path | State |
|---|---|---|
| Demo script | `demo.py` | complete; `python demo.py` prints three sections offline and exits 0 |
| Demo contract | `docs/specs/2026-08-14-offline-demo.md` | complete |
| Demo tests | `tests/test_demo.py` | 9 tests, covering the five obligations of the spec's §6 |
| AI Usage Declaration | a section of the report | **this is the submitted version** |
| AI Usage Declaration, repository working copy | `docs/AI_Usage_Declaration.md` | `status: draft`; §7 still holds Jiajun's placeholder. Owner decision 2026-08-14: not reconciled, because the report carries the submitted text. |
| Per-member contribution statements | a section of the report | **this is the submitted version**; no separate file |

`demo.py` needs neither a network connection nor a GPU: it reads
`results/main_results_v1.csv`, `results/disagreement_cases.csv`, and
`results/rerank_rescue_damage_cases.csv`, and prints the headline table, one
BM25-versus-dense disagreement, and one reranker rescue with one damage. Every
figure it prints is a CSV cell; it recomputes nothing.

The other documented commands do need a network connection on first run:
`datasets` downloads HotpotQA (~600 MB) and the dense retriever downloads
`all-MiniLM-L6-v2` (~90 MB).

## 6. What must not be in the archive

`git archive` excludes all of this automatically. The list exists so that a
hand-assembled package can be checked against it, and so the exclusions are a
recorded decision rather than an accident.

| Path | Why it is excluded |
|---|---|
| `docs/Local/` (6.3 MB) | personal working notes, the personal implementation plan, the proposal, the instructor's own PDFs, and the report draft. Not publishable. |
| `docs/Completion_Log/Xin_*` | one member's private session logs |
| `.claude/` | local design records, reviews, prompts, and scratch |
| `results/runs/` (44.8 MB) | large failure-review intermediates. Regenerable by `scripts/run_failure_review.py`, but not byte for byte -- see the note below. Nothing in the reported results depends on them. |
| `results/annotations/*/*_cases.json`, `*_notes*.csv` (~1.2 MB) | per-reviewer case files that embed full paragraph text; they regenerate byte-for-byte via `scripts/build_manual_review_batch.py` |
| `docs/manual_review_v1/per_case_analysis/`, `tools/`, `taxonomy_todo.md`, `references/2026-08-05-*.md` | working material; the exclusion is documented for readers in `docs/manual_review_v1/README.md` |
| `venv/`, `__pycache__/`, `.pytest_cache/` | environment and caches |

No secret, credential, or API key is tracked in this repository.

### 6.1 What "regenerable" means for `results/runs/`, precisely

Measured on `results/runs/2026-07-17_a/` on 2026-08-14, because the earlier
wording of the row above claimed more than is true. Three things stand between a
rerun and the original bytes, and they are not equally serious.

1. **Two of the five files can never match.** `config.json` stamps its own
   `timestamp`, and `failures_review.html` embeds that whole config block
   verbatim. A rerun therefore differs in both by construction, independently of
   anything else.
2. **The commit the run names is not on `main`.** `config.json` records
   `git_commit: 135765bb34910bd4191352d1c95ac8876e7ddb3d`, which is reachable
   only from `origin/refactor/metrics-schema-v2`. A full `git clone` fetches it,
   so `git checkout 135765b` works from a clone; the submission archive carries
   no Git history at all, so from the archive alone the producing code state is
   not recoverable.
3. **Scores are not bit-pinned.** `requirements.txt` bounds neither `torch` nor
   `sentence-transformers`, and no seed is set. Ranking itself is deterministic
   -- `DenseRetriever._rank_paragraphs` sorts stably, so equal scores keep corpus
   order -- but a different backend can move an embedding in its last bits, and
   that can reorder a near-tie.

What does survive is the part that is cited. `metrics.json` holds aggregate rates
over 500 examples rounded to three decimals, which last-bit noise does not move,
and those figures match the headline table in `README.md` and the tracked result
CSVs. So the *findings* are reproducible; the *files* are not, and no claim in
the report rests on the files.

## 7. Pre-upload verification

Run in order. Record the actual output of each, not the expectation.

1. **Freeze the commit.** `git status --short` is empty and
   `git rev-list --left-right --count origin/main...HEAD` is `0 0`. Note the
   commit hash; it is the one the report links to and the one the archive is cut
   from.
2. **Clean-environment check.** Clone the repository to a new directory, create a
   fresh virtual environment, `pip install -r requirements.txt`, then run
   `python demo.py` and confirm it exits 0 and prints all three sections. This is
   the check the plan assigns to Jiajun and it has not been run yet.
3. **Tests.** `python -m pytest tests/` in that clean clone. Record the count and
   whether the locale-dependent failure in §8 appeared.
4. **Result traceability.** Re-run the three regenerating tools named in §4 and
   confirm they reproduce their checked-in outputs.
5. **Report render.** Open the final rendered report and check layout, figure
   readability, table overflow, captions, numbering, references, and appendix
   placement. Confirm no placeholder text and no broken reference.
6. **One scope, four places.** Confirm the report, this repository's `README.md`,
   `demo.py`, and the report's AI Usage Declaration section describe the same
   final method — in particular the notes-first open-coding review of 30 units
   and the evidence-derived candidate taxonomy, not a rule-based analyzer. The
   planning documents under `docs/Plans/` are excluded from this check on
   purpose; see §8.
7. **Archive contents.** Build the archive with `git archive`, then list its
   contents and check every row of §6 is absent.
8. **Both members approve** the exact report file and the exact archive.
9. **Upload, then verify.** Re-download what was uploaded and confirm it opens.
   Retain the submission confirmation and a local copy of both uploaded files.

### 7.10 Recorded results, 2026-08-14

Steps 2, 3, 4, and 7 were run on 2026-08-14 in a clean-environment check. Steps
1, 5, 6, 8, and 9 were not part of that run and remain as written above.

Environment of the run: a fresh `git clone` of the repository at
`9bff6cd288a6deae35414d53fdbb382de7074d26`, which was verified to equal
`refs/heads/main` on `origin` at the time of the check. The clone was not a copy
of the working directory and did not reuse the project virtual environment. Host
was Windows 11, ANSI code page cp936, Python 3.11.5.

**Step 1 (freeze) — not re-run, and not green at the time of the check.** The
working tree held one modified tracked file, `README.md`, and one untracked file,
this document. `git rev-list --left-right --count origin/main...HEAD` was `0 0`
and `HEAD` was `9bff6cd`, so the commit itself is in sync; the uncommitted
changes are the open part.

**Step 2 (clean environment) — PASS, with one host-level precondition.**
`python -m venv` plus `pip install -r requirements.txt` completed with exit code
0. Resolved versions: `datasets 4.8.5`, `rank-bm25 0.2.2`,
`sentence-transformers 5.7.0`, `pandas 3.0.5`, `numpy 2.4.6`, `pytest 9.1.1`,
`torch 2.13.0`, `transformers 5.15.0`.

The first attempt at this step failed, and the failure is a property of the host,
not of the repository. With the clone at a 131-character path and Windows long
path support disabled (`HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem`,
`LongPathsEnabled = 0`), the `torch` wheel could not be unpacked:

```text
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or
directory: '...\c1\venv\Lib\site-packages\torch\include\ATen\native\transformers\
cuda\mem_eff_attention\iterators\default_warp_iterator_from_smem.h'
```

This is a setup error, not a test failure. It disappears when the clone sits at a
short path. A grader on Windows with long paths disabled will hit it if they
clone deep; `requirements.txt` cannot prevent it. Worth one line in the README's
setup section, if the owners want it.

**Step 3 (offline demo) — PASS.** `python demo.py` exited 0 and printed all three
sections with no network access. Offline was enforced with `HF_HUB_OFFLINE=1`,
`TRANSFORMERS_OFFLINE=1`, `HF_DATASETS_OFFLINE=1` and the proxy variables pointed
at a dead port, so any outbound HTTP would have failed immediately. Section 1
printed the three-row headline table, section 2 printed example
`5a71166d5542994082a3e576`, and section 3 printed rescue
`5a713a5a5542994082a3e6a9` and damage `5a7571135542992d0ec05f98`. Every printed
figure matched the checked-in CSVs.

**Step 4 (tests) — neither of the two outcomes §3.4 predicts.** Both runs
collected 2548 tests, which is the expected total, but the clean clone
distributes them differently:

```text
PYTHONUTF8=1     ->  1 failed, 2469 passed, 78 skipped   (235s)
default locale   ->  2 failed, 2468 passed, 78 skipped   (252s)
```

Two differences from the recorded baseline, both explained:

1. **78 tests skip in any clean clone.** They require `results/runs/2026-07-17_a/`,
   which §6 deliberately excludes from Git. 77 report `the read-only source run
   results/runs/2026-07-17_a/ is absent` and 1 reports `formal run directory
   results/runs/2026-07-17_a is not present`. They are spread across
   `test_manual_review_page.py`, `test_build_manual_review_batch.py`, and
   `test_build_gold_rank_patterns.py`. The skips are correct behaviour — the
   tests guard themselves — but it means no grader can ever see the 2548-passed
   line. The `2548 passed` in §3.4 was measured in the project virtual
   environment, where that directory exists locally.
2. **One failure is new and is not the locale failure.**
   `tests/test_formal_result_inputs.py::test_typed_layer_refuses_an_unknown_setting_value[0]`
   fails under both locales. `requirements.txt` sets `pandas>=2.0.0` with no
   upper bound, so a fresh install now resolves `pandas 3.0.5`, where assigning
   the integer `0` into a `str`-dtype column raises on the assignment itself:

   ```text
   tests/test_formal_result_inputs.py:961: in test_typed_layer_refuses_an_unknown_setting_value
       df.loc[df.index[0], "setting"] = value
   E   TypeError: Invalid value '0' for dtype 'str'. Value should be a string or
       missing value, got 'int' instead.
   ```

   The failure is in the test's own setup line, before the code under test runs.
   `scripts/reporting/formal_result_inputs.py` is not implicated, and the four
   sibling parameters (`"Pooled"`, `"bogus"`, `""`, `None`) all pass. Fixed on
   2026-08-14 in the test's setup; see §9 item 4.

The known §9.2 locale failure did appear under the default locale, as documented:
`tests/test_plot_rescue_damage.py::test_non_canonical_rate_lexeme_refuses[rescue_rate-０.232-fullwidth_digit]`,
raising `TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'`. In
this clone the raising line is `test_plot_rescue_damage.py:375`, inside the
`_assert_refused` helper, rather than the `:362` §9.2 names. It passes under
`PYTHONUTF8=1`. Note that the console code page was already 65001; the decode
still fails because Python decodes subprocess output with the ANSI code page,
which remained cp936. Setting `chcp` is therefore not a workaround — only
`PYTHONUTF8=1` is.

**Step 5 (result traceability) — PASS, byte for byte.** All three tools from §4
were re-run in the clone and each rewrote its target; SHA-256 before and after
was identical in every case, and `git status --short` was empty afterwards.

| Tool | Target | Result |
|---|---|---|
| `summarize_results.py --main-table --out results/main_results_v1.csv` | `results/main_results_v1.csv` | rewritten, byte-identical |
| `rescue_damage.py` | `results/rerank_rescue_damage.csv` | rewritten, byte-identical |
| `manual_review_category_counts.py --check` | `results/annotations/manual_review_v1/category_counts.csv` | matches derivation, 814 bytes |

One correction to §4's wording: `summarize_results.py --main-table` on its own
only prints the table to stdout. Writing the file needs the `--out` path, as the
tool's own usage example shows. The command as §4 states it verifies nothing.

`rescue_damage.py` self-reported `Inputs pass the §2 contract: 1000 dense + 1000
rerank rows` and `Output passes §9.3 schema, §9.2 types/ranges, §9.5 identities,
and the oracle`. `manual_review_category_counts.py --check` self-reported `30
unit rows, denominator 30, counts sum to 30`.

**Step 7 (archive contents) — PASS.** Built from `9bff6cd` with the §1 command.
The archive holds **112 files and 3.98 MB** (4,177,299 bytes compressed; 12.33 MB
uncompressed; 127 zip entries, of which 15 are directory entries). This matches
the figure §1 records.

Every row of §6 was checked against the listing and every one is absent:
`docs/Local/`, `docs/Completion_Log/Xin_*`, `.claude/`, `results/runs/`,
`results/annotations/*/*_cases.json`, `results/annotations/*/*_notes*.csv`,
`docs/manual_review_v1/per_case_analysis/`, `docs/manual_review_v1/tools/`,
`docs/manual_review_v1/taxonomy_todo.md`,
`docs/manual_review_v1/references/2026-08-05-*`, `venv/`, `__pycache__/`,
`.pytest_cache/`. A scan of the listing for `.env`, `secret`, `credential`,
`.pem`, `id_rsa`, `.key`, and `token` returned nothing, consistent with §6's
closing line.

The archive built during this check was a verification artifact and was deleted
with the clone. The archive that is actually uploaded must be rebuilt from the
final commit.

### 7.11 The archive was run as an archive, 2026-08-14

Every earlier check in §7 was performed on a Git *clone*. That is not what is
uploaded, and the difference was not cosmetic: unpacking the archive and running
the documented test command failed at collection, so **no test ran at all**.

```text
RuntimeError: could not ask git for the tracked files under docs/specs/ ...
  stderr was 'fatal: not a git repository (or any of the parent directories): .git'
Interrupted: 1 error during collection
```

`tests/test_tracked_spec_line_endings.py` discovered the tracked specification
set at import time, so the absence of an index was raised as an error during
collection rather than handled, and one module took the whole suite down with it.

Fixed by asking whether the tree is its own repository root and skipping the two
checks that enumerate tracked paths when it is not. The check is written as "is
this tree its own repository" rather than "is there a repository above", because
an archive unpacked inside an unrelated checkout answers yes to the weaker
question while every path in it belongs to a different index. The module's other
checks read bytes off disk and are unaffected, so the accepted protocol digest
and the `.gitattributes` rule stay guarded in an archive.

Verified in all three environments:

| Environment | Result |
|---|---|
| the repository itself | `18 passed` for the module; `2548 passed` for the suite |
| archive unpacked inside another repository | `9 passed, 2 skipped` |
| archive unpacked outside any repository | `2461 passed, 80 skipped` for the suite |

Two further properties of the archive were confirmed while diagnosing this, both
by comparing extracted bytes against the committed blobs:

- `.gitattributes` is honoured by `git archive`. `docs/specs/**` comes out LF and
  the course protocol still hashes to its accepted digest
  (`5BB4E045...`, 40102 bytes); the `results/annotations/**` files come out
  byte-identical to their blobs. The CR bytes visible inside those CSVs are
  literal cell content, not conversion.
- The 98 files that do differ from their blobs differ only in line endings, and
  they are exactly the files no recorded digest describes. None of them carry a
  checksum, and the suite is green over them.

### 7.12 Both supported Python versions were run, 2026-08-14

`README.md` states that the project has been tested on Python 3.9.7 and 3.11.5.
Both halves were measured, because the two versions do not resolve the same
dependency set: 3.9 caps `pandas` at the 2.x line, so only a 3.11 environment
exercises `pandas` 3.x at all.

| Interpreter | Resolved dependencies | Full suite |
|---|---|---|
| 3.9.7 (the project virtual environment) | `pandas 2.3.3` | `2548 passed` |
| 3.11.5 (clean install from `requirements.txt`) | `pandas 3.0.5`, `numpy 2.4.6`, `torch 2.13.0+cpu`, `pytest 9.1.1` | `2548 passed` |

The 3.11.5 run is what retires §9 item 4: that failure needed `pandas` 3.x to
reproduce, and the environment above is the one that resolves it.

Building that environment ran into the long-path limit of §7.10 again, and the
first workaround failed in a way worth recording. Mapping a drive letter with
`subst` does shorten the path, but `python -m venv` resolves the mapping back to
the real location and reports doing so, so the deep `torch` headers are unpacked
at the long path anyway and the install fails exactly as before. Installing with
`pip install --target <short path>` does not go through that resolution and
succeeds. On a host with `LongPathsEnabled = 1` neither workaround is needed.

## 8. Owner decisions recorded 2026-08-14

Written down because the plan requires each of these to be recorded, and because
a silent omission reads the same as an oversight.

1. **The optional fine-tuning extension is a no-go.** Contrastively fine-tuning
   the dense encoder and re-evaluating per failure category was gated by a joint
   go/no-go decision the plan scheduled for 8/5 and required to be recorded
   either way. The decision is no-go. Nothing in this repository implements it.
2. **The submitted AI Usage Declaration and contribution statements are report
   sections.** `docs/AI_Usage_Declaration.md` stays as the repository's working
   copy at `status: draft`, with the placeholder in its §7 unresolved. It is not
   being reconciled with the report, and the report is the authority.
3. **The planning documents under `docs/Plans/` are not being corrected.**
   `CS6120_Final_Project_Scope_HotpotQA_Retrieval.md` still specifies a
   rule-based `failure_analyzer.py` with six preset categories validated against
   about 20 labels. That is not what was built: the project ran a notes-first
   open-coding review of 30 units and derived a candidate taxonomy from the
   evidence, with six K1–K6 categories plus `unresolved`. The three schedule and
   scope documents are also frozen at their 2026-07-31 revision. They are
   retained as the historical plan of record and are **not** a description of the
   final method. The authoritative descriptions are the report, `README.md`,
   `docs/manual_review_v1/README.md`, `docs/taxonomy_candidate_v0_1.md`, and
   `docs/manual_review_v1_failure_analysis.md`.

## 9. Remaining open items

1. **The clean-environment check in §7.2 was run on 2026-08-14.** Results are
   recorded in §7.10. It found two things not previously known, listed as items 4
   and 5 below. Steps 5, 6, 8, and 9 of §7 remain unattempted, and §7.1 was not
   green at the time of the check: `README.md` was modified and uncommitted.
2. **One test fails under a non-UTF-8 Windows locale.**
   `tests/test_plot_rescue_damage.py` captures a subprocess without an explicit
   encoding, so a cp936 host cannot decode a full-width digit in the child's
   stderr and the test raises `TypeError`. It passes under `PYTHONUTF8=1`.
   Confirmed reproduced in the clean clone; see §7.10, which also corrects the
   line number and notes that changing `chcp` does not help.
3. **The final report is still a draft** and its final rendered filename is not
   yet recorded in §2.
4. **~~One test fails on `pandas` 3.x regardless of locale.~~ Fixed 2026-08-14.**
   `tests/test_formal_result_inputs.py::test_typed_layer_refuses_an_unknown_setting_value[0]`
   raised `TypeError` on its own setup line under `pandas` 3.x. The fix is in the
   test's setup, not in `requirements.txt` and not in the code under test: the
   frame's `setting` column is widened to `object` before the non-string value is
   placed, which is the only column type that could carry such a value to the
   validator in a real caller, and which `pandas` 2 was already using implicitly.
   `pandas` is deliberately left unpinned — the rest of the suite is clean under
   3.0.5, so an upper bound would buy nothing. Verified on both majors:
   `tests/test_formal_result_inputs.py` is `814 passed` under `pandas 3.0.5` /
   Python 3.11 and under `pandas 2.3.3` / Python 3.9, and the full suite is
   `2548 passed` in the project environment. Retired by §7.12: the full suite is
   `2548 passed` on Python 3.11.5 with `pandas 3.0.5`, which is the environment
   the failure needed. See §7.10 step 4 for the original diagnosis.
5. **78 tests skip in any clean clone.** They require `results/runs/2026-07-17_a/`,
   which §6 excludes from Git on purpose. The skips are correct behaviour, but
   the `2548 passed` line in §3.4 is only reachable in an environment where that
   directory exists locally, so no grader will see it. See §7.10 step 4.
