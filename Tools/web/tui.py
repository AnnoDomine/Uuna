import os
import sys
import datetime
import requests
import subprocess
import asyncio
import atexit
import signal

# Fix path for modular imports
sys.path.append(os.getcwd())

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Label, Log
from textual.binding import Binding

# Atomic components
from Tools.web.tui.organisms.sidebar import Sidebar
from Tools.web.tui.organisms.status_bar import StatusBar

DEBUG = str(os.getenv("AI_DEBUG", "False")).lower() in ("true", "1", "t")
API_URL = "http://127.0.0.1:8001"

class WoWDBTUI(App):
    """A modularized Terminal UI for the WoW Datamine Toolkit."""
    
    TITLE = "WoW Datamine Toolkit - Grand Library"
    SUB_TITLE = "Multi-Agent Orchestration & Vector Memory"
    CSS_PATH = "tui/styles/main.tcss"
    
    backend_process = None

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("r", "refresh", "Refresh Data"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            yield Sidebar(id="sidebar")
            
            with Vertical(id="main-content"):
                yield Label("System Dashboard", id="view-title", classes="section-title")
                yield Static(
                    "Welcome to the Grand Library. Agents are currently idle. Ready for new research assignments.",
                    id="content-area"
                )
                with Horizontal():                    
                    with Vertical(id="interface-area"):
                        yield Label("The librarian waiting for your request", classes="section-title")
                    with Vertical(id="log-area", disabled=not DEBUG):
                        yield Label("\nReal-time Observation Log", classes="section-title")
                        yield Log(id="log-view")
        
        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.log_view = self.query_one("#log-view")
        self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TUI Initialized.")
        self.run_worker(self.ensure_backend())
        self.set_interval(5, self.update_status)

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
        
        self.backend_process = subprocess.Popen(
            ['.venv/bin/python3', '-u', '-m', 'uvicorn', 'Tools.core.api.main:app', '--host', '127.0.0.1', '--port', '8001'],
            stdout=open('Data/logs/api_out.log', 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=env
        )
        # Safety net: Ensure process is killed on exit
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

    def terminate_backend(self) -> None:
        """Kills the backend process if it was started by the TUI."""
        if self.backend_process:
            try:
                # Since start_new_session=True was used, we need to kill the process group
                os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
            except:
                self.backend_process.terminate()
            self.backend_process = None

    def on_unmount(self) -> None:
        self.terminate_backend()

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

    def on_list_view_selected(self, event) -> None:
        # Simple navigation logic
        if event.item.id == "nav-home":
            self.query_one("#view-title").update("System Dashboard")
        elif event.item.id == "nav-tasks":
            self.query_one("#view-title").update("Research Tasks")

if __name__ == "__main__":
    app = WoWDBTUI()
    app.run()
