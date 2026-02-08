from textual.app import ComposeResult
from textual.widgets import Label, ListView
from textual.containers import Vertical
from ..molecules.nav_item import NavItem
from ..utils.navigation import NavigationMixin

class Sidebar(Vertical):
    """Sidebar organism. References IDs from NavigationMixin for consistency."""
    def compose(self) -> ComposeResult:
        yield Label("Navigation", classes="section-title")
        with ListView(id="nav-list"):
            yield NavItem("🏠 Overview", id=NavigationMixin.ITEM_ID_HOME)
            yield NavItem("📋 Tasks", id=NavigationMixin.ITEM_ID_TASKS)
            yield NavItem("🧠 Vector Memory", id=NavigationMixin.ITEM_ID_VECTORS)
            yield NavItem("⚖️ Scoring Board", id=NavigationMixin.ITEM_ID_SCORING)
            yield NavItem("⚙️ Settings", id=NavigationMixin.ITEM_ID_SETTINGS)