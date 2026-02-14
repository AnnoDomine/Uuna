# Tools/toolsets/tools/analysis/run_mass_indexing.py
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.db_client import DBClient
from .extract_features import extract_features_for_build

QUERY_DIR = Path(__file__).parent / "queries" / "run_mass_indexing"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def run_mass_indexing(
    db_client: DBClient, start_v: Optional[str] = None, end_v: Optional[str] = None
) -> Dict[str, Any]:
    """
    Finds all pending builds within a range and runs the feature extraction process for each.
    """
    print("INFO: Starting Mass Indexing run.")

    # Load queries
    sql_get_pending = _load_query("get_pending_builds")
    sql_get_all_versions = _load_query("get_all_versions")

    # Get data from DB
    all_pending_res = db_client.execute(sql_get_pending).fetchall()
    all_pending = [r[0] for r in all_pending_res]

    if not all_pending:
        print("INFO: No pending builds found.")
        return {"status": "complete", "processed_builds": 0}

    all_versions_res = db_client.execute(sql_get_all_versions).fetchall()
    all_versions = [r[0] for r in all_versions_res]

    # Determine range
    start_idx = all_versions.index(start_v) if start_v in all_versions else 0
    end_idx = all_versions.index(end_v) if end_v in all_versions else len(all_versions) - 1

    to_process = [v for v in all_pending if v in all_versions[start_idx : end_idx + 1]]
    total_to_process = len(to_process)
    print(f"INFO: Found {total_to_process} builds in range to process.")

    processed_count = 0
    failed_builds = []

    for idx, version in enumerate(to_process, 1):
        print(f"--- Processing {idx}/{total_to_process}: {version} ---")
        try:
            # --- REPLACED SUBPROCESS WITH DIRECT TOOL CALL ---
            result = extract_features_for_build(db_client, version)
            if result.get("status") == "success":
                processed_count += 1
            else:
                failed_builds.append(version)
        except Exception as e:
            print(f"ERROR: Unhandled exception while processing {version}: {e}")
            failed_builds.append(version)

    print("INFO: Mass indexing run finished.")

    return {
        "status": "complete",
        "total_in_range": total_to_process,
        "processed_successfully": processed_count,
        "failed_builds": failed_builds,
    }
