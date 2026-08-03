"""
chunking.py — Chiến lược chia nhỏ văn bản (Text Chunking Strategies)
Cho Lab 7: Data Foundations - Embedding & Vector Store

Chiến lược được triển khai:
1. FixedSizeChunker     - Chia theo kích thước cố định (đã có sẵn)
2. SentenceChunker      - Chia theo ranh giới câu
3. RecursiveChunker     - Chia đệ quy theo separators
4. SemanticChunker      - Chia theo ngữ nghĩa (Lựa chọn của LuongBaoLong)
5. ChunkingStrategyComparator - So sánh các chiến lược
"""

from __future__ import annotations

import math
import re
from typing import Callable, Protocol


class BaseChunker(Protocol):
    """Protocol interface cho tất cả các chunker."""

    def chunk(self, text: str) -> list[str]:
        """Chia văn bản thành các chunks."""
        ...


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

    def _split_sentences(self, text: str) -> list[str]:
        """Tách văn bản thành các câu riêng biệt."""
        # Tách theo dấu câu: . ! ? theo sau bởi khoảng trắng hoặc xuống dòng
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-ZÀ-ỹ])|(?<=[.!?])$'
        sentences = re.split(sentence_pattern, text)

        # Làm sạch và lọc các câu rỗng
        cleaned = []
        for s in sentences:
            s = s.strip()
            if s and len(s) > 0:
                cleaned.append(s)

        return cleaned

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sentences = self._split_sentences(text)
        if not sentences:
            return [text] if text.strip() else []

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_sentence_count = 0

        for sentence in sentences:
            current_chunk.append(sentence)
            current_sentence_count += 1

            if current_sentence_count >= self.max_sentences_per_chunk:
                # Ghép các câu lại thành chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = []
                current_sentence_count = 0

        # Thêm chunk cuối cùng nếu còn câu
        if current_chunk:
            chunks.append(" ".join(current_chunk))

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
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        return self._split(text, self.separators.copy())

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        """Đệ quy chia văn bản theo separators."""
        # Base case: nếu không còn separator hoặc text đủ nhỏ
        if not remaining_separators:
            return [current_text] if current_text else []

        if len(current_text) <= self.chunk_size:
            return [current_text]

        separator = remaining_separators[0]
        remaining = remaining_separators[1:]

        # Tách theo separator hiện tại
        if separator == "":
            # Separator cuối cùng: chia đều theo chunk_size
            return self._split_by_size(current_text)
        elif separator in current_text:
            parts = current_text.split(separator)
            result: list[str] = []

            for part in parts:
                if not part.strip():
                    continue

                # Nếu phần nhỏ hơn chunk_size, thêm vào kết quả
                if len(part) <= self.chunk_size:
                    result.append(part)
                else:
                    # Đệ quy chia tiếp
                    result.extend(self._split(part, remaining.copy()))

            # Merge các chunk nhỏ liên tiếp nếu có thể
            return self._merge_small_chunks(result)

        # Không tìm thấy separator, thử separator tiếp theo
        return self._split(current_text, remaining)

    def _split_by_size(self, text: str) -> list[str]:
        """Chia text thành các phần bằng nhau theo chunk_size."""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i : i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks

    def _merge_small_chunks(self, chunks: list[str]) -> list[str]:
        """Merge các chunk nhỏ liên tiếp nếu kết hợp lại vẫn <= chunk_size."""
        if not chunks:
            return []

        merged: list[str] = []
        current = chunks[0]

        for i in range(1, len(chunks)):
            next_chunk = chunks[i]
            if len(current) + len(next_chunk) <= self.chunk_size:
                current = current + "\n" + next_chunk
            else:
                merged.append(current)
                current = next_chunk

        if current:
            merged.append(current)

        return merged


