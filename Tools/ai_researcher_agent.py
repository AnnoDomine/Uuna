import json
import sqlite3
import os
import requests
import time
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import threading

KNOWLEDGE_DB = 'Data/dbs/WoW_Research_Knowledge.db'
BUILD_REGISTRY = 'Data/dbs/Build_Registry.db'
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

def get_ai_setting(key, default):
    try:
        conn = sqlite3.connect(KNOWLEDGE_DB); cur = conn.cursor()
        cur.execute("SELECT value FROM ai_settings WHERE key = ?", (key,))
        row = cur.fetchone(); conn.close()
        return row[0] if row else default
    except: return default

AI_COOLDOWN = float(os.getenv("AI_COOLDOWN", get_ai_setting("cooldown", "4.0")))
AI_THREADS = int(os.getenv("AI_THREADS", get_ai_setting("threads", "6")))
AI_DEBUG = os.getenv("AI_DEBUG", get_ai_setting("debug", "0")) == "1"
AI_CONCURRENCY = int(os.getenv("AI_CONCURRENCY", "1"))

last_activity_time = time.time()
activity_lock = threading.Lock()

def update_activity():
    global last_activity_time
    with activity_lock: last_activity_time = time.time()

class ResearchToolkit:
    @staticmethod
    def extract_features(build_version):
        print(f"[AGENT] Extracting features for {build_version}...")
        subprocess.run([".venv/bin/python3", "Tools/feature_extractor.py", build_version], capture_output=True)

    @staticmethod
    def query_db(db_path, query, params=()):
        conn = sqlite3.connect(db_path); cur = conn.cursor()
        cur.execute(query, params); res = cur.fetchall(); conn.close()
        return res

    @staticmethod
    def save_discovery(build_id, table, col, discovery, confidence):
        conn = sqlite3.connect(KNOWLEDGE_DB); cur = conn.cursor()
        cur.execute("INSERT INTO ai_discoveries (build_id, table_name, column_name, discovery, confidence) VALUES (?,?,?,?,?)",
                   (build_id, table, col, str(discovery), confidence))
        conn.commit(); conn.close()
        update_activity()

    @staticmethod
    def update_knowledge(column_pattern, table_context, target_table, confidence, build_version, ai_notes=None):
        conn = sqlite3.connect(KNOWLEDGE_DB); cur = conn.cursor()
        cur.execute('''
            INSERT INTO global_knowledge (column_pattern, source_table_context, target_table, confidence, last_verified_build, ai_notes, confirmations)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(column_pattern, source_table_context, target_table) DO UPDATE SET
                confirmations = confirmations + 1,
                last_verified_build = excluded.last_verified_build,
                ai_notes = COALESCE(excluded.ai_notes, ai_notes),
                confidence = (confidence + excluded.confidence) / 2
        ''', (column_pattern, table_context, target_table, confidence, build_version, str(ai_notes)))
        conn.commit(); conn.close()
        update_activity()

def clean_confidence(val):
    if isinstance(val, (int, float)): return float(val)
    if not isinstance(val, str): return 0.0
    val_map = {"high": 0.9, "medium": 0.5, "low": 0.2, "certain": 1.0, "likely": 0.7, "probable": 0.6}
    return val_map.get(val.lower().strip(), 0.0)

def clean_target(name):
    if not isinstance(name, str): return "UNKNOWN"
    return name.split()[-1].replace("'", "").replace('"', "").strip()

def robust_json_decode(data):
    """Tries to find the actual content even if the AI wraps it in extra keys."""
    if not isinstance(data, dict): return {}
    # If AI returns {"column_name": {"discovery": ...}}, flatten it
    if len(data) == 1:
        key = list(data.keys())[0]
        if isinstance(data[key], dict): return data[key]
    # If AI uses "analysis" or "result" as wrapper
    for wrapper in ["analysis", "result", "query_analysis"]:
        if wrapper in data and isinstance(data[wrapper], dict): return data[wrapper]
    return data

def ask_ai(role, prompt):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": f"You are {role}. Return ONLY raw JSON. No markdown, no preamble. "
                                         "Follow the exact schema provided in the task."},
            {"role": "user", "content": prompt}
        ],
        "stream": False, "format": "json", "options": {"num_thread": AI_THREADS, "temperature": 0.1}
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120).json()
        update_activity()
        content = r['message']['content']
        decoded = json.loads(content)
        return robust_json_decode(decoded)
    except: return {}

