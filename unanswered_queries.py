# unanswered_queries.py
import json
import os
from datetime import datetime

QUERIES_FILE = "data/unanswered_queries.json"

def save_unanswered_query(question, user_id=None):
    """Save an unanswered question to the file."""
    queries = []
    if os.path.exists(QUERIES_FILE):
        with open(QUERIES_FILE, 'r') as f:
            queries = json.load(f)

    new_id = max([q.get("id", 0) for q in queries] + [0]) + 1
    new_entry = {
        "id": new_id,
        "question": question,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "answered": False,
        "answer": None
    }
    queries.append(new_entry)
    with open(QUERIES_FILE, 'w') as f:
        json.dump(queries, f, indent=2)
    return new_id

def get_unanswered_queries():
    """Return a list of unanswered queries."""
    if not os.path.exists(QUERIES_FILE):
        return []
    with open(QUERIES_FILE, 'r') as f:
        return [q for q in json.load(f) if not q.get("answered")]