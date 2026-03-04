import { Option, Select } from "@mui/joy";
import { useCallback, useState } from "react";
import { changeSettings } from "../../redux/slices/settings";
import { useAppDispatch } from "../../redux/store";
import type {
    ChangeSettingActionPayload,
    ReduxSettingsState,
    StringSettings,
} from "../../redux/types/settings.types";

type Props<Setting extends keyof ReduxSettingsState> = Omit<
    ChangeSettingActionPayload<Setting>,
    "field" | "value"
> & {
    options: Array<Record<"label" | "value", string>>;
    field: StringSettings;
    value: string;
};

const SettingSelect = <Setting extends keyof ReduxSettingsState>({
    options,
    setting,
    field,
    value,
}: Props<Setting>) => {
    const [v, setV] = useState(value);
    const dispatch = useAppDispatch();
    const handleChangeSetting = useCallback(
        (value: string) => {
            setV(value);
            dispatch(
                changeSettings({
                    field: field as ChangeSettingActionPayload["field"],
                    value: value as ChangeSettingActionPayload["value"],
                    setting,
                }),
            );
        },
        [dispatch, field, setting],
    );
    return (
        <Select
            variant="outlined"
            color="neutral"
            value={v}
            onChange={(_e, v) => handleChangeSetting(v || "")}
        >
            {options.map((o) => (
                <Option key={o.value} value={o.value}>
                    {o.label}
                </Option>
            ))}
        </Select>
    );
};

export default SettingSelect;
