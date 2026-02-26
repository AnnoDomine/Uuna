import axios from "axios";
import { create } from "zustand";
import { API_BASE_URL } from "../utils/constants/globals.js";

export type TaskItem = {
    task_id: string;
    title: string;
    status: string;
    created_at: string;
};

export type EventItem = {
    event_id: string;
    role: string;
    event: string;
    details: string;
    timestamp: string;
};

export type ScoreItem = {
    score_id: string;
    task_id: string;
    event_id: string;
    score: number;
    reason: string;
    created_at: string;
};

type TasksResponse = {
    tasks: TaskItem[];
};

type EventsResponse = {
    events: EventItem[];
};

type ScoresResponse = {
    scores: ScoreItem[];
};

type TaskInspectorStore = {
    tasks: TaskItem[];
    events: EventItem[];
    scores: ScoreItem[];
    selectedTaskId: string | null;
    selectedEventId: string | null;
    isLoadingTasks: boolean;
    isLoadingEvents: boolean;
    error: string | null;

    fetchTasks: () => Promise<void>;
    selectTask: (taskId: string) => Promise<void>;
    selectEvent: (eventId: string) => void;
};

const useTaskInspectorStore = create<TaskInspectorStore>((set) => ({
    tasks: [],
    events: [],
    scores: [],
    selectedTaskId: null,
    selectedEventId: null,
    isLoadingTasks: false,
    isLoadingEvents: false,
    error: null,

    fetchTasks: async () => {
        set({ isLoadingTasks: true, error: null });
        try {
            const { data } = await axios.get<TasksResponse>(`${API_BASE_URL}/tasks/list/all`);
            set({ tasks: data.tasks, isLoadingTasks: false });
        } catch (err) {
            set({ error: `Failed to load tasks: ${err}`, isLoadingTasks: false });
        }
    },

    selectTask: async (taskId: string) => {
        set({
            selectedTaskId: taskId,
            isLoadingEvents: true,
            events: [],
            scores: [],
            selectedEventId: null,
        });
        try {
            const [eventsRes, scoresRes] = await Promise.all([
                axios.get<EventsResponse>(`${API_BASE_URL}/tasks/${taskId}/events`),
                axios.get<ScoresResponse>(`${API_BASE_URL}/tasks/${taskId}/scores`),
            ]);

            set({
                events: eventsRes.data.events,
                scores: scoresRes.data.scores,
                isLoadingEvents: false,
            });
        } catch (err) {
            set({
                error: `Failed to load events/scores: ${err}`,
                isLoadingEvents: false,
            });
        }
    },

    selectEvent: (eventId: string) => {
        set({ selectedEventId: eventId });
    },
}));

export default useTaskInspectorStore;
