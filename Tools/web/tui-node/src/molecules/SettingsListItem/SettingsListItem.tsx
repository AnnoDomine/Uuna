import { Box, Text } from "ink";
import TextInput from "ink-text-input";
import type { FC } from "react";
import { useEffect, useState } from "react";
import Button from "../../atoms/Button/Button.js";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import useSettingsListItem from "./settings_list_item.hooks.js";
import type { SettingsListItemProps } from "./settings_list_item.types.js";

const SettingsListItem: FC<SettingsListItemProps & { index: number }> = ({
    setting,
    onSave,
    index,
}) => {
    const { handleFokusScroll } = useSettingsListItem(index);
    const [currentValue, setCurrentValue] = useState<string>(String(setting.value));

    // Focus for Input (no keyMap needed as ink-text-input handles its own typing)
    const { isFocused: isInputFocused } = useScopedInput({
        id: `input-${index}`,
        areal: EFocusAreal.CONTENT,
    });

    // Focus + Logic for Save Button using keyMap
    const { isFocused: isButtonFocused } = useScopedInput({
        id: `btn-${index}`,
        areal: EFocusAreal.CONTENT,
        keyMap: (input, key) => {
            if (key.return) {
                onSave(setting.key, currentValue);
            }
        },
    });

    // Synchronize scroll when focused
    useEffect(() => {
        if (isInputFocused || isButtonFocused) {
            handleFokusScroll();
        }
    }, [isInputFocused, isButtonFocused, handleFokusScroll]);

    return (
        <Box
            flexDirection="row"
            borderStyle="round"
            borderColor={isInputFocused || isButtonFocused ? "#7aa2f7" : "#24283b"}
            paddingX={1}
            width="100%"
        >
            <Box flexDirection="column" width="40%">
                <Text bold color={isInputFocused || isButtonFocused ? "#bb9af7" : "white"}>
                    {setting.description}
                </Text>
                <Text color="#565f89" dimColor>
                    {setting.key}
                </Text>
            </Box>

            <Box width="40%" paddingX={2}>
                <Text color={isInputFocused ? "cyan" : "white"}>Value: </Text>
                <TextInput value={currentValue} onChange={setCurrentValue} focus={isInputFocused} />
            </Box>

            <Box width="20%" justifyContent="flex-end">
                <Button
                    label="SAVE"
                    onPress={() => onSave(setting.key, currentValue)}
                    isActive={isButtonFocused}
                    color={isButtonFocused ? "green" : "cyan"}
                />
            </Box>
        </Box>
    );
};

export default SettingsListItem;
