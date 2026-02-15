import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import { type FC, useMemo } from "react";
import ScrollableSelection from "../../../molecules/ScrollableSelection/ScrollableSelection.js";
import { EFocusAreal } from "../../../store/useFocusStore.js";
import useTaskInspectorStore, { type TaskItem } from "../../../store/useTaskInspectorStore.js";

const TaskList: FC = () => {
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

    return (
        <Box
            width="25%"
            flexDirection="column"
            borderStyle="single"
            borderColor={selectedTaskId ? "white" : "green"}
            marginRight={1}
        >
            <Box marginBottom={1} paddingX={1}>
                {isLoadingTasks && <Spinner type="timeTravel" />}
                <Text bold color="green">
                    TASKS ({taskItems.length})
                </Text>
            </Box>
            <ScrollableSelection
                id="task-list-selection"
                items={taskItems}
                onSelect={(taskId) => selectTask(taskId)}
                options={{
                    height: "100%",
                    areal: EFocusAreal.CONTENT,
                    mark_first_item_after_select: false,
                }}
            />
        </Box>
    );
};

export default TaskList;
