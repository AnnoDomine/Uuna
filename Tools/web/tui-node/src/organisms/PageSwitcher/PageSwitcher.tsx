import { Text } from "ink";
import type { FC } from "react";
import { ENavigationItems } from "../../molecules/Navigation/navigation.enums.js";
import Help from "../../pages/Help/Help.js";

// Page Imports
import Home from "../../pages/Home/Home.js";
import Memory from "../../pages/Memory/Memory.js";
import Settings from "../../pages/Settings/Settings.js";
import Tasks from "../../pages/Tasks/Tasks.js";
import WikiPage from "../../pages/Wiki/WikiPage.js";
import { usePageSwitcher } from "./page_switcher.hooks.js";

const PageSwitcher: FC = () => {
    const { currentPage } = usePageSwitcher();

    switch (currentPage) {
        case ENavigationItems.HOME:
            return <Home />;
        case ENavigationItems.SETTINGS:
            return <Settings />;
        case ENavigationItems.WIKI:
            return <WikiPage />;
        case ENavigationItems.HELP:
            return <Help />;
        case ENavigationItems.TASKS:
            return <Tasks />;
        case ENavigationItems.MEMORY:
            return <Memory />;
        case ENavigationItems.SCORING:
            return <Text>Scoring Board Page [Placeholder]</Text>;
        default:
            return <Home />;
    }
};

export default PageSwitcher;
