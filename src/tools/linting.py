"""
Linting tools for code quality analysis.
Enhanced version with better error handling and token optimization.
"""

import subprocess
import json
import re
from typing import Dict, List, Any


def run_pylint(file_path: str) -> dict:
    """
    Run pylint on a file and return the score and report.
    
    Args:
        file_path: Path to Python file to analyze
        
    Returns:
        dict: {
            'score': float,
            'output': str,
            'issues': list[dict]
        }
    """
    try:
        # First, get JSON output for structured issues
        result = subprocess.run(
            ["pylint", file_path, "--output-format=json"], 
            capture_output=True, 
            text=True,
            check=False,
            timeout=30  # Prevent hanging
        )
        
        # Parse JSON issues
        issues = []
        try:
            if result.stdout.strip():
                issues = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            issues = []
        
        # Second, get text output with score
        score_proc = subprocess.run(
            ["pylint", file_path, "--reports=y"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )
        
        # Extract score: "Your code has been rated at 8.33/10"
        score = 0.0
        score_match = re.search(r"Your code has been rated at ([\d.\-]+)/10", score_proc.stdout)
        if score_match:
            score = float(score_match.group(1))
        
        return {
            "score": score,
            "output": score_proc.stdout,  # Full text report for LLM
            "issues": issues
        }

    except subprocess.TimeoutExpired:
        return {
            "score": 0.0,
            "output": "ERROR: Pylint timed out after 30 seconds",
            "issues": []
        }
    except FileNotFoundError:
        return {
            "score": 0.0,
            "output": "ERROR: Pylint not found. Install with: pip install pylint",
            "issues": []
        }
    except Exception as e:
        return {
            "score": 0.0,
            "output": f"Error running pylint: {e}",
            "issues": []
        }


def format_pylint_issues(issues: List[Dict[str, Any]], max_issues: int = 15) -> str:
    """
    Format pylint issues for LLM consumption (token-optimized).
    
    Args:
        issues: List of issue dicts from run_pylint
        max_issues: Maximum number of issues to include
        
    Returns:
        Formatted string with top issues
    """
    if not issues:
        return "No issues found by pylint."
    
    # Sort by severity (error > warning > convention > refactor)
    severity_order = {'error': 0, 'warning': 1, 'convention': 2, 'refactor': 3}
    sorted_issues = sorted(
        issues,
        key=lambda x: severity_order.get(x.get('type', 'refactor').lower(), 4)
    )
    
    # Limit to save tokens
    limited_issues = sorted_issues[:max_issues]
    
    formatted = f"Total issues: {len(issues)}. Showing top {len(limited_issues)}:\n\n"
    
    for idx, issue in enumerate(limited_issues, 1):
        line = issue.get('line', '?')
        col = issue.get('column', '?')
        issue_type = issue.get('type', 'unknown')
        message = issue.get('message', 'No message')
        symbol = issue.get('symbol', 'unknown')
        
        formatted += f"{idx}. Line {line}:{col} [{issue_type.upper()}] {message} ({symbol})\n"
    
    if len(issues) > max_issues:
        formatted += f"\n... and {len(issues) - max_issues} more issues.\n"
    
    return formatted