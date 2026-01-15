from pathlib import Path
from dotenv import load_dotenv
from typing import Dict
from src.tools.file_tools import read_file
from src.tools.file_tools import list_python_files
from src.tools.llm_call import call_llm
from src.tools.analysis_tools import run_pylint
from src.prompts.auditor_prompts import AUDITOR_V1

load_dotenv()

def auditor_agent(state: dict) -> dict:

    target_dir = state["target_dir"]
    files = list_python_files(target_dir)

    # read the code of each file and put it in code_context so that it can be added to the prompt
    code_context = ""
    for file_path in files:
        content = read_file(file_path)
        code_context += f"\n File: {file_path.name}\n{content}\n"

    # run the static analysis 
    pylint_report = run_pylint(target_dir) 

    # build the prompt to pass it to the LLM
    prompt = f"""
{AUDITOR_V1}
CODEBASE:
{code_context}
PYLINT REPORT:
{pylint_report}
Produce a refactoring plan.
"""

    # call the LLM
    audit_report = call_llm(prompt)

    # save results in state
    state["audit_report"] = audit_report
    return state