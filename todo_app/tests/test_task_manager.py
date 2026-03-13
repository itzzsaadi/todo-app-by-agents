import os
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
