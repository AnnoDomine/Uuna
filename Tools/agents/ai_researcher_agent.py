import sys
import os
sys.path.append(os.getcwd())

print(">>> TRACE: Imports start", flush=True)
import requests
import json
import time
import subprocess
import threading
import re
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
print(">>> TRACE: Imports done", flush=True)

# Project modules
print(">>> TRACE: Project modules start", flush=True)
import Tools.online_researcher as online_researcher
import Tools.cartographer as cartographer
print(">>> TRACE: Project modules done", flush=True)

MASTER_DB = 'Data/WoW_Master.duckdb'
BUILD_REGISTRY = 'Data/dbs/Build_Registry.db'
OLLAMA_URL = "http://localhost:11434/api/chat"
DB_SERVICE_URL = "http://127.0.0.1:8001"
MODEL_NAME = "qwen3:8b"
print(">>> TRACE: Constants set", flush=True)

# Global Config (can be overridden by main)
AI_COOLDOWN = 4.0
AI_THREADS = 6
AI_DEBUG = True
AI_CONCURRENCY = 1

# Configure Loguru
logger.remove()
LOG_FORMAT = "[{extra[run_worker]} - {extra[build_index]} - {extra[run_info]} - {time:YYYY-MM-DD HH:mm:ss} - {level} - {extra[process]} - {extra[build]}]: {message}"

def sink_filter(record):
    for key in ["run_worker", "build_index", "run_info", "process", "build"]:
        if key not in record["extra"]:
            record["extra"][key] = "N/A"
    return True

logger.add(sys.stderr, format=LOG_FORMAT, filter=sink_filter)

session_ts = time.strftime("%Y%m%d_%H%M%S")
logger.add(f"Data/logs/ai_agent_{session_ts}.log", format=LOG_FORMAT, filter=sink_filter, rotation="10 MB")

def get_safe_log(run_info="N/A", process="DB", build="N/A", run_worker="N/A", build_index="N/A"):
    """Returns a logger bound with required fields to avoid KeyErrors."""
    return logger.bind(run_info=run_info, process=process, build=build, run_worker=run_worker, build_index=build_index)

def db_query(sql, params=[], run_info="N/A", run_worker="N/A", build_index="N/A"):
    """Unified API-based query function."""
    log = get_safe_log(run_info=run_info, run_worker=run_worker, build_index=build_index)
    try:
        r = requests.post(f"{DB_SERVICE_URL}/query", json={"sql": sql, "params": params}, timeout=60)
        r.raise_for_status()
        return r.json()["results"]
    except Exception as e:
        log.error(f"DB API Query failed: {e}")
        raise e

def db_execute(sql, params=[], run_info="N/A", run_worker="N/A", build_index="N/A"):
    """Unified API-based execution function."""
    log = get_safe_log(run_info=run_info, run_worker=run_worker, build_index=build_index)
    try:
        r = requests.post(f"{DB_SERVICE_URL}/execute", json={"sql": sql, "params": params}, timeout=60)
        r.raise_for_status()
        return True
    except Exception as e:
        log.error(f"DB API Execute failed: {e}")
        return False

def get_ai_setting(key, default):
    try:
        res = db_query(load_query("agent", "get_setting"), (key,), run_info="INIT")
        return res[0][0] if res else default
    except: return default

PROMPT_CACHE = {}
def load_prompt(role, task):
    path = f"Tools/prompts/{role}/{task}.txt"
    if path in PROMPT_CACHE: return PROMPT_CACHE[path]
    try:
        with open(path, "r") as f:
            content = f.read()
            PROMPT_CACHE[path] = content
            return content
    except: return ""

QUERY_CACHE = {}
FORBIDDEN_KEYWORDS = ["drop", "truncate", "alter", "grant", "revoke", "delete"]

def sanitize_identifier(name):
    """Ensure table/column names only contain alphanumeric characters and underscores."""
    if not re.match(r"^[a-zA-Z0-9_.]+$", str(name)):
        logger.error(f"SECURITY ALERT: Invalid identifier detected: {name}")
        sys.exit(1)
    return str(name)

