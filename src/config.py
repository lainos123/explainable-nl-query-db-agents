# src/config.py
import os
from dotenv import load_dotenv

# Absolute path to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load .env once
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Expose variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional: fail fast if required keys are missing
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")