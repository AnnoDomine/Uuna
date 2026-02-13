# Tools/run_demon_hunter_research.py
import sys
import os
import duckdb

# Ensure path resolution
sys.path.append(os.getcwd())

from core.ai_client import AIClient
from toolsets.tools.registry.check_build_status import check_build_status
from toolsets.tools.system.create_research_task import create_research_task
from toolsets.tools.tinker.assess_complexity import assess_complexity
from toolsets.tools.tinker.assign_potential_score import assign_potential_score
from toolsets.tools.courier.create_task_event import create_task_event
from toolsets.tools.audit.evaluate_agent_output import evaluate_agent_output


# Mock DB Client that uses a local connection for the demo
class LocalDBClient:
    def __init__(self, db_path):
        self.con = duckdb.connect(db_path)

    def execute(self, sql, params=None):
        return self.con.execute(sql, params or [])


def run_research():
    db = LocalDBClient("Data/WoW_Master.duckdb")
    ai = AIClient(ollama_url="http://localhost:11434/api/chat")

    # Fetch localisation setting
    loc_res = db.execute("SELECT value FROM registry.settings WHERE key = 'localisation'").fetchone()
    loc = loc_res[0] if loc_res else "english"

    print(f"\n[1. LIBRARIAN] Query: 'Demon Hunter in Legion' (Localisation: {loc})")

    # 1. Check Status
    status = check_build_status(db, "7.3.5.25600")
    print(f" Build 7.3.5.25600: {status.get('message')}")

    # 2. Spawn Task
    task_id = create_research_task(db, "Info about Demon Hunters", ["7.3.5.25600"])["task_id"]
    print(f" Task ID: {task_id}")

    # 3. Tinker & Courier
    comp = assess_complexity("Demon Hunter Legion")
    event_id = create_task_event(db, task_id, "Courier", "Expedition Group", {"query": "Lore"})["event_id"]
    assign_potential_score(db, event_id, 100)
    print(f" [OK] Complexity Tier {comp['complexity_tier']} | Event {event_id[:8]} created.")

    # 4. Expedition Group
    print("\n[4. EXPEDITION GROUP] Researching Lore...")
    lore = "Demon Hunters are a hero class introduced in WoW Legion (Patch 7.0.3). Their starting zone is Mardum. They use glaives and can transform into demons."
    print(" Lore point: introduced in Legion (7.0.3)")

    # 5. Archivist
    print("\n[5. ARCHIVIST] Researching DB Structure...")
    db_tables = ["ChrClasses", "SkillLine"]
    print(f" DB References: {db_tables}")

    # 6. Observer
    print("\n[6. OBSERVER] Evaluating Quality...")
    obs = evaluate_agent_output(db, ai.ask, task_id, event_id, {"lore": lore}, 0.95)
    print(f" Score: {obs.get('cpp_percent')}% | Honesty: {obs.get('honesty_rating')}")

    # 7. Librarian Synthesis
    print("\n[7. LIBRARIAN] Creating response for user...")
    # Using the new template logic
    prompt = f"Lore: {lore}. DB Tables: {db_tables}. Construct a response in {loc}."
    final = ai.ask("The Librarian", f"JSON Format {{'response_local': '...'}}: {prompt}")

    print("\n" + "=" * 60)
    print(f"FINAL ANSWER (Grand Library - {loc}):")
    print("-" * 60)
    print(final.get("response_local", "Error generating response."))
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_research()
