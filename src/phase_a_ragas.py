from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
import math
import re
from collections.abc import Mapping
from numbers import Real
import os
import sys
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, ANSWERS_PATH, ARTIFACTS_DIR
from src.experiment_support import write_json

Distribution = str  # "factual" | "multi_hop" | "adversarial"

DIAGNOSTIC_TREE = {
    "faithfulness": ("Kiểm tra các khẳng định/điều kiện trong answer có được nguồn hỗ trợ",
                     "Đối chiếu từng claim với nguồn; trả lời rõ phần chưa có dữ liệu thay vì suy đoán"),
    "answer_relevancy": ("Kiểm tra answer có đáp ứng từng ý, đại lượng và điều kiện được hỏi",
                         "Tách các ý cần trả lời; kiểm tra mỗi ý có context trước generation"),
    "context_precision": ("Kiểm tra thứ tự và mức liên quan của từng context được lấy",
                          "Review RRF/rerank, giảm parent trùng chủ đề và ưu tiên nguồn phù hợp câu hỏi"),
    "context_recall": ("Kiểm tra coverage của contexts so với các ý trong reference",
                       "Truy xuất theo từng ý của câu hỏi nhiều bước và đa dạng nguồn trước chọn top-k"),
}


@dataclass
class RagasResult:
    question_id: int
    distribution: Distribution
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def avg_score(self) -> float:
        return (self.faithfulness + self.answer_relevancy +
                self.context_precision + self.context_recall) / 4

    @property
    def worst_metric(self) -> str:
        scores = {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
        }
        return min(scores, key=scores.get)


# ─── Đã implement sẵn ────────────────────────────────────────────────────────

@dataclass
class RagasEvaluation:
    """Task 2 output: measured rows plus model identifiers reported by m4."""
    results: list[RagasResult]
    evaluator_models: list[str]

def load_test_set_50q(path: str = TEST_SET_PATH) -> list[dict]:
    """Load 50q test set với 3 distributions."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_answers(path: str = ANSWERS_PATH) -> list[dict]:
    """Load pre-generated answers từ setup_answers.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"answers_50q.json không tìm thấy tại {path}\n"
            "→ Chạy trước: python scripts/setup_answers.py --live"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict]) -> dict:
    """Provided exporter: preserve the student-produced Task 3 rows verbatim."""
    per_dist: dict[str, dict] = {}
    for dist in ["factual", "multi_hop", "adversarial"]:
        subset = [r for r in results if r.distribution == dist]
        if subset:
            per_dist[dist] = {
                "count": len(subset),
                "faithfulness":      sum(r.faithfulness for r in subset) / len(subset),
                "answer_relevancy":  sum(r.answer_relevancy for r in subset) / len(subset),
                "context_precision": sum(r.context_precision for r in subset) / len(subset),
                "context_recall":    sum(r.context_recall for r in subset) / len(subset),
                "avg_score":         sum(r.avg_score for r in subset) / len(subset),
            }

    report = {
        "total_questions": len(results),
        "per_question": [asdict(r) for r in results],
        "per_distribution": per_dist,
        "failure_clusters": clusters,
        "bottom_10": bottom,
    }
    return report


def save_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict],
                        path: str = os.path.join(ARTIFACTS_DIR, "ragas_50q.json")) -> None:
    write_json(path, build_phase_a_report(results, clusters, bottom))



# ─── Tasks 1-4: Sinh viên implement ──────────────────────────────────────────

DISTRIBUTIONS = ("factual", "multi_hop", "adversarial")
METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def group_by_distribution(test_set: list[dict]) -> dict[str, list[dict]]:
    """Task 1: preserve original records/order in all three groups."""
    groups = {distribution: [] for distribution in DISTRIBUTIONS}
    for item in test_set:
        distribution = item["distribution"]
        if distribution not in groups:
            raise ValueError(f"Unknown distribution: {distribution}")
        groups[distribution].append(item)
    return groups


