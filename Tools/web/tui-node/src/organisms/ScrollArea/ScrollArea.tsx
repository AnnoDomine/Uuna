import { Box } from "ink";
import { ControlledScrollView } from "ink-scroll-view";
import type { FC, PropsWithChildren } from "react";
import { createContext, useContext } from "react";
import useScrollArea from "./scroll_area.hooks.js";

interface ScrollAreaContextType {
    scrollToItem: (index: number) => void;
}

const ScrollAreaContext = createContext<ScrollAreaContextType | null>(null);

export const useScrollAreaContext = () => {
    const context = useContext(ScrollAreaContext);
    if (!context) {
        throw new Error("useScrollAreaContext must be used within a ScrollArea");
    }
    return context;
};

interface ScrollAreaProps {
    id: string;
}

const ScrollArea: FC<PropsWithChildren<ScrollAreaProps>> = ({ children, id }) => {
    const { scrollRef, scrollOffset, scrollToItem, isFocused } = useScrollArea(id);

    return (
        <ScrollAreaContext.Provider value={{ scrollToItem }}>
            <Box
                flexGrow={1}
                width="100%"
                minHeight={1}
                borderStyle="round"
                borderColor={isFocused ? "#7aa2f7" : "#24283b"}
            >
                <ControlledScrollView ref={scrollRef} scrollOffset={scrollOffset}>
                    {children}
                </ControlledScrollView>
            </Box>
        </ScrollAreaContext.Provider>
    );
};

export default ScrollArea;
