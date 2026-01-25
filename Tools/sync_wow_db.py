import os
import sqlite3
import pandas as pd
import requests
import time

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

def fetch_and_import(version, tables=None, progress_callback=None):
    conn = init_db(version)
    build_id = get_or_create_build_id(conn, version)
    
    if not tables:
        print(f"Fetching table list for build {version}...")
        try:
            r_html = requests.get(f'https://wago.tools/db2?build={version}')
            r_html.raise_for_status()
            match = re.search(r'data-page="([^"]+)"', r_html.text)
            if not match:
                raise Exception("Could not find data-page attribute in HTML")
            
            page_json_str = match.group(1).replace('&quot;', '"').replace('&amp;', '&')
            page_data = json.loads(page_json_str)
            tables_dict = page_data.get('props', {}).get('tables', {})
            tables = list(tables_dict.values())
            
            if not tables:
                raise Exception("Table list is empty")
        except Exception as e:
            msg = f"Error fetching table list: {e}"
            print(msg)
            if progress_callback: progress_callback(msg)
            return

    total = len(tables)
    for i, table in enumerate(tables):
        csv_path = os.path.join(CSV_DIR, f"{table}.csv")
        url = f"https://wago.tools/db2/{table}/csv?build={version}"
        
        status = f"[{i+1}/{total}] Processing {table}..."
        print(status, end='\r')
        if progress_callback: progress_callback(status)
        
        try:
            os.makedirs(CSV_DIR, exist_ok=True)
            r = requests.get(url, timeout=60)
            if r.status_code != 200:
                raise Exception(f"HTTP {r.status_code}")
            
            with open(csv_path, 'wb') as f:
                f.write(r.content)
            
            # Automatic delimiter detection
            df = pd.read_csv(csv_path, low_memory=False, sep=None, engine='python')
            df['build_id'] = build_id
            
            # Overwrite table in SQLite (replace) to correct schema errors
            df.to_sql(table, conn, if_exists='replace', index=False)
            os.remove(csv_path)
            
        except Exception as e:
            log_error(table, version, e)
            if progress_callback: progress_callback(f"ERROR in {table}: {e}")
            if os.path.exists(csv_path):
                os.remove(csv_path)

    conn.close()
    finish_msg = f"Sync for build {version} completed."
    print(f"\n{finish_msg}")
    if progress_callback: progress_callback(finish_msg)

if __name__ == "__main__":
    import sys, json, re
    ver = sys.argv[1] if len(sys.argv) > 1 else "12.0.0.65560"
    # If you want to test specific tables only:
    # fetch_and_import(ver, ["QuestV2", "SpellName"])
    fetch_and_import(ver)
