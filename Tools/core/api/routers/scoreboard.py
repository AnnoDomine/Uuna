from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import duckdb
import os

router = APIRouter(prefix="/score", tags=["scoreboard"])
DB_PATH = "Data/WoW_Master.duckdb"
QUERIES_PATH = "Tools/core/api/queries/scoreboard"


def _load_query(name: str) -> str:
    with open(os.path.join(QUERIES_PATH, f"{name}.sql"), "r") as f:
        return f.read().strip()


class ScoreAssignRequest(BaseModel):
    task_id: uuid.UUID
    event_id: Optional[uuid.UUID] = None
    percent: float


@router.post("/assign")
async def assign_score(req: ScoreAssignRequest):
    sql = _load_query("assign_score")
    try:
        with duckdb.connect(DB_PATH) as con:
            con.execute(sql, [str(req.task_id), str(req.event_id) if req.event_id else None, req.percent])
        return {"status": "success", "message": f"Score of {req.percent}% assigned to task {req.task_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/board")
async def get_scoreboard():
    try:
        with duckdb.connect(DB_PATH) as con:
            res = con.execute("SELECT * FROM research.score_board ORDER BY created_at DESC").fetchall()
            return {"scores": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
