import axios from "axios";
import { useCallback, useEffect, useState } from "react";
import { useImmer } from "use-immer";
import useBackend from "../../hooks/useBackend.js";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import useDebugStore from "../../store/useDebugStore.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import { useStore } from "../../store/useStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { API_BASE_URL } from "../../utils/constants/globals.js";
import type { ISetting, ISettingsResponse } from "./settings.types.js";

const useSettings = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [settings, updateSettings] = useImmer<ISetting[]>([]);
    const { addLog } = useDebugStore();

    const { restartBackend } = useBackend();
    const { isRestarting } = useStore();

    const fetchSettings = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        addLog({
            type: ELogTypes.DEBUG,
            message: "Fetching settings from API",
            process: "useSettings",
        });
        try {
            const response = await axios.get<ISettingsResponse>(`${API_BASE_URL}/settings/list`);
            updateSettings(() => response.data.settings);
            addLog({
                type: ELogTypes.INFO,
                message: `Loaded ${response.data.settings.length} settings`,
                process: "useSettings",
            });
        } catch (_err) {
            setError("Failed to fetch settings from API.");
            addLog({
                type: ELogTypes.ERROR,
                message: "Failed to fetch settings",
                process: "useSettings",
            });
        } finally {
            setIsLoading(false);
        }
    }, [updateSettings, addLog]);

    const handleUpdateSetting = async (key: string, newValue: string) => {
        addLog({
            type: ELogTypes.INFO,
            message: `Updating setting: ${key}`,
            process: "useSettings",
        });
        try {
            await axios.post(`${API_BASE_URL}/settings/update`, {
                key,
                value: newValue,
            });
            updateSettings((draft) => {
                const setting = draft.find((s) => s.key === key);
                if (setting) {
                    setting.value = newValue;
                }
            });
            addLog({
                type: ELogTypes.INFO,
                message: `Successfully updated setting: ${key}`,
                process: "useSettings",
            });
        } catch (_err) {
            setError(`Failed to update setting: ${key}`);
            addLog({
                type: ELogTypes.ERROR,
                message: `Failed to update setting: ${key}`,
                process: "useSettings",
            });
        }
    };

    // RESTART BACKEND: Scoped Focus + Return logic
    const { isFocused: isRestartFocused } = useScopedInput({
        id: "btn-restart-backend",
        areal: EFocusAreal.CONTENT,
        keyMap: (_input, key) => {
            if (key.return) {
                restartBackend();
            }
        },
    });

    // RELOAD: Scoped Focus + Return logic
    const { isFocused: isReloadFocused } = useScopedInput({
        id: "btn-reload-settings",
        areal: EFocusAreal.CONTENT,
        keyMap: (_input, key) => {
            if (key.return) {
                fetchSettings();
            }
        },
    });

    useEffect(() => {
        fetchSettings();
    }, [fetchSettings]);

    return {
        settings,
        isLoading,
        error,
        fetchSettings,
        handleUpdateSetting,
        isRestarting,
        restartBackend,
        isRestartFocused,
        isReloadFocused,
    };
};

export default useSettings;
