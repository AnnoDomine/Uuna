# Tools/toolsets/tools/tinker/assign_potential_score.py
from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "assign_potential_score"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def assign_potential_score(event_id: str, potential: int) -> Dict[str, Any]:
    """
    Sets the Max_Potential score for a specific task event.

    Args:
    - event_id: The UUID of the event.
    - potential: The maximum potential points for this event.
    """
    try:
        sql = _load_query("update_potential")
        db.execute(sql, [potential, event_id])

        return {"status": "success", "event_id": event_id, "max_potential": potential}
    except Exception as e:
        return {"status": "error", "error": str(e)}
