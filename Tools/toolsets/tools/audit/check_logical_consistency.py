# Tools/toolsets/tools/audit/check_logical_consistency.py
from typing import Dict, Any
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "check_logical_consistency"

def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", 'r') as f:
        return f.read().strip()

def check_logical_consistency(db_client: DBClient, table: str, column: str, proposed_target: str) -> Dict[str, Any]:
    """
    Checks if a proposed mapping contradicts existing established knowledge in the research database.
    """
    try:
        sql = _load_query("get_conflicts")
        res = db_client.execute(sql, [column, table]).fetchall()
        
        if not res:
            return {"status": "consistent", "message": "No existing knowledge found for this column/table combination."}
            
        conflicts = []
        for row in res:
            existing_target = row[2]
            if existing_target.lower() != proposed_target.lower():
                conflicts.append({
                    "existing_target": existing_target,
                    "existing_confidence": row[3],
                    "notes": row[4]
                })
                
        if conflicts:
            return {
                "status": "contradictory",
                "conflicts": conflicts,
                "message": f"Proposed target '{proposed_target}' differs from {len(conflicts)} established knowledge entries."
            }
            
        return {"status": "consistent", "message": "Proposed mapping aligns with existing global knowledge."}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}
