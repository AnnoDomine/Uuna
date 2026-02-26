export type LoadingStates<ST> = ST & {
    isUninitialised: boolean;
    isLoading: boolean;
    isFetching: boolean;
    isSucceeded: boolean;
    isErrored: boolean;
    error: string | null;
};
// biome-ignore lint/complexity/noBannedTypes: Only for typing reason
export const DEFAULT_LOADING_STATES: LoadingStates<{}> = {
    isUninitialised: true,
    isLoading: false,
    isFetching: false,
    isSucceeded: false,
    isErrored: false,
    error: null,
};
