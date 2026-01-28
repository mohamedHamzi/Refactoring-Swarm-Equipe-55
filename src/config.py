
import os
from dotenv import load_dotenv

load_dotenv()

# Centralized configuration
DEFAULT_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
