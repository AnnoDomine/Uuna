import { useCallback, useState } from "react";
import { useListTasksQuery } from "../../redux/api/tasksApi";

const useTaskModal = () => {
    const { data: tasksList, isFetching: isTasksListFetching, refetch } = useListTasksQuery();

    const [openTask, setOpenTask] = useState<string | null>(null);

    const toggleTask = useCallback(
        (taskId: string) => {
            if (openTask === taskId) {
                setOpenTask(null);
            } else {
                setOpenTask(taskId);
            }
        },
        [openTask],
    );

    const handleRefetch = useCallback(() => {
        refetch();
        setOpenTask(null);
    }, [refetch]);

    return {
        tasks: tasksList?.tasks || [],
        isTasksFetching: isTasksListFetching,
        openTask,
        toggleTask,
        handleRefetch,
    };
};

export default useTaskModal;
