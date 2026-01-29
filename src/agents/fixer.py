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