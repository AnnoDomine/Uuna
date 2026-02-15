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

/**
 * Reads the stored log-chat and returns an array from the messages.
 * @returns {Promise<LogChatItem[]>} - Chat log items as array
 */
const getChatLog = async (): Promise<LogChatItem[]> => {
    try {
        // Add initialising log message - Creates the file if not esxists
        await fsPromises.appendFile(chatLogPath, "");
        // Reads the file
        const data = await fsPromises.readFile(chatLogPath, "utf-8");
        // Parses the data into typed variable
        const parsedData: LogChatItem[] = JSON.parse(data) || [];
        // Save changes
        await fsPromises.writeFile(chatLogPath, JSON.stringify(parsedData));
        // Return data
        return parsedData;
    } catch (err) {
        console.error(err);
        return [];
    }
};

/**
 * Writes the chat log to the log file.
 * @param {LogChatItem[]} data - New chat log
 */
const writeChatLog = async (data: LogChatItem[]) => {
    try {
        await fsPromises.writeFile(chatLogPath, JSON.stringify(data));
    } catch (err) {
        console.error(err);
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

const addLog = async (log: Omit<LogEntry, "timestamp">): Promise<void> => {
    const newEntry: LogChatItem = {
        ...log,
        timestamp: Date.now(),
        actor: getActor(log.process),
        id: uuidv4(),
    };
    try {
        const oldLogs = await getChatLog();
        const newCombinedFileLogs: LogChatItem[] = [...oldLogs, newEntry];
        writeChatLog(newCombinedFileLogs);
    } catch (err) {
        console.error(err);
    }
};

const logQueue: Array<{
    log: LogEntry;
    fn: (log: LogEntry) => Promise<void>;
}> = [];
let isQueueRunning = false;

const runQueuedFn = async (log: LogEntry, fn: (log: LogEntry) => Promise<void>) => {
    isQueueRunning = true;
    try {
        await fn(log);
    } finally {
        isQueueRunning = false;
    }
};

const runNextQueuedItem = async () => {
    const item = logQueue.shift();
    if (!item) {
        return;
    }
    try {
        await runQueuedFn(item.log, item.fn);
    } catch (err) {
        console.error(err);
    } finally {
        await runNextQueuedItem();
    }
};

const logging = async (log: LogEntry, fn: (log: LogEntry) => Promise<void>) => {
    logQueue.push({ log, fn });
    if (isQueueRunning) {
        // No need to continue, if queue is running
        return;
    }
    try {
        await runNextQueuedItem();
    } catch (err) {
        console.error(err);
    }
};

const useDebugStore = create<DebbugState>((set, get) => ({
    log: [],
    enabled: false,
    addLog: async (log) => {
        const isDebugMode = process.env.AI_DEBUG === "true";
        const state = get();
        const newEntry: LogEntry = {
            ...log,
            timestamp: Date.now(),
        };
        const newLog = [...state.log, newEntry];
        if (!isDebugMode && log.type === ELogTypes.DEBUG) return;
        set({
            log: newLog,
        });
        try {
            logging(newEntry, addLog);
        } catch (err) {
            console.error(err);
        }
    },
    setEnabled: (enabled) => set({ enabled }),
}));

export default useDebugStore;
