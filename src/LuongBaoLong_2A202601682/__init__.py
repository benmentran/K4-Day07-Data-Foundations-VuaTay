"""
LuongBaoLong_2A202601682 — RAG Solution Package
Lab 7: Data Foundations - Embedding & Vector Store

Exports all core components for the RAG system:
- Document data model
- Chunking strategies (FixedSize, Sentence, Recursive, Semantic)
- Embedding store with search and filtering
- Knowledge base agent
- Embedding providers
- Utility functions (compute_similarity)
"""

from .models import Document, SearchResult
from .chunking import (
    FixedSizeChunker,
    SentenceChunker,
    RecursiveChunker,
    SemanticChunker,
    ChunkingStrategyComparator,
    compute_similarity,
)
from .store import EmbeddingStore, _mock_embed
from .agent import KnowledgeBaseAgent
from .embeddings import (
    MockEmbedder,
    LocalEmbedder,
    OpenAIEmbedder,
    MistralEmbedder,
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    MISTRAL_EMBEDDING_MODEL,
)

__version__ = "1.0.0"
__author__ = "LuongBaoLong_2A202601682"

__all__ = [
    # Models
    "Document",
    "SearchResult",
    # Chunking
    "FixedSizeChunker",
    "SentenceChunker",
    "RecursiveChunker",
    "SemanticChunker",
    "ChunkingStrategyComparator",
    "compute_similarity",
    # Store
    "EmbeddingStore",
    "_mock_embed",
    # Agent
    "KnowledgeBaseAgent",
    # Embeddings
    "MockEmbedder",
    "LocalEmbedder",
    "OpenAIEmbedder",
    "MistralEmbedder",
    "EMBEDDING_PROVIDER_ENV",
    "LOCAL_EMBEDDING_MODEL",
    "OPENAI_EMBEDDING_MODEL",
    "MISTRAL_EMBEDDING_MODEL",
]
