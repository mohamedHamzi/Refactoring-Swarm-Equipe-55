import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment
from src.graph import create_graph
from src.tools.files import list_files

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    # log_experiment("System", "STARTUP", "START", {"target": args.target_dir, "input_prompt": "START", "output_response": "STARTED"}, "INFO")

    # Initialize Graph
    from src.config import DEFAULT_MODEL_NAME
    print(f"🤖 Using Model: {DEFAULT_MODEL_NAME}")
    app = create_graph(model_name=DEFAULT_MODEL_NAME)
    
    # Find python files to refactor
    all_files = list_files(args.target_dir)
    py_files = [f for f in all_files if f.endswith(".py") and "test" not in os.path.basename(f).lower()] # Exclude test files from being refactored directly for now
    
    for py_file in py_files:
        print(f"\nProcessing file: {py_file}")
        
        initial_state = { 
            "target_file": py_file,
            "current_code": "",
            "refactoring_plan": "",
            "pylint_score": 0.0,
            "test_results": {},
            "iterations": 0,
            "max_iterations": 10, 
            "error_context": "",
            "status": "START"
        }
        
        try:
            for output in app.stream(initial_state):
                pass
            print(f"✅ Finished processing {py_file}")
        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")
            import traceback
            traceback.print_exc()

    print("✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()
