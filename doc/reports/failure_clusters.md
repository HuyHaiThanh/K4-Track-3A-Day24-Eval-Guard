# Phân tích lỗi Phase A — Huy-Dat

Người phụ trách: Nguyễn Văn Huy — 2A202602428; Codex hỗ trợ implement, chạy kiểm chứng và phân tích. Cần học viên đọc/giải thích lại kết quả trước khi khai điều đã học.

Nguồn duy nhất cho các số đo: artifacts/ragas_50q.json. Run timestamp: 2026-10-16T02:07:49.789793+00:00 (09:07:49 ngày 16/10/2026, UTC+07:00). Batch RAGAS mới hoàn tất 200 metric tasks cho 50 câu, khoảng 147 giây theo progress runner; không phải latency request/guardrails. Lượt thử đầu gặp 401 và không ghi điểm; sau khi cập nhật key, batch này hoàn tất.

Generation: 50/50 llm, model gpt-4o-mini-2024-07-18, không có generation fallback. Evaluator RAGAS 0.1.22: gpt-4o-mini và text-embedding-3-small — IDs từ metadata m4, tách vai trò generation/evaluator; judge và guard chưa dùng. Enrichment của lượt retrieval trước đó dùng fallback cho 125 chunks vì chưa có key lúc index. Hai PDF scan chưa OCR. Phase A dùng nguyên 50 answers/contexts, không generation hoặc index lại.

Answers SHA-256: 9b30fefda5717851744ff2ff4e59f51996158d1c8f3d38715d6abe7257728016; fixture SHA-256: 0e87f26e020a32c62ea0864940720618f39600b9d3378193704cf2f86e88446d.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9500 | 0.6377 | 0.9500 |
| answer_relevancy | 0.5206 | 0.5193 | 0.6307 |
| context_precision | 1.0000 | 0.9750 | 0.9500 |
| context_recall | 1.0000 | 0.9042 | 0.7167 |
| avg_score | 0.8677 | 0.7591 | 0.8118 |

Multi_hop yếu nhất theo mean 0.7591, không phải do kích thước nhóm. Factual 0.8677; adversarial 0.8118. Multi_hop có faithfulness mean 0.6377 và 7/10 câu trong bottom. Tuy nhiên có answer tính toán đúng vẫn bị chấm thấp, nên chưa thể quy toàn bộ chênh lệch cho hallucination.

## Bottom 10 giữ nguyên output Task 3

Các diagnosis/suggested_fix được lấy nguyên từ Task 3 trong JSON (chỉ escape Markdown). Đây là giả thuyết điều tra có question/answer/source cụ thể, không phải kết luận tự động từ metric.

