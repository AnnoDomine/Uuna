import { useEffect, useMemo } from "react";
import type { Item } from "../../molecules/ScrollableSelection/ScrollableSelection.js";
import useBuildsStore from "../../store/useBuildsStore.js";
import useDebugStore from "../../store/useDebugStore.js";
import { ELogTypes } from "../../types/global.enums.js";

const useSelectBuild = () => {
    const { builds, isLoading, isFetching, isUninitialised, isErrored, error, fetchBuilds } =
        useBuildsStore();
    const { addLog } = useDebugStore();

    const isLoadingBuilds = isLoading || isFetching || isUninitialised;

    const parsedBuilds = useMemo((): Item<(typeof builds)[number]>[] => {
        addLog({
            message: JSON.stringify(builds),
            process: "useSelectBuild-parsedBuilds",
            type: ELogTypes.INFO,
        });
        return (builds || []).map(
            (b): Item<(typeof builds)[number]> => ({
                id: b.version,
                value: b.version,
                label: b.version,
                meta: b,
            }),
        );
    }, [builds, addLog]);

    useEffect(() => {
        if (isUninitialised) fetchBuilds();
    }, [fetchBuilds, isUninitialised]);

    return {
        parsedBuilds,
        isLoadingBuilds,
        isErrored,
        error,
    };
};

export default useSelectBuild;
