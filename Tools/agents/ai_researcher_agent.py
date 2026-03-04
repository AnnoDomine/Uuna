# AI RESEARCHER AGENT - REFACTORED
#
import sys
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Ensure path resolution
sys.path.append(os.getcwd())

# Project modules
from Tools.core.db_client import DBClient
from Tools.core.ai_client import AIClient
from Tools.core.shared_debugger import debugger
from Tools.toolsets.tools.analysis.generate_relationship_map import generate_relationship_map
from Tools.toolsets.tools.analysis.extract_features import extract_features_for_build
from Tools.toolsets.tools.analysis.perform_column_discovery import perform_column_discovery
from Tools.toolsets.tools.analysis.perform_column_mapping import perform_column_mapping

# Constants
DB_SERVICE_URL = "http://127.0.0.1:8002"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

# Global Config (can be overridden by settings DB)
AI_COOLDOWN = 4.0
AI_THREADS = 6
AI_DEBUG = True
AI_CONCURRENCY = 1


def ask_ai_wrapper(ai_client: AIClient, role, prompt, build_ver, run_info, process_name, **kwargs):
    """Wrapper to maintain compatibility with existing tool signatures."""
    debugger.add_log(f"AI Request for {role}", agent="AI_CLIENT", process=process_name, build=build_ver, run_info=run_info, **kwargs)
    return ai_client.ask(role, prompt)


def get_version_context(current, previous):
    if not previous:
        return "NEVER-SAW-IN-PREVIOUS-VERSIONS"
    c_parts, p_parts = current.split("."), previous.split(".")
    if c_parts[0] != p_parts[0]:
        return f"MAJOR EXPANSION UPDATE (from {previous} to {current})"
    if c_parts[1] != p_parts[1]:
        return f"MINOR CONTENT PATCH (from {previous} to {current})"
    return f"MINOR BUILD UPDATE / HOTFIX (from {previous} to {current})"


def analyze_column_task(
    db_client: DBClient, ai_client: AIClient, col_info, build_id, build_version, run_info, version_context="", **kwargs
):
    """Coordination of Discovery and Mapping workflows for a single column."""
    f_id, table, col, d_type, v_min, v_max = col_info
    
    debugger.add_log(f"Analyzing column: {table}.{col}", agent="RESEARCHER", process="ColAnalysis", build=build_version, run_info=run_info, **kwargs)

    # Bridge to AIClient
    def ask_ai(r, p, bv, ri, pn, **kw):
        return ask_ai_wrapper(ai_client, r, p, bv, ri, pn, **kw)

    # 1. Perform Column Discovery (Identifying semantics)
    try:
        discovery_res = perform_column_discovery(
            db_client, ask_ai, col_info, build_id, build_version, version_context, run_info=run_info, **kwargs
        )
    except Exception as e:
        debugger.add_log(f"Discovery failed for {table}.{col}: {e}", agent="RESEARCHER", level="ERROR", process="ColAnalysis", build=build_version, run_info=run_info, **kwargs)
        return

    # 2. Perform Column Mapping (Finding relationships)
    try:
        mapping_res = perform_column_mapping(
            db_client, ask_ai, discovery_res, col_info, build_version, run_info=run_info, **kwargs
        )

        status = mapping_res.get("status")
        if status == "confirmed":
            debugger.add_log(f"Confirmed mapping: {table}.{col} -> {mapping_res.get('target')}", agent="RESEARCHER", level="SUCCESS", process="ColAnalysis", build=build_version, run_info=run_info, **kwargs)
        elif status == "vetoed":
            debugger.add_log(f"Vetoed mapping: {table}.{col} -> {mapping_res.get('target')}", agent="RESEARCHER", level="WARNING", process="ColAnalysis", build=build_version, run_info=run_info, **kwargs)
        else:
            debugger.add_log(f"Discovery only: {table}.{col}", agent="RESEARCHER", process="ColAnalysis", build=build_version, run_info=run_info, **kwargs)

    except Exception as e:
        debugger.add_log(f"Mapping failed for {table}.{col}: {e}", agent="RESEARCHER", level="ERROR", process="ColAnalysis", build=build_version, run_info=run_info, **kwargs)

    time.sleep(AI_COOLDOWN)


