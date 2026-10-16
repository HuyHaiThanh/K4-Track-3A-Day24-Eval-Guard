# Đánh giá LLM Judge Phase B

Nhóm: Huy–Đạt. Người phụ trách phần này: Nguyen Quoc Dat (2A202602369).

Nguồn kết quả: `artifacts/judge_results.json`; Phase B chạy live ngày
2026-10-16 lúc 11:13:20 ICT (04:13:20 UTC). Model sinh answer gốc:
`gpt-4o-mini-2024-07-18`; judge: `gpt-4o-mini`.
Artifact đã qua `validate_phase_b` với 5 pairwise results, 10 calibration rows,
đúng fixtures và source hashes.

## Năm cặp A/B và hai lượt

A lấy từ `artifacts/answers_50q.json:answer`; B lấy từ
`fixtures/human_labels_10q.json:model_answer`; reference lấy từ
`fixtures/test_set_50q.json:ground_truth`. IDs theo thứ tự cố định: 1, 5, 12,
21, 41. Ở lượt hai, thứ tự đầu vào được đảo; winner và scores dưới đây đã được
quy đổi về nhãn A/B ban đầu.

| ID | Candidate A | Candidate B | Winner P1 / P2 / final | Position consistent | Scores P1 A/B | Scores P2 A/B |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Nhân viên được nghỉ 3 ngày làm việc khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B / B / B | Có | 0.70 / 1.00 | 0.80 / 1.00 |
| 5 | Đối với đơn hàng trị giá 55 triệu VNĐ, cần có phê duyệt của Tổng Giám đốc (CEO) theo thẩm quyền phê duyệt trong quy trình mua sắm. | Cần Giám đốc phòng ban phê duyệt. | A / A / A | Có | 1.00 / 0.00 | 1.00 / 0.30 |
| 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên là **1 tháng lương**. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | A / A / A | Có | 1.00 / 0.80 | 1.00 / 0.80 |
| 21 | Nhân viên Senior có 9 năm thâm niên sẽ được hưởng **18 ngày phép năm** (15 ngày cơ bản + 3 ngày cộng thêm cho 9 năm thâm niên). Về lương, nhân viên này sẽ được hưởng lương trong thời gian nghỉ phép năm, vì phép năm là có lương. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | A / A / A | Có | 1.00 / 0.80 | 1.00 / 0.80 |
| 41 | Nhân viên chính thức được hưởng **15 ngày phép năm** có lương theo chính sách hiện hành (phiên bản 2024, hiệu lực từ 01/01/2024). | Nhân viên được nghỉ 12 ngày phép năm. | A / A / A | Có | 1.00 / 0.00 | 1.00 / 0.00 |

Reasoning raw của hai lượt. Nhãn A/B trong reasoning lượt hai là thứ tự đã đảo;
winner/scores trong bảng phía trên đã được quy về candidate gốc:

- ID 1 P1: “Answer B cung cấp thông tin đầy đủ về việc nghỉ có lương, trong khi Answer A không đề cập đến điều này.” P2: “Answer A cung cấp thông tin chính xác và đầy đủ về việc nghỉ có lương, trong khi Answer B thiếu thông tin này.”
- ID 5 P1: “Câu trả lời A cung cấp thông tin chính xác về việc cần Tổng Giám đốc phê duyệt cho đơn hàng trên 50 triệu VNĐ, trong khi câu trả lời B sai lệch.” P2: “Answer B cung cấp thông tin chính xác và đầy đủ theo chính sách phê duyệt, trong khi Answer A cung cấp thông tin không đúng.”
- ID 12 P1: “Answer A cung cấp thông tin chính xác và đầy đủ về mức thưởng Tết cho nhân viên có thời gian làm việc từ 6 tháng trở lên, bao gồm cả cụm 'tối thiểu' và '1 tháng lương'.” P2: “Answer B cung cấp câu trả lời rõ ràng và chính xác hơn với định dạng cụ thể, tách biệt thông tin liên quan đến thời gian làm việc.”
- ID 21 P1: “Answer A cung cấp thông tin đầy đủ về chính sách nghỉ phép cũng như lương, có giải thích chi tiết về cách tính ngày phép.” P2: “Answer B cung cấp thông tin chính xác về số ngày phép và cách tính thâm niên, đồng thời giải thích rõ ràng về lương trong thời gian nghỉ phép.”
- ID 41 P1: “Answer A cung cấp thông tin chính xác và cập nhật theo chính sách năm 2024, trong khi Answer B sử dụng thông tin lỗi thời từ chính sách năm 2023.” P2: “Answer B cung cấp thông tin chính xác về số ngày phép theo chính sách v2024, trong khi Answer A chỉ đưa ra thông tin của chính sách cũ.”

