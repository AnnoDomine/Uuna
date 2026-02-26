import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { useTasksPage } from "./tasks.hooks.js";

// Mock store
const mockFetchTasks = vi.fn();
vi.mock("../../store/useTaskInspectorStore.js", () => ({
    default: () => ({
        fetchTasks: mockFetchTasks,
        error: null,
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useTasksPage>) => void }> = ({
    onRender,
}) => {
    const data = useTasksPage();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useTasksPage", () => {
    it("should fetch tasks on mount", () => {
        render(<TestComponent onRender={() => {}} />);
        expect(mockFetchTasks).toHaveBeenCalled();
    });

    it("should return error from store", () => {
        let result: ReturnType<typeof useTasksPage> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.error).toBeNull();
    });
});
