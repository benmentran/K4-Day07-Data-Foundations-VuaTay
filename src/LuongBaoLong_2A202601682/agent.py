"""
agent.py — Knowledge Base Agent
Lab 7: Data Foundations - Embedding & Vector Store
Author: LuongBaoLong_2A202601682

RAG Agent that retrieves relevant documents and generates answers.
"""

from __future__ import annotations

from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    RAG Agent that combines retrieval with LLM generation.

    Takes a query, retrieves relevant documents from the embedding store,
    and generates an answer using the provided LLM function.

    Usage:
        agent = KnowledgeBaseAgent(store=my_store, llm_fn=my_llm)
        answer = agent.answer("What is the return policy?", top_k=5)
    """

    def __init__(
        self,
        store: EmbeddingStore,
        llm_fn: Callable[[str], str] | None = None,
        system_prompt: str | None = None,
    ) -> None:
        """
        Initialize the knowledge base agent.

        Args:
            store: EmbeddingStore instance to query
            llm_fn: Function that takes a prompt and returns an LLM response
            system_prompt: Optional system prompt to guide the LLM
        """
        self.store = store
        self.llm_fn = llm_fn or self._default_llm
        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        """Default system prompt for the RAG agent."""
        return """Bạn là một trợ lý AI thông minh, được thiết kế để trả lời câu hỏi dựa trên ngữ cảnh (context) được cung cấp.

Quy tắc:
1. Chỉ trả lời dựa trên thông tin có trong ngữ cảnh được cung cấp
2. Nếu ngữ cảnh không chứa thông tin cần thiết, hãy nói rõ điều đó
3. Trả lời bằng tiếng Việt, rõ ràng và súc tích
4. Trích dẫn nguồn nếu có thể
5. Nếu câu hỏi không rõ ràng, hãy yêu cầu làm rõ"""

    def _default_llm(self, prompt: str) -> str:
        """Default LLM function for demo purposes."""
        return f"[DEMO LLM] Generated answer based on prompt:\n{prompt[:200]}..."

    def _build_prompt(self, query: str, contexts: list[dict]) -> str:
        """
        Build the prompt for the LLM with retrieved contexts.

        Args:
            query: The user's question
            contexts: List of retrieved document chunks with scores

        Returns:
            Formatted prompt string
        """
        # Format contexts
        context_texts = []
        for i, ctx in enumerate(contexts, 1):
            source = ctx.get("metadata", {}).get("source", "Unknown")
            content = ctx.get("content", "")
            score = ctx.get("score", 0.0)
            context_texts.append(f"[Nguồn {i}] (Độ tương tự: {score:.3f})\nNguồn: {source}\nNội dung: {content}")

        context_block = "\n\n".join(context_texts)

        prompt = f"""{self.system_prompt}

## Ngữ cảnh (Context)
{context_block}

## Câu hỏi của người dùng
{query}

## Hướng dẫn trả lời
Dựa trên ngữ cảnh trên, hãy trả lời câu hỏi một cách chính xác và đầy đủ. Nếu thông tin không đủ, hãy nói rõ."""

        return prompt

    def answer(
        self,
        query: str,
        top_k: int = 5,
        include_sources: bool = True,
    ) -> str:
        """
        Answer a question using retrieval-augmented generation.

        Args:
            query: The user's question
            top_k: Number of documents to retrieve
            include_sources: Whether to include source citations in the answer

        Returns:
            Generated answer string
        """
        # Retrieve relevant documents
        contexts = self.store.search(query, top_k=top_k)

        if not contexts:
            return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong cơ sở tri thức để trả lời câu hỏi này."

        # Build prompt
        prompt = self._build_prompt(query, contexts)

        # Generate answer
        answer = self.llm_fn(prompt)

        # Optionally include sources
        if include_sources:
            sources = self._format_sources(contexts)
            answer = f"{answer}\n\n---\n\nNguồn tham khảo:\n{sources}"

        return answer

    def _format_sources(self, contexts: list[dict]) -> str:
        """Format source citations from retrieved contexts."""
        if not contexts:
            return "Không có nguồn."

        source_lines = []
        for i, ctx in enumerate(contexts, 1):
            metadata = ctx.get("metadata", {})
            source = metadata.get("source", "N/A")
            doc_id = metadata.get("doc_id", "N/A")
            source_lines.append(f"{i}. {source} (doc_id: {doc_id})")

        return "\n".join(source_lines)

    def get_relevant_context(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Get relevant context without generating an answer.

        Useful for debugging or when you just need the retrieved chunks.

        Args:
            query: The search query
            top_k: Number of chunks to retrieve

        Returns:
            List of retrieved chunks with scores
        """
        return self.store.search(query, top_k=top_k)
