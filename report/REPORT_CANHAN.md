# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, tức nội dung hai câu/đoạn văn có ý nghĩa giống hoặc rất liên quan. Khi cosine similarity gần 1, hai văn bản thường chia sẻ cùng chủ đề hoặc thông tin tương tự.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả cho phép hoàn tiền trong vòng 30 ngày kể từ ngày nhận hàng."
- Câu B: "Khách hàng có thể yêu cầu hoàn tiền trong 30 ngày sau khi nhận sản phẩm."
- Tại sao tương đồng: Cả hai câu đều nói cùng một chính sách hoàn tiền 30 ngày, nên embedding của chúng có hướng rất giống nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Quy định đổi trả hàng được áp dụng cho sản phẩm điện tử."
- Câu B: "Người bán cần cung cấp thông tin chính xác về sản phẩm."
- Tại sao khác: Câu thứ nhất nói về chính sách đổi trả, câu thứ hai nói về trách nhiệm người bán; nội dung khác nhau nên cosine similarity thấp.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity đo góc giữa hai vector và bỏ qua độ lớn, nên nó phù hợp với embedding văn bản khi độ dài tài liệu hoặc cường độ embedding không đồng nhất. Khoảng cách Euclid bị ảnh hưởng bởi biên độ vector, còn cosine tập trung vào hướng ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Với chunk_size=500 và overlap=50, mỗi bước di chuyển là 450 ký tự. Số chunk bằng `ceil((10000 - 500)/450) + 1 = ceil(9500 / 450) + 1 = 22 + 1 = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap=100, bước di chuyển còn 400 ký tự, do đó số chunk tăng lên thành `ceil((10000-500)/400) + 1 = 25` chunk. Độ chồng chéo nhiều hơn giúp giữ ngữ cảnh giữa các chunk kế tiếp, giảm khả năng mất thông tin khi truy vấn rơi vào vùng biên của một chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=\.\n)|(?<=[.!?])\s+` để tách câu dựa trên dấu chấm, dấu chấm than, dấu hỏi và dấu chấm xuống dòng. Sau đó tôi loại bỏ khoảng trắng thừa và nhóm mỗi `max_sentences_per_chunk` câu thành một chunk. Với các edge case như chuỗi trống hoặc ký tự khoảng trắng, hàm trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán chạy đệ quy theo thứ tự phân cách ưu tiên: `\n\n`, `\n`, `. `, ` ` rồi `''`. Base case là khi đoạn hiện tại ngắn hơn chunk_size hoặc khi không còn separator nào thì dùng cắt cố định. Nếu một phần còn quá dài, hàm tiếp tục phân chia bằng separator tiếp theo.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi lưu mỗi document dưới dạng record gồm `id`, `content`, `metadata` và `embedding` trong một list nội bộ. Khi tìm kiếm, tôi tạo embedding của truy vấn và dùng tích vô hướng (dot product) giữa vector truy vấn và vector tài liệu để ước lượng cosine similarity của embeddings đã chuẩn hóa.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi lọc metadata trước khi truy vấn similarity, nghĩa là chỉ những record thỏa mãn điều kiện filter mới được so sánh với truy vấn. `delete_document` được thực hiện bằng cách giữ lại những record có `metadata['doc_id']` khác với `doc_id` cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunk relevants từ store, ghép nội dung chunk thành một khối context và thêm vào prompt trước câu hỏi. Prompt có dạng `Context: ... \n\nQuestion: ...`, rồi gọi hàm `llm_fn` để tạo phản hồi dựa trên ngữ cảnh.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: python -m pytest tests/test_solution.py -q
```

**Số lượng bài test vượt qua (pass):** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Chính sách đổi trả áp dụng trong 30 ngày." | "Khách hàng có thể trả hàng trong vòng 30 ngày." | cao | | |
| 2 | "Người bán phải cung cấp thông tin sản phẩm chính xác." | "Người bán cần đảm bảo mô tả hàng chính xác." | cao | | |
| 3 | "Chính sách giao hàng mất 3-5 ngày." | "Hình thức thanh toán bằng thẻ tín dụng." | thấp | | |
| 4 | "Tài khoản người bán cần xác thực email." | "Người bán phải xác nhận danh tính trước khi đăng bán." | cao | | |
| 5 | "Chính sách bảo mật dữ liệu người dùng." | "Hàng cấm không được phép đăng bán." | thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Embeddings thường ghi nhận mối liên hệ ý nghĩa giữa các câu nếu chúng cùng nói về cùng một chính sách hoặc chủ đề. Kết quả bất ngờ nhất là khi hai câu dùng từ khác nhau nhưng vẫn có cosine similarity cao, vì embeddings tập trung vào ý nghĩa chung hơn là từ ngữ chính xác.

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

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng mỗi chiến lược chunking có ưu/nhược riêng: Sentence-based giữ tốt câu, Recursive giữ tốt đoạn, còn Fixed-size lại ổn định về kích thước. Nhóm khác đã cho thấy nếu dùng lọc metadata phù hợp, truy xuất có thể chính xác hơn cho câu hỏi dựa trên vai trò hoặc loại tài liệu.

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
