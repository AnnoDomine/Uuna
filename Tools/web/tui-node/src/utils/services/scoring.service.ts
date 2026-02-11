import axios from "axios";
import type { IScoreboardResponse, IScoreEntry } from "../../pages/Scoring/scoring.types.js";
import useDebugStore from "../../store/useDebugStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { API_BASE_URL } from "../constants/globals.js";

class ScoringService {
    private static instance: ScoringService;

    private constructor() {}

    public static getInstance(): ScoringService {
        if (!ScoringService.instance) {
            ScoringService.instance = new ScoringService();
        }
        return ScoringService.instance;
    }

    /**
     * Fetches the raw scoreboard from the backend.
     */
    public async getBoard(): Promise<IScoreEntry[]> {
        const { addLog } = useDebugStore.getState();
        try {
            addLog({
                type: ELogTypes.DEBUG,
                message: "Fetching scoreboard",
                process: "ScoringService",
            });
            const response = await axios.get<IScoreboardResponse>(`${API_BASE_URL}/score/board`);

            // Map the raw DuckDB fetchall rows to objects
            const mappedScores: IScoreEntry[] = response.data.scores.map((row) => ({
                score_id: row[0],
                task_id: row[1],
                event_id: row[2],
                final_percent: row[3],
                created_at: row[4],
            }));

            return mappedScores;
        } catch (error) {
            addLog({
                type: ELogTypes.ERROR,
                message: `Failed to fetch scoreboard: ${error}`,
                process: "ScoringService",
            });
            return [];
        }
    }
}

export default ScoringService.getInstance();
