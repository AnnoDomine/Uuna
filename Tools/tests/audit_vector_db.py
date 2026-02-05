import sys
import os
sys.path.append(os.getcwd())

from Tools.core.api.managers.vector_manager import VectorManager
import json

def audit_knowledge():
    vm = VectorManager()
    categories = [
        "expansion", "lore", "cosmology", "geography", "city", 
        "class", "race", "history", "faction", "branch", 
        "datamining", "profession", "dungeon_raid", "corporate"
    ]
    
    print("="*50)
    print("VECTOR DB KNOWLEDGE AUDIT (FEBRUARY 2026)")
    print("="*50)
    
    for cat in categories:
        # Search for the category name to see if records are found
        results = vm.search_memory("Global", f"What info do we have about {cat}?", limit=3) 
        
        status = "✅ LOADED" if results else "❌ EMPTY"
        print(f"\n[{status}] Category: {cat.upper()}")
        
        for i, res in enumerate(results):
            score = res['score']
            content = res['content'][:120] + "..." if len(res['content']) > 120 else res['content']
            print(f"  {i+1}. [Score: {score:.4f}] {content}")

if __name__ == "__main__":
    audit_knowledge()
