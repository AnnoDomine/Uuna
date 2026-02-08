import axios from "axios";
import type {
    IMemoryResult,
    IMemorySearchRequest,
    IMemorySearchResponse,
} from "../../pages/Memory/memory.types.js";
import useDebugStore from "../../store/useDebugStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { API_BASE_URL } from "../constants/globals.js";

class MemoryService {
    private static instance: MemoryService;

    private constructor() {}

    public static getInstance(): MemoryService {
        if (!MemoryService.instance) {
            MemoryService.instance = new MemoryService();
        }
        return MemoryService.instance;
    }

    /**
     * Performs a semantic search in the vector memory.
     */
    public async search(request: IMemorySearchRequest): Promise<IMemoryResult[]> {
        const { addLog } = useDebugStore.getState();
        try {
            addLog({
                type: ELogTypes.DEBUG,
                message: `Semantic search for: "${request.query}" (role: ${request.role})`,
                process: "MemoryService",
            });
            const response = await axios.post<IMemorySearchResponse>(
                `${API_BASE_URL}/memory/search`,
                request,
            );
            addLog({
                type: ELogTypes.INFO,
                message: `Found ${response.data.results.length} matches in memory`,
                process: "MemoryService",
            });
            return response.data.results;
        } catch (error) {
            addLog({
                type: ELogTypes.ERROR,
                message: `Memory search failed: ${error}`,
                process: "MemoryService",
            });
            return [];
        }
    }
}

export default MemoryService.getInstance();