def validate_sql(sql, context=""):
    """Runtime check for forbidden keywords and injection patterns."""
    sql_lower = sql.lower()
    for word in FORBIDDEN_KEYWORDS:
        if f" {word} " in f" {sql_lower} " or sql_lower.startswith(word):
            logger.error(f"SECURITY BLOCKED: Forbidden keyword '{word.upper()}' in SQL {context}")
            sys.exit(1)
    return sql

def load_query(role, task):
    path = f"Tools/queries/{role}/{task}.sql"
    if path in QUERY_CACHE: return QUERY_CACHE[path]
    try:
        with open(path, "r") as f:
            content = f.read()
            validate_sql(content, f"file: {path}")
            QUERY_CACHE[path] = content
            return content
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to load query {path}: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

last_activity_time = time.time()
activity_lock = threading.Lock()
def update_activity():
    global last_activity_time
    with activity_lock: last_activity_time = time.time()

class ResearchToolkit:
    @staticmethod
    def extract_features(build_version):
        subprocess.run([".venv/bin/python3", "Tools/feature_extractor.py", build_version], capture_output=True)
    @staticmethod
    def query_db(query, params=(), run_info="N/A", run_worker="N/A", build_index="N/A"):
        return db_query(query, params, run_info=run_info, run_worker=run_worker, build_index=build_index)
    @staticmethod
    def check_ids(table_name, id_list, run_info="N/A", run_worker="N/A", build_index="N/A"):
        """Action: Checks if provided IDs exist in the target table."""
        if not id_list: return 0
        try:
            clean_ids = list(set([int(x) for x in id_list if str(x).replace('-','').isdigit()]))
            if not clean_ids: return 0
            sql_template = load_query("agent", "check_id_existence")
            safe_table = sanitize_identifier(table_name)
            query = sql_template.format(table=safe_table, id_list=','.join(map(str, clean_ids)))
            validate_sql(query, "check_ids task")
            res = db_query(query, run_info=run_info, run_worker=run_worker, build_index=build_index)
            return res[0][0] if res else 0
        except Exception as e:
            return 0
    @staticmethod
    def save_discovery(build_id, table, col, discovery, confidence, run_info="N/A", run_worker="N/A", build_index="N/A"):
        db_execute(load_query("agent", "save_discovery"), 
                   (build_id, table, col, str(discovery), confidence), run_info=run_info, run_worker=run_worker, build_index=build_index)
        update_activity()
    @staticmethod
    def save_attempt(build_version, table, col, target, decision, reasoning, run_info="N/A", run_worker="N/A", build_index="N/A"):
        db_execute(load_query("agent", "save_attempt"), 
                    (build_version, table, col, target, decision, str(reasoning)), run_info=run_info, run_worker=run_worker, build_index=build_index)
        update_activity()
    @staticmethod
    def get_last_attempt(table, col, run_info="N/A", run_worker="N/A", build_index="N/A"):
        res = db_query(load_query("agent", "get_last_attempt"), (table, col), run_info=run_info, run_worker=run_worker, build_index=build_index)
        return res[0] if res else None
    @staticmethod
    def update_knowledge(column_pattern, table_context, target_table, confidence, build_version, ai_notes=None, run_info="N/A", run_worker="N/A", build_index="N/A"):
        db_execute(load_query("agent", "upsert_global_knowledge"), 
                   (column_pattern, table_context, target_table, confidence, str(ai_notes), build_version), run_info=run_info, run_worker=run_worker, build_index=build_index)
        update_activity()

def clean_confidence(val):
    if isinstance(val, (int, float)): return float(val)
    val_map = {"high": 0.9, "medium": 0.5, "low": 0.2, "certain": 1.0, "likely": 0.7, "probable": 0.6}
    return val_map.get(str(val).lower().strip(), 0.0)

