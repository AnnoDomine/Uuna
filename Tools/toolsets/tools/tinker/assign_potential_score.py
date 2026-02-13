# Tools/toolsets/tools/tinker/assign_potential_score.py
from typing import Dict, Any
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "assign_potential_score"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def assign_potential_score(db_client: DBClient, event_id: str, potential: int) -> Dict[str, Any]:
    """
    Sets the Max_Potential score for a specific task event.
    This defines the performance ceiling for the agent assigned to this event.
    """
    try:
        sql = _load_query("update_potential")
        db_client.execute(sql, [potential, event_id])

        return {"status": "success", "event_id": event_id, "max_potential": potential}
    except Exception as e:
        return {"status": "error", "error": str(e)}
