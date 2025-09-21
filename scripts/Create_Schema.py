"""
Schema Creation Utilities

Creates AI-agent friendly database schemas from SQLite files in the Spider dataset.
Extracts table structures, columns, primary keys, and foreign keys.

Output Files (to data/processed/):
- combined_schema.json: Main AI-agent friendly schema with metadata
- sql_file_paths.json: Database name to file path mapping
- db_names.json: Database names structure
- db_names_test.json: Simplified table/column mapping for testing
- schema_{db_name}.json: Individual database schemas (optional)

Usage:
    from Create_Schema import create_combined_schema, extract_sql_file_paths
    sql_paths = extract_sql_file_paths(save_json=True)
    schema = create_combined_schema(sql_paths, save_json=True)
"""

import os
import json
import sys
from pathlib import Path
from SQL_Connector import SQLite_Connector
from tqdm import tqdm

# Import project config
sys.path.append(str(Path(__file__).parent.parent))
from src.config import (
    DATA_PATH_SPIDER,
    SCHEMA_OUTPUT_DIR,
    COMBINED_SCHEMA_FILE,
    SQL_FILE_PATHS_FILE,
    DB_NAMES_FILE,
)

# Ensure output directory exists
SCHEMA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Function to extract SQL file paths from the data folder
def extract_sql_file_paths(indent: int = 4, save_json: bool = False):
    base_path = Path(__file__).parent.parent
    data_folder = DATA_PATH_SPIDER / "database"

    if not data_folder.exists():
        raise ValueError("Data folder is not available")
    elif not any(data_folder.iterdir()):
        raise ValueError("Data folder is empty.")

    sql_file_paths = {}
    for db_folder in data_folder.iterdir():
        if db_folder.is_dir():
            for sql_file in db_folder.glob("*.sqlite"):
                rel_path = sql_file.relative_to(base_path)
                rel_path_str = str(rel_path).replace(os.sep, "/")
                db_name = sql_file.stem
                sql_file_paths[db_name] = rel_path_str

    if not sql_file_paths:
        sys.exit("Error: No SQL files found in the data folder.")

    if save_json:
        with open(SQL_FILE_PATHS_FILE, "w") as f:
            f.write(json.dumps(sql_file_paths, indent=indent, ensure_ascii=False))
        print(f"SQL file paths saved to {SQL_FILE_PATHS_FILE}")

    return json.dumps(sql_file_paths, indent=indent, ensure_ascii=False)


# Function to extract schema from SQLite files
def schema_extractor(sql_file_paths: str, db_name: str, save_json: bool = False):
    connector = SQLite_Connector(sql_file_paths)
    connector.connect(db_name, verbose=True)
    table_names = connector.execute_queries(
        ["SELECT name FROM sqlite_master WHERE type='table';"]
    )
    table_names = json.loads(table_names)

    schema = {
        "database_name": db_name,  # Include database name in schema
        "tables": {},
    }
    for table_dict in table_names[0]:
        table_name = table_dict["name"]
        cols_raw = connector.execute_queries([f"PRAGMA table_info({table_name});"])
        cols_raw = json.loads(cols_raw)[0]
        columns = []
        pk_cols = []
        for col in cols_raw:
            columns.append(col["name"])
            if col["pk"]:
                pk_cols.append(col["name"])

        fks_raw = connector.execute_queries([f"PRAGMA foreign_key_list({table_name});"])
        fks_raw = json.loads(fks_raw)[0] if fks_raw else []
        fk_list = []
        for fk in fks_raw:
            fk_list.append(
                {
                    "from_column": fk["from"],
                    "ref_table": fk["table"],
                    "ref_column": fk["to"],
                }
            )

        schema["tables"][table_name] = {
            "columns": columns,
            "primary_key": pk_cols,
            "foreign_keys": fk_list,
        }

        if save_json:
            schema_file = SCHEMA_OUTPUT_DIR / f"schema_{db_name}.json"
            with open(schema_file, "w") as f:
                f.write(json.dumps(schema, indent=4, ensure_ascii=False))
            print(f"Schema for {db_name} saved to {schema_file}")

    return json.dumps(schema, indent=4, ensure_ascii=False)


# Function to create db_names.json from sql_file_paths.json
def create_names_json(sql_file_paths: str, save_json: bool = False):
    sql_file_paths = json.loads(sql_file_paths)
    db_names = {db_name: {} for db_name in tqdm(sql_file_paths.keys())}
    print("Database names extracted.")
    if save_json:
        with open(DB_NAMES_FILE, "w") as f:
            json.dump(db_names, f, indent=4, ensure_ascii=False)
        print(f"Database names saved to {DB_NAMES_FILE}")

    return json.dumps(db_names, indent=4, ensure_ascii=False)


