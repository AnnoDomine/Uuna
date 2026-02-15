# Tools/toolsets/tools/database/get_confirmed_mappings.py
from typing import List, Tuple
import sys
import os
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.shared_db_instance import db

# Define the path to the queries for this specific tool
QUERY_DIR = Path(__file__).parent / "queries" / "get_confirmed_mappings"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / name, "r") as f:
        return f.read().strip()


def get_confirmed_mappings(build_version: str) -> List[Tuple]:
    """
    Fetches all confirmed mappings for a specific build version.

    Args:
    - build_version: The specific build version to get mappings for.
    """
    try:
        sql = _load_query("get_confirmed_mappings.sql")
        res = db.execute(sql, [build_version])
        return res.fetchall()
    except Exception as e:
        print(f"ERROR: Failed to get confirmed mappings: {e}")
        return []
