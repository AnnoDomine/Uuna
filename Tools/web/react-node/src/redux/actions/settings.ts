import { createAsyncThunk } from "@reduxjs/toolkit/react";
import { SETTINGS_STORE_SETTTINGSFALLBACK } from "../constants/settings";
import type { SettingsObj } from "../types/settings.types";

export const fetchSettingsJson = createAsyncThunk("settings/fetchSettingsJson", async () => {
    try {
        const settings = (await window.electronAPI.getSettings()) as SettingsObj;
        return settings;
    } catch (e) {
        console.error("Error fetching settings:", e);
        return SETTINGS_STORE_SETTTINGSFALLBACK;
    }
});
