# Báo cáo Nhóm – Lab 7: Embedding & Vector Store

**Nhóm:** K4 - Nhóm 1
**Thành viên:** Trần Bình Minh (2A202601434), Tạ Đăng Đức (2A202601772), Trần An Thắng (2A202601756), Trần Kiều Hạnh (2A202601760), Lương Bảo Long (2A202601682)
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
| shopee-listing-policy | FixedSizeChunker (`fixed_size`) | 44 | 495.5 | Trung bình – chunk có thể cắt giữa câu |
| shopee-listing-policy | SentenceChunker (`by_sentences`) | 79 | 273.2 | Cao – tách theo câu, giữ nguyên nghĩa |
| shopee-listing-policy | RecursiveChunker (`recursive`) | 53 | 409.2 | Khá cao – ưu tiên tách theo đoạn/câu nhưng vẫn giữ giới hạn chunk |

### Chiến lược của từng thành viên

**Thành viên 1 – Trần Bình Minh**
- **Loại chiến lược:** SentenceChunker (chia theo câu)
- **Mô tả & lý do chọn cho chủ đề này:** Chính sách Shopee/Tiki có nhiều điều khoản liệt kê, câu dài và phức tạp. Chia theo câu đảm bảo mỗi chunk chứa một ý trọn vẹn, giúp agent trích dẫn chính xác khi trả lời. Câu tiếng Việt thường kết thúc bằng dấu ". ", "! ", "? " nên regex phân tách ổn định.
- **Code snippet (nếu custom):** Không cần custom, dùng `SentenceChunker(max_sentences_per_chunk=3)` sẵn có.

**Thành viên 2 – Tạ Đăng Đức (2A202601772)**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=400`, `overlap=50`)
- **Mô tả & lý do chọn cho chủ đề này:** Dùng làm đối chứng (control) cho SentenceChunker — cắt cố định theo ký tự, không quan tâm ranh giới câu/mục. Mục tiêu là đo xem việc bỏ qua cấu trúc ngữ nghĩa (so với chia theo câu) ảnh hưởng thế nào đến độ chính xác truy xuất trên cùng corpus/câu hỏi.
- **Code snippet (nếu custom):** Không custom, dùng `FixedSizeChunker(chunk_size=400, overlap=50)` sẵn có. Script chạy: `bench_TaDangDuc_2A202601772.py` (repo root).

**Thành viên 3 – Trần An Thắng (2A202601756)**
- **Loại chiến lược:** `HeadingSectionChunker` (chunk theo heading/section).
- **Tham số:** `chunk_size=700`, corpus `data/k4_ecommerce`.
- **Mô tả & lý do chọn:** Tài liệu chính sách được tổ chức theo các mục Markdown; mỗi section thường là một đơn vị nghĩa tự nhiên. Section dài được hạ xuống recursive, và heading được gắn lại vào mọi mảnh con để không mất ngữ cảnh.
- **Benchmark script:** `python -m src.TranAnThang_2A202601756.bench`.

**Thành viên 4 – Trần Kiều Hạnh (2A202601760)**
- **Loại chiến lược:** SentenceChunker (max_sentences_per_chunk=3)
- **Mô tả & lý do chọn cho chủ đề này:** Chọn SentenceChunker với tham số 3 câu/chunk nhằm đánh giá độc lập hiệu quả của việc bảo toàn ranh giới ngữ nghĩa câu đối với văn bản quy định/chính sách e-commerce. Việc gom đúng 3 câu liên tiếp giúp chunk duy trì dung lượng vừa đủ (tránh quá tải nhiễu như chunk dung lượng lớn), đồng thời không ngắt đôi ngữ cảnh điều kiện — hành vi vốn là điểm yếu của FixedSizeChunker.
- **Code snippet / Script:** Dùng SentenceChunker(max_sentences_per_chunk=3). Script chạy: `python src/TranKieuHanh_2A202601760/bench.py` 

**Thành viên 5 – Lương Bảo Long (2A202601682)**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=400`).
- **Tham số:** 400 ký tự/chunk, corpus `data/k4_ecommerce`.
- **Mô tả & lý do chọn:** Chia ưu tiên theo cấu trúc (\n\n → \n → . → space) rồi **gộp ngược** các mảnh nhỏ về đúng `chunk_size` — vừa tôn trọng ranh giới đoạn/câu, vừa giữ chunk đủ lớn để chứa trọn đáp án. Đây là chiến lược trung gian giữa fixed-size và sentence.
- **Benchmark script:** `python src/LuongBaoLong_2A202601682/bench.py`.

