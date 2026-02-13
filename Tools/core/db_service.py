import duckdb
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Any
import uvicorn
import traceback
import os

app = FastAPI(title="WoW Datamine DB Service")
DB_PATH = os.getenv("WOW_DB_PATH", "Data/WoW_Master.duckdb")
con = None


@app.on_event("startup")
async def startup_event():
    global con
    try:
        # Absolute path to ensure it finds the DB
        abs_db_path = os.path.abspath(DB_PATH)
        # Ensure directory exists
        os.makedirs(os.path.dirname(abs_db_path), exist_ok=True)

        con = duckdb.connect(abs_db_path)
        con.execute("CREATE SCHEMA IF NOT EXISTS archive")
        con.execute("CREATE SCHEMA IF NOT EXISTS registry")
        con.execute("CREATE SCHEMA IF NOT EXISTS research")
        print(f"DB Service ready at {abs_db_path}")
    except Exception as e:
        print(f"STARTUP ERROR: {e}")
        traceback.print_exc()


class QueryRequest(BaseModel):
    sql: str
    params: List[Any] = []


@app.post("/query")
async def run_query(req: QueryRequest):
    global con
    if con is None:
        return JSONResponse(status_code=503, content={"detail": "Database not initialized"})
    try:
        cursor = con.cursor()
        cursor.execute(req.sql, req.params)
        cols = [desc[0] for desc in cursor.description] if cursor.description else []
        res = cursor.fetchall()
        return {"columns": cols, "results": res}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/execute")
async def run_execute(req: QueryRequest):
    global con
    if con is None:
        return JSONResponse(status_code=503, content={"detail": "Database not initialized"})
    try:
        cursor = con.cursor()
        cursor.execute(req.sql, req.params)
        return {"status": "success"}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})


if __name__ == "__main__":
    # Use the app object directly to avoid module resolution issues
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="debug")
