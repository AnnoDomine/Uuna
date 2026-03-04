# Tools/toolsets/tools/research/search_wow_wiki.py
from typing import List

import requests

from Tools.core.shared_debugger import debugger
from .fetch_web_content import _check_cache, _save_cache

WIKI_BASE = "https://warcraft.wiki.gg"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def search_wow_wiki(query: str, use_cache: bool = True) -> List[str]:
    """
    Searches the official Warcraft Wiki via MediaWiki API.

    Args:
    - query: The search query.
    - use_cache: Whether to use the local cache (defaults to True).
    """
    cache_key = f"wiki_api://{query}"

    if use_cache:
        cached = _check_cache(cache_key)
        if cached:
            debugger.add_log(f"Using cached Wiki search results for: {query}", agent="RESEARCH", process="WikiSearch")
            return cached.split(",")

    debugger.add_log(f"Searching Wiki API for: {query}", agent="RESEARCH", process="WikiSearch")
    api_url = f"{WIKI_BASE}/api.php?action=opensearch&format=json&formatversion=2&search={query.replace(' ', '+')}&namespace=0&limit=5"

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if len(data) >= 4 and isinstance(data[3], list):
            urls = data[3]
            if use_cache and urls:
                _save_cache(cache_key, ",".join(urls), "wiki_search")
            return urls

        return []
    except Exception as e:
        debugger.add_log(f"Wiki API search failed: {e}", agent="RESEARCH", level="ERROR", process="WikiSearch")
        return []
