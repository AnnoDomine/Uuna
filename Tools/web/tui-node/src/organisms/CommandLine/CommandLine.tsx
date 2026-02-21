import { Box, Text } from "ink";
import type React from "react";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import { useCommandLine } from "./commandLine.hooks.js";

const CommandLine: React.FC = () => {
    const { input, setInput, info, handleExecute, handleCycleSuggestion } = useCommandLine();

    // Use our Enterprise Focus/Input helper
    useScopedInput({
        id: "main-command-line",
        areal: EFocusAreal.COMMAND,
        autoFocus: true,
        ctrlQToExit: true,
        keyMap: (inputStr, key) => {
            if (key.return) {
                handleExecute(input);
                return;
            }
            if (key.backspace) {
                setInput(input.slice(0, -1));
                return;
            }
            if (key.tab && key.ctrl) {
                // Ctrl + Tab for auto-completion
                handleCycleSuggestion(key.shift ? "prev" : "next");
                return;
            }
            if (!key.ctrl && !key.meta && inputStr) {
                setInput(input + inputStr);
            }
        },
    });

    return (
        <Box flexDirection="column" borderStyle="round" borderColor="#3b4261" paddingX={1}>
            {/* Info Box (5 lines) */}
            <Box flexDirection="column" height={5} marginBottom={1}>
                {info.map((line, i) => (
                    // biome-ignore lint/suspicious/noArrayIndexKey: Fixed size static display
                    <Text key={`info-${i}`} color="#9ece6a">
                        {line}
                    </Text>
                ))}
            </Box>

            {/* Input Line */}
            <Box>
                <Text color="#bb9af7" bold>
                    {"> "}
                </Text>
                <Text color="white">{input}</Text>
                <Text color="white" backgroundColor="#414868">
                    {" "}
                </Text>
            </Box>
        </Box>
    );
};

export default CommandLine;
