# Tools/toolsets/tools/analysis/perform_column_mapping.py
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Callable

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient
from toolsets.tools.database.check_ids import check_ids
from toolsets.tools.database.save_attempt import save_attempt
from toolsets.tools.database.update_global_knowledge import update_global_knowledge

QUERY_DIR = Path(__file__).parent / "queries" / "perform_column_mapping"
PROMPT_DIR = Path(__file__).parent / "prompts" / "perform_column_mapping"

def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", 'r') as f:
        return f.read().strip()

def _load_prompt(name: str) -> str:
    """Loads a prompt template from the tool's local prompt directory."""
    path = PROMPT_DIR / f"{name}.txt"
    if path.exists():
        with open(path, 'r') as f:
            return f.read().strip()
    return ""

def _clean_target(name: str, all_tables: List[str] = None) -> str:
    if not isinstance(name, str): return "NONE"
    target = name.split()[-1].replace("'", "").replace('"', "").strip()
    if all_tables and target != "NONE":
        base = target
        if target.lower().endswith("id"): base = target[:-2]
        if target in all_tables: return target
        if base in all_tables: return base
        if f"{base}s" in all_tables: return f"{base}s"
    return target

def perform_column_mapping(
    db_client: DBClient,
    ask_ai_func: Callable,
    discovery_result: Dict[str, Any],
    col_info: List[Any],
    build_version: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Workflow to map a column to a target table using the Archivist and Sages.
    """
    f_id, table, col, d_type, v_min, v_max = col_info
    ai_full_response = discovery_result.get("ai_full_response", {})
    
    # 1. Check if we should map
    preds_res = db_client.execute(_load_query("get_statistical_predictions"), [f_id])
    preds = preds_res.fetchall()
    
    ai_type = str(ai_full_response.get("type", "")).lower()
    is_value_col = any(col.lower().endswith(s) for s in ["msec", "count", "amount", "charges", "percent", "flag", "flags", "index", "idx"])
    
    should_map = (ai_type == "structure" or col.lower().endswith("id") or preds) and not is_value_col
    
    if not should_map:
        return {"status": "skipped", "reason": "Not a candidate for mapping"}

    # 2. Archivist: Propose Mapping
    all_tables_res = db_client.execute(_load_query("get_available_tables"))
    all_tables = [r[0] for r in all_tables_res.fetchall()]
    
    # Use context from discovery result
    context = discovery_result.get("context", {})
    samples = context.get("samples", [])
    memory_section = context.get("memory_section", "")
    online_info = context.get("online_info", "")

    archivist_template = _load_prompt("mapping_references_between_tables_and_columns")
    p_map = archivist_template.format(
        table=table, col=col, samples=samples, preds=preds,
        memory_section=memory_section, online_info=online_info,
        all_tables=all_tables[:100]
    )
    
    prop = ask_ai_func("WoW Lore Archivist", p_map, build_version, kwargs.get('run_info', 'N/A'), "Mapping")
    target = _clean_target(prop.get("target", "NONE"), all_tables=all_tables)
    
    if target == "NONE":
        return {"status": "skipped", "reason": "No target proposed by Archivist"}

    # 3. ID Check: Empirical Proof
    match_count = check_ids(db_client, target, samples)
    proof = f"ID Check: {match_count} of {len(samples)} samples found in target '{target}'."

    # 4. Sages: Verify
    sages_template = _load_prompt("verification_mapping_integrity_and_id_checks")
    p_crit = sages_template.format(table=table, col=col, target=target, proof=proof)
    
    crit = ask_ai_func("The Sages", p_crit, build_version, kwargs.get('run_info', 'N/A'), "Verification")
    decision = str(crit.get("decision", "")).lower()
    reasoning = crit.get("reasoning", "No reason provided")

    # 5. Save results
    save_attempt(db_client, build_version, table, col, target, decision.upper(), f"{proof} | {reasoning}")
    
    mapping_confirmed = False
    if decision in ("confirm", "yes", "true"):
        update_global_knowledge(
            db_client, col, table, target, 
            prop.get("confidence", 0.5), 
            build_version, 
            ai_notes=f"{proof} | {prop.get('reasoning')}"
        )
        mapping_confirmed = True
        
    return {
        "status": "confirmed" if mapping_confirmed else "vetoed",
        "target": target,
        "proof": proof,
        "reasoning": reasoning,
        "mapping_confirmed": mapping_confirmed
    }
