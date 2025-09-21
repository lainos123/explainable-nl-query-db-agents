# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 2. Subdirectories
DATA_PATH = PROJECT_ROOT / "data"
SCHEMA_OUTPUT_DIR = DATA_PATH / "processed"
MODELS_PATH = PROJECT_ROOT / "models"
EMBEDDINGS_FOLDER = SCHEMA_OUTPUT_DIR / "spider_schemas_embeddings"

# 3. Files
SQL_DATA_PATH = DATA_PATH / "spider_data" / "train_spider.json"
SQL_TESTING_PATH = DATA_PATH / "test" / "spider_query_answers.json"
SCHEMA_PATH = DATA_PATH / "spider_data" / "tables.json"
SCHEMA_PROCESSED_FILE = SCHEMA_OUTPUT_DIR / "spider_schemas_processed.jsonl"
COMBINED_SCHEMA_FILE = SCHEMA_OUTPUT_DIR / "combined_schema.json"
PROCESSED_SCHEMA_AI_FRIENDLY = SCHEMA_OUTPUT_DIR / "combined_schema.json"  # not used
SQL_FILE_PATHS_FILE = SCHEMA_OUTPUT_DIR / "sql_file_paths.json"
DB_NAMES_FILE = SCHEMA_OUTPUT_DIR / "db_names.json"

# 4. Environment variables
load_dotenv(PROJECT_ROOT / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")
