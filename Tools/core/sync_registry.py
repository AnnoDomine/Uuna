import duckdb
import os
import sys
from loguru import logger

DB_PATH = 'Data/WoW_Master.duckdb'
QUERIES_DIR = 'Tools/core/queries/sync_registry'

# UNIFIED LOG SCHEMA
logger.remove()
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
logger.add("Data/logs/migration.log", format=LOG_FORMAT, rotation="10 MB", level="DEBUG")

def load_query(name):
    path = os.path.join(QUERIES_DIR, f"{name}.sql")
    with open(path, 'r') as f:
        return f.read().strip()

def sync_registry():
    log = logger.bind(run_info="SYNC", process="RegistrySync", build="ALL")
    log.info("Starting Registry Sync with Archive...")
    
    if not os.path.exists(DB_PATH):
        log.error(f"Master DB not found at {DB_PATH}")
        return

    con = duckdb.connect(DB_PATH)
    sql_update = load_query("update_downloaded_flag")
    con.execute(sql_update)
    
    sql_stats = load_query("get_registry_stats")
    stats = con.execute(sql_stats).fetchone()
    
    total, downloaded, indexed = stats
    log.success(f"Sync OK: {downloaded}/{total} builds available, {indexed} indexed.")
    con.close()

if __name__ == "__main__":
    sync_registry()
