from textual.app import ComposeResult
from textual.widgets import Static, Input, Label, Button, ListView
from textual.containers import Vertical
import requests

from ..atoms.settings_list_item import SettingsListItem

class SettingsPage(Vertical):
    def __init__(self, api_url: str, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url

    def compose(self) -> ComposeResult:
        yield Label("AI & System Settings", classes="section-title")
        yield ListView(id="settings-list")
        yield Button("Reload Settings", id="reload-settings")

    async def on_mount(self) -> None:
        await self.load_settings()

    async def load_settings(self) -> None:
        try:
            r = requests.get(f"{self.api_url}/settings/list", timeout=2)
            if r.status_code == 200:
                settings = r.json().get("settings", [])
                list_view = self.query_one("#settings-list")
                list_view.clear()
                for s in settings:
                    list_view.append(SettingsListItem(s['key'], s['value'], s['description']))
        except Exception as e:
            self.app.log_view.write_line(f"Failed to load settings: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "reload-settings":
            await self.load_settings()
        elif event.button.id.startswith("btn-"):
            key = event.button.id.replace("btn-", "")
            # Find the input for this key
            input_widget = self.query_one(f"#input-{key}", Input)
            new_value = input_widget.value
            
            try:
                r = requests.post(f"{self.api_url}/settings/update", 
                                 json={"key": key, "value": new_value}, timeout=2)
                if r.status_code == 200:
                    self.app.log_view.write_line(f"Setting '{key}' updated successfully.")
                else:
                    self.app.log_view.write_line(f"Failed to update '{key}': {r.text}")
            except Exception as e:
                self.app.log_view.write_line(f"Update error: {e}")