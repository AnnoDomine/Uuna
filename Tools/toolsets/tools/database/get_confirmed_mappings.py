# Tools/toolsets/tools/database/get_confirmed_mappings.py
from typing import List, Tuple
import sys
import os
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

# Define the path to the queries for this specific tool
QUERY_DIR = Path(__file__).parent / "queries" / "get_confirmed_mappings"

def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / name, 'r') as f:
        return f.read().strip()

def get_confirmed_mappings(db_client: DBClient, build_version: str) -> List[Tuple]:
    """
    Fetches all confirmed mappings for a specific build version.

    Args:
        db_client: An instance of DBClient to interact with the database service.
        build_version: The specific build version to get mappings for.

    Returns:
        A list of tuples, where each tuple represents a mapping
        (e.g., (source_table, column_pattern, target_table)).
    """
    try:
        sql = _load_query("get_confirmed_mappings.sql")
        res = db_client.execute(sql, [build_version])
        return res.fetchall()
    except Exception as e:
        print(f"ERROR: Failed to get confirmed mappings: {e}")
        return []
