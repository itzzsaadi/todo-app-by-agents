import uuid
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
