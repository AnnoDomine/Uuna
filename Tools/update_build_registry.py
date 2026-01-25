import sqlite3
import requests
import os

DB_PATH = 'Data/dbs/Build_Registry.db'
API_URL = 'https://wago.tools/api/builds'

def fetch_versions():
    print(f"Fetching available builds from {API_URL}...")
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching versions: {e}")
    return []

def update_registry(builds_dict=None):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Advanced schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY,
            version TEXT,
            product TEXT,
            is_downloaded INTEGER DEFAULT 0,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_synced TIMESTAMP
        )
    ''')
    
    if builds_dict:
        count = 0
        for product_name, entries in builds_dict.items():
            for entry in entries:
                ver_str = entry.get('version')
                if ver_str:
                    try:
                        build_num = int(ver_str.split('.')[-1])
                        # Check if file exists locally to mark as downloaded
                        is_dl = 1 if os.path.exists(f'Data/dbs/WoW_Data_{ver_str}.db') else 0
                        
                        cursor.execute('''
                            INSERT INTO builds (id, version, product, is_downloaded) 
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(id) DO UPDATE SET 
                                version = excluded.version,
                                product = excluded.product,
                                is_downloaded = MAX(is_downloaded, excluded.is_downloaded),
                                last_seen = CURRENT_TIMESTAMP
                        ''', (build_num, ver_str, product_name, is_dl))
                        count += 1
                    except ValueError: continue
        conn.commit()
        print(f"Registry updated: {count} entries processed.")
    
    # Final pass: Verify all local files match the DB state
    cursor.execute("SELECT version FROM builds")
    rows = cursor.fetchall()
    for (ver,) in rows:
        is_dl = 1 if os.path.exists(f'Data/dbs/WoW_Data_{ver}.db') else 0
        cursor.execute("UPDATE builds SET is_downloaded = ? WHERE version = ?", (is_dl, ver))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    data = fetch_versions()
    update_registry(data)