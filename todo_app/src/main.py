from .task_manager import TaskManager

def main():
    task_manager = TaskManager()

    print("\n Welcome to your AI-built Todo App!")
    print("Built by AI agents using CrewAI + Groq\n")

    while True:
        print("\n--- MENU ---")
        print("1. Add task")
        print("2. List tasks")
        print("3. Complete task")
        print("4. Delete task")
        print("5. Exit")

        choice = input("\nChoose an option (1-5): ").strip()

        if choice == "1":
            title = input("Enter task title: ").strip()
            task = task_manager.add_task(title)
            print(f"Task added! ID: {task['id'][:8]}...")

        elif choice == "2":
            tasks = task_manager.list_tasks()
            if tasks:
                print(f"\n--- YOUR TASKS ({len(tasks)} total) ---")
                for task in tasks:
                    status = "[DONE]" if task["completed"] else "[ ]"
                    short_id = task["id"][:8]
                    print(f"{status} {short_id}... | {task['title']}")
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
