import { create } from "zustand";

export enum EFocusAreal {
    NAVIGATION = "navigation",
    CONTENT = "content",
    LOGS = "logs",
}

interface FocusState {
    activeAreal: EFocusAreal;
    setActiveAreal: (areal: EFocusAreal) => void;
}

export const useFocusStore = create<FocusState>((set) => ({
    activeAreal: EFocusAreal.NAVIGATION,
    setActiveAreal: (areal) => set({ activeAreal: areal }),
}));
