import { useMemo } from "react";
import useDebugStore from "../../store/useDebbugStore.js";

const useLogTable = () => {
    const { log } = useDebugStore();

    /**
     * Combine all logs, sort them from yungest to oldes and only return the first 10 rows.
     */
    const logs = useMemo(() => {
        const parsedDebugLogs = log.map((l) => {
            let combinedMessage = `${l.type} | ${l.process || "no process"} | ${l.message}`;
            if (combinedMessage.length > 40) {
                combinedMessage = `${combinedMessage.slice(0, 37)}...`;
            }
            return {
                timestamp: l.timestamp,
                message: combinedMessage,
                from: "APP",
            };
        });
        const combinedLogs = [...parsedDebugLogs].sort((a, b) => b.timestamp - a.timestamp);
        return combinedLogs
            .map((l) => ({ ...l, timestamp: new Date(l.timestamp).toLocaleString() }))
            .slice(0, 10);
    }, [log]);

    return { logs };
};

export default useLogTable;
