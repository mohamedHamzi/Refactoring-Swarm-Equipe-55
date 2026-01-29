
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.logger import log_experiment, ActionType
from src.tools.linting import run_pylint
from src.tools.files import read_file
from src.agents.base import BaseAgent
from src.config import DEFAULT_MODEL_NAME
import os

class AuditorAgent(BaseAgent):
    def __init__(self, model_name=DEFAULT_MODEL_NAME):
        super().__init__(model_name)
        self.agent_name = "Auditor_Agent"

    def analyze(self, file_path: str):
        """
        Analyzes the code using Pylint and an LLM to produce a refactoring plan.
        """
        code_content = read_file(file_path)
        pylint_results = run_pylint(file_path) 
        
        system_prompt = """
### Role and Identity
You are the Auditor Agent, a highly skilled Python software engineer and code quality expert specialized in static analysis and refactoring planning. You are part of "The Refactoring Swarm", a multi-agent system that autonomously refactors messy, buggy, undocumented, and untested Python code into clean, functional, well-documented, and fully tested code.

Your sole responsibility is to thoroughly analyze the codebase, identify all issues, and produce a precise, actionable refactoring plan. You do NOT modify any code yourself — that is the Fixer's job.

### Context
- The input is a directory containing one or more Python files that are poorly written: they may contain bugs, code smells, style violations, missing docstrings/type hints, duplicated code, poor structure, and usually NO unit tests.
- The overall goal is to produce refactored code that:
  - Passes all unit tests (new tests must be created if none exist).
  - Achieves a significantly higher Pylint score.
  - Is clean, readable, well-documented, and follows Python best practices (PEP 8, PEP 257, etc.).
- You have access to tools: read_file, list_files, run_pylint, and any other tools provided by the Toolsmith.
- After you output your plan, the Fixer will implement it file by file, then the Judge will run pytest. Failures may loop back for further fixes, but your plan must be comprehensive enough to succeed in as few iterations as possible.

### Core Guidelines
- Be thorough and objective. Base every finding on actual evidence from the code and tool outputs (especially Pylint).
- Prioritize issues that most impact functionality, testability, maintainability, and Pylint score.
- Always reason step-by-step before producing the final plan.
- Never hallucinate issues or files that do not exist.
- Never write or suggest code changes directly in your response unless explicitly requested in a tool format.
- Write concise but complete descriptions — the Fixer must be able to act without ambiguity.
- Security constraint: You may only work inside the sandbox directory. Never reference or suggest paths outside it.

### Task Steps (Always Follow This Process)
1. List all Python files in the target directory using the appropriate tool.
2. Read the content of each Python file.
3. Run Pylint on each file (or the whole project if supported) and collect the full report.
4. Perform your own expert analysis for issues that Pylint might miss (e.g., logical bugs, missing tests, poor architecture, security issues, performance problems).
5. Categorize all identified issues.
6. Create a prioritized refactoring plan.

### Required Issue Categories
For each file, identify issues in these categories (include only relevant ones):
- Critical Bugs: Errors that would cause runtime failures or incorrect behavior.
- Code Smells / Refactoring Opportunities: Duplication, long functions, poor naming, complex conditionals, etc.
- Style & Convention Violations: PEP 8 issues not caught or emphasized by Pylint.
- Documentation: Missing/incomplete docstrings, type hints, module/class/function comments.
- Testing: Absence of tests, or suggestions for key test cases needed (specify functions/classes to test and what to cover).
- Security / Best Practices: Unsafe functions, hardcoded secrets, poor error handling, etc.
- Performance: Inefficient algorithms or patterns.



This structured plan will be passed directly to the Fixer. Make it complete and clear to minimize iterations.
        """
        
        # Optimize Pylint output to save tokens
        issues = pylint_results.get('issues', [])
        if issues and isinstance(issues, list):
            # Sort by severity/importance if possible, or just take first N
            # Limit to top 15 issues to save context
            limited_issues = issues[:15]
            
            pylint_summary = f"Total issues: {len(issues)}. Showing top {len(limited_issues)}:\n"
            for issue in limited_issues:
                # Format: line:col [type] message (symbol)
                pylint_summary += f"Line {issue.get('line')}:{issue.get('column')} [{issue.get('type')}] {issue.get('message')} ({issue.get('symbol')})\n"
                
            if len(issues) > 15:
                pylint_summary += f"... and {len(issues) - 15} more issues."
        else:
            # Fallback to truncated raw output if structure is missing
            raw_output = pylint_results.get('output', '')
            pylint_summary = raw_output[:2000] + "\n...(truncated)" if len(raw_output) > 2000 else raw_output

        # Escape curly braces in dynamic content to prevent LangChain template variable interpolation
        escaped_code = code_content.replace("{", "{{").replace("}", "}}")
        escaped_pylint = pylint_summary.replace("{", "{{").replace("}", "}}")
        
        user_prompt = f"""
        CODE TO ANALYZE ({os.path.basename(file_path)}):
        ```python
        {escaped_code}
        ```
        
        PYLINT OUPUT:
        {escaped_pylint}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        chain = prompt | self.llm
        
        # Invoke LLM
        response = self.invoke_with_delay(chain, {})
        refactoring_plan = response.content
        
        # LOGGING (MANDATORY)
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.ANALYSIS,
            details={
                "file_analyzed": os.path.basename(file_path),
                "input_prompt": system_prompt + "\n" + user_prompt,
                "output_response": refactoring_plan,
                "pylint_score": pylint_results['score']
            },
            status="SUCCESS"
        )
        
        return {
            "plan": refactoring_plan,
            "pylint_score": pylint_results['score'],
            "original_code": code_content
        }
