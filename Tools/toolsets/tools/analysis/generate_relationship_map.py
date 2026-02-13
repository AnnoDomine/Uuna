# Tools/toolsets/tools/analysis/generate_relationship_map.py
import json
from typing import Callable
import sys
import os
from pathlib import Path

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient
from toolsets.tools.database.get_confirmed_mappings import get_confirmed_mappings
from toolsets.tools.filesystem.save_mermaid_diagram import save_mermaid_diagram

# Define paths to query/prompt directories
QUERY_DIR = Path(__file__).parent / "queries" / "generate_relationship_map"
PROMPT_DIR = Path(__file__).parent / "prompts" / "generate_relationship_map"

def _load_file(path: Path) -> str:
    """Loads a file from a given path."""
    with open(path, 'r') as f:
        return f.read().strip()

def _get_mermaid_documentation(db_client: DBClient) -> str:
    """
    Fetches Mermaid syntax documentation, with a caching mechanism.
    (This is a simplified version of the original's caching).
    """
    try:
        sql = _load_file(QUERY_DIR / "get_mermaid_docs_cache.sql")
        # In this context, we assume a simple cache check. The original had a time-based check.
        res = db_client.execute(sql, ["mermaid_docs", 7]) 
        if res.fetchall():
            return res.fetchone()[0]
    except Exception:
        # Fallback on any error
        pass
        
    # Fallback documentation
    return "erDiagram\n    TABLE1 ||--o{ TABLE2 : relationship"


def generate_relationship_map(db_client: DBClient, ask_ai_func: Callable, build_version: str) -> str:
    """
    Orchestrates the generation of a Mermaid diagram for a build's data relationships.

    Args:
        db_client: An instance of DBClient.
        ask_ai_func: A callable function that takes a prompt and returns a JSON response from an AI.
        build_version: The build version to generate the map for.

    Returns:
        A status string indicating success or failure.
    """
    # 1. Get data using another refactored tool
    mappings = get_confirmed_mappings(db_client, build_version)
    if not mappings:
        return f"INFO: No confirmed mappings found for build {build_version}. No map generated."

    # 2. Get context and templates
    mapping_str = "\n".join([f"- {m[0]}.{m[1]} -> {m[2]}" for m in mappings])
    mmd_docs = _get_mermaid_documentation(db_client)
    template = _load_file(PROMPT_DIR / "visualization_build_relation_map.txt")

    # 3. Format the prompt for the AI
    prompt = template.format(
        build_version=build_version,
        mapping_str=mapping_str,
        mmd_docs=mmd_docs
    )

    # 4. Call the AI
    try:
        # The AI function is expected to handle its own errors and return a dict
        ai_response_str = ask_ai_func(prompt)
        # The original script implies ask_ai_func returns a dict, but if it's a raw string, parse it.
        if isinstance(ai_response_str, str):
            ai_response = json.loads(ai_response_str)
        else:
            ai_response = ai_response_str

        mermaid_code = ai_response.get("mermaid")
        
        if not mermaid_code:
            return "ERROR: AI failed to generate mermaid code."

    except Exception as e:
        return f"ERROR: Failed to get or parse AI response: {e}"

    # 5. Save the result using another refactored tool
    result_status = save_mermaid_diagram(
        name="Build_Map",
        content=mermaid_code,
        build_version=build_version
    )
    
    return result_status

