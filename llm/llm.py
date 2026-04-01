# llm/llm.py

import logging
from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

# Global client instance
_openai_client = None

def get_openai_client():
    """Return a singleton OpenAI client configured for OpenRouter."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )
    return _openai_client

def ask_llm(prompt: str, system_prompt: str = "You are a precise hotel assistant.") -> str:
    """Send a prompt to the LLM and return the response."""
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        raise