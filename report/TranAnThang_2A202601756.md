# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Bạn điền]
**Nhóm:** K4 - Nhóm 1
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có cùng hướng hoặc gần cùng hướng, tức là hai văn bản có nội dung/ngữ nghĩa gần nhau theo mô hình embedding. Giá trị thường nằm trong [-1, 1], với 1 là cùng hướng.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả cho phép hoàn tiền trong 30 ngày."
- Câu B: "Khách hàng có thể trả hàng và nhận hoàn tiền trong vòng 30 ngày."
- Tại sao tương đồng: Hai câu cùng nói về việc đổi trả và thời hạn hoàn tiền.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chính sách đổi trả cho phép hoàn tiền trong 30 ngày."
- Câu B: "Mặt trời là một ngôi sao."
- Tại sao khác: Hai câu nói về hai chủ đề không liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào hướng của vector và ít bị ảnh hưởng bởi độ dài/độ lớn tuyệt đối của embedding. Điều này phù hợp với text embedding vì văn bản dài hơn không nhất thiết có nghĩa là khác chủ đề.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước dịch chuyển giữa hai chunk là `500 - 50 = 450` ký tự. Số chunk là `ceil((10000 - 500) / 450) + 1 = 23`.
> **Đáp án: 23 chunks.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap 100, bước dịch chuyển còn 400 ký tự và số chunk tăng thành `ceil((10000 - 500) / 400) + 1 = 25`. Overlap lớn giúp giữ lại ngữ cảnh ở ranh giới chunk nhưng làm tăng số chunk, chi phí embedding và khả năng trùng lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> `SentenceChunker` dùng regex `(?<=[.!?])(?:\s+|$)` để tách sau dấu kết thúc câu và khoảng trắng/xuống dòng. Nó loại bỏ chunk rỗng, trim khoảng trắng và ép `max_sentences_per_chunk` tối thiểu là 1; văn bản rỗng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `RecursiveChunker` thử separator theo thứ tự đoạn văn, dòng, câu, khoảng trắng rồi mới cắt theo ký tự. Nếu văn bản đã ngắn hơn `chunk_size` thì trả về ngay; nếu separator hiện tại không phù hợp hoặc không còn separator thì chuyển xuống mức thấp hơn/cắt cố định, đồng thời gộp các phần nhỏ khi vẫn nằm trong giới hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được embed và chuẩn hóa thành record gồm id, content, metadata và embedding. Khi ChromaDB có sẵn, record được lưu trong collection Chroma; nếu không, dùng list trong bộ nhớ. In-memory search xếp hạng theo cosine similarity tương đương với khoảng cách Euclidean trên vector đã chuẩn hóa.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước rồi mới tính similarity trên các record còn lại; với ChromaDB, filter được truyền trực tiếp vào query. `delete_document` xóa tất cả chunk có `metadata['doc_id']` tương ứng và trả về `True` nếu có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` lấy top-k chunk liên quan, đánh số và ghép chúng thành phần Context trong prompt. Prompt yêu cầu model chỉ dùng context, nêu rõ khi context không đủ, sau đó truyền prompt cho hàm LLM được inject từ bên ngoài.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
..........................................                               [100%]
42 passed
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

### Benchmark đã chạy

Strategy: `HeadingSectionChunker(chunk_size=700)`; corpus: `data/k4_ecommerce`; số chunk: **127**.
Embedding offline dùng `_mock_embed` cho lần benchmark có thể tái lập. Gemini đã được thử với API key nhưng request embedding trả lỗi dịch vụ `503 UNAVAILABLE`, vì vậy không ghi kết quả Gemini như kết quả chính thức.

| # | Top-1 doc_id | Filter | Top-3 có đúng tài liệu kỳ vọng? | Ghi chú |
|---|---|---|---|---|
| 1 | shopee-return-refund | Không | Có ở top-2 (`shopee-listing-policy`) | Mock embedding xếp sai top-1 |
| 2 | shopee-prohibited-products | Không | Có ở top-3 (`shopee-listing-policy`) | Mock embedding xếp sai tài liệu |
| 3 | shopee-return-refund | Không | Có | Cần đánh giá lại bằng embedding semantic |
| 4 | tiki-return-policy | Không | Không | Mock embedding không phù hợp để kết luận |
| 5 | shopee-return-refund | `source_url=.../77251` | Có | Filter loại tài liệu Tiki |

**Kết luận tạm thời:** Pipeline, heading preservation và metadata filter hoạt động; kết quả mock không đại diện cho chất lượng semantic. Cần chạy lại sau khi Gemini hết lỗi 503 để chốt điểm retrieval.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
