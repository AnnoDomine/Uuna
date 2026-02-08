export enum ETaskStatus {
    PENDING = "pending",
    IN_PROGRESS = "in_progress",
    COMPLETED = "completed",
    FAILED = "failed",
}

export interface ITask {
    id: string;
    title: string;
    description: string;
    status: ETaskStatus;
    progress: number; // 0 to 100
    agent_id?: string;
    created_at: string;
    updated_at: string;
}

export interface ITasksResponse {
    tasks: ITask[];
}
