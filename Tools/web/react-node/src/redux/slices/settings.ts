import { createSlice, type PayloadAction } from "@reduxjs/toolkit/react";
import { fetchSettingsJson } from "../actions/settings";
import type {
    ChangeSettingActionPayload,
    ReduxSettingsStore,
    SettingsObj,
} from "../types/settings.types";

const SETTINGS_FALLBACK: SettingsObj = {
    ai: {
        num_thread: 10,
        num_ctx: 4096,
        num_gpu: 99,
        acceleration_mode: "gpu",
        memory_limit: 3,
    },
    ingestion: {
        workers: 8,
        threads: 4,
        limit_per_build: 1000,
        sync_builds_on_startup: true,
    },
    analysis: {
        use_global_mapping: false,
        auto_skip_unidentifiable: false,
    },
    system: {
        debug: true,
        localisation: "german",
        ui_theme: "dark",
        cooldown: 4.0,
    },
    tasks: {
        max_events_total: 80,
        max_tries_archivist: 6,
        max_tries_cartorapher: 3,
        max_tries_expedition_group: 5,
        max_tries_sentinel: 3,
    },
};

const initialValue: ReduxSettingsStore = {
    settings: SETTINGS_FALLBACK,
};

const settingsSlice = createSlice({
    reducerPath: "settings",
    initialState: initialValue,
    name: "settings",
    reducers: {
        changeSettings: (state, action: PayloadAction<ChangeSettingActionPayload>) => {
            const { setting, field, value } = action.payload;
            state.settings[setting][field] = value;
        },
        saveSettings: (state) => {
            window.electronAPI.writeSettings(JSON.stringify(state.settings, null, 2));
        },
    },
    extraReducers: (builder) => ({
        initializeSettings: builder.addCase(fetchSettingsJson.fulfilled, (state, action) => {
            state.settings = action.payload as SettingsObj;
        }),
    }),
    selectors: {
        getSettings: (state) => state.settings,
        getAiSettings: (state) => state.settings.ai,
        getIngestionSettings: (state) => state.settings.ingestion,
        getAnalysisSettings: (state) => state.settings.analysis,
        getSystemSettings: (state) => state.settings.system,
        getTasksSettings: (state) => state.settings.tasks,
    },
});

export const { changeSettings, saveSettings } = settingsSlice.actions;
export const {
    getSettings,
    getAiSettings,
    getIngestionSettings,
    getAnalysisSettings,
    getSystemSettings,
    getTasksSettings,
} = settingsSlice.selectors;
export default settingsSlice;
