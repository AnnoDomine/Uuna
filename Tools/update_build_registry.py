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
        data = r.json()
        # The API returns a list of dictionaries with version information
        return data
    except Exception as e:
        print(f"Error fetching versions: {e}")
    return []

def update_registry(builds_dict):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY,
            version TEXT,
            product TEXT,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    count = 0
    # builds_dict is { "product_name": [ {build_info}, ... ], ... }
    for product_name, entries in builds_dict.items():
        for entry in entries:
            ver_str = entry.get('version')
            
            if ver_str:
                parts = ver_str.split('.')
                if len(parts) >= 1:
                    try:
                        build_num = int(parts[-1])
                        # We use build_num as ID, but different products might have the same build number?
                        # In WoW, build numbers are usually unique across versions, but let's be safe.
                        # If we want unique per version string:
                        cursor.execute('''
                            INSERT INTO builds (id, version, product) 
                            VALUES (?, ?, ?)
                            ON CONFLICT(id) DO UPDATE SET 
                                version = excluded.version,
                                product = excluded.product,
                                last_seen = CURRENT_TIMESTAMP
                        ''', (build_num, ver_str, product_name))
                        count += 1
                    except ValueError:
                        continue
                
    conn.commit()
    conn.close()
    print(f"Registry updated. Processed {count} entries across all products.")

if __name__ == "__main__":
    builds_data = fetch_versions()
    if builds_data:
        update_registry(builds_data)
    else:
        print("No build data received.")
