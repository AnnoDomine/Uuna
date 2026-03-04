# Tools/toolsets/tools/database/find_column_references.py
from pathlib import Path
from typing import Dict

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

# Define paths to query directories
QUERY_DIR_SPECIFIC = Path(__file__).parent / "queries" / "find_column_references"
QUERY_DIR_GENERIC = Path(__file__).parent / "queries" / "find_value"  # Re-use generic queries


def _load_query(name: str, specific_dir: Path) -> str:
    """Loads a SQL query from a specified query directory."""
    with open(specific_dir / name, "r") as f:
        return f.read().strip()


def find_column_references(column_name: str) -> Dict[str, int]:
    """
    Finds all tables that contain a specific column.

    Args:
    - column_name: The name of the column to search for (e.g. 'CreatureID').
    """
    found_in = {}

    # --- Load all queries first ---
    get_tables_sql = _load_query("get_archive_tables.sql", QUERY_DIR_GENERIC)
    describe_table_template = _load_query("describe_table.sql", QUERY_DIR_GENERIC)
    get_count_template = _load_query("get_table_count.sql", QUERY_DIR_SPECIFIC)

    # --- Execute logic ---
    tables_res = db.execute(get_tables_sql)
    tables = [row[0] for row in tables_res.fetchall()]

    for table in tables:
        try:
            describe_sql = describe_table_template.format(table_name=table)
            cols_res = db.execute(describe_sql)
            columns = [row[0].lower() for row in cols_res.fetchall()]

            if column_name.lower() in columns:
                # If column is found, get the total row count of the table
                count_sql = get_count_template.format(table_name=table)
                count_res = db.execute(count_sql)
                count = count_res.fetchone()[0]
                found_in[table] = count

        except Exception as e:
            debugger.add_log(f"Skipping table '{table}' due to error: {e}", agent="CORE", level="WARNING", process="DB:FindColRefs")
            continue

    # Sort by count descending, as in the original script
    sorted_found_in = dict(sorted(found_in.items(), key=lambda item: item[1], reverse=True))

    return sorted_found_in
