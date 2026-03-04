# Tools/toolsets/tools/analysis/extract_features.py
import json
import time
from pathlib import Path

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "extract_features"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def extract_features_for_build(build_version: str) -> dict:
    """
    Extracts column features (stats, samples) from a build.

    Args:
    - build_version: The version string of the build (e.g. '10.0.0.12345').
    """
    start_time = time.time()
    debugger.add_log(f"Feature extraction started for build: {build_version}", agent="CORE", process="Analysis:ExtractFeatures")

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
    db.execute(queries["init_infra"])

    # Get Build ID
    res = db.execute(queries["get_build_id"], [build_version]).fetchone()
    if not res:
        return {"status": "error", "message": f"Build {build_version} not in registry."}
    build_id = res[0]

    # Get all tables for the build
    tables = [row[0] for row in db.execute(queries["get_tables"], [build_id]).fetchall()]
    total_tables = len(tables)
    total_cols = 0

    for idx, table in enumerate(tables, 1):
        try:
            # Check if table exists in the main archive schema
            table_exists_res = db.execute(queries["check_table"], [table]).fetchone()
            if not table_exists_res or table_exists_res[0] == 0:
                debugger.add_log(f"Table {table} MISSING in archive. Logged for re-sync.", agent="CORE", level="WARNING", process="Analysis:ExtractFeatures")
                db.execute(queries["log_error"], [build_id, table, "MISSING_TABLE", "Missing in archive schema."])
                continue

            # Get column info
            cols_info_df = db.execute(f'PRAGMA table_info(archive."{table}")').df()
            if cols_info_df.empty:
                continue

            columns = [c for c in cols_info_df["name"].tolist() if c not in ("_row_hash", "build_id")]
            build_rows_res = db.execute(queries["get_row_count"], [build_id, table]).fetchone()
            build_rows = build_rows_res[0] if build_rows_res else 0

            if idx % 50 == 0 or idx == 1:
                debugger.add_log(f"Processing {idx}/{total_tables}: {table} ({build_rows} rows)", agent="CORE", process="Analysis:ExtractFeatures")

            for col in columns:
                total_cols += 1
                try:
                    stats_query = queries["get_stats_tpl"].format(table=table, col=col)
                    stats = db.execute(stats_query, [build_id, table]).fetchone()
                    if not stats:
                        continue

                    samples_query = queries["get_samples_tpl"].format(table=table, col=col)
                    sample_data = db.execute(samples_query, [build_id, table]).fetchall()
                    samples = [row[0] for row in sample_data]

                    db.execute(
                        queries["save_feature"],
                        [build_id, table, col, stats[0], str(stats[2]), str(stats[3]), stats[4], json.dumps(samples)],
                    )
                except Exception:
                    # Continue to next column on inner failure
                    continue

        except Exception as e:
            debugger.add_log(f"Critical error in table {table}: {e}", agent="CORE", level="ERROR", process="Analysis:ExtractFeatures")
            db.execute(queries["log_error"], [build_id, table, "CRASH", str(e)])

    # Mark build as indexed
    db.execute(queries["mark_indexed"], [build_id])
    elapsed = time.time() - start_time

    summary = {
        "status": "success",
        "processed_columns": total_cols,
        "processed_tables": total_tables,
        "duration_seconds": round(elapsed, 2),
    }
    debugger.add_log(f"Finished feature extraction for {build_version}. Processed {total_cols} columns in {elapsed:.1f}s", agent="CORE", level="SUCCESS", process="Analysis:ExtractFeatures")
    return summary
