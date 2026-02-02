
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
        
        system_prompt = """You are a Python Code Auditor. Your goal is to analyze code and provide a refactoring plan.
        You will be given the code and the output of a static analysis tool (pylint).
        
        Your output must be a clear, step-by-step plan for a developer to fix the issues.
        Focus on:
        1. Fixing errors and bugs reported by pylint.
        2. Improving code style and following PEP 8.
        3. Adding missing docstrings and type hints.
        4. Removing unused code.
        
        Return ONLY the plan as a numbered list.
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
