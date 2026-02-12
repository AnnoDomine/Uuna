# Tools/run_demon_hunter_research.py
import sys
import os
import json
import duckdb
from loguru import logger

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
    db = LocalDBClient('Data/WoW_Master.duckdb')
    ai = AIClient(ollama_url="http://localhost:11434/api/chat")
    
    print("\n[1. LIBRARIAN] Anfrage: 'Dämonenjäger in Legion'")
    
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
    print(f" [OK] Komplexität Tier {comp['complexity_tier']} | Event {event_id[:8]} erstellt.")

    # 4. Expedition Group
    print("\n[4. EXPEDITION GROUP] Recherchiere Lore...")
    lore = "Dämonenjäger sind eine Heldenklasse, die in WoW Legion (Patch 7.0.3) eingeführt wurde. Ihre Startzone ist Mardum. Sie nutzen Gleven und können sich in Dämonen verwandeln."
    print(f" Lore-Punkt: introduziert in Legion (7.0.3)")

    # 5. Archivist
    print("\n[5. ARCHIVIST] Recherchiere DB-Struktur...")
    db_tables = ["ChrClasses", "SkillLine"]
    print(f" Datenbank-Referenzen: {db_tables}")

    # 6. Observer
    print("\n[6. OBSERVER] Berechne Qualität...")
    obs = evaluate_agent_output(db, ai.ask, task_id, event_id, {"lore": lore}, 0.95)
    print(f" Score: {obs.get('cpp_percent')}% | Honesty: {obs.get('honesty_rating')}")

    # 7. Librarian Synthesis
    print("\n[7. LIBRARIAN] Erstelle Antwort für Nutzer...")
    prompt = f"Lore: {lore}. DB Tables: {db_tables}. Erkläre es einem Nutzer auf Deutsch."
    final = ai.ask("The Librarian", f"JSON Format {{'response_german': '...'}}: {prompt}")
    
    print("\n" + "="*60)
    print("FINALE ANTWORT (Grand Library):")
    print("-" * 60)
    print(final.get("response_german"))
    print("="*60 + "\n")

if __name__ == "__main__":
    run_research()
