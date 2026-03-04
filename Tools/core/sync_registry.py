import duckdb
import os
from Tools.core.shared_debugger import debugger

DB_PATH = "Data/WoW_Master.duckdb"
QUERIES_DIR = "Tools/core/queries/sync_registry"


def load_query(name):
    path = os.path.join(QUERIES_DIR, f"{name}.sql")
    with open(path, "r") as f:
        return f.read().strip()


def sync_registry():
    debugger.add_log("Starting Registry Sync with Archive...", agent="CORE", process="RegistrySync")

    if not os.path.exists(DB_PATH):
        debugger.add_log(f"Master DB not found at {DB_PATH}", agent="CORE", level="ERROR", process="RegistrySync")
        return

    con = duckdb.connect(DB_PATH)
    sql_update = load_query("update_downloaded_flag")
    con.execute(sql_update)

    sql_stats = load_query("get_registry_stats")
    stats = con.execute(sql_stats).fetchone()

    total, downloaded, indexed = stats
    debugger.add_log(f"Sync OK: {downloaded}/{total} builds available, {indexed} indexed.", agent="CORE", level="SUCCESS", process="RegistrySync")
    con.close()


if __name__ == "__main__":
    sync_registry()
