import requests
from bs4 import BeautifulSoup
import re
import os
import time
import duckdb
from loguru import logger

# Configuration for Online Research
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
WIKI_BASE = "https://warcraft.wiki.gg"
DB_SERVICE_URL = "http://127.0.0.1:8001"
CACHE_EXPIRY_HOURS = 24

QUERY_CACHE = {}
def load_query(role, task):
    path = f"Tools/queries/{role}/{task}.sql"
    if path in QUERY_CACHE: return QUERY_CACHE[path]
    try:
        with open(path, "r") as f:
            content = f.read()
            QUERY_CACHE[path] = content
            return content
    except: return ""

def db_query(sql, params=[]):
    """Unified API-based query function."""
    try:
        r = requests.post(f"{DB_SERVICE_URL}/query", json={"sql": sql, "params": params}, timeout=60)
        r.raise_for_status()
        return r.json()["results"]
    except Exception as e:
        logger.error(f"DB API Query failed: {e}")
        return []

def db_execute(sql, params=[]):
    """Unified API-based execution function."""
    try:
        r = requests.post(f"{DB_SERVICE_URL}/execute", json={"sql": sql, "params": params}, timeout=60)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"DB API Execute failed: {e}")
        return False

def check_cache(url):
    """Checks if a URL is in the cache and not expired (24h)."""
    try:
        res = db_query(load_query("researcher", "get_cache_entry"), (url, CACHE_EXPIRY_HOURS))
        return res[0][0] if res else None
    except: return None

def save_cache(url, content, source_type):
    """Saves content to the cache."""
    db_execute(load_query("researcher", "save_cache_entry"), (url, content, source_type))

def get_safe_log(run_info="N/A", process="Research", build="N/A"):
    """Returns a logger bound with required fields to avoid KeyErrors."""
    return logger.bind(run_info=run_info, process=process, build=build)

def google_research(queries: list, run_info="N/A"):
    """
    Performs research via a search engine and returns relevant URLs.
    """
    log = get_safe_log(run_info=run_info, process="Google")
    
    # We cache the primary query results
    primary_query = queries[0]
    cached = check_cache(f"search://{primary_query}")
    if cached:
        log.info(f"Using cached search results for: {primary_query}")
        return cached.split(",")

    links = []
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    for query in queries:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        log.info(f"Performing Search for: {query}")
        try:
            r = requests.get(search_url, headers=headers, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if "url?q=" in href and not "webcache" in href:
                        url = href.split("url?q=")[1].split("&")[0]
                        if url.startswith("http"):
                            links.append(url)
        except Exception as e:
            log.error(f"Search error: {e}")
    
    results = list(set(links))[:10]
    if results:
        save_cache(f"search://{primary_query}", ",".join(results), "search")
    return results

def sanitize_html(html_content):
    """
    Strictly sanitizes HTML content. 
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(["script", "style", "iframe", "noscript", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()
    text = soup.get_text(separator='\n')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def get_html_webside(url, run_info="N/A"):
    """
    Fetches HTML content from a URL and sanitizes it strictly.
    """
    log = get_safe_log(run_info=run_info, process="Fetch")
    
    cached = check_cache(url)
    if cached:
        log.info(f"Using cached content for: {url}")
        return cached

    log.info(f"Fetching: {url}")
    try:
        headers = {"User-Agent": USER_AGENT, "Referer": WIKI_BASE}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        sanitized = sanitize_html(response.text)
        save_cache(url, sanitized, "html")
        return sanitized
    except Exception as e:
        log.error(f"Error fetching {url}: {e}")
        return f"ERROR: Could not fetch content from {url}"

def get_wow_wiki_search(query, run_info="N/A"):
    """
    Searches the official Warcraft Wiki via MediaWiki API (opensearch).
    """
    log = get_safe_log(run_info=run_info, process="WikiAPI")
    cache_key = f"wiki_api://{query}"
    
    cached = check_cache(cache_key)
    if cached:
        log.info(f"Using cached Wiki search results for: {query}")
        return cached.split(",")

    api_url = f"{WIKI_BASE}/api.php?action=opensearch&format=json&formatversion=2&search={query.replace(' ', '+')}&namespace=0&limit=5"
    
    log.info(f"Searching Wiki API for: {query}")
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if len(data) >= 4 and isinstance(data[3], list):
            urls = data[3]
            save_cache(cache_key, ",".join(urls), "wiki_search")
            return urls
            
        return []
    except Exception as e:
        log.error(f"Wiki API error: {e}")
        return []

def get_wow_wiki_content(url, run_info="N/A"):
    return get_html_webside(url, run_info=run_info)

def get_wago_structure(table_name, build_version, run_info="N/A"):
    """
    Fetches the DB2 structure (headers) from wago.tools for a given table and build.
    """
    log = get_safe_log(run_info=run_info, process="WagoAPI")
    csv_url = f"https://wago.tools/db2/{table_name}/csv?build={build_version}"
    
    cached = check_cache(csv_url)
    if cached:
        log.info(f"Using cached Wago structure for {table_name}")
        return cached

    log.info(f"Fetching Wago structure for {table_name} (Build {build_version})")
    try:
        headers = {"User-Agent": USER_AGENT}
        with requests.get(csv_url, headers=headers, stream=True, timeout=15) as r:
            r.raise_for_status()
            header_line = ""
            for chunk in r.iter_lines(decode_unicode=True):
                if chunk:
                    header_line = chunk
                    break
            
            if header_line:
                result = f"Wago.tools Headers for {table_name}: {header_line}"
                log.info(f"Successfully retrieved headers from Wago for {table_name}")
                save_cache(csv_url, result, "wago_structure")
                return result
            
        return f"Wago.tools: No headers found for {table_name} in build {build_version}."
    except Exception as e:
        log.error(f"Wago API error: {e}")
        return f"Wago.tools: Error fetching structure ({e})"

if __name__ == "__main__":
    # Test sanitization
    test_html = "<html><body><script>alert('xss')</script><h1>Test</h1><p>Relevant info</p></body></html>"
    print(f"Sanitized: {sanitize_html(test_html)}")
