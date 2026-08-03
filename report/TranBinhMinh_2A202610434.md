# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Bình Minh
**Nhóm:** K4 - Nhóm 1
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector có góc giữa chúng gần bằng 0°, tức là cùng hướng trong không gian vector. Với text embedding, điều này nghĩa là hai văn bản được biểu diễn với nội dung/ngữ nghĩa gần giống nhau (nói về cùng một chủ đề, cùng ý).

**Ví dụ có độ tương tự CAO:**
- Câu A: Shopee hoàn tiền cho người mua trong 15 ngày kể từ khi nhận hàng.
- Câu B: Shopee hoàn tiền trong vòng 15 ngày sau khi người mua nhận hàng.
- Tại sao tương đồng: cùng ý nghĩa (hoàn tiền 15 ngày sau nhận hàng), gần như trùng từ vựng nên vector embedding gần như trùng hướng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Cách đăng bán sản phẩm trên Shopee.
- Câu B: Chính sách bảo mật thông tin cá nhân của Tiki.
- Tại sao khác: hai chủ đề hoàn toàn khác nhau (đăng bán vs bảo mật), các từ vựng không chồng lấn về ngữ nghĩa nên vector gần như vuông góc.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Text embeddings thường được chuẩn hóa (normalize) về độ dài 1, nên khoảng cách Euclid chỉ phản ánh sự khác nhau về "độ dài" chứ không phản ánh mối quan hệ hướng. Cosine chỉ xét góc giữa hai vector nên không bị ảnh hưởng bởi độ dài câu (2 câu cùng nghĩa nhưng dài ngắn khác nhau vẫn cho cosine cao, trong khi Euclid lại lớn).

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính:
> - Bước nhảy (step) = chunk_size − overlap = 500 − 50 = **450**.
> - Chunk đầu chiếm 500 ký tự đầu; mỗi chunk sau bắt đầu dịch đi 450 ký tự.
> - Số chunk = ceil((10000 − 500) / 450) + 1 = ceil(9500 / 450) + 1 = 22 + 1 = **23 chunks**.
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Overlap tăng → step giảm: step = 500 − 100 = 400 → ceil((10000 − 500) / 400) + 1 = 24 + 1 = **25 chunks** (nhiều hơn). Overlap lớn giúp các chunk liền kề chia sẻ phần nội dung ở ranh giới, tránh mất ngữ cảnh khi câu/ý bị cắt đứt giữa hai chunk, tăng độ chính xác khi truy xuất từng mảnh thông tin.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex tách câu với lookbehind: `(?<=[.!?])\s+` và `(?<=[.!?])\n` để tách ngay sau mỗi dấu chấm/cảm thán/câu hỏi, rồi bỏ câu rỗng và strip khoảng trắng. Gom tối đa `max_sentences_per_chunk` câu vào một chunk; các câu lẻ còn lại ở cuối văn bản được gom thành chunk cuối (edge case: text rỗng trả về `[]`).

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Duyệt danh sách separator theo thứ tự ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Với separator đầu tiên, tách text thành nhiều phần; phần có độ dài ≤ chunk_size thì giữ nguyên, phần dài hơn thì **đệ quy** tách tiếp bằng separator kế tiếp. Base case: hết separator hoặc gặp `sep == ""` → trả về `[current_text]`. Text rỗng trả về `[]`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` tính embedding của từng `doc.content` bằng `self._embedding_fn` và lưu record `{id, content, embedding, metadata}` vào danh sách in-memory (khi có ChromaDB thì dùng `collection.add`). `search` nhúng câu hỏi rồi tính cosine (dot product, vì vector mock đã chuẩn hóa) với embedding của mọi record, sắp xếp giảm dần theo score và trả về top_k với đủ các key `content`/`score`/`metadata`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` **lọc trước, chấm điểm sau**: giữ lại record có metadata khớp toàn bộ `metadata_filter` (lọc theo mọi cặp key-value) rồi mới tính similarity trên tập đã lọc. `delete_document` (in-memory) tạo lại danh sách loại bỏ record có `id == doc_id`; nếu số record giảm thì trả `True`, không đổi thì trả `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer(question, top_k)` gọi `store.search(question, top_k)` để lấy các chunk phù hợp nhất, nối `content` của các chunk thành khối `Context`, rồi dựng prompt mẫu `Context:\n...\n\nQuestion: ...` và gọi `llm_fn(prompt)`. Ngữ cảnh được "inject" toàn bộ vào trước câu hỏi để LLM có nguồn tham chiếu khi sinh câu trả lời (mô hình RAG).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.0.2, pluggy-1.5.0 -- F:\miniconda3\python.exe
cachedir: .pytest_cache
rootdir: F:\K4-Day07-Data-Foundations-VuaTay
plugins: anyio-4.10.0, Faker-40.13.0, langsmith-0.8.3, asyncio-1.3.0, cov-7.1.0, mock-3.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
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
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
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

