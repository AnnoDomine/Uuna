import os
from fastapi import APIRouter, HTTPException
from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

router = APIRouter(prefix="/builds", tags=["builds"])
QUERIES_PATH = "Tools/core/api/queries/builds"


def _load_query(name: str) -> str:
    with open(os.path.join(QUERIES_PATH, f"{name}.sql"), "r") as f:
        return f.read().strip()


@router.get("/list/all")
async def list_builds():
    """Fetches all WoW builds from the registry."""
    debugger.add_log("Start fetching list of builds", agent="API", process="Builds:ListAll")
    try:
        sql = _load_query("list_builds")
        res = db.execute(sql=sql)
        columns = res.data.get("columns", [])
        rows = res.fetchall()
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        debugger.add_log(f"Successfully fetched {len(result)} builds.", agent="API", level="SUCCESS", process="Builds:ListAll")
        return {"builds": result}

    except Exception as e:
        debugger.add_log(f"Error while fetching build list: {e}", agent="API", level="ERROR", process="Builds:ListAll")
        raise HTTPException(status_code=400, detail=f"Error while fetching build list: {str(e)}")
