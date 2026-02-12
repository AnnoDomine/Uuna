# Tools/toolsets/tools/system/get_verified_results.py
import json
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "get_verified_results"

def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", 'r') as f:
        return f.read().strip()

def get_verified_results(db_client: DBClient, task_id: str) -> Dict[str, Any]:
    """
    Collects all finalized and approved findings for a specific task.
    This data is used by the Librarian to construct the final answer for the user.
    """
    try:
        sql = _load_query("get_results")
        res = db_client.execute(sql, [task_id]).fetchall()
        
        findings = []
        for row in res:
            findings.append({
                "source_agent": row[1],
                "data": row[2],
                "confidence": row[3]
            })
            
        return {
            "task_id": task_id,
            "findings": findings,
            "count": len(findings)
        }
    except Exception as e:
        return {"error": str(e), "findings": []}
