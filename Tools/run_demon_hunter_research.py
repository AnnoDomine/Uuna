# Tools/run_demon_hunter_research.py
import sys
import os

# Ensure path resolution
sys.path.append(os.getcwd())

from Tools.core.ai_client import AIClient
from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger
from Tools.toolsets.tools.registry.check_build_status import check_build_status
from Tools.toolsets.tools.system.create_research_task import create_research_task
from Tools.toolsets.tools.tinker.assess_complexity import assess_complexity
from Tools.toolsets.tools.tinker.assign_potential_score import assign_potential_score
from Tools.toolsets.tools.courier.create_task_event import create_task_event
from Tools.toolsets.tools.audit.evaluate_agent_output import evaluate_agent_output


def ask_ai_wrapper(ai_client: AIClient, role, prompt, build_ver, run_info, process_name, **kwargs):
    """Wrapper to maintain compatibility with existing tool signatures."""
    debugger.add_log(f"AI Request for {role}", agent="AI_CLIENT", process=process_name, build=build_ver, run_info=run_info, **kwargs)
    return ai_client.ask(role, prompt)


def run_research():
    ai = AIClient(ollama_url="http://localhost:11434/api/chat")

    # Fetch localisation setting
    loc_res = db.execute("SELECT value FROM registry.settings WHERE key = 'localisation'").fetchone()
    loc = loc_res[0] if loc_res else "english"

    debugger.add_log(f"Starting Demon Hunter Research Demo (Localisation: {loc})", agent="LIBRARIAN", process="Demo:Run")

    # 1. Check Status
    status = check_build_status("7.3.5.25600")
    debugger.add_log(f"Build 7.3.5.25600 status: {status.get('message')}", agent="LIBRARIAN", process="Demo:Status")

    # 2. Spawn Task
    task_res = create_research_task("Info about Demon Hunters", ["7.3.5.25600"])
    task_id = task_res["task_id"]
    debugger.add_log(f"Task spawned: {task_id}", agent="LIBRARIAN", process="Demo:Task")

    # 3. Tinker & Courier
    comp = assess_complexity("Demon Hunter Legion")

    # Bridge to AIClient
    def ask_ai(r, p, bv, ri, pn, **kw):
        return ask_ai_wrapper(ai, r, p, bv, ri, pn, **kw)

    event_res = create_task_event(task_id, "Courier", "Expedition Group", {"query": "Lore"})
    event_id = event_res["event_id"]
    assign_potential_score(event_id, 100)
    debugger.add_log(f"Complexity Tier {comp.get('complexity_tier')} | Event {event_id[:8]} created.", agent="COURIER", process="Demo:Event")

    # 4. Expedition Group
    debugger.add_log("Researching Lore...", agent="EXPEDITION_GROUP", process="Demo:Lore")
    lore = "Demon Hunters are a hero class introduced in WoW Legion (Patch 7.0.3). Their starting zone is Mardum. They use glaives and can transform into demons."

    # 5. Archivist
    debugger.add_log("Researching DB Structure...", agent="ARCHIVIST", process="Demo:DB")
    db_tables = ["ChrClasses", "SkillLine"]

    # 6. Observer
    debugger.add_log("Evaluating Quality...", agent="OBSERVER", process="Demo:Quality")
    obs = evaluate_agent_output(ask_ai, task_id, event_id, {"lore": lore}, 0.95)
    debugger.add_log(f"Score: {obs.get('cpp_percent')}% | Honesty: {obs.get('honesty_rating')}", agent="OBSERVER", process="Demo:Quality")

    # 7. Librarian Synthesis
    debugger.add_log("Creating response for user...", agent="LIBRARIAN", process="Demo:Synthesis")
    role_header = "ROLE: You are the Librarian. Synthesize knowledge for the user."
    prompt = f"Lore: {lore}. DB Tables: {db_tables}. Construct a response in {loc}."
    final = ai.ask(role_header, f"JSON Format {{'response_local': '...'}}: {prompt}")

    print("\n" + "=" * 60)
    print(f"FINAL ANSWER (Grand Library - {loc}):")
    print("-" * 60)
    print(final.get("response_local", "Error generating response."))
    print("=" * 60 + "\n")
    debugger.add_log("Demo research finished successfully.", agent="LIBRARIAN", level="SUCCESS", process="Demo:Run")


if __name__ == "__main__":
    run_research()
