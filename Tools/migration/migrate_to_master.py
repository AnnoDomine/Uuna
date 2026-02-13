import os
import re
import sys
import zipfile
import shutil
import duckdb
from loguru import logger

# Config
DB_PATH = os.path.abspath('Data/WoW_Master.duckdb')
DBS_DIR = os.path.abspath("Data/dbs")
ARCHIVE_DIR = os.path.abspath("Data/backups/archived_sqlite")
LOG_FILE = os.path.abspath("Data/logs/migration.log")

# Configure Logger
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add(LOG_FILE, rotation="10 MB", level="DEBUG")

def archive_database(file_path):
    if not os.path.exists(file_path): return False
    base_name = os.path.basename(file_path)
    zip_name = f"{base_name}.zip"
    zip_temp_path = os.path.join(DBS_DIR, zip_name)
    target_path = os.path.join(ARCHIVE_DIR, zip_name)

    try:
        logger.info(f"  -> Archiving {base_name}...")
        with zipfile.ZipFile(zip_temp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, base_name)
        if os.path.exists(target_path): os.remove(target_path)
        shutil.move(zip_temp_path, target_path)
        for suffix in ["", "-shm", "-wal"]:
            f = file_path + suffix
            if os.path.exists(f): os.remove(f)
        return True
    except Exception as e:
        logger.error(f"  -> Archive failed: {e}")
        return False

def migrate():
    logger.info(">>> Starting Robust Sequential Migration <<<")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    files = [f for f in os.listdir(DBS_DIR) if re.match(r"WoW_Data_(\d+\.\d+\.\d+\.\d+)\.db$", f)]
    files.sort()

    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS archive")
    con.execute("CREATE SCHEMA IF NOT EXISTS registry")
    con.execute("CREATE TABLE IF NOT EXISTS archive.build_data_map (build_id INTEGER, table_name VARCHAR, row_hash VARCHAR)")

    for db_file in files:
        file_path = os.path.join(DBS_DIR, db_file)
        version = re.search(r"WoW_Data_(\d+\.\d+\.\d+\.\d+)\.db", db_file).group(1)
        
        logger.info(f"Processing Build {version}...")
        alias = "src"
        
        try:
            con.execute(f"ATTACH '{file_path}' AS {alias} (TYPE SQLITE, READ_ONLY)")
            tables = con.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{alias}'").fetchall()
            
            res = con.execute("SELECT id FROM registry.builds WHERE version = ?", [version]).fetchone()
            if not res:
                con.execute(f"DETACH {alias}")
                continue
            build_id = res[0]

            for (table_name,) in tables:
                if table_name.startswith('sqlite_'): continue
                
                # 1. Create table in archive if not exists
                con.execute(f"CREATE TABLE IF NOT EXISTS archive.{table_name} AS SELECT * FROM {alias}.{table_name} LIMIT 0")
                
                # 2. Get columns from the SOURCE (SQLite)
                src_cols = [c[0] for c in con.execute(f"DESCRIBE {alias}.{table_name}").fetchall()]
                col_list = ", ".join([f'"{c}"' for c in src_cols])
                
                # 3. Ensure _row_hash exists in TARGET (DuckDB)
                target_cols = [c[0] for c in con.execute(f"DESCRIBE archive.{table_name}").fetchall()]
                if "_row_hash" not in target_cols:
                    con.execute(f"ALTER TABLE archive.{table_name} ADD COLUMN _row_hash VARCHAR")

                # 4. Insert data using ONLY the common columns
                # We assume SQLite has _row_hash because feature_extractor adds it. 
                # If not, the SELECT * from source would fail if we expect it.
                # Let's check if source has it
                if "_row_hash" in src_cols:
                    # Full deduplicated insert
                    con.execute(f"""
                        INSERT INTO archive.{table_name} 
                        SELECT * FROM {alias}.{table_name} 
                        WHERE _row_hash NOT IN (SELECT _row_hash FROM archive.{table_name})
                    """)
                    con.execute(f"INSERT INTO archive.build_data_map (build_id, table_name, row_hash) SELECT {build_id}, '{table_name}', _row_hash FROM {alias}.{table_name}")
                else:
                    # Fallback if _row_hash is missing in source (should not happen normally)
                    logger.warning(f"  [MISSING HASH] {table_name} in {version}")
                    con.execute(f"INSERT INTO archive.{table_name} ({col_list}) SELECT {col_list} FROM {alias}.{table_name}")

            con.execute(f"DETACH {alias}")
            archive_database(file_path)
            logger.success(f"  [OK] {version}")

        except Exception as e:
            logger.error(f"  [FAIL] {version}: {e}")
            try: con.execute(f"DETACH {alias}")
            except: pass

    con.close()

if __name__ == "__main__":
    migrate()