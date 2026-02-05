import sys
import os
sys.path.append(os.getcwd())

from Tools.core.api.managers.vector_manager import VectorManager
from loguru import logger

# Import modular knowledge
from Tools.core.api.managers.knowledge.expansions import WOW_EXPANSIONS
from Tools.core.api.managers.knowledge.lore import LORE_BASICS, WOW_COSMOLOGY
from Tools.core.api.managers.knowledge.geography import WOW_GEOGRAPHY, WOW_CITIES
from Tools.core.api.managers.knowledge.mechanics import WOW_CLASSES_SPECS, WOW_RACES
from Tools.core.api.managers.knowledge.history_factions import WOW_HISTORY, WOW_FACTIONS
from Tools.core.api.managers.knowledge.technical import WOW_BRANCH_TYPES, CORPORATE_CONTEXT, DATAMINING_PRINCIPLES, DATAMINING_SOP
from Tools.core.api.managers.knowledge.professions import WOW_PROFESSIONS
from Tools.core.api.managers.knowledge.dungeons_raids import WOW_DUNGEONS_RAIDS
from Tools.core.api.managers.knowledge.ai_system import AI_CORE_CONCEPTS, SYSTEM_ARCHITECTURE, SCORING_AND_QUALITY, MEMORY_SYSTEMS

def seed_base_knowledge():
    logger.info("Seeding Finalized Modular Knowledge into Vector Memory...")
    vm = VectorManager(db_path="Data/knowledge/role_memory.duckdb")
    
    # 1. Expansions
    for version, name in WOW_EXPANSIONS.items():
        vm.add_memory("Global", f"Expansion: {name} (Version {version})", {"type": "expansion", "version": version})

    # 2. Lore & Cosmology
    for item in LORE_BASICS:
        vm.add_memory("Global", f"Lore: {item['entity']}. Context: {item['context']}", {"type": "lore"})
    for item in WOW_COSMOLOGY:
        vm.add_memory("Global", f"Cosmology: {item['force']} - {item['entity']}. {item['context']}", {"type": "cosmology"})

    # 3. Geography & Cities
    for item in WOW_GEOGRAPHY:
        vm.add_memory("Global", f"Geography: {item['continent']}. {item['context']}", {"type": "geography"})
    for item in WOW_CITIES:
        vm.add_memory("Global", f"City: {item['city']} ({item['continent']}). {item['context']}", {"type": "city"})

    # 4. Mechanics (Classes, Specs, Races)
    for item in WOW_CLASSES_SPECS:
        vm.add_memory("Global", f"Class: {item['class']}. Specs: {', '.join(item['specs'])}", {"type": "class"})
    for item in WOW_RACES:
        vm.add_memory("Global", f"Race: {item['side']} - {', '.join(item['races'])}", {"type": "race"})

    # 5. History & Factions
    for item in WOW_HISTORY:
        vm.add_memory("Global", f"History: {item['event']}. {item['context']}", {"type": "history"})
    for item in WOW_FACTIONS:
        vm.add_memory("Global", f"Faction: {item['name']}. {item['context']}", {"type": "faction"})

    # 6. Technical & Datamining
    for item in WOW_BRANCH_TYPES:
        vm.add_memory("Global", f"Branch: {item['branch']} ({item['product']})", {"type": "branch"})
    for item in DATAMINING_PRINCIPLES:
        vm.add_memory("Global", f"Datamining Topic: {item['topic']}. {item['context']}", {"type": "datamining"})
    for item in DATAMINING_SOP:
        vm.add_memory("Global", f"Datamining Step: {item['step']}. Action: {item['action']}", {"type": "datamining_sop"})

    # 7. AI System Core
    for item in AI_CORE_CONCEPTS:
        vm.add_memory("Global", f"AI Concept: {item['topic']}. {item['context']}", {"type": "ai_concept"})
    
    # 8. System Architecture
    for item in SYSTEM_ARCHITECTURE:
        vm.add_memory("Global", f"Architecture: {item['component']}. {item['context']}", {"type": "architecture"})

    # 9. Scoring & Quality
    for item in SCORING_AND_QUALITY:
        vm.add_memory("Global", f"Quality/Scoring: {item['mechanism']}. {item['context']}", {"type": "scoring_logic"})

    # 10. Memory Systems
    for item in MEMORY_SYSTEMS:
        vm.add_memory("Global", f"Memory System: {item['system']}. {item['context']}", {"type": "memory_system"})

    # 11. Corporate Context
    for item in CORPORATE_CONTEXT:
        vm.add_memory("Global", f"Corporate Info: {item['entity']}. {item['context']}", {"type": "corporate"})

    # 12. Professions
    for item in WOW_PROFESSIONS:
        vm.add_memory("Global", f"Profession: {item['name']} ({item['type']}). {item['context']}", {"type": "profession"})

    # 13. Dungeons & Raids
    for item in WOW_DUNGEONS_RAIDS:
        vm.add_memory("Global", f"Dungeon/Raid: {item['name']} ({item['type']}). Exp: {item['expansion']}. {item['context']}", {"type": "dungeon_raid"})

    logger.success("All knowledge successfully seeded!")

if __name__ == "__main__":
    seed_base_knowledge()