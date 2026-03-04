from contextlib import asynccontextmanager
import os
from typing import Any, List

import duckdb
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from Tools.core.shared_debugger import debugger

DB_PATH = os.getenv("WOW_DB_PATH", "Data/WoW_Master.duckdb")
con = None


@asynccontextmanager
async def lifespan(app: FastAPI):
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
        debugger.add_log(f"DB Service ready at {abs_db_path} (Security Checks Disabled)", agent="DB_SERVICE", process="Lifespan")
    except Exception as e:
        debugger.add_log(f"STARTUP ERROR: {e}", agent="DB_SERVICE", level="ERROR", process="Lifespan")
        # Ensure we don't proceed with a broken connection object if it was partially initialized
        con = None
    
    yield
    
    # Cleanup on shutdown
    if con:
        try:
            con.close()
            debugger.add_log("Database connection closed.", agent="DB_SERVICE", process="Shutdown")
        except Exception as e:
            debugger.add_log(f"Error during shutdown: {e}", agent="DB_SERVICE", level="ERROR", process="Shutdown")

app = FastAPI(title="WoW Datamine DB Service", lifespan=lifespan)

# CORS configuration for local frontend access
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    sql: str
    params: List[Any] = []


@app.post("/query")
async def run_query(req: QueryRequest):
    global con
    if con is None:
        return JSONResponse(status_code=503, content={"detail": "Database not initialized"})

    try:
        # Use the main connection directly for better consistency
        debugger.add_log(f"QUERY: {req.sql} | PARAMS: {req.params}", agent="DB_SERVICE", process="API:Query")
        res_obj = con.execute(req.sql, req.params)
        cols = [desc[0] for desc in res_obj.description] if res_obj.description else []
        res = res_obj.fetchall()
        return {"columns": cols, "results": res}
    except Exception as e:
        import traceback
        debugger.add_log(f"QUERY ERROR: {e}\n{traceback.format_exc()}", agent="DB_SERVICE", level="ERROR", process="API:Query")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/execute")
async def run_execute(req: QueryRequest):
    global con
    if con is None:
        return JSONResponse(status_code=503, content={"detail": "Database not initialized"})

    try:
        debugger.add_log(f"EXECUTE: {req.sql} | PARAMS: {req.params}", agent="DB_SERVICE", process="API:Execute")
        res_obj = con.execute(req.sql, req.params)
        # Explicitly commit to ensure visibility across different handles/processes
        con.commit()

        # Return results even for execute, just in case it was a misrouted query
        cols = [desc[0] for desc in res_obj.description] if res_obj.description else []
        res = res_obj.fetchall() if res_obj.description else []

        return {"status": "success", "columns": cols, "results": res}
    except Exception as e:
        import traceback
        debugger.add_log(f"EXECUTE ERROR: {e}\n{traceback.format_exc()}", agent="DB_SERVICE", level="ERROR", process="API:Execute")
        return JSONResponse(status_code=500, content={"detail": str(e)})


# Health check endpoint for frontend and AI tools
@app.get("/health")
async def run_health():
    global con
    if con is not None:
        return {"status": "ok", "database": "connected", "path": DB_PATH}
    return JSONResponse(status_code=503, content={"status": "error", "database": "disconnected"})


if __name__ == "__main__":
    # Use the app object directly to avoid module resolution issues
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="debug")
