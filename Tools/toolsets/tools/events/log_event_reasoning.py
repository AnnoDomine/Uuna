# Tools/toolsets/tools/events/log_event_reasoning.py
import os
from pathlib import Path
from typing import Dict, Any
import sys

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))


from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "log_event_reasoning"


def _load_query(name: str) -> str:
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
