# Tools/toolsets/tools/database/find_column_references.py
from typing import Dict
import sys
import os
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

# Define paths to query directories
QUERY_DIR_SPECIFIC = Path(__file__).parent / "queries" / "find_column_references"
QUERY_DIR_GENERIC = Path(__file__).parent / "queries" / "find_value"  # Re-use generic queries


def _load_query(name: str, specific_dir: Path) -> str:
    """Loads a SQL query from a specified query directory."""
    with open(specific_dir / name, "r") as f:
        return f.read().strip()


def find_column_references(db_client: DBClient, column_name: str) -> Dict[str, int]:
    """
    Finds all tables in the 'archive' schema that contain a specific column,
    and returns a dictionary mapping the table name to its total row count.

    Args:
        db_client: An instance of DBClient to interact with the database service.
        column_name: The name of the column to search for.

    Returns:
        A dictionary mapping table names to their total row count for tables
        containing the specified column.
    """
    found_in = {}

    # --- Load all queries first ---
    get_tables_sql = _load_query("get_archive_tables.sql", QUERY_DIR_GENERIC)
    describe_table_template = _load_query("describe_table.sql", QUERY_DIR_GENERIC)
    get_count_template = _load_query("get_table_count.sql", QUERY_DIR_SPECIFIC)

    # --- Execute logic ---
    tables_res = db_client.execute(get_tables_sql)
    tables = [row[0] for row in tables_res.fetchall()]

    for table in tables:
        try:
            describe_sql = describe_table_template.format(table_name=table)
            cols_res = db_client.execute(describe_sql)
            columns = [row[0].lower() for row in cols_res.fetchall()]

            if column_name.lower() in columns:
                # If column is found, get the total row count of the table
                count_sql = get_count_template.format(table_name=table)
                count_res = db_client.execute(count_sql)
                count = count_res.fetchone()[0]
                found_in[table] = count

        except Exception as e:
            print(f"Skipping table '{table}' due to error: {e}")
            continue

    # Sort by count descending, as in the original script
    sorted_found_in = dict(sorted(found_in.items(), key=lambda item: item[1], reverse=True))

    return sorted_found_in
