# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Absolute path to project root - FIXED: Convert to Path object
PROJECT_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env once
load_dotenv(PROJECT_ROOT / ".env")

# Expose variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional: fail fast if required keys are missing
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")
