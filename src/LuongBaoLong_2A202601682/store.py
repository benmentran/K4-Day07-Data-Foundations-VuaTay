"""
store.py — Embedding Store implementation
Lab 7: Data Foundations - Embedding & Vector Store
Author: LuongBaoLong_2A202601682

Provides in-memory vector storage with metadata filtering support.
"""

from __future__ import annotations

import math
from typing import Callable

from .models import Document, SearchResult


class EmbeddingStore:
    """
    In-memory vector store for document embeddings.

    Features:
    - Add documents with automatic embedding
    - Search by semantic similarity
    - Metadata filtering
    - Document deletion by doc_id

    Usage:
        store = EmbeddingStore(collection_name="my_kb", embedding_fn=my_embed_fn)
        store.add_documents([doc1, doc2])
        results = store.search("query", top_k=5)
        results = store.search_with_filter("query", top_k=5, metadata_filter={"lang": "vi"})
    """

    def __init__(
        self,
        collection_name: str = "default",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        """
        Initialize the embedding store.

        Args:
            collection_name: Name identifier for this collection
            embedding_fn: Function to compute embeddings from text
        """
        self.collection_name = collection_name
        self.embedding_fn = embedding_fn or _mock_embed

        # In-memory storage
        self._documents: list[Document] = []
        self._embeddings: list[list[float]] = []
        self._doc_id_to_indices: dict[str, list[int]] = {}

    def get_collection_size(self) -> int:
        """Return the number of documents in the store."""
        return len(self._documents)

    def add_documents(self, documents: list[Document]) -> None:
        """
        Add documents to the store with embeddings.

        Args:
            documents: List of Document objects to add
        """
        for doc in documents:
            # Compute embedding for the document
            embedding = self.embedding_fn(doc.content)

            # Store document and embedding
            index = len(self._documents)
            self._documents.append(doc)
            self._embeddings.append(embedding)

            # Track indices by doc_id (handles multiple chunks per doc)
            doc_id = doc.id.split("::chunk_")[0]
            if doc_id not in self._doc_id_to_indices:
                self._doc_id_to_indices[doc_id] = []
            self._doc_id_to_indices[doc_id].append(index)

    def _compute_cosine_similarity(
        self, vec_a: list[float], vec_b: list[float]
    ) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search for relevant documents using semantic similarity.

        Args:
            query: The search query text
            top_k: Maximum number of results to return

        Returns:
            List of result dicts with 'content', 'score', and 'metadata' keys,
            sorted by relevance (highest score first)
        """
        if not self._documents:
            return []

        # Embed the query
        query_embedding = self.embedding_fn(query)

        # Compute similarities
        scores: list[tuple[int, float]] = []
        for i, doc_embedding in enumerate(self._embeddings):
            similarity = self._compute_cosine_similarity(query_embedding, doc_embedding)
            scores.append((i, similarity))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Take top_k
        results: list[dict] = []
        for idx, score in scores[:top_k]:
            doc = self._documents[idx]
            results.append({
                "content": doc.content,
                "score": score,
                "metadata": doc.metadata,
                "id": doc.id,
            })

        return results

    def search_with_filter(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: dict | None = None,
    ) -> list[dict]:
        """
        Search with metadata filtering.

        Args:
            query: The search query text
            top_k: Maximum number of results to return
            metadata_filter: Dict of key-value pairs to filter by
                            (AND logic - all conditions must match)

        Returns:
            List of result dicts sorted by relevance
        """
        if not self._documents:
            return []

        # If no filter, just do regular search
        if metadata_filter is None or not metadata_filter:
            return self.search(query, top_k)

        # Embed the query
        query_embedding = self.embedding_fn(query)

        # Compute similarities only for documents matching the filter
        scores: list[tuple[int, float]] = []
        for i, doc in enumerate(self._documents):
            # Check metadata filter
            matches = True
            for key, value in metadata_filter.items():
                if doc.metadata.get(key) != value:
                    matches = False
                    break

            if matches:
                similarity = self._compute_cosine_similarity(
                    query_embedding, self._embeddings[i]
                )
                scores.append((i, similarity))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Take top_k
        results: list[dict] = []
        for idx, score in scores[:top_k]:
            doc = self._documents[idx]
            results.append({
                "content": doc.content,
                "score": score,
                "metadata": doc.metadata,
                "id": doc.id,
            })

        return results

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and all its chunks by doc_id.

        Args:
            doc_id: The document ID to delete

        Returns:
            True if document was found and deleted, False otherwise
        """
        # Get all chunk indices for this doc_id
        indices = self._doc_id_to_indices.get(doc_id, [])

        if not indices:
            # Try without chunk suffix
            for idx, doc in enumerate(self._documents):
                if doc.id.split("::chunk_")[0] == doc_id:
                    indices.append(idx)

        if not indices:
            return False

        # Remove from storage (in reverse order to maintain indices)
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self._documents):
                self._documents.pop(idx)
                self._embeddings.pop(idx)

        # Update index tracking
        del self._doc_id_to_indices[doc_id]

        # Rebuild index (simplified approach)
        self._rebuild_index()

        return True

    def _rebuild_index(self) -> None:
        """Rebuild the doc_id to indices mapping after deletions."""
        self._doc_id_to_indices = {}
        for i, doc in enumerate(self._documents):
            base_id = doc.id.split("::chunk_")[0]
            if base_id not in self._doc_id_to_indices:
                self._doc_id_to_indices[base_id] = []
            self._doc_id_to_indices[base_id].append(i)

    def get_all_documents(self) -> list[Document]:
        """Return all documents in the store."""
        return self._documents.copy()

    def clear(self) -> None:
        """Clear all documents from the store."""
        self._documents.clear()
        self._embeddings.clear()
        self._doc_id_to_indices.clear()


def _mock_embed(text: str) -> list[float]:
    """
    Generate a mock embedding for testing.

    Returns a random vector of 64 dimensions.
    This is NOT suitable for production - only for unit tests.
    """
    import hashlib

    # Deterministic "random" based on text hash
    hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
    import random

    random.seed(hash_val % (2**32))
    return [random.uniform(-1, 1) for _ in range(64)]


# Export mock embed function for testing
_mock_embed = _mock_embed
