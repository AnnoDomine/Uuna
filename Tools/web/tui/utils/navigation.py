from textual.widgets import ListView, Static
from ..pages.settings import SettingsPage

class NavigationMixin:
    """Provides navigation logic for the TUI App."""
    
    ITEM_ID_HOME = "nav-home"
    ITEM_ID_TASKS = "nav-tasks"
    ITEM_ID_VECTORS = "nav-memory"
    ITEM_ID_SCORING = "nav-scoring"
    ITEM_ID_SETTINGS = "nav-settings"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handles sidebar selection. 'self' is the App instance."""
        # Only react to the navigation sidebar
        if event.list_view.id != "nav-list":
            return

        view_title = self.query_one("#view-title")
        content_container = self.query_one("#content-area")
        
        # Clear existing content ONLY if we are actually switching a page
        for child in list(content_container.children):
            child.remove()

        if event.item.id == self.ITEM_ID_HOME:
            view_title.update("System Dashboard")
            content_container.mount(Static("Welcome back. Overview of agents and current mining status."))
            
        elif event.item.id == self.ITEM_ID_SETTINGS:
            view_title.update("Settings")
            content_container.mount(SettingsPage(api_url=self.api_url))
        
        elif event.item.id == self.ITEM_ID_TASKS:
            view_title.update("Research Tasks")
            content_container.mount(Static("Task Management coming soon..."))

        elif event.item.id == self.ITEM_ID_VECTORS:
            view_title.update("Vector Memory")
            content_container.mount(Static("Vector Search coming soon..."))

        elif event.item.id == self.ITEM_ID_SCORING:
            view_title.update("Scoring Board")
            content_container.mount(Static("Scoring Board coming soon..."))