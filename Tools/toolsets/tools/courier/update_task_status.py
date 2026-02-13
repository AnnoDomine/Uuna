# Tools/toolsets/tools/courier/update_task_status.py
from typing import Dict, Any
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "update_task_status"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def update_task_status(db_client: DBClient, task_id: str, status: str, location: str) -> Dict[str, Any]:
    """
    Updates the global state and current location of a research task.
    Valid statuses: spawned, active, stalled, rejected, finalized.
    """
    try:
        sql = _load_query("update_status")
        db_client.execute(sql, [status, location, task_id])

        return {"status": "success", "task_id": task_id, "new_status": status, "current_location": location}
    except Exception as e:
        return {"status": "error", "error": str(e)}
