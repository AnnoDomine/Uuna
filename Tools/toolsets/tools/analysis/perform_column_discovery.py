# Tools/toolsets/tools/analysis/perform_column_discovery.py
import sys
import os
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient
from toolsets.tools.database.save_discovery import save_discovery
from toolsets.tools.database.get_last_attempt import get_last_attempt
from toolsets.tools.research.get_wago_structure import get_wago_structure
from toolsets.tools.research.search_wow_wiki import search_wow_wiki
from toolsets.tools.research.fetch_web_content import fetch_web_content

QUERY_DIR = Path(__file__).parent / "queries" / "perform_column_discovery"
PROMPT_DIR = Path(__file__).parent / "prompts" / "perform_column_discovery"

def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", 'r') as f:
        return f.read().strip()

def _load_prompt(name: str) -> str:
    # First check local tool prompts
    local_path = PROMPT_DIR / f"{name}.txt"
    if local_path.exists():
        with open(local_path, 'r') as f:
            return f.read().strip()
    
    # Fallback to legacy agent prompts if not yet migrated
    legacy_path = Path("Tools/agents/prompts/archivist") / f"{name}.txt"
    if legacy_path.exists():
        with open(legacy_path, 'r') as f:
            return f.read().strip()
    return ""

def _sanitize_identifier(name: str) -> str:
    if not re.match(r"^[a-zA-Z0-9_.]+$", str(name)):
        raise ValueError(f"Invalid identifier: {name}")
    return str(name)

def perform_column_discovery(
    db_client: DBClient, 
    ask_ai_func: Callable,
    col_info: List[Any],
    build_id: int,
    build_version: str,
    version_context: str = "",
    **kwargs
) -> Dict[str, Any]:
    """
    Full workflow to discover the purpose and semantics of a database column.
    """
    f_id, table, col, d_type, v_min, v_max = col_info
    
    # 1. Fetch Samples and Context from DB
    safe_table = _sanitize_identifier(table)
    safe_col = _sanitize_identifier(col)
    
    sample_sql = _load_query("get_column_samples").format(col=safe_col, table=safe_table)
    samples = [r[0] for r in db_client.execute(sample_sql, [build_id, table]).fetchall()]

    prev_discoveries = db_client.execute(_load_query("get_legacy_discoveries"), [table, col, build_id]).fetchall()
    existing = db_client.execute(_load_query("get_global_knowledge"), [col, table]).fetchall()
    last_attempt = get_last_attempt(db_client, table, col)

    # 2. Online Research (conditional)
    online_info = ""
    is_first_time = not last_attempt
    if is_first_time or (last_attempt and last_attempt[1] == "VETO"):
        try:
            wago_headers = get_wago_structure(db_client, table, build_version)
            online_info += f"\n### WAGO.TOOLS STRUCTURE:\n{wago_headers}\n"
            wiki_links = search_wow_wiki(db_client, f"WoW DB2 {table} {col}")
            if wiki_links:
                content = fetch_web_content(db_client, wiki_links[0])
                online_info += f"\n### ONLINE RESEARCH (WoW Wiki):\nURL: {wiki_links[0]}\nCONTENT: {content[:500]}...\n"
        except Exception:
            pass

    # 3. Build AI Context
    memory_section = f"\n### VERSIONING CONTEXT:\n- {version_context}\n"
    if prev_discoveries or existing or last_attempt:
        memory_section += "\n### LEGACY KNOWLEDGE:\n"
        if last_attempt:
            target_p, decision_p, reason_p = last_attempt
            memory_section += f"- LAST RESEARCH RESPONSE: [{decision_p}] Proposed '{target_p}'. Reason: {reason_p}\n"
        if existing:
            memory_section += f"- PREVIOUS MAPPING: table '{existing[0][0]}'. Notes: {existing[0][1]}\n"
        for d in prev_discoveries:
            memory_section += f"- PAST DISCOVERY: {d[0]}\n"
    else:
        memory_section += "\n### LEGACY KNOWLEDGE:\n- STATUS: NEVER-SAW-IN-PREVIOUS-VERSIONS\n"

    # 4. Prepare and Call AI
    is_value_col = any(col.lower().endswith(s) for s in ["msec", "count", "amount", "charges", "percent", "flag", "flags", "index", "idx"])
    template_name = "value_research_metrics_and_enums" if is_value_col else "discovery_column_semantics_and_structure"
    template = _load_prompt(template_name)
    
    # Add Identity Header if not present in legacy template
    identity_header = f"IDENTITY: You are the WoW Lore Archivist, an expert in Azeroth's history and game mechanics. Your role is described in `docs/wiki/roles/Archivist.md`.\n\n"
    full_prompt = identity_header + template.format(
        table=table, col=col, v_min=v_min, v_max=v_max, 
        samples=samples, memory_section=memory_section, online_info=online_info
    )

    ai_result = ask_ai_func("WoW Lore Archivist", full_prompt, build_version, kwargs.get('run_info', 'N/A'), "Discovery")
    
    # 5. Save and Return
    discovery_text = ai_result.get("discovery") or "Analysis pending"
    confidence = ai_result.get("confidence", 0.5)
    
    save_discovery(db_client, build_id, table, col, discovery_text, confidence)
    
    return {
        "table": table,
        "column": col,
        "discovery": discovery_text,
        "confidence": confidence,
        "ai_full_response": ai_result,
        "context": {
            "samples": samples,
            "memory_section": memory_section,
            "online_info": online_info
        }
    }
