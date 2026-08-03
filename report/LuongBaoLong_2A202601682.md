# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lương Bảo Long
**MSSV:** 2A202601682
**Nhóm:** K4 - Nhóm 1
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai embedding vector cùng hướng (góc gần 0) => hai văn bản gần nhau về nghĩa. Cosine gần 1 đồng nghĩa cùng chủ đề hoặc nội dung tương đương.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả cho phép hoàn tiền trong vòng 30 ngày."
- Câu B: "Khách hàng có thể yêu cầu hoàn tiền trong 30 ngày sau khi nhận sản phẩm."
- Tại sao tương đồng: cùng một quy định hoàn tiền 30 ngày.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chính sách giao hàng mất 3-5 ngày."
- Câu B: "Hình thức thanh toán bằng thẻ tín dụng."
- Tại sao khác: giao hàng vs thanh toán — chủ đề khác.

**Tại sao độ tương tự cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**
> Cosine chuẩn hóa độ lớn vector, chỉ giữ hướng. Text embedding của các câu dài/ngắn khác nhau sẽ có norm khác nhau; Euclid bị norm này làm sai thứ tự, còn cosine phản ánh đúng quan hệ ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Bước di chuyển = `500 - 50 = 450`. Số chunk = `ceil((10000-500)/450) + 1 = 22 + 1 = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100? Tại sao dùng overlap?**
> Với overlap=100: bước còn 400 → `ceil(9500/400)+1 = 25` chunk. Overlap giữ ngữ cảnh ở vùng ranh giới giữa các chunk, khiến truy vấn rơi vào biên chunk vẫn có đủ thông tin.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Chia đệ quy theo bảng separator ưu tiên (`\n\n` → `\n` → `. ` → ` ` → `''`). Một phần chỉ được giữ lại khi ≤ `chunk_size`; nếu lớn hơn sẽ chuyển xuống separator kế tiếp. Điểm cải tiến: sau phân chia tôi **gộp lại (merge)** các mảnh liên tiếp cho đến đủ `chunk_size`, tránh việc một câu dài hơn `chunk_size` bị vỡ vụn thành các chunk từ đơn lẻ làm hỏng chất lượng embedding tìm kiếm.

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tách theo dấu câu rồi gom `max_sentences_per_chunk` câu; phần sentence giữ ngữ cảnh câu nhưng tạo nhiều chunk nhỏ.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Record = {id, content, metadata, embedding}. Search tính dot product tương đương cosine (vector đã chuẩn hóa) giữa query embedding và từng record, xếp hạng giảm dần, trả top-k kèm `score`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc metadata trước rồi mới tìm similarity trong tập con; đổi trả Query#5 (Shopee vs Tiki) cần đúng kỹ thuật này để không lẫn dữ liệu. Delete xóa record theo `metadata['doc_id']`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Lấy top-k chunk, nối thành `Context`, chèn `Question` và gọi hàm LLM inject; agent trả lời dựa hẳn lên context.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```
$env:LAB_SOLUTION_PACKAGE='src.LuongBaoLong_2A202601682'
python -m pytest tests -q

..........................................                               [100%]
42 passed
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Điểm thực tế tính bằng `LocalEmbedder`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách đổi trả áp dụng trong 30 ngày. | Khách hàng có thể trả hàng trong vòng 30 ngày. | cao | 0.8258 | Có |
| 2 | Người bán phải cung cấp thông tin sản phẩm chính xác. | Người bán cần đảm bảo mô tả hàng chính xác. | cao | 0.9238 | Có |
| 3 | Chính sách giao hàng mất 3-5 ngày. | Hình thức thanh toán bằng thẻ tín dụng. | thấp | 0.2345 | Có |
| 4 | Tài khoản người bán cần xác thực email. | Người bán phải xác nhận danh tính trước khi đăng bán. | cao | 0.5123 | Trung bình |
| 5 | Chính sách bảo mật dữ liệu người dùng. | Hàng cấm không được phép đăng bán. | thấp | 0.1427 | Có |

**Kết quả nào bất ngờ nhất?**
> Cặp 4 (0.51) dự đoán "cao" nhưng thực tế ở mức trung bình — model nhận ra mối liên hệ "xác thực/phân định danh người bán" nhưng không xem hai bước này là cùng một việc. Embedding ngữ nghĩa phản ánh độ liên quan chủ đề, không phải sự tương đương cú pháp.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong `src/LuongBaoLong_2A202601682`.
Chiến lược: `RecursiveChunker(chunk_size=400)` — corpus `data/k4_ecommerce` — **185 chunks**.
Embedding **local** (MiniLM-L12-v2).

| # | Câu hỏi (Query) | Top-1 chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quy định đăng bán liệt kê bao nhiêu danh mục ngành hàng? | Top-1 = `shopee-listing-policy` (nội dung chung, chưa tới danh mục C.3) | 0.76 | Tài liệu đúng; đáp án C.3 không trong top-3 | Agent DEMO |
| 2 | Người bán cần giấy tờ gì cho ngành mỹ phẩm? | Top-1 = `shopee-listing-policy` — đúng mục C.3.1 Mỹ phẩm | 0.71 | **Có** — "Phiếu công bố mỹ phẩm"/"Chứng nhận đại lý" trong top-3 | Đủ context để trả lời |
| 3 | COM áp dụng cho đối tượng nào? | Top-1 = `shopee-return-refund` (chunk khác section 4.1) | 0.63 | Tài liệu đúng; đáp án 4.1 không trong top-3 | Agent DEMO |
| 4 | Sản phẩm bị cấm đăng bán? | Top-1/2 = `shopee-prohibited-products` | 0.79 | Tài liệu đúng; list "Súng, vũ khí"/"ma túy" không trong top-3 | Agent DEMO |
| 5 | Thời gian đổi trả sản phẩm? | **Filter** `source_url=.../77251` → top-3 toàn `shopee-return-refund` | 0.75 | **Có** — đáp án trong top-3 sau filter | Bắt buộc filter |

**Bao nhiêu câu hỏi trả về chunk liên quan trong top-3?** 5 / 5 theo doc_id; đáp án trong top-3 theo `answer_marks`: 2 / 5 (Q2 và Q5).

**Điều hay nhất tôi học được từ thành viên/nhóm khác (qua demo):**
> `RecursiveChunker` gộp nội dung liên quan về một mục nên với các câu trả lời nằm gọn trong một đoạn (mỹ phẩm ở Q2) chiến thắng retrievals; với câu hỏi liệt kê dài (danh mục, sản phẩm cấm) câu trả lời bị phân tán nhiều chunk hơn. Kết hợp với demo của các bạn, em thấy cần đọc metadata filter bắt buộc cho câu hỏi "chung chung" kiểu Q5.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |