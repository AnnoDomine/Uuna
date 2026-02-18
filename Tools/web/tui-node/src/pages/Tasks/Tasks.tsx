import { Box, Text } from "ink";
import type { FC } from "react";
import EventList from "../../organisms/TaskInspector/EventList/EventList.js";
import TaskDetails from "../../organisms/TaskInspector/TaskDetails/TaskDetails.js";
import TaskList from "../../organisms/TaskInspector/TaskList/TaskList.js";
import { useTasksPage } from "./tasks.hooks.js";

const Tasks: FC = () => {
    const { error } = useTasksPage();

    if (error) {
        return (
            <Box flexDirection="column" flexGrow={1} padding={1} width="100%">
                <Text color="red">{error}</Text>
            </Box>
        );
    }

    return (
        <Box flexDirection="row" flexGrow={1} padding={1} width="100%">
            {/* COLUMN 1: TASKS (25%) */}
            <TaskList />

            {/* COLUMN 2: EVENTS (25%) - Visible only if task selected */}
            <EventList />

            {/* COLUMN 3: DETAILS (50%) - Split View */}
            <TaskDetails />
        </Box>
    );
};

export default Tasks;