---

### So Sánh Giá Trị Các Thành Viên

Kết quả benchmark chính thức bằng **local embeddings** (paraphrase-multilingual-MiniLM-L12-v2, `EMBEDDING_PROVIDER=local`) trên cùng corpus và 5 câu hỏi. Chấm theo `docs/SCORING.md`: **2đ** – đáp án (`answer_marks`) trong top-3; **1đ** – đúng tài liệu trong top-3 nhưng đáp án ngoài top-3; **0đ** – không tìm thấy.

| Thành viên | Chiến lược (Strategy) | #Chunk | Q1 | Q2 | Q3 | Q4 | Q5* | Điểm (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|--------|----|----|----|----|----|-----------|-----------|----------|
| Trần Bình Minh | SentenceChunker (3 câu) | 200 | 1 | 1 | 1 | 1 | 2 | 6/10 | Giữ ngữ cảnh câu trọn vẹn, ổn định ở Q5 filter | Đáp án nằm rải nhiều chunk nên chỉ Q5 trúng mark |
| Trần Kiều Hạnh | SentenceChunker (2 câu) | 299 | 1 | 1 | 1 | 1 | 2 | 6/10 | Chunk nhỏ, dễ tìm đúng tài liệu | Đáp án thường "nằm giữa" các chunk, tạo nhiều chunk nhất |
| Lương Bảo Long | RecursiveChunker (400) | 185 | 1 | 2 | 1 | 1 | 2 | 7/10 | Q2 trúng mục C.3.1 Mỹ phẩm — gộp đúng ranh giới đoạn | Danh sách dài (cấm, danh mục) trải nhiều chunk |
| Tạ Đăng Đức | FixedSizeChunker (400, 50) | 169 | 1 | 2 | 1 | 1 | 2 | 7/10 | Q2 trúng mục Mỹ phẩm; overlap giữ biên | Cắt cứng làm đáp án Q1/Q3/Q4 lệch chunk |
| Trần An Thắng | HeadingSectionChunker (700) | 127 | 1 | 2 | 2 | 2 | 2 | **9/10** | Giữ đúng section chứa câu trả lời (Q2-Q5) — tốt nhất nhóm | Q1: mục C.3 danh mục bị trộn trong chunk lớn với nội dung khác |

*Q5 chấm trên kết quả **đã filter** `source_url=.../77251` (bắt buộc); không filter vẫn có 3/5 thành viên lẫn Tiki vào top-3.

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **HeadingSectionChunker (Trần An Thắng) là tốt nhất: 9/10.** Tài liệu chính sách được viết theo cấu trúc mục (section) rõ ràng, và câu hỏi đánh giá nhắm đúng vào các section cụ thể (C.3.1 Mỹ phẩm, 4.1 COM, 4.x cấm, 3.2 thời gian) — chunk theo heading giữ trọn từng mục nên đáp án không bị cắt mất. SentenceChunker/Recursive/Fixed chỉ đạt 6-7/10 vì đáp án nằm trong câu/đoạn nhưng thường bị "kẹp" giữa các chunk hoặc bị gộp lẫn nội dung khác. Khi tài liệu không có heading chuẩn, RecursiveChunker (Long) là phương án thay thế an toàn.

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

**⚠️ Cần nhóm kiểm tra lại Query #1:** Khi chạy thử với `FixedSizeChunker`, mục "C.5. Danh mục ngành hàng" trong `shopee-listing-policy.md` (dòng 330-338) thực ra **không liệt kê danh mục nào** — chỉ có hướng dẫn chọn đúng danh mục. Danh sách ~13 ngành hàng (Mỹ phẩm, Thực phẩm chức năng, Thời trang..., Bách hóa Online, Mẹ & Bé, Đồng Hồ, Voucher & Dịch vụ, Đồ chơi, Nhà sách Online, Băng đĩa phim, thuốc không kê đơn...) thực chất nằm ở **Mục C.3 "Quy định riêng với một số ngành hàng"** (các mục con 3.1 → 3.13), không phải C.5. Gold answer cần sửa lại trích dẫn đúng "Mục C.3" trước khi tính điểm retrieval, nếu không câu hỏi này sẽ luôn bị chấm sai (không tài liệu/chunk nào ở C.5 chứa đáp án).

