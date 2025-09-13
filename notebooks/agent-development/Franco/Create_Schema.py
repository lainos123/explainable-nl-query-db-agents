import os
import json
from SQL_Connector import SQLite_Connector
import tqdm  # Process bar

# This function extracts SQL file paths from the data folder
def extract_sql_file_paths(indent:int = 4, save_json: bool = False):
    base_path = os.path.dirname(os.path.abspath(__file__))

    data_folder = os.path.join(base_path, "data")
    if not os.path.exists(data_folder):
        raise ValueError("Data folder is not available")
    elif not os.listdir(data_folder):
        raise ValueError("Data folder is empty.")

    sql_file_paths = {}
    for root, _, files in os.walk(data_folder):
        for file in files:
            if file.endswith('.sqlite'):
                rel_path = os.path.relpath(os.path.join(root, file), base_path)
                rel_path = rel_path.replace(os.sep, "/")
                sql_file_paths[file.replace(".sqlite", "")] = rel_path

    if save_json:
        with open("sql_file_paths.json", "w") as f:
            f.write(json.dumps(sql_file_paths, indent=indent, ensure_ascii=False))

    return json.dumps(sql_file_paths, indent=indent, ensure_ascii=False)

def schema_extractor(sql_file_paths: str, db_name: str, save_json: bool = False):
    connector = SQLite_Connector(sql_file_paths)
    connector.connect(db_name, verbose=True)
    # Get all table names
    table_names = connector.execute_queries(["SELECT name FROM sqlite_master WHERE type='table';"])
    table_names = json.loads(table_names)

    schema = {
        "database_name": db_name,  # Indicate this is the database name
        "tables": {}               # Indicate this will contain table names as keys
    }
    for table_dict in table_names[0]:
        table_name = table_dict["name"]
        # Columns + PK
        cols_raw = connector.execute_queries([f"PRAGMA table_info({table_name});"])
        cols_raw = json.loads(cols_raw)[0]
        columns = []
        pk_cols = []
        for col in cols_raw:
            columns.append(col["name"])
            if col["pk"]:
                pk_cols.append(col["name"])

        # Foreign keys
        fks_raw = connector.execute_queries([f"PRAGMA foreign_key_list({table_name});"])
        fks_raw = json.loads(fks_raw)[0] if fks_raw else []
        fk_list = []
        for fk in fks_raw:
            fk_list.append({
                "from_column": fk["from"],
                "ref_table": fk["table"],
                "ref_column": fk["to"]
            })

        schema["tables"][table_name] = {  # Table name as key under "tables"
            "columns": columns,
            "primary_key": pk_cols,
            "foreign_keys": fk_list
        }

        if save_json:
            with open(f"schema_{db_name}.json", "w") as f:
                f.write(json.dumps(schema, indent=4, ensure_ascii=False))

    return json.dumps(schema, indent=4, ensure_ascii=False)

# Create the combined schema
def create_combined_schema(sql_file_paths, save_json: bool = False):
    # Add database's name into a list
    database_list = []
    for db_name in json.loads(sql_file_paths):
        database_list.append(db_name)

    # Experimental combined schema with detailed structure and instructions for AI agents
    # Call it out to use
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
        "schema": {}
    }
    
    # Scan from all tables and inject into 1 JSON schema
    # Load the JSON to python dictionary
    json_sql = json.loads(sql_file_paths)
    # Extract schema for each database
    for db_name in tqdm.tqdm(json_sql):
        schema = schema_extractor(sql_file_paths, db_name=db_name)
        combined_schema["schema"][db_name] = json.loads(schema)
    if save_json:
        with open("combined_schema.json", "w") as f:
            json.dump(combined_schema, f, indent=4)
    print("Combined schema saved to combined_schema.json")

# Extract schema by database name from local JSON files
def schema_from_json_file(path: str, db_name: str, save_json=False):
    with open(path, "r") as f:
        data = json.load(f)
        schema = data.get("schema").get(db_name)
        if save_json:
            with open(f"schema_{db_name}.json", "w") as f:
                json.dump(schema, f, indent=4)
        return schema
    
if __name__ == "__main__":
    # Generate combined schema
    schema_from_json_file("combined_schema.json", db_name="cinema", save_json=True)
