from fastapi import APIRouter, HTTPException
import duckdb
import os

router = APIRouter(prefix="/logs", tags=["logs"])
DB_PATH = "Data/WoW_Master.duckdb"
QUERIES_PATH = "Tools/core/api/queries/logs"


def _load_query(name: str) -> str:
    with open(os.path.join(QUERIES_PATH, f"{name}.sql"), "r") as f:
        return f.read().strip()


@router.get("/latest")
async def get_latest_logs(limit: int = 50):
    sql = _load_query("get_latest_logs")
    try:
        with duckdb.connect(DB_PATH) as con:
            res = con.execute(sql, [limit]).fetchall()
            # Convert to list of dicts for easier consumption
            logs = []
            for row in res:
                logs.append(
                    {
                        "timestamp": row[0].strftime("%Y-%m-%d %H:%M:%S") if row[0] else "N/A",
                        "role": row[1],
                        "message": row[2],
                    }
                )
            return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
