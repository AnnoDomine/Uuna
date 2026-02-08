import { useCallback, useEffect } from "react";
import useDebugStore from "../store/useDebbugStore.js";
import { useStore } from "../store/useStore.js";
import { ELogTypes } from "../types/global.enums.js";
import { REFRESH_INTERVAL } from "../utils/constants/globals.js";
import BackendService from "../utils/services/backend.service.js";

const useBackend = () => {
    const { setApiOnline, isRestarting, setRestarting } = useStore();
    const { addLog } = useDebugStore();

    const checkHealth = useCallback(async () => {
        addLog({ type: ELogTypes.DEBUG, message: "Checking backend health" });
        if (isRestarting) return;
        addLog({ type: ELogTypes.DEBUG, message: "Backend health check" });
        const isAlive = await BackendService.healthCheck();
        addLog({
            type: ELogTypes.INFO,
            message: `Backend health check result: ${isAlive}`,
        });
        setApiOnline(isAlive);

        // Auto-start if offline and not explicitly restarting
        if (!isAlive && !isRestarting) {
            addLog({
                type: ELogTypes.INFO,
                message: "Backend is offline, starting it",
            });
            BackendService.start();
        } else {
            addLog({ type: ELogTypes.DEBUG, message: "Backend is online" });
        }
    }, [isRestarting, setApiOnline, addLog]);

    const restartBackend = async () => {
        setRestarting(true);
        setApiOnline(false);
        addLog({ type: ELogTypes.INFO, message: "Restarting backend" });
        await BackendService.restart();
        // Give it some time to boot
        setTimeout(() => {
            setRestarting(false);
        }, 3000);
    };

    useEffect(() => {
        const interval = setInterval(checkHealth, REFRESH_INTERVAL);
        checkHealth(); // Initial check

        return () => clearInterval(interval);
    }, [checkHealth]);

    return { restartBackend };
};

export default useBackend;
