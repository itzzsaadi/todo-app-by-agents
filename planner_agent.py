# ============================================
# YOUR FIRST AGENT — The Planner + Reviewer
# ============================================

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import os

# Load your API keys from .env file
load_dotenv()

# ── TELL CREWAI TO USE GROQ (FREE) ──────────
# CrewAI uses OpenAI by default, we override it
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

# ── AGENT 1: THE PLANNER ─────────────────────
planner = Agent(
    role="Project Planner",
    goal="Create a detailed, structured project plan based on user requirements",
    backstory="""You are a senior software architect with 15 years experience. 
    You break down any project into clear phases, tasks, and file structures.
    You always output plans in a clean structured format.""",
    verbose=True,        # Shows thinking process
    allow_delegation=False  # This agent works alone
)

# ── AGENT 2: THE REVIEWER ────────────────────
reviewer = Agent(
    role="Plan Reviewer",
    goal="Review project plans and either APPROVE or REJECT them with feedback",
    backstory="""You are a critical but fair technical lead. 
    You review plans for completeness and clarity.
    You respond with either APPROVED or REJECTED followed by specific reasons.""",
    verbose=True,
    allow_delegation=False
)

# ── TASK 1: PLANNING ─────────────────────────
# A Task = what the agent actually has to DO
plan_task = Task(
    description="""Create a complete project plan for the following project:
    
    PROJECT: {project_idea}
    
    Your plan must include:
    1. Project overview (2-3 sentences)
    2. Tech stack (what languages/tools to use and WHY)
    3. Project phases (at least 3 phases)
    4. File/folder structure
    5. Estimated time for each phase
    """,
    expected_output="A structured project plan with all 5 sections filled out",
    agent=planner  # Assign to planner agent
)

# ── TASK 2: REVIEWING ────────────────────────
review_task = Task(
    description="""Review the project plan created by the planner.
    
    Check for:
    - Is the tech stack appropriate?
    - Are the phases logical and complete?
    - Is the file structure sensible?
    - Is anything missing?
    
    End your response with either:
    VERDICT: APPROVED ✅
    or
    VERDICT: REJECTED ❌ (with specific fixes needed)
    """,
    expected_output="A review with a clear VERDICT at the end",
    agent=reviewer,
    context=[plan_task]  # Reviewer READS the plan task output
)

# ── THE CREW ─────────────────────────────────
# Crew = a team of agents working on tasks together
crew = Crew(
    agents=[planner, reviewer],
    tasks=[plan_task, review_task],
    process=Process.sequential,  # One after another (planner first, then reviewer)
    verbose=True
)

# ── RUN IT! ───────────────────────────────────
print("\n" + "="*50)
print("🤖 AGENT PIPELINE STARTING...")
print("="*50 + "\n")

# This is where YOU describe your project
result = crew.kickoff(inputs={
    "project_idea": "A simple todo app in Python with a command line interface. Users can add, delete, mark complete, and list tasks. Data should be saved to a file."
})

print("\n" + "="*50)
print("✅ PIPELINE COMPLETE! FINAL OUTPUT:")
print("="*50)
print(result)

# Save the output to a file
with open("outputs/plan_output.txt", "w", encoding="utf-8") as f:
    f.write(str(result))
    print("\n📄 Plan saved to outputs/plan_output.txt")