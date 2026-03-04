import os
import sys
from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger


def search_in_duckdb(value, target_build=None):
    """
    Searches for a value in the DuckDB Master Archive.
    """
    debugger.add_log(f"Searching for value '{value}' in DuckDB (Build: {target_build or 'ALL'})", agent="ANALYSIS", process="FindValue")
    print(f"\n[ Master Archive: {'Build ' + str(target_build) if target_build else 'ALL Builds'} ]")
    print("-" * 60)

    try:
        # 1. Get build_id if requested
        build_id = None
        if target_build:
            res = db.execute("SELECT id FROM registry.builds WHERE ? IN (version, id::VARCHAR)", [target_build])
            row = res.fetchone()
            if not row:
                print(f"Error: Build '{target_build}' not found in registry.")
                return
            build_id = row[0]

        # 2. Get all tables in 'archive' schema
        tables_res = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'archive'")
        tables = [row[0] for row in tables_res.fetchall() if row[0] != 'build_data_map' and not row[0].startswith('tmp_')]

        found_any = False
        for table in tables:
            try:
                # 3. Get columns
                cols_res = db.execute(f"PRAGMA table_info('archive.{table}')")
                columns = [row[1] for row in cols_res.fetchall() if row[1] != '_row_hash']

                # 4. Construct Query
                # We search for exact match as string or number
                clauses = [f'"{col}" = ?' for col in columns]
                where_clause = " OR ".join(clauses)
                params = [value] * len(columns)

                if build_id:
                    # Join with mapping table for build-specific search
                    query = f"""
                        SELECT COUNT(*) 
                        FROM archive."{table}" d
                        JOIN archive.build_data_map m ON d._row_hash = m.row_hash
                        WHERE ({where_clause}) 
                          AND m.build_id = ? 
                          AND m.table_name = ?
                    """
                    params.extend([build_id, table])
                else:
                    # Global search in Master Archive
                    query = f'SELECT COUNT(*) FROM archive."{table}" WHERE ' + where_clause

                count_res = db.execute(query, params)
                count = count_res.fetchone()[0]

                if count > 0:
                    debugger.add_log(f"Found match in {table}: {count}", agent="ANALYSIS", level="SUCCESS", process="FindValue")
                    print(f"  FOUND in '{table}': {count} matches")
                    found_any = True
            except Exception:
                # debugger.add_log(f"Error searching in {table}: {e}", agent="ANALYSIS", level="WARNING")
                continue

        if not found_any:
            print("  No matches found in DuckDB.")

    except Exception as e:
        debugger.add_log(f"DuckDB search failed: {e}", agent="ANALYSIS", level="ERROR", process="FindValue")
        print(f"  DuckDB Search Error: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_val.py <value> [-build=xxx]")
        return

    val = sys.argv[1]
    target_build = None

    for arg in sys.argv[2:]:
        if arg.startswith("-build="):
            target_build = arg.split("=")[1]

    # First search in DuckDB (Modern way)
    search_in_duckdb(val, target_build)

    # Then search in legacy SQLite if build matches or no build specified
    # (Optional: we keep this to support historical data not yet migrated)
    import glob
    import sqlite3
    from Tools.core.security_utils import sanitize_identifier

    dbs_to_search = []
    if target_build:
        path = f"Data/dbs/WoW_Data_{target_build}.db"
        if os.path.exists(path):
            dbs_to_search.append(path)
    else:
        dbs_to_search = sorted(glob.glob("Data/dbs/WoW_Data_*.db"), reverse=True)

    if dbs_to_search:
        print(f"\n[ Legacy SQLite: Searching across {len(dbs_to_search)} old database(s)... ]")
        for db_path in dbs_to_search:
            build_name = os.path.basename(db_path).replace("WoW_Data_", "").replace(".db", "")
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall() if row[0] not in ("builds", "sqlite_sequence")]
                
                for table in tables:
                    try:
                        safe_table = sanitize_identifier(table)
                        cursor.execute(f'PRAGMA table_info("{safe_table}")')
                        columns = [sanitize_identifier(col[1]) for col in cursor.fetchall()]
                        clauses = [f'"{col}" = ?' for col in columns]
                        query = f'SELECT COUNT(*) FROM "{safe_table}" WHERE ' + " OR ".join(clauses)
                        cursor.execute(query, [val] * len(columns))
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"  FOUND in '{build_name}.{table}': {count} matches")
                    except Exception:
                        continue
                conn.close()
            except Exception:
                continue


if __name__ == "__main__":
    main()
