import axios from "axios";
import type { ITask, ITasksResponse } from "../../pages/Tasks/tasks.types.js";
import useDebugStore from "../../store/useDebbugStore.js";
import { ELogTypes } from "../../types/global.enums.js";
import { API_BASE_URL } from "../constants/globals.js";

class TaskService {
    private static instance: TaskService;

    private constructor() {}

    public static getInstance(): TaskService {
        if (!TaskService.instance) {
            TaskService.instance = new TaskService();
        }
        return TaskService.instance;
    }

    /**
     * Fetches all research tasks from the backend.
     */
    public async getTasks(): Promise<ITask[]> {
        const { addLog } = useDebugStore.getState();
        try {
            addLog({
                type: ELogTypes.DEBUG,
                message: "Fetching tasks from API",
                process: "TaskService",
            });
            const response = await axios.get<ITasksResponse>(`${API_BASE_URL}/tasks/list`);
            addLog({
                type: ELogTypes.TRACE,
                message: `Successfully fetched ${response.data.tasks.length} tasks`,
                process: "TaskService",
            });
            return response.data.tasks;
        } catch (error) {
            addLog({
                type: ELogTypes.ERROR,
                message: `Failed to fetch tasks: ${error}`,
                process: "TaskService",
            });
            return [];
        }
    }

    /**
     * Gets a single task by ID.
     */
    public async getTaskDetails(taskId: string): Promise<ITask | null> {
        const { addLog } = useDebugStore.getState();
        try {
            addLog({
                type: EFocusAreal as any,
                message: `Fetching details for task ${taskId}`,
                process: "TaskService",
            });
            const response = await axios.get<ITask>(`${API_BASE_URL}/tasks/${taskId}`);
            return response.data;
        } catch (error) {
            addLog({
                type: ELogTypes.ERROR,
                message: `Failed to fetch details for task ${taskId}: ${error}`,
                process: "TaskService",
            });
            return null;
        }
    }
}

export default TaskService.getInstance();
