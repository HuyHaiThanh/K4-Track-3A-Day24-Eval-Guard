# Blueprint CI/CD cho RAG và guardrails — Huy-Dat

Người tổng hợp: Nguyễn Văn Huy — 2A202602428, có Codex hỗ trợ. NguyenQuocDat bổ sung judge/rails sau khi tích hợp. Đây là đề xuất, chưa triển khai workflow CI/CD.

## Bằng chứng hiện có và phần chờ

Phase A dùng artifacts/ragas_50q.json, timestamp 2026-10-16T02:07:49.789793+00:00; generation gpt-4o-mini-2024-07-18, evaluator gpt-4o-mini + text-embedding-3-small. Overall avg_score 0.8131, nhóm yếu multi_hop 0.7591. Answers/fixture giữ nguyên hashes trong metadata.

Phase B live đã chạy 2026-10-16T04:13:20Z với judge `gpt-4o-mini`: 5/5 pairwise decisions giữ nguyên candidate sau swap; κ=1.00 trên 10 calibration labels. Chi tiết và giới hạn mẫu ở `doc/reports/bias_report.md`, artifact là `artifacts/judge_results.json`.

Phase C code đã tích hợp và offline tests pass; full live `guard_results.json` chưa có. Vì vậy attacks/clean/output pass counts, false-positive rate, guard model IDs và latency thực tế vẫn chưa đo. Chỉ điền các trường đó từ artifact của runner C; không đoán từ `JUDGE_MODEL` hoặc model generation. Tests mock không thay số đo live.

## Kiến trúc và failure action

Request: input → Presidio → NeMo input → RAG → NeMo output → response. PII được phát hiện/redact trước xử lý tiếp; suite lab chặn input có PII. Nếu PII chặn thì request thật không cần gọi NeMo. NeMo quyết định từ activated rails; không dùng từ khóa xin lỗi/không thể để suy ra blocked. Output sạch giữ nguyên; output nhạy cảm được thay/redact bởi output rail.

Failure actions / monitoring (đề xuất, chưa triển khai hoặc chạy): nếu một rail chặn,
dừng request và không chuyển nội dung bị chặn sang bước sau. Lỗi engine/API phải được
truyền lên caller và xử lý fail-closed với thông báo dịch vụ tạm không sẵn sàng; không tự
coi allowed/safe hoặc bỏ qua guard. Chỉ cân nhắc fallback sau review rủi ro và quyết định
có ghi nhận.

Prompt calibration không nhận `human_label`/`human_note`. Secrets lấy từ `.env` hoặc biến
môi trường và không commit. Log production chỉ giữ request ID đã khử định danh, stage,
entity types/counts, quyết định, timing và model/source version; không lưu raw PII, prompt,
answer, context hay key. `artifacts/pii_smoke.json` chỉ chứa chuỗi PII giả lập trong fixture.

Theo dõi tỷ lệ allow/block theo stage, engine/API errors và timeout, latency p50/p95/p99,
false-positive rate trên clean controls và drift theo model/source hashes. Cảnh báo khi
ngưỡng CI hoặc ngưỡng vận hành đã được nhóm thống nhất bị vi phạm. Lấy mẫu định kỳ theo
chính sách lưu giữ, review false positives với người phụ trách guard, rồi chỉ đổi
rule/prompt/model sau khi chạy lại attacks, clean controls và review drift. Ngưỡng vận
hành, retention, reviewer và kênh cảnh báo còn phải được nhóm xác định; chưa triển khai
monitoring production.

## Phạm vi latency và trạng thái

Task 12 đã implement thu mẫu, reuse engines, hai warm-up thật rồi đo sequential cả Presidio và NeMo input cho từng sample, kể cả khi PII chặn. Thời gian dùng perf_counter; tổng mỗi sample bằng hai thành phần. summarize_latency nội suy tuyến tính tại (n-1)*q. Batch nộp cần ít nhất 20 timed samples; warm-up không tính vào mẫu. Unit tests kiểm call counts và percentile bằng clock giả.

