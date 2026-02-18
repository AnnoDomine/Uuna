import { useCallback, useState } from "react";
import { useImmer } from "use-immer";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import useDebugStore from "../../store/useDebugStore.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import MemoryService from "../../utils/services/memory.service.js";
import type { IMemoryResult } from "./memory.types.js";

const useMemory = () => {
    const [query, setQuery] = useState<string>("");
    const [role, setRole] = useState<string>("Librarian");
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [results, updateResults] = useImmer<IMemoryResult[]>([]);
    const { addLog } = useDebugStore();

    const handleSearch = useCallback(async () => {
        if (!query.trim()) {
            addLog({
                type: ELogTypes.WARN,
                message: "Empty search query ignored",
                process: "useMemory",
            });
            return;
        }

        setIsLoading(true);
        updateResults(() => []); // Clear previous results
        addLog({
            type: ELogTypes.INFO,
            message: `Searching memory for "${query}" as role ${role}`,
            process: "useMemory",
        });

        try {
            const data = await MemoryService.search({
                query,
                role,
                limit: 10,
            });
            updateResults(() => data);
        } catch (_err) {
            addLog({
                type: ELogTypes.ERROR,
                message: "Hook: Memory search failed",
                process: "useMemory",
            });
        } finally {
            setIsLoading(false);
        }
    }, [query, role, updateResults, addLog]);

    // Search Input Scope
    const { isFocused: isSearchFocused } = useScopedInput({
        id: "memory-search-input",
        areal: EFocusAreal.CONTENT,
        autoFocus: true,
        keyMap: (_input, key) => {
            if (key.return) {
                handleSearch();
            }
        },
    });

    return {
        query,
        setQuery,
        role,
        setRole,
        results,
        isLoading,
        handleSearch,
        isSearchFocused,
    };
};

export default useMemory;
