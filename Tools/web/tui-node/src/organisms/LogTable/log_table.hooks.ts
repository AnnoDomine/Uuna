import { useCallback, useMemo } from "react";
import useDebugStore from "../../store/useDebugStore.js";

const useLogTable = () => {
    const { log } = useDebugStore();

    const convertTimestampToTime = useCallback((timestamp: number) => {
        const date = new Date(timestamp);
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");
        const seconds = date.getSeconds().toString().padStart(2, "0");
        return `${hours}:${minutes}:${seconds}`;
    }, []);

    /**
     * Combine all logs, sort them from yungest to oldes and only return the rows.
     */
    const logs = useMemo(() => {
        const parsedDebugLogs = log.map((l) => {
            const combinedMessage = `${l.type} | ${l.process || "no process"} | ${l.message}`;
            // if (combinedMessage.length > 25) {
            // 	combinedMessage = `${combinedMessage.slice(0, 22)}...`;
            // }
            return {
                timestamp: l.timestamp,
                message: combinedMessage,
            };
        });
        const combinedLogs = [...parsedDebugLogs].sort((a, b) => b.timestamp - a.timestamp);
        return combinedLogs.map((l) => ({
            ...l,
            timestamp: convertTimestampToTime(l.timestamp),
        }));
    }, [log, convertTimestampToTime]);

    return { logs };
};

export default useLogTable;
