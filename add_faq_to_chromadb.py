import json
from rag.vector_store import get_vector_store

# Load your JSON file (the 1000+ Q&A pairs)
with open("data/faq/curated_qa.json", "r", encoding="utf-8") as f:
    qa_list = json.load(f)   # expects a list of {"question": "...", "answer": "..."}

# Prepare documents and metadata
documents = []
ids = []
metadatas = []
for i, item in enumerate(qa_list):
    doc = f"Q: {item['question']}\nA: {item['answer']}"
    documents.append(doc)
    ids.append(f"faq_{i}")
    metadatas.append({
        "source": "curated_faq",
        "question": item['question']   # optional, for debugging
    })

# Add to existing collection
vector_store = get_vector_store()
vector_store.add_documents(documents, ids=ids, metadatas=metadatas)
print(f"Added {len(documents)} curated Q&A pairs to the collection.")