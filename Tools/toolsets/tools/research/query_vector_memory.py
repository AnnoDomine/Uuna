# Tools/toolsets/tools/research/query_vector_memory.py
from typing import Any, Dict, List

import requests
from Tools.core.shared_debugger import debugger

ORCHESTRA_API_URL = "http://127.0.0.1:8001"


def query_vector_memory(role: str, query: str = None, limit: int = 5, term: str = None) -> List[Dict[str, Any]]:
    """
    Performs a semantic search in the long-term vector memory.

    Args:
    - role: The role name of the agent performing the search.
    - query: The natural language search query.
    - term: Alias for query.
    - limit: Maximum number of results to return.
    """
    search_query = query or term
    if not search_query:
        return []

    payload = {"role": role, "query": search_query, "limit": limit}

    try:
        r = requests.post(f"{ORCHESTRA_API_URL}/memory/search", json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("results", [])
    except Exception as e:
        debugger.add_log(f"Vector memory search failed: {e}", agent="RESEARCH", level="ERROR", process="VectorMemory")
        return []