def clean_target(name, all_tables=None):
    if not isinstance(name, str): return "UNKNOWN"
    target = name.split()[-1].replace("'", "").replace('"', "").strip()
    if all_tables and target != "NONE":
        base = target
        if target.lower().endswith("id"): base = target[:-2]
        if target in all_tables: return target
        if base in all_tables: return base
        if f"{base}s" in all_tables: return f"{base}s"
        v_match = [t for t in all_tables if t.startswith(base) and ("V" in t or t[-1].isdigit())]
        if v_match: return sorted(v_match)[0]
    return target

def robust_json_decode(data):
    if not isinstance(data, dict): return {}
    if len(data) == 1:
        key = list(data.keys())[0]
        if isinstance(data[key], dict): return data[key]
    for wrapper in ["analysis", "result", "query_analysis"]:
        if wrapper in data and isinstance(data[wrapper], dict): return data[wrapper]
    return data

def ask_ai(role, prompt, build_ver, run_info, process_name, run_worker="N/A", build_index="N/A"):
    log = get_safe_log(build=build_ver, run_info=run_info, process=process_name, run_worker=run_worker, build_index=build_index)
    if AI_DEBUG: log.debug(f"\n{'='*80}\n[DEBUG] ROLE: {role}\nPROMPT:\n{prompt}\n{'-'*80}")
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": f"You are {role}. Return ONLY raw JSON."}, {"role": "user", "content": prompt}],
        "stream": False, "format": "json", "options": {"num_thread": AI_THREADS, "temperature": 0.1}
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120).json()
        update_activity()
        content = r['message']['content']
        if AI_DEBUG: log.debug(f"RAW RESPONSE:\n{content}\n{'='*80}")
        return robust_json_decode(json.loads(content))
    except: return {}

def get_version_context(current, previous):
    if not previous: return "NEVER-SAW-IN-PREVIOUS-VERSIONS"
    c_parts = current.split('.'); p_parts = previous.split('.')
    if c_parts[0] != p_parts[0]: return f"MAJOR EXPANSION UPDATE (from {previous} to {current})"
    if c_parts[1] != p_parts[1]: return f"MINOR CONTENT PATCH (from {previous} to {current})"
    return f"MINOR BUILD UPDATE / HOTFIX (from {previous} to {current})"

