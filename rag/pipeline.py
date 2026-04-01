# rag/pipeline.py
import logging
from rag.vector_store import get_vector_store
from llm.llm import ask_llm
from faq import get_faq_matcher

logger = logging.getLogger(__name__)

def rag_pipeline(query: str, history: list = None) -> str | None:
    # First try FAQ (no history needed)
    matcher = get_faq_matcher()
    answer = matcher.get_answer(query)
    if answer is not None:
        return answer

    # Build conversation context if history exists
    conversation_context = ""
    if history:
        # Take last 5 turns to avoid token overflow
        recent = history[-5:]
        turns = []
        for turn in recent:
            if turn["role"] == "user":
                turns.append(f"User: {turn['content']}")
            else:
                turns.append(f"Assistant: {turn['content']}")
        conversation_context = "Previous conversation:\n" + "\n".join(turns) + "\n\n"

    # RAG
    try:
        vector_store = get_vector_store()
        docs, metadatas, distances = vector_store.query(query, n_results=10)

        if not docs:
            return None

        context_parts = []
        for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances)):
            source = meta.get("source", "unknown") if meta else "unknown"
            context_parts.append(f"[Source: {source}]\n{doc}")
        context = "\n\n".join(context_parts)

        prompt = f"""{conversation_context}Answer the question using ONLY the context provided below.
If the answer is not in the context, respond with exactly: "Not found."

Context:
{context}

Question: {query}
"""
        answer = ask_llm(prompt, system_prompt="You are a precise hotel assistant.")
        if answer == "Not found.":
            return None
        return answer

    except Exception as e:
        logger.error(f"RAG pipeline failed: {e}")
        return None