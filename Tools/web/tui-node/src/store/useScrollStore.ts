import type { ControlledScrollViewRef } from "ink-scroll-view";
import { create } from "zustand";

type ScrollState = {
    scrollRef: ControlledScrollViewRef | null;
    setScrollRef: (scrollRef: ControlledScrollViewRef | null) => void;
    scrollOffset: number;
    setScrollOffset: (scrollOffset: number) => void;
};

const useScrollStore = create<ScrollState>((set) => ({
    scrollRef: null,
    setScrollRef: (scrollRef) => set({ scrollRef }),
    scrollOffset: 0,
    setScrollOffset: (scrollOffset) => set({ scrollOffset }),
}));

export default useScrollStore;
export type { ScrollState };
