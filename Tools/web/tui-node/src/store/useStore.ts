import { create } from "zustand";
import { ENavigationItems } from "../molecules/Navigation/navigation.enums.js";
import type { BasicFunction } from "../types/global.types.js";

interface AppState {
    currentPage: ENavigationItems;
    apiOnline: boolean;
    activeAgents: number;
    currentBuild: string;
    isRestarting: boolean;
}

interface AppActions {
    setCurrentPage: BasicFunction<[ENavigationItems]>;
    setApiOnline: BasicFunction<[boolean]>;
    setAgents: BasicFunction<[number]>;
    setRestarting: BasicFunction<[boolean]>;
}

export const useStore = create<AppState & AppActions>((set) => ({
    currentPage: ENavigationItems.HOME,
    apiOnline: false,
    activeAgents: 0,
    currentBuild: "Midnight 12.0.0",
    isRestarting: false,
    setCurrentPage: (page) => set({ currentPage: page }),
    setApiOnline: (status) => set({ apiOnline: status }),
    setAgents: (count) => set({ activeAgents: count }),
    setRestarting: (status) => set({ isRestarting: status }),
}));
