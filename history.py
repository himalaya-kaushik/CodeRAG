# history.py

import os
import json
import hashlib
from datetime import datetime
from subprocess import check_output

def get_project_id() -> str:
    """Get a unique hash for the current project based on Git root or cwd."""
    try:
        repo_root = check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
    except Exception:
        repo_root = os.getcwd()
    return hashlib.md5(repo_root.encode()).hexdigest()

def get_history_path(project_id: str) -> str:
    """Return path to the history file for a given project."""
    history_dir = os.path.join(os.getcwd(), ".codebuddy_history")
    os.makedirs(history_dir, exist_ok=True)
    return os.path.join(history_dir, f"chat_{project_id}.json")

def load_chat_history(history_path: str) -> list:
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat_history(history_path: str, history: list):
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def append_message(history: list, user_msg: str, assistant_msg: str) -> list:
    history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_msg,
        "assistant": assistant_msg
    })
    return history

def delete_chat_history(history_path: str) -> bool:
    """Delete the chat history file from disk if it exists."""
    try:
        if os.path.exists(history_path):
            os.remove(history_path)
            return True
        return False
    except Exception as e:
        print(f"⚠️ Failed to delete history: {e}")
        return False

