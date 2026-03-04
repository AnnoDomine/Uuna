import { Switch } from "@mui/joy";
import { useCallback, useState } from "react";
import { changeSettings } from "../../redux/slices/settings";
import { useAppDispatch } from "../../redux/store";
import type {
    ChangeSettingActionPayload,
    ReduxSettingsState,
} from "../../redux/types/settings.types";

type Props<Setting extends keyof ReduxSettingsState> = ChangeSettingActionPayload<Setting>;

const SettingSwitch = <Setting extends keyof ReduxSettingsState>({
    setting,
    field,
    value,
}: Props<Setting>) => {
    const [v, setV] = useState(value as boolean);
    const dispatch = useAppDispatch();

    const handleChangeSetting = useCallback(
        (value: ChangeSettingActionPayload<Setting>["value"]) => {
            dispatch(changeSettings({ field, setting, value } as ChangeSettingActionPayload));
        },
        [dispatch, field, setting],
    );
    return (
        <Switch
            checked={v}
            onChange={(e) => {
                setV(e.target.checked);
                handleChangeSetting(
                    e.target.checked as ChangeSettingActionPayload<Setting>["value"],
                );
            }}
        />
    );
};

export default SettingSwitch;
