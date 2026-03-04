import { useCallback, useEffect, useMemo } from "react";
import {
    deselectBuild,
    getBuildsStore,
    getFetchStatus,
    initializeBuilds,
    refetchBuilds,
    selectAll,
    selectBuild,
    unselectAll,
} from "../../redux/slices/builds";
import { useAppDispatch, useAppSelector } from "../../redux/store";

const useBuildBelection = () => {
    const dispatch = useAppDispatch();
    const buildsStore = useAppSelector(getBuildsStore);
    const { isUnintiualised, isLoading, isErrored, isSucceeded } = useAppSelector(getFetchStatus);

    const builds = useMemo(() => buildsStore.builds, [buildsStore.builds]);

    const selectedBuilds = useMemo(() => buildsStore.selected, [buildsStore.selected]);

    const handleSelection = useCallback(
        (build: string) => {
            if (selectedBuilds.map((b) => b.version).includes(build)) {
                dispatch(deselectBuild(build));
            } else {
                dispatch(selectBuild(build));
            }
        },
        [dispatch, selectedBuilds],
    );

    const handleSelectAll = useCallback(() => {
        dispatch(selectAll());
    }, [dispatch]);

    const handleUnselectAll = useCallback(() => {
        dispatch(unselectAll());
    }, [dispatch]);

    const handleRefetch = useCallback(() => {
        if (isLoading) {
            return;
        }
        dispatch(refetchBuilds());
    }, [dispatch, isLoading]);

    useEffect(() => {
        if (isUnintiualised) {
            dispatch(initializeBuilds());
        }
    }, [dispatch, isUnintiualised]);

    return {
        builds,
        selectedBuilds,
        handleSelection,
        handleRefetch,
        isLoading,
        isErrored,
        isSucceeded,
        handleSelectAll,
        handleUnselectAll,
    };
};

export default useBuildBelection;
