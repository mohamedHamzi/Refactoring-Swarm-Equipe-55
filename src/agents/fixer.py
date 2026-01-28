from src.agents.base import BaseAgent
from src.config import DEFAULT_MODEL_NAME

class FixerAgent(BaseAgent):
    def __init__(self, model_name=DEFAULT_MODEL_NAME): 
        super().__init__(model_name)
        self.agent_name = "Fixer_Agent"

    def fix(self, file_path: str, code_content: str, plan: str, error_context: str = None):
        pass