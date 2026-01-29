
from src.utils.logger import log_experiment, ActionType
from src.tools.testing import run_pytest
import os


class JudgeAgent:
    def __init__(self):
        self.agent_name = "Judge_Agent"

    def evaluate(self, test_dir: str):
        """
        Runs tests and determines if the refactoring was successful.
        
        Args:
            test_dir: Directory containing test files
            
        Returns:
            dict: {
                'success': bool,
                'output': str,
                'tests_passed': int,
                'tests_failed': int,
                'tests_error': int,
                'duration': float,
                'error_details': str  # For passing to Fixer
            }
        """
        print(f"🧑‍⚖️ Judge Agent: Evaluating {test_dir}")
        
        # Run pytest
        results = run_pytest(test_dir)
        
        status = "SUCCESS" if results["success"] else "FAILURE"
        
        # Print summary
        if results["success"]:
            print(f"   ✅ All {results.get('tests_passed', 0)} tests passed!")
        else:
            print(f"   ❌ Failed: {results.get('tests_failed', 0)}, "
                  f"Errors: {results.get('tests_error', 0)}")
        
        # LOGGING (MANDATORY)
        # We use DEBUG action type because we're debugging/testing the code
        log_experiment(
            agent_name=self.agent_name,
            model_used="pytest",  # Tool version, not LLM
            action=ActionType.DEBUG,
            details={
                "directory_tested": test_dir,
                "input_prompt": f"pytest {test_dir} -v --tb=short",  # REQUIRED
                "output_response": results["output"],  # REQUIRED
                "success": results["success"],
                "tests_passed": results.get("tests_passed", 0),
                "tests_failed": results.get("tests_failed", 0),
                "tests_error": results.get("tests_error", 0),
                "duration": results.get("duration", 0.0)
            },
            status=status
        )
        
        return results