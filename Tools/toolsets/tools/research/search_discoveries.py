# Tools/toolsets/tools/research/search_discoveries.py
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "search_discoveries"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def search_discoveries(db_client: DBClient, term: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Searches through confirmed discoveries in the research schema.
    Use this to find previously analyzed table/column purposes.
    """
    try:
        sql = _load_query("search")
        # ILIKE with wildcards
        pattern = f"%{term}%"
        res = db_client.execute(sql, [pattern, pattern, limit]).fetchall()

        results = []
        for row in res:
            results.append({"table": row[0], "column": row[1], "discovery": row[2], "confidence": row[3]})
        return results
    except Exception as e:
        print(f"ERROR: Discovery search failed: {e}")
        return []
