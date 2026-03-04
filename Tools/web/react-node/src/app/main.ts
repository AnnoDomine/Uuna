import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import bodyParser from "body-parser";
import cors from "cors";
import { app, BrowserWindow, ipcMain } from "electron";
import {
    installExtension,
    REACT_DEVELOPER_TOOLS,
    REDUX_DEVTOOLS,
} from "electron-devtools-installer";
import express from "express";
import { GLOBAL } from "../utils/global.constants.ts";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SETTINGS_STORE_SETTTINGSFALLBACK = {
    ai: {
        num_thread: 10,
        num_ctx: 4096,
        num_gpu: 99,
        acceleration_mode: "gpu",
        memory_limit: 3,
    },
    ingestion: {
        workers: 8,
        threads: 4,
        limit_per_build: 1000,
        sync_builds_on_startup: true,
    },
    analysis: {
        use_global_mapping: false,
        auto_skip_unidentifiable: false,
    },
    system: {
        debug: true,
        localisation: "german",
        ui_theme: "light",
        cooldown: 4.0,
    },
    tasks: {
        max_events_total: 80,
        max_tries_archivist: 6,
        max_tries_cartorapher: 3,
        max_tries_expedition_group: 5,
        max_tries_sentinel: 3,
    },
};
const expressApp = express();

expressApp.use(bodyParser.json());
expressApp.use(cors());

function startExpressServer(mainWindow: BrowserWindow) {
    expressApp.post("/webhook", (req: express.Request, res: express.Response) => {
        const data = req.body;

        console.log("========= LOG DATA REQUEST BODEY =========");
        console.table(data);
        console.log("========= LOG DATA REQUEST BODEY =========");

        mainWindow.webContents.send("webhook-data", data);

        res.status(200).send({ status: "received" });
    });
    expressApp.get("/health", (_req: express.Request, res: express.Response) =>
        res.status(200).send({ status: "online" }),
    );

    expressApp.listen(GLOBAL.EXPRESS_PORT, () => {
        console.log(`Express server läuft auf ${GLOBAL.EXPRESS_URL}`);
    });
}

function createWindow() {
    console.log({ dirname: __dirname });
    console.log({ getAppPath: app.getAppPath() });
    console.log({ resourcesPath: process.resourcesPath });

    const preloadPath = path.join(__dirname, "preload.js");

    const win = new BrowserWindow({
        webPreferences: {
            preload: preloadPath,
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    if (process.env.VITE_DEV_SERVER_URL) {
        win.loadURL(process.env.VITE_DEV_SERVER_URL);
        win.webContents.toggleDevTools();
    } else {
        win.loadFile(path.join(__dirname, "../dist/index.html"));
    }

    startExpressServer(win);
}

ipcMain.handle("write-settings", async (_event, log) => {
    const fullPath = path.join(__dirname, "./settings.json");
    try {
        console.log("Write settings to file", log)
        await fs.access(fullPath);
        await fs.writeFile(fullPath, `${log}\n`);
    } catch (error) {
        console.error(error);
    }
});

ipcMain.handle("get-settings", async () => {
    const fullPath = path.join(__dirname, "./settings.json");
    try {
        console.log("Read settings from file")
        await fs.access(fullPath);
        const data = await fs.readFile(fullPath, "utf-8");
        console.log("Read settings from file", data)
        return JSON.parse(data);
    } catch (error) {
        console.error(error);
        await fs.writeFile(fullPath, JSON.stringify(SETTINGS_STORE_SETTTINGSFALLBACK, null, 2));
        return SETTINGS_STORE_SETTTINGSFALLBACK;
    }
});

ipcMain.handle("write-log", async (_event, log) => {
    const fullPath = path.join(__dirname, "./logs.log");
    try {
        console.log("Write log to file", log)
        await fs.access(fullPath);
        await fs.appendFile(fullPath, `${log}\n`);
    } catch (error) {
        console.error(error);
    }
});

ipcMain.handle("get-logs", async () => {
    const fullPath = path.join(__dirname, "./logs.log");
    try {
        console.log("Read logs from file")
        await fs.access(fullPath);
        const data = (await fs.readFile(fullPath, "utf-8")).split("\n");
        console.log("Read logs from file", data)
        return data;
    } catch (error) {
        console.error(error);
        await fs.writeFile(fullPath, JSON.stringify("", null, 2));
        return [];
    }
});

ipcMain.on("open-dev-tools", (event) => {
    const webContents = event.sender;
    webContents.openDevTools();
});

app.whenReady().then(() => {
    installExtension([REDUX_DEVTOOLS, REACT_DEVELOPER_TOOLS])
        .then(([redux, react]) => console.log(`Added Extensions:  ${redux.name}, ${react.name}`))
        .catch((err) => console.log("An error occurred: ", err));
    createWindow();
});
