# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Kiều Hạnh
**MSSV:** 2A202601760
**Nhóm:** K4 - Nhóm 1
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có hướng gần giống nhau, tức hai văn bản có ý nghĩa/ngữ cảnh gần nhau. Cosine similarity gần 1 nghĩa là hai câu hoặc đoạn văn nói về cùng chủ đề, nội dung tương đương.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả cho phép hoàn tiền trong vòng 30 ngày."
- Câu B: "Khách hàng có thể yêu cầu hoàn tiền trong 30 ngày sau khi nhận sản phẩm."
- Tại sao tương đồng: Cả hai cùng nói về quy định hoàn tiền trong 30 ngày nên vector có cùng hướng ngữ nghĩa.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Quy định đổi trả hàng ứng dụng cho sản phẩm điện tử."
- Câu B: "Người bán cần cung cấp thông tin chính xác về sản phẩm."
- Tại sao khác: Một câu về chính sách đổi trả, một câu về trách nhiệm người bán — chủ đề khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm góc giữa hai vector, bỏ qua độ lớn (norm), nên không bị ảnh hưởng khi độ dài văn bản hoặc cường độ embedding khác nhau. Euclid bị biên độ làm nhiễu thứ hạng; cosine dồn sự khác biệt vào "hướng ngữ nghĩa" nên phù hợp hơn để so sánh văn bản dài ngắn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước di chuyển = `500 - 50 = 450`. Số chunk = `ceil((10000 - 500)/450) + 1 = ceil(9500/450) + 1 = 22 + 1 = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao dùng độ chồng chéo nhiều hơn?**
> Với overlap=100, bước còn 400 ký tự → `ceil(9500/400) + 1 = 25` chunk (tăng 2 so với 23). Overlap lớn hơn giữ ngữ cảnh tại ranh giới giữa hai chunk kế tiếp, giảm khả năng câu trả lời bị nằm vừa vùng cắt mà truy vấn không tìm thấy.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi tách câu dựa trên dấu câu (dấu chấm, chấm than, hỏi, cuối dòng) rồi nhóm theo `max_sentences_per_chunk`. Nội dung chính sách thường là các điều khoản liệt kê, mỗi câu mang một ý trọn vẹn, nên chunk 2 câu vẫn giữ ngữ cảnh đồng thời tạo nhiều chunk hơn (nhỏ hơn) so với bản 3 câu — giúp đối chứng độ ảnh hưởng của kích thước chunk với cùng chiến lược sentence.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Độ quy theo trật tự separator ưu tiên `\n\n` → `\n` → `. ` → ` ` để chia cho tới khi mỗi phần nhỏ hơn `chunk_size`; dùng cho các đoạn dài không tách ngay được theo câu.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được embed và lưu thành record (id, content, metadata, embedding). `search` tạo embedding cho câu hỏi rồi tính dot product giữa vector truy vấn và từng record (mô phỏng cosine trên vector chuẩn hóa) để xếp hạng, trả kèm `score`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc metadata trước khi tính similarity: chỉ các record thỏa mãn điều kiện mới được so sánh, tránh lẫn tài liệu cùng chủ đề nhưng khác sàn. `delete_document` giữ lại record có `metadata['doc_id']` khác doc_id cần xóa và trả True nếu có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunk, ghép nội dung thành `Context:` rồi đặt câu hỏi `Question:` cho hàm LLM được inject; agent chỉ dựa vào context được trả, không tự sinh nội dung ngoài phạm vi.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$env:LAB_SOLUTION_PACKAGE='src.TranKieuHanh_2A202601760'
python -m pytest tests -q

..........................................                               [100%]
42 passed
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Điểm thực tế tính bằng `LocalEmbedder` (paraphrase-multilingual-MiniLM-L12-v2).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách đổi trả áp dụng trong 30 ngày. | Khách hàng có thể trả hàng trong vòng 30 ngày. | cao | 0.8258 | Có |
| 2 | Người bán phải cung cấp thông tin sản phẩm chính xác. | Người bán cần đảm bảo mô tả hàng chính xác. | cao | 0.9238 | Có |
| 3 | Chính sách giao hàng mất 3-5 ngày. | Hình thức thanh toán bằng thẻ tín dụng. | thấp | 0.2345 | Có |
| 4 | Tài khoản người bán cần xác thực email. | Người bán phải xác nhận danh tính trước khi đăng bán. | cao | 0.5123 | Trung bình |
| 5 | Chính sách bảo mật dữ liệu người dùng. | Hàng cấm không được phép đăng bán. | thấp | 0.1427 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 3 (chủ đề khác nhau) vẫn đạt 0.23 — cao hơn dự đoán thấp tuyệt đối vì hai câu cùng nằm trong nhóm "chính sách/thủ tục của sàn TMĐT". Cặp 4 (0.51) cho thấy model nhận ra liên hệ xác thực/phân định danh của người bán nhưng không phân biệt được hai bước khác nhau. Embedding ngữ nghĩa đo mức liên quan chủ đề, không đo sự đồng nhất từ ngữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong `src/TranKieuHanh_2A202601760`.
Chiến lược: `SentenceChunker(max_sentences_per_chunk=2)` — corpus `data/k4_ecommerce` — **299 chunks**.
Embedding **local** (`EMBEDDING_PROVIDER=local`). Điểm là cosine similarity thực tế của top-1.

| # | Câu hỏi (Query) | Top-1 nguyên như truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quy định đăng bán liệt kê bao nhiêu danh mục ngành hàng? | Top-1 = `shopee-listing-policy`, nội dung hướng dẫn chung, chưa chạm phần danh mục C.3 | 0.82 | Tài liệu đúng nhưng đáp án ở C.3 không nằm trong top-3 | Agent DEMO (không sinh nội dung thật) |
| 2 | Người bán cần giấy tờ gì để đăng bán mỹ phẩm? | Top-1 = `shopee-listing-policy` (mục đặt tên sản phẩm), không phải C.3.1 Mỹ phẩm | 0.75 | Tài liệu đúng nhưng đáp án "Phiếu công bố mỹ phẩm" không ở top-3 | Agent DEMO |
| 3 | COM được áp dụng cho đối tượng nào? | Top-1 = `shopee-listing-policy` (sai); top-2/3 = `shopee-return-refund` | 0.64 | Có doc đúng ở top-2; đáp án mục 4.1 không ở top-3 | Agent DEMO |
| 4 | Các loại sản phẩm bị cấm đăng bán? | Top-1 = `shopee-listing-policy` (sai); top-2 = `shopee-prohibited-products` | 0.82 | Có doc đúng ở top-2; đáp án "Súng, vũ khí"/"ma túy" không ở top-3 | Agent DEMO |
| 5 | Thời gian đổi trả sản phẩm là bao lâu? | Phải **filter** `source_url=.../77251`; sau filter top-3 toàn `shopee-return-refund` | 0.74 | **Có** — đáp án nằm trong top-3 sau filter | Bắt buộc filter mới phân biệt được Shopee và Tiki |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 theo doc_id (đúng tài liệu); đáp án trong top-3 theo `answer_marks`: 1 / 5 (chỉ Q5).

**Điều hay nhất tôi học được từ các thành viên/nhóm khác (qua demo):**
> SentenceChunker(2 câu) làm số chunk tăng lên (299) nhưng retrieval vẫn về đúng tài liệu ở hầu hết câu hỏi; thất bại nằm ở việc "trúng đúng câu" chứa câu trả lời. Demo các bạn cho thấy filter metadata và top-k lớn hơn sẽ khắc phục được nhược điểm của chunk nhỏ, và chiến lược chỉ là một biến trong cả pipeline.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |