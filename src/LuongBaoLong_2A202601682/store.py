from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        return {
            "id": doc.id,
            "content": doc.content,
            "embedding": embedding,
            "metadata": doc.metadata,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_embedding = self._embedding_fn(query)
        scored: list[dict[str, Any]] = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored.append({**record, "score": score})
        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        if self._use_chroma and self._collection is not None:
            self._collection.add(
                ids=[doc.id for doc in docs],
                documents=[doc.content for doc in docs],
                embeddings=[self._embedding_fn(doc.content) for doc in docs],
                metadatas=[doc.metadata for doc in docs],
            )
        else:
            for doc in docs:
                self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self._use_chroma and self._collection is not None:
            results = self._collection.query(query_texts=[query], n_results=top_k)
            return [
                {"content": doc, "score": score, "metadata": meta}
                for doc, score, meta in zip(
                    results["documents"][0],
                    results["distances"][0],
                    results["metadatas"][0],
                )
            ]
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        if metadata_filter is None:
            return self.search(query, top_k)
        if self._use_chroma and self._collection is not None:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                where=metadata_filter,
            )
            return [
                {"content": doc, "score": score, "metadata": meta}
                for doc, score, meta in zip(
                    results["documents"][0],
                    results["distances"][0],
                    results["metadatas"][0],
                )
            ]
        filtered = [
            r for r in self._store
            if all(r["metadata"].get(k) == v for k, v in metadata_filter.items())
        ]
        return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        if self._use_chroma and self._collection is not None:
            self._collection.delete(ids=[doc_id])
            return True
        before = len(self._store)
        self._store = [r for r in self._store if r["id"] != doc_id]
        return len(self._store) < before
