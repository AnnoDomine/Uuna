import { useMemo } from "react";
import { getCurrentAgent, getCurrentLevel } from "../../redux/slices/ai";
import { useAppSelector } from "../../redux/store";

export type Steps =
    | "user"
    | "lib"
    | "cour"
    | "arch"
    | "exp"
    | "sani"
    | "cart"
    | "sage"
    | "tink"
    | "obs"
    | "system";

const useMapCurrentAgent = () => {
    const currAgent = useAppSelector(getCurrentAgent);
    const currentLevel = useAppSelector(getCurrentLevel);

    const isError = currentLevel === "error";

    const step = useMemo((): Steps => {
        if (isError) {
            return "system";
        }
        switch (currAgent.toLowerCase()) {
            case "librarian":
                return "lib";
            case "courier":
                return "cour";
            case "archiver":
            case "archivist":
                return "arch";
            case "explorer":
            case "expedition group":
            case "expedition_group":
                return "exp";
            case "sanitizer":
            case "sentinel":
                return "sani";
            case "cart":
                return "cart";
            case "sage":
            case "sages":
                return "sage";
            case "tinkerer":
                return "tink";
            case "observer":
                return "obs";
            default:
                return "system";
        }
    }, [currAgent, isError]);

    return { step, isError };
};

export default useMapCurrentAgent;
