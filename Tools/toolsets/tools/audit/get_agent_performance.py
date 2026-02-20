from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "get_agent_performance"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    path = QUERY_DIR / f"{name}.sql"
    if not path.exists():
        # Fallback inline query if folder/file doesn't exist yet
        return "SELECT initiator_role, AVG(agent_confidence) as avg_conf FROM research.task_events WHERE initiator_role = ? GROUP BY initiator_role"
    with open(path, "r") as f:
        return f.read().strip()


def get_agent_performance(agent_role: str) -> Dict[str, Any]:
    """
    Retrieves performance metrics and historical honesty ratings for an agent.

    Args:
    - agent_role: The role name of the agent (e.g. 'Archivist').
    """
    try:
        # This query would ideally pull from a view or combined table of events and observer scores
        # For now, we perform a basic aggregation from task_events
        sql = _load_query("get_metrics")
        res = db.execute(sql, [agent_role]).fetchone()

        if not res:
            return {"agent": agent_role, "status": "no_data", "message": "No historical data found for this agent."}

        return {
            "agent": agent_role,
            "average_confidence": round(float(res[1] or 0), 2),
            "total_events": int(res[2] or 0),
            "performance_status": "established" if int(res[2] or 0) > 10 else "new",
        }

    except Exception as e:
        return {"error": str(e)}
