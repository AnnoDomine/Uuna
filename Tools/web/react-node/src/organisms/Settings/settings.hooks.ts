import { useCallback, useEffect } from "react";
import { getSettings, saveSettings } from "../../redux/slices/settings";
import { useAppDispatch, useAppSelector } from "../../redux/store";
import { fetchSettingsJson } from "../../redux/actions/settings";

const useSettings = () => {
    const dispatch = useAppDispatch();
    const settings = useAppSelector(getSettings);

    const handleSaveSetting = useCallback(() => {
        dispatch(saveSettings());
    }, [dispatch]);

    useEffect(() => {
        dispatch(fetchSettingsJson())
    }, [dispatch])

    return {
        settings,
        handleSaveSetting,
    };
};

export default useSettings;
