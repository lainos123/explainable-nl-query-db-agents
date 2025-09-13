"""
Schema Generation Pipeline

Generates complete AI-agent friendly database schemas from SQLite files.
Creates all schema files in data/processed/ directory.

Output Files:
- combined_schema.json: Main schema with AI instructions and metadata
- sql_file_paths.json: Database name to file path mapping  
- db_names.json: Database names structure
- db_names_test.json: Simplified table/column mapping

Usage:
    python3 scripts/Schema_Generation.py
"""

import sys
from pathlib import Path

# Add the scripts directory to the Python path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Now import the modules
import Create_Schema

# Add project root to path for config import
sys.path.append(str(Path(__file__).parent.parent))
from src.config import COMBINED_SCHEMA_FILE, SQL_FILE_PATHS_FILE, DB_NAMES_FILE

print("Starting schema generation...")
print(f"Output directory: {Path(__file__).parent.parent / 'data' / 'processed'}")

# Create path JSON
print("\n1. Extracting SQL file paths...")
sql_file_paths = Create_Schema.extract_sql_file_paths(save_json=True)
print(f"SQL file paths extracted and saved to {SQL_FILE_PATHS_FILE}")

# Create database name JSON
print("\n2. Creating database names JSON...")
Create_Schema.create_names_json(sql_file_paths, save_json=True)
print(f"Database names saved to {DB_NAMES_FILE}")

# Create the combined schema
print("\n3. Creating combined schema...")
combined_schema = Create_Schema.create_combined_schema(sql_file_paths, save_json=True)
print(f"Combined schema saved to {COMBINED_SCHEMA_FILE}")

# Create the schema with tables and columns (TESTING)
print("\n4. Creating test database names...")
Create_Schema.create_names_json_test(combined_schema, save_json=True)

print("\n✅ Schema generation completed successfully!")
print(f"All files saved to: {Path(__file__).parent.parent / 'data' / 'processed'}")
