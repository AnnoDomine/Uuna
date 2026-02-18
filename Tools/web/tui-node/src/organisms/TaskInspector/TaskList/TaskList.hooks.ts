import { useMemo } from "react";
import useTaskInspectorStore, { type TaskItem } from "../../../store/useTaskInspectorStore.js";

export const useTaskList = () => {
    const { tasks, selectedTaskId, selectTask, isLoadingTasks } = useTaskInspectorStore();

    const taskItems = useMemo(
        () =>
            tasks.map((t: TaskItem) => ({
                label: `[${t.status}] ${t.title.slice(0, 20)}...`,
                value: t.task_id,
                id: t.task_id,
                meta: t,
            })),
        [tasks],
    );

    return {
        taskItems,
        selectedTaskId,
        selectTask,
        isLoadingTasks,
    };
};
