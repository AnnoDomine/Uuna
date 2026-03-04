import { MenuItem, Select, styled } from "@mui/joy";
import clsx from "clsx";
import useBuildBelection from "./buildSelection.hooks";

const BuildFetchIndicator = ({
    state,
    refetch,
}: {
    state: Record<"isLoading" | "isErrored" | "isSucceeded", boolean>;
    refetch: () => void;
}) => {
    switch (true) {
        case state.isLoading:
            return <div>Builds Loading...</div>;
        case state.isErrored:
            return (
                <div>
                    Builds Error...{" "}
                    <button type="button" onClick={refetch}>
                        Refetch
                    </button>
                </div>
            );
        case state.isSucceeded:
            return <div>Builds Success!</div>;
        default:
            return (
                <div>
                    <button type="button" onClick={refetch}>
                        Refetch
                    </button>
                </div>
            );
    }
};

const BuildItem = styled(MenuItem)(({ theme }) => ({
    color: theme.palette.text.primary,
    "&.unfetched": {
        color: theme.palette.danger[500],
    },
    "&.unindexed": {
        color: theme.palette.warning[500],
    },
    "&.selected": {
        color: theme.palette.success[500],
    },
}));

const BuildSelection = () => {
    const {
        builds,
        selectedBuilds,
        handleSelection,
        handleRefetch,
        isLoading,
        isErrored,
        isSucceeded,
        handleSelectAll,
        handleUnselectAll,
    } = useBuildBelection();

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", width: "100%" }}>
            <BuildFetchIndicator
                state={{ isLoading, isErrored, isSucceeded }}
                refetch={handleRefetch}
            />
            {selectedBuilds.length > 0 && (
                <div>
                    <ul>
                        {selectedBuilds.slice(0, 2).map((build) => (
                            <li key={build.version}>{build.version}</li>
                        ))}
                        {selectedBuilds.length > 2 && <li>...</li>}
                    </ul>
                </div>
            )}
            <Select>
                {selectedBuilds.length !== builds.length && (
                    <MenuItem key="select-all" onClick={handleSelectAll}>
                        Select All
                    </MenuItem>
                )}
                <MenuItem key="unselect-all" onClick={handleUnselectAll}>
                    Unselect All
                </MenuItem>
                {builds.map((build) => (
                    <BuildItem
                        className={clsx({
                            unfetched: !build.is_downloaded,
                            unindexed: !build.indexed,
                            selected: selectedBuilds.map((b) => b.version).includes(build.version),
                        })}
                        key={build.version}
                        disabled={!build.indexed || !build.is_downloaded}
                        onClick={() => handleSelection(build.version)}
                    >
                        {build.version}
                    </BuildItem>
                ))}
            </Select>
        </div>
    );
};

export default BuildSelection;
