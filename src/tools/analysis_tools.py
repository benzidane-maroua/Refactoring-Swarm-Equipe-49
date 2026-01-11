import subprocess
from pathlib import Path
from .sandbox import BASE_SANDBOX, ensure_safe_path

# src/tools/pylint_runner.py
import subprocess
from pathlib import Path
from .sandbox import ensure_safe_path

def run_pylint(file_path: Path) -> dict:
    """
    Runs pylint on a given Python file.
    
    Args:
        file_path: Path to the Python file. Must start inside sandbox.
                Can be the teacher folder or sandbox/input/output.   
    Returns:
        dict with:
            - returncode: 0 if pylint passed, non-zero otherwise
            - stdout: pylint standard output
            - stderr: pylint standard error
    """
    # Ensure sandbox safety
    safe_file = ensure_safe_path(file_path)

    # Run pylint
    result = subprocess.run(
        ["pylint", str(safe_file), "--score=n"],
        capture_output=True,
        text=True
    )
    """example :result = run_pylint(Path("sandbox/student_code/main.py"))

    if result["returncode"] != 0:
    print("Lint failed")
    print(result["stdout"])"""

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
