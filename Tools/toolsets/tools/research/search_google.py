from typing import List

from ddgs import DDGS

from Tools.core.shared_debugger import debugger

from .fetch_web_content import _check_cache, _save_cache


class DDGSResult:
    title: str
    href: str
    body: str


def merge_search_results(results: List[DDGSResult]) -> List[str]:
    merged_results = []
    for result in results:
        title = result.title
        href = result.href
        body = result.body

        string = f"\n====== Search Result: {title} ======\nHref: {href}\nBody:\n{body}\n====================================\n"

        merged_results.append(string)

    return merged_results


def search_web(query: str, use_cache: bool = True) -> List[str]:
    """
    Search web via duckduckgo.

    Args:
    - query: The search query.
    - use_cache: Whether to use the local cache (defaults to True).
    """
    if use_cache:
        cached = _check_cache(query)
        if cached:
            debugger.add_log(
                f"Using cached Google search results for: {query}", agent="RESEARCH", process="GoogleSearch"
            )
            return cached.split(",")

    debugger.add_log(f"Searching Google for: {query}", agent="RESEARCH", process="GoogleSearch")
    try:
        searchRes: DDGSResult = DDGS().text(query, max_results=5, safesearch="off")

        result_list = merge_search_results(searchRes)
        if use_cache and result_list:
            _save_cache(query, ",".join(result_list), "google_search")
        return result_list
    except Exception as e:
        debugger.add_log(f"Google search failed: {e}", agent="RESEARCH", level="ERROR", process="GoogleSearch")
        return []