# Function to create combined schema from SQL file paths (AI-agent friendly version)
def create_combined_schema(sql_file_paths, save_json: bool = False):
    # Add database's name into a list
    database_list = []
    for db_name in json.loads(sql_file_paths):
        database_list.append(db_name)

    # AI-agent friendly combined schema with detailed structure and instructions
    combined_schema = {
        "database_list": database_list,  # List of all database names
        "json_structure": (
            # Structure of the combined schema JSON
            "{\n"
            "  'database_list': List[str],  # List of database names\n"
            "  'json_structure': str,       # Description of this JSON structure\n"
            "  'schema_data_instruction': str,  # Instructions for using the schema\n"
            "  'schema': {\n"
            "    <database_name>: {\n"
            "      'database_name': str,    # Name of the database\n"
            "      'tables': {\n"
            "        <table_name>: {\n"
            "          'columns': List[str],      # List of column names in the table\n"
            "          'primary_key': List[str],  # List of primary key columns\n"
            "          'foreign_keys': [          # List of foreign key relationships\n"
            "            {\n"
            "              'from_column': str,    # Column in this table\n"
            "              'ref_table': str,      # Referenced table\n"
            "              'ref_column': str      # Referenced column\n"
            "            }\n"
            "          ]\n"
            "        }\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "}"
        ),
        "schema_data_instruction": (
            # Instructions for using the combined schema JSON
            "- 'database_list': List of all database names in the schema.\n"
            "- 'json_structure': Description of the JSON structure.\n"
            "- 'schema_data_instruction': How to use this schema JSON.\n"
            "- 'schema': Dictionary containing schema details for each database.\n"
            "  - Each <database_name> contains:\n"
            "    - 'database_name': Name of the database.\n"
            "    - 'tables': Dictionary of tables in the database.\n"
            "      - Each <table_name> contains:\n"
            "        - 'columns': List of column names.\n"
            "        - 'primary_key': List of primary key columns.\n"
            "        - 'foreign_keys': List of foreign key relationships, each with:\n"
            "          - 'from_column': Column in this table.\n"
            "          - 'ref_table': Referenced table.\n"
            "          - 'ref_column': Referenced column.\n"
            "Instructions: Use 'database_list' to enumerate databases. For each database, access tables and their columns, primary keys, and foreign keys as needed."
        ),
        "schema": {},
    }

    # Extract schema for each database
    json_sql = json.loads(sql_file_paths)
    for db_name in tqdm(json_sql):
        schema = schema_extractor(sql_file_paths, db_name=db_name)
        combined_schema["schema"][db_name] = json.loads(schema)

    if save_json:
        with open(COMBINED_SCHEMA_FILE, "w") as f:
            json.dump(combined_schema, f, indent=4)
        print(f"Combined schema saved to {COMBINED_SCHEMA_FILE}")

    return json.dumps(combined_schema, indent=4, ensure_ascii=False)


# Function to extract schema from a JSON file based on database name
def schema_from_json_file(path: str, db_name: str, save_json=False):
    with open(path, "r") as f:
        data = json.load(f)
        schema = data.get("schema").get(db_name)
        if save_json:
            schema_file = SCHEMA_OUTPUT_DIR / f"schema_{db_name}.json"
            with open(schema_file, "w") as f:
                json.dump(schema, f, indent=4)
        return schema


# Wrapper for schema_from_json_file for input as JSON -> list of db names
def schema_from_json_names(db_names: str, path: str, save_json: bool = False):
    # str->Json conversion
    try:
        db_names = json.loads(db_names).get("db_names", [])
    except:
        db_names = db_names.get("db_names", [])
    schemas = {}
    for db_name in db_names:
        schema = schema_from_json_file(path, db_name=db_name, save_json=False)
        schemas[db_name] = schema
    if save_json:
        temp_schemas_file = SCHEMA_OUTPUT_DIR / "temp_schemas.json"
        with open(temp_schemas_file, "w") as f:
            json.dump(schemas, f, indent=4, ensure_ascii=False)
    return json.dumps(schemas, indent=4, ensure_ascii=False)


def create_names_json_test(combined_schema: str, save_json: bool = False):
    data = json.loads(combined_schema)
    result = {}
    for db, schema in data.get("schema", {}).items():
        result[db] = {}
        for table, info in schema.get("tables", {}).items():
            result[db][table] = info.get("columns", [])
    if save_json:
        db_names_test_file = SCHEMA_OUTPUT_DIR / "db_names_test.json"
        with open(db_names_test_file, "w") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"Database names test file saved to {db_names_test_file}")
    return json.dumps(result, indent=4, ensure_ascii=False)
