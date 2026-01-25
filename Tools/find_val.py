import sqlite3
import os
import glob

def find_value_everywhere(value, db_path=None):
    if not db_path:
        # Find the latest WoW_Data database
        dbs = glob.glob('Data/dbs/WoW_Data_*.db')
        if not dbs:
            # Fallback to the old file if present
            if os.path.exists('Data/dbs/WoW_Data.db'):
                db_path = 'Data/dbs/WoW_Data.db'
            else:
                print("No database found in Data/dbs/WoW_Data_*.db")
                return
        else:
            db_path = max(dbs, key=os.path.getmtime)
    
    print(f"Using database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nSearching for value: '{value}' in all tables...")
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
                print(f"FOUND in table '{table}': {count} matches")
        except:
            continue
            
    conn.close()

if __name__ == "__main__":
    import sys
    val = sys.argv[1] if len(sys.argv) > 1 else ""
    db = sys.argv[2] if len(sys.argv) > 2 else None
    if val:
        find_value_everywhere(val, db)
