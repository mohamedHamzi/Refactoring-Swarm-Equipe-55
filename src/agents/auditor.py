from src.agents.base import BaseAgent
from src.config import DEFAULT_MODEL_NAME


class AuditorAgent(BaseAgent):
    def __init__(self, model_name=DEFAULT_MODEL_NAME):
        super().__init__(model_name)
        self.agent_name = "Auditor_Agent"
    def analyze(self, file_path: str):
        pass