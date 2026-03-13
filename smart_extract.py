# ============================================
# SMART EXTRACTOR
# Reads routing plan and extracts the right
# files dynamically — works for ANY project
# ============================================

import os
import re
import json

# ── LOAD ROUTING PLAN ────────────────────────
with open("outputs/routing_plan.json", "r", encoding="utf-8") as f:
    plan = json.load(f)

# ── LOAD DEV OUTPUT ──────────────────────────
with open("outputs/dev_output.txt", "r", encoding="utf-8") as f:
    dev_output = f.read()

print("\n" + "="*50)
print(f"SMART EXTRACTOR RUNNING")
print(f"Project type : {plan['project_type']}")
print(f"Output folder: {plan['output_folder']}")
print("="*50)

# ── CREATE OUTPUT FOLDER ─────────────────────
output_folder = plan['output_folder']
os.makedirs(output_folder, exist_ok=True)

def extract_code_block(content, filename):
    """Extract code block for a specific file from agent output"""
    # Try to find by filename
    ext = filename.split('.')[-1]
    
    # Pattern 1: ```ext ... ```
    pattern1 = rf'```{ext}\s*(.*?)\s*```'
    match = re.search(pattern1, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Pattern 2: FILE: filename ... ``` 
    escaped = re.escape(filename)
    pattern2 = rf'{escaped}.*?```(?:\w+)?\s*(.*?)\s*```'
    match = re.search(pattern2, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return None

def extract_by_type(plan, dev_output):
    """Route to correct extraction based on project type"""
    project_type = plan['project_type']
    output_folder = plan['output_folder']
    files_created = []

    # ── HTML/LANDING PAGE ────────────────────
    if project_type in ['web_landing_page', 'javascript_app']:
        html_match = re.search(
            r'(<!DOCTYPE.*?</html>)', 
            dev_output, 
            re.DOTALL | re.IGNORECASE
        )
        if html_match:
            html = html_match.group(1)
        else:
            block = re.search(r'```html\s*(.*?)\s*```', dev_output, re.DOTALL)
            html = block.group(1) if block else dev_output

        path = os.path.join(output_folder, "index.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        files_created.append(path)
        print(f"Created: {path}")

    # ── PYTHON APPS ──────────────────────────
    elif project_type in ['python_cli_app', 'python_web_app', 
                           'api_backend', 'data_science']:
        # Create subfolders
        for file_info in plan['files_to_create']:
            file_path = file_info['path']
            full_path = os.path.join(output_folder, file_path)
            folder = os.path.dirname(full_path)
            if folder:
                os.makedirs(folder, exist_ok=True)

        # Extract each file
        for file_info in plan['files_to_create']:
            file_path = file_info['path']
            filename = os.path.basename(file_path)
            full_path = os.path.join(output_folder, file_path)

            # Find this file's code in the output
            section_pattern = rf'(?:FILE[:\s]+.*?{re.escape(filename)}.*?|#{1,3}\s+.*?{re.escape(filename)}.*?)\n(.*?)(?=(?:FILE[:\s]+|#{1,3}\s+\w)|$)'
            section_match = re.search(
                section_pattern, dev_output, re.DOTALL | re.IGNORECASE
            )

            code = extract_code_block(dev_output, filename)

            if code:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(code)
                files_created.append(full_path)
                print(f"Created: {full_path}")
            else:
                # Create empty placeholder
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(f"# {filename} - extracted from agent output\n")
                    f.write(f"# Please check outputs/dev_output.txt\n")
                files_created.append(full_path)
                print(f"Warning: Could not extract {filename} cleanly")

        # Always create __init__.py for Python packages
        src_folder = os.path.join(output_folder, "src")
        if os.path.exists(src_folder):
            init_path = os.path.join(src_folder, "__init__.py")
            if not os.path.exists(init_path):
                open(init_path, "w").close()

    # ── REACT APPS ───────────────────────────
    elif project_type == 'react_app':
        jsx_match = re.search(
            r'```(?:jsx|tsx|js)\s*(.*?)\s*```', dev_output, re.DOTALL
        )
        if jsx_match:
            path = os.path.join(output_folder, "App.jsx")
            with open(path, "w", encoding="utf-8") as f:
                f.write(jsx_match.group(1))
            files_created.append(path)
            print(f"Created: {path}")

    # ── FALLBACK ─────────────────────────────
    else:
        path = os.path.join(output_folder, "output.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(dev_output)
        files_created.append(path)
        print(f"Saved raw output: {path}")

    return files_created

# ── RUN EXTRACTION ───────────────────────────
files = extract_by_type(plan, dev_output)

# ── SAVE SUMMARY ─────────────────────────────
summary = {
    "project_type": plan['project_type'],
    "output_folder": plan['output_folder'],
    "files_created": files,
    "entry_point": plan['entry_point'],
    "run_command": plan['run_command'],
    "test_command": plan['test_command']
}

with open("outputs/extraction_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("\n" + "="*50)
print("EXTRACTION COMPLETE!")
print(f"Files created: {len(files)}")
print(f"\nTo run your project:")
print(f"  {plan['run_command']}")
print("="*50)