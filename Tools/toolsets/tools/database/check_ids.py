# Tools/toolsets/tools/database/check_ids.py
import re
from pathlib import Path
from typing import Any, List, Optional

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "check_ids"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def _sanitize_identifier(name: str) -> str:
    """Ensure table/column names only contain alphanumeric characters and underscores."""
    if not re.match(r"^[a-zA-Z0-9_]+$", str(name)):
        raise ValueError(f"Invalid identifier detected: {name}")
    return str(name)


def check_ids(table_name: str, id_list: List[Any], build_version: Optional[str] = None) -> int:
    """
    Checks how many of the provided IDs exist in a table.

    Args:
    - table_name: The name of the table to check (e.g. 'Creature').
    - id_list: List of numeric IDs to look for.
    - build_version: Optional build version to filter by.
    """
    # 1. Input validation
    safe_table = _sanitize_identifier(table_name)

    if not id_list:
        return 0

    # 2. Input sanitization
    try:
        clean_ids = list(set([int(x) for x in id_list if str(x).replace("-", "").isdigit()]))
    except (TypeError, ValueError):
        clean_ids = []

    if not clean_ids:
        return 0

    # 3. Resolve build_id if needed
    build_id = None
    if build_version:
        res = db.execute("SELECT id FROM registry.builds WHERE ? IN (version, id::VARCHAR)", [build_version])
        row = res.fetchone()
        if row:
            build_id = row[0]

    # 4. DB execution
    try:
        placeholders = ", ".join(["?"] * len(clean_ids))
        params = clean_ids

        # Check if table has _row_hash for mapping
        has_hash = False
        if build_id:
            cols_res = db.execute(f"PRAGMA table_info('archive.{safe_table}')")
            has_hash = any(row[1] == '_row_hash' for row in cols_res.fetchall())

        if build_id and has_hash:
            # Query with mapping table
            query = f"""
                SELECT COUNT(*) 
                FROM archive."{safe_table}" d
                JOIN archive.build_data_map m ON d._row_hash = m.row_hash
                WHERE d.ID IN ({placeholders})
                  AND m.build_id = ?
                  AND m.table_name = ?
            """
            params.extend([build_id, table_name])
        else:
            # Generic query (no mapping or no _row_hash column)
            query = f'SELECT COUNT(*) FROM archive."{safe_table}" WHERE ID IN ({placeholders})'

        res = db.execute(query, params)
        fetch_result = res.fetchone()
        return fetch_result[0] if fetch_result else 0

    except Exception as e:
        debugger.add_log(f"ERROR in check_ids: DB execution failed - {e}", agent="CORE", level="ERROR", process="DB:CheckIDs")
        return 0
