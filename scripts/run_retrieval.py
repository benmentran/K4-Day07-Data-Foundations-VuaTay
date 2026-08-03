"""Run retrieval test on the 5 evaluation queries from the group report."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

import csv
from pathlib import Path

from src.LuongBaoLong_2A202601682 import (
    Document,
    EmbeddingStore,
    KnowledgeBaseAgent,
    SemanticChunker,
    LocalEmbedder,
)


def load_documents(corpus_dir: str) -> list[Document]:
    """Load all documents from the k4_ecommerce corpus."""
    docs = []
    corpus_path = Path(corpus_dir)
    sources_csv = corpus_path / "sources.csv"

    sources = {}
    if sources_csv.exists():
        with open(sources_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sources[row["doc_id"]] = row

    for md_file in sorted(corpus_path.glob("*.md")):
        doc_id = md_file.stem
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        meta = sources.get(doc_id, {})
        metadata = {
            "doc_id": doc_id,
            "source": meta.get("source_url", ""),
            "retrieved_at": meta.get("retrieved_at", "2026-08-03"),
            "customer_role": meta.get("customer_role", ""),
            "category": meta.get("category", ""),
            "language": "vi",
        }
        docs.append(Document(id=doc_id, content=content, metadata=metadata))
    return docs


def main():
    output_lines = []
    output_lines.append("=" * 70)
    output_lines.append("Phan 5 - Ket qua truy xuat (Competition Results)")
    output_lines.append("=" * 70)

    # Load embedder (LocalEmbedder from sentence-transformers)
    embedder = LocalEmbedder()
    output_lines.append(f"Embedder: {embedder.__class__.__name__}")
    output_lines.append("")

    # Load documents
    docs = load_documents("data/k4_ecommerce")
    output_lines.append(f"Loaded {len(docs)} documents")
    output_lines.append("")

    # Chunk documents using SemanticChunker
    chunker = SemanticChunker(
        embedding_fn=embedder,
        threshold=0.3,
        min_chunk_size=2,
        max_chunk_size=8,
    )

    chunked_docs = []
    for doc in docs:
        chunks = chunker.chunk(doc.content)
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{doc.id}::chunk_{i}"
            chunked_docs.append(Document(
                id=chunk_id,
                content=chunk_text,
                metadata=dict(doc.metadata, chunk_index=i),
            ))
    output_lines.append(f"Total chunks after semantic chunking: {len(chunked_docs)}")
    output_lines.append("")

    # Build store
    store = EmbeddingStore(collection_name="ecommerce_qa", embedding_fn=embedder)
    store.add_documents(chunked_docs)
    output_lines.append(f"Store size: {store.get_collection_size()}")
    output_lines.append("")

    # 5 evaluation queries
    queries = [
        {
            "id": 1,
            "query": "Quy dinh dang ban san pham tren Shopee liet ke bao nhieu danh muc nganh hang?",
            "expected_doc": "shopee-listing-policy",
            "gold": "Khoang 14 danh muc nganh hang (M. pham, TP chuc nang, Thoi trang, Thiet bi dien tu,...)",
        },
        {
            "id": 2,
            "query": "Nguoi ban Shopee can nhung giay to gi de dang ban san pham thuoc nganh hang my pham?",
            "expected_doc": "shopee-listing-policy",
            "gold": "Giay chung nhan cong bo, chung nhan dai ly, giay xac nhan quang cao",
        },
        {
            "id": 3,
            "query": "Quy trinh tra hang COM (Change of Mind) tren Shopee duoc ap dung cho doi tuong nao?",
            "expected_doc": "shopee-return-refund",
            "gold": "Thanh vien CT khach hang than thiet Shopee (Vang/VIP Kim Cuong) hoac nguoi dung Goo ShopeeVIP",
        },
        {
            "id": 4,
            "query": "Nhung loai san pham nao bi cam dang ban tren Shopee theo danh sach cam/han che?",
            "expected_doc": "shopee-prohibited-products",
            "gold": "Hang vi pham ban quyen, thiet bi quan su, tai lieu phan dong, dich vu bat hop phap, sung, ma tuy, thuoc la, san pham nguoi lon, thiet bi giam sat, hoa chat nguy hiem, bo phan co the nguoi, hang gia,...",
        },
        {
            "id": 5,
            "query": "Thoi gian doi tra san pham tren Shopee la bao lau?",
            "expected_doc": "shopee-return-refund",
            "gold": "Shopee: 15 ngay (don COD/chuyen khoan duoi 200tr) hoac 24h (thuc pham/tuoi song)",
            "metadata_filter": None,
        },
    ]

    output_lines.append("=" * 70)
    output_lines.append("RESULTS")
    output_lines.append("=" * 70)

    relevant_count = 0
    for q in queries:
        output_lines.append("")
        output_lines.append(f"--- Query {q['id']} ---")
        output_lines.append(f"Q: {q['query']}")
        output_lines.append(f"Expected doc: {q['expected_doc']}")
        output_lines.append(f"Gold: {q['gold']}")

        # Search with top-k=3
        results = store.search(q["query"], top_k=3)

        output_lines.append("Top-3 chunks:")
        top1_relevant = False
        for i, r in enumerate(results, 1):
            chunk_doc_id = r["id"].split("::chunk_")[0]
            is_relevant = chunk_doc_id == q["expected_doc"]
            if i == 1 and is_relevant:
                top1_relevant = True
            output_lines.append(
                f"  [{i}] score={r['score']:.4f} doc={chunk_doc_id} "
                f"relevant={'Y' if is_relevant else 'N'}"
            )
            output_lines.append(f"      preview: {r['content'][:100]}...")

        top3_relevant = any(
            r["id"].split("::chunk_")[0] == q["expected_doc"] for r in results
        )
        if top3_relevant:
            relevant_count += 1

        # Run agent
        agent = KnowledgeBaseAgent(store=store, llm_fn=lambda p: "[DEMO] " + p[:120])
        answer = agent.answer(q["query"], top_k=3)
        output_lines.append(f"Agent answer (preview): {answer[:300]}...")

        # For query 5 also test with filter
        if q["id"] == 5:
            filtered = store.search_with_filter(
                q["query"], top_k=3,
                metadata_filter={"doc_id": "shopee-return-refund"},
            )
            output_lines.append(f"Filtered search (doc_id=shopee-return-refund):")
            for i, r in enumerate(filtered, 1):
                chunk_doc_id = r["id"].split("::chunk_")[0]
                output_lines.append(
                    f"  [{i}] score={r['score']:.4f} doc={chunk_doc_id}"
                )

    output_lines.append("")
    output_lines.append("=" * 70)
    output_lines.append(f"Relevant in top-3: {relevant_count}/5")
    output_lines.append("=" * 70)

    # Write to file
    with open("scripts/retrieval_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"Done. Results written to scripts/retrieval_results.txt")
    print(f"Relevant in top-3: {relevant_count}/5")


if __name__ == "__main__":
    main()
