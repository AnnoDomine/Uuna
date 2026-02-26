import { useEffect } from "react";
import useTaskInspectorStore from "../../store/useTaskInspectorStore.js";

export const useTasksPage = () => {
    const { fetchTasks, error } = useTaskInspectorStore();

    useEffect(() => {
        fetchTasks();
        const interval = setInterval(fetchTasks, 5000);
        return () => clearInterval(interval);
    }, [fetchTasks]);

    return { error };
};
