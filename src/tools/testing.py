
import subprocess

def run_pytest(test_dir: str) -> dict:
    """Runs pytest in the specified directory and returns results."""
    try:
        result = subprocess.run(
            ["pytest", test_dir],
            capture_output=True,
            text=True,
            check=False
        )
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "output": result.stdout + "\n" + result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "output": f"Error running pytest: {e}"
        }
