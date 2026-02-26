import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import TextInput from "ink-text-input";
import type { FC } from "react";
import ScrollArea from "../../organisms/ScrollArea/ScrollArea.js";
import SelectBuild from "../../organisms/SelectBuild/SelectBuild.js";
import { useHome } from "./home.hooks.js";

const Home: FC = () => {
    const {
        chat,
        isErrored,
        error,
        showSpinner,
        value,
        setValue,
        selectedBuild,
        handleSelectBuild,
        handleSubmit,
        getChatColor,
        getActorName,
        isFocused,
    } = useHome();

    return (
        <Box flexDirection="row" height="100%" minHeight="100%" minWidth="100%" width="100%">
            <SelectBuild
                id={"select-build-container"}
                selectedBuild={selectedBuild}
                onChange={handleSelectBuild}
            />
            <Box
                flexDirection="column"
                flexGrow={1}
                justifyContent="flex-end"
                alignItems="stretch"
                borderStyle="single"
                borderColor={isFocused ? "#5F71DA" : "#414868"}
                height="100%"
                minHeight="100%"
            >
                <Box padding={1} flexGrow={1} flexDirection="column" height="100%" minHeight={0}>
                    <ScrollArea id="home-chat-scroll" autoScrollToBottom>
                        {chat.map((v) => (
                            <Text key={v.id} color={getChatColor(v.actor)}>
                                [{new Date(v.timestamp).toLocaleString()}]{" "}
                                {getActorName(v.actor, v.agent)}:{"\n"}
                                {v.message}
                            </Text>
                        ))}
                    </ScrollArea>
                </Box>
                {isErrored && (
                    <Box padding={1} flexGrow={1} flexDirection="column" minHeight={0}>
                        <Text color="red">{error || "Unknown error"}</Text>
                    </Box>
                )}
                <Box padding={1} minHeight={0} display="flex" flexDirection="row" gap={2}>
                    {showSpinner && <Spinner type="timeTravel" />}
                    <Text>Please enter your question:</Text>
                    <TextInput
                        value={value}
                        onChange={setValue}
                        onSubmit={handleSubmit}
                        focus={isFocused}
                    />
                </Box>
            </Box>
        </Box>
    );
};

export default Home;
