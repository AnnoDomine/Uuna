type FrontendSignal = {
    task_id: string;
    agent: string;
    message: string;
    type: "research" | "response" | "error";
    level: string;
    task_context?: object;
};

export interface IElectronAPI {
    getSettings: () => Promise<unknown>;
    getLogs: () => Promise<string[]>;
    writeLog: (log: string) => Promise<void>;
    writeSettings: (log: string) => Promise<void>;
    openConsole: () => void;
    onWebhookReceived: (callback: (data: FrontendSignal) => void) => () => void;
}

declare global {
    interface Window {
        electronAPI: IElectronAPI;
    }
}
