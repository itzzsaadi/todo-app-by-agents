import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/tasks.json")

def load_tasks():
    """Loads tasks from tasks.json, returns empty list if file doesnt exist."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_tasks(tasks):
    """Saves tasks list to tasks.json"""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)
