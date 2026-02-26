from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "log_event_reasoning"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def log_event_reasoning(event_id: str, task_id: str, role: str, message: str) -> Dict[str, Any]:
    """
    Standardized logging for agent reasoning steps.

    Args:
    - event_id: The related event id.
    - task_id: The related task id.
    - role: The role name of the agent logging the reasoning.
    - message: The reasoning message or "breath" to log.
    """
    try:
        sql = _load_query("insert_log")
        db.execute(sql, [event_id, task_id, role, message])
        return {"status": "success", "message": "Log entry recorded."}
    except Exception as e:
        return {"status": "error", "error": str(e)}
