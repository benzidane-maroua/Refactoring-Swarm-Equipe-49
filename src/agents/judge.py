import subprocess
import sys
from pathlib import Path
from src.utils.logger import log_experiment, ActionType

def sanitize_output(text: str, root_path: Path) -> str:
    """
    Remove sensitive file paths from output for privacy.
    """
    clean_text = text.replace(str(root_path), ".")
    clean_text = clean_text.replace(str(root_path).replace("\\", "\\\\"), ".")
    return clean_text

def judge_agent(state: dict) -> dict:
    """
    Executes all Python files in the target directory and updates state
    with the judge verdict. Works for fixed files from the LLM Fixer.
    """
    target_dir = Path('sandbox/test').resolve()
    iteration = state.get("iteration", 0) + 1
    print(f"\nStarting Execution of the Judge... Iteration {iteration}")

    python_files = list(target_dir.glob("*.py"))

    if not python_files:
        print("Judge: No Python files found to test")
        state["judge_verdict"] = "PASS"
        state["last_error"] = None
        state["iteration"] = iteration
        return state

    errors_found = []

    for file_path in python_files:
        print(f"Running {file_path.name}...")

        try:
            # Execute Python file safely
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=15  # prevent infinite loops
            )
        except subprocess.TimeoutExpired:
            print("Judge: Timeout detected")
            error_msg = f"TimeoutError: {file_path.name} exceeded 15s execution time."
            errors_found.append(error_msg)
            log_experiment(
                agent_name="Judge",
                model_used="System Execution",
                action=ActionType.DEBUG,
                details={
                    "file": file_path.name,
                    "input_prompt": f"Run {file_path.name}",
                    "output_response": "Process timed out (infinite loop detection)",
                    "issues_found": 1
                },
                status="FAILURE"
            )
            break

        # Handle runtime errors
        if result.returncode != 0:
            print("Judge: Code execution failed")
            clean_error = sanitize_output(result.stderr, target_dir)
            errors_found.append(f"{file_path.name}:\n{clean_error}")
            log_experiment(
                agent_name="Judge",
                model_used="System Execution",
                action=ActionType.DEBUG,
                details={
                    "file": file_path.name,
                    "input_prompt": f"Run {file_path.name}",
                    "output_response": clean_error,
                    "exit_code": result.returncode,
                    "issues_found": 1
                },
                status="FAILURE"
            )
            break
        else:
            print(f"Judge: {file_path.name} passed")
            log_experiment(
                agent_name="Judge",
                model_used="System Execution",
                action=ActionType.ANALYSIS,
                details={
                    "file": file_path.name,
                    "input_prompt": f"Run {file_path.name}",
                    "output_response": "Execution successful"
                },
                status="SUCCESS"
            )

    # Update state based on errors
    if errors_found:
        state["judge_verdict"] = "FAIL"
        state["last_error"] = "\n".join(errors_found)
        print("Judge: Code is not correct. Send back to Fixer")
    else:
        state["judge_verdict"] = "PASS"
        state["last_error"] = None
        print("Judge: The code is correct")

    state["iteration"] = iteration
    return state