import sqlite3
import os
import json
import difflib
import re
import sys

GLOBAL_MAP_PATH = 'Data/dbs/Global_Column_Map.json'
SETTINGS_DB = 'Data/dbs/Settings.db'

# Session state to skip all remaining questions
session_skip_all = False

def get_setting(key, default):
    try:
        conn = sqlite3.connect(SETTINGS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    except:
        return default

def get_latest_local_db():
    db_reg = 'Data/dbs/Build_Registry.db'
    if not os.path.exists(db_reg):
        return None
    conn = sqlite3.connect(db_reg)
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM builds ORDER BY id DESC")
    versions = [row[0] for row in cursor.fetchall()]
    conn.close()
    for v in versions:
        path = f'Data/dbs/WoW_Data_{v}.db'
        if os.path.exists(path): return path
    return None

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def resolve_table_name(potential_name, tables, user_mappings, global_mappings, mapping_path, current_table, current_col, use_global=True):
    global session_skip_all
    mapping_key = f"{current_table}.{current_col}"
    
    # 0. Check session skip
    if session_skip_all:
        return None

    # 1. Check build-specific local user mapping first
    if mapping_key in user_mappings:
        val = user_mappings[mapping_key]
        return val if val != "NONE" else None

    # 2. Check Global Mapping if enabled
    if use_global and current_col in global_mappings:
        target = global_mappings[current_col]
        if target in tables: return target
        if target == "NONE": return None

    # Hardcoded known aliases
    aliases = {
        "Quest": "QuestV2",
        "Spell": "SpellName",
        "Item": "ItemSparse",
        "BroadcastText": "BroadcastText",
        "ConversationLine": "ConversationLine"
    }
    
    # 3. Direct Match (Case Insensitive)
    p_low = potential_name.lower()
    for t in tables:
        if t.lower() == p_low: return t
            
    # 4. Check Aliases
    if potential_name in aliases:
        target = aliases[potential_name]
        if target in tables: return target

    # 5. Auto-Suffixes
    for suffix in ['V2', 'V3', 'V4', 'Sparse', 'Name']:
        variant = potential_name + suffix
        if variant in tables: return variant
        for t in tables:
            if t.lower() == variant.lower(): return t

    # 6. Interactive Input or Auto-Skip
    auto_skip_setting = get_setting('map_references_auto_skip_unidentifiable', '0') == '1'
    if auto_skip_setting:
        print(f"[!] Auto-skipping ambiguous reference: {current_table}.{current_col}")
        session_skip_all = True
        return None

    print(f"\n[?] Ambiguous: {current_table}.{current_col} (Base: '{potential_name}')")
    
    suggestions = difflib.get_close_matches(potential_name, tables, n=15, cutoff=0.2)
    for t in tables:
        if p_low in t.lower() and t not in suggestions:
            suggestions.append(t)
    suggestions.sort()
    
    print("    Possible targets:")
    print("    0) [ SKIP / NONE ]")
    print("    0a) [ SKIP ALL REMAINING ]")
    for i, s in enumerate(suggestions, 1):
        print(f"    {i}) {s}")
    print("    m) [ MANUAL INPUT ]")
    
    try:
        choice = input(f"    Select (0-{len(suggestions)}, 0a, m): ").strip().lower()
        target_result = None
        
        if choice == '0':
            target_result = "NONE"
        elif choice == '0a':
            session_skip_all = True
            return None
        elif choice == 'm':
            manual = input("    Enter table name: ").strip()
            if manual in tables: target_result = manual
        elif choice.isdigit() and 1 <= int(choice) <= len(suggestions):
            target_result = suggestions[int(choice)-1]

        if target_result:
            # Save locally
            user_mappings[mapping_key] = target_result
            save_json(mapping_path, user_mappings)
            
            # Save globally if not disabled
            if use_global:
                global_mappings[current_col] = target_result
                save_json(GLOBAL_MAP_PATH, global_mappings)
            
            return target_result if target_result != "NONE" else None
            
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
                
    return None

def get_previous_build(current_version):
    """Finds the build number immediately preceding the current one in the registry."""
    db_reg = 'Data/dbs/Build_Registry.db'
    if not os.path.exists(db_reg):
        return None
    
    try:
        current_id = int(current_version.split('.')[-1])
        conn = sqlite3.connect(db_reg)
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM builds WHERE id < ? ORDER BY id DESC LIMIT 1", (current_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None

def map_references(db_path, use_global=True):
    build_version = os.path.basename(db_path).replace('WoW_Data_', '').replace('.db', '')
    print(f"=== REFERENCE MAPPING - {build_version} (Global: {use_global}) ===")
    
    mapping_path = db_path.replace('.db', '_user_map.json')
    user_mappings = load_json(mapping_path)
    
    # NEW: Import from previous build
    if not user_mappings:
        prev_version = get_previous_build(build_version)
        if prev_version:
            prev_map_path = f'Data/dbs/WoW_Data_{prev_version}_user_map.json'
            if os.path.exists(prev_map_path):
                choice = input(f"[!] Found mappings from previous build {prev_version}. Import them? (y/n): ").lower()
                if choice == 'y':
                    user_mappings = load_json(prev_map_path)
                    save_json(mapping_path, user_mappings)
                    print(f"    Imported {len(user_mappings)} mappings from {prev_version}.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    global_mappings = load_json(GLOBAL_MAP_PATH)
    references = {}
    
    for table in tables:
        if table in ('builds', 'sqlite_sequence'): continue
        cursor.execute(f"PRAGMA table_info(\"{table}\")")
        columns = [col[1] for col in cursor.fetchall()]
        
        for col in columns:
            if ';' in col or col in ('ID', 'build_id'): continue
            
            potential_target_base = None
            if col.endswith('ID'): potential_target_base = col[:-2]
            elif col.endswith('_ID'): potential_target_base = col[:-3]
            elif col in tables or any(t.lower() == col.lower() for t in tables):
                potential_target_base = col
            
            if potential_target_base:
                clean_target = potential_target_base
                if not any(t.lower() == clean_target.lower() for t in tables):
                    for i in range(1, len(potential_target_base)):
                        if potential_target_base[i].isupper():
                            sub = potential_target_base[i:]
                            if any(t.lower() == sub.lower() or t.lower().startswith(sub.lower()) for t in tables):
                                clean_target = sub
                                break

                match = resolve_table_name(clean_target, tables, user_mappings, global_mappings, mapping_path, table, col, use_global)
                if match:
                    if table not in references: references[table] = []
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM \"{table}\" WHERE \"{col}\" NOT IN (0, -1) AND \"{col}\" IS NOT NULL")
                        val_count = cursor.fetchone()[0]
                        references[table].append({"column": col, "target_table": match, "active_entries": val_count})
                        print(f"  LINK: {table}.{col} -> {match} ({val_count})")
                    except: pass

    ref_path = db_path.replace('.db', '_refs.json')
    save_json(ref_path, references)
    conn.close()
    print(f"\nReference map saved: {ref_path}")

if __name__ == "__main__":
    args = sys.argv[1:]
    
    # Check settings for global mapping default
    settings_use_global = get_setting('map_references_use_global_mapping', '0') == '1'
    
    use_global = settings_use_global
    if "--ng" in args: 
        use_global = False
        args.remove("--ng")
    elif "--g" in args:
        use_global = True
        args.remove("--g")
    
    build = args[0] if args else None
    db = f"Data/dbs/WoW_Data_{build}.db" if build else get_latest_local_db()
    
    if db and os.path.exists(db):
        map_references(db, use_global)
    else:
        print("No DB found.")
