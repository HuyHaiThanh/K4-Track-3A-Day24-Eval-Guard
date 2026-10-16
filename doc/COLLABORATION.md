# Làm chung repo Huy-Dat

Repo: https://github.com/HuyHaiThanh/K4-Track-3A-Day24-Eval-Guard

## Đạt lấy bản chuẩn bị

~~~powershell
git clone https://github.com/HuyHaiThanh/K4-Track-3A-Day24-Eval-Guard.git
cd K4-Track-3A-Day24-Eval-Guard
git switch -c dat/phase-b-rails
~~~

Nếu đã clone, commit hoặc cất thay đổi đang làm trước khi chuyển nhánh. Khi working tree sạch:

~~~powershell
git switch main
git pull --ff-only origin main
git switch -c dat/phase-b-rails
~~~

Đạt làm Tasks 5–8 trong src/phase_b_judge.py và hai hàm check_input_rail/check_output_rail trong src/phase_c_guard.py; điền bias_report.md và INDIVIDUAL của mình. Huy làm Tasks 1–4 và ba hàm PII/suite/latency của Phase C. Khi sửa TEAM.md/blueprint.md hoặc cùng file Phase C, review diff khi merge để giữ phần của nhau.

## Môi trường riêng của mỗi máy

Virtualenv, model cache và .env không nằm trên GitHub. Mỗi máy chuẩn bị Python 3.11, dependencies/model theo ENVIRONMENT.md; điền key riêng trong .env. Không gửi key vào chat, commit hoặc PR. Repo đã có 50 answers thật; dùng đúng artifact này cho Phase A, không generation lại chỉ để đồng bộ code.

## Commit theo phần việc

Cấu hình tên/email Git của chính mình trên máy trước khi commit. Gợi ý tách commits: pairwise judge; swap/kappa/bias; NeMo input/output; báo cáo evidence thật. Mỗi commit mô tả phần đã làm và tests đã chạy; không nhận TODO/mocks thành thực nghiệm live.

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase_b.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_phase_c.py -k "input_uses_rail_decision or output_checks_supplied_answer" -q
git add src/phase_b_judge.py
 git commit -m "feat: implement pairwise judge and bias analysis"
git push -u origin dat/phase-b-rails
~~~

Lệnh git add ở ví dụ chỉ chọn Phase B; các file Phase C/report đã tích hợp riêng trên nhánh `dat`. Sau khi merge cập nhật Phase A, batch Phase C live đã chạy trên bản tích hợp và được ghi trong `artifacts/guard_results.json`. Chưa push lên GitHub; nếu Đạt chưa có quyền push, Huy cần thêm tài khoản GitHub của Đạt vào collaborators; họ tên/MSSV không xác định được tài khoản GitHub để cấp quyền.

## Bản chuẩn bị đã commit

- 85fbb32: môi trường Windows và constraints.
- 0e66686: m1–m5, setup/checker và regression tests.
- 48f3fd9: 50 LLM answers, environment evidence và hướng dẫn.
- Commit checkpoint/team tiếp theo ghi phân công và cách tích hợp.
