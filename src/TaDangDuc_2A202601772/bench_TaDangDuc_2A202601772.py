"""
bench_TaDangDuc_2A202601772.py — Bài tập 3.1/3.4 (Giai đoạn 2, cá nhân)

Chiến lược thử nghiệm: FixedSizeChunker(chunk_size=400, overlap=50)
Corpus: data/k4_ecommerce (5 tài liệu, chung với cả nhóm)
5 câu hỏi đánh giá: lấy nguyên văn từ report/REPORT_NHOM.md — Mục 3.

Chạy: EMBEDDING_PROVIDER=local python bench_TaDangDuc_2A202601772.py
(mặc định .env đã đặt EMBEDDING_PROVIDER=local nên chỉ cần: python bench_TaDangDuc_2A202601772.py)
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src import FixedSizeChunker, KnowledgeBaseAgent, LocalEmbedder, _mock_embed

DATA_DIR = "data/k4_ecommerce"

QUERIES = [
    {
        "id": 1,
        "label": "Số liệu",
        "question": "Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng?",
        "metadata_filter": None,
    },
    {
        "id": 2,
        "label": "Điều kiện",
        "question": "Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm?",
        "metadata_filter": None,
    },
    {
        "id": 3,
        "label": "Quy trình",
        "question": "Quy trình trả hàng COM (Change of Mind) trên Shopee được áp dụng cho đối tượng nào?",
        "metadata_filter": None,
    },
    {
        "id": 4,
        "label": "Liệt kê",
        "question": "Những loại sản phẩm nào bị cấm đăng bán trên Shopee theo danh sách cấm/hạn chế?",
        "metadata_filter": None,
    },
    {
        "id": 5,
        "label": "Ngoại lệ (cần filter)",
        "question": "Thời gian đổi trả sản phẩm là bao lâu?",
        "metadata_filter": {"source_url": "https://help.shopee.vn/portal/4/article/77251"},
    },
]


def select_embedder():
    """Chọn embedder theo EMBEDDING_PROVIDER trong .env (fallback về mock nếu thiếu backend)."""
    load_dotenv(override=False)
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder()
        except Exception as exc:  # pragma: no cover - phụ thuộc môi trường
            print(f"Local embedder không sẵn sàng ({exc}); dùng mock.")
            return _mock_embed
    return _mock_embed


def demo_llm(prompt: str) -> str:
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] {preview}..."


def main() -> int:
    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    chunker = FixedSizeChunker(chunk_size=400, overlap=50)
    print(f"=== Strategy: FixedSizeChunker(chunk_size=400, overlap=50) | embedder={backend} ===\n")

    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
    print(f"Đã nạp {store.get_collection_size()} chunk từ '{DATA_DIR}'\n")

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    for q in QUERIES:
        print(f"--- Query #{q['id']} [{q['label']}]: {q['question']} ---")
        if q["metadata_filter"]:
            print(f"(metadata_filter={q['metadata_filter']})")
            results = store.search_with_filter(q["question"], top_k=3, metadata_filter=q["metadata_filter"])
        else:
            results = store.search(q["question"], top_k=3)

        for rank, r in enumerate(results, start=1):
            doc_id = r["metadata"].get("doc_id")
            preview = r["content"][:150].replace("\n", " ").strip()
            print(f"  {rank}. score={r['score']:.4f} doc_id={doc_id}")
            print(f"     {preview}...")

        if q["metadata_filter"]:
            # KnowledgeBaseAgent.answer() gọi store.search() KHÔNG lọc metadata,
            # nên với câu hỏi cần filter phải tự build prompt từ kết quả đã lọc ở trên.
            context = "\n\n".join(r["content"] for r in results)
            prompt = (
                "Answer the question using only the context below. "
                "If the context does not contain the answer, say you don't know.\n\n"
                f"Context:\n{context}\n\nQuestion: {q['question']}\nAnswer:"
            )
            answer = demo_llm(prompt)
            unfiltered_answer = agent.answer(q["question"], top_k=3)
            print(f"  Agent (CÓ filter, đúng cách): {answer[:220]}...")
            print(f"  Agent (KHÔNG filter, agent.answer() mặc định — minh họa lỗi): {unfiltered_answer[:220]}...\n")
        else:
            answer = agent.answer(q["question"], top_k=3)
            print(f"  Agent: {answer[:220]}...\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
