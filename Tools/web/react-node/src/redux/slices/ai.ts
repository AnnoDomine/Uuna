import { createSlice, type PayloadAction } from "@reduxjs/toolkit/react";
import type { AIChatItem, FrontendSignal } from "../types/ai.types";

export type ChatType = "research" | "response" | "error" | "idle" | "request";

const aiSlice = createSlice({
    name: "ai",
    initialState: {
        chat: [] as Array<AIChatItem>,
        currentAgent: "user",
        currentLevel: "info",
        currentType: "idle" as ChatType,
    },
    reducers: {
        addMessage: (state, action: PayloadAction<AIChatItem>) => {
            state.currentAgent = action.payload.agent;
            state.currentLevel = action.payload.level;
            state.currentType = "request";
            state.chat.push(action.payload);
        },
        receiveUpdate: (state, action: PayloadAction<FrontendSignal>) => {
            console.table(action.payload);
            const aiChat: AIChatItem = {
                agent: action.payload.agent,
                message: action.payload.message,
                timestamp: Date.now(),
                level: action.payload.level,
                type: action.payload.type,
            };
            state.currentAgent = action.payload.type === "response" ? "system" : aiChat.agent;
            state.currentLevel = aiChat.level;
            state.currentType = action.payload.type === "response" ? "idle" : action.payload.type;
            state.chat.push(aiChat);
        },
    },
    selectors: {
        getChat: (state) => state.chat,
        getCurrentAgent: (state) => state.currentAgent,
        getCurrentLevel: (state) => state.currentLevel,
        getCurrentType: (state) => state.currentType,
    },
});

export const { addMessage, receiveUpdate } = aiSlice.actions;
export const { getChat, getCurrentAgent, getCurrentLevel, getCurrentType } = aiSlice.selectors;
export default aiSlice;
