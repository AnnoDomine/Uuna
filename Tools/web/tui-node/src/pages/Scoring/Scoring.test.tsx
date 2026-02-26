import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import useScoring from "./scoring.hooks.js";

// Mock services
vi.mock("../../utils/services/scoring.service.js", () => ({
    default: {
        getBoard: vi.fn().mockResolvedValue([]),
    },
}));

vi.mock("../../utils/services/task.service.js", () => ({
    default: {
        getTasks: vi.fn().mockResolvedValue([]),
    },
}));

vi.mock("../../store/useDebugStore.js", () => ({
    default: () => ({
        addLog: vi.fn(),
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useScoring>) => void }> = ({
    onRender,
}) => {
    const data = useScoring();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useScoring", () => {
    it("should initialize correctly", () => {
        let result: ReturnType<typeof useScoring> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.agentStats).toEqual([]);
        expect(result?.rawScores).toEqual([]);
        expect(result?.agentTableData).toEqual([]);
        expect(result?.historyTableData).toEqual([]);
    });
});
