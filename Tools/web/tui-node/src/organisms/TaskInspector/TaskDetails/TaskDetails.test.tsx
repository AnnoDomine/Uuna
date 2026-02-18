import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { useTaskDetails } from "./TaskDetails.hooks.js";

const mockTasks = [
    {
        task_id: "task-1",
        title: "Test Task",
        status: "pending",
        created_at: "2024-01-01",
    },
];

const mockEvents = [
    {
        event_id: "event-1",
        role: "TestRole",
        event: "TestEvent",
        details: "TestDetails",
        timestamp: "2024-01-01",
    },
];

const mockScores = [
    {
        score_id: "score-1",
        task_id: "task-1",
        event_id: "event-1",
        score: 100,
        reason: "Test Reason",
        created_at: "2024-01-01",
    },
];

// Mock store with different selected states
const mockStore = vi.fn(() => ({
    tasks: mockTasks,
    events: mockEvents,
    scores: mockScores,
    selectedTaskId: "task-1",
    selectedEventId: "event-1",
}));

vi.mock("../../../store/useTaskInspectorStore.js", () => ({
    default: () => mockStore(),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useTaskDetails>) => void }> = ({
    onRender,
}) => {
    const data = useTaskDetails();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useTaskDetails", () => {
    it("should return selected task details", () => {
        let result: ReturnType<typeof useTaskDetails> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.selectedTask).toEqual(mockTasks[0]);
        expect(result?.selectedTaskId).toBe("task-1");
    });

    it("should return selected event details", () => {
        let result: ReturnType<typeof useTaskDetails> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.selectedEvent).toEqual(mockEvents[0]);
    });

    it("should return scores", () => {
        let result: ReturnType<typeof useTaskDetails> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.scores).toEqual(mockScores);
    });

    it("should handle null selections", () => {
        // Override mock for this test
        mockStore.mockReturnValueOnce({
            tasks: mockTasks,
            events: mockEvents,
            scores: [],
            selectedTaskId: null,
            selectedEventId: null,
        } as unknown as ReturnType<typeof useTaskDetails>);

        let result: ReturnType<typeof useTaskDetails> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.selectedTask).toBeUndefined();
        expect(result?.selectedEvent).toBeUndefined();
        expect(result?.selectedTaskId).toBeNull();
    });
});
