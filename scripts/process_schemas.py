#!/usr/bin/env python3
"""
process_schemas.py

Process the Spider dataset schemas and save them in a format suitable for embedding.

This script:
1. Loads the original tables.json schema file
2. Extracts essential schema information (db_id, table_names, column_names)
3. Reshapes the data with descriptive headings for LLM compatibility
4. Formats each table as a separate JSON entry
5. Saves the processed schemas to a JSONL file

Usage:
    python3 -m scripts.process_schemas
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Import project config
from src.config import (
    PROJECT_ROOT,
    SCHEMA_OUTPUT_DIR,
    SCHEMA_PATH,
    SCHEMA_PROCESSED_FILE,
)

# Add project root to Python path
sys.path.append(str(PROJECT_ROOT))


def load_schemas(path: Path) -> List[Dict[str, Any]]:
    """
    Load the schema file from the given path and return a list of schema objects.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            schemas_json = json.load(f)
        print(f"Loaded {len(schemas_json)} schema entries from file '{path}'.")
        return schemas_json
    except FileNotFoundError:
        print(f"Error: Schema file '{path}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file '{path}': {e}")
        return []


def extract_essential_schema(tables_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract only essential schema information from tables.json"""
    essential_data = []
    for entry in tables_data:
        simplified_entry = {
            "database_name": entry.get("db_id", "undefined"),
            "table_names": entry.get("table_names", []),
            "column_names": entry.get("column_names", []),
        }
        essential_data.append(simplified_entry)
    return essential_data


def reshape_with_headings(
    essential_schemas: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Add descriptive headings to make schema more LLM-friendly"""
    out = {}
    for db in essential_schemas:
        db_name = db.get("database_name", "unknown")
        table_names = list(db.get("table_names", []))
        col_specs = list(db.get("column_names", []))
        tables = []

        for idx, table_name in enumerate(table_names):
            cols = []
            for pair in col_specs:
                if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                    continue
                t_idx, col = pair
                try:
                    t_idx = int(t_idx)
                except (ValueError, TypeError):
                    continue
                if t_idx != idx:
                    continue
                if col is None or str(col).strip() == "*" or t_idx < 0:
                    continue
                cols.append(str(col))

            tables.append(
                {
                    "table_name": table_name,
                    "columns": cols,
                }
            )

        out[db_name] = {"database_name": db_name, "tables": tables}
    return out


def format_schema_jsonish(
    reshaped_essential_schemas: Dict[str, Dict[str, Any]],
) -> List[str]:
    """Convert schema to JSON format for embedding - one JSON per table"""
    lines = []
    for _, db in reshaped_essential_schemas.items():
        db_name = db.get("database_name", "unknown")
        for t in db.get("tables", []):
            obj = {
                "database": db_name,
                "table": t.get("table_name", "unknown"),
                "columns": t.get("columns", []),
            }
            lines.append(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
    return lines


def save_processed_schema(
    reshaped_essential_schemas: Dict[str, Dict[str, Any]], output_file: Path
) -> None:
    """Save formatted schema into a JSONL file (one table per line)."""
    lines = format_schema_jsonish(reshaped_essential_schemas)
    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"Saved {len(lines)} schema entries to {output_file}")


def main():
    """Main processing pipeline"""
    print("=" * 60)
    print("PROCESSING SPIDER SCHEMAS")
    print("=" * 60)

    # Step 1: Load schemas
    print("\n1. Loading schemas...")
    schemas_json = load_schemas(SCHEMA_PATH)

    if not schemas_json:
        print("Failed to load schemas. Exiting.")
        return

    # Step 2: Extract essential schema
    print("\n2. Extracting essential schema...")
    essential_schemas = extract_essential_schema(schemas_json)
    print(f"Extracted data for {len(essential_schemas)} database schemas")

    # Step 3: Reshape with headings
    print("\n3. Reshaping with descriptive headings...")
    reshaped_schemas = reshape_with_headings(essential_schemas)
    print(f"Reshaped {len(reshaped_schemas)} databases with descriptive headings")

    # Step 4: Create output directory
    print("\n4. Creating output directory...")
    SCHEMA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 5: Save processed schema
    print("\n5. Saving processed schema...")
    save_processed_schema(reshaped_schemas, SCHEMA_PROCESSED_FILE)

    print("\n" + "=" * 60)
    print("SCHEMA PROCESSING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
