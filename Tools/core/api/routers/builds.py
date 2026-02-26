import os
import sys
import time

from fastapi import APIRouter, HTTPException
from loguru import logger

from Tools.core.db_client import DBClient

logger.remove()
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]}]: {message}"


def sink_filter(record):
    for key in ["run_info", "process"]:
        if key not in record["extra"]:
            record["extra"][key] = "N/A"
    return True


logger.add(sys.stderr, format=LOG_FORMAT, filter=sink_filter)
session_ts = time.strftime("%Y%m%d_%H%M%S")
logger.add(
    f"Data/logs/log_{session_ts}.log",
    format=LOG_FORMAT,
    filter=sink_filter,
    rotation="10 MB",
)

router = APIRouter(prefix="/builds", tags=["builds"])
DB_PATH = "Data/WoW_Master.duckdb"
QUERIES_PATH = "Tools/core/api/queries/builds"


def get_safe_log(run_info="FETCH BUILD LIST", process="DB", **kwargs):
    return logger.bind(run_info=run_info, process=process, **kwargs)


def _load_query(name: str) -> str:
    with open(os.path.join(QUERIES_PATH, f"{name}.sql"), "r") as f:
        return f.read().strip()


@router.get("/list/all")
async def list_builds():
    """ """
    db = DBClient(url="http://127.0.0.1:8002")
    get_safe_log(message="Start fetching list of builds")
    try:
        sql = _load_query("list_builds")
        res = db.execute(sql=sql)
        columns = res.data.get("columns", [])
        rows = res.fetchall()
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        get_safe_log(message=f"List: {str(rows)}")

        return {"builds": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while fetching build list: {str(e)}")
