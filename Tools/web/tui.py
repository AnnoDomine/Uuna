import os
import sys
import datetime
import subprocess
import asyncio
import atexit
import signal
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer, Static, Label
from textual.binding import Binding

# Fix path for modular imports
sys.path.append(os.getcwd())

# Atomic components
from Tools.web.tui.organisms.sidebar import Sidebar
from Tools.web.tui.organisms.status_bar import StatusBar
from Tools.web.tui.organisms.log_area import LogArea

# Utils (Mixin)
from Tools.web.tui.utils.backend_manager import BackendMixin
from Tools.web.tui.utils.navigation import NavigationMixin

DEBUG = str(os.getenv("AI_DEBUG", "False")).lower() in ("true", "1", "t")
API_URL = "http://127.0.0.1:8001"

class WoWDBTUI(App, BackendMixin, NavigationMixin):
    """A modularized Terminal UI for the WoW Datamine Toolkit."""
    
    TITLE = "WoW Datamine Toolkit - Grand Library"
    SUB_TITLE = "Multi-Agent Orchestration & Vector Memory"
    CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tui/styles/main.tcss")
    
    backend_process = None

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("r", "refresh", "Refresh Data"),
        Binding("s", "screenshot", "Save Screenshot"),
    ]

    def action_screenshot(self) -> None:
        path = f"Data/screenshots/tui_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
        self.save_screenshot(path)
        if hasattr(self, "log_view") and self.log_view:
            self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Screenshot saved: {path}")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="app-body"):
            yield Sidebar(id="sidebar")
            with Vertical(id="main-content"):
                yield Label("System Dashboard", id="view-title")
                with Vertical(id="content-area"):
                    yield Static("Welcome back. Overview of agents and current mining status.")
                yield StatusBar(id="status-bar")
            yield LogArea(api_url=API_URL, id="log-area", disabled=not DEBUG)
        yield Footer()

    def on_mount(self) -> None:
        self.api_url = API_URL
        self.log_view = self.query_one("#log-view")
        self.log_view.write_line(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TUI Initialized.")
        
        self.run_worker(self.ensure_backend())
        self.set_interval(5, self.update_status)
        self.set_interval(2, self.refresh_tui_logs)

    async def refresh_tui_logs(self) -> None:
        log_area = self.query_one("LogArea")
        if not log_area.disabled:
            await log_area.refresh_logs()

    def on_unmount(self) -> None:
        self.terminate_backend()

if __name__ == "__main__":
    app = WoWDBTUI()
    app.run()