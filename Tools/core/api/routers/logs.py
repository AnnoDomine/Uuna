from fastapi import APIRouter, HTTPException
import os
from Tools.core.shared_db_instance import db

router = APIRouter(prefix="/logs", tags=["logs"])
QUERIES_PATH = "Tools/core/api/queries/logs"


def _load_query(name: str) -> str:
    with open(os.path.join(QUERIES_PATH, f"{name}.sql"), "r") as f:
        return f.read().strip()


@router.get("/latest")
async def get_latest_logs(limit: int = 50):
    sql = _load_query("get_latest_logs")
    try:
        res = db.execute(sql, [limit])
        rows = res.fetchall()
        
        # Convert to list of dicts for easier consumption
        logs = []
        for row in rows:
            # Assuming row[0] is the timestamp
            # If DuckDB through API returns ISO strings or datetime objects, handle accordingly
            ts = str(row[0]) if row[0] else "N/A"
            logs.append(
                {
                    "timestamp": ts,
                    "role": row[1],
                    "message": row[2],
                }
            )
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
