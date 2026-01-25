import os
import sqlite3
import pandas as pd
import requests
import time
import re
import json

CSV_DIR = 'Data/DB2_CSV'
LOG_FILE = 'Data/logs/import_errors.log'

def init_db(version):
    db_path = f'Data/dbs/WoW_Data_{version}.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create builds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def get_or_create_build_id(conn, version):
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO builds (version) VALUES (?)', (version,))
    conn.commit()
    cursor.execute('SELECT id FROM builds WHERE version = ?', (version,))
    return cursor.fetchone()[0]

def log_error(table_name, version, error):
    os.makedirs('Data/logs', exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.ctime()}] Table: {table_name}, Build: {version}, Error: {str(error)}\n")

def fetch_available_builds():
    """Fetches the list of available builds from Wago.tools."""
    try:
        r = requests.get('https://wago.tools/db2', timeout=10)
        r.raise_for_status()
        match = re.search(r'data-page="([^"]+)"', r.text)
        if match:
            page_json_str = match.group(1).replace('&quot;', '"').replace('&amp;', '&')
            page_data = json.loads(page_json_str)
            builds = page_data.get('props', {}).get('builds', [])
            return builds # List of build strings
    except Exception as e:
        print(f"Error fetching builds: {e}")
    return []

import os
import sqlite3
import pandas as pd
import requests
import time
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from project_init import init_all

# Ensure environment is ready
init_all()

CSV_DIR = 'Data/DB2_CSV'
LOG_FILE = 'Data/logs/import_errors.log'
SETTINGS_DB = 'Data/dbs/Settings.db'

def get_setting(key, default):
    try:
        conn = sqlite3.connect(SETTINGS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    except:
        return default

def init_db(version):
    db_path = f'Data/dbs/WoW_Data_{version}.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Performance tuning for SQLite
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA synchronous=NORMAL')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def get_or_create_build_id(conn, version):
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO builds (version) VALUES (?)', (version,))
    conn.commit()
    cursor.execute('SELECT id FROM builds WHERE version = ?', (version,))
    return cursor.fetchone()[0]

def log_error(table_name, version, error):
    os.makedirs('Data/logs', exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.ctime()}] Table: {table_name}, Build: {version}, Error: {str(error)}\n")

def process_table(table, version, build_id, db_path):
    csv_path = os.path.join(CSV_DIR, f"{table}_{version}.csv")
    url = f"https://wago.tools/db2/{table}/csv?build={version}"
    
    try:
        # 1. Download
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            raise Exception(f"HTTP {r.status_code}")
        
        if len(r.content) < 10:
            return f"SKIP: {table} (empty)"

        with open(csv_path, 'wb') as f:
            f.write(r.content)
        
        # 2. Parse
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            sep = ';' if ';' in first_line and first_line.count(';') > first_line.count(',') else ','
        
        try:
            df = pd.read_csv(csv_path, low_memory=False, sep=sep)
        except:
            df = pd.read_csv(csv_path, low_memory=False, sep=sep, engine='python', on_bad_lines='skip')

        df.columns = [c.replace('"', '').replace("'", "").strip() for c in df.columns]
        if df.empty:
            os.remove(csv_path)
            return f"SKIP: {table} (empty df)"

        df['build_id'] = build_id
        
        # 3. Import into SQLite (one connection per thread is safer)
        conn = sqlite3.connect(db_path)
        df.to_sql(table, conn, if_exists='replace', index=False)
        conn.close()
        
        if os.path.exists(csv_path):
            os.remove(csv_path)
        return f"OK: {table}"
        
    except Exception as e:
        log_error(table, version, e)
        if os.path.exists(csv_path):
            os.remove(csv_path)
        return f"ERROR: {table} - {e}"

def fetch_and_import(version, tables=None, progress_callback=None):
    db_path = f'Data/dbs/WoW_Data_{version}.db'
    conn = init_db(version)
    build_id = get_or_create_build_id(conn, version)
    conn.close() # Close main connection for parallel processing
    
    if not tables:
        print(f"Fetching table list for build {version}...")
        try:
            api_url = f"https://wago.tools/api/db2?build={version}"
            r_api = requests.get(api_url, timeout=30)
            if r_api.status_code == 200:
                tables = r_api.json()
            else:
                r_html = requests.get(f'https://wago.tools/db2?build={version}')
                r_html.raise_for_status()
                match = re.search(r'data-page="([^"]+)"', r_html.text)
                page_json_str = match.group(1).replace('&quot;', '"').replace('&amp;', '&')
                page_data = json.loads(page_json_str)
                tables_dict = page_data.get('props', {}).get('tables', {})
                tables = list(tables_dict.values())
        except Exception as e:
            print(f"Error fetching table list: {e}")
            return

    num_workers = int(get_setting('workers', 1))
    print(f"Starting parallel sync with {num_workers} workers...")
    
    os.makedirs(CSV_DIR, exist_ok=True)
    
    total = len(tables)
    completed = 0
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_table, table, version, build_id, db_path): table for table in tables}
        
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            msg = f"[{completed}/{total}] {result}"
            print(msg, end='\r')
            if progress_callback: progress_callback(msg)

    finish_msg = f"\nSync for build {version} completed."
    print(finish_msg)
    
    # Update Registry with sync status
    try:
        reg_conn = sqlite3.connect('Data/dbs/Build_Registry.db')
        reg_cursor = reg_conn.cursor()
        reg_cursor.execute("UPDATE builds SET is_downloaded = 1, last_synced = CURRENT_TIMESTAMP WHERE version = ?", (version,))
        reg_conn.commit()
        reg_conn.close()
    except: pass

    if progress_callback: progress_callback(finish_msg)

if __name__ == "__main__":
    import sys, json, re
    ver = sys.argv[1] if len(sys.argv) > 1 else "12.0.0.65560"
    # If you want to test specific tables only:
    # fetch_and_import(ver, ["QuestV2", "SpellName"])
    fetch_and_import(ver)
