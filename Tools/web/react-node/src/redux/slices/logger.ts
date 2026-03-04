import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

/**
 * Initial read log-file from "./logs/logs.log".
 */
const initialiseLog = async () => {
    try {
        const res = window.electronAPI.getLogs();
        return res;
    } catch (e) {
        console.error(e);
        return [];
    }
};

const writeLog = async (log: string) => {
    try {
        await window.electronAPI.writeLog(log);
    } catch (e) {
        console.error(e);
    }
};

const loggerSlice = createSlice({
    name: "logger",
    initialState: {
        logs: [] as string[],
    },
    reducers: {
        init: (state) => {
            initialiseLog().then((logs) => {
                state.logs = logs;
            });
        },
        log: (state, action: PayloadAction<string>) => {
            state.logs.push(action.payload);
            writeLog(action.payload);
        },
    },
});

export const { init, log } = loggerSlice.actions;
export default loggerSlice;
