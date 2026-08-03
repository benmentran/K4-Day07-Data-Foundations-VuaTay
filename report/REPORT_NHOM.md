# Báo cáo Nhóm – Lab 7: Embedding & Vector Store

**Nhóm:** VuaTay
**Thành viên:** LuongBaoLong (2A202601682), TranBinhMinh (2A202601434)
**Ngày:** 2026-08-03

> Nộp 1 bản / nhóm. Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán...) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) – Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề theo định dạng lớp K4:** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán).

**Phạm vi cụ thể nhóm tập trung:**
> Chính sách đăng bán & hàng cấm trên Shopee (cho người bán); chính sách đổi trả & thanh toán trên Shopee và Tiki (cho người mua).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định đăng bán sản phẩm trên Shopee | https://help.shopee.vn/portal/4/article/77246 | 2026-08-03 / not-stated | ~29,248 | doc_id=shopee-listing-policy, customer_role=seller, category=listing-policy, language=vi |
| 2 | Danh sách sản phẩm bị cấm/hạn chế trên Shopee | https://help.shopee.vn/portal/4/article/77247 | 2026-08-03 / not-stated | ~17,470 | doc_id=shopee-prohibited-products, customer_role=seller, category=prohibited-items, language=vi |
| 3 | Chính sách trả hàng và hoàn tiền Shopee | https://help.shopee.vn/portal/4/article/77251 | 2026-08-03 / 2026-03-11 | ~26,401 | doc_id=shopee-return-refund, customer_role=both, category=returns-policy, language=vi |
| 4 | Phương thức thanh toán trên Tiki | https://hotro.tiki.vn/knowledge-base/post/970 | 2026-08-03 / not-stated | ~1,834 | doc_id=tiki-payment-methods, customer_role=buyer, category=payment-policy, language=vi |
| 5 | Chính sách đổi trả sản phẩm Tiki | https://hotro.tiki.vn/knowledge-base/post/802-chinh-sach-doi-tra-san-pham | 2026-08-03 / not-stated | ~4,664 | doc_id=tiki-return-policy, customer_role=buyer, category=returns-policy, language=vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hay tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `customer_role` | string | seller, buyer, both | Phân biệt tài liệu dành cho người bán vs người mua – cùng chủ đề (đổi trả) nhưng nội dung khác nhau tùy đối tượng |
| `category` | string | listing-policy, prohibited-items, returns-policy, payment-policy | Lọc theo lĩnh vực chính sách khi truy vấn |
| `source_url` | string | URL gốc | Truy vết nguồn, phân biệt Shopee vs Tiki khi cùng chủ đề đổi trả |
| `language` | string | vi | Đảm bảo truy xuất đúng ngôn ngữ |
| `doc_id` | string | shopee-listing-policy, ... | Định danh duy nhất cho mỗi tài liệu, dùng để xóa/ lọc theo document |

---

## 2. Thiết kế chiến lược (Strategy Design) – Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| shopee-listing-policy | FixedSizeChunker (`fixed_size`) | ~58 | ~500 | Trung bình – chunk có thể cắt giữa câu |
| shopee-listing-policy | SentenceChunker (`by_sentences`) | ~120 | ~243 | Cao – tách theo câu, giữ nguyên nghĩa |
| shopee-listing-policy | RecursiveChunker (`recursive`) | ~35 | ~835 | Cao – tách theo đoạn lớn trước, giữ ngữ cảnh tốt |

### Chiến lược của từng thành viên

**Thành viên 1 – Trần Bình Minh**
- **Loại chiến lược:** SentenceChunker (chia theo câu)
- **Mô tả & lý do chọn cho chủ đề này:** Chính sách Shopee/Tiki có nhiều điều khoản liệt kê, câu dài và phức tạp. Chia theo câu đảm bảo mỗi chunk chứa một ý trọn vẹn, giúp agent trích dẫn chính xác khi trả lời. Câu tiếng Việt thường kết thúc bằng dấu ". ", "! ", "? " nên regex phân tách ổn định.
- **Code snippet (nếu custom):** Không cần custom, dùng `SentenceChunker(max_sentences_per_chunk=3)` sẵn có.

