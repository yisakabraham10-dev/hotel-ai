# tasks/task_extractor.py
import json
import logging
from llm.llm import ask_llm

logger = logging.getLogger(__name__)

def classify_message(message: str) -> dict:
    """
    Classify user message into task, feedback, or question.
    Returns a dictionary with appropriate fields.
    """
    prompt = f"""
You are a hotel assistant. Classify the user's message into one of three types:

- TASK: a service request that requires action by staff. Examples:
  "I need towels", "Fix the AC", "Send water", "Change room 202", "Please clean my room"

- FEEDBACK: a comment about the experience, including complaints or praise. Examples:
  "The food was bad", "Great service", "The room was too cold", "The staff was amazing", "Loved the pool"

- QUESTION: a request for information. Examples:
  "What time is breakfast?", "Do you have a pool?", "Who founded C4?"

If it is a TASK, output JSON with:
{{"type": "task", "task": "...", "department": "housekeeping/front desk/maintenance/spa/restaurant/general", "priority": "low/medium/high"}}

If it is FEEDBACK, output JSON with:
{{"type": "feedback", "sentiment": "positive/negative/neutral", "category": "optional (e.g., food, room, service, etc.)"}}

If it is a QUESTION, output JSON with:
{{"type": "question"}}

Output ONLY the JSON object, no extra text.

User message: "{message}"

JSON:
"""
    try:
        response = ask_llm(prompt, system_prompt="You are a precise hotel assistant. Respond only with valid JSON.")
        print(f"DEBUG: classify_message response = {response}")   # for debugging
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != -1:
            data = json.loads(response[start:end])
            msg_type = data.get("type")
            if msg_type == "task":
                return {
                    "type": "task",
                    "task": data.get("task", message),
                    "department": data.get("department", "general"),
                    "priority": data.get("priority", "medium")
                }
            elif msg_type == "feedback":
                return {
                    "type": "feedback",
                    "sentiment": data.get("sentiment", "neutral"),
                    "category": data.get("category")
                }
            else:
                return {"type": "question"}
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        logger.warning(f"Classification failed: {e}. Defaulting to question.")
        return {"type": "question"}

# For backward compatibility (if needed)
def extract_task(message: str) -> dict:
    result = classify_message(message)
    if result["type"] == "task":
        return {
            "task": result["task"],
            "department": result["department"],
            "priority": result["priority"],
            "is_task": True
        }
    else:
        return {
            "task": message,
            "department": "general",
            "priority": "medium",
            "is_task": False
        }