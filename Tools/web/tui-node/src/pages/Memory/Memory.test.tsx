import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import useMemory from "./memory.hooks.js";

// Mock useScopedInput
vi.mock("../../hooks/useScopedInput.js", () => ({
    useScopedInput: () => ({
        isFocused: true,
    }),
}));

vi.mock("../../store/useDebugStore.js", () => ({
    default: () => ({
        addLog: vi.fn(),
    }),
}));

vi.mock("../../utils/services/memory.service.js", () => ({
    default: {
        search: vi.fn().mockResolvedValue([]),
    },
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useMemory>) => void }> = ({
    onRender,
}) => {
    const data = useMemory();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useMemory", () => {
    it("should initialize correctly", () => {
        let result: ReturnType<typeof useMemory> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.query).toBe("");
        expect(result?.role).toBe("Librarian");
        expect(result?.isLoading).toBe(false);
        expect(result?.results).toEqual([]);
        expect(result?.isSearchFocused).toBe(true);
    });
});
