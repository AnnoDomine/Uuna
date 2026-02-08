import type { ENavigationItems } from "./navigation.enums.js";

export type NavigationItem = {
    /**
     * Label of the navigation item
     */
    label: string;
    /**
     * Value enum
     */
    value: ENavigationItems;
    /**
     * Icon of the navigation item.
     * Is used for highlighting
     */
    icon: string;
};

export type NavigationItemList = Array<NavigationItem>;
