# Tools/toolsets/tools/sentinel/sanitize_data.py
import re
from bs4 import BeautifulSoup
from typing import Dict, Any


def sanitize_data(raw_content: str) -> Dict[str, Any]:
    """
    Strictly sanitizes raw content by removing HTML tags, scripts,
    styles, and common web noise (boilerplate).
    """
    if not raw_content:
        return {"sanitized_content": "", "removed_elements_count": 0, "purity_score": 1.0}

    # 1. HTML Sanitization
    soup = BeautifulSoup(raw_content, "html.parser")
    removed_count = 0

    # Elements to completely remove
    for tag in soup(["script", "style", "iframe", "noscript", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()
        removed_count += 1

    text = soup.get_text(separator="\n")

    # 2. Cleanup Whitespace and Noise
    lines = (line.strip() for line in text.splitlines())
    # Remove common boilerplate patterns
    noise_patterns = [r"Copyright ©.*", r"All rights reserved.*", r"Terms of Service", r"Privacy Policy"]

    clean_lines = []
    for line in lines:
        if not line:
            continue
        is_noise = any(re.search(p, line, re.IGNORECASE) for p in noise_patterns)
        if not is_noise:
            clean_lines.append(line)
        else:
            removed_count += 1

    sanitized = "\n".join(clean_lines)

    # Calculate a basic purity score (ratio of clean vs raw length)
    purity = min(1.0, len(sanitized) / max(1, len(raw_content)))

    return {"sanitized_content": sanitized, "removed_elements_count": removed_count, "purity_score": round(purity, 2)}