**Thành viên 1 — LuongBaoLong (2A202601682)**
- **Loại chiến lược:** Semantic Chunking (Custom - theo ngữ nghĩa)
- **Mô tả & lý do chọn cho chủ đề này:** Tôi chọn Semantic Chunking vì các tài liệu TMĐT (chính sách đổi trả, thanh toán, vận chuyển) có đặc điểm ngữ cảnh liên tục - một ý thường trải qua nhiều câu, không nên cắt ngang. Chiến lược này sử dụng embeddings để nhóm các câu có ngữ cảnh liên quan với nhau, dựa trên độ tương tự cosine giữa các câu liền kề. Điều này giữ được luồng ý của văn bản và tránh cắt ngang các điều khoản liên quan.
- **Code snippet (SemanticChunker):**
```python
class SemanticChunker:
    def __init__(self, threshold: float = 0.3, min_chunk_size: int = 2, max_chunk_size: int = 8):
        self.threshold = threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def _semantic_boundary_score(self, sentence_a: str, sentence_b: str) -> float:
        # Tính điểm ranh giới ngữ nghĩa (0-1)
        # 1.0 = khác nhau hoàn toàn (ranh giới mạnh)
        # 0.0 = giống nhau (cùng ngữ cảnh)
        ...

    def chunk(self, text: str) -> list[str]:
        # 1. Tách văn bản thành các câu
        # 2. Tính điểm ranh giới ngữ nghĩa giữa các câu
        # 3. Nhóm câu vào chunks dựa trên threshold và kích thước
        ...
```

**Thành viên 2 — TranBinhMinh (2A202601434)**
- **Loại chiến lược:** SentenceChunker (chia theo câu)
- **Mô tả & lý do chọn cho chủ đề này:** Chính sách Shopee/Tiki có nhiều điều khoản liệt kê, câu dài và phức tạp. Chia theo câu đảm bảo mỗi chunk chứa một ý trọn vẹn, giúp agent trích dẫn chính xác khi trả lời. Câu tiếng Việt thường kết thúc bằng dấu ". ", "! ", "? " nên regex phân tách ổn định.
- **Code snippet (nếu custom):** Không cần custom, dùng `SentenceChunker(max_sentences_per_chunk=3)` sẵn có.

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trần Bình Minh | SentenceChunker (3 sentences/chunk) | /10 | Giữ ngữ cảnh câu trọn vẹn, phù hợp điều khoản liệt kê | Chunk nhỏ → nhiều chunk cho 1 tài liệu, tốn bộ nhớ |
| LuongBaoLong | SemanticChunking (custom, threshold=0.3, min=2, max=8) | **6/10** | Giữ luồng ý liên tục, nhóm câu cùng ngữ cảnh; 4/5 query có chunk liên quan trong top-3 | Cần embedding model (LocalEmbedder `paraphrase-multilingual-MiniLM-L12-v2`), chậm hơn fixed/sentence; query về danh sách cấm (Q4) không truy xuất được top-3 đúng |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Với dữ liệu TMĐT (chính sách đổi trả, thanh toán), **Semantic Chunking** có tiềm năng tốt nhất vì nó giữ được các điều khoản và luật liên quan trong cùng một chunk. Tuy nhiên, nếu tài liệu có cấu trúc rõ ràng (headers, paragraphs), **SentenceChunker** với `max_sentences_per_chunk=3` là lựa chọn đơn giản và hiệu quả. RecursiveChunker cũng tốt nhưng có thể gộp quá nhiều nội dung vào 1 chunk. Trên thực tế, cần chạy benchmark để xác nhận chiến lược nào phù hợp nhất cho corpus cụ thể.

