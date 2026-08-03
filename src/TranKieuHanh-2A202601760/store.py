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
            import chromadb  # noqa: F401

            # TODO: initialize chromadb client + collection
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # Build a normalized stored record for one document
        metadata = dict(doc.metadata or {})
        # ensure a doc_id exists for delete/filter operations
        metadata.setdefault("doc_id", doc.id)

        embedding = self._embedding_fn(doc.content)

        record = {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": embedding,
            "index": self._next_index,
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not records:
            return []

        query_vec = self._embedding_fn(query)
        scores: list[tuple[float, dict[str, Any]]] = []
        for r in records:
            emb = r.get("embedding")
            if not emb:
                score = 0.0
            else:
                # dot product of normalized vectors approximates cosine similarity
                try:
                    score = float(_dot(query_vec, emb))
                except Exception:
                    score = 0.0
            scores.append((score, r))

        # sort by score desc
        scores.sort(key=lambda x: x[0], reverse=True)

        results: list[dict[str, Any]] = []
        for score, rec in scores[:top_k]:
            results.append({"id": rec.get("id"), "content": rec.get("content"), "metadata": rec.get("metadata"), "score": score})
        return results

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if docs is None:
            return

        if self._use_chroma and self._collection is not None:
            # Chroma integration not required for tests; fallback to in-memory
            pass

        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if not query:
            return []

        if self._use_chroma and self._collection is not None:
            # Chroma path omitted for lab; fallback to in-memory
            pass

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        candidates = self._store
        if metadata_filter:
            def matches(meta: dict) -> bool:
                for k, v in (metadata_filter or {}).items():
                    if meta.get(k) != v:
                        return False
                return True

            candidates = [r for r in self._store if matches(r.get("metadata", {}))]

        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        before = len(self._store)
        self._store = [r for r in self._store if (r.get("metadata", {}).get("doc_id") != doc_id)]
        after = len(self._store)
        return after < before
