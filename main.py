import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType
from verify_logs import verify_logs

load_dotenv()

def main():
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

    # Orchastrator logic

    print("✅ MISSION_COMPLETE")

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