import sqlite3
import os
import glob
from Tools.core.security_utils import sanitize_identifier


def find_references(column_name, db_path=None):
    # Sanitize inputs
    safe_column = sanitize_identifier(column_name)
    
    if not db_path:
        # Find the latest WoW_Data database
        dbs = glob.glob("Data/dbs/WoW_Data_*.db")
        if not dbs:
            print("No database found in Data/dbs/WoW_Data_*.db")
            return
        else:
            db_path = max(dbs, key=os.path.getmtime)

    print(f"Using database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    found_in = []
    for table in tables:
        safe_table = sanitize_identifier(table)
        cursor.execute(f"PRAGMA table_info('{safe_table}')")
        columns = [col[1] for col in cursor.fetchall()]
        if safe_column in columns:
            cursor.execute(f"SELECT COUNT(*) FROM '{safe_table}'")
            count = cursor.fetchone()[0]
            found_in.append((safe_table, count))

    conn.close()

    print(f"\nSearching for column: '{safe_column}'")
    print("-" * 40)
    for table, count in sorted(found_in, key=lambda x: x[1], reverse=True):
        print(f"{table:<30} | {count:>8} entries")


if __name__ == "__main__":
    import sys

    search = sys.argv[1] if len(sys.argv) > 1 else "ID"
    db = sys.argv[2] if len(sys.argv) > 2 else None
    find_references(search, db)
