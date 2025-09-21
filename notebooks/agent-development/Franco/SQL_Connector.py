'''
This script connect with the SQL file base on the extracted paths
Currently only work with SQLite, future plan to support other SQL databases
return a connection object that can be used to interact with the database

It also containt protocol for SQL query, the path is depend of what is the OS that are used
'''
import nt
import sqlite3
import os
import json

class SQLite_Connector:
    def __init__(self, path_json: str):
        # path_json is a JSON string containing the path dictionary
        try:
            self.path_dict = json.loads(path_json)
        except json.JSONDecodeError as e:
            print("Invalid JSON for path_dict:", e)
            self.path_dict = {}
        self.conn = None
        self.db_name = None

    def connect(self, db_name: str, verbose: bool = False):
        self.db_name = db_name
        db_path = self.path_dict.get(db_name)
        db_path = db_path.replace("/", os.sep) if db_path else None
        if db_path is None:
            print("Database {} path not found.".format(db_name))
            return None
        try:
            if not verbose:
                print("Connecting to SQLite database at:", db_path)
            self.conn = sqlite3.connect(db_path)
            if not verbose:
                print("Connection successful.")
        except sqlite3.Error as e:
            print("Connection failed:", e)
            self.conn = None
        return self.conn

    def execute_queries(self, queries: list, indent: int = 4):
        # Ensure the connection is established
        if self.conn is None:
            print("Database connection is not established. ",
                  "\nPlease use connect() method on the object.")
            return json.dumps({"error": "Database connection is not established."})
        
        cursor = self.conn.cursor()
        results = []
        try:
            for query in queries:
                cursor.execute(query)
                # Try to get column names for better JSON output
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                if columns:
                    # Return as list of dicts
                    results.append([dict(zip(columns, row)) for row in rows])
                else:
                    results.append(rows)
            return json.dumps(results, indent=indent)
        except sqlite3.Error as e:
            print("Query execution failed:", e)
            return json.dumps({"error": str(e)}, indent=indent, ensure_ascii=False)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
