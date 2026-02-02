
from src.utils.logger import log_experiment, ActionType
from src.tools.testing import run_pytest
import os

class JudgeAgent:
    def __init__(self):
        self.agent_name = "Judge_Agent"

    def evaluate(self, test_dir: str):
        """
        Runs tests and determines if the refactoring was successful.
        """
        
        # Run pytest
        results = run_pytest(test_dir)
        
        status = "SUCCESS" if results["success"] else "FAILURE"
        
        # LOGGING (MANDATORY)
        # Note: Even though Judge doesn't necessarily use an LLM for judgment here (it uses pytest),
        # we log the action. If we used an LLM to analyze the failure, specific input/output would be needed.
        # For pure execution, we can leave input_prompt/output_response empty or provide execution details if strictly required by logger validator.
        # The logger validator requires input/output for ANALYSIS, GEN, DEBUG, FIX. 
        # Let's map this to DEBUG if it fails, or ANALYSIS if it passes?
        # Actually, let's just use "ANALYSIS" or a custom action if allowed, but strict enum is required.
        # Let's use DEBUG for the log entry as it's testing/debugging context.
        
        log_experiment(
            agent_name=self.agent_name,
            model_used="pytest-7.4.4", # Not an LLM, but tool version
            action=ActionType.DEBUG,
            details={
                "directory_tested": test_dir,
                "input_prompt": f"Run pytest on {test_dir}",
                "output_response": results["output"],
                "success": results["success"]
            },
            status=status
        )
        
        return results
