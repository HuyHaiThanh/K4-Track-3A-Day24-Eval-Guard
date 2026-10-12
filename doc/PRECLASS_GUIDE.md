# Chuẩn bị pipeline trước lớp

Phạm vi: tích hợp m1–m5, chuẩn bị runtime và sinh answers. Phase A/B/C vẫn là phần bài tập tiếp theo.

## Luồng mã thực tế

1. m1 đọc Markdown và PDF có text layer từ config.DATA_DIR. Mỗi document giữ source. Hierarchical chunking tạo parent tối đa 2048 ký tự, child tối đa 256 ký tự, giữ parent_id, parent_text và metadata nguồn. Kích thước là ký tự, không phải token.
2. m5 giữ nguyên số lượng/thứ tự chunks. Combined enrichment tạo summary, câu hỏi giả định và metadata bằng một request/chunk. Nếu API lỗi hoặc thiếu key, enrichment dùng fallback extractive và ghi enrichment_status; không được coi fallback là kết quả LLM.
3. m2 index chunks trên BM25 và Qdrant thật với embedding BAAI/bge-m3, 1024 chiều. Tách từ tiếng Việt giữ dấu gạch dưới của từ ghép. RRF kết hợp thứ hạng hai nguồn thay vì cộng trực tiếp các score khác thang đo.
4. m3 dùng BAAI/bge-reranker-v2-m3 chấm từng cặp question/child rồi lấy top 3. Model lazy-load ở lần rerank đầu.
5. Setup lấy parent_text gốc của các child được chọn, loại contexts trùng. Nếu không có parent_text thì dùng original_text. Văn bản enrichment được dùng cho retrieval; phần summary/HyQA sinh thêm không được dùng như bằng chứng nguồn của generation.
6. Setup gửi question và contexts đến generation model, không gửi ground_truth. Sau khi generation hoàn tất mới ghép ground_truth từ fixture để đánh giá sau này. API client được reuse, temperature=0; điều này không bảo đảm tuyệt đối tính tái lập.
7. Mỗi row ghi generation_mode và generation_model. API lỗi, output rỗng hoặc thiếu contexts dẫn đến extractive_fallback, model=null. Fallback chỉ lấy context đầu, chưa phải một câu trả lời được tổng hợp tốt.
8. Trước khi ghi answers, setup validate JSON Schema và nguồn id/question/distribution/ground_truth. Ghi qua file tạm rồi replace để tránh ghi đè kết quả trước bằng batch chưa hợp lệ.

## M4 được chuẩn bị cho Phase A

M4 nhận bốn list cùng độ dài, gọi RAGAS với LLM và embeddings được cấu hình riêng qua RAGAS_MODEL và RAGAS_EMBEDDING_MODEL. Metadata evaluator_models lấy các model IDs thực sự truyền vào lượt evaluate này. M4 không lấy JUDGE_MODEL thay thế, không biến NaN thành điểm 0 và báo lỗi khi evaluation không hợp lệ. Chưa có report RAGAS thật chỉ từ việc kiểm tra adapter.

## Tự chạy lại trên PowerShell từ gốc repo

Dùng Python 3.11. Nếu Annoy không build được, cài Microsoft C++ Build Tools với workload Desktop development with C++, MSVC và Windows SDK.

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements/requirements.txt -c requirements/constraints-core.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m spacy download en_core_web_lg
docker compose -f infra/docker-compose.yml up -d
.\.venv\Scripts\python.exe -m pytest tests/test_preclass_pipeline.py tests/test_support.py -q
.\.venv\Scripts\python.exe scripts/setup_answers.py --live
.\.venv\Scripts\python.exe scripts/check_preclass.py
~~~

Setup --live có thể gọi API cho enrichment/generation, tải model và thay collection lab24_production. Không chạy lại batch chỉ để đọc kết quả. check_preclass chỉ kiểm tra môi trường, Qdrant và artifact có sẵn; không generation lại.

## Cách đọc một row answers

- question: câu hỏi gốc trong fixture.
- contexts: những parent passages gốc đã lấy thông qua search/rerank. Với top 3 children, số contexts có thể ít hơn 3 do cùng parent.
- answer: đầu ra generation hoặc fallback có ghi rõ.
- ground_truth: reference được giữ nguyên từ fixture; không phải answer của pipeline.
- generation_model: model provider báo về hoặc ID truyền vào request; null với fallback.

Một answer sai vẫn có thể là artifact hợp lệ: schema kiểm tra hợp đồng dữ liệu, RAGAS và phân tích sau này mới giúp đánh giá chất lượng.

## Tự review và giới hạn

Các sửa lỗi tích hợp: dùng Qdrant search API đúng với qdrant-client 1.9.x; không tự rơi về Qdrant in-memory khi dịch vụ lỗi; giữ từ ghép cho BM25; thêm evaluator metadata; tránh contexts chứa enrichment sinh thêm; không log nguyên exception provider; kiểm tra output generation rỗng; validate và ghi answers nguyên tử.

Tests offline kiểm tra bảo toàn văn bản/metadata, Qdrant API, enrichment order, evaluator model IDs, NaN rejection, generation fallback và source-only contexts. Chúng không chứng minh model/API chạy thật; cần batch setup và check_preclass thực tế.

Hai PDF BCTC.pdf và Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.pdf không có text layer trong lần kiểm tra corpus. Loader cảnh báo và bỏ qua; chưa có OCR. Corpus Markdown, PDF so_tay_an_toan.pdf và cả policy cũ/mới được giữ nguyên. Không suy ra đã đọc đầy đủ mọi PDF.

