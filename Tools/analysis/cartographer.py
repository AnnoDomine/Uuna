import requests
import os
from loguru import logger
import json
import re
import sys

# Config
DB_SERVICE_URL = "http://127.0.0.1:8001"

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
def load_query(role, task):
    path = f"Tools/queries/{role}/{task}.sql"
    if path in QUERY_CACHE: return QUERY_CACHE[path]
    try:
        with open(path, "r") as f:
            content = f.read()
            QUERY_CACHE[path] = content
            return content
    except: return ""

def db_query(sql, params=[], run_info="N/A", run_worker="N/A", build_index="N/A"):
    """Unified API-based query function."""
    try:
        r = requests.post(f"{DB_SERVICE_URL}/query", json={"sql": sql, "params": params}, timeout=60)
        r.raise_for_status()
        return r.json()["results"]
    except Exception as e:
        logger.error(f"Cartographer DB Query failed: {e}")
        return []

def db_execute(sql, params=[], run_info="N/A", run_worker="N/A", build_index="N/A"):
    """Unified API-based execution function."""
    try:
        r = requests.post(f"{DB_SERVICE_URL}/execute", json={"sql": sql, "params": params}, timeout=60)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Cartographer DB Execute failed: {e}")
        return False

def get_safe_log(run_info="N/A", process="Research", build="N/A", run_worker="N/A", build_index="N/A"):
    """Returns a logger bound with required fields to avoid KeyErrors."""
    return logger.bind(run_info=run_info, process=process, build=build, run_worker=run_worker, build_index=build_index)

def get_mermaid_documentation(run_info="N/A", build="N/A", run_worker="N/A", build_index="N/A"):
    """
    Fetches Mermaid documentation and caches it for 7 days.
    """
    log = get_safe_log(run_info=run_info, process="Cartographer", build=build, run_worker=run_worker, build_index=build_index)
    cache_key = "mermaid_docs"
    try:
        sql = load_query("cartographer", "get_mermaid_docs_cache")
        # In DuckDB, multiply interval for dynamic parameters
        res = db_query(sql, (cache_key, 7), run_info=run_info, run_worker=run_worker, build_index=build_index)
        
        if res:
            return res[0][0]
            
        log.info("Fetching fresh Mermaid documentation...")
        docs = """
        Mermaid Syntax Guide for WoW Datamine:
        - ER Diagram: erDiagram
        - Entity Example: TableName { string column_name }
        - Relationship: SourceTable ||--o{ TargetTable : "foreign_key"
        - Legend: Use meaningful labels for connections.
        """
        
        db_execute(load_query("researcher", "save_cache_entry"), (cache_key, docs, "doc"), run_info=run_info, run_worker=run_worker, build_index=build_index)
        return docs
    except Exception as e:
        log.error(f"Error getting Mermaid docs: {e}")
        return "erDiagram Table { type col }"

def create_mermaid(name, content, build_version="N/A", run_info="N/A", run_worker="N/A", build_index="N/A"):
    """Saves a mermaid diagram string to a file in Data/maps/."""
    log = get_safe_log(run_info=run_info, process="Cartographer", build=build_version, run_worker=run_worker, build_index=build_index)
    os.makedirs("Data/maps", exist_ok=True)
    safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '.', '_')]).rstrip()
    file_path = f"Data/maps/{safe_name}_{build_version}.mmd"
    try:
        with open(file_path, "w") as f: f.write(content)
        log.info(f"Mermaid diagram created: {file_path}")
        return f"SUCCESS: Diagram saved to {file_path}"
    except Exception as e:
        log.error(f"Failed to save mermaid diagram: {e}")
        return f"ERROR: {e}"

def update_build_map(build_version, toolkit, ask_ai_func, run_info="N/A", run_worker="N/A", build_index="N/A"):
    """Fetches all confirmed mappings for a build and creates a single comprehensive map."""
    log = get_safe_log(run_info=run_info, process="Cartographer", build=build_version, run_worker=run_worker, build_index=build_index)
    log.info(f"Updating comprehensive build map for {build_version}")
    
    mappings = db_query(load_query("cartographer", "get_confirmed_mappings"), (build_version,), run_info=run_info, run_worker=run_worker, build_index=build_index)
    if not mappings:
        log.warning(f"No confirmed mappings found for build {build_version}")
        return
        
    mapping_str = "\n".join([f"- {m[0]}.{m[1]} -> {m[2]}" for m in mappings])
    mmd_docs = get_mermaid_documentation(run_info=run_info, build=build_version, run_worker=run_worker, build_index=build_index)
    
    template = load_prompt("cartographer", "visualization_build_relation_map")
    p_carto = template.format(build_version=build_version, mapping_str=mapping_str, mmd_docs=mmd_docs)

    viz = ask_ai_func("WoW Cartographer", p_carto, build_version, run_info, "Cartography", run_worker=run_worker, build_index=build_index)
    if viz.get("mermaid"):
        create_mermaid("Build_Map", viz["mermaid"], build_version=build_version, run_info=run_info, run_worker=run_worker, build_index=build_index)
        log.info(f"Build map updated with {len(mappings)} relationships.")
    else:
        log.error("AI failed to generate build map mermaid code.")
