# Tools/toolsets/tools/analysis/guess_table_reference.py
import difflib
from typing import List, Dict, Union


def guess_table_reference(potential_name: str, all_table_names: List[str]) -> List[Dict[str, Union[str, float]]]:
    """
    Suggests matching table names based on a potential reference name.

    Args:
    - potential_name: The base name to find a match for (e.g. 'Spell').
    - all_table_names: A list of all table names to search within.
    """
    suggestions = {}

    # Hardcoded known aliases with high confidence
    aliases = {
        "Quest": "QuestV2",
        "Spell": "SpellName",
        "Item": "ItemSparse",
        "BroadcastText": "BroadcastText",
        "ConversationLine": "ConversationLine",
    }

    # 1. Direct Match (Case Insensitive)
    p_low = potential_name.lower()
    for t in all_table_names:
        if t.lower() == p_low:
            suggestions[t] = {"reason": "Direct Match (case-insensitive)", "confidence": 1.0}

    # 2. Check Aliases
    if potential_name in aliases:
        target = aliases[potential_name]
        if target in all_table_names and target not in suggestions:
            suggestions[target] = {"reason": "Alias Match", "confidence": 0.98}

    # 3. Auto-Suffixes
    for suffix in ["V2", "V3", "V4", "Sparse", "Name"]:
        variant = potential_name + suffix
        if variant in all_table_names and variant not in suggestions:
            suggestions[variant] = {"reason": f"Suffix Match ('{suffix}')", "confidence": 0.95}
        # Check case-insensitively as well
        for t in all_table_names:
            if t.lower() == variant.lower() and t not in suggestions:
                suggestions[t] = {"reason": f"Suffix Match (case-insensitive, '{suffix}')", "confidence": 0.94}

    # 4. Fuzzy Matching using difflib
    fuzzy_matches = difflib.get_close_matches(potential_name, all_table_names, n=15, cutoff=0.5)
    for match in fuzzy_matches:
        if match not in suggestions:
            # difflib doesn't give a score, so we'll estimate one.
            # A higher cutoff in get_close_matches implies higher confidence.
            ratio = difflib.SequenceMatcher(None, potential_name, match).ratio()
            suggestions[match] = {"reason": "Fuzzy Match", "confidence": round(ratio, 2)}

    # 5. Substring matches
    for t in all_table_names:
        if p_low in t.lower() and t not in suggestions:
            suggestions[t] = {"reason": "Substring Match", "confidence": 0.4}

    # Format the output into a sorted list of dictionaries
    result = [{"table": table, **data} for table, data in suggestions.items()]
    result.sort(key=lambda x: x["confidence"], reverse=True)

    return result