**Lưu ý về Query #5 (cần filter metadata):** Câu hỏi "Thời gian đổi trả sản phẩm là bao lâu?" không nêu rõ sàn thương mại điện tử nào. Corpus có 2 tài liệu cùng chủ đề đổi trả (Shopee và Tiki) với từ vựng tương tự nhưng đáp án khác nhau (15 ngày vs 30 ngày). Nếu không lọc metadata, retrieval có thể trả về chunks từ cả 2 tài liệu và agent đưa ra câu trả lời mơ hồ hoặc sai đối tượng. Cần dùng `metadata_filter={"source_url": "https://help.shopee.vn/portal/4/article/77251"}` để chỉ truy xuất chính sách Shopee.

### Tổng hợp chất lượng truy xuất của nhóm

Kết quả chính thức (local embeddings, MiniLM-L12-v2) — đánh dấu theo `answer_marks` trong top-3:

| # | Câu hỏi | Minh (Sentence 3) | Hạnh (Sentence 2) | Long (Recursive 400) | Đức (Fixed 400/50) | Thắng (Heading 700) |
|---|---------|-------------------|-------------------|----------------------|---------------------|----------------------|
| 1 | Số liệu – bao nhiêu danh mục? | 1 (đúng doc, đáp án C.3 ngoài top-3) | 1 | 1 | 1 | 1 |
| 2 | Điều kiện – giấy tờ mỹ phẩm? | 1 | 1 | **2** | **2** | **2** |
| 3 | Quy trình – đối tượng COM? | 1 | 1 | 1 | 1 | **2** |
| 4 | Liệt kê – sản phẩm cấm? | 1 | 1 | 1 | 1 | **2** |
| 5 | Ngoại lệ – thời gian đổi trả (sau filter) | **2** | **2** | **2** | **2** | **2** |
| | **Tổng /10** | **6** | **6** | **7** | **7** | **9** |

Nhận xét rút ra từ số liệu thật:
- **Q5 (filter) là câu "ăn điểm" duy nhất cho mọi chiến lược** — metadata filter triệt tiêu hoàn toàn nhược điểm của embedding khi có 2 tài liệu cùng chủ đề (Shopee/Tiki).
- **Q1 là failure case chung cả 5 thành viên:** danh mục ngành hàng nằm ở các mục C.3.1→C.3.13; chunk giữ mục đó không lọt top-3 với bất kỳ chiến lược nào (score top-1 chỉ 0.76–0.82, lạc sang chunk "hướng dẫn chung").
- **Q2 (giấy tờ mỹ phẩm) chỉ trúng với chunk ≥ 400 ký tự** (Recursive, Fixed, Heading) — đáp án nằm gọn trong 1 đoạn dài, chunk nhỏ (Sentence 2-3 câu) tách rời "câu hỏi chủ đề" và "liệt kê giấy tờ".
- **Q3/Q4 trúng đáp án chỉ có HeadingSectionChunker** — section 4.1 (COM) và danh sách 4.x là đơn vị mục hoàn chỉnh, chiến lược theo heading giữ trọn ranh giới mục.

### Kết quả benchmark strategy Heading/Section của Trần An Thắng

Đã chạy `python -m src.TranAnThang_2A202601756.bench` trên `data/k4_ecommerce` với `HeadingSectionChunker(chunk_size=700)`, tạo **127 chunks**. Bản chạy offline bằng mock embedding cho kết quả: Q1 đúng tài liệu kỳ vọng ở top-2; Q2 ở top-3; Q3 có Shopee ở top-1; Q4 không có Shopee trong top-3; Q5 sau filter chỉ trả về chunks của `shopee-return-refund`. Đây là kết quả kiểm tra pipeline, không dùng để chấm semantic vì mock embedding gần như ngẫu nhiên.

