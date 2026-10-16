# Nhóm thực hiện K4 Track 3A

Tên nhóm: Huy-Dat (tên làm việc; đổi theo tên nhóm chính thức nếu cần)

Repo chung: https://github.com/HuyHaiThanh/K4-Track-3A-Day24-Eval-Guard

Trưởng nhóm/người nộp được phân công: Nguyễn Văn Huy — 2A202602428

Ngày lab/deadline áp dụng: {{Ngày giờ theo thông báo lớp}} — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: chưa chốt bản nộp cuối. Snapshot chuẩn bị pipeline/answers: `48f3fd9`; các phase còn TODO.

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Văn Huy | 2A202602428 | Được giao: Phase A (Tasks 1–4); Phase C Tasks 9a, 10, 12; tích hợp và nộp bài. TODO chưa implement tại checkpoint. | tests/test_phase_a.py; các tests PII/suite/latency trong tests/test_phase_c.py; commit cá nhân bổ sung sau khi làm |
| 2 | NguyenQuocDat | 2A202602369 | Được giao: Phase B (Tasks 5–8); Phase C Tasks 9b, 11; phối hợp blueprint/review. TODO chưa implement tại checkpoint. | tests/test_phase_b.py; các tests input/output rails trong tests/test_phase_c.py; commit cá nhân bổ sung sau khi làm |

Người tích hợp/chạy batch/nộp link được giao: Nguyễn Văn Huy. Dat review judge và
rail decisions; Huy review sources/counts/statistics trước khi chạy batch chung.
Phân công không đồng nghĩa đã hoàn thành. Môi trường/answers có bằng chứng chạy
và phần AI hỗ trợ được mô tả bên dưới; chưa tự quy thành commit/đóng góp cá nhân.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows; Python 3.11.9; Visual Studio Build Tools 2022
17.14.37710.0, MSVC 14.44.35207. Annoy 1.17.3 đã build/cài thành công.
Virtualenv/dependencies/imports: `.venv`; cài full `requirements/requirements.txt`
với `constraints-core.txt`, bổ sung pin PyArrow 16.1.0 để tương thích NumPy 1.26.4.
`pip check`: No broken requirements found. Full imports và load `en_core_web_lg`
đã pass khi import PyTorch trước các thư viện NLP trên Windows.
Tests support sau cập nhật generation-only: 69 passed, 29 deselected; không phải
kết quả student tests Phase A/B/C.
Models/Qdrant/50 answers đã chuẩn bị: BGE-M3 encode đúng 1024 chiều;
BGE reranker đã load/inference local. Qdrant v1.9.7 chạy thật, collection
`lab24_production` có 125 chunks từ 26 tài liệu đọc được.
`artifacts/answers_50q.json`: 50 answers, factual=20/multi_hop=20/adversarial=10;
generation_mode=llm cho cả 50, generation_model=gpt-4o-mini-2024-07-18.
Enrichment của lượt retrieval dùng fallback vì lúc đó chưa có key thật; sau cập
nhật key, generation-only chạy trên cùng contexts gốc. Hai PDF scan không có
text layer được bỏ qua có cảnh báo, chưa OCR. Không sửa corpus hoặc fixtures.
Schema/nguồn/context được kiểm chứng bằng `scripts/check_preclass.py`; bằng chứng
môi trường trong `artifacts/preclass_environment.json`. Review và giải thích ở
`doc/PRECLASS_GUIDE.md`. Câu 21 còn thiếu khung lương trong retrieval; chưa thể
khẳng định toàn bộ answers đúng chỉ từ kiểm tra schema.
NeMo 0.10.0 đã cài và import thành công. Chưa chạy live input/output rails hoặc
RAGAS evaluation trong phạm vi chuẩn bị này.

AI hỗ trợ phần chuẩn bị: Codex review module m1–m5 có sẵn, sửa tích hợp, cài
môi trường, thêm regression tests/checker và hướng dẫn trong `doc/PRECLASS_GUIDE.md`.
Nhóm cần đọc/giải thích mã và khai đóng góp thực tế của từng người; thông tin
thành viên chưa được tự điền.

## Checkpoint sẵn sàng đầu buổi

