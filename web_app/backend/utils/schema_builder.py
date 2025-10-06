import os
import json
import sqlite3
from typing import Dict, Tuple, Union
from django.conf import settings


def get_schema_dir(user_id: int) -> str:
    """
    Build per-user schema directory under MEDIA_ROOT/<user_id>/schema
    """
    schema_dir = os.path.join(settings.MEDIA_ROOT, str(user_id), "schema")
    os.makedirs(schema_dir, exist_ok=True)
    return schema_dir


def _exec_query(db_path: str, query: str) -> Tuple[Union[list, None], Union[str, None]]:
    """
    Execute a SQLite query against a specific database file path.
    Returns (rows_as_list_of_dicts, error_message)
    """
    if not os.path.isfile(db_path):
        return None, f"Database file not found: {db_path}"

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        if columns:
            result = [dict(zip(columns, row)) for row in rows]
        else:
            result = rows
        return result, None
    except sqlite3.Error as e:
        return None, str(e)
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:
            pass


def schema_extractor(db_key: str, db_path: str):
    """
    Extract schema (tables, columns, PK, FK) for one SQLite database.
    - db_key: logical database key (e.g., stored in Files.database)
    - db_path: absolute path to the .sqlite file
    """
    tables, err = _exec_query(db_path, "SELECT name FROM sqlite_master WHERE type='table';")
    if err:
        return {"error": err, "database": db_key}

    schema = {"tables": {}}
    for table_dict in tables:
        table_name = table_dict["name"] if isinstance(table_dict, dict) else table_dict[0]

        cols_raw, err = _exec_query(db_path, f"PRAGMA table_info({table_name});")
        if err:
            return {"error": err, "database": db_key}
        columns = []
        pk_cols = []
        for col in cols_raw:
            name = col.get("name") if isinstance(col, dict) else col[1]
            pk = col.get("pk") if isinstance(col, dict) else col[5]
            columns.append(name)
            if pk:
                pk_cols.append(name)

        fks_raw, err = _exec_query(db_path, f"PRAGMA foreign_key_list({table_name});")
        if err:
            return {"error": err, "database": db_key}
        fk_list = []
        for fk in fks_raw or []:
            if isinstance(fk, dict):
                fk_list.append({
                    "from_column": fk.get("from"),
                    "ref_table": fk.get("table"),
                    "ref_column": fk.get("to"),
                })
            else:
                # fallback for tuple format
                # PRAGMA foreign_key_list returns: id,seq,table,from,to,on_update,on_delete,match
                fk_list.append({
                    "from_column": fk[3],
                    "ref_table": fk[2],
                    "ref_column": fk[4],
                })

        schema["tables"][table_name] = {
            "columns": columns,
            "primary_key": pk_cols,
            "foreign_keys": fk_list,
        }

    return schema


def build_schema_ab(sql_file_paths: Union[Dict[str, str], str], user_or_dir: Union[int, str]):
    """
    Build schema for Agent A/B (flat JSONL with {db, table, columns}).
    Save as schema_ab.jsonl and wipe old embeddings.
    sql_file_paths: dict or JSON string of { "db_key": "/abs/path/to/db.sqlite" }
    user_or_dir: user_id (int) or explicit schema_dir (str)
    """
    # Parse inputs
    if isinstance(sql_file_paths, str):
        paths = json.loads(sql_file_paths)
    else:
        paths = sql_file_paths

    if isinstance(user_or_dir, str):
        schema_dir = user_or_dir
        os.makedirs(schema_dir, exist_ok=True)
    else:
        schema_dir = get_schema_dir(user_or_dir)

    # reset embeddings folder to avoid stale data
    embeddings_folder = os.path.join(schema_dir, "embeddings")
    if os.path.isdir(embeddings_folder):
        for f in os.listdir(embeddings_folder):
            try:
                os.remove(os.path.join(embeddings_folder, f))
            except Exception:
                pass
        try:
            os.rmdir(embeddings_folder)
        except Exception:
            pass

    lines = []

    for db_key, db_path in paths.items():
        abs_path = os.path.normpath(db_path)
        schema = schema_extractor(db_key, abs_path)
        if "error" in schema:
            return schema
        for table, info in schema.get("tables", {}).items():
            obj = {
                "database": db_key,
                "table": table,
                "columns": info.get("columns", []),
            }
            lines.append(json.dumps(obj, ensure_ascii=False))

    out_path = os.path.join(schema_dir, "schema_ab.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {"file": out_path, "count": len(lines), "embeddings": "reset"}


def build_schema_c(sql_file_paths: Union[Dict[str, str], str], user_or_dir: Union[int, str]):
    """
    Build schema for Agent C (nested JSON {db: {tables: {...}}}).
    Save as schema_c.json
    sql_file_paths: dict or JSON string of { "db_key": "/abs/path/to/db.sqlite" }
    user_or_dir: user_id (int) or explicit schema_dir (str)
    """
    if isinstance(sql_file_paths, str):
        paths = json.loads(sql_file_paths)
    else:
        paths = sql_file_paths

    if isinstance(user_or_dir, str):
        schema_dir = user_or_dir
        os.makedirs(schema_dir, exist_ok=True)
    else:
        schema_dir = get_schema_dir(user_or_dir)

    combined_schema: Dict[str, dict] = {}

    for db_key, db_path in paths.items():
        abs_path = os.path.normpath(db_path)
        schema = schema_extractor(db_key, abs_path)
        if "error" in schema:
            return schema
        combined_schema[db_key] = schema

    out_path = os.path.join(schema_dir, "schema_c.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(combined_schema, f, indent=4, ensure_ascii=False)

    return {"file": out_path, "databases": list(combined_schema.keys())}


def run(request, media_path: str):
    """
    Django endpoint for schema build.

    Expected request.data:
    {
        "sql_file_paths": { "mydb.sqlite": "/abs/path/to/mydb.sqlite" },
        "version": "ab" | "c"
    }
    """
    try:
        user_id = request.user.id if request.user.is_authenticated else "anonymous"
        data = request.data
        sql_file_paths = data.get("sql_file_paths", {})
        version = data.get("version", "").lower()

        if not sql_file_paths:
            return {"error": "sql_file_paths is required"}
        if version not in ("ab", "c"):
            return {"error": "version must be 'ab' or 'c'"}

        if version == "ab":
            result = build_schema_ab(sql_file_paths, user_id)
        else:
            result = build_schema_c(sql_file_paths, user_id)

        return {"success": True, "version": version, **result}

    except Exception as e:
        return {"error": f"Schema build failed: {str(e)}"}
