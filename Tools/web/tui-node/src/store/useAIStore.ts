import fsPromises from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import { create } from "zustand";
import { API_BASE_URL } from "../utils/constants/globals.js";
import { parseAnswerToString } from "./utils.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const chatLogPath = path.join(__dirname, "chatlog.json");

export enum EActors {
    SYSTEM = "system",
    USER = "user",
    LIBRARIAN = "librarian",
    AGENT = "agent",
}

export type LogChatItem = {
    actor: EActors;
    agent?: string;
    message: string;
    timestamp: number;
    id: string;
};

const inititalMessage: LogChatItem = {
    actor: EActors.SYSTEM,
    message: `Initialising new thread - ${new Date(Date.now()).toLocaleString()}`,
    timestamp: Date.now(),
    id: uuidv4(),
};

type AIAnswer = { [key: string]: string | number | AIAnswer };

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
        // Add initial message
        parsedData.push(inititalMessage);
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

export type FrontendSignal = {
    task_id: string;
    agent: string;
    message: string;
    type: "research" | "response" | "error";
    level: string;
    task_context?: object;
};

type AIStore = {
    isUninitialised: boolean;
    isLoading: boolean;
    isFetching: boolean;
    isSucceeded: boolean;
    isErrored: boolean;
    error: string | null;
    chat: LogChatItem[];
    addChat: (newMessage: string) => void;
    receiveSignal: (signal: FrontendSignal) => void;
    initialiseChat: () => Promise<void>;
};

const useAIStore = create<AIStore>((set, get) => ({
    isUninitialised: true,
    isLoading: false,
    isFetching: false,
    isSucceeded: false,
    isErrored: false,
    error: null,
    chat: [],
    receiveSignal: (signal) => {
        const storeState = new Set(get().chat);

        // Map the signal type to the internal state
        if (signal.type === "error") {
            set(() => ({ isErrored: true, isFetching: false, error: signal.message }));
        } else if (signal.type === "research") {
            set(() => ({ isFetching: true, isErrored: false }));
        } else if (signal.type === "response") {
            set(() => ({ isFetching: false, isSucceeded: true, isErrored: false }));
        }

        const signalMessage: LogChatItem = {
            actor:
                signal.type === "response"
                    ? EActors.LIBRARIAN
                    : signal.type === "error"
                      ? EActors.SYSTEM
                      : EActors.AGENT,
            agent: signal.agent,
            message: signal.message,
            timestamp: Date.now(),
            id: uuidv4(),
        };

        storeState.add(signalMessage);
        const sortedChat = [...storeState].sort((a, b) => a.timestamp - b.timestamp);

        set(() => ({
            chat: sortedChat,
        }));

        writeChatLog(sortedChat);
    },
    addChat: async (newMessage) => {
        const storeState = new Set(get().chat);
        // Reset loading states
        set(() => ({
            isErrored: false,
            isSucceeded: false,
            isFetching: true,
            error: null,
        }));

        try {
            const userMessage: LogChatItem = {
                message: newMessage,
                timestamp: Date.now(),
                id: uuidv4(),
                actor: EActors.USER,
            };
            storeState.add(userMessage);
            set(() => ({
                chat: [...storeState].sort((a, b) => a.timestamp - b.timestamp),
            }));
            const { data } = await axios.post<AIAnswer>(
                `${API_BASE_URL}/ai/ask`,
                {
                    prompt: userMessage.message,
                },
                /**
                 * Timeout -> 10 min
                 */
                { timeout: 1000 * 60 * 10 },
            );
            console.log(data);
            if (!parseAnswerToString(data)) {
                throw new Error("No response from AI");
            }
            const aiMessage: LogChatItem = {
                actor: EActors.LIBRARIAN,
                message: parseAnswerToString(data),
                timestamp: Date.now(),
                id: uuidv4(),
            };
            storeState.add(aiMessage);
            set(() => ({
                chat: [...storeState].sort((a, b) => a.timestamp - b.timestamp),
            }));
            await writeChatLog([...storeState].sort((a, b) => a.timestamp - b.timestamp));
            set(() => ({
                isSucceeded: true,
            }));
        } catch (err) {
            console.error(err);
            set(() => ({
                error: String(err),
                isErrored: true,
            }));
        } finally {
            set(() => ({
                isFetching: false,
            }));
        }
    },
    initialiseChat: async () => {
        try {
            set(() => ({
                isLoading: true,
            }));
            const res = await getChatLog();
            set(() => ({
                chat: res,
            }));
        } catch (err) {
            console.error(err);
            set(() => ({
                error: String(err),
                isErrored: true,
            }));
        } finally {
            set(() => ({
                isUninitialised: false,
                isLoading: false,
            }));
        }
    },
}));

useAIStore.getState().initialiseChat();

export default useAIStore;