def analyze_column_task(col_info, build_id, build_version, toolkit):
    f_id, table, col, d_type, v_min, v_max = col_info
    
    # 1. DISCOVERY PHASE
    prompt_disc = f"""
    Analyze WoW database column: {table}.{col}
    Stats: {v_min} to {v_max}
    Return ONLY JSON using this EXACT schema:
    {{
        "discovery": "Short semantic description of the column purpose",
        "type": "structure" (if it's an ID/ref) or "content" (if it's text/stats),
        "confidence": 0.9
    }}
    """
    disc = ask_ai("WoW Lore Archivist", prompt_disc)
    discovery_text = disc.get("discovery") or "Analysis pending"
    toolkit.save_discovery(build_id, table, col, discovery_text, disc.get('confidence', 0.5))
    
    msg = f"  [💡] {table}.{col}: {str(discovery_text)[:60]}..."
    
    # 2. MAPPING PHASE
    preds = toolkit.query_db(KNOWLEDGE_DB, "SELECT target_table, confidence FROM statistical_predictions WHERE feature_id = ?", (f_id,))
    if col.endswith("ID") or len(preds) > 0:
        prompt_map = f"""
        Map WoW column: {table}.{col}. Suggestions: {preds}
        Return ONLY JSON using this EXACT schema:
        {{
            "target": "CorrectTableName",
            "confidence": 0.95,
            "reasoning": "Brief explanation"
        }}
        """
        prop = ask_ai("WoW Data Engineer", prompt_map)
        if prop.get("target") and prop.get("target") != "NONE":
            target = clean_target(prop['target'])
            conf = clean_confidence(prop.get('confidence', 0.5))
            
            prompt_crit = f"Verify: {table}.{col} -> {target}. Reasoning: {prop.get('reasoning')}. Return JSON: {{\"decision\": \"confirm\", \"reasoning\": \"...\"}}"
            crit = ask_ai("Senior Critic", prompt_crit)
            
            if str(crit.get("decision", "")).lower() in ("confirm", "yes", "true"):
                toolkit.update_knowledge(col, table, target, conf, build_version, ai_notes=prop.get('reasoning'))
                msg += f" | [✅] -> {target}"
            else: msg += f" | [❌] Vetoed"
    
    print(msg, flush=True)
    time.sleep(AI_COOLDOWN)

def process_build(build_version, toolkit, limit=5):
    print(f"\n>>> RESEARCHING BUILD: {build_version} <<<", flush=True)
    if not toolkit.query_db(KNOWLEDGE_DB, "SELECT id FROM builds WHERE version = ?", (build_version,)):
        toolkit.extract_features(build_version)
    
    build_id = toolkit.query_db(KNOWLEDGE_DB, "SELECT id FROM builds WHERE version = ?", (build_version,))[0][0]
    cols = toolkit.query_db(KNOWLEDGE_DB, "SELECT id, table_name, column_name, data_type, min_val, max_val FROM column_features WHERE build_id = ? AND column_name NOT IN ('ID', 'build_id') LIMIT ?", (build_id, limit))

    with ThreadPoolExecutor(max_workers=AI_CONCURRENCY) as executor:
        for col_info in cols: 
            executor.submit(analyze_column_task, col_info, build_id, build_version, toolkit)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--limit", type=int, help="Limit of columns per build (Default from DB)")
    args = parser.parse_args(); toolkit = ResearchToolkit()
    
    # Use arg if provided, otherwise DB setting, otherwise fallback 100000
    current_limit = args.limit if args.limit is not None else int(get_ai_setting("limit_per_build", "100000"))
    
    all_local = [r[0] for r in toolkit.query_db(BUILD_REGISTRY, "SELECT version FROM builds WHERE is_downloaded=1 ORDER BY id ASC")]
    if not all_local: return
    s_idx = all_local.index(args.start) if args.start in all_local else 0
    e_idx = all_local.index(args.end) if args.end in all_local else len(all_local)-1
    for build in all_local[s_idx:e_idx+1]: 
        process_build(build, toolkit, limit=current_limit)

if __name__ == "__main__":
    main()