def process_build(db_client: DBClient, ai_client: AIClient, build_version, limit=5, prev_version=None):
    """Main loop for processing all columns of a specific build."""
    debugger.add_log(f">>> RESEARCHING BUILD: {build_version} <<<", agent="RESEARCHER", process="BuildProcessing", build=build_version)
    version_context = get_version_context(build_version, prev_version)

    # Pre-run feature extraction if needed
    extract_features_for_build(db_client, build_version)

    res = db_client.execute("SELECT id FROM registry.builds WHERE version = ?", [build_version]).fetchone()
    if not res:
        debugger.add_log(f"Build {build_version} not found in registry!", agent="RESEARCHER", level="ERROR", process="BuildProcessing", build=build_version)
        return
    build_id = res[0]

    # Fetch columns pending analysis
    cols_res = db_client.execute(
        "SELECT id, table_name, column_name, data_type, min_val, max_val FROM research.column_features WHERE build_id = ? LIMIT ?",
        [build_id, limit],
    )
    cols = cols_res.fetchall()

    debugger.add_log(f"Starting parallel analysis of {len(cols)} columns...", agent="RESEARCHER", process="BuildProcessing", build=build_version)
    with ThreadPoolExecutor(max_workers=AI_CONCURRENCY) as executor:
        futures = []
        for i, col_info in enumerate(cols, 1):
            worker_id = f"W{(i - 1) % AI_CONCURRENCY + 1}"
            run_info = f"{i}/{len(cols)}"
            futures.append(
                executor.submit(
                    analyze_column_task,
                    db_client,
                    ai_client,
                    col_info,
                    build_id,
                    build_version,
                    run_info,
                    version_context,
                    run_worker=worker_id,
                    build_index=run_info,
                )
            )
        for f in futures:
            try:
                f.result()
            except Exception as e:
                debugger.add_log(f"Task failed: {e}", agent="RESEARCHER", level="ERROR", process="BuildProcessing", build=build_version)

    # Generate final build map diagram
    def ask_ai_simple(p):
        return ai_client.ask("Cartographer", p)

    debugger.add_log(f"Generating relationship map for {build_version}...", agent="RESEARCHER", process="BuildProcessing", build=build_version)
    generate_relationship_map(db_client, ask_ai_simple, build_version)


def main():
    # Wait for DB Service
    max_retries = 30
    for i in range(max_retries):
        try:
            r = requests.post(f"{DB_SERVICE_URL}/query", json={"sql": "SELECT 1"}, timeout=2)
            r.raise_for_status()
            debugger.add_log("DB Service is ready!", agent="RESEARCHER", level="SUCCESS", process="Init")
            break
        except Exception:
            if i == max_retries - 1:
                debugger.add_log("DB Service unreachable. Exiting.", agent="RESEARCHER", level="ERROR", process="Init")
                sys.exit(1)
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
        debugger.add_log("No local builds found in registry.", agent="RESEARCHER", level="ERROR", process="Init")
        return

    s_idx = all_local.index(args.start) if args.start in all_local else 0
    e_idx = all_local.index(args.end) if args.end in all_local else len(all_local) - 1

    # Load configuration
    global AI_COOLDOWN, AI_THREADS, AI_DEBUG, AI_CONCURRENCY
    try:
        AI_COOLDOWN = float(
            db_client.execute("SELECT value FROM registry.settings WHERE key = 'cooldown'").fetchone()[0]
        )
        AI_THREADS = int(db_client.execute("SELECT value FROM registry.settings WHERE key = 'threads'").fetchone()[0])
    except Exception:
        AI_COOLDOWN, AI_THREADS = 4.0, 6  # Fallback
    AI_DEBUG = os.getenv("AI_DEBUG", "1") == "1"
    AI_CONCURRENCY = int(os.getenv("AI_CONCURRENCY", "1"))

    ai_client = AIClient(ollama_url=OLLAMA_URL, model=MODEL_NAME, debug=AI_DEBUG, threads=AI_THREADS)

    prev_v = all_local[s_idx - 1] if s_idx > 0 else None
    for build in all_local[s_idx : e_idx + 1]:
        process_build(db_client, ai_client, build, limit=args.limit, prev_version=prev_v)
        prev_v = build


if __name__ == "__main__":
    debugger.add_log(">>> AGENT SCRIPT EXECUTION START <<<", agent="RESEARCHER", process="Lifecycle")
    main()
    debugger.add_log(">>> AGENT SCRIPT EXECUTION END <<<", agent="RESEARCHER", process="Lifecycle")
