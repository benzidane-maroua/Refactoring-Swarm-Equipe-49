# src/agents/auditor.py
from pathlib import Path
from dotenv import load_dotenv
import json
from src.tools.file_tools import read_file, list_python_files
from src.tools.analysis_tools import run_pylint
from src.tools.llm_call import call_llm
from src.prompts.auditor_prompts import AUDITOR_V1
from src.utils.logger import log_experiment, ActionType

load_dotenv()


def auditor_agent(state: dict) -> dict:
    """
    Auditor agent that analyzes Python files using pylint and optionally
    enhances the report using an LLM. Always returns a JSON-safe
    audit_report with issues_found and refactoring_plan.
    """
    target_dir = state["target_dir"]
    files = list_python_files(target_dir)

    all_reports = []

    for file_path in files:
        content = read_file(file_path)
        print(f"Auditing {file_path.name}\n")

        # Skip empty files
        if not content.strip():
            audit_json = {"issues_found": 0, "refactoring_plan": []}
            all_reports.append(audit_json)
            continue

        # Run pylint on file
        pylint_result = run_pylint(file_path)
        pylint_output = pylint_result.get("stdout", "")
        pylint_messages = [line for line in pylint_output.splitlines() if line.strip()]

        # Fallback: generate audit from pylint if LLM fails
        fallback_audit = {
            "issues_found": len(pylint_messages),
            "refactoring_plan": pylint_messages
        }

        # Build prompt for LLM
        snippet = "\n".join(content.splitlines()[:150])
        pylint_snippet = "\n".join(pylint_messages[:20])
        prompt = f"""
{AUDITOR_V1}

Analyze this Python code and Pylint report and produce a JSON object with:
- "issues_found": integer
- "refactoring_plan": list of strings

CODE SNIPPET:
{snippet}

PYLINT REPORT:
{pylint_snippet}
"""

        try:
            # Call LLM to enhance report (optional)
            llm_output = call_llm(prompt)
            if isinstance(llm_output, dict) and "issues_found" in llm_output:
                audit_json = llm_output
            else:
                # fallback to pylint-based audit
                audit_json = fallback_audit

        except Exception as e:
            print(f"LLM failed for {file_path.name}: {e}")
            audit_json = fallback_audit

        print(f"Audit report for {file_path.name}: {audit_json}\n")

        # Log the audit
        log_experiment(
            agent_name="Auditor",
            model_used="HuggingFace/starcoder",
            action=ActionType.ANALYSIS,
            details={
                "file": file_path.name,
                "input_prompt": prompt,
                "output_response": audit_json,
                "issues_found": audit_json.get("issues_found", 0)
            },
            status="SUCCESS"
        )

        all_reports.append(audit_json)

    state["audit_report"] = all_reports
    return state