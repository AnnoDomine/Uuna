import SettingDetails from "../../atoms/SettingDetails/SettingDetails";
import SettingSwitch from "../../atoms/SettingSwitch/SettingSwitch";
import { ALL_SETTING_LABELS, SETTING_TITLES } from "../../organisms/Settings/settings.constants";
import { getAnalysisSettings } from "../../redux/slices/settings";
import { useAppSelector } from "../../redux/store";

const MapAnalysisSettig = () => {
    const analysisSettings = useAppSelector(getAnalysisSettings);
    return (
        <>
            <SettingDetails
                label={ALL_SETTING_LABELS.use_global_mapping}
                title={SETTING_TITLES.use_global_mapping}
                ValuComponent={
                    <SettingSwitch
                        setting="analysis"
                        field="use_global_mapping"
                        value={analysisSettings.use_global_mapping}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.auto_skip_unidentifiable}
                title={SETTING_TITLES.auto_skip_unidentifiable}
                ValuComponent={
                    <SettingSwitch
                        setting="analysis"
                        field="auto_skip_unidentifiable"
                        value={analysisSettings.auto_skip_unidentifiable}
                    />
                }
            />
        </>
    );
};

export default MapAnalysisSettig;
