import { describe, expect, it, vi } from "vitest";
import { ELogTypes } from "../../types/global.enums.js";
import useLogTable from "./log_table.hooks.js";

const mockLog = [
    {
        id: "1",
        type: ELogTypes.INFO,
        process: "test-process",
        message: "Test message 1",
        timestamp: 1704063600000, // 2024-01-01T00:00:00.000Z
        actor: "system",
    },
    {
        id: "2",
        type: ELogTypes.ERROR,
        process: "error-process",
        message: "Error message",
        timestamp: 1704063660000, // 2024-01-01T00:01:00.000Z
        actor: "system",
    },
];

vi.mock("../../store/useDebugStore.js", () => ({
    default: () => ({
        log: mockLog,
    }),
}));

// We need to use render from ink-testing-library and dummy component pattern
// Correcting the implementation here before writing to file
import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useLogTable>) => void }> = ({
    onRender,
}) => {
    const data = useLogTable();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useLogTable", () => {
    it("should format logs correctly", () => {
        let result: ReturnType<typeof useLogTable> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.logs).toHaveLength(2);

        // Check sorting (newest first)
        expect(result?.logs[0].message).toContain("ERROR | error-process | Error message");
        expect(result?.logs[1].message).toContain("INFO | test-process | Test message 1");
    });

    it("should format timestamp correctly", () => {
        let result: ReturnType<typeof useLogTable> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        // Note: The formatted time depends on the local timezone of the environment running the test.
        // We check if it matches the XX:XX:XX pattern
        expect(result?.logs[0].timestamp).toMatch(/^\d{2}:\d{2}:\d{2}$/);
    });
});
