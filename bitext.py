# bitext.py

import logging
from datasets import load_dataset
from rag.vector_store import get_vector_store
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Load the free Bitext Hospitality dataset
    logger.info("Loading Bitext Hospitality dataset...")
    dataset = load_dataset("bitext/Bitext-hospitality-llm-chatbot-training-dataset")
    train_data = dataset["train"]

    # Prepare documents and metadata
    documents = []
    ids = []
    metadatas = []

    logger.info("Preparing documents...")
    for idx, item in enumerate(train_data):
        instruction = item["instruction"]
        response = item["response"]
        doc = f"Q: {instruction}\nA: {response}"
        documents.append(doc)
        ids.append(f"bitext_{idx}")
        metadatas.append({
            "intent": item["intent"],
            "category": item["category"],
            "variation_type": item.get("variation_type", ""),
            "source": "bitext"
        })

    logger.info(f"Loaded {len(documents)} examples from Bitext.")

    # Connect to ChromaDB
    vector_store = get_vector_store()
    logger.info("Adding documents to ChromaDB in batches...")

    # Batch size (max ChromaDB allows is 5461, we use 1000 for safety)
    batch_size = 1000
    total_batches = (len(documents) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(documents), batch_size), desc="Adding batches"):
        batch_docs = documents[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        vector_store.add_documents(batch_docs, ids=batch_ids, metadatas=batch_meta)

    logger.info("Done!")

    # Verify
    info = vector_store.get_collection_info()
    logger.info(f"Collection '{info['name']}' now has {info['count']} documents.")

if __name__ == "__main__":
    main()