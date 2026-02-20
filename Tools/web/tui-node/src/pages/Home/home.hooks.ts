import { useState } from "react";
import { useImmer } from "use-immer";
import { type InputCallback, useScopedInput } from "../../hooks/useScopedInput.js";
import useAIStore, { EActors } from "../../store/useAIStore.js";
import { EFocusAreal } from "../../store/useFocusStore.js";

export const useHome = () => {
    const { chat, addChat, isUninitialised, isLoading, isFetching, isErrored, error } =
        useAIStore();

    const showSpinner = isUninitialised || isLoading || isFetching;

    const [value, setValue] = useState("");
    const [prevUserRequests, setPrevUserRequests] = useImmer<{
        cursor: number;
        requests: Array<string>;
    }>({ cursor: -1, requests: [] });
    const [selectedBuild, setSelectedBuild] = useState("");

    const handleSelectBuild = (val: string) => {
        if (selectedBuild === val) {
            // De-select
            setSelectedBuild("");
            return;
        }
        setSelectedBuild(val);
    };

    const handleSubmit = () => {
        if (!value) return;
        setPrevUserRequests((draft) => {
            draft.requests.push(value);
        });
        addChat(
            `SELECTED BUILD: ${selectedBuild || 'Request build version range in "user request" or user should select one, if not a range or a build version is already in "user request"'}
USER REQUEST: ${value}`,
        );
        setValue("");
    };

    const getChatColor = (actor: EActors) => {
        switch (actor) {
            case EActors.USER:
                return "grey";
            case EActors.LIBRARIAN:
                return "magenta";
            case EActors.AGENT:
                return "cyan";
            default:
                return "white";
        }
    };

    const getActorName = (actor: EActors, agent?: string) => {
        switch (actor) {
            case EActors.USER:
                return "You";
            case EActors.LIBRARIAN:
                return "Librarian";
            case EActors.AGENT:
                return agent || "Agent";
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

    return {
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
    };
};
