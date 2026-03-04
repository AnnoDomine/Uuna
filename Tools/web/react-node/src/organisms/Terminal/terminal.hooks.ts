import { useCallback, useState } from "react";
import { useAskMutation } from "../../redux/api/aiApi";
import { addMessage } from "../../redux/slices/ai";
import { getBuildsStore } from "../../redux/slices/builds";
import { useAppDispatch, useAppSelector } from "../../redux/store";

const useTerminal = () => {
    const dispatch = useAppDispatch();
    const [value, setValue] = useState<string>("");
    const [lastValues, setLastValues] = useState<string[]>([]);
    const [lastValuesIndex, setLastValuesIndex] = useState<number>(-1);
    const { selected } = useAppSelector(getBuildsStore);
    const [askAi, { isLoading }] = useAskMutation();
    const mode = value.startsWith(":") ? "command" : "research";

    const handleSubmit = useCallback(() => {
        if (!value) return;
        setLastValues((p) => {
            const next = [...p, value];
            setLastValuesIndex(next.length);
            return next;
        });
        setValue("");
        switch (mode) {
            case "command":
                console.log("Execute command");
                return;
            case "research":
                dispatch(
                    addMessage({
                        agent: "user",
                        message: value,
                        timestamp: Date.now(),
                        level: "info",
                        type: "chat",
                    }),
                );
                askAi({ prompt: value, builds: selected.map((b) => b.version) });
                console.log("Submit research");
                return;
            default:
                console.log("Unknown mode");
                return;
        }
    }, [value, mode, dispatch, askAi, selected]);

    return {
        value,
        setValue,
        mode,
        handleSubmit,
        lastValues,
        lastValuesIndex,
        setLastValuesIndex,
        isLoading,
    };
};

export default useTerminal;
