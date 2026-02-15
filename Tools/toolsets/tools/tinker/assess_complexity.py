# Tools/toolsets/tools/tinker/assess_complexity.py
import re
from typing import Dict, Any


def assess_complexity(query: str) -> Dict[str, Any]:
    """
    Analyzes a research query to determine its complexity tier.

    Args:
    - query: The research query string.
    """
    if not query:
        return {"tier": 1, "factors": ["Empty query"]}

    factors = []
    score = 0

    # 1. Multi-build detection
    if re.search(r"across|between|all builds|compare", query, re.IGNORECASE):
        factors.append("Multi-build analysis")
        score += 50

    # 2. Lore vs Technical
    if re.search(r"who|why|history|lore|background", query, re.IGNORECASE):
        factors.append("Lore discovery required")
        score += 30

    # 3. Ambiguity check
    if re.search(r"Field_\d+|unknown|cryptic", query, re.IGNORECASE):
        factors.append("Highly ambiguous columns")
        score += 40

    # Tier assignment
    if score >= 80:
        tier = 3
    elif score >= 40:
        tier = 2
    else:
        tier = 1

    return {"complexity_tier": tier, "difficulty_factors": factors, "base_complexity_score": score}
