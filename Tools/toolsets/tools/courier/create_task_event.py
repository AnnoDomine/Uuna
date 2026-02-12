# Tools/toolsets/tools/courier/create_task_event.py
import uuid
import json
from typing import Dict, Any, Optional
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "create_task_event"

def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", 'r') as f:
        return f.read().strip()

def create_task_event(
    db_client: DBClient, 
    task_id: str, 
    initiator: str, 
    target: str, 
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates a new event in the task chain. This is how the Courier hands off 
    work to a specialist agent.
    """
    try:
        event_id = str(uuid.uuid4())
        sql = _load_query("insert_event")
        
        db_client.execute(sql, [
            event_id, 
            task_id, 
            initiator, 
            target, 
            json.dumps(input_data), 
            0.0 # Initial confidence
        ])
        
        return {
            "status": "success",
            "event_id": event_id,
            "target": target
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
