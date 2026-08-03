from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        # store references to the provided store and llm function
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Retrieve top-k relevant contexts from the store
        results = []
        try:
            results = self.store.search(question, top_k=top_k)
        except Exception:
            results = []

        # Build a simple prompt containing the retrieved contexts
        contexts = []
        for r in results:
            # r is expected to contain 'content' and optionally 'metadata'
            content = r.get('content') if isinstance(r, dict) else str(r)
            if content:
                contexts.append(content)

        context_block = "\n\n---\n\n".join(contexts) if contexts else ""

        prompt_parts = []
        if context_block:
            prompt_parts.append("Context:\n" + context_block)
        prompt_parts.append("Question:\n" + (question or ""))

        prompt = "\n\n".join(prompt_parts)

        # Call the LLM function with the constructed prompt
        return self.llm_fn(prompt)
