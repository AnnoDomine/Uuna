# Tools/toolsets/tools/database/save_discovery.py
import sys
from pathlib import Path
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "save_discovery"

def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, 'r') as f:
        return f.read().strip()

def save_discovery(db_client: DBClient, build_id: int, table_name: str, column_name: str, discovery: str, confidence: float):
    """
    Saves a new discovery about a column to the research database.
    """
    try:
        sql = _load_query("save_discovery")
        params = [build_id, table_name, column_name, discovery, confidence]
        db_client.execute(sql, params)
        print(f"INFO: Discovery saved for {table_name}.{column_name}")
        return {"status": "success"}
    except Exception as e:
        print(f"ERROR: Failed to save discovery: {e}")
        return {"status": "error", "message": str(e)}
