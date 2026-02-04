from uuid import UUID
from typing import Dict, Any, Optional
from .base import DBModel

class TaskEvent(DBModel):
    event_id: UUID
    task_id: UUID
    initiator_role: str
    target_role: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    agent_confidence: float = 0.0

    @classmethod
    def get_table_name(cls) -> str:
        return "task_events"
