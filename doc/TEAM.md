# Nhóm thực hiện K4 Track 3A

Tên nhóm: Huy-Dat (tên làm việc; đổi theo tên nhóm chính thức nếu cần)

Repo chung: https://github.com/HuyHaiThanh/K4-Track-3A-Day24-Eval-Guard

Trưởng nhóm/người nộp được phân công: Nguyễn Văn Huy — 2A202602428

Ngày lab cụ thể không được ghi trong checkout. Deadline mặc định theo RULES.md là 23:59 ngày diễn ra lab, Asia/Ho_Chi_Minh; đối chiếu ngày với thông báo lớp.

Commit dùng để chấm: chưa nộp; trưởng nhóm Nguyễn Văn Huy được phân công push và ghi SHA sau khi chốt. Branch `dat` đã pull `origin/main` tại checkout này; không xem merge local là bằng chứng đã nộp.

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Văn Huy | 2A202602428 | Được giao: Phase A (Tasks 1–4); Phase C Tasks 9a, 10, 12; tích hợp và nộp bài. Đã hoàn thiện A, 9a/10/12; AI hỗ trợ được kê khai. Full C live batch đã chạy; latency input guard P95 922.3 ms vượt budget 500 ms. | artifacts/ragas_50q.json; artifacts/guard_results.json; doc/reports/failure_clusters.md; tests/test_huy_guard_tasks.py; artifacts/pii_smoke.json; doc/PHASE_A_GUIDE.md |
| 2 | NguyenQuocDat | 2A202602369 | Được giao: Phase B (Tasks 5–8); Phase C Tasks 9b, 11; phối hợp blueprint/review. Code và Phase B live đã hoàn thành với Codex hỗ trợ. | artifacts/judge_results.json; doc/reports/bias_report.md; tests/test_phase_b.py; tests/test_phase_c.py; commit `c962a79` |

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
NeMo 0.10.0 đã cài và import thành công; MSVC 19.44 đã build được `annoy`
(`cl.exe` tại `C:\Program\VC\Tools\MSVC\14.44.35207`). Installer trả mã 3010,
Windows báo pending reboot. Phase A RAGAS live evidence có trong
`artifacts/ragas_50q.json`; Phase B judge live evidence có trong
`artifacts/judge_results.json`. Phase C live evidence có trong
`artifacts/guard_results.json`; PII smoke là kiểm tra riêng, không thay batch này.

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
- Trạng thái cập nhật 16/10: Phase A đã implement, chạy RAGAS thật và qua focused offline tests. Tasks 9a/10/12 đã implement; Phase C live đạt 19/20 attacks, clean 8/8, outputs 4/4. Input guard P95 922.3 ms vượt budget 500 ms; artifacts có raw 20 samples.
- Bằng chứng: artifacts/ragas_50q.json, doc/reports/failure_clusters.md, tests/test_huy_guard_tasks.py, artifacts/pii_smoke.json, doc/HUY_GUARD_TASKS.md; lịch sử commit phần của Huy. Không khai results B/C khi chưa chạy thật.
- Cách kiểm tra phần được giao: `tests/test_phase_a.py`, `tests/test_phase_a_edge_cases.py`, PII/suite/latency trong `tests/test_phase_c.py`, và `tests/test_huy_guard_tasks.py`.
- Điều cần giải thích: evaluator metadata; nhóm yếu theo mean; expected không quyết định actual; hai warm-up ngoài samples và scope input layers.
- Điều đã học và đóng góp đã hoàn thành: chưa được học viên xác nhận; cập nhật bằng nội dung thực tế sau khi làm.
- Nguồn/AI hỗ trợ: Codex hỗ trợ chuẩn bị pipeline, kiểm tra readiness và lập phân công; tự kiểm chứng trước khi nhận là phần đã hiểu.

### NguyenQuocDat-2A202602369

- Phần được giao: Tasks 5–8; check_input_rail (9b), check_output_rail (11); bias_report.md và phần failure actions/monitoring trong blueprint phối hợp với Huy.
- Trạng thái code: Tasks 5–8 và rails 9b/11 đã implement với hỗ trợ Codex. Phase B live đã sinh `artifacts/judge_results.json`; `validate_phase_b` xác nhận 5 cặp, 10 calibration rows và đúng fixtures. `bias_report.md` ghi kết quả artifact này.
- Trạng thái Phase C: hai rail 9b/11 cùng Tasks 9a/10/12 đã qua offline tests; live batch đạt attacks 19/20, clean 8/8, outputs 4/4 với guard model gpt-4o-mini. Off-topic case 11 bị bỏ lọt; xem raw results trong `artifacts/guard_results.json`.
- Kiểm tra rộng sau cập nhật: `python -m pytest -q --basetemp .pytest-tmp-final-phase-c` đạt 126 passed, 3 deselected. `scripts/check_lab.py` exit 0. Input guard P95 là 922.3 ms so với budget 500 ms; chưa push/nộp.
- Điều cần giải thích khi báo cáo: quy đổi winner/scores sau swap; A/B/tie khác label 0/1; không leak human labels; đọc quyết định rail thay vì suy từ từ khóa refusal.
- Điều đã học và đóng góp đã hoàn thành: phần reflection cá nhân cần học viên xác nhận; các nội dung kỹ thuật đã thực hành gồm quy đổi winner/scores sau swap, Cohen’s κ với nhãn binary và đọc activated rail decisions từ `activated_rails`.
  - Nguồn/AI hỗ trợ: Codex hỗ trợ implementation, cập nhật báo cáo và kiểm tra offline; nội dung phản ánh trải nghiệm cá nhân do học viên xác nhận.

## Cập nhật sau khi nộp

Chưa nộp lên GitHub và chưa có thay đổi sau deadline được khai báo. Trưởng nhóm
ghi commit SHA dùng để chấm cùng thời điểm nộp sau khi đẩy bản cuối và nhận thông báo
của coach nếu có cập nhật muộn.
