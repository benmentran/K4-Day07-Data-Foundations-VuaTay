from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        # Split into sentences using the requested boundaries. Keep punctuation
        # by splitting on whitespace that follows sentence-ending punctuation
        # or on a dot + newline.
        pieces = re.split(r"(?<=\.\n)|(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in pieces if s and s.strip()]

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk = " ".join(s for s in group).strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if text is None:
            return []
        text = text.strip()
        if not text:
            return []

        return [c for c in self._split(text, list(self.separators)) if c]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base cases
        if not current_text:
            return []

        if len(current_text) <= self.chunk_size:
            return [current_text.strip()]

        if not remaining_separators:
            # No separators left — fall back to fixed-size splitting
            chunks: list[str] = []
            for i in range(0, len(current_text), self.chunk_size):
                part = current_text[i : i + self.chunk_size].strip()
                if part:
                    chunks.append(part)
            return chunks

        sep = remaining_separators[0]
        rest_seps = remaining_separators[1:]

        if sep == "":
            # empty separator behaves like no separator
            return self._split(current_text, rest_seps)

        parts = current_text.split(sep)
        out: list[str] = []
        # Re-add separator between parts when meaningful to preserve boundaries
        for idx, part in enumerate(parts):
            if part == "":
                continue
            # If not last, append separator back so context is preserved
            if idx != len(parts) - 1:
                segment = part + sep
            else:
                segment = part

            segment = segment.strip()
            if not segment:
                continue

            if len(segment) <= self.chunk_size:
                out.append(segment)
            else:
                # Too large — recurse with next separators
                out.extend(self._split(segment, rest_seps))

        return out


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b:
        return 0.0

    # Ensure vectors are same length for dot product
    n = min(len(vec_a), len(vec_b))
    if n == 0:
        return 0.0

    dot = _dot(vec_a[:n], vec_b[:n])
    norm_a = math.sqrt(_dot(vec_a[:n], vec_a[:n]))
    norm_b = math.sqrt(_dot(vec_b[:n], vec_b[:n]))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        # Run fixed-size
        fixed_chunks = FixedSizeChunker(chunk_size=chunk_size, overlap=0).chunk(text)

        # Choose a reasonable sentence grouping based on chunk_size
        max_sent = max(1, chunk_size // 100)
        by_sent_chunks = SentenceChunker(max_sentences_per_chunk=max_sent).chunk(text)

        recursive_chunks = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def stats(chunks: list[str]) -> dict:
            count = len(chunks)
            avg_length = float(sum(len(c) for c in chunks) / count) if count else 0.0
            return {"count": count, "avg_length": avg_length, "chunks": chunks}

        return {
            "fixed_size": stats(fixed_chunks),
            "by_sentences": stats(by_sent_chunks),
            "recursive": stats(recursive_chunks),
        }
