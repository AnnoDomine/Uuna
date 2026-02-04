from uuid import UUID
from typing import Optional
from .base import DBModel

class ScoreBoard(DBModel):
    score_id: int
    task_id: UUID
    event_id: Optional[UUID] = None
    final_percent: float

    @classmethod
    def get_table_name(cls) -> str:
        return "score_board"