============================= 42 passed in 0.41s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Shopee hoàn tiền cho người mua trong 15 ngày kể từ khi nhận hàng. | Shopee hoàn tiền trong vòng 15 ngày sau khi người mua nhận hàng. | cao | 0.2023 | Sai |
| 2 | Làm sao để tôi trả hàng trên Shopee? | Quy trình trả hàng và hoàn tiền trên Shopee như thế nào? | cao | 0.0496 | Sai |
| 3 | Cách đăng bán sản phẩm trên Shopee. | Chính sách bảo mật thông tin cá nhân của Tiki. | thấp | 0.0740 | Đúng |
| 4 | Trả hàng COM chỉ áp dụng cho thành viên hạng Vàng và VIP Kim Cương. | Hàng bị cấm bao gồm vũ khí, ma túy và hàng giả. | thấp | -0.0951 | Đúng |
| 5 | Tiki cho phép đổi trả sản phẩm trong 30 ngày. | Shopee cho phép đổi trả sản phẩm trong 15 ngày. | cao | 0.1351 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Điều bất ngờ nhất: các cặp câu gần như đồng nghĩa (cặp 1, 2) lại có điểm rất thấp (0.20 và 0.05), không khác mấy so với các cặp khác chủ đề (cặp 3). Nguyên nhân là `MockEmbedder` dùng hash MD5 để sinh vector, nên nó **không hề hiểu ngữ nghĩa** — hai câu cùng nghĩa nhưng khác từ vựng sẽ được hash thành vector khác nhau hoàn toàn. Điều này cho thấy text embedding chỉ biểu diễn "ý nghĩa" khi được học từ ngôn ngữ thực (ví dụ model đa ngữ `paraphrase-multilingual-MiniLM-L12-v2`); vector hash ngẫu nhiên không mang bất kỳ mối quan hệ ngữ nghĩa nào.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng? | Quy định mô tả sản phẩm đã qua sử dụng (shopee-listing-policy) | 0.4180 | Không (đúng tài liệu, sai nội dung — không chứa danh mục) | Agent chỉ lặp lại context, không đưa ra con số danh mục |
| 2 | Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm? | Quy định hạn sử dụng của sản phẩm/thực phẩm (shopee-listing-policy) | 0.3627 | Không (đúng tài liệu, sai mục — không phải giấy tờ mỹ phẩm) | Agent không nêu được danh sách giấy tờ yêu cầu |
| 3 | Quy trình trả hàng COM trên Shopee được áp dụng cho đối tượng nào? | Top-1: quy định nhãn hàng (shopee-listing-policy); Top-2: Điều kiện áp dụng (shopee-return-refund) | 0.3584 | Có (top-2 thuộc đúng tài liệu return-refund) | Agent trả lời chưa đúng đối tượng COM (cần top-1 chính xác) |
| 4 | Những loại sản phẩm nào bị cấm đăng bán trên Shopee? | "Các nội dung không được phép đăng bán" (shopee-listing-policy) | 0.2748 | Có (chunk đúng chủ đề cấm đăng) | Agent trích được nội dung nghiêm cấm nhưng chưa đủ danh sách 4.1–4.28 |
| 5 | Thời gian đổi trả sản phẩm là bao lâu? | Hàng cấm (shopee-prohibited-products); Top-2: tiki-return-policy | 0.2846 | Có (top-2 thuộc tiki-return-policy; shopee-return-refund có trong top-5) | Agent trả lời sai do mock không phân biệt Shopee vs Tiki |

> **Lưu ý:** Bảng trên chạy với `MockEmbedder` (hash-based, không hiểu ngữ nghĩa) nên kết quả phản ánh giới hạn của mock, không phải chất lượng chiến lược. Khi chạy lại với filter metadata cho câu 5 (`metadata_filter={"source_url": ".../article/77251"}`), top-5 kết quả đều nằm trong `shopee-return-refund` — minh chứng filter hoạt động đúng: nó thu hẹp không gian tìm kiếm về đúng tài liệu của sàn cần hỏi (Shopee), không còn lẫn Tiki.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Với corpus có nhiều tài liệu cùng chủ đề (Shopee vs Tiki cùng chính sách đổi trả), metadata filtering là công cụ quyết định để giữ câu trả lời đúng đối tượng; embedding similarity một mình (nhất là mock) không đủ để phân biệt nguồn tài liệu. Đồng thời, chiến lược chunking (SentenceChunker vs RecursiveChunker) ảnh hưởng trực tiếp đến việc chunk giữ được trọn ý pháp lý hay bị cắt giữa câu.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |

