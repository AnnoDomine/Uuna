import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { GLOBAL } from "../../utils/global.constants";
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

const tasksApi = createApi({
    reducerPath: "tasksApi",
    baseQuery: fetchBaseQuery({ baseUrl: `${GLOBAL.VECTOR_DB_URL}/tasks` }),
    tagTypes: ["Tasks", "Task", "Events", "Scores"],
    endpoints: (builder) => ({
        listTasks: builder.query<TasksResponse, void>({
            query: () => "/list/all",
            providesTags: ["Tasks"],
        }),
        getEvents: builder.query<EventsResponse, string>({
            query: (taskId) => `/${taskId}/events`,
            providesTags: (_res, _e, taskId) => [{ type: "Events", id: taskId }],
        }),
        getScores: builder.query<ScoresResponse, string>({
            query: (taskId) => `/${taskId}/scores`,
            providesTags: (_res, _e, taskId) => [{ type: "Scores", id: taskId }],
        }),
        getTask: builder.query({
            query: (taskId) => `/${taskId}`,
            providesTags: ["Task"],
        }),
    }),
});

export const { useGetEventsQuery, useGetScoresQuery, useGetTaskQuery, useListTasksQuery } =
    tasksApi;

export default tasksApi;
