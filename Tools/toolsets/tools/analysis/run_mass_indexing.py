# Tools/toolsets/tools/analysis/run_mass_indexing.py
from pathlib import Path
from typing import Any, Dict, Optional

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger
from .extract_features import extract_features_for_build

QUERY_DIR = Path(__file__).parent / "queries" / "run_mass_indexing"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def run_mass_indexing(start_v: Optional[str] = None, end_v: Optional[str] = None) -> Dict[str, Any]:
    """
    Runs feature extraction for all pending builds in a range.

    Args:
    - start_v: Optional start version string (e.g. '9.0.1.36216').
    - end_v: Optional end version string (e.g. '11.0.2.56110').
    """
    debugger.add_log("Starting Mass Indexing run.", agent="CORE", process="Analysis:MassIndexing")

    # Load queries
    sql_get_pending = _load_query("get_pending_builds")
    sql_get_all_versions = _load_query("get_all_versions")

    # Get data from DB
    all_pending_res = db.execute(sql_get_pending).fetchall()
    all_pending = [r[0] for r in all_pending_res]

    if not all_pending:
        debugger.add_log("No pending builds found.", agent="CORE", process="Analysis:MassIndexing")
        return {"status": "complete", "processed_builds": 0}

    all_versions_res = db.execute(sql_get_all_versions).fetchall()
    all_versions = [r[0] for r in all_versions_res]

    # Determine range
    start_idx = all_versions.index(start_v) if start_v in all_versions else 0
    end_idx = all_versions.index(end_v) if end_v in all_versions else len(all_versions) - 1

    to_process = [v for v in all_pending if v in all_versions[start_idx : end_idx + 1]]
    total_to_process = len(to_process)
    debugger.add_log(f"Found {total_to_process} builds in range to process.", agent="CORE", process="Analysis:MassIndexing")

    processed_count = 0
    failed_builds = []

    for idx, version in enumerate(to_process, 1):
        debugger.add_log(f"--- Processing {idx}/{total_to_process}: {version} ---", agent="CORE", process="Analysis:MassIndexing")
        try:
            # --- REPLACED SUBPROCESS WITH DIRECT TOOL CALL ---
            result = extract_features_for_build(version)
            if result.get("status") == "success":
                processed_count += 1
            else:
                failed_builds.append(version)
        except Exception as e:
            debugger.add_log(f"Unhandled exception while processing {version}: {e}", agent="CORE", level="ERROR", process="Analysis:MassIndexing")
            failed_builds.append(version)

    debugger.add_log("Mass indexing run finished.", agent="CORE", process="Analysis:MassIndexing")

    return {
        "status": "complete",
        "total_in_range": total_to_process,
        "processed_successfully": processed_count,
        "failed_builds": failed_builds,
    }
