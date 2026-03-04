import SettingDetails from "../../atoms/SettingDetails/SettingDetails";
import SettingInput from "../../atoms/SettingInput/SettingInput";
import { ALL_SETTING_LABELS, SETTING_TITLES } from "../../organisms/Settings/settings.constants";
import { getTasksSettings } from "../../redux/slices/settings";
import { useAppSelector } from "../../redux/store";

const MapTasksSetting = () => {
    const tasksSetting = useAppSelector(getTasksSettings);
    return (
        <>
            <SettingDetails
                label={ALL_SETTING_LABELS.max_events_total}
                title={SETTING_TITLES.max_events_total}
                ValuComponent={
                    <SettingInput<"tasks">
                        setting="tasks"
                        field="max_events_total"
                        value={tasksSetting.max_events_total as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 1,
                                max: 500,
                                step: 1,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.max_tries_archivist}
                title={SETTING_TITLES.max_tries_archivist}
                ValuComponent={
                    <SettingInput<"tasks">
                        setting="tasks"
                        field="max_tries_archivist"
                        value={tasksSetting.max_tries_archivist as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 1,
                                max: 500,
                                step: 1,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.max_tries_cartorapher}
                title={SETTING_TITLES.max_tries_cartorapher}
                ValuComponent={
                    <SettingInput<"tasks">
                        setting="tasks"
                        field="max_tries_cartorapher"
                        value={tasksSetting.max_tries_cartorapher as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 1,
                                max: 500,
                                step: 1,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.max_tries_expedition_group}
                title={SETTING_TITLES.max_tries_expedition_group}
                ValuComponent={
                    <SettingInput<"tasks">
                        setting="tasks"
                        field="max_tries_expedition_group"
                        value={tasksSetting.max_tries_expedition_group as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 1,
                                max: 500,
                                step: 1,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.max_tries_sentinel}
                title={SETTING_TITLES.max_tries_sentinel}
                ValuComponent={
                    <SettingInput<"tasks">
                        setting="tasks"
                        field="max_tries_sentinel"
                        value={tasksSetting.max_tries_sentinel as number}
                        type="number"
                        slotProps={{
                            input: {
                                min: 1,
                                max: 500,
                                step: 1,
                            },
                        }}
                    />
                }
            />
        </>
    );
};

export default MapTasksSetting;
