import type { Middleware } from "@reduxjs/toolkit";
import aiApi from "./api/aiApi";
import connectorApi from "./api/connectorApi";
import tasksApi from "./api/tasksApi";

const rootMiddleware = [
    connectorApi.middleware,
    aiApi.middleware,
    tasksApi.middleware,
] as Middleware[];

export default rootMiddleware;
