---
last_updated: 2026-08-14
---

# Reporting and audit tools

Post-run tooling. Most modules here consume artifacts that the experiment
runners have already produced -- the formal long-format result CSVs and the
failure-review run directories -- and reduce them to a table, a shortlist, or a
figure that the report and the slides quote. Two inputs come from elsewhere:
`manual_review_category_counts.py` reads human-reviewed final labels, and
`build_gold_matching_audit.py` additionally reads raw HotpotQA data.

This is an index. Each module's own docstring is the authority on its behaviour,
and where a specification governs the module, the one it cites is the authority
on its contract; neither is restated here.

## The boundary this directory keeps

**No module here defines a metric.** Metric definitions and their per-example
computation live in [src/evaluator.py](../../src/evaluator.py); the column set and
its emptiness rules live in [src/results_schema.py](../../src/results_schema.py).
These tools aggregate, filter, join, and render values that are already computed.

**No module here assigns a failure category.** Causal labels are assigned by a
human reviewer under
[docs/specs/2026-07-27-manual-failure-review-course-protocol.md](../../docs/specs/2026-07-27-manual-failure-review-course-protocol.md).
`bm25_failure_shortlist.py` in particular emits only mechanically observable
signals -- it is deliberately not a classifier.

Both boundaries are recorded in
[docs/AI_Usage_Declaration.md](../../docs/AI_Usage_Declaration.md): the counting
and metric logic is hand-written, the validation and serialization plumbing
around it is agent-generated.

## Modules

| Module | Reads | Writes |
|---|---|---|
| [`formal_result_inputs.py`](formal_result_inputs.py) | *shared library -- not a command* | -- |
| [`summarize_results.py`](summarize_results.py) | `bm25_results.csv`, `dense_results.csv`, `rerank_results.csv` | per-`(method, setting)` summary to stdout; `--out` for a CSV, `--main-table` for the report-facing pooled table |
| [`disagreement_cases.py`](disagreement_cases.py) | `bm25_results.csv`, `dense_results.csv`, optionally `rerank_results.csv` | `results/disagreement_cases.csv` |
| [`bm25_failure_shortlist.py`](bm25_failure_shortlist.py) | `bm25_results.csv`, `dense_results.csv` | `results/bm25_failure_shortlist.csv` |
| [`rescue_damage.py`](rescue_damage.py) | `dense_results.csv`, `rerank_results.csv` | `results/rerank_rescue_damage.csv` (aggregate) |
| [`rerank_rescue_damage_cases.py`](rerank_rescue_damage_cases.py) | `dense_results.csv`, `rerank_results.csv` | `results/rerank_rescue_damage_cases.csv` (per example) |
| [`plot_rescue_damage.py`](plot_rescue_damage.py) | the two rescue/damage CSVs above | `results/figures/rerank_rescue_damage.html` |
| [`build_gold_rank_patterns.py`](build_gold_rank_patterns.py) | a run directory's `details.jsonl` + `config.json` | `<run>/gold_rank_patterns.csv` |
| [`manual_review_category_counts.py`](manual_review_category_counts.py) | `manual_review_v1/final_labels.csv` | `manual_review_v1/category_counts.csv`; `--check` re-derives and byte-compares instead |
| [`build_gold_matching_audit.py`](build_gold_matching_audit.py) | raw HotpotQA arrow + run details + both result CSVs | a manual gold-title audit worksheet (`--out`; the default target is local-only) |

`formal_result_inputs.py` is the odd one out: it has no `__main__` and no
arguments. It is the shared input contract that `disagreement_cases.py`,
`bm25_failure_shortlist.py`, and `rescue_damage.py` all load through, so that the
join those three perform can never silently combine unrelated records that merely
share an `example_id`. Change it and you change all three.

## Governing documents

| Document | Governs |
|---|---|
| [2026-07-15-results-csv-schema.md](../../docs/specs/2026-07-15-results-csv-schema.md) | the long-format result CSVs every tool here reads; `summarize_results.py` |
| [2026-07-27-bm25-dense-reporting-contracts.md](../../docs/specs/2026-07-27-bm25-dense-reporting-contracts.md) | `formal_result_inputs.py`, `disagreement_cases.py`, `bm25_failure_shortlist.py`, `rescue_damage.py` |
| [2026-07-26-reranker-rescue-damage.md](../../docs/specs/2026-07-26-reranker-rescue-damage.md) | `rescue_damage.py` (frozen 17-column / 21-row output); the summary half of what `plot_rescue_damage.py` re-validates |
| [2026-08-12-rerank-rescue-damage-cases.md](../../docs/specs/2026-08-12-rerank-rescue-damage-cases.md) | `rerank_rescue_damage_cases.py`; the cases half of what `plot_rescue_damage.py` re-validates |
| [2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md](../../docs/specs/2026-07-26-hotpotqa_gold_rank_pattern_partition_spec.md) | `build_gold_rank_patterns.py` |
| [2026-07-12-failure-review-pipeline-design.md](../../docs/specs/2026-07-12-failure-review-pipeline-design.md) | the run directories `build_gold_rank_patterns.py` consumes; the failure-review boundary `bm25_failure_shortlist.py` observes |
| [2026-07-27-manual-failure-review-course-protocol.md](../../docs/specs/2026-07-27-manual-failure-review-course-protocol.md) | `manual_review_category_counts.py`; the notes-first boundary |
| [docs/taxonomy_candidate_v0_1.md](../../docs/taxonomy_candidate_v0_1.md) | the closed label vocabulary `manual_review_category_counts.py` validates against |

