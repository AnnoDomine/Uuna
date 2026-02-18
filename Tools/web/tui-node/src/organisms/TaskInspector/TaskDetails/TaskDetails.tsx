import { Box, Text } from "ink";
import type { FC } from "react";
import { EFocusAreal } from "../../../store/useFocusStore.js";
import ScrollArea from "../../ScrollArea/ScrollArea.js";
import { useTaskDetails } from "./TaskDetails.hooks.js";

const TaskDetails: FC = () => {
    const { selectedTask, selectedEvent, scores, selectedTaskId } = useTaskDetails();

    if (!selectedTaskId) {
        return null;
    }

    return (
        <Box width="50%" flexDirection="column" borderStyle="single" borderColor="gray">
            {/* TOP: TASK INFO & SCORES (45%) */}
            <Box height="45%" flexDirection="column" borderStyle="single">
                <Box marginBottom={1} paddingX={1}>
                    <Text bold color="yellow">
                        TASK INFO
                    </Text>
                </Box>
                <ScrollArea id="task-info-scroll" areal={EFocusAreal.CONTENT}>
                    <Box flexDirection="column" padding={1}>
                        {selectedTask && (
                            <>
                                <Text>
                                    <Text bold>ID:</Text> {selectedTask.task_id}
                                </Text>
                                <Text>
                                    <Text bold>Title:</Text> {selectedTask.title}
                                </Text>
                                <Text>
                                    <Text bold>Status:</Text> {selectedTask.status}
                                </Text>
                                <Text>
                                    <Text bold>Created:</Text> {selectedTask.created_at}
                                </Text>
                            </>
                        )}
                        <Box marginTop={1}>
                            <Text bold underline>
                                Scores:
                            </Text>
                        </Box>
                        {scores.length === 0 ? (
                            <Text color="gray">No scores yet.</Text>
                        ) : (
                            scores.map((s) => (
                                <Box
                                    key={s.score_id}
                                    flexDirection="column"
                                    borderStyle="round"
                                    borderColor="gray"
                                    padding={1}
                                    marginBottom={1}
                                >
                                    <Text>
                                        Score:{" "}
                                        <Text bold color="green">
                                            {s.score}
                                        </Text>
                                    </Text>
                                    <Text>Reason: {s.reason}</Text>
                                </Box>
                            ))
                        )}
                    </Box>
                </ScrollArea>
            </Box>

            {/* BOTTOM: EVENT DETAILS (55%) */}
            <Box height="55%" flexDirection="column" borderStyle="single">
                <Box marginBottom={1} paddingX={1}>
                    <Text bold color="magenta">
                        EVENT DETAILS
                    </Text>
                </Box>
                <ScrollArea id="event-details-scroll" areal={EFocusAreal.CONTENT}>
                    {selectedEvent ? (
                        <Box flexDirection="column" padding={1}>
                            <Text>
                                <Text bold>Role:</Text> {selectedEvent.role}
                            </Text>
                            <Text>
                                <Text bold>Event:</Text> {selectedEvent.event}
                            </Text>
                            <Text>
                                <Text bold>Timestamp:</Text> {selectedEvent.timestamp}
                            </Text>
                            <Box marginTop={1} borderStyle="round" padding={1}>
                                <Text>{selectedEvent.details}</Text>
                            </Box>
                        </Box>
                    ) : (
                        <Box padding={1}>
                            <Text color="gray">Select an event to see details.</Text>
                        </Box>
                    )}
                </ScrollArea>
            </Box>
        </Box>
    );
};

export default TaskDetails;
