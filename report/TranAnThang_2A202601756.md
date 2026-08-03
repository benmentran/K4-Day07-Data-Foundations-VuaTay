# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Trần An Thắng]
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

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (`_mock_embed`) | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách đổi trả áp dụng trong 30 ngày. | Khách hàng có thể trả hàng trong vòng 30 ngày. | cao | 0.017851 | Không* |
| 2 | Người bán phải cung cấp thông tin sản phẩm chính xác. | Người bán cần đảm bảo mô tả hàng chính xác. | cao | 0.022806 | Không* |
| 3 | Chính sách giao hàng mất 3-5 ngày. | Hình thức thanh toán bằng thẻ tín dụng. | thấp | 0.087810 | Có* |
| 4 | Tài khoản người bán cần xác thực email. | Người bán phải xác nhận danh tính trước khi đăng bán. | cao | 0.057412 | Không* |
| 5 | Chính sách bảo mật dữ liệu người dùng. | Hàng cấm không được phép đăng bán. | thấp | 0.021149 | Có* |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả mock cho thấy các cặp có nghĩa gần nhau không nhất thiết có điểm cao (cặp 1 và 2 chỉ khoảng 0.02), trong khi cặp 3 có điểm cao nhất dù chủ đề khác nhau. Đây là kết quả bất ngờ nhưng phù hợp với cảnh báo của lab: mock embedding là vector giả lập theo hash, không biểu diễn ngữ nghĩa; không nên dùng nó để đánh giá chất lượng retrieval.
>
> *​(*) “Đúng?” chỉ là so sánh định tính với mock score trong bộ thí nghiệm này, không phải đánh giá embedding semantic.*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Khoảng 14 danh mục ngành hàng Shopee | Local: top-1 = `shopee-listing-policy` (policy chung) | 0.32 | **Không** (local: đúng tài liệu top-3, đáp án C.3 không trong top-3) | Agent DEMO |
| 2 | Giấy tờ/điều kiện cho ngành hàng mỹ phẩm Shopee | Local: top-1 = `shopee-listing-policy` (đúng section Mỹ phẩm) | 0.71 | **Có** — "Phiếu công bố mỹ phẩm"/"Chứng nhận đại lý" | Đủ context |
| 3 | Đối tượng được áp dụng trả hàng COM | Local: top-1 = `shopee-return-refund` (đáp án 4.1 trong top-3) | 0.30 | **Có** | Đủ context |
| 4 | Các loại sản phẩm bị cấm trên Shopee | Local: top-1/2/3 đều `shopee-prohibited-products` | 0.41 | **Có** | Đủ context |
| 5 | Thời gian đổi trả trên Shopee | Filter `source_url=.../77251` → top-3 toàn `shopee-return-refund` | 0.26 | **Có, sau filter** | Bắt buộc filter |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** với **local embeddings**: 5 / 5 theo doc_id; đáp án (`answer_marks`) trong top-3: 4 / 5 (Q2, Q3, Q4, Q5; Q1 thiếu).

### Benchmark đã chạy

Strategy: `HeadingSectionChunker(chunk_size=700)`; corpus: `data/k4_ecommerce`; số chunk: **127**.
Embedding **local** (`EMBEDDING_PROVIDER=local`, paraphrase-multilingual-MiniLM-L12-v2). Lần chạy mock trước đó chỉ để kiểm tra pipeline; kết quả chính thức lấy từ lần chạy local.

| # | Top-1 doc_id | Filter | Top-3 có đúng tài liệu kỳ vọng? (local) | Đáp án trong top-3? |
|---|---|---|---|---|
| 1 | shopee-listing-policy | Không | Có | Không (đáp án C.3 không lọt top-3) |
| 2 | shopee-listing-policy | Không | Có | Có |
| 3 | shopee-return-refund | Không | Có | Có |
| 4 | shopee-prohibited-products | Không | Có | Có |
| 5 | shopee-return-refund | `source_url=.../77251` | Có | Có |

**Kết luận chính thức:** HeadingSectionChunker giữ nguyên cấu trúc tài liệu (heading → chunk) nên 4/5 câu trả lời nằm trọn trong top-3 với embedding local — tốt nhất nhóm ở CP6. Điểm thấp còn lại ở Q1 do danh mục ngành hàng (C.3) bị trộn trong chunk lớn với nội dung khác. Metadata filter (Q5) tiếp tục chứng minh giá trị.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Bài học chính là metadata filter có thể loại bỏ tài liệu cùng chủ đề nhưng sai sàn/đối tượng, như Query #5. Ngoài ra, heading preservation giúp mỗi chunk vẫn biết mình thuộc section nào; kết quả local embedding xác nhận heading chunk giữ đúng section chứa câu trả lời tốt hơn các chiến lược khác của nhóm.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 3 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
