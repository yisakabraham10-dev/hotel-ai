# check_chromadb.py

import chromadb
from config.settings import CHROMA_DB_PATH

# Connect to your existing ChromaDB
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# List all collections
print("Available collections:")
for collection in client.list_collections():
    print(f"  - {collection.name}: {collection.count()} documents")

# Check the hotel_rag collection specifically
try:
    collection = client.get_collection("hotel_rag")
    print(f"\n'hotel_rag' collection has {collection.count()} documents")
    
    # Get a sample to see what's inside
    sample = collection.get(limit=2)
    if sample['documents']:
        print("\nSample document:")
        print(sample['documents'][0][:200] + "...")
except Exception as e:
    print(f"Error accessing hotel_rag collection: {e}")