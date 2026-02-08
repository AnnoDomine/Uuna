import { ENavigationItems } from "./navigation.enums.js";
import type { NavigationItemList } from "./navigation.types.js";

export const NAVIGATION_ITEMS: NavigationItemList = [
    { label: "Overview", value: ENavigationItems.HOME, icon: "🏠" },
    { label: "Tasks", value: ENavigationItems.TASKS, icon: "📋" },
    { label: "Vector Memory", value: ENavigationItems.MEMORY, icon: "🧠" },
    { label: "Scoring Board", value: ENavigationItems.SCORING, icon: "⚖️" },
    { label: "Settings", value: ENavigationItems.SETTINGS, icon: "⚙️" },
    { label: "Wiki", value: ENavigationItems.WIKI, icon: "📖" },
    { label: "Help", value: ENavigationItems.HELP, icon: "❓" },
];
