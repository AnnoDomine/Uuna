import duckdb
import os
import subprocess
import time
import sys
from loguru import logger

MASTER_DB = "Data/WoW_Master.duckdb"
QUERIES_DIR = "Tools/analysis/queries/mass_indexer"

# UNIFIED LOG SCHEMA
logger.remove()
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
logger.add("Data/logs/migration.log", format=LOG_FORMAT, rotation="10 MB", level="DEBUG")


def get_con():
    return duckdb.connect(MASTER_DB)


def load_query(name):
    path = os.path.join(QUERIES_DIR, f"{name}.sql")
    with open(path, "r") as f:
        return f.read().strip()


def run_mass_indexing(start_v=None, end_v=None):
    base_log = logger.bind(run_info="INIT", process="MassIndexer", build="ALL")
    base_log.info("Starting Batch Indexing...")

    con = get_con()
    sql_get_pending = load_query("get_pending_builds")
    sql_get_all_versions = load_query("get_all_versions")

    all_pending = [r[0] for r in con.execute(sql_get_pending).fetchall()]
    if not all_pending:
        base_log.bind(run_info="DONE").info("No pending builds found.")
        con.close()
        return

    all_versions = [r[0] for r in con.execute(sql_get_all_versions).fetchall()]
    con.close()

    start_idx = all_versions.index(start_v) if start_v in all_versions else 0
    end_idx = all_versions.index(end_v) if end_v in all_versions else len(all_versions) - 1

    to_process = [v for v in all_pending if v in all_versions[start_idx : end_idx + 1]]
    total = len(to_process)
    base_log.info(f"Queue: {total} builds.")

    for idx, version in enumerate(to_process, 1):
        run_info = f"{idx}/{total}"
        b_log = logger.bind(run_info=run_info, process="Indexing", build=version)

        start_time = time.time()
        try:
            # Execute feature_extractor as subprocess
            result = subprocess.run(
                [".venv/bin/python3", "Tools/analysis/feature_extractor.py", version], capture_output=True, text=True
            )
            elapsed = time.time() - start_time
            if result.returncode == 0:
                b_log.success(f"Build completed in {elapsed:.1f}s")
            else:
                b_log.error(f"Failed: {result.stderr}")
        except Exception as e:
            b_log.error(f"Error: {e}")

    base_log.bind(run_info="DONE").info("All tasks finished.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    args = parser.parse_args()
    run_mass_indexing(args.start, args.end)
