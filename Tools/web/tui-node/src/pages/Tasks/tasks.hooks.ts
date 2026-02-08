import { useCallback, useEffect, useState } from "react";
import { useImmer } from "use-immer";
import useDebugStore from "../../store/useDebbugStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { REFRESH_INTERVAL } from "../../utils/constants/globals.js";
import TaskService from "../../utils/services/task.service.js";
import type { ITask } from "./tasks.types.js";

const useTasks = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [tasks, updateTasks] = useImmer<ITask[]>([]);
    const { addLog } = useDebugStore();

    const fetchTasks = useCallback(async () => {
        setIsLoading(true);
        addLog({
            type: ELogTypes.DEBUG,
            message: "Syncing tasks with backend",
            process: "useTasks",
        });
        try {
            const data = await TaskService.getTasks();
            updateTasks(() => data);
            setError(null);
            addLog({
                type: ELogTypes.TRACE,
                message: `Synced ${data.length} tasks`,
                process: "useTasks",
            });
        } catch (_err) {
            setError("Failed to sync tasks with central archive.");
            addLog({ type: ELogTypes.ERROR, message: "Task sync failed", process: "useTasks" });
        } finally {
            setIsLoading(false);
        }
    }, [updateTasks, addLog]);

    useEffect(() => {
        fetchTasks();
        const interval = setInterval(fetchTasks, REFRESH_INTERVAL);
        return () => clearInterval(interval);
    }, [fetchTasks]);

    return {
        tasks,
        isLoading,
        error,
        refresh: fetchTasks,
    };
};

export default useTasks;
