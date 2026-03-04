import { AccordionSummary, type AccordionSummaryProps, styled } from "@mui/joy";
import type { TaskItem } from "../../redux/api/tasksApi";

type Props = TaskItem & AccordionSummaryProps;

const TaskRowContainer = styled(AccordionSummary)(() => ({
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "8px",
}));

const TaskModalTaskRow = ({ task_id, title, created_at, status, ...rest }: Props) => {
    return (
        <TaskRowContainer {...rest}>
            <div style={{ width: "30%" }} title={task_id}>
                {task_id}
            </div>
            <div
                style={{
                    width: "35%",
                    textOverflow: "ellipsis",
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                }}
                title={title}
            >
                {title}
            </div>
            <div style={{ width: "15%" }} title={status}>
                {status}
            </div>
            <div style={{ width: "20%" }} title={created_at}>
                {created_at}
            </div>
        </TaskRowContainer>
    );
};

export default TaskModalTaskRow;
