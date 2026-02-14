# Tools/toolsets/tools/database/find_value.py
from typing import Optional, Dict
import sys
import os
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.db_client import DBClient

# Define the path to the queries for this specific tool
QUERY_DIR = Path(__file__).parent / "queries" / "find_value"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / name, "r") as f:
        return f.read().strip()


def find_value(db_client: DBClient, search_term: str, build_version: Optional[str] = None) -> Dict[str, int]:
    """
    Searches for a given value across all tables in the 'archive' schema by loading external SQL files.

    Args:
        db_client: An instance of DBClient to interact with the database service.
        search_term: The value to search for.
        build_version: Optional specific build version to filter the search.

    Returns:
        A dictionary mapping table names to the count of matches found.
    """
    found_in = {}
    build_id = None

    if build_version:
        sql = _load_query("get_build_id_by_version.sql")
        res = db_client.execute(sql, [build_version])
        build_id_row = res.fetchone()
        if not build_id_row:
            raise ValueError(f"Build version '{build_version}' not found in registry.")
        build_id = build_id_row[0]

    # 1. Get all tables in the 'archive' schema
    tables_sql = _load_query("get_archive_tables.sql")
    tables_res = db_client.execute(tables_sql)
    tables = [row[0] for row in tables_res.fetchall()]

    # Load templates once
    describe_template = _load_query("describe_table.sql")
    count_template = _load_query("count_matches.sql")
    count_with_build_template = _load_query("count_matches_with_build.sql")

    for table in tables:
        try:
            # 2. Get columns for the current table
            describe_sql = describe_template.format(table_name=table)
            cols_res = db_client.execute(describe_sql)
            columns = [row[0] for row in cols_res.fetchall()]

            # We search for exact match as string or number
            clauses = [f'"{col}" = ?' for col in columns]
            where_clause = " OR ".join(clauses)

            params = [search_term] * len(columns)

            if build_id:
                if "build_id" in [c.lower() for c in columns]:
                    query = count_with_build_template.format(table_name=table, where_clause=where_clause)
                    params.append(build_id)
                else:
                    continue
            else:
                query = count_template.format(table_name=table, where_clause=where_clause)

            # 3. Execute the count query
            count_res = db_client.execute(query, params)
            count = count_res.fetchone()[0]

            if count > 0:
                found_in[table] = count
        except Exception as e:
            print(f"Skipping table '{table}' due to error: {e}")
            continue

    return found_in
