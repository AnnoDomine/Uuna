import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import { type FC, useMemo } from "react";
import ScrollableSelection from "../../../molecules/ScrollableSelection/ScrollableSelection.js";
import { EFocusAreal } from "../../../store/useFocusStore.js";
import useTaskInspectorStore, { type EventItem } from "../../../store/useTaskInspectorStore.js";

const EventList: FC = () => {
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

    if (!selectedTaskId) {
        return null;
    }

    return (
        <Box
            width="25%"
            flexDirection="column"
            borderStyle="single"
            borderColor={selectedEventId ? "white" : "green"}
            marginRight={1}
        >
            <Box marginBottom={1} paddingX={1}>
                {isLoadingEvents && <Spinner type="timeTravel" />}
                <Text bold color="cyan">
                    EVENTS ({eventItems.length})
                </Text>
            </Box>
            <ScrollableSelection
                id="event-list-selection"
                items={eventItems}
                onSelect={(eventId) => selectEvent(eventId)}
                options={{
                    height: "100%",
                    areal: EFocusAreal.CONTENT,
                    mark_first_item_after_select: false,
                }}
            />
        </Box>
    );
};

export default EventList;