def analyze_column_task(col_info, build_id, build_version, toolkit, run_info, version_context="", run_worker="N/A", build_index="N/A"):
    f_id, table, col, d_type, v_min, v_max = col_info
    log = get_safe_log(build=build_version, run_info=run_info, process="Analysis", run_worker=run_worker, build_index=build_index)
    log.debug(f"Starting analysis for {table}.{col} (Type: {d_type}, Range: {v_min}-{v_max})")
    
    safe_table = sanitize_identifier(table)
    safe_col = sanitize_identifier(col)
    sample_sql = load_query("agent", "get_column_samples").format(col=safe_col, table=safe_table)
    validate_sql(sample_sql, f"samples query for {table}.{col}")
    samples = [r[0] for r in toolkit.query_db(sample_sql, (build_id, table), run_info=run_info, run_worker=run_worker, build_index=build_index)]
    
    prev_discoveries = toolkit.query_db(load_query("agent", "get_legacy_discoveries"), (table, col, build_id), run_info=run_info, run_worker=run_worker, build_index=build_index)
    existing = toolkit.query_db(load_query("agent", "get_global_knowledge"), (col, table), run_info=run_info, run_worker=run_worker, build_index=build_index)
    all_tables = [r[0] for r in toolkit.query_db(load_query("agent", "get_available_tables"), run_info=run_info, run_worker=run_worker, build_index=build_index)]
    last_attempt = toolkit.get_last_attempt(table, col, run_info=run_info, run_worker=run_worker, build_index=build_index)
    
    is_first_time = not last_attempt
    memory_section = f"\n### VERSIONING CONTEXT:\n- {version_context}\n"
    if prev_discoveries or existing or last_attempt:
        memory_section += "\n### LEGACY KNOWLEDGE:\n"
        if last_attempt:
            target_p, decision_p, reason_p = last_attempt
            memory_section += f"- LAST RESEARCH RESPONSE: [{decision_p}] Proposed '{target_p}'. Reason: {reason_p}\n"
        else:
            memory_section += "- STATUS: NEVER-SAW-IN-PREVIOUS-VERSIONS\n"
        if existing: memory_section += f"- PREVIOUS MAPPING: table '{existing[0][0]}'. Notes: {existing[0][1]}\n"
        for d in prev_discoveries: memory_section += f"- PAST DISCOVERY: {d[0]}\n"
    else:
        memory_section += "\n### LEGACY KNOWLEDGE:\n- STATUS: NEVER-SAW-IN-PREVIOUS-VERSIONS\n"

    online_info = ""
    if is_first_time or (last_attempt and last_attempt[1] == "VETO"):
        try:
            wago_headers = online_researcher.get_wago_structure(table, build_version, run_info=run_info)
            online_info += f"\n### WAGO.TOOLS STRUCTURE:\n{wago_headers}\n"
            wiki_links = online_researcher.get_wow_wiki_search(f"WoW DB2 {table} {col}", run_info=run_info)
            if wiki_links:
                content = online_researcher.get_wow_wiki_content(wiki_links[0], run_info=run_info)
                online_info += f"\n### ONLINE RESEARCH (WoW Wiki):\nURL: {wiki_links[0]}\nCONTENT: {content[:500]}...\n"
        except: pass

    is_value_col = any(col.lower().endswith(s) for s in ["msec", "count", "amount", "charges", "percent", "flag", "flags", "index", "idx"])
    if is_value_col: template = load_prompt("archivist", "value_research_metrics_and_enums")
    else: template = load_prompt("archivist", "discovery_column_semantics_and_structure")
    
    p_disc = template.format(table=table, col=col, v_min=v_min, v_max=v_max, samples=samples, memory_section=memory_section, online_info=online_info)
    disc = ask_ai("WoW Lore Archivist", p_disc, build_version, run_info, "Discovery", run_worker=run_worker, build_index=build_index)
    discovery_text = disc.get("discovery") or "Analysis pending"
    toolkit.save_discovery(build_id, table, col, discovery_text, disc.get('confidence', 0.5), run_info=run_info, run_worker=run_worker, build_index=build_index)

    preds = toolkit.query_db(load_query("agent", "get_statistical_predictions"), (f_id,), run_info=run_info, run_worker=run_worker, build_index=build_index)
    ai_type = str(disc.get("type", "")).lower()
    should_map = (ai_type == "structure" or col.lower().endswith("id") or preds) and not is_value_col

    if should_map:
        template = load_prompt("engineer", "mapping_references_between_tables_and_columns")
        p_map = template.format(table=table, col=col, samples=samples, preds=preds, memory_section=memory_section, online_info=online_info, all_tables=all_tables[:100])
        prop = ask_ai("WoW Data Engineer", p_map, build_version, run_info, "Mapping", run_worker=run_worker, build_index=build_index)
        target = clean_target(prop.get("target", "NONE"), all_tables=all_tables)
        if target != "NONE":
            match_count = toolkit.check_ids(target, samples, run_info=run_info, run_worker=run_worker, build_index=build_index)
            proof = f"ID Check: {match_count} of {len(samples)} samples found in target '{target}'."
            p_crit = load_prompt("critic", "verification_mapping_integrity_and_id_checks").format(table=table, col=col, target=target, proof=proof)
            crit = ask_ai("Senior Critic", p_crit, build_version, run_info, "Critic", run_worker=run_worker, build_index=build_index)
            decision = str(crit.get("decision", "")).lower()
            reasoning = crit.get("reasoning", "No reason provided")
            toolkit.save_attempt(build_version, table, col, target, decision.upper(), f"{proof} | {reasoning}", run_info=run_info, run_worker=run_worker, build_index=build_index)
            if decision in ("confirm", "yes", "true"):
                toolkit.update_knowledge(col, table, target, clean_confidence(prop.get('confidence', 0.5)), build_version, ai_notes=f"{proof} | {prop.get('reasoning')}", run_info=run_info, run_worker=run_worker, build_index=build_index)
                print(f"[{run_worker} - {build_index}] [✅] {table}.{col} -> {target}", flush=True)
            else: print(f"[{run_worker} - {build_index}] [❌] Vetoed: {table}.{col} -> {target}", flush=True)
    else: print(f"[{run_worker} - {build_index}] [💡] {table}.{col}: {discovery_text[:60]}...", flush=True)
    time.sleep(AI_COOLDOWN)

