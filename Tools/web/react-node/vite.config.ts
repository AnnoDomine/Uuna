import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import electron from "vite-plugin-electron";

// https://vite.dev/config/
export default defineConfig({
    define: {},
    plugins: [
        react(),
        electron([
            {
                // Main-Process entry file of the Electron App.
                entry: "src/app/main.ts",
                onstart(options) {
                    options.startup(["."]);
                },
            },
            {
                entry: "src/app/preload.js",
                onstart(options) {
                    options.reload();
                },
            }
        ]),
    ],
});
