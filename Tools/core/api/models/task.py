from uuid import UUID
from typing import List, Optional
from .base import DBModel

class Task(DBModel):
    task_id: UUID
    query: str
    output: Optional[str] = None
    status: str = "running"
    current_location: str = "Librarian"
    assigned_builds: List[str]

    @classmethod
    def get_table_name(cls) -> str:
        return "tasks"
