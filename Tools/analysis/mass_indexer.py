import duckdb
import os
import subprocess
import time
from Tools.core.shared_debugger import debugger

MASTER_DB = "Data/WoW_Master.duckdb"
QUERIES_DIR = "Tools/analysis/queries/mass_indexer"


def get_con():
    return duckdb.connect(MASTER_DB)


def load_query(name):
    path = os.path.join(QUERIES_DIR, f"{name}.sql")
    with open(path, "r") as f:
        return f.read().strip()


def run_mass_indexing(start_v=None, end_v=None):
    debugger.add_log("Starting Batch Indexing...", agent="ANALYSIS", process="MassIndexer", build="ALL")

    con = get_con()
    sql_get_pending = load_query("get_pending_builds")
    sql_get_all_versions = load_query("get_all_versions")

    all_pending = [r[0] for r in con.execute(sql_get_pending).fetchall()]
    if not all_pending:
        debugger.add_log("No pending builds found.", agent="ANALYSIS", process="MassIndexer", build="ALL")
        con.close()
        return

    all_versions = [r[0] for r in con.execute(sql_get_all_versions).fetchall()]
    con.close()

    start_idx = all_versions.index(start_v) if start_v in all_versions else 0
    end_idx = all_versions.index(end_v) if end_v in all_versions else len(all_versions) - 1

    to_process = [v for v in all_pending if v in all_versions[start_idx : end_idx + 1]]
    total = len(to_process)
    debugger.add_log(f"Queue: {total} builds.", agent="ANALYSIS", process="MassIndexer", build="ALL")

    for idx, version in enumerate(to_process, 1):
        run_info = f"{idx}/{total}"
        debugger.add_log(f"Starting Indexing for {version}", agent="ANALYSIS", process="MassIndexer", build=version, run_info=run_info)

        start_time = time.time()
        try:
            # Execute feature_extractor as subprocess
            result = subprocess.run(
                [".venv/bin/python3", "Tools/analysis/feature_extractor.py", version], capture_output=True, text=True
            )
            elapsed = time.time() - start_time
            if result.returncode == 0:
                debugger.add_log(f"Build completed in {elapsed:.1f}s", agent="ANALYSIS", level="SUCCESS", process="MassIndexer", build=version, run_info=run_info)
            else:
                debugger.add_log(f"Failed: {result.stderr}", agent="ANALYSIS", level="ERROR", process="MassIndexer", build=version, run_info=run_info)
        except Exception as e:
            debugger.add_log(f"Error indexing {version}: {e}", agent="ANALYSIS", level="ERROR", process="MassIndexer", build=version, run_info=run_info)

    debugger.add_log("All tasks finished.", agent="ANALYSIS", level="SUCCESS", process="MassIndexer", build="ALL")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    args = parser.parse_args()
    run_mass_indexing(args.start, args.end)
