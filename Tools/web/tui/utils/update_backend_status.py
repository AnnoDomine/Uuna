import requests

API_URL = "http://127.0.0.1:8001"


def update_status(self) -> None:
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        api_online = r.status_code == 200
    except:
        api_online = False

    status_label = self.query_one("#api-status-label")
    api_text = "Online" if api_online else "Offline"
    
    self.query_one("#build-status-label").update("Builds: 1156 | Downloaded: 1025 | Indexed: 520")
    status_label.update(f"API: {api_text} | Agents: 0 Active")