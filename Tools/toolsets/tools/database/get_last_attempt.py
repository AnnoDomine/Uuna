# Tools/toolsets/tools/database/get_last_attempt.py
import sys
from pathlib import Path
import os
from typing import Optional, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "get_last_attempt"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def get_last_attempt(db_client: DBClient, table_name: str, column_name: str) -> Optional[Tuple]:
    """
    Retrieves the last mapping attempt for a specific table and column.
    """
    try:
        sql = _load_query("get_last_attempt")
        res = db_client.execute(sql, [table_name, column_name])
        return res.fetchone()
    except Exception as e:
        print(f"ERROR: Failed to get last attempt: {e}")
        return None
