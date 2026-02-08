from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import duckdb
import os

router = APIRouter(prefix="/settings", tags=["settings"])
DB_PATH = 'Data/WoW_Master.duckdb'
QUERIES_PATH = "Tools/core/api/queries/settings"

def _load_query(name: str) -> str:
    with open(os.path.join(QUERIES_PATH, f"{name}.sql"), 'r') as f:
        return f.read().strip()

class SettingUpdate(BaseModel):
    key: str
    value: str

@router.get("/list")
async def list_settings():
    sql = _load_query("get_settings")
    try:
        with duckdb.connect(DB_PATH) as con:
            res = con.execute(sql).fetchall()
            return {"settings": [{"key": r[0], "value": r[1], "description": r[2]} for r in res]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update")
async def update_setting(req: SettingUpdate):
    sql = _load_query("update_setting")
    try:
        with duckdb.connect(DB_PATH) as con:
            con.execute(sql, [req.value, req.key])
        return {"status": "success", "message": f"Setting {req.key} updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
