import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { GLOBAL } from "../../utils/global.constants";

export type BuildItem = {
    version: string;
    is_downloaded: boolean;
    indexed: boolean;
};

export type BuildStatus = "uninitialised" | "loading" | "error" | "fullfilled";

export const initializeBuilds = createAsyncThunk("builds/initializeBuilds", async () => {
    try {
        const res = await fetch(`${GLOBAL.VECTOR_DB_URL}/builds/list/all`);
        const data: { builds: BuildItem[] } = await res.json();
        return data.builds;
    } catch (err) {
        console.error(err);
        return [];
    }
});

const buildsSlice = createSlice({
    name: "builds",
    initialState: {
        builds: [] as BuildItem[],
        selected: [] as BuildItem[],
        buildFetchStatus: "uninitialised" as BuildStatus,
    },
    reducers: {
        selectBuild: (state, action: PayloadAction<BuildItem["version"]>) => {
            const build = state.builds.find((build) => build.version === action.payload);
            if (!build) return;
            if (state.selected.includes(build)) return;
            state.selected.push(build);
        },
        deselectBuild: (state, action: PayloadAction<BuildItem["version"]>) => {
            const build = state.builds.find((build) => build.version === action.payload);
            if (!build) return;
            if (!state.selected.includes(build)) return;
            state.selected = state.selected.filter((b) => build.version !== b.version);
        },
        refetchBuilds: (state) => {
            state.buildFetchStatus = "uninitialised";
        },
        unselectAll: (state) => {
            state.selected = [];
        },
        selectAll: (state) => {
            state.selected = state.builds;
        },
    },
    extraReducers: (builder) => ({
        initializeBuilds: builder.addAsyncThunk(initializeBuilds, {
            fulfilled: (state, action: PayloadAction<BuildItem[]>) => {
                state.builds = action.payload;
                state.buildFetchStatus = "fullfilled";
            },
            rejected: (state, action) => {
                console.error(action.error);
                state.builds = [];
                state.buildFetchStatus = "error";
            },
            pending: (state) => {
                state.buildFetchStatus = "loading";
            },
        }),
    }),
    selectors: {
        getBuildsStore: (state) => state,
        getFetchStatus: (state) => ({
            isUnintiualised: state.buildFetchStatus === "uninitialised",
            isLoading: state.buildFetchStatus === "loading",
            isErrored: state.buildFetchStatus === "error",
            isSucceeded: state.buildFetchStatus === "fullfilled",
        }),
    },
});

export const { selectBuild, deselectBuild, refetchBuilds, unselectAll, selectAll } =
    buildsSlice.actions;
export const { getBuildsStore, getFetchStatus } = buildsSlice.selectors;
export default buildsSlice;
