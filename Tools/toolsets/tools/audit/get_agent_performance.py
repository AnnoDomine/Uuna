from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "get_agent_performance"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    path = QUERY_DIR / f"{name}.sql"
    if not path.exists():
        # Fallback inline query if folder/file doesn't exist yet
        return "SELECT initiator_role, AVG(agent_confidence) as avg_conf, COUNT(*) as total FROM research.task_events WHERE initiator_role = ? GROUP BY initiator_role"
    with open(path, "r") as f:
        return f.read().strip()


def get_agent_performance(agent_role: str) -> Dict[str, Any]:
    """
    Retrieves performance metrics and historical honesty ratings for an agent.

    Args:
    - agent_role: The role name of the agent (e.g. 'Archivist').
    """
    debugger.add_log(f"Fetching performance metrics for agent: {agent_role}", agent="AUDIT", process="Audit:Performance")
    try:
        # This query would ideally pull from a view or combined table of events and observer scores
        sql = _load_query("get_metrics")
        res = db.execute(sql, [agent_role]).fetchone()

        if not res:
            debugger.add_log(f"No historical data found for agent {agent_role}.", agent="AUDIT", level="WARNING", process="Audit:Performance")
            return {"agent": agent_role, "status": "no_data", "message": "No historical data found for this agent."}

        result = {
            "agent": agent_role,
            "average_confidence": round(float(res[1] or 0), 2),
            "total_events": int(res[2] or 0),
            "performance_status": "established" if int(res[2] or 0) > 10 else "new",
        }
        debugger.add_log(f"Metrics for {agent_role} retrieved successfully.", agent="AUDIT", level="SUCCESS", process="Audit:Performance")
        return result

    except Exception as e:
        debugger.add_log(f"Failed to fetch performance for {agent_role}: {e}", agent="AUDIT", level="ERROR", process="Audit:Performance")
        return {"error": str(e)}
