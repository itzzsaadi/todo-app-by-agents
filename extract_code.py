# ============================================
# EXTRACT CODE — Creates actual .py files
# from the agent's output
# ============================================
import os

# ── CREATE FOLDER STRUCTURE ─────────────────
os.makedirs("todo_app/src", exist_ok=True)
os.makedirs("todo_app/data", exist_ok=True)
os.makedirs("todo_app/tests", exist_ok=True)

# ── CREATE __init__.py FILES ─────────────────
# These make Python treat folders as packages
open("todo_app/__init__.py", "w").close()
open("todo_app/src/__init__.py", "w").close()
open("todo_app/tests/__init__.py", "w").close()

# ── FILE 1: data.py ──────────────────────────
data_py = '''import json
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
'''

# ── FILE 2: task_manager.py ──────────────────
task_manager_py = '''import uuid
from .data import load_tasks, save_tasks

class TaskManager:
    def __init__(self):
        self.tasks = load_tasks()

    def add_task(self, title):
        """Adds a new task with id, title, completed=False"""
        new_task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "completed": False
        }
        self.tasks.append(new_task)
        save_tasks(self.tasks)
        return new_task

    def delete_task(self, task_id):
        """Removes task by id"""
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        save_tasks(self.tasks)

    def complete_task(self, task_id):
        """Marks task as completed=True"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
        save_tasks(self.tasks)

    def list_tasks(self):
        """Returns all tasks"""
        return self.tasks
'''

# ── FILE 3: main.py ──────────────────────────
main_py = '''from .task_manager import TaskManager

def main():
    task_manager = TaskManager()

    print("\\n Welcome to your AI-built Todo App!")
    print("Built by AI agents using CrewAI + Groq\\n")

    while True:
        print("\\n--- MENU ---")
        print("1. Add task")
        print("2. List tasks")
        print("3. Complete task")
        print("4. Delete task")
        print("5. Exit")

        choice = input("\\nChoose an option (1-5): ").strip()

        if choice == "1":
            title = input("Enter task title: ").strip()
            task = task_manager.add_task(title)
            print(f"Task added! ID: {task[\'id\'][:8]}...")

        elif choice == "2":
            tasks = task_manager.list_tasks()
            if tasks:
                print(f"\\n--- YOUR TASKS ({len(tasks)} total) ---")
                for task in tasks:
                    status = "[DONE]" if task["completed"] else "[ ]"
                    short_id = task["id"][:8]
                    print(f"{status} {short_id}... | {task[\'title\']}")
            else:
                print("No tasks yet! Add one first.")

        elif choice == "3":
            task_id = input("Enter task ID (first 8 chars): ").strip()
            tasks = task_manager.list_tasks()
            matches = [t for t in tasks if t["id"].startswith(task_id)]
            if matches:
                task_manager.complete_task(matches[0]["id"])
                print(f"Task marked complete!")
            else:
                print("Task not found!")

        elif choice == "4":
            task_id = input("Enter task ID (first 8 chars): ").strip()
            tasks = task_manager.list_tasks()
            matches = [t for t in tasks if t["id"].startswith(task_id)]
            if matches:
                task_manager.delete_task(matches[0]["id"])
                print("Task deleted!")
            else:
                print("Task not found!")

        elif choice == "5":
            print("Goodbye! App built by AI agents.")
            break

        else:
            print("Invalid option. Please choose 1-5.")

if __name__ == "__main__":
    main()
'''

# ── FILE 4: test file ────────────────────────
test_py = '''import os
import pytest
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from todo_app.src.task_manager import TaskManager
from todo_app.src.data import load_tasks

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/tasks.json")

@pytest.fixture(autouse=True)
def clean_tasks():
    """Fresh start before each test"""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    yield
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def test_add_task():
    tm = TaskManager()
    tm.add_task("Test Task")
    tasks = load_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task"
    assert tasks[0]["completed"] == False

def test_delete_task():
    tm = TaskManager()
    tm.add_task("Delete me")
    tasks = load_tasks()
    task_id = tasks[0]["id"]
    tm.delete_task(task_id)
    assert len(load_tasks()) == 0

def test_complete_task():
    tm = TaskManager()
    tm.add_task("Complete me")
    tasks = load_tasks()
    task_id = tasks[0]["id"]
    tm.complete_task(task_id)
    tasks = load_tasks()
    assert tasks[0]["completed"] == True

def test_list_tasks():
    tm = TaskManager()
    tm.add_task("Task 1")
    tm.add_task("Task 2")
    tm.add_task("Task 3")
    assert len(tm.list_tasks()) == 3

def test_add_multiple_tasks():
    tm = TaskManager()
    tm.add_task("Task 1")
    tm.add_task("Task 2")
    tm.add_task("Task 3")
    assert len(load_tasks()) == 3
'''

# ── WRITE ALL FILES ──────────────────────────
files = {
    "todo_app/src/data.py": data_py,
    "todo_app/src/task_manager.py": task_manager_py,
    "todo_app/src/main.py": main_py,
    "todo_app/tests/test_task_manager.py": test_py,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {path}")

print("\nAll files created successfully!")
print("\nYour project structure:")
print("todo_app/")
print("   src/")
print("      data.py         <- saves/loads tasks")
print("      task_manager.py <- manages tasks")
print("      main.py         <- the app itself")
print("   data/")
print("      tasks.json      <- your data")
print("   tests/")
print("      test_task_manager.py <- 5 tests")