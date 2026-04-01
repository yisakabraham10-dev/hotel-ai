# rag/vector_store.py

import chromadb
import logging
from config.settings import CHROMA_DB_PATH, CHROMA_COLLECTION
from rag.embeddings import get_embedding_model

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str = None):
        if collection_name is None:
            collection_name = CHROMA_COLLECTION
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding_model = get_embedding_model()
        logger.info(f"Connected to collection '{collection_name}' with {self.collection.count()} documents")

    def add_documents(self, documents: list, ids: list = None, metadatas: list = None):
        """Add documents to the collection."""
        if not documents:
            return
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        embeddings = self.embedding_model.embed_documents(documents)

        add_params = {
            "documents": documents,
            "embeddings": embeddings,
            "ids": ids
        }
        if metadatas:
            add_params["metadatas"] = metadatas

        self.collection.add(**add_params)
        logger.info(f"Added {len(documents)} documents to collection")

    def query(self, query: str, n_results: int = 10):
        try:
            query_embedding = self.embedding_model.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            docs = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            return docs, metadatas, distances
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return [], [], []

    def get_collection_info(self):
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
            "path": CHROMA_DB_PATH
        }

# Singleton
_vector_store = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store