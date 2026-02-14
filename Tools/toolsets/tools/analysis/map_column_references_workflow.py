# Tools/toolsets/tools/analysis/map_column_references_workflow.py
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from Tools.core.db_client import DBClient
from .guess_table_reference import guess_table_reference

# --- Constants ---
GLOBAL_MAP_PATH = "Data/dbs/Global_Column_Map.json"
CONFIDENCE_THRESHOLD = 0.85


# --- File I/O Helpers ---
def _load_json(path: str) -> Dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_json(path: str, data: Dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# --- Query Loading Helper ---
QUERY_DIR = Path(__file__).parent / "queries" / "map_column_references_workflow"


def _load_query(name: str) -> str:
    path = QUERY_DIR / f"{name}.sql"
    with open(path, "r") as f:
        return f.read().strip()


def _resolve_table_name_headless(
    potential_name: str,
    all_tables: List[str],
    user_mappings: Dict,
    global_mappings: Dict,
    current_table: str,
    current_col: str,
    pending_questions: List[Dict],
) -> str:
    """
    Resolves a table name using heuristics and returns a confirmed match or None.
    If confidence is low, it adds a question to the pending_questions list.
    """
    mapping_key = f"{current_table}.{current_col}"

    # 1. Check existing mappings first
    if mapping_key in user_mappings:
        return user_mappings[mapping_key] if user_mappings[mapping_key] != "NONE" else None
    if current_col in global_mappings:
        target = global_mappings[current_col]
        if target in all_tables:
            return target
        if target == "NONE":
            return None

    # 2. Get suggestions from the pure logic tool
    suggestions = guess_table_reference(potential_name, all_tables)

    if not suggestions:
        return None

    # 3. Auto-accept high confidence suggestions
    top_suggestion = suggestions[0]
    if top_suggestion["confidence"] >= CONFIDENCE_THRESHOLD:
        print(f"  [AUTO] {mapping_key} -> {top_suggestion['table']} (Confidence: {top_suggestion['confidence']})")
        # Update mappings in memory
        user_mappings[mapping_key] = top_suggestion["table"]
        global_mappings[current_col] = top_suggestion["table"]
        return top_suggestion["table"]

    # 4. Add to pending questions if confidence is too low
    else:
        pending_question = {
            "mapping_key": mapping_key,
            "potential_name": potential_name,
            "suggestions": suggestions[:5],  # Return top 5 suggestions
        }
        if pending_question not in pending_questions:
            pending_questions.append(pending_question)
        return None


def map_column_references_workflow(
    db_client: DBClient, build_version: str, auto_import_previous: bool = True
) -> Dict[str, Any]:
    print(f"=== REFERENCE MAPPING WORKFLOW - {build_version} ===")

    # --- Setup and Data Loading ---
    mapping_path = f"Data/dbs/WoW_Data_{build_version}_user_map.json"
    user_mappings = _load_json(mapping_path)
    global_mappings = _load_json(GLOBAL_MAP_PATH)

    # --- Automatic import from previous build ---
    if auto_import_previous and not user_mappings:
        try:
            prev_build_sql = _load_query("get_previous_build")
            prev_res = db_client.execute(prev_build_sql, [build_version]).fetchone()
            if prev_res:
                prev_version = prev_res[0]
                prev_map_path = f"Data/dbs/WoW_Data_{prev_version}_user_map.json"
                if os.path.exists(prev_map_path):
                    print(f"INFO: Importing mappings from previous build {prev_version}.")
                    user_mappings = _load_json(prev_map_path)
        except Exception as e:
            print(f"WARNING: Could not import previous build mappings: {e}")

    # --- Main Logic ---
    all_tables_res = db_client.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'archive'"
    ).fetchall()
    all_tables = [row[0] for row in all_tables_res]

    newly_confirmed_references = {}
    pending_questions = []

    get_cols_template = _load_query("get_table_columns")
    count_template = _load_query("count_active_entries")

    for table in all_tables:
        if table in ("builds", "sqlite_sequence"):
            continue

        get_cols_sql = get_cols_template.format(table_name=table)
        columns_res = db_client.execute(get_cols_sql).fetchall()
        columns = [col[0] for col in columns_res]

        for col in columns:
            if ";" in col or col.lower() in ("id", "build_id", "_row_hash"):
                continue

            potential_target_base = None
            if col.endswith("ID"):
                potential_target_base = col[:-2]
            elif col.endswith("_ID"):
                potential_target_base = col[:-3]

            if potential_target_base:
                match = _resolve_table_name_headless(
                    potential_target_base, all_tables, user_mappings, global_mappings, table, col, pending_questions
                )
                if match:
                    if table not in newly_confirmed_references:
                        newly_confirmed_references[table] = []

                    count_sql = count_template.format(table_name=table, column_name=col)
                    count_res = db_client.execute(count_sql).fetchone()
                    val_count = count_res[0] if count_res else 0

                    newly_confirmed_references[table].append(
                        {"column": col, "target_table": match, "active_entries": val_count}
                    )
                    print(f"  LINK: {table}.{col} -> {match} ({val_count})")

    # --- Save results ---
    _save_json(mapping_path, user_mappings)
    _save_json(GLOBAL_MAP_PATH, global_mappings)

    ref_path = f"Data/dbs/WoW_Data_{build_version}_refs.json"
    _save_json(ref_path, newly_confirmed_references)
    print(f"\nReference map saved: {ref_path}")

    # --- Return summary ---
    return {
        "status": "complete_with_pending" if pending_questions else "complete",
        "newly_confirmed_mappings": sum(len(v) for v in newly_confirmed_references.values()),
        "total_user_mappings": len(user_mappings),
        "pending_questions": pending_questions,
    }
