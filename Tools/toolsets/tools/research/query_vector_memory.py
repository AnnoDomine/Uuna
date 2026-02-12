# Tools/toolsets/tools/research/query_vector_memory.py
import requests
from typing import List, Dict, Any, Optional
import sys
import os
from pathlib import Path

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

ORCHESTRA_API_URL = "http://127.0.0.1:8001"

def query_vector_memory(role: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a semantic search in the library's long-term vector memory.
    Useful for finding patterns or lore facts across different WoW expansions.
    """
    payload = {
        "role": role,
        "query": query,
        "limit": limit
    }
    
    try:
        r = requests.post(f"{ORCHESTRA_API_URL}/memory/search", json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("results", [])
    except Exception as e:
        print(f"ERROR: Vector memory search failed: {e}")
        return []
