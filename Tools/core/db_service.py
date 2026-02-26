import duckdb
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Any
import uvicorn
import traceback
import os
import re

app = FastAPI(title="WoW Datamine DB Service")
DB_PATH = os.getenv("WOW_DB_PATH", "Data/WoW_Master.duckdb")
con = None

# Security configuration
FORBIDDEN_DESTRUCTIVE = re.compile(r"\b(DROP|DELETE|TRUNCATE|GRANT|REVOKE|DETACH)\b", re.IGNORECASE)
ALLOWED_QUERY_START = re.compile(r"^\s*(SELECT|PRAGMA|DESCRIBE|SHOW|EXPLAIN|WITH)\b", re.IGNORECASE)
ALLOWED_EXECUTE_START = re.compile(r"^\s*(INSERT|UPDATE|CREATE|ALTER|PRAGMA|SET)\b", re.IGNORECASE)


def validate_sql(sql: str, read_only: bool = False):
    """
    Validates SQL for potential injection and destructive operations.
    """
    clean_sql = sql.split("--")[0].strip()  # Ignore comments
    
    # 1. Block multiple statements (semicolon injection)
    if ";" in clean_sql:
        # Only allow multiple statements if they are all within the ALLOWED range
        # For simplicity, we check if it's a series of CREATE/INSERT
        statements = [s.strip() for s in clean_sql.split(";") if s.strip()]
        if len(statements) > 1:
            for s in statements:
                if read_only and not ALLOWED_QUERY_START.match(s):
                    raise HTTPException(status_code=403, detail="Forbidden multi-statement in query endpoint.")
                if not read_only and not ALLOWED_EXECUTE_START.match(s):
                    raise HTTPException(status_code=403, detail="Forbidden multi-statement in execute endpoint.")

    # 2. Check for destructive keywords (always forbidden for this API)
    if FORBIDDEN_DESTRUCTIVE.search(clean_sql):
        match = FORBIDDEN_DESTRUCTIVE.search(clean_sql).group(1)
        raise HTTPException(status_code=403, detail=f"Destructive operation '{match.upper()}' is forbidden.")

    # 3. Check allowed starts based on endpoint
    if read_only:
        if not ALLOWED_QUERY_START.match(clean_sql):
            raise HTTPException(status_code=403, detail="Only read-only operations (SELECT, PRAGMA, etc.) are allowed on the /query endpoint.")
    else:
        if not ALLOWED_EXECUTE_START.match(clean_sql):
            raise HTTPException(status_code=403, detail="Forbidden operation start in execute endpoint.")


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
        validate_sql(req.sql, read_only=True)
        
        # Use a cursor for thread safety and to avoid side effects on the main connection
        cursor = con.cursor()
        cursor.execute(req.sql, req.params)
        cols = [desc[0] for desc in cursor.description] if cursor.description else []
        res = cursor.fetchall()
        return {"columns": cols, "results": res}
    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"detail": he.detail})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/execute")
async def run_execute(req: QueryRequest):
    global con
    if con is None:
        return JSONResponse(status_code=503, content={"detail": "Database not initialized"})
    
    try:
        validate_sql(req.sql, read_only=False)
        
        cursor = con.cursor()
        cursor.execute(req.sql, req.params)
        return {"status": "success"}
    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"detail": he.detail})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(e)})


if __name__ == "__main__":
    # Use the app object directly to avoid module resolution issues
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="debug")
