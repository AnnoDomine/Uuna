import sqlite3
import os
import glob
import sys


def search_in_db(db_path, value):
    build_name = os.path.basename(db_path).replace("WoW_Data_", "").replace(".db", "")
    print(f"\n[ Build: {build_name} ]")
    print("-" * 40)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] not in ("builds", "sqlite_sequence")]

        found_any = False
        for table in tables:
            try:
                cursor.execute(f'PRAGMA table_info("{table}")')
                columns = [col[1] for col in cursor.fetchall()]

                # We search for exact match as string or number
                clauses = [f'"{col}" = ?' for col in columns]
                query = f'SELECT COUNT(*) FROM "{table}" WHERE ' + " OR ".join(clauses)

                cursor.execute(query, [value] * len(columns))
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  FOUND in '{table}': {count} matches")
                    found_any = True
            except:
                continue

        if not found_any:
            print("  No matches found.")

        conn.close()
    except Exception as e:
        print(f"  Error accessing DB: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_val.py <value> [-build=xxx]")
        return

    val = sys.argv[1]
    target_build = None

    for arg in sys.argv[2:]:
        if arg.startswith("-build="):
            target_build = arg.split("=")[1]

    dbs_to_search = []
    if target_build:
        path = f"Data/dbs/WoW_Data_{target_build}.db"
        if os.path.exists(path):
            dbs_to_search.append(path)
        else:
            print(f"Error: Build database not found for '{target_build}'")
            return
    else:
        # All local builds
        dbs_to_search = sorted(glob.glob("Data/dbs/WoW_Data_*.db"), reverse=True)

    if not dbs_to_search:
        print("No databases found to search in.")
        return

    print(f"Searching for '{val}' across {len(dbs_to_search)} build(s)...")
    for db in dbs_to_search:
        search_in_db(db, val)


if __name__ == "__main__":
    main()
