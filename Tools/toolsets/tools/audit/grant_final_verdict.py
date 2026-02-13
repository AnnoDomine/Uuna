# Tools/toolsets/tools/audit/grant_final_verdict.py
from typing import Dict, Any, Optional
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "grant_final_verdict"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def grant_final_verdict(
    db_client: DBClient, task_id: str, decision: str, summary: str, final_output: Optional[str] = None
) -> Dict[str, Any]:
    """
    Exclusively for The Sages. Sets the final verdict for a research task.
    APPROVE: Moves task to a state where the Librarian can synthesize the answer.
    BLOCK: Rejects the findings and requires rework.
    """
    try:
        # Map decision to task status
        status = "pending_librarian" if decision.upper() == "APPROVE" else "rejected"

        sql = _load_query("update_task_final")
        # We store the summary/output in the task record
        db_client.execute(sql, [status, final_output or summary, task_id])

        return {"status": "success", "task_id": task_id, "verdict": decision.upper(), "new_task_status": status}
    except Exception as e:
        return {"status": "error", "error": str(e)}
