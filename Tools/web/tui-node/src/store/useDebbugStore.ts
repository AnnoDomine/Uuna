import { create } from "zustand";
import { ELogTypes } from "../types/global.enums.js";

type LogEntry = {
    timestamp: number;
    message: string;
    type: ELogTypes;
    process?: string;
};

type DebbugState = {
    log: Array<LogEntry>;
    addLog: (log: Omit<LogEntry, "timestamp">) => void;
    enabled: boolean;
    setEnabled: (enabled: boolean) => void;
};

const addLog = (log: Omit<LogEntry, "timestamp">) => (state: DebbugState) => {
    const isDebugMode = process.env.AI_DEBUG === "true";
    if (!isDebugMode && log.type !== ELogTypes.DEBUG) return state;
    return {
        log: [...state.log, { ...log, timestamp: Date.now() }],
    };
};

const useDebugStore = create<DebbugState>((set) => ({
    log: [],
    enabled: false,
    addLog: (log) => set(addLog(log)),
    setEnabled: (enabled) => set({ enabled }),
}));

export default useDebugStore;
