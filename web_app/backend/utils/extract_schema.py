import os
import json
import sys
from django.conf import settings
from .sql_connector import SQLite_connector

MEDIA_ROOT = settings.MEDIA_ROOT
SCHEMA_DIR = settings.SCHEMA_DIR

# Function to extract schema from SQLite files
def schema_extractor(sql_file_paths: str, db_name: str, save_json: bool = False):
    connector = SQLite_connector(sql_file_paths)
    connector.connect(db_name, verbose=True)
    table_names = connector.execute_queries(["SELECT name FROM sqlite_master WHERE type='table';"])
    table_names = json.loads(table_names)

    schema = {
        "tables": {}
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
            fk_list.append({
                "from_column": fk["from"],
                "ref_table": fk["table"],
                "ref_column": fk["to"]
            })

        schema["tables"][table_name] = {
            "columns": columns,
            "primary_key": pk_cols,
            "foreign_keys": fk_list
        }

        if save_json:
            with open(os.path.join(SCHEMA_DIR, f"schema_{db_name}.json"), "w") as f:
                f.write(json.dumps(schema, indent=4, ensure_ascii=False))

    return json.dumps(schema, indent=4, ensure_ascii=False)

# Function to create db_names.json from sql_file_paths.json
def create_names_json(sql_file_paths: str, save_json: bool = False):
    sql_file_paths = json.loads(sql_file_paths)
    db_names = {db_name: {} for db_name in sql_file_paths.keys()}
    print("Database names extracted to db_names.json.")
    if save_json:
        with open(os.path.join(SCHEMA_DIR, "db_names.json"), "w") as f:
            json.dump(db_names, f, indent=4, ensure_ascii=False)

    return json.dumps(db_names, indent=4, ensure_ascii=False)

# Function to create combined schema from SQL file paths
def create_combined_schema(sql_file_paths, save_json: bool = False):
    combined_schema = {}
    json_sql = json.loads(sql_file_paths)
    for db_name in json_sql:
        schema = schema_extractor(sql_file_paths, db_name=db_name)
        combined_schema[db_name] = json.loads(schema)
    if save_json:
        with open(os.path.join(SCHEMA_DIR, "combined_schema.json"), "w") as f:
            json.dump(combined_schema, f, indent=4)
    print("Combined schema saved to combined_schema.json")
    return json.dumps(combined_schema, indent=4, ensure_ascii=False)

# Function to extract schema from a JSON file based on database name
def schema_from_json_file(path: str, db_name: str, save_json=False):
    with open(path, "r") as f:
        data = json.load(f)
        schema = data.get(db_name)
        if save_json:
            with open(os.path.join(SCHEMA_DIR, f"schema_{db_name}.json"), "w") as f:
                json.dump(schema, f, indent=4)
        return schema

# Wapper for schema_from_json_file for input as JSON -> list of db names
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
        with open(os.path.join(SCHEMA_DIR, "temp_schemas.json"), "w") as f:
            json.dump(schemas, f, indent=4, ensure_ascii=False)
    return json.dumps(schemas, indent=4, ensure_ascii=False)

# Function to create a simplified names JSON (testing)
def create_names_json_test(combined_schema: str, save_json: bool = False):
    data = json.loads(combined_schema)
    result = {}
    for db, schema in data.items():
        result[db] = {}
        for table, info in schema.get("tables", {}).items():
            result[db][table] = info.get("columns", [])
    if save_json:
        with open(os.path.join(SCHEMA_DIR, "db_names_test.json"), "w") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
    return json.dumps(result, indent=4, ensure_ascii=False)


if not os.path.exists(SCHEMA_DIR):
    os.makedirs(SCHEMA_DIR)
def extract_schema(json_data: str, db_name: str, save_json: bool = False):
    json_data = json.loads(json_data)
    schema = json_data.get(db_name)
    if save_json:
        with open(os.path.join(SCHEMA_DIR, f"schema_{db_name}.json"), "w") as f:
            json.dump(schema, f, indent=4, ensure_ascii=False)
    return json.dumps(schema, indent=4, ensure_ascii=False)


def run(request, media_path: str):
    """
    Django endpoint function for schema extraction
    Expected request data format:
    {
        "json_data": "JSON string containing schema data",
        "db_name": "database name to extract schema for"
    }
    """
    try:
        # Get data from request
        data = request.data
        
        # Extract required parameters
        json_data = data.get('json_data', '{}')
        db_name = data.get('db_name', '')
        
        # Validate parameters
        if not db_name:
            return {"error": "db_name is required"}
        
        # Extract schema
        result = extract_schema(json_data, db_name)
        
        # Parse the result to return as dict instead of JSON string
        try:
            parsed_result = json.loads(result)
            return {"success": True, "result": parsed_result}
        except json.JSONDecodeError:
            return {"success": True, "result": result}
            
    except Exception as e:
        return {"error": f"Schema extraction failed: {str(e)}"}
