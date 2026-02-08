import type { IKeybinding } from "./help.types.js";

export const KEYBINDINGS_DATA: IKeybinding[] = [
    { key: "q", action: "Quit Application", scope: "Global" },
    { key: "Ctrl + L", action: "Toggle Debug Console", scope: "Global" },
    { key: "Tab", action: "Next Focus Element", scope: "Global" },
    { key: "Shift + Tab", action: "Previous Focus Element", scope: "Global" },
    { key: "↑ / ↓", action: "Move Cursor Up/Down", scope: "Scrolling" },
    { key: "PageUp / PageDown", action: "Scroll Page Up/Down", scope: "Scrolling" },
    { key: "Home / End", action: "Jump to Top/Bottom", scope: "Scrolling" },
    { key: "Enter", action: "Select Item / Save Action", scope: "Selection" },
];
