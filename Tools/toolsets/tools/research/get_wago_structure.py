# Tools/toolsets/tools/research/get_wago_structure.py
import requests

from Tools.core.shared_debugger import debugger
from .fetch_web_content import _check_cache, _save_cache

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def get_wago_structure(table_name: str, build_version: str, use_cache: bool = True) -> str:
    """
    Fetches the DB2 structure (headers) from wago.tools for a given table and build.

    Args:
    - table_name: The name of the DB2 table.
    - build_version: The WoW build version (e.g. '10.0.0.12345').
    - use_cache: Whether to use the local cache (defaults to True).
    """
    csv_url = f"https://wago.tools/db2/{table_name}/csv?build={build_version}"

    if use_cache:
        cached = _check_cache(csv_url)
        if cached:
            debugger.add_log(f"Using cached Wago structure for {table_name}", agent="RESEARCH", process="WagoStructure")
            return cached

    debugger.add_log(f"Fetching Wago structure for {table_name} (Build {build_version})", agent="RESEARCH", process="WagoStructure")
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
                    _save_cache(csv_url, result, "wago_structure")
                return result

        return f"Wago.tools: No headers found for {table_name} in build {build_version}."
    except Exception as e:
        error_msg = f"Wago API error for {table_name} - {e}"
        debugger.add_log(error_msg, agent="RESEARCH", level="ERROR", process="WagoStructure")
        return error_msg
