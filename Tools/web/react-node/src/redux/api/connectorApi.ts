import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { GLOBAL } from "../../utils/global.constants.ts";

const connectorApi = createApi({
    reducerPath: "connector",
    baseQuery: fetchBaseQuery(),
    keepUnusedDataFor: 0,
    endpoints: (b) => ({
        checkExpress: b.query<void, void>({
            query: () => ({
                url: `${GLOBAL.EXPRESS_URL}/health`,
                headers: {
                    "Content-Type": "application/json",
                },
                method: "GET",
            }),
        }),
        checkDbConnection: b.query<void, void>({
            query: () => ({
                url: `${GLOBAL.DB_URL}/health`,
                headers: {
                    "Content-Type": "application/json",
                },
                method: "GET",
            }),
        }),
        checkVectorDbConnection: b.query<void, void>({
            query: () => ({
                url: `${GLOBAL.VECTOR_DB_URL}/health`,
                headers: {
                    "Content-Type": "application/json",
                },
                method: "GET",
            }),
        }),
    }),
});

export const { useCheckExpressQuery, useCheckDbConnectionQuery, useCheckVectorDbConnectionQuery } =
    connectorApi;

export default connectorApi;
