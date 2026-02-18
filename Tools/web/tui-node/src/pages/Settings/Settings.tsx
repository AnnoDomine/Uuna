import { Box, Text } from "ink";
import type { FC } from "react";
import Button from "../../atoms/Button/Button.js";
import SettingsListItem from "../../molecules/SettingsListItem/SettingsListItem.js";
import ScrollArea from "../../organisms/ScrollArea/ScrollArea.js";
import useSettings from "./settings.hooks.js";

const Settings: FC = () => {
    const {
        settings,
        isLoading,
        error,
        handleUpdateSetting,
        fetchSettings,
        isRestarting,
        restartBackend,
        isRestartFocused,
        isReloadFocused,
    } = useSettings();

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
