# Tools/toolsets/tools/database/save_discovery.py
from pathlib import Path

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "save_discovery"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def save_discovery(
    build_id: int, table_name: str, column_name: str, discovery: str, confidence: float
) -> dict:
    """
    Saves a new discovery about a column.

    Args:
    - build_id: The internal ID of the build.
    - table_name: The name of the table.
    - column_name: The name of the column.
    - discovery: The textual description of the discovery.
    - confidence: Confidence score (0.0 to 1.0).
    """
    try:
        sql = _load_query("save_discovery")
        params = [build_id, table_name, column_name, discovery, confidence]
        db.execute(sql, params)
        debugger.add_log(f"Discovery saved for {table_name}.{column_name}", agent="CORE", process="DB:SaveDiscovery")
        return {"status": "success"}
    except Exception as e:
        debugger.add_log(f"Failed to save discovery: {e}", agent="CORE", level="ERROR", process="DB:SaveDiscovery")
        return {"status": "error", "message": str(e)}