One module is deliberately absent from that table. `build_gold_matching_audit.py`
renders a worksheet for a human to read and approve; no frozen contract
constrains its output, so it is governed by no specification and cites none.
That is a disclosure rather than an omission: every other module in this
directory has a row above and names the same document, by the same repository
path, in its own docstring.

## Order of operations

Nothing in this directory produces the three formal method result CSVs or a
failure-review run directory. Those inputs come from the runners one level up;
the derived CSVs in the module table above are outputs of this directory:

```text
scripts/run_bm25_experiment.py     ->  results/bm25_results.csv
scripts/run_dense_experiment.py    ->  results/dense_results.csv
scripts/run_rerank_experiment.py   ->  results/rerank_results.csv
scripts/run_failure_review.py      ->  results/runs/<run_id>/
```

Given those, the dependencies inside this directory are:

```text
bm25 / dense / rerank_results.csv
  |
  |-- summarize_results.py           -> summary table
  |-- disagreement_cases.py          -> disagreement_cases.csv
  |-- bm25_failure_shortlist.py      -> bm25_failure_shortlist.csv
  |-- rescue_damage.py               -> rerank_rescue_damage.csv ------.
  `-- rerank_rescue_damage_cases.py  -> rerank_rescue_damage_cases.csv -+
                                                                       |
                                        plot_rescue_damage.py  <--------'
                                             -> figures/rerank_rescue_damage.html

results/runs/<run_id>/       -> build_gold_rank_patterns.py
final_labels.csv             -> manual_review_category_counts.py
```

`plot_rescue_damage.py` is the only tool with an in-directory prerequisite, and
what it checks depends on which of its two modes runs.

In the **default three-figure mode** it reads both rescue/damage CSVs, and it
does not trust them to match. Before it renders anything, and before the
destination file is touched, it re-validates each input against its frozen
contract and then cross-checks them: every `(setting, k)` slice of the cases file
must aggregate back to the summary's Full Evidence rows -- all five slices, not
only the one Figure 3 plots. So regenerating one CSV without the other fails
closed: the run aborts with a disagreement diagnostic and the previous figure is
left in place, rather than rendering a figure that looks clean and is wrong. The
residual risk is the narrow one the cross-check cannot see -- drift that changes
provenance or text while preserving every aggregate count -- so regenerate the
pair together instead of relying on the check to catch a stale half.

`--no-cases` is the documented exception, and it is deliberately weaker. It
renders Figures 1-2 from the summary alone: the cases file is never opened, a
missing or stale cases file is not an error, and no cross-file agreement is
checked at all -- only the summary's own frozen contract is validated. The
destination is still replaced on success, so a `--no-cases` run can overwrite a
three-figure page with a two-figure one that no cases file ever agreed with. Use
it when only the summary exists; use the default whenever both artifacts do.

`rerank_rescue_damage_cases.py` must aggregate back to
`rerank_rescue_damage.csv`'s Full Evidence rows exactly; it reuses that module's
loader and join rather than defining a second one.

Run every command from the repository root, with the project virtual environment:

```bash
venv/Scripts/python.exe scripts/reporting/summarize_results.py --main-table
```

## Tests

Every module here except `build_gold_matching_audit.py` has a regression suite
named after it:

- [tests/test_formal_result_inputs.py](../../tests/test_formal_result_inputs.py)
- [tests/test_summarize_results.py](../../tests/test_summarize_results.py)
- [tests/test_disagreement_cases.py](../../tests/test_disagreement_cases.py)
- [tests/test_bm25_failure_shortlist.py](../../tests/test_bm25_failure_shortlist.py)
- [tests/test_rescue_damage.py](../../tests/test_rescue_damage.py)
- [tests/test_rerank_rescue_damage_cases.py](../../tests/test_rerank_rescue_damage_cases.py)
- [tests/test_plot_rescue_damage.py](../../tests/test_plot_rescue_damage.py)
- [tests/test_build_gold_rank_patterns.py](../../tests/test_build_gold_rank_patterns.py)
- [tests/test_manual_review_category_counts.py](../../tests/test_manual_review_category_counts.py)

`build_gold_matching_audit.py` is the exception: no suite in `tests/` is named
after it, and nothing else there exercises it either. Its worksheet is a
hand-read audit input whose default destination is local-only, so the gap is
disclosed rather than hidden -- treat its output as unguarded, and re-read it by
hand after changing that module.

Beside them,
[tests/test_reporting_doc_references.py](../../tests/test_reporting_doc_references.py)
checks something the behavioural suites structurally cannot: that the documents
`formal_result_inputs.py`, `disagreement_cases.py`, `bm25_failure_shortlist.py`,
and `rescue_damage.py` cite as their authority still exist, still live at the
cited path, and still say what the citing file claims. A tool with a dead
authority reference behaves exactly like a tool with a live one, so that kind of
rot is invisible to every other test.

Two conventions for anyone editing this file, kept by hand rather than by a test:
write links in the inline `[text](destination)` form, resolved against *this*
directory; and keep it readable by someone who has only the repository, which is
why the audit worksheet's local-only default output path is described above
rather than spelled out. Adding a tool here means adding it in three places: a
row in **Modules**, an entry in **Governing documents** -- plus the matching
repository-path citation in the tool's own docstring -- or a mention in the
disclosure beneath that table, and a suite in **Tests** or a mention in the
disclosure there.
