import os
import re
import zipfile
import shutil
import duckdb
from Tools.core.shared_debugger import debugger

# Config
DB_PATH = os.path.abspath("Data/WoW_Master.duckdb")
DBS_DIR = os.path.abspath("Data/dbs")
ARCHIVE_DIR = os.path.abspath("Data/backups/archived_sqlite")


def archive_database(file_path):
    if not os.path.exists(file_path):
        return False
    base_name = os.path.basename(file_path)
    zip_name = f"{base_name}.zip"
    zip_temp_path = os.path.join(DBS_DIR, zip_name)
    target_path = os.path.join(ARCHIVE_DIR, zip_name)

    try:
        debugger.add_log(f"Archiving {base_name}...", agent="MIGRATOR", process="Archive")
        with zipfile.ZipFile(zip_temp_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, base_name)
        if os.path.exists(target_path):
            os.remove(target_path)
        shutil.move(zip_temp_path, target_path)
        for suffix in ["", "-shm", "-wal"]:
            f = file_path + suffix
            if os.path.exists(f):
                os.remove(f)
        return True
    except Exception as e:
        debugger.add_log(f"Archive failed for {base_name}: {e}", agent="MIGRATOR", level="ERROR", process="Archive")
        return False


def migrate():
    debugger.add_log(">>> Starting Robust Sequential Migration <<<", agent="MIGRATOR", process="Migration")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    files = [f for f in os.listdir(DBS_DIR) if re.match(r"WoW_Data_(\d+\.\d+\.\d+\.\d+)\.db$", f)]
    files.sort()

    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS archive")
    con.execute("CREATE SCHEMA IF NOT EXISTS registry")
    con.execute(
        "CREATE TABLE IF NOT EXISTS archive.build_data_map (build_id INTEGER, table_name VARCHAR, row_hash VARCHAR)"
    )

    for db_file in files:
        file_path = os.path.join(DBS_DIR, db_file)
        version = re.search(r"WoW_Data_(\d+\.\d+\.\d+\.\d+)\.db", db_file).group(1)

        debugger.add_log(f"Processing Build {version}...", agent="MIGRATOR", process="Migration", build=version)
        alias = "src"

        try:
            con.execute(f"ATTACH '{file_path}' AS {alias} (TYPE SQLITE, READ_ONLY)")
            tables = con.execute(
                f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{alias}'"
            ).fetchall()

            res = con.execute("SELECT id FROM registry.builds WHERE version = ?", [version]).fetchone()
            if not res:
                debugger.add_log(f"Build {version} not in registry. Skipping migration.", agent="MIGRATOR", level="WARNING", process="Migration", build=version)
                con.execute(f"DETACH {alias}")
                continue
            build_id = res[0]

            for (table_name,) in tables:
                if table_name.startswith("sqlite_"):
                    continue

                # 1. Create table in archive if not exists
                con.execute(
                    f"CREATE TABLE IF NOT EXISTS archive.{table_name} AS SELECT * FROM {alias}.{table_name} LIMIT 0"
                )

                # 2. Get columns from the SOURCE (SQLite)
                src_cols = [c[0] for c in con.execute(f"DESCRIBE {alias}.{table_name}").fetchall()]
                col_list = ", ".join([f'"{c}"' for c in src_cols])

                # 3. Ensure _row_hash exists in TARGET (DuckDB)
                target_cols = [c[0] for c in con.execute(f"DESCRIBE archive.{table_name}").fetchall()]
                if "_row_hash" not in target_cols:
                    con.execute(f"ALTER TABLE archive.{table_name} ADD COLUMN _row_hash VARCHAR")

                # 4. Insert data using ONLY the common columns
                if "_row_hash" in src_cols:
                    # Full deduplicated insert
                    con.execute(f"""
                        INSERT INTO archive.{table_name} 
                        SELECT * FROM {alias}.{table_name} 
                        WHERE _row_hash NOT IN (SELECT _row_hash FROM archive.{table_name})
                    """)
                    con.execute(
                        f"INSERT INTO archive.build_data_map (build_id, table_name, row_hash) SELECT {build_id}, '{table_name}', _row_hash FROM {alias}.{table_name}"
                    )
                else:
                    # Fallback if _row_hash is missing in source
                    debugger.add_log(f"Missing hash for {table_name} in {version}", agent="MIGRATOR", level="WARNING", process="Migration", build=version)
                    con.execute(
                        f"INSERT INTO archive.{table_name} ({col_list}) SELECT {col_list} FROM {alias}.{table_name}"
                    )

            con.execute(f"DETACH {alias}")
            archive_database(file_path)
            debugger.add_log(f"Migration of Build {version} successful.", agent="MIGRATOR", level="SUCCESS", process="Migration", build=version)

        except Exception as e:
            debugger.add_log(f"Migration failed for {version}: {e}", agent="MIGRATOR", level="ERROR", process="Migration", build=version)
            try:
                con.execute(f"DETACH {alias}")
            except Exception:
                pass

    con.close()
    debugger.add_log("Robust migration finished.", agent="MIGRATOR", level="SUCCESS", process="Migration")


if __name__ == "__main__":
    migrate()
