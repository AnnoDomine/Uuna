import json
from pathlib import Path
from typing import Dict, Union

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "get_event_data"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def get_event_data(event_id: str) -> Dict[str, Union[str, float, dict]]:
    """
    Retrieves the payload and metadata of a specific task event.

    Args:
    - event_id: The UUID of the event to retrieve.
    """
    debugger.add_log(f"Retrieving data for Event: {event_id}", agent="SYSTEM", process="Event:GetData")
    try:
        sql = _load_query("get_event")
        res = db.execute(sql, [event_id]).fetchone()

        if not res:
            debugger.add_log(f"Event ID {event_id} not found in database.", agent="SYSTEM", level="WARNING", process="Event:GetData")
            return {"error": f"Event ID {event_id} not found."}

        data = {
            "event_id": res[0],
            "task_id": res[1],
            "initiator": res[2],
            "target": res[3],
            "input_data": json.loads(res[4]) if isinstance(res[4], str) else res[4],
            "confidence": res[5],
            "max_potential": res[6],
        }
        debugger.add_log(f"Successfully retrieved data for Event {event_id[:8]}.", agent="SYSTEM", level="SUCCESS", process="Event:GetData")
        return data
    except Exception as e:
        debugger.add_log(f"Failed to retrieve event data: {e}", agent="SYSTEM", level="ERROR", process="Event:GetData")
        return {"error": str(e)}
