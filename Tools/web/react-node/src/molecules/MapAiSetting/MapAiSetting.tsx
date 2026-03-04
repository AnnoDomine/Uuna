import SettingDetails from "../../atoms/SettingDetails/SettingDetails";
import SettingInput from "../../atoms/SettingInput/SettingInput";
import SettingSelect from "../../atoms/SettingSelect/SettingSelect";
import { ALL_SETTING_LABELS, SETTING_TITLES } from "../../organisms/Settings/settings.constants";
import useMapAiSetting from "./mapAiSetting.hooks";

const MapAiSetting = () => {
    const { aiSetting } = useMapAiSetting();
    return (
        <>
            <SettingDetails
                label={ALL_SETTING_LABELS.num_thread}
                title={SETTING_TITLES.num_thread}
                ValuComponent={
                    <SettingInput<"ai">
                        setting="ai"
                        field="num_thread"
                        value={aiSetting.num_thread}
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
                label={ALL_SETTING_LABELS.num_ctx}
                title={SETTING_TITLES.num_ctx}
                ValuComponent={
                    <SettingInput<"ai">
                        setting="ai"
                        field="num_ctx"
                        value={aiSetting.num_ctx}
                        type="number"
                        slotProps={{
                            input: {
                                min: 16,
                                max: 65536,
                                step: 16,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.num_gpu}
                title={SETTING_TITLES.num_gpu}
                ValuComponent={
                    <SettingInput<"ai">
                        setting="ai"
                        field="num_gpu"
                        value={aiSetting.num_gpu}
                        type="number"
                        slotProps={{
                            input: {
                                min: 0,
                                max: 99,
                                step: 1,
                            },
                        }}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.acceleration_mode}
                title={SETTING_TITLES.acceleration_mode}
                ValuComponent={
                    <SettingSelect<"ai">
                        setting="ai"
                        field="acceleration_mode"
                        value={aiSetting.acceleration_mode.toString()}
                        options={[
                            {
                                value: "hybrid",
                                label: "Hybrid",
                            },
                            {
                                value: "cpu",
                                label: "CPU",
                            },
                            {
                                value: "gpu",
                                label: "GPU",
                            },
                        ]}
                    />
                }
            />
            <SettingDetails
                label={ALL_SETTING_LABELS.memory_limit}
                title={SETTING_TITLES.memory_limit}
                ValuComponent={
                    <SettingInput<"ai">
                        setting="ai"
                        field="memory_limit"
                        value={aiSetting.memory_limit}
                        type="number"
                        slotProps={{
                            input: {
                                min: 0,
                                max: 16,
                                step: 1,
                            },
                        }}
                    />
                }
            />
        </>
    );
};

export default MapAiSetting;
