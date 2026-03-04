import { getCurrentLevel } from "../../redux/slices/ai";
import { useAppSelector } from "../../redux/store";

const useCurrentLevel = () => {
    const currentLevel = useAppSelector(getCurrentLevel);

    return {
        currentLevel,
    };
};

export default useCurrentLevel;
