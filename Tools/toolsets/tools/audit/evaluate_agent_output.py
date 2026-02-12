# Tools/toolsets/tools/audit/evaluate_agent_output.py
import json
from typing import Callable, Dict, Any, List
from pathlib import Path
import sys
import os

# Ensure the parent directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

PROMPT_DIR = Path(__file__).parent / "prompts" / "evaluate_agent_output"

def _load_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}.txt"
    if path.exists():
        with open(path, 'r') as f:
            return f.read().strip()
    return ""

def evaluate_agent_output(
    db_client: DBClient, 
    ask_ai_func: Callable,
    task_id: str,
    event_id: str,
    agent_output: Any,
    reported_confidence: float,
    max_potential_points: int = 100
) -> Dict[str, Any]:
    """
    Evaluates an agent's output using the Observer's strict logic.
    """
    # 1. Prepare Context (In a real system, we'd fetch logs/input here)
    system_prompt = _load_prompt("system_prompt")
    protocol = _load_prompt("protocol_database")
    
    # 2. Call the AI Observer
    # Note: ask_ai_func parameters might vary, but we follow the agent's pattern
    full_prompt = f"{system_prompt}\n\nEVALUATION PROTOCOL:\n{protocol}\n\nAGENT OUTPUT:\n{json.dumps(agent_output)}\nCONFIDENCE: {reported_confidence}"
    
    # For now, we assume ask_ai_func takes (role, prompt, build_version, run_info, process_name)
    ai_result = ask_ai_func("The Observer", full_prompt, "N/A", f"Task: {task_id[:8]}", "Evaluation")
    
    # 3. Apply the "Bad Boy" Observer logic
    awarded_points = float(ai_result.get("quality_score", 0))
    
    # Effective Confidence Floor (0.7)
    effective_confidence = max(float(reported_confidence), 0.7)
    
    # Role-Personal-Score (Honesty Check)
    # Awarded_Points / (Max_Potential * Effective_Confidence)
    personal_score = (awarded_points / (max_potential_points * effective_confidence)) * 100
    personal_score = min(personal_score, 100.0)
    
    # Cooperation-Part-Points (CPP)
    # Awarded_Points / Max_Potential
    cpp = (awarded_points / max_potential_points) * 100
    
    return {
        "verdict": ai_result.get("verdict"),
        "quality_score": awarded_points,
        "personal_score_percent": personal_score,
        "cpp_percent": cpp,
        "honesty_rating": ai_result.get("honesty_rating"),
        "recommendation": ai_result.get("sage_recommendation")
    }
