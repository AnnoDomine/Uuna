# Tools/toolsets/tools/database/save_discovery.py
from pathlib import Path

from Tools.core.shared_db_instance import db

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
        print(f"INFO: Discovery saved for {table_name}.{column_name}")
        return {"status": "success"}
    except Exception as e:
        print(f"ERROR: Failed to save discovery: {e}")
        return {"status": "error", "message": str(e)}
