import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import { IconButton, styled } from "@mui/joy";
import { useState } from "react";
import TaskModal from "../../organisms/TaskModal/TaskModal";

const MenuIconContainer = styled("div")({
    position: "absolute",
    top: "8px",
    left: "8px",
    zIndex: 1,
});

const Tasks = () => {
    const [open, setOpen] = useState<boolean>(false);
    return (
        <div>
            <MenuIconContainer>
                <IconButton
                    variant="outlined"
                    color="neutral"
                    onClick={() => setOpen(true)}
                    sx={{
                        width: "30px",
                        height: "30px",
                    }}
                >
                    <AssignmentOutlinedIcon />
                </IconButton>
            </MenuIconContainer>
            {open && <TaskModal open={open} onClose={() => setOpen(false)} />}
        </div>
    );
};

export default Tasks;
