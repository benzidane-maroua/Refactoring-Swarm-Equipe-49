from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, List
from src.tools.file_tools import read_file, write_file, list_python_files
from src.tools.llm_call import call_llm
from src.prompts.fixer_prompts import FIXER_V1
from src.utils.logger import log_experiment,ActionType
from src.agents.auditor import count_issues

load_dotenv()

def fixer_agent(state: dict) -> dict:

    target_dir = state["target_dir"]
    refactoring_plan = state["audit_report"]
    counter = 0

    # get the files containing the code we want to fix
    python_files = list_python_files(target_dir)
    fixed_files = []

    for file_path in python_files:
        original_code = read_file(file_path)
        prompt = f""" {FIXER_V1}
                 Refactoring PLAN: 
                 {refactoring_plan}
                 FILE NAME:
                 {file_path.name}
                 CURRENT CODE:
                 ```python
                 {original_code}
                """

        try:
            fixed_code = call_llm(prompt)
            print("\nPrinting fixed code\n", fixed_code)
            log_experiment(
                agent_name="Fixer",
                model_used="Ollama/deepseek-coder",
                action=ActionType.FIX,
                details={
                    "file": file_path.name,
                    "input_prompt": prompt,
                    "output_response": fixed_code,
                    "issues_found": state["audit_report"][0]
                },
                status="SUCCESS"
            )
            if fixed_code.strip():
                write_file(file_path, fixed_code)
                fixed_files.append(file_path.name)

        except TimeoutError:
            log_experiment(
                agent_name="Fixer",
                model_used="Ollama/deepseek-coder",
                action=ActionType.FIX,
                details={
                    "file": file_path.name,
                    "input_prompt": prompt,
                    "output_response": "Process timed out (infinite loop detection)",
                    "issues_found": 1
                },
                status="FAILURE"
            )

    print(fixed_files)
    state["fixed_files"] = fixed_files
    return state