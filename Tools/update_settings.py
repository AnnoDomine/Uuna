import sqlite3
import sys
import os

SETTINGS_DB = 'Data/dbs/Settings.db'

def set_setting(key, value):
    os.makedirs(os.path.dirname(SETTINGS_DB), exist_ok=True)
    conn = sqlite3.connect(SETTINGS_DB)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value', (key, str(value)))
    conn.commit()
    conn.close()
    print(f"Setting '{key}' updated to '{value}'.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_settings.py <key> <value>")
        sys.exit(1)
    
    key = sys.argv[1]
    value = sys.argv[2]
    
    if key == "workers" and int(value) < 1:
        print("Error: workers must be at least 1.")
        sys.exit(1)
        
    set_setting(key, value)
