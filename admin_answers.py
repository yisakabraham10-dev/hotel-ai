# main.py
import logging
from rag.pipeline import rag_pipeline
from tasks.task_extractor import extract_task
from unanswered_queries import save_unanswered_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("Hotel AI Task Manager Running...")
    # ... (vector store init if needed) ...

    while True:
        msg = input("\nEnter message (or 'exit' to quit): ").strip()
        if msg.lower() == "exit":
            break
        if not msg:
            continue

        # 1. Try FAQ / RAG
        answer = rag_pipeline(msg)   # returns None if no answer
        if answer is not None:
            print("\n📚 RAG Answer:")
            print(answer)
            continue

        # 2. Try task extraction
        task_data = extract_task(msg)
        if task_data.get("is_task"):
            print("\n📝 Task added:")
            print(f"  Task: {task_data['task']}")
            print(f"  Department: {task_data['department']}")
            print(f"  Priority: {task_data['priority']}")
            # Here you would send the task to your backend or database
            continue

        # 3. No answer and not a task → escalate to human
        save_unanswered_query(msg)
        print("\n🤔 I don't have an answer for that yet. A staff member will get back to you shortly.")

if __name__ == "__main__":
    main()