**Hướng tiếp cận của LuongBaoLong (SemanticChunker) — chi tiết:**
> - Sử dụng `LocalEmbedder` (model `paraphrase-multilingual-MiniLM-L12-v2`) để tính cosine similarity giữa các câu liền kề.
> - Threshold = 0.3, min_chunk_size = 2, max_chunk_size = 8 câu/chunk.
> - Chia 5 tài liệu gốc thành **185 chunks** (cao hơn SentenceChunker ~120 do ranh giới ngữ nghĩa).
> - **Điểm yếu nhận diện được:** Chunk "Quy định chung" của shopee-listing-policy có nhiều từ khóa phổ biến ("Shopee", "sản phẩm", "quy định") nên được xếp hạng cao hơn chunk cụ thể về COM/sản phẩm cấm. → Cải thiện bằng cách re-rank BM25 + embedding hybrid, hoặc chunk theo đề mục.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) – Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời đúng.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | (Số liệu) Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng? | Khoảng 14 danh mục: Mỹ phẩm, Thực phẩm chức năng, Thời trang/Đồ lót, Thời trang nam, Thiết bị điện tử, Bách hóa Online, Mẹ & Bé, Đồ gia dụng, Voucher & Dịch vụ, Đồ chơi, Nhà sách Online, Băng đĩa phim/ca nhạc/sân khấu, Sản phẩm thuộc kho hàng không kê đơn, và Sản phẩm khác. (Mục C.5 của shopee-listing-policy) | shopee-listing-policy, section C.5 |
| 2 | (Điều kiện) Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm? | Giấy chứng nhận công bố phù hợp quy định an toàn thực phẩm; Chứng nhận đại lý/hợp đồng mua bán/hóa đơn nhập hàng; Giấy xác nhận quảng cáo. (Mục C.3.1 của shopee-listing-policy) | shopee-listing-policy, section C.3.1 |
| 3 | (Quy trình) Quy trình trả hàng COM (Change of Mind) trên Shopee được áp dụng cho đối tượng nào? | Chỉ áp dụng cho thành viên Chương trình khách hàng thân thiết Shopee (hạng Vàng/VIP Kim Cương) hoặc người mua đang sử dụng Gói ShopeeVIP. (Mục 4.1 của shopee-return-refund) | shopee-return-refund, section 4.1 |
| 4 | (Liệt kê) Những loại sản phẩm nào bị cấm đăng bán trên Shopee theo danh sách cấm/hạn chế? | Bao gồm: hàng vi phạm bản quyền, thiết bị quân sự, tài liệu phản động, dịch vụ bất hợp pháp, súng/vũ khí, chất ma túy, thuốc lá, sản phẩm người lớn, thiết bị giám sát, hóa chất nguy hiểm, bộ phận cơ thể người, hàng cấm theo luật, hàng giả/gian lận, v.v. (Mục 4 của shopee-prohibited-products, từ 4.1 đến 4.28) | shopee-prohibited-products, section 4 |
| 5 | (Ngoại lệ – cần filter) Thời gian đổi trả sản phẩm là bao lâu? | **Shopee:** 15 ngày kể từ ngày nhận hàng (đơn hàng COD/chuyển khoản dưới 200 triệu), hoặc 24 giờ đối với sản phẩm thực phẩm/tươi sống. **Tiki:** 30 ngày kể từ ngày nhận hàng với mọi sản phẩm (ngoại trừ một vài sản phẩm đặc thù). (shopee-return-refund mục 3.2; tiki-return-policy mục 1) | shopee-return-refund section 3.2 + tiki-return-policy section 1 |

