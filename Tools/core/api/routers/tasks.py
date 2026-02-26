from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import json
import duckdb
import os

router = APIRouter(prefix="/tasks", tags=["tasks"])
DB_PATH = "Data/WoW_Master.duckdb"
QUERIES_PATH = "Tools/core/api/queries/tasks"


def _load_query(name: str) -> str:
    with open(os.path.join(QUERIES_PATH, f"{name}.sql"), "r") as f:
        return f.read().strip()


class TaskCreateRequest(BaseModel):
    objective: str
    initiator: str = "User"


@router.post("/create")
async def create_task(req: TaskCreateRequest):
    task_id = str(uuid.uuid4())
    sql = _load_query("create_task")
    try:
        with duckdb.connect(DB_PATH) as con:
            # Parameters: task_id, query, status, current_location, assigned_builds
            con.execute(sql, [task_id, req.objective, "OPEN", "Librarian", json.dumps(["12.0.0"])])
        return {"task_id": task_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}")
async def get_task(task_id: str):
    sql = _load_query("get_task")
    with duckdb.connect(DB_PATH) as con:
        res = con.execute(sql, [task_id]).fetchone()
        if not res:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"task": res}


@router.get("/list/all")
async def list_tasks():
    try:
        sql = _load_query("list_tasks")
        with duckdb.connect(DB_PATH) as con:
            cursor = con.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

        return {"tasks": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{task_id}/events")
async def get_task_events(task_id: str):
    try:
        sql = _load_query("get_task_events")
        with duckdb.connect(DB_PATH) as con:
            cursor = con.execute(sql, [task_id])
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

        return {"events": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{task_id}/scores")
async def get_task_scores(task_id: str):
    try:
        sql = _load_query("get_task_scores")
        with duckdb.connect(DB_PATH) as con:
            cursor = con.execute(sql, [task_id])
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

        return {"scores": result}
    except Exception:
        # Fallback empty list if table doesn't exist or other error
        return {"scores": []}
