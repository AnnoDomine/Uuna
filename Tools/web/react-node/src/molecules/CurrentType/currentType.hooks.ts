import { getCurrentType } from "../../redux/slices/ai";
import { useAppSelector } from "../../redux/store";

const useCurrentType = () => {
    const currentType = useAppSelector(getCurrentType);

    return {
        currentType,
    };
};

export default useCurrentType;
