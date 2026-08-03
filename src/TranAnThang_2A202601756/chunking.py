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
        if not text or not text.strip():
            return []
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])(?:\s+|$)", text) if sentence.strip()]
        limit = self.max_sentences_per_chunk
        return [" ".join(sentences[index : index + limit]) for index in range(0, len(sentences), limit)]


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
        if not text:
            return []

        chunks = self._split(text, self.separators)

        return [
            chunk.strip()
            for chunk in chunks
            if chunk.strip()
        ]


    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base case 1: Text đủ ngắn
        if not current_text or len(current_text) <= self.chunk_size:
            return [current_text]

        # Base case 2: không còn separator nào
        # Base case 2: không còn separator
        if not remaining_separators:
            return [
                current_text[index:index + self.chunk_size]
                for index in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Separator rỗng nghĩa là cắt cố định theo số ký tự
        if separator == "":
            return [
                current_text[index:index + self.chunk_size]
                for index in range(0, len(current_text), self.chunk_size)
            ]

        # Separator hiện tại không tồn tại: thử separator tiếp theo
        if separator not in current_text:
            return self._split(current_text, next_separators)

        parts = current_text.split(separator)
        chunks: list[str] = []
        current_chunk = ""

        for part in parts:
            if not part:
                continue

            # Thêm lại separator đã bị split loại bỏ
            candidate = (
                part
                if not current_chunk
                else current_chunk + separator + part
            )

            # Vẫn nằm trong giới hạn thì tiếp tục gộp
            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
                continue

            # Đưa chunk hiện tại vào kết quả
            if current_chunk:
                chunks.extend(
                    self._split(current_chunk, next_separators)
                )

            # Part riêng lẻ vẫn quá dài thì split tiếp bằng separator thấp hơn
            if len(part) > self.chunk_size:
                chunks.extend(
                    self._split(part, next_separators)
                )
                current_chunk = ""
            else:
                current_chunk = part

        if current_chunk:
            chunks.extend(
                self._split(current_chunk, next_separators)
            )

        return chunks


class HeadingSectionChunker:
    """Split Markdown into heading-based sections and preserve heading context.

    A section is kept intact when it fits ``chunk_size``. Longer sections are
    split recursively, with the section heading prepended to every child chunk.
    """

    HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*$")

    def __init__(self, chunk_size: int = 700) -> None:
        self.chunk_size = max(1, chunk_size)
        self._recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        matches = list(self.HEADING_RE.finditer(text))
        if not matches:
            return self._recursive.chunk(text)

        sections: list[tuple[str, str]] = []
        if text[: matches[0].start()].strip():
            sections.append(("", text[: matches[0].start()].strip()))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            heading = match.group(0).strip()
            body = text[match.end():end].strip()
            sections.append((heading, body))

        chunks: list[str] = []
        for heading, body in sections:
            prefix = f"{heading}\n" if heading else ""
            if not body:
                if heading:
                    chunks.append(heading)
                continue
            whole = f"{prefix}{body}".strip()
            if len(whole) <= self.chunk_size:
                chunks.append(whole)
                continue
            child_size = max(1, self.chunk_size - len(prefix))
            for child in RecursiveChunker(chunk_size=child_size).chunk(body):
                chunks.append(f"{prefix}{child}".strip())
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)
    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }
        result = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            result[name] = {
                "count": len(chunks),
                "avg_length": sum(map(len, chunks)) / len(chunks) if chunks else 0.0,
                "chunks": chunks,
            }
        return result
