# Blueprint CI/CD cho RAG và guardrails

Nhóm: {{Tên nhóm}}

Người phụ trách: {{Họ tên và MSSV}}

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: {{created_at}}; guard models: {{metadata.models.guard}}.
Models generation/evaluator/judge từ A/B: {{models theo từng vai trò và nguồn report}}.

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

Failure actions / monitoring (đề xuất, chưa triển khai hoặc chạy): request thực đi lần lượt
qua Presidio, NeMo input, RAG và NeMo output; nếu một rail chặn, dừng request và không
chuyển nội dung bị chặn sang bước sau. Nếu guard/provider lỗi hoặc timeout, fail closed
cho luồng nhạy cảm, trả lỗi an toàn và không tự bỏ qua guard; chỉ cân nhắc fallback sau
đánh giá rủi ro và quyết định có ghi nhận. Không ghi prompt/answer thô hoặc secrets vào
logs; lưu tối thiểu timestamp, stage, decision, rule/model version, latency và request ID
đã khử định danh, với quyền truy cập hạn chế. Secrets lấy từ môi trường triển khai, không
đưa vào artifact hay báo cáo.

Theo dõi tỷ lệ allow/block theo stage, lỗi/timeout, latency p50/p95/p99 và false-positive
qua tập clean có nhãn; cảnh báo khi ngưỡng CI hoặc ngưỡng vận hành được nhóm chốt bị vi phạm.
Lấy mẫu định kỳ từ traffic đã khử định danh theo chính sách lưu giữ, review false positives
với người phụ trách guard, rồi điều chỉnh rule/prompt/model chỉ qua bộ hồi quy attacks,
clean controls và review drift. Các ngưỡng vận hành, retention, reviewer và kênh cảnh báo
còn phải được nhóm xác định. Chưa có metrics hay kết quả live để báo cáo.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: {{n_samples}}; warm-up: {{warmup_runs}};
phương pháp: {{percentile_method}}.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | {{p50}} | {{p95}} | {{p99}} | {{Kết quả đo Task 12}} |
| NeMo input | {{p50}} | {{p95}} | {{p99}} | {{Kết quả đo Task 12}} |
| Input guard sequential | {{p50}} | {{p95}} | {{p99}} | {{Kết quả đo Task 12}} |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: {{giá trị và bool}}.
{{Nêu bottleneck nếu vượt target. Nếu chưa đo các phần ngoài phạm vi, giữ “chưa đo”
và nêu kế hoạch lấy mẫu/warm-up/timestamps; nếu đã đo thì thay bằng số và phương pháp.}}

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.
{{Đề xuất lệnh job và cách script trả nonzero khi không đạt. MIN_* là biến đề
xuất, không tự làm quality gate nếu runner chưa kiểm tra ngưỡng. Ghi rõ workflow
chưa triển khai, hoặc dẫn bằng chứng nếu nhóm thực sự đã triển khai.}}

## Monitoring và cải tiến

{{Nêu metric, ngưỡng cảnh báo, cách lấy samples, xử lý false positives, drift,
privacy và người xử lý. Dùng kết quả thật và ghi giới hạn của bộ 50/20/8/4.}}

RAGAS mean/worst distribution: {{giá trị}}.
Cohen’s κ: {{giá trị}}.
Attacks passed: {{số lượng}}/20; clean false_positive_rate: {{giá trị}}.
{{Nêu 3–5 câu cải tiến có thể kiểm tra, gắn với bằng chứng của nhóm.}}
