# Tools/toolsets/tools/audit/check_logical_consistency.py
from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "check_logical_consistency"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def check_logical_consistency(table: str, column: str, proposed_target: str) -> Dict[str, Any]:
    """
    Checks if a mapping contradicts existing knowledge.

    Args:
    - table: The source table.
    - column: The source column.
    - proposed_target: The proposed target table.
    """
    debugger.add_log(f"Checking consistency for {table}.{column} -> {proposed_target}", agent="AUDIT", process="ConsistencyCheck")
    try:
        sql = _load_query("get_conflicts")
        res = db.execute(sql, [column, table]).fetchall()

        if not res:
            debugger.add_log(f"No conflicts found for {table}.{column}", agent="AUDIT", process="ConsistencyCheck")
            return {"status": "consistent", "message": "No existing knowledge found for this column/table combination."}

        conflicts = []
        for row in res:
            existing_target = row[2]
            if existing_target.lower() != proposed_target.lower():
                conflicts.append({"existing_target": existing_target, "existing_confidence": row[3], "notes": row[4]})

        if conflicts:
            debugger.add_log(f"Contradiction detected for {table}.{column}! Found {len(conflicts)} conflicting entries.", agent="AUDIT", level="WARNING", process="ConsistencyCheck")
            return {
                "status": "contradictory",
                "conflicts": conflicts,
                "message": f"Proposed target '{proposed_target}' differs from {len(conflicts)} established knowledge entries.",
            }

        debugger.add_log(f"Mapping {table}.{column} -> {proposed_target} is consistent with global knowledge.", agent="AUDIT", level="SUCCESS", process="ConsistencyCheck")
        return {"status": "consistent", "message": "Proposed mapping aligns with existing global knowledge."}

    except Exception as e:
        debugger.add_log(f"Consistency check failed: {e}", agent="AUDIT", level="ERROR", process="ConsistencyCheck")
        return {"status": "error", "error": str(e)}
