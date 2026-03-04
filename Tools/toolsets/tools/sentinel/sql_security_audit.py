# Tools/toolsets/tools/sentinel/sql_security_audit.py
import re
from typing import Dict, Any
from Tools.core.shared_debugger import debugger

FORBIDDEN_KEYWORDS = ["DROP", "TRUNCATE", "GRANT", "REVOKE", "ALTER", "DELETE"]


def sql_security_audit(query: str) -> Dict[str, Any]:
    """
    Scans a SQL query for forbidden keywords and patterns.

    Args:
    - query: The raw SQL query string to audit.
    """
    debugger.add_log(f"Auditing SQL Security for query: {query[:50]}...", agent="SENTINEL", process="Sentinel:SQLAudit")
    if not query:
        return {"audit_passed": False, "forbidden_detected": ["Empty query"], "threat_level": "Low"}

    forbidden_found = []
    sql_upper = query.upper()

    # 1. Keyword Scan
    for word in FORBIDDEN_KEYWORDS:
        # Match word with boundaries to avoid false positives
        if re.search(rf"\b{word}\b", sql_upper):
            forbidden_found.append(word)

    # 2. Identifier Validation
    if "--" in query or ";" in query.split("--")[0]:
        if ";" in query and not query.strip().endswith(";"):
            forbidden_found.append("Multiple statements (semi-colon)")

    # 3. Threat Level Assessment
    threat_level = "Low"
    if forbidden_found:
        threat_level = "Critical" if any(w in ["DROP", "TRUNCATE"] for w in forbidden_found) else "Medium"
        level = "ERROR" if threat_level == "Critical" else "WARNING"
        debugger.add_log(f"SECURITY ALERT: Forbidden patterns detected: {forbidden_found} (Threat: {threat_level})", agent="SENTINEL", level=level, process="Sentinel:SQLAudit")

    result = {
        "audit_passed": len(forbidden_found) == 0,
        "forbidden_detected": forbidden_found,
        "threat_level": threat_level,
        "checked_query": query[:100] + ("..." if len(query) > 100 else ""),
    }
    
    if result["audit_passed"]:
        debugger.add_log("SQL Security Audit passed.", agent="SENTINEL", level="SUCCESS", process="Sentinel:SQLAudit")
        
    return result
