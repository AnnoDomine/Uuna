import axios from "axios";
import { useInput } from "ink";
import type { ControlledScrollViewRef } from "ink-scroll-view";
import { useCallback, useEffect, useRef, useState } from "react";
import { useImmer } from "use-immer";
import useDebugStore from "../../store/useDebugStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { API_BASE_URL } from "../../utils/constants/globals.js";
import type { ISetting, ISettingsResponse } from "./settings.types.js";

const useSettings = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [settings, updateSettings] = useImmer<ISetting[]>([]);

    const [scrollOffset, setScrollOffset] = useState(0);
    const scrollRef = useRef<ControlledScrollViewRef>(null);
    const { addLog } = useDebugStore();

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

            setTimeout(() => {
                scrollRef.current?.remeasure();
            }, 100);
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

    const handleItemFocus = useCallback((index: number) => {
        const scroll = scrollRef.current;
        if (!scroll) return;

        const position = scroll.getItemPosition(index);
        if (!position) return;

        const viewportHeight = scroll.getViewportHeight();
        if (viewportHeight === 0) return;

        setScrollOffset((current) => {
            let newOffset = current;
            if (position.top < current) {
                newOffset = position.top;
            } else if (position.top + position.height > current + viewportHeight) {
                newOffset = position.top + position.height - viewportHeight;
            }
            return newOffset;
        });
    }, []);

    // Keyboard scrolling (Manual)
    useInput((_input, key) => {
        if (key.upArrow) setScrollOffset((prev) => Math.max(0, prev - 1));
        if (key.downArrow) {
            const max = scrollRef.current?.getBottomOffset() || 0;
            setScrollOffset((prev) => Math.min(max, prev + 1));
        }
    });

    useEffect(() => {
        fetchSettings();
    }, [fetchSettings]);

    return {
        settings,
        isLoading,
        error,
        scrollOffset,
        scrollRef,
        fetchSettings,
        handleUpdateSetting,
        handleItemFocus,
    };
};

export default useSettings;
