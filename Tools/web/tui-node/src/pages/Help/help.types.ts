export enum EHelpTopic {
    KEYBINDINGS = "keybindings",
    AGENT_ROLES = "agent_roles",
    ARCHITECTURE = "architecture",
}

export interface IKeybinding {
    key: string;
    action: string;
    scope: "Global" | "Scrolling" | "Selection" | "System";
}
