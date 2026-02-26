import { useMemo } from "react";
import useTaskInspectorStore, { type EventItem } from "../../../store/useTaskInspectorStore.js";

export const useEventList = () => {
    const { events, selectedTaskId, selectedEventId, selectEvent, isLoadingEvents } =
        useTaskInspectorStore();

    const eventItems = useMemo(
        () =>
            events.map((e: EventItem) => ({
                label: `${e.role}: ${e.event}`,
                value: e.event_id,
                id: e.event_id,
                meta: e,
            })),
        [events],
    );

    return {
        eventItems,
        selectedTaskId,
        selectedEventId,
        selectEvent,
        isLoadingEvents,
    };
};