| Layer/scope | P50 | P95 | P99 | Trạng thái |
|---|---|---|---|---|
| Presidio | chưa đo | chưa đo | chưa đo | Smoke test chức năng riêng; chưa benchmark |
| NeMo input | chưa đo | chưa đo | chưa đo | Chờ Phase C live batch |
| Input guard sequential | chưa đo | chưa đo | chưa đo | Chờ chạy Task 12 với rail thật, ≥20 samples + 2 warm-up |
| RAG | chưa đo | chưa đo | chưa đo | Không suy latency từ thời gian batch evaluation |
| NeMo output | chưa đo | chưa đo | chưa đo | Chờ task 11; ngoài scope Task 12 |
| Full guard/request short-circuit | chưa đo | chưa đo | chưa đo | Đo riêng sau tích hợp, không dùng input_guard_ms thay thế |

Budget mục tiêu 500ms; budget_ok hiện chưa xác định. Không sử dụng 2ms/4ms trong tests mock như số đo runtime. Sau khi được phép chạy batch live, dùng runner C `--live --latency-samples 20` một lần; đối chiếu raw samples, scope/model IDs/warm-up rồi điền bảng và bottleneck thật. Nếu đo vượt budget phải ghi số thật và phân tích, không sửa số.

## CI gates đề xuất

1. Offline job: pytest không gọi mạng; mọi student/support tests phải pass sau khi hoàn tất cả ba phase.
2. Evidence job: check_lab.py kiểm schema, hashes và hợp đồng. Thiếu report hoặc còn TODO làm job fail; checker không tự tạo artifacts hay gọi API.
3. Quality job riêng: đề xuất kiểm faithfulness mean ≥0.75 và avg_score ≥0.65 trên 50 câu; attacks ≥18/20, clean 8/8 allowed, bốn output cases đúng. Lab bắt buộc vẫn attacks ≥15/20; bonus ≥18/20 kèm clean đạt. Full guard P95 <500ms chỉ áp dụng sau khi đo đúng scope full guard.
4. Quality gate bổ sung chưa được implement trong CI: cần script đọc artifact, trả nonzero khi dưới ngưỡng hoặc thiếu measurement. Khai báo MIN_* đơn thuần không tạo gate. Không đặt scheduled live batch chạy lặp khi artifacts đã đủ mà không có thay đổi/lý do.

## Monitoring, phân tích và người xử lý

Huy theo dõi coverage multi-hop, lỗi số học và latency samples; Dat theo dõi κ, swap inconsistency, input/output rails và false positives. Các cảnh báo đề xuất: clean bị chặn >0 trong bộ 8 câu; attacks <18/20 trong gate đề xuất; drift điểm RAGAS so baseline hoặc model/source hashes thay đổi mà report chưa cập nhật. Ngưỡng lab/gate tách biệt; chưa có monitoring deployment.

Lấy mẫu đánh giá có reference, human review cho các case bất đồng evaluator; lưu phiên bản prompt/model/corpus và kiểm soát quyền xem evidence. Tập 50/20/8/4 nhỏ, cần held-out controls và review định kỳ trước kết luận production. Sau mỗi lỗi thật, bổ sung regression case phù hợp thay vì chỉ thêm keyword cho fixture.

## Ưu tiên cải tiến có thể kiểm chứng

- Q21/Q33/Q35: truy xuất đủ nguồn theo từng ý; Q33 còn phải kiểm công thức 12÷3 trước cộng phép.
- Q9: nguồn đã có nhưng generation từ chối; kiểm span liên quan trước nói không tìm thấy.
- Q28/Q31/Q38: đối chiếu NLI/arithmetic trace hoặc human labels khi faithfulness thấp nhưng phép tính được hỗ trợ; không sửa score bằng tay.
- Kiểm clean controls song song attacks để phát hiện always-block và chặn nhầm tên công nghệ/khung lương.
- Sau Phase C live batch, ghi kết quả attacks, clean, output và latency thật; blueprint là đề xuất monitoring, không phải bằng chứng đã deploy.
