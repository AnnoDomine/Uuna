# AI RESEARCHER AGENT - REFACTORED
#
import sys
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

# Ensure path resolution
sys.path.append(os.getcwd())

# Project modules
from core.db_client import DBClient
from core.ai_client import AIClient
from toolsets.tools.analysis.generate_relationship_map import generate_relationship_map
from toolsets.tools.analysis.extract_features import extract_features_for_build
from toolsets.tools.analysis.perform_column_discovery import perform_column_discovery
from toolsets.tools.analysis.perform_column_mapping import perform_column_mapping

# Constants
DB_SERVICE_URL = "http://127.0.0.1:8002"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

# Global Config (can be overridden by settings DB)
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
logger.add(
    f"Data/logs/ai_agent_{session_ts}.log",
    format=LOG_FORMAT,
    filter=sink_filter,
    rotation="10 MB",
)

def get_safe_log(run_info="N/A", process="DB", build="N/A", run_worker="N/A", build_index="N/A"):
    return logger.bind(run_info=run_info, process=process, build=build, run_worker=run_worker, build_index=build_index)

def ask_ai_wrapper(ai_client: AIClient, role, prompt, build_ver, run_info, process_name, **kwargs):
    """Wrapper to maintain compatibility with existing tool signatures."""
    get_safe_log(build=build_ver, run_info=run_info, process=process_name, **kwargs)
    return ai_client.ask(role, prompt)

def get_version_context(current, previous):
    if not previous: return "NEVER-SAW-IN-PREVIOUS-VERSIONS"
    c_parts, p_parts = current.split("."), previous.split(".")
    if c_parts[0] != p_parts[0]: return f"MAJOR EXPANSION UPDATE (from {previous} to {current})"
    if c_parts[1] != p_parts[1]: return f"MINOR CONTENT PATCH (from {previous} to {current})"
    return f"MINOR BUILD UPDATE / HOTFIX (from {previous} to {current})"

def analyze_column_task(db_client: DBClient, ai_client: AIClient, col_info, build_id, build_version, run_info, version_context="", **kwargs):
    """Coordination of Discovery and Mapping workflows for a single column."""
    f_id, table, col, d_type, v_min, v_max = col_info
    log = get_safe_log(build=build_version, run_info=run_info, process="Analysis", **kwargs)
    
    # Bridge to AIClient
    def ask_ai(r, p, bv, ri, pn, **kw):
        return ask_ai_wrapper(ai_client, r, p, bv, ri, pn, **kw)

    # 1. Perform Column Discovery (Identifying semantics)
    try:
        discovery_res = perform_column_discovery(
            db_client, ask_ai, col_info, build_id, build_version, 
            version_context, run_info=run_info, **kwargs
        )
    except Exception as e:
        log.error(f"Discovery failed for {table}.{col}: {e}")
        return

    # 2. Perform Column Mapping (Finding relationships)
    try:
        mapping_res = perform_column_mapping(
            db_client, ask_ai, discovery_res, col_info, build_version, 
            run_info=run_info, **kwargs
        )
        
        status = mapping_res.get("status")
        if status == "confirmed":
            print(f"[{kwargs.get('run_worker')} - {kwargs.get('build_index')}] [✅] {table}.{col} -> {mapping_res.get('target')}", flush=True)
        elif status == "vetoed":
            print(f"[{kwargs.get('run_worker')} - {kwargs.get('build_index')}] [❌] Vetoed: {table}.{col} -> {mapping_res.get('target')}", flush=True)
        else:
            print(f"[{kwargs.get('run_worker')} - {kwargs.get('build_index')}] [💡] {table}.{col}: {discovery_res.get('discovery')[:60]}...", flush=True)

    except Exception as e:
        log.error(f"Mapping failed for {table}.{col}: {e}")

    time.sleep(AI_COOLDOWN)

