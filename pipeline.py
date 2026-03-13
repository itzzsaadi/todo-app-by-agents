# ============================================
# MASTER PIPELINE — FULLY DYNAMIC
# One command to run ALL agents in sequence
# Works for ANY project type automatically
# ============================================

import subprocess
import sys
import os
import json
from dotenv import load_dotenv

load_dotenv()

def run_step(script, step_name, emoji):
    """Run one agent script and show output live"""
    print(f"\n{'='*55}")
    print(f"{emoji}  STEP: {step_name}")
    print(f"{'='*55}")

    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,
        text=True
    )

    if result.returncode == 0:
        print(f"\n  {step_name} COMPLETED SUCCESSFULLY")
        return True
    else:
        print(f"\n  {step_name} FAILED — stopping pipeline")
        return False

def run_dynamic_tests():
    """Run tests based on project type from routing plan"""
    print(f"\n{'='*55}")
    print(f"   STEP: Running Tests")
    print(f"{'='*55}")

    # Load routing plan to know what kind of tests to run
    try:
        with open("outputs/routing_plan.json", "r", encoding="utf-8") as f:
            plan = json.load(f)
        project_type = plan.get("project_type", "unknown")
        test_command  = plan.get("test_command", "")
        output_folder = plan.get("output_folder", "")
    except FileNotFoundError:
        print("No routing plan found — skipping tests")
        return True

    print(f"Project type : {project_type}")
    print(f"Test command : {test_command}")

    # Web / HTML projects — no pytest, just verify file exists
    if project_type in ["web_landing_page", "javascript_app"]:
        index_path = os.path.join(output_folder, "index.html")
        if os.path.exists(index_path):
            size = os.path.getsize(index_path)
            print(f"\n  index.html found ({size} bytes)")
            print("  Open in browser to preview")
            print("\n  ALL CHECKS PASSED")
            return True
        else:
            print(f"\n  index.html NOT found at {index_path}")
            return False

    # Python projects — run pytest
    elif project_type in ["python_cli_app", "python_web_app",
                           "api_backend", "data_science"]:
        tests_folder = os.path.join(output_folder, "tests")
        if os.path.exists(tests_folder):
            result = subprocess.run(
                [sys.executable, "-m", "pytest", tests_folder, "-v"],
                capture_output=False,
                text=True
            )
            if result.returncode == 0:
                print("\n  ALL TESTS PASSED")
                return True
            else:
                print("\n  SOME TESTS FAILED")
                return False
        else:
            print("  No tests folder found — skipping pytest")
            return True

    # React / JS — just check files exist
    elif project_type == "react_app":
        app_path = os.path.join(output_folder, "App.jsx")
        if os.path.exists(app_path):
            print("\n  App.jsx found — PASSED")
            return True
        else:
            print("\n  App.jsx NOT found")
            return False

    else:
        print("  Unknown project type — skipping tests")
        return True

def ask_to_push():
    """Ask user if they want to push to GitHub"""
    print(f"\n{'='*55}")
    print(f"   STEP: GitHub Push")
    print(f"{'='*55}")
    answer = input("\nPush to GitHub? (yes/no): ").strip().lower()
    if answer == "yes":
        result = subprocess.run(
            [sys.executable, "github_agent.py"],
            capture_output=False,
            text=True,
            input="push\n\n"
        )
        return result.returncode == 0
    else:
        print("Skipping GitHub push.")
        return True

def print_final_summary():
    """Print dynamic summary based on what was built"""
    try:
        with open("outputs/routing_plan.json", "r", encoding="utf-8") as f:
            plan = json.load(f)
        with open("outputs/extraction_summary.json", "r", encoding="utf-8") as f:
            summary = json.load(f)

        print("\n")
        print("*" * 55)
        print("   PIPELINE COMPLETE!")
        print("*" * 55)
        print(f"\n  Project type  : {plan['project_type']}")
        print(f"  Project name  : {plan['project_name']}")
        print(f"  Output folder : {plan['output_folder']}/")
        print(f"\n  Files created :")
        for f in summary.get("files_created", []):
            print(f"    {f}")
        print(f"\n  To run your project:")
        print(f"    {plan['run_command']}")
        print(f"\n  Reports saved:")
        print(f"    outputs/plan_output.txt      <- project plan")
        print(f"    outputs/routing_plan.json    <- routing decisions")
        print(f"    outputs/dev_output.txt       <- generated code")
        print(f"    outputs/security_report.txt  <- security audit")
        print("*" * 55)

    except FileNotFoundError:
        print("\n PIPELINE COMPLETE!")

# ── MAIN ─────────────────────────────────────
def main():
    print("\n")
    print("*" * 55)
    print("   AI AGENT PIPELINE")
    print("   Describe any project — agents handle the rest")
    print("*" * 55)

    # ── GET PROJECT IDEA ─────────────────────
    print("\nWhat do you want to build?")
    print("Examples:")
    print("  - A landing page for my business X")
    print("  - A Python CLI tool that does Y")
    print("  - A REST API for Z")
    print("  - A React dashboard for W\n")

    project_idea = input("Describe your project: ").strip()

    if not project_idea:
        project_idea = "A simple todo app in Python with CLI interface"

    # Save for all agents to read
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/project_idea.txt", "w", encoding="utf-8") as f:
        f.write(project_idea)

    print(f"\nBuilding: {project_idea[:80]}...")
    print("Starting agent pipeline...\n")

    # ── STEP 1: PLAN ─────────────────────────
    success = run_step("planner_agent.py", "Planning + Review", "📋")
    if not success:
        print("Pipeline stopped at Planning.")
        return

    # ── STEP 2: ROUTE ────────────────────────
    success = run_step("router_agent.py", "Routing — detecting project type", "🔀")
    if not success:
        print("Pipeline stopped at Routing.")
        return

    # ── STEP 3: DEVELOP ──────────────────────
    success = run_step("developer_agent.py", "Development + Testing", "💻")
    if not success:
        print("Pipeline stopped at Development.")
        return

    # ── STEP 4: SMART EXTRACT ────────────────
    success = run_step("smart_extract.py", "Extracting files dynamically", "📁")
    if not success:
        print("Pipeline stopped at Extraction.")
        return

    # ── STEP 5: TESTS ────────────────────────
    run_dynamic_tests()

    # ── STEP 6: SECURITY ─────────────────────
    run_step("security_agent.py", "Security Scan", "🔒")

    # ── STEP 7: GITHUB ───────────────────────
    ask_to_push()

    # ── DONE ─────────────────────────────────
    print_final_summary()

if __name__ == "__main__":
    main()