**Lưu ý về Query #5 (cần filter metadata):** Câu hỏi "Thời gian đổi trả sản phẩm là bao lâu?" không nêu rõ sàn thương mại điện tử nào. Corpus có 2 tài liệu cùng chủ đề đổi trả (Shopee và Tiki) với từ vựng tương tự nhưng đáp án khác nhau (15 ngày vs 30 ngày). Nếu không lọc metadata, retrieval có thể trả về chunks từ cả 2 tài liệu và agent đưa ra câu trả lời mơ hồ hoặc sai đối tượng. Cần dùng `metadata_filter={"source_url": "https://help.shopee.vn/portal/4/article/77251"}` để chỉ truy xuất chính sách Shopee.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** – top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Số liệu – bao nhiêu danh mục? | SentenceChunker | Có | FixedSizeChunker có thể cắt đứt danh sách giữa câu |
| 2 | Điều kiện – giấy tờ mỹ phẩm? | SentenceChunker | Có | Câu trả lời nằm trong 1 câu dài, cần chunk giữ nguyên câu |
| 3 | Quy trình – đối tượng COM? | SentenceChunker | Có | Câu trả lời nằm ở section 4.1, rõ ràng |
| 4 | Liệt kê – sản phẩm cấm? | RecursiveChunker | Có | RecursiveChunker gộp nhiều danh sách con vào 1 chunk |
| 5 | Ngoại lệ – thời gian đổi trả | Cần filter theo `source_url` | **Cần filter** | Không filter → lẫn Shopee/Tiki → trả lời sai |

**Kết quả truy xuất thực tế của LuongBaoLong (SemanticChunker + LocalEmbedder):**

> Cấu hình chạy: `SemanticChunker(threshold=0.3, min_chunk_size=2, max_chunk_size=8)` + `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`). Corpus: 5 tài liệu → **185 chunks**. Output chi tiết: `scripts/retrieval_results.txt`.

| # | Câu hỏi | Top-1 doc | Top-1 score | Relevant trong top-3? | Nhận xét |
|---|---------|-----------|-------------|----------------------|---------|
| 1 | Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng? | `shopee-listing-policy` | 0.5961 | ✓ Top-1 | SemanticChunker bám tốt câu hỏi về "quy định" của Shopee |
| 2 | Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm? | `shopee-listing-policy` | 0.4676 | ✓ Top-1 | Chunk "Quy định chung" của shopee-listing-policy đứng top-1, top-3 cũng có chunk liên quan |
| 3 | Quy trình trả hàng COM (Change of Mind) trên Shopee được áp dụng cho đối tượng nào? | `shopee-listing-policy` (không đúng) | 0.5292 | ⚠ Top-2 mới có chunk `shopee-return-refund` (0.4862) | Chunk phổ biến "Quy định chung" ăn điểm cao hơn; cần re-rank để ưu tiên chunk cụ thể |
| 4 | Những loại sản phẩm nào bị cấm đăng bán trên Shopee theo danh sách cấm/hạn chế? | `shopee-listing-policy` (không đúng) | 0.5285 | ✗ Không có chunk `shopee-prohibited-products` trong top-3 | Điểm yếu lớn nhất: top-3 lạc sang các đoạn khác của shopee-listing-policy thay vì đúng tài liệu cấm |
| 5 | Thời gian đổi trả sản phẩm là bao lâu? | `shopee-return-refund` | 0.4680 | ✓ Top-1 (và Top-3) | Đúng tài liệu ở top-1; với `metadata_filter={"doc_id":"shopee-return-refund"}` cả 3 chunks đều từ đúng tài liệu |

**Relevant trong top-3: 4/5.** Phân tích chi tiết xem trong `report/LuongBaoLong_2A202601682_REPORT_CANHAN.md` (mục 5).

