import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import TextInput from "ink-text-input";
import { type FC, useState } from "react";
import { useImmer } from "use-immer";
import { type InputCallback, useScopedInput } from "../../hooks/useScopedInput.js";
import ScrollArea from "../../organisms/ScrollArea/ScrollArea.js";
import SelectBuild from "../../organisms/SelectBuild/SelectBuild.js";
import useAIStore, { EActors } from "../../store/useAIStore.js";
import { EFocusAreal } from "../../store/useFocusStore.js";

const Home: FC = () => {
    const { chat, addChat, isUninitialised, isLoading, isFetching, isErrored, error } =
        useAIStore();

    const showSpinner = isUninitialised || isLoading || isFetching;

    const [value, setValue] = useState("");
    const [prevUserRequests, setPrevUserRequests] = useImmer<{
        cursor: number;
        requests: Array<string>;
    }>({ cursor: -1, requests: [] });
    const [selectedBuild, setSelectedBuild] = useState("");

    const handleSelectBuild = (value: string) => {
        if (selectedBuild === value) {
            // De-select
            setSelectedBuild("");
            return;
        }
        setSelectedBuild(value);
    };

    const handleSubmit = () => {
        if (!value) return;
        setPrevUserRequests((draft) => {
            draft.requests.push(value);
        });
        addChat(
            `SELECTED BUILD: ${selectedBuild || 'Request build version range in "user request" or user should select one, if not a range or a build version is already in "user request"'}\nUSER REQUEST: ${value}`,
        );
        setValue("");
    };

    const getChatColor = (actor: EActors) => {
        switch (actor) {
            case EActors.USER:
                return "grey";
            case EActors.LIBRARIAN:
                return "magenta";
            default:
                return "white";
        }
    };

    const getActorName = (actor: EActors) => {
        switch (actor) {
            case EActors.USER:
                return "You";
            case EActors.LIBRARIAN:
                return "Librarian";
            case EActors.SYSTEM:
                return "System";
            default:
                return "Unknown";
        }
    };

    const customKeyMap: InputCallback = (_input, key) => {
        if (key.upArrow) {
            const cursor = prevUserRequests.cursor;
            const prev = prevUserRequests.requests;
            if (!prev.length) return;
            if (cursor === 0) return;
            if (cursor === -1) {
                const lastEntryIdx = prev.length - 1;
                const lastEntry = prev[lastEntryIdx];
                setValue(() => {
                    setPrevUserRequests((draft) => {
                        draft.cursor = lastEntryIdx;
                    });
                    return lastEntry;
                });
                return;
            }
            const prevEntryIdx = cursor - 1;
            const prevEntry = prev[prevEntryIdx];
            setValue(() => {
                setPrevUserRequests((draft) => {
                    draft.cursor = prevEntryIdx;
                });
                return prevEntry;
            });
        }
    };

    const { isFocused } = useScopedInput({
        id: "home",
        areal: EFocusAreal.CONTENT,
        keyMap: customKeyMap,
    });

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
                                [{new Date(v.timestamp).toLocaleString()}] {getActorName(v.actor)}:
                                {"\n"}
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
