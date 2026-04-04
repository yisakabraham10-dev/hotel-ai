import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from rag.pipeline import rag_pipeline
from tasks.task_extractor import classify_message
from unanswered_queries import save_unanswered_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service keywords mapped to departments
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

# Action words that indicate a service request (must be present to trigger task)
ACTION_WORDS = ["need", "want", "get", "send", "bring", "fix", "repair", "clean", "help", "please"]

def detect_task(message: str):
    lower = message.lower()
    # First, check if any action word is present
    has_action = any(aw in lower for aw in ACTION_WORDS)
    if not has_action:
        return None
    # Then, check for a service keyword
    for keyword, dept in SERVICE_KEYWORDS.items():
        if keyword in lower:
            return {
                "type": "task",
                "task": message,
                "department": dept,
                "priority": "medium"
            }
    return None

def main():
    print("Hotel AI Task Manager Running...")
    conversation_history = []

    while True:
        msg = input("\nEnter message (or 'exit' to quit): ").strip()
        if msg.lower() == "exit":
            break
        if not msg:
            continue

        conversation_history.append({"role": "user", "content": msg})

        # 1. Fast‑path keyword task detection (requires action word)
        task = detect_task(msg)
        if task:
            print("\n📝 Task added:")
            print(f"  Task: {task['task']}")
            print(f"  Department: {task['department']}")
            print(f"  Priority: {task['priority']}")
            confirm = f"Task created: {task['task']} (Department: {task['department']})"
            conversation_history.append({"role": "assistant", "content": confirm})
            continue

        # 2. RAG / FAQ (knowledge)
        answer = rag_pipeline(msg, history=conversation_history)
        if answer is not None:
            print("\n📚 RAG Answer:")
            print(answer)
            conversation_history.append({"role": "assistant", "content": answer})
            continue

        # 3. No knowledge answer – classify the message (feedback or question)
        classification = classify_message(msg)
        if classification["type"] == "task":
            print("\n📝 Task added (LLM):")
            print(f"  Task: {classification['task']}")
            print(f"  Department: {classification['department']}")
            print(f"  Priority: {classification['priority']}")
            confirm = f"Task created: {classification['task']} (Department: {classification['department']})"
            conversation_history.append({"role": "assistant", "content": confirm})
        elif classification["type"] == "feedback":
            sentiment = classification.get("sentiment", "neutral")
            category = classification.get("category", "general")
            print(f"\n💬 Feedback received: {sentiment} ({category})")
            print("Thank you for your feedback! We appreciate it.")
            confirm = "Thank you for your feedback! We'll use it to improve."
            conversation_history.append({"role": "assistant", "content": confirm})
        else:  # question
            save_unanswered_query(msg)
            escalation_msg = "I don't have an answer for that yet. A staff member will get back to you shortly."
            print(f"\n🤔 {escalation_msg}")
            conversation_history.append({"role": "assistant", "content": escalation_msg})

if __name__ == "__main__":
    main()
