# load_test_data.py

"""
Load the test data from the Spider dataset and save it to a JSON file.

Run: python3 -m scripts.load_test_data
"""

import os
import sys
from pathlib import Path
from typing import Union
import pandas as pd
import json

# Import project config first to get PROJECT_ROOT
from src.config import PROJECT_ROOT

# Add project root to Python path so imports work
sys.path.append(PROJECT_ROOT)

SQL_DATA_PATH = PROJECT_ROOT / "data" / "spider_data" / "train_spider.json"
SQL_TESTING = PROJECT_ROOT / "data" / "test" / "spider_query_answers.json"


def load_sql_dataset(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load the Spider dataset (JSON with a list of records) and return a DataFrame with
    db_id, query, question.
    """

    file_path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # load entire JSON list

    records = [
        {
            "db_id": rec.get("db_id"),
            "question": rec.get("question"),
            "query": rec.get("query"),
            "guery_toks": rec.get("query_toks"),  # list
        }
        for rec in data
    ]

    df = pd.DataFrame(records)
    return df


# sql_answers_df = load_sql_dataset(SQL_DATA_PATH)
# sql_answers_df.head()

if __name__ == "__main__":
    SQL_TESTING.parent.mkdir(parents=True, exist_ok=True)
    df = load_sql_dataset(SQL_DATA_PATH)
    df.to_json(SQL_TESTING, orient="records", indent=2)
    print(f"Saved simplified queries to {SQL_TESTING}")
