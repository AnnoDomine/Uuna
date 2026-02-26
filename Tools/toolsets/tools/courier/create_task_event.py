import json
import uuid
from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "create_task_event"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def create_task_event(task_id: str, initiator: str, target: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a new event in the task chain.

    Args:
    - task_id: The ID of the task this event belongs to.
    - initiator: The role name of the agent creating the event.
    - target: The role name of the agent who should receive the event.
    - input_data: Dictionary containing the data for the target agent.
    """
    try:
        event_id = str(uuid.uuid4())
        # We use a query that does NOT include max_potential
        # because the Courier doesn't (and shouldn't) know it.
        sql = "INSERT INTO research.task_events (event_id, task_id, initiator_role, target_role, input_data, agent_confidence) VALUES (?, ?, ?, ?, ?, ?)"

        db.execute(
            sql,
            [
                event_id,
                task_id,
                initiator,
                target,
                json.dumps(input_data),
                0.0,  # Initial confidence
            ],
        )

        return {"status": "success", "event_id": event_id, "target": target}
    except Exception as e:
        return {"status": "error", "error": str(e)}
