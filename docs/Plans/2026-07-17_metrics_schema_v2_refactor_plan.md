# Metrics/Schema v2 Refactor Execution Plan

- **Status:** In progress; Draft PR only
- **Working branch:** `refactor/metrics-schema-v2`
- **Merge target:** `main`
- **Last updated:** 2026-07-17

## 1. Objective and scope

Separate retrieval artifacts from evaluation artifacts without destabilizing the current formal pipeline:

```text
results/ = raw retriever/reranker rankings + manifests
evals/   = per-example evaluation + aggregate/subgroup evaluation + manifests
```

The migration must preserve the existing legacy workflow until v2 outputs pass explicit comparison and acceptance.
This plan governs implementation, review, and merge sequencing. Detailed local design notes may supplement it, but
team-visible contracts, tests, and decisions must be reflected in tracked files before final merge.

## 2. Branch and PR policy

- Keep `main` stable and usable. Implement schema v2 only on `refactor/metrics-schema-v2`.
- Open a Draft PR early for review and CI, but do not mark it ready or merge it until the final merge gate passes.
- Use one independently reviewable and reversible commit for each stage in §5. Do not collapse the refactor into one
  giant commit.
- Prefer a normal PR merge commit so the eight stage commits remain visible and individually inspectable.
- When `main` advances, merge it into the refactor branch at a stage boundary and rerun the full test suite. Sync it
  again immediately before final acceptance.
- Before freezing changes to `RESULT_COLUMNS`, paths, manifests, CLI defaults, or report-facing interfaces, align the
  contract with the BM25 collaborator.
- Keep this plan and the Draft PR checklist current as stages finish; a code-complete claim alone is not an exit gate.

## 3. Baseline and hard gates

Before implementation, record the branch SHA, test result, formal artifact row counts, schemas, and checksums in the
Draft PR. The baseline test command is:

```powershell
.\venv\Scripts\python.exe -m pytest -q --basetemp=.pytest_tmp_handoff
```

### Metric-definition freeze

Do not modify the core metric logic in `src/evaluator.py`, generate formal v2 evals, or cut over formal paths until
Xin/the team has frozen and documented:

- gold-evidence unit and matching policy;
- K policy, including corpus-shorter-than-K behavior;
- empty-gold, missing-value, and denominator policy;
- macro/micro aggregation policy and `n_valid` behavior;
- machine identifiers, report-facing labels, and metric-definition version;
- team-authored or team-verified golden examples with expected per-example and aggregate values.

Schema constants, file I/O, structural validators, manifests, and synthetic offline tests may proceed before this
freeze only when they do not define or silently change metric semantics.

## 4. Compatibility and cutover policy

Runner migration must follow this order:

```text
legacy only -> dual-write -> raw/eval comparison -> v2 default -> legacy retirement
```

- Dual-write before changing defaults; never replace the legacy path in the same step that first introduces v2.
- Keep legacy artifacts read-only and recoverable until formal comparisons pass. Do not overwrite existing n=500
  outputs or fabricate missing scores.
- Prove raw ranking parity before metric parity. Raw comparison requires identical ordering; eval comparison requires
  full parity for unchanged definitions and team-approved expected differences for intentionally changed definitions.
- Validators validate contracts, types, ranges, joins, ordering, uniqueness, and checksums; they must not recompute or
  redefine metrics.
- Switch default paths only in Stage 8, after downstream consumers use the new contracts and rollback remains possible.

## 5. Eight implementation stages

Each stage ends with tests, review evidence in the Draft PR, and one scoped commit before the next stage begins.

1. **Document raw retrieval and evaluation v2 contracts.**
   Freeze directory layout, `rankings.csv`, raw/eval manifests, per-example output, aggregate output, IDs, versions,
   and storage-to-report naming mappings.
2. **Add schema constants, validators, and offline tests.**
   Use synthetic fixtures; keep existing runners, evaluator core logic, and formal artifacts unchanged.
3. **Add raw ranking writers and dual-write runner support.**
   Integrate Dense and BM25 without making v2 paths the only defaults or invoking retrieval a second time.
4. **Generate and validate formal n=500 raw retrieval runs.**
   Validate all method/setting bundles, manifests, row counts, checksums, saved depth, and zero ordering mismatches.
5. **Integrate the team-authored per-example evaluator v2.**
   Begin only after the metric-definition freeze and golden examples pass; compare all unchanged and changed metrics.
6. **Add aggregate evaluation v2 and report-label mapping.**
   Aggregate only from validated per-example artifacts; record traceability, denominators, `n_valid`, and versions.
7. **Migrate downstream consumers.**
   Move reranker, failure review, summary, analysis, and annotation inputs to raw plus eval artifacts without duplicate
   metric implementations.
8. **Cut over defaults and retire the active legacy workflow.**
   Update CLI behavior and documentation only after all comparisons pass; retain recoverable legacy history and a
   migration record.

## 6. Definition of Done and final merge gate

The Draft PR may be marked ready, and then merged into `main`, only when all of the following are true:

- [ ] All eight stages have separate, reviewable commits and their acceptance evidence is present in the PR.
- [ ] `results/` active outputs contain only validated raw rankings and manifests.
- [ ] `evals/` separates per-example and aggregate outputs with unambiguous machine names and versions.
- [ ] Dense, BM25, and rerank outputs use the same raw ranking contract.
- [ ] Pooled and per-question formal n=500 raw bundles are complete, traceable, and have zero ordering mismatches.
- [ ] Unchanged metric definitions have full legacy parity; changed definitions have approved golden tests and expected
  differences.
- [ ] Every aggregate output traces to a validated per-example eval, raw run ID, and raw checksum.
- [ ] Reranker consumes raw Dense candidates and failure review consumes raw plus eval data without recomputing metrics.
- [ ] The legacy mixed CSV workflow is no longer the active default, but its artifacts remain recoverable.
- [ ] Schema, validator, unit, integration, and end-to-end tests all pass after the final sync from `main`.
- [ ] README, specifications, plans, handoff, `.gitignore`, directory layout, and CLI behavior agree.
- [ ] BM25 interface alignment and the team-owned metric-definition freeze are documented.
- [ ] No migration step fabricates scores, hand-edits formal values, overwrites legacy artifacts, or changes only a
  header while retaining mixed semantics.

## 7. Review and rollback

- Review each stage before starting the next stage that depends on it.
- If a stage fails acceptance, revert or correct that stage without deleting legacy evidence or bypassing its gate.
- Do not squash the final PR by default. Keeping the stage commits makes both targeted review and rollback practical.
- Merge to `main` only through the reviewed PR after CI and every checkbox in §6 pass.
