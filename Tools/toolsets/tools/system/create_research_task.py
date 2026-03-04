import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "create_research_task"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def create_research_task(query: str, assigned_builds: List[str]) -> Dict[str, Any]:
    """
    Initiates a new research mission in the system.

    Args:
    - query: The research query or objective.
    - assigned_builds: List of WoW build versions to research.
    """
    debugger.add_log(f"Spawning Research Task: '{query[:50]}...' for {len(assigned_builds)} builds.", agent="SYSTEM", process="Task:Create")
    try:
        task_id = str(uuid.uuid4())
        sql = _load_query("insert_task")

        db.execute(sql, [task_id, query, json.dumps(assigned_builds)])

        debugger.add_log(f"Task {task_id[:8]} created successfully.", agent="SYSTEM", level="SUCCESS", process="Task:Create")
        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Research task spawned for {len(assigned_builds)} build(s).",
        }
    except Exception as e:
        debugger.add_log(f"Failed to create research task: {e}", agent="SYSTEM", level="ERROR", process="Task:Create")
        return {"status": "error", "error": str(e)}
