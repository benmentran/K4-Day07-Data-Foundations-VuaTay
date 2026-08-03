from __future__ import annotations

import uuid
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
            import chromadb  # noqa: F401

            import chromadb
            # Ephemeral storage keeps each store instance isolated while
            # retaining Chroma's vector-search behavior when installed.
            client_factory = getattr(chromadb, "EphemeralClient", chromadb.Client)
            self._client = client_factory()
            # Chroma's in-process clients may share collections by name;
            # isolate store instances so separate runs/tests cannot leak data.
            isolated_name = f"{collection_name}_{uuid.uuid4().hex}"
            self._collection = self._client.get_or_create_collection(name=isolated_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata or {})
        # ChromaDB rejects empty metadata objects; the document id is also a
        # useful stable default for filtering and deletion.
        metadata.setdefault("doc_id", doc.id)
        return {"id": doc.id, "content": doc.content, "metadata": metadata,
                "embedding": list(self._embedding_fn(doc.content))}

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0:
            return []
        query_embedding = self._embedding_fn(query)
        ranked = []
        for record in records:
            item = dict(record)
            item["score"] = 1 - sum((a - b) ** 2 for a, b in zip(query_embedding, record["embedding"])) / 2
            ranked.append(item)
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        records = [self._make_record(doc) for doc in docs]
        if not records:
            return
        if self._use_chroma:
            existing_ids = set(self._collection.get(include=[]).get("ids", []))
            used_ids = set(existing_ids)
            for record in records:
                original_id = record["id"]
                candidate = original_id
                suffix = 1
                while candidate in used_ids:
                    candidate = f"{original_id}::{suffix}"
                    suffix += 1
                record["id"] = candidate
                used_ids.add(candidate)
            self._collection.add(ids=[r["id"] for r in records], documents=[r["content"] for r in records],
                                 metadatas=[r["metadata"] for r in records], embeddings=[r["embedding"] for r in records])
        else:
            self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma:
            result = self._collection.query(query_embeddings=[self._embedding_fn(query)], n_results=max(0, top_k))
            return [{"id": i, "content": d, "metadata": (m or {}), "score": 1 - dist}
                    for i, d, m, dist in zip(result["ids"][0], result["documents"][0], result.get("metadatas", [[]])[0], result["distances"][0])]
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return self._collection.count() if self._use_chroma else len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k)
        if self._use_chroma:
            result = self._collection.query(query_embeddings=[self._embedding_fn(query)], n_results=max(0, top_k), where=metadata_filter)
            return [{"id": i, "content": d, "metadata": (m or {}), "score": 1 - dist}
                    for i, d, m, dist in zip(result["ids"][0], result["documents"][0], result.get("metadatas", [[]])[0], result["distances"][0])]
        records = [r for r in self._store if all(r["metadata"].get(k) == v for k, v in metadata_filter.items())]
        return self._search_records(query, records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma:
            result = self._collection.get(where={"doc_id": doc_id})
            ids = result.get("ids", [])
            if ids:
                self._collection.delete(ids=ids)
            return bool(ids)
        before = len(self._store)
        self._store = [r for r in self._store if r["metadata"].get("doc_id", r["id"]) != doc_id]
        return len(self._store) < before
