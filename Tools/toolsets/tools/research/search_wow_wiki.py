# Tools/toolsets/tools/research/search_wow_wiki.py
import requests
from typing import List, Optional
import sys
import os
from pathlib import Path

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient
from .fetch_web_content import _check_cache, _save_cache

WIKI_BASE = "https://warcraft.wiki.gg"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def search_wow_wiki(db_client: DBClient, query: str, use_cache: bool = True) -> List[str]:
    """
    Searches the official Warcraft Wiki via MediaWiki API.
    """
    cache_key = f"wiki_api://{query}"
    
    if use_cache:
        cached = _check_cache(db_client, cache_key)
        if cached:
            print(f"INFO: Using cached Wiki search results for: {query}")
            return cached.split(",")

    print(f"INFO: Searching Wiki API for: {query}")
    api_url = f"{WIKI_BASE}/api.php?action=opensearch&format=json&formatversion=2&search={query.replace(' ', '+')}&namespace=0&limit=5"

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if len(data) >= 4 and isinstance(data[3], list):
            urls = data[3]
            if use_cache and urls:
                _save_cache(db_client, cache_key, ",".join(urls), "wiki_search")
            return urls

        return []
    except Exception as e:
        print(f"ERROR: Wiki API search failed: {e}")
        return []
