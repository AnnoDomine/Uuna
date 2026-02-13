import sqlite3
import os

DB_DIR = "Data/dbs"
LOG_DIR = "Data/logs"
CSV_DIR = "Data/DB2_CSV"
SETTINGS_DB = os.path.join(DB_DIR, "Settings.db")
REGISTRY_DB = os.path.join(DB_DIR, "Build_Registry.db")


def init_all():
    """Initializes folders and databases with default values if they don't exist."""
    # Create directories
    for d in [DB_DIR, LOG_DIR, CSV_DIR]:
        os.makedirs(d, exist_ok=True)

    # Initialize Settings.db
    init_settings()

    # Initialize Build_Registry.db
    init_registry()


def init_settings():
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            name TEXT,
            description TEXT,
            setting_group TEXT,
            type TEXT
        )
    """)

    # Default settings
    default_settings = [
        (
            "workers",
            "4",
            "Parallel Workers",
            "Number of simultaneous table downloads and imports.",
            "Performance",
            "int",
        ),
        (
            "sync_builds_list_on_startup",
            "1",
            "Update Registry on Startup",
            "Automatically fetch the latest build list from Wago.tools when the GUI starts.",
            "Startup",
            "bool",
        ),
        (
            "map_references_use_global_mapping",
            "0",
            "Use Global Column Mapping",
            "Enable sharing learned column-to-table relationships across all builds.",
            "Mapping",
            "bool",
        ),
        (
            "map_references_auto_skip_unidentifiable",
            "0",
            "Auto-skip Unidentifiable Refs",
            "Automatically skip ambiguous columns instead of asking during mapping sessions.",
            "Mapping",
            "bool",
        ),
        ("ui_theme", "dark", "UI Theme", "Choose between dark and light mode for the interface.", "UI", "text"),
    ]

    for s in default_settings:
        c.execute(
            """
            INSERT INTO settings (key, value, name, description, setting_group, type)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO NOTHING
        """,
            s,
        )

    conn.commit()
    conn.close()


def init_registry():
    conn = sqlite3.connect(REGISTRY_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY,
            version TEXT,
            product TEXT,
            is_downloaded INTEGER DEFAULT 0,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_synced TIMESTAMP
        )
    """)

    # Simple migration: Add missing columns if they don't exist
    c.execute("PRAGMA table_info(builds)")
    columns = [col[1] for col in cursor.fetchall()] if "cursor" in locals() else [col[1] for col in c.fetchall()]
    # Re-fetch because I made a mistake in the line above (cursor vs c)
    c.execute("PRAGMA table_info(builds)")
    columns = [col[1] for col in c.fetchall()]

    if "is_downloaded" not in columns:
        c.execute("ALTER TABLE builds ADD COLUMN is_downloaded INTEGER DEFAULT 0")
    if "last_synced" not in columns:
        c.execute("ALTER TABLE builds ADD COLUMN last_synced TIMESTAMP")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_all()
    print("Project environment initialized successfully.")
