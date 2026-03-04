import { AccordionSummary, type AccordionSummaryProps, styled } from "@mui/joy";
import type { EventItem } from "../../redux/api/tasksApi";

type Props = EventItem & AccordionSummaryProps;

const TaskEventContainer = styled(AccordionSummary)(() => ({
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "8px",
}));

const TaskEventMapSummary = ({ event, event_id, role, timestamp, ...rest }: Props) => {
    return (
        <TaskEventContainer {...rest}>
            <div style={{ width: "30%" }} title={event_id}>
                {event_id}
            </div>
            <div
                style={{
                    width: "35%",
                    textOverflow: "ellipsis",
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                }}
                title={event}
            >
                {event}
            </div>
            <div style={{ width: "15%" }} title={role}>
                {role}
            </div>
            <div style={{ width: "20%" }} title={timestamp}>
                {timestamp}
            </div>
        </TaskEventContainer>
    );
};

export default TaskEventMapSummary;
