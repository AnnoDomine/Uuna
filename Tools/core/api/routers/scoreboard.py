from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from Tools.core.shared_db_instance import db

router = APIRouter(prefix="/score", tags=["scoreboard"])
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
        db.execute(sql, [str(req.task_id), str(req.event_id) if req.event_id else None, req.percent])
        return {"status": "success", "message": f"Score of {req.percent}% assigned to task {req.task_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/board")
async def get_scoreboard():
    try:
        res = db.execute("SELECT * FROM research.score_board ORDER BY created_at DESC")
        columns = res.data.get("columns", [])
        rows = res.fetchall()
        
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
            
        return {"scores": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
