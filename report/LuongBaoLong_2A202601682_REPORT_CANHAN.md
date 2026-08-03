# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** LuongBaoLong
**MSSV:** 2A202601682
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai đoạn văn bản có độ tương tự cosine cao, điều đó có nghĩa là chúng nằm "gần nhau" trong không gian vector - chúng chia sẻ cùng một hướng ngữ nghĩa, bất kể độ dài tuyệt đối của chúng. Nói cách khác, hai văn bản nói về cùng một chủ đề, sử dụng từ vựng và ngữ cảnh tương tự nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả hàng trong vòng 30 ngày kể từ ngày mua"
- Câu B: "Quý khách có thể hoàn trả sản phẩm trong thời hạn 1 tháng kể từ khi nhận hàng"
- Tại sao tương đồng: Cả hai câu đều nói về chính sách đổi trả với khoảng thời gian 30 ngày, sử dụng từ vựng liên quan như "đổi trả", "ngày", và cùng ngữ cảnh về quyền lợi khách hàng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Hướng dẫn thanh toán qua thẻ tín dụng Visa"
- Câu B: "Cách nấu món phở bò truyền thống Việt Nam"
- Tại sao khác: Hai câu thuộc hoàn toàn các lĩnh vực khác nhau - một về tài chính/thanh toán, một về ẩm thực. Không có sự chồng chéo về từ vựng hay ngữ cảnh ngữ nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity đo độ tương đồng về hướng (direction) của hai vector, không quan tâm đến độ lớn (magnitude) của chúng. Trong NLP, điều này quan trọng vì một câu dài và một câu ngắn có thể nói cùng một ý nhưng sẽ có vector norm rất khác nhau. Euclid đo khoảng cách tuyệt đối nên sẽ cho kết quả khác biệt giữa hai câu cùng ý nhưng khác độ dài, trong khi cosine sẽ nhận ra chúng tương tự nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
>
> Áp dụng công thức: `số lượng chunk = ceil((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))`
>
> Thay số: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
>
> Đáp án: **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng từ 50 lên 100:
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25` chunks
>
> Số chunk tăng từ 23 lên 25. Độ chồng chéo cao hơn giúp đảm bảo rằng các ý/chủ đề không bị cắt đứt giữa hai chunk, đặc biệt quan trọng khi ranh giới chunk không trùng với ranh giới tự nhiên của câu/đoạn văn. Tuy nhiên, overlap cao cũng tăng số lượng chunk và có thể gây trùng lặp thông tin, ảnh hưởng đến hiệu suất và chi phí.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi sử dụng regex `(?<=[.!?])\s+(?=[A-ZÀ-ỹ])` để tách câu dựa trên dấu câu (. ! ?) theo sau bởi khoảng trắng và chữ in hoa/tiếng Việt. Sau đó nhóm các câu lại thành chunks với số câu tối đa được quy định. Edge cases: xử lý text rỗng, dấu câu cuối text không có khoảng trắng, và các câu ngắn liên tiếp.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy ưu tiên tách theo separator lớn nhất trước (\n\n), nếu phần nào vẫn lớn hơn chunk_size thì tiếp tục tách theo separator nhỏ hơn (\n, . , space). Base case: khi hết separator hoặc text đủ nhỏ (<= chunk_size). Cuối cùng merge các chunk nhỏ liên tiếp nếu kết hợp lại vẫn <= chunk_size.

**`SemanticChunker.chunk`** — hướng tiếp cận:
> Sử dụng embedding function để tính cosine similarity giữa các câu liền kề. Nếu similarity thấp (boundary score cao), đó là ranh giới ngữ nghĩa - nên cắt chunk ở đó. Fallback: nếu không có embedding function, dùng Jaccard similarity trên từ vựng. Kết hợp cả threshold ngữ nghĩa và giới hạn kích thước để tìm chunk boundaries tối ưu.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi lưu trữ documents và embeddings trong hai list đồng bộ (_documents, _embeddings). Mỗi document được embed bằng hàm embedding_fn được truyền vào lúc khởi tạo. Khi search, query được embed, sau đó tính cosine similarity với tất cả embeddings trong store, sắp xếp giảm dần theo score và trả về top_k kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Filter được áp dụng TRƯỚC khi tính similarity - chỉ những documents có metadata khớp với filter mới được đưa vào tính toán. Xóa document: tìm tất cả indices của doc_id (có thể nhiều chunks), xóa khỏi cả hai lists, và rebuild index để đảm bảo consistency.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tôi xây dựng prompt theo cấu trúc: system prompt (hướng dẫn LLM) → context block (các chunks đã retrieve với nguồn và score) → câu hỏi người dùng → hướng dẫn trả lời. Mỗi chunk được format với số thứ tự, nguồn, và score để LLM có thể ưu tiên chunk có độ tương tự cao hơn. Kết quả cuối cùng được gắn thêm phần trích nguồn để tăng tính đáng tin cậy.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.51s ==============================
```

