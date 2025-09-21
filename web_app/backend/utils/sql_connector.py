import sqlite3
import os
from django.apps import apps

class SQLiteConnector:
    def __init__(self):
        self.path_dict = self._build_path_dict()
        self.conn = None

    def _build_path_dict(self):
        """
        Build {database: file_path} from Files model.
        """
        Files = apps.get_model("core", "Files")
        path_dict = {}
        for f in Files.objects.all():
            db_key = f.database
            db_path = f.file.path  # FileField -> absolute path
            path_dict[db_key] = db_path
        return path_dict

    def connect(self, db_name: str):
        db_path = self.path_dict.get(db_name)
        if db_path:
            db_path = db_path.replace("/", os.sep)
        if not db_path:
            return None
        try:
            self.conn = sqlite3.connect(db_path)
        except sqlite3.Error:
            self.conn = None
        return self.conn

    def execute(self, db_name: str, query: str):
        conn = self.connect(db_name)
        if conn is None:
            return {"error": f"Failed to connect to database '{db_name}'."}

        cursor = conn.cursor()
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            if columns:
                result = [dict(zip(columns, row)) for row in rows]
            else:
                result = rows
            return {"success": True, "result": result}
        except sqlite3.Error as e:
            return {"error": str(e)}
        finally:
            self.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


def run(api_key, payload: dict):
    """
    Agent endpoint.
    Expected payload:
    {
        "database": "database name",
        "query": "SELECT ..."
    }
    """

    try:
        db_name = payload.get("database")
        query = payload.get("query")

        if not db_name:
            return {"error": "database name is required"}
        if not query:
            return {"error": "query is required"}

        connector = SQLiteConnector()
        return connector.execute(db_name, query)

    except Exception as e:
        return {"error": f"SQL connector failed: {str(e)}"}
