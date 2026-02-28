
from src.utils.logger import log_experiment, ActionType
from src.tools.testing import run_pytest
import os

# Environment error patterns that indicate infrastructure issues, not code bugs
ENVIRONMENT_ERROR_PATTERNS = [
    "WinError",
    "FileNotFoundError",
    "No module named",
    "command not found",
    "not recognized as an internal",
    "not found",
    "TIMEOUT",
    "ENVIRONMENT_ERROR",
]


class JudgeAgent:
    def __init__(self):
        self.agent_name = "Judge_Agent"

    def _classify_failure(self, results: dict) -> str:
        """Classifies a test failure as CODE_ERROR or ENVIRONMENT_ERROR.
        
        Returns:
            "ENVIRONMENT_ERROR" if the failure is due to infrastructure/tooling.
            "CODE_ERROR" if the failure is due to actual test failures.
        """
        # Check structured error_type first (from upgraded testing.py)
        if results.get("error_type") in ("ENVIRONMENT_ERROR", "TIMEOUT"):
            return results["error_type"]
        
        # Fallback: pattern match on output text
        output = results.get("output", "")
        for pattern in ENVIRONMENT_ERROR_PATTERNS:
            if pattern in output:
                return "ENVIRONMENT_ERROR"
        
        return "CODE_ERROR"

    def evaluate(self, test_dir: str, iteration: int = None):
        """
        Runs tests and determines if the refactoring was successful.
        Classifies failures to avoid wasting iterations on environment errors.
        """
        
        # Run pytest
        results = run_pytest(test_dir)
        
        if results["success"]:
            status = "SUCCESS"
            error_type = None
        else:
            error_type = self._classify_failure(results)
            status = "FAILURE"
        
        # LOGGING (MANDATORY)
        log_experiment(
            agent_name=self.agent_name,
            model_used="pytest-7.4.4",
            action=ActionType.DEBUG,
            details={
                "directory_tested": test_dir,
                "input_prompt": f"Run pytest on {test_dir}",
                "output_response": results["output"],
                "success": results["success"],
                "error_type": error_type
            },
            status=status,
            iteration=iteration
        )
        
        # Add error_type to results for graph edge logic
        results["error_type"] = error_type
        return results
