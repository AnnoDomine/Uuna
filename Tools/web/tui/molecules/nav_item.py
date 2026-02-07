from textual.widgets import ListItem, Label

class NavItem(ListItem):
    def __init__(self, label: str, id: str):
        super().__init__(Label(label), id=id)
