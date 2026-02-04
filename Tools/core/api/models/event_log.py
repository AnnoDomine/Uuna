from uuid import UUID
from .base import DBModel

class EventLog(DBModel):
    log_id: int
    event_id: UUID
    task_id: UUID
    role: str
    log_entry: str

    @classmethod
    def get_table_name(cls) -> str:
        return "event_logs"
