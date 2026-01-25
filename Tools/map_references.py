import sqlite3
import os
import glob
import json

def get_latest_db():
    dbs = glob.glob('Data/dbs/WoW_Data_*.db')
    if not dbs:
        if os.path.exists('Data/dbs/WoW_Data.db'):
            return 'Data/dbs/WoW_Data.db'
        return None
    return max(dbs, key=os.path.getmtime)

def map_references(db_path):
    print(f"Analyzing references in: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    references = {}
    
import sqlite3
import os
import glob
import json
import difflib

def get_user_mapping_path(db_path):
    return db_path.replace('.db', '_user_map.json')

def load_user_mappings(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_mappings(path, mappings):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2)

def resolve_table_name(potential_name, tables, user_mappings, mapping_path, current_table, current_col):
    """
    Maps potential names to actual table names.
    Uses: 1. Build-specific User Mappings, 2. Hardcoded Aliases, 3. Auto-Suffixes, 4. Interactive Input
    """
    mapping_key = f"{current_table}.{current_col}"
    
    # 1. Check build-specific user mappings
    if mapping_key in user_mappings:
        val = user_mappings[mapping_key]
        return val if val != "NONE" else None

    # Explicit mapping for known changes
    aliases = {
        "Quest": "QuestV2",
        "QuestLine": "QuestLine",
        "BroadcastText": "BroadcastText",
        "ConversationLine": "ConversationLine",
        "Spell": "SpellName"
    }
    
    # 2. Check direct alias
    if potential_name in aliases:
        target = aliases[potential_name]
        if target in tables:
            return target

    # 3. Case-insensitive search
    p_low = potential_name.lower()
    for t in tables:
        if t.lower() == p_low:
            return t
            
    # 4. Handle V2, V3 suffixes automatically
    for suffix in ['V2', 'V3', 'V4', 'Sparse']:
        variant = potential_name + suffix
        for t in tables:
            if t.lower() == variant.lower():
                return t
    
    # 5. Interactive Input if not found
    print(f"\n[?] Ambiguous reference found: {current_table}.{current_col}")
    print(f"    Suggested base name: '{potential_name}'")
    
    # Get all fuzzy matches from tables without a fixed limit
    suggestions = difflib.get_close_matches(potential_name, tables, n=len(tables), cutoff=0.2)
    
    # Also include tables that contain the potential_name as a substring but might have been missed
    p_low = potential_name.lower()
    for t in tables:
        if p_low in t.lower() and t not in suggestions:
            suggestions.append(t)
            
    # Sort alphabetically for better overview if many results
    suggestions.sort()
    
    print("    Possible target tables:")
    print("    0) [ SKIP / NONE ]")
    for i, s in enumerate(suggestions, 1):
        print(f"    {i}) {s}")
    print("    m) [ MANUAL INPUT ]")
    
    try:
        choice = input(f"    Select option (0-{len(suggestions)}, m): ").strip().lower()
        
        if choice == '0':
            # Do NOT save to user_mappings, just return None for this run
            return None
        elif choice == 'm':
            manual = input("    Enter table name exactly: ").strip()
            if manual in tables:
                user_mappings[mapping_key] = manual
                save_user_mappings(mapping_path, user_mappings)
                return manual
            else:
                print(f"    Table '{manual}' not found. Skipping.")
                return None
        elif choice.isdigit() and 1 <= int(choice) <= len(suggestions):
            selected = suggestions[int(choice)-1]
            user_mappings[mapping_key] = selected
            save_user_mappings(mapping_path, user_mappings)
            return selected
    except EOFError:
        pass
                
    return None

def map_references(db_path):
    # Extract build version from filename for display
    build_version = os.path.basename(db_path).replace('WoW_Data_', '').replace('.db', '')
    
    print("=" * 60)
    print(f" REFERENCE MAPPING - BUILD: {build_version}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    user_mapping_path = get_user_mapping_path(db_path)
    user_mappings = load_user_mappings(user_mapping_path)
    references = {}
    
    for table in tables:
        if table in ('builds', 'sqlite_sequence'):
            continue
            
        cursor.execute(f"PRAGMA table_info(\"{table}\")")
        columns = [col[1] for col in cursor.fetchall()]
        
        for col in columns:
            # Skip corrupted columns (import errors with semicolon)
            if ';' in col:
                print(f"\n[!] WARNING: Table '{table}' has corrupted column names ('{col[:50]}...')")
                print(f"    Please re-sync this build or check the CSV delimiter.")
                continue

            if col == 'ID' or col == 'build_id':
                continue
            
            # Identify potential reference columns
            potential_target_base = None
            if col.endswith('ID'):
                potential_target_base = col[:-2]
            elif col.endswith('_ID'):
                potential_target_base = col[:-3]
            
            if potential_target_base:
                # Clean prefix logic (targetQuest -> Quest)
                clean_target = potential_target_base
                for i in range(1, len(potential_target_base)):
                    if potential_target_base[i].isupper():
                        sub = potential_target_base[i:]
                        if any(t.lower() == sub.lower() or t.lower().startswith(sub.lower()) for t in tables):
                            clean_target = sub
                            break

                match = resolve_table_name(clean_target, tables, user_mappings, user_mapping_path, table, col)
                
                if match:
                    if table not in references:
                        references[table] = []
                    
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM \"{table}\" WHERE \"{col}\" NOT IN (0, -1) AND \"{col}\" IS NOT NULL")
                        val_count = cursor.fetchone()[0]
                        
                        references[table].append({
                            "column": col,
                            "target_table": match,
                            "active_entries": val_count
                        })
                        print(f"LINK: {table}.{col} -> {match} ({val_count} active refs)")
                    except Exception as e:
                        pass

    # Saving the reference map
    ref_path = db_path.replace('.db', '_refs.json')
    with open(ref_path, 'w', encoding='utf-8') as f:
        json.dump(references, f, indent=2)
    
    conn.close()
    print(f"\nReference map saved at: {ref_path}")

    # Saving the reference map
    ref_path = db_path.replace('.db', '_refs.json')
    with open(ref_path, 'w', encoding='utf-8') as f:
        json.dump(references, f, indent=2)
    
    conn.close()
    print(f"\nReference map saved at: {ref_path}")

if __name__ == "__main__":
    db = get_latest_db()
    if db:
        map_references(db)
    else:
        print("No database found for analysis.")
