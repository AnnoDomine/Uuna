import re

def sanitize_user_prompt(prompt: str) -> str:
    """
    Sanitizes user input to mitigate prompt injection attacks.
    Removes common injection patterns and escapes sensitive sequences.
    """
    if not prompt:
        return ""

    # 1. Block common prompt injection keywords/phrases (case-insensitive)
    injection_patterns = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+prior",
        r"system\s+override",
        r"you\s+are\s+now\s+an\s+admin",
        r"new\s+role:",
        r"forget\s+everything",
        r"stop\s+following\s+rules"
    ]
    
    sanitized = prompt
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "[DELETED_INJECTION_ATTEMPT]", sanitized, flags=re.IGNORECASE)

    # 2. Limit length to prevent overflow/resource exhaustion attacks
    max_length = 2000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... [TRUNCATED]"

    # 3. Escape potential markdown/structure breaking characters if necessary
    # (Simplified for now, as most LLMs handle this via roles)
    
    return sanitized.strip()

def sanitize_identifier(name: str) -> str:
    """
    Validates that a table or column name contains only alphanumeric characters 
    and underscores. Raises ValueError if invalid characters are detected.
    Supports 'schema.table' format.
    """
    if not name:
        raise ValueError("Identifier name cannot be empty.")
    
    # Allow alphanumeric, underscores, and a single dot for schema prefix
    if not re.match(r"^[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)?$", name):
        raise ValueError(f"Invalid identifier detected: '{name}'. Only alphanumeric characters and underscores are allowed.")
    
    return name
