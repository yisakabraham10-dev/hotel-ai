# faq.py
import json
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from rag.embeddings import get_embedding_model

logger = logging.getLogger(__name__)

class FAQMatcher:
    def __init__(self, json_path: str, threshold: float = 0.70):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.qa_list = json.load(f)

        self.questions = [item["question"] for item in self.qa_list]
        self.answers = [item["answer"] for item in self.qa_list]
        self.threshold = threshold

        logger.info(f"Loaded {len(self.questions)} FAQ questions")
        self.embedding_model = get_embedding_model()
        self.question_embeddings = self.embedding_model.embed_documents(self.questions)
        logger.info("Precomputed FAQ question embeddings")

    def get_answer(self, query: str) -> str | None:
        if not self.question_embeddings:
            return None

        query_emb = self.embedding_model.embed_query(query)
        sims = cosine_similarity([query_emb], self.question_embeddings)[0]
        best_idx = int(np.argmax(sims))
        best_sim = sims[best_idx]

        if best_sim >= self.threshold:
            logger.debug(f"FAQ match: '{query}' -> '{self.questions[best_idx]}' (sim={best_sim:.3f})")
            return self.answers[best_idx]
        else:
            logger.debug(f"No FAQ match for '{query}' (best sim={best_sim:.3f} < {self.threshold})")
            return None

# Singleton
_faq_matcher = None

def get_faq_matcher(json_path: str = "data/faq/curated_qa.json", threshold: float = 0.70):
    global _faq_matcher
    if _faq_matcher is None:
        _faq_matcher = FAQMatcher(json_path, threshold=threshold)
    return _faq_matcher