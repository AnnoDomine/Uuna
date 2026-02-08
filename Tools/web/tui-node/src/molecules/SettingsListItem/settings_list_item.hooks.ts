import { useCallback } from "react";
import { useScrollAreaContext } from "../../organisms/ScrollArea/ScrollArea.js";

const useSettingsListItem = (idx: number) => {
    const { scrollToItem } = useScrollAreaContext();

    const handleFokusScroll = useCallback(() => {
        scrollToItem(idx);
    }, [idx, scrollToItem]);

    return { handleFokusScroll };
};

export default useSettingsListItem;
