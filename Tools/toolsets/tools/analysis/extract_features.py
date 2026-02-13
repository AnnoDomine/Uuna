# Tools/toolsets/tools/analysis/extract_features.py
import sys
import os
import time
import json
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.db_client import DBClient

QUERY_DIR = Path(__file__).parent / "queries" / "extract_features"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def extract_features_for_build(db_client: DBClient, build_version: str) -> dict:
    """
    Analyzes a build, extracts column features (stats, samples), and saves them
    to the research schema.
    """
    start_time = time.time()
    print(f"INFO: Feature extraction started for build: {build_version}")

    # Load all queries
    queries = {
        "init_infra": _load_query("init_infrastructure"),
        "check_table": _load_query("check_table_exists"),
        "get_build_id": _load_query("get_build_id"),
        "get_tables": _load_query("get_tables_for_build"),
        "get_row_count": _load_query("get_row_count"),
        "get_stats_tpl": _load_query("get_column_stats"),
        "get_samples_tpl": _load_query("get_column_samples"),
        "save_feature": _load_query("save_feature"),
        "mark_indexed": _load_query("mark_build_indexed"),
        "log_error": _load_query("log_error"),
    }

    # Execute infrastructure setup
    db_client.execute(queries["init_infra"])

    # Get Build ID
    res = db_client.execute(queries["get_build_id"], [build_version]).fetchone()
    if not res:
        return {"status": "error", "message": f"Build {build_version} not in registry."}
    build_id = res[0]

    # Get all tables for the build
    tables = [row[0] for row in db_client.execute(queries["get_tables"], [build_id]).fetchall()]
    total_tables = len(tables)
    total_cols = 0

    for idx, table in enumerate(tables, 1):
        try:
            # Check if table exists in the main archive schema
            table_exists_res = db_client.execute(queries["check_table"], [table]).fetchone()
            if not table_exists_res or table_exists_res[0] == 0:
                print(f"WARNING: Table {table} MISSING in archive. Logged for re-sync.")
                db_client.execute(
                    queries["log_error"], [build_id, table, "MISSING_TABLE", "Missing in archive schema."]
                )
                continue

            # Get column info
            cols_info_df = db_client.execute(f'PRAGMA table_info(archive."{table}")').df()
            if cols_info_df.empty:
                continue

            columns = [c for c in cols_info_df["name"].tolist() if c not in ("_row_hash", "build_id")]
            build_rows_res = db_client.execute(queries["get_row_count"], [build_id, table]).fetchone()
            build_rows = build_rows_res[0] if build_rows_res else 0

            if idx % 50 == 0 or idx == 1:
                print(f"INFO: Processing {idx}/{total_tables}: {table} ({build_rows} rows)")

            for col in columns:
                total_cols += 1
                try:
                    stats_query = queries["get_stats_tpl"].format(table=table, col=col)
                    stats = db_client.execute(stats_query, [build_id, table]).fetchone()
                    if not stats:
                        continue

                    samples_query = queries["get_samples_tpl"].format(table=table, col=col)
                    sample_data = db_client.execute(samples_query, [build_id, table]).fetchall()
                    samples = [row[0] for row in sample_data]

                    db_client.execute(
                        queries["save_feature"],
                        [build_id, table, col, stats[0], str(stats[2]), str(stats[3]), stats[4], json.dumps(samples)],
                    )
                except Exception:
                    # Continue to next column on inner failure
                    continue

        except Exception as e:
            print(f"ERROR: Critical error in table {table}: {e}")
            db_client.execute(queries["log_error"], [build_id, table, "CRASH", str(e)])

    # Mark build as indexed
    db_client.execute(queries["mark_indexed"], [build_id])
    elapsed = time.time() - start_time

    summary = {
        "status": "success",
        "processed_columns": total_cols,
        "processed_tables": total_tables,
        "duration_seconds": round(elapsed, 2),
    }
    print(f"SUCCESS: Finished feature extraction for {build_version}. Processed {total_cols} columns in {elapsed:.1f}s")
    return summary
