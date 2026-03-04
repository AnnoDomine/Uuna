import requests
import pandas as pd
from Tools.core.shared_debugger import debugger


class DBResult:
    def __init__(self, data):
        self.data = data

    def fetchall(self):
        return self.data.get("results", [])

    def fetchone(self):
        results = self.data.get("results", [])
        return results[0] if results else None

    def df(self):
        results = self.data.get("results", [])
        columns = self.data.get("columns", [])
        return pd.DataFrame(results, columns=columns)

    @property
    def rowcount(self):
        if self.data.get("status") == "success":
            return 1
        return len(self.data.get("results", []))


class DBClient:
    def __init__(self, url="http://127.0.0.1:8002"):
        self.url = url

    def execute(self, sql, params=None):
        if params is None:
            params = []

        # Determine endpoint: Modifying operations MUST go to /execute
        # 1. Clean SQL (remove comments and whitespace for detection)
        import re
        clean_lines = [line.split('--')[0].split('#')[0].strip() for line in sql.splitlines()]
        clean_sql_for_detect = " ".join([line for line in clean_lines if line]).upper()
        
        words = clean_sql_for_detect.split()
        first_word = words[0] if words else ""

        modifying_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "SET"]
        query_keywords = ["SELECT", "PRAGMA", "SHOW", "DESCRIBE", "WITH", "EXPLAIN"]
        
        if first_word in modifying_keywords:
            endpoint = "/execute"
        elif first_word in query_keywords:
            endpoint = "/query"
        else:
            # Fallback: check if ANY modifying keyword exists as a full word
            is_modifying = any(re.search(rf"\b{k}\b", clean_sql_for_detect) for k in modifying_keywords)
            endpoint = "/execute" if is_modifying else "/query"

        try:
            r = requests.post(f"{self.url}{endpoint}", json={"sql": sql, "params": params}, timeout=600)
            if r.status_code != 200:
                debugger.add_log(f"DB API Error: {r.status_code} - {r.text} | SQL: {sql[:200]}", agent="DB_CLIENT", level="ERROR", no_db=True)
            r.raise_for_status()
            data = r.json()
            return DBResult(data)
        except Exception as e:
            # Use a simpler logger call without extra dependencies
            debugger.add_log(f"DB API Exception: {e} | SQL: {sql[:100]}...", agent="DB_CLIENT", level="ERROR", no_db=True)
            raise

    def close(self):
        pass
