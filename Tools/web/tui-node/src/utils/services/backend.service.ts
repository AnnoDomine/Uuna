import { type ChildProcess, spawn } from "node:child_process";
import path from "node:path";
import axios from "axios";
import useDebugStore from "../../store/useDebugStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { API_BASE_URL } from "../constants/globals.js";

class BackendService {
    private static instance: BackendService;
    private process: ChildProcess | null = null;

    private constructor() {}

    public static getInstance(): BackendService {
        if (!BackendService.instance) {
            BackendService.instance = new BackendService();
        }
        return BackendService.instance;
    }

    /**
     * Performs a health check on the Python API
     */
    public async healthCheck(): Promise<boolean> {
        const { addLog } = useDebugStore.getState();
        try {
            addLog({
                type: ELogTypes.DEBUG,
                message: "Performing backend health check",
                process: "BackendService",
            });
            const response = await axios.get(`${API_BASE_URL}/health`, {
                timeout: 1000,
            });
            const isAlive = response.status === 200;
            if (isAlive) {
                addLog({
                    type: ELogTypes.TRACE,
                    message: "Backend is healthy",
                    process: "BackendService",
                });
            }
            return isAlive;
        } catch (_error) {
            addLog({
                type: ELogTypes.WARN,
                message: "Backend health check failed",
                process: "BackendService",
            });
            return false;
        }
    }

    /**
     * Starts the Python backend process using uvicorn
     */
    public start(): void {
        const { addLog } = useDebugStore.getState();
        if (this.process) {
            addLog({
                type: ELogTypes.DEBUG,
                message: "Backend already running, skip start",
                process: "BackendService",
            });
            return;
        }

        addLog({
            type: ELogTypes.INFO,
            message: "Starting Python backend process...",
            process: "BackendService",
        });

        const tuiNodeDir = process.cwd();
        const projectRoot = path.resolve(tuiNodeDir, "../../..");
        const pythonPath = path.join(projectRoot, ".venv/bin/python3");

        this.process = spawn(
            pythonPath,
            ["-m", "uvicorn", "Tools.core.api.main:app", "--port", "8001", "--host", "127.0.0.1"],
            {
                stdio: "ignore",
                detached: true,
                cwd: projectRoot,
                env: {
                    ...process.env,
                    PYTHONPATH: projectRoot,
                },
            },
        );

        this.process.unref();
        addLog({
            type: ELogTypes.INFO,
            message: "Backend spawn initiated",
            process: "BackendService",
        });
    }

    /**
     * Stops the Python backend process
     */
    public stop(): void {
        const { addLog } = useDebugStore.getState();
        if (this.process?.pid) {
            addLog({
                type: ELogTypes.INFO,
                message: `Stopping backend (PID: ${this.process.pid})`,
                process: "BackendService",
            });
            try {
                process.kill(-this.process.pid, "SIGTERM");
            } catch (_e) {
                this.process.kill("SIGTERM");
            }
            this.process = null;
            addLog({
                type: ELogTypes.INFO,
                message: "Backend stopped",
                process: "BackendService",
            });
        }
    }

    /**
     * Restarts the backend
     */
    public async restart(): Promise<void> {
        const { addLog } = useDebugStore.getState();
        addLog({
            type: ELogTypes.WARN,
            message: "Restarting backend service...",
            process: "BackendService",
        });
        this.stop();
        await new Promise((resolve) => setTimeout(resolve, 2000));
        this.start();
    }
}

export default BackendService.getInstance();
