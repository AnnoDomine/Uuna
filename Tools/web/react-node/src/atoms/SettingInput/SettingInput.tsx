import { Input, type InputProps } from "@mui/joy";
import { useCallback, useState } from "react";
import { changeSettings } from "../../redux/slices/settings";
import { useAppDispatch } from "../../redux/store";
import type {
    ChangeSettingActionPayload,
    ReduxSettingsState,
} from "../../redux/types/settings.types";

type Props<Setting extends keyof ReduxSettingsState> = ChangeSettingActionPayload<Setting> &
    InputProps;

const SettingInput = <Setting extends keyof ReduxSettingsState>({
    setting,
    field,
    value,
    type,
    ...props
}: Props<Setting>) => {
    const [v, setV] = useState(value as string);
    const dispatch = useAppDispatch();

    const handleChangeSetting = useCallback(
        (value: ChangeSettingActionPayload<Setting>["value"]) => {
            dispatch(changeSettings({ field, setting, value } as ChangeSettingActionPayload));
        },
        [dispatch, field, setting],
    );

    return (
        <Input
            variant="outlined"
            color="neutral"
            value={v}
            onChange={(e) => {
                setV(e.target.value);
                handleChangeSetting(e.target.value as ChangeSettingActionPayload<Setting>["value"]);
            }}
            type={type}
            {...props}
        />
    );
};

export default SettingInput;
