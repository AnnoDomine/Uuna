import { Box, Text } from "ink";
import InkSelectInput from "ink-select-input";
import type { FC } from "react";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import useNavigation from "./navigation.hooks.js";

const Navigation: FC = () => {
    const { handleSelectItem, highlitedItems, setHighlitedItem } = useNavigation();

    // Use our enterprise hook for navigation
    const { isFocused } = useScopedInput({
        id: "main-navigation",
        areal: EFocusAreal.NAVIGATION,
        autoFocus: true,
        // SelectInput handles its own internal keys,
        // but we ensure it only does so when our scope is active.
    });

    return (
        <Box
            flexDirection="column"
            borderStyle="single"
            borderColor={isFocused ? "#bb9af7" : "#414868"}
            padding={1}
            width={30}
        >
            <Text color={isFocused ? "#bb9af7" : "white"} bold underline>
                Navigation
            </Text>
            <Box marginTop={1}>
                <InkSelectInput
                    items={highlitedItems}
                    onSelect={(i) => handleSelectItem(i.value)}
                    onHighlight={(i) => setHighlitedItem(i.value)}
                    isFocused={isFocused}
                />
            </Box>
        </Box>
    );
};

export default Navigation;
