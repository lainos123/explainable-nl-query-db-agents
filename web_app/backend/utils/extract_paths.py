import os, sys, json
from django.conf import settings
from pathlib import Path

DATA_DIR = settings.MEDIA_ROOT / "data"
SCHEMA_DIR = settings.MEDIA_ROOT / "schema"

# Function to extract SQL file paths from the data folder
def extract_paths(path: str, indent: int = 4, save_json: bool = False):
    # Extract media folder path
    path_folder = path
    if path_folder is None or path_folder == "":
        print("No path provided!" )
    if not os.path.exists(path_folder):
        raise ValueError("Data directory is not available")
    elif not os.listdir(path_folder):
        raise ValueError("Data directory is empty.")

    # Extract SQL file paths
    sql_file_paths = {}
    for root, _, files in os.walk(path_folder):
        for file in files:
            if file.endswith('.sqlite'):
                rel_path = os.path.relpath(os.path.join(root, file), path_folder)
                rel_path = rel_path.replace(os.sep, "/")
                sql_file_paths[file.replace(".sqlite", "")] = rel_path

    if sql_file_paths == {}:
        sys.exit("Error: No SQL files found in the data folder.")

    # Save to MEDIA_ROOT/schema
    with open(os.path.join(SCHEMA_DIR, "sql_file_paths.json"), "w") as f:
        f.write(json.dumps(sql_file_paths, indent=indent, ensure_ascii=False))

    return {"status": 200, "data": sql_file_paths}


def run(request, media_path: str):
    """
    Django endpoint function for path extraction
    Expected request data format:
    {
        "path": "path to data folder" (optional, uses media_path if not provided)
    }
    """
    try:
        # Get data from request
        data = request.data

        # Extract path parameter, default to media_path
        path = data.get('path', media_path)

        # Extract paths
        result = extract_paths(path)

        # Parse the result to return as dict instead of JSON string
        try:
            parsed_result = json.loads(result)
            return {"success": True, "result": parsed_result}
        except json.JSONDecodeError:
            return {"success": True, "result": result}

    except Exception as e:
        return {"error": f"Path extraction failed: {str(e)}"}