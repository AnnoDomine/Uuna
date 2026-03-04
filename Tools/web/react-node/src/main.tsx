import { StrictMode } from "react";
import { type Container, createRoot } from "react-dom/client";
import "./index.css";
import { Provider } from "react-redux";
import App from "./App.tsx";
import store from "./redux/store.ts";

createRoot(document.getElementById("root") as Container).render(
    <StrictMode>
        <Provider store={store}>
            <App />
        </Provider>
    </StrictMode>,
);
