import type { ControlledScrollViewRef } from "ink-scroll-view";
import { useCallback, useEffect, useRef } from "react";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import useScrollStore from "../../store/useScrollStore.js";

const useScrollArea = (id: string) => {
    const { scrollOffset, setScrollOffset, setScrollRef } = useScrollStore();
    const scrollRef = useRef<ControlledScrollViewRef>(null);

    const scrollToItem = useCallback(
        (index: number) => {
            const scroll = scrollRef.current;
            if (!scroll) return;

            const position = scroll.getItemPosition(index);
            if (!position) return;

            const viewportHeight = scroll.getViewportHeight();
            if (viewportHeight === 0) return;

            let newOffset = scrollOffset;
            if (position.top < scrollOffset) {
                newOffset = position.top;
            } else if (position.top + position.height > scrollOffset + viewportHeight) {
                newOffset = position.top + position.height - viewportHeight;
            }

            if (newOffset !== scrollOffset) {
                setScrollOffset(newOffset);
            }
        },
        [scrollOffset, setScrollOffset],
    );

    // Provide manual scrolling via Scoped Input
    const { isFocused } = useScopedInput({
        id,
        areal: EFocusAreal.CONTENT,
        keyMap: (_input, key) => {
            if (key.upArrow) setScrollOffset(Math.max(0, scrollOffset - 1));
            if (key.downArrow) {
                const max = scrollRef.current?.getBottomOffset() || 0;
                setScrollOffset(Math.min(max, scrollOffset + 1));
            }
            if (key.pageUp) {
                const height = scrollRef.current?.getViewportHeight() || 1;
                setScrollOffset(Math.max(0, scrollOffset - height));
            }
            if (key.pageDown) {
                const height = scrollRef.current?.getViewportHeight() || 1;
                setScrollOffset(
                    Math.min(scrollRef.current?.getBottomOffset() || 0, scrollOffset + height),
                );
            }
        },
    });

    useEffect(() => {
        setScrollRef(scrollRef.current);
        return () => setScrollRef(null);
    }, [setScrollRef]);

    return {
        scrollRef,
        scrollOffset,
        scrollToItem,
        isFocused,
    };
};

export default useScrollArea;
