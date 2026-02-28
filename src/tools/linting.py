
import subprocess
import json


def run_pylint(file_path: str) -> dict:
    """Run pylint on a file and return the score and report."""
    try:
        # Run pylint with JSON output
        result = subprocess.run(
            ["pylint", file_path, "--output-format=json"], 
            capture_output=True, 
            text=True,
            check=False,
            timeout=120  # 2-minute timeout to prevent hangs
        )
        
        try:
            issues = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "score": 0.0,
                "output": result.stdout + "\n" + result.stderr,
                "issues": []
            }
            
        # Get the score via text output
        score_proc = subprocess.run(
            ["pylint", file_path, "--reports=y"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120  # 2-minute timeout to prevent hangs
        )
        
        # Extract score from text output: "Your code has been rated at 8.33/10"
        import re
        score_match = re.search(r"Your code has been rated at ([\d\.]+)/10", score_proc.stdout)
        score = float(score_match.group(1)) if score_match else 0.0
        
        return {
            "score": score,
            "output": score_proc.stdout,
            "issues": issues
        }

    except subprocess.TimeoutExpired:
        return {
            "score": 0.0,
            "output": "TIMEOUT: Pylint exceeded 120-second time limit.",
            "issues": [],
            "error_type": "TIMEOUT"
        }
    except FileNotFoundError:
        return {
            "score": 0.0,
            "output": "ERROR: Pylint not found. Install with: pip install pylint",
            "issues": [],
            "error_type": "ENVIRONMENT_ERROR"
        }
    except Exception as e:
        return {"score": 0.0, "output": f"Error running pylint: {e}", "issues": []}
