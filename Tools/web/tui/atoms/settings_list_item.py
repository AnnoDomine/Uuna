from textual.widgets import (
    Static,
    Input,
    Label,
    Button,
    ListView,
    ListItem,
    SelectionList,
)
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual.binding import Binding
import os


class SettingsListItem(ListItem):
    def __init__(self, key: str, value: str, description: str):
        super().__init__()
        self.setting_key = key
        self.setting_value = value
        self.setting_description = description
        self.input_key = f"input-{self.setting_key}"
        self.button_key = f"btn-{self.setting_key}"

    # Use absolute path for safety
    CSS_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "styles/settings_list_item.tcss"
    )

    BINDINGS = [
        Binding("enter", "action_select_setting", "Select Setting", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal(id="settings-list-item-container"):
            with Horizontal(id="settings-list-item-label-container"):
                with Vertical(id="settings-list-item-labels"):
                    yield Label(f"[b]{self.setting_key}[/b]", id="key-label")
                    yield Label(self.setting_description, id="desc-label")
                with Vertical(id="settings-list-item-input-container"):
                    if self.setting_key == "ui_theme":
                        yield SelectionList[str](
                            [("Light", "light"), ("Dark", "dark")],
                            id=self.input_key,
                            classes="settings-list-item-input",
                        )
                    else:
                        yield Input(
                            value=str(self.setting_value),
                            id=self.input_key,
                            classes="settings-list-item-input",
                        )
            with Horizontal(id="settings-list-item-buttons"):
                yield Button(
                    "Save",
                    variant="primary",
                    id=f"btn-{self.setting_key}",
                    classes="settings-list-item-button",
                )

    def action_select_setting(self) -> None:
        """Called when Enter is pressed on the ListItem."""
        try:
            input_widget = self.query_one(".settings-list-item-input", Input)
            input_widget.focus()
        except:
            pass
