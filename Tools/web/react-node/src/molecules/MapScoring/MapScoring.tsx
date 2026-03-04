import { styled } from "@mui/joy";
import type { ScoreItem } from "../../redux/api/tasksApi";

type Props = ScoreItem;

const ScorboardContainer = styled("div")(() => ({
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "8px",
    borderRadius: "8px",
    backgroundColor: "white",
}));

const ScorboardIDs = styled("div")(() => ({
    display: "flex",
    flexDirection: "row",
    fontSize: "14px",
    gap: "8px",
    alignItems: "center",
    justifyContent: "space-between",
}));

const ScorboardValue = styled("div")(() => ({
    display: "flex",
    flexDirection: "row",
    fontSize: "18px",
    fontWeight: "bold",
    gap: "8px",
    alignItems: "center",
    justifyContent: "space-between",
}));

const ScorboardReason = styled("div")(() => ({
    fontSize: "14px",
    fontWeight: "bold",
}));

const MapScoring = ({ event_id, reason, score_id, score, task_id, created_at }: Props) => {
    return (
        <ScorboardContainer>
            <ScorboardIDs>
                <span>Score: {score_id}</span>
                <span>Task: {task_id}</span>
                <span>Event: {event_id}</span>
            </ScorboardIDs>
            <ScorboardValue>
                <span>Score: {score.toLocaleString()}</span>
                <span>Created at: {new Date(created_at).toLocaleString()}</span>
            </ScorboardValue>
            <ScorboardReason>{reason}</ScorboardReason>
        </ScorboardContainer>
    );
};

export default MapScoring;
