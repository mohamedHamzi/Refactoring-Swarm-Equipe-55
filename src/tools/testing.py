
import subprocess
import sys
import os


def run_pytest(test_dir: str) -> dict:
    """Runs pytest in the specified directory and returns results."""
    # Validate that the test directory exists
    if not os.path.exists(test_dir):
        return {
            "success": False,
            "output": f"Test directory not found: {test_dir}",
            "error_type": "ENVIRONMENT_ERROR"
        }

    try:
        # Use sys.executable to run pytest as a module for cross-platform reliability
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_dir, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120  # 2-minute timeout to prevent hangs
        )

        success = result.returncode == 0

        return {
            "success": success,
            "output": result.stdout + "\n" + result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "TIMEOUT: Pytest exceeded 120-second time limit.",
            "error_type": "TIMEOUT"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "output": "Python executable not found. Ensure Python is installed correctly.",
            "error_type": "ENVIRONMENT_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "output": f"Error running pytest: {e}",
            "error_type": "ENVIRONMENT_ERROR" if "WinError" in str(e) or "FileNotFoundError" in str(e) else "UNKNOWN"
        }
