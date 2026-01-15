import argparse
import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from src.utils.logger import log_experiment, ActionType
from verify_logs import verify_logs
from src.graph.workflow import build_workflow
from src.tools.sandbox_tools import ensure_safe_path

load_dotenv()

def main():
    # parsing the directory argument from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()
    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")

    log_experiment(
        agent_name="System",
        model_used="STARTUP", 
        action=ActionType.ANALYSIS, 
        details={
            "target_directory": args.target_dir,
            "input_prompt": "System Start", 
            "output_response": "Checking directory existence"
        },
        status="SUCCESS"
    )

    target_dir = Path(args.target_dir)

    # ensure that we're working in sandbox
    ensure_safe_path(target_dir)

    # initialize the state
    state = { 
        "target_dir": target_dir,
        "iteration": 0,
        "audit_report": None,
        "fixes_applied": False,
        "test_results": None,
        "judge_verdict": None,
    }

    # build and run the workflow
    workflow = build_workflow()
    final_state = workflow.invoke(state)

    print("\n FINAL RESULT")
    print("Judge verdict:", final_state.get("judge_verdict"))
    print(state)

    # Run verification at the end to check for data validity
    print("\nDATA OFFICER CHECK:")
    try:
        verify_logs() 
    except SystemExit:
        print("Data verification failed")
        sys.exit(1)
    except Exception as e:
        print(f"There is an exception: {e}")  

if __name__ == "__main__":
    main()