class SemanticChunker:
    """
    Chia văn bản theo ngữ nghĩa (Semantic Chunking).

    Chiến lược này sử dụng embeddings để nhóm các câu có ngữ cảnh 
    liên quan với nhau vào cùng một chunk, dựa trên độ tương tự cosine
    giữa các câu liền kề.

    Ưu điểm:
    - Giữ nguyên ngữ cảnh và luồng ý của văn bản
    - Tránh cắt ngang các ý liên quan
    - Phù hợp với tài liệu có cấu trúc ngữ nghĩa rõ ràng

    Tham số:
        embedding_fn: Hàm tạo embedding vector từ text
        threshold: Ngưỡng cosine similarity tối thiểu để nhóm câu (0.0 - 1.0)
        min_chunk_size: Số câu tối thiểu trong một chunk
        max_chunk_size: Số câu tối đa trong một chunk
        combine_sentences: Kết hợp các câu ngắn thành chunk hoàn chỉnh
    """

    def __init__(
        self,
        embedding_fn: Callable[[str], list[float]] | None = None,
        threshold: float = 0.3,
        min_chunk_size: int = 2,
        max_chunk_size: int = 8,
        combine_sentences: bool = True,
    ) -> None:
        self.embedding_fn = embedding_fn
        self.threshold = max(0.0, min(1.0, threshold))
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.combine_sentences = combine_sentences

    def _split_sentences(self, text: str) -> list[str]:
        """Tách văn bản thành các câu riêng biệt."""
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-ZÀ-ỹ])|(?<=[.!?])$'
        sentences = re.split(sentence_pattern, text)

        cleaned = []
        for s in sentences:
            s = s.strip()
            if s and len(s) > 0:
                cleaned.append(s)

        return cleaned

    def _compute_cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Tính cosine similarity giữa hai vector."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _get_embedding(self, text: str) -> list[float] | None:
        """Lấy embedding cho một đoạn text."""
        if self.embedding_fn is None:
            return None
        try:
            return self.embedding_fn(text)
        except Exception:
            return None

    def _semantic_boundary_score(self, sentence_a: str, sentence_b: str) -> float:
        """
        Tính điểm ranh giới ngữ nghĩa giữa 2 câu.
        Trả về giá trị 0.0-1.0:
        - 1.0: Hai câu rất khác nhau về ngữ nghĩa (ranh giới mạnh)
        - 0.0: Hai câu rất giống nhau (cùng ngữ cảnh)
        """
        if self.embedding_fn is None:
            # Fallback: dựa vào từ khóa chung
            words_a = set(sentence_a.lower().split())
            words_b = set(sentence_b.lower().split())

            if not words_a or not words_b:
                return 1.0

            common = words_a & words_b
            union = words_a | words_b
            jaccard = len(common) / len(union) if union else 0

            # Cosine similarity ~= Jaccard với binary vectors
            return 1.0 - jaccard

        embedding_a = self._get_embedding(sentence_a)
        embedding_b = self._get_embedding(sentence_b)

        if embedding_a is None or embedding_b is None:
            return 0.5  # Không chắc chắn

        similarity = self._compute_cosine_similarity(embedding_a, embedding_b)
        # Ranh giới mạnh = similarity thấp
        return 1.0 - max(0.0, similarity)

    def _find_optimal_boundaries(
        self, sentences: list[str], max_chars: int = 500
    ) -> list[int]:
        """
        Tìm các vị trí ranh giới tối ưu cho các chunk dựa trên:
        1. Điểm ngữ nghĩa (semantic boundary score)
        2. Kích thước chunk (max_chars)
        3. Số câu trong chunk (min/max)
        """
        if len(sentences) <= self.min_chunk_size:
            return [len(sentences)]

        boundaries: list[int] = [0]
        current_start = 0
        current_chars = 0
        current_sentences_count = 0

        for i in range(len(sentences) - 1):
            current_chars += len(sentences[i])
            current_sentences_count += 1

            # Tính điểm ranh giới ngữ nghĩa
            boundary_score = self._semantic_boundary_score(
                sentences[i], sentences[i + 1]
            )

            # Kiểm tra xem có nên cắt ở đây không
            should_split = False

            # Điều kiện 1: Quá nhiều ký tự
            if current_chars >= max_chars:
                should_split = True

            # Điều kiện 2: Đủ số câu tối thiểu + ranh giới ngữ nghĩa mạnh
            if (
                current_sentences_count >= self.min_chunk_size
                and boundary_score >= self.threshold
            ):
                should_split = True

            # Điều kiện 3: Đạt số câu tối đa
            if current_sentences_count >= self.max_chunk_size:
                should_split = True

            if should_split:
                boundaries.append(i + 1)
                current_start = i + 1
                current_chars = 0
                current_sentences_count = 0

        # Thêm vị trí cuối
        if boundaries[-1] < len(sentences):
            boundaries.append(len(sentences))

        return boundaries

    def chunk(self, text: str) -> list[str]:
        """
        Chia văn bản thành các chunk theo ngữ nghĩa.

        Quy trình:
        1. Tách văn bản thành các câu
        2. Tính điểm ranh giới ngữ nghĩa giữa các câu
        3. Nhóm câu vào chunks dựa trên:
           - Điểm ngữ nghĩa (threshold)
           - Kích thước tối thiểu/tối đa
           - Giới hạn ký tự
        """
        if not text:
            return []

        # Bước 1: Tách câu
        sentences = self._split_sentences(text)

        if not sentences:
            return [text] if text.strip() else []

        if len(sentences) <= self.min_chunk_size:
            return [text.strip()]

        # Bước 2: Tìm ranh giới tối ưu
        boundaries = self._find_optimal_boundaries(sentences)

        # Bước 3: Ghép thành chunks
        chunks: list[str] = []
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_text = " ".join(chunk_sentences)
            chunks.append(chunk_text)

        # Xử lý chunk cuối nếu chưa đủ nhỏ
        if len(chunks) == 1 and len(chunks[0]) > self.max_chunk_size * 150:
            # Nếu chunk duy nhất quá lớn, chia đều
            fallback_chunks = self._split_large_chunk(chunks[0])
            chunks = fallback_chunks

        return chunks

    def _split_large_chunk(self, chunk: str) -> list[str]:
        """Chia chunk lớn thành các phần nhỏ hơn (fallback)."""
        sentences = self._split_sentences(chunk)
        chunks = []
        current: list[str] = []
        current_count = 0

        for sentence in sentences:
            current.append(sentence)
            current_count += 1

            if current_count >= self.max_chunk_size:
                chunks.append(" ".join(current))
                current = []
                current_count = 0

        if current:
            chunks.append(" ".join(current))

        return chunks if chunks else [chunk]


