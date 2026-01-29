import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.logger import log_experiment, ActionType
from src.tools.files import write_file
from src.agents.base import BaseAgent
from src.config import DEFAULT_MODEL_NAME

class FixerAgent(BaseAgent):
    """
    Expert AI agent responsible for autonomous code refactoring and bug fixing.
    Uses LLM-based reasoning to apply specific implementation plans to existing source code.
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        super().__init__(model_name)
        self.agent_name = "Fixer_Agent"
        
    def _sanitize_output(self, raw_code: str) -> str:
        """
        Removes markdown code blocks and extraneous whitespace from the LLM response.
        Ensures the final string is pure, executable Python.
        """
        code = raw_code.strip()
        # Handle various markdown code block variations
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        
        if code.endswith("```"):
            code = code[:-3]
        
        return code.strip()
    
    def fix(self, file_path: str, code_content: str, plan: str, error_context: Optional[str] = None) -> str:
        """
        Analyzes code and applies the refactoring plan using structured prompt engineering.
        """
        
        system_prompt = (
            "You are a Senior Python Expert Developer (The Fixer).\n"
            "Your mission is to rewrite the provided Python code based on a specific plan.\n\n"
            "CRITICAL RULES:\n"
            "1. Output ONLY valid, runnable Python code.\n"
            "2. Never include markdown backticks (```) or conversational text.\n"
            "3. Ensure the code is production-ready and maintains existing functionality unless the plan states otherwise.\n"
            "4. Follow the provided plan exactly."
        )

        # Escaping curly braces to prevent LangChain parsing issues
        escaped_code = code_content.replace("{", "{{").replace("}", "}}")
        escaped_plan = plan.replace("{", "{{").replace("}", "}}")

        user_message = (
            f"TARGET FILE: {os.path.basename(file_path)}\n\n"
            f"### ORIGINAL SOURCE CODE ###\n{escaped_code}\n\n"
            f"### REFACTORING PLAN ###\n{escaped_plan}"
        )

        if error_context:
            escaped_error = error_context.replace("{", "{{").replace("}", "}}")
            user_message += f"\n\n### PREVIOUS ERRORS TO RESOLVE ###\n{escaped_error}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_message)
        ])

        # Execution via LangChain
        chain = prompt | self.llm
        response = self.invoke_with_delay(chain, {})
        
        # Clean and validate the output
        fixed_code = self._sanitize_output(response.content)
        
        return fixed_code