import SettingDetails from "../../atoms/SettingDetails/SettingDetails";
import SettingInput from "../../atoms/SettingInput/SettingInput";
import SettingSwitch from "../../atoms/SettingSwitch/SettingSwitch";
import { ALL_SETTING_LABELS, SETTING_TITLES } from "../../organisms/Settings/settings.constants";
import { getIngestionSettings } from "../../redux/slices/settings";
import { useAppSelector } from "../../redux/store";

const MapIngestionSetting = () => {
    const ingestionSetting = useAppSelector(getIngestionSettings);
    return (
        <>
            <SettingDetails
                label={ALL_SETTING_LABELS.workers}
                title={SETTING_TITLES.workers}
                ValuComponent={
                    <SettingInput<"ingestion">
                        setting="ingestion"
                        field="workers"
                        value={ingestionSetting.workers as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 1,
                                max: 16,
                                step: 1,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.threads}
                title={SETTING_TITLES.threads}
                ValuComponent={
                    <SettingInput<"ingestion">
                        setting="ingestion"
                        field="threads"
                        value={ingestionSetting.threads as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 1,
                                max: 16,
                                step: 1,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.limit_per_build}
                title={SETTING_TITLES.limit_per_build}
                ValuComponent={
                    <SettingInput<"ingestion">
                        setting="ingestion"
                        field="limit_per_build"
                        value={ingestionSetting.limit_per_build as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 100,
                                max: 8000,
                                step: 100,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.sync_builds_on_startup}
                title={SETTING_TITLES.sync_builds_on_startup}
                ValuComponent={
                    <SettingSwitch
                        setting="ingestion"
                        field="sync_builds_on_startup"
                        value={ingestionSetting.sync_builds_on_startup}
                    />
                }
            />
        </>
    );
};

export default MapIngestionSetting;
