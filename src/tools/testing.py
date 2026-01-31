import subprocess
import re
from typing import Dict, Any


def run_pytest(test_dir: str) -> dict:
    """
    Runs pytest in the specified directory and returns structured results.
    
    Args:
        test_dir: Directory or file to test
        
    Returns:
        dict: {
            'success': bool,
            'output': str,
            'tests_passed': int,      # NEW: count of passed tests
            'tests_failed': int,      # NEW: count of failed tests
            'tests_error': int,       # NEW: count of errors
            'duration': float,        # NEW: execution time
            'error_details': str      # NEW: extracted failure details for Fixer
        }
    """
    try:
        result = subprocess.run(
            ["pytest", test_dir, "-v", "--tb=short"],  # Added verbose and short traceback
            capture_output=True,
            text=True,
            check=False,
            timeout=120  # Prevent hanging tests
        )
        
        output = result.stdout + "\n" + result.stderr
        success = result.returncode == 0
        
        # Handle specific pytest exit codes
        if result.returncode == 5:
            output += "\n\nNO TESTS FOUND: Pytest exit code 5. functionality needs to be tested."
            success = False
        
        # NEW: Parse test counts from output
        tests_passed = len(re.findall(r'PASSED', output))
        tests_failed = len(re.findall(r'FAILED', output))
        tests_error = len(re.findall(r'ERROR', output))
        
        # NEW: Extract duration
        duration = 0.0
        duration_match = re.search(r'in ([\d.]+)s', output)
        if duration_match:
            duration = float(duration_match.group(1))
        
        # NEW: Extract error details for Fixer
        error_details = ""
        if not success:
            error_details = extract_test_failures(output)
        
        return {
            "success": success,
            "output": output,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_error": tests_error,
            "duration": duration,
            "error_details": error_details if error_details else None
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "ERROR: Tests timed out after 120 seconds",
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_error": 1,
            "duration": 120.0,
            "error_details": "Tests timed out - possible infinite loop or hanging test"
        }
    except Exception as e:
        return {
            "success": False,
            "output": f"Error running pytest: {e}",
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_error": 1,
            "duration": 0.0,
            "error_details": str(e)
        }


def extract_test_failures(output: str) -> str:
    """
    Extracts failure details from pytest output.
    Useful for providing context to the Fixer agent.
    
    Args:
        output: Full pytest output
        
    Returns:
        Extracted failure/error details
    """
    # Look for FAILED section with details
    failure_section = re.search(r'(FAILED.*?)(?:=+\s+|$)', output, re.DOTALL)
    if failure_section:
        content = failure_section.group(1)
        return content[:2000] + "\n...(truncated)" if len(content) > 2000 else content
    
    # Look for ERROR section
    error_section = re.search(r'(ERROR.*?)(?:=+\s+|$)', output, re.DOTALL)
    if error_section:
        content = error_section.group(1)
        return content[:2000] + "\n...(truncated)" if len(content) > 2000 else content
    
    # Fallback: return last part of output (likely contains errors)
    return output[-1000:] if len(output) > 1000 else output


def check_test_coverage(directory: str) -> Dict[str, Any]:
    """
    Checks if test files exist in the directory.
    Useful for validating that tests are present before running.
    
    Args:
        directory: Directory to check
        
    Returns:
        dict: {
            'has_tests': bool,
            'test_files': list[str],
            'count': int
        }
    """
    import os
    
    test_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
            elif file.endswith('_test.py'):
                test_files.append(os.path.join(root, file))
    
    return {
        'has_tests': len(test_files) > 0,
        'test_files': test_files,
        'count': len(test_files)
    }