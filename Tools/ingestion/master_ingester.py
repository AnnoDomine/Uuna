import duckdb
import os
import sys
import requests
import re
import json
import time
import subprocess
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

# CONFIG
MASTER_DB = 'Data/WoW_Master.duckdb'
CSV_TEMP_DIR = 'Data/DB2_CSV'
QUERIES_DIR = 'Tools/ingestion/queries/master_ingester'
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"

# LOGGING
logger.remove()
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
logger.add("Data/logs/master_ingester.log", format=LOG_FORMAT, rotation="10 MB")
base_logger = logger.bind(run_info="START", process="MasterIngester", build="INIT")

def get_con():
    return duckdb.connect(MASTER_DB)

def load_query(name):
    path = os.path.join(QUERIES_DIR, f"{name}.sql")
    with open(path, 'r') as f:
        return f.read().strip()

def fetch_wago_builds():
    try:
        r = requests.get('https://wago.tools/db2', timeout=10)
        r.raise_for_status()
        match = re.search(r'data-page="([^"]+)"', r.text)
        if match:
            page_data = json.loads(match.group(1).replace('&quot;', '"').replace('&amp;', '&'))
            return page_data.get('props', {}).get('builds', [])
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
            if tables: return tables
    except: pass

    # 2. HTML Fallback
    try:
        url = f"https://wago.tools/db2?build={version}"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        match = re.search(r'data-page="([^"]+)"', r.text)
        if match:
            page_data = json.loads(match.group(1).replace('&quot;', '"').replace('&amp;', '&'))
            tables_dict = page_data.get('props', {}).get('tables', {})
            # Depending on page structure, it's either a list or a dict
            if isinstance(tables_dict, dict):
                return list(tables_dict.values())
            elif isinstance(tables_dict, list):
                return [t.get('name') if isinstance(t, dict) else t for t in tables_dict]
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
        if res > 0: new_count += 1
    con.close()
    base_logger.info(f"Registry Sync: Added {new_count} new builds from Wago.")

def process_table_master(table, version, build_id):
    if not table: return False
    csv_path = os.path.join(CSV_TEMP_DIR, f"{table}_{version}.csv")
    url = f"https://wago.tools/db2/{table}/csv?build={version}"
    t_log = logger.bind(process="Ingestion", build=version, run_info=table)
    
    try:
        r = requests.get(url, timeout=60)
        if r.status_code != 200: return False
        if len(r.content) < 10: return False
        
        with open(csv_path, 'wb') as f:
            f.write(r.content)
            
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            sep = ';' if ';' in first_line and first_line.count(';') > first_line.count(',') else ','

        con = get_con()
        sql_init_temp = load_query("init_temp_table").format(csv_path=csv_path, sep=sep)
        sql_ensure_table = load_query("ensure_archive_table").format(table=table)
        sql_insert_rows = load_query("insert_unique_rows")
        sql_insert_map = load_query("insert_build_map")
        
        con.execute(sql_init_temp)
        cols_df = con.execute("PRAGMA table_info('temp_load')").df()
        col_names = [f'"{c}"' for c in cols_df['name'].tolist()]
        
        con.execute(sql_ensure_table)
        hash_expr = "md5(concat_ws('|', " + ", ".join(col_names) + "))"
        con.execute(sql_insert_rows.format(table=table, hash_expr=hash_expr))
        con.execute(sql_insert_map.format(build_id=build_id, table=table, hash_expr=hash_expr))
        
        con.close()
        if os.path.exists(csv_path): os.remove(csv_path)
        return True
    except Exception as e:
        # t_log.error(f"Failed: {e}")
        if os.path.exists(csv_path): os.remove(csv_path)
        return False

def run_ingester(limit=None):
    os.makedirs(CSV_TEMP_DIR, exist_ok=True)
    sync_registry_with_wago()
    
    con = get_con()
    sql_get_pending = load_query("get_pending_builds")
    if limit: sql_get_pending += f" LIMIT {limit}"
    
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
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda t: process_table_master(t, version, b_id), tables)

        con = get_con()
        con.execute(sql_mark_done, (b_id,))
        con.close()
        
        b_log.info("Triggering Indexer...")
        subprocess.run([".venv/bin/python3", "Tools/analysis/feature_extractor.py", version])
        b_log.success(f"Build {version} completed.")

if __name__ == "__main__":
    limit_val = os.getenv('MAX_BUILDS', '0')
    limit = int(limit_val) if limit_val.isdigit() else 0
    run_ingester(limit if limit > 0 else None)