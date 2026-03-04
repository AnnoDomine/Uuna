import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import TimelineRoundedIcon from "@mui/icons-material/TimelineRounded";
import TuneRoundedIcon from "@mui/icons-material/TuneRounded";
import AssignmentTurnedInOutlinedIcon from '@mui/icons-material/AssignmentTurnedInOutlined';
import { styled } from "@mui/joy";
import type { SettingsObj } from "../../redux/types/settings.types";

type Props = {
    setting: keyof SettingsObj;
};

const IconContainer = styled("div")(({ theme }) => ({
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    width: "30px",
    height: "30px",
    borderRadius: "50%",
    border: "1px solid transparent",
    "&.ai": {
        color: theme.palette.primary[500],
    },
    "&.ingestion": {
        color: theme.palette.success[500],
    },
    "&.analysis": {
        color: theme.palette.neutral[500],
    },
    "&.system": {
        color: theme.palette.danger[500],
    },
    "&.tasks": {
        color: theme.palette.warning[500],
    },
}));

const SettingIcons = ({ setting }: Props) => {
    switch (setting) {
        case "ai":
            return (
                <IconContainer className={setting}>
                    <AutoAwesomeRoundedIcon />
                </IconContainer>
            );
        case "ingestion":
            return (
                <IconContainer className={setting}>
                    <StorageRoundedIcon />
                </IconContainer>
            );
        case "analysis":
            return (
                <IconContainer className={setting}>
                    <TimelineRoundedIcon />
                </IconContainer>
            );
        case "system":
            return (
                <IconContainer className={setting}>
                    <TuneRoundedIcon />
                </IconContainer>
            );
        case "tasks":
            return (
                <IconContainer className={setting}>
                    <AssignmentTurnedInOutlinedIcon />
                </IconContainer>
            );
        default:
            return <IconContainer />;
    }
};

export default SettingIcons;
