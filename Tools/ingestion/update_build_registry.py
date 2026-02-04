import duckdb
import requests
import os
import sys
from loguru import logger

MASTER_DB = 'Data/WoW_Master.duckdb'
API_URL = 'https://wago.tools/api/builds'

# Configure Loguru
logger.remove()
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"
logger.add(sys.stderr, format=LOG_FORMAT)

def get_con():
    return duckdb.connect(MASTER_DB)

def fetch_versions():
    log = logger.bind(run_info="FETCH", process="Registry", build="ALL")
    log.info(f"Fetching available builds from {API_URL}...")
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.error(f"Error fetching versions: {e}")
    return []

def update_registry(builds_dict=None):
    log = logger.bind(run_info="UPDATE", process="Registry", build="ALL")
    if not builds_dict: return

    con = get_con()
    count = 0
    
    for product_name, entries in builds_dict.items():
        for entry in entries:
            ver_str = entry.get('version')
            if ver_str:
                try:
                    build_num = int(ver_str.split('.')[-1])
                    # UPSERT into DuckDB
                    con.execute('''
                        INSERT INTO registry.builds (id, version, product, last_seen) 
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT (version) DO UPDATE SET 
                            last_seen = CURRENT_TIMESTAMP,
                            product = excluded.product
                    ''', (build_num, ver_str, product_name))
                    count += 1
                except: continue
    
    con.commit()
    log.success(f"Registry updated: {count} entries processed in Master DB.")
    con.close()

if __name__ == "__main__":
    data = fetch_versions()
    update_registry(data)
