# backend.py
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any

# Import your AI modules
from rag.pipeline import rag_pipeline
from tasks.task_extractor import classify_message
from unanswered_queries import save_unanswered_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Keyword task detection (fast path) ----------
SERVICE_KEYWORDS = {
    "towels": "housekeeping",
    "pillow": "housekeeping",
    "blanket": "housekeeping",
    "water": "housekeeping",
    "coffee": "housekeeping",
    "tea": "housekeeping",
    "ice": "housekeeping",
    "clean": "housekeeping",
    "maintenance": "maintenance",
    "fix": "maintenance",
    "repair": "maintenance",
    "light": "maintenance",
    "toilet": "maintenance",
    "check-in": "front desk",
    "check-out": "front desk",
    "late checkout": "front desk",
    "room": "front desk",
    "spa": "spa",
    "restaurant": "restaurant"
}

ACTION_WORDS = ["need", "want", "get", "send", "bring", "fix", "repair", "clean", "help", "please"]

def detect_task(message: str):
    lower = message.lower()
    if not any(aw in lower for aw in ACTION_WORDS):
        return None
    for keyword, dept in SERVICE_KEYWORDS.items():
        if keyword in lower:
            return {
                "type": "task",
                "task": message,
                "department": dept,
                "priority": "medium"
            }
    return None

# ---------- Pydantic models (matching frontend) ----------
class Message(BaseModel):
    id: str
    text: str
    sender: str
    createdAt: Optional[int] = None
    status: Optional[str] = None
    meta: Optional[Any] = None

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    reply: str
    meta: Optional[dict] = None

# ---------- FastAPI app ----------
app = FastAPI(title="Hotel AI Backend")

# CORS – allow frontend origin (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # for development; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_history(history: List[Message]) -> List[dict]:
    """Convert frontend Message list to a list of {role, content} for the AI."""
    formatted = []
    for msg in history:
        role = "user" if msg.sender == "user" else "assistant"
        formatted.append({"role": role, "content": msg.text})
    return formatted

def process_message(message: str, history: List[Message]) -> dict:
    # 0. Fast‑path keyword task detection
    task = detect_task(message)
    if task:
        return {
            "reply": f"Task created: {task['task']} (Department: {task['department']})",
            "meta": {
                "action": "CREATE_TASK",
                "payload": {
                    "task": task["task"],
                    "department": task["department"],
                    "priority": task["priority"]
                }
            }
        }

    # 1. Format history for RAG
    formatted_history = format_history(history)

    # 2. Try RAG/FAQ (knowledge)
    answer = rag_pipeline(message, history=formatted_history)
    if answer is not None:
        return {"reply": answer, "meta": {"type": "answer"}}

    # 3. No knowledge – classify
    classification = classify_message(message)

    if classification["type"] == "task":
        task = classification.get("task", message)
        dept = classification.get("department", "general")
        priority = classification.get("priority", "medium")
        return {
            "reply": f"Task created: {task} (Department: {dept})",
            "meta": {
                "action": "CREATE_TASK",
                "payload": {
                    "task": task,
                    "department": dept,
                    "priority": priority
                }
            }
        }

    if classification["type"] == "feedback":
        sentiment = classification.get("sentiment", "neutral")
        category = classification.get("category")
        return {
            "reply": "Thank you for your feedback! We appreciate it.",
            "meta": {
                "action": "SEND_FEEDBACK",
                "payload": {
                    "sentiment": sentiment,
                    "category": category
                }
            }
        }

    # 4. Default: question not answered → escalate
    save_unanswered_query(message)
    return {
        "reply": "I don't have an answer for that yet. A staff member will get back to you shortly.",
        "meta": {"type": "escalate"}
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = process_message(request.message, request.history)
        return result
    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}