| Rank | ID | Distribution | Question | Avg score | Worst metric | Diagnosis | Suggested fix |
|---|---|---|---|---|---|---|---|
| 1 | 33 | multi_hop | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | 0.5000 | answer_relevancy | answer_relevancy=0.0000 là chỉ báo điều tra. Kiểm tra answer có đáp ứng từng ý, đại lượng và điều kiện được hỏi. Q33: Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? Answer: Chưa tìm thấy thông tin về tổng phụ cấp hàng tháng cho nhân viên Manager trong context. <br><br>Về số ngày phép năm theo phiên bản 2024:<br>- Nhân viên chính thức được hưởng 15 ngày phép năm.<br>- Nhân viên có thâm niên 12 năm sẽ được cộng thêm 3 ngày  Contexts=2; nguồn: Chính sách nghỉ phép năm (Phiên bản 2024), Chính sách nghỉ phép năm (Phiên bản 2023). Contexts chứa cả 2023/2024; cần đọc trạng thái/thay thế, không suy ra bản áp dụng từ điểm. Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu. Chưa kết luận nguyên nhân chỉ từ metric. | Tách các ý cần trả lời; kiểm tra mỗi ý có context trước generation; giữ policy cũ trong corpus, xác định bản áp dụng từ hiệu lực/thay thế của nguồn |
| 2 | 31 | multi_hop | Nhân viên đi công tác trong nước, ở khách sạn 2 đêm với giá 1.500.000 VNĐ/đêm. Công ty thanh toán tối đa bao nhiêu cho tiền khách sạn? | 0.5389 | faithfulness | faithfulness=0.0000 là chỉ báo điều tra. Kiểm tra các khẳng định/điều kiện trong answer có được nguồn hỗ trợ. Q31: Nhân viên đi công tác trong nước, ở khách sạn 2 đêm với giá 1.500.000 VNĐ/đêm. Công ty thanh toán tối đa bao nhiêu cho tiền khách sạn? Answer: Công ty thanh toán tối đa cho tiền khách sạn là 2.400.000 VNĐ (1.200.000 VNĐ/đêm x 2 đêm). Contexts=2; nguồn: Chính sách công tác phí, Chính sách tạm ứng. Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu. Chưa kết luận nguyên nhân chỉ từ metric. | Đối chiếu từng claim với nguồn; trả lời rõ phần chưa có dữ liệu thay vì suy đoán |
| 3 | 9 | factual | Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? | 0.6250 | answer_relevancy | answer_relevancy=0.0000 là chỉ báo điều tra. Kiểm tra answer có đáp ứng từng ý, đại lượng và điều kiện được hỏi. Q9: Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? Answer: Chưa tìm thấy thông tin về số ngày nghỉ phép đặc biệt cho nam nhân viên khi vợ sinh con trong context. Contexts=3; nguồn: Chính sách nghỉ phép đặc biệt, Chính sách nghỉ phép năm (Phiên bản 2024), Chính sách nghỉ ốm. Chưa kết luận nguyên nhân chỉ từ metric. | Tách các ý cần trả lời; kiểm tra mỗi ý có context trước generation |
| 4 | 28 | multi_hop | Nhân viên cấp Lead nhận tổng phụ cấp hàng tháng (ăn trưa + điện thoại) là bao nhiêu? | 0.6342 | faithfulness | faithfulness=0.0000 là chỉ báo điều tra. Kiểm tra các khẳng định/điều kiện trong answer có được nguồn hỗ trợ. Q28: Nhân viên cấp Lead nhận tổng phụ cấp hàng tháng (ăn trưa + điện thoại) là bao nhiêu? Answer: Nhân viên cấp Lead nhận tổng phụ cấp hàng tháng như sau:<br><br>- Phụ cấp ăn trưa: **1.000.000 VNĐ/tháng**<br>- Phụ cấp điện thoại: **300.000 VNĐ/tháng**<br><br>Tổng phụ cấp hàng tháng = 1.000.000 VNĐ + 300.000 VNĐ = **1.300.000 VNĐ/tháng**. Contexts=2; nguồn: Chính sách phụ cấp, Bảng lương năm 2024. Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu. Chưa kết luận nguyên nhân chỉ từ metric. | Đối chiếu từng claim với nguồn; trả lời rõ phần chưa có dữ liệu thay vì suy đoán |
| 5 | 38 | multi_hop | Nhân viên đi công tác nước ngoài 4 ngày tại thành phố lớn, ở khách sạn 200 USD/đêm (3 đêm). Công ty thanh toán bao nhiêu tiền khách sạn? | 0.6363 | faithfulness | faithfulness=0.0000 là chỉ báo điều tra. Kiểm tra các khẳng định/điều kiện trong answer có được nguồn hỗ trợ. Q38: Nhân viên đi công tác nước ngoài 4 ngày tại thành phố lớn, ở khách sạn 200 USD/đêm (3 đêm). Công ty thanh toán bao nhiêu tiền khách sạn? Answer: Công ty sẽ thanh toán cho nhân viên số tiền khách sạn là 600 USD (200 USD/đêm x 3 đêm). Contexts=1; nguồn: Chính sách công tác phí. Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu. Chưa kết luận nguyên nhân chỉ từ metric. | Đối chiếu từng claim với nguồn; trả lời rõ phần chưa có dữ liệu thay vì suy đoán |
| 6 | 24 | multi_hop | Nhân viên tạm ứng 15 triệu, sau 20 ngày mới thanh toán. Bị phạt bao nhiêu? | 0.6457 | faithfulness | faithfulness=0.2000 là chỉ báo điều tra. Kiểm tra các khẳng định/điều kiện trong answer có được nguồn hỗ trợ. Q24: Nhân viên tạm ứng 15 triệu, sau 20 ngày mới thanh toán. Bị phạt bao nhiêu? Answer: Nhân viên tạm ứng 15 triệu VNĐ và thanh toán sau 20 ngày. Thời hạn thanh toán là 15 ngày, do đó nhân viên đã quá hạn 5 ngày.<br><br>Phí phạt được tính theo công thức: <br>\[ \text{Phí} = 2\% \times \text{số tiền chưa hoàn ứng} \times \left(\frac{\te Contexts=1; nguồn: Chính sách tạm ứng. Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu. Chưa kết luận nguyên nhân chỉ từ metric. | Đối chiếu từng claim với nguồn; trả lời rõ phần chưa có dữ liệu thay vì suy đoán |
| 7 | 35 | multi_hop | Nhân viên Junior P1 có lương cơ bản 12 triệu vừa vào thử việc: nhận lương bao nhiêu và phụ cấp gì tháng đầu tiên? | 0.6888 | faithfulness | faithfulness=0.4000 là chỉ báo điều tra. Kiểm tra các khẳng định/điều kiện trong answer có được nguồn hỗ trợ. Q35: Nhân viên Junior P1 có lương cơ bản 12 triệu vừa vào thử việc: nhận lương bao nhiêu và phụ cấp gì tháng đầu tiên? Answer: Nhân viên Junior P1 có lương cơ bản 12 triệu sẽ nhận lương thử việc là 85% của 12 triệu, tức là 10.200.000 VNĐ. Phụ cấp ăn trưa được áp dụng đầy đủ từ ngày đầu tiên, nên nhân viên này cũng sẽ nhận phụ cấp ăn trưa trong tháng đầu tiên. Contexts=2; nguồn: Chính sách thử việc, Bảng lương năm 2024. Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu. Chưa kết luận nguyên nhân chỉ từ metric. | Đối chiếu từng claim với nguồn; trả lời rõ phần chưa có dữ liệu thay vì suy đoán |
| 8 | 50 | adversarial | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | 0.6945 | faithfulness | faithfulness=0.5000 là chỉ báo điều tra. Kiểm tra các khẳng định/điều kiện trong answer có được nguồn hỗ trợ. Q50: Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? Answer: Nhân viên Manager không thể sử dụng VPN cá nhân (như NordVPN, ExpressVPN) trong mạng công ty, bao gồm cả khi làm việc từ xa (WFH). Contexts=2; nguồn: Chính sách VPN và truy cập từ xa, Chính sách mật khẩu (Phiên bản hiện hành). Chưa kết luận nguyên nhân chỉ từ metric. | Đối chiếu từng claim với nguồn; trả lời rõ phần chưa có dữ liệu thay vì suy đoán |
| 9 | 42 | adversarial | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | 0.7192 | context_precision | context_precision=0.5000 là chỉ báo điều tra. Kiểm tra thứ tự và mức liên quan của từng context được lấy. Q42: Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? Answer: Nhân viên có thâm niên từ **3 năm trở lên** được cộng thêm **1 ngày phép** cho mỗi 3 năm làm việc liên tục. Contexts=2; nguồn: Chính sách nghỉ phép năm (Phiên bản 2023), Chính sách nghỉ phép năm (Phiên bản 2024). Contexts chứa cả 2023/2024; cần đọc trạng thái/thay thế, không suy ra bản áp dụng từ điểm. Chưa kết luận nguyên nhân chỉ từ metric. | Review RRF/rerank, giảm parent trùng chủ đề và ưu tiên nguồn phù hợp câu hỏi; giữ policy cũ trong corpus, xác định bản áp dụng từ hiệu lực/thay thế của nguồn |
| 10 | 23 | multi_hop | Nhân viên được tài trợ khóa học 25 triệu, nghỉ việc sau 8 tháng hoàn thành khóa học. Phải hoàn trả bao nhiêu? | 0.7302 | answer_relevancy | answer_relevancy=0.4207 là chỉ báo điều tra. Kiểm tra answer có đáp ứng từng ý, đại lượng và điều kiện được hỏi. Q23: Nhân viên được tài trợ khóa học 25 triệu, nghỉ việc sau 8 tháng hoàn thành khóa học. Phải hoàn trả bao nhiêu? Answer: Nhân viên phải hoàn trả **100% chi phí** đào tạo đã được tài trợ, tức là **25 triệu VNĐ**. Contexts=1; nguồn: Chính sách hoàn chi đào tạo. Câu có yếu tố tính toán: kiểm tra dữ kiện từ question và quy tắc trong contexts; kết quả suy ra không cần xuất hiện nguyên dạng trong tài liệu. Chưa kết luận nguyên nhân chỉ từ metric. | Tách các ý cần trả lời; kiểm tra mỗi ý có context trước generation |

## Đối chiếu từng case: nguồn → answer → reference

### Q33 — vừa thiếu nguồn phụ cấp, vừa sai phép tính

Contexts chỉ có policy phép năm v2024 và v2023. Không có [phu_cap.md](../../data/phu_cap.md), nên phần phụ cấp Manager chưa được retrieval hỗ trợ. Answer nêu thiếu phụ cấp nhưng tính 12 năm thành 3 ngày cộng thêm và tổng 18 ngày. [Policy v2024](../../data/nghi_phep_nam_v2024.md) quy định 1 ngày/3 năm: 12÷3=4, tổng 15+4=19. Reference phụ cấp là ăn trưa 1.000.000 + điện thoại Manager 500.000 = 1.500.000. Không đưa các số reference này vào answer đã lưu. Case này có hai lỗi quan sát được: thiếu coverage và generation áp dụng sai công thức; không thể sửa chỉ bằng thêm prompt chung hoặc chỉ thêm chunks.

Ưu tiên truy xuất theo hai ý phụ cấp/phép, bảo đảm nguồn khác chủ đề; sau đó tách operands và công thức để kiểm tra số học. Validate với các mức thâm niên mới (6/12/15 năm), không chỉ ví dụ 9 năm có sẵn trong policy.

### Q9 — nguồn đã có, generation lại nói không tìm thấy

Context [nghi_phep_dac_biet.md](../../data/nghi_phep_dac_biet.md) ghi Sinh con (nam giới): 5 ngày làm việc liên tục; phần đầu áp dụng nghỉ có lương, không trừ phép năm. Answer lại nói chưa tìm thấy thông tin. Precision gần 1 và recall 1 phù hợp quan sát nguồn đã được lấy. Faithfulness=0.5 và relevancy=0 không nên được gọi chung là hallucination thêm dữ kiện: đây là bỏ qua nguồn/từ chối sai. Có thể cách diễn đạt vợ sinh con so với sinh con (nam giới) gây khó cho generation; đó là giả thuyết, không có trace nội bộ để xác nhận. Sửa cách trích span liên quan và kiểm tra answer không tìm thấy với clauses thực có trong context trước khi trả lời.

### Q31 — số tiền chính đúng, evaluator faithfulness cần phản biện

[Công tác phí](../../data/cong_tac_phi.md) có trần 1.200.000/đêm. Question cho 2 đêm, hóa đơn 1.500.000/đêm. Answer 2×1.200.000=2.400.000 khớp số chính của reference; chưa nói phần vượt 300.000/đêm tự chi trả. Faithfulness=0, recall=0.6667 không đủ chứng minh answer bịa. Tổng 2.400.000 và số đêm là dữ kiện suy ra/từ question, không nhất thiết có nguyên dạng trong policy. Review cần kiểm tra min(hóa đơn,trần)×số đêm và thông tin phần vượt, thay vì yêu cầu retrieval tìm một đoạn có sẵn mọi kết quả tính toán.

### Q28 — answer khớp phép cộng và reference nhưng faithfulness=0

[Phụ cấp](../../data/phu_cap.md) có ăn trưa 1.000.000 và Lead điện thoại 300.000; answer cộng đúng 1.300.000/tháng, reference giống số này. Có đầy đủ operands trong context; thiếu việc ghi các điều kiện ngày nghỉ có thể đáng kiểm tra, nhưng không giải thích chắc chắn score=0. Ưu tiên kiểm tra cách evaluator tách/verify statements và arithmetic grounding, không tăng số chunks để tìm số tổng được tính ra.

### Q38 — đúng trần thành phố lớn và tổng 600 USD

[Công tác phí](../../data/cong_tac_phi.md) có trần khách sạn thành phố lớn 200 USD/đêm; question cho 3 đêm và giá 200. Answer 600 USD khớp reference. Faithfulness=0 dù context có đúng quy tắc và reference hỗ trợ phép tính là một bất đồng evaluator/manual review. Số ngày đi công tác 4 không thay số đêm 3. Giữ nguyên score thật; đề xuất kiểm tra arithmetic và nguồn của từng operand.

### Q24 — công thức pro-rata có trong nguồn, nhiều bước suy luận bị chấm thấp

[Tạm ứng](../../data/tam_ung.md) ghi hạn 15 ngày, phí 2%/tháng và quy ước pro-rata tháng 30 ngày của lab. Question cho 15 triệu và thanh toán sau 20 ngày; answer tính 5 ngày quá hạn và 50.000, khớp reference. Faithfulness=0.2/relevancy=0.3829 có thể bị ảnh hưởng bởi nhiều bước/định dạng công thức và dữ kiện question. Không sửa score hoặc giả sử thiếu formula trong retrieval. Hướng cải tiến: answer ngắn, ghi operands/công thức/kết quả riêng; evaluator review từng claim. Số 50.000 không cần xuất hiện trước trong corpus.

### Q35 — lương thử việc đúng, thiếu phụ cấp cụ thể

Contexts có [thử việc](../../data/thu_viec.md) và [bảng lương](../../data/bang_luong_2024.md): 85%, ăn trưa từ ngày đầu. Answer tính đúng 10.200.000 và nói có ăn trưa, nhưng không ghi số 1.000.000, không có phụ cấp điện thoại Junior và tổng 11.200.000 như reference. Các amounts/phân loại phụ cấp cần [phu_cap.md](../../data/phu_cap.md) nhưng chưa được lấy. Có thiếu coverage/completeness; faithfulness=0.4 còn có thể chịu giới hạn đánh giá số học. Truy xuất thêm theo ý phụ cấp, không đoán amount từ kiến thức ngoài nguồn.

### Q50 — giữ đúng phủ định, cần kiểm tra phạm vi WFH

[VPN](../../data/vpn_truy_cap.md) cấm VPN cá nhân trong mạng công ty và yêu cầu kết nối từ xa qua VPN công ty. Answer giữ phủ định nhưng thêm diễn giải bao gồm WFH; reference còn nêu WireGuard bắt buộc. Faithfulness=0.5, recall=0.6667 là tín hiệu kiểm tra phạm vi: truy cập tài nguyên/mạng công ty khác mọi hoạt động Internet cá nhân tại nhà. Sửa cách diễn đạt bám đúng phạm vi và nêu cơ chế được phép nếu context có; chưa kết luận answer hoàn toàn sai chỉ từ 0.5.

### Q42 — bản cũ xếp trước, answer vẫn dùng quy tắc mới

Contexts theo thứ tự [v2023](../../data/nghi_phep_nam_v2023.md), [v2024](../../data/nghi_phep_nam_v2024.md). Answer 3 năm/1 ngày theo v2024 đúng ý chính reference, faithfulness=1; precision=0.5 cho thấy thứ tự/mức phù hợp cần xem xét. Retrieval nên giữ bản cũ phục vụ câu hỏi lịch sử nhưng ưu tiên bản áp dụng theo câu hỏi/trạng thái. Không xóa policy cũ. Không xem worst_metric=context_precision là bằng chứng generation chọn sai phiên bản.

### Q23 — hoàn trả 25 triệu đúng nhưng thiếu cầu nối 8 tháng < 1 năm

[Hoàn chi đào tạo](../../data/hoan_chi_dao_tao.md) yêu cầu cam kết ít nhất 1 năm, nghỉ trước hạn trả 100%. Question có 25 triệu/8 tháng; answer 100%=25 triệu đúng reference nhưng không giải thích 8<12 tháng. Recall=1/precision gần 1: rule đã có; faithfulness=0.5/relevancy=0.4207 cho thấy cần đọc chain suy luận và giới hạn evaluator. Sửa explanation ngắn bằng ngưỡng thời gian → tỷ lệ hoàn trả → tiền, không lấy reference làm answer.

## Matrix và nhóm yếu nhất

| Worst metric | factual | multi_hop | adversarial | Tổng |
|---|---|---|---|---|
| faithfulness | 1 | 6 | 1 | 8 |
| answer_relevancy | 19 | 12 | 6 | 37 |
| context_precision | 0 | 1 | 1 | 2 |
| context_recall | 0 | 1 | 2 | 3 |
| Tổng cột | 20 | 20 | 10 | 50 |

Nhóm yếu theo mean: multi_hop, 0.7590618809. Answer relevancy là worst_metric của 37/50 câu. Mỗi câu góp đúng một ô, kể cả câu tốt; tổng cột chỉ là số câu. Tie-break metric: faithfulness → answer_relevancy → context_precision → context_recall.

Relevancy dùng cosine liên tục, các metric khác thường cao hoặc rời rạc theo claims; việc nó thường nhỏ nhất không tự chứng minh pipeline chỉ có lỗi generation. Mean batch không phải ngưỡng production.

## Tự phản biện evaluator và chẩn đoán

Đã đối chiếu mã RAGAS 0.1.22 cài trong môi trường: ragas/metrics/_faithfulness.py, _create_nli_prompt đưa contexts và statements vào NLI; question được dùng ở bước tạo statements. Dữ kiện số từ question và tổng suy ra có thể không được evaluator coi là hỗ trợ bởi riêng context. Đây là giả thuyết phù hợp Q24/Q28/Q31/Q38, chưa có intermediate statements/verdicts lưu lại để chứng minh nguyên nhân mỗi score. _answer_relevance.py còn dùng câu hỏi sinh ngược/cosine và noncommittal flag; score=0 không nhất thiết chỉ do cosine thấp. Cần review trace/nhãn người ở thực nghiệm tiếp theo, không sửa các score hiện tại cho đẹp.

Heuristic diagnosis đầu tiên dùng số reference không có nguyên dạng trong contexts như cảnh báo coverage. Self-review loại bỏ nó vì gây hiểu nhầm đối với arithmetic. Cũng sửa detection phiên bản để nhìn titles có cả v2023/v2024, không chỉ thấy năm 2023 được nhắc trong policy 2024. Task 3 được export lại từ cùng 200 metric values; không gọi RAGAS lại, không thay answer/context/reference/model/timestamp hoặc score.

## Bẫy adversarial và giới hạn

Adversarial mean 0.8118 thấp hơn factual 0.8677 khoảng 0.0558; đây là điều kiện số đo cho bonus A kèm phân tích, không tự chứng minh tất cả bẫy được nhận ra. Q41 trả 15 ngày theo policy hiện hành; Q42 đúng 3 năm dù bản cũ xuất hiện trước. Q43/Q44/Q45 trả 12 ký tự/120 ngày/MFA bắt buộc theo password mới. Q46/Q48 giữ phủ định thử việc; Q47 không tự xử lý malware. Q49 nhắc đúng bản hiện hành nhưng thiếu chi tiết quyền lợi của bản mới so với reference; Q50 cần làm rõ phạm vi VPN/WFH. Q42/Q50 nằm trong bottom; không đổi answers hoặc corpus để đạt bonus.

Reference adversarial có cả nội dung giải thích bẫy (ví dụ version conflict/negation, pipeline có thể retrieve hai tài liệu). Đó không phải lúc nào cũng là fact nguyên văn trong policy; context_recall thấp có thể trộn thiếu coverage với cách evaluator đọc annotations. Bộ fixtures giữ nguyên theo đề, không sửa để tăng score.

Batch chính có 50 mẫu/nhóm 20–20–10, cùng họ model nhỏ cho generation và evaluator, và enrichment fallback: chưa đủ kết luận production hoặc độ ổn định thống kê. Đã đối chiếu với batch 12/10 cục bộ trên cùng answers; báo cáo và artifact chấm chính chỉ dùng batch 16/10. Hai batch chưa đủ ước lượng độ ổn định/CI; chênh lệch này không phải cải tiến RAG vì answers không thay đổi. NaN/metrics thiếu bị từ chối; lượt này đủ bốn metric hữu hạn cho cả 50 câu. Không coi NaN là failure của RAG để điền điểm giả.

## Ưu tiên sửa và cách đánh giá lại

1. Coverage multi-hop: phân rã các ý, chọn nguồn đa dạng cho Q21/Q33/Q35. Kiểm tra truy xuất đủ các operands/điều kiện, không tăng top-k mù quáng.
2. Generation khi nguồn đủ: kiểm tra từ chối sai Q9 và số học Q33; thêm validation công thức dựa dữ kiện question + policy, giữ rõ phạm vi như Q50.
3. Evaluator reliability: review riêng Q24/Q28/Q31/Q38 với trace/nhãn người và tính toán kiểm chứng; không biến score thấp thành kết luận hallucination.
4. Phiên bản: ưu tiên effective policy theo câu hỏi nhưng vẫn giữ nguồn lịch sử, thử Q42/Q49 và câu ngoài bộ test.

Đây là đề xuất sau baseline, chưa sửa hoặc sinh lại pipeline answers trong Phase A. Nếu thay pipeline ở bước sau, tạo version answers mới có nguồn/hashes rõ rồi chạy evaluation tương ứng, so sánh cùng fixture và thêm held-out controls. Không ghép metrics cũ vào answers mới.

## Kiểm chứng

Tasks 1–4 và regression/support: 90 passed với selection Phase A + edge cases + support/report contracts/preclass tests (không có integration trong selection); tests B/C không nằm trong selection này. validate_phase_a pass (schema/50 ids/4 metrics/counts/means/bottom/matrix); validate_metadata pass (source hashes/models). Bottom diagnosis/fix tái tạo từ Task 3 khớp JSON. B/C của Dat chưa bị sửa trên nhánh này. Branch: huy/phase-a-ragas.

Giải thích mã và cách tự chạy: [PHASE_A_GUIDE.md](../PHASE_A_GUIDE.md). Không sửa TEAM.md hay source B/C để giảm xung đột khi Dat tích hợp; cập nhật đóng góp cá nhân sau review/merge.
