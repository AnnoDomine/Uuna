import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { useTaskList } from "./TaskList.hooks.js";

const mockSelectTask = vi.fn();
const mockTasks = [
    {
        task_id: "task-1",
        title: "Test Task",
        status: "pending",
        created_at: "2024-01-01",
    },
];

vi.mock("../../../store/useTaskInspectorStore.js", () => ({
    default: () => ({
        tasks: mockTasks,
        selectedTaskId: null,
        selectTask: mockSelectTask,
        isLoadingTasks: false,
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useTaskList>) => void }> = ({
    onRender,
}) => {
    const data = useTaskList();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useTaskList", () => {
    it("should return formatted task items", () => {
        let result: ReturnType<typeof useTaskList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.taskItems).toHaveLength(1);
        expect(result?.taskItems[0]).toEqual({
            label: "[pending] Test Task...",
            value: "task-1",
            id: "task-1",
            meta: mockTasks[0],
        });
    });

    it("should return selectedTaskId", () => {
        let result: ReturnType<typeof useTaskList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.selectedTaskId).toBeNull();
    });

    it("should expose selectTask function", () => {
        let result: ReturnType<typeof useTaskList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        result?.selectTask("task-1");
        expect(mockSelectTask).toHaveBeenCalledWith("task-1");
    });

    it("should return isLoadingTasks", () => {
        let result: ReturnType<typeof useTaskList> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.isLoadingTasks).toBe(false);
    });
});
