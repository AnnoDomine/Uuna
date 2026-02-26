import { create } from "zustand";

export enum EFocusAreal {
    NAVIGATION = "navigation",
    CONTENT = "content",
    LOGS = "logs",
    COMMAND = "command",
}

interface FocusState {
    activeAreal: EFocusAreal;
    setActiveAreal: (areal: EFocusAreal) => void;
}

export const useFocusStore = create<FocusState>((set) => ({
    activeAreal: EFocusAreal.COMMAND,
    setActiveAreal: (areal) => set({ activeAreal: areal }),
}));
