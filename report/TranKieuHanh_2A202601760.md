# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Kiều Hạnh
<<<<<<< HEAD
**Nhóm:** VuaTay
**Ngày:** 03/08/2026
=======
**MSSV:** 2A202601760
**Nhóm:** K4 - Nhóm 1
**Ngày:** 2026-08-03
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
<<<<<<< HEAD
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
=======
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
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
<<<<<<< HEAD
> Với chunk_size=500 và overlap=50, mỗi bước di chuyển là 450 ký tự. Số chunk bằng `ceil((10000 - 500)/450) + 1 = ceil(9500 / 450) + 1 = 22 + 1 = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap=100, bước di chuyển còn 400 ký tự, do đó số chunk tăng lên thành `ceil((10000-500)/400) + 1 = 25` chunk. Độ chồng chéo nhiều hơn giúp giữ ngữ cảnh giữa các chunk kế tiếp, giảm khả năng mất thông tin khi truy vấn rơi vào vùng biên của một chunk.
=======
> Bước di chuyển = `500 - 50 = 450`. Số chunk = `ceil((10000 - 500)/450) + 1 = ceil(9500/450) + 1 = 22 + 1 = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao dùng độ chồng chéo nhiều hơn?**
> Với overlap=100, bước còn 400 ký tự → `ceil(9500/400) + 1 = 25` chunk (tăng 2 so với 23). Overlap lớn hơn giữ ngữ cảnh tại ranh giới giữa hai chunk kế tiếp, giảm khả năng câu trả lời bị nằm vừa vùng cắt mà truy vấn không tìm thấy.
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
<<<<<<< HEAD
> Tôi dùng regex `(?<=\.\n)|(?<=[.!?])\s+` để tách câu dựa trên dấu chấm, dấu chấm than, dấu hỏi và dấu chấm xuống dòng. Sau đó tôi loại bỏ khoảng trắng thừa và nhóm mỗi `max_sentences_per_chunk` câu thành một chunk. Với các edge case như chuỗi trống hoặc ký tự khoảng trắng, hàm trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán chạy đệ quy theo thứ tự phân cách ưu tiên: `\n\n`, `\n`, `. `, ` ` rồi `''`. Base case là khi đoạn hiện tại ngắn hơn chunk_size hoặc khi không còn separator nào thì dùng cắt cố định. Nếu một phần còn quá dài, hàm tiếp tục phân chia bằng separator tiếp theo.
=======
> Tôi tách câu dựa trên dấu câu (dấu chấm, chấm than, hỏi, cuối dòng) rồi nhóm theo `max_sentences_per_chunk`. Nội dung chính sách thường là các điều khoản liệt kê, mỗi câu mang một ý trọn vẹn, nên chunk 2 câu vẫn giữ ngữ cảnh đồng thời tạo nhiều chunk hơn (nhỏ hơn) so với bản 3 câu — giúp đối chứng độ ảnh hưởng của kích thước chunk với cùng chiến lược sentence.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Độ quy theo trật tự separator ưu tiên `\n\n` → `\n` → `. ` → ` ` để chia cho tới khi mỗi phần nhỏ hơn `chunk_size`; dùng cho các đoạn dài không tách ngay được theo câu.
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
<<<<<<< HEAD
> Tôi lưu mỗi document dưới dạng record gồm `id`, `content`, `metadata` và `embedding` trong một list nội bộ. Khi tìm kiếm, tôi tạo embedding của truy vấn và dùng tích vô hướng (dot product) giữa vector truy vấn và vector tài liệu để ước lượng cosine similarity của embeddings đã chuẩn hóa.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi lọc metadata trước khi truy vấn similarity, nghĩa là chỉ những record thỏa mãn điều kiện filter mới được so sánh với truy vấn. `delete_document` được thực hiện bằng cách giữ lại những record có `metadata['doc_id']` khác với `doc_id` cần xóa.
=======
> Mỗi document được embed và lưu thành record (id, content, metadata, embedding). `search` tạo embedding cho câu hỏi rồi tính dot product giữa vector truy vấn và từng record (mô phỏng cosine trên vector chuẩn hóa) để xếp hạng, trả kèm `score`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc metadata trước khi tính similarity: chỉ các record thỏa mãn điều kiện mới được so sánh, tránh lẫn tài liệu cùng chủ đề nhưng khác sàn. `delete_document` giữ lại record có `metadata['doc_id']` khác doc_id cần xóa và trả True nếu có record bị xóa.
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
<<<<<<< HEAD
> Agent lấy top-k chunk relevants từ store, ghép nội dung chunk thành một khối context và thêm vào prompt trước câu hỏi. Prompt có dạng `Context: ... \n\nQuestion: ...`, rồi gọi hàm `llm_fn` để tạo phản hồi dựa trên ngữ cảnh.
=======
> Agent lấy top-k chunk, ghép nội dung thành `Context:` rồi đặt câu hỏi `Question:` cho hàm LLM được inject; agent chỉ dựa vào context được trả, không tự sinh nội dung ngoài phạm vi.
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
<<<<<<< HEAD
..........................................                                                                                     [100%]
42 passed in 0.23s
```
**Số lượng bài test vượt qua (pass):** **42 / 42**
=======
$env:LAB_SOLUTION_PACKAGE='src.TranKieuHanh_2A202601760'
python -m pytest tests -q

..........................................                               [100%]
42 passed
```

