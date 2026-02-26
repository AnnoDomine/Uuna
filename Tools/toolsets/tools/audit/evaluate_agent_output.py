import json
from pathlib import Path
from typing import Any, Callable, Dict

from Tools.core.shared_db_instance import db

QUERY_DIR = Path(__file__).parent / "queries" / "evaluate_agent_output"
PROMPT_DIR = Path(__file__).parent / "prompts" / "evaluate_agent_output"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def _load_prompt(name: str) -> str:
    """Loads a prompt template from the tool's local prompt directory."""
    path = PROMPT_DIR / f"{name}.txt"
    if path.exists():
        with open(path, "r") as f:
            return f.read().strip()
    return ""


def evaluate_agent_output(
    ask_ai_func: Callable,
    task_id: str,
    event_id: str,
    agent_output: Any,
    reported_confidence: float,
) -> Dict[str, Any]:
    """
    Evaluates an agent's output using the Observer's strict logic.

    Args:
    - ask_ai_func: Function to call the AI for evaluation.
    - task_id: The UUID of the task.
    - event_id: The UUID of the event.
    - agent_output: The actual output produced by the agent.
    - reported_confidence: The confidence reported by the agent.
    """
    try:
        # 1. Fetch Max Potential blindly from DB
        sql_pot = _load_query("get_potential")
        res_pot = db.execute(sql_pot, [event_id]).fetchone()

        # Default to 100 if for some reason not set, but log warning
        max_potential_points = res_pot[0] if res_pot and res_pot[0] > 0 else 100

        # 2. Prepare AI Observer Context
        system_prompt = _load_prompt("system_prompt")
        protocol = _load_prompt("protocol_database")

        full_prompt = f"{system_prompt}\n\nEVALUATION PROTOCOL:\n{protocol}\n\nAGENT OUTPUT:\n{json.dumps(agent_output)}\nCONFIDENCE: {reported_confidence}"

        # 3. Call AI Observer
        ai_result = ask_ai_func("The Observer", full_prompt, "N/A", f"Task: {task_id[:8]}", "Evaluation")

        # 4. Process internal points
        awarded_points = float(ai_result.get("quality_score", 0))

        # Effective Confidence Floor (0.7)
        effective_confidence = max(float(reported_confidence), 0.7)

        # Role-Personal-Score (Honesty Check)
        # Formula: Awarded_Points / (Max_Potential * Effective_Confidence)
        personal_score = (awarded_points / (max_potential_points * effective_confidence)) * 100
        personal_score = min(personal_score, 100.0)

        # Cooperation-Part-Points (CPP)
        # Formula: Awarded_Points / Max_Potential
        cpp = (awarded_points / max_potential_points) * 100

        # 5. Return ONLY percentage and qualitative results
        return {
            "verdict": ai_result.get("verdict"),
            "personal_score_percent": round(personal_score, 2),
            "cpp_percent": round(cpp, 2),
            "honesty_rating": ai_result.get("honesty_rating"),
            "recommendation": ai_result.get("sage_recommendation"),
        }
    except Exception as e:
        return {"error": str(e), "recommendation": "BLOCK"}
