# Tools/toolsets/tools/system/get_task_context.py
import os
from pathlib import Path
from typing import Dict, Any
import sys

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "get_task_context"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def get_task_context(db_client: DBClient, task_id: str) -> Dict[str, Any]:
    """
    Retrieves the full history and original intent of a research task.
    Helps agents understand what has already been discovered and by whom.
    """
    try:
        sql = _load_query("get_history")
        res = db_client.execute(sql, [task_id]).fetchall()

        if not res:
            return {"error": f"Task ID {task_id} not found."}

        history = []
        # Index 0: task_id, 1: original_query, 2: task_status
        task_info = {"task_id": res[0][0], "original_query": res[0][1], "status": res[0][2]}

        for row in res:
            if row[3]:  # if event_id exists
                history.append({"event_id": row[3], "agent": row[4], "output": row[5], "confidence": row[6]})

        return {"task": task_info, "history": history}
    except Exception as e:
        return {"error": str(e)}
