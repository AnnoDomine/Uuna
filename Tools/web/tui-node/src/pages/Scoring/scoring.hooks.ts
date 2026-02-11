import { useCallback, useEffect, useState } from "react";
import { useImmer } from "use-immer";
import useDebugStore from "../../store/useDebugStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { REFRESH_INTERVAL } from "../../utils/constants/globals.js";
import ScoringService from "../../utils/services/scoring.service.js";
import TaskService from "../../utils/services/task.service.js";
import type { IAgentStats, IScoreEntry } from "./scoring.types.js";

const useScoring = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [rawScores, updateScores] = useImmer<IScoreEntry[]>([]);
    const [agentStats, updateAgentStats] = useImmer<IAgentStats[]>([]);
    const { addLog } = useDebugStore();

    const aggregateScores = useCallback(
        async (scores: IScoreEntry[]) => {
            // In a real enterprise app, we'd do this join in the backend.
            // For now, we fetch tasks to match agents to scores.
            const tasks = await TaskService.getTasks();
            const taskToAgentMap = new Map(tasks.map((t) => [t.id, t.agent_id || "Unknown"]));

            const statsMap = new Map<string, { total: number; count: number }>();

            for (const score of scores) {
                const agent = taskToAgentMap.get(score.task_id) || "System";
                const current = statsMap.get(agent) || { total: 0, count: 0 };
                statsMap.set(agent, {
                    total: current.total + score.final_percent,
                    count: current.count + 1,
                });
            }

            const stats: IAgentStats[] = Array.from(statsMap.entries()).map(([agent, data]) => ({
                agent,
                totalScore: Number(data.total.toFixed(2)),
                averageScore: Number((data.total / data.count).toFixed(2)),
                taskCount: data.count,
            }));

            updateAgentStats(() => stats);
        },
        [updateAgentStats],
    );

    const fetchBoard = useCallback(async () => {
        setIsLoading(true);
        try {
            const scores = await ScoringService.getBoard();
            updateScores(() => scores);
            await aggregateScores(scores);
            setError(null);
        } catch (_err) {
            setError("Failed to sync scoreboard.");
            addLog({
                type: ELogTypes.ERROR,
                message: "Scoreboard sync failed",
                process: "useScoring",
            });
        } finally {
            setIsLoading(false);
        }
    }, [updateScores, aggregateScores, addLog]);

    useEffect(() => {
        fetchBoard();
        const interval = setInterval(fetchBoard, REFRESH_INTERVAL);
        return () => clearInterval(interval);
    }, [fetchBoard]);

    return {
        rawScores,
        agentStats,
        isLoading,
        error,
        refresh: fetchBoard,
    };
};

export default useScoring;
