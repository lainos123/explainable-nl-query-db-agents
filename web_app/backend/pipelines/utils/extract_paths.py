import os, sys, json

from django.conf import settings
from pathlib import Path

project_root = settings.BASE_DIR
data_dir = project_root / "data" / "processed"
print(data_dir)



# Function to extract SQL file paths from the data folder
def extract_sql_file_paths(path: str, indent: int = 4, save_json: bool = False):
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
    if save_json:
        with open(os.path.join(SCHEMA_DIR, "sql_file_paths.json"), "w") as f:
            f.write(json.dumps(sql_file_paths, indent=indent, ensure_ascii=False))

    return json.dumps(sql_file_paths, indent=indent, ensure_ascii=False)