def _metric_value(record, metric: str) -> float:
    value = record[metric] if isinstance(record, Mapping) else getattr(record, metric)
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{metric} must be a numeric score, not a placeholder")
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{metric} must be finite and in [0, 1]")
    return value


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: keep source identity and evaluator metadata from the same call."""
    if len(answers) != 50:
        raise ValueError("Phase A requires exactly 50 saved answers")
    ids = [a["id"] for a in answers]
    if any(type(qid) is not int or qid <= 0 for qid in ids) or len(set(ids)) != 50:
        raise ValueError("Answer ids must be distinct positive integers")
    group_by_distribution(answers)
    from src.m4_eval import evaluate_ragas
    raw = evaluate_ragas(
        [a["question"] for a in answers], [a["answer"] for a in answers],
        [a["contexts"] for a in answers], [a["ground_truth"] for a in answers])
    per_question = raw["per_question"]
    if len(per_question) != len(answers):
        raise ValueError("Evaluator row count differs from answer count; refusing to truncate zip")
    models = raw.get("metadata", {}).get("evaluator_models")
    if not isinstance(models, list) or not models or any(
            not isinstance(model, str) or not model.strip() for model in models):
        raise ValueError("m4 must declare its actual evaluator_models")
    results = []
    for answer, measured in zip(answers, per_question):
        # When m4 supplies row identity, check it before positional alignment.
        for name in ("question", "answer", "contexts", "ground_truth"):
            actual = measured.get(name) if isinstance(measured, Mapping) else getattr(measured, name, None)
            if actual is not None and actual != answer[name]:
                raise ValueError(f"Evaluator reordered or changed source field {name}")
        results.append(RagasResult(
            question_id=answer["id"], distribution=answer["distribution"],
            question=answer["question"], answer=answer["answer"],
            contexts=list(answer["contexts"]), ground_truth=answer["ground_truth"],
            **{metric: _metric_value(measured, metric) for metric in METRICS}))
    return RagasEvaluation(results, list(models))


def _diagnose(result: RagasResult) -> tuple[str, str]:
    """Evidence-linked investigation hints, not an automatic root-cause verdict."""
    metric = result.worst_metric
    hint, fix = DIAGNOSTIC_TREE[metric]
    titles = [line.lstrip("# ").strip() for c in result.contexts
              for line in c.splitlines() if line.startswith("# ")]
    evidence = f"Q{result.question_id}: {result.question} Answer: {result.answer[:240]}"
    evidence += f" Contexts={len(result.contexts)}; nguồn: {', '.join(dict.fromkeys(titles)) or 'xem per_question.contexts'}."
    versions = (any("2023" in title for title in titles)
                and any("2024" in title for title in titles))
    if versions:
        evidence += " Contexts chứa cả 2023/2024; cần đọc trạng thái/thay thế, không suy ra bản áp dụng từ điểm."
        fix += "; giữ policy cũ trong corpus, xác định bản áp dụng từ hiệu lực/thay thế của nguồn"
    if "tổng" in result.question.lower() or (
            re.search(r"\d", result.question) and any(
                word in result.question.lower() for word in ("triệu", "đêm", "phạt"))):
        evidence += (" Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; "
                     "kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu.")
    diagnosis = f"{metric}={getattr(result, metric):.4f} là chỉ báo điều tra. {hint}. {evidence} Chưa kết luận nguyên nhân chỉ từ metric."
    return diagnosis, fix


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: stable ranking; retain full measured precision before export."""
    output = []
    for rank, result in enumerate(sorted(results, key=lambda r: (r.avg_score, r.question_id))[:10], 1):
        diagnosis, fix = _diagnose(result)
        output.append({"rank": rank, "question_id": result.question_id,
                       "distribution": result.distribution, "question": result.question,
                       "avg_score": result.avg_score, "worst_metric": result.worst_metric,
                       "diagnosis": diagnosis, "suggested_fix": fix})
    return output


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: count every row, select weakest nonempty group by its mean."""
    matrix = {metric: {d: 0 for d in DISTRIBUTIONS} for metric in METRICS}
    totals = {d: 0.0 for d in DISTRIBUTIONS}
    counts = {d: 0 for d in DISTRIBUTIONS}
    for result in results:
        if result.distribution not in counts:
            raise ValueError(f"Unknown distribution: {result.distribution}")
        matrix[result.worst_metric][result.distribution] += 1
        totals[result.distribution] += result.avg_score
        counts[result.distribution] += 1
    means = {d: totals[d] / counts[d] for d in DISTRIBUTIONS if counts[d]}
    weakest = min(means, key=means.get) if means else None
    dominant = max(METRICS, key=lambda m: sum(matrix[m].values())) if results else None
    insight = (f"Nhóm {weakest} có avg_score mean thấp nhất ({means[weakest]:.4f}); "
               f"{dominant} là worst metric của {sum(matrix[dominant].values())}/{len(results)} câu. "
               "Matrix đếm mọi câu, không phải số failures; cần đọc nguồn/answer/reference để chẩn đoán."
               if results else "Không có dữ liệu; chưa thể xác định nhóm yếu hoặc metric chủ đạo.")
    return {"matrix": matrix, "distribution_avg_scores": means,
            "dominant_failure_distribution": weakest, "dominant_failure_metric": dominant,
            "insight": insight}


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))
