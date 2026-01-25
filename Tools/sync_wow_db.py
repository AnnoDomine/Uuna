import os
import sqlite3
import pandas as pd
import requests
import time

DB_PATH = 'Data/WoW_Data.db'
CSV_DIR = 'Data/DB2_CSV'
LOG_FILE = 'Data/import_errors.log'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Build-Tabelle erstellen
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
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.ctime()}] Table: {table_name}, Build: {version}, Error: {str(error)}\n")

def fetch_and_import(version, tables=None):
    conn = init_db()
    build_id = get_or_create_build_id(conn, version)
    
    if not tables:
        # Liste aller Tabellen von Wago.tools holen
        print(f"Hole Tabellenliste für Build {version}...")
        try:
            import json, re
            r_html = requests.get('https://wago.tools/db2')
            r_html.raise_for_status()
            
            # Suche nach data-page="..."
            match = re.search(r'data-page="([^"]+)"', r_html.text)
            if not match:
                raise Exception("Konnte data-page Attribut nicht im HTML finden")
            
            # HTML Entities dekodieren
            page_json_str = match.group(1).replace('&quot;', '"').replace('&amp;', '&')
            page_data = json.loads(page_json_str)
            
            tables_dict = page_data.get('props', {}).get('tables', {})
            tables = list(tables_dict.values())
            
            if not tables:
                raise Exception("Tabellenliste in props.tables ist leer")
                
            print(f"Gefundene Tabellen: {len(tables)}")
        except Exception as e:
            print(f"Fehler beim Holen der Tabellenliste: {e}")
            return

    for table in tables:
        csv_path = os.path.join(CSV_DIR, f"{table}.csv")
        url = f"https://wago.tools/db2/{table}/csv?build={version}"
        
        print(f"Verarbeite {table}...", end='\r')
        
        try:
            # Download
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                raise Exception(f"HTTP {r.status_code}")
            
            with open(csv_path, 'wb') as f:
                f.write(r.content)
            
            # Import via Pandas (einfachste Methode für dynamische Schemas)
            df = pd.read_csv(csv_path, low_memory=False)
            df['build_id'] = build_id
            
            # In SQLite schreiben (append falls existiert)
            df.to_sql(table, conn, if_exists='append', index=False)
            
            # Cleanup
            os.remove(csv_path)
            
        except Exception as e:
            log_error(table, version, e)
            if os.path.exists(csv_path):
                os.remove(csv_path)

    conn.close()
    print(f"\nSync für Build {version} abgeschlossen. Fehler siehe {LOG_FILE}")

if __name__ == "__main__":
    import sys
    ver = sys.argv[1] if len(sys.argv) > 1 else "12.0.0.65560"
    # Falls du nur spezifische Tabellen testen willst:
    # fetch_and_import(ver, ["QuestV2", "SpellName"])
    fetch_and_import(ver)
