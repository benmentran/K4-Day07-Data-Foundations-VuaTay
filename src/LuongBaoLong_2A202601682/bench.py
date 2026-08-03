"""
bench.py — benchmark 5 câu hỏi đánh giá với strategy riêng của thành viên.

Thành viên: Lương Bảo Long (2A202601682)
Strategy  : RecursiveChunker(chunk_size=400) — tách theo mức ưu tiên separator,
            dùng chung chunk_size với FixedSizeChunker của nhóm để so sánh công bằng.

Pipeline nạp dữ liệu ĐƯỢC DÙNG LẠI từ ingest.py (parse front matter -> chunk bằng
CHUNKER -> gắn doc_id + metadata lên từng chunk -> nạp vào EmbeddingStore).

  - DÒNG DUY NHẤT khác với bạn cùng nhóm: CHUNKER
  - Embedder: dùng chung (mock | local | openai) qua EMBEDDING_PROVIDER.
  - 5 query giống hệt nhóm (report/REPORT_NHOM.md §3).

Chạy:
    python src/LuongBaoLong_2A202601682/bench.py
    # hoặc
    EMBEDDING_PROVIDER=local python src/LuongBaoLong_2A202601682/bench.py
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest import build_knowledge_base  # noqa: E402
from src.LuongBaoLong_2A202601682.agent import KnowledgeBaseAgent  # noqa: E402
from src.LuongBaoLong_2A202601682.chunking import RecursiveChunker  # noqa: E402
from src.LuongBaoLong_2A202601682.embeddings import (  # noqa: E402
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)

# ---------------------------------------------------------------------------
# 1) Strategy riêng — DÒNG DUY NHẤT khác với bạn cùng nhóm
# ---------------------------------------------------------------------------
CHUNKER = RecursiveChunker(chunk_size=400)
STRATEGY_LABEL = "RecursiveChunker(chunk_size=400)"

DATA_DIR = "data/k4_ecommerce"

SHOPEE_RETURN_SOURCE_URL = "https://help.shopee.vn/portal/4/article/77251"

QUERIES = [
    {
        "type": "số liệu",
        "query": "Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng?",
        "gold": "~14 danh mục (Mỹ phẩm, Thực phẩm chức năng, Mẹ & Bé, Voucher & Dịch vụ, ... Sản phẩm khác).",
        "expect_doc_id": "shopee-listing-policy",
        "expect_section": "Quy định đăng bán – Mục danh mục ngành hàng (3.1 – 3.10)",
        "answer_marks": ["Mẹ & Bé", "Voucher & Dịch vụ"],
    },
    {
        "type": "điều kiện",
        "query": "Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm?",
        "gold": "Phiếu công bố mỹ phẩm do Bộ/Sở Y tế cấp; Chứng nhận đại lý/hợp đồng mua bán/hóa đơn nhập hàng; giấy xác nhận quảng cáo.",
        "expect_doc_id": "shopee-listing-policy",
        "expect_section": "3.1. Mỹ phẩm",
        "answer_marks": ["Phiếu công bố mỹ phẩm", "Chứng nhận đại lý"],
    },
    {
        "type": "quy trình",
        "query": "Quy trình trả hàng COM (Change of Mind) trên Shopee được áp dụng cho đối tượng nào?",
        "gold": "Chỉ áp dụng cho thành viên Chương trình khách hàng thân thiết Shopee (hạng Vàng/VIP Kim Cương) hoặc người mua đang dùng Gói ShopeeVIP.",
        "expect_doc_id": "shopee-return-refund",
        "expect_section": "4.1. Đối tượng áp dụng (Trả hàng COM)",
        "answer_marks": ["thân thiết", "ShopeeVIP"],
    },
    {
        "type": "liệt kê",
        "query": "Những loại sản phẩm nào bị cấm đăng bán trên Shopee theo danh sách cấm/hạn chế?",
        "gold": "Súng/vũ khí, ma túy, hàng giả, thiết bị quân sự, hàng vi phạm bản quyền, ...",
        "expect_doc_id": "shopee-prohibited-products",
        "expect_section": "4.x Danh sách cấm/hạn chế (từ 4.1 – 4.28)",
        "answer_marks": ["Súng, vũ khí", "ma túy"],
    },
    {
        "type": "ngoại lệ (cần filter theo source)",
        "query": "Thời gian đổi trả sản phẩm là bao lâu?",
        "gold": "Shopee: 15 ngày (thực phẩm tươi/đông lạnh: 24 giờ).  Tiki: 30 ngày.",
        "expect_doc_id": "shopee-return-refund | tiki-return-policy",
        "expect_section": "shopee-return-refund §3.2 + tiki-return-policy §1",
        "answer_marks": ["mười lăm) ngày", "30 ngày"],
        "requires_filter": True,
        "filter_field": "source_url",
        "filter_value": SHOPEE_RETURN_SOURCE_URL,
    },
]


class _CachedEmbed:
    def __init__(self, func):
        self._func = func
        self._cache: dict[str, list[float]] = {}

    def __call__(self, text: str) -> list[float]:
        key = hashlib.md5(text.encode()).hexdigest()
        if key not in self._cache:
            self._cache[key] = self._func(text)
        return self._cache[key]


def _select_embedder():
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return _CachedEmbed(
                LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
            ), f"local ({LOCAL_EMBEDDING_MODEL})"
        except Exception:
            print("Local embedder không sẵn sàng; tạm dùng mock.")
    if provider == "openai":
        try:
            return _CachedEmbed(
                OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
            ), "openai"
        except Exception:
            print("OpenAI embedder không sẵn sàng; tạm dùng mock.")
    return _mock_embed, "mock"


def _demo_llm(prompt: str) -> str:
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] Generated answer from prompt preview: {preview}..."


def _run_search(store, query: str, metadata_filter=None, top_k: int = 3):
    if metadata_filter:
        return store.search_with_filter(query, top_k=top_k, metadata_filter=metadata_filter)
    return store.search(query, top_k=top_k)


def _render_top3(results) -> str:
    lines = []
    for rank, r in enumerate(results, start=1):
        lines.append(
            f"  top{rank} score={r['score']:.4f} "
            f"doc_id={r['metadata'].get('doc_id')} "
            f"src={r['metadata'].get('source')}"
        )
        lines.append(f"    {r['content'][:170].replace(chr(10), ' ')}")
    return "\n".join(lines)


def main() -> int:
    print("=== BENCHMARK — K4 Nhóm 1 · Lương Bảo Long (2A202601682) ===")
    print(f"Strategy: {STRATEGY_LABEL}")
    embedder, backend = _select_embedder()
    print(f"Embedder backend: {backend}")

    print(f"\n=== Nạp corpus: {DATA_DIR} ===")
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=CHUNKER)
    print(f"Chunks đã nạp: {store.get_collection_size()}")

    agent = KnowledgeBaseAgent(store=store, llm_fn=_demo_llm)

    for q in QUERIES:
        print("\n" + "=" * 76)
        print(f"[Q — {q['type']}] {q['query']}")
        print(f"  gold: {q['gold'][:130]}")
        print(f"  kỳ vọng: doc={q.get('expect_doc_id')}, section={q.get('expect_section')}")

        if q.get("requires_filter"):
            top_unfiltered = _run_search(store, q["query"])
            print("\n  --- A/B = False (không filter) ---")
            print(_render_top3(top_unfiltered))
            ctx_unfiltered = " ".join(r["content"] for r in top_unfiltered)
            has_unfiltered = any(m in ctx_unfiltered for m in q["answer_marks"])

            top_filtered = _run_search(
                store, q["query"], metadata_filter={q["filter_field"]: q["filter_value"]}
            )
            print(f"\n  --- A/B = True (filter {q['filter_field']} = {q['filter_value']}) ---")
            print(_render_top3(top_filtered))
            ctx_filtered = " ".join(r["content"] for r in top_filtered)
            has_filtered = any(m in ctx_filtered for m in q["answer_marks"])

            print(f"\n  Đáp án trong top-3?  không filter={has_unfiltered} | filter={has_filtered}")
        else:
            results = _run_search(store, q["query"])
            print("\n  --- top-3 ---")
            print(_render_top3(results))
            ctx = " ".join(r["content"] for r in results)
            has = any(m in ctx for m in q["answer_marks"])
            print(f"  Đáp án trong top-3? {has}")

        answer = agent.answer(q["query"], top_k=3)
        print(f"  AGENT: {answer[:200]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
