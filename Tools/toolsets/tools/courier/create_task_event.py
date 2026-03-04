import json
import uuid
from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "create_task_event"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    path = QUERY_DIR / f"{name}.sql"
    if path.exists():
        with open(path, "r") as f:
            return f.read().strip()
    return "INSERT INTO research.task_events (event_id, task_id, initiator_role, target_role, input_data, agent_confidence, max_potential) VALUES (?, ?, ?, ?, ?, ?, ?)"


def create_task_event(task_id: str, initiator: str, target: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new event in the task chain.

    Args:
    - task_id: The ID of the task this event belongs to.
    - initiator: The role name of the agent creating the event.
    - target: The role name of the agent who should receive the event.
    - input_data: Dictionary containing the data for the target agent.
    """
    debugger.add_log(f"Creating Event: {initiator} -> {target} (Task: {task_id})", agent="COURIER", process="Event:Creation")
    try:
        event_id = str(uuid.uuid4())
        sql = _load_query("insert_event")

        db.execute(
            sql,
            [
                event_id,
                task_id,
                initiator,
                target,
                json.dumps(input_data),
                0.0,  # Initial confidence
                0,    # Initial max_potential (assigned by Tinker later)
            ],
        )

        debugger.add_log(f"Event {event_id[:8]} created successfully.", agent="COURIER", level="SUCCESS", process="Event:Creation")
        return {"status": "success", "event_id": event_id, "target": target}
    except Exception as e:
        debugger.add_log(f"Failed to create event: {e}", agent="COURIER", level="ERROR", process="Event:Creation")
        return {"status": "error", "error": str(e)}
