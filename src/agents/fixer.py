
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.logger import log_experiment, ActionType
from src.tools.files import write_file
from src.agents.base import BaseAgent
from src.config import DEFAULT_MODEL_NAME
import os

class FixerAgent(BaseAgent):
    def __init__(self, model_name=DEFAULT_MODEL_NAME): 
        super().__init__(model_name)
        self.agent_name = "Fixer_Agent"

    def _clean_code_output(self, code: str) -> str:
        """Remove markdown code blocks if present."""
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    def _generate_tests(self, source_code: str, filename: str) -> str:
        """Generate pytest test file for the given source code."""
        
        system_prompt = """You are a Python Test Engineer.
        Your task is to write comprehensive pytest tests for the provided Python code.
        
        Rules:
        1. Return ONLY the complete, valid Python test code.
        2. Do NOT include markdown backticks (e.g. ```python) at the start or end.
        3. Import the module being tested at the top (e.g., `from app import Calculator, calculate_area`).
        4. Include ALL necessary imports (pytest, math, etc.).
        5. Do NOT use the `mocker` fixture; use `unittest.mock.patch` or `unittest.mock.MagicMock` instead.
        6. Only use standard pytest features - no external plugins.
        7. Test all functions and class methods.
        8. Include edge cases (e.g., division by zero, negative numbers).
        9. Use descriptive test function names starting with `test_`.
        """
        
        escaped_code = source_code.replace("{", "{{").replace("}", "}}")
        module_name = filename.replace(".py", "")
        
        user_message = f"""
        SOURCE CODE TO TEST ({filename}):
        ```python
        {escaped_code}
        ```
        
        Generate a complete pytest test file that imports from `{module_name}` and tests all functions and classes.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_message)
        ])
        
        chain = prompt | self.llm
        response = self.invoke_with_delay(chain, {})
        test_code = self._clean_code_output(response.content)
        
        return test_code

    def fix(self, file_path: str, code_content: str, plan: str, error_context: str = None, iteration: int = None):
        """
        Applies fixes to the code based on the implementation plan and optional error context.
        Also generates a test file for the fixed code.
        """
        
        system_prompt = """You are a Python Expert Developer (The Fixer).
        Your task is to rewrite the provided Python code to address a refactoring plan and fix bugs.
        
        Rules:
        1. Return ONLY the complete, valid Python code.
        2. Do NOT include markdown backticks (e.g. ```python) at the start or end.
        3. Ensure the code is complete and runnable.
        4. Strictly follow the plan provided.
        5. For test files: include ALL necessary imports at the top (e.g., `import math`, `import pytest`).
        6. Do NOT use the `mocker` fixture; use `unittest.mock.patch` or `unittest.mock.MagicMock` instead.
        7. Only use standard pytest features - no external plugins like pytest-mock.
        """
        
        # Escape curly braces in dynamic content to prevent LangChain template variable interpolation
        escaped_code = code_content.replace("{", "{{").replace("}", "}}")
        escaped_plan = plan.replace("{", "{{").replace("}", "}}")
        
        user_message = f"""
        ORIGINAL CODE:
        ```python
        {escaped_code}
        ```
        
        REFACTORING PLAN:
        {escaped_plan}
        """
        
        if error_context:
            escaped_error = error_context.replace("{", "{{").replace("}", "}}")
            user_message += f"\n\nPREVIOUS ERROR CONTEXT (Fix these issues specifically):\n{escaped_error}"
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_message)
        ])
        
        chain = prompt | self.llm
        
        response = self.invoke_with_delay(chain, {})
        fixed_code = self._clean_code_output(response.content)
        
        # Apply the fix to source file
        write_file(file_path, fixed_code)
        
        # Generate and write test file
        filename = os.path.basename(file_path)
        test_filename = f"test_{filename}"
        test_file_path = os.path.join(os.path.dirname(file_path), test_filename)
        
        # Only generate tests if they don't exist or if this is the first iteration
        if not os.path.exists(test_file_path):
            test_code = self._generate_tests(fixed_code, filename)
            write_file(test_file_path, test_code)
            
            # Log test generation
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.GENERATION,
                details={
                    "file_generated": test_filename,
                    "input_prompt": f"Generate tests for {filename}",
                    "output_response": test_code,
                    "source_file": filename
                },
                status="SUCCESS",
                iteration=iteration
            )
        
        # LOGGING (MANDATORY)
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.FIX,
            details={
                "file_fixed": os.path.basename(file_path),
                "input_prompt": system_prompt + "\n" + user_message,
                "output_response": fixed_code,
                "plan_followed": plan
            },
            status="SUCCESS",
            iteration=iteration
        )
        
        return fixed_code