def _dot(a: list[float], b: list[float]) -> float:
    """Tính dot product của hai vectors."""
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)

    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))

    # Bảo vệ chia cho 0
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        """
        So sánh tất cả các chiến lược chunking.

        Trả về dict với format:
        {
            'strategy_name': {
                'count': so_luong_chunks,
                'avg_length': do_dai_trung_binh,
                'min_length': do_dai_nho_nhat,
                'max_length': do_dai_lon_nhat,
                'chunks': [danh_sach_chunks]
            }
        }
        """
        results: dict = {}

        # 1. Fixed Size Chunking
        fixed_chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=0)
        fixed_chunks = fixed_chunker.chunk(text)
        results["fixed_size"] = self._compute_stats(fixed_chunks)

        # 2. Sentence-based Chunking
        # Ước lượng: trung bình 1 câu ~ 100 ký tự
        sentences_per_chunk = max(1, chunk_size // 100)
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=sentences_per_chunk)
        sentence_chunks = sentence_chunker.chunk(text)
        results["by_sentences"] = self._compute_stats(sentence_chunks)

        # 3. Recursive Chunking
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)
        recursive_chunks = recursive_chunker.chunk(text)
        results["recursive"] = self._compute_stats(recursive_chunks)

        # 4. Semantic Chunking (Lựa chọn của LuongBaoLong)
        # Sử dụng threshold mặc định 0.3 (ranh giới ngữ nghĩa vừa phải)
        semantic_chunker = SemanticChunker(
            threshold=0.3,
            min_chunk_size=2,
            max_chunk_size=6,
        )
        semantic_chunks = semantic_chunker.chunk(text)
        results["semantic"] = self._compute_stats(semantic_chunks)

        return results

    def _compute_stats(self, chunks: list[str]) -> dict:
        """Tính toán thống kê cho một danh sách chunks."""
        if not chunks:
            return {
                "count": 0,
                "avg_length": 0.0,
                "min_length": 0,
                "max_length": 0,
                "chunks": [],
            }

        lengths = [len(c) for c in chunks]

        return {
            "count": len(chunks),
            "avg_length": sum(lengths) / len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "chunks": chunks,
        }

    def print_comparison(self, text: str, chunk_size: int = 200) -> None:
        """In bảng so sánh các chiến lược."""
        results = self.compare(text, chunk_size)

        print(f"\n{'=' * 60}")
        print(f"So sanh Chien luoc Chunking (chunk_size={chunk_size})")
        print(f"{'=' * 60}")
        print(f"{'Chien luoc':<15} {'So chunk':<10} {'TB':<10} {'Min':<8} {'Max':<8}")
        print(f"{'-' * 60}")

        for name, stats in results.items():
            print(
                f"{name:<15} {stats['count']:<10} "
                f"{stats['avg_length']:<10.1f} {stats['min_length']:<8} {stats['max_length']:<8}"
            )

        print(f"{'=' * 60}\n")
