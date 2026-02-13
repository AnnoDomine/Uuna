import { Box, Text } from "ink";
import type { FC } from "react";
import Table from "../../atoms/Table/Table.js";
import useTasks from "./tasks.hooks.js";

const Tasks: FC = () => {
    const { tasks, isLoading, error } = useTasks();

    // Map data for the Table component
    const tableData = tasks.map((task) => ({
        ID: task.id.slice(0, 8),
        Title: task.title,
        Status: task.status.toUpperCase(),
        Progress: `${task.progress}%`,
        Updated: new Date(task.updated_at).toLocaleTimeString(),
    }));

    return (
        <Box flexDirection="column" flexGrow={1} padding={1}>
            <Box marginBottom={1}>
                <Text color="#7aa2f7" bold>
                    RESEARCH TASK MONITORING
                </Text>
            </Box>

            {isLoading && tasks.length === 0 && (
                <Text color="yellow">Syncing with task queue...</Text>
            )}
            {error && <Text color="red">{error}</Text>}

            {!isLoading && tasks.length === 0 && (
                <Text color="gray">No active or historical tasks found.</Text>
            )}

            {tasks.length > 0 && (
                <Box borderStyle="single" borderColor="#414868">
                    <Table id="tasks-table" data={tableData} headerStyles={{ color: "magenta" }} />
                </Box>
            )}
        </Box>
    );
};

export default Tasks;
