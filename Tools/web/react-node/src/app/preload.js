const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
    getSettings: () => ipcRenderer.invoke("get-settings"),
    getLogs: () => ipcRenderer.invoke("get-logs"),
    writeLog: (log) => ipcRenderer.invoke("write-log", log),
    writeSettings: (log) => ipcRenderer.invoke("write-settings", log),
    onWebhookReceived: (callback) => {
        const subscription = (_event, value) => {
            console.log("Receive signal from express backend.");
            console.log(value);
            callback(value);
        };
        ipcRenderer.on("webhook-data", subscription);
        return () => ipcRenderer.removeListener("webhook-data", subscription);
    },
    openConsole: () => ipcRenderer.send("open-dev-tools"),
});
