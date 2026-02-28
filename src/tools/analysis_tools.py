# src/tools/analysis_tools.py
import subprocess
from pathlib import Path
import re

def run_pylint(file_path: Path) -> dict:
    """
    Runs pylint on a Python file and returns structured messages.
    """
    # Run pylint with parseable output
    result = subprocess.run(
        ["pylint", str(file_path), "--output-format=text", "--score=n"],
        capture_output=True,
        text=True
    )

    # Extract lines that look like messages
    # Example pylint line: example.py:3:0: C0114: Missing module docstring (missing-module-docstring)
    message_pattern = re.compile(r"^(.*?):(\d+):\d+: (\w\d+): (.*) \((.*)\)$")
    messages = []
    for line in result.stdout.splitlines():
        match = message_pattern.match(line.strip())
        if match:
            filename, line_no, code, msg, symbol = match.groups()
            messages.append(f"{code} (line {line_no}): {msg}")

    return {
        "returncode": result.returncode,
        "messages": messages,
        "stdout": result.stdout,
        "stderr": result.stderr
    }