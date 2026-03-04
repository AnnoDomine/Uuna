# Tools/toolsets/tools/sentinel/privacy_protection.py
import re
from typing import Dict, Any
from Tools.core.shared_debugger import debugger

# Common patterns for API keys and secrets
SENSITIVE_PATTERNS = {
    "API Key": r"(?:api_key|apikey|secret|token|password|is)\s*[:=\s]\s*[a-zA-Z0-9_\-\.]{16,}",
    "JWT": r"eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+",
    "Private Key": r"-----BEGIN [A-Z ]+ PRIVATE KEY-----",
}


def privacy_protection(data: str) -> Dict[str, Any]:
    """
    Scans data for potential PII or secrets and masks them.

    Args:
    - data: The input string to scan for sensitive information.
    """
    debugger.add_log("Starting privacy scan on data.", agent="SENTINEL", process="Sentinel:Privacy")
    if not data:
        return {"protected_data": "", "leaks_detected": 0}

    leaks_count = 0
    protected = data

    for label, pattern in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, protected, re.IGNORECASE)
        if matches:
            leaks_count += len(matches)
            debugger.add_log(f"Detected {len(matches)} potential leaks of type '{label}'. Masking...", agent="SENTINEL", level="WARNING", process="Sentinel:Privacy")
            # Mask the secret
            protected = re.sub(pattern, f"[MASKED_{label.upper()}]", protected, flags=re.IGNORECASE)

    if leaks_count > 0:
        debugger.add_log(f"Privacy protection complete. {leaks_count} secrets masked.", agent="SENTINEL", level="SUCCESS", process="Sentinel:Privacy")
    else:
        debugger.add_log("No secrets detected in data.", agent="SENTINEL", process="Sentinel:Privacy")

    return {
        "protected_data": protected,
        "leaks_detected": leaks_count,
        "status": "safe" if leaks_count == 0 else "sanitized",
    }
