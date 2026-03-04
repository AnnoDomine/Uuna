import { Accordion, AccordionGroup, AccordionSummary, Button } from "@mui/joy";
import SettingIcons from "../../atoms/SettingIcons/SettingIcons";
import type { SettingsObj } from "../../redux/types/settings.types";
import MapSettings from "../MapSettings/MapSettings";
import { SETTING_LABELS } from "./settings.constants";
import useSettings from "./settings.hooks";

const Settings = () => {
    const { settings, handleSaveSetting } = useSettings();
    return (
        <AccordionGroup>
            {Object.keys(settings || {}).map((setting) => (
                <Accordion key={SETTING_LABELS[setting as keyof typeof SETTING_LABELS] || setting}>
                    <AccordionSummary>
                        <SettingIcons setting={setting as keyof SettingsObj} />
                        {SETTING_LABELS[setting as keyof typeof SETTING_LABELS] || setting}
                    </AccordionSummary>
                    <MapSettings setting={setting as keyof SettingsObj} />
                </Accordion>
            ))}
            <Button onClick={handleSaveSetting} sx={{ mx: 2, mt: 3 }}>
                Save
            </Button>
        </AccordionGroup>
    );
};

export default Settings;
