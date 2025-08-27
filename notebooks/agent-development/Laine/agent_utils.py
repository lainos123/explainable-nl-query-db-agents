# src/agent_utils.py
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any

def load_schemas(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load the schema file from the given path and return a dictionary of schema objects."""
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    return {it["db_id"]: it for it in items}

def schema_text(db: Dict[str, Any], max_cols_per_table: int = 24) -> str:
    """Convert a database schema to a text string with tables and attributes."""
    tnames = db["table_names_original"]
    cols = db["column_names_original"]
    by_table = defaultdict(list)
    for _, (tidx, cname) in enumerate(cols):
        if tidx >= 0:
            by_table[tidx].append(str(cname))
    parts = []
    for i, t in enumerate(tnames):
        c = by_table[i][:max_cols_per_table]
        parts.append(f"{t}({', '.join(c)})")
    return "\n".join(parts)

def build_texts(schemas: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """Creates a dictionary of schemas to their tables(...columns...)"""
    return {db_id: schema_text(db) for db_id, db in schemas.items()}

def get_schema_text(db_id: str, schemas: dict) -> str:
    """
    Return the schema text for a specific database id.
    """
    if db_id not in schemas:
        raise ValueError(f"Database id '{db_id}' not found in schemas.")
    
    return schema_text(schemas[db_id])