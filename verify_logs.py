from src.utils.logger import ActionType
import json
import os
import sys

LOG_FILE = os.path.join("logs", "experiment_data.json")

def verify_logs():
    print(f"Starting verification of {LOG_FILE}...")

    # Check if the experiment_data file exists and read it
    if not os.path.exists(LOG_FILE):
        print(f"ERROR: File {LOG_FILE} does not exist")
        sys.exit(1)
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            content= json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: The file is not valid JSON. Syntax error: {e}")
        exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error while opening the file: {e}")
        exit(1)

    print("Check1 succeeded: the file is opened and parsed as JSON")

    # Check if the file contains a list
    if not isinstance(content, list):
        print(f"ERROR: {LOG_FILE} does not contain a list")
        sys.exit(1)

    # Check if file is empty (no logs)
    if len(content) == 0:
        print(f"WARNING: {LOG_FILE} is empty! (Data Quality Score = 0 if submitted like this)")
        sys.exit(1)

    print(f"Check2 succeeded: the file contains {len(content)} log entries")

    # Loop over the entries of the list
    log_fields = ["id", "timestamp", "agent", "model", "action", "details", "status"]
    valid_action_values = [a.value for a in ActionType]
    required_keys = ["input_prompt", "output_response"]
    for i, log in enumerate(content):
        for field in log_fields:
            if field not in log:
                print(f"ERROR at log number {i}: Missing field {field}") 
                sys.exit(1)

        # Check if action is valid
        if log["action"] not in valid_action_values:
            print(f"ERROR at log number {i}: Action '{log['action']}' is not valid")
            sys.exit(1)

        # Check the validity of the prompt (two mandatory fields: "input_prompt" and "output_prompt")
        missing_keys = [key for key in required_keys if key not in log["details"]]
        if missing_keys:
            print(f"ERROR at log number {i}: Missing key 'input_prompt' or 'output_response' in {log['details']}")
            sys.exit(1)

    print("Check3 succeeded: All logs are valid")
    print("\nDATA QUALITY CHECK PASSED")