**Số lượng bài test vượt qua (pass): 42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> **Kết quả thực tế** được chạy với `LocalEmbedder` (model `paraphrase-multilingual-MiniLM-L12-v2` từ sentence-transformers) thông qua script `scripts/run_predictions.py`. Output chi tiết: `scripts/similarity_results.txt`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách đổi trả hàng trong vòng 30 ngày kể từ ngày mua. | Quý khách có thể hoàn trả sản phẩm trong thời hạn 1 tháng kể từ khi nhận hàng. | cao | 0.5602 | ✓ |
| 2 | Thanh toán bằng thẻ tín dụng Visa hoặc Mastercard được chấp nhận. | Các phương thức thanh toán được hỗ trợ gồm: thẻ ATM, thẻ visa, và ví điện tử MoMo. | cao | 0.6994 | ✓ |
| 3 | Phí vận chuyển cho đơn hàng dưới 500.000đ là 25.000đ. | Cách nấu món phở bò truyền thống Việt Nam với nước dùng đậm đà. | thấp | 0.4254 | ✓ |
| 4 | Chính sách bảo mật thông tin khách hàng theo tiêu chuẩn quốc tế. | Chúng tôi cam kết bảo vệ dữ liệu cá nhân của bạn bằng mã hóa SSL 256-bit. | cao | 0.5264 | ✓ |
| 5 | Thời gian giao hàng tiêu chuẩn là 3-5 ngày làm việc. | Đơn hàng sẽ được xử lý trong 24 giờ và giao trong khoảng 1 tuần. | cao | 0.4158 | ✗ |

**Tổng kết:** 4/5 dự đoán đúng (đạt 80%).

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> **Cặp 5** (giao hàng) là kết quả bất ngờ nhất: dự đoán "cao" nhưng thực tế chỉ 0.4158. Cả hai câu đều nói về thời gian giao hàng, nhưng có sự khác biệt tinh tế mà model có thể đã nắm bắt được:
> - Câu A nhấn mạnh "tiêu chuẩn" (standard) và "ngày làm việc" (business days).
> - Câu B đề cập "xử lý trong 24 giờ" (processing) + "giao trong khoảng 1 tuần" (delivery window).
> - Model có thể đã tách "thời gian xử lý" (processing time) và "thời gian giao" (delivery time) thành hai khái niệm riêng, làm giảm similarity.
>
> **Cặp 2** cũng thú vị: cùng chủ đề "thanh toán" nhưng câu A hẹp (Visa/Mastercard) còn câu B rộng (ATM/Visa/MoMo) → similarity 0.6994 cho thấy model nhận ra đây là cùng lĩnh vực nhưng khác phạm vi.
>
> **Bài học:** Embeddings không chỉ so khớp từ vựng mà còn hiểu được **ngữ cảnh và phạm vi ngữ nghĩa**. Hai câu cùng chủ đề nhưng có scope khác nhau (cụ thể vs. tổng quát, processing vs. delivery) có thể có similarity thấp hơn mong đợi. Điều này cho thấy tầm quan trọng của việc test trên dữ liệu thực tế thay vì chỉ dựa vào intuition.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> **Cấu hình chạy:**
> - Embedder: `LocalEmbedder` (model `paraphrase-multilingual-MiniLM-L12-v2`)
> - Chunker: `SemanticChunker` (lựa chọn cá nhân) với `threshold=0.3, min_chunk_size=2, max_chunk_size=8`
> - Tổng số chunks: 185 (chia từ 5 tài liệu gốc)
> - Câu hỏi lấy từ `REPORT_NHOM.md` (mục 3) - cùng bộ 5 câu hỏi với các thành viên nhóm
> - Output chi tiết: `scripts/retrieval_results.txt`

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng? | Chunk từ `shopee-listing-policy` (Mục B. Quy định chung) | 0.5961 | ✓ (Top-1) | Agent sinh câu trả lời dựa trên context, có trích nguồn shopee-listing-policy. |
| 2 | Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm? | Chunk từ `shopee-listing-policy` (Mục B. Quy định chung) | 0.4676 | ✓ (Top-1) | Agent sinh câu trả lời với context từ shopee-listing-policy. |
| 3 | Quy trình trả hàng COM (Change of Mind) trên Shopee được áp dụng cho đối tượng nào? | Chunk từ `shopee-listing-policy` (không đúng tài liệu) | 0.5292 | ⚠ Top-3 mới có (Top-2, score=0.4862 từ shopee-return-refund) | Chunk đúng ở vị trí thứ 2 - agent có thể trả lời nhưng cần LLM tốt để tổng hợp. |
| 4 | Những loại sản phẩm nào bị cấm đăng bán trên Shopee theo danh sách cấm/hạn chế? | Chunk từ `shopee-listing-policy` (không đúng tài liệu) | 0.5285 | ✗ (Không liên quan trong top-3) | Top-3 hoàn toàn không chứa chunk từ shopee-prohibited-products. |
| 5 | Thời gian đổi trả sản phẩm trên Shopee là bao lâu? | Chunk từ `shopee-return-refund` (đúng tài liệu) | 0.4680 | ✓ (Top-1) | Top-1 trùng tài liệu shopee-return-refund; dùng `metadata_filter` chỉ trả về 3 chunks từ tài liệu này. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **4 / 5**

