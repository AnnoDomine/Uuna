# Tools/toolsets/tools/system/create_research_task.py
import uuid
import json
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "create_research_task"


def _load_query(name: str) -> str:
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
