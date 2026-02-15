# Tools/toolsets/tools/events/get_event_data.py
import json
import os
import sys
from pathlib import Path
from typing import Tuple

from Tools.core.shared_db_instance import db

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from typing import TypedDict

QUERY_DIR = Path(__file__).parent / "queries" / "get_event_data"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


class EventReturn(TypedDict):
    event_id: int
    task_id: int
    initialiator: str
    target: str
    input_data: str
    confidence: float
    max_potential: str


class EventError(TypedDict):
    error: str


def get_event_data(event_id: str) -> Tuple[EventReturn, EventError]:
    """
    Retrieves the payload and metadata of a specific task event.

    Args:
    - event_id: The UUID of the event to retrieve.
    """
    try:
        sql = _load_query("get_event")
        res = db.execute(sql, [event_id]).fetchone()

        if not res:
            return {"error": f"Event ID {event_id} not found."}

        return {
            "event_id": res[0],
            "task_id": res[1],
            "initiator": res[2],
            "target": res[3],
            "input_data": json.loads(res[4]) if isinstance(res[4], str) else res[4],
            "confidence": res[5],
            "max_potential": res[6],
        }
    except Exception as e:
        return {"error": str(e)}
