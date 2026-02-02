
import subprocess
import json

def run_pylint(file_path: str) -> dict:
    """Run pylint on a file and return the score and report."""
    try:
        # Run pylint just to get the score and checking
        # We use a custom format to easily parse, or just standard text
        result = subprocess.run(
            ["pylint", file_path, "--output-format=json"], 
            capture_output=True, 
            text=True,
            check=False
        )
        
        # Pylint output might not be pure JSON if there are other logs, but --output-format=json usually works
        # Sometimes pylint returns non-zero exit code even on success (if score < 10)
        
        try:
            issues = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback if json parsing fails (rare but possible with mixed output)
            return {
                "score": 0.0,
                "output": result.stdout + "\n" + result.stderr,
                "issues": []
            }
            
        # Get the score. Pylint doesn't output score in JSON mode by default easily accessibly in old versions,
        # but we can run it again or calculate it. 
        # Alternatively, we can run with text output to grab the score line.
        
        score_proc = subprocess.run(
            ["pylint", file_path, "--reports=y"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Extract score from text output: "Your code has been rated at 8.33/10"
        import re
        score_match = re.search(r"Your code has been rated at ([\d\.]+)/10", score_proc.stdout)
        score = float(score_match.group(1)) if score_match else 0.0
        
        return {
            "score": score,
            "output": score_proc.stdout, # Full text report is useful for the LLM
            "issues": issues
        }

    except Exception as e:
        return {"score": 0.0, "output": f"Error running pylint: {e}", "issues": []}
