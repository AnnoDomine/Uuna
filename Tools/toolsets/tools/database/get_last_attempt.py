# Tools/toolsets/tools/database/get_last_attempt.py
from pathlib import Path
from typing import Optional, Tuple

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "get_last_attempt"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def get_last_attempt(table_name: str, column_name: str) -> Optional[Tuple]:
    """
    Retrieves the last mapping attempt for a specific column.

    Args:
    - table_name: The name of the table.
    - column_name: The name of the column.
    """
    try:
        sql = _load_query("get_last_attempt")
        res = db.execute(sql, [table_name, column_name])
        return res.fetchone()
    except Exception as e:
        print(f"ERROR: Failed to get last attempt: {e}")
        return None
