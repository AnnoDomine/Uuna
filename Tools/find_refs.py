import sqlite3

def find_references(column_name):
    conn = sqlite3.connect('Data/WoW_Data.db')
    cursor = conn.cursor()
    
    # Alle Tabellen abrufen
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    found_in = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info('{table}')")
        columns = [col[1] for col in cursor.fetchall()]
        if column_name in columns:
            cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
            count = cursor.fetchone()[0]
            found_in.append((table, count))
            
    conn.close()
    
    print(f"\nSuche nach Spalte: '{column_name}'")
    print("-" * 40)
    for table, count in sorted(found_in, key=lambda x: x[1], reverse=True):
        print(f"{table:<30} | {count:>8} Einträge")

if __name__ == "__main__":
    import sys
    search = sys.argv[1] if len(sys.argv) > 1 else "ID"
    find_references(search)

