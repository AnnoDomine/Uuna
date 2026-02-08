import type { StatusBarItem } from "./statusBar.types.js";

export const DELIMITER_ITEM_DEFINITION: StatusBarItem = {
    label: "",
    value: "-",
    color: "",
    id: "delimiter",
};

const QUIT_KEY_ITEM_DEFINITION: StatusBarItem = {
    label: "Press to quit",
    value: "q",
    color: "red",
    id: "quit-key",
};

const BUILD_ITEM_DEFINITION = (build: string): StatusBarItem => ({
    label: "Build",
    value: build,
    color: "green",
    id: "build",
});

const API_HEALTH_ITEM_DEFINITION = (isAlive: boolean): StatusBarItem => ({
    label: "API Health",
    value: isAlive ? "Online" : "Offline",
    color: isAlive ? "green" : "red",
    id: "api-health",
});

const AGENTS_AMOUNT_ITEM_DEFINITION = (amount: number): StatusBarItem => ({
    label: "Agents",
    value: amount.toString(),
    color: "blue",
    id: "agents-amount",
});

export const STATUS_BAR_ITEMS = (
    build: string,
    isAlive: boolean,
    agentsAmount: number,
): Array<StatusBarItem> => [
    QUIT_KEY_ITEM_DEFINITION,
    DELIMITER_ITEM_DEFINITION,
    BUILD_ITEM_DEFINITION(build),
    DELIMITER_ITEM_DEFINITION,
    API_HEALTH_ITEM_DEFINITION(isAlive),
    DELIMITER_ITEM_DEFINITION,
    AGENTS_AMOUNT_ITEM_DEFINITION(agentsAmount),
];
