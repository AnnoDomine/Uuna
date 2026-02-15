# Tools/run_demon_hunter_research.py
import sys
import os

# Ensure path resolution
sys.path.append(os.getcwd())

from Tools.core.ai_client import AIClient
from Tools.core.db_client import DBClient
from Tools.toolsets.tools.registry.check_build_status import check_build_status
from Tools.toolsets.tools.system.create_research_task import create_research_task
from Tools.toolsets.tools.tinker.assess_complexity import assess_complexity
from Tools.toolsets.tools.tinker.assign_potential_score import assign_potential_score
from Tools.toolsets.tools.courier.create_task_event import create_task_event
from Tools.toolsets.tools.audit.evaluate_agent_output import evaluate_agent_output


def ask_ai_wrapper(ai_client: AIClient, role, prompt, build_ver, run_info, process_name, **kwargs):
    """Wrapper to maintain compatibility with existing tool signatures."""
    # Role header is added by AIClient.ask internally
    return ai_client.ask(role, prompt)


def run_research():
    # Mandate: Use DBClient with Middleware
    db = DBClient(url="http://127.0.0.1:8002")
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

    # Bridge to AIClient
    def ask_ai(r, p, bv, ri, pn, **kw):
        return ask_ai_wrapper(ai, r, p, bv, ri, pn, **kw)

    event_id = create_task_event(db, task_id, "Courier", "Expedition Group", {"query": "Lore"})["event_id"]
    assign_potential_score(db, event_id, 100)
    print(f" [OK] Complexity Tier {comp.get('complexity_tier')} | Event {event_id[:8]} created.")

    # 4. Expedition Group
    print("\n[4. EXPEDITION GROUP] Researching Lore...")
    lore = "Demon Hunters are a hero class introduced in WoW Legion (Patch 7.0.3). Their starting zone is Mardum. They use glaives and can transform into demons."

    # 5. Archivist
    print("\n[5. ARCHIVIST] Researching DB Structure...")
    db_tables = ["ChrClasses", "SkillLine"]

    # 6. Observer
    print("\n[6. OBSERVER] Evaluating Quality...")
    obs = evaluate_agent_output(db, ask_ai, task_id, event_id, {"lore": lore}, 0.95)
    print(f" Score: {obs.get('cpp_percent')}% | Honesty: {obs.get('honesty_rating')}")

    # 7. Librarian Synthesis
    print("\n[7. LIBRARIAN] Creating response for user...")
    role_header = "ROLE: You are the Librarian. Synthesize knowledge for the user."
    prompt = f"Lore: {lore}. DB Tables: {db_tables}. Construct a response in {loc}."
    final = ai.ask(role_header, f"JSON Format {{'response_local': '...'}}: {prompt}")

    print("\n" + "=" * 60)
    print(f"FINAL ANSWER (Grand Library - {loc}):")
    print("-" * 60)
    print(final.get("response_local", "Error generating response."))
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_research()
