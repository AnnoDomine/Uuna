import os
import sys
import requests
import re
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from Tools.core.db_client import DBClient
from Tools.core.security_utils import sanitize_identifier
from Tools.core.config_manager import get_config

# CONFIG
MASTER_DB = "Data/WoW_Master.duckdb"
CSV_TEMP_DIR = "Data/DB2_CSV"
QUERIES_DIR = "Tools/ingestion/queries/master_ingester"
DB_SERVICE_URL = "http://127.0.0.1:8002"
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"

# LOGGING
logger.remove()
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
logger.add("Data/logs/master_ingester.log", format=LOG_FORMAT, rotation="10 MB")
base_logger = logger.bind(run_info="START", process="MasterIngester", build="INIT")


def get_con():
    return DBClient(DB_SERVICE_URL)


def load_query(name):
    path = os.path.join(QUERIES_DIR, f"{name}.sql")
    with open(path, "r") as f:
        return f.read().strip()


def fetch_wago_builds():
    try:
        r = requests.get("https://wago.tools/db2", timeout=10)
        r.raise_for_status()
        match = re.search(r'data-page="([^"]+)"', r.text)
        if match:
            page_data = json.loads(match.group(1).replace("&quot;", '"').replace("&amp;", "&"))
            return page_data.get("props", {}).get("builds", [])
    except Exception as e:
        base_logger.error(f"Failed to fetch Wago builds: {e}")
    return []


def fetch_tables_for_build(version):
    """Tries API first, then falls back to HTML scraping."""
    # 1. API Try
    try:
        api_url = f"https://wago.tools/api/db2?build={version}"
        r = requests.get(api_url, timeout=30)
        if r.status_code == 200:
            tables = r.json()
            if tables:
                return tables
    except Exception as e:
        base_logger.error(f"API fetch failed for {version}: {e}")
        pass

    # 2. HTML Fallback
    try:
        url = f"https://wago.tools/db2?build={version}"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        match = re.search(r'data-page="([^"]+)"', r.text)
        if match:
            page_data = json.loads(match.group(1).replace("&quot;", '"').replace("&amp;", "&"))
            tables_dict = page_data.get("props", {}).get("tables", {})
            # Depending on page structure, it's either a list or a dict
            if isinstance(tables_dict, dict):
                return list(tables_dict.values())
            elif isinstance(tables_dict, list):
                return [t.get("name") if isinstance(t, dict) else t for t in tables_dict]
    except Exception as e:
        base_logger.error(f"Scraping failed for {version}: {e}")

    return []


def sync_registry_with_wago():
    con = get_con()
    wago_builds = fetch_wago_builds()
    sql_upsert = load_query("upsert_build")
    new_count = 0
    for b in wago_builds:
        res = con.execute(sql_upsert, (b,)).rowcount
        if res > 0:
            new_count += 1
    con.close()
    base_logger.info(f"Registry Sync: Added {new_count} new builds from Wago.")


