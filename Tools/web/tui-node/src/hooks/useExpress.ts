import express from "express";
import { useCallback, useEffect } from "react";
import useAIStore, { type FrontendSignal } from "../store/useAIStore.js";

const DEFAULT_PORT = 3800;

const useExpress = () => {
    const { receiveSignal } = useAIStore();

    const handleSignal = useCallback(
        (signal: FrontendSignal) => {
            receiveSignal(signal);
        },
        [receiveSignal],
    );

    useEffect(() => {
        const port = process.env.TUI_SIGNAL_PORT
            ? Number.parseInt(process.env.TUI_SIGNAL_PORT, 10)
            : DEFAULT_PORT;
        const app = express();
        app.use(express.json());

        app.post("/update", (req, res) => {
            const signal: FrontendSignal = req.body;
            handleSignal(signal);
            res.sendStatus(200);
        });

        const server = app.listen(port, () => {
            console.log(`Signal receiver listening on port ${port}`);
        });

        return () => {
            server.close();
        };
    }, [handleSignal]);

    return null;
};

export default useExpress;