Ngày kiểm tra: 12/10/2026 (Asia/Saigon). Support: 69 passed; toàn bộ offline:
71 passed, 24 failed, 3 integration deselected. 24 failures thuộc TODO student:
Phase A=6, B=6, C=12. Hai student cases pass tình cờ với stub; chưa hoàn thành phase.
`check_preclass.py` pass, answers hash giữ nguyên; không gọi API/generation lại.
Đã phân công hai thành viên: Huy A/PII/suite/latency/tích hợp; Dat B/input-output rails.
Mỗi người cần đọc assertions phần được giao và giải thích lại trước khi implement.
Bản đồ assertions và checklist: `doc/READINESS_CHECKPOINT.md`; evidence:
`artifacts/readiness_checkpoint.json`. Bản chuẩn bị đã chia commit: môi trường `85fbb32`, pipeline/tests `0e66686`,
answers/evidence `48f3fd9`. Nhóm dùng chung nhánh main và review khi tích hợp.

## INDIVIDUAL

### NguyenVanHuy-2A202602428

- Phần được giao: Tasks 1–4; pii_scan (9a), run_adversarial_suite (10), measure_p95_latency (12); tổng hợp failure_clusters.md và blueprint.md, kiểm tra/nộp repo chung.
- Trạng thái thực tế tại checkpoint: các hàm student vẫn TODO; chưa khai đã implement hoặc có commit cá nhân.
- Bằng chứng hiện có của repo: artifacts/answers_50q.json, artifacts/preclass_environment.json, artifacts/readiness_checkpoint.json. Bằng chứng cá nhân sẽ bổ sung sau khi làm.
- Cách kiểm tra phần được giao: tests/test_phase_a.py; tests PII/suite/latency trong tests/test_phase_c.py; runner A/C thật sau khi implement.
- Điều cần giải thích: evaluator metadata; nhóm yếu theo mean; expected không quyết định actual; hai warm-up ngoài samples và scope input layers.
- Điều đã học và đóng góp đã hoàn thành: chưa được học viên xác nhận; cập nhật bằng nội dung thực tế sau khi làm.
- Nguồn/AI hỗ trợ: Codex hỗ trợ chuẩn bị pipeline, kiểm tra readiness và lập phân công; tự kiểm chứng trước khi nhận là phần đã hiểu.

### NguyenQuocDat-2A202602369

- Phần được giao: Tasks 5–8; check_input_rail (9b), check_output_rail (11); bias_report.md và phần failure actions/monitoring trong blueprint phối hợp với Huy.
  - Trạng thái code: Tasks 5–8 và rails 9b/11 đã được implement với hỗ trợ Codex. Unit checks phần được giao: `tests/test_phase_b.py` cùng `test_input_uses_rail_decision` và `test_output_checks_supplied_answer` trong `tests/test_phase_c.py` đạt 18 passed.
  - Trạng thái đánh giá: Phase B live đã sinh `artifacts/judge_results.json` ngày 2026-10-16; `validate_phase_b` xác nhận 5 cặp, 10 calibration rows và đúng fixtures. `bias_report.md` ghi kết quả artifact này. Phase C runner chưa chạy vì các TODO PII/input-batch/latency ngoài phân công Đạt vẫn chặn kiểm tra hoàn thành. Blueprint chỉ ghi đề xuất failure actions/monitoring, workflow chưa được triển khai.
  - Kiểm tra rộng: `python -m pytest -q --tb=no` chưa đạt (14 failed, 33 errors, 54 passed, 3 deselected); các lỗi quan sát được gồm Phase A, PII/input batch/latency Phase C và report/preclass fixtures, ngoài hai rail 9b/11 được giao.
- Điều cần giải thích khi báo cáo: quy đổi winner/scores sau swap; A/B/tie khác label 0/1; không leak human labels; đọc quyết định rail thay vì suy từ từ khóa refusal.
- Điều đã học và đóng góp đã hoàn thành: chưa được học viên cung cấp; cần cập nhật bằng nội dung thực tế của học viên.
  - Nguồn/AI hỗ trợ: Codex hỗ trợ implementation, cập nhật báo cáo và kiểm tra offline; nội dung học được cá nhân chưa được học viên cung cấp.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
