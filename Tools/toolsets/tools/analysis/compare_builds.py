# Tools/toolsets/tools/analysis/compare_builds.py
from typing import Dict, Any, List
import sys
import os
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

# Define the path to the queries for this tool and related generic ones
QUERY_DIR_COMPARE = Path(__file__).parent / "queries" / "compare_builds"
QUERY_DIR_GENERIC = Path(__file__).parent.parent / "database" / "queries" / "find_value"

def _load_query(name: str, specific_dir: Path) -> str:
    """Loads a SQL query from a specified query directory."""
    with open(specific_dir / name, 'r') as f:
        return f.read().strip()

def _get_schema_for_build(db_client: DBClient, build_version: str) -> Dict[str, Dict[str, Any]]:
    """
    Retrieves the full schema for a given build version, including table names,
    columns, and row counts.
    """
    schema = {}
    
    # --- Load all queries first ---
    get_build_id_sql = _load_query("get_build_id_by_version.sql", QUERY_DIR_GENERIC)
    get_tables_sql = _load_query("get_archive_tables.sql", QUERY_DIR_GENERIC)
    describe_table_template = _load_query("describe_table.sql", QUERY_DIR_GENERIC)
    get_count_template = _load_query("get_table_count_for_build.sql", QUERY_DIR_COMPARE)
    
    # --- Execute logic ---
    res = db_client.execute(get_build_id_sql, [build_version])
    build_id_row = res.fetchone()
    if not build_id_row:
        raise ValueError(f"Build version '{build_version}' not found in registry.")
    build_id = build_id_row[0]

    tables_res = db_client.execute(get_tables_sql)
    tables = [row[0] for row in tables_res.fetchall()]

    for table in tables:
        try:
            describe_sql = describe_table_template.format(table_name=table)
            cols_res = db_client.execute(describe_sql)
            columns = [row[0] for row in cols_res.fetchall()]

            if 'build_id' not in [c.lower() for c in columns]:
                continue

            count_sql = get_count_template.format(table_name=table)
            count_res = db_client.execute(count_sql, [build_id])
            count = count_res.fetchone()[0]

            if count > 0:
                schema[table] = {"columns": columns, "count": count}
        except Exception:
            # If a table fails, we just skip it for the comparison
            continue
            
    return schema

def compare_builds(db_client: DBClient, build_version_A: str, build_version_B: str) -> Dict[str, Any]:
    """
    Compares the schemas of two build versions and returns a diff.
    """
    schema_A = _get_schema_for_build(db_client, build_version_A)
    schema_B = _get_schema_for_build(db_client, build_version_B)
    
    diff = {
        "added_tables": [],
        "removed_tables": [],
        "modified_tables": {}
    }
    
    all_table_names = set(schema_A.keys()) | set(schema_B.keys())
    
    for table in sorted(list(all_table_names)):
        if table not in schema_A:
            diff["added_tables"].append({
                "name": table,
                "count": schema_B[table]["count"]
            })
        elif table not in schema_B:
            diff["removed_tables"].append({
                "name": table,
                "count": schema_A[table]["count"]
            })
        else:
            # Table exists in both
            data_A = schema_A[table]
            data_B = schema_B[table]
            
            changes = []
            if data_A["count"] != data_B["count"]:
                diff_count = data_B["count"] - data_A["count"]
                changes.append(f"Count: {data_A['count']} -> {data_B['count']} ({'+' if diff_count > 0 else ''}{diff_count})")
            
            # For simplicity, just comparing lengths. A more detailed diff could compare contents.
            if len(data_A["columns"]) != len(data_B["columns"]) or set(data_A["columns"]) != set(data_B["columns"]):
                added_cols = set(data_B["columns"]) - set(data_A["columns"])
                removed_cols = set(data_A["columns"]) - set(data_B["columns"])
                if added_cols: changes.append(f"Added columns: {', '.join(sorted(list(added_cols)))}")
                if removed_cols: changes.append(f"Removed columns: {', '.join(sorted(list(removed_cols)))}")
            
            if changes:
                diff["modified_tables"][table] = changes
                
    return diff
