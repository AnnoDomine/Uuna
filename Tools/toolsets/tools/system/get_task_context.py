# Tools/toolsets/tools/system/get_task_context.py
from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "get_task_context"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def get_task_context(task_id: str) -> Dict[str, Any]:
    """
    Retrieves the full history and intent of a research task.

    Args:
    - task_id: The UUID of the task to retrieve.
    """
    try:
        import json
        sql = _load_query("get_history")
        res = db.execute(sql, [task_id]).fetchall()

        if not res:
            return {"error": f"Task ID {task_id} not found."}

        history = []
        # Index 0: task_id, 1: original_query, 2: task_status, 3: assigned_builds
        builds = res[0][3]
        if isinstance(builds, str):
            try:
                builds = json.loads(builds)
            except Exception:
                pass

        task_info = {
            "task_id": res[0][0], 
            "original_query": res[0][1], 
            "status": res[0][2],
            "assigned_builds": builds
        }

        for row in res:
            if row[4]:  # if event_id exists (index shifted by 1)
                history.append({"event_id": row[4], "agent": row[5], "output": row[6], "confidence": row[7]})

        return {"task": task_info, "history": history}
    except Exception as e:
        return {"error": str(e)}
