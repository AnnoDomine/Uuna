import sqlite3
import os
import json
import sys
import requests
import time

KNOWLEDGE_DB = 'Data/dbs/WoW_Research_Knowledge.db'
EMBEDDING_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "qwen3-embedding"

def get_embedding(text):
    try:
        payload = {"model": EMBEDDING_MODEL, "prompt": text}
        response = requests.post(EMBEDDING_URL, json=payload, timeout=30)
        return response.json()["embedding"]
    except: return None

def get_id_map(db_path):
    id_map = {}
    conn = sqlite3.connect(db_path); cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] not in ('builds', 'sqlite_sequence')]
    for table in tables:
        try:
            cursor.execute(f"SELECT ID FROM \"{table}\" LIMIT 1000")
            ids = set(row[0] for row in cursor.fetchall() if row[0] is not None)
            if ids: id_map[table] = ids
        except: continue
    conn.close()
    return id_map

def process_build(db_path):
    start_time = time.time()
    build_version = os.path.basename(db_path).replace('WoW_Data_', '').replace('.db', '')
    print(f"\n[INDEXER] >>> Starting Build: {build_version} <<<", flush=True)
    
    res_conn = sqlite3.connect(KNOWLEDGE_DB); res_cur = res_conn.cursor()
    res_cur.execute("INSERT OR IGNORE INTO builds (version) VALUES (?)", (build_version,))
    res_conn.commit()
    res_cur.execute("SELECT id FROM builds WHERE version = ?", (build_version,))
    build_id = res_cur.fetchone()[0]

    id_map = get_id_map(db_path)
    data_conn = sqlite3.connect(db_path); data_cur = data_conn.cursor()
    data_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in data_cur.fetchall() if row[0] not in ('builds', 'sqlite_sequence')]
    
    total_cols = 0
    total_preds = 0
    
    for table_idx, table in enumerate(tables, 1):
        data_cur.execute(f"PRAGMA table_info(\"{table}\")")
        columns = [col[1] for col in data_cur.fetchall()]
        data_cur.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        total_rows = data_cur.fetchone()[0]
        
        if table_idx % 50 == 0:
            print(f"  [Progress] Table {table_idx}/{len(tables)}: {table} ({len(columns)} columns)", flush=True)

        for col in columns:
            total_cols += 1
            data_cur.execute(f"SELECT COUNT(DISTINCT \"{col}\"), COUNT(\"{col}\"), MIN(\"{col}\"), MAX(\"{col}\") FROM \"{table}\"" )
            distinct_count, non_null_count, min_val, max_val = data_cur.fetchone()
            
            d_type = "int" if isinstance(min_val, int) else "float" if isinstance(min_val, float) else "string" if isinstance(min_val, str) else "unknown"
            d_ratio = distinct_count / total_rows if total_rows > 0 else 0
            n_ratio = (total_rows - non_null_count) / total_rows if total_rows > 0 else 0
            
            res_cur.execute('''INSERT OR REPLACE INTO column_features (build_id, table_name, column_name, data_type, distinct_ratio, min_val, max_val, null_ratio)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (build_id, table, col, d_type, d_ratio, str(min_val), str(max_val), n_ratio))
            feature_id = res_cur.lastrowid
            
            if d_type == "int" and max_val is not None and str(max_val).isdigit() and int(max_val) > 1 and col != "ID":
                data_cur.execute(f"SELECT DISTINCT \"{col}\" FROM \"{table}\" WHERE \"{col}\" > 0 LIMIT 100")
                samples = [row[0] for row in data_cur.fetchall()]
                if samples:
                    for target_table, target_ids in id_map.items():
                        if target_table == table: continue
                        matches = sum(1 for s in samples if s in target_ids)
                        if matches / len(samples) > 0.1:
                            res_cur.execute("INSERT INTO statistical_predictions (feature_id, target_table, confidence) VALUES (?, ?, ?)",
                                          (feature_id, target_table, matches / len(samples)))
                            total_preds += 1
        res_conn.commit()
    
    elapsed = time.time() - start_time
    print(f"[INDEXER] Finished {build_version}: {total_cols} columns indexed, {total_preds} cross-refs found in {elapsed:.1f}s", flush=True)
    data_conn.close(); res_conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    process_build(f"Data/dbs/WoW_Data_{sys.argv[1]}.db")
