from textual.app import ComposeResult
from textual.widgets import Label, Log
from textual.containers import Vertical
import requests

class LogArea(Vertical):
    def __init__(self, api_url: str, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url
        self.last_log_count = 0

    def compose(self) -> ComposeResult:
        yield Label("Real-time Observation Log", classes="section-title")
        yield Log(id="log-view")

    async def refresh_logs(self) -> None:
        try:
            # Note: In a real app, use a more efficient way to get only NEW logs
            r = requests.get(f"{self.api_url}/logs/latest?limit=50", timeout=1)
            if r.status_code == 200:
                logs = r.json().get("logs", [])
                log_view = self.query_one("#log-view")
                
                # Simple logic: if count changed, clear and redraw (or append new ones)
                # For now, let's just show the latest messages if they are different
                if logs:
                    # Clear and rewrite to simulate a "live table" feel
                    log_view.clear()
                    for entry in reversed(logs): # Show oldest first in the log view
                        msg = f"[{entry['timestamp']} - {entry['role']}]: {entry['message']}"
                        log_view.write_line(msg)
        except:
            pass
