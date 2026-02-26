import duckdb
import os
import sys
import sqlite3
import gzip
import shutil
from loguru import logger

MASTER_DB = "Data/WoW_Master.duckdb"
SQLITE_DIR = "Data/dbs"

# Configure Loguru
logger.remove()
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"
logger.add(sys.stderr, format=LOG_FORMAT)


def get_con():
    return duckdb.connect(MASTER_DB)


def get_all_builds_list():
    con = get_con()
    df = con.execute("SELECT id, version, product, is_downloaded FROM registry.builds ORDER BY id ASC").df()
    con.close()
    return df


def select_build_interactively(df, prompt_text):
    page_size = 5
    current_page = 0
    total_pages = (len(df) + page_size - 1) // page_size
    while True:
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(df))
        print(f"\n--- {prompt_text} (Page {current_page + 1}/{total_pages}) ---")
        for i in range(start_idx, end_idx):
            row = df.iloc[i]
            status = "[Archived]" if row["is_downloaded"] else "[Missing]"
            print(f"  {i + 1}) {row['version']} ({row['product']}) {status}")
        print("\nCommands: [Number] Select, [N] Next, [P] Previous, [Q] Quit")
        choice = input("Choice: ").strip().lower()
        if choice == "n" and current_page < total_pages - 1:
            current_page += 1
        elif choice == "p" and current_page > 0:
            current_page -= 1
        elif choice == "q":
            sys.exit(0)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(df):
                return df.iloc[idx]["version"]
        else:
            print("Invalid input.")


def cleanup_local_db(version, run_info):
    log = logger.bind(run_info=run_info, process="Cleanup", build=version)
    old_path = os.path.join(SQLITE_DIR, f"WoW_Data_{version}.db")
    backup_dir = "Data/backups/archived_sqlite"
    os.makedirs(backup_dir, exist_ok=True)
    new_path = os.path.join(backup_dir, f"WoW_Data_{version}.db.gz")
    if not os.path.exists(old_path):
        return
    log.info(f"Archiving to {new_path}...")
    try:
        with open(old_path, "rb") as f_in:
            with gzip.open(new_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(old_path)
        log.success("Legacy file removed successfully.")
    except Exception as e:
        log.error(f"Cleanup Error: {e}")


def process_table_local(con, table_name, sqlite_path, build_id, run_info, build_ver):
    log = logger.bind(run_info=run_info, process="Archive", build=build_ver)
    try:
        archive_table = f"archive.data_{table_name}"
        con.execute(
            f"CREATE OR REPLACE TEMP VIEW source_view AS SELECT * FROM sqlite_scan('{sqlite_path}', '{table_name}')"
        )
        row_count = con.execute("SELECT COUNT(*) FROM source_view").fetchone()[0]
        if row_count == 0:
            return True

        con.execute(f"CREATE TABLE IF NOT EXISTS {archive_table} AS SELECT * FROM source_view WHERE 1=0")
        existing_cols = [c[1] for c in con.execute(f"PRAGMA table_info('{archive_table}')").fetchall()]
        if "_row_hash" not in existing_cols:
            con.execute(f"ALTER TABLE {archive_table} ADD COLUMN _row_hash VARCHAR")
            existing_cols.append("_row_hash")

        source_cols = [c[1] for c in con.execute("PRAGMA table_info('source_view')").fetchall()]
        for col in source_cols:
            if col not in existing_cols:
                con.execute(f'ALTER TABLE {archive_table} ADD COLUMN "{col}" VARCHAR')

        hash_cols = [
            f"COALESCE(CAST(\"{c}\" AS VARCHAR), '')" for c in source_cols if c not in ("build_id", "_row_hash")
        ]
        hash_sql = " || ".join(hash_cols)
        common_cols = [f'"{c}"' for c in source_cols if c not in ("_row_hash")]
        col_list_str = ", ".join(common_cols) + ", _row_hash"

        con.execute(
            f"INSERT INTO {archive_table} ({col_list_str}) SELECT {', '.join(common_cols)}, md5({hash_sql}) as _row_hash FROM source_view WHERE md5({hash_sql}) NOT IN (SELECT _row_hash FROM {archive_table})"
        )
        con.execute(
            f"INSERT OR IGNORE INTO archive.build_data_map (build_id, table_name, row_hash) SELECT {build_id}, '{table_name}', md5({hash_sql}) FROM source_view"
        )
        return True
    except Exception as e:
        log.error(f"Error in {table_name}: {e}")
        return False


def sync_build(row, all_builds, current_count, total_count, auto_migrate=False):
    version = row["version"]
    build_id = row["id"]
    run_info = f"{current_count}/{total_count}"
    log = logger.bind(run_info=run_info, process="Sync", build=version)
    sqlite_path = os.path.join(SQLITE_DIR, f"WoW_Data_{version}.db")

    log.info(f">>> Processing {version} ({row['product']}) <<<")

    use_local = False
    if os.path.exists(sqlite_path):
        size_kb = os.path.getsize(sqlite_path) // 1024
        if size_kb >= 24000 or auto_migrate:
            log.info(f"Local DB used ({size_kb} KB).")
            use_local = True
        else:
            log.warning(f"Local DB small ({size_kb} KB).")
            if input(f"  [?] Use {version} anyway? [y/N]: ").lower() == "y":
                use_local = True

    con = get_con()
    con.execute("INSTALL sqlite; LOAD sqlite;")
    if use_local:
        lite_con = sqlite3.connect(sqlite_path)
        tables = [
            r[0]
            for r in lite_con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if r[0] not in ("builds", "sqlite_sequence")
        ]
        lite_con.close()
        done = sum(1 for t in tables if process_table_local(con, t, sqlite_path, build_id, run_info, version))
        log.info(f"Result: {done}/{len(tables)} tables migrated.")
        if done == len(tables) and len(tables) > 0:
            cleanup_local_db(version, run_info)
    else:
        log.info("Downloading from Wago.tools (Not yet fully implemented for DuckDB)...")
        # Placeholder for future remote logic
        pass

    con.execute("UPDATE registry.builds SET is_downloaded = TRUE WHERE id = ?", (build_id,))
    con.close()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--auto-migrate", action="store_true")
    args = parser.parse_args()
    from master_db_init import init_master

    init_master()
    df = get_all_builds_list()
    start_v = args.start if args.start else select_build_interactively(df, "Select START Build")
    end_v = args.end if args.end else select_build_interactively(df, "Select END Build")
    start_idx = df[df["version"] == start_v].index[0]
    end_idx = df[df["version"] == end_v].index[0]
    if start_idx > end_idx:
        start_idx, end_idx = end_idx, start_idx
    target_builds = df.iloc[start_idx : end_idx + 1]
    total_to_process = len(target_builds)
    log = logger.bind(run_info="INIT", process="Main", build="ALL")
    log.info(f"Starting sync for {total_to_process} builds...")
    for i, (_, row) in enumerate(target_builds.iterrows(), 1):
        sync_build(row, df, i, total_to_process, auto_migrate=args.auto_migrate)


if __name__ == "__main__":
    main()