Import NeMo/Presidio và tải spaCy chỉ là chuẩn bị môi trường. Chưa chứng minh input/output rails chạy thật hoặc đạt tiêu chí Phase C. Chưa chạy đánh giá RAGAS 50 câu trong phần chuẩn bị này.

AI hỗ trợ: Codex review và sửa giao diện/tích hợp, chuẩn bị môi trường, chạy kiểm chứng và giải thích. Nhóm cần đọc mã, giải thích được phần dùng và khai phạm vi hỗ trợ theo quy định lớp.

Runtime review phát hiện PyArrow mới không import được với NumPy 1.26.4 của lab. constraints-core.txt bổ sung pyarrow==16.1.0 để tránh lặp lỗi này. Embedding/reranker dùng batch_size=4; reranker giới hạn 512 tokens mỗi cặp để giảm đỉnh RAM trên máy 16 GB. Nội dung child/enrichment vẫn có thể bị tokenizer truncation nếu vượt giới hạn; cần cân nhắc khi thay corpus hoặc enrichment.

Nếu key được cập nhật sau một batch fallback, chạy `python scripts/setup_answers.py --live --generation-only` để dùng lại contexts đã lấy thực tế và chỉ sinh lại answer. Chế độ này kiểm tra schema/nguồn và xác nhận contexts thuộc corpus gốc trước khi gọi LLM; không chạy lại enrichment/index/rerank. Cần ghi rõ enrichment fallback của lượt retrieval trước đó. Trên Windows runtime hiện tại, lệnh kiểm tra full imports dùng `python -c "import torch; import ragas, nemoguardrails, presidio_analyzer, spacy; print('imports OK')"` để tránh lỗi thứ tự khởi tạo DLL.

Chỉ dùng generation-only khi corpus và cấu hình retrieval/rerank vẫn giữ nguyên (ví dụ đổi key hoặc prompt generation). Nếu đổi corpus/chunking/model/search, chạy lại setup đầy đủ. Kiểm tra context thuộc corpus không tự chứng minh retrieval cache còn phù hợp sau khi thêm chính sách mới.

Review thủ công của lượt LLM đầu: câu 41 lấy được cả policy v2023/v2024 nhưng answer chỉ liệt kê hai mức phép, chưa chọn bản hiện hành; prompt được cải thiện theo ngày hiệu lực/trạng thái/thay thế ghi trong context, không đưa reference vào prompt. Câu 21 lấy được chính sách phép nhưng thiếu khung lương Senior trong contexts; đây là giới hạn retrieval cần phân tích ở Phase A, không điền đáp án tham chiếu để che lỗi. Sau sửa prompt, generation được chạy lại trên chính contexts đã lưu.

## Kết quả và review cuối của phần chuẩn bị

- Full runtime đã cài, Annoy đã build bằng MSVC 14.44.35207. Python 3.11.9; pip check không báo xung đột; full imports đã pass theo thứ tự Torch trước NLP. spaCy en_core_web_lg 3.8.0 load được.
- BGE-M3 encode vector 1024 chiều; BGE reranker inference thành công. Qdrant v1.9.7 có 125 points từ 26 tài liệu có text.
- Artifact cuối có 50 answers từ LLM gpt-4o-mini-2024-07-18, không có generation fallback; phân phối 20 factual, 20 multi_hop, 10 adversarial.
- Enrichment của lượt retrieval là fallback cho 125 chunks vì lúc ấy chưa có key thật. Generation dùng key thật sau đó và cùng contexts, không chạy lại retrieval. Hai lượt generation sau key: 58.5 giây và 68.8 giây (lượt sau sửa prompt). Lượt retrieval/rerank 50 câu trên CPU mất 1349.2 giây; đây không phải P95 latency hoặc số đo guardrails.
- Regression tests: 69 passed, 29 deselected với marker support; student tasks Phase A/B/C chưa hoàn thiện.

### Ví dụ giúp phân biệt lỗi

Câu 41 trước sửa prompt: Nhân viên chính thức được hưởng **12 ngày phép năm** có lương theo chính sách năm 2023 và **15 ngày phép năm** có lương theo chính sách năm 2024.

Câu 41 sau sửa prompt: Nhân viên chính thức được hưởng **15 ngày phép năm** có lương theo chính sách hiện hành (phiên bản 2024, hiệu lực từ 01/01/2024).

Cả hai lượt nhận cùng contexts chứa policy 2023 và 2024. Lỗi chọn phiên bản thuộc generation/prompt; cải thiện dùng quy tắc hiệu lực/thay thế của tài liệu, không sửa reference hoặc bỏ policy cũ.

Câu 21 cuối: Nhân viên Senior có 9 năm thâm niên sẽ được hưởng **18 ngày phép năm** (15 ngày cơ bản + 3 ngày cộng thêm cho 9 năm thâm niên).

Về lương, nhân viên này sẽ được hưởng lương trong thời gian nghỉ phép năm, vì phép năm là có lương.

Contexts câu 21 chứa policy phép năm 2024, 2023 và nghỉ không lương, không chứa khung lương Senior. Vì thế retrieval chưa đủ cho câu hỏi nhiều ý. Answer còn nói về lương trong thời gian nghỉ thay vì khoảng lương được hỏi: thông tin có căn cứ vẫn có thể không đáp ứng câu hỏi. Hướng điều tra ở Phase A là coverage của retrieval và answer relevancy; chưa có số đo RAGAS để kết luận metric thấp nhất. Không bổ sung mức lương từ ground_truth vào answer để che failure.

Schema hợp lệ chứng minh hình dạng và nguồn dữ liệu đúng hợp đồng; chưa chứng minh mọi answer đúng/đủ hoặc hệ thống sẵn sàng production. Artifact này đủ để bắt đầu Phase A và phân tích lỗi từ thực nghiệm.
