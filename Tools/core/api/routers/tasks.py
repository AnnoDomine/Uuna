from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import json
import os
from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

router = APIRouter(prefix="/tasks", tags=["tasks"])
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
    debugger.add_log(f"API Request: Creating task for '{req.objective[:50]}...'", agent="API", process="Tasks:Create")
    sql = _load_query("create_task")
    try:
        # Parameters: task_id, query, status, current_location, assigned_builds
        db.execute(sql, [task_id, req.objective, "OPEN", "Librarian", json.dumps(["12.0.0"])])
        debugger.add_log(f"Task {task_id[:8]} created successfully.", agent="API", level="SUCCESS", process="Tasks:Create")
        return {"task_id": task_id, "status": "created"}
    except Exception as e:
        debugger.add_log(f"Failed to create task: {e}", agent="API", level="ERROR", process="Tasks:Create")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}")
async def get_task(task_id: str):
    debugger.add_log(f"API Request: Fetching Task {task_id[:8]}", agent="API", process="Tasks:Get")
    sql = _load_query("get_task")
    try:
        res = db.execute(sql, [task_id])
        row = res.fetchone()
        if not row:
            debugger.add_log(f"Task {task_id} not found.", agent="API", level="WARNING", process="Tasks:Get")
            raise HTTPException(status_code=404, detail="Task not found")
        
        columns = res.data.get("columns", [])
        return {"task": dict(zip(columns, row))}
    except HTTPException:
        raise
    except Exception as e:
        debugger.add_log(f"Error fetching task {task_id}: {e}", agent="API", level="ERROR", process="Tasks:Get")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/all")
async def list_tasks():
    debugger.add_log("API Request: Listing all tasks", agent="API", process="Tasks:ListAll")
    try:
        sql = _load_query("list_tasks")
        res = db.execute(sql)
        columns = res.data.get("columns", [])
        rows = res.fetchall()

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        return {"tasks": result}
    except Exception as e:
        debugger.add_log(f"Database error listing tasks: {e}", agent="API", level="ERROR", process="Tasks:ListAll")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{task_id}/events")
async def get_task_events(task_id: str):
    debugger.add_log(f"API Request: Fetching events for Task {task_id[:8]}", agent="API", process="Tasks:GetEvents")
    try:
        sql = _load_query("get_task_events")
        res = db.execute(sql, [task_id])
        columns = res.data.get("columns", [])
        rows = res.fetchall()

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        return {"events": result}
    except Exception as e:
        debugger.add_log(f"Database error fetching events for {task_id}: {e}", agent="API", level="ERROR", process="Tasks:GetEvents")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{task_id}/scores")
async def get_task_scores(task_id: str):
    debugger.add_log(f"API Request: Fetching scores for Task {task_id[:8]}", agent="API", process="Tasks:GetScores")
    try:
        sql = _load_query("get_task_scores")
        res = db.execute(sql, [task_id])
        columns = res.data.get("columns", [])
        rows = res.fetchall()

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        return {"scores": result}
    except Exception as e:
        debugger.add_log(f"Error fetching scores for {task_id}: {e}", agent="API", process="Tasks:GetScores")
        return {"scores": []}
