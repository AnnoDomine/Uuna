# Tools/toolsets/tools/research/fetch_web_content.py
from pathlib import Path
from typing import Optional

# We use curl_cffi to impersonate a real browser TLS fingerprint
# This is essential to bypass Cloudflare 403 Forbidden errors.
from curl_cffi import requests
from bs4 import BeautifulSoup

from Tools.core.shared_db_instance import db
from Tools.core.shared_debugger import debugger

QUERY_DIR = Path(__file__).parent / "queries" / "cache"


def _load_query(name: str) -> str:
    """Loads a SQL query from the tool's query directory."""
    with open(QUERY_DIR / f"{name}.sql", "r") as f:
        return f.read().strip()


def _check_cache(url: str, expiry_hours: int = 24) -> Optional[str]:
    try:
        sql = _load_query("get_cache_entry")
        res = db.execute(sql, [url, expiry_hours])
        fetch = res.fetchone()
        return fetch[0] if fetch else None
    except Exception:
        return None


def _save_cache(url: str, content: str, source_type: str):
    try:
        sql = _load_query("save_cache_entry")
        db.execute(sql, [url, content, source_type])
    except Exception:
        pass


def sanitize_html(html_content: str) -> str:
    """Strictly cleans HTML content to extract meaningful text."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove noisy tags
    for tag in soup(["script", "style", "iframe", "noscript", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return "\n".join(chunk for chunk in chunks if chunk)


def fetch_web_content(url: str, use_cache: bool = True) -> str:
    """
    Fetches, sanitizes, and optionally caches web content.
    Uses curl_cffi to impersonate Chrome and bypass bot protection.

    Args:
    - url: The target URL to fetch.
    - use_cache: Whether to use the local cache (defaults to True).
    """
    if use_cache:
        cached = _check_cache(url)
        if cached:
            debugger.add_log(f"Using cached content for: {url}", agent="RESEARCH", process="FetchWeb")
            return cached

    debugger.add_log(f"Fetching web content via curl_cffi: {url}", agent="RESEARCH", process="FetchWeb")
    try:
        # Use headers that look like a real browser based on provided data
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "referer": "https://www.google.com/"
        }
        
        # impersonate="chrome" handles TLS fingerprinting and HTTP/2 pseudo-headers automatically
        response = requests.get(
            url, 
            headers=headers, 
            impersonate="chrome120", 
            timeout=20,
            allow_redirects=True
        )
        
        response.raise_for_status()
        
        sanitized = sanitize_html(response.text)

        if use_cache and sanitized:
            _save_cache(url, sanitized, "html")

        return sanitized
            
    except Exception as e:
        error_msg = f"Could not fetch content from {url} - {e}"
        debugger.add_log(error_msg, agent="RESEARCH", level="ERROR", process="FetchWeb")
        return error_msg
