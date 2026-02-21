import fsPromises from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { v4 as uuidv4 } from "uuid";
import { create } from "zustand";
import { ELogTypes } from "../types/global.enums.js";
import { EActors, type LogChatItem } from "./useAIStore.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const chatLogPath = path.join(__dirname, "log.json");

type LogEntry = {
    timestamp: number;
    message: string;
    type: ELogTypes;
    process?: string;
};

// Global lock for file operations
let isFileOperating = false;

const getChatLog = async (): Promise<LogChatItem[]> => {
    try {
        // Ensure file exists with empty array if missing
        try {
            await fsPromises.access(chatLogPath);
        } catch {
            await fsPromises.writeFile(chatLogPath, "[]");
        }

        const data = await fsPromises.readFile(chatLogPath, "utf-8");
        if (!data || data.trim() === "") {
            return [];
        }

        const parsedData = JSON.parse(data);
        return Array.isArray(parsedData) ? parsedData : [];
    } catch (err) {
        // Silently recover for tests, but log error
        if (process.env.NODE_ENV !== "test") {
            console.error("Error reading chat log:", err);
        }
        return [];
    }
};

const writeChatLog = async (data: LogChatItem[]) => {
    if (isFileOperating) return;
    isFileOperating = true;
    try {
        await fsPromises.writeFile(chatLogPath, JSON.stringify(data, null, 2));
    } catch (err) {
        console.error("Error writing chat log:", err);
    } finally {
        isFileOperating = false;
    }
};

type DebbugState = {
    log: Array<LogEntry>;
    addLog: (log: Omit<LogEntry, "timestamp">) => Promise<void>;
    enabled: boolean;
    setEnabled: (enabled: boolean) => void;
};

const getActor = (actor = "") => {
    switch (actor.toLowerCase()) {
        case "user":
            return EActors.USER;
        case "ki":
        case "ai":
        case "librarian":
            return EActors.LIBRARIAN;
        default:
            return EActors.SYSTEM;
    }
};

const addLogEntryToFile = async (log: Omit<LogEntry, "timestamp">): Promise<void> => {
    const newEntry: LogChatItem = {
        ...log,
        timestamp: Date.now(),
        actor: getActor(log.process),
        id: uuidv4(),
    };

    const oldLogs = await getChatLog();
    const newCombinedFileLogs: LogChatItem[] = [...oldLogs, newEntry].slice(-100); // Keep last 100
    await writeChatLog(newCombinedFileLogs);
};

const logQueue: Array<{
    log: LogEntry;
    fn: (log: LogEntry) => Promise<void>;
}> = [];
let isQueueRunning = false;

const runNextQueuedItem = async () => {
    if (logQueue.length === 0) {
        isQueueRunning = false;
        return;
    }

    isQueueRunning = true;
    const item = logQueue.shift();
    if (item) {
        try {
            await item.fn(item.log);
        } catch (err) {
            console.error(err);
        }
    }

    // Process next in next tick to avoid stack overflow
    setImmediate(runNextQueuedItem);
};

const logging = async (log: LogEntry, fn: (log: LogEntry) => Promise<void>) => {
    logQueue.push({ log, fn });
    if (!isQueueRunning) {
        runNextQueuedItem();
    }
};

const useDebugStore = create<DebbugState>((set, get) => ({
    log: [],
    enabled: false,
    addLog: async (log) => {
        const isDebugMode = process.env.AI_DEBUG === "true" || process.env.NODE_ENV === "test";
        const state = get();
        const newEntry: LogEntry = {
            ...log,
            timestamp: Date.now(),
        };

        const newLog = [...state.log, newEntry].slice(-50);
        if (!isDebugMode && log.type === ELogTypes.DEBUG) return;

        set({ log: newLog });

        // Skip file logging in tests to avoid IO issues
        if (process.env.NODE_ENV !== "test") {
            try {
                logging(newEntry, addLogEntryToFile);
            } catch (err) {
                console.error(err);
            }
        }
    },
    setEnabled: (enabled) => set({ enabled }),
}));

export default useDebugStore;
