import requests
import pandas as pd

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
        
        # Determine endpoint
        is_query = any(keyword in sql.upper() for keyword in ["SELECT", "PRAGMA", "SHOW", "DESCRIBE"])
        endpoint = "/query" if is_query else "/execute"
        
        try:
            r = requests.post(f"{self.url}{endpoint}", json={"sql": sql, "params": params}, timeout=600)
            r.raise_for_status()
            data = r.json()
            return DBResult(data)
        except Exception as e:
            # Use a simpler logger call without extra dependencies
            print(f"DB API Error: {e} | SQL: {sql[:100]}...")
            raise

    def close(self):
        pass
