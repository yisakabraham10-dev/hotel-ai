# rag/embeddings.py

import logging
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def embed_query(self, text: str) -> list:
        return self.model.encode(text).tolist()

    def embed_documents(self, texts: list) -> list:
        return self.model.encode(texts).tolist()

# Singleton
_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model