Gemini embedding đã được thử với API key nhưng dịch vụ trả `503 UNAVAILABLE` trong lúc embed corpus; do đó chưa ghi nhận điểm Gemini chính thức và cần chạy lại khi API ổn định.

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** – top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Số liệu – bao nhiêu danh mục? | SentenceChunker | Có | FixedSizeChunker có thể cắt đứt danh sách giữa câu. Đối chứng thực tế (Tạ Đăng Đức, FixedSizeChunker chunk_size=400): top-3 KHÔNG chứa mục C.3 đúng nội dung — top-1 score=0.78 nhưng lạc sang đoạn "giấy phép bán lẻ rượu". |
| 2 | Điều kiện – giấy tờ mỹ phẩm? | SentenceChunker | Có | Câu trả lời nằm trong 1 câu dài, cần chunk giữ nguyên câu. Đối chứng (FixedSizeChunker): cũng đúng (top-1 score=0.72, đúng mục 3.1 Mỹ phẩm) — câu này dễ với cả 2 chiến lược vì thông tin nằm liền mạch trong 1 đoạn ngắn. |
| 3 | Quy trình – đối tượng COM? | SentenceChunker | Có | Câu trả lời nằm ở section 4.1, rõ ràng. Đối chứng (FixedSizeChunker): top-3 KHÔNG chứa mục 4.1 — cả 3 kết quả lạc sang mục 2, 8, 9 (điều kiện áp dụng chung, hoàn tiền) dù cùng tài liệu shopee-return-refund. |
| 4 | Liệt kê – sản phẩm cấm? | RecursiveChunker | Có | RecursiveChunker gộp nhiều danh sách con vào 1 chunk. Đối chứng (FixedSizeChunker): một phần — top-1 chỉ là tiêu đề trang, top-2/3 lạc sang shopee-listing-policy (mục hạn sử dụng, mục cấm phân biệt chủng tộc) thay vì đúng tài liệu shopee-prohibited-products. |
| 5 | Ngoại lệ – thời gian đổi trả | Cần filter theo `source_url` | **Cần filter** | Không filter → lẫn Shopee/Tiki → trả lời sai. Đối chứng (FixedSizeChunker) xác nhận đúng lỗi này bằng số liệu thật: `search_with_filter()` lọc đúng (chỉ trả về shopee-return-refund), nhưng gọi `agent.answer()` mặc định (không filter) thì context bị lẫn chunk từ tiki-return-policy ("365 ngày nếu sản phẩm lỗi kỹ thuật") — minh chứng sống rằng `KnowledgeBaseAgent.answer()` cần được gọi cùng kết quả đã lọc, không thể bỏ qua bước filter. |

**Lọc metadata có giúp ích không? Ở câu nào?**
> Có, lọc metadata rất hữu ích ở Query #5 (câu hỏi đổi trả). Cùng một câu hỏi, corpus chứa 2 tài liệu cùng chủ đề (Shopee và Tiki) với từ vựng gần giống nhau nhưng đáp án khác nhau (15 ngày vs 30 ngày). Khi không lọc, embedding similarity không phân biệt được nguồn gốc tài liệu → retrieval trả về chunks từ cả 2 → agent trả lời mơ hồ hoặc sai. Khi dùng `metadata_filter={"source_url": "..."}`, chỉ truy xuất chunks từ tài liệu đúng → trả lời chính xác. Đây là minh chứng rõ ràng rằng metadata filtering là cần thiết khi corpus có nhiều tài liệu cùng chủ đề nhưng dành cho đối tượng khác nhau.

---

