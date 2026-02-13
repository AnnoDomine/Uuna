# Tools/toolsets/tools/research/get_wago_structure.py
import requests
import sys
import os

# Ensure path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from core.db_client import DBClient
from .fetch_web_content import _check_cache, _save_cache

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_wago_structure(db_client: DBClient, table_name: str, build_version: str, use_cache: bool = True) -> str:
    """
    Fetches the DB2 structure (headers) from wago.tools for a given table and build.
    """
    csv_url = f"https://wago.tools/db2/{table_name}/csv?build={build_version}"

    if use_cache:
        cached = _check_cache(db_client, csv_url)
        if cached:
            print(f"INFO: Using cached Wago structure for {table_name}")
            return cached

    print(f"INFO: Fetching Wago structure for {table_name} (Build {build_version})")
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
                if use_cache:
                    _save_cache(db_client, csv_url, result, "wago_structure")
                return result

        return f"INFO: Wago.tools: No headers found for {table_name} in build {build_version}."
    except Exception as e:
        error_msg = f"ERROR: Wago API error for {table_name} - {e}"
        print(error_msg)
        return error_msg
