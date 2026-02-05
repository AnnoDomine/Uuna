import requests
import uuid
import json
from loguru import logger

API_URL = "http://127.0.0.1:8001"

def run_research_test():
    logger.info("Starting Research Test Flow...")

    # 1. Create a Task
    objective = "Find all spells related to Sylvanas Windrunner in Midnight (12.0.0)"
    try:
        r = requests.post(f"{API_URL}/tasks/create", json={"objective": objective})
        r.raise_for_status()
        task_id = r.json()["task_id"]
        logger.success(f"Task Created: {task_id}")
    except Exception as e:
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Failed to create task: {e.response.text}")
        else:
            logger.error(f"Failed to create task: {e}")
        return

    # 2. Query Vector Memory for Context (Simulating Librarian)
    logger.info("Querying Vector Memory for context...")
    try:
        # Search for Sylvanas and Midnight
        r = requests.post(f"{API_URL}/memory/search", json={
            "role": "Global",
            "query": "Who is Sylvanas Windrunner and what version is Midnight?",
            "limit": 3
        })
        r.raise_for_status()
        results = r.json()["results"]
        
        logger.info("Context found in Vector Memory:")
        for res in results:
            logger.info(f"  - [{res['score']:.4f}] {res['content']}")
    except Exception as e:
        logger.error(f"Failed to query memory: {e}")

    # 3. Simulate an Agent Step (Event)
    event_id = str(uuid.uuid4())
    logger.info(f"Simulating Agent Action (Event: {event_id})...")
    
    # In a real scenario, we'd have a /events/create endpoint. 
    # For now, we'll just log it.
    logger.info(f"Agent 'Archivist' is searching archive.Spell for 'Sylvanas' in build_id corresponding to 12.0.0")
    
    # 4. Simulate a Discovery
    discovery = {
        "spell_id": 456789,
        "name": "Banshee's Wail (Midnight Edition)",
        "description": "Sylvanas unleashes a cry from the void."
    }
    
    logger.success(f"Discovery made: {discovery['name']} (ID: {discovery['spell_id']})")
    
    # 5. Store Discovery back to Vector Memory (Simulating Sages approval)
    logger.info("Committing approved knowledge to Long-Term Memory...")
    try:
        mem_content = f"Discovery: Spell '{discovery['name']}' (ID: {discovery['spell_id']}) found in Midnight (12.0.0). Context: Related to Sylvanas Windrunner."
        r = requests.post(f"{API_URL}/memory/add", json={
            "role": "Archivist",
            "content": mem_content,
            "metadata": {"task_id": task_id, "build": "12.0.0", "type": "discovery"}
        })
        r.raise_for_status()
        logger.success("Knowledge stored in Vector DB.")
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")

if __name__ == "__main__":
    run_research_test()
