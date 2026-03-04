import { useCallback, useState } from "react";
import { useGetEventsQuery, useGetScoresQuery } from "../../redux/api/tasksApi";

const useTaskEventMap = (taskId: string, isOpen: boolean) => {
    const { data: events, isFetching: isEventsFetching } = useGetEventsQuery(taskId, {
        skip: !isOpen,
    });
    const { data: scores, isFetching: isScoresFetching } = useGetScoresQuery(taskId, {
        skip: !isOpen,
    });
    const [openEvent, setOpenEvent] = useState<string | null>(null);
    const [openScoring, setOpenScoring] = useState<string | null>(null);

    const toggleEvent = useCallback(
        (eventId: string) => {
            if (openEvent === eventId) {
                setOpenEvent(null);
            } else {
                setOpenEvent(eventId);
            }
        },
        [openEvent],
    );

    const toggleScoring = useCallback(
        (scoringId: string) => {
            if (openScoring === scoringId) {
                setOpenScoring(null);
            } else {
                setOpenScoring(scoringId);
            }
        },
        [openScoring],
    );

    // Reset openEvent state during render if the parent container is closed
    if (!isOpen && (openEvent !== null || openScoring !== null)) {
        setOpenEvent(null);
        setOpenScoring(null);
    }

    return {
        events: events?.events || [],
        isEventsFetching,
        toggleEvent,
        openEvent,
        scores: scores?.scores || [],
        isScoresFetching,
        toggleScoring,
        openScoring,
    };
};

export default useTaskEventMap;
