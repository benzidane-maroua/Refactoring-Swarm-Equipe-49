from pathlib import Path
from dotenv import load_dotenv
from typing import Dict
import re
from src.tools.file_tools import read_file, write_file, list_python_files
from src.tools.llm_call import call_llm
from src.prompts.fixer_prompts import FIXER_V2
from src.utils.logger import log_experiment, ActionType

load_dotenv()

def fixer_agent(state: dict) -> dict:
    """
    Fixes Python files in target_dir using LLM + audit report.
    Extracts code between ``` from LLM output and writes it to sandbox/test.
    """
    target_dir = Path(state["target_dir"])
    audit_report = state.get("audit_report", [])
    python_files = list_python_files(target_dir)
    
    # Directory to save fixed files
    output_dir = Path("sandbox/test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fixed_files = []

    for idx, file_path in enumerate(python_files):
        print(file_path)
        original_code = read_file(file_path)
       
        # Get the corresponding report (safe)
        file_report = audit_report[idx] if idx < len(audit_report) else {}
        issues_found = file_report.get("issues_found", 0)
        refactoring_plan = file_report.get("refactoring_plan", [])

        # Build prompt for LLM
        prompt = f"""{FIXER_V2}

REFATORING PLAN:
{refactoring_plan}

FILE TO FIX: {file_path.name}
CURRENT CODE:
```python
{original_code}
```"""

        try:
            # Call Hugging Face model
            llm_output = call_llm(prompt)

            # Print raw output for debugging
            print(f"\n--- LLM raw output for {file_path.name} ---\n")
            print(llm_output)
            print("\n----------------------------------------\n")

            # Extract code between ``` or ```python
            match = re.search(r"```(?:python)?\n(.*?)```", llm_output, re.DOTALL)
            if match:
                fixed_code = match.group(1).strip()
            else:
                fixed_code = ""
                print(f"No code found in LLM output for {file_path.name}")

            # Write fixed code if valid
            if fixed_code:
                output_file = output_dir / file_path.name
                with output_file.open("w", encoding="utf-8") as f:
                    f.write(fixed_code)
                fixed_files.append(file_path.name)
                print(f"Fixed code written to {output_file.resolve()}")

            # Log experiment
            log_experiment(
                agent_name="Fixer",
                model_used="HuggingFace/your-model",
                action=ActionType.FIX,
                details={
                    "file": file_path.name,
                    "input_prompt": prompt,
                    "output_response": llm_output,
                    "issues_found": issues_found
                },
                status="SUCCESS" if fixed_code else "FAILURE"
            )

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            log_experiment(
                agent_name="Fixer",
                model_used="HuggingFace/your-model",
                action=ActionType.FIX,
                details={
                    "file": file_path.name,
                    "input_prompt": prompt,
                    "output_response": str(e),
                    "issues_found": issues_found
                },
                status="FAILURE"
            )

    state["fixed_files"] = fixed_files
    return state