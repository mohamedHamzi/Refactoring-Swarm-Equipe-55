
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

    def fix(self, file_path: str, code_content: str, plan: str, error_context: str = None):
        """
        Applies fixes to the code based on the implementation plan and optional error context.
        """
        
        system_prompt = """You are a Python Expert Developer (The Fixer).
        Your task is to rewrite the provided Python code to address a refactoring plan and fix bugs.
        
        Rules:
        1. Return ONLY the complete, valid Python code.
        2. Do NOT include markdown backticks (e.g. ```python) at the start or end.
        3. Ensure the code is complete and runnable.
        4. strictly follow the plan provided.
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
        fixed_code = response.content.strip()
        
        # Clean up markdown code blocks if the LLM adds them despite instructions
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code[9:]
        if fixed_code.startswith("```"):
            fixed_code = fixed_code[3:]
        if fixed_code.endswith("```"):
            fixed_code = fixed_code[:-3]
            
        fixed_code = fixed_code.strip()
        
        # Apply the fix
        write_file(file_path, fixed_code)
        
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
            status="SUCCESS"
        )
        
        return fixed_code
