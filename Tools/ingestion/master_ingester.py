import os
import requests
import re
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from Tools.core.db_client import DBClient
from Tools.core.security_utils import sanitize_identifier
from Tools.core.config_manager import get_config
from Tools.core.shared_debugger import debugger

# CONFIG
MASTER_DB = "Data/WoW_Master.duckdb"
CSV_TEMP_DIR = "Data/DB2_CSV"
QUERIES_DIR = "Tools/ingestion/queries/master_ingester"
DB_SERVICE_URL = "http://127.0.0.1:8002"


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
        debugger.add_log(f"Failed to fetch Wago builds: {e}", agent="INGESTER", level="ERROR", process="WagoFetch")
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
        debugger.add_log(f"API fetch failed for {version}: {e}", agent="INGESTER", level="WARNING", process="WagoFetch", build=version)
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
            if isinstance(tables_dict, dict):
                return list(tables_dict.values())
            elif isinstance(tables_dict, list):
                return [t.get("name") if isinstance(t, dict) else t for t in tables_dict]
    except Exception as e:
        debugger.add_log(f"Scraping failed for {version}: {e}", agent="INGESTER", level="ERROR", process="WagoFetch", build=version)

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
    debugger.add_log(f"Registry Sync: Added {new_count} new builds from Wago.", agent="INGESTER", level="SUCCESS", process="RegistrySync")


def process_table_master(table, version, build_id):
    if not table:
        return False
    csv_path = os.path.join(CSV_TEMP_DIR, f"{table}_{version}.csv")
    url = f"https://wago.tools/db2/{table}/csv?build={version}"

    try:
        debugger.add_log(f"Processing {table}...", agent="INGESTER", process="TableIngestion", build=version, run_info=table)
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            debugger.add_log(f"HTTP {r.status_code} for {table}", agent="INGESTER", level="ERROR", process="TableIngestion", build=version, run_info=table)
            return False
        if len(r.content) < 10:
            debugger.add_log(f"Empty response for {table}", agent="INGESTER", level="WARNING", process="TableIngestion", build=version, run_info=table)
            return False

        with open(csv_path, "wb") as f:
            f.write(r.content)

        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
            sep = ";" if ";" in first_line and first_line.count(";") > first_line.count(",") else ","

        con = get_con()
        safe_table = sanitize_identifier(table)
        temp_table = sanitize_identifier(f"tmp_{safe_table}_{version.replace('.', '_')}")

        sql_init_temp = load_query("init_temp_table").format(csv_path=csv_path, sep=sep, temp_table=f"archive.{temp_table}")
        sql_ensure_table = load_query("ensure_archive_table").format(table=safe_table, temp_table=f"archive.{temp_table}")
        sql_insert_map = load_query("insert_build_map")

        con.execute(f"DROP TABLE IF EXISTS archive.{temp_table}")
        con.execute(sql_init_temp)
        con.execute(sql_ensure_table)

        # Schema Evolution
        existing_cols_real = con.execute(f"PRAGMA table_info('archive.\"{safe_table}\"')").df()["name"].tolist()
        existing_cols_lower = {c.lower() for c in existing_cols_real}
        temp_cols_df = con.execute(f"PRAGMA table_info('archive.{temp_table}')").df()
        temp_cols = [sanitize_identifier(c) for c in temp_cols_df["name"].tolist()]

        for c in temp_cols:
            if c.lower() not in existing_cols_lower:
                debugger.add_log(f'Schema Evolution: Adding column {c} to archive."{safe_table}"', agent="INGESTER", process="SchemaEvolution", build=version)
                con.execute(f'ALTER TABLE archive."{safe_table}" ADD COLUMN "{c}" VARCHAR')

        col_list_str = ", ".join([f'"{c}"' for c in temp_cols])
        hash_expr = "md5(concat_ws('|', " + col_list_str + "))"

        insert_sql = f"""
            INSERT INTO archive."{safe_table}" ({col_list_str}, _row_hash)
            SELECT {col_list_str}, {hash_expr} as _row_hash
            FROM archive.{temp_table}
            WHERE {hash_expr} NOT IN (SELECT _row_hash FROM archive."{safe_table}")
        """
        con.execute(insert_sql)

        con.execute(
            sql_insert_map.format(
                build_id=build_id,
                table=safe_table,
                hash_expr=hash_expr,
                temp_table=f"archive.{temp_table}",
            )
        )

        con.execute(f"DROP TABLE archive.{temp_table}")
        con.close()
        
        if os.path.exists(csv_path):
            os.remove(csv_path)
        return True
    except Exception as e:
        debugger.add_log(f"Failed to process table {table}: {e}", agent="INGESTER", level="ERROR", process="TableIngestion", build=version, run_info=table)
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
        debugger.add_log(f"--- Starting Integration: {version} ---", agent="INGESTER", process="MasterIngester", build=version, run_info=run_info)

        tables = fetch_tables_for_build(version)
        if not tables:
            debugger.add_log(f"Table list fetch failed for {version}. Skipping.", agent="INGESTER", level="ERROR", process="MasterIngester", build=version)
            continue

        debugger.add_log(f"Syncing {len(tables)} tables...", agent="INGESTER", process="MasterIngester", build=version)
        config = get_config()
        with ThreadPoolExecutor(max_workers=config.ingestion.workers) as executor:
            executor.map(lambda t: process_table_master(t, version, b_id), tables)

        con = get_con()
        con.execute(sql_mark_done, (b_id,))
        con.close()

        debugger.add_log(f"Triggering Indexer for {version}...", agent="INGESTER", process="MasterIngester", build=version)
        subprocess.run(
            [".venv/bin/python3", "Tools/analysis/feature_extractor.py", version],
            env=os.environ.copy(),
        )
        debugger.add_log(f"Build {version} completed.", agent="INGESTER", level="SUCCESS", process="MasterIngester", build=version)


if __name__ == "__main__":
    limit_val = os.getenv("MAX_BUILDS", "0")
    config = get_config()
    limit = int(limit_val) if limit_val.isdigit() else 0
    debugger.add_log(f"Starting Master Ingester... (Limit: {limit}, Workers: {config.ingestion.workers})", agent="INGESTER", process="MasterIngester")
    run_ingester(limit if limit > 0 else None)
