import sqlite3

def find_value_everywhere(value):
    conn = sqlite3.connect('Data/WoW_Data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nSuche nach Wert: '{value}' in allen Tabellen...")
    print("-" * 60)

    for table in tables:
        cursor.execute(f"PRAGMA table_info('{table}')")
        columns = [col[1] for col in cursor.fetchall()]
        
        where_clauses = [f'"{col}" = ?' for col in columns]
        query = f"SELECT COUNT(*) FROM '{table}' WHERE " + " OR ".join(where_clauses)
        
        try:
            cursor.execute(query, [value] * len(columns))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"GEFUNDEN in Tabelle '{table}': {count} Treffer")
        except:
            continue
            
    conn.close()

if __name__ == "__main__":
    import sys
    val = sys.argv[1] if len(sys.argv) > 1 else ""
    if val:
        find_value_everywhere(val)
