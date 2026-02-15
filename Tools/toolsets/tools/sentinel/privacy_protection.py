# Tools/toolsets/tools/sentinel/privacy_protection.py
import re
from typing import Dict, Any

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
    if not data:
        return {"protected_data": "", "leaks_detected": 0}

    leaks_count = 0
    protected = data

    for label, pattern in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, protected, re.IGNORECASE)
        if matches:
            leaks_count += len(matches)
            # Mask the secret
            protected = re.sub(pattern, f"[MASKED_{label.upper()}]", protected, flags=re.IGNORECASE)

    return {
        "protected_data": protected,
        "leaks_detected": leaks_count,
        "status": "safe" if leaks_count == 0 else "sanitized",
    }
