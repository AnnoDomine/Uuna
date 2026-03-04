import MenuIcon from "@mui/icons-material/Menu";
import { styled } from "@mui/joy";
import Drawer from "@mui/joy/Drawer";
import IconButton from "@mui/joy/IconButton";
import { useState } from "react";
import Settings from "../../organisms/Settings/Settings";

const MenuIconContainer = styled("div")({
    position: "absolute",
    top: "8px",
    right: "8px",
    zIndex: 1,
});

const Menu = () => {
    const [open, setOpen] = useState<boolean>(false);
    return (
        <>
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
                    <MenuIcon />
                </IconButton>
            </MenuIconContainer>
            <Drawer open={open} onClose={() => setOpen(false)} anchor="right">
                <Settings />
            </Drawer>
        </>
    );
};

export default Menu;
