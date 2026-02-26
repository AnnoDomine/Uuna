import axios from "axios";
import { create } from "zustand";
import { ELogTypes } from "../types/global.enums.js";
import { API_BASE_URL } from "../utils/constants/globals.js";
import { DEFAULT_LOADING_STATES, type LoadingStates } from "./defaultLoadingStates.js";
import useDebugStore from "./useDebugStore.js";

export type BuildItem = {
    version: string;
    is_downloaded: boolean;
    indexed: boolean;
};

type BuildsStore = {
    builds: BuildItem[];
    fetchBuilds: () => Promise<void>;
};

export const useBuildsStore = create<LoadingStates<BuildsStore>>((set, get) => ({
    ...DEFAULT_LOADING_STATES,
    builds: [],
    fetchBuilds: async () => {
        const { addLog } = useDebugStore.getState();
        const haveItems = get().isUninitialised;
        set({
            isLoading: !haveItems,
            isErrored: false,
            error: null,
            isSucceeded: false,
            isFetching: true,
        });
        try {
            const res = await axios.get<{ builds: BuildItem[] }>(`${API_BASE_URL}/builds/list/all`);
            const { data } = res;
            await addLog({
                message: JSON.stringify(data),
                type: ELogTypes.TRACE,
                process: "fetchBuilds-res.data",
            });
            set({ builds: data.builds, isSucceeded: true });
        } catch (err) {
            console.error(err);
            set({
                isErrored: true,
                error: JSON.stringify(err),
                isSucceeded: false,
            });
            addLog({
                message: JSON.stringify(err),
                type: ELogTypes.ERROR,
                process: "fetchBuilds-error",
            });
        } finally {
            set({
                isLoading: false,
                isFetching: false,
                isUninitialised: false,
            });
        }
    },
}));

export default useBuildsStore;
