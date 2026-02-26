import { useMemo } from "react";
import useTaskInspectorStore from "../../../store/useTaskInspectorStore.js";

export const useTaskDetails = () => {
    const { tasks, events, scores, selectedTaskId, selectedEventId } = useTaskInspectorStore();

    const selectedTask = useMemo(
        () => tasks.find((t) => t.task_id === selectedTaskId),
        [tasks, selectedTaskId],
    );

    const selectedEvent = useMemo(
        () => events.find((e) => e.event_id === selectedEventId),
        [events, selectedEventId],
    );

    return {
        selectedTask,
        selectedEvent,
        scores,
        selectedTaskId,
    };
};
