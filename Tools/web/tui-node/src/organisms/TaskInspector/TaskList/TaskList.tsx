import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import type { FC } from "react";
import ScrollableSelection from "../../../molecules/ScrollableSelection/ScrollableSelection.js";
import { EFocusAreal } from "../../../store/useFocusStore.js";
import { useTaskList } from "./TaskList.hooks.js";

const TaskList: FC = () => {
    const { taskItems, selectedTaskId, selectTask, isLoadingTasks } = useTaskList();

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
