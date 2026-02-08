import type { BasicFunction } from "../../types/global.types.js";
import quitApplication from "../../utils/helpers/quitApplication.js";
import { NAVIGATION_ITEMS } from "./navigation.constants.js";
import { ENavigationItems } from "./navigation.enums.js";
import type { NavigationItem } from "./navigation.types.js";

export const handleSelectItemHelper = (
    currentPage: ENavigationItems,
    setCurrentPage: BasicFunction<[ENavigationItems]>,
    value: ENavigationItems,
) => {
    // Skip if we are already on the selected page
    if (currentPage === value) {
        return;
    }
    // If the item is "quit" then exit the application
    if (value === ENavigationItems.QUIT) {
        quitApplication();
        return;
    }
    const selectedItem: NavigationItem | undefined = NAVIGATION_ITEMS.find(
        (i) => i.value === value,
    );
    if (!selectedItem) {
        return;
    }
    setCurrentPage(selectedItem.value);
};
