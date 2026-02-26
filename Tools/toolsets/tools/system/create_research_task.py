import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

from Tools.core.shared_db_instance import db

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
    try:
        task_id = str(uuid.uuid4())
        sql = _load_query("insert_task")

        db.execute(sql, [task_id, query, json.dumps(assigned_builds)])

        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Research task spawned for {len(assigned_builds)} build(s).",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
