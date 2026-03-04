# Tools/toolsets/tools/database/get_last_attempt.py
from pathlib import Path
from typing import Optional, Tuple

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

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
        debugger.add_log(f"Failed to get last attempt: {e}", agent="CORE", level="ERROR", process="DB:GetLastAttempt")
        return None
