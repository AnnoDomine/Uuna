import { AccordionDetails } from "@mui/joy";
import type { JSX } from "react";

type Props = {
    label: string;
    title: string;
    ValuComponent: JSX.Element;
};

const SettingDetails = ({ label, title, ValuComponent }: Props) => {
    return (
        <AccordionDetails key={label} title={title}>
            <div>{label}</div>
            <div style={{ alignSelf: "flex-end" }}>{ValuComponent}</div>
        </AccordionDetails>
    );
};

export default SettingDetails;
