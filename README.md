Hotel AI Assistant – Service
A production‑ready AI assistant for hotels, providing natural language understanding, knowledge retrieval (RAG), task extraction, feedback handling, and conversational memory. Built with FastAPI, ChromaDB, and sentence‑transformers.

Features
Knowledge Base (RAG) – Answers questions using a vector database built from hotel manuals and curated FAQs.

Task Extraction – Identifies service requests and creates structured tasks with department and priority.

Feedback Handling – Detects sentiment and categories (positive/negative/neutral) from guest comments.

Conversation Memory – Maintains context across multiple exchanges to handle follow‑up questions.

Human Escalation – Saves unanswered queries for manual review.

All‑in‑One API – Exposes a single /chat endpoint that orchestrates all capabilities.

Architecture
FastAPI – High‑performance web framework.

ChromaDB – Vector database for document retrieval.

Sentence‑Transformers – Local embedding model (all-MiniLM-L6-v2).

OpenRouter – LLM provider (supports many models, free options available).

SQLite (optional) – Stores escalated queries and feedback (can be swapped for PostgreSQL).

Prerequisites
Python 3.11 or higher (3.13 is experimental; use 3.11 for full compatibility)

Git

An OpenRouter API key (get one at openrouter.ai)

Installation
Clone the repository:

bash
git clone https://github.com/your-username/hotel-ai.git
cd hotel-ai
Create and activate a virtual environment:

bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Configuration
Create a .env file in the project root with the following variables:

ini
# Required
OPENROUTER_API_KEY=your-key-here

# Optional (with defaults shown)
LLM_MODEL=openai/gpt-3.5-turbo          # Model used for chat completions
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_COLLECTION=c4_project_data        # Name of your ChromaDB collection
CHROMA_DB_PATH=./data/chroma_db          # Path to ChromaDB storage
Data Preparation
The service expects a ChromaDB collection with your hotel knowledge base. You can load it using the provided rag/load_data.py script (see comments inside for instructions). A curated FAQ file (data/faq/curated_qa.json) is also used for fast matching.

Running the Service
Start the FastAPI server:

bash
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
The API will be available at http://localhost:8000. Interactive documentation is at /docs.

API Endpoints
POST /chat
Process a user message and return an AI‑generated response with optional metadata.

Request body (JSON):

json
{
  "message": "Who founded C4?",
  "history": []
}
message (string) – The user's input.

history (list of objects, optional) – Previous messages in the conversation, each with role ("user"/"assistant") and content.

Response (JSON):

json
{
  "reply": "Adrian Chancellor",
  "meta": {
    "type": "answer"
  }
}
For tasks:

json
{
  "reply": "Task created: Provide towels (Department: housekeeping)",
  "meta": {
    "action": "CREATE_TASK",
    "payload": {
      "task": "Provide towels",
      "department": "housekeeping",
      "priority": "medium"
    }
  }
}
For feedback:

json
{
  "reply": "Thank you for your feedback! We'll use it to improve.",
  "meta": {
    "action": "SEND_FEEDBACK",
    "payload": {
      "sentiment": "positive",
      "category": "service"
    }
  }
}
For escalation:

json
{
  "reply": "I don't have an answer for that yet. A staff member will get back to you shortly.",
  "meta": {
    "type": "escalate"
  }
}
GET /health
Health check endpoint. Returns {"status": "ok"}.

Testing the Service
Use curl or tools like Postman to test:

bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who founded C4?"}'
Integration Notes
Task extraction: When a task is created, the meta.action is set to "CREATE_TASK". The calling system should handle this by storing the task in its own database.

Feedback handling: Similarly, "SEND_FEEDBACK" indicates the message is feedback; the caller can record it.

Escalation: Unanswered questions are saved to the local SQLite database (if configured). The backend team can expose an admin interface to review and answer them.

Conversation history: The history field is optional but highly recommended for follow‑up support. Include the last 5‑10 exchanges.

Deployment
Docker
Build the image:

bash
docker build -t hotel-ai .
Run the container:

bash
docker run -p 8000:8000 --env-file .env hotel-ai
Using a Production Server
For production, use gunicorn with uvicorn workers:

bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend:app
Environment Variables Reference
Variable	Description	Default
OPENROUTER_API_KEY	Your OpenRouter API key (required)	–
LLM_MODEL	Model identifier for completions	openai/gpt-3.5-turbo
EMBEDDING_MODEL	Sentence‑transformer model name	sentence-transformers/all-MiniLM-L6-v2
CHROMA_COLLECTION	Name of the ChromaDB collection	c4_project_data
CHROMA_DB_PATH	Path to ChromaDB storage	./data/chroma_db
FAQ_JSON_PATH	Path to curated FAQ JSON file	data/faq/curated_qa.json
Troubleshooting
ModuleNotFoundError – Ensure all dependencies are installed (pip install -r requirements.txt).

OpenRouter 404 errors – Check that LLM_MODEL is a valid model name (visit openrouter.ai/models).

ChromaDB issues – Verify that the CHROMA_DB_PATH is writable and that you have loaded data into the collection.

Large pushes to Git – Exclude data/chroma_db/, *.pdf, and venv/ via .gitignore.
