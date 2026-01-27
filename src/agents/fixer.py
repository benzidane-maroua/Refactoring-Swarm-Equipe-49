from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, List
from src.tools.file_tools import read_file, write_file, list_python_files
from src.tools.llm_call import call_llm
from src.prompts.fixer_prompts import FIXER_V1

load_dotenv()

def fixer_agent(state: dict) -> dict:
    """
    Fixer agent:
    - Reads refactoring plan
    - Applies fixes file by file using LLM
    """

    target_dir = state["target_dir"]
    refactoring_plan = state["audit_report"]

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
        fixed_code = call_llm(prompt)

        if fixed_code.strip():
            write_file(file_path, fixed_code)
            fixed_files.append(file_path.name)
    print(fixed_files)
    state["fixed_files"] = fixed_files
    return state