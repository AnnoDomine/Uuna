# Tools/toolsets/tools/database/save_attempt.py
from pathlib import Path

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

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
) -> dict:
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
        debugger.add_log(f"Failed to save attempt: {e}", agent="CORE", level="ERROR", process="DB:SaveAttempt")
        return {"status": "error", "message": str(e)}