def process_table_master(table, version, build_id):
    if not table:
        return False
    csv_path = os.path.join(CSV_TEMP_DIR, f"{table}_{version}.csv")
    url = f"https://wago.tools/db2/{table}/csv?build={version}"
    t_log = logger.bind(process="Ingestion", build=version, run_info=table)

    try:
        t_log.info(f"Processing {table}...")
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            t_log.error(f"HTTP {r.status_code}")
            return False
        if len(r.content) < 10:
            t_log.error("Empty response")
            return False

        t_log.info(f"Writing to {csv_path}...")
        with open(csv_path, "wb") as f:
            t_log.info(f"Path found. Writing to {csv_path}...")
            f.write(r.content)

        t_log.info("Parsing CSV...")
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            t_log.info("Reading first line...")
            first_line = f.readline()
            sep = ";" if ";" in first_line and first_line.count(";") > first_line.count(",") else ","
            t_log.info(f"Detected separator: {sep}")

        con = get_con()
        t_log.info("Creating temp table...")
        # Sanitize table name and generate temp name
        safe_table = sanitize_identifier(table)
        temp_table = sanitize_identifier(f"tmp_{safe_table}_{version.replace('.', '_')}")

        sql_init_temp = load_query("init_temp_table").format(csv_path=csv_path, sep=sep, temp_table=temp_table)
        t_log.info("Ensuring table exists...")
        sql_ensure_table = load_query("ensure_archive_table").format(table=safe_table, temp_table=temp_table)
        t_log.info("Inserting rows...")
        load_query("insert_unique_rows")
        t_log.info("Inserting build map...")
        sql_insert_map = load_query("insert_build_map")

        t_log.info("Cleanup potential old temp table...")
        con.execute(f"DROP TABLE IF EXISTS archive.{temp_table}")

        con.execute(sql_init_temp)
        t_log.info("Ensuring table exists...")
        con.execute(sql_ensure_table)

        # Schema Evolution: Add missing columns (case-insensitive check)
        existing_cols_real = con.execute(f"PRAGMA table_info('archive.\"{safe_table}\"')").df()["name"].tolist()
        existing_cols_lower = {c.lower() for c in existing_cols_real}

        temp_cols_df = con.execute(f"PRAGMA table_info('archive.{temp_table}')").df()
        temp_cols = [sanitize_identifier(c) for c in temp_cols_df["name"].tolist()]

        for c in temp_cols:
            if c.lower() not in existing_cols_lower:
                t_log.info(f'Schema Evolution: Adding column {c} to archive."{safe_table}"')
                con.execute(f'ALTER TABLE archive."{safe_table}" ADD COLUMN "{c}" VARCHAR')
            elif c not in existing_cols_real:
                t_log.warning(f"Column casing mismatch for {c}. Existing: {existing_cols_real}. Skipping.")

        # Explicit column list for safe insertion
        col_list_str = ", ".join([f'"{c}"' for c in temp_cols])
        hash_expr = "md5(concat_ws('|', " + col_list_str + "))"

        t_log.info("Inserting rows...")
        insert_sql = f"""
            INSERT INTO archive."{safe_table}" ({col_list_str}, _row_hash)
            SELECT {col_list_str}, {hash_expr} as _row_hash
            FROM archive.{temp_table}
            WHERE {hash_expr} NOT IN (SELECT _row_hash FROM archive."{safe_table}")
        """
        con.execute(insert_sql)

        t_log.info("Inserting build map...")
        con.execute(
            sql_insert_map.format(
                build_id=build_id,
                table=safe_table,
                hash_expr=hash_expr,
                temp_table=f"archive.{temp_table}",
            )
        )

        t_log.info("Dropping temp table...")
        con.execute(f"DROP TABLE archive.{temp_table}")

        t_log.info("Close connection...")
        con.close()
        if os.path.exists(csv_path):
            os.remove(csv_path)
        return True
    except Exception as e:
        t_log.error(f"Failed: {e}")
        if os.path.exists(csv_path):
            os.remove(csv_path)
        return False


def run_ingester(limit=None):
    os.makedirs(CSV_TEMP_DIR, exist_ok=True)
    sync_registry_with_wago()

    con = get_con()
    sql_get_pending = load_query("get_pending_builds")
    if limit:
        sql_get_pending += f" LIMIT {limit}"

    pending = con.execute(sql_get_pending).fetchall()
    con.close()

    total_builds = len(pending)
    sql_mark_done = load_query("mark_build_downloaded")

    for idx, (version, b_id) in enumerate(pending, 1):
        run_info = f"{idx}/{total_builds}"
        b_log = logger.bind(process="MasterIngester", build=version, run_info=run_info)
        b_log.info(f"--- Starting Integration: {version} ---")

        tables = fetch_tables_for_build(version)

        if not tables:
            b_log.error("Table list fetch failed after fallback. Skipping.")
            continue

        b_log.info(f"Syncing {len(tables)} tables...")
        config = get_config()
        with ThreadPoolExecutor(max_workers=config.ingestion.workers) as executor:
            executor.map(lambda t: process_table_master(t, version, b_id), tables)

        con = get_con()
        con.execute(sql_mark_done, (b_id,))
        con.close()

        b_log.info("Triggering Indexer...")
        subprocess.run(
            [".venv/bin/python3", "Tools/analysis/feature_extractor.py", version],
            env=os.environ.copy(),
        )
        b_log.success(f"Build {version} completed.")


if __name__ == "__main__":
    limit_val = os.getenv("MAX_BUILDS", "0")
    config = get_config()
    base_logger.info(f"Starting Master Ingester... (Limit: {limit_val}, Workers: {config.ingestion.workers})")
    limit = int(limit_val) if limit_val.isdigit() else 0
    run_ingester(limit if limit > 0 else None)
