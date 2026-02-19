import express from "express";
import { useCallback, useEffect } from "react";
import useAIStore from "../store/useAIStore.js";

const PORT = 3800;

const useExpress = () => {
    const { addChat } = useAIStore();

    const receiveMessage = useCallback(
        (message: string) => {
            addChat(message);
        },
        [addChat],
    );

    useEffect(() => {
        const app = express();
        app.use(express.json());
        app.post("/update", (req, res) => {
            const { message } = req.body;
            receiveMessage(message);
            res.sendStatus(200);
        });
        const server = app.listen(PORT, () => {
            console.log(`Express server listening on port ${PORT}`);
        });
        return () => {
            server.close();
        };
    }, [receiveMessage]);
    return null;
};

export default useExpress;
