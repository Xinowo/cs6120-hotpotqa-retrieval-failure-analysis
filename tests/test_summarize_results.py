import pandas as pd
import pytest

from scripts import summarize_results
from src.results_schema import RESULT_COLUMNS


def _result_frame(method="dense", setting="pooled", rr_at_10=0.5, rr_at_50=0.5):
    row = {column: 0.0 for column in RESULT_COLUMNS}
    row.update(
        {
            "method": method,
            "setting": setting,
            "example_id": f"{method}-{setting}",
            "question_type": "bridge",
            "level": "hard",
            "question": "Question?",
            "gold_titles": "Gold A | Gold B",
            "retrieved_titles": "Gold A | Candidate B",
            "reciprocal_rank_at_10": rr_at_10,
            "reciprocal_rank_at_50": rr_at_50,
        }
    )
    return pd.DataFrame([row], columns=RESULT_COLUMNS)


def test_load_inputs_requires_every_requested_file(tmp_path):
    dense_path = tmp_path / "dense_results.csv"
    missing_path = tmp_path / "bm25_results.csv"
    _result_frame().to_csv(dense_path, index=False)

    with pytest.raises(FileNotFoundError, match="bm25_results.csv"):
        summarize_results.load_inputs([dense_path, missing_path])


def test_load_inputs_rejects_missing_metric_column(tmp_path):
    path = tmp_path / "dense_results.csv"
    _result_frame().drop(columns="reciprocal_rank_at_50").to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing columns.*reciprocal_rank_at_50"):
        summarize_results.load_inputs([path])


def test_load_inputs_rejects_wrong_column_order(tmp_path):
    path = tmp_path / "dense_results.csv"
    reordered = RESULT_COLUMNS[1:] + RESULT_COLUMNS[:1]
    _result_frame()[reordered].to_csv(path, index=False)

    with pytest.raises(ValueError, match="not in RESULT_COLUMNS order"):
        summarize_results.load_inputs([path])


def test_summarize_rejects_incomplete_direct_dataframe():
    incomplete = _result_frame().drop(columns="reciprocal_rank_at_50")

    with pytest.raises(ValueError, match="missing columns.*reciprocal_rank_at_50"):
        summarize_results.summarize(incomplete, ["method", "setting"])


def test_valid_inputs_are_concatenated_and_aggregated(tmp_path):
    dense_path = tmp_path / "dense_results.csv"
    bm25_path = tmp_path / "bm25_results.csv"
    _result_frame("dense", rr_at_10=0.5, rr_at_50=0.25).to_csv(
        dense_path, index=False
    )
    _result_frame("bm25", rr_at_10=1.0, rr_at_50=1.0).to_csv(
        bm25_path, index=False
    )

    combined = summarize_results.load_inputs([dense_path, bm25_path])
    summary = summarize_results.summarize(combined, ["method", "setting"])

    assert len(combined) == 2
    assert summary["method"].tolist() == ["bm25", "dense"]
    assert summary["n"].tolist() == [1, 1]
    assert summary["MRR@10"].tolist() == [1.0, 0.5]
    assert summary["MRR@50"].tolist() == [1.0, 0.25]


def test_build_main_table_is_pooled_report_facing_and_method_ordered():
    dense = _result_frame("dense", rr_at_10=0.75, rr_at_50=0.8)
    bm25 = _result_frame("bm25", rr_at_10=0.5, rr_at_50=0.6)
    per_question = _result_frame("dense", setting="per_question")
    for frame in (dense, bm25):
        frame["example_id"] = "shared-example"
        frame["any_evidence_recall@2"] = 1.0
        frame["partial_evidence_recall@5"] = 0.5

    table = summarize_results.build_main_table(
        pd.concat([per_question, dense, bm25], ignore_index=True)
    )

    assert table.columns.tolist() == summarize_results.MAIN_TABLE_COLUMNS
    assert table["Method"].tolist() == ["BM25", "Dense"]
    assert table["Any Evidence Hit Rate@2"].tolist() == [1.0, 1.0]
    assert table["Evidence Recall@5"].tolist() == [0.5, 0.5]
    assert table["MRR@10"].tolist() == [0.5, 0.75]
    assert table["MRR@50"].tolist() == [0.6, 0.8]


def test_build_main_table_requires_both_pooled_methods():
    with pytest.raises(ValueError, match="missing pooled method.*bm25"):
        summarize_results.build_main_table(_result_frame("dense"))


def test_build_main_table_requires_matching_example_ids():
    combined = pd.concat(
        [_result_frame("dense"), _result_frame("bm25")], ignore_index=True
    )

    with pytest.raises(ValueError, match="example ID sets do not match"):
        summarize_results.build_main_table(combined)


def test_main_table_csv_is_written_with_three_decimal_values(tmp_path):
    dense_path = tmp_path / "dense_results.csv"
    bm25_path = tmp_path / "bm25_results.csv"
    out_path = tmp_path / "main_results_v1.csv"
    dense = _result_frame("dense", rr_at_10=1 / 3, rr_at_50=2 / 3)
    bm25 = _result_frame("bm25", rr_at_10=0.25, rr_at_50=0.5)
    dense["example_id"] = "shared-example"
    bm25["example_id"] = "shared-example"
    dense.to_csv(dense_path, index=False)
    bm25.to_csv(bm25_path, index=False)

    summarize_results.main(
        inputs=[dense_path, bm25_path],
        group_by=["method", "setting"],
        out_path=out_path,
        main_table=True,
    )

    written = out_path.read_text(encoding="utf-8")
    assert "BM25" in written
    assert "Dense" in written
    assert "0.333" in written
    assert "0.667" in written
