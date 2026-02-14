# Tools/toolsets/tools/registry/check_build_status.py
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "check_build_status"


def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def check_build_status(db_client: DBClient, build_version: str) -> Dict[str, Any]:
    """
    Checks if a specific build is available (downloaded) and indexed in the master archive.
    This information is vital for the Librarian to decide if research can be performed.
    """
    try:
        sql = _load_query("get_build_status")
        res = db_client.execute(sql, [build_version]).fetchone()

        if not res:
            return {
                "version": build_version,
                "exists": False,
                "is_downloaded": False,
                "is_indexed": False,
                "message": f"Build {build_version} is unknown to the registry.",
            }

        version, is_downloaded, is_indexed = res
        return {
            "version": version,
            "exists": True,
            "is_downloaded": bool(is_downloaded),
            "is_indexed": bool(is_indexed),
            "message": "Build is ready." if is_downloaded and is_indexed else "Build is not fully available yet.",
        }
    except Exception as e:
        return {"error": str(e), "exists": False}
