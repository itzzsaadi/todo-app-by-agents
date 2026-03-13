# ============================================
# DEVELOPER AGENT — Reads plan, writes code
# ============================================

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import os

load_dotenv()

# ── SAME GROQ SETUP ──────────────────────────
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

# ── READ THE APPROVED PLAN ───────────────────
# Load the plan that was approved in previous step
with open("outputs/plan_output.txt", "r", encoding="utf-8") as f:
    approved_plan = f.read()

print("📄 Approved plan loaded successfully!")

# ── AGENT: DEVELOPER ─────────────────────────
developer = Agent(
    role="Senior Python Developer",
    goal="Write complete, working Python code based on the approved project plan",
    backstory="""You are a senior Python developer with 10 years experience.
    You write clean, well-commented, production-ready code.
    You always write COMPLETE code — never use placeholders like 'add code here'.
    You write every single line needed for the app to work.""",
    verbose=True,
    allow_delegation=False
)

# ── AGENT: TESTER ────────────────────────────
tester = Agent(
    role="QA Engineer",
    goal="Write complete pytest test cases for the developer's code",
    backstory="""You are a QA engineer who specializes in Python testing.
    You write thorough pytest tests covering happy paths, edge cases, and errors.
    You always write complete, runnable test code.""",
    verbose=True,
    allow_delegation=False
)

# ── TASK 1: WRITE THE CODE ───────────────────
dev_task = Task(
    description="""Based on this approved project plan:

{approved_plan}

Write the COMPLETE Python code for this todo app.

You must write ALL of these files completely:

FILE 1 — todo_app/src/data.py:
- load_tasks() function: loads tasks from tasks.json, returns empty list if file doesn't exist
- save_tasks() function: saves tasks list to tasks.json

FILE 2 — todo_app/src/task_manager.py:
- add_task(title) function: adds a new task with id, title, completed=False
- delete_task(task_id) function: removes task by id
- complete_task(task_id) function: marks task as completed=True
- list_tasks() function: returns all tasks

FILE 3 — todo_app/src/main.py:
- Command line interface with a menu
- Options: 1=Add task, 2=List tasks, 3=Complete task, 4=Delete task, 5=Exit
- Keep looping until user picks 5

Write the FULL code for each file. No placeholders.""",
    expected_output="Complete Python code for all 3 files clearly labeled",
    agent=developer
)

# ── TASK 2: WRITE THE TESTS ──────────────────
test_task = Task(
    description="""Write pytest tests for the todo app code that was just written.

Write a complete test file: todo_app/tests/test_task_manager.py

Include tests for:
1. test_add_task — adds a task and checks it exists
2. test_delete_task — adds then deletes a task
3. test_complete_task — adds a task then marks it complete
4. test_list_tasks — checks list returns all tasks
5. test_add_multiple_tasks — adds 3 tasks, checks count

Make tests independent (use a fresh task list each time).
Write complete, runnable pytest code.""",
    expected_output="Complete pytest test file with all 5 tests",
    agent=tester,
    context=[dev_task]  # Tester reads the developer's code
)

# ── THE CREW ─────────────────────────────────
crew = Crew(
    agents=[developer, tester],
    tasks=[dev_task, test_task],
    process=Process.sequential,
    verbose=True
)

# ── RUN IT ───────────────────────────────────
print("\n" + "="*50)
print("💻 DEVELOPER + TESTER AGENTS STARTING...")
print("="*50 + "\n")

result = crew.kickoff(inputs={
    "approved_plan": approved_plan
})

# ── SAVE THE OUTPUT ──────────────────────────
with open("outputs/dev_output.txt", "w", encoding="utf-8") as f:
    f.write(str(result))

print("\n" + "="*50)
print("✅ CODE WRITTEN! Saved to outputs/dev_output.txt")
print("="*50)