## 4. Thuyết trình (Demo) & Bài học nhóm – Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Cùng một câu hỏi (đổi trả), corpus có 2 tài liệu cùng chủ đề nhưng dành cho đối tượng khác nhau (Shopee vs Tiki) → metadata filtering là bắt buộc để phân biệt.
> 2. Chiến lược chunk theo cấu trúc tài liệu (HeadingSectionChunker, 9/10) vượt trội chiến lược theo độ dài/ký tự (6–7/10): câu hỏi đánh giá nhắm đúng vào các section chính sách, và heading chunk giữ trọn ranh giới mục chứa câu trả lời.
> 3. Kích thước chunk quyết định độ chính xác: đáp án dạng "liệt kê giấy tờ" nằm gọn trong 1 đoạn dài → chunk ≥ 400 ký tự (Recursive/Fixed/Heading) trúng, chunk 2-3 câu (Sentence) bị tách rời; ngược lại chunk quá lớn dễ trộn nội dung (Q1 của Thắng).

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus, cùng câu hỏi, nhưng chiến lược chunking khác nhau dẫn đến kết quả retrieval khác nhau. Chiến lược ảnh hưởng đến khả năng giữ ngữ cảnh (chunk coherence) và độ chính xác của retrieval (retrieval precision). Metadata schema thiết kế tốt (có `customer_role`, `source_url`, `category`) giúp phân biệt tài liệu cùng chủ đề mà không phụ thuộc vào embedding similarity.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thu thập thêm tài liệu từ nhiều sàn TMĐT khác nhau (Lazada, TikTok Shop) để mở rộng corpus và tăng độ khó cho retrieval. Cũng sẽ bổ sung thêm trường metadata như `last_updated` và `applicable_region` để hỗ trợ lọc theo thời gian và khu vực.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá | Điểm tối đa |
|----------|-------------------|-------------|
| Lựa chọn tài liệu (Document Set Quality) | **9 / 10** | 10 |
| Thiết kế chiến lược (Strategy Design) | **13 / 15** | 15 |
| Chất lượng truy xuất (Retrieval Quality) | **8 / 10** | 10 |
| Thuyết trình (Demo) | **4 / 5** | 5 |
| **Tổng phần nhóm** | **34 / 40** | 40 |

**Giải thích chi tiết:**

**1. Lựa chọn tài liệu (9/10):**
- ✓ Chủ đề rõ ràng, đúng định dạng K4 (chính sách TMĐT/hỗ trợ khách hàng).
- ✓ 5 tài liệu công khai (Shopee + Tiki), có `source_url`, `retrieved_at`, đầy đủ metadata `customer_role`, `category`, `language`, `doc_id`.
- ✓ Data governance checklist đầy đủ.
- ✗ Trừ 1 điểm: corpus chỉ giới hạn 2 sàn (Shopee, Tiki) — chưa đa dạng nguồn (Lazada, TikTok Shop) để mở rộng phạm vi.

**2. Thiết kế chiến lược (13/15):**
- ✓ Đã chạy baseline analysis so sánh 3 chiến lược (FixedSize, Sentence, Recursive) trên `shopee-listing-policy` với số liệu cụ thể (44/79/53 chunks).
- ✓ Mỗi thành viên có chiến lược riêng (Sentence 3 câu, Sentence 2 câu, Recursive 400, Fixed 400/50, HeadingSection 700) kèm code snippet, tham số, lý do chọn.
- ✓ Có bảng benchmark đầy đủ 5 thành viên với local embeddings (MiniLM-L12-v2) — điểm số cụ thể từng thành viên (6/10, 7/10, 9/10).
- ✓ Rút ra chiến lược tốt nhất: HeadingSectionChunker (9/10).
- ✗ Trừ 2 điểm: chưa benchmark đầy đủ với Gemini/local embedding so sánh trên cùng 5 câu hỏi; chưa đánh giá chi phí (latency, cost) giữa các phương án.

**3. Chất lượng truy xuất (8/10):**
- ✓ 5 câu hỏi đa dạng (số liệu, điều kiện, quy trình, liệt kê, ngoại lệ cần filter).
- ✓ Có gold answer cụ thể, có trích dẫn section.
- ✓ Đã phát hiện vấn đề Query #1 (gold answer trỏ C.5 nhưng đáp án thực tế ở C.3) — chứng tỏ chất lượng review cao.
- ✓ Có insight rõ ràng: Q5 chỉ "ăn điểm" khi filter; Q1 failure case chung; Q3/Q4 chỉ HeadingSectionChunker trúng; Q2 cần chunk ≥400 ký tự.
- ✗ Trừ 2 điểm: Q1 vẫn là failure chung (giảm ~1 điểm); chưa có báo cáo chi tiết điểm retrieval giữa các thành viên trên cùng embedder (mock vs local chưa thống nhất).

**4. Thuyết trình (4/5):**
- ✓ Có 3 insights chất lượng, có số liệu thực tế đi kèm.
- ✓ Bài học rõ ràng: metadata filter bắt buộc ở Q5; chunk theo heading vượt trội chunk theo độ dài; kích thước chunk quyết định precision.
- ✓ Có phần "Nếu làm lại, sẽ thay đổi gì" thể hiện tư duy cải tiến.
- ✗ Trừ 1 điểm: chưa có kế hoạch demo trực quan (screencast, slides), chưa phân công thời gian/thuyết trình viên cụ thể.
