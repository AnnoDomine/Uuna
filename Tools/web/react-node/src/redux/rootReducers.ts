import { combineSlices } from "@reduxjs/toolkit";
import aiApi from "./api/aiApi";
import connectorApi from "./api/connectorApi";
import tasksApi from "./api/tasksApi";
import aiSlice from "./slices/ai";
import buildsSlice from "./slices/builds";
import loggerSlice from "./slices/logger";
import settingsSlice from "./slices/settings";

const rootReducers = combineSlices({
    [aiSlice.name]: aiSlice.reducer,
    [connectorApi.reducerPath]: connectorApi.reducer,
    [settingsSlice.name]: settingsSlice.reducer,
    [aiApi.reducerPath]: aiApi.reducer,
    [loggerSlice.name]: loggerSlice.reducer,
    [buildsSlice.name]: buildsSlice.reducer,
    [tasksApi.reducerPath]: tasksApi.reducer,
});

export default rootReducers;
