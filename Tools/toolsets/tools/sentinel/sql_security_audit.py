# Tools/toolsets/tools/sentinel/sql_security_audit.py
import re
from typing import Dict, Any

FORBIDDEN_KEYWORDS = ["DROP", "TRUNCATE", "GRANT", "REVOKE", "ALTER", "DELETE"]


def sql_security_audit(sql_query: str) -> Dict[str, Any]:
    """
    Scans a SQL query for forbidden keywords and potential injection patterns.
    Ensures that only read-safe or allowed internal operations are performed.
    """
    if not sql_query:
        return {"audit_passed": False, "forbidden_detected": ["Empty query"], "threat_level": "Low"}

    forbidden_found = []
    sql_upper = sql_query.upper()

    # 1. Keyword Scan
    for word in FORBIDDEN_KEYWORDS:
        # Match word with boundaries to avoid false positives (e.g., "DROP" vs "DROP_TABLE_LIST")
        if re.search(rf"\b{word}\b", sql_upper):
            forbidden_found.append(word)

    # 2. Identifier Validation (simple check for illegal chars in table names if string formatted)
    # Looking for -- or ; which are common in injections
    if "--" in sql_query or ";" in sql_query.split("--")[0]:
        if ";" in sql_query and not sql_query.strip().endswith(";"):
            forbidden_found.append("Multiple statements (semi-colon)")

    # 3. Threat Level Assessment
    threat_level = "Low"
    if forbidden_found:
        threat_level = "Critical" if any(w in ["DROP", "TRUNCATE"] for w in forbidden_found) else "Medium"

    return {
        "audit_passed": len(forbidden_found) == 0,
        "forbidden_detected": forbidden_found,
        "threat_level": threat_level,
        "checked_query": sql_query[:100] + ("..." if len(sql_query) > 100 else ""),
    }
