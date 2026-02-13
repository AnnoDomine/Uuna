# Tools/toolsets/tools/database/update_global_knowledge.py
import sys
from pathlib import Path
import os
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "update_global_knowledge"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def update_global_knowledge(
    db_client: DBClient,
    column_pattern: str,
    source_table: str,
    target_table: str,
    confidence: float,
    build_version: str,
    ai_notes: Optional[str] = None,
):
    """
    Upserts a piece of global knowledge about a column-to-table relationship.
    """
    try:
        sql = _load_query("upsert_global_knowledge")
        params = [column_pattern, source_table, target_table, confidence, ai_notes, build_version]
        db_client.execute(sql, params)
        print(f"INFO: Global knowledge updated for {column_pattern} ({source_table} -> {target_table})")
        return {"status": "success"}
    except Exception as e:
        print(f"ERROR: Failed to update global knowledge: {e}")
        return {"status": "error", "message": str(e)}
