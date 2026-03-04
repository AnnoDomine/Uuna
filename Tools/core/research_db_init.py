import sqlite3
import os
from Tools.core.shared_debugger import debugger

DB_PATH = "Data/dbs/WoW_Research_Knowledge.db"


def init_research_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Builds Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Features Table (Statistical Signatures)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS column_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            build_id INTEGER,
            table_name TEXT,
            column_name TEXT,
            data_type TEXT,
            distinct_ratio REAL,
            min_val TEXT,
            max_val TEXT,
            null_ratio REAL,
            FOREIGN KEY(build_id) REFERENCES builds(id),
            UNIQUE(build_id, table_name, column_name)
        )
    """)

    # 3. Statistical Predictions (Cross-Refs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistical_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_id INTEGER,
            target_table TEXT,
            confidence REAL,
            FOREIGN KEY(feature_id) REFERENCES column_features(id)
        )
    """)

    # 4. Global AI Knowledge (Learned Truths)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            column_pattern TEXT,
            source_table_context TEXT,
            target_table TEXT,
            confidence REAL,
            confirmations INTEGER DEFAULT 1,
            contradictions INTEGER DEFAULT 0,
            last_verified_build TEXT,
            ai_notes TEXT,
            UNIQUE(column_pattern, source_table_context, target_table)
        )
    """)

    # 5. AI Agent Settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT
        )
    """)

    # Default Settings
    defaults = [
        ("cooldown", "4.0", "Pause between AI calls in seconds"),
        ("threads", "4", "Number of threads for Ollama"),
        ("limit_per_build", "5", "Max columns to analyze per build session"),
        ("debug", "0", "Enable verbose logging (0 or 1)"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO ai_settings (key, value, description) VALUES (?, ?, ?)", defaults)

    # 6. AI In-game Discoveries (Lore, Bosses, Context)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_discoveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            build_id INTEGER,
            table_name TEXT,
            column_name TEXT,
            discovery TEXT,
            confidence REAL,
            FOREIGN KEY(build_id) REFERENCES builds(id)
        )
    """)

    # Indices for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_table ON column_features(table_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_features_col ON column_features(column_name)")

    conn.commit()
    conn.close()
    debugger.add_log(f"Research Knowledge DB initialized: {DB_PATH}", agent="CORE", process="Init:ResearchDB")


if __name__ == "__main__":
    init_research_db()
