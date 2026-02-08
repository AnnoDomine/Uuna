from textual.app import ComposeResult
from textual.widgets import Label
from textual.containers import Horizontal

class StatusBar(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("Builds: Loading...", id="build-status-label")
        yield Label("API: Checking...", id="api-status-label")
