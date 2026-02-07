from textual.app import ComposeResult
from textual.widgets import Label, ListView
from textual.containers import Vertical
from ..molecules.nav_item import NavItem

class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("Navigation", classes="section-title")
        with ListView(id="nav-list"):
            yield NavItem("🏠 Overview", id="nav-home")
            yield NavItem("📋 Tasks", id="nav-tasks")
            yield NavItem("🧠 Vector Memory", id="nav-memory")
            yield NavItem("⚖️ Scoring Board", id="nav-scoring")
            yield NavItem("⚙️ Settings", id="nav-settings")
