import time
import sys
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted

from src.config import DEFAULT_MODEL_NAME

# Rate limiting constants
DELAY_BETWEEN_CALLS = 5  # seconds between API calls
STATE_SAVE_FILE = "logs/checkpoint_state.json"

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
        Invokes the chain with rate limiting and circuit breaker for quota errors.
        """
        time.sleep(DELAY_BETWEEN_CALLS)
        
        try:
            return chain.invoke(input_data)
        except ResourceExhausted as e:
            print("\n" + "="*60)
            print("⚠️  RATE LIMIT REACHED (429 ResourceExhausted)")
            print("="*60)
            print(f"Error: {e}")
            print("\nThe Gemini API quota has been exhausted.")
            print("Options:")
            print("  1. Wait 24 hours for quota reset (Free Tier)")
            print("  2. Upgrade to a paid tier")
            print("  3. Switch to a different API key")
            print("="*60 + "\n")
            
            # Save state for resumption
            try:
                import os
                os.makedirs("logs", exist_ok=True)
                with open(STATE_SAVE_FILE, "w") as f:
                    json.dump({"error": "ResourceExhausted", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}, f)
                print(f"📁 State saved to {STATE_SAVE_FILE}")
            except Exception as save_err:
                print(f"Could not save state: {save_err}")
            
            sys.exit(1)
        except Exception as e:
            # Re-raise other exceptions
            raise
