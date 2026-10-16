"""Phase A regression cases for source identity and honest evaluation failures."""
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src import phase_a_ragas as phase

pytestmark = pytest.mark.student


@pytest.fixture
def answer_rows():
    return [{**q, "answer": "measured answer", "contexts": ["original context"]}
            for q in phase.load_test_set_50q()]


def evaluator(monkeypatch, rows, models=None):
    mocked = Mock(return_value={"per_question": rows, "metadata": {
        "evaluator_models": ["eval-llm", "eval-embedding"] if models is None else models}})
    monkeypatch.setitem(sys.modules, "src.m4_eval", SimpleNamespace(evaluate_ragas=mocked))
    return mocked


def test_mapping_and_numpy_scores_preserve_input_order(monkeypatch, answer_rows):
    import numpy as np
    rows = [{m: np.float32(.5) for m in phase.METRICS} for _ in answer_rows]
    call = evaluator(monkeypatch, rows)
    result = phase.run_ragas_50q(list(reversed(answer_rows)))
    assert [r.question_id for r in result.results] == [a["id"] for a in reversed(answer_rows)]
    assert all(type(r.faithfulness) is float for r in result.results)
    assert result.evaluator_models == ["eval-llm", "eval-embedding"]
    assert call.call_args.args[2] == [a["contexts"] for a in reversed(answer_rows)]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -.1, 1.1, None, True, "0.8"])
def test_invalid_metrics_are_not_replaced_by_scores(monkeypatch, answer_rows, bad):
    rows = [dict.fromkeys(phase.METRICS, .5) for _ in answer_rows]
    rows[0]["context_recall"] = bad
    evaluator(monkeypatch, rows)
    with pytest.raises(ValueError):
        phase.run_ragas_50q(answer_rows)


def test_short_evaluator_output_cannot_silently_zip(monkeypatch, answer_rows):
    evaluator(monkeypatch, [dict.fromkeys(phase.METRICS, .5)] * 49)
    with pytest.raises(ValueError, match="row count"):
        phase.run_ragas_50q(answer_rows)


@pytest.mark.parametrize("models", [[], [None], [" "]])
def test_missing_evaluator_models_are_rejected(monkeypatch, answer_rows, models):
    evaluator(monkeypatch, [dict.fromkeys(phase.METRICS, .5)] * 50, models)
    with pytest.raises(ValueError, match="evaluator_models"):
        phase.run_ragas_50q(answer_rows)


def test_reordered_source_rows_are_rejected(monkeypatch, answer_rows):
    rows = [{**a, **dict.fromkeys(phase.METRICS, .5)} for a in reversed(answer_rows)]
    evaluator(monkeypatch, rows)
    with pytest.raises(ValueError, match="source field"):
        phase.run_ragas_50q(answer_rows)


def test_empty_distributions_are_excluded_and_ties_are_stable():
    r = phase.RagasResult(2, "adversarial", "question", "answer", ["context"], "reference", .5,.5,.5,.5)
    a = phase.cluster_analysis([r])
    assert a["distribution_avg_scores"] == {"adversarial": .5}
    assert a["dominant_failure_distribution"] == "adversarial"
    assert sum(a["matrix"][m]["adversarial"] for m in phase.METRICS) == 1
    assert phase.cluster_analysis([])["dominant_failure_distribution"] is None
    r1 = phase.RagasResult(1, "adversarial", "another question", "answer", ["context"], "reference", .5,.5,.5,.5)
    assert [x["question_id"] for x in phase.bottom_10([r, r1])] == [1, 2]
    assert phase.bottom_10([]) == []


def test_diagnosis_does_not_treat_computed_totals_as_missing_retrieval():
    r = phase.RagasResult(31, "multi_hop", "Khách sạn 2 đêm, thanh toán bao nhiêu?",
                         "2.400.000 VNĐ", ["# Chính sách 2024\n1.200.000 VNĐ/đêm; sửa từ năm 2023."],
                         "2.400.000 VNĐ", 0,.5,1,1)
    row = phase.bottom_10([r])[0]
    assert "kết quả suy ra không cần xuất hiện" in row["diagnosis"]
    assert "Chuỗi số reference chưa xuất hiện" not in row["diagnosis"]
    assert "Contexts chứa cả 2023/2024" not in row["diagnosis"]
