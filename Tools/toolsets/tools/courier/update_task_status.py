# Tools/toolsets/tools/courier/update_task_status.py
from typing import Dict, Any
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "update_task_status"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def update_task_status(task_id: str, status: str, location: str) -> Dict[str, Any]:
    """
    Updates the state and location of a research task.

    Args:
    - task_id: The UUID of the task.
    - status: The new status (e.g. 'active', 'finalized').
    - location: The role name where the task is currently located.
    """
    try:
        sql = _load_query("update_status")
        db.execute(sql, [status, location, task_id])

        return {"status": "success", "task_id": task_id, "new_status": status, "current_location": location}
    except Exception as e:
        return {"status": "error", "error": str(e)}
