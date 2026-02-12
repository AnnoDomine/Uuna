import duckdb
import os

DB_PATH = 'Data/WoW_Master.duckdb'

def init_master():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = duckdb.connect(DB_PATH)
    
    # 1. SCHEMAS
    con.execute("CREATE SCHEMA IF NOT EXISTS registry")
    con.execute("CREATE SCHEMA IF NOT EXISTS research")
    con.execute("CREATE SCHEMA IF NOT EXISTS archive")
    
    # 2. REGISTRY (Builds & Settings)
    # Using rowid or explicit sequence for DuckDB compatibility
    con.execute("CREATE SEQUENCE IF NOT EXISTS registry.build_id_seq")
    con.execute('''
        CREATE TABLE IF NOT EXISTS registry.builds (
            id INTEGER PRIMARY KEY DEFAULT nextval('registry.build_id_seq'),
            version VARCHAR UNIQUE,
            product VARCHAR,
            is_downloaded BOOLEAN DEFAULT FALSE,
            indexed BOOLEAN DEFAULT FALSE,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    con.execute('''
        CREATE TABLE IF NOT EXISTS registry.settings (
            key VARCHAR PRIMARY KEY,
            value VARCHAR,
            description VARCHAR
        )
    ''')
    
    # Seed default settings
    default_settings = [
        ('workers', '4', 'Parallel Workers for ingestion'),
        ('ui_theme', 'dark', 'TUI Theme (dark/light)'),
        ('localisation', 'english', 'Language for user communication'),
        ('cooldown', '4.0', 'Pause between AI calls in seconds'),
        ('threads', '6', 'Number of threads for Ollama')
    ]
    for key, val, desc in default_settings:
        con.execute("INSERT OR IGNORE INTO registry.settings (key, value, description) VALUES (?, ?, ?)", [key, val, desc])
    
    # 3. RESEARCH (AI Knowledge)
    con.execute("CREATE SEQUENCE IF NOT EXISTS research.knowledge_id_seq")
    con.execute('''
        CREATE TABLE IF NOT EXISTS research.global_knowledge (
            id INTEGER PRIMARY KEY DEFAULT nextval('research.knowledge_id_seq'),
            column_pattern VARCHAR,
            source_table VARCHAR,
            target_table VARCHAR,
            confidence DOUBLE,
            confirmations INTEGER DEFAULT 1,
            ai_notes TEXT,
            last_verified_build VARCHAR,
            UNIQUE(column_pattern, source_table, target_table)
        )
    ''')
    
    con.execute("CREATE SEQUENCE IF NOT EXISTS research.discovery_id_seq")
    con.execute('''
        CREATE TABLE IF NOT EXISTS research.discoveries (
            id INTEGER PRIMARY KEY DEFAULT nextval('research.discovery_id_seq'),
            build_id INTEGER,
            table_name VARCHAR,
            column_name VARCHAR,
            discovery TEXT,
            confidence DOUBLE
        )
    ''')

    con.execute("CREATE SEQUENCE IF NOT EXISTS research.feature_id_seq")
    con.execute('''
        CREATE TABLE IF NOT EXISTS research.column_features (
            id INTEGER PRIMARY KEY DEFAULT nextval('research.feature_id_seq'),
            build_id INTEGER,
            table_name VARCHAR,
            column_name VARCHAR,
            data_type VARCHAR,
            distinct_ratio DOUBLE,
            min_val VARCHAR,
            max_val VARCHAR,
            null_ratio DOUBLE
        )
    ''')

    con.execute("CREATE SEQUENCE IF NOT EXISTS research.prediction_id_seq")
    con.execute('''
        CREATE TABLE IF NOT EXISTS research.statistical_predictions (
            id INTEGER PRIMARY KEY DEFAULT nextval('research.prediction_id_seq'),
            feature_id INTEGER,
            target_table VARCHAR,
            confidence DOUBLE,
            FOREIGN KEY(feature_id) REFERENCES research.column_features(id)
        )
    ''')

    # 4. ARCHIVE (The Heart: Row-Level Dedup)
    con.execute('''
        CREATE TABLE IF NOT EXISTS archive.build_data_map (
            build_id INTEGER,
            table_name VARCHAR,
            row_hash VARCHAR,
            PRIMARY KEY(build_id, table_name, row_hash)
        )
    ''')
    
    print(f"Master DuckDB initialized with sequences at: {DB_PATH}")
    con.close()

if __name__ == "__main__":
    init_master()