Position bias count/rate là 0/5 (0%): cả năm candidate thắng đều giữ nguyên sau
khi đổi vị trí. Verbosity win rate là 5/5 (100%) trong năm case quyết định; A dài
hơn và thắng ở bốn case, B dài hơn và thắng ở một case. Đây chỉ là dấu hiệu mô tả
trong mẫu nhỏ: ID 1 thêm điều kiện nghỉ có lương, ID 21 giải thích ngày phép và
lương, ID 41 cập nhật policy; không thể quy kết độ dài là nguyên nhân thắng.

## Calibration đúng model_answer

Runner đánh giá nguyên văn `model_answer` trong
`fixtures/human_labels_10q.json`, không tạo answer mới. Prompt chỉ chứa question,
answer và reference. `human_label`/`human_note` không được truyền cho helper; nhãn
human chỉ được ghép sau đó để so sánh.

| ID | Model answer gốc | Judge | Reasoning của judge | Human | Agree |
| --- | --- | --- | --- | --- | --- |
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | Câu trả lời chính xác theo thông tin trong tài liệu tham khảo, nêu rõ số ngày nghỉ và điều kiện không trừ vào phép năm. | 1 | Có |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | Câu trả lời sai vì yêu cầu phê duyệt cho đơn hàng trên 50 triệu là từ Tổng Giám đốc, không phải Giám đốc phòng ban. | 0 | Có |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | Câu trả lời chính xác theo thông tin trong reference, nêu rõ điều kiện và mức thưởng cho nhân viên chính thức có từ 6 tháng trở lên. | 1 | Có |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | Câu trả lời đúng theo chính sách công ty, nêu rõ số ngày phép và khoảng lương cho nhân viên Senior với 9 năm thâm niên. | 1 | Có |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | Câu trả lời đúng theo chính sách công ty, nêu rõ nhân viên phải hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | Có |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | Câu trả lời sai vì chỉ đề cập đến Trưởng phòng phê duyệt mà không nhắc đến Kế toán trưởng, và phí phạt được tính cho quá hạn 15 ngày chứ không phải là 2% trên 8 triệu cho toàn bộ tháng. | 0 | Có |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | Câu trả lời cung cấp đúng số ngày phép và tổng phụ cấp hàng tháng theo thông tin trong tài liệu tham khảo. | 1 | Có |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | Câu trả lời sai vì nó dựa trên chính sách cũ (v2023) thay vì chính sách hiện hành (v2024), trong đó quy định nhân viên được nghỉ 15 ngày phép năm. | 0 | Có |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | Câu trả lời chính xác theo reference, nêu rõ rằng nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần, đồng thời không bỏ qua điều kiện cần có sự phê duyệt của trưởng phòng. | 1 | Có |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | Câu trả lời sai vì cho phép sử dụng VPN cá nhân trong khi chính sách rõ ràng cấm điều này. | 0 | Có |

Observed agreement là 10/10 = 1.00. Hai tập nhãn đều có 6 nhãn 1 và 4 nhãn 0,
nên chance agreement = (6×6 + 4×4)/10² = 0.52. Cohen’s κ = (1.00 − 0.52) /
(1 − 0.52) = 1.00. Không có case bất đồng trong 10 rows này.

## Giới hạn và cách dùng judge

κ vượt ngưỡng tham chiếu 0.6 trong bộ 10 nhãn đã chọn, nhưng không chứng minh
judge đúng tuyệt đối hoặc tổng quát cho các câu hỏi khác. Các candidate pair chỉ
có năm case chọn trước; verbosity rate 100% cần đọc cùng nội dung và không chứng
minh thiên lệch nhân quả. Các reasoning ở trên giải thích kết luận của model, không
thay reference hoặc kiểm duyệt của con người. Với bất đồng trong lần đánh giá sau,
đối chiếu question, exact answer, policy reference và version; giữ lại raw reasoning,
đưa case sang người review và không tự sửa nhãn human để khớp judge.
