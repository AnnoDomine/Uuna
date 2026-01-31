import sqlite3
import sys
import os

KNOWLEDGE_DB = 'Data/dbs/WoW_Research_Knowledge.db'

def query_db(query, params=(), commit=False):
    conn = sqlite3.connect(KNOWLEDGE_DB)
    cur = conn.cursor()
    cur.execute(query, params)
    res = cur.fetchall()
    if commit: conn.commit()
    conn.close()
    return res

def list_settings():
    print("\n=== AI AGENT SETTINGS ===")
    res = query_db("SELECT key, value, description FROM ai_settings")
    for key, val, desc in res:
        print(f"  {key:<15} : {val:<10} # {desc}")
    print("")

def set_setting(key, value):
    # Check if key exists
    res = query_db("SELECT key FROM ai_settings WHERE key = ?", (key,))
    if not res:
        print(f"Error: Setting '{key}' not found.")
        return
    
    query_db("UPDATE ai_settings SET value = ? WHERE key = ?", (value, key), commit=True)
    print(f"Successfully updated {key} to {value}.")

def show_status():
    print("\n=== ARCHIVIST KNOWLEDGE STATUS ===")
    stats = {}
    stats['total_builds'] = query_db("SELECT COUNT(*) FROM builds")[0][0]
    stats['total_features'] = query_db("SELECT COUNT(*) FROM column_features")[0][0]
    stats['mapped_cols'] = query_db("SELECT COUNT(*) FROM global_knowledge")[0][0]
    stats['total_confirmations'] = query_db("SELECT SUM(confirmations) FROM global_knowledge")[0][0] or 0
    stats['lore_discoveries'] = query_db("SELECT COUNT(*) FROM ai_discoveries")[0][0]
    
    print(f"  Analyzed Builds   : {stats['total_builds']}")
    print(f"  Indexed Columns   : {stats['total_features']}")
    print(f"  Knowledge Entries : {stats['mapped_cols']}")
    print(f"  Total Confirms    : {stats['total_confirmations']}")
    print(f"  Lore Discoveries  : {stats['lore_discoveries']}")
    print("")

def main():
    if len(sys.argv) < 2:
        print("AI Control CLI")
        print("Usage: python ai_control.py <command> [args]")
        print("Commands: list, set <key> <value>, status")
        return

    cmd = sys.argv[1].lower()
    
    if cmd == "list":
        list_settings()
    elif cmd == "status":
        show_status()
    elif cmd == "set" and len(sys.argv) == 4:
        set_setting(sys.argv[2], sys.argv[3])
    else:
        print("Unknown command or missing arguments.")

if __name__ == "__main__":
    main()
