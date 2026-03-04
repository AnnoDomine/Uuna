export type FrontendSignal = {
    task_id: string;
    agent: string;
    message: string;
    type: "research" | "response" | "error";
    level: string;
    task_context?: object;
};

export type AIChatItem = {
    agent: string;
    message: string;
    timestamp: number;
    level: string;
    type: "chat" | "research" | "response" | "error";
};
