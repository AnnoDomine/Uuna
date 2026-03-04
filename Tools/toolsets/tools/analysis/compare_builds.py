# Tools/toolsets/tools/analysis/compare_builds.py
from pathlib import Path
from typing import Any, Dict

from Tools.core.shared_db_instance import db

# Define the path to the queries for this tool and related generic ones
QUERY_DIR_COMPARE = Path(__file__).parent / "queries" / "compare_builds"
QUERY_DIR_GENERIC = Path(__file__).parent.parent / "database" / "queries" / "find_value"


def _load_query(name: str, specific_dir: Path) -> str:
    """Loads a SQL query from a specified query directory."""
    with open(specific_dir / name, "r") as f:
        return f.read().strip()


def _get_schema_for_build(build_version: str) -> Dict[str, Dict[str, Any]]:
    """
    Retrieves the full schema for a given build version.
    """
    schema = {}

    # --- Load all queries first ---
    get_build_id_sql = _load_query("get_build_id_by_version.sql", QUERY_DIR_GENERIC)
    get_tables_sql = _load_query("get_archive_tables.sql", QUERY_DIR_GENERIC)
    describe_table_template = _load_query("describe_table.sql", QUERY_DIR_GENERIC)
    get_count_template = _load_query("get_table_count_for_build.sql", QUERY_DIR_COMPARE)

    # --- Execute logic ---
    res = db.execute(get_build_id_sql, [build_version])
    build_id_row = res.fetchone()
    if not build_id_row:
        raise ValueError(f"Build version '{build_version}' not found in registry.")
    build_id = build_id_row[0]

    tables_res = db.execute(get_tables_sql)
    tables = [row[0] for row in tables_res.fetchall()]

    for table in tables:
        try:
            describe_sql = describe_table_template.format(table_name=table)
            cols_res = db.execute(describe_sql)
            columns = [row[0] for row in cols_res.fetchall()]
            
            col_names_lower = [c.lower() for c in columns]
            has_hash = "_row_hash" in col_names_lower
            has_build_id = "build_id" in col_names_lower

            if has_hash:
                # Modern architecture: use mapping table
                count_sql = f"""
                    SELECT COUNT(*) 
                    FROM archive."{table}" d
                    JOIN archive.build_data_map m ON d._row_hash = m.row_hash
                    WHERE m.build_id = ? AND m.table_name = ?
                """
                count_res = db.execute(count_sql, [build_id, table])
            elif has_build_id:
                # Transition architecture: table has build_id
                count_sql = get_count_template.format(table_name=table)
                count_res = db.execute(count_sql, [build_id])
            else:
                # Table doesn't support build-specific filtering
                continue

            count = count_res.fetchone()[0]
            if count > 0:
                schema[table] = {"columns": columns, "count": count}
        except Exception:
            continue

    return schema


def compare_builds(build_version_A: str, build_version_B: str) -> Dict[str, Any]:
    """
    Compares the schemas of two build versions and returns a diff.

    Args:
    - build_version_A: The first build version string.
    - build_version_B: The second build version string.
    """
    schema_A = _get_schema_for_build(build_version_A)
    schema_B = _get_schema_for_build(build_version_B)

    diff = {"added_tables": [], "removed_tables": [], "modified_tables": {}}

    all_table_names = set(schema_A.keys()) | set(schema_B.keys())

    for table in sorted(list(all_table_names)):
        if table not in schema_A:
            diff["added_tables"].append({"name": table, "count": schema_B[table]["count"]})
        elif table not in schema_B:
            diff["removed_tables"].append({"name": table, "count": schema_A[table]["count"]})
        else:
            # Table exists in both
            data_A = schema_A[table]
            data_B = schema_B[table]

            changes = []
            if data_A["count"] != data_B["count"]:
                diff_count = data_B["count"] - data_A["count"]
                changes.append(
                    f"Count: {data_A['count']} -> {data_B['count']} ({'+' if diff_count > 0 else ''}{diff_count})"
                )

            # For simplicity, just comparing lengths. A more detailed diff could compare contents.
            if len(data_A["columns"]) != len(data_B["columns"]) or set(data_A["columns"]) != set(data_B["columns"]):
                added_cols = set(data_B["columns"]) - set(data_A["columns"])
                removed_cols = set(data_A["columns"]) - set(data_B["columns"])
                if added_cols:
                    changes.append(f"Added columns: {', '.join(sorted(list(added_cols)))}")
                if removed_cols:
                    changes.append(f"Removed columns: {', '.join(sorted(list(removed_cols)))}")

            if changes:
                diff["modified_tables"][table] = changes

    return diff
