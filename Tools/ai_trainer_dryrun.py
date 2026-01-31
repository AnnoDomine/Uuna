import sqlite3
import os
import requests
import random
import sys
import json

KNOWLEDGE_DB = 'Data/dbs/WoW_Research_Knowledge.db'
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:8b"

def ask_llm(prompt):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are a World of Warcraft Datamining Expert. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        result = response.json()
        content = result['message']['content']
        return json.loads(content)
    except Exception as e:
        return {"error": f"{str(e)}"}

def run_dry_run(build_version, num_samples=10):
    conn = sqlite3.connect(KNOWLEDGE_DB)
    cur = conn.cursor()
    
    # Get build ID
    cur.execute("SELECT id FROM builds WHERE version = ?", (build_version,))
    row = cur.fetchone()
    if not row:
        print(f"Error: Build {build_version} not found in research DB.")
        return
    build_id = row[0]

    # Get all features for this build
    cur.execute("SELECT id, table_name, column_name, data_type, distinct_ratio, min_val, max_val, null_ratio FROM column_features WHERE build_id = ?", (build_id,))
    all_features = cur.fetchall()

    print(f"\n=== AI DRY-RUN EVALUATION (Build: {build_version} | Model: {MODEL_NAME}) ===")
    print(f"Testing {num_samples} random columns from database...\n")

    sampled_features = random.sample(all_features, min(len(all_features), num_samples))
    correct_guesses = 0
    total_sampled = 0

    for f_id, table, col, d_type, d_ratio, v_min, v_max, n_ratio in sampled_features:
        if col in ('ID', 'build_id'): continue
        
        # Get statistical predictions for this feature
        cur.execute("SELECT target_table, confidence FROM statistical_predictions WHERE feature_id = ?", (f_id,))
        predictions = [{"table": p[0], "confidence": p[1]} for p in cur.fetchall()]
        
        prompt = f"""
        Analyze this WoW database column and guess its semantic purpose.
        
        CONTEXT:
        Table: {table}
        Column Name (Hidden from you): [REDACTED]
        Type: {d_type}
        Range: {v_min} to {v_max}
        Distinct Ratio: {d_ratio:.4f}
        Null Ratio: {n_ratio:.4f}
        
        STATISTICAL MATCHES (ID overlaps with these tables):
        {predictions[:5]}
        
        TASK:
        Guess the most likely name for this column (e.g., SpellID, QuestID, MapID, Flags, etc.).
        
        Return JSON:
        {{
            "guess": "Name",
            "reasoning": "Why?"
        }}
        """

        result = ask_llm(prompt)
        if "error" in result:
            print(f"  [!] Error: {result['error']}")
            continue

        guess = result.get("guess", "UNKNOWN")
        reasoning = result.get("reasoning", "")
        
        is_correct = guess.lower() in col.lower() or col.lower() in guess.lower()
        if is_correct: correct_guesses += 1
        total_sampled += 1

        print(f"[{total_sampled}] Table: {table}")
        print(f"    - Stats: {d_type} | Range: {v_min}-{v_max}")
        print(f"    - AI Guess:  {guess}")
        print(f"    - Actual:    {col}")
        print(f"    - Reasoning: {reasoning}")
        print(f"    - Result:    {'✅ MATCH' if is_correct else '❌ MISMATCH'}")
        print("-" * 50)

    conn.close()
    accuracy = (correct_guesses / total_sampled) * 100 if total_sampled > 0 else 0
    print(f"\nDRY-RUN COMPLETE.")
    print(f"Accuracy: {accuracy:.2f}% ({correct_guesses}/{total_sampled})")

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "7.3.5.25600"
    run_dry_run(ver)