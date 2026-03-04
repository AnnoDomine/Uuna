import { getAiSettings } from "../../redux/slices/settings";
import { useAppSelector } from "../../redux/store";

const useMapAiSetting = () => {
    const aiSetting = useAppSelector(getAiSettings);

    return {
        aiSetting,
    };
};

export default useMapAiSetting;