**Số lượng bài test vượt qua (pass):** 42 / 42
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

<<<<<<< HEAD
> *Ghi chú: Đo đạc bằng `EMBEDDING_PROVIDER=local` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) để phản ánh đúng giá trị ngữ nghĩa của câu.*

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Chính sách đổi trả áp dụng trong 30 ngày." | "Khách hàng có thể trả hàng trong vòng 30 ngày." | cao | 0.8842 | **Có** |
| 2 | "Người bán phải cung cấp thông tin sản phẩm chính xác." | "Người bán cần đảm bảo mô tả hàng chính xác." | cao | 0.8215 | **Có** |
| 3 | "Chính sách giao hàng mất 3-5 ngày." | "Hình thức thanh toán bằng thẻ tín dụng." | thấp | 0.1834 | **Có** |
| 4 | "Tài khoản người bán cần xác thực email." | "Người bán phải xác nhận danh tính trước khi đăng bán." | cao | 0.7451 | **Có** |
| 5 | "Chính sách bảo mật dữ liệu người dùng." | "Hàng cấm không được phép đăng bán." | thấp | 0.0912 | **Có** |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Kết quả từ model `paraphrase-multilingual-MiniLM-L12-v2` phản ánh rất chính xác mức độ tương đồng ngữ nghĩa giữa các câu tiếng Việt. Điểm ấn tượng nhất là Cặp 1 và Cặp 2 đạt điểm rất cao (>0.82) mặc dù hai câu sử dụng các từ ngữ khác nhau (VD: "áp dụng" vs "có thể", "cung cấp" vs "đảm bảo mô tả"). Điều này khẳng định vector embedding thật mã hóa sâu ý nghĩa/ngữ cảnh của cả câu chứ không chỉ khớp từ khóa (keyword matching).*
=======
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
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

<<<<<<< HEAD
Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src`. **5 câu hỏi này trùng khớp 100% với các thành viên trong nhóm VuaTay**.

**Chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)` | **Embedder:** `EMBEDDING_PROVIDER=local` | **Corpus:** `data/k4_ecommerce`

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng? | "...Danh mục ngành hàng đăng bán bao gồm 13 ngành hàng chính: Thời trang, Mỹ phẩm, Điện tử..." (`shopee-listing-policy.md`, Mục C.3) | 0.8124 | **Có** — Lấy đúng đoạn niêm yết 13 ngành hàng | Trả lời chính xác: Có 13 danh mục ngành hàng chính kèm danh sách chi tiết. |
| 2 | Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm? | "Phiếu công bố mỹ phẩm do Bộ/Sở Y tế cấp... Chứng nhận đại lý/Hợp đồng mua bán/hóa đơn nhập hàng" (`shopee-listing-policy.md`, Mục 3.1) | 0.8412 | **Có** — Trích xuất chính xác các loại giấy tờ pháp lý | Trả lời đầy đủ, đúng trọng tâm các loại giấy tờ bắt buộc theo mục 3.1. |
| 3 | Quy trình trả hàng COM trên Shopee được áp dụng cho đối tượng nào? | "Dịch vụ Trả hàng COM áp dụng cho Người mua thuộc các hạng thành viên Vàng, Kim Cương và ShopeeVIP..." (`shopee-return-refund.md`, Mục 4.1) | 0.8235 | **Có** — Khớp hoàn toàn điều khoản đối tượng áp dụng 4.1 | Liệt kê chính xác đối tượng thành viên Vàng, Kim Cương và ShopeeVIP. |
| 4 | Những loại sản phẩm nào bị cấm đăng bán trên Shopee? | "Danh sách sản phẩm bị cấm bao gồm: Hàng giả/nhái, Vũ khí, Ma túy, Thực phẩm tươi sống không đảm bảo..." (`shopee-prohibited-products.md`) | 0.7981 | **Có** — Bắt đúng danh sách các mặt hàng vi phạm | Tổng hợp rõ ràng danh sách các nhóm sản phẩm bị cấm. |
| 5 | Thời gian đổi trả sản phẩm là bao lâu? *(kèm `metadata_filter={"source_url": ".../77251"}`)* | "Thời hạn gửi yêu cầu trả hàng/hoàn tiền là 07 ngày đối với Shopee Mall và 03 ngày đối với Shop thường..." (`shopee-return-refund.md`, Mục 3.1) | 0.8519 | **Có** — Metadata filter hoạt động chính xác | Trả lời đúng chính xác thời hạn 7 ngày (Mall) và 3 ngày (Shop thường). |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5** câu hỏi trả về chunk có liên quan trực tiếp.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng mỗi chiến lược chunking có ưu/nhược riêng: Sentence-based giữ tốt câu, Recursive giữ tốt đoạn, còn Fixed-size lại ổn định về kích thước. Nhóm khác đã cho thấy nếu dùng lọc metadata phù hợp, truy xuất có thể chính xác hơn cho câu hỏi dựa trên vai trò hoặc loại tài liệu.
=======
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
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
<<<<<<< HEAD
| Khởi động (Warm-up) | 5/ 5 |
| Hướng tiếp cận của tôi (My Approach) | 10/ 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 5/ 10 |
| **Tổng phần cá nhân** | **55 / 60** |
=======
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |
>>>>>>> 0400906fa21a4c6270f7a49c4e1495c9a6d13e5e
