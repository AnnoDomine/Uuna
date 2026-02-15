# Tools/toolsets/tools/database/save_attempt.py
import sys
from pathlib import Path
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "save_attempt"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def save_attempt(
    build_version: str,
    table_name: str,
    column_name: str,
    proposed_target: str,
    decision: str,
    reasoning: str,
):
    """
    Saves the result of an AI mapping attempt.

    Args:
    - build_version: The version string of the build.
    - table_name: The name of the table.
    - column_name: The name of the column.
    - proposed_target: The table name proposed as a reference.
    - decision: The decision (e.g. 'CONFIRM', 'VETO').
    - reasoning: Detailed reason for the decision.
    """
    try:
        sql = _load_query("save_attempt")
        params = [build_version, table_name, column_name, proposed_target, decision, reasoning]
        db.execute(sql, params)
        return {"status": "success"}
    except Exception as e:
        print(f"ERROR: Failed to save attempt: {e}")
        return {"status": "error", "message": str(e)}
