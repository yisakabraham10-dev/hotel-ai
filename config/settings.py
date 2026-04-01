# config/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set in environment")

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "c4_project_data")   # <-- important