import sqlite3
import os
import glob
import json
import re

def get_db_path(version):
    return f'Data/dbs/WoW_Data_{version}.db'

def get_tables(db_path):
    if not os.path.exists(db_path):
        return {}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {}
    for row in cursor.fetchall():
        table_name = row[0]
        if table_name in ('builds', 'sqlite_sequence'):
            continue
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        cols = [col[1] for col in cursor.fetchall()]
        cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
        count = cursor.fetchone()[0]
        tables[table_name] = {"columns": cols, "count": count}
    conn.close()
    return tables

def compare_builds(version_old, version_new):
    path_old = get_db_path(version_old)
    path_new = get_db_path(version_new)
    
    if not os.path.exists(path_old) or not os.path.exists(path_new):
        return {"error": "One or both databases are missing."}
    
    tables_old = get_tables(path_old)
    tables_new = get_tables(path_new)
    
    diff = {
        "added_tables": [],
        "removed_tables": [],
        "modified_tables": {}
    }
    
    all_table_names = set(tables_old.keys()) | set(tables_new.keys())
    
    for table in sorted(all_table_names):
        if table not in tables_old:
            diff["added_tables"].append({
                "name": table,
                "count": tables_new[table]["count"]
            })
        elif table not in tables_new:
            diff["removed_tables"].append({
                "name": table,
                "count": tables_old[table]["count"]
            })
        else:
            # Table exists in both
            old_data = tables_old[table]
            new_data = tables_new[table]
            
            changes = []
            if old_data["count"] != new_data["count"]:
                diff_count = new_data["count"] - old_data["count"]
                changes.append(f"Count: {old_data['count']} -> {new_data['count']} ({'+' if diff_count > 0 else ''}{diff_count})")
            
            if old_data["columns"] != new_data["columns"]:
                added_cols = set(new_data["columns"]) - set(old_data["columns"])
                removed_cols = set(old_data["columns"]) - set(new_data["columns"])
                if added_cols: changes.append(f"Added columns: {', '.join(added_cols)}")
                if removed_cols: changes.append(f"Removed columns: {', '.join(removed_cols)}")
            
            if changes:
                diff["modified_tables"].append(changes)
                
    return diff

def get_version_tuple(v):
    return tuple(map(int, (re.sub(r'[^0-9.]', '', v).split('.'))))

def run_diff_chain(start_version, end_version, include_intermediate=False):
    from sync_wow_db import fetch_available_builds
    
    available_online = fetch_available_builds()
    # Sort builds by version
    try:
        available_online.sort(key=get_version_tuple)
    except:
        available_online.sort()
        
    if start_version not in available_online or end_version not in available_online:
        print(f"Error: One of the versions ({start_version}, {end_version}) is not in the official build list.")
        return

    idx_start = available_online.index(start_version)
    idx_end = available_online.index(end_version)
    
    if idx_start > idx_end:
        idx_start, idx_end = idx_end, idx_start
        
    build_range = available_online[idx_start:idx_end+1]
    
    print(f"Comparing build chain: {' -> '.join(build_range)}")
    
    if not include_intermediate:
        # Direct comparison
        res = compare_builds(start_version, end_version)
        print_diff(start_version, end_version, res)
    else:
        # Step by step
        for i in range(len(build_range) - 1):
            v1 = build_range[i]
            v2 = build_range[i+1]
            
            if not os.path.exists(get_db_path(v1)) or not os.path.exists(get_db_path(v2)):
                print(f"\n--- Skipping {v1} -> {v2} (Local DB missing) ---")
                continue
                
            res = compare_builds(v1, v2)
            print_diff(v1, v2, res)

def print_diff(v1, v2, diff):
    if "error" in diff:
        print(f"Error comparing {v1} to {v2}: {diff['error']}")
        return
        
    print(f"\n{'='*60}")
    print(f"DIFF: {v1} -> {v2}")
    print(f"{ '='*60}")
    
    if diff["added_tables"]:
        print(f"\n[+] Added Tables ({len(diff['added_tables'])}):")
        for t in diff["added_tables"]:
            print(f"  - {t['name']} ({t['count']} rows)")
            
    if diff["removed_tables"]:
        print(f"\n[-] Removed Tables ({len(diff['removed_tables'])}):")
        for t in diff["removed_tables"]:
            print(f"  - {t['name']} ({t['count']} rows)")
            
    if diff["modified_tables"]:
        print(f"\n[*] Modified Tables ({len(diff['modified_tables'])}):")
        for table, changes in diff["modified_tables"].items():
            print(f"  - {table}:")
            for c in changes:
                print(f"    {c}")
    
    if not any([diff["added_tables"], diff["removed_tables"], diff["modified_tables"]]):
        print("\nNo changes detected.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python compare_builds.py <old_version> <new_version> [--intermediate]")
        sys.exit(1)
        
    v_old = sys.argv[1]
    v_new = sys.argv[2]
    intermediate = "--intermediate" in sys.argv
    
    run_diff_chain(v_old, v_new, intermediate)
