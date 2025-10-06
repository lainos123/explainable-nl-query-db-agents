import sqlite3
import os
from django.apps import apps


def _get_db_path_for_user(user_id: int, db_name: str):
    """
    Return absolute file path for `db_name` owned by `user_id`, or None.
    Very small and explicit: uses the Django `Files` model.
    """
    Files = apps.get_model("core", "Files")
    f = Files.objects.filter(user_id=user_id, database=db_name).first()
    if not f or not f.file:
        return None
    try:
        path = f.file.path
    except Exception:
        return None
    if not os.path.isabs(path):
        # ensure we use OS-native separators
        path = os.path.abspath(path)
    return path


def _execute_sql_at_path(db_path: str, query: str):
    """
    Execute SQL against the sqlite file at db_path. Return dict with either
    `{'success': True, 'result': ...}` or `{'error': '...'}`.
    For SELECT queries we return a list of dicts (columns -> values). For other
    statements we return rows_affected.
    """
    if not db_path or not os.path.isfile(db_path):
        return {"error": f"Database file not found: {db_path}"}

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)

        # If it's a SELECT-like statement, cursor.description is set
        if cur.description:
            columns = [d[0] for d in cur.description]
            rows = cur.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
            return {"success": True, "result": result}
        else:
            # Non-select: commit and report affected rows
            conn.commit()
            return {"success": True, "rows_affected": cur.rowcount}
    except sqlite3.Error as e:
        return {"error": str(e)}
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def run(api_key, payload: dict):
    """
    Backwards-compatible helper. If caller provides `user_id` in payload it will
    be used; otherwise this function will attempt to run without user scoping (not recommended).
    Expected payload: { 'database': name, 'query': 'SELECT ...', 'user_id': <int> }
    """
    try:
        db_name = payload.get("database")
        query = payload.get("query")
        user_id = payload.get("user_id")

        if not db_name:
            return {"error": "database name is required"}
        if not query:
            return {"error": "query is required"}

        if user_id is None:
            return {"error": "user_id is required for secure DB access"}

        db_path = _get_db_path_for_user(user_id, db_name)
        if not db_path:
            return {"error": f"Database '{db_name}' not found for user {user_id}"}

        return _execute_sql_at_path(db_path, query)
    except Exception as e:
        return {"error": f"SQL connector failed: {str(e)}"}


def run_sql(api_key, payload: dict, user_id: int = None):
    """
    Minimal, Django-first entrypoint used by the agents pipeline.
    Called as `run_sql(api_key, payload, user_id)` from `agents.views`.

    Expected payload (from Agent C): { 'database': name, 'SQL': 'SELECT ...' }
    """
    try:
        db_name = payload.get("database")
        query = payload.get("SQL") or payload.get("query")

        if not db_name:
            return {"error": "database name is required"}
        if not query:
            return {"error": "query is required"}
        if user_id is None:
            return {"error": "user_id is required"}

        db_path = _get_db_path_for_user(user_id, db_name)
        if not db_path:
            return {"error": f"Database '{db_name}' not found for user {user_id}"}

        return _execute_sql_at_path(db_path, query)
    except Exception as e:
        return {"error": f"SQL connector failed: {str(e)}"}