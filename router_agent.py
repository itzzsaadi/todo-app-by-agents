# ============================================
# ROUTER AGENT
# Reads project idea and decides:
# - What type of project is this?
# - What files need to be created?
# - What tests make sense?
# - What should the extractor do?
# ============================================

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import os
import json

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

# ── READ PROJECT IDEA ────────────────────────
with open("outputs/project_idea.txt", "r", encoding="utf-8") as f:
    project_idea = f.read().strip()

# ── ROUTER AGENT ─────────────────────────────
router = Agent(
    role="Project Router",
    goal="Analyze a project idea and output a precise routing plan as JSON",
    backstory="""You are a senior software architect who specializes in 
    classifying and routing software projects. Given any project description,
    you immediately know what type it is, what files it needs, and how to
    build and test it. You always respond with valid JSON only.""",
    verbose=True,
    allow_delegation=False
)

# ── ROUTING TASK ─────────────────────────────
route_task = Task(
    description=f"""Analyze this project idea and create a routing plan:

PROJECT IDEA: {project_idea}

Respond with ONLY a valid JSON object in exactly this format (no other text):

{{
  "project_type": "one of: web_landing_page | python_cli_app | python_web_app | react_app | api_backend | data_science | javascript_app | other",
  "project_name": "short folder-safe name like todo_app or landing_page",
  "primary_language": "one of: html_css_js | python | javascript | react",
  "output_folder": "folder name to save files in",
  "files_to_create": [
    {{"path": "relative/path/file.ext", "description": "what this file contains"}}
  ],
  "entry_point": "the main file to run or open",
  "dev_instructions": "specific instructions for the developer agent about what to build and how",
  "test_instructions": "specific instructions for the tester agent about what to check",
  "extract_method": "one of: extract_html | extract_python | extract_react | extract_js | extract_multiple",
  "run_command": "command to run the project e.g. python -m app.main or open index.html",
  "test_command": "command to test e.g. pytest tests/ -v or open in browser"
}}

Be very specific in dev_instructions and test_instructions.
Include every file the developer needs to create.""",
    expected_output="Valid JSON routing plan only, no extra text",
    agent=router
)

# ── RUN ──────────────────────────────────────
crew = Crew(
    agents=[router],
    tasks=[route_task],
    process=Process.sequential,
    verbose=True
)

print("\n" + "="*50)
print("ROUTER AGENT ANALYZING PROJECT...")
print("="*50)

result = crew.kickoff()
raw = str(result).strip()

# ── PARSE AND SAVE ROUTING PLAN ──────────────
import re

# Extract JSON from response
json_match = re.search(r'\{.*\}', raw, re.DOTALL)
if json_match:
    json_str = json_match.group(0)
    try:
        routing_plan = json.loads(json_str)
        with open("outputs/routing_plan.json", "w", encoding="utf-8") as f:
            json.dump(routing_plan, f, indent=2)
        print("\n" + "="*50)
        print(f"PROJECT TYPE   : {routing_plan['project_type']}")
        print(f"PROJECT NAME   : {routing_plan['project_name']}")
        print(f"LANGUAGE       : {routing_plan['primary_language']}")
        print(f"OUTPUT FOLDER  : {routing_plan['output_folder']}")
        print(f"ENTRY POINT    : {routing_plan['entry_point']}")
        print(f"RUN COMMAND    : {routing_plan['run_command']}")
        print("FILES TO CREATE:")
        for f in routing_plan['files_to_create']:
            print(f"  - {f['path']}")
        print("="*50)
        print("Routing plan saved to outputs/routing_plan.json")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print("Raw output saved for debugging")
        with open("outputs/routing_plan_raw.txt", "w", encoding="utf-8") as f:
            f.write(raw)
else:
    print("Could not extract JSON from router response")
    with open("outputs/routing_plan_raw.txt", "w", encoding="utf-8") as f:
        f.write(raw)