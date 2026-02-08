import { Box, Text } from "ink";
import type { FC } from "react";
import Button from "../../atoms/Button/Button.js";
import useBackend from "../../hooks/useBackend.js";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import SettingsListItem from "../../molecules/SettingsListItem/SettingsListItem.js";
import ScrollArea from "../../organisms/ScrollArea/ScrollArea.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import { useStore } from "../../store/useStore.js";
import useSettings from "./settings.hooks.js";

const Settings: FC = () => {
    const { settings, isLoading, error, handleUpdateSetting, fetchSettings } = useSettings();

    const { restartBackend } = useBackend();
    const { isRestarting } = useStore();

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

    return (
        <Box flexDirection="column" flexGrow={1} padding={1}>
            <Box marginBottom={1} justifyContent="space-between" width="100%">
                <Text color="#7aa2f7" bold>
                    AI & SYSTEM SETTINGS
                </Text>
                <Box>
                    <Button
                        label={isRestarting ? "RESTARTING..." : "RESTART BACKEND"}
                        onPress={restartBackend}
                        color={isRestartFocused ? "white" : "red"}
                        isActive={isRestartFocused}
                    />
                    <Button
                        label="RELOAD"
                        onPress={fetchSettings}
                        color={isReloadFocused ? "white" : "yellow"}
                        isActive={isReloadFocused}
                    />
                </Box>
            </Box>

            {isLoading && <Text color="yellow">Loading settings from backend...</Text>}
            {error && <Text color="red">{error}</Text>}

            {!isLoading && !error && settings.length === 0 && (
                <Text color="gray">No settings found.</Text>
            )}

            <ScrollArea id="settings-scroll-area">
                {settings.map((setting, index) => (
                    <SettingsListItem
                        key={setting.key}
                        setting={setting}
                        onSave={handleUpdateSetting}
                        index={index}
                    />
                ))}
            </ScrollArea>
        </Box>
    );
};

export default Settings;