def process_build(db_client: DBClient, ai_client: AIClient, build_version, limit=5, prev_version=None):
    """Main loop for processing all columns of a specific build."""
    print(f"\n>>> RESEARCHING BUILD: {build_version} <<<", flush=True)
    version_context = get_version_context(build_version, prev_version)
    
    # Pre-run feature extraction if needed
    extract_features_for_build(db_client, build_version)
    
    res = db_client.execute("SELECT id FROM registry.builds WHERE version = ?", [build_version]).fetchone()
    if not res: return
    build_id = res[0]

    # Fetch columns pending analysis
    cols_res = db_client.execute("SELECT id, table_name, column_name, data_type, min_val, max_val FROM research.column_features WHERE build_id = ? LIMIT ?", [build_id, limit])
    cols = cols_res.fetchall()

    print(f"Starting parallel analysis of {len(cols)} columns using {AI_CONCURRENCY} workers...", flush=True)
    with ThreadPoolExecutor(max_workers=AI_CONCURRENCY) as executor:
        futures = []
        for i, col_info in enumerate(cols, 1):
            worker_id = f"W{(i - 1) % AI_CONCURRENCY + 1}"
            run_info = f"{i}/{len(cols)}"
            futures.append(executor.submit(
                analyze_column_task, db_client, ai_client, col_info, build_id, build_version, 
                run_info, version_context, run_worker=worker_id, build_index=run_info
            ))
        for f in futures:
            try: f.result()
            except Exception as e: logger.error(f"Task failed: {e}")
    
    # Generate final build map diagram
    def ask_ai_simple(p):
        return ai_client.ask("Cartographer", p)
    generate_relationship_map(db_client, ask_ai_simple, build_version)


def main():
    # Wait for DB Service
    print("Waiting for DB Service at " + DB_SERVICE_URL, flush=True)
    max_retries = 30
    for i in range(max_retries):
        try:
            r = requests.post(f"{DB_SERVICE_URL}/query", json={"sql": "SELECT 1"}, timeout=2)
            r.raise_for_status()
            print("DB Service is ready!", flush=True)
            break
        except:
            if i == max_retries - 1:
                print("DB Service unreachable. Exiting.", flush=True); sys.exit(1)
            time.sleep(1)

    db_client = DBClient(url=DB_SERVICE_URL)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    # Get available builds from registry
    res = db_client.execute("SELECT version FROM registry.builds WHERE is_downloaded = TRUE ORDER BY id ASC")
    all_local = [r[0] for r in res.fetchall()]
    if not all_local:
        print("No local builds found in registry.")
        return

    s_idx = all_local.index(args.start) if args.start in all_local else 0
    e_idx = all_local.index(args.end) if args.end in all_local else len(all_local) - 1

    # Load configuration
    global AI_COOLDOWN, AI_THREADS, AI_DEBUG, AI_CONCURRENCY
    try:
        AI_COOLDOWN = float(db_client.execute("SELECT value FROM registry.settings WHERE key = 'cooldown'").fetchone()[0])
        AI_THREADS = int(db_client.execute("SELECT value FROM registry.settings WHERE key = 'threads'").fetchone()[0])
    except:
        AI_COOLDOWN, AI_THREADS = 4.0, 6 # Fallback
    AI_DEBUG = os.getenv("AI_DEBUG", "1") == "1"
    AI_CONCURRENCY = int(os.getenv("AI_CONCURRENCY", "1"))

    ai_client = AIClient(ollama_url=OLLAMA_URL, model=MODEL_NAME, debug=AI_DEBUG, threads=AI_THREADS)

    prev_v = all_local[s_idx - 1] if s_idx > 0 else None
    for build in all_local[s_idx : e_idx + 1]:
        process_build(db_client, ai_client, build, limit=args.limit, prev_version=prev_v)
        prev_v = build

if __name__ == "__main__":
    print(">>> AGENT SCRIPT EXECUTION START <<<", flush=True)
    main()
    print(">>> AGENT SCRIPT EXECUTION END <<<", flush=True)
