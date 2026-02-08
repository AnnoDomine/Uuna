import { useCallback, useState } from "react";
import { useStore } from "../../store/useStore.js";
import { NAVIGATION_ITEMS } from "./navigation.constants.js";
import { ENavigationItems } from "./navigation.enums.js";
import { handleSelectItemHelper } from "./navigation.helpers.js";

const useNavigation = () => {
    const { currentPage, setCurrentPage } = useStore();
    const [highlitedItem, setHighlitedItem] = useState<ENavigationItems>(ENavigationItems.HOME);

    const highlitedItems = NAVIGATION_ITEMS.map((i) =>
        i.value === highlitedItem ? { ...i, label: `${i.icon} - ${i.label}` } : i,
    );

    /**
     * Handler to select an item
     *
     * If the item is "quit", call the quit-application helper function.
     *
     * @memoriced
     *
     * @param {ENavigationItems} value - Selected navigation item
     */
    const handleSelectItem = useCallback(
        (value: ENavigationItems) => handleSelectItemHelper(currentPage, setCurrentPage, value),
        [currentPage, setCurrentPage],
    );

    return {
        highlitedItems,
        highlitedItem,
        setHighlitedItem,
        handleSelectItem,
    };
};

export default useNavigation;
