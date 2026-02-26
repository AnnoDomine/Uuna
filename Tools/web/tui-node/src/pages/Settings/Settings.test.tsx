import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import useSettings from "./settings.hooks.js";

// Mock axios
vi.mock("axios", () => ({
    default: {
        get: vi.fn().mockResolvedValue({ data: { settings: [] } }),
        post: vi.fn().mockResolvedValue({}),
    },
}));

// Mock hooks
const mockRestartBackend = vi.fn();
vi.mock("../../hooks/useBackend.js", () => ({
    default: () => ({
        restartBackend: mockRestartBackend,
    }),
}));

vi.mock("../../store/useStore.js", () => ({
    useStore: () => ({
        isRestarting: false,
    }),
}));

vi.mock("../../store/useDebugStore.js", () => ({
    default: () => ({
        addLog: vi.fn(),
    }),
}));

vi.mock("../../hooks/useScopedInput.js", () => ({
    useScopedInput: () => ({
        isFocused: true,
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useSettings>) => void }> = ({
    onRender,
}) => {
    const data = useSettings();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useSettings", () => {
    it("should initialize correctly", () => {
        let result: ReturnType<typeof useSettings> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.settings).toEqual([]);
        expect(result?.isLoading).toBe(false);
        expect(result?.error).toBeNull();
    });

    it("should expose restartBackend", () => {
        let result: ReturnType<typeof useSettings> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        result?.restartBackend();
        expect(mockRestartBackend).toHaveBeenCalled();
    });
});
