"""Run the fixed five-query benchmark for the personal heading strategy."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import agent as _agent_module
from . import chunking as _chunking_module
from . import embeddings as _embeddings_module
from . import models as _models_module
from . import store as _store_module

# ingest.py intentionally imports the conventional ``src.*`` module names.
# The personal package is selected by the repository root, so expose these
# aliases only for this benchmark process and leave ingest.py unchanged.
sys.modules["src.agent"] = _agent_module
sys.modules["src.chunking"] = _chunking_module
sys.modules["src.embeddings"] = _embeddings_module
sys.modules["src.models"] = _models_module
sys.modules["src.store"] = _store_module

import ingest as _ingest_module

# ``src`` may already expose another student's modules through its package
# initializer. Replace the globals captured by ingest.py as well as the
# import aliases above, so this benchmark is genuinely personal.
_ingest_module.EmbeddingStore = _store_module.EmbeddingStore
_ingest_module.Document = _models_module.Document
build_knowledge_base = _ingest_module.build_knowledge_base
from .chunking import HeadingSectionChunker
from .embeddings import GeminiEmbedder, _mock_embed


QUERIES = [
    ("Số liệu: Quy định đăng bán sản phẩm trên Shopee liệt kê bao nhiêu danh mục ngành hàng?", None),
    ("Điều kiện: Người bán Shopee cần những giấy tờ gì để đăng bán sản phẩm thuộc ngành hàng mỹ phẩm?", None),
    ("Quy trình: Quy trình trả hàng COM (Change of Mind) trên Shopee được áp dụng cho đối tượng nào?", None),
    ("Liệt kê: Những loại sản phẩm nào bị cấm đăng bán trên Shopee theo danh sách cấm/hạn chế?", None),
    (
        "Ngoại lệ: Thời gian đổi trả sản phẩm trên Shopee là bao lâu?",
        {"source_url": "https://help.shopee.vn/portal/4/article/77251"},
    ),
]


def _llm(prompt: str) -> str:
    if os.getenv("LLM_PROVIDER", "").lower() == "gemini":
        from google import genai
        response = genai.Client().models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt
        )
        return response.text or ""
    context = prompt.split("Context:\n", 1)[-1].split("\n\nQuestion:", 1)[0]
    return "[OFFLINE DEMO; dùng Gemini để sinh câu trả lời] " + context[:300].replace("\n", " ")


def _answer(question: str, results: list[dict]) -> str:
    context = "\n\n".join(f"[{i}] {r['content']}" for i, r in enumerate(results, 1))
    prompt = ("Answer only from the context. If the context is insufficient, say so.\n\n"
              f"Context:\n{context}\n\nQuestion: {question}\nAnswer:")
    return _llm(prompt)


def main() -> int:
    load_dotenv(override=False)
    data_dir = Path(os.getenv("LAB_DATA_DIR", "data/k4_ecommerce"))
    if os.getenv("EMBEDDING_PROVIDER", "").lower() == "gemini":
        embedding_fn = GeminiEmbedder()
    else:
        embedding_fn = _mock_embed
    chunker = HeadingSectionChunker(chunk_size=700)
    store = build_knowledge_base(data_dir, embedding_fn=embedding_fn, chunker=chunker,
                                 collection_name="tran_an_thang_heading_bench")
    print(f"strategy=heading_section chunk_size=700 corpus={data_dir} chunks={store.get_collection_size()}")
    for index, (question, metadata_filter) in enumerate(QUERIES, 1):
        results = (store.search_with_filter(question, top_k=3, metadata_filter=metadata_filter)
                   if metadata_filter else store.search(question, top_k=3))
        print(f"\nQ{index}: {question}")
        print(f"filter={metadata_filter or {}}")
        for rank, result in enumerate(results, 1):
            print(f"  top-{rank} score={result['score']:.4f} doc_id={result['metadata'].get('doc_id')} "
                  f"preview={result['content'][:180].replace(chr(10), ' ')}")
        print(f"answer={_answer(question, results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
