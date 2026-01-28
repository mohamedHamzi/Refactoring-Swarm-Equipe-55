import time
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import DEFAULT_MODEL_NAME

class BaseAgent:
    def __init__(self, model_name=DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0, 
            convert_system_message_to_human=True
        )

    def invoke_with_delay(self, chain, input_data):
        """
        Invokes the chain with a hard delay to comply with rate limits.
        Enforces a 4-second delay before calling the API.
        """
        time.sleep(10)  # Hard delay to stay under 15 RPM (1 request per 5s for safety margin)
        return chain.invoke(input_data) 
