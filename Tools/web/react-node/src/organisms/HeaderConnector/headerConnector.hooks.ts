import { useCallback, useEffect, useMemo } from "react";
import {
    useCheckDbConnectionQuery,
    useCheckExpressQuery,
    useCheckVectorDbConnectionQuery,
} from "../../redux/api/connectorApi";
import { getCurrentAgent } from "../../redux/slices/ai";
import { useAppSelector } from "../../redux/store";

const useHeaderConnector = () => {
    const {
        isSuccess: isExpressSuccess,
        isUninitialized: isExpressUninitialized,
        isFetching: isExpressFetching,
        isError: isExpressError,
        refetch: refetchExpress,
    } = useCheckExpressQuery();
    const {
        isSuccess: isDbSuccess,
        isUninitialized: isDbUninitialized,
        isFetching: isDbFetching,
        isError: isDbError,
        refetch: refetchDb,
    } = useCheckDbConnectionQuery();
    const {
        isSuccess: isVectorDbSuccess,
        isUninitialized: isVectorDbUninitialized,
        isFetching: isVectorDbFetching,
        isError: isVectorDbError,
        refetch: refetchVectorDb,
    } = useCheckVectorDbConnectionQuery();

    const currentAgent = useAppSelector(getCurrentAgent);

    const readableCurrentAgent = currentAgent
        ? currentAgent[0].toLocaleUpperCase() + currentAgent.slice(1)
        : "";

    const getConnection = useCallback((s: boolean, u: boolean, e: boolean, f: boolean) => {
        switch (true) {
            case u:
                return "idle";
            case e:
                return "error";
            case f:
                return "process";
            case s:
                return "success";
            default:
                return "idle";
        }
    }, []);

    const connections = useMemo(
        () => [
            {
                label: "Frontend-Express",
                status: getConnection(
                    isExpressSuccess,
                    isExpressUninitialized,
                    isExpressError,
                    isExpressFetching,
                ),
            },
            {
                label: "DB Connection",
                status: getConnection(isDbSuccess, isDbUninitialized, isDbError, isDbFetching),
            },
            {
                label: "Vector DB Connection",
                status: getConnection(
                    isVectorDbSuccess,
                    isVectorDbUninitialized,
                    isVectorDbError,
                    isVectorDbFetching,
                ),
            },
        ],
        [
            getConnection,
            isDbError,
            isDbFetching,
            isDbSuccess,
            isDbUninitialized,
            isExpressError,
            isExpressFetching,
            isExpressSuccess,
            isExpressUninitialized,
            isVectorDbError,
            isVectorDbFetching,
            isVectorDbSuccess,
            isVectorDbUninitialized,
        ],
    );

    useEffect(() => {
        const checkTimer = setInterval(
            () => {
                refetchExpress();
                refetchDb();
                refetchVectorDb();
            },
            1000 * 60 * 5,
        );
        return () => clearInterval(checkTimer);
    }, [refetchDb, refetchExpress, refetchVectorDb]);

    useEffect(() => {
        const init = setTimeout(() => {
            refetchExpress();
            refetchDb();
            refetchVectorDb();
        }, 1000 * 5);
        return () => clearTimeout(init);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [refetchDb, refetchExpress, refetchVectorDb]);

    return {
        connections,
        readableCurrentAgent,
        currentAgent,
    };
};

export default useHeaderConnector;
