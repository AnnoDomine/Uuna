# Tools/toolsets/tools/database/update_global_knowledge.py
from pathlib import Path
from typing import Optional

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "update_global_knowledge"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def update_global_knowledge(
    column_pattern: str,
    source_table: str,
    target_table: str,
    confidence: float,
    build_version: str,
    ai_notes: Optional[str] = None,
) -> dict:
    """
    Upserts knowledge about a column-to-table relationship.

    Args:
    - column_pattern: The name or pattern of the column (e.g. 'CreatureID').
    - source_table: The table where the column was found.
    - target_table: The table the column relates to.
    - confidence: Confidence score (0.0 to 1.0).
    - build_version: WoW version this knowledge was derived from.
    - ai_notes: Optional notes from the AI about the discovery.
    """
    try:
        sql = _load_query("upsert_global_knowledge")
        params = [column_pattern, source_table, target_table, confidence, ai_notes, build_version]
        db.execute(sql, params)
        debugger.add_log(f"Global knowledge updated for {column_pattern} ({source_table} -> {target_table})", agent="CORE", process="DB:UpdateGlobalKnowledge")
        return {"status": "success"}
    except Exception as e:
        debugger.add_log(f"Failed to update global knowledge: {e}", agent="CORE", level="ERROR", process="DB:UpdateGlobalKnowledge")
        return {"status": "error", "message": str(e)}
