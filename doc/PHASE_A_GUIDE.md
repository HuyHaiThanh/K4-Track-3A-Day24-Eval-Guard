# Phase A — đọc mã và chạy lại có kiểm soát

Nhánh riêng: huy/phase-a-ragas. Nguồn Phase B/C của Dat giữ nguyên. Phase A dùng artifacts/answers_50q.json đã chuẩn bị; không index hoặc generation lại.

## Luồng Tasks 1–4

1. group_by_distribution tạo đủ ba keys, đưa nguyên record vào đúng nhóm, giữ thứ tự. Hàm hỗ trợ nhóm rỗng; batch lab được runner kiểm số lượng 20/20/10.
2. run_ragas_50q kiểm 50 ids duy nhất, gửi bốn list đồng bộ đến m4. M4 gọi evaluator thật và trả metrics cùng evaluator_models. Task 2 từ chối thiếu rows, NaN/Inf, score ngoài [0,1], bool/string giả score và model IDs thiếu. Mapping và scalar NumPy được chuyển thành Python float. Nếu m4 có source fields, chúng phải khớp row gốc trước khi ghép.
3. bottom_10 sắp theo trung bình bốn metric tăng dần, tie-break question_id. Với ít hơn 10 input, trả số thực có. Mỗi row giữ rank/id/question/distribution/avg/worst_metric/diagnosis/fix. Diagnosis dẫn tới câu và nguồn, là hướng điều tra; phần phân tích thủ công trong failure_clusters.md mới kiểm tra nguyên nhân.
4. cluster_analysis cộng đúng một ô worst_metric cho mỗi câu. Tính mean của từng nhóm không rỗng để chọn nhóm yếu; metric chủ đạo là metric xuất hiện nhiều nhất trong matrix. Matrix không phải bảng số câu sai. Khi metrics hòa nhau, dùng thứ tự faithfulness → answer_relevancy → context_precision → context_recall nhất quán với RagasResult.

build_phase_a_report giữ nguyên rows của Task 3. Runner thêm metadata model roles và source hashes, validate schema/contract rồi mới ghi ragas_50q.json.

## Tự review đã áp dụng

- Không dùng zip để âm thầm cắt kết quả evaluator thiếu rows.
- Không biến NaN hoặc lỗi API thành điểm 0; artifact trước được giữ nếu evaluation chưa thành công.
- Không lấy generation/JUDGE_MODEL thay evaluator_models từ m4.
- Không xem một giá trị thấp là bằng chứng đủ cho nguyên nhân lỗi; đọc question, answer, contexts và reference.
- Bỏ heuristic so chuỗi số reference với contexts: tổng tính toán hợp lệ không nhất thiết xuất hiện trong policy. Cần kiểm dữ kiện question + quy tắc nguồn.
- Phát hiện hai phiên bản theo tiêu đề nguồn, không chỉ vì một policy mới nhắc năm của bản cũ trong thân bài.
- RuntimeError của m4 không in nguyên exception provider trong traceback; chỉ giữ loại lỗi, tránh log dữ liệu hoặc phần key mà provider đưa vào message.

Tests bổ sung bao phủ mapping/NumPy, thứ tự/source identity, thiếu rows/models, score lỗi, nhóm rỗng, tie và diagnosis số học. Không sửa assertions starter để làm đẹp kết quả.

## Lệnh kiểm chứng

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase_a.py tests/test_phase_a_edge_cases.py tests/test_support.py tests/test_report_contracts.py tests/test_preclass_pipeline.py -q
~~~

Đã có batch thật thì đọc artifact/report, không chạy API lại chỉ để kiểm tra file. Khi có lý do chạy lại evaluator (có phí API), dùng:

~~~powershell
.\.venv\Scripts\python.exe scripts/run_experiments.py --phase a --live
~~~

Nếu lỗi 401, cập nhật key trực tiếp trong .env; không gửi key vào chat/commit. Lần evaluation thất bại không phải kết quả mới. Nếu thay answers, phải ghi phiên bản và evaluate lại; không ghép score cũ với answers mới.

## Cách đọc kết quả

So sánh means ba nhóm, đọc bottom 10 rồi kiểm source. Ví dụ Q33 có thể vừa thiếu phụ cấp trong retrieval vừa tính thâm niên sai; Q9 có nguồn nhưng answer nói không tìm thấy; các bài cộng/nhân tiền cần review evaluator nếu answer đúng phép tính mà faithfulness thấp. Chi tiết và số đo của batch được chốt ở doc/reports/failure_clusters.md, không suy từ ví dụ này thành metric đã đo.

Artifact đủ schema và tests pass không khẳng định mọi answer đúng hoặc judge hoàn toàn đáng tin. Phase B tiếp tục kiểm độ tin cậy của judge; chưa được coi là đã hoàn thành trên nhánh này.
