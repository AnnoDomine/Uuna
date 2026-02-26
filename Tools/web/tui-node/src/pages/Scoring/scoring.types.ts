export interface IScoreEntry {
    score_id: number;
    task_id: string;
    event_id: string | null;
    final_percent: number;
    created_at: string;
    agent_id?: string; // We might need to join this
}

export interface IAgentStats {
    agent: string;
    totalScore: number;
    averageScore: number;
    taskCount: number;
}

export type ScoreRow = [number, string, string | null, number, string];

export interface IScoreboardResponse {
    scores: ScoreRow[]; // Raw fetchall() response from backend [[id, task_id, event_id, percent, created_at], ...]
}
