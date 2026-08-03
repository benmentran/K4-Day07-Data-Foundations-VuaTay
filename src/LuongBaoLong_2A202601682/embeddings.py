"""
embeddings.py — Embedding providers
Lab 7: Data Foundations - Embedding & Vector Store
Author: LuongBaoLong_2A202601682

Provides various embedding backends:
- Mock: Random vectors for testing
- Local: Sentence Transformers
- OpenAI: OpenAI Embeddings API
- Mistral: Mistral Embeddings API
"""

from __future__ import annotations

import hashlib
import os
import random
from typing import Optional

import numpy as np

# Environment variable names
EMBEDDING_PROVIDER_ENV = "EMBEDDING_PROVIDER"
LOCAL_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
MISTRAL_EMBEDDING_MODEL = "mistral-embed"


class BaseEmbedder:
    """Base class for all embedders."""

    _backend_name: str = "base"

    def __call__(self, text: str) -> list[float]:
        """Embed text into a vector."""
        raise NotImplementedError

    def get_dimension(self) -> int:
        """Return embedding dimension."""
        raise NotImplementedError


class MockEmbedder(BaseEmbedder):
    """
    Mock embedder that generates deterministic random vectors.

    Useful for testing without API calls.
    """

    _backend_name = "mock"
    DIMENSION = 64

    def __init__(self, dimension: int = 64) -> None:
        self.dimension = dimension

    def __call__(self, text: str) -> list[float]:
        """Generate a mock embedding based on text hash."""
        # Deterministic "random" based on text hash
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        random.seed(hash_val % (2**32))
        return [random.uniform(-1, 1) for _ in range(self.dimension)]

    def get_dimension(self) -> int:
        return self.dimension


class LocalEmbedder(BaseEmbedder):
    """
    Local embedder using Sentence Transformers.

    Supports multilingual models optimized for semantic similarity.
    Default: paraphrase-multilingual-MiniLM-L12-v2 (good for Vietnamese)
    """

    _backend_name = "local"

    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model '{model_name}': {e}")

    def __call__(self, text: str) -> list[float]:
        """Embed text using the local model."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def get_dimension(self) -> int:
        """Return model embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


class OpenAIEmbedder(BaseEmbedder):
    """
    OpenAI Embeddings API embedder.

    Requires OPENAI_API_KEY environment variable.
    """

    _backend_name = "openai"

    def __init__(
        self,
        model_name: str = OPENAI_EMBEDDING_MODEL,
        api_key: str | None = None,
        dimension: int = 1536,
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.dimension = dimension

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    def __call__(self, text: str) -> list[float]:
        """Embed text using OpenAI API."""
        import openai

        client = openai.OpenAI(api_key=self.api_key)
        response = client.embeddings.create(
            model=self.model_name,
            input=text,
        )
        return response.data[0].embedding

    def get_dimension(self) -> int:
        return self.dimension


class MistralEmbedder(BaseEmbedder):
    """
    Mistral Embeddings API embedder.

    Requires MISTRAL_API_KEY environment variable.
    """

    _backend_name = "mistral"

    def __init__(
        self,
        model_name: str = MISTRAL_EMBEDDING_MODEL,
        api_key: str | None = None,
        dimension: int = 1024,
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.dimension = dimension

        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")

    def __call__(self, text: str) -> list[float]:
        """Embed text using Mistral API."""
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "input": text,
        }

        response = httpx.post(
            "https://api.mistral.ai/v1/embeddings",
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]

    def get_dimension(self) -> int:
        return self.dimension


def _mock_embed(text: str) -> list[float]:
    """
    Fallback mock embed function.

    This is the default when no proper embedder is available.
    """
    return MockEmbedder()(text)


# Export commonly used items
__all__ = [
    "EMBEDDING_PROVIDER_ENV",
    "LOCAL_EMBEDDING_MODEL",
    "OPENAI_EMBEDDING_MODEL",
    "MISTRAL_EMBEDDING_MODEL",
    "BaseEmbedder",
    "MockEmbedder",
    "LocalEmbedder",
    "OpenAIEmbedder",
    "MistralEmbedder",
    "_mock_embed",
]
