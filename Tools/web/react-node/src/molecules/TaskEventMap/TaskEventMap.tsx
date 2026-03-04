import {
    Accordion,
    AccordionDetails,
    AccordionGroup,
    AccordionSummary,
    CircularProgress,
    Tab,
    TabList,
    TabPanel,
    Tabs,
} from "@mui/joy";
import TaskEventMapSummary from "../../atoms/TaskEventMapSummary/TaskEventMapSummary";
import MapEventDescription from "../MapEventDescription/MapEventDescription";
import MapScoring from "../MapScoring/MapScoring";
import useTaskEventMap from "./taskEventMap.hooks";

type Props = {
    taskId: string;
    isOpen: boolean;
};

const TaskEventMap = ({ taskId, isOpen }: Props) => {
    const {
        events,
        isEventsFetching,
        toggleEvent,
        openEvent,
        scores,
        isScoresFetching,
        toggleScoring,
        openScoring,
    } = useTaskEventMap(taskId, isOpen);

    if (!isOpen) return null;

    return (
        <AccordionGroup>
            <Tabs
                orientation="horizontal"
                size="sm"
                sx={{ backgroundColor: "lightgray", borderRadius: "8px" }}
            >
                <TabList>
                    <Tab variant="plain" color="primary">
                        Events ({events.length})
                    </Tab>
                    <Tab variant="plain" color="primary">
                        Scoring ({scores.length})
                    </Tab>
                </TabList>
                <TabPanel value={0}>
                    {isEventsFetching && (
                        <CircularProgress variant="outlined" sx={{ margin: "auto" }} />
                    )}
                    {events.map((e) => (
                        <Accordion expanded={openEvent === e.event_id} key={e.event_id}>
                            <TaskEventMapSummary
                                {...e}
                                onClick={() => toggleEvent(e.event_id)}
                                key={e.event_id}
                            />
                            <AccordionDetails>
                                <MapEventDescription description={e.details} />
                            </AccordionDetails>
                        </Accordion>
                    ))}
                </TabPanel>
                <TabPanel value={1}>
                    {isScoresFetching && (
                        <CircularProgress variant="outlined" sx={{ margin: "auto" }} />
                    )}
                    {scores.map((s) => (
                        <Accordion expanded={openScoring === s.score_id} key={s.score_id}>
                            <AccordionSummary onClick={() => toggleScoring(s.score_id)}>
                                {s.score_id}
                            </AccordionSummary>
                            <AccordionDetails>
                                <MapScoring {...s} />
                            </AccordionDetails>
                        </Accordion>
                    ))}
                </TabPanel>
            </Tabs>
        </AccordionGroup>
    );
};

export default TaskEventMap;
