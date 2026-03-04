import {
    Accordion,
    AccordionDetails,
    AccordionGroup,
    Button,
    CircularProgress,
    DialogContent,
    Modal,
    ModalClose,
    ModalDialog,
    ModalOverflow,
    Typography,
} from "@mui/joy";
import TaskModalTaskRow from "../../atoms/TaskModalTaskRow/TaskModalTaskRow";
import TaskEventMap from "../../molecules/TaskEventMap/TaskEventMap";
import useTaskModal from "./taskModal.hooks";

type Props = {
    open: boolean;
    onClose: () => void;
};

const TaskModal = ({ onClose, open }: Props) => {
    const { tasks, isTasksFetching, openTask, toggleTask, handleRefetch } = useTaskModal();
    return (
        <Modal
            open={open}
            onClose={() => {
                onClose();
            }}
        >
            <ModalOverflow>
                <ModalDialog layout="fullscreen">
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "0px 64px",
                        }}
                    >
                        <Typography level="h2">
                            Tasks and Events/Scorings. Open: {openTask || "None"}
                        </Typography>
                        <Button onClick={handleRefetch} variant="plain" color="primary">
                            Refetch
                        </Button>
                    </div>
                    <ModalClose />
                    <DialogContent>
                        {isTasksFetching && (
                            <CircularProgress variant="outlined" sx={{ margin: "auto" }} />
                        )}
                        <AccordionGroup
                            sx={{
                                maxWidth: "90%",
                                margin: "auto",
                                height: "100%",
                                maxHeight: "80vh",
                                overflow: "auto",
                                backgroundColor: "white",
                                borderRadius: "6px",
                            }}
                        >
                            {tasks.map((task) => (
                                <Accordion key={task.task_id} expanded={openTask === task.task_id}>
                                    <TaskModalTaskRow
                                        {...task}
                                        onClick={() => toggleTask(task.task_id)}
                                    />
                                    <AccordionDetails>
                                        <TaskEventMap
                                            taskId={task.task_id}
                                            isOpen={openTask === task.task_id}
                                        />
                                    </AccordionDetails>
                                </Accordion>
                            ))}
                        </AccordionGroup>
                    </DialogContent>
                </ModalDialog>
            </ModalOverflow>
        </Modal>
    );
};

export default TaskModal;
