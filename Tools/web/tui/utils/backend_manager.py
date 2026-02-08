import os
import datetime
import requests
import subprocess
import asyncio
import atexit
import signal
from loguru import logger

API_URL = "http://127.0.0.1:8001"

class BackendMixin:
    """Provides backend management logic to the TUI App."""
    backend_process = None

    async def ensure_backend(self) -> None:
        """Ensures the backend is running, starting it if necessary."""
        try:
            r = requests.get(f"{API_URL}/health", timeout=1)
            if r.status_code == 200:
                self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Backend online.")
                self.update_status()
                return
        except:
            pass

        self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] WARNING: Backend not ready, starting...")
        
        env = os.environ.copy()
        # Ensure AI_DEBUG is passed correctly as string
        env["AI_DEBUG"] = "1" if str(os.getenv("AI_DEBUG", "0")) == "1" else "0"

        self.backend_process = subprocess.Popen(
            ['.venv/bin/python3', '-u', '-m', 'uvicorn', 'Tools.core.api.main:app', '--host', '127.0.0.1', '--port', '8001'],
            stdout=open('Data/logs/api_out.log', 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=env
        )
        atexit.register(self.terminate_backend)

        for i in range(1, 11):
            self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Backend Try {i}/10...")
            await asyncio.sleep(2)
            try:
                r = requests.get(f"{API_URL}/health", timeout=1)
                if r.status_code == 200:
                    self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Backend started.")
                    self.update_status()
                    return
            except:
                pass
        
        self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ERROR: Backend start failed.")

    def update_status(self) -> None:
        """Updates the status bar with API health and build stats."""
        try:
            r = requests.get(f"{API_URL}/health", timeout=2)
            api_online = r.status_code == 200
        except:
            api_online = False

        status_label = self.query_one("#api-status-label")
        api_text = "Online" if api_online else "Offline"
        
        # Real stats integration can happen here later
        self.query_one("#build-status-label").update("Builds: 1156 | Downloaded: 1025 | Indexed: 520")
        status_label.update(f"API: {api_text} | Agents: 0 Active")

    def terminate_backend(self) -> None:
        """Gracefully kills the backend process group."""
        if self.backend_process:
            try:
                os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
            except:
                self.backend_process.terminate()
            self.backend_process = None
