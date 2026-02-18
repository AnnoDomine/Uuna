import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { useEventList } from "./EventList.hooks.js";

// Mock the store
const mockSelectEvent = vi.fn();
const mockEvents = [
    {
        event_id: "1",
        role: "TestRole",
        event: "TestEvent",
        details: "TestDetails",
        timestamp: "2024-01-01",
    },
];

vi.mock("../../../store/useTaskInspectorStore.js", () => ({
    default: () => ({
        events: mockEvents,
        selectedTaskId: "task-1",
        selectedEventId: null,
        selectEvent: mockSelectEvent,
        isLoadingEvents: false,
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useEventList>) => void }> = ({
    onRender,
}) => {
    const data = useEventList();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useEventList", () => {
    it("should return formatted event items", () => {
        let result: ReturnType<typeof useEventList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result).toBeDefined();
        if (!result) return;

        expect(result.eventItems).toHaveLength(1);
        expect(result.eventItems[0]).toEqual({
            label: "TestRole: TestEvent",
            value: "1",
            id: "1",
            meta: mockEvents[0],
        });
    });

    it("should return selectedTaskId", () => {
        let result: ReturnType<typeof useEventList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.selectedTaskId).toBe("task-1");
    });

    it("should return selectedEventId", () => {
        let result: ReturnType<typeof useEventList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.selectedEventId).toBeNull();
    });

    it("should expose selectEvent function", () => {
        let result: ReturnType<typeof useEventList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        result?.selectEvent("1");
        expect(mockSelectEvent).toHaveBeenCalledWith("1");
    });

    it("should return isLoadingEvents", () => {
        let result: ReturnType<typeof useEventList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.isLoadingEvents).toBe(false);
    });
});