**Phân tích chi tiết:**

- **Query 1, 2, 5**: Truy xuất đúng tài liệu ở top-1 → thể hiện SemanticChunker tốt cho query tổng quát về Shopee.
- **Query 3 (COM)**: Chunk liên quan ở top-2 (0.4862) thay vì top-1. Lý do: chunk "Quy định chung" của shopee-listing-policy có nhiều từ khóa phổ biến ("Shopee", "sản phẩm", "quy định") nên được xếp hạng cao hơn. → Bài học: cần re-rank hoặc tăng kích thước chunk để có thêm ngữ cảnh cụ thể.
- **Query 4 (sản phẩm cấm)**: Top-3 hoàn toàn không chứa chunk từ `shopee-prohibited-products`. Đây là điểm yếu rõ ràng - cần cải thiện bằng cách (a) re-rank sử dụng BM25 + embedding hybrid, (b) tăng top-k, hoặc (c) chunk theo đề mục để có chunk riêng cho phần "Danh sách hàng cấm".
- **Query 5 với filter**: Khi dùng `metadata_filter={"doc_id": "shopee-return-refund"}`, cả 3 chunks top-1 đều từ đúng tài liệu, chứng minh metadata filtering giúp giải quyết vấn đề khi có nhiều tài liệu cùng chủ đề (Shopee + Tiki).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Qua quá trình so sánh chiến lược chunking với thành viên Trần Bình Minh (SentenceChunker), tôi học được rằng:
> 1. **SentenceChunker đơn giản nhưng ít tốn kém**: không cần embedding model, chạy nhanh, dễ debug. Phù hợp khi corpus nhỏ hoặc cần prototype nhanh.
> 2. **SemanticChunker mạnh hơn về mặt lý thuyết** (giữ luồng ý liên tục) nhưng phụ thuộc nhiều vào chất lượng embedding model. Với corpus lớn, chi phí embed mỗi câu có thể là vấn đề.
> 3. **Hybrid approach** là hướng đi tốt: dùng SentenceChunker làm baseline, SemanticChunker cho các đoạn quan trọng, hoặc dùng BM25 + embedding để re-rank.
> 4. Bài học lớn nhất: **không có chiến lược nào tốt nhất cho tất cả** - cần benchmark trên corpus cụ thể và đánh giá theo use case (precision vs. recall, latency, cost).

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 (42/42 tests pass với 0.51s) |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 (4/5 dự đoán đúng với LocalEmbedder) |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 (4/5 relevant trong top-3, query 4 không có chunk liên quan) |
| **Tổng phần cá nhân** | **54 / 60** |
