import sys
import os

# Ensure path resolution for core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Tools.core.db_client import DBClient
from Tools.core.shared_debugger import debugger

DB_SERVICE_URL = "http://127.0.0.1:8002"


def set_setting(key, value):
    db_client = DBClient(url=DB_SERVICE_URL)

    # Update DuckDB registry.settings
    # Using UPSERT pattern for DuckDB
    sql = """
    INSERT INTO registry.settings (key, value) 
    VALUES (?, ?) 
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """
    try:
        db_client.execute(sql, [key, str(value)])
        debugger.add_log(f"Setting '{key}' updated to '{value}' in DuckDB registry.", agent="CORE", process="Settings:Update")
    except Exception as e:
        debugger.add_log(f"Error updating setting in DuckDB: {e}", agent="CORE", level="ERROR", process="Settings:Update")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        debugger.add_log("Usage: python update_settings.py <key> <value>", agent="CORE", level="ERROR", process="Settings:CLI")
        sys.exit(1)

    key = sys.argv[1]
    value = sys.argv[2]

    if key == "workers" and int(value) < 1:
        debugger.add_log("Error: workers must be at least 1.", agent="CORE", level="ERROR", process="Settings:CLI")
        sys.exit(1)

    set_setting(key, value)
