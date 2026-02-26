import duckdb
import os
from typing import List, Dict, Any
from uuid import UUID


class EventLogManager:
    """
    Manager for retrieving logs from the Chronicle.
    Used by the Observer and Tinker for retrospective analysis.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.queries_path = "Tools/core/api/queries/logs"

    def _load_query(self, name: str) -> str:
        with open(os.path.join(self.queries_path, f"{name}.sql"), "r") as f:
            return f.read().strip()

    def get_logs_by_task(self, task_id: UUID) -> List[Dict[str, Any]]:
        """Retrieves the full history of a request."""
        sql = self._load_query("get_logs_by_task")
        with duckdb.connect(self.db_path) as con:
            # Using .df() for easy conversion to list of dicts
            df = con.execute(sql, [str(task_id)]).df()
            return df.to_dict(orient="records")

    def get_logs_by_event(self, event_id: UUID) -> List[Dict[str, Any]]:
        """Retrieves logs for a specific agent mission."""
        sql = self._load_query("get_logs_by_event")
        with duckdb.connect(self.db_path) as con:
            df = con.execute(sql, [str(event_id)]).df()
            return df.to_dict(orient="records")