def process_build(build_version, toolkit, limit=5, prev_version=None):
    print(f"\n>>> RESEARCHING BUILD: {build_version} <<<", flush=True)
    version_context = get_version_context(build_version, prev_version)
    res = db_query(load_query("agent", "get_build_id"), (build_version,), run_info="BUILD_INIT")
    if not res: return
    build_id = res[0][0]
    cols = db_query(load_query("agent", "get_columns_for_build"), (build_id, limit), run_info="FETCH_COLS")
    print(f"Starting parallel analysis of {len(cols)} columns using {AI_CONCURRENCY} workers...", flush=True)
    with ThreadPoolExecutor(max_workers=AI_CONCURRENCY) as executor:
        futures = []
        for i, col_info in enumerate(cols, 1):
            worker_id = f"W{(i-1)%AI_CONCURRENCY + 1}"
            futures.append(executor.submit(analyze_column_task, col_info, build_id, build_version, toolkit, f"{i}/{len(cols)}", version_context, run_worker=worker_id, build_index=f"{i}/{len(cols)}"))
        for f in futures: 
            try: f.result()
            except Exception as e: logger.error(f"Task failed: {e}")
    cartographer.update_build_map(build_version, toolkit, ask_ai, run_info="FINAL")

def main():
    print("DEBUG: Agent main() started", flush=True)
    
    # Wait for DB Service
    print("Waiting for DB Service at " + DB_SERVICE_URL, flush=True)
    max_retries = 30
    for i in range(max_retries):
        try:
            requests.post(f"{DB_SERVICE_URL}/query", json={"sql": "SELECT 1"}, timeout=2).raise_for_status()
            print("DB Service is ready!", flush=True)
            break
        except:
            if i == max_retries - 1:
                print("DB Service unreachable. Exiting.", flush=True)
                sys.exit(1)
            time.sleep(1)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start"); parser.add_argument("--end"); parser.add_argument("--limit", type=int)
    args = parser.parse_args(); toolkit = ResearchToolkit()
    all_local = [r[0] for r in db_query(load_query("agent", "get_available_builds"), run_info="MAIN")]
    if not all_local: return
    s_idx = all_local.index(args.start) if args.start in all_local else 0
    e_idx = all_local.index(args.end) if args.end in all_local else len(all_local)-1
    
    global AI_COOLDOWN, AI_THREADS, AI_DEBUG, AI_CONCURRENCY
    AI_COOLDOWN = float(get_ai_setting("cooldown", "4.0"))
    AI_THREADS = int(get_ai_setting("threads", "6"))
    AI_DEBUG = os.getenv("AI_DEBUG", "1") == "1"
    AI_CONCURRENCY = int(os.getenv("AI_CONCURRENCY", "1"))
    
    prev_v = all_local[s_idx-1] if s_idx > 0 else None
    for build in all_local[s_idx:e_idx+1]:
        process_build(build, toolkit, limit=args.limit or 5, prev_version=prev_v)
        prev_v = build

if __name__ == "__main__": 
    print(">>> AGENT SCRIPT EXECUTION START <<<", flush=True)
    main()
    print(">>> AGENT SCRIPT EXECUTION END <<<", flush=True)