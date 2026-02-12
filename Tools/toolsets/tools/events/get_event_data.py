# Tools/toolsets/tools/events/get_event_data.py
import json
from typing import Dict, Any, Optional
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "get_event_data"

def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", 'r') as f:
        return f.read().strip()

def get_event_data(db_client: DBClient, event_id: str) -> Dict[str, Any]:
    """
    Retrieves the payload and metadata of a specific task event.
    Agents use this to read their assigned work when they receive an event_id.
    """
    try:
        sql = _load_query("get_event")
        res = db_client.execute(sql, [event_id]).fetchone()
        
        if not res:
            return {"error": f"Event ID {event_id} not found."}
            
        return {
            "event_id": res[0],
            "task_id": res[1],
            "initiator": res[2],
            "target": res[3],
            "input_data": json.loads(res[4]) if isinstance(res[4], str) else res[4],
            "confidence": res[5],
            "max_potential": res[6]
        }
    except Exception as e:
        return {"error": str(e)}
