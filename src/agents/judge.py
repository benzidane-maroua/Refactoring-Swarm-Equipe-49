import subprocess 
import sys
from src.utils.logger import log_experiment,ActionType
from pathlib import Path

# Removes the user's file path from the output response in logs.
def sanitize_output(text: str, root_path: Path) -> str:

    clean_text = text.replace(str(root_path), ".")
    # Windows sometimes uses double backslashes, so we clean that too just in case
    clean_text = clean_text.replace(str(root_path).replace("\\", "\\\\"), ".")
    return clean_text

def judge_agent(state: dict) -> dict:
    target_dir=state["target_dir"]
    print(f"\nStarting Execution of the Judge...")

    # get the path then put the python files in a list
    path = Path(target_dir).resolve()
    python_files = list(path.glob("*.py"))

    if not python_files:
        print("Judge: No Python files found to test")
        state["judge_verdict"] = "PASS" 
        return state

    errors_found = []

    # loop over the files to test each one of them
    for file_path in python_files:
        print(f"Running {file_path.name}...")

        # run the code in the virtual env
        try:
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=15 # stop infinite loops after 15 seconds
            )
        except subprocess.TimeoutExpired:
            print("Judge: timeout errror")
            error_msg = f"TimeoutError: The script {file_path.name} took too long to run (infinite loop)"
            errors_found.append(error_msg)
            
            log_experiment(
                agent_name="Judge",
                model_used="System Execution",
                action=ActionType.DEBUG,
                details={
                    "file":str(file_path.name),
                    "input_prompt":f"Run {file_path.name}",
                    "output_response":"Process timed out (infinite loop detection)",
                    "issues_found": 1 
                },
                status="FAILURE"
            )
            break

        # analyze the returned code
        if result.returncode != 0:
            print("Judge: Code execution failed")
            raw_error = result.stderr  
            clean_error = sanitize_output(raw_error, path)

            error_msg = f"File: {file_path.name}\nError:\n{clean_error}"
            errors_found.append(error_msg)


            # log the problem
            log_experiment(
                agent_name="Judge",
                model_used="System Execution",
                action=ActionType.DEBUG,
                details={
                    "file": str(file_path.name),
                    "input_prompt": f"Run {file_path.name}",
                    "output_response": clean_error, 
                    "exit_code": result.returncode,
                    "issues_found": 1 
                },
                status="FAILURE"
            )
            # here we break after we find that the program that didnt terminate successfully
            break 
        else:
            print(f"Judge: {file_path.name} passed")
            log_experiment(
                agent_name="Judge",
                model_used="System-Execution",
                action=ActionType.ANALYSIS,
                details={
                    "file":str(file_path.name),
                    "input_prompt":f"Run {file_path.name}",
                    "output_response":"Execution successful"
                },
                status="SUCCESS"
            )

    # logic to pass to the fixer
    if errors_found:
        state["judge_verdict"] = "FAIL"
        # fixer needs to read the last_error to correct his errors
        state["last_error"] = "\n".join(errors_found)
        print(f"Judge: Code is not correct. Send back to Fixer")
    else:
        state["judge_verdict"] = "PASS"
        state["last_error"] = None
        print(f"Judge: The code is correct")

    # increment the iteration so that it can stop if 10 reached
    state["iteration"] = state["iteration"] + 1
    print(f"Iteration number: {state['iteration']}/10")

    return state
