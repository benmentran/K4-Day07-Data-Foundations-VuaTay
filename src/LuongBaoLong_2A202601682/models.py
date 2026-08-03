"""
models.py — Data models for the RAG system
Lab 7: Data Foundations - Embedding & Vector Store
Author: LuongBaoLong_2A202601682
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """
    A text document with optional metadata.

    Fields:
        id:       Unique identifier string.
        content:  The raw text content.
        metadata: Arbitrary key-value metadata (e.g. source, date, author).
    """

    id: str
    content: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate document fields."""
        if not self.id:
            raise ValueError("Document id cannot be empty")
        if not isinstance(self.content, str):
            raise ValueError("Document content must be a string")
        if not isinstance(self.metadata, dict):
            raise ValueError("Document metadata must be a dictionary")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value with optional default."""
        return self.metadata.get(key, default)

    def has_metadata(self, key: str) -> bool:
        """Check if metadata key exists."""
        return key in self.metadata

    def to_dict(self) -> dict:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """Create document from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class SearchResult:
    """
    A search result with content, score, and metadata.

    Fields:
        content:  The text content of the retrieved chunk.
        score:    Similarity score (higher = more relevant).
        metadata: Metadata from the source document.
        id:       Document/chunk ID.
    """

    content: str
    score: float
    metadata: dict = field(default_factory=dict)
    id: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary format (compatible with EmbeddingStore.search)."""
        return {
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "id": self.id,
        }
