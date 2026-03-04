import "@fontsource/fira-code/300.css";
import "@fontsource/fira-code/400.css";
import "@fontsource/fira-code/500.css";
import "@fontsource/fira-code/600.css";
import "@fontsource/fira-code/700.css";

import "./App.css";
import { useEffect } from "react";
import Chat from "./organisms/Chat/Chat";
import Terminal from "./organisms/Terminal/Terminal";
import Header from "./pages/Header/Header";
import Menu from "./pages/Menu/Menu";
import Tasks from "./pages/Tasks/Tasks";
import { receiveUpdate } from "./redux/slices/ai";
import { useAppDispatch } from "./redux/store";

function App() {
    const dispatch = useAppDispatch();

    useEffect(() => {
        console.log("Attach dispatching listener...");
        if (!window.electronAPI) {
            console.log("No electronAPI found");
            return;
        }
        console.table(window.electronAPI);
        const listener = window.electronAPI.onWebhookReceived((data) => {
            console.log("Webhook in React empfangen, dispatching an Redux...", data);

            dispatch(receiveUpdate(data));
        });
        console.log("Event listener attached");

        return () => {
            console.log(`Remove listener...`);
            listener();
        };
    }, [dispatch]);

    return (
        <>
            <div className="header">
                <Header />
            </div>
            <div className="app">
                <Chat />
            </div>
            <div className="terminal">
                <Terminal />
            </div>
            <Menu />
            <Tasks />
        </>
    );
}

export default App;
