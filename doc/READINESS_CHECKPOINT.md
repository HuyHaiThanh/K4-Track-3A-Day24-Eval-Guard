# Checkpoint sẵn sàng — 12/10/2026

Kỹ thuật đã sẵn sàng để bắt đầu Phase A. Đã phân công hai thành viên Nguyễn Văn Huy (2A202602428) và NguyenQuocDat (2A202602369); tên làm việc Huy-Dat. Đây là kiểm tra đầu buổi, không phải xác nhận hoàn thành ba phase.

## Kết quả thực tế

| Kiểm tra | Kết quả |
|---|---|
| check_preclass | Pass; Python 3.11.9, pip check/imports/spaCy/Qdrant/answers hợp lệ |
| Support | 69 passed, 29 deselected |
| Toàn bộ tests offline | 71 passed, 24 failed, 3 integration deselected |
| Student Phase A | 6 failed / 6 cases |
| Student Phase B | 6 failed, 2 passed / 8 cases |
| Student Phase C | 12 failed / 12 cases |
| Answers | 50 LLM answers; 20 factual / 20 multi_hop / 10 adversarial; giữ nguyên hash |
| Qdrant | 125 indexed points; không indexing hoặc generation lại |
| Artifacts A/B/C | Chưa có, đúng trạng thái chưa implement/chạy experiments |

29 cases bị deselect khi dùng -m support gồm 26 student cases và 3 integration cases. Hai student cases pass là kappa với expected=0 và bias_report([]); stub mặc định tình cờ thỏa assertion. Không dùng hai pass này để kết luận Phase B hoàn thành.

## Assertion → hàm cần implement

| Phase/task | Hàm TODO | Test | Điều kiện cần giải thích |
|---|---|---|---|
| A/1 | group_by_distribution | test_group_exact_counts | Ba keys; số câu 20/20/10, không phải ba list rỗng |
| A/2 | run_ragas_50q | test_ragas_adapter_preserves_rows | Gọi evaluator đúng một lần; giữ đủ 50 ids/thứ tự/questions; 4 metric và evaluator_models lấy từ m4 |
| A/3 | bottom_10 | test_bottom_nonempty_sorted_complete; test_bottom_capped_at_ten | Tối đa 10 rows; với 5 input trả 5; avg_score tăng dần, rank liên tục, diagnosis/fix không rỗng |
| A/4 | cluster_analysis | test_cluster_matrix; test_weakest_distribution_is_quality_not_size | Matrix đếm worst_metric; nhóm yếu chọn bằng mean thấp nhất, không chọn nhóm đông nhất |
| B/5 | pairwise_judge | test_pairwise_uses_json_judge | Gọi mock SDK một lần, prompt có reference, JSON winner/reasoning/scores |
| B/6 | swap_and_average | test_swap_conversion_and_calls (2 cases) | Hai lượt A/B và B/A; quy winner và scores lượt hai về A/B gốc; bất đồng thành tie |
| B/7 | cohen_kappa | test_kappa_exact (3 cases) | Agreement=1, đối lập=-1, case độc lập=0; stub 0 không đủ |
| B/8 | bias_report | test_bias_known_counts; test_bias_empty | Case mẫu 2 judgments, 1 inconsistent: position=.5, verbosity=1; có interpretation; xử lý list rỗng |
| C/9a | pii_scan | test_pii_detect_and_redact (4 cases); test_pii_clean | Detect/redact CCCD, CMND, VN phone, email; input sạch giữ nguyên và vẫn gọi analyzer |
| C/9b | check_input_rail | test_input_uses_rail_decision (2 cases) | Await rail một lần, chỉ input rail; đọc quyết định stop, không đoán từ từ khóa xin lỗi/không thể |
| C/11 | check_output_rail | test_output_checks_supplied_answer (2 cases) | Gửi answer có sẵn trong messages; chỉ output rail; giữ answer sạch hoặc thay output bị chặn |
| C/10 | run_adversarial_suite | test_input_suite_exact_rows; test_attack_and_clean_control | Đủ 28 rows = 20 attacks + 8 clean; giữ ids/input; actual từ engines, expected chỉ đối chiếu; mock NeMo được await 24 lần vì 4 attacks bị PII chặn trước |
| C/12 | measure_p95_latency | test_latency_real_warmup_and_sample_count | 2 warm-up + 20 timed samples; mỗi layer gọi 22 lần; p95 mock=4ms chỉ là kiểm tra phép tính, không phải latency thật |

Tests chi tiết nằm trong tests/test_phase_a.py, tests/test_phase_b.py, tests/test_phase_c.py. TODO tương ứng trong src/phase_a_ragas.py, src/phase_b_judge.py, src/phase_c_guard.py. Không sửa expected/assertions để biến stub thành pass.

## Phiên bản và nguồn dùng chung

Base commit: b9f8d5b53bc4f94899aa30fdc52c30be0e96eb6d. Đó là base commit của starter tại lúc kiểm tra; bản chuẩn bị sau đó được commit thành 85fbb32 (môi trường), 0e66686 (pipeline/tests), 48f3fd9 (answers/evidence). Nhóm dùng main của repo chung, pull trước khi làm và review thay đổi trước khi tích hợp.

Answers SHA-256: 9b30fefda5717851744ff2ff4e59f51996158d1c8f3d38715d6abe7257728016.

artifacts/readiness_checkpoint.json lưu counts, nguồn và fingerprints src/scripts/tests/fixtures/requirements/config tại checkpoint. Không chứa key. Không sinh lại answers giữa Phase A; nếu thay pipeline/answers sau này phải ghi phiên bản và chạy lại evaluation tương ứng.

## Phân công hai thành viên

| Người | Tasks | Source/test cần mở | Báo cáo/tích hợp |
|---|---|---|---|
| Nguyễn Văn Huy — 2A202602428 | A: 1–4; C: 9a, 10, 12 | phase_a_ragas.py + test_phase_a.py; PII/suite/latency trong phase_c_guard.py + test_phase_c.py | failure_clusters.md; tổng hợp blueprint; checker, batch A/C và nộp chung |
| NguyenQuocDat — 2A202602369 | B: 5–8; C: 9b, 11 | phase_b_judge.py + test_phase_b.py; input/output rails trong phase_c_guard.py + test_phase_c.py | bias_report.md; phần failure actions/monitoring của blueprint; batch B, review C |

Quỹ kỹ thuật phần được giao xấp xỉ Huy 55 điểm, Dat 45 điểm theo rubric; đây là cân bằng phân công, không phải cách tính điểm cá nhân của khóa học. Không khai TODO như phần đã hoàn thành.

Phase C cùng một file: Huy sửa đúng ba hàm 9a/10/12, Dat sửa hai hàm async 9b/11; thống nhất việc merge để không ghi đè cả file. Huy gọi input rail qua giao diện của Dat; output rail do Dat kiểm tra trên answer có sẵn. Nếu dùng branches, merge source trước batch live và dùng đúng snapshot chung.

Mỗi người tự giải thích assertions trong bảng phía trên, sau đó review chéo. Support pass không xác nhận học viên đã hiểu.

## Bắt đầu Phase A

Đọc answers_50q.json theo question → contexts → answer → ground_truth. Câu 21 thiếu khung lương trong contexts, nên có failure retrieval/coverage để điều tra; câu 41 đã ưu tiên policy 2024 sau review prompt. Đây là quan sát thủ công, chưa phải metric RAGAS.

Implement Tasks 1–4, chạy tests/test_phase_a.py offline, rồi chạy runner A --live trên đúng tập answers hiện tại. Support tests và schema validation không thay thực nghiệm RAGAS.
