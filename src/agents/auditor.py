from pathlib import Path
from dotenv import load_dotenv
from typing import Dict
import json
from src.tools.file_tools import read_file
from src.tools.file_tools import list_python_files
from src.tools.llm_call import call_llm
from src.tools.analysis_tools import run_pylint
from src.prompts.auditor_prompts import AUDITOR_V1
from src.utils.logger import log_experiment,ActionType

load_dotenv()

def count_issues(audit_output: str) -> int:
    try:
        data = json.loads(audit_output)
        return len(data.get("issues", []))
    except json.JSONDecodeError:
        return 0

def auditor_agent(state: dict) -> dict:

    target_dir = state["target_dir"]
    files = list_python_files(target_dir)

    # run the static analysis 
    pylint_report = run_pylint(target_dir) 
    all_reports = []

    for file_path in files:
        content = read_file(file_path)

        # build the prompt to pass it to the LLM
        prompt = f"""
            {AUDITOR_V1}\n
            CODE:\n
            {content}\n
            PYLINT REPORT:\n
            {pylint_report}\n
            Produce a refactoring plan to fix the code.\n
        """
        try:
            audit = call_llm(prompt)

            log_experiment(
                agent_name="Auditor",
                model_used="Ollama/deepseek-coder",
                action=ActionType.ANALYSIS,
                details={
                    "file": file_path.name,
                    "input_prompt": prompt,
                    "output_response": audit,
                    "issues_found": count_issues(audit)
                },
                status="SUCCESS"
            )

            all_reports.append(audit)
        except TimeoutError:
            log_experiment(
                agent_name="Auditor",
                model_used="Ollama/deepseek-coder",
                action=ActionType.ANALYSIS,
                details={
                    "file": file_path.name,
                    "input_prompt": prompt,
                    "output_response": "Process timed out (infinite loop detection)",
                    "issues_found": 1
                },
                status="FAILURE"
            )
        
    # save results in the state
    state["audit_report"] = all_reports
    return state