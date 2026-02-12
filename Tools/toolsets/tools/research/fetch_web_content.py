# Tools/toolsets/tools/research/fetch_web_content.py
import requests
from bs4 import BeautifulSoup
from typing import Optional
import sys
import os
from pathlib import Path

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
QUERY_DIR = Path(__file__).parent / "queries" / "cache"

def _load_query(name: str) -> str:
    with open(QUERY_DIR / f"{name}.sql", 'r') as f:
        return f.read().strip()

def _check_cache(db_client: DBClient, url: str, expiry_hours: int = 24) -> Optional[str]:
    try:
        sql = _load_query("get_cache_entry")
        res = db_client.execute(sql, [url, expiry_hours])
        fetch = res.fetchone()
        return fetch[0] if fetch else None
    except Exception:
        return None

def _save_cache(db_client: DBClient, url: str, content: str, source_type: str):
    try:
        sql = _load_query("save_cache_entry")
        db_client.execute(sql, [url, content, source_type])
    except Exception:
        pass

def sanitize_html(html_content: str) -> str:
    """Strictly cleans HTML content to extract meaningful text."""
    if not html_content: return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove noisy tags
    for tag in soup(["script", "style", "iframe", "noscript", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return "\n".join(chunk for chunk in chunks if chunk)

def fetch_web_content(db_client: DBClient, url: str, use_cache: bool = True) -> str:
    """
    Fetches, sanitizes, and optionally caches web content from a given URL.
    """
    if use_cache:
        cached = _check_cache(db_client, url)
        if cached:
            print(f"INFO: Using cached content for: {url}")
            return cached

    print(f"INFO: Fetching web content: {url}")
    try:
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": "https://warcraft.wiki.gg/"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        sanitized = sanitize_html(response.text)
        
        if use_cache and sanitized:
            _save_cache(db_client, url, sanitized, "html")
            
        return sanitized
    except Exception as e:
        error_msg = f"ERROR: Could not fetch content from {url} - {e}"
        print(error_msg)
        return error_msg
