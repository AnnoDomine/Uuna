import SettingDetails from "../../atoms/SettingDetails/SettingDetails";
import SettingInput from "../../atoms/SettingInput/SettingInput";
import SettingSelect from "../../atoms/SettingSelect/SettingSelect";
import SettingSwitch from "../../atoms/SettingSwitch/SettingSwitch";
import { ALL_SETTING_LABELS, SETTING_TITLES } from "../../organisms/Settings/settings.constants";
import { getSystemSettings } from "../../redux/slices/settings";
import { useAppSelector } from "../../redux/store";
import { LANGUAGES, SYSTEM_MODES } from "./mapSystemSetting.constants";

const MapSystemSetting = () => {
    const systemSetting = useAppSelector(getSystemSettings);
    return (
        <>
            <SettingDetails
                label={ALL_SETTING_LABELS.debug}
                title={SETTING_TITLES.debug}
                ValuComponent={
                    <SettingSwitch setting="system" field="debug" value={systemSetting.debug} />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.localisation}
                title={SETTING_TITLES.localisation}
                ValuComponent={
                    <SettingSelect<"system">
                        setting="system"
                        field="localisation"
                        value={systemSetting.localisation as string}
                        options={LANGUAGES}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.ui_theme}
                title={SETTING_TITLES.ui_theme}
                ValuComponent={
                    <SettingSelect<"system">
                        setting="system"
                        field="ui_theme"
                        value={systemSetting.ui_theme as string}
                        options={SYSTEM_MODES}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.cooldown}
                title={SETTING_TITLES.cooldown}
                ValuComponent={
                    <SettingInput<"system">
                        setting="system"
                        field="cooldown"
                        value={systemSetting.cooldown as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 0.0,
                                max: 10.0,
                                step: 0.1,
                            },
                        }}
                    />
                }
            />
        </>
    );
};

export default MapSystemSetting;
