# Tools/toolsets/tools/database/check_ids.py
from typing import List
import sys
import os
import re
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "check_ids"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def _sanitize_identifier(name: str) -> str:
    """Ensure table/column names only contain alphanumeric characters and underscores."""
    if not re.match(r"^[a-zA-Z0-9_]+$", str(name)):
        raise ValueError(f"Invalid identifier detected: {name}")
    return str(name)


def check_ids(db_client: DBClient, table_name: str, id_list: List[any]) -> int:
    """
    Checks how many of the provided IDs exist in the target table's ID column.
    This function is safe against SQL injection and will raise a ValueError on invalid table names.
    """
    # 1. Input validation that should raise errors
    safe_table = _sanitize_identifier(table_name)

    if not id_list:
        return 0

    # 2. Input sanitization that should be graceful
    try:
        clean_ids = list(set([int(x) for x in id_list if str(x).replace("-", "").isdigit()]))
    except (TypeError, ValueError):  # Handles if something in list isn't convertible to int
        clean_ids = []

    if not clean_ids:
        return 0

    # 3. DB execution
    try:
        sql_template = _load_query("check_id_existence")
        placeholders = ", ".join(["?"] * len(clean_ids))
        query = sql_template.format(table=safe_table, placeholders=placeholders)

        res = db_client.execute(query, clean_ids)
        fetch_result = res.fetchone()
        return fetch_result[0] if fetch_result else 0

    except Exception as e:
        print(f"ERROR in check_ids: DB execution failed - {e}")
        return 0