**Lọc metadata có giúp ích không? Ở câu nào?**
> Có, lọc metadata rất hữu ích ở Query #5 (câu hỏi đổi trả). Cùng một câu hỏi, corpus chứa 2 tài liệu cùng chủ đề (Shopee và Tiki) với từ vựng gần giống nhau nhưng đáp án khác nhau (15 ngày vs 30 ngày). Khi không lọc, embedding similarity không phân biệt được nguồn gốc tài liệu → retrieval trả về chunks từ cả 2 → agent trả lời mơ hồ hoặc sai. Khi dùng `metadata_filter={"source_url": "..."}`, chỉ truy xuất chunks từ tài liệu đúng → trả lời chính xác. Đây là minh chứng rõ ràng rằng metadata filtering là cần thiết khi corpus có nhiều tài liệu cùng chủ đề nhưng dành cho đối tượng khác nhau.

---

## 4. Thuyết trình (Demo) & Bài học nhóm – Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Cùng một câu hỏi (đổi trả), corpus có 2 tài liệu cùng chủ đề nhưng dành cho đối tượng khác nhau (Shopee vs Tiki) → metadata filtering là bắt buộc để phân biệt.
> 2. SentenceChunker cho điểm precision cao hơn FixedSizeChunker cho các truy vấn điều kiện/liệt kê vì giữ nguyên ngữ cảnh câu.
> 3. FixedSizeChunker có thể cắt đứt danh sách giữa câu, gây ra retrieval không đầy đủ cho query dạng số liệu.
> 4. **SemanticChunker (LuongBaoLong):** 4/5 query có chunk liên quan trong top-3, nhưng query về **danh sách sản phẩm cấm** (Q4) thất bại — top-3 toàn lạc sang các đoạn khác của `shopee-listing-policy`. Nguyên nhân: chunk "Quy định chung" chứa nhiều từ khóa phổ biến (Shopee/sản phẩm/quy định) ăn điểm cao hơn chunk chứa danh sách cụ thể trong `shopee-prohibited-products`. → Bài học: cần **hybrid retrieval** (BM25 + embedding) hoặc chunk theo đề mục rõ ràng để ưu tiên đúng tài liệu.
> 5. **Metadata filtering giải quyết triệt để Q5:** với `metadata_filter={"doc_id":"shopee-return-refund"}`, cả 3 chunks top-1 đều từ đúng tài liệu → trả lời chính xác "15 ngày / 24h" thay vì bị lẫn sang Tiki (30 ngày).

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus, cùng câu hỏi, nhưng chiến lược chunking khác nhau dẫn đến kết quả retrieval khác nhau. Chiến lược ảnh hưởng đến khả năng giữ ngữ cảnh (chunk coherence) và độ chính xác của retrieval (retrieval precision). Metadata schema thiết kế tốt (có `customer_role`, `source_url`, `category`) giúp phân biệt tài liệu cùng chủ đề mà không phụ thuộc vào embedding similarity.
>
> Bài học từ so sánh SentenceChunker (Trần Bình Minh) vs SemanticChunker (LuongBaoLong):
> - SentenceChunker **đơn giản, nhanh, dễ debug**, không cần embedding model.
> - SemanticChunker **mạnh hơn về lý thuyết** (giữ luồng ý liên tục) nhưng phụ thuộc chất lượng embedding model và **có thể bị "ăn điểm" bởi chunk phổ biến** (như Q3 và Q4 trong thực nghiệm của LuongBaoLong).
> - **Hybrid approach** là hướng đi tốt: SentenceChunker làm baseline, SemanticChunker cho các đoạn quan trọng, hoặc dùng BM25 + embedding để re-rank.
> - Bài học lớn nhất: **không có chiến lược nào tốt nhất cho tất cả** - cần benchmark trên corpus cụ thể và đánh giá theo use case (precision vs. recall, latency, cost).

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thu thập thêm tài liệu từ nhiều sàn TMĐT khác nhau (Lazada, TikTok Shop) để mở rộng corpus và tăng độ khó cho retrieval. Cũng sẽ bổ sung thêm trường metadata như `last_updated` và `applicable_region` để hỗ trợ lọc theo thời gian và khu vực.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
