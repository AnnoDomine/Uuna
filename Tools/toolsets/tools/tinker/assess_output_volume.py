import json
from typing import Any, Dict
from Tools.core.shared_debugger import debugger


def assess_output_volume(agent_output: Any) -> Dict[str, Any]:
    """
    Assesses the volume and complexity of an agent's output for potential scoring.

    Args:
    - agent_output: The raw output data produced by an agent (list, dict, or string).
    """
    debugger.add_log(f"Assessing output volume for data type: {type(agent_output).__name__}", agent="TINKER", process="Tinker:AssessVolume")
    if not agent_output:
        return {"volume_score": 0, "metrics": {"length": 0, "keys": 0}, "complexity_level": "none"}

    metrics = {}
    score = 0

    if isinstance(agent_output, str):
        length = len(agent_output)
        metrics["char_length"] = length
        score = min(100, length // 10)  # Simple scale: 10 chars = 1 point
    
    elif isinstance(agent_output, list):
        count = len(agent_output)
        metrics["item_count"] = count
        score = min(100, count * 5)  # Simple scale: 1 item = 5 points
        
        # Deep inspection of first item if exists
        if count > 0 and isinstance(agent_output[0], (dict, list)):
            score += 20  # Bonus for structured data
            
    elif isinstance(agent_output, dict):
        keys = len(agent_output.keys())
        metrics["key_count"] = keys
        serialized = json.dumps(agent_output)
        metrics["serialized_length"] = len(serialized)
        
        score = min(100, (keys * 10) + (len(serialized) // 50))

    # Determine complexity level
    if score >= 80:
        level = "high"
    elif score >= 40:
        level = "medium"
    else:
        level = "low"

    result = {
        "volume_score": score,
        "metrics": metrics,
        "complexity_level": level,
        "reasoning": f"Volume assessment based on {type(agent_output).__name__} structure."
    }
    debugger.add_log(f"Volume assessment complete. Score: {score}. Level: {level}", agent="TINKER", level="SUCCESS", process="Tinker:AssessVolume")
    return result
