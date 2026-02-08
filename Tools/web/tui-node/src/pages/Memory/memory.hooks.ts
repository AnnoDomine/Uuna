import { useCallback, useState } from "react";
import { useImmer } from "use-immer";
import useDebugStore from "../../store/useDebugStore.js";
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
        if (!query.trim()) return;

        setIsLoading(true);
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

    return {
        query,
        setQuery,
        role,
        setRole,
        results,
        isLoading,
        handleSearch,
    };
};

export default useMemory;
