import { styled } from "@mui/joy";

const ConnectorIndicator = styled("div")(({ theme }) => ({
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    border: "0.5px solid white",
    "&.idle": {
        backgroundColor: theme.palette.divider,
    },
    "&.error": {
        backgroundColor: theme.palette.danger[500],
    },
    "&.process": {
        backgroundColor: theme.palette.warning[500],
    },
    "&.success": {
        backgroundColor: theme.palette.success[500],
    },
}));

export default ConnectorIndicator;
