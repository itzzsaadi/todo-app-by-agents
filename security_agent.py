# ============================================
# SECURITY AGENT
# Scans your code for vulnerabilities
# Uses Groq (free) for AI-powered analysis
# ============================================

from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

# ── READ ALL CODE FILES ──────────────────────
def read_code_files():
    """Reads all Python files from todo_app/"""
    code = ""
    for root, dirs, files in os.walk("todo_app"):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                code += f"\n\n{'='*40}\n"
                code += f"FILE: {filepath}\n"
                code += f"{'='*40}\n"
                code += content
    return code

code_to_scan = read_code_files()
print(f"Scanning {len(code_to_scan)} characters of code...")

# ── AGENT: SECURITY AUDITOR ──────────────────
security_auditor = Agent(
    role="Security Auditor",
    goal="Find ALL security vulnerabilities in Python code and report them clearly",
    backstory="""You are a senior cybersecurity expert specializing in Python.
    You scan code for OWASP Top 10 issues, common Python vulnerabilities,
    and bad security practices. You are thorough and precise.
    You rate each issue as CRITICAL, HIGH, MEDIUM, or LOW severity.""",
    verbose=True,
    allow_delegation=False
)

# ── AGENT: SECURITY REPORTER ─────────────────
reporter = Agent(
    role="Security Reporter",
    goal="Turn raw security findings into a clear, actionable report",
    backstory="""You are a technical writer who specializes in security reports.
    You take raw vulnerability findings and create clear reports with:
    - Executive summary
    - List of issues by severity
    - Specific fix for each issue
    - Overall security score out of 10""",
    verbose=True,
    allow_delegation=False
)

# ── TASK 1: SCAN THE CODE ────────────────────
scan_task = Task(
    description=f"""Scan this Python code for security vulnerabilities:

{code_to_scan}

Check for ALL of these:
1. Hardcoded secrets, passwords, or API keys
2. SQL injection vulnerabilities
3. Missing input validation
4. Unsafe file operations
5. Insecure data storage (storing passwords in plain text etc.)
6. Missing error handling that could expose sensitive info
7. Any use of dangerous functions (eval, exec, os.system etc.)
8. Path traversal vulnerabilities

For each issue found, state:
- SEVERITY: (CRITICAL/HIGH/MEDIUM/LOW)
- FILE: which file it's in
- LINE: approximate line number
- ISSUE: what the problem is
- WHY: why it's dangerous

If no issues found in a category, say "CLEAN" for that category.""",
    expected_output="Detailed list of all security findings organized by severity",
    agent=security_auditor
)

# ── TASK 2: WRITE THE REPORT ─────────────────
report_task = Task(
    description="""Take the security scan findings and write a professional report.

Structure it exactly like this:

SECURITY AUDIT REPORT
=====================
Project: Todo App
Date: today

EXECUTIVE SUMMARY
-----------------
(2-3 sentences summarizing overall security posture)

OVERALL SECURITY SCORE: X/10

FINDINGS BY SEVERITY
--------------------
CRITICAL ISSUES: (count)
HIGH ISSUES: (count)
MEDIUM ISSUES: (count)
LOW ISSUES: (count)

DETAILED FINDINGS
-----------------
(List each finding with severity, description, and exact fix)

RECOMMENDATIONS
---------------
(Top 3 most important things to fix first)

CONCLUSION
----------
(Is this code safe to deploy? Why/why not?)""",
    expected_output="A complete professional security audit report",
    agent=reporter,
    context=[scan_task]
)

# ── THE CREW ─────────────────────────────────
crew = Crew(
    agents=[security_auditor, reporter],
    tasks=[scan_task, report_task],
    process=Process.sequential,
    verbose=True
)

# ── RUN IT ───────────────────────────────────
print("\n" + "="*50)
print("SECURITY AGENTS SCANNING YOUR CODE...")
print("="*50 + "\n")

result = crew.kickoff()

# ── SAVE REPORT ──────────────────────────────
with open("outputs/security_report.txt", "w", encoding="utf-8") as f:
    f.write(str(result))

print("\n" + "="*50)
print("SECURITY SCAN COMPLETE!")
print("Report saved to outputs/security_report.txt")
print("="*50)
print(result)