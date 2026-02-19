# Tools/toolsets/tools/research/search_discoveries.py
from pathlib import Path
from typing import Any, Dict, List

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "search_discoveries"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def search_discoveries(term: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Searches through confirmed discoveries in the research schema.

    Args:
    - term: The search term (searches in table name, column name, and discovery text).
    - limit: Maximum number of results to return.
    """
    try:
        sql = _load_query("search")
        # ILIKE with wildcards
        pattern = f"%{term}%"
        res = db.execute(sql, [pattern, pattern, limit]).fetchall()

        results = []
        for row in res:
            results.append({"table": row[0], "column": row[1], "discovery": row[2], "confidence": row[3]})
        return results
    except Exception as e:
        print(f"ERROR: Discovery search failed: {e}")
        return []
