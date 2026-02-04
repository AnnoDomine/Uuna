import duckdb
import os
import time
import sys
import json
import traceback
from loguru import logger

MASTER_DB = 'Data/WoW_Master.duckdb'
QUERIES_DIR = 'Tools/analysis/queries/feature_extractor'

# UNIFIED LOG SCHEMA
logger.remove()
LOG_FORMAT = "[{extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
logger.add("Data/logs/migration.log", format=LOG_FORMAT, rotation="10 MB", level="DEBUG")

def get_con():
    return duckdb.connect(MASTER_DB)

def load_query(name):
    path = os.path.join(QUERIES_DIR, f"{name}.sql")
    with open(path, 'r') as f:
        return f.read().strip()

def process_build_features(build_version):
    start_time = time.time()
    # Initial bind
    base_log = logger.bind(run_info="INIT", process="Indexer", build=build_version)
    base_log.info(f">>> Analyzing Build: {build_version} <<< ")
    
    con = get_con()
    sql_init_infra = load_query("init_infrastructure")
    sql_check_table = load_query("check_table_exists")
    sql_get_build_id = load_query("get_build_id")
    sql_get_tables = load_query("get_tables_for_build")
    sql_get_row_count = load_query("get_row_count")
    sql_get_stats_tpl = load_query("get_column_stats")
    sql_get_samples_tpl = load_query("get_column_samples")
    sql_save_feature = load_query("save_feature")
    sql_mark_indexed = load_query("mark_build_indexed")
    sql_log_error = load_query("log_error")

    con.execute(sql_init_infra)

    res = con.execute(sql_get_build_id, (build_version,)).fetchone()
    if not res:
        base_log.error(f"Build {build_version} not in registry.")
        return
    build_id = res[0]

    tables = [row[0] for row in con.execute(sql_get_tables, (build_id,)).fetchall()]
    total_tables = len(tables)
    
    total_cols = 0
    for idx, table in enumerate(tables, 1):
        run_info = f"{idx}/{total_tables}"
        t_log = logger.bind(run_info=run_info, process="Indexing", build=build_version)
        
        try:
            table_exists = con.execute(sql_check_table, (table,)).fetchone()[0]
            if not table_exists:
                t_log.warning(f"Table {table} MISSING in archive. Logged for re-sync.")
                con.execute(sql_log_error, (build_id, table, "MISSING_TABLE", "Missing in archive schema."))
                continue

            cols_info = con.execute(f"PRAGMA table_info(archive.\"{table}\")").df()
            if cols_info.empty: continue
                
            columns = [c for c in cols_info['name'].tolist() if c not in ('_row_hash', 'build_id')]
            build_rows = con.execute(sql_get_row_count, (build_id, table)).fetchone()[0]
            
            if idx % 50 == 0 or idx == 1:
                t_log.info(f"Processing: {table} ({build_rows} rows)")

            for col in columns:
                total_cols += 1
                try:
                    stats_query = sql_get_stats_tpl.format(table=table, col=col)
                    stats = con.execute(stats_query, (build_id, table)).fetchone()
                    if not stats: continue
                    
                    samples_query = sql_get_samples_tpl.format(table=table, col=col)
                    sample_data = con.execute(samples_query, (build_id, table)).fetchall()
                    samples = [row[0] for row in sample_data]
                    
                    con.execute(sql_save_feature, (build_id, table, col, stats[0], str(stats[2]), str(stats[3]), stats[4], json.dumps(samples)))
                except: continue

        except Exception as e:
            t_log.error(f"Error in {table}: {e}")
            con.execute(sql_log_error, (build_id, table, "CRASH", str(e)))

    con.execute(sql_mark_indexed, (build_id,))
    elapsed = time.time() - start_time
    logger.bind(run_info="DONE", process="Indexer", build=build_version).success(f"Finished: {total_cols} columns in {elapsed:.1f}s")
    con.close()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        process_build_features(sys.argv[1])