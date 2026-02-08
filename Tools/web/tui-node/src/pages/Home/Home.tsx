import { Box, Text, useFocus } from "ink";
import Spinner from "ink-spinner";
import TextInput from "ink-text-input";
import { type FC, useState } from "react";
import { useImmer } from "use-immer";
import { v4 as uuidv4 } from "uuid";

const Home: FC = () => {
    const [value, setValue] = useState("");
    const [chat, setChat] = useImmer<
        Array<{
            from: "user" | "agent";
            message: string;
            timestamp: number;
            id: string;
        }>
    >([]);

    const handleSubmit = () => {
        if (!value) return;
        setChat((draft) => {
            draft.push({
                from: "user",
                message: value,
                timestamp: Date.now(),
                id: uuidv4(),
            });
            draft = draft.filter((v) => !!v.message);
        });
        setValue("");
    };

    const { isFocused } = useFocus({ id: "home" });

    return (
        <Box
            padding={1}
            flexDirection="column"
            flexGrow={1}
            justifyContent="flex-end"
            alignItems="stretch"
            borderStyle="single"
            borderColor={isFocused ? "#5F71DA" : "#414868"}
        >
            <Box padding={1} minHeight={0} flexGrow={1} flexDirection="column" height={20}>
                {chat.map((v) => (
                    <Text key={v.id} color={v.from === "user" ? "grey" : "magenta"}>
                        [{new Date(v.timestamp).toLocaleString()}] {v.from.toLocaleUpperCase()}:{" "}
                        {v.message}
                    </Text>
                ))}
            </Box>
            <Box padding={1} minHeight={0} display="flex" flexDirection="row">
                <Spinner type="timeTravel" />
                <Text> Please enter your question: </Text>
                <TextInput
                    value={value}
                    onChange={setValue}
                    onSubmit={handleSubmit}
                    focus={isFocused}
                />
            </Box>
        </Box>
    );
};

export default Home;
