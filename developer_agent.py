from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import os
import json

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

# ── LOAD APPROVED PLAN ───────────────────────
with open("outputs/plan_output.txt", "r", encoding="utf-8") as f:
    approved_plan = f.read()

# ── LOAD ROUTING PLAN ────────────────────────
with open("outputs/routing_plan.json", "r", encoding="utf-8") as f:
    routing = json.load(f)

print(f"Building: {routing['project_type']} — {routing['project_name']}")

# ── BUILD DYNAMIC INSTRUCTIONS ───────────────
files_list = "\n".join([
    f"- {f['path']}: {f['description']}" 
    for f in routing['files_to_create']
])

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
    description=f"""Based on this approved project plan:

{{approved_plan}}

{routing['dev_instructions']}

FILES YOU MUST CREATE:
{files_list}

IMPORTANT RULES:
- Write COMPLETE code for every file listed above
- No placeholders, no "add code here" comments
- Every file must be fully functional
- Label each file clearly before its code block
- Use proper code blocks with language tags

Project type: {routing['project_type']}
Primary language: {routing['primary_language']}
Entry point: {routing['entry_point']}""",
    expected_output=f"Complete working code for all files: {files_list}",
    agent=developer
)

# ── TASK 2: WRITE THE TESTS ──────────────────
test_task = Task(
    description=f"""Review the code written by the developer.

{routing['test_instructions']}

Project type: {routing['project_type']}
Entry point: {routing['entry_point']}

Write a PASS/FAIL checklist for each requirement.
End with either APPROVED or NEEDS_FIXES.""",
    expected_output="Checklist with APPROVED or NEEDS_FIXES verdict",
    agent=tester,
    context=[dev_task]
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