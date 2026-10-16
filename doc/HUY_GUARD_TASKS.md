# Phần guardrails của Huy — có thể làm độc lập

Đã implement Tasks 9a/10/12 trong src/phase_c_guard.py. Tasks 9b/11 đã tích hợp; full Phase C live evidence ở artifacts/guard_results.json. Artifact đạt attacks 19/20, clean 8/8, outputs 4/4; input guard P95 922.3 ms vượt budget 500 ms.

- pii_scan dùng analyzer và anonymizer thật khi không inject engines. Trả entity type/text/score/start/end và text đã redact. Phạm vi lớp này: VN_CCCD (CCCD/CMND), VN_PHONE/PHONE_NUMBER, EMAIL_ADDRESS. English PERSON/DATE/foreign-ID recognizers không quyết định block ở lớp này do false positives trên tiếng Việt; NeMo policy phải xử lý yêu cầu lấy dữ liệu cá nhân ngoài phạm vi đó.
- run_adversarial_suite nhận inputs bất kỳ, giữ ids/category/input/expected, quét PII rồi await NeMo nếu chưa chặn. actual chỉ phụ thuộc engines, expected chỉ dùng tính passed. Không sửa input, không có luật đặc biệt theo id hoặc expected. Khởi tạo engines một lần và chỉ dùng một event loop cho batch.
- measure_p95_latency tạo/reuse engines trước đo, chạy 2 warm-up rồi thu đúng n_runs samples, cycle inputs. Luôn đo cả Presidio và NeMo input ngay cả khi PII block; request thực ở suite thì được short-circuit. Thời gian ms dùng perf_counter, input_guard_ms cộng từng sample, thống kê qua summarize_latency. Submission cần n_runs≥20; clock giả trong tests không phải benchmark runtime.

Hai synchronous runners báo lỗi rõ nếu gọi bên trong event loop đang hoạt động, trước khi tạo coroutine/engines. Engine errors truyền lên caller; không tự coi safe/allowed khi có lỗi.

## Tự review và smoke

Lần Presidio thật đầu phát hiện đủ CCCD/CMND/phone/email nhưng English NER gán 7/8 câu policy sạch thành PERSON hoặc foreign ID. Đã sửa theo phạm vi entity types của Task 9a và thêm regression test. Kết quả cuối lưu ở artifacts/pii_smoke.json, scope local_presidio_only_not_full_guard; đây là test trên chuỗi giả lập, không phải dữ liệu cá nhân thật hoặc guard_results.json.

Tests độc lập gồm: expected/category không quyết định actual; source không bị đổi; PII block không làm latency short-circuit; 2 warm-up ngoài 20 samples; input count sai; active event loop; empty batch; false positives English NER. Các tests starter tương ứng cũng phải pass.

## Tích hợp tiếp

check_input_rail và check_output_rail đã tích hợp theo interface hiện tại; test Phase C và Huy guard tasks đạt 22 passed. Batch live đọc 20 attacks, 8 clean, 4 output cases và 20 latency samples; artifact giữ từng kết quả và rail decision.

Blueprint có kết quả live: input guard P50 679.3 ms, P95 922.3 ms, P99 1075.5 ms; Presidio P95 10.7 ms và NeMo input P95 914.4 ms. `latency_budget_ok` là false; đây chỉ là input layers sequential, không đại diện full request hoặc production.
