# Tools/toolsets/tools/audit/grant_final_verdict.py
from pathlib import Path
from typing import Any, Dict, Optional

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "grant_final_verdict"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def grant_final_verdict(
    task_id: str, decision: str, summary: str, final_output: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sets the final verdict for a research task.

    Args:
    - task_id: The UUID of the task.
    - decision: The final verdict (e.g. 'APPROVE', 'BLOCK').
    - summary: Summary of the findings.
    - final_output: The final processed output for the user.
    """
    debugger.add_log(f"Granting final verdict for Task: {task_id}. Decision: {decision}", agent="AUDIT", process="Audit:FinalVerdict")
    try:
        # Map decision to task status
        status = "pending_librarian" if decision.upper() == "APPROVE" else "rejected"

        sql = _load_query("update_task_final")
        # We store the summary/output in the task record
        db.execute(sql, [status, final_output or summary, task_id])

        debugger.add_log(f"Task {task_id} status updated to: {status}", agent="AUDIT", level="SUCCESS", process="Audit:FinalVerdict")
        return {"status": "success", "task_id": task_id, "verdict": decision.upper(), "new_task_status": status}
    except Exception as e:
        debugger.add_log(f"Failed to grant final verdict for task {task_id}: {e}", agent="AUDIT", level="ERROR", process="Audit:FinalVerdict")
        return {"status": "error", "error": str(e)}
